"""Intent router: uses LLM to interpret natural language and call tools."""

import json
import sys
import httpx
from services.llm_client import get_llm_client
from services.lms_api import get_api_client
from config import get_settings


# System prompt for the LLM
SYSTEM_PROMPT = """You are a helpful assistant for an LMS (Learning Management System). 
You have access to tools that fetch data about labs, learners, scores, and analytics.

When a user asks a question:
1. First, think about what data you need. If the question involves comparing labs or finding the best/worst, you MUST first call get_items to discover all available labs.
2. Then call the appropriate tool(s) to get the data for each relevant lab.
3. Once you have all the data, compare and summarize clearly for the user.

For questions like "which lab has the lowest pass rate" or "compare labs":
- Step 1: Call get_items to get all lab IDs
- Step 2: Call get_pass_rates for each lab
- Step 3: Compare the results and identify the lowest/highest

If the user's message is unclear or ambiguous, ask for clarification.
If the user greets you, respond warmly and mention what you can help with (labs, scores, pass rates, etc.).

Always use tools to get real data before answering questions about specific labs or scores.
After calling tools, you will see the results. Use those results to answer the user's question."""


async def route_intent(user_message: str) -> str:
    """
    Route a natural language message through the LLM.

    Args:
        user_message: The user's message text.

    Returns:
        The bot's response text.
    """
    llm = get_llm_client()
    api = get_api_client()
    tools = llm._get_tools()

    # Initialize conversation with system prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    # Tool calling loop
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Call LLM
        response = await llm.chat(messages, tools)

        # Check if LLM wants to call tools
        tool_calls = response.get("tool_calls", [])

        if not tool_calls:
            # LLM is done - return its response
            return response.get("content", "I'm not sure how to help with that.")

        # Execute tool calls and collect results
        tool_results = []
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            func_name = function.get("name")
            func_args = function.get("arguments", {})

            # Skip empty tool calls
            if not func_name:
                continue

            # Parse arguments if they're a JSON string
            if isinstance(func_args, str):
                try:
                    func_args = json.loads(func_args)
                except json.JSONDecodeError:
                    func_args = {}

            # Execute the tool
            result = await _execute_tool(func_name, func_args, api)
            tool_results.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.get("id"),
                    "content": result,
                }
            )

            # Debug output to stderr
            print(f"[tool] LLM called: {func_name}({func_args})", file=sys.stderr)
            print(
                f"[tool] Result: {result[:100]}..."
                if len(result) > 100
                else f"[tool] Result: {result}",
                file=sys.stderr,
            )

        # Add assistant response and tool results to conversation
        messages.append(
            {
                "role": "assistant",
                "content": response.get("content"),
                "tool_calls": tool_calls,
            }
        )
        messages.extend(tool_results)

        print(
            f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM",
            file=sys.stderr,
        )

    # If we get here, we hit max iterations
    return "I'm having trouble answering that question. Please try rephrasing."


async def _execute_tool(func_name: str, func_args: dict, api) -> str:
    """Execute a tool and return the result as a string."""
    import json

    try:
        if func_name == "get_items":
            result = await api.get_items()
            return json.dumps(result, default=str)
        elif func_name == "get_pass_rates":
            lab = func_args.get("lab", "")
            result = await api.get_pass_rates(lab)
            return json.dumps(result, default=str)
        elif func_name == "get_scores":
            lab = func_args.get("lab", "")
            # Call the analytics endpoint directly
            from config import get_settings

            settings = get_settings()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.lms_api_base_url}/analytics/scores",
                    params={"lab": lab},
                    headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                )
                return json.dumps(response.json(), default=str)
        elif func_name == "get_learners":
            from config import get_settings

            settings = get_settings()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.lms_api_base_url}/learners/",
                    headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                )
                return json.dumps(response.json(), default=str)
        elif func_name == "get_timeline":
            from config import get_settings

            settings = get_settings()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.lms_api_base_url}/analytics/timeline",
                    params={"lab": func_args.get("lab", "")},
                    headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                )
                return json.dumps(response.json(), default=str)
        elif func_name == "get_groups":
            from config import get_settings

            settings = get_settings()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.lms_api_base_url}/analytics/groups",
                    params={"lab": func_args.get("lab", "")},
                    headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                )
                return json.dumps(response.json(), default=str)
        elif func_name == "get_top_learners":
            from config import get_settings

            settings = get_settings()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.lms_api_base_url}/analytics/top-learners",
                    params={
                        "lab": func_args.get("lab", ""),
                        "limit": func_args.get("limit", 5),
                    },
                    headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                )
                return json.dumps(response.json(), default=str)
        elif func_name == "get_completion_rate":
            from config import get_settings

            settings = get_settings()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.lms_api_base_url}/analytics/completion-rate",
                    params={"lab": func_args.get("lab", "")},
                    headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                )
                return json.dumps(response.json(), default=str)
        elif func_name == "trigger_sync":
            settings = get_settings()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.lms_api_base_url}/pipeline/sync",
                    headers={"Authorization": f"Bearer {settings.lms_api_key}"},
                )
                return json.dumps(response.json(), default=str)
        else:
            return f"Unknown tool: {func_name}"
    except Exception as e:
        return f"Error executing {func_name}: {str(e)}"
