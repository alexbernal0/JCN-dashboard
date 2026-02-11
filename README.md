# JCN Financial Dashboard

Professional investment dashboard providing real-time portfolio tracking, analysis, and risk management tools.

## 🚀 Features

### Portfolio Management
- **Three Investment Portfolios**
  - Persistent Value: Value-focused investment strategy
  - Olivia Growth: Growth-focused technology stocks
  - Pure Alpha: Alpha-generating investment strategy
- Real-time position tracking with cost basis and gains/losses
- Performance comparison vs S&P 500 benchmark
- Sector and industry allocation analysis
- Portfolio metrics dashboard (total value, gains, holdings, cash)

### Stock Analysis
- Individual stock research and analysis
- Real-time price data and charts
- Fundamental metrics and company information
- Historical performance tracking

### Data Integration
- **MotherDuck**: Fundamental analysis and quality metrics
- **yfinance**: Real-time market data and historical prices
- **DuckDB**: High-performance data queries
- Automatic data caching for optimal performance

### User Experience
- Dark/Light mode toggle with Happy Hues color palette
- Responsive design for all screen sizes
- Fast loading with optimized data fetching
- Clean, modern UI with Inter font
- Interactive ECharts visualizations

## 🏗️ Architecture

### Frontend
- **Framework**: React 19 with TypeScript
- **Styling**: Tailwind CSS 4 with custom theme system
- **Charts**: ECharts for all visualizations
- **Icons**: Lucide React
- **Build Tool**: Vite
- **Deployment**: Railway

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Data Sources**:
  - MotherDuck (fundamental data)
  - yfinance (market data)
- **Caching**: In-memory caching (5-minute TTL)
- **Deployment**: Railway

### Database
- **MotherDuck**: Cloud-based DuckDB for fundamental metrics
- **Tables**:
  - `gurufocus_with_momentum`: Company fundamentals
  - `OBQ_Scores`: Quality scores
  - `NDR_BP_SP_history`: Risk indicators

## 📁 Project Structure

```
jcn-build/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── contexts/        # React contexts
│   │   ├── pages/           # Page components
│   │   ├── App.tsx          # Main app with routing
│   │   └── index.css        # Global styles
│   ├── public/              # Static assets
│   └── package.json
│
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── models/          # Data models
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utilities
│   │   └── data/            # Portfolio holdings
│   └── requirements.txt
│
└── pages/                    # Original Streamlit app (reference)
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ (frontend)
- Python 3.11+ (backend)
- MotherDuck token (for database access)

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
export MOTHERDUCK_TOKEN="your_token"
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Backend: `http://localhost:8080`

## 📊 API Endpoints

### Portfolios
- `GET /api/v1/portfolios/` - List all portfolios
- `GET /api/v1/portfolios/{portfolio_id}` - Get portfolio details

### Stocks
- `GET /api/v1/stocks/{symbol}` - Get stock information

## 🎨 Theme System

**Dark Mode:**
- Background: `#0a0a0a`
- Accent: `#3b82f6` (electric blue)

**Light Mode (Happy Hues Palette #6):**
- Background: `#fffffe`
- Accent: `#00ebc7` (turquoise)

## 🚢 Deployment

- **Frontend**: https://jcnfinancial.up.railway.app/
- **Backend**: https://jcn-dashboard-production.up.railway.app/

Railway auto-deploys from GitHub `master` branch.

## 📝 Data Flow

1. User Request → Frontend
2. API Call → Backend
3. Data Fetch → MotherDuck + yfinance
4. Processing → Calculate metrics
5. Caching → 5-minute TTL
6. Response → JSON to frontend
7. Visualization → ECharts renders

## 🎯 Future Enhancements

- Market Analysis page with indices and sectors
- Risk Management with BPSP analysis
- Portfolio editing and rebalancing
- Transaction history and tax lots

## 📄 License

Proprietary - JCN Financial & Tax Advisory Group, LLC

---

Built with React, FastAPI, and MotherDuck
