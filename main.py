#!/usr/bin/env python3
"""
LATOKEN Assistant Telegram Bot

This bot provides information about LATOKEN company, its culture, 
and ongoing hackathon using RAG from specified sources.
"""

import logging
import os
from dotenv import load_dotenv
from bot import main as run_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_env_variables():
    """Check if required environment variables are set"""
    load_dotenv()

    required_vars = ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        logger.info("Please add the missing variables to your .env file")

        if "TELEGRAM_BOT_TOKEN" in missing_vars:
            logger.info(
                "To get a Telegram bot token, talk to @BotFather on Telegram "
                "and follow the instructions"
            )

        return False

    logger.info("All required environment variables are set")
    return True


def main():
    """Main entry point for the application"""
    logger.info("Starting LATOKEN Assistant Telegram Bot")

    # Check environment variables
    if not check_env_variables():
        logger.error("Exiting due to missing environment variables")
        return

    # Run the bot
    run_bot()


if __name__ == "__main__":
    main()
