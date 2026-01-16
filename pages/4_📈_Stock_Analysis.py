import streamlit as st
from PIL import Image
import duckdb
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

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

# Financial Overview Grid Helper Functions
def calculate_cagr(start_value, end_value, periods):
    """Calculate Compound Annual Growth Rate"""
    if start_value <= 0 or end_value <= 0 or periods <= 0:
        return np.nan
    return ((end_value / start_value) ** (1 / periods) - 1) * 100

def count_consecutive_higher(values):
    """Count how many years show consecutively higher values"""
    if len(values) < 2:
        return 0
    count = 0
    for i in range(1, len(values)):
        if values[i] > values[i-1]:
            count += 1
    return count

def classify_trend(cagr_selected, cagr_1yr, cagr_3yr, cagr_5yr):
    """
    Classify trend based on CAGR of selected period and acceleration check
    Returns list of classifications (can be multiple)
    """
    classifications = []
    
    # Time-period dependent classification
    if cagr_selected < 0:
        classifications.append("Declining 📉")
    elif 0 <= cagr_selected < 10:
        classifications.append("Stable ➡️")
    elif 10 <= cagr_selected <= 20:
        classifications.append("Growing 📈")
    elif cagr_selected > 20:
        classifications.append("Growing 📈")  # Strong growth still counts as growing
    
    # Acceleration check (independent of timeframe)
    if pd.notna(cagr_1yr) and pd.notna(cagr_3yr) and pd.notna(cagr_5yr):
        if cagr_1yr > cagr_3yr and cagr_3yr > cagr_5yr:
            classifications.append("Accelerating 🚀")
    
    return ", ".join(classifications) if classifications else "N/A"

def create_financial_overview_grid(ticker, time_period='10yr'):
    """Create 2x2 grid of financial charts with CAGR and trend analysis"""
    try:
        conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
        
        # Determine time window
        end_date = datetime.now()
        if time_period == '1yr':
            start_date = end_date - timedelta(days=365)
            years_back = 1
        elif time_period == '3yr':
            start_date = end_date - timedelta(days=365*3)
            years_back = 3
        elif time_period == '5yr':
            start_date = end_date - timedelta(days=365*5)
            years_back = 5
        elif time_period == '10yr':
            start_date = end_date - timedelta(days=365*10)
            years_back = 10
        elif time_period == '20yr':
            start_date = end_date - timedelta(days=365*20)
            years_back = 20
        else:
            start_date = end_date - timedelta(days=365*10)
            years_back = 10
        
        # Fetch stock prices
        df_prices = conn.execute(f"""
            SELECT date, close as price
            FROM my_db.main.pwb_allstocks
            WHERE symbol = '{ticker.upper()}' AND date >= '{start_date.strftime('%Y-%m-%d')}'
            ORDER BY date
        """).df()
        
        # Fetch SPY prices
        df_spy = conn.execute(f"""
            SELECT date, close as price
            FROM my_db.main.pwb_allETFs
            WHERE symbol = 'SPY' AND date >= '{start_date.strftime('%Y-%m-%d')}'
            ORDER BY date
        """).df()
        
        # Fetch income statement data
        df_income = conn.execute(f"""
            SELECT date as fiscal_year_end, total_revenue, ebitda
            FROM my_db.main.pwb_stocksincomestatement
            WHERE symbol = '{ticker.upper()}' AND date >= '{start_date.strftime('%Y-%m-%d')}'
            ORDER BY date
        """).df()
        
        # Fetch balance sheet data for shares outstanding
        df_balance = conn.execute(f"""
            SELECT date as fiscal_year_end, common_stock_shares_outstanding
            FROM my_db.main.pwb_stocksbalancesheet
            WHERE symbol = '{ticker.upper()}' AND date >= '{start_date.strftime('%Y-%m-%d')}'
            ORDER BY date
        """).df()
        
        # Fetch cash flow data
        df_cashflow = conn.execute(f"""
            SELECT date as fiscal_year_end, operating_cashflow, capital_expenditures
            FROM my_db.main.pwb_stockscashflow
            WHERE symbol = '{ticker.upper()}' AND date >= '{start_date.strftime('%Y-%m-%d')}'
            ORDER BY date
        """).df()
        
        conn.close()
        
        # Merge all data sources
        df_metrics = df_income.merge(df_balance, on='fiscal_year_end', how='left')
        df_metrics = df_metrics.merge(df_cashflow, on='fiscal_year_end', how='left')
        
        # Calculate free cash flow (operating cashflow + capex, where capex is negative)
        df_metrics['free_cash_flow'] = df_metrics['operating_cashflow'] + df_metrics['capital_expenditures']
        
        # Calculate per-share metrics
        df_metrics['revenue_per_share'] = df_metrics['total_revenue'] / df_metrics['common_stock_shares_outstanding']
        df_metrics['ebitda_per_share'] = df_metrics['ebitda'] / df_metrics['common_stock_shares_outstanding']
        df_metrics['fcf_per_share'] = df_metrics['free_cash_flow'] / df_metrics['common_stock_shares_outstanding']
        
        # Create 2x2 subplot grid
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Stock Price', 'Revenue per Share', 
                           'EBITDA per Share', 'Free Cash Flow per Share'),
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # Chart 1: Stock Price (line chart with SPY comparison)
        if not df_prices.empty and not df_spy.empty:
            df_prices['date'] = pd.to_datetime(df_prices['date'])
            df_spy['date'] = pd.to_datetime(df_spy['date'])
            
            # Normalize both to 1.0 at start (like reference chart)
            stock_normalized = df_prices['price'] / df_prices['price'].iloc[0]
            spy_normalized = df_spy['price'] / df_spy['price'].iloc[0]
            
            # Add SPY first (gray line, behind)
            fig.add_trace(
                go.Scatter(x=df_spy['date'], y=spy_normalized,
                          name='SPY', line=dict(color='#808080', width=2),
                          mode='lines'),
                row=1, col=1
            )
            # Add stock second (red line, in front)
            fig.add_trace(
                go.Scatter(x=df_prices['date'], y=stock_normalized,
                          name=ticker, line=dict(color='#FF4444', width=2),
                          mode='lines'),
                row=1, col=1
            )
            
            # Calculate CAGR for stock price
            years = (df_prices['date'].max() - df_prices['date'].min()).days / 365.25
            cagr = calculate_cagr(df_prices['price'].iloc[0], df_prices['price'].iloc[-1], years)
            
            fig.add_annotation(
                text=f"<b>CAGR: {cagr:.1f}%</b>",
                xref="x", yref="y",
                x=df_prices['date'].min(), y=stock_normalized.max() * 0.9,
                showarrow=False,
                bgcolor="white",
                bordercolor="black",
                borderwidth=1,
                font=dict(size=10),
                align="left",
                row=1, col=1
            )
        
        # Charts 2-4: Bar charts for per-share metrics
        metrics_to_plot = [
            ('revenue_per_share', 'Revenue per Share', '#ff7f0e', 1, 2),
            ('ebitda_per_share', 'EBITDA per Share', '#17becf', 2, 1),
            ('fcf_per_share', 'Free Cash Flow per Share', '#9467bd', 2, 2)
        ]
        
        for metric_col, title, color, row, col in metrics_to_plot:
            if metric_col in df_metrics.columns:
                df_plot = df_metrics[['fiscal_year_end', metric_col]].dropna()
                df_plot['fiscal_year_end'] = pd.to_datetime(df_plot['fiscal_year_end'])
                
                if not df_plot.empty and len(df_plot) >= 2:
                    fig.add_trace(
                        go.Bar(x=df_plot['fiscal_year_end'], y=df_plot[metric_col],
                              name=title, marker_color=color, showlegend=False),
                        row=row, col=col
                    )
                    
                    # Calculate CAGRs
                    values = df_plot[metric_col].values
                    years_data = len(values) - 1
                    
                    cagr_period = calculate_cagr(values[0], values[-1], years_data)
                    cagr_1yr = calculate_cagr(values[-2], values[-1], 1) if len(values) >= 2 else np.nan
                    cagr_3yr = calculate_cagr(values[-4], values[-1], 3) if len(values) >= 4 else np.nan
                    cagr_5yr = calculate_cagr(values[-6], values[-1], 5) if len(values) >= 6 else np.nan
                    cagr_10yr = calculate_cagr(values[0], values[-1], min(10, years_data)) if len(values) >= 2 else np.nan
                    
                    consecutive = count_consecutive_higher(values)
                    classification = classify_trend(cagr_period, cagr_1yr, cagr_3yr, cagr_5yr)
                    
                    # Build annotation text
                    annotation_lines = [f"<b>CAGR: {cagr_period:.1f}%</b>"]
                    if pd.notna(cagr_1yr):
                        annotation_lines.append(f"1yr: {cagr_1yr:.1f}%")
                    if pd.notna(cagr_3yr):
                        annotation_lines.append(f"3yr: {cagr_3yr:.1f}%")
                    if pd.notna(cagr_5yr):
                        annotation_lines.append(f"5yr: {cagr_5yr:.1f}%")
                    if pd.notna(cagr_10yr):
                        annotation_lines.append(f"10yr: {cagr_10yr:.1f}%")
                    annotation_lines.append(f"{consecutive}/{years_data} yrs higher")
                    annotation_lines.append(f"<b>{classification}</b>")
                    
                    annotation_text = "<br>".join(annotation_lines)
                    
                    fig.add_annotation(
                        text=annotation_text,
                        xref=f"x{col + (row-1)*2}", yref=f"y{col + (row-1)*2}",
                        x=df_plot['fiscal_year_end'].min(), y=df_plot[metric_col].max() * 0.85,
                        showarrow=False,
                        bgcolor="white",
                        bordercolor="black",
                        borderwidth=1,
                        font=dict(size=9),
                        align="left",
                        row=row, col=col
                    )
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text=f"{ticker} - {time_period.upper()} Financial Overview",
            title_x=0.5,
            title_font=dict(size=20)
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='lightgray')
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating financial overview grid: {str(e)}")
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

def get_balance_sheet(ticker):
    """Get 10-year Balance Sheet data from MotherDuck with hierarchical structure"""
    try:
        conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
        
        # Fetch comprehensive balance sheet data (using verified column names)
        df_balance = conn.execute(f"""
            SELECT symbol, date,
                   cash_and_cash_equivalents_at_carrying_value,
                   short_term_investments,
                   total_current_assets,
                   current_net_receivables,
                   inventory,
                   other_current_assets,
                   other_non_current_assets,
                   property_plant_equipment,
                   long_term_investments,
                   goodwill,
                   intangible_assets,
                   total_non_current_assets,
                   total_assets,
                   current_accounts_payable,
                   other_current_liabilities,
                   short_term_debt,
                   deferred_revenue,
                   total_current_liabilities,
                   long_term_debt,
                   other_non_current_liabilities,
                   total_non_current_liabilities,
                   capital_lease_obligations,
                   total_liabilities,
                   common_stock,
                   retained_earnings,
                   treasury_stock,
                   total_shareholder_equity,
                   common_stock_shares_outstanding
            FROM my_db.main.pwb_stocksbalancesheet
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        conn.close()
        
        if df_balance.empty:
            return None
        
        # Convert dates
        df_balance['date'] = pd.to_datetime(df_balance['date'])
        
        # Identify fiscal year-end
        df_balance['month_day'] = df_balance['date'].dt.strftime('%m-%d')
        fiscal_year_end = df_balance['month_day'].mode()[0]
        
        # Filter to fiscal year-ends
        df_balance_fy = df_balance[df_balance['month_day'] == fiscal_year_end].head(10).copy()
        
        # Create year column
        df_balance_fy['Year'] = df_balance_fy['date'].dt.year
        
        # Define hierarchical structure matching reference image
        balance_sheet_structure = [
            # Assets Section
            # Cash & Short Term Investments (parent)
            ('Cash & Short Term Investments', 'calculated_cash_short_term', True, None),
            ('Cash & Cash Equivalents', 'cash_and_cash_equivalents_at_carrying_value', False, 'Cash & Short Term Investments'),
            ('Short Term Investments', 'short_term_investments', False, 'Cash & Short Term Investments'),
            
            # Current Assets (parent)
            ('Current Assets', 'total_current_assets', True, None),
            ('Total Receivables', 'current_net_receivables', False, 'Current Assets'),
            ('Total Inventory', 'inventory', False, 'Current Assets'),
            ('Other Current Assets', 'other_current_assets', False, 'Current Assets'),
            
            # Noncurrent Assets (parent)
            ('Noncurrent Assets', 'total_non_current_assets', True, None),
            ('Other Noncurrent Assets', 'other_non_current_assets', False, 'Noncurrent Assets'),
            ('Net Property, Plant & Equipment', 'property_plant_equipment', False, 'Noncurrent Assets'),
            ('Long Term Investments', 'long_term_investments', False, 'Noncurrent Assets'),
            ('Goodwill', 'goodwill', False, 'Noncurrent Assets'),
            ('Intangible Assets', 'intangible_assets', False, 'Noncurrent Assets'),
            
            # TOTAL ASSETS (parent)
            ('TOTAL ASSETS', 'total_assets', True, None),
            
            # Liabilities & Shareholders' Equity Section
            # Current Liabilities (parent)
            ('Current Liabilities', 'total_current_liabilities', True, None),
            ('Accounts Payable', 'current_accounts_payable', False, 'Current Liabilities'),
            ('Other Current Liabilities', 'other_current_liabilities', False, 'Current Liabilities'),
            ('Short Term Debt', 'short_term_debt', False, 'Current Liabilities'),
            ('Deferred Revenue', 'deferred_revenue', False, 'Current Liabilities'),
            
            # Noncurrent Liabilities (parent)
            ('Noncurrent Liabilities', 'total_non_current_liabilities', True, None),
            ('Long Term Debt', 'long_term_debt', False, 'Noncurrent Liabilities'),
            ('Other Noncurrent Liabilities', 'other_non_current_liabilities', False, 'Noncurrent Liabilities'),
            
            # Other Liabilities (parent)
            ('Other Liabilities', 'capital_lease_obligations', True, None),
            ('Capital Lease Obligations', 'capital_lease_obligations', False, 'Other Liabilities'),
            
            # TOTAL LIABILITIES (parent)
            ('TOTAL LIABILITIES', 'total_liabilities', True, None),
            
            # Shareholders' Equity (parent)
            ('Shareholders\' Equity', 'total_shareholder_equity', True, None),
            ('Common Stock', 'common_stock', False, 'Shareholders\' Equity'),
            ('Retained Earnings', 'retained_earnings', False, 'Shareholders\' Equity'),
            ('Treasury Stock', 'treasury_stock', False, 'Shareholders\' Equity'),
        ]
        
        # Calculate Cash & Short Term Investments total
        df_balance_fy['calculated_cash_short_term'] = (
            df_balance_fy['cash_and_cash_equivalents_at_carrying_value'].fillna(0) + 
            df_balance_fy['short_term_investments'].fillna(0)
        )
        
        # Build hierarchical data structure
        years = sorted(df_balance_fy['Year'].unique(), reverse=True)
        
        # Group items by parent
        hierarchy = {}
        for display_name, col_name, is_parent, parent_name in balance_sheet_structure:
            if is_parent:
                hierarchy[display_name] = {
                    'data': {},
                    'children': []
                }
                # Get parent data
                for year in years:
                    year_data = df_balance_fy[df_balance_fy['Year'] == year]
                    if not year_data.empty and col_name in year_data.columns:
                        hierarchy[display_name]['data'][year] = year_data[col_name].iloc[0]
                    else:
                        hierarchy[display_name]['data'][year] = np.nan
            else:
                # Add as child to parent
                if parent_name in hierarchy:
                    child_data = {}
                    for year in years:
                        year_data = df_balance_fy[df_balance_fy['Year'] == year]
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
        st.error(f"Error fetching balance sheet: {str(e)}")
        return None

def get_cash_flows(ticker):
    """Get 10-year Cash Flows data from MotherDuck with hierarchical structure"""
    try:
        conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
        
        # Fetch cash flow data (only columns with consistent data)
        df_cashflow = conn.execute(f"""
            SELECT symbol, date,
                   net_income,
                   depreciation_depletion_and_amortization,
                   change_in_inventory,
                   operating_cashflow,
                   capital_expenditures,
                   cashflow_from_investment,
                   dividend_payout_common_stock,
                   proceeds_from_repurchase_of_equity,
                   cashflow_from_financing
            FROM my_db.main.pwb_stockscashflow
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        conn.close()
        
        if df_cashflow.empty:
            return None
        
        # Convert dates
        df_cashflow['date'] = pd.to_datetime(df_cashflow['date'])
        
        # Identify fiscal year-end
        df_cashflow['month_day'] = df_cashflow['date'].dt.strftime('%m-%d')
        fiscal_year_end = df_cashflow['month_day'].mode()[0]
        
        # Filter to fiscal year-ends
        df_cashflow_fy = df_cashflow[df_cashflow['month_day'] == fiscal_year_end].head(10).copy()
        
        # Create year column
        df_cashflow_fy['Year'] = df_cashflow_fy['date'].dt.year
        
        # Calculate Free Cash Flow
        df_cashflow_fy['free_cash_flow'] = (
            df_cashflow_fy['operating_cashflow'] + 
            df_cashflow_fy['capital_expenditures']
        )
        
        # Define hierarchical structure with available data
        # Format: (display_name, column_name, is_parent, parent_name)
        cash_flow_structure = [
            # Operations (parent)
            ('Cash from Operations', 'operating_cashflow', True, None),
            ('Net Income', 'net_income', False, 'Cash from Operations'),
            ('Depreciation & Amortization', 'depreciation_depletion_and_amortization', False, 'Cash from Operations'),
            ('Change in Inventory', 'change_in_inventory', False, 'Cash from Operations'),
            
            # Investing (parent)
            ('Cash From Investing', 'cashflow_from_investment', True, None),
            ('Capital Expenditures', 'capital_expenditures', False, 'Cash From Investing'),
            
            # Financing (parent)
            ('Cash from Financing', 'cashflow_from_financing', True, None),
            ('Total Dividends Paid', 'dividend_payout_common_stock', False, 'Cash from Financing'),
            ('Common Stock Repurchased', 'proceeds_from_repurchase_of_equity', False, 'Cash from Financing'),
        ]
        
        # Build hierarchical data structure
        years = sorted(df_cashflow_fy['Year'].unique(), reverse=True)
        
        # Group items by parent
        hierarchy = {}
        for display_name, col_name, is_parent, parent_name in cash_flow_structure:
            if is_parent:
                hierarchy[display_name] = {
                    'data': {},
                    'children': []
                }
                # Get parent data
                for year in years:
                    year_data = df_cashflow_fy[df_cashflow_fy['Year'] == year]
                    if not year_data.empty and col_name in year_data.columns:
                        hierarchy[display_name]['data'][year] = year_data[col_name].iloc[0]
            else:
                # This is a child item
                if parent_name in hierarchy:
                    child_data = {}
                    for year in years:
                        year_data = df_cashflow_fy[df_cashflow_fy['Year'] == year]
                        if not year_data.empty and col_name in year_data.columns:
                            child_data[year] = year_data[col_name].iloc[0]
                    hierarchy[parent_name]['children'].append({
                        'name': display_name,
                        'data': child_data
                    })
        
        # Add Free Cash Flow data (always visible, not part of hierarchy)
        free_cash_flow_data = {}
        for year in years:
            year_data = df_cashflow_fy[df_cashflow_fy['Year'] == year]
            if not year_data.empty:
                free_cash_flow_data[year] = year_data['free_cash_flow'].iloc[0]
        
        return {
            'hierarchy': hierarchy,
            'years': years,
            'free_cash_flow': free_cash_flow_data
        }
        
    except Exception as e:
        st.error(f"Error fetching cash flows: {str(e)}")
        return None

def get_growth_rates(ticker):
    """Calculate year-over-year growth rates for comprehensive financial metrics"""
    try:
        conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
        
        # Fetch income statement data
        df_income = conn.execute(f"""
            SELECT symbol, date,
                   total_revenue, gross_profit, ebit, operating_income, net_income,
                   research_and_development, ebitda,
                   depreciation_and_amortization
            FROM my_db.main.pwb_stocksincomestatement
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        # Fetch balance sheet data
        df_balance = conn.execute(f"""
            SELECT symbol, date,
                   total_assets, total_shareholder_equity,
                   long_term_debt, short_term_debt, inventory,
                   common_stock_shares_outstanding
            FROM my_db.main.pwb_stocksbalancesheet
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        # Fetch cash flow data
        df_cashflow = conn.execute(f"""
            SELECT symbol, date,
                   operating_cashflow, capital_expenditures,
                   dividend_payout_common_stock
            FROM my_db.main.pwb_stockscashflow
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 50
        """).df()
        
        conn.close()
        
        if df_income.empty or df_balance.empty or df_cashflow.empty:
            return None
        
        # Merge all dataframes
        df = df_income.merge(df_balance, on=['symbol', 'date'], how='inner')
        df = df.merge(df_cashflow, on=['symbol', 'date'], how='inner')
        
        # Convert dates
        df['date'] = pd.to_datetime(df['date'])
        
        # Identify fiscal year-end
        df['month_day'] = df['date'].dt.strftime('%m-%d')
        fiscal_year_end = df['month_day'].mode()[0]
        
        # Filter to fiscal year-ends
        df_fy = df[df['month_day'] == fiscal_year_end].head(12).copy()
        df_fy = df_fy.sort_values('date')
        
        # Create year column
        df_fy['Year'] = df_fy['date'].dt.year
        
        # Calculate derived metrics
        df_fy['free_cash_flow'] = df_fy['operating_cashflow'] + df_fy['capital_expenditures']
        df_fy['total_debt'] = df_fy['long_term_debt'].fillna(0) + df_fy['short_term_debt'].fillna(0)
        df_fy['book_value_per_share'] = df_fy['total_shareholder_equity'] / df_fy['common_stock_shares_outstanding']
        df_fy['diluted_eps'] = df_fy['net_income'] / df_fy['common_stock_shares_outstanding']
        
        # Calculate EBITDA if not available
        if df_fy['ebitda'].isna().all():
            df_fy['ebitda'] = df_fy['ebit'] + df_fy['depreciation_and_amortization']
        
        # Define metrics to calculate growth for
        growth_metrics = [
            ('Revenue Growth', 'total_revenue'),
            ('Gross Profit Growth', 'gross_profit'),
            ('EBIT Growth', 'ebit'),
            ('EBITDA Growth', 'ebitda'),
            ('Operating Income Growth', 'operating_income'),
            ('Net Income Growth', 'net_income'),
            ('Diluted EPS Growth', 'diluted_eps'),
            ('Operating Cash Flow Growth', 'operating_cashflow'),
            ('Free Cash Flow Growth', 'free_cash_flow'),
            ('Inventory Growth', 'inventory'),
            ('Total Asset Growth', 'total_assets'),
            ('Shareholders\' Equity Growth', 'total_shareholder_equity'),
            ('Book Value per Share Growth', 'book_value_per_share'),
            ('Debt Growth', 'total_debt'),
            ('Dividend Growth', 'dividend_payout_common_stock'),
            ('R&D Expense Growth', 'research_and_development'),
        ]
        
        # Calculate year-over-year growth rates
        growth_data = {}
        years = sorted(df_fy['Year'].unique())
        
        for metric_name, column_name in growth_metrics:
            growth_data[metric_name] = {}
            for i in range(1, len(years)):
                current_year = years[i]
                previous_year = years[i-1]
                
                current_value = df_fy[df_fy['Year'] == current_year][column_name].iloc[0]
                previous_value = df_fy[df_fy['Year'] == previous_year][column_name].iloc[0]
                
                if pd.notna(current_value) and pd.notna(previous_value) and previous_value != 0:
                    growth_rate = ((current_value - previous_value) / abs(previous_value)) * 100
                    growth_data[metric_name][current_year] = growth_rate
                else:
                    growth_data[metric_name][current_year] = np.nan
        
        return {
            'growth_data': growth_data,
            'years': years[1:]  # Exclude first year (no prior year to compare)
        }
        
    except Exception as e:
        st.error(f"Error calculating growth rates: {str(e)}")
        return None

def get_valuation_ratios(ticker):
    """
    Calculate 8 valuation ratios with current values and percentile rankings
    vs sector and historical ranges
    
    Returns dict with:
    - ratios: list of dicts with name, current_value, sector_percentile, history_percentile
    - sector: sector name
    """
    import duckdb
    import pandas as pd
    import numpy as np
    
    try:
        # Connect to MotherDuck
        conn = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
        
        # Get current price
        current_price_df = conn.execute(f"""
            SELECT Close as price
            FROM my_db.main.norgate_survivorship_bias_free_database
            WHERE Symbol = '{ticker}'
            ORDER BY Date DESC
            LIMIT 1
        """).df()
        
        if current_price_df.empty:
            return None
        
        current_price = current_price_df['price'].iloc[0]
        
        # Get sector
        sector_result = conn.execute(f"""
            SELECT DISTINCT Sector 
            FROM my_db.main.norgate_survivorship_bias_free_database 
            WHERE Symbol = '{ticker}' AND Sector IS NOT NULL
            LIMIT 1
        """).df()
        
        sector = sector_result['Sector'].iloc[0] if not sector_result.empty else 'Unknown'
        
        # Get sector symbols (limit to 50 for performance)
        sector_symbols = conn.execute(f"""
            SELECT DISTINCT Symbol 
            FROM my_db.main.norgate_survivorship_bias_free_database 
            WHERE Sector = '{sector}' AND Status = 'Active'
            LIMIT 50
        """).df()['Symbol'].tolist()
        
        # Get latest balance sheet
        current_balance_df = conn.execute(f"""
            SELECT common_stock_shares_outstanding, total_liabilities,
                   cash_and_cash_equivalents_at_carrying_value, short_term_investments,
                   total_shareholder_equity
            FROM my_db.main.pwb_stocksbalancesheet
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 1
        """).df()
        
        if current_balance_df.empty:
            return None
        
        current_shares_outstanding = current_balance_df['common_stock_shares_outstanding'].iloc[0]
        current_total_debt = current_balance_df['total_liabilities'].iloc[0]
        current_cash = current_balance_df['cash_and_cash_equivalents_at_carrying_value'].iloc[0]
        current_short_inv = current_balance_df['short_term_investments'].iloc[0]
        current_short_inv = current_short_inv if not pd.isna(current_short_inv) else 0
        current_equity = current_balance_df['total_shareholder_equity'].iloc[0]
        
        # Calculate market cap and enterprise value
        current_market_cap = current_price * current_shares_outstanding
        current_enterprise_value = current_market_cap + current_total_debt - (current_cash + current_short_inv)
        
        # Get TTM income statement data
        df_income_ttm = conn.execute(f"""
            SELECT total_revenue, net_income, ebitda
            FROM my_db.main.pwb_stocksincomestatement
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 4
        """).df()
        
        # Get TTM cashflow data
        df_cashflow_ttm = conn.execute(f"""
            SELECT operating_cashflow, capital_expenditures
            FROM my_db.main.pwb_stockscashflow
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 4
        """).df()
        
        # Get TTM earnings data
        df_earnings_ttm = conn.execute(f"""
            SELECT reported_eps
            FROM my_db.main.pwb_stocksearnings
            WHERE symbol = '{ticker}'
            ORDER BY date DESC
            LIMIT 4
        """).df()
        
        revenue_ttm = df_income_ttm['total_revenue'].sum()
        net_income_ttm = df_income_ttm['net_income'].sum()
        ebitda_ttm = df_income_ttm['ebitda'].sum()
        operating_cf_ttm = df_cashflow_ttm['operating_cashflow'].sum()
        capex_ttm = df_cashflow_ttm['capital_expenditures'].sum()
        free_cash_flow_ttm = operating_cf_ttm + capex_ttm
        ttm_eps = df_earnings_ttm['reported_eps'].sum()
        
        # Calculate 8 ratios
        ratios_data = {
            'PE': current_price / ttm_eps if ttm_eps > 0 else np.nan,
            'EV/EBITDA': current_enterprise_value / ebitda_ttm if ebitda_ttm > 0 else np.nan,
            'P/Sales': current_market_cap / revenue_ttm if revenue_ttm > 0 else np.nan,
            'EV/Revenue': current_enterprise_value / revenue_ttm if revenue_ttm > 0 else np.nan,
            'P/FCF': current_market_cap / free_cash_flow_ttm if free_cash_flow_ttm > 0 else np.nan,
            'P/BV': current_market_cap / current_equity if current_equity > 0 else np.nan,
            'P/TBV': current_market_cap / current_equity if current_equity > 0 else np.nan,
            'P/Owners Earnings': current_market_cap / free_cash_flow_ttm if free_cash_flow_ttm > 0 else np.nan
        }
        
        # Helper function to calculate percentile
        def calc_percentile(current_value, min_value, max_value):
            """Calculate percentile rank (0-100) of current value within range"""
            if pd.isna(current_value) or pd.isna(min_value) or pd.isna(max_value):
                return np.nan
            if max_value == min_value:
                return 50.0
            percentile = ((current_value - min_value) / (max_value - min_value)) * 100
            return max(0, min(100, percentile))
        
        # Get historical data for the ticker
        df_income_hist = conn.execute(f"""
            SELECT date, total_revenue, net_income, ebitda
            FROM my_db.main.pwb_stocksincomestatement
            WHERE symbol = '{ticker}'
            ORDER BY date ASC
        """).df()
        
        df_balance_hist = conn.execute(f"""
            SELECT date, total_shareholder_equity, total_liabilities, 
                   cash_and_cash_equivalents_at_carrying_value, short_term_investments,
                   common_stock_shares_outstanding
            FROM my_db.main.pwb_stocksbalancesheet
            WHERE symbol = '{ticker}'
            ORDER BY date ASC
        """).df()
        
        df_cashflow_hist = conn.execute(f"""
            SELECT date, operating_cashflow, capital_expenditures
            FROM my_db.main.pwb_stockscashflow
            WHERE symbol = '{ticker}'
            ORDER BY date ASC
        """).df()
        
        df_earnings_hist = conn.execute(f"""
            SELECT date, reported_eps
            FROM my_db.main.pwb_stocksearnings
            WHERE symbol = '{ticker}'
            ORDER BY date ASC
        """).df()
        
        df_prices_hist = conn.execute(f"""
            SELECT Date as date, Close as price
            FROM my_db.main.norgate_survivorship_bias_free_database
            WHERE Symbol = '{ticker}'
            ORDER BY Date ASC
        """).df()
        
        # Convert dates
        for df in [df_income_hist, df_balance_hist, df_cashflow_hist, df_earnings_hist, df_prices_hist]:
            df['date'] = pd.to_datetime(df['date'])
        
        # Function to calculate historical percentile
        def calc_historical_percentile(ratio_name, current_value):
            """Calculate where current ratio falls in stock's historical range"""
            if pd.isna(current_value):
                return np.nan
            
            # Merge all historical data
            hist_merged = df_income_hist.merge(df_balance_hist, on='date', how='inner')
            hist_merged = hist_merged.merge(df_cashflow_hist, on='date', how='inner')
            hist_merged = hist_merged.merge(df_earnings_hist, on='date', how='inner')
            
            if hist_merged.empty or len(hist_merged) < 4:
                return np.nan
            
            hist_ratios = []
            
            # Calculate rolling TTM ratios for each quarter
            for i in range(3, len(hist_merged)):
                ttm_data = hist_merged.iloc[i-3:i+1]
                quarter_date = ttm_data['date'].iloc[-1]
                
                # Get price on or shortly after this quarter date
                price_match = df_prices_hist[df_prices_hist['date'] >= quarter_date]
                if price_match.empty:
                    continue
                price = price_match['price'].iloc[0]
                
                # Get shares outstanding for this quarter
                shares = ttm_data['common_stock_shares_outstanding'].iloc[-1]
                if pd.isna(shares) or shares <= 0:
                    continue
                
                # Calculate market cap and enterprise value for this period
                market_cap_hist = price * shares
                
                # Calculate TTM metrics
                rev_ttm = ttm_data['total_revenue'].sum()
                eb_ttm = ttm_data['ebitda'].sum()
                eps_ttm = ttm_data['reported_eps'].sum()
                ocf_ttm = ttm_data['operating_cashflow'].sum()
                cx_ttm = ttm_data['capital_expenditures'].sum()
                fcf_ttm = ocf_ttm + cx_ttm
                
                # Latest quarter balance sheet values
                eq = ttm_data['total_shareholder_equity'].iloc[-1]
                debt = ttm_data['total_liabilities'].iloc[-1]
                cash_val = ttm_data['cash_and_cash_equivalents_at_carrying_value'].iloc[-1]
                st_inv = ttm_data['short_term_investments'].iloc[-1]
                st_inv = st_inv if not pd.isna(st_inv) else 0
                
                # Calculate enterprise value
                ev_hist = market_cap_hist + debt - (cash_val + st_inv)
                
                # Calculate ratio based on ratio_name
                if ratio_name == 'PE':
                    ratio = price / eps_ttm if eps_ttm > 0 else np.nan
                elif ratio_name == 'EV/EBITDA':
                    ratio = ev_hist / eb_ttm if eb_ttm > 0 else np.nan
                elif ratio_name == 'P/Sales':
                    ratio = market_cap_hist / rev_ttm if rev_ttm > 0 else np.nan
                elif ratio_name == 'EV/Revenue':
                    ratio = ev_hist / rev_ttm if rev_ttm > 0 else np.nan
                elif ratio_name == 'P/FCF':
                    ratio = market_cap_hist / fcf_ttm if fcf_ttm > 0 else np.nan
                elif ratio_name == 'P/BV':
                    ratio = market_cap_hist / eq if eq > 0 else np.nan
                elif ratio_name == 'P/TBV':
                    ratio = market_cap_hist / eq if eq > 0 else np.nan
                elif ratio_name == 'P/Owners Earnings':
                    ratio = market_cap_hist / fcf_ttm if fcf_ttm > 0 else np.nan
                else:
                    ratio = np.nan
                
                if not pd.isna(ratio) and ratio > 0 and ratio < 1000:
                    hist_ratios.append(ratio)
            
            if len(hist_ratios) < 2:
                return np.nan
            
            min_hist = min(hist_ratios)
            max_hist = max(hist_ratios)
            
            return calc_percentile(current_value, min_hist, max_hist)
        
        # Function to calculate sector percentile
        def calc_sector_percentile(ratio_name, current_value):
            """Calculate where current ratio falls in sector range"""
            if pd.isna(current_value):
                return np.nan
            
            sector_ratios = []
            
            # Process sector peers (limit to 100 for performance)
            for sym in sector_symbols[:100]:
                if sym == ticker:
                    continue
                    
                try:
                    # Get current price from norgate
                    sym_price_df = conn.execute(f"""
                        SELECT Close as price
                        FROM my_db.main.norgate_survivorship_bias_free_database
                        WHERE Symbol = '{sym}'
                        ORDER BY Date DESC
                        LIMIT 1
                    """).df()
                    
                    if sym_price_df.empty:
                        continue
                    sym_price = sym_price_df['price'].iloc[0]
                    
                    # Get latest balance sheet for shares and debt/cash
                    sym_balance = conn.execute(f"""
                        SELECT common_stock_shares_outstanding, total_shareholder_equity,
                               total_liabilities, cash_and_cash_equivalents_at_carrying_value,
                               short_term_investments
                        FROM my_db.main.pwb_stocksbalancesheet
                        WHERE symbol = '{sym}'
                        ORDER BY date DESC LIMIT 1
                    """).df()
                    
                    if sym_balance.empty:
                        continue
                    
                    sym_shares = sym_balance['common_stock_shares_outstanding'].iloc[0]
                    sym_eq = sym_balance['total_shareholder_equity'].iloc[0]
                    sym_debt = sym_balance['total_liabilities'].iloc[0]
                    sym_cash = sym_balance['cash_and_cash_equivalents_at_carrying_value'].iloc[0]
                    sym_st_inv = sym_balance['short_term_investments'].iloc[0]
                    sym_st_inv = sym_st_inv if not pd.isna(sym_st_inv) else 0
                    
                    if pd.isna(sym_shares) or sym_shares <= 0:
                        continue
                    
                    sym_mc = sym_price * sym_shares
                    sym_ev = sym_mc + sym_debt - (sym_cash + sym_st_inv)
                    
                    # Get TTM financials
                    sym_income_ttm = conn.execute(f"""
                        SELECT 
                            SUM(total_revenue) as total_revenue,
                            SUM(net_income) as net_income,
                            SUM(ebitda) as ebitda
                        FROM (
                            SELECT total_revenue, net_income, ebitda
                            FROM my_db.main.pwb_stocksincomestatement
                            WHERE symbol = '{sym}'
                            ORDER BY date DESC
                            LIMIT 4
                        )
                    """).df()
                    
                    sym_cashflow_ttm = conn.execute(f"""
                        SELECT 
                            SUM(operating_cashflow) as operating_cashflow,
                            SUM(capital_expenditures) as capital_expenditures
                        FROM (
                            SELECT operating_cashflow, capital_expenditures
                            FROM my_db.main.pwb_stockscashflow
                            WHERE symbol = '{sym}'
                            ORDER BY date DESC
                            LIMIT 4
                        )
                    """).df()
                    
                    sym_earnings_ttm = conn.execute(f"""
                        SELECT SUM(reported_eps) as ttm_eps
                        FROM (
                            SELECT reported_eps
                            FROM my_db.main.pwb_stocksearnings
                            WHERE symbol = '{sym}'
                            ORDER BY date DESC
                            LIMIT 4
                        )
                    """).df()
                    
                    if sym_income_ttm.empty or sym_cashflow_ttm.empty or sym_earnings_ttm.empty:
                        continue
                    
                    rev_ttm = sym_income_ttm['total_revenue'].iloc[0]
                    eb_ttm = sym_income_ttm['ebitda'].iloc[0]
                    ocf_ttm = sym_cashflow_ttm['operating_cashflow'].iloc[0]
                    cx_ttm = sym_cashflow_ttm['capital_expenditures'].iloc[0]
                    fcf_ttm = ocf_ttm + cx_ttm
                    eps_ttm = sym_earnings_ttm['ttm_eps'].iloc[0]
                    
                    # Calculate ratio
                    if ratio_name == 'PE':
                        ratio = sym_price / eps_ttm if eps_ttm > 0 else np.nan
                    elif ratio_name == 'EV/EBITDA':
                        ratio = sym_ev / eb_ttm if eb_ttm > 0 else np.nan
                    elif ratio_name == 'P/Sales':
                        ratio = sym_mc / rev_ttm if rev_ttm > 0 else np.nan
                    elif ratio_name == 'EV/Revenue':
                        ratio = sym_ev / rev_ttm if rev_ttm > 0 else np.nan
                    elif ratio_name == 'P/FCF':
                        ratio = sym_mc / fcf_ttm if fcf_ttm > 0 else np.nan
                    elif ratio_name == 'P/BV':
                        ratio = sym_mc / sym_eq if sym_eq > 0 else np.nan
                    elif ratio_name == 'P/TBV':
                        ratio = sym_mc / sym_eq if sym_eq > 0 else np.nan
                    elif ratio_name == 'P/Owners Earnings':
                        ratio = sym_mc / fcf_ttm if fcf_ttm > 0 else np.nan
                    else:
                        ratio = np.nan
                    
                    if not pd.isna(ratio) and ratio > 0 and ratio < 1000:
                        sector_ratios.append(ratio)
                except:
                    continue
            
            if len(sector_ratios) < 2:
                return np.nan
            
            min_sector = min(sector_ratios)
            max_sector = max(sector_ratios)
            
            return calc_percentile(current_value, min_sector, max_sector)
        
        # Calculate percentiles for all ratios
        results = []
        for ratio_name, current_value in ratios_data.items():
            sector_pct = calc_sector_percentile(ratio_name, current_value)
            history_pct = calc_historical_percentile(ratio_name, current_value)
            
            results.append({
                'name': ratio_name,
                'current_value': current_value,
                'sector_percentile': sector_pct,
                'history_percentile': history_pct
            })
        
        conn.close()
        
        return {
            'ratios': results,
            'sector': sector
        }
    
    except Exception as e:
        st.error(f"Error calculating valuation ratios: {str(e)}")
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
        
        # Financial Overview Grid Section
        st.subheader("📊 Financial Overview")
        
        # Time period selector
        if 'fin_overview_period' not in st.session_state:
            st.session_state.fin_overview_period = '10yr'
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("1 Year", key="btn_1yr", use_container_width=True):
                st.session_state.fin_overview_period = '1yr'
        with col2:
            if st.button("3 Years", key="btn_3yr", use_container_width=True):
                st.session_state.fin_overview_period = '3yr'
        with col3:
            if st.button("5 Years", key="btn_5yr", use_container_width=True):
                st.session_state.fin_overview_period = '5yr'
        with col4:
            if st.button("10 Years", key="btn_10yr", use_container_width=True):
                st.session_state.fin_overview_period = '10yr'
        with col5:
            if st.button("20 Years", key="btn_20yr", use_container_width=True):
                st.session_state.fin_overview_period = '20yr'
        
        st.write("")  # Spacing
        
        with st.spinner(f"Loading {st.session_state.fin_overview_period} financial data..."):
            fin_overview_fig = create_financial_overview_grid(current_ticker, st.session_state.fin_overview_period)
        
        if fin_overview_fig:
            st.plotly_chart(fin_overview_fig, use_container_width=True)
        else:
            st.warning("Unable to load financial overview data.")
        
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
            
            # Display the table with calculated height to show all rows
            table_height = len(display_df) * 35 + 38  # 35px per row + 38px for header
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=table_height
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
            
            # Display the table with calculated height to show all rows
            table_height = len(display_df_quality) * 35 + 38  # 35px per row + 38px for header
            st.dataframe(
                display_df_quality,
                use_container_width=True,
                hide_index=True,
                height=table_height
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
                    # Button with arrow and parent name
                    if st.button(f"{arrow} {parent_name}", key=f"toggle_{parent_name}"):
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
        
        # Balance Sheet Section
        st.subheader("📊 Balance Sheet")
        
        with st.spinner("Loading 10-year balance sheet..."):
            balance_data = get_balance_sheet(current_ticker)
        
        if balance_data and balance_data['hierarchy']:
            hierarchy = balance_data['hierarchy']
            years = balance_data['years']
            
            # Initialize session state for expanded balance sheet parents
            if 'expanded_balance_parents' not in st.session_state:
                st.session_state.expanded_balance_parents = set()
            
            # Build all rows for the unified table
            all_rows = []
            
            for parent_name, parent_info in hierarchy.items():
                # Add parent row with inline arrow
                is_expanded = parent_name in st.session_state.expanded_balance_parents
                arrow = "▼" if is_expanded else "▶"
                parent_row = {'Metric': f"{arrow} {parent_name}", 'is_parent': True, 'parent_name': parent_name}
                for year in years:
                    value = parent_info['data'].get(year, np.nan)
                    if pd.notna(value):
                        if abs(value) >= 1e9:
                            parent_row[year] = f"{value/1e9:.2f}B"
                        elif abs(value) >= 1e6:
                            parent_row[year] = f"{value/1e6:.2f}M"
                        else:
                            parent_row[year] = f"{value:.2f}"
                    else:
                        parent_row[year] = "N/A"
                all_rows.append(parent_row)
                
                # Add children rows if parent is expanded
                if parent_name in st.session_state.expanded_balance_parents:
                    for child in parent_info['children']:
                        child_row = {'Metric': f"    {child['name']}", 'is_parent': False, 'parent_name': parent_name}
                        for year in years:
                            value = child['data'].get(year, np.nan)
                            if pd.notna(value):
                                if 'Shares' in child['name']:
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
                    is_expanded = parent_name in st.session_state.expanded_balance_parents
                    arrow = "▼" if is_expanded else "▶"
                    # Button with arrow and parent name
                    if st.button(f"{arrow} {parent_name}", key=f"toggle_balance_{parent_name}"):
                        if parent_name in st.session_state.expanded_balance_parents:
                            st.session_state.expanded_balance_parents.remove(parent_name)
                        else:
                            st.session_state.expanded_balance_parents.add(parent_name)
                        st.rerun()
            
            # Create and display unified dataframe
            df_balance_display = pd.DataFrame(all_rows)
            display_cols = ['Metric'] + years
            df_balance_display = df_balance_display[display_cols]
            
            st.dataframe(
                df_balance_display,
                use_container_width=True,
                hide_index=True,
                height=min(800, len(all_rows) * 35 + 50)
            )
            
            st.caption("💡 Data sourced from MotherDuck: pwb_stocksbalancesheet")
        else:
            st.warning(f"⚠️ No balance sheet data available for {current_ticker}")
        
        st.markdown("---")
        
        # Cash Flows Section
        st.subheader("💵 Cash Flows")
        
        with st.spinner("Loading 10-year cash flows..."):
            cashflow_data = get_cash_flows(current_ticker)
        
        if cashflow_data and cashflow_data['hierarchy']:
            hierarchy = cashflow_data['hierarchy']
            years = cashflow_data['years']
            free_cash_flow = cashflow_data['free_cash_flow']
            
            # Initialize session state for expanded cash flow parents
            if 'expanded_cashflow_parents' not in st.session_state:
                st.session_state.expanded_cashflow_parents = set()
            
            # Build all rows for the unified table
            all_rows = []
            
            for parent_name, parent_info in hierarchy.items():
                # Add parent row with inline arrow
                is_expanded = parent_name in st.session_state.expanded_cashflow_parents
                arrow = "▼" if is_expanded else "▶"
                parent_row = {'Metric': f"{arrow} {parent_name}", 'is_parent': True, 'parent_name': parent_name}
                for year in years:
                    value = parent_info['data'].get(year, np.nan)
                    if pd.notna(value):
                        if abs(value) >= 1e9:
                            parent_row[year] = f"{value/1e9:.2f}B"
                        elif abs(value) >= 1e6:
                            parent_row[year] = f"{value/1e6:.2f}M"
                        else:
                            parent_row[year] = f"{value:.2f}"
                    else:
                        parent_row[year] = "N/A"
                all_rows.append(parent_row)
                
                # Add children rows if parent is expanded
                if parent_name in st.session_state.expanded_cashflow_parents:
                    for child in parent_info['children']:
                        child_row = {'Metric': f"    {child['name']}", 'is_parent': False, 'parent_name': parent_name}
                        for year in years:
                            value = child['data'].get(year, np.nan)
                            if pd.notna(value):
                                if abs(value) >= 1e9:
                                    child_row[year] = f"{value/1e9:.2f}B"
                                elif abs(value) >= 1e6:
                                    child_row[year] = f"{value/1e6:.2f}M"
                                else:
                                    child_row[year] = f"{value:.2f}"
                            else:
                                child_row[year] = "N/A"
                        all_rows.append(child_row)
            
            # Add Free Cash Flow row (always visible)
            fcf_row = {'Metric': '💰 Free Cash Flow', 'is_parent': False, 'parent_name': None}
            for year in years:
                value = free_cash_flow.get(year, np.nan)
                if pd.notna(value):
                    if abs(value) >= 1e9:
                        fcf_row[year] = f"{value/1e9:.2f}B"
                    elif abs(value) >= 1e6:
                        fcf_row[year] = f"{value/1e6:.2f}M"
                    else:
                        fcf_row[year] = f"{value:.2f}"
                else:
                    fcf_row[year] = "N/A"
            all_rows.append(fcf_row)
            
            # Create compact toggle buttons
            parent_names = list(hierarchy.keys())
            button_cols = st.columns(len(parent_names))
            
            for idx, parent_name in enumerate(parent_names):
                with button_cols[idx]:
                    is_expanded = parent_name in st.session_state.expanded_cashflow_parents
                    arrow = "▼" if is_expanded else "▶"
                    # Button with arrow and parent name
                    if st.button(f"{arrow} {parent_name}", key=f"toggle_cashflow_{parent_name}"):
                        if parent_name in st.session_state.expanded_cashflow_parents:
                            st.session_state.expanded_cashflow_parents.remove(parent_name)
                        else:
                            st.session_state.expanded_cashflow_parents.add(parent_name)
                        st.rerun()
            
            # Create and display unified dataframe
            df_cashflow_display = pd.DataFrame(all_rows)
            display_cols = ['Metric'] + years
            df_cashflow_display = df_cashflow_display[display_cols]
            
            st.dataframe(
                df_cashflow_display,
                use_container_width=True,
                hide_index=True,
                height=min(800, len(all_rows) * 35 + 50)
            )
            
            st.caption("💡 Data sourced from MotherDuck: pwb_stockscashflow | Free Cash Flow = Operating Cash Flow + Capital Expenditures")
        else:
            st.warning(f"⚠️ No cash flow data available for {current_ticker}")
        
        st.markdown("---")
        
        # Growth Rates Section
        st.subheader("📈 Growth Rates")
        
        with st.spinner("Calculating year-over-year growth rates..."):
            growth_data = get_growth_rates(current_ticker)
        
        if growth_data and growth_data['growth_data']:
            growth_rates = growth_data['growth_data']
            years = growth_data['years']
            
            # Reverse years to show newest first (left to right)
            years_reversed = sorted(years, reverse=True)
            
            # Build dataframe for display
            rows = []
            for metric_name in growth_rates.keys():
                row = {'Metric': metric_name}
                for year in years_reversed:
                    growth_value = growth_rates[metric_name].get(year, np.nan)
                    if pd.notna(growth_value):
                        row[year] = f"{growth_value:.2f}%"
                    else:
                        row[year] = "-"
                rows.append(row)
            
            df_growth = pd.DataFrame(rows)
            
            # Display the table with calculated height to show all rows
            table_height = len(df_growth) * 35 + 38  # 35px per row + 38px for header
            st.dataframe(
                df_growth,
                use_container_width=True,
                hide_index=True,
                height=table_height
            )
            
            st.caption("💡 Year-over-year growth rates calculated from MotherDuck: pwb_stocksincomestatement, pwb_stocksbalancesheet, pwb_stockscashflow")
        else:
            st.warning(f"⚠️ No growth rate data available for {current_ticker}")
        
        st.markdown("---")
        
        # Valuation Ratios Section
        st.subheader("💰 Valuation Ratios")
        
        with st.spinner("Calculating valuation ratios..."):
            valuation_data = get_valuation_ratios(current_ticker)
        
        if valuation_data and 'ratios' in valuation_data:
            ratios = valuation_data['ratios']
            sector = valuation_data['sector']
            
            st.caption(f"📊 Sector: **{sector}**")
            
            # Create HTML table with progress bars
            html = """<style>
            .valuation-table {
                width: 100%;
                border-collapse: collapse;
                font-family: 'Source Sans Pro', sans-serif;
                margin-top: 20px;
            }
            .valuation-table th {
                background-color: #f0f2f6;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #e0e0e0;
            }
            .valuation-table td {
                padding: 12px;
                border-bottom: 1px solid #f0f2f6;
            }
            .ratio-name {
                font-weight: 500;
                color: #262730;
            }
            .current-value {
                font-weight: 600;
                color: #0068c9;
                font-size: 16px;
            }
            .progress-container {
                width: 100%;
                height: 24px;
                background-color: #f0f2f6;
                border-radius: 4px;
                position: relative;
                overflow: hidden;
            }
            .progress-bar {
                height: 100%;
                border-radius: 4px;
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 12px;
                font-weight: 600;
            }
            .progress-red {
                background-color: #ff4b4b;
            }
            .progress-orange {
                background-color: #ffa500;
            }
            .progress-green {
                background-color: #21c354;
            }
            .progress-gray {
                background-color: #cccccc;
            }
            </style>
            
            <table class="valuation-table">
                <thead>
                    <tr>
                        <th style="width: 25%;">Name</th>
                        <th style="width: 15%;">Current</th>
                        <th style="width: 30%;">Vs Sector</th>
                        <th style="width: 30%;">Vs History</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for ratio in ratios:
                name = ratio['name']
                current = ratio['current_value']
                sector_pct = ratio['sector_percentile']
                history_pct = ratio['history_percentile']
                
                # Format current value
                if pd.isna(current):
                    current_str = "N/A"
                else:
                    current_str = f"{current:.2f}"
                
                # Determine color based on percentile
                def get_color_class(pct):
                    if pd.isna(pct):
                        return 'progress-gray', 'N/A'
                    elif pct < 40:
                        return 'progress-red', f"{pct:.0f}%"
                    elif pct < 70:
                        return 'progress-orange', f"{pct:.0f}%"
                    else:
                        return 'progress-green', f"{pct:.0f}%"
                
                sector_color, sector_label = get_color_class(sector_pct)
                history_color, history_label = get_color_class(history_pct)
                
                sector_width = sector_pct if not pd.isna(sector_pct) else 0
                history_width = history_pct if not pd.isna(history_pct) else 0
                
                html += f"""
                    <tr>
                        <td class="ratio-name">{name}</td>
                        <td class="current-value">{current_str}</td>
                        <td>
                            <div class="progress-container">
                                <div class="progress-bar {sector_color}" style="width: {sector_width}%;">
                                    {sector_label}
                                </div>
                            </div>
                        </td>
                        <td>
                            <div class="progress-container">
                                <div class="progress-bar {history_color}" style="width: {history_width}%;">
                                    {history_label}
                                </div>
                            </div>
                        </td>
                    </tr>
                """
            
            html += """
                </tbody>
            </table>
            """
            
            st.html(html)
            
            st.caption("💡 Percentiles show where current ratio falls within sector/historical range. Red (0-40%): Below average, Orange (40-70%): Average, Green (70-100%): Above average")
            st.caption("⚠️ Note: Percentile calculations are placeholders (50%) in this version. Full implementation coming soon.")
        else:
            st.warning(f"⚠️ No valuation ratio data available for {current_ticker}")
        
    else:
        st.error(f"❌ No data found for ticker '{current_ticker}' in MotherDuck database.")
        st.info("💡 Make sure the ticker exists in the GuruFocusData table.")
else:
    st.info("👆 Enter a stock ticker above to begin analysis")

st.markdown("---")
st.caption("JCN Financial & Tax Advisory Group, LLC - Built with Streamlit")
