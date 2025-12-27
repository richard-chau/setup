import sys
import os
import json

# Add current dir to path so Shared can be imported
sys.path.append(os.getcwd())

print("--- Starting Verification ---")

# 1. Import Validation
try:
    from Shared import db_manager
    import pyodbc
    import azure.functions
    print("[PASS] Python environment dependencies (azure-functions, pyodbc) are installed and importable.")
except ImportError as e:
    print(f"[FAIL] Import error: {e}")
    sys.exit(1)

# 2. Configuration & Logic Validation
try:
    with open('local.settings.json', 'r') as f:
        settings = json.load(f)
        conn_str = settings.get("Values", {}).get("SqlConnectionString", "")
        os.environ["SqlConnectionString"] = conn_str
        print("[PASS] Loaded local.settings.json.")
except Exception as e:
    print(f"[FAIL] Could not load settings: {e}")
    sys.exit(1)

print(f"Current Connection String (masked): {conn_str[:20]}...")

# 3. DB Logic Check
try:
    print("Attempting to initialize connection (expecting validation error)...")
    db_manager.get_connection()
    print("[WARN] Connection initialization proceeded without error (Unexpected if using placeholder).")
except ValueError as e:
    if "default placeholder" in str(e):
        print(f"[PASS] Logic Verified: System correctly detected default placeholder credentials.")
        print(f"       Message: {e}")
    else:
        print(f"[FAIL] Unexpected ValueError: {e}")
except Exception as e:
    print(f"[FAIL] Unexpected Error during connection attempt: {type(e).__name__}: {e}")

print("--- Verification Complete ---")
