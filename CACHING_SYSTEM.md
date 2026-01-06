# Portfolio Data Caching System

## Overview

The JCN Dashboard now includes an intelligent caching system that solves the Yahoo Finance API rate limiting issues while providing instant page loads and always-available data.

## How It Works

### 1. Cache Storage
- All portfolio data is saved to `portfolio_cache.json` after each successful fetch
- Includes timestamp for tracking data freshness
- Stores all 14 columns of portfolio metrics

### 2. Smart Loading Logic

**On Page Load:**
- First checks if cache file exists
- If cache exists: Loads instantly from cache (no API calls)
- If no cache: Fetches fresh data from Yahoo Finance

**Refresh Button:**
- User clicks "🔄 Refresh Data" button
- Forces fresh data fetch from Yahoo Finance API
- Updates cache with new data
- Shows "✅ Fresh data loaded successfully!" message

**Auto-Refresh (15 minutes):**
- Automatically fetches fresh data every 15 minutes
- Updates cache silently in background
- Ensures data stays reasonably current

**Rate Limit Protection:**
- If API rate limit is hit during fetch
- Automatically falls back to cached data
- Shows "⚠️ Rate limit reached. Loading from cache..." message
- No errors or blank screens

### 3. User Experience

**Status Messages:**
- 📦 "Loading from cache (click Refresh Data for latest prices)" - Using cached data
- ✅ "Fresh data loaded successfully!" - Just fetched new data from API
- ⚠️ "Rate limit reached. Loading from cache..." - API limit hit, using cache

**Timestamp Display:**
- Shows "Last Updated: HH:MM:SS AM/PM"
- Indicates when data was last fetched
- Source always shows "Yahoo Finance (Cached)"

## Benefits

### 1. No More Rate Limit Errors
- App never shows errors when API limits are hit
- Always displays last known good data
- Users can continue working without interruption

### 2. Instant Page Loads
- Cache loads in < 1 second
- No waiting for 21 API calls (10-15 seconds)
- Better user experience

### 3. Reduced API Usage
- Only fetches when needed (manual refresh or 15 min interval)
- Saves API quota
- More sustainable long-term

### 4. Always Available
- Data persists even if Yahoo Finance is down
- Works offline with cached data
- Reliable for production use

## Technical Details

### Cache File Format
```json
{
  "timestamp": "2026-01-06T09:56:24.123456",
  "data": [
    {
      "Security": "Invesco S&P 500 Momentum ETF",
      "Ticker": "SPMO",
      "Cost Basis": 97.40,
      "Shares": 14301,
      "Cur Price": 119.67,
      "Position_Value": 1711234.67,
      "Daily_Change_Pct": -0.04,
      "YTD_Pct": 0.59,
      "YoY_Pct": 24.39,
      "Port_Gain_Pct": 22.86,
      "Pct_Below_52wk": -3.69,
      "Chan_Range": 90.14,
      "Sector": "N/A",
      "Industry": "N/A"
    },
    ...
  ]
}
```

### Rate Limiting
- 0.5 second delay between each stock fetch
- Prevents "Too Many Requests" errors
- Total fetch time: ~10-15 seconds for 21 stocks

### Error Handling
- Silent error handling (no warnings shown to user)
- Returns None on failure
- Triggers cache fallback automatically

## Deployment Notes

### Streamlit Cloud
- Cache file persists in app's working directory
- Survives app reboots
- Automatically created on first run

### Updates
- When you reboot the app on Streamlit Cloud
- Cache is preserved
- App loads instantly with cached data
- First user to click Refresh will populate fresh data

## Future Enhancements

Potential improvements:
1. Add cache expiration (e.g., 24 hours)
2. Store multiple cache versions
3. Add cache statistics dashboard
4. Implement Redis for production caching
5. Add manual cache clear button

## Maintenance

The cache file is automatically managed:
- Created on first successful fetch
- Updated on each refresh
- No manual intervention needed

If you need to clear cache:
```bash
rm portfolio_cache.json
```

## Summary

The caching system provides:
- ✅ Instant page loads
- ✅ Rate limit protection
- ✅ Always-available data
- ✅ Better user experience
- ✅ Reduced API usage
- ✅ Production-ready reliability

Last Updated: January 6, 2026
