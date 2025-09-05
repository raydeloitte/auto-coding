import os
import yaml
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
import sys

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from shared.data_models import AgentConfig, AnalysisType


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "stock_analysis"
    username: str = ""
    password: str = ""
    connection_pool_size: int = 10


@dataclass
class APIConfig:
    alpha_vantage_key: str = ""
    financial_modeling_prep_key: str = ""
    news_api_key: str = ""
    rate_limit_requests_per_minute: int = 60
    timeout_seconds: int = 30


@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    db: int = 0


@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5


@dataclass
class SystemConfig:
    max_concurrent_requests: int = 10
    default_timeout: float = 30.0
    retry_attempts: int = 3
    health_check_interval: int = 60
    message_queue_size: int = 1000


@dataclass
class StockAnalysisConfig:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    api: APIConfig = field(default_factory=APIConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'StockAnalysisConfig':
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yml', '.yaml']:
                data = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StockAnalysisConfig':
        config = cls()
        
        # Database config
        if 'database' in data:
            db_data = data['database']
            config.database = DatabaseConfig(**db_data)
        
        # API config
        if 'api' in data:
            api_data = data['api']
            config.api = APIConfig(**api_data)
        
        # Redis config
        if 'redis' in data:
            redis_data = data['redis']
            config.redis = RedisConfig(**redis_data)
        
        # Logging config
        if 'logging' in data:
            logging_data = data['logging']
            config.logging = LoggingConfig(**logging_data)
        
        # System config
        if 'system' in data:
            system_data = data['system']
            config.system = SystemConfig(**system_data)
        
        # Agent configs
        if 'agents' in data:
            for agent_name, agent_data in data['agents'].items():
                config.agents[agent_name] = AgentConfig(
                    agent_name=agent_name,
                    **agent_data
                )
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'database': self.database.__dict__,
            'api': self.api.__dict__,
            'redis': self.redis.__dict__,
            'logging': self.logging.__dict__,
            'system': self.system.__dict__,
            'agents': {name: config.__dict__ for name, config in self.agents.items()}
        }
    
    def save_to_file(self, config_path: str):
        path = Path(config_path)
        data = self.to_dict()
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yml', '.yaml']:
                yaml.dump(data, f, default_flow_style=False, indent=2)
            elif path.suffix.lower() == '.json':
                json.dump(data, f, indent=2)
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        return self.agents.get(agent_name)
    
    def add_agent_config(self, config: AgentConfig):
        self.agents[config.agent_name] = config
    
    def remove_agent_config(self, agent_name: str):
        if agent_name in self.agents:
            del self.agents[agent_name]


class ConfigManager:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self._load_default_config()
    
    def _load_default_config(self) -> StockAnalysisConfig:
        return StockAnalysisConfig(
            agents=self._get_default_agent_configs()
        )
    
    def _get_default_agent_configs(self) -> Dict[str, AgentConfig]:
        agents = {
            'data_collector': AgentConfig(
                agent_name='data_collector',
                agent_type='DataCollectorAgent',
                enabled=True,
                priority=1,
                timeout=60.0,
                parameters={
                    'cache_ttl': 300,  # 5 minutes
                    'max_symbols_per_request': 10
                }
            ),
            'technical_analyst': AgentConfig(
                agent_name='technical_analyst',
                agent_type='TechnicalAnalysisAgent',
                enabled=True,
                priority=2,
                timeout=30.0,
                dependencies=['data_collector'],
                parameters={
                    'indicators': ['rsi', 'macd', 'sma', 'bollinger'],
                    'lookback_periods': [20, 50, 200]
                }
            ),
            'fundamental_analyst': AgentConfig(
                agent_name='fundamental_analyst',
                agent_type='FundamentalAnalysisAgent',
                enabled=True,
                priority=2,
                timeout=30.0,
                dependencies=['data_collector'],
                parameters={
                    'metrics': ['pe', 'pb', 'roe', 'debt_to_equity'],
                    'peer_comparison': True
                }
            ),
            'risk_assessor': AgentConfig(
                agent_name='risk_assessor',
                agent_type='RiskAssessmentAgent',
                enabled=True,
                priority=2,
                timeout=30.0,
                dependencies=['data_collector'],
                parameters={
                    'confidence_level': 0.95,
                    'lookback_days': 252
                }
            ),
            'sentiment_analyzer': AgentConfig(
                agent_name='sentiment_analyzer',
                agent_type='SentimentAnalysisAgent',
                enabled=True,
                priority=2,
                timeout=45.0,
                dependencies=['data_collector'],
                parameters={
                    'news_sources': ['reuters', 'bloomberg', 'yahoo'],
                    'sentiment_window_hours': 24
                }
            ),
            'visualizer': AgentConfig(
                agent_name='visualizer',
                agent_type='VisualizationAgent',
                enabled=True,
                priority=3,
                timeout=60.0,
                dependencies=['technical_analyst', 'fundamental_analyst'],
                parameters={
                    'chart_types': ['candlestick', 'volume', 'indicators'],
                    'output_formats': ['png', 'html']
                }
            ),
            'report_generator': AgentConfig(
                agent_name='report_generator',
                agent_type='ReportGenerationAgent',
                enabled=True,
                priority=4,
                timeout=90.0,
                dependencies=['technical_analyst', 'fundamental_analyst', 'risk_assessor', 'sentiment_analyzer'],
                parameters={
                    'report_formats': ['pdf', 'html'],
                    'include_charts': True
                }
            )
        }
        return agents
    
    def load_config(self, config_path: str):
        self._config = StockAnalysisConfig.from_file(config_path)
    
    def get_config(self) -> StockAnalysisConfig:
        return self._config
    
    def save_config(self, config_path: str):
        self._config.save_to_file(config_path)
    
    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def get_env_overrides(self) -> Dict[str, Any]:
        overrides = {}
        
        # Database overrides
        if os.getenv('DB_HOST'):
            overrides['database.host'] = os.getenv('DB_HOST')
        if os.getenv('DB_PORT'):
            overrides['database.port'] = int(os.getenv('DB_PORT'))
        if os.getenv('DB_NAME'):
            overrides['database.database'] = os.getenv('DB_NAME')
        if os.getenv('DB_USERNAME'):
            overrides['database.username'] = os.getenv('DB_USERNAME')
        if os.getenv('DB_PASSWORD'):
            overrides['database.password'] = os.getenv('DB_PASSWORD')
        
        # API key overrides
        if os.getenv('ALPHA_VANTAGE_API_KEY'):
            overrides['api.alpha_vantage_key'] = os.getenv('ALPHA_VANTAGE_API_KEY')
        if os.getenv('FMP_API_KEY'):
            overrides['api.financial_modeling_prep_key'] = os.getenv('FMP_API_KEY')
        if os.getenv('NEWS_API_KEY'):
            overrides['api.news_api_key'] = os.getenv('NEWS_API_KEY')
        
        # Redis overrides
        if os.getenv('REDIS_HOST'):
            overrides['redis.host'] = os.getenv('REDIS_HOST')
        if os.getenv('REDIS_PORT'):
            overrides['redis.port'] = int(os.getenv('REDIS_PORT'))
        if os.getenv('REDIS_PASSWORD'):
            overrides['redis.password'] = os.getenv('REDIS_PASSWORD')
        
        # Logging overrides
        if os.getenv('LOG_LEVEL'):
            overrides['logging.level'] = os.getenv('LOG_LEVEL')
        
        return overrides
    
    def apply_env_overrides(self):
        overrides = self.get_env_overrides()
        
        for key_path, value in overrides.items():
            keys = key_path.split('.')
            obj = self._config
            
            for key in keys[:-1]:
                obj = getattr(obj, key)
            
            setattr(obj, keys[-1], value)