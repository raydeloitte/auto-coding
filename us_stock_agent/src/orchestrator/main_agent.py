import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.base_agent import BaseAgent
from shared.message_bus import MessageBus
from shared.data_models import (
    AnalysisRequest, AnalysisResult, AnalysisType, AgentMessage, 
    Portfolio, SignalType, AgentConfig
)
from utils.config import ConfigManager, StockAnalysisConfig
from utils.logger import setup_logging, get_agent_logger, log_performance


class DependencyResolver:
    def __init__(self, agent_configs: Dict[str, AgentConfig]):
        self.agent_configs = agent_configs
        self._dependency_graph = self._build_dependency_graph()
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        graph = {}
        for agent_name, config in self.agent_configs.items():
            graph[agent_name] = set(config.dependencies)
        return graph
    
    def get_execution_order(self) -> List[List[str]]:
        visited = set()
        temp_visited = set()
        node_levels = {}
        
        def visit(node: str):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected involving {node}")
            if node in visited:
                return node_levels[node]
            
            temp_visited.add(node)
            max_dep_level = -1
            
            for dependency in self._dependency_graph.get(node, set()):
                dep_level = visit(dependency)
                max_dep_level = max(max_dep_level, dep_level)
            
            temp_visited.remove(node)
            visited.add(node)
            
            node_level = max_dep_level + 1
            node_levels[node] = node_level
            
            return node_level
        
        # Visit all nodes to determine their levels
        for agent_name in self.agent_configs:
            if agent_name not in visited:
                visit(agent_name)
        
        # Group nodes by level
        result = []
        max_level = max(node_levels.values()) if node_levels else 0
        
        for level in range(max_level + 1):
            level_agents = [agent for agent, agent_level in node_levels.items() if agent_level == level]
            if level_agents:
                result.append(level_agents)
        
        return result
    
    def can_run_in_parallel(self, agents: List[str]) -> bool:
        dependencies = set()
        for agent in agents:
            dependencies.update(self._dependency_graph.get(agent, set()))
        
        # Check if any agent depends on another in the same list
        return not bool(dependencies.intersection(set(agents)))


class AnalysisOrchestrator:
    def __init__(self, config: Optional[StockAnalysisConfig] = None):
        self.config = config or ConfigManager().get_config()
        setup_logging(self.config.logging)
        
        self.logger = get_agent_logger("orchestrator")
        self.message_bus = MessageBus(logger=self.logger.logger)
        
        self._agents: Dict[str, BaseAgent] = {}
        self._running = False
        self._analysis_results: Dict[str, List[AnalysisResult]] = {}
        
        self.dependency_resolver = DependencyResolver(self.config.agents)
        
        self.logger.info("Stock Analysis Orchestrator initialized")
    
    async def start(self):
        if self._running:
            self.logger.warning("Orchestrator is already running")
            return
        
        self._running = True
        self.logger.info("Starting Stock Analysis Orchestrator")
        
        # Start message bus
        await self.message_bus.start()
        
        # Initialize and register agents
        await self._initialize_agents()
        
        # Start agents in dependency order
        await self._start_agents()
        
        self.logger.info("Orchestrator started successfully")
    
    async def stop(self):
        if not self._running:
            return
        
        self._running = False
        self.logger.info("Stopping Stock Analysis Orchestrator")
        
        # Stop all agents
        await self.message_bus.shutdown_all_agents()
        
        # Stop message bus
        await self.message_bus.stop()
        
        self._agents.clear()
        self.logger.info("Orchestrator stopped")
    
    async def _initialize_agents(self):
        from subagents.data_collector import DataCollectorAgent
        from subagents.technical_analyst import TechnicalAnalysisAgent
        from subagents.fundamental_analyst import FundamentalAnalysisAgent
        from subagents.risk_assessor import RiskAssessmentAgent
        from subagents.sentiment_analyzer import SentimentAnalysisAgent
        from subagents.visualizer import VisualizationAgent
        from subagents.report_generator import ReportGenerationAgent
        
        agent_classes = {
            'DataCollectorAgent': DataCollectorAgent,
            'TechnicalAnalysisAgent': TechnicalAnalysisAgent,
            'FundamentalAnalysisAgent': FundamentalAnalysisAgent,
            'RiskAssessmentAgent': RiskAssessmentAgent,
            'SentimentAnalysisAgent': SentimentAnalysisAgent,
            'VisualizationAgent': VisualizationAgent,
            'ReportGenerationAgent': ReportGenerationAgent
        }
        
        for agent_name, agent_config in self.config.agents.items():
            if not agent_config.enabled:
                self.logger.info(f"Skipping disabled agent: {agent_name}")
                continue
            
            agent_class = agent_classes.get(agent_config.agent_type)
            if not agent_class:
                self.logger.error(f"Unknown agent type: {agent_config.agent_type}")
                continue
            
            try:
                agent_logger = get_agent_logger(agent_name)
                agent = agent_class(
                    config=agent_config,
                    message_bus=self.message_bus,
                    logger=agent_logger
                )
                
                self._agents[agent_name] = agent
                self.message_bus.register_agent(agent_name, agent)
                
                self.logger.info(f"Initialized agent: {agent_name}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize agent {agent_name}: {e}")
    
    async def _start_agents(self):
        execution_levels = self.dependency_resolver.get_execution_order()
        
        for level, agent_names in enumerate(execution_levels):
            self.logger.info(f"Starting level {level} agents: {agent_names}")
            
            # Start agents in this level concurrently
            start_tasks = []
            for agent_name in agent_names:
                if agent_name in self._agents:
                    task = asyncio.create_task(self._agents[agent_name].start())
                    start_tasks.append(task)
            
            if start_tasks:
                await asyncio.gather(*start_tasks, return_exceptions=True)
            
            # Small delay between levels to allow initialization
            await asyncio.sleep(0.5)
    
    async def analyze_stock(self, symbol: str, analysis_types: Optional[List[str]] = None, 
                           depth: str = "standard", **kwargs) -> Dict[str, AnalysisResult]:
        request_id = f"analysis_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Convert string analysis types to AnalysisType enums
        if analysis_types:
            analysis_enums = [AnalysisType(at) for at in analysis_types]
        else:
            analysis_enums = [AnalysisType.TECHNICAL, AnalysisType.FUNDAMENTAL, 
                             AnalysisType.RISK, AnalysisType.SENTIMENT]
        
        request = AnalysisRequest(
            request_id=request_id,
            symbols=[symbol],
            analysis_types=analysis_enums,
            depth=depth,
            parameters=kwargs
        )
        
        with log_performance(self.logger.logger, f"stock analysis for {symbol}"):
            return await self._execute_analysis_request(request)
    
    async def analyze_portfolio(self, portfolio: Portfolio, 
                               analysis_types: Optional[List[str]] = None,
                               depth: str = "standard", **kwargs) -> Dict[str, Dict[str, AnalysisResult]]:
        symbols = list(portfolio.holdings.keys())
        
        # Analyze each stock in the portfolio
        results = {}
        for symbol in symbols:
            symbol_results = await self.analyze_stock(
                symbol=symbol,
                analysis_types=analysis_types,
                depth=depth,
                portfolio_context=portfolio,
                **kwargs
            )
            results[symbol] = symbol_results
        
        return results
    
    async def start_monitoring(self, symbols: List[str], update_frequency: str = "5min",
                              analysis_types: Optional[List[str]] = None) -> str:
        monitoring_id = f"monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # TODO: Implement real-time monitoring
        # This would involve setting up periodic analysis requests
        # and streaming results to subscribers
        
        self.logger.info(f"Started monitoring {symbols} with frequency {update_frequency}")
        return monitoring_id
    
    async def _execute_analysis_request(self, request: AnalysisRequest) -> Dict[str, AnalysisResult]:
        self.logger.info(f"Executing analysis request {request.request_id} for {request.symbols}")
        
        # Determine which agents need to run
        required_agents = self._get_required_agents(request.analysis_types)
        
        # Execute agents in dependency order
        execution_levels = self.dependency_resolver.get_execution_order()
        results = {}
        
        for level_agents in execution_levels:
            level_required_agents = [agent for agent in level_agents if agent in required_agents]
            if not level_required_agents:
                continue
            
            # Execute agents in this level concurrently
            level_tasks = []
            for agent_name in level_required_agents:
                if agent_name in self._agents:
                    task = asyncio.create_task(
                        self._execute_agent_analysis(agent_name, request)
                    )
                    level_tasks.append((agent_name, task))
            
            # Wait for all agents in this level to complete
            for agent_name, task in level_tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=self.config.agents[agent_name].timeout)
                    if result:
                        results[agent_name] = result
                except asyncio.TimeoutError:
                    self.logger.error(f"Agent {agent_name} timed out")
                except Exception as e:
                    self.logger.error(f"Agent {agent_name} failed: {e}")
        
        return results
    
    def _get_required_agents(self, analysis_types: List[AnalysisType]) -> Set[str]:
        required_agents = set()
        
        # Always include data collector
        required_agents.add('data_collector')
        
        # Map analysis types to agents
        type_to_agent = {
            AnalysisType.TECHNICAL: 'technical_analyst',
            AnalysisType.FUNDAMENTAL: 'fundamental_analyst',
            AnalysisType.RISK: 'risk_assessor',
            AnalysisType.SENTIMENT: 'sentiment_analyzer',
            AnalysisType.VISUALIZATION: 'visualizer',
            AnalysisType.REPORT: 'report_generator'
        }
        
        for analysis_type in analysis_types:
            agent_name = type_to_agent.get(analysis_type)
            if agent_name and agent_name in self.config.agents:
                required_agents.add(agent_name)
        
        # Add dependencies
        to_process = list(required_agents)
        while to_process:
            agent_name = to_process.pop()
            dependencies = self.config.agents[agent_name].dependencies
            for dep in dependencies:
                if dep not in required_agents:
                    required_agents.add(dep)
                    to_process.append(dep)
        
        return required_agents
    
    async def _execute_agent_analysis(self, agent_name: str, request: AnalysisRequest) -> Optional[AnalysisResult]:
        if agent_name not in self._agents:
            self.logger.error(f"Agent {agent_name} not found")
            return None
        
        agent = self._agents[agent_name]
        
        try:
            result = await agent.process_analysis_request(request)
            if result:
                self.logger.debug(f"Agent {agent_name} completed analysis")
            return result
        except Exception as e:
            self.logger.error(f"Agent {agent_name} analysis failed: {e}")
            return None
    
    async def get_system_status(self) -> Dict[str, Any]:
        status = {
            "orchestrator": {
                "running": self._running,
                "agents_count": len(self._agents),
                "timestamp": datetime.now().isoformat()
            },
            "message_bus": self.message_bus.get_statistics(),
            "agents": {}
        }
        
        # Get agent health status
        for agent_name, agent in self._agents.items():
            try:
                agent_health = await agent.health_check()
                status["agents"][agent_name] = agent_health
            except Exception as e:
                status["agents"][agent_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return status
    
    async def reload_agent_config(self, agent_name: str, new_config: AgentConfig):
        if agent_name not in self._agents:
            self.logger.error(f"Cannot reload config for unknown agent: {agent_name}")
            return
        
        # Stop the agent
        await self._agents[agent_name].stop()
        
        # Update configuration
        self.config.agents[agent_name] = new_config
        
        # Restart the agent with new config
        agent = self._agents[agent_name]
        agent.config = new_config
        await agent.start()
        
        self.logger.info(f"Reloaded configuration for agent: {agent_name}")


class StockAnalysisOrchestrator(AnalysisOrchestrator):
    def __init__(self, config_path: Optional[str] = None):
        if config_path:
            config_manager = ConfigManager()
            config_manager.load_config(config_path)
            config = config_manager.get_config()
        else:
            config = None
        
        super().__init__(config)
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()