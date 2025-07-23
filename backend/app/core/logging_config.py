"""
Production logging configuration with structured logging
"""
import json
import logging
import logging.handlers
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from pythonjsonlogger import jsonlogger

from app.core.settings import settings


class StructuredFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.now(timezone.utc).isoformat() + 'Z'
        
        # Add service information
        log_record['service'] = 'streamworks-ki-backend'
        log_record['version'] = getattr(production_settings, 'VERSION', 'unknown')
        log_record['environment'] = production_settings.ENV
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        # Add user ID if available
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        
        # Add correlation ID for tracing
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id


class ProductionLoggingSetup:
    """Setup production logging configuration"""
    
    @staticmethod
    def setup_logging():
        """Configure logging for production"""
        
        # Clear existing handlers
        logging.getLogger().handlers.clear()
        
        # Set log level
        log_level = getattr(logging, production_settings.LOG_LEVEL.upper())
        logging.getLogger().setLevel(log_level)
        
        # Setup formatters
        if production_settings.LOG_FORMAT == 'json':
            formatter = StructuredFormatter(
                fmt='%(timestamp)s %(level)s %(name)s %(message)s',
                rename_fields={
                    'levelname': 'level',
                    'name': 'logger',
                }
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        
        # File handler (if configured)
        handlers = [console_handler]
        
        if production_settings.LOG_FILE:
            log_file_path = Path(production_settings.LOG_FILE)
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                filename=production_settings.LOG_FILE,
                maxBytes=production_settings.LOG_MAX_SIZE,
                backupCount=production_settings.LOG_BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            handlers.append(file_handler)
        
        # Add handlers to root logger
        root_logger = logging.getLogger()
        for handler in handlers:
            root_logger.addHandler(handler)
        
        # Configure specific loggers
        ProductionLoggingSetup._configure_specific_loggers()
        
        # Setup structured logging
        ProductionLoggingSetup._setup_structlog()
        
        logging.info("Production logging configured successfully")
    
    @staticmethod
    def _configure_specific_loggers():
        """Configure specific loggers with appropriate levels"""
        
        logger_configs = {
            'uvicorn': logging.INFO,
            'uvicorn.access': logging.WARNING,  # Reduce noise
            'fastapi': logging.INFO,
            'sqlalchemy.engine': logging.WARNING,  # Reduce SQL noise in production
            'httpx': logging.WARNING,
            'chromadb': logging.INFO,
            'sentence_transformers': logging.WARNING,
            'transformers': logging.ERROR,  # Very noisy
            'torch': logging.ERROR,
            'app': logging.INFO,  # Our application logs
        }
        
        for logger_name, level in logger_configs.items():
            logging.getLogger(logger_name).setLevel(level)
    
    @staticmethod
    def _setup_structlog():
        """Setup structured logging with structlog"""
        
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


class LoggingMiddleware:
    """Middleware to add logging context to requests"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Add request context to logging
            request_id = scope.get("headers", {}).get("x-request-id", "unknown")
            
            # Create context manager for logging
            with structlog.contextvars.bound_contextvars(
                request_id=request_id,
                method=scope.get("method"),
                path=scope.get("path"),
                client=scope.get("client"),
            ):
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)


class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self):
        self.logger = structlog.get_logger("performance")
    
    def log_request_performance(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None,
        **kwargs
    ):
        """Log request performance metrics"""
        self.logger.info(
            "request_performance",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration * 1000, 2),
            request_size_bytes=request_size,
            response_size_bytes=response_size,
            **kwargs
        )
    
    def log_database_performance(
        self,
        operation: str,
        table: str,
        duration: float,
        rows_affected: Optional[int] = None,
        **kwargs
    ):
        """Log database operation performance"""
        self.logger.info(
            "database_performance",
            operation=operation,
            table=table,
            duration_ms=round(duration * 1000, 2),
            rows_affected=rows_affected,
            **kwargs
        )
    
    def log_llm_performance(
        self,
        model: str,
        operation: str,
        duration: float,
        tokens_input: Optional[int] = None,
        tokens_output: Optional[int] = None,
        **kwargs
    ):
        """Log LLM operation performance"""
        self.logger.info(
            "llm_performance",
            model=model,
            operation=operation,
            duration_ms=round(duration * 1000, 2),
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            **kwargs
        )


class SecurityLogger:
    """Logger for security events"""
    
    def __init__(self):
        self.logger = structlog.get_logger("security")
    
    def log_authentication_attempt(
        self,
        user_id: Optional[str],
        success: bool,
        ip_address: str,
        user_agent: str,
        **kwargs
    ):
        """Log authentication attempts"""
        self.logger.info(
            "authentication_attempt",
            user_id=user_id,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            **kwargs
        )
    
    def log_rate_limit_exceeded(
        self,
        ip_address: str,
        endpoint: str,
        limit: str,
        **kwargs
    ):
        """Log rate limit violations"""
        self.logger.warning(
            "rate_limit_exceeded",
            ip_address=ip_address,
            endpoint=endpoint,
            limit=limit,
            **kwargs
        )
    
    def log_suspicious_activity(
        self,
        activity_type: str,
        description: str,
        ip_address: str,
        severity: str = "medium",
        **kwargs
    ):
        """Log suspicious activities"""
        log_func = self.logger.warning if severity in ["medium", "high"] else self.logger.info
        log_func(
            "suspicious_activity",
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            severity=severity,
            **kwargs
        )


class BusinessLogger:
    """Logger for business metrics and events"""
    
    def __init__(self):
        self.logger = structlog.get_logger("business")
    
    def log_chunk_operation(
        self,
        operation: str,
        chunk_count: int,
        user_id: Optional[str] = None,
        duration: Optional[float] = None,
        **kwargs
    ):
        """Log chunk-related operations"""
        self.logger.info(
            "chunk_operation",
            operation=operation,
            chunk_count=chunk_count,
            user_id=user_id,
            duration_ms=round(duration * 1000, 2) if duration else None,
            **kwargs
        )
    
    def log_search_operation(
        self,
        query: str,
        results_count: int,
        user_id: Optional[str] = None,
        duration: Optional[float] = None,
        **kwargs
    ):
        """Log search operations"""
        self.logger.info(
            "search_operation",
            query_length=len(query),
            results_count=results_count,
            user_id=user_id,
            duration_ms=round(duration * 1000, 2) if duration else None,
            **kwargs
        )
    
    def log_upload_operation(
        self,
        filename: str,
        file_size: int,
        file_type: str,
        success: bool,
        user_id: Optional[str] = None,
        duration: Optional[float] = None,
        **kwargs
    ):
        """Log file upload operations"""
        self.logger.info(
            "upload_operation",
            filename=filename,
            file_size_bytes=file_size,
            file_type=file_type,
            success=success,
            user_id=user_id,
            duration_ms=round(duration * 1000, 2) if duration else None,
            **kwargs
        )


# Create logger instances
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()
business_logger = BusinessLogger()


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)