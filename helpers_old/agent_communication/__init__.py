# Simple Agent Communication System

from .message_protocol import AgentMessage, MessageType, MessagePriority
from .queue_manager import MessageQueueManager

__version__ = "1.0.0"
__all__ = [
    "AgentMessage",
    "MessageType", 
    "MessagePriority",
    "MessageQueueManager"
]
