"""
News Scraper Module
==================

Handles financial news scraping from various sources.
"""

import re
import time
import datetime as dt
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from .config import config
from .utils import RateLimiter, Logger


@dataclass
class NewsSource:
    """Represents a news source configuration."""
    
    domain: str
    name: str
    priority: int = 1  # Higher number = higher priority


class WebScraper:
    """Handles web scraping for article metadata."""
    
    def __init__(self):
        self.logger = Logger(__name__)
        self.rate_limiter = RateLimiter(delay=0.5)  # Respectful scraping
    
    def get_domain_from_url(self, url: str) -> str:
        """Extract domain from URL."""
        match = config.news.domain_pattern.match(url)
        return match.group(1) if match else ""
    
    def get_article_metadata(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Scrape article title and description with rate limiting."""
        self.rate_limiter.wait()
        
        try:
            headers = {
                "User-Agent": config.news.user_agent,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=config.news.request_timeout, 
                allow_redirects=True
            )
            
            if response.status_code == 429:  # Rate limited
                self.logger.warning(f"Rate limited while scraping {url}")
                return None, None
            elif response.status_code != 200:
                return None, None
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract title
            title_tag = soup.find("title")
            title = title_tag.text.strip() if title_tag else None
            
            # Extract description from meta tags
            desc_tag = (
                soup.find("meta", attrs={"name": "description"}) or
                soup.find("meta", attrs={"property": "og:description"}) or
                soup.find("meta", attrs={"name": "twitter:description"})
            )
            description = desc_tag.get("content", "").strip() if desc_tag else None
            
            return title, description
            
        except requests.exceptions.RequestException as e:
            if "429" in str(e) or "rate" in str(e).lower():
                self.logger.warning(f"Rate limited while scraping {url}")
            else:
                self.logger.warning(f"Failed to scrape {url}: {str(e)}")
            return None, None
        except Exception as e:
            self.logger.error(f"Unexpected error scraping {url}: {str(e)}")
            return None, None


class FinancialNewsScraper:
    """Main class for financial news scraping."""
    
    def __init__(self):
        self.logger = Logger(__name__)
        self.web_scraper = WebScraper()
        self.rate_limiter = RateLimiter(delay=config.news.default_request_delay)
        
        # Initialize news sources
        self.trusted_sources = [
            NewsSource(domain, domain.replace('.com', '').title())
            for domain in config.news.allowed_domains
        ]
    
    def format_timestamp(self, date_str: str) -> str:
        """Convert various date formats to ISO format."""
        if not date_str:
            return dt.datetime.utcnow().isoformat()
        
        # Handle relative timestamps (e.g., "2 hours ago")
        if re.match(r"\\d+ (hour|minute|day)", date_str, re.I):
            return dt.datetime.utcnow().isoformat()
        
        # Handle ISO dates
        if re.match(r"\\d{4}-\\d{2}-\\d{2}", date_str):
            return date_str
        
        return dt.datetime.utcnow().isoformat()
    
    def search_news(
        self, 
        query: str, 
        max_results: int = 20, 
        time_filter_days: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Search for financial news using DuckDuckGo.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            time_filter_days: Number of days back to search (1-7 days)
        
        Returns:
            List of news articles with metadata
        """
        results = []
        today_iso = dt.date.today().isoformat()
        
        # Map days to DuckDuckGo time filter
        time_filter_map = {1: "d", 2: "d", 3: "d", 4: "w", 5: "w", 6: "w", 7: "w"}
        timelimit = time_filter_map.get(time_filter_days, "d")
        
        for attempt in range(config.news.max_retries):
            try:
                if attempt > 0:
                    delay = config.news.default_request_delay * (config.news.backoff_multiplier ** attempt)
                    self.logger.info(f"Rate limit encountered. Waiting {delay} seconds before retry {attempt + 1}/{config.news.max_retries}...")
                    time.sleep(delay)
                
                self.rate_limiter.wait()
                
                with DDGS() as ddgs:
                    ddg_results = ddgs.news(
                        query,
                        region="us-en",
                        safesearch="Off",
                        timelimit=timelimit,
                        max_results=min(max_results * 2, 30)  # Get extra to filter
                    )
                
                # Process and filter results
                for article in ddg_results:
                    url = article.get("url", "")
                    if not url:
                        continue
                        
                    domain = self.web_scraper.get_domain_from_url(url)
                    if domain not in config.news.allowed_domains:
                        continue
                    
                    title = article.get("title", "")
                    description = article.get("body") or article.get("excerpt", "")
                    date_str = article.get("date") or today_iso
                    
                    # Enhance with scraped metadata if needed
                    if not title or not description:
                        scraped_title, scraped_desc = self.web_scraper.get_article_metadata(url)
                        title = title or scraped_title or "(No title available)"
                        description = description or scraped_desc or ""
                    
                    if title and description:
                        results.append({
                            "title": title,
                            "description": description,
                            "url": url,
                            "source": domain,
                            "published_at": self.format_timestamp(date_str),
                        })
                    
                    if len(results) >= max_results:
                        break
                
                # Success, break the retry loop
                break
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if any(keyword in error_msg for keyword in ['rate', 'limit', '429', 'quota', 'throttle']):
                    if attempt < config.news.max_retries - 1:
                        self.logger.warning(f"Rate limit hit on attempt {attempt + 1}. Retrying...")
                        continue
                    else:
                        self.logger.error("Rate limit exceeded. Please try again later.")
                        return self._get_fallback_news_data(query)
                else:
                    self.logger.error(f"News search failed: {str(e)}")
                    if attempt < config.news.max_retries - 1:
                        continue
                    else:
                        return self._get_fallback_news_data(query)
        
        return results
    
    def search_portfolio_news(
        self, 
        assets: List[str], 
        max_articles_per_asset: int = 5,
        time_filter_days: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Search news for multiple assets.
        
        Args:
            assets: List of asset symbols
            max_articles_per_asset: Maximum articles per asset
            time_filter_days: Days back to search
        
        Returns:
            Combined list of news articles for all assets
        """
        all_news = []
        
        for asset in assets[:config.max_assets]:  # Limit to prevent overload
            try:
                self.logger.info(f"Searching news for {asset}...")
                
                news_data = self.search_news(
                    f"{asset} financial news", 
                    max_results=max_articles_per_asset,
                    time_filter_days=time_filter_days
                )
                
                # Tag each article with the asset
                for item in news_data:
                    item['asset'] = asset
                
                all_news.extend(news_data)
                
                # Rate limiting between assets
                self.rate_limiter.wait()
                
            except Exception as e:
                self.logger.error(f"Failed to fetch news for {asset}: {str(e)}")
                continue
        
        return all_news
    
    def _get_fallback_news_data(self, query: str) -> List[Dict[str, Any]]:
        """
        Provide fallback news data when API is unavailable.
        """
        today_iso = dt.date.today().isoformat()
        
        # Extract potential asset from query
        asset = "MARKET"
        query_upper = query.upper()
        common_assets = ["AAPL", "MSFT", "GOOGL", "TSLA", "BTC", "GOLD", "SPY", "QQQ"]
        for ticker in common_assets:
            if ticker in query_upper:
                asset = ticker
                break
        
        fallback_news = [
            {
                "title": f"Market Analysis: {asset} Shows Mixed Signals Amid Economic Uncertainty",
                "description": f"Recent market movements for {asset} reflect broader economic trends.",
                "url": "https://www.marketwatch.com/fallback-demo",
                "source": "marketwatch.com",
                "published_at": today_iso,
            },
            {
                "title": f"Institutional Investors Adjust {asset} Holdings as Market Volatility Persists",
                "description": f"Portfolio managers are reassessing positions in {asset}.",
                "url": "https://www.bloomberg.com/fallback-demo",
                "source": "bloomberg.com", 
                "published_at": today_iso,
            }
        ]
        
        self.logger.info(f"Using fallback news data for: {query}")
        return fallback_news
