import pyodbc
import time
import sys

# Local Docker connection string
CONN_STR = "Driver={ODBC Driver 18 for SQL Server};Server=127.0.0.1,1433;Uid=sa;Pwd=Strong!Pass123;Encrypt=no;TrustServerCertificate=yes;Connection Timeout=30;"

print("Waiting for SQL Server to warm up...")
time.sleep(10) # Give Docker a moment

def init_db():
    try:
        # 1. Connect to 'master' to create the DB
        conn = pyodbc.connect(CONN_STR + "Database=master;", autocommit=True)
        cursor = conn.cursor()
        
        # Check if DB exists
        cursor.execute("SELECT name FROM sys.databases WHERE name = 'FunctionDB'")
        if not cursor.fetchone():
            print("Creating database 'FunctionDB'...")
            cursor.execute("CREATE DATABASE FunctionDB")
        else:
            print("Database 'FunctionDB' already exists.")
        
        cursor.close()
        conn.close()

        # 2. Connect to 'FunctionDB' to create Table
        conn = pyodbc.connect(CONN_STR + "Database=FunctionDB;", autocommit=True)
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
        print("[PASS] Table 'AccessLogs' is ready.")
        
        conn.close()
        print("\nSUCCESS: Local SQL Environment is fully prepared.")
        
    except Exception as e:
        print(f"\n[FAIL] Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
