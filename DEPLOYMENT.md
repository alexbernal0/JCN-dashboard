# JCN Dashboard - Deployment Guide

## Railway Deployment

This application consists of two separate services that need to be deployed independently on Railway:

### Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  React Frontend │ ──────> │ FastAPI Backend │
│  (Port 3000)    │         │  (Port 8000)    │
└─────────────────┘         └─────────────────┘
```

---

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Code pushed to GitHub (branch: `feature/fastapi-react`)
3. **MotherDuck Token**: For database access (if using real data)

---

## Deployment Steps

### Step 1: Deploy Backend Service

1. **Create New Project** on Railway
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `alexbernal0/JCN-dashboard`
   - Select branch: `feature/fastapi-react`

2. **Configure Backend Service**
   - Name: `jcn-backend`
   - Root Directory: `/backend`
   - Build Command: (auto-detected from railway.toml)
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   ```
   PORT=8000
   DEBUG=false
   MOTHERDUCK_TOKEN=<your-token>  # Optional, only if using real data
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Note the backend URL (e.g., `https://jcn-backend.up.railway.app`)

### Step 2: Deploy Frontend Service

1. **Add Service to Same Project**
   - In the same Railway project, click "New Service"
   - Select "GitHub Repo" again
   - Choose the same repository and branch

2. **Configure Frontend Service**
   - Name: `jcn-frontend`
   - Root Directory: `/frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npx serve -s dist -l $PORT`

3. **Set Environment Variables**
   ```
   PORT=3000
   VITE_API_URL=<backend-url-from-step-1>
   VITE_USE_MOCK=false  # Set to 'true' for mock data, 'false' for real data
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Note the frontend URL (e.g., `https://jcn-frontend.up.railway.app`)

### Step 3: Update CORS Settings

1. Go to backend service settings
2. Add frontend URL to allowed origins in `app/core/config.py`:
   ```python
   CORS_ORIGINS: List[str] = [
       "http://localhost:3000",
       "http://localhost:5173",
       "https://*.railway.app",
       "https://*.up.railway.app",
       "https://jcn-frontend.up.railway.app",  # Add your frontend URL
   ]
   ```
3. Commit and push changes
4. Railway will auto-deploy

---

## Environment Variables Reference

### Backend (`jcn-backend`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | 8000 | Port for FastAPI server |
| `DEBUG` | No | false | Enable debug mode |
| `MOTHERDUCK_TOKEN` | No | "" | MotherDuck database token |

### Frontend (`jcn-frontend`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | 3000 | Port for frontend server |
| `VITE_API_URL` | Yes | - | Backend API URL |
| `VITE_USE_MOCK` | No | false | Use mock data (true/false) |

---

## Testing Deployment

### 1. Test Backend

```bash
# Health check
curl https://your-backend-url.up.railway.app/health

# API docs
open https://your-backend-url.up.railway.app/api/docs

# Test portfolio endpoint (mock data)
curl https://your-backend-url.up.railway.app/api/v1/mock/portfolios/
```

### 2. Test Frontend

1. Open frontend URL in browser
2. Navigate to "Persistent Value" portfolio
3. Verify charts and tables load correctly
4. Test stock search functionality

---

## Monitoring

### Railway Dashboard

- **Logs**: View real-time logs for each service
- **Metrics**: CPU, memory, network usage
- **Deployments**: History of all deployments
- **Environment**: Manage environment variables

### Health Checks

- Backend: `/health` endpoint
- Frontend: `/` endpoint (serves React app)

---

## Troubleshooting

### Backend Issues

**Problem**: 500 Internal Server Error

**Solution**:
1. Check logs in Railway dashboard
2. Verify environment variables are set
3. Check MotherDuck token (if using real data)
4. Try using mock data first (`/api/v1/mock/*` endpoints)

**Problem**: CORS errors

**Solution**:
1. Add frontend URL to `CORS_ORIGINS` in `app/core/config.py`
2. Redeploy backend service

### Frontend Issues

**Problem**: Blank page or loading forever

**Solution**:
1. Check browser console for errors
2. Verify `VITE_API_URL` is set correctly
3. Test backend health endpoint directly
4. Try with mock data (`VITE_USE_MOCK=true`)

**Problem**: API calls failing

**Solution**:
1. Check Network tab in browser DevTools
2. Verify backend URL is correct
3. Check CORS configuration
4. Test backend endpoints directly with curl

---

## Scaling

### Free Tier Limits

- **Execution Time**: 500 hours/month
- **Memory**: 512 MB per service
- **Bandwidth**: 100 GB/month

### Upgrading

For production use:
1. Upgrade to Railway Pro ($20/month)
2. Add Redis for caching
3. Use MotherDuck for real-time data
4. Set up custom domain

---

## Custom Domain (Optional)

1. Go to frontend service settings
2. Click "Settings" → "Domains"
3. Click "Custom Domain"
4. Enter your domain (e.g., `dashboard.jcn.com`)
5. Add CNAME record to your DNS:
   ```
   CNAME dashboard.jcn.com -> <railway-url>
   ```

---

## Rollback

If deployment fails:
1. Go to "Deployments" tab
2. Find last working deployment
3. Click "Redeploy"

---

## CI/CD

Railway automatically deploys on git push to the configured branch.

To disable auto-deploy:
1. Go to service settings
2. Click "Settings" → "Service"
3. Toggle "Auto Deploy" off

---

## Cost Estimate

### Free Tier
- **Cost**: $0/month
- **Limits**: 500 hours execution time
- **Best for**: Development and testing

### Pro Tier
- **Cost**: $20/month + usage
- **Limits**: Unlimited execution time
- **Best for**: Production

---

## Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **GitHub Issues**: https://github.com/alexbernal0/JCN-dashboard/issues

---

## Next Steps

1. ✅ Deploy both services to Railway
2. ✅ Test with mock data
3. ⏳ Configure MotherDuck for real data
4. ⏳ Set up custom domain
5. ⏳ Add monitoring and alerts
6. ⏳ Optimize performance
7. ⏳ Add authentication (if needed)

---

**Last Updated**: February 11, 2026
