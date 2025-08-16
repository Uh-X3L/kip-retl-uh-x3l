"""
Simple Agent Messaging
======================

Simplified messaging utilities for agent coordination.
Only includes essential messaging functionality.
"""

import json
import uuid
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Essential message types for agent coordination."""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    COORDINATION = "coordination"
    AGENT_REGISTRATION = "agent_registration"
    AGENT_HEARTBEAT = "agent_heartbeat"
    TASK_PROGRESS = "task_progress"
    ERROR_REPORT = "error_report"


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    MEDIUM = 2  # Alias for NORMAL
    HIGH = 3


@dataclass
class SimpleMessage:
    """Simplified message structure for agent communication."""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: Dict[str, Any]
    priority: MessagePriority = MessagePriority.MEDIUM
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization."""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "content": self.content,
            "priority": self.priority.value,
            "created_at": self.created_at
        }


class SimpleMessaging:
    """
    Simplified messaging system that can work with or without Redis.
    Falls back to in-memory storage when Redis is unavailable.
    """
    
    def __init__(self, use_redis: bool = True):
        """Initialize simple messaging."""
        self.use_redis = use_redis
        self.redis_client = None
        self.memory_messages = []
        
        if use_redis:
            try:
                import redis
                self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
                self.redis_client.ping()
                logger.info("✅ Connected to Redis for messaging")
            except Exception as e:
                logger.info(f"ℹ️ Redis unavailable, using memory: {e}")
                self.use_redis = False
    
    def send_message(self, message: SimpleMessage) -> bool:
        """Send a message."""
        try:
            if self.use_redis and self.redis_client:
                # Use Redis list for simplicity
                message_data = json.dumps(message.to_dict())
                self.redis_client.lpush(f"agent_queue:{message.to_agent}", message_data)
                logger.info(f"📨 Message sent via Redis: {message.from_agent} -> {message.to_agent}")
            else:
                # Use in-memory storage
                self.memory_messages.append({
                    "message": message,
                    "timestamp": time.time()
                })
                logger.info(f"📨 Message sent via memory: {message.from_agent} -> {message.to_agent}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return False
    
    def get_messages(self, agent_id: str, limit: int = 10) -> List[SimpleMessage]:
        """Get messages for an agent."""
        try:
            if self.use_redis and self.redis_client:
                # Get messages from Redis list
                message_data_list = self.redis_client.lrange(f"agent_queue:{agent_id}", 0, limit-1)
                # Remove retrieved messages
                if message_data_list:
                    self.redis_client.ltrim(f"agent_queue:{agent_id}", len(message_data_list), -1)
                
                messages = []
                for message_data in message_data_list:
                    try:
                        data = json.loads(message_data)
                        message = SimpleMessage(
                            message_id=data["message_id"],
                            from_agent=data["from_agent"],
                            to_agent=data["to_agent"],
                            message_type=MessageType(data["message_type"]),
                            content=data["content"],
                            priority=MessagePriority(data["priority"]),
                            created_at=data["created_at"]
                        )
                        messages.append(message)
                    except Exception as e:
                        logger.error(f"Error parsing message: {e}")
                
                return messages
            else:
                # Get messages from memory
                agent_messages = []
                remaining_messages = []
                
                for msg_data in self.memory_messages:
                    if msg_data["message"].to_agent == agent_id and len(agent_messages) < limit:
                        agent_messages.append(msg_data["message"])
                    else:
                        remaining_messages.append(msg_data)
                
                # Update memory with remaining messages
                self.memory_messages = remaining_messages
                
                return agent_messages
                
        except Exception as e:
            logger.error(f"❌ Failed to get messages for {agent_id}: {e}")
            return []
    
    def create_message(self, from_agent: str, to_agent: str, 
                      message_type: MessageType, content: Dict[str, Any],
                      priority: MessagePriority = MessagePriority.NORMAL) -> SimpleMessage:
        """Create a generic message."""
        return SimpleMessage(
            message_id=f"msg_{int(time.time())}_{from_agent[:8]}",
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            priority=priority,
            created_at=datetime.now(timezone.utc).isoformat()
        )
    
    def create_task_message(self, from_agent: str, to_agent: str, 
                           task_data: Dict[str, Any]) -> SimpleMessage:
        """Create a task assignment message."""
        return SimpleMessage(
            message_id=f"task_{int(time.time())}_{to_agent}",
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.TASK_REQUEST,
            content={"task": task_data},
            priority=MessagePriority.HIGH
        )
    
    def create_response_message(self, from_agent: str, to_agent: str,
                               response_data: Dict[str, Any]) -> SimpleMessage:
        """Create a task response message."""
        return SimpleMessage(
            message_id=f"response_{int(time.time())}_{from_agent}",
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.TASK_RESPONSE,
            content={"response": response_data},
            priority=MessagePriority.MEDIUM
        )
    
    def create_status_message(self, from_agent: str, to_agent: str,
                             status_data: Dict[str, Any]) -> SimpleMessage:
        """Create a status update message."""
        return SimpleMessage(
            message_id=f"status_{int(time.time())}_{from_agent}",
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.STATUS_UPDATE,
            content={"status": status_data},
            priority=MessagePriority.LOW
        )
    
    def create_progress_message(self, from_agent: str, supervisor_id: str,
                               task_id: str, progress_data: Dict[str, Any]) -> SimpleMessage:
        """Create a task progress update message."""
        return SimpleMessage(
            message_id=f"progress_{int(time.time())}_{from_agent}",
            from_agent=from_agent,
            to_agent=supervisor_id,
            message_type=MessageType.TASK_PROGRESS,
            content={
                "task_id": task_id,
                "progress": progress_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            priority=MessagePriority.MEDIUM
        )
    
    def create_error_message(self, from_agent: str, supervisor_id: str,
                            error_data: Dict[str, Any]) -> SimpleMessage:
        """Create an error report message."""
        return SimpleMessage(
            message_id=f"error_{int(time.time())}_{from_agent}",
            from_agent=from_agent,
            to_agent=supervisor_id,
            message_type=MessageType.ERROR_REPORT,
            content={
                "error": error_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            priority=MessagePriority.HIGH
        )
    
    def create_registration_message(self, agent_id: str, supervisor_id: str,
                                   agent_info: Dict[str, Any]) -> SimpleMessage:
        """Create an agent registration message."""
        return SimpleMessage(
            message_id=f"register_{int(time.time())}_{agent_id}",
            from_agent=agent_id,
            to_agent=supervisor_id,
            message_type=MessageType.AGENT_REGISTRATION,
            content={
                "agent_info": agent_info,
                "capabilities": agent_info.get("capabilities", []),
                "registered_at": datetime.now(timezone.utc).isoformat()
            },
            priority=MessagePriority.MEDIUM
        )
    
    def create_heartbeat_message(self, agent_id: str, supervisor_id: str,
                                health_data: Dict[str, Any]) -> SimpleMessage:
        """Create an agent heartbeat message."""
        return SimpleMessage(
            message_id=f"heartbeat_{int(time.time())}_{agent_id}",
            from_agent=agent_id,
            to_agent=supervisor_id,
            message_type=MessageType.AGENT_HEARTBEAT,
            content={
                "health": health_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            priority=MessagePriority.LOW
        )
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get simple messaging statistics."""
        if self.use_redis and self.redis_client:
            try:
                # Count messages in all agent queues
                keys = self.redis_client.keys("agent_queue:*")
                total_messages = sum(self.redis_client.llen(key) for key in keys)
                return {
                    "mode": "redis",
                    "total_queues": len(keys),
                    "total_messages": total_messages,
                    "agent_queues": {key.split(":")[1]: self.redis_client.llen(key) for key in keys}
                }
            except Exception as e:
                return {"mode": "redis", "error": str(e)}
        else:
            # Memory stats
            agent_counts = {}
            for msg_data in self.memory_messages:
                agent = msg_data["message"].to_agent
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
            
            return {
                "mode": "memory",
                "total_messages": len(self.memory_messages),
                "agent_counts": agent_counts
            }
    
    def is_connected(self) -> bool:
        """Check if messaging system is operational."""
        if self.use_redis and self.redis_client:
            try:
                self.redis_client.ping()
                return True
            except:
                return False
        return True  # Memory mode is always "connected"


def create_simple_messaging(use_redis: bool = True) -> SimpleMessaging:
    """Create a simple messaging instance."""
    return SimpleMessaging(use_redis=use_redis)


# Convenience functions
def send_task_to_agent(messaging: SimpleMessaging, coordinator_id: str, 
                      agent_id: str, task_data: Dict[str, Any]) -> bool:
    """Send a task to a specific agent."""
    message = messaging.create_task_message(coordinator_id, agent_id, task_data)
    return messaging.send_message(message)


def send_status_update(messaging: SimpleMessaging, agent_id: str,
                      coordinator_id: str, status_data: Dict[str, Any]) -> bool:
    """Send a status update to the coordinator."""
    message = messaging.create_status_message(agent_id, coordinator_id, status_data)
    return messaging.send_message(message)


def send_task_response(messaging: SimpleMessaging, agent_id: str,
                      supervisor_id: str, task_id: str, results: Dict[str, Any]) -> bool:
    """Send task completion response to supervisor."""
    response_data = {
        "task_id": task_id,
        "status": "completed",
        "results": results,
        "completed_at": datetime.now(timezone.utc).isoformat()
    }
    message = messaging.create_response_message(agent_id, supervisor_id, response_data)
    return messaging.send_message(message)


def send_task_progress(messaging: SimpleMessaging, agent_id: str,
                      supervisor_id: str, task_id: str, progress_percent: float,
                      details: str = "") -> bool:
    """Send task progress update to supervisor."""
    progress_data = {
        "progress_percent": progress_percent,
        "details": details,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    message = messaging.create_progress_message(agent_id, supervisor_id, task_id, progress_data)
    return messaging.send_message(message)


def send_error_report(messaging: SimpleMessaging, agent_id: str,
                     supervisor_id: str, task_id: str, error_message: str,
                     error_details: Dict[str, Any] = None) -> bool:
    """Send error report to supervisor."""
    error_data = {
        "task_id": task_id,
        "error_message": error_message,
        "error_details": error_details or {},
        "reported_at": datetime.now(timezone.utc).isoformat()
    }
    message = messaging.create_error_message(agent_id, supervisor_id, error_data)
    return messaging.send_message(message)


def register_with_supervisor(messaging: SimpleMessaging, agent_id: str,
                           supervisor_id: str, agent_type: str,
                           capabilities: List[str]) -> bool:
    """Register agent with supervisor."""
    agent_info = {
        "agent_id": agent_id,
        "agent_type": agent_type,
        "capabilities": capabilities,
        "status": "ready"
    }
    message = messaging.create_registration_message(agent_id, supervisor_id, agent_info)
    return messaging.send_message(message)


def send_heartbeat(messaging: SimpleMessaging, agent_id: str,
                  supervisor_id: str, current_tasks: int = 0,
                  status: str = "active") -> bool:
    """Send heartbeat to supervisor."""
    health_data = {
        "status": status,
        "current_tasks": current_tasks,
        "last_active": datetime.now(timezone.utc).isoformat()
    }
    message = messaging.create_heartbeat_message(agent_id, supervisor_id, health_data)
    return messaging.send_message(message)
