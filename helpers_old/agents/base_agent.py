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


class BaseAgent:
    """
    Base Agent Class - Foundation for all Azure AI Foundry agents
    Provides reuse capabilities, lifecycle management, and common functionality.
    """
    
    def __init__(self, 
                 agent_id: Optional[str] = None,
                 agent_type: str = "general",
                 capabilities: Optional[List[str]] = None,
                 **kwargs):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent (e.g., 'research', 'worker', 'documentation')
            capabilities: List of agent capabilities
            **kwargs: Additional configuration options
        """
        self.agent_id = agent_id or f"{agent_type}_{int(time.time())}"
        self.agent_type = agent_type
        self.capabilities = capabilities or []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.status = "initialized"
        
        # Azure AI client setup
        self.credential = DefaultAzureCredential()
        self.ai_client = None
        self.agent = None
        self.thread = None
        
        logger.info(f"🤖 BaseAgent initialized: {self.agent_id} ({self.agent_type})")
    
    def initialize_azure_client(self, endpoint: str) -> bool:
        """
        Initialize the Azure AI client.
        
        Args:
            endpoint: Azure AI endpoint URL
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if AZURE_AI_PROJECTS_AVAILABLE:
                self.ai_client = AIProjectClient(
                    endpoint=endpoint,
                    credential=self.credential
                )
                logger.info(f"✅ Azure AI client initialized for {self.agent_id}")
                return True
            else:
                logger.warning(f"⚠️ Azure AI not available, using mock client for {self.agent_id}")
                self.ai_client = MockAIProjectClient()
                return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure AI client for {self.agent_id}: {e}")
            return False
    
    def create_agent(self, model: str = "gpt-4o", instructions: Optional[str] = None) -> bool:
        """
        Create an Azure AI agent.
        
        Args:
            model: Model to use for the agent
            instructions: Instructions for the agent
            
        Returns:
            bool: True if agent creation successful, False otherwise
        """
        try:
            if not self.ai_client:
                logger.error(f"❌ No AI client available for {self.agent_id}")
                return False
            
            if AZURE_AI_PROJECTS_AVAILABLE and hasattr(self.ai_client, 'agents'):
                self.agent = self.ai_client.agents.create_agent(
                    model=model,
                    name=self.agent_id,
                    instructions=instructions or f"You are a {self.agent_type} agent."
                )
                logger.info(f"✅ Azure AI agent created: {self.agent_id}")
                return True
            else:
                # Mock agent creation
                self.agent = MockAgent()
                logger.info(f"✅ Mock agent created: {self.agent_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create agent {self.agent_id}: {e}")
            return False
    
    def create_thread(self) -> bool:
        """
        Create a conversation thread.
        
        Returns:
            bool: True if thread creation successful, False otherwise
        """
        try:
            if not self.ai_client:
                logger.error(f"❌ No AI client available for {self.agent_id}")
                return False
            
            if AZURE_AI_PROJECTS_AVAILABLE and hasattr(self.ai_client, 'agents'):
                self.thread = self.ai_client.agents.create_thread()
                logger.info(f"✅ Thread created for {self.agent_id}")
                return True
            else:
                # Mock thread creation
                self.thread = MockThread()
                logger.info(f"✅ Mock thread created for {self.agent_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create thread for {self.agent_id}: {e}")
            return False
    
    def execute_task(self, task: str, requirements: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a task using the agent.
        
        Args:
            task: Task description
            requirements: Optional requirements or constraints
            
        Returns:
            Dict containing execution results
        """
        try:
            self.last_activity = datetime.now()
            self.status = "executing"
            
            # This is a base implementation - subclasses should override
            result = {
                "success": True,
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "task": task,
                "requirements": requirements,
                "executed_at": self.last_activity.isoformat(),
                "message": f"Task executed by {self.agent_type} agent"
            }
            
            self.status = "completed"
            logger.info(f"✅ Task completed by {self.agent_id}")
            return result
            
        except Exception as e:
            self.status = "error"
            logger.error(f"❌ Task execution failed for {self.agent_id}: {e}")
            return {
                "success": False,
                "agent_id": self.agent_id,
                "error": str(e),
                "executed_at": datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the agent.
        
        Returns:
            Dict containing agent status information
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": self.status,
            "capabilities": self.capabilities,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "has_ai_client": self.ai_client is not None,
            "has_agent": self.agent is not None,
            "has_thread": self.thread is not None
        }
    
    def cleanup(self):
        """Clean up agent resources."""
        try:
            # Cleanup Azure resources if needed
            self.status = "cleanup"
            logger.info(f"🧹 Cleaned up agent {self.agent_id}")
        except Exception as e:
            logger.error(f"❌ Cleanup failed for {self.agent_id}: {e}")
    
    def __str__(self):
        return f"BaseAgent(id={self.agent_id}, type={self.agent_type}, status={self.status})"
    
    def __repr__(self):
        return self.__str__()