#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"    # Test mode: prints response to stdout
    uv run bot.py                    # Production: connects to Telegram
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers.commands.start import handle_start
from handlers.commands.help import handle_help
from handlers.commands.health import handle_health
from handlers.commands.labs import handle_labs
from handlers.commands.scores import handle_scores


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: run a command and print response to stdout",
    )
    return parser.parse_args()


async def run_test_mode(command: str) -> None:
    """Run a command in test mode and print the response."""
    # Strip leading slash if present
    cmd = command.lstrip("/")

    # Route to appropriate handler
    if cmd == "start":
        response = await handle_start()
    elif cmd == "help":
        response = await handle_help()
    elif cmd == "health":
        response = await handle_health()
    elif cmd == "labs":
        response = await handle_labs()
    elif cmd.startswith("scores"):
        # Extract lab argument if present
        parts = cmd.split(maxsplit=1)
        lab = parts[1] if len(parts) > 1 else "unknown"
        response = await handle_scores(lab)
    else:
        response = f"Command /{cmd} not implemented yet"

    print(response)


async def run_production_mode() -> None:
    """Run the bot in production mode (Telegram)."""
    # TODO: Task 1 - implement Telegram connection
    print("Production mode not implemented yet")


async def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.test:
        await run_test_mode(args.test)
    else:
        await run_production_mode()


if __name__ == "__main__":
    asyncio.run(main())
