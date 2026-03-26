#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"    # Test mode: prints response to stdout
    uv run bot.py                    # Production: connects to Telegram
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from handlers.start import handle_start
from handlers.help import handle_help
from handlers.health import handle_health
from handlers.labs import handle_labs
from handlers.scores import handle_scores


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

    logger.info(f"Running test command: /{cmd}")

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

    logger.info(f"Response: {response}")
    print(response)


async def run_production_mode() -> None:
    """Run the bot in production mode (Telegram)."""
    logger.info("Starting bot in production mode")
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Bot crashed: {e}")
        raise
