import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.base_agent import ReportGenerationAgent
from shared.data_models import (
    AnalysisRequest, AnalysisResult, AnalysisType, AnalysisSignal, SignalType
)


class ReportGenerationAgent(ReportGenerationAgent):
    def __init__(self, config, message_bus=None, logger=None):
        super().__init__(config, message_bus, logger)
        
        self.report_formats = config.parameters.get('report_formats', ['pdf', 'html'])
        self.include_charts = config.parameters.get('include_charts', True)
        self.output_dir = Path("reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def process_analysis_request(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        self.logger.info(f"Processing report generation for {len(request.symbols)} symbols")
        
        # Collect analysis results from all other agents
        analysis_results = await self._collect_all_analysis_results(request)
        if not analysis_results:
            self.logger.error("No analysis results available for report generation")
            return None
        
        report_data = {}
        
        try:
            # Generate comprehensive report
            report = await self._generate_comprehensive_report(request, analysis_results)
            if report:
                report_data['comprehensive_report'] = report
            
            # Generate executive summary
            summary = await self._generate_executive_summary(request, analysis_results)
            if summary:
                report_data['executive_summary'] = summary
            
            # Generate actionable insights
            insights = await self._generate_actionable_insights(request, analysis_results)
            if insights:
                report_data['actionable_insights'] = insights
                
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return None
        
        if report_data:
            return AnalysisResult(
                request_id=request.request_id,
                agent_name=self.agent_name,
                symbol=",".join(request.symbols),
                analysis_type=AnalysisType.REPORT,
                data=report_data,
                confidence=1.0,  # Report generation is always successful if data exists
                timestamp=datetime.now()
            )
        
        return None

    async def _collect_all_analysis_results(self, request: AnalysisRequest) -> Dict[str, Any]:
        # In a real implementation, this would collect results from all agents
        # For now, simulate collecting comprehensive analysis data
        await asyncio.sleep(0.2)
        
        analysis_results = {}
        
        for symbol in request.symbols:
            # Mock results from all agents
            analysis_results[f"{symbol}_data"] = await self._get_mock_data_results(symbol)
            analysis_results[f"{symbol}_technical"] = await self._get_mock_technical_results(symbol)
            analysis_results[f"{symbol}_fundamental"] = await self._get_mock_fundamental_results(symbol)
            analysis_results[f"{symbol}_risk"] = await self._get_mock_risk_results(symbol)
            analysis_results[f"{symbol}_sentiment"] = await self._get_mock_sentiment_results(symbol)
            analysis_results[f"{symbol}_charts"] = await self._get_mock_chart_results(symbol)
        
        return analysis_results

    async def _get_mock_data_results(self, symbol: str) -> Dict[str, Any]:
        import random
        return {
            'current_price': random.uniform(80, 120),
            'daily_change': random.uniform(-5, 5),
            'daily_change_percent': random.uniform(-5, 5),
            'volume': random.randint(1000000, 10000000),
            'market_cap': random.uniform(1e9, 1e12),
            'last_updated': datetime.now().isoformat()
        }

    async def _get_mock_technical_results(self, symbol: str) -> Dict[str, Any]:
        import random
        signals = []
        
        # Generate mock technical signals
        signal_types = [SignalType.BUY, SignalType.SELL, SignalType.HOLD]
        for _ in range(random.randint(2, 5)):
            signals.append({
                'signal_type': random.choice(signal_types).value,
                'confidence': random.uniform(0.5, 0.9),
                'strength': random.uniform(-1, 1),
                'reason': f"Technical indicator signal based on {random.choice(['RSI', 'MACD', 'SMA', 'Bollinger'])}",
                'indicator': random.choice(['RSI', 'MACD', 'SMA_crossover', 'bollinger'])
            })
        
        return {
            'signals': signals,
            'rsi': random.uniform(30, 70),
            'macd': random.uniform(-2, 2),
            'trend': random.choice(['bullish', 'bearish', 'neutral']),
            'support_level': random.uniform(90, 95),
            'resistance_level': random.uniform(105, 110)
        }

    async def _get_mock_fundamental_results(self, symbol: str) -> Dict[str, Any]:
        import random
        return {
            'overall_score': random.uniform(0.2, 0.9),
            'pe_ratio': random.uniform(8, 35),
            'pb_ratio': random.uniform(0.8, 4.0),
            'roe': random.uniform(5, 30),
            'debt_to_equity': random.uniform(0.1, 2.5),
            'valuation': random.choice(['undervalued', 'fairly_valued', 'overvalued']),
            'growth_prospects': random.choice(['excellent', 'good', 'moderate', 'poor'])
        }

    async def _get_mock_risk_results(self, symbol: str) -> Dict[str, Any]:
        import random
        return {
            'risk_level': random.choice(['low', 'moderate', 'high', 'very_high']),
            'volatility': random.uniform(0.15, 0.40),
            'beta': random.uniform(0.5, 2.0),
            'var_95': random.uniform(0.02, 0.08),
            'max_drawdown': random.uniform(0.10, 0.35),
            'sharpe_ratio': random.uniform(-0.5, 2.0)
        }

    async def _get_mock_sentiment_results(self, symbol: str) -> Dict[str, Any]:
        import random
        return {
            'overall_sentiment': random.uniform(-0.8, 0.8),
            'news_sentiment': random.uniform(-0.6, 0.6),
            'analyst_sentiment': random.uniform(-0.5, 0.7),
            'social_sentiment': random.uniform(-0.9, 0.9),
            'sentiment_trend': random.choice(['improving', 'deteriorating', 'stable'])
        }

    async def _get_mock_chart_results(self, symbol: str) -> Dict[str, Any]:
        return {
            'candlestick_chart': f"reports/charts/{symbol}_candlestick_chart.json",
            'volume_chart': f"reports/charts/{symbol}_volume_chart.json",
            'indicators_chart': f"reports/charts/{symbol}_indicators_chart.json",
            'fundamental_chart': f"reports/charts/{symbol}_fundamental_chart.json",
            'risk_chart': f"reports/charts/{symbol}_risk_chart.json",
            'sentiment_chart': f"reports/charts/{symbol}_sentiment_chart.json"
        }

    async def _generate_comprehensive_report(self, request: AnalysisRequest, 
                                          analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        try:
            timestamp = datetime.now()
            report = {
                'report_id': f"report_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                'generated_at': timestamp.isoformat(),
                'request_id': request.request_id,
                'symbols': request.symbols,
                'analysis_depth': request.depth,
                'sections': {}
            }
            
            for symbol in request.symbols:
                symbol_section = await self._create_symbol_section(symbol, analysis_results)
                report['sections'][symbol] = symbol_section
            
            # Add portfolio-level analysis if multiple symbols
            if len(request.symbols) > 1:
                portfolio_analysis = await self._create_portfolio_analysis(request.symbols, analysis_results)
                report['sections']['portfolio_summary'] = portfolio_analysis
            
            # Save report to file
            report_path = await self._save_report(report, 'comprehensive')
            report['file_path'] = report_path
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {e}")
            return None

    async def _create_symbol_section(self, symbol: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        data_results = analysis_results.get(f"{symbol}_data", {})
        technical_results = analysis_results.get(f"{symbol}_technical", {})
        fundamental_results = analysis_results.get(f"{symbol}_fundamental", {})
        risk_results = analysis_results.get(f"{symbol}_risk", {})
        sentiment_results = analysis_results.get(f"{symbol}_sentiment", {})
        chart_results = analysis_results.get(f"{symbol}_charts", {})
        
        # Calculate overall recommendation
        overall_recommendation = await self._calculate_overall_recommendation(
            technical_results, fundamental_results, risk_results, sentiment_results
        )
        
        section = {
            'symbol': symbol,
            'overview': {
                'current_price': data_results.get('current_price'),
                'daily_change': data_results.get('daily_change'),
                'daily_change_percent': data_results.get('daily_change_percent'),
                'volume': data_results.get('volume'),
                'market_cap': data_results.get('market_cap')
            },
            'technical_analysis': {
                'trend': technical_results.get('trend'),
                'key_levels': {
                    'support': technical_results.get('support_level'),
                    'resistance': technical_results.get('resistance_level')
                },
                'indicators': {
                    'rsi': technical_results.get('rsi'),
                    'macd': technical_results.get('macd')
                },
                'signals': technical_results.get('signals', [])
            },
            'fundamental_analysis': {
                'overall_score': fundamental_results.get('overall_score'),
                'valuation': fundamental_results.get('valuation'),
                'growth_prospects': fundamental_results.get('growth_prospects'),
                'key_metrics': {
                    'pe_ratio': fundamental_results.get('pe_ratio'),
                    'pb_ratio': fundamental_results.get('pb_ratio'),
                    'roe': fundamental_results.get('roe'),
                    'debt_to_equity': fundamental_results.get('debt_to_equity')
                }
            },
            'risk_assessment': {
                'risk_level': risk_results.get('risk_level'),
                'volatility': risk_results.get('volatility'),
                'beta': risk_results.get('beta'),
                'var_95': risk_results.get('var_95'),
                'max_drawdown': risk_results.get('max_drawdown'),
                'sharpe_ratio': risk_results.get('sharpe_ratio')
            },
            'sentiment_analysis': {
                'overall_sentiment': sentiment_results.get('overall_sentiment'),
                'sentiment_breakdown': {
                    'news': sentiment_results.get('news_sentiment'),
                    'analyst': sentiment_results.get('analyst_sentiment'),
                    'social': sentiment_results.get('social_sentiment')
                },
                'sentiment_trend': sentiment_results.get('sentiment_trend')
            },
            'charts': chart_results,
            'recommendation': overall_recommendation
        }
        
        return section

    async def _calculate_overall_recommendation(self, technical: Dict, fundamental: Dict, 
                                             risk: Dict, sentiment: Dict) -> Dict[str, Any]:
        # Scoring system for overall recommendation
        scores = []
        weights = []
        
        # Technical analysis score
        technical_signals = technical.get('signals', [])
        if technical_signals:
            buy_signals = sum(1 for s in technical_signals if s.get('signal_type') == 'buy')
            sell_signals = sum(1 for s in technical_signals if s.get('signal_type') == 'sell')
            total_signals = len(technical_signals)
            
            if total_signals > 0:
                technical_score = (buy_signals - sell_signals) / total_signals
                scores.append(technical_score)
                weights.append(0.25)
        
        # Fundamental analysis score
        fundamental_score_raw = fundamental.get('overall_score', 0.5)
        fundamental_score = (fundamental_score_raw - 0.5) * 2  # Convert 0-1 to -1 to 1
        scores.append(fundamental_score)
        weights.append(0.35)
        
        # Risk analysis score (inverted - lower risk = higher score)
        risk_level = risk.get('risk_level', 'moderate')
        risk_score_map = {'low': 0.5, 'moderate': 0.0, 'high': -0.5, 'very_high': -1.0}
        risk_score = risk_score_map.get(risk_level, 0.0)
        scores.append(risk_score)
        weights.append(0.20)
        
        # Sentiment analysis score
        sentiment_score = sentiment.get('overall_sentiment', 0.0)
        scores.append(sentiment_score)
        weights.append(0.20)
        
        # Calculate weighted average
        if scores and weights:
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        else:
            weighted_score = 0.0
        
        # Convert to recommendation
        if weighted_score >= 0.6:
            recommendation = "STRONG BUY"
            confidence = min(abs(weighted_score), 1.0)
        elif weighted_score >= 0.2:
            recommendation = "BUY"
            confidence = abs(weighted_score) * 0.8
        elif weighted_score >= -0.2:
            recommendation = "HOLD"
            confidence = 0.5
        elif weighted_score >= -0.6:
            recommendation = "SELL"
            confidence = abs(weighted_score) * 0.8
        else:
            recommendation = "STRONG SELL"
            confidence = min(abs(weighted_score), 1.0)
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'score': weighted_score,
            'reasoning': await self._generate_recommendation_reasoning(
                recommendation, technical, fundamental, risk, sentiment
            )
        }

    async def _generate_recommendation_reasoning(self, recommendation: str, technical: Dict, 
                                               fundamental: Dict, risk: Dict, sentiment: Dict) -> str:
        reasons = []
        
        # Technical reasoning
        trend = technical.get('trend', 'neutral')
        if trend == 'bullish':
            reasons.append("Technical indicators show bullish trend")
        elif trend == 'bearish':
            reasons.append("Technical indicators show bearish trend")
        
        # Fundamental reasoning
        valuation = fundamental.get('valuation', 'fairly_valued')
        if valuation == 'undervalued':
            reasons.append("Company appears undervalued based on fundamentals")
        elif valuation == 'overvalued':
            reasons.append("Company appears overvalued based on fundamentals")
        
        growth = fundamental.get('growth_prospects', 'moderate')
        if growth == 'excellent':
            reasons.append("Excellent growth prospects")
        elif growth == 'poor':
            reasons.append("Poor growth prospects")
        
        # Risk reasoning
        risk_level = risk.get('risk_level', 'moderate')
        if risk_level in ['high', 'very_high']:
            reasons.append(f"High risk level ({risk_level})")
        elif risk_level == 'low':
            reasons.append("Low risk profile")
        
        # Sentiment reasoning
        overall_sentiment = sentiment.get('overall_sentiment', 0.0)
        if overall_sentiment >= 0.5:
            reasons.append("Strong positive market sentiment")
        elif overall_sentiment <= -0.5:
            reasons.append("Strong negative market sentiment")
        
        return "; ".join(reasons) if reasons else f"Based on comprehensive analysis across all factors"

    async def _create_portfolio_analysis(self, symbols: List[str], 
                                       analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        portfolio_analysis = {
            'summary': {
                'total_symbols': len(symbols),
                'analysis_date': datetime.now().isoformat()
            },
            'recommendations_distribution': {},
            'risk_profile': {},
            'sector_allocation': {},  # Would be filled with actual sector data
            'correlation_analysis': {}  # Would be filled with correlation data
        }
        
        # Count recommendations
        recommendations = []
        risk_levels = []
        
        for symbol in symbols:
            # This would use actual recommendation data
            # For now, using mock data
            import random
            rec = random.choice(['STRONG BUY', 'BUY', 'HOLD', 'SELL', 'STRONG SELL'])
            recommendations.append(rec)
            
            risk = random.choice(['low', 'moderate', 'high', 'very_high'])
            risk_levels.append(risk)
        
        # Calculate distributions
        from collections import Counter
        rec_distribution = Counter(recommendations)
        risk_distribution = Counter(risk_levels)
        
        portfolio_analysis['recommendations_distribution'] = dict(rec_distribution)
        portfolio_analysis['risk_profile'] = dict(risk_distribution)
        
        return portfolio_analysis

    async def _generate_executive_summary(self, request: AnalysisRequest, 
                                        analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        try:
            summary = {
                'title': f"Executive Summary - {', '.join(request.symbols)}",
                'generated_at': datetime.now().isoformat(),
                'key_findings': [],
                'investment_thesis': [],
                'risk_factors': [],
                'recommendations': []
            }
            
            for symbol in request.symbols:
                # Extract key findings for each symbol
                technical_results = analysis_results.get(f"{symbol}_technical", {})
                fundamental_results = analysis_results.get(f"{symbol}_fundamental", {})
                risk_results = analysis_results.get(f"{symbol}_risk", {})
                sentiment_results = analysis_results.get(f"{symbol}_sentiment", {})
                
                # Key findings
                trend = technical_results.get('trend', 'neutral')
                if trend != 'neutral':
                    summary['key_findings'].append(f"{symbol}: {trend.capitalize()} technical trend")
                
                valuation = fundamental_results.get('valuation', 'fairly_valued')
                if valuation != 'fairly_valued':
                    summary['key_findings'].append(f"{symbol}: {valuation.replace('_', ' ').title()}")
                
                risk_level = risk_results.get('risk_level', 'moderate')
                if risk_level in ['high', 'very_high', 'low']:
                    summary['key_findings'].append(f"{symbol}: {risk_level.replace('_', ' ').title()} risk")
                
                # Investment thesis
                growth = fundamental_results.get('growth_prospects', 'moderate')
                if growth in ['excellent', 'good']:
                    summary['investment_thesis'].append(f"{symbol}: {growth.capitalize()} growth prospects")
                
                # Risk factors
                volatility = risk_results.get('volatility', 0.2)
                if volatility > 0.3:
                    summary['risk_factors'].append(f"{symbol}: High volatility ({volatility:.1%})")
            
            # Overall recommendations
            if len(request.symbols) == 1:
                symbol = request.symbols[0]
                # Would calculate actual recommendation
                summary['recommendations'].append(f"Maintain current position in {symbol} with close monitoring")
            else:
                summary['recommendations'].append("Diversified portfolio approach recommended")
                summary['recommendations'].append("Monitor risk levels across all positions")
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating executive summary: {e}")
            return None

    async def _generate_actionable_insights(self, request: AnalysisRequest, 
                                          analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        try:
            insights = {
                'immediate_actions': [],
                'monitoring_points': [],
                'risk_management': [],
                'opportunities': [],
                'timeline': 'Next 30 days'
            }
            
            for symbol in request.symbols:
                technical_results = analysis_results.get(f"{symbol}_technical", {})
                risk_results = analysis_results.get(f"{symbol}_risk", {})
                
                # Immediate actions
                support = technical_results.get('support_level')
                resistance = technical_results.get('resistance_level')
                
                if support:
                    insights['immediate_actions'].append(
                        f"Set stop-loss for {symbol} below support level at ${support:.2f}"
                    )
                
                if resistance:
                    insights['monitoring_points'].append(
                        f"Watch for {symbol} breakout above resistance at ${resistance:.2f}"
                    )
                
                # Risk management
                risk_level = risk_results.get('risk_level', 'moderate')
                if risk_level in ['high', 'very_high']:
                    insights['risk_management'].append(
                        f"Consider reducing position size in {symbol} due to {risk_level} risk"
                    )
                
                # Opportunities
                volatility = risk_results.get('volatility', 0.2)
                if volatility > 0.25:
                    insights['opportunities'].append(
                        f"High volatility in {symbol} may provide trading opportunities"
                    )
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating actionable insights: {e}")
            return None

    async def _save_report(self, report: Dict[str, Any], report_type: str) -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"stock_analysis_{report_type}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Saved report: {filepath}")
        return str(filepath)

    async def health_check(self) -> Dict[str, Any]:
        base_health = await super().health_check()
        base_health.update({
            "supported_formats": self.report_formats,
            "include_charts": self.include_charts,
            "output_directory": str(self.output_dir)
        })
        return base_health