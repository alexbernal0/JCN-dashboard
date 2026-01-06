# Demo Stock App Analysis

## Key Findings

### UI Components Observed:
1. **Stock Ticker Input**: Multi-select dropdown with removable tags (AAPL, MSFT, GOOGL, NVDA, AMZN, TSLA, META)
2. **Time Horizon Buttons**: 1 Months, 3 Months, 6 Months, 1 Year, 5 Years, 10 Years, 20 Years
3. **Best/Worst Stock Display**: Shows top performer (GOOGL +179%) and worst performer (META +92%)
4. **Chart**: Normalized price chart showing multiple stocks over time

### Technical Implementation:
- **Charting Library**: Likely Plotly (standard for Streamlit financial apps) or Altair
- **Data Source**: Most likely **yfinance** library (Yahoo Finance) - the standard for free stock data
- **Color Scheme**: Dark theme with colored lines for different stocks
- **Normalization**: Prices are normalized to starting value (1.0) to compare relative performance

### For JCN Dashboard Implementation:
1. Use **yfinance** library to fetch stock data
2. Use **Plotly** for interactive charts (already in requirements.txt)
3. Implement multi-select for stock tickers
4. Add time horizon buttons
5. Normalize prices for comparison
6. Use white/light theme instead of dark theme
7. Add JCN logo to header
