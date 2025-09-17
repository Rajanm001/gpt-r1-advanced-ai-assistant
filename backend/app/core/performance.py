"""
GPT.R1 - Performance Optimization System
Database connection pooling, caching, and performance enhancements
Created by: Rajan Mishra
"""

import asyncio
from typing import Dict, Any, Optional, Union, List
import redis
import json
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.orm import sessionmaker
import logging
from contextlib import asynccontextmanager

from ..core.config import settings

logger = logging.getLogger("app.performance")

# Redis connection for caching
try:
    redis_client = redis.Redis(
        host=getattr(settings, 'REDIS_HOST', 'localhost'),
        port=getattr(settings, 'REDIS_PORT', 6379),
        db=getattr(settings, 'REDIS_DB', 0),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    # Test connection
    redis_client.ping()
    logger.info("Redis cache connected successfully")
except Exception as e:
    logger.warning(f"Redis cache not available: {e}")
    redis_client = None

class OptimizedDatabase:
    """Enhanced database configuration with connection pooling"""
    
    @staticmethod
    def create_optimized_engine():
        """Create database engine with optimized settings"""
        
        # Production-optimized engine settings
        engine_args = {
            "poolclass": QueuePool,
            "pool_size": 20,          # Number of connections to maintain
            "max_overflow": 30,       # Additional connections allowed
            "pool_pre_ping": True,    # Validate connections before use
            "pool_recycle": 3600,     # Recycle connections every hour
            "echo": False,            # Disable SQL echo in production
            "connect_args": {
                "connect_timeout": 10,
                "application_name": "GPT.R1-Production"
            }
        }
        
        # Use different settings for testing
        if "test" in settings.DATABASE_URL:
            engine_args.update({
                "poolclass": NullPool,  # No pooling for tests
                "pool_size": 0,
                "max_overflow": 0
            })
        
        engine = create_engine(settings.DATABASE_URL, **engine_args)
        
        logger.info(f"Database engine created with pool_size={engine_args['pool_size']}")
        return engine
    
    @staticmethod
    def create_optimized_sessionmaker(engine):
        """Create session maker with optimized settings"""
        return sessionmaker(
            autocommit=False,
            autoflush=False,  # Manual flushing for better control
            bind=engine,
            expire_on_commit=False  # Keep objects accessible after commit
        )

class CacheManager:
    """Intelligent caching system with Redis backend"""
    
    def __init__(self, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self.redis = redis_client
        self.enabled = redis_client is not None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.enabled:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            return self.redis.setex(key, ttl, serialized)
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.enabled:
            return False
        
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern"""
        if not self.enabled:
            return 0
        
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache invalidation error: {e}")
            return 0

# Global cache manager
cache_manager = CacheManager()

def cached(ttl: int = 3600, key_prefix: str = None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {prefix}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache set for {prefix}")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, use sync cache operations
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache (blocking)
            if cache_manager.enabled:
                try:
                    cached_result = cache_manager.redis.get(cache_key)
                    if cached_result:
                        return json.loads(cached_result)
                except Exception as e:
                    logger.warning(f"Cache get error: {e}")
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            if cache_manager.enabled:
                try:
                    serialized = json.dumps(result, default=str)
                    cache_manager.redis.setex(cache_key, ttl, serialized)
                except Exception as e:
                    logger.warning(f"Cache set error: {e}")
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def optimize_conversation_queries():
        """Optimize common conversation queries"""
        return """
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_conversations_user_id_created 
        ON conversations(user_id, created_at DESC);
        
        CREATE INDEX IF NOT EXISTS idx_messages_conversation_id_timestamp 
        ON messages(conversation_id, timestamp DESC);
        
        CREATE INDEX IF NOT EXISTS idx_users_username 
        ON users(username);
        
        CREATE INDEX IF NOT EXISTS idx_users_email 
        ON users(email);
        
        -- Analyze tables for better query planning
        ANALYZE conversations;
        ANALYZE messages;
        ANALYZE users;
        """
    
    @staticmethod
    @cached(ttl=300, key_prefix="conversation_count")
    def get_user_conversation_count(user_id: int, db_session) -> int:
        """Cached user conversation count"""
        return db_session.query(Conversation).filter(
            Conversation.user_id == user_id
        ).count()
    
    @staticmethod
    @cached(ttl=600, key_prefix="recent_conversations")
    def get_recent_conversations(user_id: int, limit: int, db_session) -> List[Dict]:
        """Cached recent conversations"""
        conversations = db_session.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.updated_at.desc()
        ).limit(limit).all()
        
        return [
            {
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]

class ConnectionPool:
    """Enhanced connection pool management"""
    
    def __init__(self):
        self.active_connections = 0
        self.peak_connections = 0
        self.total_connections_created = 0
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager for database connections"""
        self.active_connections += 1
        self.total_connections_created += 1
        self.peak_connections = max(self.peak_connections, self.active_connections)
        
        try:
            # In a real implementation, this would get a connection from the pool
            yield "connection"
        finally:
            self.active_connections -= 1
    
    def get_stats(self) -> Dict[str, int]:
        """Get connection pool statistics"""
        return {
            "active_connections": self.active_connections,
            "peak_connections": self.peak_connections,
            "total_connections_created": self.total_connections_created
        }

class StreamingOptimizer:
    """Optimize streaming response performance"""
    
    def __init__(self):
        self.chunk_size = 1024  # Optimal chunk size for streaming
        self.buffer_size = 8192  # Buffer size for streaming
    
    async def optimize_stream(self, stream_generator):
        """Optimize streaming response with buffering"""
        buffer = []
        buffer_size = 0
        
        async for chunk in stream_generator:
            buffer.append(chunk)
            buffer_size += len(chunk.encode('utf-8'))
            
            # Yield buffer when it reaches optimal size
            if buffer_size >= self.buffer_size:
                yield ''.join(buffer)
                buffer = []
                buffer_size = 0
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.01)
        
        # Yield remaining buffer
        if buffer:
            yield ''.join(buffer)

class MemoryOptimizer:
    """Memory usage optimization"""
    
    def __init__(self):
        self.conversation_cache_limit = 100  # Max conversations to keep in memory
        self.message_cache_limit = 1000     # Max messages to keep in memory
    
    async def cleanup_old_cache_entries(self):
        """Clean up old cache entries to free memory"""
        if cache_manager.enabled:
            try:
                # Clean up conversations older than 1 hour
                pattern = "conversation_*"
                await cache_manager.invalidate_pattern(pattern)
                
                # Clean up old user sessions
                pattern = "user_session_*"
                await cache_manager.invalidate_pattern(pattern)
                
                logger.info("Cache cleanup completed")
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    async def optimize_database_memory(self, db_session):
        """Optimize database session memory usage"""
        try:
            # Clear SQLAlchemy session cache
            db_session.expunge_all()
            
            # Force garbage collection periodically
            import gc
            gc.collect()
            
        except Exception as e:
            logger.error(f"Database memory optimization error: {e}")

class PerformanceProfiler:
    """Profile application performance"""
    
    def __init__(self):
        self.profiles = {}
    
    @asynccontextmanager
    async def profile(self, operation_name: str):
        """Profile an operation"""
        import time
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        start_time = time.time()
        start_memory = process.memory_info().rss
        start_cpu = process.cpu_percent()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = process.memory_info().rss
            end_cpu = process.cpu_percent()
            
            profile_data = {
                "operation": operation_name,
                "duration": end_time - start_time,
                "memory_delta": end_memory - start_memory,
                "cpu_usage": end_cpu - start_cpu,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.profiles[operation_name] = profile_data
            
            # Log slow operations
            if profile_data["duration"] > 1.0:
                logger.warning(f"Slow operation detected: {operation_name} took {profile_data['duration']:.3f}s")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""
        return {
            "profiles": self.profiles,
            "cache_stats": {
                "enabled": cache_manager.enabled,
                "hits": getattr(cache_manager.redis, 'info', lambda: {}).get('keyspace_hits', 0) if cache_manager.enabled else 0
            },
            "connection_pool_stats": connection_pool.get_stats() if 'connection_pool' in globals() else {},
            "timestamp": datetime.utcnow().isoformat()
        }

# Global instances
query_optimizer = QueryOptimizer()
connection_pool = ConnectionPool()
streaming_optimizer = StreamingOptimizer()
memory_optimizer = MemoryOptimizer()
performance_profiler = PerformanceProfiler()

# Background tasks for optimization
async def periodic_optimization():
    """Run periodic optimization tasks"""
    while True:
        try:
            await memory_optimizer.cleanup_old_cache_entries()
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            logger.error(f"Periodic optimization error: {e}")
            await asyncio.sleep(3600)

# Start background optimization task
if cache_manager.enabled:
    asyncio.create_task(periodic_optimization())
    logger.info("Background optimization tasks started")