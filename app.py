import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="JCN Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
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
col1, col2 = st.columns([1, 4])
with col1:
    try:
        logo = Image.open("jcn_logo.jpg")
        st.image(logo, width=150)
    except:
        st.write("")

with col2:
    st.title("JCN Financial Dashboard")
    st.markdown("Real-time stock analysis and portfolio tracking")

st.markdown("---")

# Sidebar for controls
with st.sidebar:
    st.header("Dashboard Controls")
    
    # Stock ticker input
    st.subheader("Stock Tickers")
    default_tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "TSLA", "META"]
    
    ticker_input = st.text_input(
        "Enter stock tickers (comma-separated)",
        value=", ".join(default_tickers),
        help="Enter stock symbols separated by commas (e.g., AAPL, MSFT, GOOGL)"
    )
    
    # Parse tickers
    tickers = [ticker.strip().upper() for ticker in ticker_input.split(",") if ticker.strip()]
    
    st.markdown("---")
    
    # Time horizon selection
    st.subheader("Time Horizon")
    time_options = {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "5 Years": "5y",
        "10 Years": "10y",
        "20 Years": "20y"
    }
    
    selected_period = st.radio(
        "Select time period",
        options=list(time_options.keys()),
        index=2  # Default to 6 Months
    )
    
    period = time_options[selected_period]

# Main content area
if tickers:
    try:
        with st.spinner("Fetching stock data..."):
            # Fetch data for all tickers
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
                    st.warning(f"Could not fetch data for {ticker}: {str(e)}")
            
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
                    
                    # Find best and worst performers
                    best_stock = max(performance, key=performance.get)
                    worst_stock = min(performance, key=performance.get)
                    
                    # Display metrics
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
                    st.subheader(f"Normalized Stock Price Comparison - {selected_period}")
                    
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
                    
                    st.markdown("---")
                    
                    # Performance table
                    st.subheader("Performance Summary")
                    
                    performance_data = []
                    for ticker in performance.keys():
                        performance_data.append({
                            'Ticker': ticker,
                            'Performance (%)': f"{performance[ticker]:.2f}%",
                            'Start Price': f"${df[ticker].iloc[0]:.2f}",
                            'Current Price': f"${df[ticker].iloc[-1]:.2f}",
                            'Performance_Value': performance[ticker]
                        })
                    
                    performance_df = pd.DataFrame(performance_data)
                    
                    # Sort by performance
                    performance_df = performance_df.sort_values('Performance_Value', ascending=False)
                    performance_df = performance_df.drop('Performance_Value', axis=1)
                    performance_df = performance_df.reset_index(drop=True)
                    
                    st.dataframe(performance_df, use_container_width=True, hide_index=True)
                else:
                    st.error("Not enough data available for the selected time period.")
            else:
                st.error("Could not fetch data for any of the provided tickers. Please check the symbols and try again.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check your ticker symbols and try again.")
else:
    st.info("👈 Please enter stock tickers in the sidebar to begin analysis.")

# Footer
st.markdown("---")
st.caption("JCN Financial & Tax Advisory Group, LLC - Built with Streamlit")
