"""
Agent Communication Protocol
============================

Core message structures and types for autonomous agent communication.
Uses JSON-based messaging with Redis Streams for high-performance messaging.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum



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


@trace_class
class MessageType(Enum):
    """Types of messages agents can send"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    COORDINATION = "coordination"
    ERROR_REPORT = "error_report"
    COMPLETION = "completion"
    HEARTBEAT = "heartbeat"
    BROADCAST = "broadcast"


@trace_class
class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
@trace_class
class AgentMessage:
    """Core message structure for agent communication"""
    message_id: str
    from_agent: str
    to_agent: Optional[str]  # None for broadcast messages
    message_type: MessageType
    content: Dict[str, Any]
    parent_message_id: Optional[str] = None
    priority: MessagePriority = MessagePriority.MEDIUM
    created_at: Optional[str] = None
    processed_at: Optional[str] = None
    status: str = "pending"  # pending, processing, processed, failed, expired
    retry_count: int = 0
    max_retries: int = 3
    expires_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()
        
        # Generate message ID if not provided
        if not self.message_id:
            self.message_id = str(uuid.uuid4())
    
    @trace_func
    def to_json(self) -> str:
        """Convert message to JSON for storage"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return json.dumps(data, default=str)
    
    @classmethod
    @trace_func
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Create message from JSON"""
        data = json.loads(json_str)
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = MessagePriority(data.get('priority', MessagePriority.MEDIUM.value))
        return cls(**data)
    
    @trace_func
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
    
    @trace_func
    def can_retry(self) -> bool:
        """Check if message can be retried"""
        return self.retry_count < self.max_retries and not self.is_expired()
    
    @trace_func
    def create_response(self, responding_agent: str, response_content: Dict[str, Any]) -> 'AgentMessage':
        """Create a response message to this message"""
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            from_agent=responding_agent,
            to_agent=self.from_agent,
            message_type=MessageType.TASK_RESPONSE,
            content=response_content,
            parent_message_id=self.message_id,
            priority=self.priority
        )
