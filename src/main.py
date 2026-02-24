"""Entry point for SpeechSnap application."""

import asyncio
import logging

from config import config
from config.Config import setup_logging
from app import App

setup_logging(config.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Run the SpeechSnap application."""
    try:
        app = App()
        await app.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception:
        logger.exception("Fatal error occurred")
        raise


if __name__ == "__main__":
    asyncio.run(main())
