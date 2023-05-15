import logging
import os

import wget
from whisper_cpp_python import Whisper

from src.constants import MODEL_DIR
from src.constants import VALID_WHISPER_MODELS


logger = logging.getLogger(__name__)


class Whisperer:

    MODEL_NAME_PATTERN = "ggml-{size}.bin"

    def __init__(self, model_size: str, model_dir: str = MODEL_DIR):

        if model_size not in VALID_WHISPER_MODELS:
            raise ValueError(
                f"'{model_size}' is not a valid model size for Whisper. "
                f"Valid options are: {VALID_WHISPER_MODELS}"
            )
        model_name = self.MODEL_NAME_PATTERN.format(size=model_size)
        model_path = os.path.join(model_dir, model_name)

        if not os.path.exists(model_path):
            logger.info(f"⌛️ Download {model_name} into {model_dir}")
            os.makedirs(model_dir, exist_ok=True)
            wget.download(VALID_WHISPER_MODELS[model_size], out=model_dir)

        logger.info(f"Loading whisper model '{model_name}'")
        self.model = Whisper(model_path=model_path)

    def transcribe(self, mp3file: str) -> str:
        with open(mp3file, "rb") as audio:
            res = self.model.transcribe(audio)
            return res["text"]
