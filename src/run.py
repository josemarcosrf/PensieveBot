import argparse
import os

import coloredlogs
from dotenv import load_dotenv

from src import logger
from src.constants import VALID_WHISPER_MODELS
from src.stt import Whisperer
from src.tbot import TelegramBot

load_dotenv()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", default="medium", choices=VALID_WHISPER_MODELS)
    parser.add_argument(
        "-v",
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )

    return parser.parse_args()


def main():
    args = get_args()

    global VALID_SENDER_IDS
    global BOT_TOKEN

    VALID_SENDER_IDS = [int(sid) for sid in os.getenv("VALID_SENDER_IDS").split(",")]
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    coloredlogs.install(logger=logger, level=args.log_level)

    logger.info("🤫 Initializing Whisper model...")
    whisperer = Whisperer(args.model)

    logger.info("🤖 Initializing Telegram bot...")
    bot = TelegramBot(BOT_TOKEN, VALID_SENDER_IDS, whisperer)

    logger.info("🏃🏻 Running...")
    bot.run()


if __name__ == "__main__":
    main()
