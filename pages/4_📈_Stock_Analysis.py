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

def get_quality_metrics(ticker):
    """Get 10-year fiscal year quality metrics and ratios from MotherDuck"""
    try:
        conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
        
        # Fetch income statement data
        df_income = conn.execute(f"""
            SELECT symbol, date, total_revenue, gross_profit, operating_income, net_income, ebitda,
                   cost_of_revenue, research_and_development, selling_general_and_administrative
            FROM my_db.main.pwb_stocksincomestatement
            WHERE symbol = '{ticker.upper()}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        # Fetch balance sheet data
        df_balance = conn.execute(f"""
            SELECT symbol, date, total_assets, total_liabilities, total_shareholder_equity,
                   short_long_term_debt_total, total_current_assets, total_current_liabilities,
                   cash_and_cash_equivalents_at_carrying_value, inventory,
                   common_stock_shares_outstanding
            FROM my_db.main.pwb_stocksbalancesheet
            WHERE symbol = '{ticker.upper()}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        # Fetch cashflow data
        df_cashflow = conn.execute(f"""
            SELECT symbol, date, operating_cashflow, capital_expenditures
            FROM my_db.main.pwb_stockscashflow
            WHERE symbol = '{ticker.upper()}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        conn.close()
        
        if df_income.empty:
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
        
        # Merge all data
        df_merged = df_income_fy.copy()
        
        df_merged = df_merged.merge(
            df_balance_fy[['date', 'total_assets', 'total_liabilities', 'total_shareholder_equity',
                           'short_long_term_debt_total', 'total_current_assets', 'total_current_liabilities',
                           'cash_and_cash_equivalents_at_carrying_value', 'inventory']],
            on='date', how='left'
        )
        
        df_merged = df_merged.merge(
            df_cashflow_fy[['date', 'operating_cashflow', 'capital_expenditures']],
            on='date', how='left'
        )
        
        # Calculate Free Cash Flow
        df_merged['free_cash_flow'] = df_merged['operating_cashflow'] + df_merged['capital_expenditures']
        
        # Calculate all ratios
        df_merged['Net Income'] = df_merged['net_income']
        df_merged['Gross Margin %'] = (df_merged['gross_profit'] / df_merged['total_revenue'] * 100).fillna(0)
        df_merged['Operating Margin %'] = (df_merged['operating_income'] / df_merged['total_revenue'] * 100).fillna(0)
        df_merged['Net Margin %'] = (df_merged['net_income'] / df_merged['total_revenue'] * 100).fillna(0)
        df_merged['EBITA Margin %'] = (df_merged['ebitda'] / df_merged['total_revenue'] * 100).fillna(0)
        df_merged['FCF Margin %'] = (df_merged['free_cash_flow'] / df_merged['total_revenue'] * 100).fillna(0)
        
        # Return ratios
        df_merged['ROIC %'] = (df_merged['net_income'] / (df_merged['total_shareholder_equity'] + df_merged['short_long_term_debt_total']) * 100).fillna(0)
        df_merged['ROC %'] = (df_merged['ebitda'] / (df_merged['total_shareholder_equity'] + df_merged['short_long_term_debt_total']) * 100).fillna(0)
        df_merged['ROCE %'] = (df_merged['operating_income'] / (df_merged['total_assets'] - df_merged['total_current_liabilities']) * 100).fillna(0)
        df_merged['ROE %'] = (df_merged['net_income'] / df_merged['total_shareholder_equity'] * 100).fillna(0)
        df_merged['ROA %'] = (df_merged['net_income'] / df_merged['total_assets'] * 100).fillna(0)
        
        # Leverage ratios
        df_merged['Debt to Equity'] = (df_merged['short_long_term_debt_total'] / df_merged['total_shareholder_equity']).fillna(0)
        df_merged['Debt to Asset'] = (df_merged['short_long_term_debt_total'] / df_merged['total_assets']).fillna(0)
        df_merged['Gross Profit to Asset'] = (df_merged['gross_profit'] / df_merged['total_assets']).fillna(0)
        
        # Turnover ratios
        df_merged['Asset Turnover'] = (df_merged['total_revenue'] / df_merged['total_assets']).fillna(0)
        df_merged['Cash Conversion Cycle'] = 0  # Requires more detailed data (DSO + DIO - DPO)
        df_merged['COGS to Revenue'] = (df_merged['cost_of_revenue'] / df_merged['total_revenue'] * 100).fillna(0)
        df_merged['Inventory to Revenue'] = (df_merged['inventory'] / df_merged['total_revenue'] * 100).fillna(0)
        df_merged['CAPEX to Revenue'] = (-df_merged['capital_expenditures'] / df_merged['total_revenue'] * 100).fillna(0)
        
        # Liquidity ratios
        df_merged['Current Ratio'] = (df_merged['total_current_assets'] / df_merged['total_current_liabilities']).fillna(0)
        df_merged['Quick Ratio'] = ((df_merged['total_current_assets'] - df_merged['inventory']) / df_merged['total_current_liabilities']).fillna(0)
        df_merged['Cash Ratio'] = (df_merged['cash_and_cash_equivalents_at_carrying_value'] / df_merged['total_current_liabilities']).fillna(0)
        
        # Create year column
        df_merged['Year'] = df_merged['date'].dt.year
        
        # Select metrics
        metrics = [
            'Gross Margin %',
            'Operating Margin %',
            'Net Margin %',
            'EBITA Margin %',
            'FCF Margin %',
            'ROIC %',
            'ROC %',
            'ROCE %',
            'ROE %',
            'ROA %',
            'Debt to Equity',
            'Debt to Asset',
            'Gross Profit to Asset',
            'Asset Turnover',
            'Cash Conversion Cycle',
            'COGS to Revenue',
            'Inventory to Revenue',
            'CAPEX to Revenue',
            'Current Ratio',
            'Quick Ratio',
            'Cash Ratio'
        ]
        
        # Pivot: Years as columns, metrics as rows
        df_pivot = df_merged.set_index('Year')[metrics].T
        df_pivot = df_pivot[sorted(df_pivot.columns, reverse=True)]
        df_pivot = df_pivot.reset_index()
        df_pivot = df_pivot.rename(columns={'index': 'Metric'})
        
        return df_pivot
        
    except Exception as e:
        st.error(f"Error fetching quality metrics: {str(e)}")
        return None

def get_income_statement(ticker):
    """Get 10-year Income Statement data from MotherDuck with hierarchical structure"""
    try:
        conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
        
        # Fetch income statement data with all necessary fields
        df_income = conn.execute(f"""
            SELECT symbol, date, total_revenue, cost_of_revenue, gross_profit,
                   operating_expenses, research_and_development, 
                   selling_general_and_administrative,
                   operating_income, interest_expense, interest_income,
                   other_non_operating_income, income_before_tax,
                   income_tax_expense, net_income, ebitda
            FROM my_db.main.pwb_stocksincomestatement
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        # Fetch balance sheet for shares outstanding
        df_balance = conn.execute(f"""
            SELECT symbol, date, common_stock_shares_outstanding
            FROM my_db.main.pwb_stocksbalancesheet
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        # Fetch earnings for EPS
        df_earnings = conn.execute(f"""
            SELECT symbol, date, reported_eps
            FROM my_db.main.pwb_stocksearnings
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        conn.close()
        
        if df_income.empty:
            return None
        
        # Convert dates
        df_income['date'] = pd.to_datetime(df_income['date'])
        df_balance['date'] = pd.to_datetime(df_balance['date'])
        df_earnings['date'] = pd.to_datetime(df_earnings['date'])
        
        # Identify fiscal year-end
        df_income['month_day'] = df_income['date'].dt.strftime('%m-%d')
        fiscal_year_end = df_income['month_day'].mode()[0]
        
        # Filter to fiscal year-ends
        df_income_fy = df_income[df_income['month_day'] == fiscal_year_end].head(10).copy()
        df_balance_fy = df_balance[df_balance['date'].dt.strftime('%m-%d') == fiscal_year_end].head(10).copy()
        df_earnings_fy = df_earnings[df_earnings['date'].dt.strftime('%m-%d') == fiscal_year_end].head(10).copy()
        
        # Merge data
        df_merged = df_income_fy.copy()
        df_merged = df_merged.merge(
            df_balance_fy[['date', 'common_stock_shares_outstanding']],
            on='date', how='left'
        )
        df_merged = df_merged.merge(
            df_earnings_fy[['date', 'reported_eps']],
            on='date', how='left'
        )
        
        # Calculate derived metrics
        df_merged['gross_margin'] = (df_merged['gross_profit'] / df_merged['total_revenue'] * 100).fillna(0)
        df_merged['operating_margin'] = (df_merged['operating_income'] / df_merged['total_revenue'] * 100).fillna(0)
        df_merged['net_margin'] = (df_merged['net_income'] / df_merged['total_revenue'] * 100).fillna(0)
        
        # Calculate EPS if not available
        if df_merged['reported_eps'].isna().all() and not df_merged['common_stock_shares_outstanding'].isna().all():
            df_merged['calculated_eps'] = (df_merged['net_income'] / df_merged['common_stock_shares_outstanding']).fillna(0)
        else:
            df_merged['calculated_eps'] = df_merged['reported_eps']
        
        # Create year column
        df_merged['Year'] = df_merged['date'].dt.year
        
        # Define hierarchical structure
        income_statement_structure = [
            # Total Revenue (parent)
            ('Total Revenue', 'total_revenue', True, None),
            ('Cost of Goods Sold', 'cost_of_revenue', False, 'Total Revenue'),
            
            # Gross Profit (parent)
            ('Gross Profit', 'gross_profit', True, None),
            ('Gross Margin %', 'gross_margin', False, 'Gross Profit'),
            ('Selling, General, Admin Expenses', 'selling_general_and_administrative', False, 'Gross Profit'),
            ('R & D Expenses', 'research_and_development', False, 'Gross Profit'),
            
            # Total Operating Expenses (parent)
            ('Total Operating Expenses', 'operating_expenses', True, None),
            
            # Operating Income (parent)
            ('Operating Income', 'operating_income', True, None),
            ('Operating Margin %', 'operating_margin', False, 'Operating Income'),
            ('Interest Expense', 'interest_expense', False, 'Operating Income'),
            ('Interest Income', 'interest_income', False, 'Operating Income'),
            ('Other Expenses', 'other_non_operating_income', False, 'Operating Income'),
            ('Income Before Tax', 'income_before_tax', False, 'Operating Income'),
            ('Income Tax', 'income_tax_expense', False, 'Operating Income'),
            
            # Net Income (parent)
            ('Net Income', 'net_income', True, None),
            ('Net Margin %', 'net_margin', False, 'Net Income'),
            ('Weighted Avg. Shares Out - Basic', 'common_stock_shares_outstanding', False, 'Net Income'),
            ('Weighted Avg. Shares Out - Diluted', 'common_stock_shares_outstanding', False, 'Net Income'),
            ('Basic EPS', 'calculated_eps', False, 'Net Income'),
            ('EPS Diluted', 'calculated_eps', False, 'Net Income'),
            
            # EBITDA (parent)
            ('EBITDA', 'ebitda', True, None),
        ]
        
        # Build hierarchical data structure
        years = sorted(df_merged['Year'].unique(), reverse=True)
        
        # Group items by parent
        hierarchy = {}
        for display_name, col_name, is_parent, parent_name in income_statement_structure:
            if is_parent:
                hierarchy[display_name] = {
                    'data': {},
                    'children': []
                }
                # Get parent data
                for year in years:
                    year_data = df_merged[df_merged['Year'] == year]
                    if not year_data.empty and col_name in year_data.columns:
                        hierarchy[display_name]['data'][year] = year_data[col_name].iloc[0]
                    else:
                        hierarchy[display_name]['data'][year] = np.nan
            else:
                # Add as child to parent
                if parent_name in hierarchy:
                    child_data = {}
                    for year in years:
                        year_data = df_merged[df_merged['Year'] == year]
                        if not year_data.empty and col_name in year_data.columns:
                            child_data[year] = year_data[col_name].iloc[0]
                        else:
                            child_data[year] = np.nan
                    hierarchy[parent_name]['children'].append({
                        'name': display_name,
                        'data': child_data
                    })
        
        return {
            'hierarchy': hierarchy,
            'years': years
        }
        
    except Exception as e:
        st.error(f"Error fetching income statement: {str(e)}")
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
        
        # Quality Metrics Section
        st.subheader("🎯 Quality Metrics")
        
        with st.spinner("Loading 10-year quality metrics..."):
            quality_df = get_quality_metrics(current_ticker)
        
        if quality_df is not None and not quality_df.empty:
            # Format the dataframe for display
            display_df_quality = quality_df.copy()
            
            # Format numeric columns to 2 decimal places
            for col in display_df_quality.columns:
                if col != 'Metric':
                    display_df_quality[col] = display_df_quality[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
            
            # Display the table
            st.dataframe(
                display_df_quality,
                use_container_width=True,
                hide_index=True,
                height=800  # Show all 21 rows without scrolling
            )
            
            st.caption("💡 Data sourced from MotherDuck: pwb_stocksincomestatement, pwb_stocksbalancesheet, pwb_stockscashflow")
        else:
            st.warning(f"⚠️ No quality metrics data available for {current_ticker}")
        
        st.markdown("---")
        
        # Income Statement Section
        st.subheader("📊 Income Statement")
        
        with st.spinner("Loading 10-year income statement..."):
            income_data = get_income_statement(current_ticker)
        
        if income_data and income_data['hierarchy']:
            hierarchy = income_data['hierarchy']
            years = income_data['years']
            
            # Initialize session state for expanded parents
            if 'expanded_parents' not in st.session_state:
                st.session_state.expanded_parents = set()
            
            # Build all rows for the unified table
            all_rows = []
            
            for parent_name, parent_info in hierarchy.items():
                # Add parent row with inline arrow
                is_expanded = parent_name in st.session_state.expanded_parents
                arrow = "▼" if is_expanded else "▶"
                parent_row = {'Metric': f"{arrow} {parent_name}", 'is_parent': True, 'parent_name': parent_name}
                for year in years:
                    value = parent_info['data'].get(year, np.nan)
                    if pd.notna(value):
                        if 'Margin' in parent_name or 'EPS' in parent_name:
                            parent_row[year] = f"{value:.2f}"
                        elif abs(value) >= 1e9:
                            parent_row[year] = f"{value/1e9:.2f}B"
                        elif abs(value) >= 1e6:
                            parent_row[year] = f"{value/1e6:.2f}M"
                        else:
                            parent_row[year] = f"{value:.2f}"
                    else:
                        parent_row[year] = "N/A"
                all_rows.append(parent_row)
                
                # Add children rows if parent is expanded
                if parent_name in st.session_state.expanded_parents:
                    for child in parent_info['children']:
                        child_row = {'Metric': f"    {child['name']}", 'is_parent': False, 'parent_name': parent_name}
                        for year in years:
                            value = child['data'].get(year, np.nan)
                            if pd.notna(value):
                                if '%' in child['name'] or 'EPS' in child['name']:
                                    child_row[year] = f"{value:.2f}"
                                elif 'Shares' in child['name']:
                                    child_row[year] = f"{value/1e9:.2f}B" if value >= 1e9 else f"{value/1e6:.2f}M"
                                elif abs(value) >= 1e9:
                                    child_row[year] = f"{value/1e9:.2f}B"
                                elif abs(value) >= 1e6:
                                    child_row[year] = f"{value/1e6:.2f}M"
                                else:
                                    child_row[year] = f"{value:.2f}"
                            else:
                                child_row[year] = "N/A"
                        all_rows.append(child_row)
            
            # Create compact toggle buttons
            parent_names = list(hierarchy.keys())
            button_cols = st.columns(len(parent_names))
            
            for idx, parent_name in enumerate(parent_names):
                with button_cols[idx]:
                    is_expanded = parent_name in st.session_state.expanded_parents
                    arrow = "▼" if is_expanded else "▶"
                    # Compact button with just arrow
                    if st.button(f"{arrow}", key=f"toggle_{parent_name}", help=parent_name):
                        if parent_name in st.session_state.expanded_parents:
                            st.session_state.expanded_parents.remove(parent_name)
                        else:
                            st.session_state.expanded_parents.add(parent_name)
                        st.rerun()
            
            # Create and display unified dataframe
            df_income_display = pd.DataFrame(all_rows)
            display_cols = ['Metric'] + years
            df_income_display = df_income_display[display_cols]
            
            st.dataframe(
                df_income_display,
                use_container_width=True,
                hide_index=True,
                height=min(800, len(all_rows) * 35 + 50)
            )
            
            st.caption("💡 Data sourced from MotherDuck: pwb_stocksincomestatement, pwb_stocksbalancesheet, pwb_stocksearnings")
        else:
            st.warning(f"⚠️ No income statement data available for {current_ticker}")
        
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
