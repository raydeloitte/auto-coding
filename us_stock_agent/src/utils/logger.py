import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.config import LoggingConfig


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        if hasattr(record, 'agent_name'):
            log_data['agent_name'] = record.agent_name
        
        if hasattr(record, 'correlation_id'):
            log_data['correlation_id'] = record.correlation_id
        
        if hasattr(record, 'symbol'):
            log_data['symbol'] = record.symbol
        
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        return json.dumps(log_data)


class AgentLoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger, agent_name):
        super().__init__(logger, {'agent_name': agent_name})
        self.agent_name = agent_name
    
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        kwargs['extra']['agent_name'] = self.agent_name
        return msg, kwargs
    
    def with_symbol(self, symbol: str):
        return SymbolLoggerAdapter(self.logger, self.agent_name, symbol)
    
    def with_request(self, request_id: str):
        return RequestLoggerAdapter(self.logger, self.agent_name, request_id)


class SymbolLoggerAdapter(AgentLoggerAdapter):
    def __init__(self, logger, agent_name, symbol):
        super().__init__(logger, agent_name)
        self.symbol = symbol
    
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        kwargs['extra']['agent_name'] = self.agent_name
        kwargs['extra']['symbol'] = self.symbol
        return msg, kwargs


class RequestLoggerAdapter(AgentLoggerAdapter):
    def __init__(self, logger, agent_name, request_id):
        super().__init__(logger, agent_name)
        self.request_id = request_id
    
    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})
        kwargs['extra']['agent_name'] = self.agent_name
        kwargs['extra']['request_id'] = self.request_id
        return msg, kwargs


class LoggerManager:
    _instance = None
    _loggers = {}
    _handlers = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._setup_done = False
    
    def setup_logging(self, config: LoggingConfig):
        if self._setup_done:
            return
        
        # Clear any existing handlers
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set root logger level
        root_logger.setLevel(getattr(logging, config.level.upper()))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(config.format)
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(getattr(logging, config.level.upper()))
        
        root_logger.addHandler(console_handler)
        self._handlers.append(console_handler)
        
        # File handler if specified
        if config.file_path:
            file_path = Path(config.file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                filename=config.file_path,
                maxBytes=config.max_file_size,
                backupCount=config.backup_count
            )
            
            # Use JSON formatter for file logs for better structured logging
            json_formatter = JSONFormatter()
            file_handler.setFormatter(json_formatter)
            file_handler.setLevel(getattr(logging, config.level.upper()))
            
            root_logger.addHandler(file_handler)
            self._handlers.append(file_handler)
        
        # Suppress noisy third-party loggers
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('yfinance').setLevel(logging.WARNING)
        
        self._setup_done = True
    
    def get_logger(self, name: str, agent_name: Optional[str] = None) -> logging.Logger:
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        
        base_logger = self._loggers[name]
        
        if agent_name:
            return AgentLoggerAdapter(base_logger, agent_name)
        
        return base_logger
    
    def get_agent_logger(self, agent_name: str) -> AgentLoggerAdapter:
        logger_name = f"agent.{agent_name}"
        base_logger = logging.getLogger(logger_name)
        return AgentLoggerAdapter(base_logger, agent_name)
    
    def shutdown(self):
        for handler in self._handlers:
            handler.close()
        self._handlers.clear()
        self._loggers.clear()
        self._setup_done = False


def setup_logging(config: LoggingConfig):
    manager = LoggerManager()
    manager.setup_logging(config)


def get_logger(name: str, agent_name: Optional[str] = None) -> logging.Logger:
    manager = LoggerManager()
    return manager.get_logger(name, agent_name)


def get_agent_logger(agent_name: str) -> AgentLoggerAdapter:
    manager = LoggerManager()
    return manager.get_agent_logger(agent_name)


def shutdown_logging():
    manager = LoggerManager()
    manager.shutdown()


class PerformanceLogger:
    def __init__(self, logger: logging.Logger, operation_name: str):
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.debug(f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.utcnow()
        duration = (self.end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation_name} in {duration:.3f}s")
        else:
            self.logger.error(f"Failed {self.operation_name} after {duration:.3f}s: {exc_val}")
    
    def get_duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


def log_performance(logger: logging.Logger, operation_name: str):
    return PerformanceLogger(logger, operation_name)