import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.base_agent import SentimentAnalysisAgent
from shared.data_models import (
    AnalysisRequest, AnalysisResult, SentimentData,
    AnalysisSignal, SignalType, AnalysisType
)


class SentimentAnalysisAgent(SentimentAnalysisAgent):
    def __init__(self, config, message_bus=None, logger=None):
        super().__init__(config, message_bus, logger)
        
        self.news_sources = config.parameters.get('news_sources', ['reuters', 'bloomberg', 'yahoo'])
        self.sentiment_window_hours = config.parameters.get('sentiment_window_hours', 24)

    async def process_analysis_request(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        self.logger.info(f"Processing sentiment analysis for {len(request.symbols)} symbols")
        
        analysis_data = {}
        signals = []
        
        for symbol in request.symbols:
            try:
                # Collect sentiment data
                sentiment_data = await self._collect_sentiment_data(symbol)
                if sentiment_data:
                    analysis_data[f"{symbol}_sentiment"] = sentiment_data
                    
                    # Generate sentiment-based signals
                    symbol_signals = await self._generate_sentiment_signals(symbol, sentiment_data)
                    signals.extend(symbol_signals)
                
            except Exception as e:
                self.logger.error(f"Error analyzing sentiment for {symbol}: {e}")
                continue
        
        if analysis_data or signals:
            return AnalysisResult(
                request_id=request.request_id,
                agent_name=self.agent_name,
                symbol=",".join(request.symbols),
                analysis_type=AnalysisType.SENTIMENT,
                signals=signals,
                data=analysis_data,
                confidence=self._calculate_overall_confidence(signals),
                timestamp=datetime.now()
            )
        
        return None

    async def _collect_sentiment_data(self, symbol: str) -> Optional[SentimentData]:
        try:
            # Simulate collecting sentiment data from various sources
            news_sentiment = await self._analyze_news_sentiment(symbol)
            social_sentiment = await self._analyze_social_sentiment(symbol)
            analyst_sentiment = await self._analyze_analyst_sentiment(symbol)
            insider_activity = await self._analyze_insider_activity(symbol)
            
            # Combine all sentiment scores
            overall_sentiment = (
                news_sentiment * 0.3 +
                social_sentiment * 0.2 +
                analyst_sentiment * 0.4 +
                insider_activity * 0.1
            )
            
            return SentimentData(
                symbol=symbol,
                timestamp=datetime.now(),
                sentiment_score=overall_sentiment,
                news_sentiment=news_sentiment,
                social_sentiment=social_sentiment,
                analyst_sentiment=analyst_sentiment,
                insider_activity_score=insider_activity
            )
            
        except Exception as e:
            self.logger.error(f"Error collecting sentiment data for {symbol}: {e}")
            return None

    async def _analyze_news_sentiment(self, symbol: str) -> float:
        # Simulate news sentiment analysis
        await asyncio.sleep(0.1)
        
        # TODO: Implement actual news sentiment analysis
        # This would involve:
        # 1. Fetching recent news articles about the symbol
        # 2. Using NLP to analyze sentiment (positive/negative/neutral)
        # 3. Weighting by news source credibility and recency
        
        import random
        # Mock sentiment analysis results
        sentiment_scores = []
        
        for source in self.news_sources:
            # Simulate different sentiment for different news sources
            base_sentiment = random.uniform(-0.5, 0.5)
            
            # Add some source-specific bias (e.g., Bloomberg might be more conservative)
            if source == 'bloomberg':
                base_sentiment *= 0.8  # More conservative
            elif source == 'yahoo':
                base_sentiment *= 1.2  # More volatile
            
            sentiment_scores.append(max(min(base_sentiment, 1.0), -1.0))
        
        # Return weighted average
        return sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0

    async def _analyze_social_sentiment(self, symbol: str) -> float:
        # Simulate social media sentiment analysis
        await asyncio.sleep(0.1)
        
        # TODO: Implement actual social media sentiment analysis
        # This would involve:
        # 1. Fetching tweets, Reddit posts, etc. mentioning the symbol
        # 2. Using sentiment analysis models
        # 3. Weighting by user influence and engagement
        
        import random
        # Simulate social sentiment (typically more volatile than news)
        social_sentiment = random.uniform(-0.8, 0.8)
        
        # Add some noise to simulate social media volatility
        noise = random.uniform(-0.2, 0.2)
        social_sentiment += noise
        
        return max(min(social_sentiment, 1.0), -1.0)

    async def _analyze_analyst_sentiment(self, symbol: str) -> float:
        # Simulate analyst sentiment analysis
        await asyncio.sleep(0.1)
        
        # TODO: Implement actual analyst recommendation analysis
        # This would involve:
        # 1. Fetching recent analyst reports and recommendations
        # 2. Converting ratings (buy/hold/sell) to numerical scores
        # 3. Weighting by analyst reputation and accuracy
        
        import random
        # Simulate analyst recommendations
        recommendations = random.choices(
            ['strong_buy', 'buy', 'hold', 'sell', 'strong_sell'],
            weights=[0.2, 0.3, 0.3, 0.15, 0.05],  # Typical distribution
            k=random.randint(3, 8)  # 3-8 analyst recommendations
        )
        
        # Convert recommendations to numerical scores
        score_map = {
            'strong_buy': 1.0,
            'buy': 0.5,
            'hold': 0.0,
            'sell': -0.5,
            'strong_sell': -1.0
        }
        
        scores = [score_map[rec] for rec in recommendations]
        return sum(scores) / len(scores) if scores else 0.0

    async def _analyze_insider_activity(self, symbol: str) -> float:
        # Simulate insider trading activity analysis
        await asyncio.sleep(0.05)
        
        # TODO: Implement actual insider trading analysis
        # This would involve:
        # 1. Fetching recent insider trading data
        # 2. Analyzing buy vs sell patterns
        # 3. Considering transaction sizes and timing
        
        import random
        # Simulate insider activity
        # Positive score = more buying, Negative score = more selling
        insider_score = random.uniform(-0.6, 0.6)
        
        # Insider activity is typically less frequent but more significant
        if random.random() > 0.7:  # 30% chance of significant insider activity
            insider_score *= 1.5
        
        return max(min(insider_score, 1.0), -1.0)

    async def _generate_sentiment_signals(self, symbol: str, sentiment_data: SentimentData) -> List[AnalysisSignal]:
        signals = []
        
        try:
            # Overall sentiment signals
            if sentiment_data.sentiment_score >= 0.6:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    confidence=0.7,
                    strength=sentiment_data.sentiment_score,
                    reason=f"Strong positive sentiment score of {sentiment_data.sentiment_score:.2f}",
                    metadata={"sentiment_type": "overall", "score": sentiment_data.sentiment_score}
                ))
            elif sentiment_data.sentiment_score <= -0.6:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    confidence=0.7,
                    strength=sentiment_data.sentiment_score,
                    reason=f"Strong negative sentiment score of {sentiment_data.sentiment_score:.2f}",
                    metadata={"sentiment_type": "overall", "score": sentiment_data.sentiment_score}
                ))
            elif abs(sentiment_data.sentiment_score) < 0.2:
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.HOLD,
                    confidence=0.5,
                    strength=0.0,
                    reason=f"Neutral sentiment score of {sentiment_data.sentiment_score:.2f}",
                    metadata={"sentiment_type": "overall", "score": sentiment_data.sentiment_score}
                ))
            
            # News sentiment signals
            if abs(sentiment_data.news_sentiment) >= 0.5:
                signal_type = SignalType.BUY if sentiment_data.news_sentiment > 0 else SignalType.SELL
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    confidence=0.6,
                    strength=sentiment_data.news_sentiment * 0.8,
                    reason=f"{'Positive' if sentiment_data.news_sentiment > 0 else 'Negative'} news sentiment of {sentiment_data.news_sentiment:.2f}",
                    metadata={"sentiment_type": "news", "score": sentiment_data.news_sentiment}
                ))
            
            # Analyst sentiment signals (high weight)
            if abs(sentiment_data.analyst_sentiment) >= 0.4:
                signal_type = SignalType.BUY if sentiment_data.analyst_sentiment > 0 else SignalType.SELL
                confidence = 0.8 if abs(sentiment_data.analyst_sentiment) >= 0.6 else 0.7
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    confidence=confidence,
                    strength=sentiment_data.analyst_sentiment,
                    reason=f"{'Positive' if sentiment_data.analyst_sentiment > 0 else 'Negative'} analyst sentiment of {sentiment_data.analyst_sentiment:.2f}",
                    metadata={"sentiment_type": "analyst", "score": sentiment_data.analyst_sentiment}
                ))
            
            # Social sentiment signals (more volatile, lower confidence)
            if abs(sentiment_data.social_sentiment) >= 0.7:
                signal_type = SignalType.BUY if sentiment_data.social_sentiment > 0 else SignalType.SELL
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    confidence=0.5,
                    strength=sentiment_data.social_sentiment * 0.6,
                    reason=f"{'Positive' if sentiment_data.social_sentiment > 0 else 'Negative'} social media sentiment of {sentiment_data.social_sentiment:.2f}",
                    metadata={"sentiment_type": "social", "score": sentiment_data.social_sentiment}
                ))
            
            # Insider activity signals
            if abs(sentiment_data.insider_activity_score) >= 0.5:
                signal_type = SignalType.BUY if sentiment_data.insider_activity_score > 0 else SignalType.SELL
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    confidence=0.8,
                    strength=sentiment_data.insider_activity_score,
                    reason=f"{'Positive' if sentiment_data.insider_activity_score > 0 else 'Negative'} insider activity of {sentiment_data.insider_activity_score:.2f}",
                    metadata={"sentiment_type": "insider", "score": sentiment_data.insider_activity_score}
                ))
            
            # Sentiment momentum signals (comparing different sources)
            if (sentiment_data.news_sentiment > 0.3 and 
                sentiment_data.analyst_sentiment > 0.3 and 
                sentiment_data.social_sentiment > 0.3):
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.STRONG_BUY,
                    confidence=0.8,
                    strength=0.7,
                    reason="Broad positive sentiment across all sources",
                    metadata={"sentiment_type": "consensus", "sources": ["news", "analyst", "social"]}
                ))
            elif (sentiment_data.news_sentiment < -0.3 and 
                  sentiment_data.analyst_sentiment < -0.3 and 
                  sentiment_data.social_sentiment < -0.3):
                signals.append(AnalysisSignal(
                    symbol=symbol,
                    signal_type=SignalType.STRONG_SELL,
                    confidence=0.8,
                    strength=-0.7,
                    reason="Broad negative sentiment across all sources",
                    metadata={"sentiment_type": "consensus", "sources": ["news", "analyst", "social"]}
                ))
        
        except Exception as e:
            self.logger.error(f"Error generating sentiment signals for {symbol}: {e}")
        
        return signals

    def _calculate_overall_confidence(self, signals: List[AnalysisSignal]) -> float:
        if not signals:
            return 0.0
        
        # Sentiment analysis confidence varies by source reliability
        source_weights = {
            "analyst": 1.0,
            "insider": 0.9,
            "news": 0.8,
            "consensus": 0.9,
            "social": 0.6,
            "overall": 0.7
        }
        
        weighted_confidence = 0.0
        total_weight = 0.0
        
        for signal in signals:
            source_type = signal.metadata.get("sentiment_type", "overall")
            weight = source_weights.get(source_type, 0.7)
            weighted_confidence += signal.confidence * weight
            total_weight += weight
        
        return min(weighted_confidence / total_weight if total_weight > 0 else 0.0, 1.0)

    async def health_check(self) -> Dict[str, Any]:
        base_health = await super().health_check()
        base_health.update({
            "news_sources": self.news_sources,
            "sentiment_window_hours": self.sentiment_window_hours
        })
        return base_health