"""
Stock API endpoints
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/{symbol}")
async def get_stock(symbol: str):
    """Get stock information by symbol"""
    # TODO: Implement stock endpoint
    return {"message": f"Stock endpoint for {symbol} - Coming soon"}
