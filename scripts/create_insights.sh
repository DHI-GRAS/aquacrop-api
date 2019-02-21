#!/usr/bin/env bash
set -e

AZURE_GROUP_NAME=$1
AZURE_FUNCTION_APP_NAME=$2
AZURE_LOCATION=$3
AZURE_INSIGHTS=$4

az resource create \
    --resource-group $AZURE_GROUP_NAME \
    --resource-type "Microsoft.Insights/components" \
    --name $AZURE_INSIGHTS \
    --location $AZURE_LOCATION \
    --properties '{"ApplicationType":"General"}' \
    --output table


INSTRUMENTATION_KEY="$(az resource show \
    --resource-group $AZURE_GROUP_NAME \
    --name $AZURE_INSIGHTS \
    --resource-type 'Microsoft.Insights/components' \
    --query properties.InstrumentationKey)"

# remove quotes around key
INSTRUMENTATION_KEY="${INSTRUMENTATION_KEY%\"}"
INSTRUMENTATION_KEY="${INSTRUMENTATION_KEY#\"}"

az functionapp config appsettings set \
    --resource-group $AZURE_GROUP_NAME \
    --name $AZURE_FUNCTION_APP_NAME \
    --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY \
    --output table
