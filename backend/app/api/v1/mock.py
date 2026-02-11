"""
Mock API endpoints for development
"""

from fastapi import APIRouter
from app.services.mock_data import generate_mock_portfolio_data, generate_mock_stock_data

router = APIRouter()

@router.get("/portfolios")
async def list_mock_portfolios():
    """Get list of mock portfolios"""
    return [
        {
            "id": "persistent_value",
            "name": "Persistent Value Portfolio",
            "description": "Value-focused investment strategy (Mock Data)"
        },
        {
            "id": "olivia_growth",
            "name": "Olivia Growth Portfolio",
            "description": "Growth-focused technology stocks (Mock Data)"
        }
    ]

@router.get("/portfolios/{portfolio_id}")
async def get_mock_portfolio(portfolio_id: str):
    """Get mock portfolio data"""
    portfolio_names = {
        "persistent_value": "Persistent Value Portfolio",
        "olivia_growth": "Olivia Growth Portfolio"
    }
    
    if portfolio_id not in portfolio_names:
        return {"error": "Portfolio not found"}, 404
    
    return generate_mock_portfolio_data(portfolio_id, portfolio_names[portfolio_id])

@router.get("/stocks/{symbol}")
async def get_mock_stock(symbol: str):
    """Get mock stock data"""
    return generate_mock_stock_data(symbol.upper())
