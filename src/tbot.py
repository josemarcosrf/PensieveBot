import datetime as dt
import re
import tempfile
from typing import List

import requests
import telebot
from loguru import logger

from src import break_path
from src import create_process
from src.stt import Whisperer


class TelegramBot:
    def __init__(
        self, bot_token: str, valid_sender_ids: List[int], whisperer: Whisperer
    ) -> None:
        self.token = bot_token
        self.valid_sender_ids = valid_sender_ids
        self.whisperer = whisperer
        self.bot = telebot.TeleBot(bot_token, parse_mode="MARKDOWN")
        self.setup()

    def _convert_and_transcribe(self, file_info):
        try:
            now = "  ".join(dt.datetime.now().isoformat().split(".")[0].split("T"))

            # Fetch the media file
            media_file = requests.get(
                f"https://api.telegram.org/file/bot{self.token}/{file_info.file_path}"
            )
            _, _, original_ext = break_path(file_info.file_path)

            with tempfile.NamedTemporaryFile(mode="wb", suffix=original_ext) as f:
                # write audio to disk
                in_file = f.name
                f.write(media_file.content)

                # Convert to mp3
                out_file = f.name.replace(original_ext, ".mp3")
                create_process(f"ffmpeg -i {in_file} {out_file}").wait()

                # transcribe
                transcript = self.whisperer.transcribe(out_file)
                if isinstance(transcript, list):
                    transcript = "\n".join(transcript)

                text = transcript.strip()
                text = re.sub("hashtag ", "#", text, flags=re.IGNORECASE)
                text = re.sub("^slash ", "/", text, flags=re.IGNORECASE)
                text = f"**{now}**\n\n" + text

            return text

        except Exception as e:
            raise RuntimeError(f"Error while transcribing media: {e}")

    def reply_or_edit(self, message, text):
        re_flags = re.MULTILINE | re.IGNORECASE
        if message.json.get("reply_to_message"):
            if re.search("^/append", text, flags=re_flags):
                text = (
                    message.reply_to_message.text
                    + "\n"
                    + re.sub("^/append ", "", text, flags=re_flags)
                )

            # Update the message which the user replied to
            text = re.sub("^/edit ", "", text, flags=re_flags) + " (edited)"
            self.bot.edit_message_text(
                text,
                message.chat.id,
                message.reply_to_message.message_id,
            )
        else:
            self.bot.reply_to(message, text)

    def handle_audio_message(self, message: telebot.types.Message):
        try:
            if message.content_type == "voice":
                tmp_reply = f"👂 Received a {message.voice.duration}s voice note. Transcribing..."
                logger.info(tmp_reply)
                ack_reply = self.bot.send_message(message.chat.id, tmp_reply)
                file_info = self.bot.get_file(message.voice.file_id)
            else:
                tmp_reply = (
                    f"👂 Received a {message.audio.duration}s audio. Transcribing..."
                )
                logger.info(tmp_reply)
                ack_reply = self.bot.send_message(message.chat.id, tmp_reply)
                file_info = self.bot.get_file(message.audio.file_id)

            text = self._convert_and_transcribe(file_info)

            # Delete ack message and send transcript as a reply
            self.bot.delete_message(message.chat.id, ack_reply.id)
            # Post a new transcription message or edit a past one
            self.reply_or_edit(message, text)

        except Exception as e:
            print(f"🚨 Error! {e}")
            self.bot.reply_to(message, f"🚨 Error! {e}")

    def handle_video_message(self, message: telebot.types.Message):
        try:
            if message.content_type == "video_note":
                tmp_reply = (
                    f"👂 Received a {message.video_note.duration}s video note. "
                    "Transcribing..."
                )
                logger.info(tmp_reply)
                ack_reply = self.bot.send_message(message.chat.id, tmp_reply)
                file_info = self.bot.get_file(message.video_note.file_id)
            else:
                tmp_reply = (
                    f"👂 Received a {message.video.duration}s video. Transcribing..."
                )
                logger.info(tmp_reply)
                ack_reply = self.bot.send_message(message.chat.id, tmp_reply)
                file_info = self.bot.get_file(message.video.file_id)

            text = self._convert_and_transcribe(file_info)

            # Delete ack message and send transcript as a reply
            self.bot.delete_message(message.chat.id, ack_reply.id)
            # Post a new transcription message or edit a past one
            self.reply_or_edit(message, text)

        except Exception as e:
            print(f"🚨 Error! {e}")
            self.bot.reply_to(message, f"🚨 Error! {e}")

    def setup(self):
        def is_known_user(message: telebot.types.Message):
            logger.debug(
                f"Checking user: {message.from_user.username} ({message.from_user.id})"
            )
            return message.from_user.id in self.valid_sender_ids

        # getMe
        me = self.bot.get_me()
        logger.info(f"Running bot with ID: {me.id} | Name: {me.username}")

        @self.bot.message_handler(func=lambda m: not is_known_user(m))
        def not_friends(message):
            logger.warning(
                f"Received message from un-known user: {message.from_user.id}"
            )
            self.bot.reply_to(message, "We are not friends...Sorry 👋🏻")

        @self.bot.message_handler(func=is_known_user, commands=["start", "help"])
        def send_welcome(message):
            self.bot.reply_to(
                message,
                (
                    "Hey, let's start. What are your thoughts? "
                    "You can send voice or video clips and I will transcribe for you"
                ),
            )

        @self.bot.message_handler(func=is_known_user)
        def ack(message):
            logger.debug(f"Message from: {message.from_user.id}")
            logger.debug(f"Text: {message.text}")
            self.bot.reply_to(message, "✅")

        @self.bot.message_handler(func=is_known_user, content_types=["audio", "voice"])
        def handle_audio(message):
            self.handle_audio_message(message)

        @self.bot.message_handler(
            func=is_known_user, content_types=["video_note", "video"]
        )
        def handle_video(message):
            self.handle_video_message(message)

    def run(self):
        # Run polling
        self.bot.infinity_polling()
