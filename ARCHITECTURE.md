# JCN Dashboard Architecture

## System Overview

The JCN Financial Dashboard is a modern web application built with a React frontend and FastAPI backend, designed for real-time portfolio tracking and analysis.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              React Frontend (TypeScript)                │ │
│  │                                                          │ │
│  │  • Landing Page                                         │ │
│  │  • Dashboard Home                                       │ │
│  │  • Portfolio Pages (3x)                                 │ │
│  │  • Stock Analysis                                       │ │
│  │  • Market Analysis                                      │ │
│  │  • Risk Management                                      │ │
│  │  • About                                                │ │
│  │                                                          │ │
│  │  Components: Sidebar, Theme Toggle, ECharts            │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTPS/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Python)                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    API Layer                            │ │
│  │  /api/v1/portfolios/{id}                               │ │
│  │  /api/v1/stocks/{symbol}                               │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                 Service Layer                           │ │
│  │  • PortfolioService                                     │ │
│  │  • StockService                                         │ │
│  │  • Cache (5-minute TTL)                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                 Data Layer                              │ │
│  │  • MotherDuckClient                                     │ │
│  │  • YFinanceClient                                       │ │
│  │  • Portfolio Holdings Data                              │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬──────────────────────────────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
┌─────────────────────────┐  ┌──────────────────┐
│      MotherDuck         │  │    yfinance      │
│   (DuckDB Cloud)        │  │   (Market Data)  │
│                         │  │                  │
│  • Fundamentals         │  │  • Real-time     │
│  • Quality Scores       │  │    prices        │
│  • Risk Indicators      │  │  • Historical    │
└─────────────────────────┘  └──────────────────┘
```

## Technology Stack

### Frontend

**Core:**
- React 19 - UI framework
- TypeScript - Type safety
- Vite - Build tool and dev server

**Styling:**
- Tailwind CSS 4 - Utility-first CSS
- Custom CSS Variables - Theme system
- Inter Font (Google Fonts) - Typography

**Visualization:**
- ECharts - All charts and graphs
- Lucide React - Icon library

**Routing:**
- Wouter - Lightweight routing

**State Management:**
- React Context API - Theme state
- useState/useEffect - Component state

### Backend

**Core:**
- FastAPI - Web framework
- Uvicorn - ASGI server
- Python 3.11 - Runtime

**Data Access:**
- DuckDB - MotherDuck client
- yfinance - Market data API
- Pandas - Data manipulation

**Utilities:**
- Pydantic - Data validation
- functools - Caching decorator

### Infrastructure

**Deployment:**
- Railway - Hosting platform
- GitHub - Version control
- CI/CD - Automatic deployments

**Database:**
- MotherDuck - Cloud DuckDB instance
- Tables: gurufocus_with_momentum, OBQ_Scores, NDR_BP_SP_history

## Data Flow

### Portfolio Page Load

1. **User navigates to portfolio page**
   - React component mounts
   - `useEffect` triggers data fetch

2. **Frontend makes API request**
   ```
   GET https://jcn-dashboard-production.up.railway.app/api/v1/portfolios/persistent_value
   ```

3. **Backend receives request**
   - API endpoint `/api/v1/portfolios/{portfolio_id}`
   - Calls `portfolio_service.get_portfolio_summary()`

4. **Service layer processes**
   - Check cache (5-minute TTL)
   - If cached: return immediately
   - If not cached: proceed to data fetch

5. **Data fetching**
   - Load portfolio holdings from `portfolio_holdings.py`
   - Fetch current prices from yfinance
   - Fetch fundamentals from MotherDuck
   - Calculate positions, gains, weights

6. **Data processing**
   - Calculate portfolio metrics
   - Generate performance history
   - Calculate sector/industry allocations
   - Format response

7. **Response caching**
   - Store result in memory cache
   - Set 5-minute expiration

8. **Frontend receives data**
   - Parse JSON response
   - Update component state
   - Render UI components

9. **Visualization**
   - ECharts renders performance chart
   - ECharts renders allocation pie charts
   - Tables display holdings data

### Stock Analysis Flow

1. User enters stock symbol
2. Frontend calls `/api/v1/stocks/{symbol}`
3. Backend fetches from yfinance
4. Returns stock info + price history
5. Frontend renders with ECharts

## Component Architecture

### Frontend Components

```
App.tsx (Root)
├── ThemeProvider (Context)
│   ├── Landing.tsx (Route: /)
│   └── DashboardLayout.tsx (Route: /dashboard/*)
│       ├── Sidebar.tsx
│       │   ├── Logo
│       │   ├── Navigation Links
│       │   └── Theme Toggle
│       └── Page Content
│           ├── Home.tsx
│           ├── PersistentValue.tsx
│           ├── OliviaGrowth.tsx
│           ├── PureAlpha.tsx
│           ├── StockAnalysis.tsx
│           ├── MarketAnalysis.tsx
│           ├── RiskManagement.tsx
│           └── About.tsx
```

### Backend Structure

```
app/
├── main.py (FastAPI app)
├── api/v1/
│   ├── portfolios.py (Portfolio endpoints)
│   └── stocks.py (Stock endpoints)
├── services/
│   └── portfolio_service.py (Business logic)
├── models/
│   └── portfolio.py (Data models)
├── utils/
│   ├── motherduck_client.py (MotherDuck integration)
│   └── yfinance_client.py (yfinance wrapper)
├── data/
│   └── portfolio_holdings.py (Holdings data)
└── core/
    └── cache.py (Caching decorator)
```

## Theme System

### Color Variables

**CSS Variables** (`index.css`):
```css
:root {
  --color-background: #fffffe;
  --color-surface: #f9f4ef;
  --color-accent: #00ebc7;
  --color-text-primary: #2b2c34;
  --color-text-secondary: #5f6c7b;
  --color-border: #e3e4e8;
}

.dark {
  --color-background: #0a0a0a;
  --color-surface: #1a1a1a;
  --color-accent: #3b82f6;
  --color-text-primary: #e5e5e5;
  --color-text-secondary: #a3a3a3;
  --color-border: #262626;
}
```

**Tailwind Classes:**
- `bg-background` - Main background
- `bg-surface` - Card/panel background
- `text-accent` - Accent color
- `text-primary` - Main text
- `text-secondary` - Secondary text
- `border-border` - Border color

### Theme Toggle

1. User clicks theme toggle button
2. `ThemeContext.toggleTheme()` called
3. Updates localStorage
4. Toggles `dark` class on `<html>`
5. CSS variables update automatically
6. All components re-render with new colors

## Caching Strategy

### Backend Cache

**Implementation:**
```python
@cached(ttl=300, key_prefix="portfolio")
async def get_portfolio_summary(portfolio_id: str):
    # Function body
```

**Cache Key Format:**
```
portfolio:{portfolio_id}
```

**TTL:** 5 minutes (300 seconds)

**Benefits:**
- Reduces MotherDuck queries
- Faster response times
- Lower API costs
- Better user experience

### Frontend State

- Component-level state with `useState`
- No global state management (yet)
- Data fetched on component mount
- Manual refresh button available

## Performance Optimizations

### Frontend

1. **Code Splitting**
   - Vite automatically splits chunks
   - Lazy loading for routes

2. **Asset Optimization**
   - Images served from CDN
   - Minified JS/CSS bundles
   - Tree-shaking unused code

3. **Rendering**
   - Conditional rendering
   - Memoization where needed
   - Efficient re-renders

### Backend

1. **Caching**
   - 5-minute cache for portfolio data
   - Reduces database queries
   - In-memory storage

2. **Data Fetching**
   - Parallel requests to yfinance
   - Batch queries to MotherDuck
   - Efficient pandas operations

3. **Response**
   - JSON serialization
   - Gzip compression
   - Fast response times

## Security

### Frontend

- HTTPS only
- No sensitive data in localStorage
- API URL from environment variables
- CORS headers validated

### Backend

- Environment variables for secrets
- MOTHERDUCK_TOKEN not in code
- Input validation with Pydantic
- Rate limiting (future)

### Database

- MotherDuck token authentication
- Read-only access for app
- No SQL injection risk (parameterized queries)

## Deployment

### Railway Configuration

**Frontend Service:**
- Build: `npm install && npm run build`
- Start: `npx serve -s dist -l $PORT`
- Port: Auto-assigned
- Domain: jcnfinancial.up.railway.app

**Backend Service:**
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Port: Auto-assigned (8080 default)
- Domain: jcn-dashboard-production.up.railway.app

**Environment Variables:**
- `MOTHERDUCK_TOKEN` - Set in Railway dashboard

### CI/CD Flow

1. Developer pushes to GitHub `master`
2. Railway detects commit
3. Triggers build for both services
4. Runs build commands
5. Deploys new containers
6. Health checks verify deployment
7. Routes traffic to new version

## Monitoring

### Health Checks

**Frontend:**
- HTTP 200 on root path
- Assets loading correctly

**Backend:**
- `GET /` returns API info
- `GET /api/v1/portfolios/` returns list

### Logging

- Railway captures stdout/stderr
- View logs in Railway dashboard
- Error tracking (future: Sentry)

## Future Architecture Improvements

1. **State Management**
   - Add React Query for data fetching
   - Centralized cache management
   - Optimistic updates

2. **Backend**
   - Add Redis for distributed caching
   - WebSocket for real-time updates
   - Background jobs for data refresh

3. **Database**
   - Add PostgreSQL for user data
   - Store portfolio edits
   - Transaction history

4. **Monitoring**
   - Add Sentry for error tracking
   - Performance monitoring
   - User analytics

5. **Testing**
   - Unit tests for components
   - Integration tests for API
   - E2E tests with Playwright

## Scalability Considerations

### Current Limits

- Single backend instance
- In-memory caching (not shared)
- No load balancing
- Manual data refresh

### Future Scaling

1. **Horizontal Scaling**
   - Multiple backend instances
   - Redis for shared cache
   - Load balancer

2. **Database**
   - Connection pooling
   - Query optimization
   - Read replicas

3. **CDN**
   - Static assets on CDN
   - Edge caching
   - Global distribution

4. **Caching**
   - Redis cluster
   - Cache warming
   - Intelligent invalidation

---

Last Updated: February 11, 2026
