import asyncio
import math
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.base_agent import RiskAssessmentAgent
from shared.data_models import (
    AnalysisRequest, AnalysisResult, RiskMetrics, RiskLevel,
    AnalysisSignal, SignalType, AnalysisType, StockData
)


class RiskAssessmentAgent(RiskAssessmentAgent):
    def __init__(self, config, message_bus=None, logger=None):
        super().__init__(config, message_bus, logger)
        
        self.confidence_level = config.parameters.get('confidence_level', 0.95)
        self.lookback_days = config.parameters.get('lookback_days', 252)

    async def process_analysis_request(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        self.logger.info(f"Processing risk assessment for {len(request.symbols)} symbols")
        
        # Get historical data for risk calculations
        historical_data = await self._get_historical_data(request)
        if not historical_data:
            self.logger.error("No historical data available for risk assessment")
            return None
        
        analysis_data = {}
        signals = []
        
        for symbol in request.symbols:
            symbol_data = historical_data.get(f"{symbol}_historical", [])
            if not symbol_data:
                self.logger.warning(f"No historical data for {symbol}")
                continue
            
            try:
                # Calculate risk metrics
                risk_metrics = await self._calculate_risk_metrics(symbol, symbol_data)
                analysis_data[f"{symbol}_risk"] = risk_metrics
                
                # Generate risk-based signals
                symbol_signals = await self._generate_risk_signals(symbol, risk_metrics)
                signals.extend(symbol_signals)
                
            except Exception as e:
                self.logger.error(f"Error assessing risk for {symbol}: {e}")
                continue
        
        if analysis_data or signals:
            return AnalysisResult(
                request_id=request.request_id,
                agent_name=self.agent_name,
                symbol=",".join(request.symbols),
                analysis_type=AnalysisType.RISK,
                signals=signals,
                data=analysis_data,
                confidence=self._calculate_overall_confidence(signals),
                timestamp=datetime.now()
            )
        
        return None

    async def _get_historical_data(self, request: AnalysisRequest) -> Dict[str, Any]:
        # Simulate getting historical data from data collector
        await asyncio.sleep(0.1)
        
        historical_data = {}
        for symbol in request.symbols:
            historical_data[f"{symbol}_historical"] = await self._generate_mock_historical_data(symbol)
        
        return historical_data

    async def _generate_mock_historical_data(self, symbol: str) -> List[StockData]:
        # Generate mock historical data with realistic volatility patterns
        import random
        data = []
        base_price = 100
        volatility = random.uniform(0.15, 0.4)  # Annual volatility between 15-40%
        daily_vol = volatility / math.sqrt(252)  # Convert to daily volatility
        
        for i in range(self.lookback_days):
            # Generate price with random walk and volatility
            return_rate = random.gauss(0, daily_vol)
            price = base_price * (1 + return_rate)
            
            data.append(StockData(
                symbol=symbol,
                timestamp=datetime.now() - timedelta(days=self.lookback_days-i),
                price=price,
                volume=random.randint(1000000, 5000000),
                open_price=price * 0.999,
                high_price=price * 1.002,
                low_price=price * 0.998,
                close_price=price
            ))
            base_price = price
        
        return data

    async def _calculate_risk_metrics(self, symbol: str, historical_data: List[StockData]) -> RiskMetrics:
        if len(historical_data) < 30:
            return RiskMetrics(
                symbol=symbol,
                timestamp=datetime.now(),
                volatility=0.0,
                beta=1.0,
                risk_level=RiskLevel.MODERATE
            )
        
        # Extract prices and calculate returns
        prices = [data.close_price for data in historical_data]
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # Calculate volatility (annualized)
        volatility = self._calculate_volatility(returns)
        
        # Calculate beta (simplified - using market proxy)
        beta = await self._calculate_beta(returns)
        
        # Calculate Value at Risk (VaR)
        var = self._calculate_var(returns, self.confidence_level)
        
        # Calculate maximum drawdown
        max_drawdown = self._calculate_max_drawdown(prices)
        
        # Calculate Sharpe ratio (simplified)
        sharpe_ratio = self._calculate_sharpe_ratio(returns, risk_free_rate=0.02/252)  # 2% annual risk-free rate
        
        # Determine risk level
        risk_level = self._determine_risk_level(volatility, max_drawdown, var)
        
        return RiskMetrics(
            symbol=symbol,
            timestamp=datetime.now(),
            volatility=volatility,
            beta=beta,
            value_at_risk=var,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            risk_level=risk_level
        )

    def _calculate_volatility(self, returns: List[float]) -> float:
        if not returns:
            return 0.0
        
        # Calculate standard deviation of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        daily_volatility = math.sqrt(variance)
        
        # Annualize volatility
        annual_volatility = daily_volatility * math.sqrt(252)
        
        return annual_volatility

    async def _calculate_beta(self, returns: List[float]) -> float:
        # Simplified beta calculation using a mock market return
        # In reality, this would compare against actual market index returns
        import random
        
        # Generate mock market returns
        market_returns = [random.gauss(0.0008, 0.015) for _ in range(len(returns))]
        
        if len(returns) != len(market_returns) or len(returns) < 2:
            return 1.0
        
        # Calculate covariance and market variance
        mean_stock = sum(returns) / len(returns)
        mean_market = sum(market_returns) / len(market_returns)
        
        covariance = sum((returns[i] - mean_stock) * (market_returns[i] - mean_market) 
                        for i in range(len(returns))) / len(returns)
        
        market_variance = sum((r - mean_market) ** 2 for r in market_returns) / len(market_returns)
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        return max(min(beta, 3.0), -1.0)  # Cap beta between -1 and 3

    def _calculate_var(self, returns: List[float], confidence_level: float) -> float:
        if not returns:
            return 0.0
        
        # Sort returns and find the percentile
        sorted_returns = sorted(returns)
        percentile_index = int((1 - confidence_level) * len(sorted_returns))
        
        if percentile_index >= len(sorted_returns):
            percentile_index = len(sorted_returns) - 1
        
        var = abs(sorted_returns[percentile_index])
        return var

    def _calculate_max_drawdown(self, prices: List[float]) -> float:
        if len(prices) < 2:
            return 0.0
        
        max_drawdown = 0.0
        peak = prices[0]
        
        for price in prices[1:]:
            if price > peak:
                peak = price
            else:
                drawdown = (peak - price) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown

    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float) -> Optional[float]:
        if not returns:
            return None
        
        # Calculate excess returns
        excess_returns = [r - risk_free_rate for r in returns]
        
        # Calculate mean excess return
        mean_excess_return = sum(excess_returns) / len(excess_returns)
        
        # Calculate standard deviation of excess returns
        if len(excess_returns) <= 1:
            return None
        
        variance = sum((r - mean_excess_return) ** 2 for r in excess_returns) / (len(excess_returns) - 1)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return None
        
        # Annualize Sharpe ratio
        sharpe_ratio = (mean_excess_return * 252) / (std_dev * math.sqrt(252))
        
        return sharpe_ratio

    def _determine_risk_level(self, volatility: float, max_drawdown: float, var: float) -> RiskLevel:
        risk_score = 0
        
        # Volatility scoring
        if volatility > 0.4:  # 40% annual volatility
            risk_score += 3
        elif volatility > 0.25:  # 25% annual volatility
            risk_score += 2
        elif volatility > 0.15:  # 15% annual volatility
            risk_score += 1
        
        # Maximum drawdown scoring
        if max_drawdown > 0.5:  # 50% drawdown
            risk_score += 3
        elif max_drawdown > 0.3:  # 30% drawdown
            risk_score += 2
        elif max_drawdown > 0.15:  # 15% drawdown
            risk_score += 1
        
        # VaR scoring
        if var > 0.05:  # 5% daily VaR
            risk_score += 2
        elif var > 0.03:  # 3% daily VaR
            risk_score += 1
        
        # Determine risk level based on score
        if risk_score >= 6:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 4:
            return RiskLevel.HIGH
        elif risk_score >= 2:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    async def _generate_risk_signals(self, symbol: str, risk_metrics: RiskMetrics) -> List[AnalysisSignal]:
        signals = []
        
        try:
            # Risk level based signals
            if risk_metrics.risk_level == RiskLevel.VERY_HIGH:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.STRONG_SELL,
                    confidence=0.8,
                    strength=-0.8,
                    reason=f"Very high risk level with volatility {risk_metrics.volatility:.1%}",
                    metadata={"risk_level": risk_metrics.risk_level.value, "volatility": risk_metrics.volatility}
                ))
            elif risk_metrics.risk_level == RiskLevel.HIGH:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    confidence=0.7,
                    strength=-0.6,
                    reason=f"High risk level with volatility {risk_metrics.volatility:.1%}",
                    metadata={"risk_level": risk_metrics.risk_level.value, "volatility": risk_metrics.volatility}
                ))
            elif risk_metrics.risk_level == RiskLevel.LOW:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    confidence=0.6,
                    strength=0.5,
                    reason=f"Low risk level with volatility {risk_metrics.volatility:.1%}",
                    metadata={"risk_level": risk_metrics.risk_level.value, "volatility": risk_metrics.volatility}
                ))
            
            # Volatility-based signals
            if risk_metrics.volatility > 0.5:  # Very high volatility
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    confidence=0.7,
                    strength=-0.6,
                    reason=f"Extremely high volatility of {risk_metrics.volatility:.1%}",
                    metadata={"metric": "volatility", "value": risk_metrics.volatility}
                ))
            elif risk_metrics.volatility < 0.15:  # Low volatility
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    confidence=0.5,
                    strength=0.3,
                    reason=f"Low volatility of {risk_metrics.volatility:.1%} indicates stability",
                    metadata={"metric": "volatility", "value": risk_metrics.volatility}
                ))
            
            # Beta-based signals
            if risk_metrics.beta > 1.5:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    confidence=0.5,
                    strength=-0.4,
                    reason=f"High beta of {risk_metrics.beta:.2f} indicates high market sensitivity",
                    metadata={"metric": "beta", "value": risk_metrics.beta}
                ))
            elif risk_metrics.beta < 0.5:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    confidence=0.5,
                    strength=0.3,
                    reason=f"Low beta of {risk_metrics.beta:.2f} indicates defensive characteristics",
                    metadata={"metric": "beta", "value": risk_metrics.beta}
                ))
            
            # Maximum drawdown signals
            if risk_metrics.max_drawdown and risk_metrics.max_drawdown > 0.4:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    confidence=0.6,
                    strength=-0.5,
                    reason=f"High maximum drawdown of {risk_metrics.max_drawdown:.1%}",
                    metadata={"metric": "max_drawdown", "value": risk_metrics.max_drawdown}
                ))
            
            # Sharpe ratio signals
            if risk_metrics.sharpe_ratio:
                if risk_metrics.sharpe_ratio > 1.5:
                    signals.append(AnalysisSignal(
                        symbol=symbol,
                        signal_type=SignalType.BUY,
                        confidence=0.6,
                        strength=0.5,
                        reason=f"Excellent Sharpe ratio of {risk_metrics.sharpe_ratio:.2f}",
                        metadata={"metric": "sharpe_ratio", "value": risk_metrics.sharpe_ratio}
                    ))
                elif risk_metrics.sharpe_ratio < 0:
                    signals.append(AnalysisSignal(
                        symbol=symbol,
                        signal_type=SignalType.SELL,
                        confidence=0.6,
                        strength=-0.5,
                        reason=f"Negative Sharpe ratio of {risk_metrics.sharpe_ratio:.2f}",
                        metadata={"metric": "sharpe_ratio", "value": risk_metrics.sharpe_ratio}
                    ))
        
        except Exception as e:
            self.logger.error(f"Error generating risk signals for {symbol}: {e}")
        
        return signals

    def _calculate_overall_confidence(self, signals: List[AnalysisSignal]) -> float:
        if not signals:
            return 0.0
        
        # Risk assessment confidence is based on data quality and signal consistency
        confidence_scores = [signal.confidence for signal in signals]
        return sum(confidence_scores) / len(confidence_scores)

    async def health_check(self) -> Dict[str, Any]:
        base_health = await super().health_check()
        base_health.update({
            "confidence_level": self.confidence_level,
            "lookback_days": self.lookback_days
        })
        return base_health