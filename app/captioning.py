# app/captioning.py
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
import torch


class ImageCaptioner:
    def __init__(self, model_name="Salesforce/blip2-opt-2.7b"):
        self.device = torch.device(
            "mps" if torch.backends.mps.is_available() else "cpu"
        )
        self.processor = Blip2Processor.from_pretrained(model_name, use_fast=True)
        self.model = Blip2ForConditionalGeneration.from_pretrained(
            model_name, device_map="auto", torch_dtype=torch.float16
        )
        self.model = self.model.to(self.device)

    def generate_caption(self, image_path: str, max_tokens=30) -> str:
        image = Image.open(image_path).convert('RGB')
        prompt = ("Describe the image for use as alt text in 1 sentence. "
                  "Be concise, informative, and neutral.")
        inputs = self.processor(
            image, prompt, return_tensors="pt"
        ).to(self.device)
        with torch.no_grad():
            output = self.model.generate(**inputs, max_new_tokens=max_tokens)
            caption = self.processor.decode(output[0], skip_special_tokens=True)
        return caption.strip()
