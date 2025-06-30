from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


class Translator:
    def __init__(self, target_lang="fr"):
        self.device = torch.device(
            "mps" if torch.backends.mps.is_available() else "cpu"
        )
        model_name = f"Helsinki-NLP/opus-mt-en-{target_lang}"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model = self.model.to(self.device)

    def translate(self, text: str) -> str:
        tokens = self.tokenizer(text, return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            translated = self.model.generate(**tokens)
        return self.tokenizer.decode(translated[0], skip_special_tokens=True)
