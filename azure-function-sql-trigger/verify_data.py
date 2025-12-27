import pyodbc

# Local Docker connection string
CONN_STR = "Driver={ODBC Driver 18 for SQL Server};Server=127.0.0.1,1433;Database=FunctionDB;Uid=sa;Pwd=Strong!Pass123;Encrypt=no;TrustServerCertificate=yes;Connection Timeout=30;"

try:
    conn = pyodbc.connect(CONN_STR)
    cursor = conn.cursor()
    
    print("--- Reading from AccessLogs ---")
    cursor.execute("SELECT * FROM AccessLogs")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
