"""
AI Analysis Module
=================

Handles AI-powered news analysis using OpenAI.
"""

import json
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from openai import AsyncOpenAI

try:
    from agents import (
        Agent,
        Runner,
        function_tool,
        set_default_openai_api,
        set_default_openai_client,
        set_tracing_disabled,
    )
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

from .config import config
from .models import NewsEntry, PortfolioAnalysis, AssetMetrics
from .utils import Logger, format_timestamp


class AIAnalyzer:
    """Handles AI-powered news analysis."""
    
    def __init__(self):
        self.logger = Logger(__name__)
        self.client: Optional[AsyncOpenAI] = None
        self.agents_enabled = AGENTS_AVAILABLE and config.ai.is_valid()
        
        if config.ai.is_valid():
            self._setup_openai_client()
    
    def _setup_openai_client(self) -> bool:
        """Configure OpenAI client."""
        try:
            self.client = AsyncOpenAI(api_key=config.ai.openai_api_key)
            
            if AGENTS_AVAILABLE:
                set_default_openai_client(client=self.client, use_for_tracing=False)
                set_default_openai_api("chat_completions")
                set_tracing_disabled(disabled=True)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup OpenAI client: {str(e)}")
            return False
    
    @function_tool
    def get_market_context(self, assets: List[str]) -> str:
        """Provide general market context for given assets."""
        return f"""
        Current Market Context for Portfolio Assets: {', '.join(assets)}
        
        Analysis Date: {format_timestamp()}
        
        Key Market Factors to Consider:
        - Federal Reserve policy and interest rate environment
        - Global economic indicators and GDP growth
        - Geopolitical events and trade relations
        - Sector-specific trends and regulatory changes
        - Currency fluctuations and commodity prices
        """
    
    def create_analysis_agent(self) -> Agent:
        """Create the news analysis agent."""
        if not AGENTS_AVAILABLE:
            raise RuntimeError("OpenAI Agents SDK not available")
        
        instructions = """
        You are a professional financial news analyst with expertise in market impact assessment.
        
        Your responsibilities:
        1. Analyze financial news for market impact and sentiment
        2. Provide structured analysis with confidence scores
        3. Focus on actionable insights for investors
        
        When analyzing news:
        - Consider both direct and indirect impacts on assets
        - Assess short-term vs long-term implications
        - Evaluate sentiment objectively (Positive/Negative/Neutral)
        - Provide confidence scores based on source credibility and clarity
        - Use impact magnitudes: High/Medium/Low
        - Use timeframes: Short-Term/Medium-Term/Long-Term
        
        Always return valid JSON that matches the required schema.
        Be precise, objective, and focus on investment-relevant information.
        """
        
        return Agent(
            name="Financial News Analyst",
            instructions=instructions,
            tools=[self.get_market_context],
            model=config.ai.model
        )
    
    def create_portfolio_agent(self) -> Agent:
        """Create portfolio analysis agent."""
        if not AGENTS_AVAILABLE:
            raise RuntimeError("OpenAI Agents SDK not available")
        
        instructions = """
        You are a portfolio risk analyst specializing in news-driven market analysis.
        
        Your role:
        1. Synthesize individual news impacts into portfolio-level insights
        2. Identify key risks and opportunities  
        3. Provide actionable recommendations
        4. Assess overall portfolio sentiment (Bullish/Bearish/Neutral) and risk level
        
        Focus on:
        - Portfolio diversification impact
        - Sector concentration risks
        - Market timing considerations
        - Risk management strategies
        
        Provide clear, actionable recommendations for portfolio management.
        """
        
        return Agent(
            name="Portfolio Risk Analyst",
            instructions=instructions,
            tools=[self.get_market_context],
            model=config.ai.model
        )
    
    async def analyze_news_with_agents(
        self, 
        news_data: List[Dict[str, Any]], 
        assets: List[str]
    ) -> Tuple[List[NewsEntry], PortfolioAnalysis]:
        """Analyze news using OpenAI Agents."""
        if not self.agents_enabled:
            raise RuntimeError("Agents not available or not configured")
        
        try:
            # Create analysis agent
            analysis_agent = Agent(
                name="Financial News Analyzer",
                instructions="""
                Analyze the provided financial news data and return structured JSON.
                
                Return a JSON object with:
                1. "news_entries": Array of analyzed news items
                2. "portfolio_analysis": Overall portfolio assessment
                
                Each news entry must have: asset, title, summary, source, url, published_at, 
                sentiment (Positive/Negative/Neutral), impact_timeframe (Short-Term/Medium-Term/Long-Term), 
                impact_magnitude (High/Medium/Low), confidence_score (0.0-1.0)
                
                Portfolio analysis must have: total_articles, high_impact_count, 
                overall_sentiment (Bullish/Bearish/Neutral), risk_level (High/Medium/Low), 
                key_concerns, opportunities, recommendations (all as arrays)
                
                Be concise and return valid JSON only.
                """,
                model=config.ai.model
            )
            
            # Prepare news summary
            news_summary = "\\n".join([
                f"Asset: {item['asset']}, Title: {item['title']}, Description: {item['description'][:200]}..."
                for item in news_data[:15]  # Limit to prevent token overflow
            ])
            
            analysis_prompt = f"""
            Analyze this financial news data for portfolio assets: {', '.join(assets)}
            
            News Data:
            {news_summary}
            
            Return JSON with this exact structure:
            {{
                "news_entries": [
                    {{
                        "asset": "AAPL",
                        "title": "Title",
                        "summary": "Impact summary",
                        "source": "source.com",
                        "url": "https://...",
                        "published_at": "{format_timestamp()}",
                        "sentiment": "Positive",
                        "impact_timeframe": "Medium-Term",
                        "impact_magnitude": "High",
                        "confidence_score": 0.85
                    }}
                ],
                "portfolio_analysis": {{
                    "total_articles": {len(news_data)},
                    "high_impact_count": 0,
                    "overall_sentiment": "Bullish",
                    "risk_level": "Medium",
                    "key_concerns": ["concern1", "concern2"],
                    "opportunities": ["opportunity1", "opportunity2"],
                    "recommendations": ["recommendation1", "recommendation2"]
                }}
            }}
            """
            
            # Run analysis with timeout
            result = await asyncio.wait_for(
                Runner.run(analysis_agent, analysis_prompt),
                timeout=60
            )
            
            # Parse results
            response_text = result.final_output if hasattr(result, 'final_output') else str(result)
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                analysis_data = json.loads(response_text[json_start:json_end])
                
                # Validate and create objects
                news_entries = []
                for item in analysis_data.get('news_entries', []):
                    try:
                        normalized_item = self._normalize_news_entry(item)
                        entry = NewsEntry.model_validate(normalized_item)
                        news_entries.append(entry)
                    except Exception as e:
                        self.logger.warning(f"Skipping invalid news entry: {str(e)}")
                        continue
                
                portfolio_analysis = PortfolioAnalysis.model_validate(
                    analysis_data.get('portfolio_analysis', {})
                )
                
                return news_entries, portfolio_analysis
            
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            self.logger.error(f"Agent analysis failed: {str(e)}")
            raise
    
    def analyze_news_simple(
        self, 
        news_data: List[Dict[str, Any]], 
        assets: List[str]
    ) -> Tuple[List[NewsEntry], PortfolioAnalysis]:
        """Simple news analysis without agents."""
        self.logger.info("Using simplified analysis mode...")
        
        if not news_data:
            return self._get_fallback_analysis(assets)
        
        # Create news entries with basic sentiment analysis
        news_entries = []
        
        for item in news_data[:15]:  # Limit processing
            try:
                # Simple sentiment analysis based on keywords
                text = (item.get('title', '') + ' ' + item.get('description', '')).lower()
                
                if any(word in text for word in ['gain', 'up', 'rise', 'positive', 'growth', 'bull']):
                    sentiment = "Positive"
                elif any(word in text for word in ['fall', 'down', 'drop', 'negative', 'decline', 'bear']):
                    sentiment = "Negative"
                else:
                    sentiment = "Neutral"
                
                # Determine impact based on keywords
                if any(word in text for word in ['major', 'significant', 'huge', 'massive', 'breaking']):
                    magnitude = "High"
                elif any(word in text for word in ['minor', 'slight', 'small']):
                    magnitude = "Low"
                else:
                    magnitude = "Medium"
                
                entry = NewsEntry(
                    asset=item.get('asset', 'MARKET'),
                    title=item.get('title', 'Market Update')[:200],
                    summary=f"News impact analysis for {item.get('asset', 'market')} based on recent developments.",
                    source=item.get('source', 'financial-news.com'),
                    url=item.get('url', 'https://example.com'),
                    published_at=item.get('published_at', format_timestamp()),
                    sentiment=sentiment,
                    impact_timeframe="Medium-Term",
                    impact_magnitude=magnitude,
                    confidence_score=0.6  # Lower confidence for simple analysis
                )
                news_entries.append(entry)
                
            except Exception as e:
                self.logger.warning(f"Failed to create news entry: {str(e)}")
                continue
        
        # Create portfolio analysis
        high_impact_count = sum(1 for entry in news_entries if entry.impact_magnitude == "High")
        positive_count = sum(1 for entry in news_entries if entry.sentiment == "Positive")
        negative_count = sum(1 for entry in news_entries if entry.sentiment == "Negative")
        
        if positive_count > negative_count:
            overall_sentiment = "Bullish"
        elif negative_count > positive_count:
            overall_sentiment = "Bearish"
        else:
            overall_sentiment = "Neutral"
        
        risk_level = "High" if high_impact_count > 2 else "Medium" if high_impact_count > 0 else "Low"
        
        portfolio_analysis = PortfolioAnalysis(
            total_articles=len(news_entries),
            high_impact_count=high_impact_count,
            overall_sentiment=overall_sentiment,
            risk_level=risk_level,
            key_concerns=[
                "Market volatility based on recent news",
                "Asset-specific developments requiring monitoring"
            ],
            opportunities=[
                "Potential market corrections for entry points",
                "Diversification opportunities across assets"
            ],
            recommendations=[
                "Monitor news developments closely",
                "Consider position sizing based on sentiment",
                "Maintain diversified portfolio approach"
            ]
        )
        
        return news_entries, portfolio_analysis
    
    async def analyze_portfolio_news(
        self, 
        news_data: List[Dict[str, Any]], 
        assets: List[str]
    ) -> Tuple[List[NewsEntry], PortfolioAnalysis]:
        """Main analysis method that tries agents first, falls back to simple analysis."""
        if not news_data:
            return self._get_fallback_analysis(assets)
        
        # Try agents first if available
        if self.agents_enabled:
            try:
                return await self.analyze_news_with_agents(news_data, assets)
            except Exception as e:
                self.logger.warning(f"Agent analysis failed: {str(e)}. Falling back to simple analysis.")
        
        # Fall back to simple analysis
        return self.analyze_news_simple(news_data, assets)
    
    def _normalize_news_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize news entry data to match Pydantic model requirements."""
        normalized = data.copy()
        
        # Fix impact_timeframe format
        if 'impact_timeframe' in normalized:
            timeframe = normalized['impact_timeframe']
            if timeframe in ['Short', 'Medium', 'Long']:
                normalized['impact_timeframe'] = f"{timeframe}-Term"
            elif timeframe not in ['Short-Term', 'Medium-Term', 'Long-Term']:
                normalized['impact_timeframe'] = "Medium-Term"
        
        # Fix sentiment format
        if 'sentiment' in normalized:
            sentiment = normalized['sentiment']
            if sentiment not in ['Positive', 'Negative', 'Neutral']:
                normalized['sentiment'] = "Neutral"
        
        # Fix impact_magnitude format
        if 'impact_magnitude' in normalized:
            magnitude = normalized['impact_magnitude']
            if magnitude not in ['High', 'Medium', 'Low']:
                normalized['impact_magnitude'] = "Medium"
        
        # Ensure confidence_score is in valid range
        if 'confidence_score' in normalized:
            score = normalized['confidence_score']
            if not isinstance(score, (int, float)) or score < 0 or score > 1:
                normalized['confidence_score'] = 0.7
        
        # Set defaults for required fields
        normalized.setdefault('asset', 'MARKET')
        normalized.setdefault('title', 'Market Update')
        normalized.setdefault('summary', 'News analysis summary')
        normalized.setdefault('source', 'financial-news.com')
        normalized.setdefault('url', 'https://example.com')
        normalized.setdefault('published_at', format_timestamp())
        
        return normalized
    
    def _get_fallback_analysis(self, assets: List[str]) -> Tuple[List[NewsEntry], PortfolioAnalysis]:
        """Provide fallback analysis when no news data is available."""
        # Create minimal portfolio analysis
        portfolio_analysis = PortfolioAnalysis(
            total_articles=0,
            high_impact_count=0,
            overall_sentiment="Neutral",
            risk_level="Low",
            key_concerns=["No recent news data available"],
            opportunities=["Consider monitoring news sources"],
            recommendations=["Check news sources and try again"]
        )
        
        return [], portfolio_analysis
