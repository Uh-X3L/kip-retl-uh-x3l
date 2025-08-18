#!/usr/bin/env python3
"""
Simple Agent Communication Demo
===============================

Basic Redis-based agent messaging demo.
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.agent_communication.message_protocol import AgentMessage, MessageType, MessagePriority
from helpers.agent_communication.queue_manager import MessageQueueManager

if __name__ == "__main__":
    main()
