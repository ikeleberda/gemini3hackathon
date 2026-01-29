# Install Google Cloud SDK on Windows
# Run this script in PowerShell as Administrator

Write-Host "🔧 Installing Google Cloud SDK..." -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  This script should be run as Administrator for best results." -ForegroundColor Yellow
    Write-Host "   However, we'll try to install for current user only." -ForegroundColor Yellow
    Write-Host ""
}

# Download the installer
$installerUrl = "https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe"
$installerPath = "$env:TEMP\GoogleCloudSDKInstaller.exe"

Write-Host "📥 Downloading Google Cloud SDK installer..." -ForegroundColor Cyan
try {
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    Write-Host "✅ Download complete!" -ForegroundColor Green
}
catch {
    Write-Host "❌ Download failed: $_" -ForegroundColor Red
    exit 1
}

# Run the installer
Write-Host ""
Write-Host "🚀 Running installer..." -ForegroundColor Cyan
Write-Host "   Please follow the installation wizard." -ForegroundColor Yellow
Write-Host ""

Start-Process -FilePath $installerPath -Wait

Write-Host ""
Write-Host "✅ Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. RESTART your terminal (or VS Code)" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Initialize gcloud:" -ForegroundColor White
Write-Host "   gcloud init" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Authenticate:" -ForegroundColor White
Write-Host "   gcloud auth login" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Set your project:" -ForegroundColor White
Write-Host "   gcloud config set project pihrate-hub-c8f3s" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Enable required APIs:" -ForegroundColor White
Write-Host "   gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com" -ForegroundColor Gray
Write-Host ""
Write-Host "6. Configure Docker:" -ForegroundColor White
Write-Host "   gcloud auth configure-docker" -ForegroundColor Gray
Write-Host ""
Write-Host "7. Deploy your backend:" -ForegroundColor White
Write-Host "   cd c:\Users\ikele\.gemini\antigravity\playground\fractal-aphelion" -ForegroundColor Gray
Write-Host "   .\deploy-backend.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "See DEPLOYMENT.md for full instructions!" -ForegroundColor Cyan
