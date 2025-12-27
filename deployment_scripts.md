# Deployment Scripts Archive

This document contains the utility scripts used to deploy and configure the project in Azure.

## 1. deploy_cloud.sh
Used to provision the Function App and publish code.

```bash
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
read -r -s -p "Connection String: " SQL_CONN_STRING
echo ""
if [ -z "$SQL_CONN_STRING" ]; then
    echo "Error: Connection string cannot be empty."
    exit 1
fi

# 3. Create Function App
echo "--> Creating Function App (Consumption Plan)..."
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
cd azure-function-sql-trigger
# Remove local venv from upload if it exists (func publish handles this usually, but good to be safe)
func azure functionapp publish "$FUNCTION_APP_NAME"

echo "=== Deployment Complete! ==="
echo "Function URL: https://$FUNCTION_APP_NAME.azurewebsites.net/api/HttpTriggerTest?name=CloudUser"
```

## 2. setup_cloud_db.py
Used to create the SQL Schema (Tables) in the cloud database.

```python
import pyodbc
import sys
import os

# Cloud Connection String
# Requires 'SQL_PASSWORD' environment variable
password = os.environ.get("SQL_PASSWORD")
if not password:
    print("Error: SQL_PASSWORD environment variable is not set.")
    sys.exit(1)

CONN_STR = f"Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:alexbeginner.database.windows.net,1433;Database=alexbeginner;Uid=CloudSA8c3bcbfd;Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

def init_cloud_db():
    print("Connecting to Cloud DB 'alexbeginner'...")
    try:
        conn = pyodbc.connect(CONN_STR, autocommit=True)
        cursor = conn.cursor()
        
        # Create Table
        print("Checking for 'AccessLogs' table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='AccessLogs' AND xtype='U')
            CREATE TABLE AccessLogs (
                Id INT IDENTITY(1,1) PRIMARY KEY,
                [User] NVARCHAR(100),
                Timestamp DATETIME DEFAULT GETDATE()
            )
        """)
        print("[PASS] Table 'AccessLogs' created successfully in the Cloud.")
        
        conn.close()
    except Exception as e:
        print(f"\n[FAIL] Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_cloud_db()
```

## 3. verify_cloud_data.py
Used to query the cloud database and verify data persistence.

```python
import pyodbc
import os
import sys

# Cloud Connection String
password = os.environ.get("SQL_PASSWORD")
if not password:
    print("Error: SQL_PASSWORD environment variable is not set.")
    sys.exit(1)

CONN_STR = f"Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:alexbeginner.database.windows.net,1433;Database=alexbeginner;Uid=CloudSA8c3bcbfd;Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

try:
    print("Connecting to Cloud DB to verify data...")
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    
    print("--- Reading from Cloud AccessLogs ---")
    cursor.execute("SELECT TOP 5 * FROM AccessLogs ORDER BY Timestamp DESC")
    rows = cursor.fetchall()
    
    for row in rows:
        print(row)
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
```
