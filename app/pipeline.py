# app/pipeline.py
from app.captioning import ImageCaptioner
from app.translation import Translator
from app.safety import AltTextSafetyChecker


class AltTextPipeline:
    def __init__(self, target_languages=["fr", "de"]):
        self.captioner = ImageCaptioner()
        self.translators = {lang: Translator(lang) for lang in target_languages}
        self.safety = AltTextSafetyChecker()

    def process_image(self, image_path: str) -> dict:
        result = {
            "image_path": image_path,
            "captions": {},
            "safety": {}
        }

        english_caption = self.captioner.generate_caption(image_path)
        result["captions"]["en"] = english_caption

        safety_check = self.safety.is_safe(english_caption)
        result["safety"]["en"] = safety_check

        for lang, translator in self.translators.items():
            translated = translator.translate(english_caption)
            result["captions"][lang] = translated
            result["safety"][lang] = self.safety.is_safe(translated)

        return result
