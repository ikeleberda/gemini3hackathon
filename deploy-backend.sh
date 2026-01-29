#!/bin/bash

# Deploy Python backend to Google Cloud Run
# This script uses Cloud Run's source-based deployment (buildpacks)

set -e

PROJECT_ID="pihrate-hub-c8f3s"
REGION="us-central1"
SERVICE_NAME="fractal-backend"

echo "🚀 Deploying backend to Google Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Deploy using gcloud run deploy with source
gcloud run deploy $SERVICE_NAME \
  --source . \
  --project $PROJECT_ID \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 900s \
  --max-instances 3 \
  --min-instances 0 \
  --set-env-vars "WP_URL=${WP_URL},WP_USERNAME=${WP_USERNAME},WP_APP_PASSWORD=${WP_APP_PASSWORD},GOOGLE_API_KEY=${GOOGLE_API_KEY},GOOGLE_MODEL_NAME=${GOOGLE_MODEL_NAME},GOOGLE_FALLBACK_MODELS=${GOOGLE_FALLBACK_MODELS},GOOGLE_SEARCH_API_KEY=${GOOGLE_SEARCH_API_KEY},GOOGLE_SEARCH_CX=${GOOGLE_SEARCH_CX},GCP_PROJECT_ID=${GCP_PROJECT_ID},GCP_LOCATION=${GCP_LOCATION},USE_VERTEX_AI=${USE_VERTEX_AI},USE_VERTEX_FOR_IMAGES=${USE_VERTEX_FOR_IMAGES},ALLOW_SIMULATED_PUBLISHING=${ALLOW_SIMULATED_PUBLISHING}"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service URL:"
gcloud run services describe $SERVICE_NAME \
  --project $PROJECT_ID \
  --region $REGION \
  --format 'value(status.url)'
