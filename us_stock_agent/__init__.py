"""
US Stock Analysis Multi-Agent System

A professional, scalable multi-agent architecture for comprehensive stock analysis.
"""

__version__ = "1.0.0"
__author__ = "Claude Code"

from .src.orchestrator.main_agent import StockAnalysisOrchestrator
from .src.shared.data_models import (
    AnalysisRequest, AnalysisResult, AnalysisType, SignalType, 
    Portfolio, StockData, AnalysisSignal
)

__all__ = [
    "StockAnalysisOrchestrator",
    "AnalysisRequest", 
    "AnalysisResult",
    "AnalysisType",
    "SignalType",
    "Portfolio",
    "StockData", 
    "AnalysisSignal"
]