# Simple Agent Communication System

from .message_protocol import AgentMessage, MessageType, MessagePriority
from .queue_manager import MessageQueueManager


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


__version__ = "1.0.0"
__all__ = [
    "AgentMessage",
    "MessageType", 
    "MessagePriority",
    "MessageQueueManager"
]
