"""
Portfolio service - Business logic for portfolio operations
"""

from typing import List
from datetime import datetime
from app.models.portfolio import (
    PortfolioSummary,
    StockData,
    PortfolioPerformance,
    PortfolioAllocation,
    PortfolioMetrics
)
from app.utils.yfinance_client import yfinance_client
from app.core.config import settings
from app.core.cache import cached

class PortfolioService:
    """Service for portfolio operations"""
    
    def __init__(self):
        self.portfolios = {
            "persistent_value": {
                "name": "Persistent Value Portfolio",
                "description": "Value-focused investment strategy with long-term growth potential",
                "stocks": settings.PERSISTENT_VALUE_STOCKS
            },
            "olivia_growth": {
                "name": "Olivia Growth Portfolio",
                "description": "Growth-focused technology and innovation stocks",
                "stocks": settings.OLIVIA_GROWTH_STOCKS
            }
        }
    
    @cached(ttl=300, key_prefix="portfolio")
    async def get_portfolio_summary(self, portfolio_id: str) -> PortfolioSummary:
        """Get complete portfolio summary"""
        if portfolio_id not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        portfolio_config = self.portfolios[portfolio_id]
        symbols = portfolio_config["stocks"]
        
        # Fetch stock data
        stocks = []
        for symbol in symbols:
            stock_info = yfinance_client.get_stock_info(symbol)
            stocks.append(StockData(**stock_info))
        
        # Get performance data
        perf_data = yfinance_client.get_portfolio_performance(symbols)
        performance = PortfolioPerformance(**perf_data)
        
        # Calculate allocation (equal-weighted for now)
        total_value = sum(s.current_price for s in stocks if s.current_price > 0)
        weights = [s.current_price / total_value if total_value > 0 else 0 for s in stocks]
        values = [s.current_price for s in stocks]
        
        allocation = PortfolioAllocation(
            symbols=[s.symbol for s in stocks],
            weights=weights,
            values=values
        )
        
        # Calculate metrics
        portfolio_values = perf_data["portfolio_values"]
        if portfolio_values:
            total_return = portfolio_values[-1] - 100
            total_return_percent = total_return
            
            # Calculate YTD return (approximate)
            ytd_start_idx = max(0, len(portfolio_values) - 252)  # ~1 year of trading days
            ytd_return = portfolio_values[-1] - portfolio_values[ytd_start_idx]
            ytd_return_percent = ytd_return
        else:
            total_return = 0
            total_return_percent = 0
            ytd_return = 0
            ytd_return_percent = 0
        
        # Calculate average PE ratio and dividend yield
        valid_pe = [s.pe_ratio for s in stocks if s.pe_ratio is not None and s.pe_ratio > 0]
        valid_div = [s.dividend_yield for s in stocks if s.dividend_yield is not None]
        
        metrics = PortfolioMetrics(
            total_value=total_value,
            total_return=total_return,
            total_return_percent=total_return_percent,
            ytd_return=ytd_return,
            ytd_return_percent=ytd_return_percent,
            sharpe_ratio=None,  # TODO: Calculate
            volatility=None,  # TODO: Calculate
            max_drawdown=None,  # TODO: Calculate
            avg_pe_ratio=sum(valid_pe) / len(valid_pe) if valid_pe else None,
            avg_dividend_yield=sum(valid_div) / len(valid_div) if valid_div else None
        )
        
        return PortfolioSummary(
            portfolio_id=portfolio_id,
            name=portfolio_config["name"],
            description=portfolio_config["description"],
            last_updated=datetime.now(),
            stocks=stocks,
            performance=performance,
            allocation=allocation,
            metrics=metrics
        )
    
    async def get_portfolio_list(self) -> List[dict]:
        """Get list of available portfolios"""
        return [
            {
                "id": pid,
                "name": config["name"],
                "description": config["description"]
            }
            for pid, config in self.portfolios.items()
        ]

# Global service instance
portfolio_service = PortfolioService()
