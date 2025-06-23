"""
Configuration Module
===================

Centralized configuration management for the Financial News Tracker.
"""

import os
import re
from typing import List, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class NewsConfig:
    """Configuration for news scraping and analysis."""
    
    # Trusted financial news sources
    allowed_domains: List[str] = field(default_factory=lambda: [
        "bloomberg.com",
        "cnbc.com", 
        "reuters.com",
        "marketwatch.com",
        "finance.yahoo.com",
        "wsj.com",
        "ft.com",
        "barrons.com",
        "investing.com",
        "seekingalpha.com"
    ])
    
    # Web scraping settings
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
    
    # Rate limiting
    default_request_delay: float = 1.0
    max_retries: int = 3
    backoff_multiplier: int = 2
    request_timeout: int = 8
    
    # Domain pattern for URL parsing
    domain_pattern: re.Pattern = field(default_factory=lambda: re.compile(r"https?://(?:www\.)?([^/]+)/", re.I))


@dataclass 
class AIConfig:
    """Configuration for AI analysis."""
    
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    max_tokens: int = 2000
    
    def is_valid(self) -> bool:
        """Check if AI configuration is valid."""
        return bool(self.openai_api_key)


@dataclass
class AppConfig:
    """Main application configuration."""
    
    # Core configurations
    news: NewsConfig = field(default_factory=NewsConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    
    # App settings
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")
    max_assets: int = 10
    max_articles_per_asset: int = 5
    time_filter_days_range: tuple = (1, 7)
    
    # UI settings
    app_title: str = "📈 Financial News Impact Tracker"
    page_icon: str = "📈"
    
    def validate(self) -> List[str]:
        """Validate configuration and return any issues."""
        issues = []
        
        if not self.ai.is_valid():
            issues.append("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        if self.max_assets < 1:
            issues.append("max_assets must be at least 1")
            
        if self.max_articles_per_asset < 1:
            issues.append("max_articles_per_asset must be at least 1")
            
        return issues


# Global configuration instance
config = AppConfig()
