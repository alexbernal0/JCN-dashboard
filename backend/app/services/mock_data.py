"""
Mock data for development and testing
"""

from datetime import datetime, timedelta
import random

def generate_mock_portfolio_data(portfolio_id: str, portfolio_name: str):
    """Generate mock portfolio data"""
    
    # Generate mock stocks
    stocks = []
    sectors = ["Technology", "Healthcare", "Finance", "Consumer", "Energy"]
    
    stock_symbols = {
        "persistent_value": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "JPM", "V", "WMT", "JNJ", "PG", "MA", "HD", "DIS"],
        "olivia_growth": ["NVDA", "TSLA", "AMD", "PLTR", "SNOW", "CRWD", "NET", "DDOG", "ZS", "OKTA", "PANW", "FTNT", "MDB", "TEAM", "ZM"]
    }
    
    symbols = stock_symbols.get(portfolio_id, stock_symbols["persistent_value"])
    
    for i, symbol in enumerate(symbols):
        price = random.uniform(50, 500)
        change = random.uniform(-10, 15)
        stocks.append({
            "symbol": symbol,
            "name": f"{symbol} Inc.",
            "price": round(price, 2),
            "change": round(change, 2),
            "changePercent": round((change / price) * 100, 2),
            "volume": random.randint(1000000, 50000000),
            "marketCap": random.randint(10000000000, 3000000000000),
            "sector": random.choice(sectors)
        })
    
    # Generate performance data (last 90 days)
    performance = []
    base_value = 100
    benchmark_value = 100
    
    for i in range(90):
        date = (datetime.now() - timedelta(days=90-i)).strftime("%Y-%m-%d")
        base_value *= (1 + random.uniform(-0.02, 0.025))
        benchmark_value *= (1 + random.uniform(-0.015, 0.02))
        
        performance.append({
            "date": date,
            "value": round(base_value, 2),
            "benchmark": round(benchmark_value, 2)
        })
    
    # Generate sector allocation
    sector_allocation = []
    total_value = sum(s["price"] for s in stocks)
    
    sector_values = {}
    for stock in stocks:
        sector = stock["sector"]
        if sector not in sector_values:
            sector_values[sector] = 0
        sector_values[sector] += stock["price"]
    
    for sector, value in sector_values.items():
        sector_allocation.append({
            "sector": sector,
            "value": round(value, 2),
            "percentage": round((value / total_value) * 100, 2)
        })
    
    # Calculate metrics
    current_value = performance[-1]["value"]
    ytd_return = current_value - 100
    
    return {
        "portfolio_id": portfolio_id,
        "name": portfolio_name,
        "description": f"{portfolio_name} - Mock data for development",
        "total_value": round(total_value, 2),
        "total_stocks": len(stocks),
        "ytd_return": round(ytd_return, 2),
        "annual_return": round(ytd_return * 1.2, 2),
        "sharpe_ratio": round(random.uniform(0.8, 2.5), 2),
        "max_drawdown": round(random.uniform(-15, -5), 2),
        "volatility": round(random.uniform(10, 25), 2),
        "beta": round(random.uniform(0.8, 1.3), 2),
        "quality_score": random.randint(60, 95),
        "value_score": random.randint(65, 90),
        "growth_score": random.randint(55, 85),
        "momentum_score": random.randint(50, 80),
        "stability_score": random.randint(70, 95),
        "stocks": stocks,
        "performance": performance,
        "sector_allocation": sector_allocation,
        "last_updated": datetime.now().isoformat()
    }


def generate_mock_stock_data(symbol: str):
    """Generate mock stock data"""
    
    price = random.uniform(50, 500)
    change = random.uniform(-10, 15)
    
    # Generate price history (candlestick data)
    price_history = []
    base_price = price * 0.9
    
    for i in range(60):  # 60 days
        date = (datetime.now() - timedelta(days=60-i)).strftime("%Y-%m-%d")
        
        open_price = base_price * (1 + random.uniform(-0.02, 0.02))
        close_price = open_price * (1 + random.uniform(-0.03, 0.03))
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
        
        price_history.append({
            "date": date,
            "open": round(open_price, 2),
            "close": round(close_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "volume": random.randint(1000000, 50000000)
        })
        
        base_price = close_price
    
    return {
        "symbol": symbol,
        "name": f"{symbol} Inc.",
        "current_price": round(price, 2),
        "change": round(change, 2),
        "change_percent": round((change / price) * 100, 2),
        "volume": random.randint(1000000, 50000000),
        "market_cap": random.randint(10000000000, 3000000000000),
        "pe_ratio": round(random.uniform(15, 45), 2),
        "pb_ratio": round(random.uniform(1.5, 8), 2),
        "eps": round(random.uniform(2, 25), 2),
        "dividend_yield": round(random.uniform(0, 4), 2),
        "week_52_high": round(price * random.uniform(1.1, 1.4), 2),
        "week_52_low": round(price * random.uniform(0.6, 0.9), 2),
        "ytd_return": round(random.uniform(-20, 40), 2),
        "beta": round(random.uniform(0.7, 1.5), 2),
        "sector": random.choice(["Technology", "Healthcare", "Finance", "Consumer", "Energy"]),
        "description": f"{symbol} is a leading company in its sector, providing innovative solutions and services to customers worldwide.",
        "price_history": price_history
    }
