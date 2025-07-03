FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    HF_HOME=/Models

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Copy app files
COPY . /home/site/wwwroot

# Create model offload folder
RUN rm -rf /home/site/models_cache/blip2  && mkdir -p /home/site/models_cache/blip2 && \
    chmod -R 777 /home/site/models_cache/blip2

# Preload models during build
RUN pip install -r /home/site/wwwroot/requirements.txt && \
    python -c "from transformers import Blip2Processor; \
               Blip2Processor.from_pretrained('Salesforce/blip2-opt-2.7b', use_fast=True, cache_dir='/home/site/models_cache/blip2');"
