#!/bin/sh

# Set vars
RG=psi
SUBSCRIPTION=""
STORAGE_ACCOUNT=privateappstorage
KV=""
DB_HOST=""
APP_NAME=$APP_NAME
ENV_NAME=my-linux-plan
IDENTITY_NAME=alttext-mi
IMAGE_TAG=0.0.3
IMAGE_NAME=psiacr.azurecr.io/alttext-func:$IMAGE_TAG

az provider register --namespace Microsoft.Web

az functionapp plan create   --name $ENV_NAME   --resource-group $RG   --location westeurope   --is-linux   --sku EP2

az functionapp create   --name $APP_NAME  \
 --storage-account privateappstorage \
 --resource-group psi   \
 --runtime python   \
 --runtime-version 3.11   \
 --functions-version 4   \
 --image $IMAGE_NAME   \
 --assign-identity $(az identity show -g psi -n $IDENTITY_NAME --query id -o tsv) \
 --plan $ENV_NAME

# Configure app to auth to ACR with user-assigned MI
az resource update \
--ids /subscriptions/$SUBSCRIPTION/resourceGroups/psi/providers/Microsoft.Web/sites/$APP_NAME/config/web \
--set properties.acrUseManagedIdentityCreds=True \
--set properties.acrUserManagedIdentityID=$(az identity show -g psi -n $IDENTITY_NAME --query clientId -o tsv)

# Create KV connection using user-assigned MI, requires UA admin role
az functionapp connection create keyvault -g psi -n $APP_NAME --tg psi \
--vault psikv --client-type python \
--user-identity client-id=$(az identity show -g psi -n $IDENTITY_NAME --query clientId -o tsv) subs-id=$SUBSCRIPTION

# Get model server url
MODEL_SERVER_CONTAINER_APP="blip2-serve-app"

# Requires system-assigned MSI
az functionapp config appsettings set \
  --name $APP_NAME \
  --resource-group $RG \
  --settings \
    BlobStorageConnectionString="@Microsoft.KeyVault(SecretUri=https://$KV.vault.azure.net/secrets/privateappstorage-sas/)" \
    AzureWebJobsStorage="@Microsoft.KeyVault(SecretUri=https://$KV.vault.azure.net/secrets/privateappstorage-sas/)" \
    HF_HOME=/Models \
    FUNCTIONS_WORKER_RUNTIME=python \
    WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
    KEY_VAULT_URL="https://$KV.vault.azure.net/" \
    DB_HOST=$DB_HOST \
    AZURE_OPENAI_API_ENDPOINT="https://openai-sc-instance.openai.azure.com/" \
    AZURE_OPENAI_API_VERSION="2023-05-15" \
    AZURE_OPENAI_DEPLOYMENT_NAME="gpt-35-turbo-instruct" \
    GPT_PROMPT_VERSION="v1" \
    CAPTIONING_MODEL_SERVER="https://$(az containerapp show \
  --name "$MODEL_SERVER_CONTAINER_APP" \
  --resource-group $RG \
  --query properties.configuration.ingress.fqdn \
  -o tsv)"

az account get-access-token --resource https://cognitiveservices.azure.com/ --query accessToken -o tsv | \
curl -X GET "https://openai-sc-instance.openai.azure.com/openai/deployments" \
  -H "Authorization: Bearer $(cat -)" \
  -H "Content-Type: application/json"


az cognitiveservices account deployment list \
  --resource-group $RG \
  --name openai-sc-instance

  az openai api show \
  --resource-group $RG \
  --name openai-sc-instance