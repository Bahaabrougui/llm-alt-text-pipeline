import time

import requests
import torch
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration

from app.utils.utils import log_metrics, log_info_message

CACHE_DIR = "/home/site/models_cache/blip2"


class ImageCaptioner:
    def __init__(self, model_name="Salesforce/blip2-opt-2.7b"):
        log_info_message(f"✅ Initializing model: {model_name}")
        # Init processor
        self.processor = Blip2Processor.from_pretrained(
            model_name,
            use_fast=True,
            cache_dir=CACHE_DIR
        )
        # Load weights
        self.model = Blip2ForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            cache_dir=CACHE_DIR
        )

    def generate_caption(
            self,
            image_path: str,
            is_url: bool = False,
            max_tokens=30,
    ) -> str:
        _start_ = time.time()
        if is_url:
            image = Image.open(
                requests.get(image_path, stream=True).raw
            ).convert("RGB")
        else:
            image = Image.open(image_path).convert('RGB')
        prompt = "Describe the image for use as alt text in 1 sentence."
        inputs = self.processor(
            images=image,
            text=prompt,
            return_tensors="pt"
        )
        # Debug
        log_info_message(f"BLIP2 Inputs: {list(inputs.keys())}")
        # Move inputs to model device (Azure functions is CPU-only)
        # inputs = {k: v.to("cpu") for k, v in inputs.items()}

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
            )
            caption = self.processor.decode(
                output[0],
                skip_special_tokens=True,
            ).strip()
            log_info_message(f"Output tokens: {output}")
            log_info_message(f"Decoded: {caption}")

        if caption == prompt:
            raise ValueError("Prompt mirrored as caption..")

        # Tokens count
        input_tokens = self.processor.tokenizer(
            prompt, return_tensors="pt"
        ).input_ids.shape[-1]
        output_tokens = self.processor.tokenizer(
            self.processor.decode(output[0], skip_special_tokens=True),
            return_tensors="pt"
        ).input_ids.shape[-1]

        # Cost estimate: tokens × $0.0001
        cost = (input_tokens or 0 + output_tokens) * 1e-4

        log_metrics(
            "Blip2",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            _start_=_start_,
            image_path=image_path,
            caption=caption,
        )

        return caption
