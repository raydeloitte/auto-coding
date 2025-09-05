from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from enum import Enum
import uuid


class AnalysisType(Enum):
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental" 
    RISK = "risk"
    SENTIMENT = "sentiment"
    VISUALIZATION = "visualization"
    REPORT = "report"


class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"


class RiskLevel(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class StockData:
    symbol: str
    timestamp: datetime
    price: float
    volume: int
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None


@dataclass
class AnalysisSignal:
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    signal_type: SignalType = SignalType.HOLD
    confidence: float = 0.0  # 0.0 to 1.0
    strength: float = 0.0    # -1.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TechnicalIndicators:
    symbol: str
    timestamp: datetime
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None


@dataclass
class FundamentalData:
    symbol: str
    timestamp: datetime
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    revenue_growth: Optional[float] = None
    eps_growth: Optional[float] = None
    free_cash_flow: Optional[float] = None
    dividend_yield: Optional[float] = None


@dataclass
class RiskMetrics:
    symbol: str
    timestamp: datetime
    volatility: float
    beta: float
    value_at_risk: Optional[float] = None
    max_drawdown: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    risk_level: RiskLevel = RiskLevel.MODERATE


@dataclass
class SentimentData:
    symbol: str
    timestamp: datetime
    sentiment_score: float  # -1.0 to 1.0
    news_sentiment: float
    social_sentiment: float
    analyst_sentiment: float
    insider_activity_score: float


@dataclass
class AgentMessage:
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""
    message_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: Optional[str] = None


@dataclass
class AnalysisRequest:
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbols: List[str] = field(default_factory=list)
    analysis_types: List[AnalysisType] = field(default_factory=list)
    timeframe: str = "1d"
    depth: str = "standard"  # basic, standard, comprehensive
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AnalysisResult:
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    agent_name: str = ""
    symbol: str = ""
    analysis_type: AnalysisType = AnalysisType.TECHNICAL
    signals: List[AnalysisSignal] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0


@dataclass
class Portfolio:
    portfolio_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    holdings: Dict[str, int] = field(default_factory=dict)  # symbol -> quantity
    cash: float = 0.0
    total_value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentConfig:
    agent_name: str
    agent_type: str
    enabled: bool = True
    priority: int = 1
    timeout: float = 30.0
    retry_count: int = 3
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)