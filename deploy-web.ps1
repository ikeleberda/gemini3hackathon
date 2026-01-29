# Deploy Next.js web app to Google Cloud Run (PowerShell version)

$ErrorActionPreference = "Stop"

$PROJECT_ID = "pihrate-hub-c8f3s"
$REGION = "us-central1"
$SERVICE_NAME = "fractal-web"
$IMAGE_NAME = "gcr.io/$PROJECT_ID/$SERVICE_NAME"

Write-Host "ðŸš€ Deploying web app to Google Cloud Run..." -ForegroundColor Cyan
Write-Host "Project: $PROJECT_ID"
Write-Host "Region: $REGION"
Write-Host "Service: $SERVICE_NAME"
Write-Host ""

# Check if we need to create a Cloud SQL instance or use Neon/external DB
Write-Host "ðŸ” Checking environment and infrastructure..." -ForegroundColor Cyan

# Try to get backend URL automatically
$BACKEND_URL = gcloud run services describe fractal-backend --project $PROJECT_ID --region $REGION --format 'value(status.url)' 2>$null
if ($BACKEND_URL) {
    Write-Host "âœ… Found backend service: $BACKEND_URL" -ForegroundColor Green
} else {
    Write-Host "âš ï¸  Could not find fractal-backend service. Link it manually after deployment." -ForegroundColor Yellow
}

# Try to get Cloud SQL instance connection name
$SQL_INSTANCE = gcloud sql instances describe fractal-db --project $PROJECT_ID --format 'value(connectionName)' 2>$null
if ($SQL_INSTANCE) {
    Write-Host "âœ… Found Cloud SQL instance: $SQL_INSTANCE" -ForegroundColor Green
}

# Build environment variables list
$envVars = @()
$DATABASE_URL = "postgresql://postgres:FractalPassword123!@localhost/fractal?host=/cloudsql/$SQL_INSTANCE"

if ($null -eq $SQL_INSTANCE) {
    Write-Host "âš ï¸  Cloud SQL instance 'fractal-db' not found. Using placeholder." -ForegroundColor Yellow
    $DATABASE_URL = "postgresql://placeholder:placeholder@localhost/placeholder"
}

$envVars += "DATABASE_URL=$DATABASE_URL"

if ($BACKEND_URL) {
    $envVars += "BACKEND_API_URL=$BACKEND_URL"
}

# Generate a random NextAuth secret only if not already set or needing a fresh one
$NEXTAUTH_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
$envVars += "NEXTAUTH_SECRET=$NEXTAUTH_SECRET"

$envVarsString = $envVars -join ","

# Deploy to Cloud Run
Write-Host "ðŸš€ Deploying to Cloud Run using source code..." -ForegroundColor Cyan

$deployArgs = @(
    "run", "deploy", $SERVICE_NAME,
    "--source", ".",
    "--project", $PROJECT_ID,
    "--region", $REGION,
    "--platform", "managed",
    "--allow-unauthenticated",
    "--memory", "512Mi",
    "--cpu", "1",
    "--timeout", "300s",
    "--max-instances", "3",
    "--min-instances", "0",
    "--set-env-vars", $envVarsString
)

if ($SQL_INSTANCE) {
    $deployArgs += "--add-cloudsql-instances"
    $deployArgs += $SQL_INSTANCE
}

gcloud @deployArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "âŒ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "âœ… Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Service URL:"
$serviceUrl = gcloud run services describe $SERVICE_NAME `
    --project $PROJECT_ID `
    --region $REGION `
    --format 'value(status.url)'

Write-Host $serviceUrl -ForegroundColor Cyan
Write-Host ""
Write-Host "âš ï¸  NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Verify DATABASE_URL if not using Cloud SQL."
Write-Host "2. Set NEXTAUTH_URL to enable authentication:"
Write-Host "   gcloud run services update $SERVICE_NAME --region $REGION --update-env-vars NEXTAUTH_URL=$serviceUrl"

 
# END