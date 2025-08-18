"""
Redis Agent Communication Demo
=============================

This script demonstrates the complete Redis-based communication system
between agents and the supervisor, including:

1. Supervisor coordination setup
2. Agent registration and communication
3. Task assignment and execution
4. Progress monitoring
5. Error handling
6. Bidirectional messaging

Run this script to see the full communication flow in action.
"""

import time
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone

from .simple_messaging import SimpleMessaging, MessageType
from .simple_agent_coordinator import SimpleAgentCoordinator
from .sample_communicating_agent import SampleAnalysisAgent, SampleDevelopmentAgent

# Configure logging to show communication details
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RedisCommunicationDemo:
    """
    Comprehensive demonstration of Redis-based agent communication.
    """
    
if __name__ == "__main__":
    main()
