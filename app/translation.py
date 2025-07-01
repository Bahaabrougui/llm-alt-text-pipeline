import time

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from app.utils.utils import log_metrics


class Translator:
    def __init__(self, target_lang="fr"):
        self.target_lang = target_lang
        self.device = torch.device(
            "mps" if torch.backends.mps.is_available() else "cpu"
        )
        model_name = f"Helsinki-NLP/opus-mt-en-{target_lang}"
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, use_fast=True
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model = self.model.to(self.device)

    def translate(self, text: str) -> str:
        _start_ = time.time()
        tokens = self.tokenizer(text, return_tensors="pt", padding=True).to(
            self.device
        )
        with torch.no_grad():
            translated = self.model.generate(**tokens)

        # Tokens count
        input_tokens = self.tokenizer(
            text, return_tensors="pt"
        ).input_ids.shape[-1]
        output_tokens = self.tokenizer(
            translated, return_tensors="pt"
        ).input_ids.shape[-1]

        # Cost estimate: tokens × $0.0001
        cost = (input_tokens or 0 + output_tokens) * 1e-4

        log_metrics(
            f"Helsinki-NLP",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            _start_=_start_,
            target_lang=self.target_lang
        )

        return self.tokenizer.decode(translated[0], skip_special_tokens=True)
