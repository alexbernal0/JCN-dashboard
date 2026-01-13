import streamlit as st
from PIL import Image
import duckdb
import os
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Stock Analysis - JCN Dashboard",
    page_icon="📈",
    layout="wide"
)

# MotherDuck connection
MOTHERDUCK_TOKEN = os.getenv('MOTHERDUCK_TOKEN')

def get_stock_info_from_motherduck(ticker):
    """Get stock information from MotherDuck"""
    try:
        # Connect to MotherDuck
        conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
        
        # Query for stock info combining gurufocus and price data
        query = f"""
        SELECT 
            g.Symbol as ticker,
            g."Company Name" as company,
            g.Sector as sector,
            g.Industry as industry,
            p.close as current_price,
            p.date as last_updated
        FROM my_db.main.gurufocus_with_momentum g
        LEFT JOIN (
            SELECT symbol, close, date
            FROM my_db.main.pwb_allstocks
            WHERE symbol = '{ticker.upper()}'
            ORDER BY date DESC
            LIMIT 1
        ) p ON g.Symbol = p.symbol
        WHERE g.Symbol = '{ticker.upper()}'
        LIMIT 1
        """
        
        result = conn.execute(query).fetchdf()
        conn.close()
        
        if not result.empty:
            return {
                'ticker': result['ticker'].iloc[0],
                'company': result['company'].iloc[0],
                'sector': result['sector'].iloc[0] if result['sector'].iloc[0] else 'N/A',
                'industry': result['industry'].iloc[0] if result['industry'].iloc[0] else 'N/A',
                'current_price': result['current_price'].iloc[0] if result['current_price'].iloc[0] else 0,
                'last_updated': result['last_updated'].iloc[0] if result['last_updated'].iloc[0] else 'N/A'
            }
        return None
        
    except Exception as e:
        st.error(f"Error fetching stock info: {str(e)}")
        return None

def get_per_share_data(ticker):
    """Get 10-year fiscal year per share metrics from MotherDuck"""
    try:
        conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
        
        # Fetch income statement data
        df_income = conn.execute(f"""
            SELECT symbol, date, total_revenue, gross_profit, ebit, operating_income, net_income, ebitda
            FROM my_db.main.pwb_stocksincomestatement
            WHERE symbol = '{ticker.upper()}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        # Fetch balance sheet data
        df_balance = conn.execute(f"""
            SELECT symbol, date, total_assets, long_term_debt, short_long_term_debt_total,
                   cash_and_cash_equivalents_at_carrying_value, total_shareholder_equity,
                   common_stock_shares_outstanding
            FROM my_db.main.pwb_stocksbalancesheet
            WHERE symbol = '{ticker.upper()}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        # Fetch cashflow data
        df_cashflow = conn.execute(f"""
            SELECT symbol, date, operating_cashflow, capital_expenditures,
                   dividend_payout_common_stock, payments_for_repurchase_of_common_stock
            FROM my_db.main.pwb_stockscashflow
            WHERE symbol = '{ticker.upper()}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        if df_income.empty:
            conn.close()
            return None
        
        # Convert dates
        df_income['date'] = pd.to_datetime(df_income['date'])
        df_balance['date'] = pd.to_datetime(df_balance['date'])
        df_cashflow['date'] = pd.to_datetime(df_cashflow['date'])
        
        # Identify fiscal year-end
        df_income['month_day'] = df_income['date'].dt.strftime('%m-%d')
        fiscal_year_end = df_income['month_day'].mode()[0]
        
        # Filter to fiscal year-ends
        df_income_fy = df_income[df_income['month_day'] == fiscal_year_end].head(10).copy()
        df_balance_fy = df_balance[df_balance['date'].dt.strftime('%m-%d') == fiscal_year_end].head(10).copy()
        df_cashflow_fy = df_cashflow[df_cashflow['date'].dt.strftime('%m-%d') == fiscal_year_end].head(10).copy()
        
        # Get price data for each fiscal year
        dates_list = df_income_fy['date'].tolist()
        price_data = []
        
        for date in dates_list:
            query_price = f"""
            SELECT week_start_date, close
            FROM my_db.main.PWB_Allstocks_weekly
            WHERE Symbol = '{ticker.upper()}'
            AND week_start_date BETWEEN '{(date - pd.Timedelta(days=14)).strftime('%Y-%m-%d')}' 
                                    AND '{(date + pd.Timedelta(days=14)).strftime('%Y-%m-%d')}'
            ORDER BY week_start_date DESC
            LIMIT 1
            """
            price_row = conn.execute(query_price).df()
            
            if not price_row.empty:
                price_data.append({'date': date, 'price': price_row['close'].iloc[0]})
            else:
                price_data.append({'date': date, 'price': np.nan})
        
        conn.close()
        
        df_prices = pd.DataFrame(price_data)
        
        # Merge all data
        df_merged = df_income_fy[['date', 'total_revenue', 'net_income', 'ebitda', 'ebit']].copy()
        
        df_merged = df_merged.merge(
            df_balance_fy[['date', 'short_long_term_debt_total', 'cash_and_cash_equivalents_at_carrying_value',
                           'total_shareholder_equity', 'common_stock_shares_outstanding']],
            on='date', how='left'
        )
        
        df_merged = df_merged.merge(
            df_cashflow_fy[['date', 'operating_cashflow', 'capital_expenditures',
                            'dividend_payout_common_stock', 'payments_for_repurchase_of_common_stock']],
            on='date', how='left'
        )
        
        df_merged = df_merged.merge(df_prices, on='date', how='left')
        
        # Calculate metrics
        df_merged['shares'] = df_merged['common_stock_shares_outstanding'].fillna(1)
        df_merged['free_cash_flow'] = df_merged['operating_cashflow'] + df_merged['capital_expenditures']
        df_merged['market_cap'] = df_merged['price'] * df_merged['shares']
        
        # Per-share metrics
        df_merged['Revenue per Share'] = df_merged['total_revenue'] / df_merged['shares']
        df_merged['EBITDA per Share'] = df_merged['ebitda'] / df_merged['shares']
        df_merged['EBIT per Share'] = df_merged['ebit'] / df_merged['shares']
        df_merged['Earnings per Share'] = df_merged['net_income'] / df_merged['shares']
        df_merged['Owners Earnings per Share'] = df_merged['free_cash_flow'] / df_merged['shares']
        df_merged['Free Cash Flow per Share'] = df_merged['free_cash_flow'] / df_merged['shares']
        df_merged['Operating Cash Flow per Share'] = df_merged['operating_cashflow'] / df_merged['shares']
        df_merged['Cash per Share'] = df_merged['cash_and_cash_equivalents_at_carrying_value'] / df_merged['shares']
        df_merged['Dividends per Share'] = df_merged['dividend_payout_common_stock'] / df_merged['shares']
        df_merged['Book Value per Share'] = df_merged['total_shareholder_equity'] / df_merged['shares']
        df_merged['Tangible Book per Share'] = df_merged['total_shareholder_equity'] / df_merged['shares']
        df_merged['Total Debt per Share'] = df_merged['short_long_term_debt_total'] / df_merged['shares']
        
        # Yields
        df_merged['Buyback Ratio'] = (-df_merged['payments_for_repurchase_of_common_stock'] / df_merged['market_cap'] * 100).fillna(0)
        df_merged['Buyback Yield'] = (-df_merged['payments_for_repurchase_of_common_stock'] / df_merged['market_cap'] * 100).fillna(0)
        df_merged['Dividend Yield'] = (df_merged['dividend_payout_common_stock'] / df_merged['market_cap'] * 100).fillna(0)
        df_merged['Shareholders Yield'] = df_merged['Buyback Yield'] + df_merged['Dividend Yield']
        df_merged['Shares Outstanding'] = df_merged['shares']
        
        # Create year column
        df_merged['Year'] = df_merged['date'].dt.year
        
        # Select metrics
        metrics = [
            'Revenue per Share', 'EBITDA per Share', 'EBIT per Share', 'Earnings per Share',
            'Owners Earnings per Share', 'Free Cash Flow per Share', 'Operating Cash Flow per Share',
            'Cash per Share', 'Dividends per Share', 'Book Value per Share', 'Tangible Book per Share',
            'Total Debt per Share', 'Buyback Ratio', 'Buyback Yield', 'Dividend Yield',
            'Shareholders Yield', 'Shares Outstanding'
        ]
        
        # Pivot: Years as columns, metrics as rows
        df_pivot = df_merged.set_index('Year')[metrics].T
        df_pivot = df_pivot[sorted(df_pivot.columns, reverse=True)]
        df_pivot = df_pivot.reset_index()
        df_pivot = df_pivot.rename(columns={'index': 'Metric'})
        
        return df_pivot
        
    except Exception as e:
        st.error(f"Error fetching per share data: {str(e)}")
        return None

# Header with logo and title
col1, col2 = st.columns([1, 4])
with col1:
    try:
        logo = Image.open("jcn_logo.jpg")
        st.image(logo, width=150)
    except:
        st.write("")

with col2:
    st.title("📈 Stock Analysis")
    st.markdown("Individual stock research and analysis tools")

st.markdown("---")

# Ticker Input Section
st.subheader("🔍 Enter Stock Ticker")

col1, col2, col3 = st.columns([2, 1, 3])

with col1:
    ticker_input = st.text_input(
        "Ticker Symbol",
        value="NVDA",
        max_chars=10,
        help="Enter a stock ticker symbol (e.g., NVDA, AAPL, MSFT)",
        key="ticker_input"
    ).upper()

with col2:
    st.write("")  # Spacing
    st.write("")  # Spacing
    analyze_button = st.button("🔎 Analyze", type="primary", use_container_width=True)

# Store ticker in session state
if analyze_button or 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = ticker_input

# Get current ticker
current_ticker = st.session_state.get('current_ticker', 'NVDA')

st.markdown("---")

# Fetch and display stock info
if current_ticker:
    with st.spinner(f"Loading data for {current_ticker}..."):
        stock_info = get_stock_info_from_motherduck(current_ticker)
    
    if stock_info:
        # Display stock header info
        st.markdown(f"**{stock_info['sector']}** • **{stock_info['industry']}**")
        
        # Company name and ticker
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"# {stock_info['company']}")
            st.markdown(f"**{stock_info['ticker']}** 🇺🇸 NASDAQ Global Select")
        
        # Current price with styling
        st.markdown("##")  # Spacing
        
        price_col1, price_col2 = st.columns([1, 3])
        with price_col1:
            st.markdown(f"<h1 style='color: #1f77b4; margin: 0;'>${stock_info['current_price']:.2f}</h1>", 
                       unsafe_allow_html=True)
            st.caption(f"Last updated: {stock_info['last_updated']}")
        
        st.markdown("---")
        
        # Per Share Data Section
        st.subheader("📊 Per Share Data")
        
        with st.spinner("Loading 10-year fiscal year data..."):
            per_share_df = get_per_share_data(current_ticker)
        
        if per_share_df is not None and not per_share_df.empty:
            # Format the dataframe for display
            display_df = per_share_df.copy()
            
            # Format numeric columns to 2 decimal places
            for col in display_df.columns:
                if col != 'Metric':
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
            
            # Display the table
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            st.caption("💡 Data sourced from MotherDuck: pwb_stocksincomestatement, pwb_stocksbalancesheet, pwb_stockscashflow, PWB_Allstocks_weekly")
        else:
            st.warning(f"⚠️ No fiscal year data available for {current_ticker}")
        
        st.markdown("---")
        
        # Placeholder for additional modules
        st.info("📊 Additional analysis modules will be added below")
        
    else:
        st.error(f"❌ No data found for ticker '{current_ticker}' in MotherDuck database.")
        st.info("💡 Make sure the ticker exists in the GuruFocusData table.")
else:
    st.info("👆 Enter a stock ticker above to begin analysis")

st.markdown("---")
st.caption("JCN Financial & Tax Advisory Group, LLC - Built with Streamlit")
