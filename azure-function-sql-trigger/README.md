# Azure Function SQL Trigger (Local Dev Ready)

This project is a fully functional Azure Function template that logs access to a SQL Database. It is currently configured for **Zero-Config Local Development** using Docker.

## Prerequisites

### 1. System Drivers (SQL Server)
The `pyodbc` library requires the Microsoft ODBC driver:
```bash
# Ubuntu 22.04 example
sudo apt-get update && sudo apt-get install -y unixodbc-dev
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

### 2. Global Tools (Functions & Azurite)
```bash
# Install Azure Functions Core Tools & Azurite Simulator
npm install -g azure-functions-core-tools@4 azurite
```

## Local Services (Docker)

Launch the required infrastructure with these commands:

### Automated Management (Recommended)
Use the provided helper script in the root directory:
```bash
# Start all services
../manage_local_env.sh start

# Stop services when done
../manage_local_env.sh stop
```

### Manual Commands
```bash
# SQL Server (Database)
docker run --cap-add SYS_PTRACE -e 'ACCEPT_EULA=1' -e 'MSSQL_SA_PASSWORD=Strong!Pass123' -p 1433:1433 --name sql_server -d mcr.microsoft.com/azure-sql-edge

# Azurite (Storage Simulator)
docker run -p 10000:10000 -p 10001:10001 -p 10002:10002 --name azurite -d mcr.microsoft.com/azure-storage/azurite
```

## Quick Start (Local)

1.  **Start Services**: Ensure the Docker containers (or standalone services) above are running.
2.  **Environment Setup**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3.  **Configure**: Create `local.settings.json` (use `local.settings.json.sample` as a template).
4.  **Initialize DB**:
    ```bash
    # Creates the 'FunctionDB' and 'AccessLogs' table
    python3 setup_local_db.py
    ```
5.  **Run**:
    ```bash
    func start
    ```
6.  **Test**:
    - Request: `curl "http://localhost:7071/api/HttpTriggerTest?name=LocalUser"`
    - Verify: `python3 verify_data.py`


## Project Structure

- `HttpTriggerTest/`: The entry point for the HTTP Function.
- `Shared/`: Common logic and `db_manager.py` (Connection pooling).
- `setup_local_db.py`: One-time script to create the local DB and tables.
- `verify_data.py`: Script to query the local database and check results.

## Cloud Deployment

When moving to production:
1. Update `SqlConnectionString` in Azure Portal (App Settings) to your real Azure SQL string.
2. The code will automatically use the Azure SQL database instead of the local Docker container.