# Deploy Python backend to Google Cloud Run (PowerShell version)
# This script uses Cloud Run's source-based deployment

$ErrorActionPreference = "Stop"

$PROJECT_ID = "pihrate-hub-c8f3s"
$REGION = "us-central1"
$SERVICE_NAME = "fractal-backend"

Write-Host "🚀 Deploying backend to Google Cloud Run..." -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host ""

# Load environment variables from .env file
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"')
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Build environment variables string
$envVars = @(
    "WP_URL=$env:WP_URL",
    "WP_USERNAME=$env:WP_USERNAME",
    "WP_APP_PASSWORD=$env:WP_APP_PASSWORD",
    "GOOGLE_API_KEY=$env:GOOGLE_API_KEY",
    "GOOGLE_MODEL_NAME=$env:GOOGLE_MODEL_NAME",
    "GOOGLE_FALLBACK_MODELS=$env:GOOGLE_FALLBACK_MODELS",
    "GOOGLE_SEARCH_API_KEY=$env:GOOGLE_SEARCH_API_KEY",
    "GOOGLE_SEARCH_CX=$env:GOOGLE_SEARCH_CX",
    "GCP_PROJECT_ID=$env:GCP_PROJECT_ID",
    "GCP_LOCATION=$env:GCP_LOCATION",
    "USE_VERTEX_AI=$env:USE_VERTEX_AI",
    "USE_VERTEX_FOR_IMAGES=$env:USE_VERTEX_FOR_IMAGES",
    "ALLOW_SIMULATED_PUBLISHING=$env:ALLOW_SIMULATED_PUBLISHING"
) -join ","

# Deploy using gcloud run deploy with source
gcloud run deploy $SERVICE_NAME `
  --source . `
  --project $PROJECT_ID `
  --region $REGION `
  --platform managed `
  --allow-unauthenticated `
  --memory 1Gi `
  --cpu 1 `
  --timeout 900s `
  --max-instances 3 `
  --min-instances 0 `
  --set-env-vars $envVars

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URL:"
gcloud run services describe $SERVICE_NAME `
  --project $PROJECT_ID `
  --region $REGION `
  --format 'value(status.url)'
