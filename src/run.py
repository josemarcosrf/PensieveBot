import os

import click
import coloredlogs
from dotenv import load_dotenv

from src import logger
from src.constants import VALID_WHISPER_MODELS
from src.stt import Whisperer
from src.tbot import TelegramBot

load_dotenv()


@click.command("run")
@click.option("-m", "--model_path", default=None)
@click.option(
    "-s", "--model_size", default=None, type=click.Choice(VALID_WHISPER_MODELS)
)
@click.option(
    "-v",
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
)
def main(model_path, model_size, log_level):
    global VALID_SENDER_IDS
    global BOT_TOKEN

    VALID_SENDER_IDS = [int(sid) for sid in os.getenv("VALID_SENDER_IDS").split(",")]
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    coloredlogs.install(logger=logger, level=log_level)

    try:
        logger.info("🤫 Initializing Whisper model...")
        whisperer = Whisperer(model_path=model_path, model_size=model_size)

        logger.info("🤖 Initializing Telegram bot...")
        bot = TelegramBot(BOT_TOKEN, VALID_SENDER_IDS, whisperer)

        logger.info("🏃🏻 Running...")
        bot.run()
    except Exception as e:
        logger.exception(f"💥 {e}")


if __name__ == "__main__":
    main()
