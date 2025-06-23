"""
Utility Functions
================

Common utility functions and classes.
"""

import time
import logging
from typing import Optional
from datetime import datetime


class Logger:
    """Simple logging wrapper."""
    
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, delay: float = 1.0):
        self.delay = delay
        self.last_call: Optional[float] = None
    
    def wait(self):
        """Wait if necessary to respect rate limits."""
        now = time.time()
        
        if self.last_call is not None:
            elapsed = now - self.last_call
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)
        
        self.last_call = time.time()


def format_timestamp(date_str: Optional[str] = None) -> str:
    """Convert various date formats to ISO format."""
    if not date_str:
        return datetime.utcnow().isoformat()
    
    # For now, just return ISO format
    # Can be extended with more sophisticated parsing
    try:
        # Try to parse and reformat
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.isoformat()
    except:
        return datetime.utcnow().isoformat()


def validate_asset_symbols(assets: list) -> list:
    """Validate and clean asset symbols."""
    valid_assets = []
    
    for asset in assets:
        if isinstance(asset, str) and asset.strip():
            # Clean and validate the asset symbol
            cleaned = asset.strip().upper()
            if len(cleaned) >= 1 and len(cleaned) <= 10:  # Reasonable length check
                valid_assets.append(cleaned)
    
    return valid_assets


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
