# Portfolio Cache Snapshots

This directory contains CSV snapshot files that serve as fallback data for the portfolio dashboards.

## Purpose

These snapshots ensure that the dashboards always have data to display, even when:
- Yahoo Finance API is rate-limited
- Network connectivity issues occur
- The app is first loaded without any cache

## Files

### Persistent Value Portfolio
- `persistent_value_snapshot.csv` - Latest portfolio data snapshot
- `persistent_value_timestamp.txt` - Timestamp of last snapshot update

### Olivia Growth Portfolio
- `olivia_growth_snapshot.csv` - Latest portfolio data snapshot
- `olivia_growth_timestamp.txt` - Timestamp of last snapshot update

## Update Strategy

1. **Automatic Updates**: Snapshots are automatically updated whenever fresh data is successfully fetched from Yahoo Finance
2. **Manual Updates**: Run `python3 generate_snapshots.py` from the project root to manually generate fresh snapshots
3. **Git Commits**: Updated snapshots should be committed to the repository to ensure all deployments have recent fallback data

## Data Structure

Each CSV snapshot contains the following columns:
- Security, Ticker, Cost Basis, Shares
- Cur Price, Position_Value
- Daily_Change_Pct, YTD_Pct, YoY_Pct, Port_Gain_Pct
- Pct_Below_52wk, Chan_Range
- Week_52_High, Week_52_Low
- Sector, Industry

## Fallback Hierarchy

The app uses this fallback hierarchy:
1. **Fresh Data** - Fetch from Yahoo Finance (preferred)
2. **JSON Cache** - Load from temporary cache file (15-minute expiry)
3. **CSV Snapshot** - Load from this directory (committed to repo)
4. **Error Message** - Only shown if all above fail

This ensures maximum availability and user experience!
