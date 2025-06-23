"""
Streamlit UI Module
==================

Streamlit interface for the Financial News Tracker.
"""

import json
import asyncio
from typing import List, Dict, Any
import pandas as pd
import streamlit as st
from datetime import datetime

from .config import config
from .tracker import FinancialNewsTracker
from .models import AnalysisResult
from .utils import Logger


class StreamlitUI:
    """Streamlit user interface for the Financial News Tracker."""
    
    def __init__(self):
        self.logger = Logger(__name__)
        self.tracker = FinancialNewsTracker()
        
        # Configure Streamlit page
        st.set_page_config(
            page_title=config.app_title,
            page_icon=config.page_icon,
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def render_header(self):
        """Render the application header."""
        st.title(config.app_title)
        st.markdown("### AI-Powered Portfolio News Analysis")
        st.markdown("Track how recent financial news impacts your portfolio with intelligent AI analysis.")
    
    def render_sidebar(self) -> Dict[str, Any]:
        """Render the sidebar and return user configuration."""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Portfolio input
            st.subheader("Portfolio Assets")
            default_assets = "AAPL, MSFT, GOOGL, TSLA, BTC-USD"
            assets_input = st.text_area(
                "Enter your assets (comma-separated):",
                value=default_assets,
                height=100,
                help="Use stock tickers, crypto symbols (BTC-USD), or commodity names"
            )
            
            # Analysis options
            st.subheader("Analysis Options")
            max_articles = st.slider(
                "Max articles per asset", 
                1, 10, 
                config.max_articles_per_asset,
                help="Number of articles to analyze per asset"
            )
            
            time_filter_days = st.slider(
                "News time filter (days)", 
                config.time_filter_days_range[0], 
                config.time_filter_days_range[1], 
                1,
                help="Search for news from the past X days"
            )
            
            # API status
            st.subheader("🔌 System Status")
            status = self.tracker.test_connectivity()
            
            for service, available in status.items():
                if available:
                    st.success(f"✅ {service.replace('_', ' ').title()}")
                else:
                    st.error(f"❌ {service.replace('_', ' ').title()}")
            
            # Supported assets info
            if st.expander("📊 Supported Assets"):
                supported = self.tracker.get_supported_assets()
                for category, examples in supported.items():
                    st.write(f"**{category.title()}:** {', '.join(examples[:3])}...")
        
        return {
            "assets_input": assets_input,
            "max_articles": max_articles,
            "time_filter_days": time_filter_days
        }
    
    def parse_assets(self, assets_input: str) -> List[str]:
        """Parse asset input string into list."""
        import re
        return [asset.strip().upper() for asset in re.split(r'[,\\n]', assets_input) if asset.strip()]
    
    def render_analysis_button(self, user_config: Dict[str, Any]) -> bool:
        """Render analysis button and handle analysis."""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🔍 Analyze Portfolio News", type="primary", use_container_width=True):
                assets = self.parse_assets(user_config["assets_input"])
                
                if not assets:
                    st.error("Please enter at least one asset symbol.")
                    return False
                
                return self._run_analysis(assets, user_config)
        
        with col2:
            if st.button("🧪 Test System", help="Test if news search is working"):
                self._test_system()
        
        return False
    
    def _run_analysis(self, assets: List[str], user_config: Dict[str, Any]) -> bool:
        """Run the portfolio analysis."""
        try:
            with st.spinner(f"🤖 Analyzing news for {len(assets)} assets..."):
                # Run analysis
                result = asyncio.run(
                    self.tracker.analyze_portfolio(
                        assets=assets,
                        max_articles_per_asset=user_config["max_articles"],
                        time_filter_days=user_config["time_filter_days"]
                    )
                )
                
                # Store in session state
                st.session_state['analysis_result'] = result
                st.success(f"✅ Analysis complete! Found {len(result.news_entries)} relevant news items.")
                return True
                
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            return False
    
    def _test_system(self):
        """Test system connectivity."""
        with st.spinner("🧪 Testing system..."):
            status = self.tracker.test_connectivity()
            
            if all(status.values()):
                st.success("✅ All systems operational!")
            else:
                failed = [service for service, ok in status.items() if not ok]
                st.warning(f"⚠️ Issues with: {', '.join(failed)}")
    
    def render_quick_stats(self, result: AnalysisResult):
        """Render quick statistics."""
        analysis = result.portfolio_analysis
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📰 Articles", analysis.total_articles)
        with col2:
            st.metric("⚠️ High Impact", analysis.high_impact_count)
        with col3:
            sentiment_emoji = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "🟡"}
            st.metric(
                "📊 Sentiment", 
                f"{sentiment_emoji.get(analysis.overall_sentiment, '⚪')} {analysis.overall_sentiment}"
            )
        with col4:
            risk_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
            st.metric(
                "🎯 Risk Level", 
                f"{risk_emoji.get(analysis.risk_level, '⚪')} {analysis.risk_level}"
            )
    
    def render_portfolio_summary(self, result: AnalysisResult):
        """Render portfolio analysis summary."""
        st.subheader("Portfolio Analysis Summary")
        
        analysis = result.portfolio_analysis
        
        # Detailed analysis in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚨 Key Concerns")
            for concern in analysis.key_concerns:
                st.write(f"• {concern}")
            
            st.subheader("🎯 Opportunities")
            for opportunity in analysis.opportunities:
                st.write(f"• {opportunity}")
        
        with col2:
            st.subheader("💡 Recommendations")
            for rec in analysis.recommendations:
                st.write(f"• {rec}")
    
    def render_news_items(self, result: AnalysisResult):
        """Render individual news items with filtering."""
        st.subheader("Individual News Items")
        
        if not result.news_entries:
            st.info("No news items found for the analyzed assets.")
            return
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            sentiment_filter = st.selectbox("Filter by Sentiment", ["All", "Positive", "Negative", "Neutral"])
        with col2:
            impact_filter = st.selectbox("Filter by Impact", ["All", "High", "Medium", "Low"])
        with col3:
            asset_filter = st.selectbox("Filter by Asset", ["All"] + result.assets_analyzed)
        
        # Apply filters
        filtered_entries = result.news_entries
        if sentiment_filter != "All":
            filtered_entries = [e for e in filtered_entries if e.sentiment == sentiment_filter]
        if impact_filter != "All":
            filtered_entries = [e for e in filtered_entries if e.impact_magnitude == impact_filter]
        if asset_filter != "All":
            filtered_entries = [e for e in filtered_entries if e.asset == asset_filter]
        
        # Display news items
        for entry in filtered_entries:
            with st.expander(f"**{entry.asset}** | {entry.impact_magnitude} Impact | {entry.sentiment} Sentiment"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{entry.title}**")
                    st.write(entry.summary)
                    st.write(f"[Read full article]({entry.url})")
                
                with col2:
                    st.write(f"**Source:** {entry.source}")
                    st.write(f"**Published:** {entry.published_at[:10]}")
                    st.write(f"**Timeframe:** {entry.impact_timeframe}")
                    st.write(f"**Confidence:** {entry.confidence_score:.2f}")
    
    def render_impact_analysis(self, result: AnalysisResult):
        """Render impact analysis dashboard."""
        st.subheader("Impact Analysis Dashboard")
        
        if not result.news_entries:
            st.info("No data available for impact analysis.")
            return
        
        # Create DataFrame for analysis
        df = pd.DataFrame([entry.model_dump() for entry in result.news_entries])
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sentiment Distribution")
            sentiment_counts = df['sentiment'].value_counts()
            st.bar_chart(sentiment_counts)
        
        with col2:
            st.subheader("Impact Magnitude Distribution")
            impact_counts = df['impact_magnitude'].value_counts()
            st.bar_chart(impact_counts)
        
        # Asset-level metrics
        if result.asset_metrics:
            st.subheader("Asset-Level Analysis")
            metrics_df = pd.DataFrame([metric.model_dump() for metric in result.asset_metrics])
            st.dataframe(metrics_df, use_container_width=True)
    
    def render_export_options(self, result: AnalysisResult):
        """Render export options."""
        st.subheader("Export Results")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Full analysis export
        full_data = result.model_dump()
        full_json = json.dumps(full_data, indent=2)
        st.download_button(
            label="📥 Download Full Analysis (JSON)",
            data=full_json,
            file_name=f"portfolio_analysis_{timestamp}.json",
            mime="application/json"
        )
        
        # News data CSV export
        if result.news_entries:
            df = pd.DataFrame([entry.model_dump() for entry in result.news_entries])
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download News Data (CSV)",
                data=csv,
                file_name=f"portfolio_news_{timestamp}.csv",
                mime="text/csv"
            )
    
    def render_main_content(self):
        """Render the main content area."""
        if 'analysis_result' not in st.session_state:
            st.info("👆 Configure your portfolio in the sidebar and click 'Analyze Portfolio News' to get started.")
            return
        
        result: AnalysisResult = st.session_state['analysis_result']
        
        # Quick stats
        self.render_quick_stats(result)
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Portfolio Summary", 
            "📰 News Items", 
            "📈 Impact Analysis", 
            "💾 Export"
        ])
        
        with tab1:
            self.render_portfolio_summary(result)
        
        with tab2:
            self.render_news_items(result)
        
        with tab3:
            self.render_impact_analysis(result)
        
        with tab4:
            self.render_export_options(result)
    
    def render_footer(self):
        """Render the application footer."""
        st.markdown("---")
        st.markdown("*Powered by OpenAI, DuckDuckGo News Search, and Pydantic Validation*")
    
    def run(self):
        """Main entry point for the Streamlit app."""
        # Validate configuration
        config_issues = config.validate()
        if config_issues:
            st.error("Configuration Issues:")
            for issue in config_issues:
                st.write(f"• {issue}")
            st.stop()
        
        # Render UI components
        self.render_header()
        user_config = self.render_sidebar()
        
        # Main content area
        analysis_started = self.render_analysis_button(user_config)
        self.render_main_content()
        
        self.render_footer()


def main():
    """Main function to run the Streamlit app."""
    ui = StreamlitUI()
    ui.run()


if __name__ == "__main__":
    main()
