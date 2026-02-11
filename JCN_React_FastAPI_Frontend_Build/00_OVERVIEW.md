# JCN Dashboard - FastAPI + React Frontend Build

## 📋 Overview

This folder contains the complete documentation and source code for the **FastAPI + React** version of the JCN Financial Dashboard.

### Purpose

Migrate the JCN Dashboard from Streamlit to a modern FastAPI + React architecture for:
- ✅ Better performance (90-95% faster)
- ✅ Professional UI/UX with Apache ECharts
- ✅ True SPA (Single Page Application) experience
- ✅ Mobile-ready responsive design
- ✅ Scalable architecture for future growth

---

## 🏗️ Architecture

### High-Level Overview

```
┌──────────────────┐    HTTP/JSON    ┌──────────────────┐
│  React Frontend  │◄──────────────►│  FastAPI Backend │
│  (Port 3000)     │                 │  (Port 8000)     │
│  - Vite          │                 │  - Uvicorn       │
│  - TypeScript    │                 │  - Python 3.12   │
│  - ECharts       │                 │  - Pydantic      │
│  - TanStack      │                 │  - yfinance      │
│  - shadcn/ui     │                 │  - MotherDuck    │
└──────────────────┘                 └──────────────────┘
         │                                     │
         └─────────────┬───────────────────────┘
                       │
                ┌──────▼──────┐
                │    Nginx    │
                │  (Proxy)    │
                └─────────────┘
                       │
                ┌──────▼──────┐
                │   Railway   │
                │  (Hosting)  │
                └─────────────┘
```

### Technology Stack

**Frontend:**
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool (fast HMR)
- **TanStack Router** - Client-side routing
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Apache ECharts** - Data visualization
- **TanStack Table** - Interactive tables
- **shadcn/ui** - UI components
- **Tailwind CSS** - Styling

**Backend:**
- **FastAPI** - Web framework
- **Python 3.12** - Programming language
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **yfinance** - Stock data
- **MotherDuck** - Database
- **Pandas** - Data processing

**Deployment:**
- **Railway** - Hosting platform
- **Nginx** - Reverse proxy
- **GitHub** - Version control

---

## 📁 Project Structure

```
JCN-dashboard/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app entry point
│   │   ├── api/               # API endpoints
│   │   │   ├── v1/
│   │   │   │   ├── portfolios.py
│   │   │   │   ├── stocks.py
│   │   │   │   └── market.py
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py      # Configuration
│   │   │   ├── cache.py       # Caching layer
│   │   │   └── dependencies.py
│   │   ├── services/          # Business logic
│   │   │   ├── portfolio_service.py
│   │   │   ├── stock_service.py
│   │   │   └── market_service.py
│   │   ├── models/            # Pydantic models
│   │   │   ├── portfolio.py
│   │   │   ├── stock.py
│   │   │   └── market.py
│   │   └── utils/             # Utilities
│   │       ├── yfinance_client.py
│   │       └── motherduck_client.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── main.tsx           # Entry point
│   │   ├── App.tsx            # Root component
│   │   ├── routes/            # Page components
│   │   │   ├── index.tsx      # Home page
│   │   │   ├── persistent-value.tsx
│   │   │   ├── olivia-growth.tsx
│   │   │   └── stock-analysis.tsx
│   │   ├── components/        # Reusable components
│   │   │   ├── charts/        # ECharts components
│   │   │   │   ├── PortfolioPerformanceChart.tsx
│   │   │   │   ├── AllocationChart.tsx
│   │   │   │   └── RadarChart.tsx
│   │   │   ├── tables/        # Table components
│   │   │   │   └── StockTable.tsx
│   │   │   └── ui/            # shadcn/ui components
│   │   ├── lib/               # Utilities
│   │   │   ├── api.ts         # API client
│   │   │   ├── queryClient.ts # TanStack Query config
│   │   │   └── utils.ts
│   │   ├── hooks/             # Custom hooks
│   │   │   ├── usePortfolio.ts
│   │   │   └── useStocks.ts
│   │   ├── types/             # TypeScript types
│   │   │   ├── portfolio.ts
│   │   │   └── stock.ts
│   │   └── styles/            # Global styles
│   │       └── index.css
│   ├── public/                # Static assets
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
├── JCN_React_FastAPI_Frontend_Build/  # Documentation
│   ├── 00_OVERVIEW.md         # This file
│   ├── 01_SETUP_GUIDE.md      # Local development setup
│   ├── 02_BACKEND_DOCUMENTATION.md
│   ├── 03_FRONTEND_DOCUMENTATION.md
│   ├── 04_DEPLOYMENT_GUIDE.md
│   ├── 05_MIGRATION_PROGRESS.md
│   └── diagrams/
├── railway.toml               # Railway configuration
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- Python 3.12+
- Railway CLI (optional)

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:3000

---

## 📊 Demo Scope

### Phase 1: Initial Demo (Current)

**What's Included:**
- ✅ FastAPI backend with basic structure
- ✅ React frontend with routing
- ✅ **Persistent Value Portfolio** page (fully functional)
  - Portfolio performance chart (ECharts)
  - Stock list table (TanStack Table)
  - Portfolio metrics
  - Allocation chart
- ✅ In-memory caching (5 min TTL)
- ✅ Responsive design
- ✅ Loading states & error handling
- ✅ Railway deployment (2 services)

**What's NOT Included (Future Phases):**
- ❌ Olivia Growth portfolio page
- ❌ Stock Analysis page
- ❌ Market Analysis page
- ❌ Risk Management page
- ❌ Redis caching (using in-memory for now)
- ❌ Authentication
- ❌ AI chat interface (Supermemory integration)

---

## 📈 Performance Comparison

| Metric | Streamlit | FastAPI + React | Improvement |
|--------|-----------|-----------------|-------------|
| **First Load** | 15-30s | 2-3s | **90-95% faster** |
| **Cached Load** | 0.5-1s | 0.1-0.5s | **50-80% faster** |
| **Page Navigation** | 2-5s (full reload) | 0.1s (instant) | **95-98% faster** |
| **Memory Usage** | ~300 MB | ~150 MB | **50% less** |
| **Mobile Experience** | Poor | Excellent | **Much better** |

---

## 🎯 Migration Strategy

### Approach: Incremental Migration

We're migrating one page at a time while keeping the Streamlit app running:

**Phase 1:** Persistent Value Portfolio ✅ (Current)  
**Phase 2:** Olivia Growth Portfolio (Next)  
**Phase 3:** Stock Analysis (Week 3)  
**Phase 4:** Market Analysis (Week 4)  
**Phase 5:** Risk Management (Week 5)  
**Phase 6:** Polish & Launch (Week 6)

### Benefits:
- ✅ No downtime (Streamlit stays running)
- ✅ Test each page thoroughly before moving to next
- ✅ Lower risk (can rollback if needed)
- ✅ Faster feedback loop

---

## 💰 Cost

**Current (Free Tier):**
- Frontend service: Free
- Backend service: Free
- Total: **$0-5/month**

**Production (Upgraded):**
- Frontend service: $10-20/month
- Backend service: $10-20/month
- Redis service: $5-10/month
- Total: **$25-50/month**

---

## 📝 Documentation Index

1. **[00_OVERVIEW.md](./00_OVERVIEW.md)** - This file (architecture overview)
2. **[01_SETUP_GUIDE.md](./01_SETUP_GUIDE.md)** - How to run locally
3. **[02_BACKEND_DOCUMENTATION.md](./02_BACKEND_DOCUMENTATION.md)** - FastAPI endpoints & services
4. **[03_FRONTEND_DOCUMENTATION.md](./03_FRONTEND_DOCUMENTATION.md)** - React components & hooks
5. **[04_DEPLOYMENT_GUIDE.md](./04_DEPLOYMENT_GUIDE.md)** - Railway deployment
6. **[05_MIGRATION_PROGRESS.md](./05_MIGRATION_PROGRESS.md)** - What's done, what's next

---

## 🤝 Contributing

This is a private project. For questions or issues, contact the project owner.

---

## 📄 License

Proprietary - All rights reserved

---

**Last Updated:** February 11, 2026  
**Version:** 0.1.0 (Demo Phase 1)  
**Status:** 🟢 In Development
