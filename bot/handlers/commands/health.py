"""Handler for /health command."""

from services.lms_api import get_api_client


async def handle_health() -> str:
    """
    Handle the /health command.

    Returns:
        Backend health status with item count or error message.
    """
    client = get_api_client()
    items = await client.get_items()

    if items is None:
        return "Backend error: connection refused. Check that the services are running."

    item_count = len(items)
    return f"Backend is healthy. {item_count} items available."
