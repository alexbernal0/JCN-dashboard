"""
Portfolio service - Business logic for portfolio operations with MotherDuck integration
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.models.portfolio import (
    PortfolioSummary,
    StockHolding,
    PortfolioPerformance,
    PortfolioAllocation,
    PortfolioMetrics
)
from app.data.portfolio_holdings import get_portfolio_holdings
from app.utils.yfinance_client import yfinance_client
from app.utils.motherduck_client import motherduck_client
from app.core.cache import cached
import yfinance as yf
import pandas as pd
from collections import defaultdict

class PortfolioService:
    """Service for portfolio operations"""
    
    def __init__(self):
        self.portfolios = {
            "persistent_value": {
                "name": "Persistent Value Portfolio",
                "description": "Value-focused investment strategy with long-term growth potential"
            },
            "olivia_growth": {
                "name": "Olivia Growth Portfolio",
                "description": "Growth-focused technology and innovation stocks"
            },
            "pure_alpha": {
                "name": "Pure Alpha Portfolio",
                "description": "Alpha-generating investment strategy"
            }
        }
    
    @cached(ttl=300, key_prefix="portfolio")
    async def get_portfolio_summary(self, portfolio_id: str) -> PortfolioSummary:
        """Get complete portfolio summary with real holdings and MotherDuck data"""
        if portfolio_id not in self.portfolios:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        portfolio_config = self.portfolios[portfolio_id]
        holdings_data = get_portfolio_holdings(portfolio_id)
        
        if not holdings_data:
            raise ValueError(f"No holdings data for portfolio {portfolio_id}")
        
        # Extract symbols
        symbols = [h['symbol'] for h in holdings_data]
        
        # Fetch current prices and market data from yfinance
        holdings = []
        total_value = 0
        total_cost = 0
        day_change_total = 0
        
        for holding_data in holdings_data:
            symbol = holding_data['symbol']
            shares = holding_data['shares']
            cost_basis = holding_data['cost_basis']
            
            # Get current stock info
            stock_info = yfinance_client.get_stock_info(symbol)
            current_price = stock_info.get('current_price', 0)
            
            # Calculate position metrics
            position_value = current_price * shares
            total_cost_for_position = cost_basis * shares
            gain_loss = position_value - total_cost_for_position
            gain_loss_percent = (gain_loss / total_cost_for_position * 100) if total_cost_for_position > 0 else 0
            
            # Day change
            day_change_percent = stock_info.get('change_percent', 0)
            day_change = position_value * (day_change_percent / 100)
            
            total_value += position_value
            total_cost += total_cost_for_position
            day_change_total += day_change
            
            holding = StockHolding(
                symbol=symbol,
                company_name=stock_info.get('name', symbol),
                shares=shares,
                cost_basis=cost_basis,
                current_price=current_price,
                position_value=position_value,
                total_cost=total_cost_for_position,
                gain_loss=gain_loss,
                gain_loss_percent=gain_loss_percent,
                weight=0,  # Will calculate after we have total_value
                day_change=day_change,
                day_change_percent=day_change_percent,
                market_cap=stock_info.get('market_cap'),
                pe_ratio=stock_info.get('pe_ratio'),
                dividend_yield=stock_info.get('dividend_yield'),
                beta=stock_info.get('beta'),
                sector=stock_info.get('sector'),
                industry=stock_info.get('industry'),
                fundamentals=None  # Will add from MotherDuck
            )
            holdings.append(holding)
        
        # Calculate weights
        for holding in holdings:
            holding.weight = (holding.position_value / total_value * 100) if total_value > 0 else 0
        
        # Fetch fundamentals from MotherDuck
        try:
            fundamentals_df = motherduck_client.get_fundamentals(symbols)
            if fundamentals_df is not None:
                # Add fundamentals to each holding
                for holding in holdings:
                    fund_row = fundamentals_df[fundamentals_df['Symbol'] == holding.symbol]
                    if not fund_row.empty:
                        # Convert row to dict and add to holding
                        holding.fundamentals = fund_row.iloc[0].to_dict()
        except Exception as e:
            print(f"Error fetching fundamentals from MotherDuck: {e}")
            # Continue without fundamentals
        
        # Get performance data (historical portfolio value)
        performance = await self._get_performance_data(holdings_data, symbols)
        
        # Calculate allocation breakdowns
        allocation = self._calculate_allocation(holdings)
        
        # Calculate aggregate metrics
        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
        day_change_percent = (day_change_total / total_value * 100) if total_value > 0 else 0
        
        # Calculate portfolio averages
        valid_pe = [h.pe_ratio for h in holdings if h.pe_ratio is not None and h.pe_ratio > 0]
        valid_div = [h.dividend_yield for h in holdings if h.dividend_yield is not None]
        valid_beta = [h.beta for h in holdings if h.beta is not None]
        
        metrics = PortfolioMetrics(
            total_value=total_value,
            total_cost=total_cost,
            total_gain_loss=total_gain_loss,
            total_gain_loss_percent=total_gain_loss_percent,
            cash=0,  # TODO: Add cash management
            num_holdings=len(holdings),
            day_change=day_change_total,
            day_change_percent=day_change_percent,
            ytd_return_percent=None,  # TODO: Calculate from performance data
            one_year_return_percent=None,  # TODO: Calculate from performance data
            sharpe_ratio=None,  # TODO: Calculate
            volatility=None,  # TODO: Calculate
            max_drawdown=None,  # TODO: Calculate
            avg_pe_ratio=sum(valid_pe) / len(valid_pe) if valid_pe else None,
            avg_dividend_yield=sum(valid_div) / len(valid_div) if valid_div else None,
            avg_beta=sum(valid_beta) / len(valid_beta) if valid_beta else None
        )
        
        return PortfolioSummary(
            portfolio_id=portfolio_id,
            name=portfolio_config["name"],
            description=portfolio_config["description"],
            last_updated=datetime.now(),
            holdings=holdings,
            performance=performance,
            allocation=allocation,
            metrics=metrics
        )
    
    async def _get_performance_data(self, holdings_data: List[Dict], symbols: List[str]) -> PortfolioPerformance:
        """Get historical performance data for portfolio"""
        try:
            # Get 1 year of historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Download historical data for all symbols
            data = yf.download(symbols, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                # Return empty performance data
                return PortfolioPerformance(
                    dates=[],
                    portfolio_values=[],
                    sp500_values=[]
                )
            
            # Get adjusted close prices
            if len(symbols) == 1:
                prices = data['Adj Close'].to_frame()
                prices.columns = [symbols[0]]
            else:
                prices = data['Adj Close']
            
            # Calculate portfolio value over time
            portfolio_values = []
            dates = []
            
            for date, row in prices.iterrows():
                portfolio_value = 0
                for holding in holdings_data:
                    symbol = holding['symbol']
                    shares = holding['shares']
                    if symbol in row and not pd.isna(row[symbol]):
                        portfolio_value += row[symbol] * shares
                
                if portfolio_value > 0:
                    portfolio_values.append(portfolio_value)
                    dates.append(date.strftime('%Y-%m-%d'))
            
            # Get S&P 500 benchmark data
            sp500_data = yf.download('^GSPC', start=start_date, end=end_date, progress=False)
            sp500_values = []
            
            if not sp500_data.empty:
                # Normalize to 100 at start
                sp500_prices = sp500_data['Adj Close']
                if len(sp500_prices) > 0:
                    start_value = sp500_prices.iloc[0]
                    sp500_values = [(price / start_value * 100) for price in sp500_prices]
            
            # Normalize portfolio values to match dates
            if len(sp500_values) > len(portfolio_values):
                sp500_values = sp500_values[:len(portfolio_values)]
            elif len(portfolio_values) > len(sp500_values):
                portfolio_values = portfolio_values[:len(sp500_values)]
                dates = dates[:len(sp500_values)]
            
            return PortfolioPerformance(
                dates=dates,
                portfolio_values=portfolio_values,
                sp500_values=sp500_values
            )
            
        except Exception as e:
            print(f"Error getting performance data: {e}")
            return PortfolioPerformance(
                dates=[],
                portfolio_values=[],
                sp500_values=[]
            )
    
    def _calculate_allocation(self, holdings: List[StockHolding]) -> PortfolioAllocation:
        """Calculate portfolio allocation breakdowns"""
        by_stock = {h.symbol: h.weight for h in holdings}
        
        # Group by sector
        by_sector = defaultdict(float)
        for h in holdings:
            if h.sector:
                by_sector[h.sector] += h.weight
        
        # Group by industry
        by_industry = defaultdict(float)
        for h in holdings:
            if h.industry:
                by_industry[h.industry] += h.weight
        
        return PortfolioAllocation(
            by_stock=by_stock,
            by_sector=dict(by_sector),
            by_industry=dict(by_industry)
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
