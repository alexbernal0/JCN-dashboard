# Railway Best Practices for Streamlit Apps

**Date:** February 3, 2026  
**Source:** Official Railway Documentation (https://docs.railway.com)  
**Purpose:** Apply Railway best practices to JCN Dashboard

---

## Overview

Railway is a modern cloud platform optimized for developer experience. This document summarizes Railway's official best practices and how they apply to Streamlit applications like the JCN Dashboard.

---

## 1. Private Networking ⭐⭐⭐

### What It Is:
Private networking allows services within a Railway project to communicate internally without exposing them publicly.

### Benefits:
- **Faster communication:** Private network routing is faster than public internet
- **No egress costs:** Service-to-service communication on private network is free
- **Increased security:** Services not exposed to public internet

### How to Use:
```python
# Instead of public URL:
DATABASE_URL = "postgresql://user:pass@mydb.up.railway.app:5432/db"

# Use private hostname:
DATABASE_URL = "postgresql://user:pass@mydb.railway.internal:5432/db"
```

### Railway Environment Variables:
- `RAILWAY_PRIVATE_DOMAIN` - Private domain for your service
- `DATABASE_URL` - Automatically uses private networking

### Application to JCN Dashboard:
- ✅ Already using `DATABASE_URL` for MotherDuck (if applicable)
- ⚠️ Verify MotherDuck connection uses private networking (if hosted on Railway)
- ⚠️ If MotherDuck is external cloud service, private networking doesn't apply

**Action:** Check MotherDuck connection string and verify it uses private networking if applicable.

---

## 2. Deploy Related Services in Same Project ⭐⭐

### What It Is:
Keep all related services (app + database + cache) in a single Railway project.

### Benefits:
- **Private networking scoped to project:** All services can communicate privately
- **Easier variable management:** Reference variables between services
- **Reduced project clutter:** One project instead of many
- **Shared environment:** All services in same region

### How to Use:
```bash
# In Railway dashboard:
# 1. Create a project
# 2. Add all related services to that project
#    - Streamlit app
#    - Database (if self-hosted)
#    - Redis cache (if needed)
```

### Application to JCN Dashboard:
- ✅ JCN Dashboard app is in one project
- ⚠️ If using self-hosted MotherDuck, add it to same project
- ⚠️ If using external MotherDuck, this doesn't apply

**Action:** Verify all related services are in same Railway project.

---

## 3. Use Reference Variables ⭐⭐

### What It Is:
Dynamically reference environment variables from other services in the same project.

### Benefits:
- **No manual copying:** Variables update automatically
- **Always in sync:** Change domain once, updates everywhere
- **Cleaner configuration:** No hard-coded values

### How to Use:
```bash
# Instead of hard-coding:
BACKEND_URL=https://my-backend-abc123.up.railway.app

# Use reference variable:
BACKEND_URL=${{Backend.RAILWAY_PUBLIC_DOMAIN}}

# Or for private networking:
BACKEND_URL=${{Backend.RAILWAY_PRIVATE_DOMAIN}}
```

### Application to JCN Dashboard:
- ⚠️ Check if any environment variables reference other services
- ⚠️ If yes, use reference variables instead of hard-coded values

**Action:** Review environment variables and convert hard-coded service URLs to reference variables.

---

## 4. Regional Deployments ⭐⭐⭐

### What It Is:
Deploy your app in the region closest to your users and database.

### Benefits:
- **Lower latency:** Reduced distance = faster response times
- **Better user experience:** Faster page loads
- **Optimized database queries:** App and database in same region

### Available Regions:
- US East (Virginia, USA)
- EU West (Amsterdam, Netherlands)
- Southeast Asia (Singapore)

### How to Use:
```bash
# In Railway dashboard:
# 1. Go to service Settings > Deploy
# 2. Find "Regions" field
# 3. Select region(s)
# 4. Redeploy
```

### Latency Impact:
| Scenario | Latency per Query |
|----------|-------------------|
| Same region | 1-5ms |
| Different region (same continent) | 20-50ms |
| Different continent | 50-150ms |

### Application to JCN Dashboard:
- ⚠️ **CRITICAL:** Verify app and MotherDuck are in same region
- ⚠️ If not, move app to MotherDuck's region

**Example:**
- If MotherDuck is in US East, deploy Railway app in US East
- If MotherDuck is in EU, deploy Railway app in EU West

**Action:** Check regions and ensure they match.

---

## 5. Horizontal Scaling with Replicas ⭐

### What It Is:
Run multiple instances (replicas) of your app for high availability and load distribution.

### Benefits:
- **Higher capacity:** Each replica gets full resources
- **Load balancing:** Traffic distributed across replicas
- **High availability:** If one replica fails, others continue

### How to Use:
```bash
# In Railway dashboard:
# 1. Go to service Settings > Deploy
# 2. Find "Regions" field
# 3. Increase number of instances per region
```

### Resource Allocation:
- **Pro Plan:** Each replica gets up to 24 vCPU and 24GB memory
- **Example:** 2 replicas = 48 vCPU and 48GB memory total

### Environment Variables:
- `RAILWAY_REPLICA_ID` - Unique ID for each replica
- `RAILWAY_REPLICA_REGION` - Region of each replica

### Application to JCN Dashboard:
- ⚠️ Start with 1 replica (current)
- ⚠️ Monitor traffic and resource usage
- ⚠️ Scale to 2+ replicas if needed

**Action:** Monitor Railway metrics and scale if CPU/memory usage is high.

---

## 6. Healthchecks ⭐⭐

### What It Is:
Railway queries your app's healthcheck endpoint to determine if it's ready for traffic.

### Benefits:
- **Zero-downtime deployments:** Old version stays up until new version is healthy
- **Automatic recovery:** Unhealthy deployments are restarted
- **Better reliability:** Only healthy instances receive traffic

### How to Configure:
```toml
# railway.toml
[deploy]
healthcheckPath = "/"
healthcheckTimeout = 100
```

### Healthcheck Behavior:
- Railway sends HTTP GET request to `healthcheckPath`
- Expects HTTP 200 response
- Retries until timeout (default 300s)
- If timeout, deployment fails

### Application to JCN Dashboard:
- ✅ Already configured: `healthcheckPath = "/"`
- ✅ Already configured: `healthcheckTimeout = 100`
- ✅ Streamlit's root path returns 200 when ready

**Action:** No changes needed. Current configuration is optimal.

---

## 7. Restart Policy ⭐⭐

### What It Is:
Automatically restart your app if it crashes.

### Benefits:
- **Automatic recovery:** No manual intervention needed
- **Higher uptime:** App restarts automatically
- **Better reliability:** Handles transient errors

### How to Configure:
```toml
# railway.toml
[deploy]
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Restart Policy Types:
- `ON_FAILURE` - Restart only if app exits with non-zero code
- `NEVER` - Never restart (not recommended)
- `ALWAYS` - Always restart (not recommended for web apps)

### Application to JCN Dashboard:
- ✅ Already configured: `restartPolicyType = "ON_FAILURE"`
- ✅ Already configured: `restartPolicyMaxRetries = 10`

**Action:** No changes needed. Current configuration is optimal.

---

## 8. Build Optimization ⭐⭐

### What It Is:
Optimize your build process to reduce deployment time.

### Benefits:
- **Faster deployments:** Less time waiting for builds
- **Lower costs:** Less build time = lower costs
- **Better developer experience:** Faster iteration

### Best Practices:

#### Use NIXPACKS (Recommended):
```toml
# railway.toml
[build]
builder = "NIXPACKS"
```

**Benefits:**
- Automatic dependency detection
- Build caching
- Optimized for Python apps

#### Use .dockerignore:
```
# .dockerignore
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.git/
.gitignore
*.md
cache_snapshots/
*.json
*.jpg
*.png
*.webp
```

**Benefits:**
- Smaller build context
- Faster uploads
- Faster builds

### Application to JCN Dashboard:
- ✅ Already using NIXPACKS
- ⚠️ Add `.dockerignore` to exclude unnecessary files

**Action:** Create `.dockerignore` file to exclude cache files and images.

---

## 9. Environment Variables ⭐⭐⭐

### What It Is:
Store configuration and secrets as environment variables.

### Benefits:
- **Security:** Secrets not in code
- **Flexibility:** Change config without code changes
- **Railway integration:** Automatic injection

### Best Practices:

#### Use Railway Environment Variables:
```bash
# In Railway dashboard:
# 1. Go to service Settings > Variables
# 2. Add environment variables
# 3. Railway injects them at runtime
```

#### Access in Code:
```python
import os

# Good:
MOTHERDUCK_TOKEN = os.getenv("MOTHERDUCK_TOKEN")

# Bad (don't use st.secrets on Railway):
MOTHERDUCK_TOKEN = st.secrets["MOTHERDUCK_TOKEN"]
```

### Application to JCN Dashboard:
- ✅ Already using `os.getenv()` for API keys
- ⚠️ Verify all secrets are in Railway environment variables

**Required Environment Variables:**
- `MOTHERDUCK_TOKEN` - MotherDuck database token
- `FINNHUB_API_KEY` - Finnhub API key (if used)
- `PORT` - Railway automatically sets this

**Action:** Verify all environment variables are set in Railway dashboard.

---

## 10. Monitoring & Logging ⭐⭐

### What It Is:
Monitor your app's performance and debug issues with logs.

### Railway Metrics:
- **CPU Usage:** % of allocated CPU used
- **Memory Usage:** % of allocated memory used
- **Network Usage:** Bytes sent/received
- **HTTP Logs:** Request/response details

### How to Access:
```bash
# In Railway dashboard:
# 1. Go to your service
# 2. Click "Metrics" tab
# 3. View real-time metrics

# For logs:
# 1. Click "Logs" tab
# 2. View real-time logs
# 3. Filter by log level, time, etc.
```

### HTTP Log Fields (for Performance Debugging):
- `totalDuration` - Total request time (ms)
- `upstreamRqDuration` - App response time (ms)
- `httpStatus` - Response status code
- `path` - Request path

### Finding Slow Requests:
```bash
# In Railway logs, filter by:
@totalDuration:>1000  # Requests > 1 second
```

### Application to JCN Dashboard:
- ⚠️ Monitor metrics after deployment
- ⚠️ Check for high CPU/memory usage
- ⚠️ Identify slow endpoints

**Action:** Review Railway metrics and logs after deployment.

---

## 11. Troubleshooting Slow Apps ⭐⭐⭐

### Common Causes & Solutions:

#### 1. Database Queries
**Problem:** Slow queries without indexes  
**Solution:** Add database indexes, use connection pooling  
**JCN Dashboard:** ✅ Already using connection pooling with `@st.cache_resource`

#### 2. Wrong Region
**Problem:** App and database in different regions  
**Solution:** Deploy in same region  
**JCN Dashboard:** ⚠️ Verify regions match

#### 3. Not Using Private Networking
**Problem:** Services communicate over public internet  
**Solution:** Use `*.railway.internal` hostnames  
**JCN Dashboard:** ⚠️ Check if applicable

#### 4. Resource Constraints
**Problem:** Hitting CPU/memory limits  
**Solution:** Upgrade plan or optimize code  
**JCN Dashboard:** ⚠️ Monitor metrics

#### 5. Large Container Images
**Problem:** Slow to pull on deployment  
**Solution:** Optimize Dockerfile, use `.dockerignore`  
**JCN Dashboard:** ⚠️ Add `.dockerignore`

#### 6. Slow Application Startup
**Problem:** Long initialization time  
**Solution:** Optimize startup code, use lazy loading  
**JCN Dashboard:** ⚠️ Monitor healthcheck timeout

---

## 12. Production Readiness Checklist ⭐⭐⭐

### Before Going to Production:

#### Infrastructure:
- [ ] Services in same project
- [ ] Private networking enabled (if applicable)
- [ ] App and database in same region
- [ ] Healthchecks configured
- [ ] Restart policy set to ON_FAILURE
- [ ] Environment variables set

#### Code:
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Caching implemented
- [ ] Input validation added
- [ ] No hard-coded secrets

#### Testing:
- [ ] Load testing completed
- [ ] Error scenarios tested
- [ ] Performance benchmarks met
- [ ] All pages tested
- [ ] Mobile responsiveness checked

#### Monitoring:
- [ ] Metrics dashboard reviewed
- [ ] Alerts configured
- [ ] Log aggregation set up
- [ ] Performance monitoring enabled

#### Documentation:
- [ ] README updated
- [ ] Deployment instructions documented
- [ ] Environment variables documented
- [ ] Troubleshooting guide created

---

## JCN Dashboard Compliance Status

| Best Practice | Status | Action Needed |
|---------------|--------|---------------|
| Private Networking | ⚠️ Unknown | Verify MotherDuck connection |
| Same Project | ✅ Good | None |
| Reference Variables | ⚠️ Unknown | Check if applicable |
| Regional Deployment | ⚠️ Unknown | Verify regions match |
| Horizontal Scaling | ✅ Good | Monitor and scale if needed |
| Healthchecks | ✅ Good | None |
| Restart Policy | ✅ Good | None |
| Build Optimization | 🟡 Partial | Add `.dockerignore` |
| Environment Variables | ✅ Good | Verify all are set |
| Monitoring | ⚠️ Unknown | Review after deployment |
| Troubleshooting | ✅ Good | Caching implemented |
| Production Readiness | 🟡 Partial | Complete checklist |

---

## Summary

Railway provides excellent infrastructure for Streamlit apps. The JCN Dashboard is already well-configured in most areas. Key actions:

### Immediate Actions:
1. ⚠️ Verify app and MotherDuck are in same region
2. ⚠️ Check if private networking is applicable
3. ⚠️ Add `.dockerignore` file

### Post-Deployment Actions:
1. ⚠️ Monitor Railway metrics
2. ⚠️ Review HTTP logs for slow requests
3. ⚠️ Set up alerts for high resource usage

### Future Actions:
1. ⚠️ Complete production readiness checklist
2. ⚠️ Set up load testing
3. ⚠️ Implement advanced monitoring

---

**Document Status:** Complete  
**Next Step:** Apply best practices to JCN Dashboard
