import logging
import os
from typing import Tuple

import requests

from app.define import CAPTIONING_MODEL_ROUTE
from app.translation.translator import Translator
from app.safety.safety_w_openai import AltTextOpenAISafetyChecker
from app.safety.safety_w_detoxify import AltTextDetoxifySafetyChecker
from app.utils.utils import safe_json


class AltTextPipeline:
    def __init__(self, target_languages=["fr", "de"]):
        self.translators = {lang: Translator(lang) for lang in target_languages}
        self.gpt_safety = AltTextOpenAISafetyChecker()
        self.detoxify_safety = AltTextDetoxifySafetyChecker()

    def process_image(self, files: dict[str, Tuple[str, bytes, str]]) -> dict:
        # Log instance id
        logging.info(
            f"Azure Instance ID: {os.environ.get('WEBSITE_INSTANCE_ID')}"
        )
        # Prepare and start pipeline
        result = {
            "file_name": files["file"][0],
            "captions": {},
            "safety": {}
        }

        # Fetch captioning API
        response = requests.post(
            os.environ["CAPTIONING_MODEL_SERVER"] + CAPTIONING_MODEL_ROUTE,
            files=files,
        )
        if response.ok:
            english_caption = response.json()["caption"]
        else:
            raise RuntimeError("Error:", response.text)
        result["captions"]["en"] = english_caption

        safety_check = self.gpt_safety.is_safe(english_caption)
        result["safety"]["en"] = safety_check

        for lang, translator in self.translators.items():
            translated = translator.translate(english_caption)
            result["captions"][lang] = translated
            result["safety"][lang] = self.detoxify_safety.is_safe(translated)

        return safe_json(result)
