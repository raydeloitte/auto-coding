import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.base_agent import VisualizationAgent
from shared.data_models import (
    AnalysisRequest, AnalysisResult, AnalysisType
)


class VisualizationAgent(VisualizationAgent):
    def __init__(self, config, message_bus=None, logger=None):
        super().__init__(config, message_bus, logger)
        
        self.chart_types = config.parameters.get('chart_types', ['candlestick', 'volume', 'indicators'])
        self.output_formats = config.parameters.get('output_formats', ['png', 'html'])
        self.output_dir = Path("reports/charts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def process_analysis_request(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        self.logger.info(f"Processing visualization request for {len(request.symbols)} symbols")
        
        # Get analysis data from other agents
        analysis_data = await self._collect_analysis_data(request)
        if not analysis_data:
            self.logger.error("No analysis data available for visualization")
            return None
        
        visualization_data = {}
        
        for symbol in request.symbols:
            try:
                # Create charts for each symbol
                charts = await self._create_charts(symbol, analysis_data, request)
                if charts:
                    visualization_data[f"{symbol}_charts"] = charts
                
            except Exception as e:
                self.logger.error(f"Error creating visualizations for {symbol}: {e}")
                continue
        
        if visualization_data:
            return AnalysisResult(
                request_id=request.request_id,
                agent_name=self.agent_name,
                symbol=",".join(request.symbols),
                analysis_type=AnalysisType.VISUALIZATION,
                data=visualization_data,
                confidence=1.0,  # Visualization is always successful if data exists
                timestamp=datetime.now()
            )
        
        return None

    async def _collect_analysis_data(self, request: AnalysisRequest) -> Dict[str, Any]:
        # In a real implementation, this would collect data from:
        # 1. Data collector (price data, historical data)
        # 2. Technical analyst (indicators, signals)
        # 3. Fundamental analyst (fundamental metrics)
        # 4. Risk assessor (risk metrics)
        # 5. Sentiment analyzer (sentiment data)
        
        # For now, simulate collecting analysis data
        await asyncio.sleep(0.1)
        
        analysis_data = {}
        
        for symbol in request.symbols:
            # Mock data from different agents
            analysis_data[f"{symbol}_price"] = await self._get_mock_price_data(symbol)
            analysis_data[f"{symbol}_indicators"] = await self._get_mock_technical_data(symbol)
            analysis_data[f"{symbol}_fundamental"] = await self._get_mock_fundamental_data(symbol)
            analysis_data[f"{symbol}_risk"] = await self._get_mock_risk_data(symbol)
            analysis_data[f"{symbol}_sentiment"] = await self._get_mock_sentiment_data(symbol)
        
        return analysis_data

    async def _get_mock_price_data(self, symbol: str) -> Dict[str, Any]:
        import random
        # Generate mock OHLCV data
        data = []
        base_price = 100
        
        for i in range(60):  # 60 days of data
            price = base_price + random.uniform(-5, 5)
            data.append({
                'date': (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - 
                        timedelta(days=60-i)).isoformat(),
                'open': price * random.uniform(0.995, 1.005),
                'high': price * random.uniform(1.000, 1.030),
                'low': price * random.uniform(0.970, 1.000),
                'close': price,
                'volume': random.randint(1000000, 5000000)
            })
            base_price = price
        
        return {'ohlcv': data}

    async def _get_mock_technical_data(self, symbol: str) -> Dict[str, Any]:
        import random
        return {
            'rsi': random.uniform(30, 70),
            'macd': random.uniform(-2, 2),
            'sma_20': random.uniform(95, 105),
            'sma_50': random.uniform(90, 110),
            'bollinger_upper': random.uniform(105, 115),
            'bollinger_lower': random.uniform(85, 95)
        }

    async def _get_mock_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        import random
        return {
            'pe_ratio': random.uniform(10, 30),
            'pb_ratio': random.uniform(1, 4),
            'roe': random.uniform(5, 25),
            'debt_to_equity': random.uniform(0.2, 2.0)
        }

    async def _get_mock_risk_data(self, symbol: str) -> Dict[str, Any]:
        import random
        return {
            'volatility': random.uniform(0.15, 0.40),
            'beta': random.uniform(0.5, 2.0),
            'var': random.uniform(0.02, 0.08),
            'max_drawdown': random.uniform(0.10, 0.35)
        }

    async def _get_mock_sentiment_data(self, symbol: str) -> Dict[str, Any]:
        import random
        return {
            'overall_sentiment': random.uniform(-0.8, 0.8),
            'news_sentiment': random.uniform(-0.6, 0.6),
            'analyst_sentiment': random.uniform(-0.5, 0.7),
            'social_sentiment': random.uniform(-0.9, 0.9)
        }

    async def _create_charts(self, symbol: str, analysis_data: Dict[str, Any], 
                           request: AnalysisRequest) -> Dict[str, Any]:
        charts = {}
        
        try:
            # Create different types of charts based on configuration
            if 'candlestick' in self.chart_types:
                candlestick_chart = await self._create_candlestick_chart(symbol, analysis_data)
                if candlestick_chart:
                    charts['candlestick'] = candlestick_chart
            
            if 'volume' in self.chart_types:
                volume_chart = await self._create_volume_chart(symbol, analysis_data)
                if volume_chart:
                    charts['volume'] = volume_chart
            
            if 'indicators' in self.chart_types:
                indicators_chart = await self._create_indicators_chart(symbol, analysis_data)
                if indicators_chart:
                    charts['indicators'] = indicators_chart
            
            # Create comparison charts if multiple symbols
            if len(request.symbols) > 1:
                comparison_chart = await self._create_comparison_chart(request.symbols, analysis_data)
                if comparison_chart:
                    charts['comparison'] = comparison_chart
            
            # Create fundamental analysis chart
            fundamental_chart = await self._create_fundamental_chart(symbol, analysis_data)
            if fundamental_chart:
                charts['fundamental'] = fundamental_chart
            
            # Create risk analysis chart
            risk_chart = await self._create_risk_chart(symbol, analysis_data)
            if risk_chart:
                charts['risk'] = risk_chart
            
            # Create sentiment analysis chart
            sentiment_chart = await self._create_sentiment_chart(symbol, analysis_data)
            if sentiment_chart:
                charts['sentiment'] = sentiment_chart
        
        except Exception as e:
            self.logger.error(f"Error creating charts for {symbol}: {e}")
        
        return charts

    async def _create_candlestick_chart(self, symbol: str, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            price_data = analysis_data.get(f"{symbol}_price", {})
            technical_data = analysis_data.get(f"{symbol}_indicators", {})
            ohlcv_data = price_data.get('ohlcv', [])
            
            if not ohlcv_data:
                return None
            
            # Create chart specification (using a simple JSON format)
            chart_spec = {
                'type': 'candlestick',
                'title': f'{symbol} Price Chart with Technical Indicators',
                'data': {
                    'ohlcv': ohlcv_data,
                    'sma_20': technical_data.get('sma_20'),
                    'sma_50': technical_data.get('sma_50'),
                    'bollinger_upper': technical_data.get('bollinger_upper'),
                    'bollinger_lower': technical_data.get('bollinger_lower')
                },
                'layout': {
                    'width': 800,
                    'height': 600,
                    'showlegend': True
                }
            }
            
            # Save chart specification
            chart_path = await self._save_chart(symbol, 'candlestick', chart_spec)
            
            return {
                'chart_type': 'candlestick',
                'file_path': chart_path,
                'specification': chart_spec,
                'created_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error creating candlestick chart for {symbol}: {e}")
            return None

    async def _create_volume_chart(self, symbol: str, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            price_data = analysis_data.get(f"{symbol}_price", {})
            ohlcv_data = price_data.get('ohlcv', [])
            
            if not ohlcv_data:
                return None
            
            chart_spec = {
                'type': 'volume',
                'title': f'{symbol} Volume Chart',
                'data': {
                    'volume_data': [{'date': item['date'], 'volume': item['volume']} 
                                   for item in ohlcv_data]
                },
                'layout': {
                    'width': 800,
                    'height': 300
                }
            }
            
            chart_path = await self._save_chart(symbol, 'volume', chart_spec)
            
            return {
                'chart_type': 'volume',
                'file_path': chart_path,
                'specification': chart_spec,
                'created_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error creating volume chart for {symbol}: {e}")
            return None

    async def _create_indicators_chart(self, symbol: str, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            technical_data = analysis_data.get(f"{symbol}_indicators", {})
            
            chart_spec = {
                'type': 'indicators',
                'title': f'{symbol} Technical Indicators',
                'data': {
                    'rsi': technical_data.get('rsi'),
                    'macd': technical_data.get('macd'),
                    'indicators': technical_data
                },
                'layout': {
                    'width': 800,
                    'height': 400
                }
            }
            
            chart_path = await self._save_chart(symbol, 'indicators', chart_spec)
            
            return {
                'chart_type': 'indicators',
                'file_path': chart_path,
                'specification': chart_spec,
                'created_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error creating indicators chart for {symbol}: {e}")
            return None

    async def _create_comparison_chart(self, symbols: List[str], analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            comparison_data = {}
            
            for symbol in symbols:
                price_data = analysis_data.get(f"{symbol}_price", {})
                if price_data:
                    comparison_data[symbol] = price_data.get('ohlcv', [])
            
            if not comparison_data:
                return None
            
            chart_spec = {
                'type': 'comparison',
                'title': f'Price Comparison: {", ".join(symbols)}',
                'data': comparison_data,
                'layout': {
                    'width': 1000,
                    'height': 600
                }
            }
            
            chart_path = await self._save_chart('comparison', 'multi_symbol', chart_spec)
            
            return {
                'chart_type': 'comparison',
                'file_path': chart_path,
                'specification': chart_spec,
                'created_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error creating comparison chart: {e}")
            return None

    async def _create_fundamental_chart(self, symbol: str, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            fundamental_data = analysis_data.get(f"{symbol}_fundamental", {})
            
            if not fundamental_data:
                return None
            
            chart_spec = {
                'type': 'fundamental',
                'title': f'{symbol} Fundamental Metrics',
                'data': {
                    'metrics': [
                        {'name': 'P/E Ratio', 'value': fundamental_data.get('pe_ratio', 0)},
                        {'name': 'P/B Ratio', 'value': fundamental_data.get('pb_ratio', 0)},
                        {'name': 'ROE %', 'value': fundamental_data.get('roe', 0)},
                        {'name': 'Debt/Equity', 'value': fundamental_data.get('debt_to_equity', 0)}
                    ]
                },
                'layout': {
                    'width': 600,
                    'height': 400,
                    'chart_type': 'bar'
                }
            }
            
            chart_path = await self._save_chart(symbol, 'fundamental', chart_spec)
            
            return {
                'chart_type': 'fundamental',
                'file_path': chart_path,
                'specification': chart_spec,
                'created_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error creating fundamental chart for {symbol}: {e}")
            return None

    async def _create_risk_chart(self, symbol: str, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            risk_data = analysis_data.get(f"{symbol}_risk", {})
            
            if not risk_data:
                return None
            
            chart_spec = {
                'type': 'risk',
                'title': f'{symbol} Risk Metrics',
                'data': {
                    'metrics': [
                        {'name': 'Volatility', 'value': risk_data.get('volatility', 0)},
                        {'name': 'Beta', 'value': risk_data.get('beta', 0)},
                        {'name': 'VaR', 'value': risk_data.get('var', 0)},
                        {'name': 'Max Drawdown', 'value': risk_data.get('max_drawdown', 0)}
                    ]
                },
                'layout': {
                    'width': 600,
                    'height': 400,
                    'chart_type': 'radar'
                }
            }
            
            chart_path = await self._save_chart(symbol, 'risk', chart_spec)
            
            return {
                'chart_type': 'risk',
                'file_path': chart_path,
                'specification': chart_spec,
                'created_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error creating risk chart for {symbol}: {e}")
            return None

    async def _create_sentiment_chart(self, symbol: str, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            sentiment_data = analysis_data.get(f"{symbol}_sentiment", {})
            
            if not sentiment_data:
                return None
            
            chart_spec = {
                'type': 'sentiment',
                'title': f'{symbol} Sentiment Analysis',
                'data': {
                    'sentiments': [
                        {'source': 'Overall', 'score': sentiment_data.get('overall_sentiment', 0)},
                        {'source': 'News', 'score': sentiment_data.get('news_sentiment', 0)},
                        {'source': 'Analysts', 'score': sentiment_data.get('analyst_sentiment', 0)},
                        {'source': 'Social Media', 'score': sentiment_data.get('social_sentiment', 0)}
                    ]
                },
                'layout': {
                    'width': 600,
                    'height': 400,
                    'chart_type': 'gauge'
                }
            }
            
            chart_path = await self._save_chart(symbol, 'sentiment', chart_spec)
            
            return {
                'chart_type': 'sentiment',
                'file_path': chart_path,
                'specification': chart_spec,
                'created_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"Error creating sentiment chart for {symbol}: {e}")
            return None

    async def _save_chart(self, symbol: str, chart_type: str, chart_spec: Dict[str, Any]) -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_{chart_type}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(chart_spec, f, indent=2)
        
        self.logger.debug(f"Saved chart specification: {filepath}")
        return str(filepath)

    async def health_check(self) -> Dict[str, Any]:
        base_health = await super().health_check()
        base_health.update({
            "supported_chart_types": self.chart_types,
            "output_formats": self.output_formats,
            "output_directory": str(self.output_dir)
        })
        return base_health