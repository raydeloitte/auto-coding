import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.base_agent import TechnicalAnalysisAgent
from shared.data_models import (
    AnalysisRequest, AnalysisResult, TechnicalIndicators,
    AnalysisSignal, SignalType, AnalysisType, StockData
)


class TechnicalAnalysisAgent(TechnicalAnalysisAgent):
    def __init__(self, config, message_bus=None, logger=None):
        super().__init__(config, message_bus, logger)
        
        self.indicators = config.parameters.get('indicators', ['rsi', 'macd', 'sma', 'bollinger'])
        self.lookback_periods = config.parameters.get('lookback_periods', [20, 50, 200])

    async def process_analysis_request(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        self.logger.info(f"Processing technical analysis for {len(request.symbols)} symbols")
        
        # Wait for data from data collector
        historical_data = await self._get_historical_data(request)
        if not historical_data:
            self.logger.error("No historical data available for technical analysis")
            return None
        
        analysis_data = {}
        signals = []
        
        for symbol in request.symbols:
            symbol_data = historical_data.get(f"{symbol}_historical", [])
            if not symbol_data:
                self.logger.warning(f"No historical data for {symbol}")
                continue
            
            try:
                # Calculate technical indicators
                indicators = await self._calculate_indicators(symbol, symbol_data)
                analysis_data[f"{symbol}_indicators"] = indicators
                
                # Generate trading signals
                symbol_signals = await self._generate_signals(symbol, indicators, symbol_data)
                signals.extend(symbol_signals)
                
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
                continue
        
        if analysis_data or signals:
            return AnalysisResult(
                request_id=request.request_id,
                agent_name=self.agent_name,
                symbol=",".join(request.symbols),
                analysis_type=AnalysisType.TECHNICAL,
                signals=signals,
                data=analysis_data,
                confidence=self._calculate_overall_confidence(signals),
                timestamp=datetime.now()
            )
        
        return None

    async def _get_historical_data(self, request: AnalysisRequest) -> Dict[str, Any]:
        # In a real implementation, this would either:
        # 1. Request data from the data collector via message bus
        # 2. Access shared data store
        # 3. Have the orchestrator pass the data
        
        # For now, simulate getting data from data collector
        await asyncio.sleep(0.1)  # Simulate data retrieval delay
        
        # Mock historical data - in reality this would come from data collector
        historical_data = {}
        for symbol in request.symbols:
            historical_data[f"{symbol}_historical"] = await self._generate_mock_historical_data(symbol)
        
        return historical_data

    async def _generate_mock_historical_data(self, symbol: str) -> List[StockData]:
        # Generate mock historical data for testing
        import random
        data = []
        base_price = 100
        
        for i in range(252):  # One year of data
            price = base_price + random.uniform(-2, 2)
            data.append(StockData(
                symbol=symbol,
                timestamp=datetime.now(),
                price=price,
                volume=random.randint(1000000, 5000000),
                open_price=price * 0.999,
                high_price=price * 1.002,
                low_price=price * 0.998,
                close_price=price
            ))
            base_price = price
        
        return data

    async def _calculate_indicators(self, symbol: str, historical_data: List[StockData]) -> TechnicalIndicators:
        if not historical_data:
            return TechnicalIndicators(symbol=symbol, timestamp=datetime.now())
        
        # Extract prices
        prices = [data.close_price for data in historical_data[-100:]]  # Last 100 days
        volumes = [data.volume for data in historical_data[-100:]]
        
        if len(prices) < 20:
            return TechnicalIndicators(symbol=symbol, timestamp=datetime.now())
        
        # Calculate indicators
        indicators = TechnicalIndicators(
            symbol=symbol,
            timestamp=datetime.now()
        )
        
        try:
            # RSI
            if 'rsi' in self.indicators:
                indicators.rsi = self._calculate_rsi(prices)
            
            # MACD
            if 'macd' in self.indicators:
                macd, signal = self._calculate_macd(prices)
                indicators.macd = macd
                indicators.macd_signal = signal
            
            # Simple Moving Averages
            if 'sma' in self.indicators:
                if len(prices) >= 20:
                    indicators.sma_20 = sum(prices[-20:]) / 20
                if len(prices) >= 50:
                    indicators.sma_50 = sum(prices[-50:]) / 50
                if len(prices) >= 200:
                    indicators.sma_200 = sum(prices[-200:]) / 200 if len(prices) >= 200 else None
            
            # Bollinger Bands
            if 'bollinger' in self.indicators and len(prices) >= 20:
                sma_20 = sum(prices[-20:]) / 20
                variance = sum((p - sma_20) ** 2 for p in prices[-20:]) / 20
                std_dev = variance ** 0.5
                indicators.bollinger_upper = sma_20 + (2 * std_dev)
                indicators.bollinger_lower = sma_20 - (2 * std_dev)
            
            # Support and Resistance (simple implementation)
            indicators.support_level = min(prices[-20:]) if len(prices) >= 20 else None
            indicators.resistance_level = max(prices[-20:]) if len(prices) >= 20 else None
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators for {symbol}: {e}")
        
        return indicators

    def _calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        if len(prices) < period + 1:
            return None
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        if len(gains) < period:
            return None
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    def _calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        if len(prices) < slow:
            return None, None
        
        # Simple EMA calculation (should be more sophisticated in production)
        ema_fast = sum(prices[-fast:]) / fast
        ema_slow = sum(prices[-slow:]) / slow
        
        macd_line = ema_fast - ema_slow
        
        # Signal line (simplified)
        signal_line = macd_line  # Should be EMA of MACD line
        
        return macd_line, signal_line

    async def _generate_signals(self, symbol: str, indicators: TechnicalIndicators, 
                               historical_data: List[StockData]) -> List[AnalysisSignal]:
        signals = []
        current_price = historical_data[-1].close_price if historical_data else 100
        
        try:
            # RSI-based signals
            if indicators.rsi is not None:
                if indicators.rsi < 30:
                    signals.append(AnalysisSignal(
                        symbol=symbol,
                        signal_type=SignalType.BUY,
                        confidence=0.7,
                        strength=0.6,
                        reason=f"RSI oversold at {indicators.rsi:.1f}",
                        metadata={"indicator": "rsi", "value": indicators.rsi}
                    ))
                elif indicators.rsi > 70:
                    signals.append(AnalysisSignal(
                        symbol=symbol,
                        signal_type=SignalType.SELL,
                        confidence=0.7,
                        strength=-0.6,
                        reason=f"RSI overbought at {indicators.rsi:.1f}",
                        metadata={"indicator": "rsi", "value": indicators.rsi}
                    ))
            
            # Moving Average crossover signals
            if indicators.sma_20 and indicators.sma_50:
                if indicators.sma_20 > indicators.sma_50 and current_price > indicators.sma_20:
                    signals.append(AnalysisSignal(
                        symbol=symbol,
                        signal_type=SignalType.BUY,
                        confidence=0.6,
                        strength=0.5,
                        reason="Price above SMA20 which is above SMA50 (bullish trend)",
                        metadata={"indicator": "sma_crossover", "sma_20": indicators.sma_20, "sma_50": indicators.sma_50}
                    ))
                elif indicators.sma_20 < indicators.sma_50 and current_price < indicators.sma_20:
                    signals.append(AnalysisSignal(
                        symbol=symbol,
                        signal_type=SignalType.SELL,
                        confidence=0.6,
                        strength=-0.5,
                        reason="Price below SMA20 which is below SMA50 (bearish trend)",
                        metadata={"indicator": "sma_crossover", "sma_20": indicators.sma_20, "sma_50": indicators.sma_50}
                    ))
            
            # MACD signals
            if indicators.macd and indicators.macd_signal:
                if indicators.macd > indicators.macd_signal:
                    signals.append(AnalysisSignal(
                        symbol=symbol,
                        signal_type=SignalType.BUY,
                        confidence=0.5,
                        strength=0.4,
                        reason="MACD above signal line",
                        metadata={"indicator": "macd", "macd": indicators.macd, "signal": indicators.macd_signal}
                    ))
                else:
                    signals.append(AnalysisSignal(
                        symbol=symbol,
                        signal_type=SignalType.SELL,
                        confidence=0.5,
                        strength=-0.4,
                        reason="MACD below signal line",
                        metadata={"indicator": "macd", "macd": indicators.macd, "signal": indicators.macd_signal}
                    ))
            
            # Bollinger Bands signals
            if indicators.bollinger_upper and indicators.bollinger_lower:
                if current_price <= indicators.bollinger_lower:
                    signals.append(AnalysisSignal(
                        symbol=symbol,
                        signal_type=SignalType.BUY,
                        confidence=0.6,
                        strength=0.5,
                        reason="Price at lower Bollinger Band (potential bounce)",
                        metadata={"indicator": "bollinger", "price": current_price, "lower": indicators.bollinger_lower}
                    ))
                elif current_price >= indicators.bollinger_upper:
                    signals.append(AnalysisSignal(
                        symbol=symbol,
                        signal_type=SignalType.SELL,
                        confidence=0.6,
                        strength=-0.5,
                        reason="Price at upper Bollinger Band (potential reversal)",
                        metadata={"indicator": "bollinger", "price": current_price, "upper": indicators.bollinger_upper}
                    ))
        
        except Exception as e:
            self.logger.error(f"Error generating signals for {symbol}: {e}")
        
        return signals

    def _calculate_overall_confidence(self, signals: List[AnalysisSignal]) -> float:
        if not signals:
            return 0.0
        
        # Calculate weighted average confidence
        total_confidence = sum(signal.confidence for signal in signals)
        return min(total_confidence / len(signals), 1.0)

    async def health_check(self) -> Dict[str, Any]:
        base_health = await super().health_check()
        base_health.update({
            "supported_indicators": self.indicators,
            "lookback_periods": self.lookback_periods
        })
        return base_health