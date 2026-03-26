"""Handler for /help command."""


async def handle_help() -> str:
    """
    Handle the /help command.
    
    Returns:
        List of available commands.
    """
    return """Available commands:
/start - Welcome message
/help - Show this help message
/health - Check backend status
/labs - List available labs
/scores <lab> - Get scores for a lab"""
