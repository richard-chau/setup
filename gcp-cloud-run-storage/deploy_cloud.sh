#!/bin/bash

# deploy_cloud.sh
# Deploys the application to Google Cloud Run and configures resources.

PROJECT_ID="n8n-server-482107"
REGION="us-east1"
SERVICE_NAME="gcp-cloud-run-storage"
BUCKET_NAME="${PROJECT_ID}-logs-bucket" # Bucket names must be globally unique

echo "====================================================="
echo "   Deploying to GCP Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "====================================================="

# 0. Prerequisites Check
if ! command -v gcloud &> /dev/null; then
    echo "[ERROR] 'gcloud' CLI is not installed."
    echo "Please install it: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "[0/5] Authentication already handled via Service Account."

# 1. Set Project
gcloud config set project $PROJECT_ID

# 2. Enable APIs
echo "[1/5] Enabling necessary APIs..."
gcloud services enable run.googleapis.com \
    firestore.googleapis.com \
    storage.googleapis.com \
    cloudbuild.googleapis.com

# 3. Create Cloud Storage Bucket
echo "[2/5] Checking/Creating Storage Bucket..."
if gsutil ls -b gs://$BUCKET_NAME > /dev/null 2>&1; then
    echo "   Bucket gs://$BUCKET_NAME already exists."
else
    echo "   Creating bucket gs://$BUCKET_NAME..."
    gcloud storage buckets create gs://$BUCKET_NAME --location=$REGION
fi

# 4. Create Firestore Database (Native Mode)
echo "[3/5] Checking/Creating Firestore Database..."
# Try to list databases; if fail/empty, create one.
# Note: This command might fail if the default database already exists, which is fine.
gcloud firestore databases create --location=$REGION --type=firestore-native --quiet 2>/dev/null || echo "   Firestore database likely already exists or is being created."

# 5. Deploy to Cloud Run
echo "[4/5] Deploying Cloud Run Service..."
# We use --source . to build and deploy in one step
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GCLOUD_PROJECT=$PROJECT_ID,BUCKET_NAME=$BUCKET_NAME \
    --quiet

# 6. Output URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo "====================================================="
echo "   Deployment Complete!"
echo "   Service URL: $SERVICE_URL"
echo "====================================================="
echo "Test your cloud deployment:"
echo "   curl \"$SERVICE_URL/?name=CloudUser\""
