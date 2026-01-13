"""
Generate initial CSV snapshots for both portfolios.
This creates fallback cache files that will be committed to GitHub.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import time

# Persistent Value Portfolio
persistent_tickers = {
    'SPMO': {'cost_basis': 97.40, 'shares': 14301},
    'ASML': {'cost_basis': 660.32, 'shares': 1042},
    'MNST': {'cost_basis': 50.01, 'shares': 8234},
    'MSCI': {'cost_basis': 342.94, 'shares': 2016},
    'COST': {'cost_basis': 655.21, 'shares': 798},
    'AVGO': {'cost_basis': 138.00, 'shares': 6088},
    'MA': {'cost_basis': 418.76, 'shares': 1389},
    'FICO': {'cost_basis': 1850.00, 'shares': 778},
    'SPGI': {'cost_basis': 427.93, 'shares': 1554},
    'IDXX': {'cost_basis': 378.01, 'shares': 1570},
    'ISRG': {'cost_basis': 322.50, 'shares': 2769},
    'V': {'cost_basis': 276.65, 'shares': 2338},
    'CAT': {'cost_basis': 287.70, 'shares': 1356},
    'ORLY': {'cost_basis': 103.00, 'shares': 3566},
    'HEI': {'cost_basis': 172.00, 'shares': 1804},
    'CPRT': {'cost_basis': 52.00, 'shares': 21136},
    'WM': {'cost_basis': 177.77, 'shares': 3082},
    'TSLA': {'cost_basis': 270.00, 'shares': 5022},
    'AAPL': {'cost_basis': 181.40, 'shares': 2865},
    'LRCX': {'cost_basis': 73.24, 'shares': 18667},
    'TSM': {'cost_basis': 99.61, 'shares': 5850}
}

# Olivia Growth Portfolio
olivia_tickers = {
    'QGRW': {'cost_basis': 50.50, 'shares': 52098},
    'GOOG': {'cost_basis': 137.21, 'shares': 13082},
    'AMZN': {'cost_basis': 145.09, 'shares': 13427},
    'MELI': {'cost_basis': 1545.00, 'shares': 1486},
    'SPOT': {'cost_basis': 705.00, 'shares': 1740},
    'VEEV': {'cost_basis': 186.46, 'shares': 3286},
    'AMD': {'cost_basis': 214.00, 'shares': 3870},
    'MSFT': {'cost_basis': 369.07, 'shares': 2164},
    'CRWD': {'cost_basis': 248.42, 'shares': 4380},
    'FTNT': {'cost_basis': 58.48, 'shares': 18172},
    'META': {'cost_basis': 589.00, 'shares': 2264},
    'NVDA': {'cost_basis': 50.00, 'shares': 12295},
    'GEV': {'cost_basis': 660.00, 'shares': 1704},
    'PWR': {'cost_basis': 430.00, 'shares': 2581},
    'SHOP': {'cost_basis': 74.18, 'shares': 14351},
    'CDNS': {'cost_basis': 254.50, 'shares': 3476},
    'ANET': {'cost_basis': 57.62, 'shares': 15522},
    'NFLX': {'cost_basis': 118.00, 'shares': 17010},
    'CRCL': {'cost_basis': 84.01, 'shares': 15056},
    'AXON': {'cost_basis': 520.00, 'shares': 2598},
    'PLTR': {'cost_basis': 39.00, 'shares': 4298}
}

def get_stock_data(ticker):
    """Get comprehensive stock data from yfinance"""
    try:
        time.sleep(0.5)  # Rate limiting
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get company info
        security_name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        
        # Get recent price data
        recent_data = stock.history(period="5d", interval="1d")
        
        if len(recent_data) >= 2:
            current_price = recent_data['Close'].iloc[-1]
            previous_close = recent_data['Close'].iloc[-2]
            daily_change_pct = ((current_price - previous_close) / previous_close) * 100
        else:
            current_price = recent_data['Close'].iloc[-1] if len(recent_data) > 0 else None
            daily_change_pct = 0.0
        
        # Get YTD data
        current_year = datetime.now().year
        start_date = f"{current_year}-01-01"
        ytd_data = stock.history(start=start_date)
        
        if len(ytd_data) > 0:
            year_start_price = ytd_data['Close'].iloc[0]
            if current_price and year_start_price:
                ytd_pct_change = ((current_price - year_start_price) / year_start_price) * 100
            else:
                ytd_pct_change = 0.0
        else:
            ytd_pct_change = 0.0
        
        # Get 52-week data
        year_data = stock.history(period="1y", interval="1d")
        
        if len(year_data) > 0:
            week_52_high = year_data['High'].max()
            week_52_low = year_data['Low'].min()
            one_year_ago_price = year_data['Close'].iloc[0]
            
            if current_price and one_year_ago_price:
                yoy_pct_change = ((current_price - one_year_ago_price) / one_year_ago_price) * 100
            else:
                yoy_pct_change = 0.0
            
            if current_price and week_52_high:
                pct_below_52wk_high = ((week_52_high - current_price) / week_52_high) * 100
            else:
                pct_below_52wk_high = 0.0
            
            if current_price and week_52_high and week_52_low and week_52_high != week_52_low:
                chan_range_pct = ((current_price - week_52_low) / (week_52_high - week_52_low)) * 100
            else:
                chan_range_pct = 0.0
        else:
            yoy_pct_change = 0.0
            pct_below_52wk_high = 0.0
            chan_range_pct = 0.0
            week_52_high = 0
            week_52_low = 0
        
        return {
            'security_name': security_name,
            'current_price': current_price,
            'daily_change_pct': daily_change_pct,
            'ytd_pct_change': ytd_pct_change,
            'yoy_pct_change': yoy_pct_change,
            'pct_below_52wk_high': pct_below_52wk_high,
            'chan_range_pct': chan_range_pct,
            'week_52_high': week_52_high,
            'week_52_low': week_52_low,
            'sector': sector,
            'industry': industry
        }
    except Exception as e:
        print(f"  ❌ Error fetching {ticker}: {str(e)}")
        return None

def generate_snapshot(tickers_dict, portfolio_name):
    """Generate CSV snapshot for a portfolio"""
    print(f"\n{'='*80}")
    print(f"Generating {portfolio_name} snapshot...")
    print(f"{'='*80}\n")
    
    portfolio_data = []
    
    for ticker, info in tickers_dict.items():
        print(f"  Fetching {ticker}...", end=" ")
        stock_data = get_stock_data(ticker)
        
        if stock_data:
            cost_basis = info['cost_basis']
            shares = info['shares']
            current_price = stock_data['current_price']
            
            if current_price:
                position_value = current_price * shares
                port_gain_pct = ((current_price - cost_basis) / cost_basis) * 100
            else:
                position_value = 0
                port_gain_pct = 0.0
            
            portfolio_data.append({
                'Security': stock_data['security_name'],
                'Ticker': ticker,
                'Cost Basis': cost_basis,
                'Shares': int(shares),
                'Cur Price': current_price if current_price else 0,
                'Position_Value': position_value,
                'Daily_Change_Pct': stock_data['daily_change_pct'],
                'YTD_Pct': stock_data['ytd_pct_change'],
                'YoY_Pct': stock_data['yoy_pct_change'],
                'Port_Gain_Pct': port_gain_pct,
                'Pct_Below_52wk': stock_data['pct_below_52wk_high'],
                'Chan_Range': stock_data['chan_range_pct'],
                'Week_52_High': stock_data['week_52_high'],
                'Week_52_Low': stock_data['week_52_low'],
                'Sector': stock_data['sector'],
                'Industry': stock_data['industry']
            })
            print("✅")
        else:
            print("❌")
    
    # Save to CSV
    if portfolio_data:
        df = pd.DataFrame(portfolio_data)
        csv_path = f"cache_snapshots/{portfolio_name}_snapshot.csv"
        df.to_csv(csv_path, index=False)
        
        # Save timestamp
        timestamp_path = f"cache_snapshots/{portfolio_name}_timestamp.txt"
        with open(timestamp_path, 'w') as f:
            f.write(datetime.now().isoformat())
        
        print(f"\n✅ Snapshot saved: {csv_path}")
        print(f"   Stocks: {len(portfolio_data)}/{len(tickers_dict)}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    else:
        print(f"\n❌ No data to save for {portfolio_name}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PORTFOLIO SNAPSHOT GENERATOR")
    print("="*80)
    
    # Generate Persistent Value snapshot
    generate_snapshot(persistent_tickers, "persistent_value")
    
    # Generate Olivia Growth snapshot
    generate_snapshot(olivia_tickers, "olivia_growth")
    
    print("\n" + "="*80)
    print("✅ All snapshots generated!")
    print("="*80 + "\n")
