# Agent Communication System
# Autonomous Agent Communication and Coordination System

from .message_protocol import AgentMessage, MessageType, AgentRole
from .queue_manager import MessageQueueManager
from .agent_registry import AgentRegistry
from .supervisor_coordinator import SupervisorCoordinator

__version__ = "1.0.0"
__all__ = [
    "AgentMessage",
    "MessageType", 
    "AgentRole",
    "MessageQueueManager",
    "AgentRegistry",
    "SupervisorCoordinator"
]
