"""
Portfolio API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.portfolio import PortfolioSummary
from app.services.portfolio_service import portfolio_service

router = APIRouter()

@router.get("/", response_model=List[dict])
async def list_portfolios():
    """Get list of available portfolios"""
    return await portfolio_service.get_portfolio_list()

@router.get("/{portfolio_id}", response_model=PortfolioSummary)
async def get_portfolio(portfolio_id: str):
    """Get portfolio summary by ID"""
    try:
        return await portfolio_service.get_portfolio_summary(portfolio_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
