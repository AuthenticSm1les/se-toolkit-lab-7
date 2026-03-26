"""Handler for /scores command."""


async def handle_scores(lab: str) -> str:
    """
    Handle the /scores command.
    
    Args:
        lab: The lab identifier (e.g., 'lab-04').
    
    Returns:
        Scores for the specified lab.
    """
    # TODO: Task 2 - call backend API
    return f"Scores for {lab}: Task 1: 80%, Task 2: 75% (placeholder)"
