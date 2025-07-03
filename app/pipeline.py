import logging
import os

from app.factory.image_captioner_factory import ImageCaptionerFactory
from app.translation import Translator
from app.safety import AltTextSafetyChecker


class AltTextPipeline:
    def __init__(self, target_languages=["fr", "de"]):
        self.image_captioner = ImageCaptionerFactory.get()
        self.translators = {lang: Translator(lang) for lang in target_languages}
        self.safety = AltTextSafetyChecker()

    def process_image(self, image_path: str) -> dict:
        # Log instance id
        logging.info(
            f"Azure Instance ID: {os.environ.get('WEBSITE_INSTANCE_ID')}"
        )
        # Prepare and start pipeline
        result = {
            "image_path": image_path,
            "captions": {},
            "safety": {}
        }

        english_caption = self.image_captioner.generate_caption(image_path)
        result["captions"]["en"] = english_caption

        safety_check = self.safety.is_safe(english_caption)
        result["safety"]["en"] = safety_check

        for lang, translator in self.translators.items():
            translated = translator.translate(english_caption)
            result["captions"][lang] = translated
            result["safety"][lang] = self.safety.is_safe(translated)

        return result
