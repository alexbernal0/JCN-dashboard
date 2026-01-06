import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
from PIL import Image
import time
import json
import os

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

# Cache file path
CACHE_FILE = "portfolio_cache.json"

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
            'sector': sector,
            'industry': industry
        }
    except Exception as e:
        # Silent error handling - return None to indicate failure
        return None

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
            
            # Prepare display dataframe with proper formatting
            display_df = perf_df[[
                'Security', 'Ticker', 'Cost Basis', 'Shares', 'Cur Price', 'Port_Pct',
                'Daily_Change_Pct', 'YTD_Pct', 'YoY_Pct', 'Port_Gain_Pct',
                'Pct_Below_52wk', 'Chan_Range', 'Sector', 'Industry'
            ]].copy()
            
            # Format columns for display
            display_df['Cost Basis'] = display_df['Cost Basis'].apply(lambda x: f"${x:.2f}")
            display_df['Cur Price'] = display_df['Cur Price'].apply(lambda x: f"${x:.2f}")
            display_df['Port_Pct'] = display_df['Port_Pct'].apply(lambda x: f"{x:.2f}%")
            display_df['Daily_Change_Pct'] = display_df['Daily_Change_Pct'].apply(lambda x: f"{x:.2f}%")
            display_df['YTD_Pct'] = display_df['YTD_Pct'].apply(lambda x: f"{x:.2f}%")
            display_df['YoY_Pct'] = display_df['YoY_Pct'].apply(lambda x: f"{x:.2f}%")
            display_df['Port_Gain_Pct'] = display_df['Port_Gain_Pct'].apply(lambda x: f"{x:.2f}%")
            display_df['Pct_Below_52wk'] = display_df['Pct_Below_52wk'].apply(lambda x: f"-{x:.2f}%")
            display_df['Chan_Range'] = display_df['Chan_Range'].apply(lambda x: f"{x:.2f}%")
            
            # Rename columns to match desired output
            display_df.columns = [
                'Security', 'Ticker', 'Cost Basis', 'Shares', 'Cur Price', '% Port.',
                'Daily % Change', 'YTD %', 'YoY % Change', 'Port. Gain %',
                '% Below 52wk High', '52wk Chan Range', 'Sector', 'Industry'
            ]
            
            # Display full table without scrolling - using a large height value
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=800  # Large enough to show all 21 rows
            )
            
            # Portfolio totals
            st.markdown("---")
            st.subheader("💰 Portfolio Totals")
            
            total_cost = (perf_df['Cost Basis'] * perf_df['Shares']).sum()
            total_current_value = perf_df['Position_Value'].sum()
            total_gain_loss = total_current_value - total_cost
            total_gain_loss_pct = (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Cost Basis", f"${total_cost:,.2f}")
            
            with col2:
                st.metric("Current Value", f"${total_current_value:,.2f}")
            
            with col3:
                st.metric("Total Gain/Loss", f"${total_gain_loss:,.2f}", 
                         delta=f"{total_gain_loss_pct:.2f}%")
            
            with col4:
                st.metric("Return on Investment", f"{total_gain_loss_pct:.2f}%")
            
            st.markdown("---")
            
            # Performance Summary
            st.subheader("📈 Performance Summary")
            
            best_idx = perf_df['Port_Gain_Pct'].idxmax()
            worst_idx = perf_df['Port_Gain_Pct'].idxmin()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="📈 Best Performer",
                    value=perf_df.loc[best_idx, 'Ticker'],
                    delta=f"+{perf_df.loc[best_idx, 'Port_Gain_Pct']:.2f}%"
                )
            
            with col2:
                st.metric(
                    label="📉 Worst Performer",
                    value=perf_df.loc[worst_idx, 'Ticker'],
                    delta=f"{perf_df.loc[worst_idx, 'Port_Gain_Pct']:.2f}%"
                )
            
            with col3:
                avg_performance = perf_df['Port_Gain_Pct'].mean()
                st.metric(
                    label="📊 Average Performance",
                    value=f"{avg_performance:.2f}%",
                    delta=f"{len(tickers)} stocks tracked"
                )
            
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
