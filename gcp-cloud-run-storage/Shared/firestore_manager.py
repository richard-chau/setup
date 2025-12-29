from google.cloud import firestore
import os

class FirestoreManager:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirestoreManager, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        # Automatically detects 'FIRESTORE_EMULATOR_HOST' if set in Docker/Env
        # If not set, it uses default Google Cloud credentials (for production)
        project_id = os.getenv("GCLOUD_PROJECT")
        if not project_id:
            raise ValueError("Environment variable 'GCLOUD_PROJECT' is not set.")
            
        self._client = firestore.Client(project=project_id)
        print(f"[FirestoreManager] Initialized for project: {project_id}")

    def add_log(self, collection_name, data):
        """
        Adds a document to the specified Firestore collection.
        """
        try:
            doc_ref = self._client.collection(collection_name).document()
            doc_ref.set(data)
            return doc_ref.id
        except Exception as e:
            print(f"[FirestoreManager] Error writing to Firestore: {e}")
            raise e

    def get_logs(self, collection_name, limit=10):
        """
        Retrieves logs from Firestore.
        """
        try:
            docs = self._client.collection(collection_name).limit(limit).stream()
            return [{**doc.to_dict(), 'id': doc.id} for doc in docs]
        except Exception as e:
            print(f"[FirestoreManager] Error reading from Firestore: {e}")
            raise e
