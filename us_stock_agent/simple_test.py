#!/usr/bin/env python3
"""
Simple test script to verify the multi-agent system functionality
without requiring pytest
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from orchestrator.main_agent import DependencyResolver
from shared.data_models import AgentConfig
from utils.config import ConfigManager


def test_dependency_resolver():
    """Test dependency resolution functionality."""
    print("🧪 Testing DependencyResolver...")
    
    # Test simple dependency chain
    configs = {
        'agent_a': AgentConfig(agent_name='agent_a', agent_type='TestAgent', dependencies=[]),
        'agent_b': AgentConfig(agent_name='agent_b', agent_type='TestAgent', dependencies=['agent_a']),
        'agent_c': AgentConfig(agent_name='agent_c', agent_type='TestAgent', dependencies=['agent_b'])
    }
    
    resolver = DependencyResolver(configs)
    execution_order = resolver.get_execution_order()
    
    # The algorithm groups agents into dependency levels
    # Level 0: agents with no dependencies
    # Level 1: agents that depend on level 0
    # Level 2: agents that depend on level 1, etc.
    
    print(f"    Execution order: {execution_order}")
    
    # Find which level each agent is in
    agent_levels = {}
    for level, agents in enumerate(execution_order):
        for agent in agents:
            agent_levels[agent] = level
    
    # Verify dependency ordering is respected
    assert agent_levels['agent_a'] < agent_levels['agent_b'], "agent_a should come before agent_b"
    assert agent_levels['agent_b'] < agent_levels['agent_c'], "agent_b should come before agent_c"
    
    print("  ✅ Simple dependency chain test passed")
    
    # Test parallel execution
    configs = {
        'agent_a': AgentConfig(agent_name='agent_a', agent_type='TestAgent', dependencies=[]),
        'agent_b': AgentConfig(agent_name='agent_b', agent_type='TestAgent', dependencies=[]),
        'agent_c': AgentConfig(agent_name='agent_c', agent_type='TestAgent', dependencies=['agent_a', 'agent_b'])
    }
    
    resolver = DependencyResolver(configs)
    execution_order = resolver.get_execution_order()
    
    assert len(execution_order) == 2, f"Expected 2 levels, got {len(execution_order)}"
    assert set(execution_order[0]) == {'agent_a', 'agent_b'}, "Agents A and B should be in level 0"
    assert 'agent_c' in execution_order[1], "agent_c should be in level 1"
    
    print("  ✅ Parallel execution test passed")
    
    # Test circular dependency detection
    configs = {
        'agent_a': AgentConfig(agent_name='agent_a', agent_type='TestAgent', dependencies=['agent_b']),
        'agent_b': AgentConfig(agent_name='agent_b', agent_type='TestAgent', dependencies=['agent_a'])
    }
    
    resolver = DependencyResolver(configs)
    
    try:
        execution_order = resolver.get_execution_order()
        assert False, "Should have raised ValueError for circular dependency"
    except ValueError as e:
        assert "Circular dependency detected" in str(e)
        print("  ✅ Circular dependency detection test passed")
    
    print("✅ DependencyResolver tests completed successfully")


def test_config_manager():
    """Test configuration management functionality."""
    print("🧪 Testing ConfigManager...")
    
    # Test singleton behavior
    manager1 = ConfigManager()
    manager2 = ConfigManager()
    
    assert manager1 is manager2, "ConfigManager should be a singleton"
    print("  ✅ Singleton behavior test passed")
    
    # Test default config creation
    config = manager1.get_config()
    
    assert config is not None, "Config should not be None"
    assert len(config.agents) > 0, "Should have default agents configured"
    
    required_agents = [
        'data_collector', 'technical_analyst', 'fundamental_analyst',
        'risk_assessor', 'sentiment_analyzer', 'visualizer', 'report_generator'
    ]
    
    for agent_name in required_agents:
        assert agent_name in config.agents, f"Missing required agent: {agent_name}"
    
    print("  ✅ Default configuration test passed")
    
    # Test agent configuration properties
    data_collector = config.agents['data_collector']
    assert data_collector.agent_name == 'data_collector'
    assert data_collector.agent_type == 'DataCollectorAgent'
    assert data_collector.enabled == True
    assert len(data_collector.dependencies) == 0
    
    technical_analyst = config.agents['technical_analyst']
    assert technical_analyst.agent_name == 'technical_analyst'
    assert technical_analyst.agent_type == 'TechnicalAnalysisAgent'
    assert 'data_collector' in technical_analyst.dependencies
    
    print("  ✅ Agent configuration properties test passed")
    print("✅ ConfigManager tests completed successfully")


async def test_orchestrator_basic():
    """Test basic orchestrator functionality."""
    print("🧪 Testing StockAnalysisOrchestrator...")
    
    from orchestrator.main_agent import StockAnalysisOrchestrator
    
    # Test initialization
    orchestrator = StockAnalysisOrchestrator()
    assert orchestrator.config is not None, "Orchestrator should have config"
    assert orchestrator.message_bus is not None, "Orchestrator should have message bus"
    assert orchestrator._running == False, "Orchestrator should not be running initially"
    
    print("  ✅ Orchestrator initialization test passed")
    
    # Test agent requirement calculation
    from shared.data_models import AnalysisType
    required_agents = orchestrator._get_required_agents([AnalysisType.TECHNICAL])
    
    # Should include data_collector (always required) and technical_analyst
    expected_agents = {'data_collector', 'technical_analyst'}
    assert required_agents == expected_agents, f"Expected {expected_agents}, got {required_agents}"
    
    print("  ✅ Agent requirement calculation test passed")
    print("✅ StockAnalysisOrchestrator tests completed successfully")


async def main():
    """Run all tests."""
    print("🎯 Running Simple Test Suite for Multi-Agent Stock Analysis System")
    print("=" * 70)
    
    try:
        # Run synchronous tests
        test_dependency_resolver()
        test_config_manager()
        
        # Run async tests
        await test_orchestrator_basic()
        
        print("\n🎉 All tests passed successfully!")
        print("✅ The multi-agent stock analysis system is working correctly")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)