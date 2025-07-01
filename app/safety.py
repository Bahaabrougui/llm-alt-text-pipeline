import time

from detoxify import Detoxify
import re

from transformers import BertTokenizer

from app.utils.utils import log_metrics


class AltTextSafetyChecker:
    def __init__(self, max_words=25, min_words=3, toxicity_threshold=0.3):
        self.detoxifier = Detoxify("original")
        # Detoxify is a wrapper around bert-base-uncased
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.max_words = max_words
        self.min_words = min_words
        self.toxicity_threshold = toxicity_threshold

    def is_safe(self, text: str) -> dict:
        _start_ = time.time()
        score = self.detoxifier.predict(text)
        num_words = len(text.split())
        is_too_short = num_words < self.min_words
        is_too_long = num_words > self.max_words
        has_profanity = bool(re.search(r"\b(fuck|shit|damn|bitch)\b", text.lower()))
        is_toxic = score["toxicity"] > self.toxicity_threshold

        input_tokens = self.tokenizer(
            text, return_tensors="pt"
        ).input_ids.shape[-1]
        # Cost estimate: tokens × $0.0001
        cost = input_tokens * 1e-4

        log_metrics(
            f"Detoxify",
            input_tokens=input_tokens,
            cost_usd=cost,
            _start_=_start_,
            is_safe=not (is_toxic or is_too_short or is_too_long or has_profanity),
            toxicity=score["toxicity"],
        )

        return {
            "is_safe": not (is_toxic or is_too_short or is_too_long or has_profanity),
            "toxicity": score["toxicity"],
            "too_short": is_too_short,
            "too_long": is_too_long,
            "profanity": has_profanity
        }
