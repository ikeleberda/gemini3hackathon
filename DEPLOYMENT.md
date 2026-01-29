# Google Cloud Deployment Guide

## Prerequisites

Before deploying, you need to install the Google Cloud SDK (gcloud CLI).

### Install Google Cloud SDK on Windows

**Option 1: Using PowerShell (Recommended)**

```powershell
# Download and run the installer
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

**Option 2: Using Chocolatey**

```powershell
choco install gcloudsdk
```

**Option 3: Manual Download**

Download from: https://cloud.google.com/sdk/docs/install

### After Installation

1. **Restart your terminal** (or restart VS Code)

2. **Initialize gcloud**:
   ```powershell
   gcloud init
   ```

3. **Authenticate**:
   ```powershell
   gcloud auth login
   ```

4. **Set your project**:
   ```powershell
   gcloud config set project pihrate-hub-c8f3s
   ```

5. **Enable required APIs**:
   ```powershell
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

6. **Configure Docker for GCR**:
   ```powershell
   gcloud auth configure-docker
   ```

---

## Deployment Steps

### Step 1: Deploy Backend (Python Multi-Agent System)

```powershell
cd c:\Users\ikele\.gemini\antigravity\playground\fractal-aphelion
.\deploy-backend.ps1
```

This will:
- Build a Docker image with your Python backend
- Deploy to Cloud Run as `fractal-backend`
- Set up all environment variables from your `.env` file
- Provide you with a public URL

**Expected time**: 3-5 minutes

### Step 2: Set Up Database for Web App

You have two options:

**Option A: Neon (Free, Recommended for Demo)**

1. Sign up at https://neon.tech
2. Create a new project
3. Copy the connection string (looks like: `postgresql://user:pass@host/db`)
4. Save it for the next step

**Option B: Cloud SQL (Costs ~$10/month)**

```powershell
# Create Cloud SQL instance
gcloud sql instances create fractal-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# Create database
gcloud sql databases create fractal --instance=fractal-db

# Get connection string
gcloud sql instances describe fractal-db --format="value(connectionName)"
```

### Step 3: Deploy Web App

```powershell
cd c:\Users\ikele\.gemini\antigravity\playground\fractal-aphelion\web

# Set your database URL (replace with your actual connection string)
$env:DATABASE_URL = "postgresql://user:pass@host/db"

# Deploy
.\deploy-web.ps1
```

This will:
- Build a Docker image with your Next.js app
- Deploy to Cloud Run as `fractal-web`
- Set up environment variables
- Provide you with a public URL

**Expected time**: 5-7 minutes

### Step 4: Update Web App with Backend URL

After both services are deployed:

```powershell
# Get backend URL
$BACKEND_URL = gcloud run services describe fractal-backend --region us-central1 --format 'value(status.url)'

# Get web URL
$WEB_URL = gcloud run services describe fractal-web --region us-central1 --format 'value(status.url)'

# Update web app with backend URL
gcloud run services update fractal-web \
  --region us-central1 \
  --update-env-vars "BACKEND_API_URL=$BACKEND_URL,NEXTAUTH_URL=$WEB_URL"
```

---

## Quick Start (After gcloud is installed)

```powershell
# 1. Deploy backend
cd c:\Users\ikele\.gemini\antigravity\playground\fractal-aphelion
.\deploy-backend.ps1

# 2. Set up Neon database (get connection string from neon.tech)

# 3. Deploy web app
cd web
$env:DATABASE_URL = "your-neon-connection-string"
.\deploy-web.ps1

# 4. Link services
$BACKEND_URL = gcloud run services describe fractal-backend --region us-central1 --format 'value(status.url)'
$WEB_URL = gcloud run services describe fractal-web --region us-central1 --format 'value(status.url)'
gcloud run services update fractal-web --region us-central1 --update-env-vars "BACKEND_API_URL=$BACKEND_URL,NEXTAUTH_URL=$WEB_URL"
```

---

## Testing Your Deployment

### Test Backend

```powershell
# Get backend URL
$BACKEND_URL = gcloud run services describe fractal-backend --region us-central1 --format 'value(status.url)'

# Test health check
curl "$BACKEND_URL/"

# Test agent run
curl -X POST "$BACKEND_URL/run" `
  -H "Content-Type: application/json" `
  -d '{"topic": "Test Topic"}'
```

### Test Web App

Just open the web URL in your browser:

```powershell
$WEB_URL = gcloud run services describe fractal-web --region us-central1 --format 'value(status.url)'
Start-Process $WEB_URL
```

---

## Cost Monitoring

Check your usage (should be $0 within free tier):

```powershell
gcloud run services describe fractal-backend --region us-central1 --format="table(status.url,status.traffic)"
gcloud run services describe fractal-web --region us-central1 --format="table(status.url,status.traffic)"
```

---

## Troubleshooting

### View Logs

```powershell
# Backend logs
gcloud run services logs read fractal-backend --region us-central1 --limit 50

# Web app logs
gcloud run services logs read fractal-web --region us-central1 --limit 50
```

### Update Environment Variables

```powershell
# Update backend
gcloud run services update fractal-backend \
  --region us-central1 \
  --update-env-vars "KEY=VALUE"

# Update web app
gcloud run services update fractal-web \
  --region us-central1 \
  --update-env-vars "KEY=VALUE"
```

### Redeploy

Just run the deployment script again:

```powershell
.\deploy-backend.ps1  # For backend
.\deploy-web.ps1      # For web app
```
