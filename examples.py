"""
Example Usage Script
===================

Demonstrates how to use the Financial News Tracker programmatically.
"""

import asyncio
import json
from src.tracker import FinancialNewsTracker


async def basic_example():
    """Basic usage example."""
    print("🚀 Financial News Tracker - Basic Example")
    print("=" * 50)
    
    # Initialize tracker
    tracker = FinancialNewsTracker()
    
    # Test connectivity
    print("🧪 Testing system connectivity...")
    status = tracker.test_connectivity()
    for service, available in status.items():
        status_icon = "✅" if available else "❌"
        print(f"{status_icon} {service.replace('_', ' ').title()}")
    
    if not all(status.values()):
        print("⚠️ Some services unavailable. Analysis may use fallback methods.")
    
    print()
    
    # Define portfolio
    assets = ["AAPL", "MSFT", "GOOGL"]
    print(f"📊 Analyzing portfolio: {', '.join(assets)}")
    
    try:
        # Run analysis
        result = await tracker.analyze_portfolio(
            assets=assets,
            max_articles_per_asset=3,
            time_filter_days=1
        )
        
        # Display results
        print(f"\\n✅ Analysis complete!")
        print(f"   📰 Articles found: {len(result.news_entries)}")
        print(f"   📊 Overall sentiment: {result.portfolio_analysis.overall_sentiment}")
        print(f"   🎯 Risk level: {result.portfolio_analysis.risk_level}")
        
        # Show key insights
        print("\\n🚨 Key Concerns:")
        for concern in result.portfolio_analysis.key_concerns[:3]:
            print(f"   • {concern}")
        
        print("\\n💡 Recommendations:")
        for rec in result.portfolio_analysis.recommendations[:3]:
            print(f"   • {rec}")
        
        # Show recent headlines
        if result.news_entries:
            print("\\n📰 Recent Headlines:")
            for entry in result.news_entries[:3]:
                print(f"   [{entry.asset}] {entry.title[:80]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return None


async def detailed_example():
    """Detailed usage example with export."""
    print("\\n🔬 Financial News Tracker - Detailed Example")
    print("=" * 50)
    
    tracker = FinancialNewsTracker()
    
    # Larger portfolio with crypto and commodities
    assets = ["AAPL", "TSLA", "BTC-USD", "Gold", "SPY"]
    
    result = await tracker.analyze_portfolio(
        assets=assets,
        max_articles_per_asset=5,
        time_filter_days=2
    )
    
    # Detailed metrics
    print(f"\\n📈 Detailed Analysis Results:")
    print(f"   Assets analyzed: {len(result.assets_analyzed)}")
    print(f"   Total articles: {result.portfolio_analysis.total_articles}")
    print(f"   High impact articles: {result.portfolio_analysis.high_impact_count}")
    
    # Asset-level metrics
    if result.asset_metrics:
        print("\\n📊 Asset-Level Metrics:")
        for metric in result.asset_metrics:
            print(f"   {metric.asset}:")
            print(f"      Articles: {metric.article_count}")
            print(f"      Sentiment: {metric.dominant_sentiment}")
            print(f"      Impact: {metric.average_impact}")
            print(f"      Confidence: {metric.average_confidence:.2f}")
    
    # Export results
    output_file = "example_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(result.model_dump(), f, indent=2)
    print(f"\\n💾 Results exported to {output_file}")
    
    return result


async def single_asset_example():
    """Quick analysis for a single asset."""
    print("\\n⚡ Quick Single Asset Analysis")
    print("=" * 30)
    
    tracker = FinancialNewsTracker()
    
    # Quick analysis for Tesla
    result = await tracker.quick_analysis("TSLA")
    
    print(f"📊 TSLA Quick Analysis:")
    print(f"   Articles: {len(result.news_entries)}")
    print(f"   Sentiment: {result.portfolio_analysis.overall_sentiment}")
    print(f"   Risk: {result.portfolio_analysis.risk_level}")
    
    if result.news_entries:
        latest = result.news_entries[0]
        print(f"   Latest: {latest.title[:60]}...")
    
    return result


async def main():
    """Run all examples."""
    try:
        # Basic example
        await basic_example()
        
        # Detailed example
        await detailed_example()
        
        # Quick single asset example
        await single_asset_example()
        
        print("\\n🎉 All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\\n❌ Examples cancelled by user.")
    except Exception as e:
        print(f"\\n❌ Example failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
