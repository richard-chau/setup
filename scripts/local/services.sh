#!/bin/bash

# Usage: ./manage_local_env.sh [start|stop|restart|clean]

ACTION=$1

if [ -z "$ACTION" ]; then
    echo "Usage: ./manage_local_env.sh [start|stop|restart|clean]"
    exit 1
fi

echo "=== Local Environment Manager: $ACTION ==="

case "$ACTION" in
    start)
        echo "Starting SQL Server..."
        docker start sql_server || docker run --cap-add SYS_PTRACE -e 'ACCEPT_EULA=1' -e 'MSSQL_SA_PASSWORD=Strong!Pass123' -p 1433:1433 --name sql_server -d mcr.microsoft.com/azure-sql-edge
        echo "Starting Azurite..."
        docker start azurite || docker run -p 10000:10000 -p 10001:10001 -p 10002:10002 --name azurite -d mcr.microsoft.com/azure-storage/azurite
        ;;
    stop)
        echo "Stopping containers..."
        docker stop sql_server azurite
        ;;
    restart)
        echo "Restarting containers..."
        docker restart sql_server azurite
        ;;
    clean)
        echo "WARNING: This will DELETE all local data (SQL tables and Blobs)."
        read -p "Are you sure? (y/N) " confirm
        if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
            docker stop sql_server azurite
            docker rm sql_server azurite
            
            # Resolve path relative to script location
            SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
            PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
            
            # Optional: Remove local SQLite/Log files if any
            rm -f "$PROJECT_ROOT/azure-function-sql-trigger/local_test.db"
            echo "Clean complete. Run '$0 start' to recreate fresh containers."
        else
            echo "Operation cancelled."
        fi
        ;;
    *)
        echo "Invalid action: $ACTION"
        exit 1
        ;;
esac

echo "Done."
