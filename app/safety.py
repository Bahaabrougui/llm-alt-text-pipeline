from detoxify import Detoxify
import re


class AltTextSafetyChecker:
    def __init__(self, max_words=25, min_words=3, toxicity_threshold=0.4):
        self.detoxifier = Detoxify("original")
        self.max_words = max_words
        self.min_words = min_words
        self.toxicity_threshold = toxicity_threshold

    def is_safe(self, text: str) -> dict:
        score = self.detoxifier.predict(text)
        num_words = len(text.split())
        is_too_short = num_words < self.min_words
        is_too_long = num_words > self.max_words
        has_profanity = bool(re.search(r"\b(fuck|shit|damn|bitch)\b", text.lower()))
        is_toxic = score["toxicity"] > self.toxicity_threshold

        return {
            "is_safe": not (is_toxic or is_too_short or is_too_long or has_profanity),
            "toxicity": score["toxicity"],
            "too_short": is_too_short,
            "too_long": is_too_long,
            "profanity": has_profanity
        }
