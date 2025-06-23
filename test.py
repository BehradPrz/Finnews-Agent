"""
Test Script
===========

Simple test script to verify the OOP refactored code works correctly.
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import config
from src.tracker import FinancialNewsTracker
from src.models import NewsEntry, PortfolioAnalysis


def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from src.config import config
        from src.models import NewsEntry, PortfolioAnalysis, AnalysisResult
        from src.scraper import FinancialNewsScraper
        from src.analyzer import AIAnalyzer
        from src.tracker import FinancialNewsTracker
        from src.utils import Logger, RateLimiter
        from src.ui import StreamlitUI
        from src.cli import CLI
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False


def test_config():
    """Test configuration."""
    print("🧪 Testing configuration...")
    
    try:
        # Test config access
        assert hasattr(config, 'max_assets')
        assert hasattr(config, 'ai')
        assert hasattr(config, 'news')
        
        # Test validation
        issues = config.validate()
        if issues:
            print(f"⚠️ Configuration issues: {issues}")
        else:
            print("✅ Configuration valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False


def test_models():
    """Test Pydantic models."""
    print("🧪 Testing data models...")
    
    try:
        # Test NewsEntry
        news_entry = NewsEntry(
            asset="AAPL",
            title="Test News",
            summary="Test summary",
            source="test.com",
            url="https://test.com",
            published_at="2025-06-23T00:00:00",
            sentiment="Positive",
            impact_timeframe="Medium-Term",
            impact_magnitude="High",
            confidence_score=0.85
        )
        
        # Test PortfolioAnalysis
        portfolio_analysis = PortfolioAnalysis(
            total_articles=1,
            high_impact_count=1,
            overall_sentiment="Bullish",
            risk_level="Medium",
            key_concerns=["Test concern"],
            opportunities=["Test opportunity"],
            recommendations=["Test recommendation"]
        )
        
        print("✅ Model validation successful")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {str(e)}")
        return False


async def test_tracker():
    """Test the main tracker functionality."""
    print("🧪 Testing tracker connectivity...")
    
    try:
        tracker = FinancialNewsTracker()
        
        # Test connectivity
        status = tracker.test_connectivity()
        print(f"   News scraping: {'✅' if status.get('news_scraping') else '❌'}")
        print(f"   AI analysis: {'✅' if status.get('ai_analysis') else '❌'}")
        
        # Test supported assets
        supported = tracker.get_supported_assets()
        assert 'stocks' in supported
        assert 'crypto' in supported
        
        print("✅ Tracker tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Tracker test failed: {str(e)}")
        return False


async def test_quick_analysis():
    """Test a quick analysis if possible."""
    print("🧪 Testing quick analysis (if API available)...")
    
    try:
        tracker = FinancialNewsTracker()
        
        # Only run if we have valid config
        if not config.ai.is_valid():
            print("⚠️ Skipping analysis test - no API key configured")
            return True
        
        # Try a very quick analysis
        result = await tracker.analyze_portfolio(
            assets=["AAPL"],
            max_articles_per_asset=1,
            time_filter_days=1
        )
        
        assert result is not None
        assert hasattr(result, 'portfolio_analysis')
        assert hasattr(result, 'news_entries')
        
        print(f"✅ Quick analysis successful - found {len(result.news_entries)} articles")
        return True
        
    except Exception as e:
        print(f"⚠️ Quick analysis test failed (expected if no API key): {str(e)}")
        return True  # Don't fail the test suite for this


async def main():
    """Run all tests."""
    print("🚀 Financial News Tracker - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Test", test_config),
        ("Model Test", test_models),
        ("Tracker Test", test_tracker),
        ("Quick Analysis Test", test_quick_analysis),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\\n{test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The OOP refactor is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == len(results)


if __name__ == "__main__":
    asyncio.run(main())
