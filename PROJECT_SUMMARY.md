# JCN Financial Dashboard - Project Summary

## 📋 Overview
Migration of JCN Financial Dashboard from Streamlit to React + FastAPI, deployed on Railway.

---

## 🔗 Project Links

### GitHub Repository
**Main Repository:** https://github.com/alexbernal0/JCN-dashboard

### Railway Deployments

**Frontend (React):**
- URL: https://jcnfinancial.up.railway.app
- Service: Frontend
- Framework: React + Vite + TypeScript + Tailwind CSS

**Backend (FastAPI):**
- URL: https://jcn-dashboard-production.up.railway.app
- Service: Backend
- Framework: FastAPI + Python 3.9
- API Docs: https://jcn-dashboard-production.up.railway.app/api/docs

### Original Streamlit App
- Located in same repository under `/pages/` directory
- Main file: `app.py`
- Persistent Value page: `pages/1_📊_Persistent_Value.py`

---

## 📁 Project Structure

```
jcn-build/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── pages/           # Page components
│   │   │   ├── Home.tsx
│   │   │   ├── PersistentValue.tsx
│   │   │   └── ...
│   │   ├── components/      # Reusable components
│   │   ├── hooks/           # Custom React hooks
│   │   │   └── usePortfolio.ts
│   │   └── index.css        # Global styles
│   ├── railway.toml         # Railway frontend config
│   └── package.json
│
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/v1/          # API routes
│   │   ├── models/          # Pydantic models
│   │   ├── services/        # Business logic
│   │   │   └── portfolio_service_v2.py
│   │   ├── data/            # Data files
│   │   │   ├── persistent_value_snapshot.json
│   │   │   └── default_portfolio.json
│   │   └── main.py          # FastAPI app entry
│   ├── railway.toml         # Railway backend config
│   └── requirements.txt
│
├── pages/                    # Original Streamlit app
│   └── 1_📊_Persistent_Value.py
├── app.py                    # Streamlit main file
└── cache_snapshots/          # Cached stock data
    └── persistent_value_snapshot.csv
```

---

## 🎯 Current Status

### ✅ Completed Features

**Frontend:**
- ✅ Sidebar navigation with portfolio sections
- ✅ Dark mode toggle
- ✅ Persistent Value page layout
- ✅ Portfolio metrics cards (Total Value, Gain/Loss, Holdings, Cash)
- ✅ Performance chart (Portfolio vs S&P 500)
- ✅ Allocation pie chart
- ✅ Holdings table with Symbol, Shares, Value, Gain/Loss
- ✅ Basic Portfolio Input table (read-only)

**Backend:**
- ✅ FastAPI server with CORS enabled
- ✅ Portfolio API endpoints (`/api/v1/portfolios/`, `/api/v1/portfolios/{portfolio_id}`)
- ✅ Mock portfolio endpoints for testing
- ✅ Snapshot system to avoid yfinance rate limits
- ✅ 21 default holdings pre-loaded from Streamlit cache

**Deployment:**
- ✅ Frontend deployed on Railway
- ✅ Backend deployed on Railway
- ✅ GitHub integration for auto-deployment

### ⚠️ Known Issues

1. **API Endpoint Mismatch:**
   - Frontend calls: `/api/v1/user-portfolios/persistent_value`
   - Backend provides: `/api/v1/portfolios/{portfolio_id}`
   - **Fix needed:** Update frontend to use correct endpoint

2. **Portfolio Input Component:**
   - Read-only table works ✅
   - Edit mode with state management breaks the page ❌
   - **Issue:** Adding `useState` for edit functionality causes "Failed to fetch" error
   - **Next step:** Debug React rendering issue or create separate component

3. **Data Loading:**
   - Page shows "No data available" or "Failed to fetch"
   - Backend returns 404 for incorrect endpoint
   - **Fix needed:** Align frontend/backend API contracts

---

## 🛠️ Technology Stack

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite
- **Language:** TypeScript
- **Styling:** Tailwind CSS 4
- **Charts:** ECharts (via echarts-for-react)
- **Icons:** Lucide React
- **HTTP Client:** Fetch API

### Backend
- **Framework:** FastAPI 0.115.6
- **Language:** Python 3.9
- **Data:** yfinance, pandas, numpy
- **CORS:** fastapi-cors-middleware
- **Server:** Uvicorn

### Deployment
- **Platform:** Railway
- **CI/CD:** GitHub integration (auto-deploy on push)
- **Frontend Build:** `npm run build` → static files
- **Backend Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 📊 Default Portfolio Holdings (21 stocks)

| Symbol | Cost Basis | Shares  |
|--------|-----------|---------|
| SPMO   | $97.40    | 14,301  |
| ASML   | $660.32   | 1,042   |
| MNST   | $50.00    | 8,234   |
| MSCI   | $595.23   | 2,016   |
| COST   | $655.21   | 798     |
| AVGO   | $138.00   | 6,088   |
| MA     | $418.76   | 1,389   |
| FICO   | $1,850.00 | 778     |
| SPGI   | $427.93   | 1,554   |
| IDXX   | $378.01   | 1,570   |
| ISRG   | $322.50   | 2,769   |
| V      | $276.65   | 2,338   |
| CAT    | $287.70   | 1,356   |
| ORLY   | $91.00    | 4,696   |
| HEI    | $172.00   | 1,804   |
| NFLX   | $80.82    | 10,083  |
| WM     | $177.77   | 5,000   |
| TSLA   | $270.00   | 5,022   |
| AAPL   | $181.40   | 2,865   |
| LRCX   | $73.24    | 18,667  |
| TSM    | $99.61    | 5,850   |

---

## 🔧 Next Steps

### Immediate Fixes
1. **Fix API endpoint mismatch** - Update `frontend/src/hooks/usePortfolio.ts` to call correct backend endpoint
2. **Debug Portfolio Input** - Investigate why adding state breaks the page
3. **Test data flow** - Verify backend → frontend data pipeline works end-to-end

### Feature Development
1. **Portfolio Input Module** (Module 1)
   - Editable table with Lock/Edit toggle
   - Add/Remove rows (max 30)
   - Save functionality
   - Pre-populated with 21 holdings

2. **Remaining Modules** (from Streamlit app)
   - Module 2: Allocation Charts (4 pie charts)
   - Module 3: Benchmark Comparison
   - Module 4: Fundamental Metrics
   - Module 5: Quality Radar Charts
   - Module 6: Trend Analysis
   - Module 7: AI-Generated News

---

## 📝 Development Notes

### Railway Configuration

**Frontend (`frontend/railway.toml`):**
```toml
[build]
builder = "nixpacks"
buildCommand = "npm install && npm run build"

[deploy]
startCommand = "npx serve -s dist -l $PORT"
```

**Backend (`backend/railway.toml`):**
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### API Base URL
- Hardcoded in `frontend/src/hooks/usePortfolio.ts`:
  ```typescript
  const API_BASE_URL = 'https://jcn-dashboard-production.up.railway.app/api/v1';
  ```

### Snapshot System
- Backend uses cached data from `backend/app/data/persistent_value_snapshot.json`
- Converted from Streamlit CSV cache: `cache_snapshots/persistent_value_snapshot.csv`
- Avoids yfinance rate limiting (429 errors)

---

## 🐛 Debugging Tips

1. **Check Railway logs:**
   - Frontend: Railway dashboard → Frontend service → Logs
   - Backend: Railway dashboard → Backend service → Logs

2. **Test backend API:**
   ```bash
   curl https://jcn-dashboard-production.up.railway.app/api/v1/portfolios/
   ```

3. **Check browser console:**
   - Open DevTools (F12)
   - Look for network errors or React errors

4. **Verify API docs:**
   - Visit: https://jcn-dashboard-production.up.railway.app/api/docs
   - Test endpoints directly in Swagger UI

---

## 📞 Support

For issues or questions:
1. Check Railway deployment logs
2. Review GitHub commit history
3. Test API endpoints in Swagger docs
4. Check browser console for frontend errors

---

**Last Updated:** February 13, 2026
**Current Commit:** 035bcfd (basic Portfolio Input table - read-only)
