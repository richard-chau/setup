from google.cloud import storage
import os
import datetime

class StorageManager:
    _instance = None
    _client = None
    _bucket_name = os.getenv("BUCKET_NAME", "app-logs-bucket")  # Default bucket name

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StorageManager, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        project_id = os.getenv("GCLOUD_PROJECT")
        if not project_id:
            raise ValueError("Environment variable 'GCLOUD_PROJECT' is not set.")
        
        # Check for Emulator
        # Standard lib supports STORAGE_EMULATOR_HOST, but for fsouza/fake-gcs-server
        # we often need to ensure the client is configured to allow HTTP.
        # However, the python client usually handles STORAGE_EMULATOR_HOST automatically 
        # for connecting to localhost.
        
        self._client = storage.Client(project=project_id)
        print(f"[StorageManager] Initialized for project: {project_id}")
        
        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            bucket = self._client.bucket(self._bucket_name)
            if not bucket.exists():
                print(f"[StorageManager] Creating bucket: {self._bucket_name}")
                self._client.create_bucket(self._bucket_name)
            else:
                print(f"[StorageManager] Bucket exists: {self._bucket_name}")
        except Exception as e:
            print(f"[StorageManager] Warning: Could not check/create bucket (might be permissions or emulator issue): {e}")

    def upload_log(self, content, filename=None):
        """
        Uploads a text string as a file to GCS.
        """
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"log-{timestamp}.txt"
        
        try:
            bucket = self._client.bucket(self._bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_string(content)
            print(f"[StorageManager] Uploaded {filename}")
            return filename
        except Exception as e:
            print(f"[StorageManager] Error uploading blob: {e}")
            raise e

    def list_files(self):
        try:
            bucket = self._client.bucket(self._bucket_name)
            blobs = self._client.list_blobs(self._bucket_name)
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"[StorageManager] Error listing blobs: {e}")
            return []
