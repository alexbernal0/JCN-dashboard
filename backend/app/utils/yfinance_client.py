"""
yfinance client for fetching stock data
"""

import yfinance as yf
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

class YFinanceClient:
    """Client for fetching stock data from Yahoo Finance"""
    
    @staticmethod
    def get_stock_info(symbol: str) -> Dict[str, Any]:
        """Get current stock information"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Use fast_info for current price (more reliable)
            try:
                current_price = ticker.fast_info.last_price
            except:
                # Fallback to history if fast_info fails
                hist = ticker.history(period="1d")
                current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            
            # Get previous close for change calculation
            try:
                hist = ticker.history(period="5d")
                if len(hist) >= 2:
                    prev_close = hist['Close'].iloc[-2]
                    change_percent = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
                else:
                    change_percent = 0
            except:
                change_percent = 0
            
            # Get info dict for other data (less reliable but needed for fundamentals)
            try:
                info = ticker.info
            except:
                info = {}
            
            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "current_price": float(current_price) if current_price else 0,
                "change_percent": float(change_percent) if change_percent else 0,
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "beta": info.get("beta"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
            }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return {
                "symbol": symbol,
                "name": symbol,
                "current_price": 0,
                "change_percent": 0,
                "market_cap": None,
                "pe_ratio": None,
                "dividend_yield": None,
                "beta": None,
                "sector": None,
                "industry": None,
            }
    
    @staticmethod
    def get_historical_data(symbols: List[str], period: str = "1y") -> pd.DataFrame:
        """Get historical price data for multiple symbols"""
        try:
            data = yf.download(symbols, period=period, group_by='ticker', progress=False)
            return data
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_portfolio_performance(symbols: List[str], period: str = "1y") -> Dict[str, Any]:
        """Calculate portfolio performance vs benchmarks"""
        try:
            # Fetch portfolio stocks + benchmarks
            all_symbols = symbols + ["SPY", "QQQ"]
            data = yf.download(all_symbols, period=period, group_by='ticker', progress=False)
            
            if data.empty:
                return {
                    "dates": [],
                    "portfolio_values": [],
                    "sp500_values": [],
                    "nasdaq_values": []
                }
            
            # Calculate equal-weighted portfolio
            portfolio_prices = []
            for symbol in symbols:
                try:
                    if len(symbols) == 1:
                        prices = data['Close']
                    else:
                        prices = data[symbol]['Close']
                    portfolio_prices.append(prices)
                except:
                    continue
            
            if not portfolio_prices:
                return {
                    "dates": [],
                    "portfolio_values": [],
                    "sp500_values": [],
                    "nasdaq_values": []
                }
            
            # Average portfolio performance
            portfolio_df = pd.concat(portfolio_prices, axis=1).mean(axis=1)
            portfolio_normalized = (portfolio_df / portfolio_df.iloc[0]) * 100
            
            # Benchmark performance
            if len(symbols) == 1:
                spy_prices = data['Close']
                qqq_prices = data['Close']
            else:
                spy_prices = data['SPY']['Close']
                qqq_prices = data['QQQ']['Close']
            
            spy_normalized = (spy_prices / spy_prices.iloc[0]) * 100
            qqq_normalized = (qqq_prices / qqq_prices.iloc[0]) * 100
            
            # Format dates
            dates = [d.strftime("%Y-%m-%d") for d in portfolio_df.index]
            
            return {
                "dates": dates,
                "portfolio_values": portfolio_normalized.tolist(),
                "sp500_values": spy_normalized.tolist(),
                "nasdaq_values": qqq_normalized.tolist()
            }
        
        except Exception as e:
            print(f"Error calculating portfolio performance: {e}")
            return {
                "dates": [],
                "portfolio_values": [],
                "sp500_values": [],
                "nasdaq_values": []
            }

# Global client instance
yfinance_client = YFinanceClient()
