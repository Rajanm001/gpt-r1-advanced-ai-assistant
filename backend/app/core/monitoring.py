"""
GPT.R1 - Production Logging & Monitoring System
Comprehensive observability for production deployment
Created by: Rajan Mishra
"""

import logging
import logging.config
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import traceback
from contextlib import contextmanager
import asyncio
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Structured logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/gpt_r1.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10
        }
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "sqlalchemy.engine": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"]
    }
}

# Performance metrics storage
performance_metrics = {
    "requests_total": 0,
    "requests_by_endpoint": {},
    "response_times": [],
    "errors_total": 0,
    "errors_by_type": {},
    "database_queries": 0,
    "database_query_times": [],
    "openai_requests": 0,
    "openai_response_times": [],
    "memory_usage": [],
    "active_connections": 0
}

def setup_logging():
    """Initialize logging configuration"""
    import os
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    logging.config.dictConfig(LOGGING_CONFIG)
    
    logger = logging.getLogger("app.setup")
    logger.info("Logging system initialized")
    
    return logger

class StructuredLogger:
    """Enhanced structured logger for production"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"app.{name}")
    
    def log_request(self, method: str, path: str, user_id: Optional[int] = None, 
                   status_code: Optional[int] = None, response_time: Optional[float] = None,
                   **kwargs):
        """Log HTTP request with structured data"""
        log_data = {
            "event_type": "http_request",
            "method": method,
            "path": path,
            "user_id": user_id,
            "status_code": status_code,
            "response_time_ms": response_time * 1000 if response_time else None,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        level = logging.INFO
        if status_code and status_code >= 400:
            level = logging.WARNING
        if status_code and status_code >= 500:
            level = logging.ERROR
        
        self.logger.log(level, json.dumps(log_data))
    
    def log_database_operation(self, operation: str, table: str, 
                             execution_time: Optional[float] = None, 
                             error: Optional[str] = None, **kwargs):
        """Log database operations"""
        log_data = {
            "event_type": "database_operation",
            "operation": operation,
            "table": table,
            "execution_time_ms": execution_time * 1000 if execution_time else None,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        level = logging.INFO if not error else logging.ERROR
        self.logger.log(level, json.dumps(log_data))
    
    def log_openai_request(self, model: str, tokens_used: Optional[int] = None,
                          response_time: Optional[float] = None, 
                          error: Optional[str] = None, **kwargs):
        """Log OpenAI API requests"""
        log_data = {
            "event_type": "openai_request",
            "model": model,
            "tokens_used": tokens_used,
            "response_time_ms": response_time * 1000 if response_time else None,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        level = logging.INFO if not error else logging.ERROR
        self.logger.log(level, json.dumps(log_data))
    
    def log_user_action(self, user_id: int, action: str, details: Dict[str, Any] = None):
        """Log user actions for analytics"""
        log_data = {
            "event_type": "user_action",
            "user_id": user_id,
            "action": action,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None, 
                  user_id: Optional[int] = None):
        """Log errors with full context"""
        log_data = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.error(json.dumps(log_data))

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.logger = StructuredLogger("performance")
    
    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """Record request metrics"""
        performance_metrics["requests_total"] += 1
        performance_metrics["requests_by_endpoint"][endpoint] = \
            performance_metrics["requests_by_endpoint"].get(endpoint, 0) + 1
        performance_metrics["response_times"].append(response_time)
        
        if status_code >= 400:
            performance_metrics["errors_total"] += 1
            error_type = f"{status_code}_error"
            performance_metrics["errors_by_type"][error_type] = \
                performance_metrics["errors_by_type"].get(error_type, 0) + 1
    
    def record_database_query(self, execution_time: float):
        """Record database query metrics"""
        performance_metrics["database_queries"] += 1
        performance_metrics["database_query_times"].append(execution_time)
    
    def record_openai_request(self, response_time: float):
        """Record OpenAI request metrics"""
        performance_metrics["openai_requests"] += 1
        performance_metrics["openai_response_times"].append(response_time)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        response_times = performance_metrics["response_times"]
        db_query_times = performance_metrics["database_query_times"]
        openai_times = performance_metrics["openai_response_times"]
        
        return {
            "requests": {
                "total": performance_metrics["requests_total"],
                "by_endpoint": performance_metrics["requests_by_endpoint"],
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0
            },
            "errors": {
                "total": performance_metrics["errors_total"],
                "by_type": performance_metrics["errors_by_type"],
                "error_rate": performance_metrics["errors_total"] / performance_metrics["requests_total"] 
                    if performance_metrics["requests_total"] > 0 else 0
            },
            "database": {
                "queries_total": performance_metrics["database_queries"],
                "avg_query_time": sum(db_query_times) / len(db_query_times) if db_query_times else 0,
                "max_query_time": max(db_query_times) if db_query_times else 0
            },
            "openai": {
                "requests_total": performance_metrics["openai_requests"],
                "avg_response_time": sum(openai_times) / len(openai_times) if openai_times else 0,
                "max_response_time": max(openai_times) if openai_times else 0
            },
            "system": {
                "active_connections": performance_metrics["active_connections"]
            }
        }

# Decorators for automatic logging
def log_execution_time(operation_name: str):
    """Decorator to log function execution time"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = StructuredLogger("performance")
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.logger.info(f"{operation_name} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.log_error(e, {"operation": operation_name, "execution_time": execution_time})
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = StructuredLogger("performance")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.logger.info(f"{operation_name} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.log_error(e, {"operation": operation_name, "execution_time": execution_time})
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def log_database_queries():
    """Setup database query logging"""
    @event.listens_for(Engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._query_start_time = time.time()
    
    @event.listens_for(Engine, "after_cursor_execute")
    def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total = time.time() - context._query_start_time
        
        # Log slow queries
        if total > 1.0:  # Log queries taking more than 1 second
            logger = StructuredLogger("database")
            logger.logger.warning(f"Slow query detected: {total:.3f}s - {statement[:100]}...")
        
        # Record metrics
        monitor = PerformanceMonitor()
        monitor.record_database_query(total)

@contextmanager
def log_context(operation: str, **kwargs):
    """Context manager for logging operations"""
    logger = StructuredLogger("operations")
    start_time = time.time()
    
    logger.logger.info(f"Starting {operation}", extra=kwargs)
    
    try:
        yield logger
        execution_time = time.time() - start_time
        logger.logger.info(f"Completed {operation} in {execution_time:.3f}s")
    except Exception as e:
        execution_time = time.time() - start_time
        logger.log_error(e, {"operation": operation, "execution_time": execution_time, **kwargs})
        raise

class HealthChecker:
    """System health monitoring"""
    
    def __init__(self):
        self.logger = StructuredLogger("health")
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        from ..core.database import engine
        
        try:
            start_time = time.time()
            connection = engine.connect()
            connection.execute("SELECT 1")
            connection.close()
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time_ms": response_time * 1000,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.log_error(e, {"check": "database_health"})
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def check_openai_health(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity"""
        try:
            from ..services.openai_service import OpenAIService
            
            openai_service = OpenAIService()
            start_time = time.time()
            
            # Simple test request
            # In production, you might want a lighter health check
            response_time = time.time() - start_time
            
            return {
                "status": "healthy" if openai_service.is_configured else "degraded",
                "response_time_ms": response_time * 1000,
                "fallback_available": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.log_error(e, {"check": "openai_health"})
            return {
                "status": "unhealthy",
                "error": str(e),
                "fallback_available": True,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        import psutil
        
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "network": dict(psutil.net_io_counters()._asdict()),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.log_error(e, {"check": "system_metrics"})
            return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

# Global instances
performance_monitor = PerformanceMonitor()
health_checker = HealthChecker()

# Initialize logging on import
setup_logging()