# Financial News Impact Tracker

A production-ready, object-oriented financial news analysis system that combines web scraping, AI-powered analysis, and portfolio impact assessment.

## 🚀 Features

- **Real-time News Scraping**: Fetches financial news from trusted sources using DuckDuckGo
- **AI-Powered Analysis**: Uses OpenAI Agents SDK for intelligent sentiment and impact analysis
- **Portfolio Assessment**: Generates portfolio-level insights and recommendations
- **Structured Data**: Pydantic models ensure data validation and consistency
- **Multiple Interfaces**: Both Streamlit web UI and command-line interface
- **Export Capabilities**: JSON and CSV export for further analysis

## 📁 Project Structure

```
Finnews_Agent_CC/
├── src/                          # Main source code
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── models.py                # Pydantic data models
│   ├── scraper.py               # News scraping functionality
│   ├── analyzer.py              # AI analysis engine
│   ├── tracker.py               # Main orchestration class
│   ├── ui.py                    # Streamlit user interface
│   ├── cli.py                   # Command-line interface
│   └── utils.py                 # Utility functions
├── app.py                       # Streamlit app entry point
├── requirements.txt             # Python dependencies
├── config.py                    # Legacy config (for backward compatibility)
├── financial_news_tracker.py   # Legacy monolithic file
└── README.md                    # This file
```

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Internet connection for news scraping

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Finnews_Agent_CC
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   DEBUG=False
   ```

4. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

   Or use the command-line interface:
   ```bash
   python -m src.cli --assets AAPL MSFT GOOGL
   ```

## 🎯 Usage

### Web Interface (Streamlit)

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```

2. **Configure your portfolio:**
   - Enter asset symbols in the sidebar (e.g., AAPL, MSFT, BTC-USD, Gold)
   - Adjust analysis parameters (articles per asset, time filter)
   - Check system status

3. **Run analysis:**
   - Click "Analyze Portfolio News"
   - View results in multiple tabs:
     - Portfolio Summary: Overall insights and recommendations
     - News Items: Individual article analysis with filtering
     - Impact Analysis: Charts and asset-level metrics
     - Export: Download results in JSON/CSV format

### Command-Line Interface

**Basic usage:**
```bash
python -m src.cli --assets AAPL MSFT GOOGL
```

**Advanced options:**
```bash
python -m src.cli --assets AAPL MSFT GOOGL TSLA BTC-USD \\
                  --articles 10 \\
                  --days 3 \\
                  --output results.json \\
                  --format json
```

**Test system connectivity:**
```bash
python -m src.cli --test
```

**Available CLI options:**
- `--assets`: Asset symbols to analyze
- `--articles`: Maximum articles per asset (default: 5)
- `--days`: Days back to search (1-7, default: 1)
- `--output`: Output file path
- `--format`: Output format (json/summary, default: summary)
- `--test`: Test system connectivity
- `--verbose`: Enable verbose logging

### Programmatic Usage

```python
import asyncio
from src.tracker import FinancialNewsTracker

async def analyze_portfolio():
    tracker = FinancialNewsTracker()
    
    result = await tracker.analyze_portfolio(
        assets=["AAPL", "MSFT", "GOOGL"],
        max_articles_per_asset=5,
        time_filter_days=1
    )
    
    print(f"Found {len(result.news_entries)} news articles")
    print(f"Overall sentiment: {result.portfolio_analysis.overall_sentiment}")
    
    return result

# Run the analysis
result = asyncio.run(analyze_portfolio())
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DEBUG`: Enable debug mode (optional, default: False)

### Configuration Options

The application can be configured via the `src/config.py` file:

```python
from src.config import config

# Modify configuration
config.max_assets = 10
config.max_articles_per_asset = 5
config.ai.model = "gpt-4o-mini"
```

## 📊 Supported Assets

The system supports various asset types:

- **Stocks**: AAPL, MSFT, GOOGL, AMZN, TSLA, etc.
- **Cryptocurrency**: BTC-USD, ETH-USD, ADA-USD, etc.
- **Commodities**: Gold, Silver, Oil, Copper
- **ETFs**: SPY, QQQ, VTI, ARKK
- **Indices**: ^GSPC, ^IXIC, ^DJI

## 🏗️ Architecture

### Core Classes

1. **FinancialNewsTracker**: Main orchestration class
   - Coordinates scraping and analysis
   - Validates inputs and manages workflow
   - Generates comprehensive results

2. **FinancialNewsScraper**: Handles news scraping
   - DuckDuckGo search integration
   - Trusted source filtering
   - Rate limiting and error handling

3. **AIAnalyzer**: AI-powered analysis engine
   - OpenAI Agents SDK integration
   - Sentiment and impact analysis
   - Fallback to simple analysis when needed

4. **StreamlitUI**: Web interface
   - Interactive portfolio configuration
   - Real-time analysis and visualization
   - Export functionality

### Data Models

All data is validated using Pydantic models:

- **NewsEntry**: Individual news article with analysis
- **PortfolioAnalysis**: Portfolio-level insights
- **AssetMetrics**: Per-asset analysis metrics
- **AnalysisResult**: Complete analysis container

## 🛡️ Error Handling

The system includes comprehensive error handling:

- **Rate Limiting**: Automatic backoff for API limits
- **Fallback Analysis**: Simple analysis when AI fails
- **Input Validation**: Pydantic model validation
- **Graceful Degradation**: Continues operation with partial failures

## 📈 Performance Considerations

- **Rate Limiting**: Built-in delays to respect API limits
- **Asset Limits**: Maximum of 10 assets per analysis
- **Article Limits**: Configurable articles per asset
- **Timeout Protection**: 60-second timeout for AI analysis

## 🧪 Testing

**Test system connectivity:**
```bash
python -m src.cli --test
```

**Test with sample data:**
```bash
python -m src.cli --assets AAPL --articles 2 --days 1
```

## 🚨 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure `OPENAI_API_KEY` is set in `.env` file
   - Verify API key has sufficient credits

2. **Rate Limiting**
   - Increase delays between requests
   - Reduce number of assets or articles
   - Wait before retrying

3. **No News Found**
   - Check internet connectivity
   - Verify asset symbols are correct
   - Try different time filters

4. **Agent Analysis Fails**
   - System falls back to simple analysis
   - Check OpenAI API status
   - Verify model availability

### Debug Mode

Enable debug logging:
```bash
export DEBUG=True
python -m src.cli --verbose --test
```

## 🔄 Migration from Legacy Version

The new OOP version is backward compatible. To migrate:

1. Update imports:
   ```python
   # Old
   from financial_news_tracker import analyze_portfolio_news
   
   # New
   from src.tracker import FinancialNewsTracker
   ```

2. Update function calls:
   ```python
   # Old
   news_entries, portfolio_analysis = await analyze_portfolio_news(assets)
   
   # New
   tracker = FinancialNewsTracker()
   result = await tracker.analyze_portfolio(assets)
   news_entries = result.news_entries
   portfolio_analysis = result.portfolio_analysis
   ```

## 📋 Development

### Code Structure

- **Modular Design**: Separate modules for different concerns
- **Type Hints**: Full type annotation throughout
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging for debugging
- **Configuration**: Centralized configuration management

### Adding New Features

1. **New Data Sources**: Extend `FinancialNewsScraper`
2. **Analysis Methods**: Extend `AIAnalyzer`
3. **UI Components**: Add to `StreamlitUI`
4. **CLI Commands**: Extend `CLI` class

### Testing

```bash
# Install development dependencies
pip install pytest black flake8

# Run tests (when available)
pytest

# Format code
black src/

# Lint code
flake8 src/
```

## 📜 License

This project is licensed under the MIT License. See LICENSE file for details.

## 👨‍💻 Author

Ahmad PourReza - June 2025

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in debug mode
3. Create an issue on GitHub

---

*Powered by OpenAI, DuckDuckGo News Search, and Pydantic Validation*
