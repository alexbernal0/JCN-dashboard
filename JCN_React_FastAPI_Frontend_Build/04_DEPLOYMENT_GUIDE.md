# Deployment Guide - Railway

**Last Updated:** February 11, 2026  
**Platform:** Railway  
**Cost:** Free tier (upgradeable)

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Railway Configuration](#railway-configuration)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Environment Variables](#environment-variables)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Architecture

```
GitHub (feature/fastapi-react branch)
    ↓
Railway Auto-Deploy
    ├── Backend Service (FastAPI on port 8000)
    └── Frontend Service (React + Nginx on port 3000)
```

### Deployment Strategy

- **Auto-deploy:** Push to GitHub → Railway deploys automatically
- **Zero-downtime:** Rolling deployments
- **Rollback:** One-click rollback to previous version

---

## Prerequisites

### 1. Railway Account

- Sign up at https://railway.app
- Connect GitHub account
- Link to `alexbernal0/JCN-dashboard` repository

### 2. Environment Variables

Prepare these values:
- `MOTHERDUCK_TOKEN` - Your MotherDuck database token
- `FINNHUB_API_KEY` (optional) - For news features
- `GROK_API_KEY` (optional) - For AI features

---

## Railway Configuration

### railway.toml

Create `railway.toml` in project root:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "echo 'Use service-specific start commands'"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

# Backend Service
[[services]]
name = "backend"
source = "backend"

[services.build]
buildCommand = "pip install -r requirements.txt"

[services.deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100

[[services.domains]]
# Railway will auto-generate: backend-production.up.railway.app

# Frontend Service
[[services]]
name = "frontend"
source = "frontend"

[services.build]
buildCommand = "pnpm install && pnpm build"

[services.deploy]
startCommand = "pnpm preview --host 0.0.0.0 --port $PORT"

[[services.domains]]
# Railway will auto-generate: frontend-production.up.railway.app
```

---

## Backend Deployment

### Step 1: Create Backend Service

1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `alexbernal0/JCN-dashboard`
5. Select branch: `feature/fastapi-react`
6. Railway detects `backend/` directory

### Step 2: Configure Backend

**Build Settings:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Root Directory:** `backend/`

**Environment Variables:**
```
MOTHERDUCK_TOKEN=your_token_here
FINNHUB_API_KEY=your_key_here (optional)
GROK_API_KEY=your_key_here (optional)
PORT=8000
```

**Health Check:**
- **Path:** `/health`
- **Timeout:** 100 seconds

### Step 3: Deploy

Click "Deploy" - Railway will:
1. Clone repository
2. Install Python dependencies
3. Start FastAPI server
4. Assign public URL

**Expected URL:** `https://backend-production.up.railway.app`

---

## Frontend Deployment

### Step 1: Create Frontend Service

1. In same Railway project, click "New Service"
2. Select "Deploy from GitHub repo"
3. Choose `alexbernal0/JCN-dashboard`
4. Select branch: `feature/fastapi-react`
5. Railway detects `frontend/` directory

### Step 2: Configure Frontend

**Build Settings:**
- **Build Command:** `pnpm install && pnpm build`
- **Start Command:** `pnpm preview --host 0.0.0.0 --port $PORT`
- **Root Directory:** `frontend/`

**Environment Variables:**
```
VITE_API_URL=https://backend-production.up.railway.app
PORT=3000
```

### Step 3: Deploy

Click "Deploy" - Railway will:
1. Clone repository
2. Install Node dependencies
3. Build React app
4. Start preview server
5. Assign public URL

**Expected URL:** `https://frontend-production.up.railway.app`

---

## Environment Variables

### Backend Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MOTHERDUCK_TOKEN` | ✅ Yes | MotherDuck database token | `md_xxx...` |
| `FINNHUB_API_KEY` | ❌ No | Finnhub news API key | `xxx...` |
| `GROK_API_KEY` | ❌ No | Grok API key | `xxx...` |
| `PORT` | ✅ Yes | Server port (auto-set by Railway) | `8000` |

### Frontend Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_URL` | ✅ Yes | Backend API URL | `https://backend-production.up.railway.app` |
| `PORT` | ✅ Yes | Server port (auto-set by Railway) | `3000` |

### Setting Variables in Railway

1. Go to service settings
2. Click "Variables" tab
3. Click "New Variable"
4. Enter name and value
5. Click "Add"
6. Service will auto-redeploy

---

## Monitoring

### Railway Dashboard

**Metrics Available:**
- CPU usage
- Memory usage
- Network traffic
- Request count
- Response time

**Logs:**
- Real-time logs
- Filter by service
- Download logs

### Health Checks

**Backend Health Check:**
```bash
curl https://backend-production.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-11T12:00:00Z"
}
```

**Frontend Health Check:**
```bash
curl https://frontend-production.up.railway.app
```

**Expected:** HTML page loads

---

## Troubleshooting

### Issue: Backend won't start

**Symptoms:**
- Service shows "Crashed" status
- Logs show "ModuleNotFoundError"

**Solutions:**
1. Check `requirements.txt` is complete
2. Verify Python version (should be 3.11+)
3. Check environment variables are set
4. Review logs for specific error

### Issue: Frontend can't connect to backend

**Symptoms:**
- Frontend loads but shows "Network Error"
- API requests fail

**Solutions:**
1. Verify `VITE_API_URL` is set correctly
2. Check backend is running (visit `/health`)
3. Verify CORS is configured in backend
4. Check backend logs for errors

### Issue: Slow performance

**Symptoms:**
- Requests take >5 seconds
- High memory usage

**Solutions:**
1. Check cache is working (backend logs)
2. Verify database connection is stable
3. Consider upgrading to paid tier for more resources
4. Add Redis for better caching

### Issue: Build fails

**Symptoms:**
- Deployment stuck at "Building"
- Build logs show errors

**Solutions:**
1. Check build command is correct
2. Verify all dependencies are in package files
3. Check for syntax errors in code
4. Review build logs for specific error

---

## Upgrade Path

### Free Tier Limitations

- **Memory:** 512 MB per service
- **CPU:** Shared
- **Sleep:** Services sleep after 30 min inactivity
- **Credits:** $5/month free

### When to Upgrade

Upgrade to paid tier ($5-20/month) when:
- Traffic increases (>1000 requests/day)
- Need faster response times
- Want to add Redis
- Need more memory (>512 MB)

### Paid Tier Benefits

- **Memory:** Up to 8 GB
- **CPU:** Dedicated
- **No sleep:** Always-on services
- **Redis:** Add Redis service
- **Priority support**

---

## Rollback Procedure

### If Deployment Fails

1. Go to Railway dashboard
2. Click on service
3. Click "Deployments" tab
4. Find previous successful deployment
5. Click "Redeploy"

### If Deployment Succeeds But Has Bugs

1. Fix bugs in code
2. Push to GitHub
3. Railway auto-deploys new version

**OR**

1. Rollback to previous deployment (see above)
2. Fix bugs
3. Push to GitHub

---

## Next Steps

1. Deploy backend service
2. Deploy frontend service
3. Test both services
4. Monitor logs and metrics
5. Optimize based on usage

---

**Status:** Ready for deployment once frontend components are complete
