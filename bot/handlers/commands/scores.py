"""Handler for /scores command."""

from services.lms_api import get_api_client


async def handle_scores(lab: str) -> str:
    """
    Handle the /scores command.

    Args:
        lab: The lab identifier (e.g., 'lab-04').

    Returns:
        Per-task pass rates for the specified lab.
    """
    if not lab or lab == "unknown":
        return "Usage: /scores <lab> (e.g., /scores lab-04)"

    client = get_api_client()
    pass_rates = await client.get_pass_rates(lab)

    if pass_rates is None:
        return (
            f"Backend error: connection refused. Check that the services are running."
        )

    if not pass_rates:
        return f"No scores found for lab '{lab}'. The lab may not exist."

    # Format pass rates (API returns 'task', 'avg_score', 'attempts')
    lines = [f"Pass rates for {lab}:"]
    for rate in pass_rates:
        task_name = rate.get("task", "Unknown task")
        avg_score = rate.get("avg_score", 0)
        attempts = rate.get("attempts", 0)
        lines.append(f"- {task_name}: {avg_score:.1f}% ({attempts} attempts)")

    return "\n".join(lines)
