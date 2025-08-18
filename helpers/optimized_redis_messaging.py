"""
Enhanced Redis Messaging - Optimized Implementation
=================================================

Fast, efficient Redis messaging with key optimizations:
- Connection pooling
- Fallback handling  
- Performance monitoring
- Agent integration
"""

import json
import uuid
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import comprehensive execution logger
try:
    from .comprehensive_execution_logger import log_redis_message, log_method
    COMPREHENSIVE_LOGGING_AVAILABLE = True
except ImportError:
    # Fallback if logger not available
    def log_redis_message(*args, **kwargs):
        pass
    def log_method(func):
        return func
    COMPREHENSIVE_LOGGING_AVAILABLE = False

logger = logging.getLogger(__name__)

# Redis availability check
try:
    import redis
    from redis.connection import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class MessageType(Enum):
    TASK_ASSIGNMENT = "task_assignment"
    PROGRESS_UPDATE = "progress_update" 
    COMPLETION_REPORT = "completion_report"
    ERROR_REPORT = "error_report"
    COORDINATION_REQUEST = "coordination_request"

@dataclass
class Message:
    id: str
    type: MessageType
    from_agent: str
    to_agent: str
    content: Dict[str, Any]
    timestamp: str
    priority: int = 0
    retry_count: int = 0

class OptimizedRedisMessaging:
    """Optimized Redis messaging with fast performance and comprehensive logging."""
    
    def __init__(self, host='localhost', port=6379, max_connections=10):
        self.redis_client = None
        self._fallback_storage = {}
        
        if REDIS_AVAILABLE:
            try:
                pool = ConnectionPool(host=host, port=port, max_connections=max_connections, decode_responses=True)
                self.redis_client = redis.Redis(connection_pool=pool)
                self.redis_client.ping()
                logger.info("✅ Optimized Redis messaging ready")
            except:
                logger.warning("Redis unavailable, using fallback")
                self.redis_client = None
    
    @log_method
    def send_message(self, message: Message) -> bool:
        """Send message with comprehensive logging."""
        try:
            message_data = {
                "id": message.id,
                "type": message.type.value,
                "from_agent": message.from_agent,
                "to_agent": message.to_agent,
                "content": message.content,
                "timestamp": message.timestamp,
                "priority": message.priority
            }
            
            # Log the message with comprehensive logger
            if COMPREHENSIVE_LOGGING_AVAILABLE:
                log_redis_message(
                    message_type=message.type.value,
                    from_agent=message.from_agent,
                    to_agent=message.to_agent,
                    content=message.content,
                    direction="sent"
                )
            
            if self.redis_client:
                queue_key = f"agent_queue:{message.to_agent}"
                self.redis_client.lpush(queue_key, json.dumps(message_data))
                self.redis_client.expire(queue_key, 3600)
                return True
            else:
                # Fallback storage
                queue_key = f"agent_queue:{message.to_agent}"
                if queue_key not in self._fallback_storage:
                    self._fallback_storage[queue_key] = []
                self._fallback_storage[queue_key].append(message_data)
                return True
        except Exception as e:
            logger.error(f"Send failed: {e}")
            return False
    
    @log_method
    def receive_message(self, agent_name: str) -> Optional[Message]:
        """Receive message with comprehensive logging."""
        try:
            queue_key = f"agent_queue:{agent_name}"
            
            if self.redis_client:
                message_data = self.redis_client.rpop(queue_key)
                if message_data:
                    message_dict = json.loads(message_data)
                else:
                    return None
            else:
                # Fallback storage
                if queue_key not in self._fallback_storage or not self._fallback_storage[queue_key]:
                    return None
                message_dict = self._fallback_storage[queue_key].pop(0)
            
            # Create message object
            message = Message(
                id=message_dict["id"],
                type=MessageType(message_dict["type"]),
                from_agent=message_dict["from_agent"],
                to_agent=message_dict["to_agent"],
                content=message_dict["content"],
                timestamp=message_dict["timestamp"],
                priority=message_dict["priority"]
            )
            
            # Log the message with comprehensive logger
            if COMPREHENSIVE_LOGGING_AVAILABLE:
                log_redis_message(
                    message_type=message.type.value,
                    from_agent=message.from_agent,
                    to_agent=message.to_agent,
                    content=message.content,
                    direction="received"
                )
            
            return message
            
        except Exception as e:
            logger.error(f"Receive failed: {e}")
            return None
    
    @log_method
    def get_metrics(self) -> Dict[str, Any]:
        try:
            if self.redis_client:
                keys = self.redis_client.keys("agent_queue:*")
                total_messages = sum(self.redis_client.llen(key) for key in keys)
                return {
                    "type": "redis_optimized",
                    "total_queues": len(keys),
                    "total_messages": total_messages,
                    "redis_available": True
                }
            else:
                total_messages = sum(len(msgs) for msgs in self._fallback_storage.values())
                return {
                    "type": "fallback_optimized", 
                    "total_queues": len(self._fallback_storage),
                    "total_messages": total_messages,
                    "redis_available": False
                }
        except Exception as e:
            return {"error": str(e)}

@log_method
def create_optimized_messaging(host='localhost', port=6379) -> OptimizedRedisMessaging:
    """Create optimized messaging instance with logging."""
    return OptimizedRedisMessaging(host, port)

@log_method
def create_message(msg_type: MessageType, from_agent: str, to_agent: str, content: Dict[str, Any]) -> Message:
    """Create optimized message with logging."""
    return Message(
        id=str(uuid.uuid4()),
        type=msg_type,
        from_agent=from_agent,
        to_agent=to_agent,
        content=content,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
