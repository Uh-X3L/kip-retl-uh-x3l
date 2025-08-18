"""
Base Agent Class - Foundation for all Azure AI Foundry agents
Provides reuse capabilities, lifecycle management, and common functionality.
"""

import logging
from typing import Dict, Any, Optional, List
from azure.identity import DefaultAzureCredential
import os
import json
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Azure AI Projects import with fallback
try:
    from azure.ai.projects import AIProjectClient
    AZURE_AI_PROJECTS_AVAILABLE = True
except ImportError:
    # Fallback for when Azure AI Projects is not installed
    AZURE_AI_PROJECTS_AVAILABLE = False
    logger.warning("Azure AI Projects not available - using mock client")
    
    class MockAIProjectClient:
        pass
        
    class MockAgentManager:
        def create_agent(self, *args, **kwargs):
            return MockAgent()
        
        def get_agent(self, agent_id):
            return MockAgent()
        
        def create_thread(self):
            return MockThread()
        
        def get_thread(self, thread_id):
            return MockThread()
    
    class MockAgent:
        def __init__(self):
            self.id = "mock_agent_id"
    
    class MockThread:
        def __init__(self):
            self.id = "mock_thread_id"