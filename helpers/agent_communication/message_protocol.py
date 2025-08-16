"""
Agent Communication Protocol
============================

Core message structures and types for autonomous agent communication.
Uses JSON-based messaging with Azure SQL Server as the message store.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum


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


class AgentRole(Enum):
    """Agent roles in the system"""
    SUPERVISOR = "supervisor"
    WORKER = "worker"
    RESEARCHER = "researcher"
    TESTER = "tester"
    DEVOPS = "devops"
    DOCUMENTATION = "documentation"


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
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
    
    def to_json(self) -> str:
        """Convert message to JSON for storage"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return json.dumps(data, default=str)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Create message from JSON"""
        data = json.loads(json_str)
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = MessagePriority(data.get('priority', MessagePriority.MEDIUM.value))
        return cls(**data)
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
    
    def can_retry(self) -> bool:
        """Check if message can be retried"""
        return self.retry_count < self.max_retries and not self.is_expired()
    
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


@dataclass
class TaskRequest:
    """Structured task request content"""
    task_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any]
    deadline: Optional[str] = None
    required_capabilities: List[str] = None
    
    def __post_init__(self):
        if self.required_capabilities is None:
            self.required_capabilities = []


@dataclass
class TaskResponse:
    """Structured task response content"""
    task_id: str
    status: str  # completed, failed, in_progress
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: Optional[float] = None  # 0.0 to 1.0
    next_steps: Optional[List[str]] = None


@dataclass
class StatusUpdate:
    """Agent status update content"""
    agent_id: str
    status: str  # active, idle, busy, offline
    current_task: Optional[str] = None
    capabilities: Optional[List[str]] = None
    load_factor: Optional[float] = None  # 0.0 to 1.0


def create_task_request_message(
    from_agent: str,
    to_agent: str,
    task_request: TaskRequest,
    priority: MessagePriority = MessagePriority.MEDIUM
) -> AgentMessage:
    """Helper function to create a task request message"""
    return AgentMessage(
        message_id=str(uuid.uuid4()),
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.TASK_REQUEST,
        content=asdict(task_request),
        priority=priority
    )


def create_broadcast_message(
    from_agent: str,
    content: Dict[str, Any],
    message_type: MessageType = MessageType.BROADCAST
) -> AgentMessage:
    """Helper function to create a broadcast message"""
    return AgentMessage(
        message_id=str(uuid.uuid4()),
        from_agent=from_agent,
        to_agent=None,  # Broadcast to all
        message_type=message_type,
        content=content
    )


def create_heartbeat_message(agent_id: str, status_info: Dict[str, Any]) -> AgentMessage:
    """Helper function to create a heartbeat message"""
    return AgentMessage(
        message_id=str(uuid.uuid4()),
        from_agent=agent_id,
        to_agent="supervisor",  # Always send heartbeats to supervisor
        message_type=MessageType.HEARTBEAT,
        content=status_info,
        priority=MessagePriority.LOW
    )
