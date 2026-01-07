"""
Populate MotherDuck with 10 years of WEEKLY OHLC data for portfolio stocks.

This script:
1. Creates the StockDataYfinance4Streamlit table if it doesn't exist
2. Downloads 10 years of WEEKLY OHLC data from yfinance
3. Stores data in MotherDuck database

Usage:
    python populate_weekly_stock_data.py

Requirements:
    - MOTHERDUCK_TOKEN environment variable
    - Portfolio tickers list (modify TICKERS variable)
"""

import duckdb
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

# Configuration
MOTHERDUCK_TOKEN = os.getenv('MOTHERDUCK_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImJlbkBvYnNpZGlhbnF1YW50aXRhdGl2ZS5jb20iLCJtZFJlZ2lvbiI6ImF3cy11cy1lYXN0LTEiLCJzZXNzaW9uIjoiYmVuLm9ic2lkaWFucXVhbnRpdGF0aXZlLmNvbSIsInBhdCI6IkFUZ3ZBQVZoN3VpZVAtWGVDNnIxc0RVbXVyRzlsVG5TRkMyaTByQXFpb3ciLCJ1c2VySWQiOiJlZGZhZTYyMi0yMTBlLTRiYmItODU3Mi1kZjBjZTA2MjNkOWIiLCJpc3MiOiJtZF9wYXQiLCJyZWFkT25seSI6ZmFsc2UsInRva2VuVHlwZSI6InJlYWRfd3JpdGUiLCJpYXQiOjE3NjU5MTAwMzl9.c7_uLy07jXSP5NhczE818Zf-EhGCdyIFv1wJtfIoMUs')

# Portfolio tickers will be passed as command line argument or read from portfolio input
# Default tickers for standalone execution
DEFAULT_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B',
    'V', 'JNJ', 'WMT', 'JPM', 'MA', 'PG', 'UNH', 'HD', 'DIS', 'PYPL',
    'NFLX', 'ADBE', 'CRM'
]

def create_table(conn):
    """Create the StockDataYfinance4Streamlit table if it doesn't exist."""
    print("Creating table if not exists...")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS my_db.main.StockDataYfinance4Streamlit (
            symbol VARCHAR,
            date DATE,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            last_updated TIMESTAMP,
            PRIMARY KEY (symbol, date)
        )
    """)
    print("✅ Table created/verified")

def download_weekly_data(ticker, years=10):
    """
    Download WEEKLY OHLC data from yfinance.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    years : int
        Number of years of historical data to download
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with columns: Date, Open, High, Low, Close
    """
    try:
        print(f"  Downloading {ticker}...", end=" ")
        
        # Calculate start date
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years*365)
        
        # Download data with weekly interval
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date, interval='1wk')
        
        if data.empty:
            print(f"❌ No data")
            return None
        
        # Reset index to get Date as column
        data = data.reset_index()
        
        # Select only OHLC columns
        data = data[['Date', 'Open', 'High', 'Low', 'Close']].copy()
        
        # Add symbol column
        data['Symbol'] = ticker
        
        # Add last_updated timestamp
        data['Last_Updated'] = datetime.now()
        
        # Reorder columns
        data = data[['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Last_Updated']]
        
        # Convert column names to lowercase for MotherDuck
        data.columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'last_updated']
        
        # Convert date to date only (remove time)
        data['date'] = pd.to_datetime(data['date']).dt.date
        
        print(f"✅ {len(data)} weeks")
        return data
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def populate_data(conn, tickers, years=10):
    """
    Populate the table with weekly data for all tickers.
    
    Parameters:
    -----------
    conn : duckdb.DuckDBPyConnection
        MotherDuck connection
    tickers : list
        List of ticker symbols
    years : int
        Number of years of historical data
    """
    print(f"\nDownloading {years} years of WEEKLY data for {len(tickers)} stocks...")
    print("=" * 80)
    
    total_rows = 0
    successful = 0
    failed = 0
    
    for ticker in tickers:
        data = download_weekly_data(ticker, years)
        
        if data is not None and not data.empty:
            try:
                # Insert data into MotherDuck
                conn.execute("""
                    INSERT OR REPLACE INTO my_db.main.StockDataYfinance4Streamlit
                    SELECT * FROM data
                """)
                total_rows += len(data)
                successful += 1
            except Exception as e:
                print(f"  ❌ Error inserting {ticker}: {str(e)}")
                failed += 1
        else:
            failed += 1
    
    print("=" * 80)
    print(f"\n✅ Population complete!")
    print(f"   Successful: {successful}/{len(tickers)} stocks")
    print(f"   Failed: {failed}/{len(tickers)} stocks")
    print(f"   Total rows inserted: {total_rows:,}")

def verify_data(conn):
    """Verify the data was inserted correctly."""
    print("\nVerifying data...")
    
    # Count total rows
    result = conn.execute("""
        SELECT COUNT(*) as total_rows,
               COUNT(DISTINCT symbol) as unique_symbols,
               MIN(date) as earliest_date,
               MAX(date) as latest_date
        FROM my_db.main.StockDataYfinance4Streamlit
    """).df()
    
    print(f"  Total rows: {result['total_rows'].iloc[0]:,}")
    print(f"  Unique symbols: {result['unique_symbols'].iloc[0]}")
    print(f"  Date range: {result['earliest_date'].iloc[0]} to {result['latest_date'].iloc[0]}")
    
    # Show sample data
    sample = conn.execute("""
        SELECT * FROM my_db.main.StockDataYfinance4Streamlit
        ORDER BY symbol, date DESC
        LIMIT 5
    """).df()
    
    print("\nSample data (most recent):")
    print(sample.to_string(index=False))

def main(tickers=None):
    """Main execution function."""
    if tickers is None:
        tickers = DEFAULT_TICKERS
    
    print("=" * 80)
    print("WEEKLY STOCK DATA POPULATION SCRIPT")
    print("=" * 80)
    print(f"\nTarget: my_db.main.StockDataYfinance4Streamlit")
    print(f"Tickers: {len(tickers)} stocks")
    print(f"Period: 10 years of WEEKLY OHLC data")
    print(f"Data: Open, High, Low, Close (no volume)")
    
    # Connect to MotherDuck
    print("\nConnecting to MotherDuck...")
    conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
    print("✅ Connected")
    
    # Create table
    create_table(conn)
    
    # Populate data
    populate_data(conn, tickers, years=10)
    
    # Verify data
    verify_data(conn)
    
    # Close connection
    conn.close()
    print("\n✅ Script complete!")

if __name__ == "__main__":
    import sys
    
    # Check if tickers provided as command line arguments
    if len(sys.argv) > 1:
        tickers = sys.argv[1].split(',')
        tickers = [t.strip().upper() for t in tickers if t.strip()]
        main(tickers)
    else:
        main()
