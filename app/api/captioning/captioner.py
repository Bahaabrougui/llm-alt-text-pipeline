import os
import time

import torch
import yaml
from PIL import Image
from fastapi import FastAPI, UploadFile, File, Query
from transformers import Blip2Processor, Blip2ForConditionalGeneration

from app.define import CAPTIONING_MODEL_NAME, MODEL_CACHE_DIR, \
    CAPTIONING_MODEL_ROUTE
from app.utils.utils import log_metrics

app = FastAPI()

if torch.cuda.is_available():
    device = "cuda"
else:
    raise RuntimeError("GPU not supported, check your configuration.")

# Load prompts
with open("prompts/blip.yaml", "r") as blip_prompt_file:
    blip_prompt_file_content = yaml.safe_load(blip_prompt_file)
    _prompt = blip_prompt_file_content["blip"][os.environ["BLIP_PROMPT_VERSION"]]

processor = Blip2Processor.from_pretrained(
    CAPTIONING_MODEL_NAME,
    use_fast=True,
    cache_dir=MODEL_CACHE_DIR,
)
model = Blip2ForConditionalGeneration.from_pretrained(
    CAPTIONING_MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto",
    cache_dir=MODEL_CACHE_DIR,
).to(device)


@app.post(CAPTIONING_MODEL_ROUTE)
async def caption_image(
        file: UploadFile = File(...),
        max_tokens: int = Query(100),
):
    _start_ = time.time()
    image = Image.open(file.file).convert("RGB")
    inputs = processor(
        images=image,
        text=_prompt,
        return_tensors="pt",
    ).to(device)
    output = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
    )
    caption = processor.decode(
        output[0],
        skip_special_tokens=True,
    ).strip()
    # Tokens count
    input_tokens = 0 if _prompt is None else inputs["input_ids"].shape[1]
    output_tokens = output[0].shape[-1]
    # Cost estimate: tokens × $0.0001
    cost = (input_tokens or 0 + output_tokens) * 1e-4

    log_metrics(
        CAPTIONING_MODEL_NAME,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost,
        _start_=_start_,
        image_path=file.filename,
        caption=caption,
    )
    return {"caption": caption}


@app.post("/health")
async def health_check():
    return {"status": "ok"}