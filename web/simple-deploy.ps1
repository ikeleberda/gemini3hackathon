# Simplified Deploy to Cloud Run
$PROJECT_ID = "pihrate-hub-c8f3s"
$REGION = "us-central1"
$SERVICE_NAME = "fractal-web"

$BACKEND_URL = gcloud run services describe fractal-backend --project $PROJECT_ID --region $REGION --format 'value(status.url)'
$SQL_INSTANCE = gcloud sql instances describe fractal-db --project $PROJECT_ID --format 'value(connectionName)'
$DATABASE_URL = "postgresql://postgres:FractalPassword123!@localhost/fractal?host=/cloudsql/$SQL_INSTANCE"
$NEXTAUTH_SECRET = "zYaIgrpKLFVwkUNfx2OcZCM0AhutGbSR"
$envVarsString = "DATABASE_URL=$DATABASE_URL,BACKEND_API_URL=$BACKEND_URL,NEXTAUTH_SECRET=$NEXTAUTH_SECRET"

Write-Host "Deploying $SERVICE_NAME..."
gcloud run deploy $SERVICE_NAME `
    --source . `
    --project $PROJECT_ID `
    --region $REGION `
    --platform managed `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --timeout 300s `
    --max-instances 3 `
    --min-instances 0 `
    --set-env-vars $envVarsString `
    --add-cloudsql-instances $SQL_INSTANCE
