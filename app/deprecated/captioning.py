import time

import requests
import torch
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

from app.utils.utils import log_metrics, log_info_message

CACHE_DIR = "/home/site/models_cache/blip-base"


class ImageCaptioner:
    def __init__(self, model_name="Salesforce/blip-image-captioning-base"):
        log_info_message(f"✅ Initializing model: {model_name}")
        self.model_name = model_name
        # Init processor
        self.processor = BlipProcessor.from_pretrained(
            model_name,
            use_fast=True,
            cache_dir=CACHE_DIR
        )
        # Load weights
        self.model = BlipForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            cache_dir=CACHE_DIR
        )

    def generate_caption(
            self,
            image_path: str,
            is_url: bool = False,
            max_tokens=100,
    ) -> str:
        _start_ = time.time()
        if is_url:
            image = Image.open(
                requests.get(image_path, stream=True).raw
            ).convert("RGB")
        else:
            image = Image.open(image_path).convert('RGB')
        prompt = None
        inputs = self.processor(
            images=image,
            text=prompt,
            return_tensors="pt"
        )

        # Move inputs to model device (Azure functions is CPU-only)
        # inputs = {k: v.to("cpu") for k, v in inputs.items()}

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
            )
            # Decode caption
            caption = self.processor.decode(
                output[0],
                skip_special_tokens=True,
            ).strip()

        # Tokens count
        input_tokens = 0 if prompt is None else inputs["input_ids"].shape[1]
        output_tokens = output[0].shape[-1]
        # Cost estimate: tokens × $0.0001
        cost = (input_tokens or 0 + output_tokens) * 1e-4

        log_metrics(
            self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            _start_=_start_,
            image_path=image_path,
            caption=caption,
        )

        return caption
