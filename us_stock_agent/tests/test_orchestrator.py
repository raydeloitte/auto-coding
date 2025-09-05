import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator.main_agent import StockAnalysisOrchestrator, DependencyResolver
from utils.config import StockAnalysisConfig, ConfigManager
from shared.data_models import AnalysisRequest, AnalysisType, AgentConfig


class TestDependencyResolver:
    def test_simple_dependency_chain(self):
        """Test dependency resolution with a simple chain."""
        configs = {
            'agent_a': AgentConfig(agent_name='agent_a', agent_type='TestAgent', dependencies=[]),
            'agent_b': AgentConfig(agent_name='agent_b', agent_type='TestAgent', dependencies=['agent_a']),
            'agent_c': AgentConfig(agent_name='agent_c', agent_type='TestAgent', dependencies=['agent_b'])
        }
        
        resolver = DependencyResolver(configs)
        execution_order = resolver.get_execution_order()
        
        assert len(execution_order) == 3
        assert 'agent_a' in execution_order[0]
        assert 'agent_b' in execution_order[1]
        assert 'agent_c' in execution_order[2]

    def test_parallel_execution(self):
        """Test agents that can run in parallel."""
        configs = {
            'agent_a': AgentConfig(agent_name='agent_a', agent_type='TestAgent', dependencies=[]),
            'agent_b': AgentConfig(agent_name='agent_b', agent_type='TestAgent', dependencies=[]),
            'agent_c': AgentConfig(agent_name='agent_c', agent_type='TestAgent', dependencies=['agent_a', 'agent_b'])
        }
        
        resolver = DependencyResolver(configs)
        execution_order = resolver.get_execution_order()
        
        assert len(execution_order) == 2
        assert set(execution_order[0]) == {'agent_a', 'agent_b'}
        assert 'agent_c' in execution_order[1]

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        configs = {
            'agent_a': AgentConfig(agent_name='agent_a', agent_type='TestAgent', dependencies=['agent_b']),
            'agent_b': AgentConfig(agent_name='agent_b', agent_type='TestAgent', dependencies=['agent_a'])
        }
        
        resolver = DependencyResolver(configs)
        
        with pytest.raises(ValueError, match="Circular dependency detected"):
            resolver.get_execution_order()

    def test_can_run_in_parallel(self):
        """Test parallel execution capability detection."""
        configs = {
            'agent_a': AgentConfig(agent_name='agent_a', agent_type='TestAgent', dependencies=[]),
            'agent_b': AgentConfig(agent_name='agent_b', agent_type='TestAgent', dependencies=[]),
            'agent_c': AgentConfig(agent_name='agent_c', agent_type='TestAgent', dependencies=['agent_a'])
        }
        
        resolver = DependencyResolver(configs)
        
        # These can run in parallel (no dependencies on each other)
        assert resolver.can_run_in_parallel(['agent_a', 'agent_b']) == True
        
        # These cannot run in parallel (agent_c depends on agent_a)
        assert resolver.can_run_in_parallel(['agent_a', 'agent_c']) == False


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    config = StockAnalysisConfig()
    
    # Add test agent configurations
    config.agents = {
        'data_collector': AgentConfig(
            agent_name='data_collector',
            agent_type='DataCollectorAgent',
            enabled=True,
            timeout=30.0,
            dependencies=[]
        ),
        'technical_analyst': AgentConfig(
            agent_name='technical_analyst',
            agent_type='TechnicalAnalysisAgent',
            enabled=True,
            timeout=30.0,
            dependencies=['data_collector']
        )
    }
    
    return config


class TestStockAnalysisOrchestrator:
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, mock_config):
        """Test orchestrator initialization."""
        orchestrator = StockAnalysisOrchestrator()
        assert orchestrator.config is not None
        assert orchestrator.message_bus is not None
        assert orchestrator._running == False

    @pytest.mark.asyncio
    async def test_get_required_agents(self, mock_config):
        """Test agent requirement calculation."""
        orchestrator = StockAnalysisOrchestrator()
        orchestrator.config = mock_config
        
        # Test technical analysis requirement
        required_agents = orchestrator._get_required_agents([AnalysisType.TECHNICAL])
        
        # Should include data_collector (always required) and technical_analyst
        expected_agents = {'data_collector', 'technical_analyst'}
        assert required_agents == expected_agents

    @pytest.mark.asyncio
    async def test_analyze_stock_request_creation(self, mock_config):
        """Test stock analysis request creation."""
        orchestrator = StockAnalysisOrchestrator()
        orchestrator.config = mock_config
        
        # Mock the execute method to avoid actual execution
        orchestrator._execute_analysis_request = AsyncMock(return_value={})
        
        result = await orchestrator.analyze_stock(
            symbol="AAPL",
            analysis_types=["technical"],
            depth="standard"
        )
        
        # Check that the request was created and passed correctly
        orchestrator._execute_analysis_request.assert_called_once()
        call_args = orchestrator._execute_analysis_request.call_args[0][0]
        
        assert call_args.symbols == ["AAPL"]
        assert AnalysisType.TECHNICAL in call_args.analysis_types
        assert call_args.depth == "standard"


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestConfigManager:
    def test_config_manager_singleton(self):
        """Test that ConfigManager is a singleton."""
        manager1 = ConfigManager()
        manager2 = ConfigManager()
        
        assert manager1 is manager2

    def test_default_config_creation(self):
        """Test creation of default configuration."""
        manager = ConfigManager()
        config = manager.get_config()
        
        assert config is not None
        assert isinstance(config, StockAnalysisConfig)
        assert len(config.agents) > 0
        
        # Check that all required agents are present
        required_agents = [
            'data_collector', 'technical_analyst', 'fundamental_analyst',
            'risk_assessor', 'sentiment_analyzer', 'visualizer', 'report_generator'
        ]
        
        for agent_name in required_agents:
            assert agent_name in config.agents

    def test_agent_config_properties(self):
        """Test agent configuration properties."""
        manager = ConfigManager()
        config = manager.get_config()
        
        # Test data collector configuration
        data_collector = config.agents['data_collector']
        assert data_collector.agent_name == 'data_collector'
        assert data_collector.agent_type == 'DataCollectorAgent'
        assert data_collector.enabled == True
        assert len(data_collector.dependencies) == 0
        
        # Test technical analyst configuration
        technical_analyst = config.agents['technical_analyst']
        assert technical_analyst.agent_name == 'technical_analyst'
        assert technical_analyst.agent_type == 'TechnicalAnalysisAgent'
        assert 'data_collector' in technical_analyst.dependencies


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])