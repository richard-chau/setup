# Azure Function Cloud Deployment Project

This repository contains a complete Azure Function application with SQL database integration, including deployment scripts, verification tools, and comprehensive documentation.

## Project Structure

```
.
├── azure-function-sql-trigger/   # Main Azure Function application
│   ├── HttpTriggerTest/          # HTTP trigger function
│   ├── Shared/                   # Shared database management code
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # Detailed function app documentation
├── deploy_cloud.sh               # Cloud deployment automation script
├── github_setup.sh               # GitHub repository setup script
├── setup_swap.sh                 # Swap space configuration script
├── setup_cloud_db.py             # Cloud database initialization script
├── verify_cloud_data.py          # Cloud database verification script
├── deployment_scripts.md         # Archive of deployment scripts and commands
├── command_log.md                # Complete command history for reference
└── project_requirements.md       # Project requirements and architecture (Chinese)

```

## Quick Start

### Local Development

1. **Prerequisites**: Install Docker, Python 3.11+, and Azure Functions Core Tools
2. **Navigate to function app**: `cd azure-function-sql-trigger`
3. **Follow the README**: Complete instructions are in `azure-function-sql-trigger/README.md`

### Cloud Deployment

1. **Set environment variables**:
   ```bash
   export SQL_PASSWORD="your_secure_password"
   ```

2. **Run deployment script**:
   ```bash
   ./deploy_cloud.sh
   ```

3. **Initialize cloud database**:
   ```bash
   python3 setup_cloud_db.py
   ```

4. **Verify deployment**:
   ```bash
   python3 verify_cloud_data.py
   ```

## Documentation

- **[Azure Function README](azure-function-sql-trigger/README.md)**: Local development, testing, and project structure
- **[Project Requirements](project_requirements.md)**: Architecture decisions and cloud deployment summary (中文)
- **[Deployment Scripts](deployment_scripts.md)**: Archived deployment scripts with explanations
- **[Command Log](command_log.md)**: Complete command history from setup to deployment

## Security

- All deployment scripts use **environment variables** for credentials
- Connection strings are never hardcoded in production scripts
- See individual README files for security best practices

## Features

- ✅ HTTP-triggered Azure Function
- ✅ SQL Database integration with connection pooling
- ✅ Local development with Docker (Azure SQL Edge + Azurite)
- ✅ Production deployment to Azure (Consumption Plan)
- ✅ Comprehensive verification scripts
- ✅ Automated deployment scripts

## Requirements

- Python 3.11+
- Azure CLI
- Azure Functions Core Tools
- Docker (for local development)
- ODBC Driver 18 for SQL Server

## License

This is a demonstration project for learning Azure Functions and cloud deployment.
