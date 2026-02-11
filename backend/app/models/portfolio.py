"""
Pydantic models for portfolio data
"""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class StockData(BaseModel):
    """Individual stock data"""
    symbol: str
    name: str
    current_price: float
    change_percent: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None

class PortfolioPerformance(BaseModel):
    """Portfolio performance over time"""
    dates: List[str]
    portfolio_values: List[float]
    sp500_values: List[float]
    nasdaq_values: List[float]

class PortfolioAllocation(BaseModel):
    """Portfolio allocation by stock"""
    symbols: List[str]
    weights: List[float]
    values: List[float]

class PortfolioMetrics(BaseModel):
    """Portfolio aggregate metrics"""
    total_value: float
    total_return: float
    total_return_percent: float
    ytd_return: float
    ytd_return_percent: float
    sharpe_ratio: Optional[float] = None
    volatility: Optional[float] = None
    max_drawdown: Optional[float] = None
    avg_pe_ratio: Optional[float] = None
    avg_dividend_yield: Optional[float] = None

class PortfolioSummary(BaseModel):
    """Complete portfolio summary"""
    portfolio_id: str
    name: str
    description: str
    last_updated: datetime
    stocks: List[StockData]
    performance: PortfolioPerformance
    allocation: PortfolioAllocation
    metrics: PortfolioMetrics
