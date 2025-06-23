"""
Financial News Tracker
======================

Main tracker class that orchestrates news scraping and analysis.
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime

from .config import config
from .models import AnalysisResult, AssetMetrics
from .scraper import FinancialNewsScraper
from .analyzer import AIAnalyzer
from .utils import Logger, validate_asset_symbols


class FinancialNewsTracker:
    """
    Main class for tracking and analyzing financial news impact on portfolios.
    
    This class orchestrates the entire process:
    1. Validates input assets
    2. Scrapes news from trusted sources
    3. Analyzes news with AI for sentiment and impact
    4. Generates portfolio-level insights and recommendations
    """
    
    def __init__(self):
        self.logger = Logger(__name__)
        self.scraper = FinancialNewsScraper()
        self.analyzer = AIAnalyzer()
        
        # Validate configuration on initialization
        config_issues = config.validate()
        if config_issues:
            for issue in config_issues:
                self.logger.warning(f"Configuration issue: {issue}")
    
    async def analyze_portfolio(
        self,
        assets: List[str],
        max_articles_per_asset: int = None,
        time_filter_days: int = 1
    ) -> AnalysisResult:
        """
        Analyze news impact for a portfolio of assets.
        
        Args:
            assets: List of asset symbols (stocks, crypto, commodities)
            max_articles_per_asset: Maximum articles to fetch per asset
            time_filter_days: Number of days back to search for news (1-7)
        
        Returns:
            AnalysisResult containing all analysis data
        
        Raises:
            ValueError: If input validation fails
            RuntimeError: If analysis fails completely
        """
        # Validate inputs
        if not assets:
            raise ValueError("At least one asset must be provided")
        
        # Clean and validate asset symbols
        validated_assets = validate_asset_symbols(assets)
        if not validated_assets:
            raise ValueError("No valid asset symbols provided")
        
        # Limit number of assets to prevent overload
        if len(validated_assets) > config.max_assets:
            self.logger.warning(f"Limiting analysis to {config.max_assets} assets")
            validated_assets = validated_assets[:config.max_assets]
        
        # Set defaults
        if max_articles_per_asset is None:
            max_articles_per_asset = config.max_articles_per_asset
        
        # Validate time filter
        min_days, max_days = config.time_filter_days_range
        if not (min_days <= time_filter_days <= max_days):
            self.logger.warning(f"Time filter adjusted to {min_days}-{max_days} days range")
            time_filter_days = max(min_days, min(time_filter_days, max_days))
        
        self.logger.info(f"Starting analysis for {len(validated_assets)} assets: {', '.join(validated_assets)}")
        
        try:
            # Step 1: Scrape news data
            self.logger.info("Scraping news data...")
            news_data = self.scraper.search_portfolio_news(
                assets=validated_assets,
                max_articles_per_asset=max_articles_per_asset,
                time_filter_days=time_filter_days
            )
            
            self.logger.info(f"Found {len(news_data)} news articles")
            
            # Step 2: Analyze news with AI
            self.logger.info("Analyzing news with AI...")
            news_entries, portfolio_analysis = await self.analyzer.analyze_portfolio_news(
                news_data=news_data,
                assets=validated_assets
            )
            
            # Step 3: Generate asset-level metrics
            asset_metrics = self._generate_asset_metrics(news_entries, validated_assets)
            
            # Step 4: Create final result
            result = AnalysisResult(
                assets_analyzed=validated_assets,
                news_entries=news_entries,
                portfolio_analysis=portfolio_analysis,
                asset_metrics=asset_metrics
            )
            
            self.logger.info(f"Analysis complete. Found {len(news_entries)} analyzed articles.")
            return result
            
        except Exception as e:
            self.logger.error(f"Portfolio analysis failed: {str(e)}")
            raise RuntimeError(f"Failed to analyze portfolio: {str(e)}")
    
    def _generate_asset_metrics(self, news_entries: List, validated_assets: List[str]) -> List[AssetMetrics]:
        """Generate per-asset metrics from news entries."""
        asset_metrics = []
        
        for asset in validated_assets:
            # Filter news for this asset
            asset_news = [entry for entry in news_entries if entry.asset == asset]
            
            if not asset_news:
                # No news found for this asset
                metrics = AssetMetrics(
                    asset=asset,
                    article_count=0,
                    dominant_sentiment="Neutral",
                    average_impact="Low",
                    average_confidence=0.0
                )
            else:
                # Calculate metrics
                sentiments = [entry.sentiment for entry in asset_news]
                impacts = [entry.impact_magnitude for entry in asset_news]
                confidences = [entry.confidence_score for entry in asset_news]
                
                # Find dominant sentiment
                sentiment_counts = {s: sentiments.count(s) for s in set(sentiments)}
                dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
                
                # Find average impact (simplified)
                impact_weights = {"High": 3, "Medium": 2, "Low": 1}
                avg_impact_weight = sum(impact_weights[i] for i in impacts) / len(impacts)
                
                if avg_impact_weight >= 2.5:
                    average_impact = "High"
                elif avg_impact_weight >= 1.5:
                    average_impact = "Medium"
                else:
                    average_impact = "Low"
                
                # Calculate average confidence
                average_confidence = sum(confidences) / len(confidences)
                
                metrics = AssetMetrics(
                    asset=asset,
                    article_count=len(asset_news),
                    dominant_sentiment=dominant_sentiment,
                    average_impact=average_impact,
                    average_confidence=round(average_confidence, 2)
                )
            
            asset_metrics.append(metrics)
        
        return asset_metrics
    
    def test_connectivity(self) -> Dict[str, bool]:
        """
        Test connectivity to various services.
        
        Returns:
            Dict with service names and their availability status
        """
        results = {}
        
        # Test news scraping
        try:
            test_results = self.scraper.search_news("AAPL", max_results=1, time_filter_days=1)
            results["news_scraping"] = len(test_results) > 0
        except Exception as e:
            self.logger.error(f"News scraping test failed: {str(e)}")
            results["news_scraping"] = False
        
        # Test AI analysis
        try:
            results["ai_analysis"] = self.analyzer.agents_enabled or config.ai.is_valid()
        except Exception as e:
            self.logger.error(f"AI analysis test failed: {str(e)}")
            results["ai_analysis"] = False
        
        return results
    
    def get_supported_assets(self) -> Dict[str, List[str]]:
        """
        Get examples of supported asset types.
        
        Returns:
            Dict with asset categories and examples
        """
        return {
            "stocks": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"],
            "crypto": ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD"],
            "commodities": ["Gold", "Silver", "Oil", "Copper"],
            "etfs": ["SPY", "QQQ", "VTI", "ARKK"],
            "indices": ["^GSPC", "^IXIC", "^DJI"]
        }
    
    async def quick_analysis(self, asset: str) -> AnalysisResult:
        """
        Perform a quick analysis on a single asset.
        
        Args:
            asset: Single asset symbol
        
        Returns:
            AnalysisResult for the single asset
        """
        return await self.analyze_portfolio(
            assets=[asset],
            max_articles_per_asset=3,
            time_filter_days=1
        )
