# Azure Function SQL Trigger (Local Dev Ready)

This project is a fully functional Azure Function template that logs access to a SQL Database. It is currently configured for **Zero-Config Local Development** using Docker.

## Quick Start (Local)

1.  **Ensure Docker is Running**.
2.  **Activate Environment**:
    ```bash
    source .venv/bin/activate
    ```
3.  **Start SQL Server (if not already running)**:
    ```bash
    docker start sql_server || docker run --cap-add SYS_PTRACE -e 'ACCEPT_EULA=1' -e 'MSSQL_SA_PASSWORD=Strong!Pass123' -p 1433:1433 --name sql_server -d mcr.microsoft.com/azure-sql-edge
    ```
4.  **Run the Function**:
    ```bash
    func start
    ```
5.  **Test**:
    - Request: `curl "http://localhost:7071/api/HttpTriggerTest?name=LocalUser"`
    - Verify DB: `python3 verify_data.py`

## Project Structure

- `HttpTriggerTest/`: The entry point for the HTTP Function.
- `Shared/`: Common logic and `db_manager.py` (Connection pooling).
- `setup_local_db.py`: One-time script to create the local DB and tables.
- `verify_data.py`: Script to query the local database and check results.

## Cloud Deployment

When moving to production:
1. Update `SqlConnectionString` in Azure Portal (App Settings) to your real Azure SQL string.
2. The code will automatically use the Azure SQL database instead of the local Docker container.