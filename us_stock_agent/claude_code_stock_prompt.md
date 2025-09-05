Please help me create a professional US stock analysis agent using a multi-subagent architecture with the following capabilities:

## Multi-Agent Architecture Overview
Design a main orchestrator agent that coordinates multiple specialized subagents, each responsible for specific analysis domains:

### 1. Data Collection Subagent
- **Responsibility**: Fetch and manage all stock data
- **Tasks**: Real-time prices, historical data, financial statements, news sentiment
- **APIs**: yfinance, Alpha Vantage, Financial Modeling Prep
- **Features**: Data caching, rate limiting, error recovery

### 2. Technical Analysis Subagent
- **Responsibility**: Perform technical indicator calculations and pattern recognition
- **Tasks**: MA, RSI, MACD, Bollinger Bands, support/resistance levels
- **Features**: Signal generation, trend identification, momentum analysis
- **Output**: Technical scores and trading signals

### 3. Fundamental Analysis Subagent
- **Responsibility**: Analyze company financials and valuation metrics
- **Tasks**: PE, PB, ROE, DCF modeling, sector comparison
- **Features**: Financial health scoring, growth analysis, peer benchmarking
- **Output**: Fundamental scores and investment recommendations

### 4. Risk Assessment Subagent
- **Responsibility**: Calculate and evaluate investment risks
- **Tasks**: Volatility analysis, VaR calculation, correlation analysis
- **Features**: Portfolio risk metrics, drawdown analysis, beta calculations
- **Output**: Risk scores and position sizing recommendations

### 5. Market Sentiment Subagent
- **Responsibility**: Analyze market sentiment and news impact
- **Tasks**: News sentiment analysis, social media monitoring, insider trading
- **Features**: Sentiment scoring, event impact analysis
- **Output**: Sentiment indicators and market mood assessment

### 6. Visualization Subagent
- **Responsibility**: Generate charts and visual reports
- **Tasks**: Price charts, technical indicators, comparison plots
- **Features**: Interactive charts, multi-timeframe analysis
- **Output**: Publication-ready charts and dashboards

### 7. Report Generation Subagent
- **Responsibility**: Compile and format comprehensive analysis reports
- **Tasks**: Aggregate insights from all subagents, generate summaries
- **Features**: PDF/HTML reports, executive summaries, actionable insights
- **Output**: Professional investment analysis reports

## Project Structure
```
us_stock_agent/
├── src/
│   ├── orchestrator/
│   │   └── main_agent.py           # Main orchestrator
│   ├── subagents/
│   │   ├── data_collector.py       # Data Collection Subagent
│   │   ├── technical_analyst.py    # Technical Analysis Subagent
│   │   ├── fundamental_analyst.py  # Fundamental Analysis Subagent
│   │   ├── risk_assessor.py       # Risk Assessment Subagent
│   │   ├── sentiment_analyzer.py  # Market Sentiment Subagent
│   │   ├── visualizer.py          # Visualization Subagent
│   │   └── report_generator.py    # Report Generation Subagent
│   ├── shared/
│   │   ├── base_agent.py          # Base class for all subagents
│   │   ├── message_bus.py         # Inter-agent communication
│   │   └── data_models.py         # Shared data structures
│   └── utils/
│       ├── config.py              # Configuration management
│       └── logger.py              # Logging utilities
├── config/
│   └── agent_config.yaml          # Multi-agent configuration
├── data/                          # Shared data storage
└── reports/                       # Generated reports
```

## Inter-Agent Communication System
Implement a message-passing system where:
- **Orchestrator** coordinates subagent execution and data flow
- **Message Bus** handles async communication between subagents
- **Shared Data Store** allows subagents to access and update common data
- **Event System** triggers subagent actions based on data updates

## Expected Usage Examples
```python
# Main orchestrator usage
orchestrator = StockAnalysisOrchestrator()

# Comprehensive analysis using all subagents
full_analysis = orchestrator.analyze_stock("AAPL", depth="comprehensive")

# Selective analysis using specific subagents
tech_analysis = orchestrator.analyze_stock("TSLA", subagents=["technical", "sentiment"])

# Portfolio analysis across multiple subagents
portfolio_report = orchestrator.analyze_portfolio({
    "AAPL": 100, "GOOGL": 50, "MSFT": 75
})

# Real-time monitoring with multiple subagents
orchestrator.start_monitoring(["AAPL", "TSLA"], update_frequency="5min")
```

## Subagent Coordination Features
- **Parallel Processing**: Execute independent subagents simultaneously
- **Data Dependency Management**: Ensure subagents receive required data from others
- **Consensus Building**: Aggregate recommendations from multiple subagents
- **Conflict Resolution**: Handle disagreements between subagent recommendations
- **Performance Monitoring**: Track individual subagent performance and accuracy

## Technical Requirements
- Use Python with asyncio for concurrent subagent execution
- Implement proper inter-process communication (IPC) or message queues
- Design modular subagent interfaces for easy extension
- Include comprehensive logging and monitoring for each subagent
- Implement graceful error handling and subagent failover
- Support hot-swapping of subagents without stopping the system

## Development Sequence
1. **Phase 1**: Create base agent architecture and message bus system
2. **Phase 2**: Implement Data Collection and Technical Analysis subagents
3. **Phase 3**: Add Fundamental Analysis and Risk Assessment subagents
4. **Phase 4**: Integrate Sentiment Analysis and Visualization subagents
5. **Phase 5**: Implement Report Generation and orchestrator coordination
6. **Phase 6**: Add monitoring, testing, and performance optimization

## Advanced Multi-Agent Features
- **Learning System**: Subagents learn from prediction accuracy and adapt
- **Dynamic Weight Assignment**: Adjust subagent influence based on market conditions
- **Ensemble Methods**: Combine subagent outputs using machine learning techniques
- **A/B Testing**: Compare different subagent configurations and strategies

Please start with Phase 1 and create the foundational multi-agent architecture. Focus on creating a scalable, maintainable system where subagents can operate independently while contributing to a unified analysis framework.