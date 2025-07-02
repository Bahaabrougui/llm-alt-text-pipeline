import time

import torch
from PIL import Image
from huggingface_hub import snapshot_download
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from accelerate import init_empty_weights, load_checkpoint_and_dispatch

from app.utils.utils import log_metrics


class ImageCaptioner:
    def __init__(self, model_name="Salesforce/blip2-opt-2.7b"):
        # Download the model repo to a local folder (cached during image build)
        local_model_path = snapshot_download(
            model_name,
            local_dir="/home/site/models_cache/blip2",
            local_dir_use_symlinks=False,
        )
        # Init processor
        self.processor = Blip2Processor.from_pretrained(
            model_name,
            use_fast=True,
        )
        # Init empty model on meta
        with init_empty_weights():
            model = Blip2ForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16
            )
        # Load weights and dispatch properly
        self.model = load_checkpoint_and_dispatch(
            model,
            checkpoint=local_model_path,
            device_map="sequential",
            # required for disk/cpu fallback
            offload_folder="/home/site/models_offload/blip2",
            offload_state_dict=True,
        )

    def generate_caption(self, image_path: str, max_tokens=30) -> str:
        _start_ = time.time()
        image = Image.open(image_path).convert('RGB')
        prompt = ("Describe the image for use as alt text in 1 sentence. "
                  "Be concise, informative, and neutral. "
                  "Be in the range of max_words=25 and min_words=3.")
        inputs = self.processor(
            image, prompt, return_tensors="pt"
        )
        # Move inputs to model device (for accelerate offloading models)
        device = next(self.model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            output = self.model.generate(**inputs, max_new_tokens=max_tokens)
            caption = self.processor.decode(
                output[0],
                skip_special_tokens=True,
            )

        # Tokens count
        input_tokens = self.processor.tokenizer(
            prompt, return_tensors="pt"
        ).input_ids.shape[-1]
        output_tokens = output.shape[-1] - input_tokens

        # Cost estimate: tokens × $0.0001
        cost = (input_tokens or 0 + output_tokens) * 1e-4

        log_metrics(
            "Blip2",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            _start_=_start_,
            image_path=image_path
        )

        return caption.strip()
