import os
from flask import Flask, request, jsonify
from Shared.firestore_manager import FirestoreManager
from Shared.storage_manager import StorageManager
import datetime

app = Flask(__name__)

# Initialize managers
firestore_mgr = FirestoreManager()
storage_mgr = StorageManager()

@app.route("/", methods=["GET", "POST"])
def index():
    """
    Simulates the Trigger. 
    Accepts a name/message, logs it to Firestore (DB) and Cloud Storage (File).
    """
    name = request.args.get("name", "Anonymous")
    
    timestamp = datetime.datetime.now().isoformat()
    message = f"Hello, {name}. Processed at {timestamp}."
    
    results = {
        "message": message,
        "actions": {}
    }

    # 1. Write to Firestore (Database)
    try:
        doc_id = firestore_mgr.add_log("access_logs", {
            "name": name,
            "timestamp": timestamp,
            "source": "GCP Cloud Run"
        })
        results["actions"]["firestore"] = f"Written to collection 'access_logs' with ID: {doc_id}"
    except Exception as e:
        results["actions"]["firestore"] = f"Failed: {str(e)}"

    # 2. Write to Cloud Storage (File)
    try:
        file_content = f"Log Entry:\nName: {name}\nTime: {timestamp}\n"
        filename = storage_mgr.upload_log(file_content)
        results["actions"]["storage"] = f"Uploaded file: {filename}"
    except Exception as e:
        results["actions"]["storage"] = f"Failed: {str(e)}"

    return jsonify(results), 200

@app.route("/verify", methods=["GET"])
def verify():
    """
    Helper endpoint to view what's in the DB/Storage
    """
    try:
        logs = firestore_mgr.get_logs("access_logs")
        files = storage_mgr.list_files()
        return jsonify({
            "firestore_logs": logs,
            "storage_files": files
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Cloud Run injects PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
