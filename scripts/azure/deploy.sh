#!/bin/bash
set -e

# --- Configuration ---
RESOURCE_GROUP="beginner"
LOCATION="westus2"
STORAGE_ACCOUNT="beginnerbf9b"
# Generate a unique name for the function app to avoid conflicts
RANDOM_ID=$(openssl rand -hex 3)
FUNCTION_APP_NAME="sql-trigger-$RANDOM_ID"
PYTHON_VERSION="3.11" # Azure Functions valid version

echo "=== Azure Cloud Deployment ==="
echo "Target Resource Group: $RESOURCE_GROUP"
echo "Target Storage Account: $STORAGE_ACCOUNT"
echo "New Function App Name: $FUNCTION_APP_NAME"
echo "Plan: Consumption (Serverless/Free Tier)"
echo "------------------------------"

# 1. Verify Prerequisites
echo "--> Checking resources..."
if ! az group show --name "$RESOURCE_GROUP" &>/dev/null; then
    echo "Error: Resource group '$RESOURCE_GROUP' not found."
    exit 1
fi

# 2. Get SQL Credentials safely
echo ""
echo "Please enter the SQL Connection String for the CLOUD database."
echo "Format: Driver={ODBC Driver 18 for SQL Server};Server=tcp:alexbeginner.database.windows.net,1433;Database=alexbeginner;Uid=...;Pwd=...;"
read -s -p "Connection String: " SQL_CONN_STRING
echo ""
if [ -z "$SQL_CONN_STRING" ]; then
    echo "Error: Connection string cannot be empty."
    exit 1
fi

# 3. Create Function App
echo "--> Creating Function App (Consumption Plan)..."
# Note: --consumption-plan-location is required for Windows, but for Linux we use --os-type Linux and it defaults to consumption if no plan is specified or if we create a dynamic plan.
# However, 'az functionapp create' creates a plan automatically if not specified.
# To be explicit about "Free" (Consumption), we use --consumption-plan-location westeurope etc. 
# But better: just let it create a serverless plan.
az functionapp create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$FUNCTION_APP_NAME" \
    --storage-account "$STORAGE_ACCOUNT" \
    --runtime python \
    --runtime-version "$PYTHON_VERSION" \
    --os-type Linux \
    --consumption-plan-location "$LOCATION" \
    --functions-version 4

# 4. Configure App Settings
echo "--> Configuring App Settings..."
az functionapp config appsettings set \
    --name "$FUNCTION_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings "SqlConnectionString=$SQL_CONN_STRING" "SCM_DO_BUILD_DURING_DEPLOYMENT=true"

# 5. Publish Code
echo "--> Publishing Code..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Assuming script is in scripts/azure/, project root is ../../
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_ROOT/azure-function-sql-trigger" || { echo "Error: Project directory not found!"; exit 1; }

# Remove local venv from upload if it exists (func publish handles this usually, but good to be safe)
func azure functionapp publish "$FUNCTION_APP_NAME"

echo "=== Deployment Complete! ==="
echo "Function URL: https://$FUNCTION_APP_NAME.azurewebsites.net/api/HttpTriggerTest?name=CloudUser"
