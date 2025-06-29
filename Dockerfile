FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    HF_HOME=/Models

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Copy app files
COPY . /home/site/wwwroot

# Preload models during build
RUN pip install -r /home/site/wwwroot/requirements.txt && \
    python -c "from transformers import Blip2Processor; \
               Blip2Processor.from_pretrained('Salesforce/blip2-opt-2.7b', use_fast=True);"

