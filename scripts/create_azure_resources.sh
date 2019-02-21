#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIG_FILE=$DIR/../config.ini
echo "Reading environment variables from $CONFIG_FILE"
source <(grep = $CONFIG_FILE | sed 's/ *= */=/g')

echo "Setting default subscription: $AZURE_SUBSCRIPTION"
az account set -s "$AZURE_SUBSCRIPTION"

echo "Creating resource group '$AZURE_GROUP_NAME' ..."
az group create \
    --name $AZURE_GROUP_NAME \
    --location $AZURE_LOCATION 

echo "Creating storage account '$AZURE_STORAGE_ACCOUNT' in '$AZURE_GROUP_NAME' ..."
az storage account create \
    --name $AZURE_STORAGE_ACCOUNT \
    --location $AZURE_LOCATION \
    --resource-group $AZURE_GROUP_NAME \
    --sku Standard_LRS

echo "Creating '$AZURE_AWAIT_QUEUE_NAME' queue in '$AZURE_STORAGE_ACCOUNT' ..."
az storage queue create \
    --name $AZURE_AWAIT_QUEUE_NAME \
    --account-name $AZURE_STORAGE_ACCOUNT

echo "Creating '$AZURE_DONE_QUEUE_NAME' queue in '$AZURE_STORAGE_ACCOUNT' ..."
az storage queue create \
    --name $AZURE_DONE_QUEUE_NAME \
    --account-name $AZURE_STORAGE_ACCOUNT

echo "Creating functionapp '$AZURE_FUNCTION_APP_NAME' in '$AZURE_GROUP_NAME' ..."
az functionapp create \
    --resource-group $AZURE_GROUP_NAME \
    --os-type Linux \
    --consumption-plan-location $AZURE_LOCATION \
    --runtime python \
    --name $AZURE_FUNCTION_APP_NAME \
    --storage-account $AZURE_STORAGE_ACCOUNT

echo "Creating ApplicationInsights (for logging)"
$DIR/create_insights.sh $AZURE_GROUP_NAME $AZURE_FUNCTION_APP_NAME $AZURE_LOCATION $AZURE_INSIGHTS
