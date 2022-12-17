import whisper
from loguru import logger

from src.constants import VALID_WHISPER_MODELS


class Whisperer:
    def __init__(self, model_size: str):
        if model_size not in VALID_WHISPER_MODELS:
            raise ValueError(
                f"'{model_size}' is not a valid model size for Whisper. "
                f"Valid options are: {VALID_WHISPER_MODELS}"
            )
        logger.info(f"Loading whisper model '{model_size}'")
        self.model = whisper.load_model(model_size)

    def transcribe(self, mp3file: str):
        res = self.model.transcribe(mp3file)
        return res["text"]
