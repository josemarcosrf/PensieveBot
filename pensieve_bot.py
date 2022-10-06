import argparse
import datetime as dt
import logging
import os
import re
import tempfile
from subprocess import PIPE
from subprocess import Popen

import coloredlogs
import requests
import telebot
import whisper

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


VALID_SENDER_IDS = []
BOT_TOKEN = ""
VALID_MODELS = ["tiny", "base", "small", "medium", "large"]


class Whisperer:
    def __init__(self, model_size: str):
        print(f"Loading whisper model '{model_size}'")
        self.model = whisper.load_model(model_size)

    def transcribe(self, mp3file: str):
        res = self.model.transcribe(mp3file)
        return res["text"]


def create_process(cmd):
    process = Popen(
        [cmd], stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True, preexec_fn=os.setsid
    )
    return process


def handle_audio_message(bot, whisperer: Whisperer, message: telebot.types.Message):
    now = "  ".join(dt.datetime.now().isoformat().split(".")[0].split("T"))

    if message.content_type == "voice":
        msg = f"👂 Received a {message.voice.duration}s voice note. Transcribing..."
        logger.info(msg)
        ack_reply = bot.send_message(message.chat.id, msg)
        file_info = bot.get_file(message.voice.file_id)
    else:
        logger.warning("Received audio clip. Cannot handle these yet...")
        bot.reply_to(message, "😓 Sorry can't handle audio clips yet...")
        file_info = bot.get_file(message.audio.file_id)

    try:
        # Fetch the audio file
        audio_file = requests.get(
            f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        )

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".ogg") as f:
            # write audio to disk
            in_file = f.name
            f.write(audio_file.content)

            # Convert to mp3
            out_file = f.name.replace(".ogg", ".mp3")
            create_process(f"ffmpeg -i {in_file} {out_file}").wait()

            # transcribe
            transcript = whisperer.transcribe(out_file)
            if isinstance(transcript, list):
                transcript = "\n".join(transcript)

            text = f"**{now}**\n\n" + transcript
            text = re.sub("hashtag ", "#", text, flags=re.IGNORECASE)

            # Delete ack message and send transcript as a reply
            bot.delete_message(message.chat.id, ack_reply.id)
            bot.reply_to(message, text)

    except Exception as e:
        print(f"🚨 Error! {e}")
        bot.reply_to(message, f"🚨 Error! {e}")


def run_telebot(bot, whisperer):
    def is_known_user(message: telebot.types.Message):
        logger.debug(
            f"Checking user: {message.from_user.username} ({message.from_user.id})"
        )
        return message.from_user.id in VALID_SENDER_IDS

    # getMe
    me = bot.get_me()
    logger.info(f"Running bot with ID: {me.id} | Name: {me.username}")

    @bot.message_handler(func=lambda m: not is_known_user(m))
    def not_friends(message):
        logger.warning(f"Received message from un-known user: {message.from_user.id}")
        bot.reply_to(message, "We are not friends...Sorry 👋🏻")

    @bot.message_handler(func=is_known_user, commands=["start", "help"])
    def send_welcome(message):
        bot.reply_to(
            message,
            (
                "Hey, let's start. What are your thoughts? "
                "You can send voice clips and I will transcribe for you"
            ),
        )

    @bot.message_handler(func=is_known_user)
    def ack(message):
        logger.debug(f"Message from: {message.from_user.id}")
        logger.debug(f"Text: {message.text}")
        bot.reply_to(message, "✅")

    @bot.message_handler(func=is_known_user, content_types=["audio", "voice"])
    def handle_audio(message):
        handle_audio_message(bot, whisperer, message)

    @bot.message_handler(func=is_known_user, content_types=["video_note", "video"])
    def handle_audio(message):
        bot.reply_to(
            message,
            "😖 Sorry. Transcribing from videos and video notes is not implemented yet."
        )

    # Run polling
    bot.infinity_polling()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", default="medium", choices=VALID_MODELS)
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
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="MARKDOWN")
    run_telebot(bot, whisperer)

    print(args.model)


if __name__ == "__main__":
    main()
