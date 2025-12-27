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