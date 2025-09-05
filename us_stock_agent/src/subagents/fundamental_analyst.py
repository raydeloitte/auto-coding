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

from shared.base_agent import FundamentalAnalysisAgent
from shared.data_models import (
    AnalysisRequest, AnalysisResult, FundamentalData,
    AnalysisSignal, SignalType, AnalysisType, StockData
)


class FundamentalAnalysisAgent(FundamentalAnalysisAgent):
    def __init__(self, config, message_bus=None, logger=None):
        super().__init__(config, message_bus, logger)
        
        self.metrics = config.parameters.get('metrics', ['pe', 'pb', 'roe', 'debt_to_equity'])
        self.peer_comparison = config.parameters.get('peer_comparison', True)

    async def process_analysis_request(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        self.logger.info(f"Processing fundamental analysis for {len(request.symbols)} symbols")
        
        # Get fundamental data
        fundamental_data = await self._get_fundamental_data(request)
        if not fundamental_data:
            self.logger.error("No fundamental data available")
            return None
        
        analysis_data = {}
        signals = []
        
        for symbol in request.symbols:
            symbol_fundamental = fundamental_data.get(f"{symbol}_fundamental")
            if not symbol_fundamental:
                self.logger.warning(f"No fundamental data for {symbol}")
                continue
            
            try:
                # Analyze fundamental metrics
                analysis = await self._analyze_fundamentals(symbol, symbol_fundamental)
                analysis_data[f"{symbol}_fundamental_analysis"] = analysis
                
                # Generate investment signals
                symbol_signals = await self._generate_investment_signals(symbol, symbol_fundamental, analysis)
                signals.extend(symbol_signals)
                
            except Exception as e:
                self.logger.error(f"Error analyzing fundamentals for {symbol}: {e}")
                continue
        
        if analysis_data or signals:
            return AnalysisResult(
                request_id=request.request_id,
                agent_name=self.agent_name,
                symbol=",".join(request.symbols),
                analysis_type=AnalysisType.FUNDAMENTAL,
                signals=signals,
                data=analysis_data,
                confidence=self._calculate_overall_confidence(signals),
                timestamp=datetime.now()
            )
        
        return None

    async def _get_fundamental_data(self, request: AnalysisRequest) -> Dict[str, Any]:
        # Simulate getting fundamental data from data collector
        await asyncio.sleep(0.1)
        
        fundamental_data = {}
        for symbol in request.symbols:
            fundamental_data[f"{symbol}_fundamental"] = await self._generate_mock_fundamental_data(symbol)
        
        return fundamental_data

    async def _generate_mock_fundamental_data(self, symbol: str) -> FundamentalData:
        import random
        return FundamentalData(
            symbol=symbol,
            timestamp=datetime.now(),
            pe_ratio=random.uniform(8, 35),
            pb_ratio=random.uniform(0.8, 4.0),
            roe=random.uniform(5, 30),
            debt_to_equity=random.uniform(0.1, 2.5),
            revenue_growth=random.uniform(-15, 25),
            eps_growth=random.uniform(-20, 30),
            free_cash_flow=random.uniform(-500000, 2000000),
            dividend_yield=random.uniform(0, 6)
        )

    async def _analyze_fundamentals(self, symbol: str, fundamental_data: FundamentalData) -> Dict[str, Any]:
        analysis = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "valuation": {},
            "profitability": {},
            "financial_health": {},
            "growth": {},
            "overall_score": 0.0
        }
        
        try:
            # Valuation Analysis
            valuation_score = 0.0
            valuation_signals = []
            
            if fundamental_data.pe_ratio:
                if fundamental_data.pe_ratio < 15:
                    valuation_score += 2
                    valuation_signals.append("Low PE ratio indicates potential undervaluation")
                elif fundamental_data.pe_ratio > 25:
                    valuation_score -= 1
                    valuation_signals.append("High PE ratio indicates potential overvaluation")
                else:
                    valuation_score += 1
                    valuation_signals.append("PE ratio in reasonable range")
            
            if fundamental_data.pb_ratio:
                if fundamental_data.pb_ratio < 1.5:
                    valuation_score += 1
                    valuation_signals.append("Low PB ratio suggests good value")
                elif fundamental_data.pb_ratio > 3:
                    valuation_score -= 1
                    valuation_signals.append("High PB ratio suggests premium valuation")
            
            analysis["valuation"] = {
                "score": min(max(valuation_score, 0), 5),
                "signals": valuation_signals,
                "pe_ratio": fundamental_data.pe_ratio,
                "pb_ratio": fundamental_data.pb_ratio
            }
            
            # Profitability Analysis
            profitability_score = 0.0
            profitability_signals = []
            
            if fundamental_data.roe:
                if fundamental_data.roe > 20:
                    profitability_score += 2
                    profitability_signals.append("High ROE indicates excellent profitability")
                elif fundamental_data.roe > 15:
                    profitability_score += 1
                    profitability_signals.append("Good ROE indicates solid profitability")
                elif fundamental_data.roe < 10:
                    profitability_score -= 1
                    profitability_signals.append("Low ROE indicates weak profitability")
            
            analysis["profitability"] = {
                "score": min(max(profitability_score, 0), 5),
                "signals": profitability_signals,
                "roe": fundamental_data.roe
            }
            
            # Financial Health Analysis
            health_score = 0.0
            health_signals = []
            
            if fundamental_data.debt_to_equity:
                if fundamental_data.debt_to_equity < 0.5:
                    health_score += 2
                    health_signals.append("Low debt-to-equity ratio indicates strong financial health")
                elif fundamental_data.debt_to_equity < 1.0:
                    health_score += 1
                    health_signals.append("Moderate debt-to-equity ratio indicates acceptable financial health")
                else:
                    health_score -= 1
                    health_signals.append("High debt-to-equity ratio indicates potential financial risk")
            
            if fundamental_data.free_cash_flow:
                if fundamental_data.free_cash_flow > 0:
                    health_score += 1
                    health_signals.append("Positive free cash flow indicates good cash generation")
                else:
                    health_score -= 1
                    health_signals.append("Negative free cash flow indicates cash flow challenges")
            
            analysis["financial_health"] = {
                "score": min(max(health_score, 0), 5),
                "signals": health_signals,
                "debt_to_equity": fundamental_data.debt_to_equity,
                "free_cash_flow": fundamental_data.free_cash_flow
            }
            
            # Growth Analysis
            growth_score = 0.0
            growth_signals = []
            
            if fundamental_data.revenue_growth:
                if fundamental_data.revenue_growth > 15:
                    growth_score += 2
                    growth_signals.append("High revenue growth indicates strong business expansion")
                elif fundamental_data.revenue_growth > 5:
                    growth_score += 1
                    growth_signals.append("Moderate revenue growth indicates steady business growth")
                elif fundamental_data.revenue_growth < 0:
                    growth_score -= 1
                    growth_signals.append("Negative revenue growth indicates business contraction")
            
            if fundamental_data.eps_growth:
                if fundamental_data.eps_growth > 15:
                    growth_score += 2
                    growth_signals.append("High EPS growth indicates strong earnings momentum")
                elif fundamental_data.eps_growth > 5:
                    growth_score += 1
                    growth_signals.append("Moderate EPS growth indicates steady earnings growth")
                elif fundamental_data.eps_growth < 0:
                    growth_score -= 1
                    growth_signals.append("Negative EPS growth indicates earnings decline")
            
            analysis["growth"] = {
                "score": min(max(growth_score, 0), 5),
                "signals": growth_signals,
                "revenue_growth": fundamental_data.revenue_growth,
                "eps_growth": fundamental_data.eps_growth
            }
            
            # Overall Score
            total_score = (
                analysis["valuation"]["score"] +
                analysis["profitability"]["score"] +
                analysis["financial_health"]["score"] +
                analysis["growth"]["score"]
            )
            analysis["overall_score"] = total_score / 20.0  # Normalize to 0-1 scale
            
        except Exception as e:
            self.logger.error(f"Error in fundamental analysis for {symbol}: {e}")
        
        return analysis

    async def _generate_investment_signals(self, symbol: str, fundamental_data: FundamentalData, 
                                         analysis: Dict[str, Any]) -> List[AnalysisSignal]:
        signals = []
        overall_score = analysis.get("overall_score", 0.0)
        
        try:
            # Generate signals based on overall score
            if overall_score >= 0.8:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.STRONG_BUY,
                    confidence=0.8,
                    strength=0.8,
                    reason=f"Excellent fundamentals with overall score of {overall_score:.2f}",
                    metadata={"fundamental_score": overall_score, "analysis": "comprehensive"}
                ))
            elif overall_score >= 0.6:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    confidence=0.7,
                    strength=0.6,
                    reason=f"Strong fundamentals with overall score of {overall_score:.2f}",
                    metadata={"fundamental_score": overall_score, "analysis": "comprehensive"}
                ))
            elif overall_score >= 0.4:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.HOLD,
                    confidence=0.6,
                    strength=0.0,
                    reason=f"Mixed fundamentals with overall score of {overall_score:.2f}",
                    metadata={"fundamental_score": overall_score, "analysis": "comprehensive"}
                ))
            elif overall_score >= 0.2:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    confidence=0.7,
                    strength=-0.6,
                    reason=f"Weak fundamentals with overall score of {overall_score:.2f}",
                    metadata={"fundamental_score": overall_score, "analysis": "comprehensive"}
                ))
            else:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.STRONG_SELL,
                    confidence=0.8,
                    strength=-0.8,
                    reason=f"Poor fundamentals with overall score of {overall_score:.2f}",
                    metadata={"fundamental_score": overall_score, "analysis": "comprehensive"}
                ))
            
            # Specific metric-based signals
            if fundamental_data.pe_ratio and fundamental_data.pe_ratio < 10:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    confidence=0.6,
                    strength=0.5,
                    reason=f"Very low PE ratio of {fundamental_data.pe_ratio:.1f} suggests undervaluation",
                    metadata={"metric": "pe_ratio", "value": fundamental_data.pe_ratio}
                ))
            
            if fundamental_data.roe and fundamental_data.roe > 25:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    confidence=0.7,
                    strength=0.6,
                    reason=f"Excellent ROE of {fundamental_data.roe:.1f}% indicates high profitability",
                    metadata={"metric": "roe", "value": fundamental_data.roe}
                ))
            
            if fundamental_data.debt_to_equity and fundamental_data.debt_to_equity > 2.0:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    confidence=0.6,
                    strength=-0.5,
                    reason=f"High debt-to-equity ratio of {fundamental_data.debt_to_equity:.1f} indicates financial risk",
                    metadata={"metric": "debt_to_equity", "value": fundamental_data.debt_to_equity}
                ))
            
            # Growth-based signals
            if (fundamental_data.revenue_growth and fundamental_data.eps_growth and
                fundamental_data.revenue_growth > 20 and fundamental_data.eps_growth > 20):
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.STRONG_BUY,
                    confidence=0.8,
                    strength=0.7,
                    reason=f"Strong growth: {fundamental_data.revenue_growth:.1f}% revenue, {fundamental_data.eps_growth:.1f}% EPS",
                    metadata={"growth_type": "high_growth", "revenue_growth": fundamental_data.revenue_growth, "eps_growth": fundamental_data.eps_growth}
                ))
        
        except Exception as e:
            self.logger.error(f"Error generating investment signals for {symbol}: {e}")
        
        return signals

    def _calculate_overall_confidence(self, signals: List[AnalysisSignal]) -> float:
        if not signals:
            return 0.0
        
        # Weight confidence by signal strength
        weighted_confidence = sum(abs(signal.strength) * signal.confidence for signal in signals)
        total_weight = sum(abs(signal.strength) for signal in signals)
        
        if total_weight == 0:
            return sum(signal.confidence for signal in signals) / len(signals)
        
        return min(weighted_confidence / total_weight, 1.0)

    async def health_check(self) -> Dict[str, Any]:
        base_health = await super().health_check()
        base_health.update({
            "supported_metrics": self.metrics,
            "peer_comparison_enabled": self.peer_comparison
        })
        return base_health