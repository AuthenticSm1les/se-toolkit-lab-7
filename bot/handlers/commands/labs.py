"""Handler for /labs command."""

from services.lms_api import get_api_client


async def handle_labs() -> str:
    """
    Handle the /labs command.

    Returns:
        Formatted list of available labs.
    """
    client = get_api_client()
    items = await client.get_items()

    if items is None:
        return "Backend error: connection refused. Check that the services are running."

    # Extract labs from items (items have 'id', 'title', 'type' fields)
    labs = []
    for item in items:
        if item.get("type") == "lab":
            lab_id = item.get("id")
            lab_title = item.get("title")
            if lab_id and lab_title:
                labs.append((lab_id, lab_title))

    if not labs:
        return "No labs available."

    lines = ["Available labs:"]
    for lab_id, lab_title in sorted(labs, key=lambda x: x[0]):
        lines.append(f"- {lab_title}")

    return "\n".join(lines)
