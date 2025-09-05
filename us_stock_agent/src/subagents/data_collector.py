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

from shared.base_agent import BaseAgent
from shared.data_models import (
    AnalysisRequest, AnalysisResult, StockData, FundamentalData,
    TechnicalIndicators, AnalysisSignal, SignalType, AnalysisType
)


class DataCollectorAgent(BaseAgent):
    def __init__(self, config, message_bus=None, logger=None):
        super().__init__(config, message_bus, logger)
        
        self.cache_ttl = config.parameters.get('cache_ttl', 300)  # 5 minutes default
        self.max_symbols_per_request = config.parameters.get('max_symbols_per_request', 10)
        
        # Data cache with TTL
        self._price_cache: Dict[str, Dict[str, Any]] = {}
        self._fundamental_cache: Dict[str, Dict[str, Any]] = {}
        
        # API session (placeholder for future implementation)
        self._session: Optional[Any] = None

    async def _start_background_tasks(self):
        # Start cache cleanup task
        cleanup_task = asyncio.create_task(self._cache_cleanup_task())
        self._tasks.append(cleanup_task)

    async def stop(self):
        await super().stop()

    async def process_analysis_request(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        self.logger.info(f"Processing data collection request for {len(request.symbols)} symbols")
        
        collected_data = {}
        
        for symbol in request.symbols:
            try:
                # Collect stock price data
                price_data = await self._get_price_data(symbol, request.timeframe)
                if price_data:
                    collected_data[f"{symbol}_price"] = price_data
                
                # Collect fundamental data if needed
                if request.depth in ["standard", "comprehensive"]:
                    fundamental_data = await self._get_fundamental_data(symbol)
                    if fundamental_data:
                        collected_data[f"{symbol}_fundamental"] = fundamental_data
                
                # Collect historical data for technical analysis
                if AnalysisType.TECHNICAL in request.analysis_types:
                    historical_data = await self._get_historical_data(symbol, request.timeframe)
                    if historical_data:
                        collected_data[f"{symbol}_historical"] = historical_data
                
            except Exception as e:
                self.logger.error(f"Error collecting data for {symbol}: {e}")
                continue
        
        if collected_data:
            return AnalysisResult(
                request_id=request.request_id,
                agent_name=self.agent_name,
                symbol=",".join(request.symbols),
                analysis_type=AnalysisType.TECHNICAL,  # Data collection supports all types
                data=collected_data,
                confidence=1.0,
                timestamp=datetime.now()
            )
        
        return None

    async def _get_price_data(self, symbol: str, timeframe: str) -> Optional[StockData]:
        cache_key = f"{symbol}_{timeframe}"
        
        # Check cache first
        if cache_key in self._price_cache:
            cached_data = self._price_cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                self.logger.debug(f"Using cached price data for {symbol}")
                return cached_data['data']
        
        # Fetch from API (stub implementation)
        try:
            # TODO: Replace with actual API call to yfinance, Alpha Vantage, etc.
            price_data = await self._simulate_price_data_fetch(symbol)
            
            # Cache the result
            self._price_cache[cache_key] = {
                'data': price_data,
                'timestamp': datetime.now()
            }
            
            return price_data
            
        except Exception as e:
            self.logger.error(f"Failed to fetch price data for {symbol}: {e}")
            return None

    async def _get_fundamental_data(self, symbol: str) -> Optional[FundamentalData]:
        cache_key = f"{symbol}_fundamental"
        
        # Check cache first
        if cache_key in self._fundamental_cache:
            cached_data = self._fundamental_cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(hours=1):  # Longer TTL for fundamentals
                self.logger.debug(f"Using cached fundamental data for {symbol}")
                return cached_data['data']
        
        try:
            # TODO: Replace with actual API call
            fundamental_data = await self._simulate_fundamental_data_fetch(symbol)
            
            # Cache the result
            self._fundamental_cache[cache_key] = {
                'data': fundamental_data,
                'timestamp': datetime.now()
            }
            
            return fundamental_data
            
        except Exception as e:
            self.logger.error(f"Failed to fetch fundamental data for {symbol}: {e}")
            return None

    async def _get_historical_data(self, symbol: str, timeframe: str) -> Optional[List[StockData]]:
        try:
            # TODO: Replace with actual historical data fetch
            historical_data = await self._simulate_historical_data_fetch(symbol, timeframe)
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Failed to fetch historical data for {symbol}: {e}")
            return None

    async def _simulate_price_data_fetch(self, symbol: str) -> StockData:
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        # Return mock data for testing
        import random
        base_price = 100 + random.uniform(-50, 100)
        
        return StockData(
            symbol=symbol,
            timestamp=datetime.now(),
            price=base_price,
            volume=random.randint(1000000, 10000000),
            open_price=base_price * random.uniform(0.98, 1.02),
            high_price=base_price * random.uniform(1.00, 1.05),
            low_price=base_price * random.uniform(0.95, 1.00),
            close_price=base_price,
            market_cap=base_price * 1000000000,
            pe_ratio=random.uniform(10, 30),
            dividend_yield=random.uniform(0, 5)
        )

    async def _simulate_fundamental_data_fetch(self, symbol: str) -> FundamentalData:
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        import random
        return FundamentalData(
            symbol=symbol,
            timestamp=datetime.now(),
            pe_ratio=random.uniform(10, 30),
            pb_ratio=random.uniform(1, 5),
            roe=random.uniform(5, 25),
            debt_to_equity=random.uniform(0.2, 2.0),
            revenue_growth=random.uniform(-10, 20),
            eps_growth=random.uniform(-15, 25),
            free_cash_flow=random.uniform(-1000000, 5000000),
            dividend_yield=random.uniform(0, 5)
        )

    async def _simulate_historical_data_fetch(self, symbol: str, timeframe: str) -> List[StockData]:
        # Simulate API delay
        await asyncio.sleep(0.2)
        
        import random
        data = []
        base_date = datetime.now() - timedelta(days=365)
        base_price = 100 + random.uniform(-50, 100)
        
        for i in range(252):  # One year of trading days
            date = base_date + timedelta(days=i)
            price = base_price + random.uniform(-5, 5)
            
            data.append(StockData(
                symbol=symbol,
                timestamp=date,
                price=price,
                volume=random.randint(1000000, 10000000),
                open_price=price * random.uniform(0.99, 1.01),
                high_price=price * random.uniform(1.00, 1.03),
                low_price=price * random.uniform(0.97, 1.00),
                close_price=price,
                market_cap=price * 1000000000
            ))
            
            base_price = price  # Price walk
        
        return data

    async def _cache_cleanup_task(self):
        while self._running:
            try:
                current_time = datetime.now()
                
                # Clean price cache
                expired_keys = []
                for key, cached_data in self._price_cache.items():
                    if current_time - cached_data['timestamp'] > timedelta(seconds=self.cache_ttl * 2):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self._price_cache[key]
                
                # Clean fundamental cache
                expired_keys = []
                for key, cached_data in self._fundamental_cache.items():
                    if current_time - cached_data['timestamp'] > timedelta(hours=2):
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self._fundamental_cache[key]
                
                if expired_keys:
                    self.logger.debug(f"Cleaned {len(expired_keys)} expired cache entries")
                
                # Sleep for 5 minutes before next cleanup
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in cache cleanup: {e}")
                await asyncio.sleep(60)

    async def health_check(self) -> Dict[str, Any]:
        base_health = await super().health_check()
        base_health.update({
            "price_cache_size": len(self._price_cache),
            "fundamental_cache_size": len(self._fundamental_cache),
            "session_active": self._session is not None
        })
        return base_health