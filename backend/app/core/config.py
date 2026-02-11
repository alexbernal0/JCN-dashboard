"""
Configuration settings for the FastAPI application
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "JCN Dashboard API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.railway.app",
        "https://*.up.railway.app",
    ]
    
    # Cache settings
    CACHE_TTL: int = 300  # 5 minutes
    
    # MotherDuck settings
    MOTHERDUCK_TOKEN: str = os.getenv("MOTHERDUCK_TOKEN", "")
    
    # Stock data settings
    PERSISTENT_VALUE_STOCKS: List[str] = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META",
        "NVDA", "TSLA", "JPM", "V", "WMT",
        "JNJ", "PG", "MA", "HD", "DIS",
        "BAC", "ADBE", "CRM", "NFLX", "INTC", "CSCO"
    ]
    
    OLIVIA_GROWTH_STOCKS: List[str] = [
        "NVDA", "TSLA", "AMD", "PLTR", "SNOW",
        "CRWD", "NET", "DDOG", "ZS", "OKTA",
        "PANW", "FTNT", "MDB", "TEAM", "ZM"
    ]
    
    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings()
