"""
Data Models
===========

Pydantic models for structured data validation.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class NewsEntry(BaseModel):
    """Structured news entry with validation."""
    
    asset: str = Field(..., description="Stock ticker, crypto, or commodity symbol")
    title: str = Field(..., max_length=500, description="News headline")
    summary: str = Field(..., description="AI-generated summary of the article")
    source: str = Field(..., description="News source domain")
    url: str = Field(..., description="Article URL")
    published_at: str = Field(..., description="Publication timestamp (ISO format)")
    sentiment: str = Field(..., pattern="^(Positive|Negative|Neutral)$", description="News sentiment")
    impact_timeframe: str = Field(..., pattern="^(Short|Medium|Long)-Term$", description="Expected impact duration")
    impact_magnitude: str = Field(..., pattern="^(High|Medium|Low)$", description="Impact severity")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="AI confidence in analysis")
    
    @validator('published_at')
    def validate_published_at(cls, v):
        """Ensure published_at is a valid ISO format string."""
        if not v:
            return datetime.utcnow().isoformat()
        return v
    
    @validator('title', 'summary')
    def validate_text_fields(cls, v):
        """Ensure text fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Text fields cannot be empty")
        return v.strip()


class PortfolioAnalysis(BaseModel):
    """Portfolio-level analysis results."""
    
    total_articles: int = Field(..., ge=0, description="Number of articles analyzed")
    high_impact_count: int = Field(..., ge=0, description="Number of high-impact news items")
    overall_sentiment: str = Field(..., pattern="^(Bullish|Bearish|Neutral)$")
    risk_level: str = Field(..., pattern="^(High|Medium|Low)$")
    key_concerns: List[str] = Field(default_factory=list, description="Main risk factors identified")
    opportunities: List[str] = Field(default_factory=list, description="Potential opportunities")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    
    @validator('high_impact_count')
    def validate_high_impact_count(cls, v, values):
        """Ensure high_impact_count doesn't exceed total_articles."""
        if 'total_articles' in values and v > values['total_articles']:
            raise ValueError("high_impact_count cannot exceed total_articles")
        return v


class AssetMetrics(BaseModel):
    """Metrics for individual assets."""
    
    asset: str = Field(..., description="Asset symbol")
    article_count: int = Field(..., ge=0, description="Number of articles found")
    dominant_sentiment: str = Field(..., pattern="^(Positive|Negative|Neutral)$")
    average_impact: str = Field(..., pattern="^(High|Medium|Low)$")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence score")


class AnalysisResult(BaseModel):
    """Complete analysis result container."""
    
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    assets_analyzed: List[str] = Field(..., description="List of assets that were analyzed")
    news_entries: List[NewsEntry] = Field(default_factory=list)
    portfolio_analysis: PortfolioAnalysis
    asset_metrics: List[AssetMetrics] = Field(default_factory=list)
    
    @property
    def summary_stats(self) -> dict:
        """Generate summary statistics."""
        return {
            "total_assets": len(self.assets_analyzed),
            "total_articles": len(self.news_entries),
            "high_impact_articles": sum(1 for entry in self.news_entries if entry.impact_magnitude == "High"),
            "sentiment_distribution": {
                sentiment: sum(1 for entry in self.news_entries if entry.sentiment == sentiment)
                for sentiment in ["Positive", "Negative", "Neutral"]
            }
        }
