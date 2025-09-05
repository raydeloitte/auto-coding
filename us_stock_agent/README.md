# Stock Analysis Multi-Agent System

A professional, scalable multi-agent architecture for comprehensive US stock analysis. This system coordinates multiple specialized subagents to provide technical analysis, fundamental analysis, risk assessment, sentiment analysis, visualization, and comprehensive reporting.

## 🏗️ Architecture Overview

The system uses a **main orchestrator** that coordinates **7 specialized subagents**, each responsible for specific analysis domains:

### Core Components

- **🎯 Main Orchestrator**: Coordinates all subagents and manages analysis workflows
- **📡 Message Bus**: Handles async communication between agents
- **📊 Data Models**: Shared data structures across all components
- **⚙️ Configuration Management**: Centralized configuration with environment support
- **📝 Logging System**: Comprehensive logging with structured output

### Subagent Architecture

1. **📥 Data Collection Subagent**
   - Fetches real-time prices, historical data, financial statements
   - Manages data caching and rate limiting
   - Supports multiple APIs (yfinance, Alpha Vantage, Financial Modeling Prep)

2. **📈 Technical Analysis Subagent**
   - Calculates technical indicators (RSI, MACD, Bollinger Bands, etc.)
   - Performs pattern recognition and trend analysis  
   - Generates technical trading signals

3. **🏢 Fundamental Analysis Subagent**
   - Analyzes financial metrics (PE, ROE, debt ratios, etc.)
   - Performs DCF modeling and peer comparison
   - Generates investment recommendations

4. **⚠️ Risk Assessment Subagent**
   - Calculates volatility, VaR, beta, maximum drawdown
   - Performs correlation analysis and stress testing
   - Generates risk-adjusted position sizing recommendations

5. **💭 Market Sentiment Subagent**
   - Analyzes news sentiment and social media mentions
   - Tracks analyst recommendations and insider trading
   - Provides sentiment scores and market mood assessment

6. **📊 Visualization Subagent**
   - Generates interactive charts and technical indicators
   - Creates comparison plots and risk visualizations
   - Supports multiple output formats (PNG, HTML, PDF)

7. **📋 Report Generation Subagent**
   - Compiles comprehensive analysis reports
   - Generates executive summaries and actionable insights
   - Creates professional PDF/HTML reports

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd us_stock_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
import asyncio
from orchestrator.main_agent import StockAnalysisOrchestrator

async def analyze_stock():
    # Initialize orchestrator
    orchestrator = StockAnalysisOrchestrator()
    
    async with orchestrator:
        # Comprehensive analysis
        results = await orchestrator.analyze_stock(
            symbol="AAPL",
            analysis_types=["technical", "fundamental", "risk", "sentiment"],
            depth="comprehensive"
        )
        
        # Process results
        for agent_name, result in results.items():
            print(f"{agent_name}: {len(result.signals)} signals")

# Run analysis
asyncio.run(analyze_stock())
```

### Configuration

The system uses YAML configuration files. Copy and customize the default configuration:

```bash
cp config/agent_config.yaml config/my_config.yaml
```

Set your API keys via environment variables:

```bash
export ALPHA_VANTAGE_API_KEY="your_key_here"
export FMP_API_KEY="your_fmp_key_here"
export NEWS_API_KEY="your_news_key_here"
```

## 📖 Usage Examples

### Single Stock Analysis

```python
# Basic technical analysis
results = await orchestrator.analyze_stock("TSLA", ["technical"])

# Comprehensive analysis with all agents
results = await orchestrator.analyze_stock(
    symbol="MSFT", 
    analysis_types=["technical", "fundamental", "risk", "sentiment"],
    depth="comprehensive"
)
```

### Portfolio Analysis

```python
from shared.data_models import Portfolio

portfolio = Portfolio(
    holdings={"AAPL": 100, "GOOGL": 50, "MSFT": 75},
    cash=10000.0
)

results = await orchestrator.analyze_portfolio(portfolio)
```

### Real-time Monitoring

```python
# Start real-time monitoring
monitoring_id = await orchestrator.start_monitoring(
    symbols=["AAPL", "TSLA"],
    update_frequency="5min"
)
```

### Selective Agent Execution

```python
# Use only specific agents
results = await orchestrator.analyze_stock(
    symbol="NVDA",
    analysis_types=["technical", "sentiment"]  # Only these agents
)
```

## 🔧 Advanced Features

### Multi-Agent Coordination

- **Parallel Processing**: Independent agents run simultaneously
- **Dependency Management**: Automatic execution ordering based on dependencies  
- **Consensus Building**: Aggregates recommendations from multiple agents
- **Conflict Resolution**: Handles disagreements between agent recommendations

### Inter-Agent Communication

```python
# Agents communicate via message bus
await agent.send_message(
    recipient="technical_analyst",
    message_type="data_update", 
    payload={"symbol": "AAPL", "price": 150.0}
)
```

### Performance Monitoring

```python
# System health check
status = await orchestrator.get_system_status()
print(f"Active agents: {status['orchestrator']['agents_count']}")
print(f"Message bus stats: {status['message_bus']['message_stats']}")
```

### Custom Agent Development

Extend the base agent class to create custom analysis agents:

```python
from shared.base_agent import BaseAgent

class CustomAnalysisAgent(BaseAgent):
    async def process_analysis_request(self, request):
        # Your custom analysis logic here
        return AnalysisResult(...)
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_orchestrator.py -v
```

## 📁 Project Structure

```
us_stock_agent/
├── src/
│   ├── orchestrator/
│   │   └── main_agent.py           # Main orchestrator
│   ├── subagents/
│   │   ├── data_collector.py       # Data Collection Subagent
│   │   ├── technical_analyst.py    # Technical Analysis Subagent
│   │   ├── fundamental_analyst.py  # Fundamental Analysis Subagent
│   │   ├── risk_assessor.py        # Risk Assessment Subagent
│   │   ├── sentiment_analyzer.py   # Market Sentiment Subagent
│   │   ├── visualizer.py           # Visualization Subagent
│   │   └── report_generator.py     # Report Generation Subagent
│   ├── shared/
│   │   ├── base_agent.py           # Base class for all subagents
│   │   ├── message_bus.py          # Inter-agent communication
│   │   └── data_models.py          # Shared data structures
│   └── utils/
│       ├── config.py               # Configuration management
│       └── logger.py               # Logging utilities
├── config/
│   └── agent_config.yaml           # Multi-agent configuration
├── tests/                          # Test files
├── data/                           # Shared data storage
├── reports/                        # Generated reports
├── requirements.txt                # Python dependencies
└── example_usage.py                # Usage examples
```

## ⚙️ Configuration Options

### Agent Configuration

Each agent can be individually configured:

```yaml
agents:
  technical_analyst:
    enabled: true
    priority: 2
    timeout: 30.0
    parameters:
      indicators: ["rsi", "macd", "bollinger"]
      lookback_periods: [20, 50, 200]
```

### System Configuration

```yaml
system:
  max_concurrent_requests: 10
  default_timeout: 30.0
  retry_attempts: 3
```

### API Configuration

```yaml
api:
  alpha_vantage_key: "${ALPHA_VANTAGE_API_KEY}"
  rate_limit_requests_per_minute: 60
  timeout_seconds: 30
```

## 🔐 Security & Best Practices

- **API Key Management**: Store sensitive keys in environment variables
- **Rate Limiting**: Built-in rate limiting for external APIs
- **Error Handling**: Comprehensive error handling and recovery
- **Logging**: Structured logging for debugging and monitoring
- **Data Validation**: Input validation using dataclasses

## 🛠️ Development Roadmap

### Phase 2: Enhanced Data Collection & Technical Analysis
- Real API integrations (yfinance, Alpha Vantage, FMP)
- Advanced technical indicators and pattern recognition
- Real-time data streaming capabilities

### Phase 3: Advanced Analytics
- Machine learning models for price prediction
- Advanced risk modeling and stress testing
- Real-time sentiment analysis from news and social media

### Phase 4: Production Features  
- Web dashboard with Streamlit
- REST API with FastAPI
- Background task processing with Celery
- Docker containerization

### Phase 5: Enterprise Features
- Multi-user support and authentication
- Portfolio optimization algorithms
- Backtesting and performance attribution
- Compliance and audit trails

 Phase 1: Base agent architecture and message bus system ✅
  - src/shared/base_agent.py - Complete abstract base class with lifecycle management
  - src/shared/message_bus.py - Full async message routing system with statistics and filtering
  - src/shared/data_models.py - Comprehensive data models for all analysis types

  Phase 2: Data Collection and Technical Analysis subagents ✅
  - src/subagents/data_collector.py - Data fetching with caching, rate limiting, mock data generation
  - src/subagents/technical_analyst.py - RSI, MACD, SMA, Bollinger Bands, signal generation

  Phase 3: Fundamental Analysis and Risk Assessment subagents ✅
  - src/subagents/fundamental_analyst.py - PE/PB ratios, ROE, debt analysis, investment signals
  - src/subagents/risk_assessor.py - Volatility, VaR, beta, Sharpe ratio, risk level classification

  Phase 4: Sentiment Analysis and Visualization subagents ✅
  - src/subagents/sentiment_analyzer.py - News, social media, analyst, insider sentiment analysis
  - src/subagents/visualizer.py - Chart generation for candlesticks, volume, indicators, comparisons

  Phase 5: Report Generation and orchestrator coordination ✅
  - src/subagents/report_generator.py - Comprehensive reports, executive summaries, actionable insights
  - src/orchestrator/main_agent.py - Full orchestrator with dependency resolution, parallel execution

  Phase 6: Monitoring, testing, and performance optimization ✅
  - src/utils/logger.py - Structured logging with performance monitoring
  - tests/test_orchestrator.py - Unit tests for dependency resolution and orchestration
  - SYSTEM_STATUS.md - Complete system documentation showing operational status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Support

For questions and support:
- Create an issue in the GitHub repository
- Review the example usage scripts
- Check the comprehensive test suite for implementation examples

---

**⚠️ Disclaimer**: This software is for educational and research purposes only. It is not intended as financial advice. Always consult with qualified financial advisors before making investment decisions.