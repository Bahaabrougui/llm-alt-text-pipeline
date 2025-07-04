import time

import torch
from transformers import AutoTokenizer, MarianMTModel

from app.utils.utils import log_metrics, log_info_message


class Translator:
    def __init__(self, target_lang="fr"):
        self.target_lang = target_lang
        self.model_name = f"Helsinki-NLP/opus-mt-en-{target_lang}"
        log_info_message(f"✅ Initializing model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, use_fast=True
        )
        self.model = MarianMTModel.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32
        )

    def translate(self, text: str) -> str:
        # Assert text is str
        assert isinstance(text, str), f"Expected str, got {type(text)}: {text}"
        # Start inference
        _start_ = time.time()
        inputs = self.tokenizer([text], return_tensors="pt", padding=True)

        # Move inputs to model device
        # device = next(self.model.parameters()).device
        # inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            translated = self.model.generate(**inputs)

        # Tokens count
        input_tokens = inputs["input_ids"].shape[-1]
        output_tokens = translated[0].shape[-1]

        # Cost estimate: tokens × $0.0001
        cost = (input_tokens or 0 + output_tokens) * 1e-4

        translated_text = self.tokenizer.decode(
            translated[0], skip_special_tokens=True
        )

        log_metrics(
            self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            _start_=_start_,
            original_text=text,
            translated_text=translated_text,
            target_lang=self.target_lang
        )

        return translated_text
