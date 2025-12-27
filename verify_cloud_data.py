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
    
    if not rows:
        print("No records found.")
    for row in rows:
        print(row)
        
    conn.close()
    print("--- Verification Complete ---")
except Exception as e:
    print(f"Error: {e}")