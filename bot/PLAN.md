# Development Plan

This document outlines the approach for building the LMS Telegram bot across four tasks.

## Task 1: Plan and Scaffold

**Goal:** Create a testable project structure with handler separation from the Telegram transport layer.

**Approach:**
- Create `bot/` directory with entry point (`bot.py`), handlers (`handlers/`), services (`services/`), and configuration (`config.py`)
- Implement `--test` mode that calls handlers directly without Telegram connection
- Each command (`/start`, `/help`, `/health`, `/labs`, `/scores`) is a separate handler function that takes input and returns text
- This separation of concerns allows testing handlers independently from Telegram

**Key Pattern:** Handlers are plain async functions. They don't know about Telegram. The same function works from `--test` mode, unit tests, or the Telegram bot.

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

**Approach:**
- Create `services/api_client.py` with a `LMSClient` class
- Use `httpx` for async HTTP requests with Bearer token authentication
- Read `LMS_API_BASE_URL` and `LMS_API_KEY` from environment variables
- Update handlers to call the API client instead of returning placeholders
- Add error handling: if the backend is down, show a friendly message instead of crashing

**Key Pattern:** API client encapsulates all HTTP logic. Handlers call simple methods like `get_health()` or `get_labs()`.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Allow users to ask questions in plain language using an LLM.

**Approach:**
- Create `services/llm_client.py` with tool definitions for each backend endpoint
- Create `handlers/intent_router.py` that sends user messages to the LLM with tool descriptions
- The LLM decides which tool to call based on the user's intent
- Execute the tool and return the result to the user

**Key Pattern:** Tool descriptions matter more than prompt engineering. Clear, specific descriptions help the LLM choose correctly.

## Task 4: Containerize and Document

**Goal:** Deploy the bot using Docker alongside the existing backend.

**Approach:**
- Create `Dockerfile` for the bot service
- Add bot service to `docker-compose.yml`
- Configure container networking (containers use service names, not `localhost`)
- Document deployment steps in README

**Key Pattern:** Docker networking uses service names. The bot container connects to `backend:42002`, not `localhost:42002`.

## Testing Strategy

- **Unit tests:** Test handlers directly with mocked services
- **Integration tests:** Test `--test` mode with real backend
- **Manual testing:** Deploy to VM and test in Telegram

## Git Workflow

For each task:
1. Create issue describing the work
2. Create branch: `task-N-description`
3. Make changes, commit with clear messages
4. Create PR: `Closes #<issue-number>`
5. Partner review, then merge
