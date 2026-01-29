# Quick Setup Script for Google Cloud Deployment
# Run this after installing gcloud CLI

$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up Google Cloud for deployment..." -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
try {
    $gcloudVersion = gcloud version 2>&1
    Write-Host "✅ gcloud CLI is installed" -ForegroundColor Green
}
catch {
    Write-Host "❌ gcloud CLI is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run: .\install-gcloud.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 1: Authenticating with Google Cloud..." -ForegroundColor Cyan
gcloud auth login

Write-Host ""
Write-Host "Step 2: Setting project..." -ForegroundColor Cyan
gcloud config set project pihrate-hub-c8f3s

Write-Host ""
Write-Host "Step 3: Enabling required APIs..." -ForegroundColor Cyan
Write-Host "   This may take a few minutes..." -ForegroundColor Yellow

gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

Write-Host ""
Write-Host "Step 4: Configuring Docker for Google Container Registry..." -ForegroundColor Cyan
gcloud auth configure-docker

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 You're ready to deploy!" -ForegroundColor Cyan
Write-Host ""
Write-Host "To deploy the backend:" -ForegroundColor White
Write-Host "   .\deploy-backend.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "To deploy the web app:" -ForegroundColor White
Write-Host "   cd web" -ForegroundColor Gray
Write-Host "   .\deploy-web.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "See DEPLOYMENT.md for detailed instructions!" -ForegroundColor Cyan
