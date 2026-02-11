# Setup Guide - JCN Dashboard FastAPI + React

**Last Updated:** February 11, 2026  
**Status:** Backend Complete, Frontend In Progress

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Environment Variables](#environment-variables)
6. [Running Locally](#running-locally)
7. [Testing](#testing)

---

## Prerequisites

### Required Software

- **Python 3.11+** - Backend runtime
- **Node.js 22+** - Frontend runtime
- **pnpm** - Package manager (or npm/yarn)
- **Git** - Version control

### Required Accounts

- **MotherDuck** - Database (already configured)
- **Railway** - Deployment platform

---

## Project Structure

```
jcn-dashboard/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── core/
│   │   │   ├── config.py      # Configuration management
│   │   │   └── cache.py       # In-memory caching
│   │   ├── models/
│   │   │   └── portfolio.py   # Pydantic models
│   │   ├── services/
│   │   │   └── portfolio_service.py  # Business logic
│   │   ├── utils/
│   │   │   └── yfinance_client.py    # Stock data fetching
│   │   └── api/
│   │       └── v1/
│   │           ├── portfolios.py     # Portfolio endpoints
│   │           └── stocks.py         # Stock endpoints
│   ├── requirements.txt       # Python dependencies
│   └── README.md             # Backend documentation
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── main.tsx          # React entry point
│   │   ├── App.tsx           # Root component
│   │   ├── components/       # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API client
│   │   └── types/            # TypeScript types
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite configuration
│
├── JCN_React_FastAPI_Frontend_Build/  # Documentation
│   ├── 00_OVERVIEW.md
│   ├── 01_SETUP_GUIDE.md (this file)
│   ├── 02_BACKEND_DOCUMENTATION.md
│   ├── 03_FRONTEND_DOCUMENTATION.md
│   ├── 04_DEPLOYMENT_GUIDE.md
│   └── BUILD_TODO.md
│
└── railway.toml              # Railway deployment config
```

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables

Create `.env` file in `backend/` directory:

```env
# Required
MOTHERDUCK_TOKEN=your_motherduck_token_here

# Optional (for news features)
FINNHUB_API_KEY=your_finnhub_key
GROK_API_KEY=your_grok_key

# Server Config
HOST=0.0.0.0
PORT=8000
```

### 5. Run Backend Server

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Verify Backend is Running

Open browser to:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
pnpm install
# or: npm install
# or: yarn install
```

### 3. Set Environment Variables

Create `.env` file in `frontend/` directory:

```env
VITE_API_URL=http://localhost:8000
```

### 4. Run Frontend Development Server

```bash
pnpm dev
# or: npm run dev
# or: yarn dev
```

### 5. Verify Frontend is Running

Open browser to: http://localhost:5173

---

## Environment Variables

### Backend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MOTHERDUCK_TOKEN` | ✅ Yes | MotherDuck database token | `md_xxx...` |
| `FINNHUB_API_KEY` | ❌ No | Finnhub news API key | `xxx...` |
| `GROK_API_KEY` | ❌ No | Grok API key | `xxx...` |
| `HOST` | ❌ No | Server host (default: 0.0.0.0) | `0.0.0.0` |
| `PORT` | ❌ No | Server port (default: 8000) | `8000` |

### Frontend Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_API_URL` | ✅ Yes | Backend API URL | `http://localhost:8000` |

---

## Running Locally

### Option 1: Run Both Services Separately

**Terminal 1 (Backend):**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
pnpm dev
```

### Option 2: Use Docker Compose (Future)

```bash
docker-compose up
```

---

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
pnpm test
```

### API Testing

Use the interactive API docs at http://localhost:8000/docs to test endpoints.

---

## Common Issues

### Issue: Backend won't start

**Solution:** Check that:
1. Virtual environment is activated
2. All dependencies are installed
3. `MOTHERDUCK_TOKEN` is set in `.env`

### Issue: Frontend can't connect to backend

**Solution:** Check that:
1. Backend is running on port 8000
2. `VITE_API_URL` is set correctly in frontend `.env`
3. CORS is configured properly in backend

### Issue: MotherDuck connection fails

**Solution:** Verify:
1. Token is valid and not expired
2. Internet connection is working
3. MotherDuck service is operational

---

## Next Steps

1. Read [Backend Documentation](./02_BACKEND_DOCUMENTATION.md)
2. Read [Frontend Documentation](./03_FRONTEND_DOCUMENTATION.md)
3. Read [Deployment Guide](./04_DEPLOYMENT_GUIDE.md)
4. Check [Build TODO](./BUILD_TODO.md) for remaining work

---

## Support

For issues or questions:
1. Check the documentation in `JCN_React_FastAPI_Frontend_Build/`
2. Review the code comments
3. Check the GitHub issues

---

**Status:** ✅ Backend fully functional | 🔄 Frontend in progress
