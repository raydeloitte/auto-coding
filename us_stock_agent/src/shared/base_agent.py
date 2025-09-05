import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.data_models import (
    AnalysisRequest, AnalysisResult, AnalysisType, AgentMessage, 
    AgentConfig, AnalysisSignal
)


class BaseAgent(ABC):
    def __init__(self, config: AgentConfig, message_bus=None, logger=None):
        self.config = config
        self.agent_name = config.agent_name
        self.agent_type = config.agent_type
        self.message_bus = message_bus
        self.logger = logger or logging.getLogger(self.agent_name)
        
        self._running = False
        self._tasks = []
        self._message_queue = asyncio.Queue()
        
        self.logger.info(f"Initialized {self.agent_name} agent")

    @property
    def is_running(self) -> bool:
        return self._running

    async def start(self):
        if self._running:
            self.logger.warning(f"Agent {self.agent_name} is already running")
            return
            
        self._running = True
        self.logger.info(f"Starting agent {self.agent_name}")
        
        # Start message processing task
        message_task = asyncio.create_task(self._process_messages())
        self._tasks.append(message_task)
        
        # Start any agent-specific background tasks
        await self._start_background_tasks()

    async def stop(self):
        if not self._running:
            return
            
        self._running = False
        self.logger.info(f"Stopping agent {self.agent_name}")
        
        # Cancel all running tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()

    async def send_message(self, recipient: str, message_type: str, payload: Dict[str, Any], 
                          correlation_id: Optional[str] = None):
        if not self.message_bus:
            self.logger.warning("No message bus configured - cannot send message")
            return
            
        message = AgentMessage(
            sender=self.agent_name,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            correlation_id=correlation_id
        )
        
        await self.message_bus.send_message(message)
        self.logger.debug(f"Sent {message_type} message to {recipient}")

    async def receive_message(self, message: AgentMessage):
        await self._message_queue.put(message)

    async def _process_messages(self):
        while self._running:
            try:
                # Wait for messages with timeout to allow for graceful shutdown
                message = await asyncio.wait_for(
                    self._message_queue.get(), timeout=1.0
                )
                await self._handle_message(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")

    async def _handle_message(self, message: AgentMessage):
        try:
            if message.message_type == "analysis_request":
                request = AnalysisRequest(**message.payload)
                result = await self.process_analysis_request(request)
                
                if result:
                    await self.send_message(
                        recipient=message.sender,
                        message_type="analysis_result",
                        payload=result.__dict__,
                        correlation_id=message.correlation_id
                    )
            else:
                await self.handle_custom_message(message)
                
        except Exception as e:
            self.logger.error(f"Error handling message {message.message_type}: {e}")

    @abstractmethod
    async def process_analysis_request(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        pass

    async def handle_custom_message(self, message: AgentMessage):
        self.logger.debug(f"Received custom message: {message.message_type}")

    async def _start_background_tasks(self):
        pass

    def get_supported_analysis_types(self) -> List[AnalysisType]:
        return []

    async def health_check(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": "healthy" if self._running else "stopped",
            "uptime": datetime.now().isoformat(),
            "message_queue_size": self._message_queue.qsize()
        }

    def __str__(self):
        return f"{self.__class__.__name__}(name={self.agent_name}, type={self.agent_type})"


class DataCollectorAgent(BaseAgent):
    def get_supported_analysis_types(self) -> List[AnalysisType]:
        return []  # Data collector doesn't produce analysis directly


class TechnicalAnalysisAgent(BaseAgent):
    def get_supported_analysis_types(self) -> List[AnalysisType]:
        return [AnalysisType.TECHNICAL]


class FundamentalAnalysisAgent(BaseAgent):
    def get_supported_analysis_types(self) -> List[AnalysisType]:
        return [AnalysisType.FUNDAMENTAL]


class RiskAssessmentAgent(BaseAgent):
    def get_supported_analysis_types(self) -> List[AnalysisType]:
        return [AnalysisType.RISK]


class SentimentAnalysisAgent(BaseAgent):
    def get_supported_analysis_types(self) -> List[AnalysisType]:
        return [AnalysisType.SENTIMENT]


class VisualizationAgent(BaseAgent):
    def get_supported_analysis_types(self) -> List[AnalysisType]:
        return [AnalysisType.VISUALIZATION]


class ReportGenerationAgent(BaseAgent):
    def get_supported_analysis_types(self) -> List[AnalysisType]:
        return [AnalysisType.REPORT]