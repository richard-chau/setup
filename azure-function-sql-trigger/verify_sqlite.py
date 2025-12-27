import sqlite3
import os

db_file = "local_test.db"

print(f"--- Testing SQLite (Local File: {db_file}) ---")

try:
    # 1. Connect (Creates file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 2. Create Table
    cursor.execute("CREATE TABLE IF NOT EXISTS Logs (id INTEGER PRIMARY KEY, message TEXT)")
    
    # 3. Insert Data
    cursor.execute("INSERT INTO Logs (message) VALUES (?)", ("Hello from SQLite!",))
    conn.commit()
    print("[PASS] Inserted record.")

    # 4. Read Data
    cursor.execute("SELECT * FROM Logs")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  -> Read Record: {row}")
    
    conn.close()
    print("[PASS] SQLite verification successful.")

except Exception as e:
    print(f"[FAIL] SQLite error: {e}")
finally:
    # Cleanup
    if os.path.exists(db_file):
        os.remove(db_file)
        print("[INFO] Cleaned up test file.")
