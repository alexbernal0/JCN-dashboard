import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
from PIL import Image
import time

# Page configuration
st.set_page_config(
    page_title="Persistent Value - JCN Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for white theme
st.markdown("""
    <style>
    .main {
        background-color: white;
    }
    .stApp {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

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
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True, type="primary"):
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    # Display last refresh time and source
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    refresh_time = st.session_state.last_refresh.strftime("%I:%M:%S %p")
    st.caption(f"**Last Updated:** {refresh_time}")
    st.caption("**Source:** Yahoo Finance")

st.markdown("---")

# Auto-refresh every 15 minutes
if 'last_refresh' in st.session_state:
    time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
    if time_since_refresh > 900:  # 900 seconds = 15 minutes
        st.session_state.last_refresh = datetime.now()
        st.rerun()

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

# Main content area - Stock Analysis
if tickers and len(tickers) > 0:
    try:
        with st.spinner("Fetching stock data..."):
            # Fetch data for all tickers
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
            valid_tickers = []
            
            for ticker in tickers:
                try:
                    stock = yf.Ticker(ticker)
                    data = stock.history(period=period)
                    
                    if not data.empty and len(data) > 0:
                        stock_data[ticker] = data['Close']
                        valid_tickers.append(ticker)
                except Exception as e:
                    st.warning(f"Could not fetch data for {ticker}")
            
            if stock_data and len(valid_tickers) > 0:
                # Create DataFrame with all stocks
                df = pd.DataFrame(stock_data)
                df = df.dropna()
                
                if len(df) > 0:
                    # Normalize prices to starting value (for comparison)
                    df_normalized = df.copy()
                    for col in df_normalized.columns:
                        df_normalized[col] = df_normalized[col] / df_normalized[col].iloc[0]
                    
                    # Calculate performance metrics
                    performance = {}
                    for ticker in df_normalized.columns:
                        start_price = df_normalized[ticker].iloc[0]
                        end_price = df_normalized[ticker].iloc[-1]
                        pct_change = ((end_price - start_price) / start_price) * 100
                        performance[ticker] = pct_change
                    
                    # MOVED TO TOP: Portfolio Performance Details Table
                    st.subheader("💼 Portfolio Performance Details")
                    
                    performance_data = []
                    total_cost = 0
                    total_current_value = 0
                    
                    for ticker in performance.keys():
                        # Get portfolio data for this ticker
                        portfolio_row = st.session_state.portfolio_data[st.session_state.portfolio_data['Symbol'] == ticker]
                        
                        if not portfolio_row.empty:
                            cost_basis = portfolio_row['Cost Basis'].values[0]
                            shares = portfolio_row['Shares'].values[0]
                            current_price = df[ticker].iloc[-1]
                            
                            total_cost_position = cost_basis * shares
                            current_value = current_price * shares
                            gain_loss = current_value - total_cost_position
                            gain_loss_pct = (gain_loss / total_cost_position) * 100 if total_cost_position > 0 else 0
                            
                            total_cost += total_cost_position
                            total_current_value += current_value
                            
                            performance_data.append({
                                'Ticker': ticker,
                                'Shares': int(shares),
                                'Cost Basis': f"${cost_basis:.2f}",
                                'Current Price': f"${current_price:.2f}",
                                'Total Cost': f"${total_cost_position:,.2f}",
                                'Current Value': f"${current_value:,.2f}",
                                'Gain/Loss': f"${gain_loss:,.2f}",
                                'Gain/Loss %': f"{gain_loss_pct:.2f}%",
                                'Period Performance': f"{performance[ticker]:.2f}%",
                                '_sort_value': gain_loss_pct
                            })
                    
                    performance_df = pd.DataFrame(performance_data)
                    
                    # Sort by gain/loss percentage
                    performance_df = performance_df.sort_values('_sort_value', ascending=False)
                    performance_df = performance_df.drop('_sort_value', axis=1)
                    performance_df = performance_df.reset_index(drop=True)
                    
                    # Display full table without scrolling
                    st.dataframe(
                        performance_df, 
                        use_container_width=True, 
                        hide_index=True
                    )
                    
                    # Portfolio totals
                    st.markdown("---")
                    st.subheader("💰 Portfolio Totals")
                    
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
                    
                    # Find best and worst performers
                    best_stock = max(performance, key=performance.get)
                    worst_stock = min(performance, key=performance.get)
                    
                    # Display metrics
                    st.subheader("📈 Performance Summary")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            label="📈 Best Performer",
                            value=best_stock,
                            delta=f"+{performance[best_stock]:.2f}%"
                        )
                    
                    with col2:
                        st.metric(
                            label="📉 Worst Performer",
                            value=worst_stock,
                            delta=f"{performance[worst_stock]:.2f}%"
                        )
                    
                    with col3:
                        avg_performance = np.mean(list(performance.values()))
                        st.metric(
                            label="📊 Average Performance",
                            value=f"{avg_performance:.2f}%",
                            delta=f"{len(valid_tickers)} stocks tracked"
                        )
                    
                    st.markdown("---")
                    
                    # Create interactive chart
                    st.subheader(f"📊 Normalized Stock Price Comparison - {st.session_state.selected_period}")
                    
                    fig = go.Figure()
                    
                    # Add a line for each stock
                    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
                    
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
                    
                    # Update layout for white theme
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
                    
                    # Dashboard Controls Section (MOVED BELOW CHART, HORIZONTAL LAYOUT)
                    st.markdown("---")
                    st.subheader("⚙️ Dashboard Controls")
                    
                    st.markdown("**Time Horizon**")
                    
                    # Horizontal time period selection
                    time_period_options = list(time_options.keys())
                    
                    cols = st.columns(7)
                    for idx, option in enumerate(time_period_options):
                        with cols[idx]:
                            if st.button(option, use_container_width=True, 
                                       type="primary" if st.session_state.selected_period == option else "secondary"):
                                st.session_state.selected_period = option
                                st.rerun()
                    
                else:
                    st.error("Not enough data available for the selected time period.")
            else:
                st.error("Could not fetch data for any of the provided tickers. Please check the symbols and try again.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check your ticker symbols and try again.")
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
    # Read-only mode - show all rows
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
