#!/bin/bash

# manage_local.sh
# Manages the Local GCP Simulator Environment (Run from inside gcp-cloud-run-storage/)

NETWORK_NAME="gcp-local-net"
GCS_CONTAINER="gcs-emulator"
FIRESTORE_CONTAINER="firestore-emulator"
APP_CONTAINER="gcp-app"

# Load .env variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Fallback defaults
: "${GCLOUD_PROJECT:=local-project}"
: "${BUCKET_NAME:=local-bucket}"

function start() {
    echo "Starting Local GCP Environment..."

    # 1. Create Network
    docker network create $NETWORK_NAME 2>/dev/null || true

    # 2. GCS Emulator
    echo "Starting GCS Emulator..."
    # We mount ./data/storage relative to this script
    docker run -d --rm --name $GCS_CONTAINER \
        --network $NETWORK_NAME \
        -p 4443:4443 \
        -v $(pwd)/data/storage:/data \
        fsouza/fake-gcs-server -scheme http

    # 3. Firestore Emulator
    echo "Starting Firestore Emulator..."
    docker run -d --rm --name $FIRESTORE_CONTAINER \
        --network $NETWORK_NAME \
        -p 8080:8080 \
        -e FIRESTORE_PROJECT_ID=$GCLOUD_PROJECT \
        ridedott/firestore-emulator

    # 4. Local App (Build & Run)
    echo "Building and Starting App..."
    docker build -t gcp-local-app .
    
    docker run -d --rm --name $APP_CONTAINER \
        --network $NETWORK_NAME \
        -p 8000:8080 \
        -e PORT=8080 \
        -e STORAGE_EMULATOR_HOST=http://$GCS_CONTAINER:4443 \
        -e FIRESTORE_EMULATOR_HOST=$FIRESTORE_CONTAINER:8080 \
        -e GCLOUD_PROJECT=$GCLOUD_PROJECT \
        -e BUCKET_NAME=$BUCKET_NAME \
        -e FLASK_ENV=development \
        gcp-local-app

    echo "---------------------------------------------------"
    echo "Services started:"
    echo "  - Local App:          http://localhost:8000"
    echo "  - Firestore Emulator: http://localhost:8080"
    echo "  - Storage Emulator:   http://localhost:4443"
    echo "---------------------------------------------------"
    echo "Test with: python3 verify_local.py"
}

function stop() {
    echo "Stopping services..."
    docker stop $APP_CONTAINER $FIRESTORE_CONTAINER $GCS_CONTAINER 2>/dev/null || true
    docker network rm $NETWORK_NAME 2>/dev/null || true
    echo "Services stopped."
}

function logs() {
    echo "--- App Logs ---"
    docker logs $APP_CONTAINER
    echo "--- Firestore Logs ---"
    docker logs $FIRESTORE_CONTAINER
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    logs)
        logs
        ;;
    restart)
        stop
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|logs|restart}"
        exit 1
esac
