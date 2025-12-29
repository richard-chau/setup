import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def run_test():
    print(f"--- Testing Local GCP Simulator ({BASE_URL}) ---")
    
    # 1. Trigger the Function
    print("[1] Triggering Cloud Run Service...")
    try:
        response = requests.get(f"{BASE_URL}/?name=VerificationUser")
        response.raise_for_status()
        data = response.json()
        print("    [PASS] Request successful.")
        print(f"    Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"    [FAIL] Request failed: {e}")
        return

    # 2. Check Data Consistency (via the Verify Endpoint)
    print("\n[2] Verifying Data Persistence...")
    try:
        response = requests.get(f"{BASE_URL}/verify")
        response.raise_for_status()
        data = response.json()
        
        firestore_logs = data.get("firestore_logs", [])
        storage_files = data.get("storage_files", [])

        print(f"    Firestore Logs Found: {len(firestore_logs)}")
        print(f"    Storage Files Found: {len(storage_files)}")

        if len(firestore_logs) > 0 and len(storage_files) > 0:
            print("    [PASS] Both Firestore and Storage contain data.")
        else:
            print("    [WARN] Data might be missing.")

    except Exception as e:
        print(f"    [FAIL] Verification endpoint failed: {e}")

if __name__ == "__main__":
    run_test()
