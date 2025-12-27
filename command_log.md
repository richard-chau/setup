# Complete Command Log (2025-12-27)

This log contains the key commands executed to set up, verify, and deploy the project.

## 1. System Dependencies & Environment
```bash
# Install Python Venv and ODBC Headers
sudo apt update && sudo apt install -y python3.12-venv python3-pip unixodbc-dev

# Install Microsoft ODBC Driver 18 (Ubuntu 22.04)
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Create Local Python Environment
cd azure-function-sql-trigger
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Local Infrastructure (Docker)
```bash
# Start Azurite (Blob Simulator)
docker run -d -p 10000:10000 -p 10001:10001 -p 10002:10002 --name azurite mcr.microsoft.com/azure-storage/azurite

# Start Azure SQL Edge (SQL Simulator)
docker run --cap-add SYS_PTRACE -e 'ACCEPT_EULA=1' -e 'MSSQL_SA_PASSWORD=Strong!Pass123' -p 1433:1433 --name sql_server -d mcr.microsoft.com/azure-sql-edge
```

## 3. Local Verification
```bash
# Verify SQLite
python3 verify_sqlite.py

# Verify Blob Storage (Azurite)
python3 verify_blob.py

# Initialize Local SQL Database
python3 setup_local_db.py

# Start Function Locally (Background)
setsid func start > func.log 2>&1 &

# Test Local Function
curl "http://localhost:7071/api/HttpTriggerTest?name=LocalUser"
```

## 4. Cloud Management
```bash
# Login to Azure
az login --use-device-code

# Check Existing Resources
az group list -o table
az storage account list -o table
az sql server list -o table

# Configure SQL Firewall (Allow Azure + Local IP)
az sql server firewall-rule create --resource-group beginner --server alexbeginner --name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
az sql server firewall-rule create --resource-group beginner --server alexbeginner --name DevBox --start-ip-address 141.148.150.146 --end-ip-address 141.148.150.146

# Reset SQL Admin Password (after disabling AD-only)
az sql server update --name alexbeginner --resource-group beginner --admin-password "<REDACTED_PASSWORD>"

# Get Function Default Key
az functionapp function keys list --resource-group beginner --name sql-trigger-64568d --function-name HttpTriggerTest --query "default" -o tsv
```

## 5. Cloud Verification
```bash
# Initialize Cloud Table
python3 setup_cloud_db.py

# Test Cloud Function
curl "https://sql-trigger-64568d.azurewebsites.net/api/httptriggertest?code=<FUNCTION_KEY_HIDDEN>&name=CloudUser"
```
