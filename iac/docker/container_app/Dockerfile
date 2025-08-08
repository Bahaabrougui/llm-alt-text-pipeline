FROM pytorch/pytorch:2.7.1-cuda12.6-cudnn9-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y git

COPY . /home/fastapi_app
WORKDIR /home/fastapi_app

# Create model cache folder
RUN rm -rf /home/fastapi_app/models_cache/blip2  && mkdir -p /home/fastapi_app/models_cache/blip2 && \
    chmod -R 777 /home/fastapi_app/models_cache/blip2

# Preload processor during build
RUN pip install -r /home/fastapi_app/requirements/container_app_requirements.txt && \
    python -c "from transformers import Blip2Processor; \
               Blip2Processor.from_pretrained('Salesforce/blip2-opt-2.7b', use_fast=True, cache_dir='/home/fastapi_app/models_cache/blip2');"

CMD ["gunicorn", "app.api.captioning.captioner:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80", "--workers", "1", "--threads", "4"]
