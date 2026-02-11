"""
Portfolio holdings data - matches original Streamlit app
"""

# Persistent Value Portfolio Holdings
PERSISTENT_VALUE_HOLDINGS = [
    {'symbol': 'SPMO', 'cost_basis': 97.40, 'shares': 14301},
    {'symbol': 'ASML', 'cost_basis': 660.32, 'shares': 1042},
    {'symbol': 'MNST', 'cost_basis': 50.01, 'shares': 8234},
    {'symbol': 'MSCI', 'cost_basis': 342.94, 'shares': 2016},
    {'symbol': 'COST', 'cost_basis': 655.21, 'shares': 798},
    {'symbol': 'AVGO', 'cost_basis': 138.00, 'shares': 6088},
    {'symbol': 'MA', 'cost_basis': 418.76, 'shares': 1389},
    {'symbol': 'FICO', 'cost_basis': 1850.00, 'shares': 778},
    {'symbol': 'SPGI', 'cost_basis': 427.93, 'shares': 1554},
    {'symbol': 'IDXX', 'cost_basis': 378.01, 'shares': 1570},
    {'symbol': 'ISRG', 'cost_basis': 322.50, 'shares': 1842},
    {'symbol': 'V', 'cost_basis': 276.65, 'shares': 2100},
    {'symbol': 'CAT', 'cost_basis': 287.70, 'shares': 2056},
    {'symbol': 'ORLY', 'cost_basis': 103.00, 'shares': 5000},
    {'symbol': 'HEI', 'cost_basis': 172.00, 'shares': 3000},
    {'symbol': 'CPRT', 'cost_basis': 52.00, 'shares': 10000},
    {'symbol': 'WM', 'cost_basis': 177.77, 'shares': 3000},
    {'symbol': 'TSLA', 'cost_basis': 270.00, 'shares': 2000},
    {'symbol': 'AAPL', 'cost_basis': 181.40, 'shares': 3000},
    {'symbol': 'LRCX', 'cost_basis': 73.24, 'shares': 7000},
    {'symbol': 'TSM', 'cost_basis': 99.61, 'shares': 5000},
]

# Olivia Growth Portfolio Holdings
OLIVIA_GROWTH_HOLDINGS = [
    {'symbol': 'AAPL', 'cost_basis': 150.00, 'shares': 1000},
    {'symbol': 'MSFT', 'cost_basis': 300.00, 'shares': 800},
    {'symbol': 'GOOGL', 'cost_basis': 120.00, 'shares': 500},
    {'symbol': 'AMZN', 'cost_basis': 140.00, 'shares': 600},
    {'symbol': 'NVDA', 'cost_basis': 400.00, 'shares': 400},
    {'symbol': 'META', 'cost_basis': 300.00, 'shares': 350},
    {'symbol': 'TSLA', 'cost_basis': 200.00, 'shares': 500},
]

# Pure Alpha Portfolio Holdings
PURE_ALPHA_HOLDINGS = [
    {'symbol': 'SPY', 'cost_basis': 400.00, 'shares': 500},
    {'symbol': 'QQQ', 'cost_basis': 350.00, 'shares': 400},
    {'symbol': 'IWM', 'cost_basis': 200.00, 'shares': 300},
]

def get_portfolio_holdings(portfolio_id: str):
    """Get holdings for a specific portfolio"""
    holdings_map = {
        'persistent_value': PERSISTENT_VALUE_HOLDINGS,
        'olivia_growth': OLIVIA_GROWTH_HOLDINGS,
        'pure_alpha': PURE_ALPHA_HOLDINGS,
    }
    return holdings_map.get(portfolio_id, [])
