from azure.storage.blob import BlobServiceClient
import os

# Azurite Default Connection String
AZURITE_CONN_STR = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"

CONTAINER_NAME = "local-logs"
BLOB_NAME = "test-log.txt"

print(f"--- Testing Azurite Blob Storage (Object Storage) ---")

try:
    # 1. Connect
    blob_service_client = BlobServiceClient.from_connection_string(AZURITE_CONN_STR)
    print("[PASS] Connected to Azurite.")

    # 2. Create Container (if not exists)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    if not container_client.exists():
        container_client.create_container()
        print(f"[PASS] Created container '{CONTAINER_NAME}'.")
    else:
        print(f"[INFO] Container '{CONTAINER_NAME}' already exists.")

    # 3. Upload Blob
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=BLOB_NAME)
    data = "Hello from Azurite Object Storage!"
    blob_client.upload_blob(data, overwrite=True)
    print(f"[PASS] Uploaded blob '{BLOB_NAME}'.")

    # 4. Read Blob
    download_stream = blob_client.download_blob()
    content = download_stream.readall()
    print(f"  -> Read Content: {content.decode('utf-8')}")

    print("[PASS] Blob Storage verification successful.")

except Exception as e:
    print(f"[FAIL] Blob Storage error: {e}")
