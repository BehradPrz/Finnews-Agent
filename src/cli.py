"""
Command Line Interface
=====================

CLI for the Financial News Tracker.
"""

import asyncio
import argparse
import json
import sys
from typing import List

from .tracker import FinancialNewsTracker
from .utils import Logger


class CLI:
    """Command line interface for the Financial News Tracker."""
    
    def __init__(self):
        self.logger = Logger(__name__)
        self.tracker = FinancialNewsTracker()
    
    def parse_args(self) -> argparse.Namespace:
        """Parse command line arguments."""
        parser = argparse.ArgumentParser(
            description="Financial News Impact Tracker - CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  python -m src.cli --assets AAPL MSFT GOOGL
  python -m src.cli --assets BTC-USD ETH-USD --days 3 --articles 10
  python -m src.cli --test
            """
        )
        
        parser.add_argument(
            "--assets", 
            nargs="+", 
            help="Asset symbols to analyze (e.g., AAPL MSFT BTC-USD)"
        )
        
        parser.add_argument(
            "--articles", 
            type=int, 
            default=5,
            help="Maximum articles per asset (default: 5)"
        )
        
        parser.add_argument(
            "--days", 
            type=int, 
            default=1,
            help="Days back to search for news (1-7, default: 1)"
        )
        
        parser.add_argument(
            "--output", 
            "-o",
            help="Output file for results (JSON format)"
        )
        
        parser.add_argument(
            "--format",
            choices=["json", "summary"],
            default="summary",
            help="Output format (default: summary)"
        )
        
        parser.add_argument(
            "--test",
            action="store_true",
            help="Test system connectivity"
        )
        
        parser.add_argument(
            "--verbose", 
            "-v",
            action="store_true",
            help="Verbose output"
        )
        
        return parser.parse_args()
    
    async def test_system(self):
        """Test system connectivity."""
        print("🧪 Testing system connectivity...")
        
        status = self.tracker.test_connectivity()
        
        for service, available in status.items():
            status_icon = "✅" if available else "❌"
            print(f"{status_icon} {service.replace('_', ' ').title()}: {'Available' if available else 'Unavailable'}")
        
        if all(status.values()):
            print("\\n🎉 All systems operational!")
            return True
        else:
            print("\\n⚠️ Some systems are unavailable. Check configuration.")
            return False
    
    async def analyze_portfolio(self, args: argparse.Namespace):
        """Analyze portfolio from command line arguments."""
        if not args.assets:
            print("❌ Error: No assets provided. Use --assets to specify assets.")
            sys.exit(1)
        
        print(f"🔍 Analyzing {len(args.assets)} assets: {', '.join(args.assets)}")
        print(f"📊 Parameters: {args.articles} articles/asset, {args.days} day(s) back")
        
        try:
            result = await self.tracker.analyze_portfolio(
                assets=args.assets,
                max_articles_per_asset=args.articles,
                time_filter_days=args.days
            )
            
            if args.format == "json":
                self._output_json(result, args.output)
            else:
                self._output_summary(result, args.output)
            
            print(f"\\n✅ Analysis complete! Found {len(result.news_entries)} news articles.")
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            sys.exit(1)
    
    def _output_json(self, result, output_file=None):
        """Output results in JSON format."""
        data = result.model_dump()
        json_str = json.dumps(data, indent=2)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(json_str)
            print(f"📁 Results saved to {output_file}")
        else:
            print(json_str)
    
    def _output_summary(self, result, output_file=None):
        """Output results in human-readable summary format."""
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("FINANCIAL NEWS ANALYSIS SUMMARY")
        lines.append("=" * 60)
        lines.append("")
        
        # Portfolio overview
        analysis = result.portfolio_analysis
        lines.append(f"📊 Portfolio Overview:")
        lines.append(f"   Assets Analyzed: {', '.join(result.assets_analyzed)}")
        lines.append(f"   Total Articles: {analysis.total_articles}")
        lines.append(f"   High Impact: {analysis.high_impact_count}")
        lines.append(f"   Overall Sentiment: {analysis.overall_sentiment}")
        lines.append(f"   Risk Level: {analysis.risk_level}")
        lines.append("")
        
        # Key insights
        lines.append("🚨 Key Concerns:")
        for concern in analysis.key_concerns:
            lines.append(f"   • {concern}")
        lines.append("")
        
        lines.append("🎯 Opportunities:")
        for opportunity in analysis.opportunities:
            lines.append(f"   • {opportunity}")
        lines.append("")
        
        lines.append("💡 Recommendations:")
        for rec in analysis.recommendations:
            lines.append(f"   • {rec}")
        lines.append("")
        
        # Asset metrics
        if result.asset_metrics:
            lines.append("📈 Asset-Level Metrics:")
            for metric in result.asset_metrics:
                lines.append(f"   {metric.asset}:")
                lines.append(f"      Articles: {metric.article_count}")
                lines.append(f"      Sentiment: {metric.dominant_sentiment}")
                lines.append(f"      Impact: {metric.average_impact}")
                lines.append(f"      Confidence: {metric.average_confidence:.2f}")
                lines.append("")
        
        # Recent news headlines
        if result.news_entries:
            lines.append("📰 Recent News Headlines:")
            for entry in result.news_entries[:10]:  # Show top 10
                lines.append(f"   [{entry.asset}] {entry.title}")
                lines.append(f"      Impact: {entry.impact_magnitude} | Sentiment: {entry.sentiment}")
                lines.append("")
        
        output_text = "\\n".join(lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output_text)
            print(f"📁 Summary saved to {output_file}")
        else:
            print(output_text)
    
    async def run(self):
        """Main CLI entry point."""
        args = self.parse_args()
        
        if args.verbose:
            import logging
            logging.basicConfig(level=logging.INFO)
        
        try:
            if args.test:
                await self.test_system()
            else:
                await self.analyze_portfolio(args)
        
        except KeyboardInterrupt:
            print("\\n❌ Operation cancelled by user.")
            sys.exit(1)


async def main():
    """Main function for CLI."""
    cli = CLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
