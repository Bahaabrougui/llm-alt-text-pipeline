#!/bin/sh

# Set vars
RG=psi
APP_NAME=blip2-serve-app
ENV_NAME=container-app-env
IDENTITY_NAME=alttext-mi
ACR_SERVER=psiacr.azurecr.io
IMAGE_NAME=psiacr.azurecr.io/blip-serve:0.0.1
WORKLOAD_PROFILE=NC8as-T4

# Get MI resource ID and client ID
MI_ID=$(az identity show -g $RG -n $IDENTITY_NAME --query id -o tsv)

# Create the container app
az containerapp create \
  --name $APP_NAME \
  --resource-group $RG \
  --environment $ENV_NAME \
  --image $IMAGE_NAME \
  --workload-profile-name "$WORKLOAD_PROFILE" \
  --memory "32.0Gi" \
  --cpu "4.0" \
  --target-port 80 \
  --ingress external \
  --user-assigned "$MI_ID" \
  --registry-server $ACR_SERVER \
  --registry-identity "$MI_ID" \
  --env-vars BLIP_PROMPT_VERSION=v2


