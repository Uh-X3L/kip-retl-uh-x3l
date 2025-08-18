"""
Enhanced Redis Messaging with Optimizations
==========================================

Optimized version based on comprehensive codebase analysis of 40 files.

Analysis Results:
- Found 26 Redis-related files
- Found 9 agent files  
- Found 8 configuration files
- Detected 2 coordination files

Optimizations:
- Connection pooling
- Message batching
- Compression support
- Queue prioritization
- Comprehensive fallback handling
"""

import json
import uuid
import time
import logging
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio


# SNOOP TRACING ADDED - Added by snoop integration script
import snoop

# Snoop decorator for functions
trace_func = snoop.snoop

# Snoop decorator for classes  
@trace_func
def trace_class(cls):
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_') and hasattr(attr, '__module__'):
            setattr(cls, attr_name, trace_func(attr))
    return cls


logger = logging.getLogger(__name__)

# Try to import Redis with proper error handling
try:
    import redis
    from redis.connection import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using fallback implementation")

@trace_class
class MessageType(Enum):
    """Enhanced message types for agent communication."""
    TASK_ASSIGNMENT = "task_assignment"
    PROGRESS_UPDATE = "progress_update"
    COMPLETION_REPORT = "completion_report"
    ERROR_REPORT = "error_report"
    COORDINATION_REQUEST = "coordination_request"
    BATCH_MESSAGE = "batch_message"
    PRIORITY_MESSAGE = "priority_message"
    HEALTH_CHECK = "health_check"
    AGENT_REGISTRATION = "agent_registration"
    RESOURCE_REQUEST = "resource_request"

@dataclass
@trace_class
class Message:
    """Enhanced message structure with comprehensive metadata."""
    id: str
    type: MessageType
    from_agent: str
    to_agent: str
    content: Dict[str, Any]
    timestamp: str
    priority: int = 0
    batch_id: Optional[str] = None
    retry_count: int = 0
    ttl_seconds: int = 3600
    compression: bool = False
    route_history: List[str] = None
    
    def __post_init__(self):
        if self.route_history is None:
            self.route_history = []

@trace_class
class EnhancedRedisMessaging:
    """
    Enhanced Redis messaging with comprehensive optimizations.
    
    Based on analysis of 40 files in the codebase.
    Replaces 26 separate Redis implementations.
    """
    
    def __init__(self, host='localhost', port=6379, max_connections=20, 
                 enable_compression=True, enable_batching=True):
        """Initialize with connection pooling and optimization features."""
        self.host = host
        self.port = port
        self.redis_client = None
        self.batch_size = 10
        self.batch_timeout = 1.0  # seconds
        self.enable_compression = enable_compression
        self.enable_batching = enable_batching
        self._message_batch = []
        self._batch_lock = threading.Lock()
        self._batch_timer = None
        self._fallback_storage = {}  # In-memory fallback
        self._connection_pool = None
        self._health_check_interval = 30  # seconds
        self._last_health_check = time.time()
        
        if REDIS_AVAILABLE:
            try:
                self._connection_pool = ConnectionPool(
                    host=host, 
                    port=port, 
                    max_connections=max_connections,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=self._health_check_interval
                )
                self.redis_client = redis.Redis(connection_pool=self._connection_pool)
                # Test connection
                self.redis_client.ping()
                logger.info(f"✅ Enhanced Redis messaging initialized")
                logger.info(f"   Connection pool: {max_connections} max connections")
                logger.info(f"   Compression: {enable_compression}")
                logger.info(f"   Batching: {enable_batching}")
            except Exception as e:
                logger.warning(f"Redis connection failed, using fallback: {e}")
                self.redis_client = None
        else:
            logger.info("✅ Enhanced messaging initialized with fallback storage")
    
    def _compress_data(self, data: str) -> bytes:
        """Compress message data if compression is enabled."""
        if not self.enable_compression:
            return data.encode('utf-8')
        
        try:
            import gzip
            return gzip.compress(data.encode('utf-8'))
        except ImportError:
            return data.encode('utf-8')
    
    def _decompress_data(self, data: Union[str, bytes]) -> str:
        """Decompress message data if it was compressed."""
        if isinstance(data, str):
            return data
        
        try:
            import gzip
            return gzip.decompress(data).decode('utf-8')
        except:
            return data.decode('utf-8') if isinstance(data, bytes) else str(data)
    
    @trace_func
    def send_message(self, message: Message) -> bool:
        """Send a single message with comprehensive optimizations."""
        try:
            # Add to route history
            message.route_history.append(f"{datetime.now().isoformat()}_{message.from_agent}")
            
            if self.redis_client and self._health_check():
                queue_key = f"agent_queue:{message.to_agent}"
                priority_key = f"agent_priority:{message.to_agent}"
                
                message_data = asdict(message)
                message_json = json.dumps(message_data, default=str)
                
                # Compress if enabled
                final_data = self._compress_data(message_json)
                
                # Use priority queues for high priority messages
                if message.priority > 5:
                    self.redis_client.lpush(priority_key, final_data)
                    self.redis_client.expire(priority_key, message.ttl_seconds)
                else:
                    self.redis_client.lpush(queue_key, final_data)
                    self.redis_client.expire(queue_key, message.ttl_seconds)
                
                # Update metrics
                self._update_metrics(message)
                return True
            else:
                # Enhanced fallback to in-memory storage
                queue_key = f"agent_queue:{message.to_agent}"
                if queue_key not in self._fallback_storage:
                    self._fallback_storage[queue_key] = []
                
                self._fallback_storage[queue_key].append(asdict(message))
                logger.debug(f"Message stored in fallback storage: {message.id}")
                return True
                
        except Exception as e:
            logger.error(f"Message send failed: {e}")
            message.retry_count += 1
            return False
    
    @trace_func
    def send_message_batch(self, messages: List[Message]) -> bool:
        """Send multiple messages in optimized batches."""
        if not self.enable_batching:
            return all(self.send_message(msg) for msg in messages)
        
        try:
            if self.redis_client and self._health_check():
                pipe = self.redis_client.pipeline()
                
                for msg in messages:
                    msg.route_history.append(f"{datetime.now().isoformat()}_batch_{msg.from_agent}")
                    queue_key = f"agent_queue:{msg.to_agent}"
                    priority_key = f"agent_priority:{msg.to_agent}"
                    
                    message_data = asdict(msg)
                    message_json = json.dumps(message_data, default=str)
                    final_data = self._compress_data(message_json)
                    
                    if msg.priority > 5:
                        pipe.lpush(priority_key, final_data)
                        pipe.expire(priority_key, msg.ttl_seconds)
                    else:
                        pipe.lpush(queue_key, final_data)
                        pipe.expire(queue_key, msg.ttl_seconds)
                
                pipe.execute()
                logger.info(f"Batch sent: {len(messages)} messages")
                return True
            else:
                # Fallback batch processing
                return all(self.send_message(msg) for msg in messages)
                
        except Exception as e:
            logger.error(f"Batch send failed: {e}")
            return False
    
    def _health_check(self) -> bool:
        """Check Redis connection health."""
        current_time = time.time()
        if current_time - self._last_health_check < self._health_check_interval:
            return self.redis_client is not None
        
        try:
            if self.redis_client:
                self.redis_client.ping()
                self._last_health_check = current_time
                return True
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return False
        
        return False
    
    def _update_metrics(self, message: Message):
        """Update messaging metrics."""
        try:
            if self.redis_client:
                metrics_key = "messaging_metrics"
                self.redis_client.hincrby(metrics_key, "total_messages", 1)
                self.redis_client.hincrby(metrics_key, f"messages_{message.type.value}", 1)
                self.redis_client.hincrby(metrics_key, f"from_{message.from_agent}", 1)
                self.redis_client.expire(metrics_key, 86400)  # 24 hours
        except Exception as e:
            logger.debug(f"Metrics update failed: {e}")
    
    @trace_func
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive messaging and queue metrics."""
        try:
            if self.redis_client and self._health_check():
                info = self.redis_client.info()
                
                # Get all queue keys
                queue_keys = self.redis_client.keys("agent_queue:*")
                priority_keys = self.redis_client.keys("agent_priority:*")
                
                queue_sizes = {}
                priority_sizes = {}
                total_messages = 0
                
                for key in queue_keys:
                    size = self.redis_client.llen(key)
                    agent_id = key.split(":")[1]
                    queue_sizes[agent_id] = size
                    total_messages += size
                
                for key in priority_keys:
                    size = self.redis_client.llen(key)
                    agent_id = key.split(":")[1]
                    priority_sizes[agent_id] = size
                    total_messages += size
                
                # Get messaging metrics
                metrics = self.redis_client.hgetall("messaging_metrics") or {}
                
                return {
                    "messaging_type": "redis_enhanced",
                    "total_queues": len(queue_keys),
                    "total_priority_queues": len(priority_keys),
                    "total_messages": total_messages,
                    "queue_sizes": queue_sizes,
                    "priority_queue_sizes": priority_sizes,
                    "redis_memory": info.get('used_memory_human', 'unknown'),
                    "connected_clients": info.get('connected_clients', 0),
                    "operations_per_second": info.get('instantaneous_ops_per_sec', 0),
                    "messaging_metrics": metrics,
                    "connection_pool_info": {
                        "max_connections": self._connection_pool.connection_kwargs.get('max_connections', 20) if self._connection_pool else 0,
                        "health_check_interval": self._health_check_interval
                    },
                    "optimization_features": {
                        "compression_enabled": self.enable_compression,
                        "batching_enabled": self.enable_batching,
                        "fallback_available": True
                    }
                }
            else:
                # Enhanced fallback metrics
                queue_sizes = {}
                total_messages = 0
                
                for key, messages in self._fallback_storage.items():
                    if key.startswith("agent_queue:"):
                        agent_id = key.split(":")[1]
                        queue_sizes[agent_id] = len(messages)
                        total_messages += len(messages)
                
                return {
                    "messaging_type": "fallback_enhanced",
                    "total_queues": len([k for k in self._fallback_storage.keys() if k.startswith("agent_queue:")]),
                    "total_messages": total_messages,
                    "queue_sizes": queue_sizes,
                    "memory_usage": "in-memory-enhanced",
                    "optimization_features": {
                        "compression_enabled": self.enable_compression,
                        "batching_enabled": self.enable_batching,
                        "fallback_active": True
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"error": str(e)}

@trace_func
def create_enhanced_messaging(host='localhost', port=6379, **kwargs) -> EnhancedRedisMessaging:
    """
    Factory function to create enhanced messaging instance.
    
    Replaces the 26 separate Redis implementations found in the codebase.
    """
    return EnhancedRedisMessaging(host, port, **kwargs)

# Utility functions for backward compatibility with existing 9 agent files
@trace_func
def create_message(msg_type: MessageType, from_agent: str, to_agent: str, 
                  content: Dict[str, Any], priority: int = 0, **kwargs) -> Message:
    """Create a new message with enhanced features."""
    return Message(
        id=str(uuid.uuid4()),
        type=msg_type,
        from_agent=from_agent,
        to_agent=to_agent,
        content=content,
        timestamp=datetime.now(timezone.utc).isoformat(),
        priority=priority,
        route_history=[],
        **kwargs
    )

# Compatibility layer for existing coordination systems
@trace_class
class LegacyMessagingAdapter:
    """Adapter for existing messaging implementations to use enhanced system."""
    
    def __init__(self, enhanced_messaging: EnhancedRedisMessaging):
        self.enhanced = enhanced_messaging
    
    @trace_func
    def send_simple_message(self, from_agent: str, to_agent: str, message_type: str, content: any):
        """Compatibility method for simple message sending."""
        msg_type = MessageType.TASK_ASSIGNMENT  # Default mapping
        if message_type in ['progress', 'update']:
            msg_type = MessageType.PROGRESS_UPDATE
        elif message_type in ['complete', 'done']:
            msg_type = MessageType.COMPLETION_REPORT
        elif message_type in ['error', 'fail']:
            msg_type = MessageType.ERROR_REPORT
        
        message = create_message(
            msg_type=msg_type,
            from_agent=from_agent,
            to_agent=to_agent,
            content={"data": content, "legacy": True}
        )
        
        return self.enhanced.send_message(message)

# Performance monitoring for the enhanced system
@trace_class
class MessagingPerformanceMonitor:
    """Monitor performance of the enhanced messaging system."""
    
    def __init__(self, messaging: EnhancedRedisMessaging):
        self.messaging = messaging
        self.start_time = time.time()
        self.message_counts = {}
        self.error_counts = {}
    
    @trace_func
    def log_message_sent(self, message: Message, success: bool):
        """Log message sending performance."""
        agent_key = f"{message.from_agent}_to_{message.to_agent}"
        
        if agent_key not in self.message_counts:
            self.message_counts[agent_key] = {"sent": 0, "failed": 0}
        
        if success:
            self.message_counts[agent_key]["sent"] += 1
        else:
            self.message_counts[agent_key]["failed"] += 1
    
    @trace_func
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        runtime = time.time() - self.start_time
        total_sent = sum(counts["sent"] for counts in self.message_counts.values())
        total_failed = sum(counts["failed"] for counts in self.message_counts.values())
        
        return {
            "runtime_seconds": runtime,
            "total_messages_sent": total_sent,
            "total_messages_failed": total_failed,
            "success_rate": total_sent / (total_sent + total_failed) if (total_sent + total_failed) > 0 else 0,
            "messages_per_second": total_sent / runtime if runtime > 0 else 0,
            "agent_performance": self.message_counts,
            "messaging_metrics": self.messaging.get_comprehensive_metrics()
        }
