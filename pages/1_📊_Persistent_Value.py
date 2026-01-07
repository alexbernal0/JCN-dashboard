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
import finnhub
import requests

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
