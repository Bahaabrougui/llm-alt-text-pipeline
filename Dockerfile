FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    HF_HOME=/Models

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Copy app files
COPY . /home/site/wwwroot

# Create model offload folder
RUN rm -rf /home/site/models_cache/blip-base  && mkdir -p /home/site/models_cache/blip-base && \
    chmod -R 777 /home/site/models_cache/blip-base

# Preload models during build
RUN pip install -r /home/site/wwwroot/requirements.txt && \
    python -c "from transformers import BlipProcessor; \
               BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base', use_fast=True, cache_dir='/home/site/models_cache/blip-base');"
