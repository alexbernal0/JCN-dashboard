import streamlit as st
from PIL import Image
import duckdb
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta
import os

st.set_page_config(
    page_title="Risk Management - JCN Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# MotherDuck connection
MOTHERDUCK_TOKEN = os.getenv('MOTHERDUCK_TOKEN')

# Years to display
YEARS_TO_DISPLAY = 5

def load_bpsp_data():
    """Load Buying Power / Selling Pressure data from MotherDuck"""
    try:
        con = duckdb.connect(f'md:?motherduck_token={MOTHERDUCK_TOKEN}')
        
        df = con.execute("""
            SELECT 
                Date,
                Buying_Power,
                Selling_Pressure,
                BPSP_Ratio,
                SPX_Open,
                SPX_High,
                SPX_Low,
                SPX_Close
            FROM NDR_BP_SP_history
            ORDER BY Date
        """).df()
        
        con.close()
        
        # Convert date and filter to last N years
        df['Date'] = pd.to_datetime(df['Date'])
        cutoff_date = df['Date'].max() - timedelta(days=YEARS_TO_DISPLAY*365.25)
        df_viz = df[df['Date'] >= cutoff_date].copy()
        
        return df_viz
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def create_bpsp_visualization(df):
    """Create BPSP visualization with SPX candlestick and BP/SP indicators"""
    
    # Create subplots with 2 rows
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.6, 0.4],
        vertical_spacing=0.08,
        subplot_titles=(
            f'S&P 500 Index (Weekly OHLC) - Last {YEARS_TO_DISPLAY} Years',
            'Buying Power / Selling Pressure Index (Volume-Based, 21-Week MA)'
        )
    )
    
    # ========================================================================
    # SUBPLOT 1: SPX CANDLESTICK CHART
    # ========================================================================
    
    # Separate up and down weeks for coloring
    colors = ['green' if close >= open_price else 'red' 
              for close, open_price in zip(df['SPX_Close'], df['SPX_Open'])]
    
    # Add candlestick trace
    fig.add_trace(
        go.Candlestick(
            x=df['Date'],
            open=df['SPX_Open'],
            high=df['SPX_High'],
            low=df['SPX_Low'],
            close=df['SPX_Close'],
            increasing_line_color='darkgreen',
            decreasing_line_color='darkred',
            increasing_fillcolor='lightgreen',
            decreasing_fillcolor='lightcoral',
            name='SPX',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add stats annotation
    latest = df.iloc[-1]
    stats_text = f"""<b>Latest ({latest['Date'].strftime('%Y-%m-%d')}):</b><br>
SPX: {latest['SPX_Close']:,.2f}<br>
BP: {latest['Buying_Power']:.4f}<br>
SP: {latest['Selling_Pressure']:.4f}<br>
Ratio: {latest['BPSP_Ratio']:.4f}"""
    
    fig.add_annotation(
        text=stats_text,
        xref="x domain", yref="y domain",
        x=0.02, y=0.98,
        xanchor='left', yanchor='top',
        showarrow=False,
        bgcolor='wheat',
        bordercolor='black',
        borderwidth=1,
        font=dict(size=10, family='monospace'),
        row=1, col=1
    )
    
    # ========================================================================
    # SUBPLOT 2: BUYING POWER / SELLING PRESSURE
    # ========================================================================
    
    # Add Buying Power line
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Buying_Power'],
            name='Buying Power (21-wk MA)',
            line=dict(color='green', width=2.5),
            mode='lines'
        ),
        row=2, col=1
    )
    
    # Add Selling Pressure line
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Selling_Pressure'],
            name='Selling Pressure (21-wk MA)',
            line=dict(color='red', width=2.5),
            mode='lines'
        ),
        row=2, col=1
    )
    
    # Add neutral line
    fig.add_hline(
        y=0.5, 
        line_dash="dash", 
        line_color="gray",
        annotation_text="Neutral (0.5)",
        annotation_position="right",
        row=2, col=1
    )
    
    # Add fill between BP and SP
    # Use a simple approach: fill between the two lines
    # The color will blend based on which is higher
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Buying_Power'],
            fill=None,
            mode='lines',
            line_color='rgba(0,0,0,0)',
            showlegend=False,
            hoverinfo='skip',
            name='BP_fill'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Selling_Pressure'],
            fill='tonexty',
            fillcolor='rgba(0, 200, 0, 0.15)',
            mode='lines',
            line_color='rgba(0,0,0,0)',
            showlegend=False,
            hoverinfo='skip',
            name='SP_fill'
        ),
        row=2, col=1
    )
    
    # Customize candlestick hover
    fig.update_traces(
        hovertemplate='<b>Date</b>: %{x|%Y-%m-%d}<br>' +
                      '<b>Open</b>: %{open:,.2f}<br>' +
                      '<b>High</b>: %{high:,.2f}<br>' +
                      '<b>Low</b>: %{low:,.2f}<br>' +
                      '<b>Close</b>: %{close:,.2f}<br>' +
                      '<extra></extra>',
        selector=dict(type='candlestick')
    )
    
    # Update layout
    fig.update_layout(
        height=900,
        showlegend=True,
        hovermode='x unified',
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(t=80, b=80, l=60, r=60),
        xaxis_rangeslider_visible=False  # Hide rangeslider for cleaner look
    )
    
    # Update axes
    fig.update_xaxes(
        title_text="Date",
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        row=2, col=1
    )
    
    fig.update_yaxes(
        title_text="SPX Price",
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        row=1, col=1
    )
    
    fig.update_yaxes(
        title_text="BP / SP Value",
        range=[0.35, 0.65],
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        row=2, col=1
    )
    
    # Update subplot titles
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=14, color='black')
    
    return fig

# Header with logo and title
col1, col2 = st.columns([1, 4])
with col1:
    try:
        logo = Image.open("jcn_logo.jpg")
        st.image(logo, width=150)
    except:
        st.write("")

with col2:
    st.title("🛡️ Risk Management")
    st.markdown("Buying Power / Selling Pressure Analysis")

st.markdown("---")

# Load and display data
with st.spinner("Loading BPSP data from MotherDuck..."):
    df = load_bpsp_data()

if df is not None and not df.empty:
    st.success(f"✓ Loaded {len(df)} weeks of data (Last {YEARS_TO_DISPLAY} years)")
    
    # Create and display visualization
    with st.spinner("Creating visualization..."):
        fig = create_bpsp_visualization(df)
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        
        # Display current signal
        latest = df.iloc[-1]
        signal = "🟢 BULLISH (BP > SP)" if latest['Buying_Power'] > latest['Selling_Pressure'] else "🔴 BEARISH (SP > BP)"
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Signal", signal)
        with col2:
            st.metric("SPX Close", f"${latest['SPX_Close']:,.2f}")
        with col3:
            st.metric("Buying Power", f"{latest['Buying_Power']:.4f}")
        with col4:
            st.metric("Selling Pressure", f"{latest['Selling_Pressure']:.4f}")
        
        st.caption("📊 **Data Source**: MotherDuck NDR_BP_SP_history | Norgate Survivorship-Bias-Free (10,397 stocks, 1990-2025, including delisted)")
else:
    st.error("❌ Failed to load BPSP data from MotherDuck")

st.markdown("---")
st.caption("JCN Financial & Tax Advisory Group, LLC - Built with Streamlit")
