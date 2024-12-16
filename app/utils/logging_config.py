"""
Logging configuration for Research Assistant.

This module provides a centralized logging configuration with:
- Structured logging
- Log rotation
- Performance monitoring
- Error tracking
- Different log levels for different components
"""

import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
import os
from typing import Dict, Any, Optional
import time
import functools
import traceback
from pythonjsonlogger import jsonlogger

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to the log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add source location
        log_record['filename'] = record.filename
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add process and thread info
        log_record['process'] = record.process
        log_record['process_name'] = record.processName
        log_record['thread'] = record.thread
        log_record['thread_name'] = record.threadName

class PerformanceMonitor:
    """Monitor and log performance metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger('research_assistant.performance')
    
    def log_execution_time(self, func):
        """Decorator to log function execution time."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            self.logger.info(
                'Function execution time',
                extra={
                    'function_name': func.__name__,
                    'execution_time': execution_time,
                    'metric_type': 'execution_time'
                }
            )
            return result
        return wrapper
    
    def log_memory_usage(self, memory_usage: float, context: str):
        """Log memory usage."""
        self.logger.info(
            'Memory usage',
            extra={
                'memory_usage_mb': memory_usage,
                'context': context,
                'metric_type': 'memory_usage'
            }
        )
    
    def log_batch_processing(self, batch_size: int, processing_time: float, context: str):
        """Log batch processing metrics."""
        self.logger.info(
            'Batch processing',
            extra={
                'batch_size': batch_size,
                'processing_time': processing_time,
                'items_per_second': batch_size / processing_time,
                'context': context,
                'metric_type': 'batch_processing'
            }
        )

class ErrorTracker:
    """Track and log errors with context."""
    
    def __init__(self):
        self.logger = logging.getLogger('research_assistant.errors')
    
    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: bool = True
    ):
        """Log an error with context."""
        error_data = {
            'error_type': error.__class__.__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        if stack_trace:
            error_data['stack_trace'] = traceback.format_exc()
        
        self.logger.error('Error occurred', extra=error_data)
    
    def handle_exception(self, context: Optional[Dict[str, Any]] = None):
        """Decorator for exception handling and logging."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    error_context = context or {}
                    error_context.update({
                        'function': func.__name__,
                        'args': repr(args),
                        'kwargs': repr(kwargs)
                    })
                    self.log_error(e, error_context)
                    raise
            return wrapper
        return decorator

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "research_assistant.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True
) -> None:
    """
    Setup application-wide logging configuration.

    Args:
        log_level: Logging level
        log_file: Log file name
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        enable_console: Whether to enable console logging
    """
    # Create formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    # Create root logger
    root_logger = logging.getLogger('research_assistant')
    root_logger.setLevel(log_level)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Create component loggers
    components = ['processing', 'vector_store', 'api', 'performance', 'errors']
    for component in components:
        logger = logging.getLogger(f'research_assistant.{component}')
        logger.setLevel(log_level)
    
    # Log startup
    root_logger.info(
        'Logging system initialized',
        extra={
            'log_level': log_level,
            'log_file': str(LOGS_DIR / log_file),
            'max_bytes': max_bytes,
            'backup_count': backup_count,
            'console_enabled': enable_console
        }
    )

# Performance monitoring instance
performance_monitor = PerformanceMonitor()

# Error tracking instance
error_tracker = ErrorTracker()

# Initialize logging on module import
setup_logging()
