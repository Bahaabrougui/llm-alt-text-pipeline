FROM pytorch/pytorch:2.7.1-cuda12.6-cudnn9-runtime

# Install system dependencies
RUN apt-get update && apt-get install -y git

COPY . /home/app
WORKDIR /home/app

# Create model cache folder
RUN rm -rf /home/app/models_cache/blip2  && mkdir -p /home/app/models_cache/blip2 && \
    chmod -R 777 /home/app/models_cache/blip2

# Preload processor during build
RUN pip install -r /home/app/requirements/container_app_requirements.txt && \
    python -c "from transformers import Blip2Processor; \
               Blip2Processor.from_pretrained('Salesforce/blip2-opt-2.7b', use_fast=True, cache_dir='/home/app/models_cache/blip2');"

CMD ["gunicorn", "app.api.captioning.captioner:app", "-k", "uvicorn.workers.UvicornWorker", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]
