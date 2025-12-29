# GCP Migration Guide: Cloud Run + Storage + Firestore

This project replicates an Azure Function (SQL Trigger) architecture using **Google Cloud Platform (GCP)** services, fully capable of running within the Free Tier.

## 1. Architecture Overview

| Feature | Azure Equivalent | GCP Implementation | Free Tier Note |
| :--- | :--- | :--- | :--- |
| **Compute** | Azure Functions | **Cloud Run** (Python Flask) | 2M requests/month free |
| **Database** | Azure SQL | **Firestore** (NoSQL) | 1GB storage, 50k reads/day |
| **File Storage** | Blob Storage | **Cloud Storage** | 5GB free |
| **Local Dev** | Azurite + SQL Edge | **Local Simulators** (Docker) | Zero cost |

## 2. Project Structure

```text
gcp-cloud-run-storage/
├── main.py                 # The Application Entrypoint (Flask)
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── deploy_cloud.sh         # Automated Cloud Deployment Script
├── verify_local.py         # Local Verification Script
├── Shared/                 # Shared Logic Modules
│   ├── firestore_manager.py # Connects to Firestore (Local or Cloud)
│   └── storage_manager.py   # Connects to GCS (Local or Cloud)
└── data/                   # Local storage for simulators
```

## 3. Local Development (The Simulator)

We built a "Zero-Config" local environment using Docker. It runs:
1.  **Local App**: Your code running in a container.
2.  **Firestore Emulator**: `ridedott/firestore-emulator` (ARM64/AMD64 compatible).
3.  **GCS Emulator**: `fsouza/fake-gcs-server`.

### Control Scripts
Located inside `gcp-cloud-run-storage/`:

```bash
# Start all services
./start.sh

# Stop services
./stop.sh

# Advanced management (logs, restart)
./manage_local.sh logs
./manage_local.sh restart
```

**Verification:**
Run `python3 gcp-cloud-run-storage/verify_local.py` to test writes to the local emulators.

## 4. Cloud Deployment Process

We successfully deployed to project **n8n-server-482107** in **us-east1**.

### The Deployment Script: `gcp-cloud-run-storage/deploy_cloud.sh`
This script automates the entire process:
1.  Enables APIs (`run`, `firestore`, `storage`, `cloudbuild`).
2.  Creates the **Cloud Storage Bucket** (`n8n-server-482107-logs-bucket`).
3.  Creates the **Firestore Database** (Native Mode).
4.  Builds and Deploys the Container to **Cloud Run**.

### Authentication Fix
To bypass the deprecated OOB login flow on the remote server:
1.  We created a **Service Account** (`deployer`).
2.  Generated a JSON Key.
3.  Uploaded it to the server.
4.  Authenticated via `gcloud auth activate-service-account`.

### IAM Permission Fix
During the first deployment, Cloud Build failed. We fixed it by granting the following permissions to the **Cloud Build Service Account**:
-   `roles/logging.logWriter`
-   `roles/storage.objectViewer`
-   `roles/cloudbuild.builds.builder`

### Current Status
-   **Service URL**: `https://gcp-cloud-run-storage-crodk7cewq-ue.a.run.app`
-   **Test Command**:
    ```bash
    curl "https://gcp-cloud-run-storage-crodk7cewq-ue.a.run.app/?name=DocReader"
    ```

## 5. Source Code Dump

### A. Application Logic (`main.py`)
```python
import os
from flask import Flask, request, jsonify
from Shared.firestore_manager import FirestoreManager
from Shared.storage_manager import StorageManager
import datetime

app = Flask(__name__)
firestore_mgr = FirestoreManager()
storage_mgr = StorageManager()

@app.route("/", methods=["GET", "POST"])
def index():
    name = request.args.get("name", "Anonymous")
    timestamp = datetime.datetime.now().isoformat()
    message = f"Hello, {name}. Processed at {timestamp}."
    
    results = {"message": message, "actions": {}}

    # 1. Write to Firestore
    try:
        doc_id = firestore_mgr.add_log("access_logs", {
            "name": name, "timestamp": timestamp, "source": "GCP Cloud Run"
        })
        results["actions"]["firestore"] = f"Written to collection 'access_logs' with ID: {doc_id}"
    except Exception as e:
        results["actions"]["firestore"] = f"Failed: {str(e)}"

    # 2. Write to Cloud Storage
    try:
        file_content = f"Log Entry:\nName: {name}\nTime: {timestamp}\n"
        filename = storage_mgr.upload_log(file_content)
        results["actions"]["storage"] = f"Uploaded file: {filename}"
    except Exception as e:
        results["actions"]["storage"] = f"Failed: {str(e)}"

    return jsonify(results), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
```

### B. Firestore Manager (`Shared/firestore_manager.py`)
*Handles auto-switching between Emulator and Cloud.*
```python
from google.cloud import firestore
import os

class FirestoreManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirestoreManager, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        project_id = os.getenv("GCLOUD_PROJECT")
        if not project_id:
            raise ValueError("Environment variable 'GCLOUD_PROJECT' is not set.")
            
        # The library automatically detects FIRESTORE_EMULATOR_HOST env var
        self._client = firestore.Client(project=project_id)
        print(f"[FirestoreManager] Initialized for project: {project_id}")

    def add_log(self, collection_name, data):
        doc_ref = self._client.collection(collection_name).document()
        doc_ref.set(data)
        return doc_ref.id
```

### C. Storage Manager (`Shared/storage_manager.py`)
```python
from google.cloud import storage
import os
import datetime

class StorageManager:
    _instance = None
    _bucket_name = os.getenv("BUCKET_NAME", "app-logs-bucket")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StorageManager, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        project_id = os.getenv("GCLOUD_PROJECT")
        if not project_id:
             raise ValueError("Environment variable 'GCLOUD_PROJECT' is not set.")
             
        self._client = storage.Client(project=project_id)
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            bucket = self._client.bucket(self._bucket_name)
            if not bucket.exists():
                self._client.create_bucket(self._bucket_name)
        except Exception as e:
            print(f"[Warning] Bucket check failed: {e}")

    def upload_log(self, content):
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"log-{timestamp}.txt"
        bucket = self._client.bucket(self._bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_string(content)
        return filename
```

### D. Deployment Script (`deploy_cloud.sh`)
```bash
#!/bin/bash
PROJECT_ID="n8n-server-482107"
REGION="us-east1"
SERVICE_NAME="gcp-cloud-run-storage"
BUCKET_NAME="${PROJECT_ID}-logs-bucket"

# Check Auth (Simplified)
if ! command -v gcloud &> /dev/null; then echo "Install gcloud first"; exit 1; fi

gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com firestore.googleapis.com storage.googleapis.com cloudbuild.googleapis.com

# Create Bucket
if ! gsutil ls -b gs://$BUCKET_NAME > /dev/null 2>&1;
then
    gcloud storage buckets create gs://$BUCKET_NAME --location=$REGION
fi

# Create Firestore
gcloud firestore databases create --location=$REGION --type=firestore-native --quiet 2>/dev/null || true

# Deploy Cloud Run
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GCLOUD_PROJECT=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME \
    --quiet
```