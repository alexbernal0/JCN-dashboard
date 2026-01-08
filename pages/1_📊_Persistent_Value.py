import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
from PIL import Image
import time
import json
import os
import finnhub
import requests
import duckdb
import math
from scipy import stats
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Page configuration
st.set_page_config(
    page_title="Persistent Value - JCN Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for white theme and black table headers
st.markdown("""
    <style>
    .main {
        background-color: white;
    }
    .stApp {
        background-color: white;
    }
    /* Make dataframe headers black and bold */
    .stDataFrame thead tr th {
        background-color: white !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 14px !important;
    }
    /* Ensure table text is readable */
    .stDataFrame tbody tr td {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Cache file paths
CACHE_FILE = "portfolio_cache.json"
NEWS_CACHE_FILE = "news_cache.json"
SUMMARY_CACHE_FILE = "portfolio_summary_cache.json"

# API Keys for news aggregation (using Streamlit secrets)
# Configure these in Streamlit Cloud: Settings > Secrets
try:
    FINNHUB_API_KEY = st.secrets["FINNHUB_API_KEY"]
    GROK_API_KEY = st.secrets["GROK_API_KEY"]
except Exception as e:
    st.error("⚠️ API keys not configured. Please add FINNHUB_API_KEY and GROK_API_KEY to Streamlit secrets.")
    FINNHUB_API_KEY = None
    GROK_API_KEY = None

# Helper functions for caching
def save_to_cache(data, timestamp):
    """Save portfolio data to cache file"""
    try:
        cache_data = {
            'timestamp': timestamp.isoformat(),
            'data': data
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        st.warning(f"Could not save cache: {str(e)}")

def load_from_cache():
    """Load portfolio data from cache file"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            return cache_data['data'], datetime.fromisoformat(cache_data['timestamp'])
        return None, None
    except Exception as e:
        st.warning(f"Could not load cache: {str(e)}")
        return None, None

# Header with logo and title
col1, col2, col3 = st.columns([1, 4, 2])
with col1:
    try:
        logo = Image.open("jcn_logo.jpg")
        st.image(logo, width=150)
    except:
        st.write("")

with col2:
    st.title("📊 Persistent Value Portfolio")
    st.markdown("Value-focused investment strategy with long-term growth potential")

with col3:
    st.write("")  # Spacer
    # Refresh button - forces fresh data fetch
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.session_state.force_refresh = True
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    # Display last refresh time and source
    if 'last_refresh' not in st.session_state:
        # Try to load from cache first
        cached_data, cached_time = load_from_cache()
        if cached_time:
            st.session_state.last_refresh = cached_time
        else:
            st.session_state.last_refresh = datetime.now()
    
    refresh_time = st.session_state.last_refresh.strftime("%I:%M:%S %p")
    st.caption(f"**Last Updated:** {refresh_time}")
    st.caption("**Source:** Yahoo Finance (Cached)")

st.markdown("---")

# Initialize force refresh flag
if 'force_refresh' not in st.session_state:
    st.session_state.force_refresh = False

# Initialize session state for portfolio data with default stocks
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = pd.DataFrame({
        'Symbol': ['SPMO', 'ASML', 'MNST', 'MSCI', 'COST', 'AVGO', 'MA', 'FICO', 'SPGI', 'IDXX', 
                   'ISRG', 'V', 'CAT', 'ORLY', 'HEI', 'CPRT', 'WM', 'TSLA', 'AAPL', 'LRCX', 'TSM'],
        'Cost Basis': [97.40, 660.32, 50.01, 342.94, 655.21, 138.00, 418.76, 1850.00, 427.93, 378.01,
                       322.50, 276.65, 287.70, 103.00, 172.00, 52.00, 177.77, 270.00, 181.40, 73.24, 99.61],
        'Shares': [14301, 1042, 8234, 2016, 798, 6088, 1389, 778, 1554, 1570,
                   2769, 2338, 1356, 3566, 1804, 21136, 3082, 5022, 2865, 18667, 5850]
    })

# Initialize edit mode state
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

# Initialize time period state
if 'selected_period' not in st.session_state:
    st.session_state.selected_period = "6 Months"

# Extract valid tickers from current portfolio data
tickers = [ticker.strip().upper() for ticker in st.session_state.portfolio_data['Symbol'].dropna().tolist() if ticker.strip()]

# Helper function to get comprehensive stock data with rate limiting
def get_comprehensive_stock_data(ticker):
    """Get all required stock data from yfinance with rate limiting"""
    try:
        # Add delay to avoid rate limiting (0.5 seconds between requests)
        time.sleep(0.5)
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get company info
        security_name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        
        # Get recent price data for current price and daily change
        recent_data = stock.history(period="5d", interval="1d")
        
        if len(recent_data) >= 2:
            current_price = recent_data['Close'].iloc[-1]
            previous_close = recent_data['Close'].iloc[-2]
            daily_change_pct = ((current_price - previous_close) / previous_close) * 100
        else:
            current_price = recent_data['Close'].iloc[-1] if len(recent_data) > 0 else None
            daily_change_pct = 0.0
        
        # Get year-to-date data
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
        
        # Get 52-week high/low and year-over-year data
        year_data = stock.history(period="1y", interval="1d")
        
        if len(year_data) > 0:
            week_52_high = year_data['High'].max()
            week_52_low = year_data['Low'].min()
            one_year_ago_price = year_data['Close'].iloc[0]
            
            # Calculate YoY % change
            if current_price and one_year_ago_price:
                yoy_pct_change = ((current_price - one_year_ago_price) / one_year_ago_price) * 100
            else:
                yoy_pct_change = 0.0
            
            # Calculate % Below 52wk High
            if current_price and week_52_high:
                pct_below_52wk_high = ((week_52_high - current_price) / week_52_high) * 100
            else:
                pct_below_52wk_high = 0.0
            
            # Calculate 52wk Chan Range (position within range)
            if current_price and week_52_high and week_52_low and week_52_high != week_52_low:
                chan_range_pct = ((current_price - week_52_low) / (week_52_high - week_52_low)) * 100
            else:
                chan_range_pct = 0.0
        else:
            yoy_pct_change = 0.0
            pct_below_52wk_high = 0.0
            chan_range_pct = 0.0
        
        return {
            'security_name': security_name,
            'current_price': current_price,
            'daily_change_pct': daily_change_pct,
            'ytd_pct_change': ytd_pct_change,
            'yoy_pct_change': yoy_pct_change,
            'pct_below_52wk_high': pct_below_52wk_high,
            'chan_range_pct': chan_range_pct,
            'week_52_high': week_52_high if len(year_data) > 0 else 0,
            'week_52_low': week_52_low if len(year_data) > 0 else 0,
            'sector': sector,
            'industry': industry
        }
    except Exception as e:
        # Silent error handling - return None to indicate failure
        return None

# ============================================================================
# BENCHMARK CALCULATION FUNCTIONS
# ============================================================================

# SPY cache file
SPY_CACHE_FILE = "spy_cache.json"

def save_spy_to_cache(spy_data, timestamp):
    """Save SPY data to cache file"""
    try:
        cache_data = {
            'spy_daily_change': spy_data,
            'timestamp': timestamp.isoformat()
        }
        with open(SPY_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        pass

def load_spy_from_cache():
    """Load SPY data from cache file"""
    try:
        if os.path.exists(SPY_CACHE_FILE):
            with open(SPY_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            return cache_data['spy_daily_change'], datetime.fromisoformat(cache_data['timestamp'])
        return None, None
    except Exception as e:
        return None, None

def get_spy_daily_change(should_fetch_fresh, cached_time):
    """
    Get SPY's daily percentage change with caching.
    
    Parameters:
    -----------
    should_fetch_fresh : bool
        Whether to fetch fresh data or use cache
    cached_time : datetime
        Timestamp of cached data
    
    Returns:
    --------
    float
        SPY daily percentage change
    """
    # Try to load from cache first
    cached_spy, spy_cache_time = load_spy_from_cache()
    
    # If we should fetch fresh or cache doesn't exist
    if should_fetch_fresh or cached_spy is None:
        try:
            spy = yf.Ticker('SPY')
            data = spy.history(period="5d", interval="1d")
            
            if data is not None and len(data) >= 2:
                current_price = data['Close'].iloc[-1]
                previous_price = data['Close'].iloc[-2]
                daily_change = ((current_price - previous_price) / previous_price) * 100
                
                # Save to cache
                save_spy_to_cache(daily_change, datetime.now())
                return daily_change
            return cached_spy if cached_spy is not None else 0.0
        except Exception as e:
            return cached_spy if cached_spy is not None else 0.0
    else:
        # Return cached value
        return cached_spy if cached_spy is not None else 0.0

def calculate_portfolio_daily_change(portfolio_df):
    """
    Calculate portfolio's weighted daily percentage change.
    
    Parameters:
    -----------
    portfolio_df : pd.DataFrame
        Portfolio DataFrame with '% Port.' and 'Daily % Change' columns
    
    Returns:
    --------
    float
        Portfolio weighted daily percentage change
    """
    try:
        # Get the relevant columns
        port_pct_col = '% Port.'
        daily_change_col = 'Daily % Change'
        
        if port_pct_col not in portfolio_df.columns or daily_change_col not in portfolio_df.columns:
            return 0.0
        
        # Calculate weighted average
        # Weight = portfolio percentage / 100
        # Weighted change = sum(weight * daily_change)
        weights = portfolio_df[port_pct_col] / 100
        daily_changes = portfolio_df[daily_change_col]
        
        weighted_daily_change = (weights * daily_changes).sum()
        
        return weighted_daily_change
    except Exception as e:
        return 0.0

# ============================================================================
# PORTFOLIO ALLOCATION FUNCTIONS
# ============================================================================

def get_category_style(ticker):
    """
    Get category style (e.g., Large Growth, Mid Value) from yfinance.
    
    Parameters:
    -----------
    ticker : str
        Stock ticker symbol
    
    Returns:
    --------
    str
        Category style (e.g., 'Large Growth', 'Mid Value', 'Small Blend')
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Try to get category directly from yfinance first
        category = info.get('category', None)
        if category:
            return category
        
        fund_category = info.get('fundCategory', None)
        if fund_category:
            return fund_category
            
        style_box = info.get('styleBox', None)
        if style_box:
            return style_box
        
        # Fallback: construct from market cap and style metrics
        market_cap = info.get('marketCap', 0)
        
        # Determine size category
        if market_cap >= 10_000_000_000:  # $10B+
            size = 'Large'
        elif market_cap >= 2_000_000_000:  # $2B - $10B
            size = 'Mid'
        else:
            size = 'Small'
        
        # Try to determine growth/value from PE ratio and other metrics
        pe_ratio = info.get('trailingPE', None)
        pb_ratio = info.get('priceToBook', None)
        
        # Simple heuristic for growth vs value
        if pe_ratio is not None and pb_ratio is not None:
            if pe_ratio > 25 or pb_ratio > 3:
                style = 'Growth'
            elif pe_ratio < 15 and pb_ratio < 2:
                style = 'Value'
            else:
                style = 'Blend'
        else:
            style = 'Blend'
        
        return f"{size} {style}"
        
    except Exception as e:
        return 'Unknown'

def prepare_company_data(portfolio_df):
    """Prepare data for company allocation pie chart."""
    company_data = []
    for idx, row in portfolio_df.iterrows():
        security = row.get('Security', 'Unknown')
        ticker = row.get('Ticker', '')
        port_pct = row.get('Port_Pct', 0)
        
        company_data.append({
            'Company': security,
            'Ticker': ticker,
            'Percentage': port_pct
        })
    
    return pd.DataFrame(company_data)

def prepare_category_data(portfolio_df):
    """Prepare data for category style allocation pie chart."""
    category_data = {}
    
    for idx, row in portfolio_df.iterrows():
        ticker = row.get('Ticker', '')
        security = row.get('Security', ticker)
        port_pct = row.get('Port_Pct', 0)
        
        # Get category style
        category = get_category_style(ticker)
        
        if category not in category_data:
            category_data[category] = {
                'percentage': 0,
                'companies': []
            }
        
        category_data[category]['percentage'] += port_pct
        category_data[category]['companies'].append(security)
    
    # Convert to DataFrame
    df_data = []
    for category, data in category_data.items():
        df_data.append({
            'Category': category,
            'Percentage': data['percentage'],
            'Companies': ', '.join(data['companies'])
        })
    
    return pd.DataFrame(df_data)

def prepare_sector_data(portfolio_df):
    """Prepare data for sector allocation pie chart."""
    sector_data = {}
    
    for idx, row in portfolio_df.iterrows():
        sector = row.get('Sector', 'Unknown')
        
        # Skip N/A sectors
        if sector == 'N/A' or sector == 'Unknown':
            continue
        
        port_pct = row.get('Port_Pct', 0)
        
        if sector not in sector_data:
            sector_data[sector] = 0
        
        sector_data[sector] += port_pct
    
    # Convert to DataFrame
    df_data = [{'Sector': k, 'Percentage': v} for k, v in sector_data.items()]
    return pd.DataFrame(df_data)

def prepare_industry_data(portfolio_df):
    """Prepare data for industry allocation pie chart."""
    industry_data = {}
    
    for idx, row in portfolio_df.iterrows():
        industry = row.get('Industry', 'Unknown')
        
        # Skip N/A industries
        if industry == 'N/A' or industry == 'Unknown':
            continue
        
        port_pct = row.get('Port_Pct', 0)
        
        if industry not in industry_data:
            industry_data[industry] = 0
        
        industry_data[industry] += port_pct
    
    # Convert to DataFrame
    df_data = [{'Industry': k, 'Percentage': v} for k, v in industry_data.items()]
    return pd.DataFrame(df_data)

def create_portfolio_pie_charts(portfolio_df):
    """
    Create 2x2 grid of pie charts for portfolio allocation analysis.
    
    Parameters:
    -----------
    portfolio_df : pd.DataFrame
        Portfolio DataFrame (before formatting)
    
    Returns:
    --------
    plotly.graph_objects.Figure
        2x2 grid of pie charts
    """
    # Prepare data for each chart
    company_df = prepare_company_data(portfolio_df)
    category_df = prepare_category_data(portfolio_df)
    sector_df = prepare_sector_data(portfolio_df)
    industry_df = prepare_industry_data(portfolio_df)
    
    # Create subplots: 2 rows, 2 columns
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{'type': 'pie'}, {'type': 'pie'}],
               [{'type': 'pie'}, {'type': 'pie'}]],
        subplot_titles=('Company Allocation', 'Category Style Allocation',
                       'Sector Allocation', 'Industry Allocation')
    )
    
    # Subtle color palette (muted/pastel colors)
    colors = [
        '#B8D4E3', '#D4E3B8', '#E3D4B8', '#E3B8D4',
        '#B8E3D4', '#D4B8E3', '#E3B8B8', '#B8E3B8',
        '#C8D8E8', '#E8D8C8', '#D8C8E8', '#C8E8D8',
        '#E8C8D8', '#D8E8C8', '#C8C8E8', '#E8E8C8',
        '#A8C8D8', '#D8C8A8', '#C8A8D8', '#A8D8C8'
    ]
    
    # Chart 1: Company Allocation (Top Left)
    fig.add_trace(
        go.Pie(
            labels=company_df['Ticker'],
            values=company_df['Percentage'],
            text=company_df['Ticker'],
            textposition='inside',
            textinfo='text',
            textfont=dict(size=10, color='black'),
            hovertemplate='<b>%{customdata}</b><br>%{percent}<extra></extra>',
            customdata=company_df['Company'],
            marker=dict(colors=colors),
            name='Company'
        ),
        row=1, col=1
    )
    
    # Chart 2: Category Style Allocation (Top Right)
    fig.add_trace(
        go.Pie(
            labels=category_df['Category'],
            values=category_df['Percentage'],
            textposition='inside',
            textinfo='label+percent',
            textfont=dict(size=10),
            hovertemplate='<b>%{label}</b><br>%{percent}<br>Companies: %{customdata}<extra></extra>',
            customdata=category_df['Companies'],
            marker=dict(colors=colors),
            name='Category'
        ),
        row=1, col=2
    )
    
    # Chart 3: Sector Allocation (Bottom Left)
    fig.add_trace(
        go.Pie(
            labels=sector_df['Sector'],
            values=sector_df['Percentage'],
            textposition='inside',
            textinfo='label',
            textfont=dict(size=10),
            hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>',
            marker=dict(colors=colors),
            name='Sector'
        ),
        row=2, col=1
    )
    
    # Chart 4: Industry Allocation (Bottom Right)
    fig.add_trace(
        go.Pie(
            labels=industry_df['Industry'],
            values=industry_df['Percentage'],
            textposition='inside',
            textinfo='label',
            textfont=dict(size=9),
            hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>',
            marker=dict(colors=colors),
            name='Industry'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        showlegend=False,
        height=700,
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    return fig

# ============================================================================
# MOTHERDUCK FUNDAMENTALS FUNCTIONS
# ============================================================================

def get_portfolio_aggregated_metrics(fundamentals_df):
    """
    Calculate Max, Median, Average, and Min for all fundamental metrics.
    
    Args:
        fundamentals_df: DataFrame from get_fundamentals_from_motherduck
        
    Returns:
        DataFrame with rows = Max/Median/Avg/Min, columns = metrics
    """
    try:
        if fundamentals_df is None or fundamentals_df.empty:
            return None
        
        # Get all numeric columns (exclude Ticker, Company, and GF_Valuation)
        exclude_cols = ['Ticker', 'Company', 'GF Valuation']
        numeric_columns = [col for col in fundamentals_df.columns if col not in exclude_cols]
        
        # Calculate statistics for each column
        composite_data = []
        
        for col in numeric_columns:
            # Get non-null values (exclude 'N/A' strings)
            values = fundamentals_df[col].copy()
            
            # Convert to numeric, coercing 'N/A' to NaN
            values = pd.to_numeric(values, errors='coerce')
            values = values.dropna()
            
            if len(values) > 0:
                composite_data.append({
                    'Metric': col,
                    'Max': values.max(),
                    'Median': values.median(),
                    'Average': values.mean(),
                    'Min': values.min()
                })
        
        # Create composite DataFrame
        composite = pd.DataFrame(composite_data)
        
        # Round all numeric columns to 1 decimal place
        composite['Max'] = composite['Max'].round(1)
        composite['Median'] = composite['Median'].round(1)
        composite['Average'] = composite['Average'].round(1)
        composite['Min'] = composite['Min'].round(1)
        
        # Transpose: Rows = Max/Median/Avg/Min, Columns = Metrics
        composite = composite.set_index('Metric').T
        
        return composite
        
    except Exception as e:
        st.error(f"Error calculating aggregated metrics: {str(e)}")
        return None

def get_fundamentals_from_motherduck(tickers, portfolio_df):
    """
    Fetch fundamental metrics from MotherDuck database for portfolio stocks.
    Uses SELECT * and accesses columns directly in pandas to avoid SQL escaping issues.
    
    Parameters:
    -----------
    tickers : list
        List of ticker symbols
    portfolio_df : pd.DataFrame
        Portfolio DataFrame with Security (company name) column
    
    Returns:
    --------
    pd.DataFrame
        Fundamentals scorecard with all metrics (NaN filled with appropriate defaults)
    """
    try:
        # Get MotherDuck token from environment
        motherduck_token = os.getenv('MOTHERDUCK_TOKEN')
        if not motherduck_token:
            st.warning("MotherDuck token not configured. Fundamentals table unavailable.")
            return None
        
        # Filter out empty tickers and prepare for SQL
        valid_tickers = [t.strip().upper() for t in tickers if t and t.strip()]
        if not valid_tickers:
            return None
        
        symbols_str = "', '".join(valid_tickers)
        
        # Connect to MotherDuck
        conn = duckdb.connect(f'md:?motherduck_token={motherduck_token}')
        
        # Get all data with SELECT * and join with latest OBQ scores
        query = f"""
        WITH latest_obq AS (
            SELECT *
            FROM my_db.main.OBQ_Scores
            QUALIFY ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY calculation_date DESC) = 1
        )
        SELECT 
            gf.*,
            obq.obq_growth_score,
            obq.OBQ_Quality_Rank,
            obq.obq_momentum_score,
            obq.obq_finstr_score,
            obq.obq_value_score,
            -- Compute OBQ GM (always available)
            CASE 
                WHEN obq.obq_growth_score IS NOT NULL AND obq.obq_momentum_score IS NOT NULL
                THEN (obq.obq_growth_score + obq.obq_momentum_score) / 2.0
                ELSE NULL
            END as computed_obq_gm,
            -- Compute OBQ GQM (always available)
            CASE 
                WHEN obq.obq_growth_score IS NOT NULL AND obq.OBQ_Quality_Rank IS NOT NULL AND obq.obq_momentum_score IS NOT NULL
                THEN (obq.obq_growth_score + obq.OBQ_Quality_Rank + obq.obq_momentum_score) / 3.0
                ELSE NULL
            END as computed_obq_gqm,
            -- Compute OBQ GQV (only if value score exists)
            CASE 
                WHEN obq.obq_value_score IS NOT NULL AND obq.obq_growth_score IS NOT NULL AND obq.OBQ_Quality_Rank IS NOT NULL
                THEN (obq.obq_growth_score + obq.OBQ_Quality_Rank + obq.obq_value_score) / 3.0
                ELSE NULL
            END as computed_obq_gqv,
            -- Compute OBQ VQF (only if value score exists)
            CASE 
                WHEN obq.obq_value_score IS NOT NULL AND obq.OBQ_Quality_Rank IS NOT NULL AND obq.obq_finstr_score IS NOT NULL
                THEN (obq.obq_value_score + obq.OBQ_Quality_Rank + obq.obq_finstr_score) / 3.0
                ELSE NULL
            END as computed_obq_vqf,
            -- Compute OBQ Composite (only if value score exists)
            CASE 
                WHEN obq.obq_value_score IS NOT NULL AND obq.obq_growth_score IS NOT NULL AND obq.obq_momentum_score IS NOT NULL AND obq.OBQ_Quality_Rank IS NOT NULL AND obq.obq_finstr_score IS NOT NULL
                THEN (obq.obq_growth_score + obq.obq_momentum_score + obq.OBQ_Quality_Rank + (0.5 * obq.obq_value_score) + (0.5 * obq.obq_finstr_score)) / 5.0
                ELSE NULL
            END as computed_obq_composite
        FROM my_db.main.gurufocus_with_momentum gf
        LEFT JOIN latest_obq obq ON gf.Symbol = obq.symbol
        WHERE gf.Symbol IN ('{symbols_str}')
        ORDER BY gf.Symbol
        """
        
        # Execute query
        result = conn.execute(query).df()
        conn.close()
        
        if result.empty:
            st.warning("No data found in MotherDuck for portfolio stocks.")
            return None
        
        # Build final scorecard with proper formatting
        scorecard = pd.DataFrame()
        scorecard['Ticker'] = result['Symbol']
        
        # Use company name from portfolio if available, otherwise from database
        ticker_to_company = dict(zip(portfolio_df['Ticker'], portfolio_df['Security']))
        scorecard['Company'] = scorecard['Ticker'].apply(
            lambda x: ticker_to_company.get(x, result[result['Symbol']==x]['Company Name'].iloc[0] if len(result[result['Symbol']==x]) > 0 else 'N/A')
        )
        
        # Growth Metrics (Ranks) - round to 1 decimal, fill NaN with 'N/A'
        scorecard['3Y Rev Growth Rank'] = result['"3-Year Revenue Growth Rate (Per Share)" Rank'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['3Y EBITDA Growth Rank'] = result['"3-Year EBITDA Growth Rate (Per Share)" Rank'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['3Y FCF Growth Rank'] = result['"3-Year FCF Growth Rate (Per Share)" Rank'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        
        # Profitability Metrics - round to 1 decimal, fill NaN with 'N/A'
        scorecard['Gross Margin %'] = result['Gross Margin %'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['Gross Profit to Asset'] = result['Gross-Profit-to-Asset %'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['ROIC %'] = result['"ROC (ROIC) %"'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['ROIC 5y Median'] = result['"ROC (ROIC) (5y Median)"'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        
        # Quality Metrics - integer, fill NaN with 0
        scorecard['Years Positive FCF'] = result['Years of Positive FCF over Past 10-Year'].fillna(0).astype(int)
        scorecard['Years Profitable'] = result['Years of Profitability over Past 10-Year'].fillna(0).astype(int)
        
        # OBQ Base Scores - round to 1 decimal, fill NaN with 'N/A'
        scorecard['OBQ Growth'] = result['obq_growth_score'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['OBQ Quality'] = result['OBQ_Quality_Rank'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['OBQ Momentum'] = result['obq_momentum_score'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['OBQ FinStr'] = result['obq_finstr_score'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['OBQ Value'] = result['obq_value_score'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        
        # OBQ Composite Scores - use computed values
        scorecard['OBQ Composite'] = result['computed_obq_composite'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['OBQ GM'] = result['computed_obq_gm'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['OBQ GQM'] = result['computed_obq_gqm'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['OBQ GQV'] = result['computed_obq_gqv'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        scorecard['OBQ VQF'] = result['computed_obq_vqf'].apply(
            lambda x: round(x, 1) if pd.notna(x) else 'N/A'
        )
        
        # Valuation Metrics
        scorecard['GF Valuation'] = result['GF Valuation'].fillna('N/A')
        
        # Maintain portfolio order
        scorecard['order'] = scorecard['Ticker'].map({s: i for i, s in enumerate(valid_tickers)})
        scorecard = scorecard.sort_values('order').drop('order', axis=1).reset_index(drop=True)
        
        return scorecard
        
    except Exception as e:
        st.error(f"Error fetching fundamentals from MotherDuck: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

# ============================================================================
# PORTFOLIO RADAR CHARTS FUNCTIONS
# ============================================================================

def get_green_gradient_color(score, min_score, max_score):
    """
    Get color from Teal to Bright Green gradient based on score.
    Lowest score = Teal (#4DB8A8)
    Highest score = Bright Green (#00C851)
    """
    # Avoid division by zero
    if max_score == min_score:
        normalized = 0.5
    else:
        normalized = (score - min_score) / (max_score - min_score)
    
    # Teal RGB: (77, 184, 168) = #4DB8A8
    # Bright Green RGB: (0, 200, 81) = #00C851
    start_r, start_g, start_b = 77, 184, 168
    end_r, end_g, end_b = 0, 200, 81
    
    # Interpolate
    r = int(start_r + (end_r - start_r) * normalized)
    g = int(start_g + (end_g - start_g) * normalized)
    b = int(start_b + (end_b - start_b) * normalized)
    
    line_color = f'rgb({r}, {g}, {b})'
    fill_color = f'rgba({r}, {g}, {b}, 0.5)'
    
    return line_color, fill_color


def create_portfolio_radar_charts(tickers):
    """
    Create radar charts for portfolio stocks with dynamic color scheme.
    Color intensity based on relative composite scores (heatmap style).
    """
    try:
        # Get MotherDuck token
        motherduck_token = os.getenv('MOTHERDUCK_TOKEN')
        if not motherduck_token:
            return None
        
        # Filter out empty tickers and SPMO
        valid_tickers = [t.strip().upper() for t in tickers if t and t.strip() and t.strip().upper() != 'SPMO']
        if not valid_tickers:
            return None
        
        symbols_str = "', '".join(valid_tickers)
        
        # Connect to MotherDuck
        conn = duckdb.connect(f'md:?motherduck_token={motherduck_token}')
        
        # Get GuruFocus data for all symbols
        data = conn.execute(f"""
            SELECT * FROM my_db.main.gurufocus_with_momentum 
            WHERE Symbol IN ('{symbols_str}')
        """).df()
        
        conn.close()
        
        if data.empty:
            return None
        
        # Filter symbols to only those with data
        symbols_with_data = data['Symbol'].unique().tolist()
        symbols = [s for s in valid_tickers if s in symbols_with_data]
        
        if not symbols:
            return None
        
        # Calculate composite scores for all stocks first (for min/max)
        composite_scores = {}
        for ticker in symbols:
            ticker_data = data[data['Symbol'] == ticker]
            if not ticker_data.empty:
                profitability_rank = ticker_data['"Profitability Rank"'].iloc[0]
                quality_rank = ticker_data['"Quality Rank"'].iloc[0]
                growth_rank = ticker_data['"Growth Rank"'].iloc[0]
                financial_strength = ticker_data['Financial Strength'].iloc[0]
                value_rank = ticker_data['JCN Value Rank'].iloc[0] / 10
                momentum = ticker_data['JCN Mom'].iloc[0] / 10
                
                composite = (profitability_rank + quality_rank + growth_rank + 
                           financial_strength + value_rank + momentum) / 6
                composite_scores[ticker] = composite
        
        # Get min and max composite scores for color scaling
        min_composite = min(composite_scores.values())
        max_composite = max(composite_scores.values())
        
        # Calculate grid dimensions (3 columns)
        n_stocks = len(symbols)
        n_cols = 3
        n_rows = math.ceil(n_stocks / n_cols)
        
        # Create subplot grid with polar charts
        fig = make_subplots(
            rows=n_rows, 
            cols=n_cols,
            specs=[[{'type': 'polar'}] * n_cols for _ in range(n_rows)],
            subplot_titles=[f"<b>{sym}</b>" for sym in symbols],
            vertical_spacing=0.08,
            horizontal_spacing=0.05
        )
        
        # Categories for radar chart
        categories = ['Profitability', 'Quality', 'Growth', 'Financial<br>Strength', 'Value', 'Momentum']
        
        # Add radar chart for each stock
        for idx, ticker in enumerate(symbols):
            row = (idx // n_cols) + 1
            col = (idx % n_cols) + 1
            
            ticker_data = data[data['Symbol'] == ticker]
            
            if not ticker_data.empty:
                # Extract metrics (all on 0-10 scale)
                profitability_rank = ticker_data['"Profitability Rank"'].iloc[0]
                quality_rank = ticker_data['"Quality Rank"'].iloc[0]
                growth_rank = ticker_data['"Growth Rank"'].iloc[0]
                financial_strength = ticker_data['Financial Strength'].iloc[0]
                value_rank = ticker_data['JCN Value Rank'].iloc[0] / 10
                momentum = ticker_data['JCN Mom'].iloc[0] / 10
                
                # Get title metrics
                jcn_pv_rank = ticker_data['JCN PV'].iloc[0]
                jcn_olivia = ticker_data['JCN Olivia'].iloc[0]
                
                # Get composite score
                jcn_composite = composite_scores[ticker]
                
                values = [profitability_rank, quality_rank, growth_rank, 
                         financial_strength, value_rank, momentum]
                
                # Get color based on relative composite score (heatmap style)
                line_color, fill_color = get_green_gradient_color(jcn_composite, min_composite, max_composite)
                
                # Add trace
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    fillcolor=fill_color,
                    line=dict(color=line_color, width=2),
                    name=ticker,
                    showlegend=False
                ), row=row, col=col)
                
                # Update subplot title
                fig.layout.annotations[idx].update(
                    text=f"<b>{ticker}</b><br>" +
                         f"<span style='font-size:10px'>Composite: <b>{jcn_composite:.1f}</b> | " +
                         f"PV: {jcn_pv_rank:.1f} | Olivia: {jcn_olivia:.1f}</span>"
                )
        
        # Update all polar axes
        for i in range(1, n_stocks + 1):
            fig.update_polars(
                bgcolor='rgba(255, 255, 255, 0.9)',
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    tickvals=[0, 2, 4, 6, 8, 10],
                    ticktext=['0', '2', '4', '6', '8', '10'],
                    gridcolor='rgba(200, 200, 200, 0.5)',
                    gridwidth=1,
                    tickfont=dict(size=8)
                ),
                angularaxis=dict(
                    gridcolor='rgba(200, 200, 200, 0.5)',
                    gridwidth=1,
                    tickfont=dict(size=9)
                ),
                selector=dict(type='polar')
            )
        
        # Update layout
        fig.update_layout(
            height=400 * n_rows,
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(l=40, r=40, t=60, b=40),
            autosize=True
        )
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating radar charts: {str(e)}")
        return None

# ============================================================================
# PORTFOLIO TRENDS FUNCTIONS
# ============================================================================

def get_last_refresh_time(conn):
    """Get the last time data was refreshed."""
    try:
        result = conn.execute("""
            SELECT MAX(last_updated) as last_refresh
            FROM my_db.main.StockDataYfinance4Streamlit
        """).df()
        
        if not result.empty and pd.notna(result['last_refresh'].iloc[0]):
            return result['last_refresh'].iloc[0]
        return None
    except:
        return None


def get_missing_data_range(conn, symbol):
    """Get the date range that needs to be updated for a symbol."""
    try:
        result = conn.execute(f"""
            SELECT MAX(date) as last_date
            FROM my_db.main.StockDataYfinance4Streamlit
            WHERE symbol = '{symbol}'
        """).df()
        
        if not result.empty and pd.notna(result['last_date'].iloc[0]):
            last_date = pd.to_datetime(result['last_date'].iloc[0])
            return last_date
        return None
    except:
        return None


def update_weekly_data(conn, symbols):
    """
    Update weekly data for symbols - only fetch missing data since last update.
    
    Returns:
        tuple: (success_count, failed_count, total_rows_added)
    """
    success_count = 0
    failed_count = 0
    total_rows = 0
    
    for symbol in symbols:
        try:
            # Get last date in database
            last_date = get_missing_data_range(conn, symbol)
            
            if last_date is None:
                # No data exists, download 10 years
                start_date = datetime.now() - timedelta(days=10*365)
            else:
                # Data exists, only get new data
                start_date = last_date + timedelta(days=1)
            
            end_date = datetime.now()
            
            # Skip if no new data needed
            if start_date >= end_date:
                continue
            
            # Download data
            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date, interval='1wk')
            
            if data.empty:
                continue
            
            # Process data
            data = data.reset_index()
            data = data[['Date', 'Open', 'High', 'Low', 'Close']].copy()
            data['Symbol'] = symbol
            data['Last_Updated'] = datetime.now()
            data = data[['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Last_Updated']]
            data.columns = ['symbol', 'date', 'open', 'high', 'low', 'close', 'last_updated']
            data['date'] = pd.to_datetime(data['date']).dt.date
            
            # Insert data
            conn.execute("""
                INSERT OR REPLACE INTO my_db.main.StockDataYfinance4Streamlit
                SELECT * FROM data
            """)
            
            total_rows += len(data)
            success_count += 1
            
        except Exception as e:
            failed_count += 1
            continue
    
    return success_count, failed_count, total_rows


def fetch_weekly_data(conn, symbols, years=8):
    """Fetch weekly OHLC data for the last N years."""
    try:
        start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y-%m-%d')
        symbols_str = "', '".join(symbols)
        
        data = conn.execute(f"""
            SELECT symbol as Symbol, date as Date, open as Open, 
                   high as High, low as Low, close as Close
            FROM my_db.main.StockDataYfinance4Streamlit
            WHERE symbol IN ('{symbols_str}')
            AND date >= '{start_date}'
            ORDER BY Symbol, Date
        """).df()
        
        return data
    except Exception as e:
        return pd.DataFrame()


def create_portfolio_trends_charts(tickers):
    """
    Create Plotly candlestick charts with regression and drawdown subplots for portfolio stocks.
    Each stock gets 2 rows: candlestick chart on top, drawdown chart below.
    """
    try:
        motherduck_token = os.getenv('MOTHERDUCK_TOKEN')
        if not motherduck_token:
            return None
        
        # Filter valid tickers
        valid_tickers = [t.strip().upper() for t in tickers if t and t.strip() and t.strip().upper() != 'SPMO']
        if not valid_tickers:
            return None
        
        # Connect to MotherDuck
        conn = duckdb.connect(f'md:?motherduck_token={motherduck_token}')
        
        # Fetch 8 years of data
        price_data = fetch_weekly_data(conn, valid_tickers, years=8)
        
        conn.close()
        
        if price_data.empty:
            return None
        
        # Filter to symbols with data
        symbols_with_data = price_data['Symbol'].unique().tolist()
        symbols = [s for s in valid_tickers if s in symbols_with_data]
        
        if not symbols:
            return None
        
        # Sort symbols alphabetically for consistent display
        symbols = sorted(symbols)
        
        # Calculate grid dimensions (3 columns, 2 rows per stock)
        n_stocks = len(symbols)
        n_cols = 3
        n_stock_rows = math.ceil(n_stocks / n_cols)
        total_rows = n_stock_rows * 2  # Each stock row becomes 2 subplot rows
        
        # Create specs and row heights
        specs = []
        row_heights = []
        for stock_row in range(n_stock_rows):
            # Candlestick row (larger to show more data)
            specs.append([{}] * n_cols)
            row_heights.append(0.85)
            # Drawdown row (smaller, just for reference)
            specs.append([{}] * n_cols)
            row_heights.append(0.15)
        
        # Create subplots
        fig = make_subplots(
            rows=total_rows,
            cols=n_cols,
            row_heights=row_heights,
            vertical_spacing=0.01,  # Minimal spacing so charts touch
            horizontal_spacing=0.08,
            specs=specs
        )
        
        for idx, symbol in enumerate(symbols):
            # Calculate which column this stock is in
            col = (idx % n_cols) + 1
            # Calculate which stock row this is (0-indexed)
            stock_row = idx // n_cols
            # Calculate actual subplot rows (each stock row = 2 subplot rows)
            candlestick_row = stock_row * 2 + 1
            drawdown_row = stock_row * 2 + 2
            
            stock_data = price_data[price_data['Symbol'] == symbol].copy()
            stock_data = stock_data.sort_values('Date').reset_index(drop=True)
            
            if len(stock_data) < 10:
                continue
            
            # Get last 5 years for regression (260 weeks)
            last_5_years = stock_data.tail(min(260, len(stock_data)))
            regression_start_idx = len(stock_data) - len(last_5_years)
            
            # Calculate regression
            x_reg = np.arange(len(last_5_years))
            y_reg = last_5_years['Close'].values
            slope, intercept, r_value, _, _ = stats.linregress(x_reg, y_reg)
            r_squared = r_value**2
            
            # Calculate CAGR
            start_price = last_5_years['Close'].iloc[0]
            end_price = last_5_years['Close'].iloc[-1]
            years = len(last_5_years) / 52
            cagr = (end_price / start_price) ** (1/years) - 1 if start_price > 0 else 0
            system_score = r_squared * cagr
            
            # Calculate Avg Annual High-Low Range %
            stock_data['Year'] = pd.to_datetime(stock_data['Date']).dt.year
            yearly_ranges = []
            for year in stock_data['Year'].unique():
                year_data = stock_data[stock_data['Year'] == year]
                if len(year_data) > 0:
                    year_high = year_data['High'].max()
                    year_low = year_data['Low'].min()
                    range_pct = ((year_high - year_low) / year_low) * 100 if year_low > 0 else 0
                    yearly_ranges.append(range_pct)
            avg_annual_range = np.mean(yearly_ranges) if yearly_ranges else 0
            
            # Regression line and confidence bands
            predicted = intercept + slope * x_reg
            residuals = y_reg - predicted
            std_error = np.sqrt(np.sum(residuals**2) / (len(x_reg) - 2))
            
            # Dates for regression plot
            reg_dates = stock_data['Date'].iloc[regression_start_idx:].values
            
            # Calculate drawdown
            cummax = stock_data['Close'].cummax()
            drawdown = ((stock_data['Close'] - cummax) / cummax) * 100
            current_drawdown = drawdown.iloc[-1]
            median_dd = drawdown.median()
            
            # Add candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=stock_data['Date'],
                    open=stock_data['Open'],
                    high=stock_data['High'],
                    low=stock_data['Low'],
                    close=stock_data['Close'],
                    name=symbol,
                    showlegend=False,
                    increasing_line_color='#2E7D32',
                    decreasing_line_color='#C62828'
                ),
                row=candlestick_row, col=col
            )
            
            # Add regression line
            fig.add_trace(
                go.Scatter(
                    x=reg_dates,
                    y=predicted,
                    mode='lines',
                    line=dict(color='blue', width=2),
                    name='Regression',
                    showlegend=False
                ),
                row=candlestick_row, col=col
            )
            
            # Add confidence bands (1, 2, 3 std errors)
            for std_mult, alpha in [(3, 0.05), (2, 0.08), (1, 0.10)]:
                fig.add_trace(
                    go.Scatter(
                        x=reg_dates,
                        y=predicted + std_mult*std_error,
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo='skip'
                    ),
                    row=candlestick_row, col=col
                )
                fig.add_trace(
                    go.Scatter(
                        x=reg_dates,
                        y=predicted - std_mult*std_error,
                        mode='lines',
                        line=dict(width=0),
                        fillcolor=f'rgba(128, 128, 128, {alpha})',
                        fill='tonexty',
                        showlegend=False,
                        hoverinfo='skip'
                    ),
                    row=candlestick_row, col=col
                )
            
            # Add drawdown chart (separate subplot below)
            fig.add_trace(
                go.Scatter(
                    x=stock_data['Date'],
                    y=drawdown,
                    mode='lines',
                    line=dict(color='darkred', width=1),
                    fill='tozeroy',
                    fillcolor='rgba(200, 0, 0, 0.2)',
                    name='Drawdown',
                    showlegend=False
                ),
                row=drawdown_row, col=col
            )
            
            # Add median drawdown line
            fig.add_trace(
                go.Scatter(
                    x=stock_data['Date'],
                    y=[median_dd] * len(stock_data),
                    mode='lines',
                    line=dict(color='gray', width=1, dash='dash'),
                    name='Median DD',
                    showlegend=False
                ),
                row=drawdown_row, col=col
            )
            
            # Add legend box at top-left with ticker and metrics (black text)
            fig.add_annotation(
                text=f"<b><span style='font-size:14px; color:black'>{symbol}</span></b><br>" +
                     f"<span style='font-size:9px; color:black'>SystemScore: {system_score:.4f} | R²: {r_squared:.4f} | CAGR: {cagr:.2%}<br>" +
                     f"Avg Annual Range: {avg_annual_range:.1f}% | Current DD: {current_drawdown:.1f}%</span>",
                xref="x domain",
                yref="y domain",
                x=0.02,  # Top-left position
                y=0.98,  # Top-left position
                showarrow=False,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(255, 255, 255, 0.8)',  # White background with slight transparency
                bordercolor='black',
                borderwidth=1,
                borderpad=4,
                row=candlestick_row,
                col=col
            )
            
            # Update y-axes labels
            fig.update_yaxes(title_text="Price ($)", row=candlestick_row, col=col)
            fig.update_yaxes(title_text="DD %", row=drawdown_row, col=col, 
                           range=[drawdown.min() * 1.1, 5])
            
            # Hide x-axis labels for candlestick charts (only show on drawdown)
            fig.update_xaxes(showticklabels=False, row=candlestick_row, col=col)
        
        # Update layout
        fig.update_layout(
            height=500 * n_stock_rows,  # Increased from 350px to 500px per stock row for larger charts
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(l=40, r=40, t=80, b=40),
            xaxis_rangeslider_visible=False
        )
        
        # Update all x-axes to hide rangeslider
        fig.update_xaxes(rangeslider_visible=False)
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating trend charts: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

# ============================================================================
# NEWS AGGREGATION FUNCTIONS
# ============================================================================

def filter_articles_batch(ticker, articles):
    """Use Grok to filter multiple articles at once for efficiency."""
    if not articles:
        return []
    
    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROK_API_KEY}"
        }
        
        articles_text = f"Ticker: {ticker}\n\n"
        for i, article in enumerate(articles, 1):
            articles_text += f"Article {i}:\n"
            articles_text += f"Headline: {article['headline']}\n"
            articles_text += f"Summary: {article['summary'][:200]}\n\n"
        
        payload = {
            "model": "grok-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial news analyst filtering articles for relevance."
                },
                {
                    "role": "user",
                    "content": f"""{articles_text}

For each article above, determine if it is PRIMARILY about {ticker} (not just mentioning it).

Respond with ONLY a comma-separated list of article numbers that are primarily about {ticker}.
Example: "1,3,5" or "2,4" or "NONE" if no articles are relevant.

Numbers only, no explanations."""
                }
            ],
            "stream": False,
            "temperature": 0
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        answer = result['choices'][0]['message']['content'].strip().upper()
        
        if "NONE" in answer:
            return []
        
        try:
            relevant_indices = [int(x.strip()) - 1 for x in answer.replace("ARTICLE", "").replace(":", "").split(",") if x.strip().isdigit()]
            return [articles[i] for i in relevant_indices if i < len(articles)]
        except:
            return articles
            
    except Exception as e:
        return articles

def fetch_finnhub_news_curated(symbols, days_back=1, target_per_stock=3):
    """Fetch and filter company news from Finnhub."""
    finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)
    all_news = []
    
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days_back)
    
    for symbol in symbols:
        try:
            news = finnhub_client.company_news(
                symbol, 
                _from=from_date.strftime('%Y-%m-%d'), 
                to=to_date.strftime('%Y-%m-%d')
            )
            
            recent_articles = []
            for article in news:
                article_time = datetime.fromtimestamp(article['datetime'])
                if article_time >= (to_date - timedelta(hours=24)):
                    recent_articles.append({
                        'headline': article.get('headline', ''),
                        'summary': article.get('summary', ''),
                        'datetime': article_time,
                        'url': article['url']
                    })
            
            if recent_articles:
                filtered_articles = []
                for i in range(0, len(recent_articles), 10):
                    batch = recent_articles[i:i+10]
                    relevant = filter_articles_batch(symbol, batch)
                    filtered_articles.extend(relevant)
                    time.sleep(2)
                
                for article in filtered_articles[:target_per_stock]:
                    summary = article['summary']
                    
                    if len(summary) > 150:
                        first_period = summary.find('.', 50)
                        if first_period > 0:
                            second_period = summary.find('.', first_period + 1)
                            if second_period > 0:
                                summary = summary[:second_period + 1]
                            else:
                                summary = summary[:first_period + 1]
                        else:
                            summary = summary[:150] + '...'
                    
                    all_news.append({
                        'Datetime': article['datetime'],
                        'Stock Ticker': symbol,
                        'Article Summary': summary,
                        'Article Link': article['url']
                    })
            
            time.sleep(1)
            
        except Exception as e:
            continue
    
    return all_news

def fetch_grok_news_curated(symbols, max_articles=30):
    """Fetch curated news from Grok API."""
    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROK_API_KEY}"
        }
        
        stock_list = ", ".join(symbols)
        today = datetime.now()
        yesterday = today - timedelta(hours=24)
        
        payload = {
            "model": "grok-4",
            "messages": [
                {
                    "role": "user",
                    "content": f"""For these stocks: {stock_list}

Find {max_articles} news articles from the LAST 24 HOURS where each article is PRIMARILY about ONE specific company (not just mentioning it).

For EACH article, provide:
TICKER: [the ONE stock this article is mainly about]
SUMMARY: [1-2 sentence summary]
---

Only include articles that are genuinely focused on that company."""
                }
            ],
            "search_parameters": {
                "mode": "on",
                "sources": [{"type": "news", "country": "US"}],
                "from_date": yesterday.strftime('%Y-%m-%d'),
                "to_date": today.strftime('%Y-%m-%d'),
                "return_citations": True,
                "max_search_results": max_articles
            },
            "stream": False,
            "temperature": 0
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        citations = result['choices'][0]['message'].get('citations', [])
        
        all_news = []
        sections = content.split('---')
        
        for i, citation in enumerate(citations[:max_articles]):
            section = sections[i] if i < len(sections) else ""
            
            found_symbol = None
            if 'TICKER:' in section:
                ticker_line = section.split('TICKER:')[1].split('\n')[0].strip()
                for symbol in symbols:
                    if symbol in ticker_line:
                        found_symbol = symbol
                        break
            
            if not found_symbol:
                for symbol in symbols:
                    if symbol in section:
                        found_symbol = symbol
                        break
            
            if not found_symbol:
                continue
            
            summary_text = section.strip()
            if 'SUMMARY:' in summary_text:
                summary_text = summary_text.split('SUMMARY:')[1].strip()
            
            if len(summary_text) > 200:
                first_period = summary_text.find('.', 50)
                if first_period > 0:
                    second_period = summary_text.find('.', first_period + 1)
                    if second_period > 0:
                        summary_text = summary_text[:second_period + 1]
                    else:
                        summary_text = summary_text[:first_period + 1]
                else:
                    summary_text = summary_text[:200] + '...'
            
            if not summary_text:
                summary_text = "Recent market news"
            
            all_news.append({
                'Datetime': datetime.now(),
                'Stock Ticker': found_symbol,
                'Article Summary': summary_text,
                'Article Link': citation
            })
        
        return all_news
        
    except Exception as e:
        return []

def aggregate_curated_news(symbols, target_total=63):
    """Aggregate curated news targeting up to 63 articles (3 per stock)."""
    target_per_stock = 3
    
    finnhub_news = fetch_finnhub_news_curated(symbols, days_back=1, target_per_stock=target_per_stock)
    grok_news = fetch_grok_news_curated(symbols, max_articles=30)
    
    all_news = finnhub_news + grok_news
    
    if not all_news:
        return pd.DataFrame(columns=['Datetime', 'Stock Ticker', 'Article Summary', 'Article Link'])
    
    news_df = pd.DataFrame(all_news)
    news_df = news_df.drop_duplicates(subset=['Article Link'], keep='first')
    news_df = news_df.sort_values('Datetime', ascending=False)
    news_df = news_df.head(target_total)
    news_df = news_df.reset_index(drop=True)
    
    return news_df

def save_news_to_cache(news_df, timestamp):
    """Save news data to cache file"""
    try:
        cache_data = {
            'timestamp': timestamp.isoformat(),
            'news': news_df.to_dict('records')
        }
        with open(NEWS_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        pass

def load_news_from_cache():
    """Load news data from cache file"""
    try:
        if os.path.exists(NEWS_CACHE_FILE):
            with open(NEWS_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            
            news_df = pd.DataFrame(cache_data['news'])
            news_df['Datetime'] = pd.to_datetime(news_df['Datetime'])
            timestamp = datetime.fromisoformat(cache_data['timestamp'])
            
            return news_df, timestamp
    except Exception as e:
        pass
    return None, None

# Portfolio Summary Generation Functions
def generate_stock_summary_grok(ticker, articles):
    """Generate AI summary for a single stock using Grok API"""
    try:
        # Prepare articles text
        articles_text = f"Stock: {ticker}\n\n"
        for i, article in enumerate(articles, 1):
            articles_text += f"Article {i}:\n"
            articles_text += f"Headline: {article['headline']}\n"
            articles_text += f"Summary: {article['summary']}\n\n"
        
        payload = {
            "model": "grok-3",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a senior financial analyst writing daily market summaries for institutional investors."
                },
                {
                    "role": "user",
                    "content": f"""Based on the following news articles about {ticker}, write a comprehensive 6-8 sentence paragraph summarizing the key developments, market sentiment, and implications for portfolio managers.

Focus on:
1. Main themes and narratives
2. Specific events or announcements
3. Market sentiment and analyst views
4. Actionable insights for investors
5. Risk factors or concerns

Articles:
{articles_text}

Provide only the summary paragraph, no additional commentary."""
                }
            ],
            "stream": False,
            "temperature": 0.7
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROK_API_KEY}"
        }
        
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content'].strip()
            return summary
        else:
            return f"Error generating summary: {response.status_code}"
            
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def generate_portfolio_summary(news_df, portfolio_symbols):
    """Generate comprehensive portfolio summary from news articles"""
    # Group articles by stock
    articles_by_stock = {}
    for _, row in news_df.iterrows():
        ticker = row['Stock Ticker']
        if ticker not in articles_by_stock:
            articles_by_stock[ticker] = []
        
        articles_by_stock[ticker].append({
            'headline': row['Article Summary'][:100],
            'summary': row['Article Summary'],
            'datetime': pd.to_datetime(row['Datetime']),
            'url': row['Article Link']
        })
    
    # Generate summaries for each stock
    summaries = {}
    for ticker in portfolio_symbols:
        if ticker in articles_by_stock:
            articles = articles_by_stock[ticker]
            summary = generate_stock_summary_grok(ticker, articles)
            summaries[ticker] = {
                'article_count': len(articles),
                'summary': summary
            }
            time.sleep(1)  # Rate limiting
    
    return summaries

def save_summary_to_cache(summaries, timestamp):
    """Save portfolio summary to cache file"""
    try:
        cache_data = {
            'summaries': summaries,
            'timestamp': timestamp.isoformat()
        }
        with open(SUMMARY_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
    except Exception as e:
        st.error(f"Error saving summary cache: {str(e)}")

def load_summary_from_cache():
    """Load portfolio summary from cache file"""
    try:
        if os.path.exists(SUMMARY_CACHE_FILE):
            with open(SUMMARY_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            
            summaries = cache_data['summaries']
            timestamp = datetime.fromisoformat(cache_data['timestamp'])
            
            return summaries, timestamp
    except Exception as e:
        pass
    return None, None

# Check if we should fetch fresh data
should_fetch_fresh = False

# Check for force refresh (user clicked button)
if st.session_state.force_refresh:
    should_fetch_fresh = True
    st.session_state.force_refresh = False

# Check for auto-refresh (15 minutes elapsed)
if 'last_refresh' in st.session_state:
    time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
    if time_since_refresh > 900:  # 900 seconds = 15 minutes
        should_fetch_fresh = True

# Try to load from cache first
cached_portfolio_data, cached_time = load_from_cache()

# Main content area - Portfolio Performance Details
if tickers and len(tickers) > 0:
    try:
        portfolio_data = []
        
        # If we should fetch fresh data, try to get it from API
        if should_fetch_fresh or cached_portfolio_data is None:
            with st.spinner("Fetching fresh stock data from Yahoo Finance..."):
                fetch_success = True
                
                for ticker in tickers:
                    # Get portfolio input data
                    portfolio_row = st.session_state.portfolio_data[st.session_state.portfolio_data['Symbol'] == ticker]
                    
                    if not portfolio_row.empty:
                        cost_basis = portfolio_row['Cost Basis'].values[0]
                        shares = portfolio_row['Shares'].values[0]
                        
                        # Get comprehensive stock data
                        stock_data = get_comprehensive_stock_data(ticker)
                        
                        # If fetch failed (rate limit), use cached data
                        if stock_data is None:
                            fetch_success = False
                            break
                        
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
                
                # If fetch was successful, save to cache
                if fetch_success and portfolio_data:
                    save_to_cache(portfolio_data, datetime.now())
                    st.session_state.last_refresh = datetime.now()
                    st.success("✅ Fresh data loaded successfully!")
                elif not fetch_success and cached_portfolio_data:
                    # Fall back to cached data
                    portfolio_data = cached_portfolio_data
                    st.warning("⚠️ Rate limit reached. Loading from cache...")
                elif not fetch_success:
                    st.error("❌ Could not fetch data and no cache available. Please try again later.")
                    portfolio_data = []
        else:
            # Load from cache
            if cached_portfolio_data:
                portfolio_data = cached_portfolio_data
                st.info("📦 Loading from cache (click Refresh Data for latest prices)")
        
        if portfolio_data:
            # Create DataFrame
            perf_df = pd.DataFrame(portfolio_data)
            
            # Calculate portfolio percentage
            total_portfolio_value = perf_df['Position_Value'].sum()
            if total_portfolio_value > 0:
                perf_df['Port_Pct'] = (perf_df['Position_Value'] / total_portfolio_value) * 100
            else:
                perf_df['Port_Pct'] = 0.0
            
            # PORTFOLIO PERFORMANCE DETAILS TABLE (TOP OF PAGE)
            st.subheader("💼 Portfolio Performance Details")
            
            # Prepare display dataframe (don't include Shares column or Sparkline)
            display_df = perf_df[[
                'Security', 'Ticker', 'Cost Basis', 'Cur Price', 'Port_Pct',
                'Daily_Change_Pct', 'YTD_Pct', 'YoY_Pct', 'Port_Gain_Pct',
                'Pct_Below_52wk', 'Chan_Range', 'Sector', 'Industry'
            ]].copy()
            
            # Rename columns
            display_df.columns = [
                'Security', 'Ticker', 'Cost Basis', 'Cur Price', '% Port.',
                'Daily % Change', 'YTD %', 'YoY % Change', 'Port. Gain %',
                '% Below 52wk High', '52wk Chan Range', 'Sector', 'Industry'
            ]
            
            # Helper function for % Portfolio heatmap (white to light blue)
            def color_port_pct(val):
                if pd.isna(val):
                    return ''
                # Normalize to 0-1 range based on min/max
                min_val = display_df['% Port.'].min()
                max_val = display_df['% Port.'].max()
                if max_val == min_val:
                    normalized = 0.5
                else:
                    normalized = (val - min_val) / (max_val - min_val)
                # Create blue gradient (light blue at max)
                blue_intensity = int(255 - (normalized * 100))  # 255 (white) to 155 (light blue)
                color = f'background-color: rgb({blue_intensity}, {blue_intensity}, 255)'
                return color
            
            # Helper function for Daily % Change heatmap (red for negative, green for positive)
            def color_daily_change(val):
                if pd.isna(val):
                    return ''
                if val < 0:
                    # Negative: shades of red (darker red for more negative)
                    intensity = min(abs(val) * 20, 200)  # Cap at 200 for readability
                    red = int(255 - intensity)
                    color = f'background-color: rgb(255, {red}, {red})'
                elif val > 0:
                    # Positive: shades of green (brighter green for more positive)
                    intensity = min(val * 20, 200)
                    green = int(255 - intensity)
                    color = f'background-color: rgb({green}, 255, {green})'
                else:
                    color = ''
                return color
            
            # Apply styling
            styled_df = display_df.style\
                .format({
                    'Cost Basis': '${:.2f}',
                    'Cur Price': '${:.2f}',
                    '% Port.': '{:.2f}%',
                    'Daily % Change': '{:.2f}%',
                    'YTD %': '{:.2f}%',
                    'YoY % Change': '{:.2f}%',
                    'Port. Gain %': '{:.2f}%',
                    '% Below 52wk High': '{:.2f}%',
                    '52wk Chan Range': '{:.1f}%'
                })\
                .applymap(color_port_pct, subset=['% Port.'])\
                .applymap(color_daily_change, subset=['Daily % Change'])\
                .set_properties(**{
                    'text-align': 'left',
                    'font-size': '12px'
                })\
                .set_table_styles([{
                    'selector': 'thead th',
                    'props': [('font-weight', 'bold'), ('color', '#000000'), ('background-color', '#f0f0f0')]
                }])
            
            # Display styled dataframe (no column_config needed with Styler)
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                height=800
            )
            
            # Benchmarks section
            st.markdown("---")
            st.subheader("📊 Benchmarks")
            
            # Calculate portfolio weighted daily change
            portfolio_daily_change = calculate_portfolio_daily_change(display_df)
            
            # Get SPY daily change (from cache or fresh)
            spy_daily_change = get_spy_daily_change(should_fetch_fresh, cached_time)
            
            # Calculate daily alpha
            daily_alpha = portfolio_daily_change - spy_daily_change
            
            # Display 3 metrics horizontally
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Portfolio Est. Daily % Change",
                    f"{portfolio_daily_change:+.2f}%"
                )
            
            with col2:
                st.metric(
                    "Benchmark Est. Daily % Change",
                    f"{spy_daily_change:+.2f}%"
                )
            
            with col3:
                st.metric(
                    "Est. Daily Alpha",
                    f"{daily_alpha:+.2f}%"
                )
            
            st.markdown("---")
            
            # Portfolio Allocation
            st.subheader("📊 Portfolio Allocation")
            
            # Create pie charts using the raw portfolio dataframe
            with st.spinner("Generating allocation charts..."):
                allocation_fig = create_portfolio_pie_charts(perf_df)
                st.plotly_chart(allocation_fig, use_container_width=True)
            
            st.markdown("---")
            
            # Normalized Price Comparison Chart
            st.subheader(f"📊 Normalized Stock Price Comparison - {st.session_state.selected_period}")
            
            # Fetch historical data for chart
            time_options = {
                "1 Month": "1mo",
                "3 Months": "3mo",
                "6 Months": "6mo",
                "1 Year": "1y",
                "5 Years": "5y",
                "10 Years": "10y",
                "20 Years": "20y"
            }
            
            period = time_options[st.session_state.selected_period]
            
            stock_data = {}
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    data = stock.history(period=period)
                    if not data.empty:
                        stock_data[ticker] = data['Close']
                except:
                    pass
            
            if stock_data:
                df = pd.DataFrame(stock_data).dropna()
                
                if len(df) > 0:
                    # Normalize prices
                    df_normalized = df.copy()
                    for col in df_normalized.columns:
                        df_normalized[col] = df_normalized[col] / df_normalized[col].iloc[0]
                    
                    # Create chart
                    fig = go.Figure()
                    
                    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', 
                             '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
                    
                    for idx, ticker in enumerate(df_normalized.columns):
                        color = colors[idx % len(colors)]
                        fig.add_trace(go.Scatter(
                            x=df_normalized.index,
                            y=df_normalized[ticker],
                            mode='lines',
                            name=ticker,
                            line=dict(width=2, color=color),
                            hovertemplate=f'<b>{ticker}</b><br>Date: %{{x}}<br>Normalized Price: %{{y:.2f}}<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        height=600,
                        hovermode='x unified',
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        xaxis=dict(
                            title="Date",
                            showgrid=True,
                            gridcolor='lightgray',
                            showline=True,
                            linecolor='black'
                        ),
                        yaxis=dict(
                            title="Normalized Price",
                            showgrid=True,
                            gridcolor='lightgray',
                            showline=True,
                            linecolor='black'
                        ),
                        legend=dict(
                            orientation="v",
                            yanchor="top",
                            y=1,
                            xanchor="left",
                            x=1.02,
                            bgcolor='rgba(255,255,255,0.8)',
                            bordercolor='lightgray',
                            borderwidth=1
                        ),
                        font=dict(color='black')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Dashboard Controls (Horizontal Time Horizon)
            st.markdown("---")
            st.subheader("⚙️ Dashboard Controls")
            st.markdown("**Time Horizon**")
            
            time_period_options = list(time_options.keys())
            cols = st.columns(7)
            
            for idx, option in enumerate(time_period_options):
                with cols[idx]:
                    if st.button(option, use_container_width=True, 
                               type="primary" if st.session_state.selected_period == option else "secondary"):
                        st.session_state.selected_period = option
                        st.rerun()
        else:
            st.error("Could not load portfolio data.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    st.info("👇 Add stocks to your portfolio table below to begin analysis.")

# ============================================================================
# PORTFOLIO FUNDAMENTALS TABLE
# ============================================================================

if 'portfolio_data' in st.session_state and not st.session_state.portfolio_data.empty and tickers:
    st.markdown("---")
    st.subheader("📊 Portfolio Fundamentals")
    
    with st.spinner("Fetching fundamental metrics from MotherDuck..."):
        fundamentals_df = get_fundamentals_from_motherduck(tickers, perf_df)
    
    if fundamentals_df is not None and not fundamentals_df.empty:
        # Configure AG Grid with frozen columns
        gb = GridOptionsBuilder.from_dataframe(fundamentals_df)
        
        # Pin Ticker and Company columns to the left (frozen)
        gb.configure_column("Ticker", pinned='left', width=80, suppressSizeToFit=True)
        gb.configure_column("Company", pinned='left', width=200, suppressSizeToFit=True)
        
        # Configure other columns with appropriate widths for readability
        column_widths = {
            '3Y Rev Growth Rank': 160,
            '3Y EBITDA Growth Rank': 180,
            '3Y FCF Growth Rank': 160,
            'Gross Margin %': 130,
            'Gross Profit to Asset': 170,
            'ROIC %': 100,
            'ROIC 5y Median': 140,
            'Years Positive FCF': 150,
            'Years Profitable': 140,
            'OBQ Composite': 140,
            'OBQ Growth': 120,
            'OBQ Quality': 120,
            'OBQ Momentum': 140,
            'OBQ FinStr': 120,
            'OBQ Value': 120,
            'GF Valuation': 130,
            'OBQ GQV': 110,
            'OBQ GQM': 110,
            'OBQ VQF': 110,
            'OBQ GM': 110
        }
        
        for col in fundamentals_df.columns:
            if col not in ['Ticker', 'Company']:
                width = column_widths.get(col, 140)  # Default 140px if not specified
                gb.configure_column(col, width=width, minWidth=width)
        
        # Enable sorting and filtering
        gb.configure_default_column(sortable=True, filterable=False, resizable=True)
        
        # Grid options
        gb.configure_grid_options(
            domLayout='normal',
            enableRangeSelection=True,
            suppressHorizontalScroll=False
        )
        
        gridOptions = gb.build()
        
        # Display AG Grid
        AgGrid(
            fundamentals_df,
            gridOptions=gridOptions,
            height=600,
            fit_columns_on_grid_load=False,
            theme='streamlit',
            update_mode=GridUpdateMode.NO_UPDATE,
            allow_unsafe_jscode=False
        )
        
        st.caption("💡 Tip: Scroll horizontally to see all metrics. Ticker and Company columns remain frozen on the left.")
        
        # ============================================================================
        # PORTFOLIO AGGREGATED METRICS SECTION
        # ============================================================================
        st.markdown("---")
        st.subheader("📊 Portfolio Aggregated Metrics")
        
        with st.spinner("Calculating portfolio aggregates..."):
            aggregated_df = get_portfolio_aggregated_metrics(fundamentals_df)
            
            if aggregated_df is not None and not aggregated_df.empty:
                st.dataframe(
                    aggregated_df,
                    use_container_width=True,
                    height=None  # Auto height to show all rows without scrolling
                )
                st.caption("💡 Shows Max, Median, Average, and Min values across all portfolio stocks for each fundamental metric.")
            else:
                st.info("No aggregated metrics available.")
    else:
        st.info("No fundamental data available from MotherDuck for portfolio stocks.")

# ============================================================================
# PORTFOLIO RADAR CHARTS SECTION
# ============================================================================
st.markdown("---")
st.subheader("📊 Portfolio Quality Radar Charts")

with st.spinner("Loading radar charts from MotherDuck..."):
    radar_fig = create_portfolio_radar_charts(tickers)
    
    if radar_fig is not None:
        st.plotly_chart(radar_fig, use_container_width=True)
        st.caption("💡 Color intensity indicates relative performance: Brightest green = highest composite score, Lighter teal = lowest composite score")
    else:
        st.info("No radar chart data available from MotherDuck for portfolio stocks.")

# ============================================================================
# PORTFOLIO TRENDS SECTION
# ============================================================================
st.markdown("---")

# Auto-refresh check (Friday 5 PM EST)
try:
    from datetime import timezone
    import pytz
    
    est = pytz.timezone('US/Eastern')
    now_est = datetime.now(est)
    
    # Check if it's Friday after 5 PM
    if now_est.weekday() == 4 and now_est.hour >= 17:  # Friday = 4
        motherduck_token = os.getenv('MOTHERDUCK_TOKEN')
        if motherduck_token and tickers:
            conn = duckdb.connect(f'md:?motherduck_token={motherduck_token}')
            last_refresh = get_last_refresh_time(conn)
            
            # Only auto-refresh if last refresh was before this Friday 5 PM
            if last_refresh:
                last_refresh_est = last_refresh.astimezone(est)
                friday_5pm = now_est.replace(hour=17, minute=0, second=0, microsecond=0)
                
                if last_refresh_est < friday_5pm:
                    # Auto-refresh needed
                    success, failed, total_rows = update_weekly_data(conn, tickers)
                    if total_rows > 0:
                        st.success(f"✅ Auto-refreshed {success} stocks ({total_rows} new weeks) - Friday 5 PM EST")
            
            conn.close()
except:
    pass

# Header with refresh button and timestamp
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("📈 Portfolio Trends")
    
    # Get last refresh time
    try:
        motherduck_token = os.getenv('MOTHERDUCK_TOKEN')
        if motherduck_token:
            conn = duckdb.connect(f'md:?motherduck_token={motherduck_token}')
            last_refresh = get_last_refresh_time(conn)
            conn.close()
            
            if last_refresh:
                st.caption(f"🕒 Last data refresh: {last_refresh.strftime('%Y-%m-%d %I:%M %p EST')}")
            else:
                st.caption("⚠️ No data found - please run initial data population script")
    except:
        pass

with col2:
    if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_trends_data"):
        with st.spinner("Updating weekly data..."):
            try:
                motherduck_token = os.getenv('MOTHERDUCK_TOKEN')
                if motherduck_token:
                    conn = duckdb.connect(f'md:?motherduck_token={motherduck_token}')
                    success, failed, total_rows = update_weekly_data(conn, tickers)
                    conn.close()
                    
                    if total_rows > 0:
                        st.success(f"✅ Updated {success} stocks ({total_rows} new weeks)")
                    else:
                        st.info("✅ Data is already up to date")
                    
                    if failed > 0:
                        st.warning(f"⚠️ {failed} stocks failed to update")
                else:
                    st.error("MotherDuck token not configured")
            except Exception as e:
                st.error(f"Error updating data: {str(e)}")

# Display charts
if tickers:
    with st.spinner("Loading trend charts from MotherDuck..."):
        trends_fig = create_portfolio_trends_charts(tickers)
        
        if trends_fig is not None:
            st.plotly_chart(trends_fig, use_container_width=True)
            st.caption("💡 8 years of weekly OHLC data with 5-year regression line. Drawdown shown below each chart.")
        else:
            st.info("⚠️ No trend data available. Please run the initial data population script in Data_Management folder.")
else:
    st.info("👇 Add stocks to your portfolio to see trend charts.")

# ============================================================================
# GROK NEWS AGGREGATOR SECTION
# ============================================================================
st.markdown("---")
st.markdown("---")

# ============================================================================
# PORTFOLIO NEWS SUMMARY SECTION
# ============================================================================

st.markdown("---")

# Initialize session state for summary refresh
if 'force_summary_refresh' not in st.session_state:
    st.session_state.force_summary_refresh = False
if 'last_summary_refresh' not in st.session_state:
    st.session_state.last_summary_refresh = None

# Header with regenerate button
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("📝 Portfolio News Summary")
with col2:
    if st.button("🔄 Regenerate Summary", use_container_width=True):
        st.session_state.force_summary_refresh = True
        st.rerun()

# Check if portfolio exists
if 'portfolio_data' in st.session_state and not st.session_state.portfolio_data.empty:
    portfolio_symbols = st.session_state.portfolio_data['Symbol'].tolist()
    
    # Check if we should generate fresh summary
    should_generate_fresh_summary = False
    
    # Check for force refresh (user clicked button)
    if st.session_state.force_summary_refresh:
        should_generate_fresh_summary = True
        st.session_state.force_summary_refresh = False
    
    # Check for auto-refresh (daily at midnight)
    if st.session_state.last_summary_refresh:
        now = datetime.now()
        last_refresh = st.session_state.last_summary_refresh
        # Check if it's a new day
        if now.date() > last_refresh.date():
            should_generate_fresh_summary = True
    
    # Try to load from cache first
    cached_summaries, cached_summary_time = load_summary_from_cache()
    
    # Check if we have news articles to summarize
    cached_news, _ = load_news_from_cache()
    
    if cached_news is not None and len(cached_news) > 0:
        # If we should generate fresh summary, try to generate it
        if should_generate_fresh_summary or cached_summaries is None:
            with st.spinner("🤖 Generating AI-powered portfolio summary... This may take 3-5 minutes."):
                try:
                    summaries = generate_portfolio_summary(cached_news, portfolio_symbols)
                    summary_timestamp = datetime.now()
                    
                    # Save to cache
                    save_summary_to_cache(summaries, summary_timestamp)
                    
                    # Update session state
                    st.session_state.last_summary_refresh = summary_timestamp
                    
                    st.success("✅ Portfolio summary generated successfully!")
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")
                    # Fall back to cached summaries if available
                    if cached_summaries:
                        summaries = cached_summaries
                        summary_timestamp = cached_summary_time
                        st.info("📦 Loaded from cache due to error.")
                    else:
                        summaries = None
                        summary_timestamp = None
        else:
            # Use cached summaries
            summaries = cached_summaries
            summary_timestamp = cached_summary_time
            if summaries:
                st.info(f"📦 Loaded from cache (Last updated: {summary_timestamp.strftime('%Y-%m-%d %I:%M:%S %p')} EST)")
        
        # Display summaries
        if summaries and len(summaries) > 0:
            st.markdown(f"**{len(summaries)} stocks analyzed** | **Generated: {summary_timestamp.strftime('%B %d, %Y at %I:%M %p EST')}**")
            st.markdown("")
            
            # Display each stock summary in an expander
            for ticker in portfolio_symbols:
                if ticker in summaries:
                    summary_data = summaries[ticker]
                    with st.expander(f"📊 **{ticker}** ({summary_data['article_count']} articles)", expanded=False):
                        st.markdown(summary_data['summary'])
        else:
            st.info("💡 No summaries available. Click 'Regenerate Summary' to generate AI-powered analysis.")
    else:
        st.info("💡 No news articles available. Load news first using the Grok News Aggregator below.")
else:
    st.info("👇 Add stocks to your portfolio to see AI-powered news summaries.")

# ============================================================================
# GROK NEWS AGGREGATOR SECTION
# ============================================================================

st.markdown("---")

# Initialize session state for news refresh
if 'force_news_refresh' not in st.session_state:
    st.session_state.force_news_refresh = False
if 'last_news_refresh' not in st.session_state:
    st.session_state.last_news_refresh = None

# Header with reload button
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("📰 Grok News Aggregator")
with col2:
    if st.button("🔄 Reload News", use_container_width=True):
        st.session_state.force_news_refresh = True
        st.rerun()

# Check if we should fetch fresh news
should_fetch_fresh_news = False

# Check for force refresh (user clicked button)
if st.session_state.force_news_refresh:
    should_fetch_fresh_news = True
    st.session_state.force_news_refresh = False

# Check for midnight refresh (daily at midnight EST)
if st.session_state.last_news_refresh:
    now = datetime.now()
    last_refresh = st.session_state.last_news_refresh
    # Check if it's past midnight and we haven't refreshed today
    if now.date() > last_refresh.date():
        should_fetch_fresh_news = True

# Try to load from cache first
if not should_fetch_fresh_news:
    news_df, news_timestamp = load_news_from_cache()
    if news_df is not None and len(news_df) > 0:
        st.info(f"📦 Loaded from cache (Last updated: {news_timestamp.strftime('%Y-%m-%d %I:%M:%S %p')} EST) - Click 'Reload News' for latest articles")
    else:
        should_fetch_fresh_news = True
else:
    news_df = None

# Fetch fresh news if needed
if should_fetch_fresh_news:
    # Check if portfolio data exists
    if 'portfolio_df' in st.session_state and len(st.session_state.portfolio_df) > 0:
        with st.spinner("🔍 Fetching curated news from Finnhub and Grok... This may take a few minutes."):
            # Get portfolio symbols
            portfolio_symbols = st.session_state.portfolio_df['Symbol'].tolist()
            
            # Aggregate news
            news_df = aggregate_curated_news(portfolio_symbols, target_total=63)
            
            if len(news_df) > 0:
                # Save to cache
                now = datetime.now()
                save_news_to_cache(news_df, now)
                st.session_state.last_news_refresh = now
                st.success(f"✅ Fresh news loaded successfully! Found {len(news_df)} articles.")
            else:
                st.warning("⚠️ No recent news articles found for your portfolio stocks.")
    else:
        st.info("👇 Add stocks to your portfolio to see curated news.")
        news_df = None

# Display news table
if news_df is not None and len(news_df) > 0:
    st.markdown(f"**Showing {len(news_df)} articles from the last 24 hours**")
    st.markdown(f"*Source: Finnhub + Grok AI (filtered for relevance)*")
    
    # Format datetime for display
    display_news_df = news_df.copy()
    display_news_df['Datetime'] = display_news_df['Datetime'].dt.strftime('%Y-%m-%d %I:%M %p')
    
    # Make links clickable
    display_news_df['Article Link'] = display_news_df['Article Link'].apply(lambda x: f'<a href="{x}" target="_blank">Read Article</a>')
    
    # Display as HTML table for clickable links
    st.markdown(
        display_news_df.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
else:
    st.info("No news articles available. Click 'Reload News' to fetch the latest articles.")

# Portfolio Input Section (AT BOTTOM)
st.markdown("---")
st.markdown("---")
st.subheader("📊 Portfolio Input")

# Edit/Save button
col1, col2 = st.columns([1, 5])
with col1:
    if st.session_state.edit_mode:
        if st.button("💾 Save", use_container_width=True, type="primary"):
            st.session_state.edit_mode = False
            st.rerun()
    else:
        if st.button("✏️ Edit", use_container_width=True):
            st.session_state.edit_mode = True
            st.rerun()

with col2:
    if st.session_state.edit_mode:
        st.info("✏️ **Edit Mode Active** - You can now modify the portfolio. Click 'Save' when done.")
    else:
        st.success("🔒 **View Mode** - Portfolio is locked. Click 'Edit' to make changes.")

st.markdown("Enter your portfolio holdings below (max 30 positions)")

# Display table based on edit mode
if st.session_state.edit_mode:
    # Editable mode
    edited_df = st.data_editor(
        st.session_state.portfolio_data,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Symbol": st.column_config.TextColumn(
                "Stock Symbol",
                help="Enter stock ticker symbol (e.g., AAPL, MSFT)",
                max_chars=10,
                required=True
            ),
            "Cost Basis": st.column_config.NumberColumn(
                "Cost Basis ($)",
                help="Average purchase price per share",
                min_value=0.01,
                format="$%.2f",
                required=True
            ),
            "Shares": st.column_config.NumberColumn(
                "Number of Shares",
                help="Total shares owned",
                min_value=0,
                format="%d",
                required=True
            )
        },
        hide_index=False,
        key="portfolio_editor"
    )
    
    # Limit to 30 rows
    if len(edited_df) > 30:
        st.error("⚠️ Maximum 30 positions allowed. Please remove some rows.")
        edited_df = edited_df.head(30)
    
    # Update session state with edited data
    st.session_state.portfolio_data = edited_df
else:
    # Read-only mode
    st.dataframe(
        st.session_state.portfolio_data,
        use_container_width=True,
        hide_index=False,
        column_config={
            "Symbol": "Stock Symbol",
            "Cost Basis": st.column_config.NumberColumn(
                "Cost Basis ($)",
                format="$%.2f"
            ),
            "Shares": st.column_config.NumberColumn(
                "Number of Shares",
                format="%d"
            )
        }
    )

# Footer
st.markdown("---")
st.caption("JCN Financial & Tax Advisory Group, LLC - Built with Streamlit")
