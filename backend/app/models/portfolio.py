"""
Pydantic models for portfolio data - matches original Streamlit app structure
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class StockHolding(BaseModel):
    """Individual stock holding with position data"""
    symbol: str
    company_name: str
    shares: float
    cost_basis: float
    current_price: float
    position_value: float
    total_cost: float
    gain_loss: float
    gain_loss_percent: float
    weight: float  # Portfolio weight percentage
    
    # Market data
    day_change: Optional[float] = None
    day_change_percent: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    # Fundamental metrics from MotherDuck
    fundamentals: Optional[Dict[str, Any]] = None

class PortfolioPerformance(BaseModel):
    """Portfolio performance over time"""
    dates: List[str]
    portfolio_values: List[float]
    sp500_values: List[float]  # Benchmark

class PortfolioAllocation(BaseModel):
    """Portfolio allocation breakdowns"""
    by_stock: Dict[str, float]  # symbol -> weight
    by_sector: Dict[str, float]  # sector -> weight
    by_industry: Dict[str, float]  # industry -> weight

class PortfolioMetrics(BaseModel):
    """Portfolio aggregate metrics"""
    total_value: float
    total_cost: float
    total_gain_loss: float
    total_gain_loss_percent: float
    cash: float
    num_holdings: int
    
    # Daily metrics
    day_change: float
    day_change_percent: float
    
    # Performance metrics
    ytd_return_percent: Optional[float] = None
    one_year_return_percent: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    volatility: Optional[float] = None
    max_drawdown: Optional[float] = None
    
    # Portfolio averages
    avg_pe_ratio: Optional[float] = None
    avg_dividend_yield: Optional[float] = None
    avg_beta: Optional[float] = None

class PortfolioSummary(BaseModel):
    """Complete portfolio summary"""
    portfolio_id: str
    name: str
    description: str
    last_updated: datetime
    holdings: List[StockHolding]
    performance: PortfolioPerformance
    allocation: PortfolioAllocation
    metrics: PortfolioMetrics
