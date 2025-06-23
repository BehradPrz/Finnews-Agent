"""
Configuration module for Financial News Tracker
==============================================

Centralized configuration management for the financial news analysis application.
Handles environment variables, API settings, and application constants.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # API Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # News Sources Configuration
    ALLOWED_DOMAINS: List[str] = [
        "bloomberg.com",
        "cnbc.com",
        "reuters.com", 
        "marketwatch.com",
        "finance.yahoo.com",
        "wsj.com",
        "ft.com",
        "barrons.com",
        "investing.com",
        "seekingalpha.com",
        "fool.com",
        "benzinga.com"
    ]
    
    # Web Scraping Configuration
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    
    REQUEST_TIMEOUT: int = 10
    MAX_ARTICLES_PER_ASSET: int = 20
    
    # Analysis Configuration
    DEFAULT_ASSETS: List[str] = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
        "BTC-USD", "ETH-USD", "Gold", "Silver"
    ]
    
    SENTIMENT_OPTIONS: List[str] = ["Positive", "Negative", "Neutral"]
    IMPACT_LEVELS: List[str] = ["High", "Medium", "Low"]
    TIMEFRAMES: List[str] = ["Short-Term", "Medium-Term", "Long-Term"]    
    # UI Configuration
    APP_TITLE: str = "Financial News Impact Tracker"
    APP_ICON: str = "📈"
    
    # File Configuration
    CACHE_DIR: str = ".cache"
    EXPORT_DIR: str = "exports"
    
    @classmethod
    def has_openai_api(cls) -> bool:
        """Check if OpenAI API configuration is available"""
        return bool(cls.OPENAI_API_KEY)
    
    @classmethod
    def get_preferred_api_config(cls) -> dict:
        """Get the OpenAI API configuration"""
        if cls.OPENAI_API_KEY:
            return {
                "type": "openai",
                "api_key": cls.OPENAI_API_KEY
            }
        else:
            raise ValueError("No valid OpenAI API configuration found")
    
    @classmethod
    def validate_config(cls) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        if not cls.has_openai_api():
            issues.append("No OpenAI API key configured")
        
        if cls.DEBUG:
            issues.append("Debug mode is enabled (not recommended for production)")
        
        return issues

# Create global config instance
config = Config()

# Export commonly used constants
__all__ = [
    "config",
    "Config"
]
