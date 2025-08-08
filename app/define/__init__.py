# Azure cognitive services scope
AZURE_COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"
INPUT_PRICE_PER_1_K = {
    "gpt-35-turbo-instruct": 0.0015,
    "gpt-4": 0.03,
}
OUTPUT_PRICE_PER_1_K = {
    "gpt-35-turbo-instruct": 0.002,
    "gpt-4": 0.06,
}

# Captioning model
CAPTIONING_MODEL_NAME = "Salesforce/blip2-opt-2.7b"
MODEL_CACHE_DIR = "/home/fastapi_app/models_cache/blip2"
CAPTIONING_MODEL_ROUTE = "/api/caption"

# Application path to avoid relative paths
APPLICATION_PATH_CONTAINER_APP = "/home/fastapi_app/app"
APPLICATION_PATH_FUNCTION_APP = "/home/site/wwwroot/app"
