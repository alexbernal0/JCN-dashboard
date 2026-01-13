import streamlit as st
from PIL import Image
import duckdb
import os

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
        
        # Placeholder for additional modules
        st.info("📊 Additional analysis modules will be added below")
        
    else:
        st.error(f"❌ No data found for ticker '{current_ticker}' in MotherDuck database.")
        st.info("💡 Make sure the ticker exists in the GuruFocusData table.")
else:
    st.info("👆 Enter a stock ticker above to begin analysis")

st.markdown("---")
st.caption("JCN Financial & Tax Advisory Group, LLC - Built with Streamlit")
