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
        def __init__(self, *args, **kwargs):
            pass
        
        def agents(self):
            return MockAgentManager()
    
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
    
    AIProjectClient = MockAIProjectClient

class BaseAgent:
    """
    Base class for all Azure AI Foundry agents with built-in reuse capabilities.
    """
    
    def __init__(self, project_client, agent_name: str, instructions: str, 
                 model: str = "gpt-4o", tools: List = None, agent_type: str = "assistant"):
        """
        Initialize base agent with reuse capabilities.
        
        Args:
            project_client: Azure AI Projects client (or mock client)
            agent_name: Unique identifier for the agent
            instructions: System instructions for the agent
            model: AI model to use
            tools: List of tools available to the agent
            agent_type: Type of agent (assistant, researcher, planner, etc.)
        """
        self.project_client = project_client
        self.agent_name = agent_name
        self.instructions = instructions
        self.model = model
        self.tools = tools or []
        self.agent_type = agent_type
        self.azure_available = AZURE_AI_PROJECTS_AVAILABLE
        
        # Agent instance variables
        self.agent = None
        self.thread = None
        self.is_reused = False
        
        # Registry path for agent persistence
        self.registry_path = "helpers/config/agent_registry.json"
        
        # Initialize agent with reuse logic
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize agent with intelligent reuse logic."""
        try:
            # Try to find existing agent first
            existing_agent = self._find_existing_agent()
            
            if existing_agent:
                self.agent = self.project_client.agents.get_agent(existing_agent['agent_id'])
                self.is_reused = True
                logger.info(f"♻️ Reusing existing agent: {self.agent_name} (ID: {existing_agent['agent_id']})")
                self._update_agent_registry(existing_agent['agent_id'], reused=True)
            else:
                # Create new agent
                self.agent = self.project_client.agents.create_agent(
                    model=self.model,
                    name=self.agent_name,
                    instructions=self.instructions,
                    tools=self.tools
                )
                self.is_reused = False
                logger.info(f"🆕 Created new agent: {self.agent_name} (ID: {self.agent.id})")
                self._register_agent(self.agent.id)
                
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.agent_name}: {str(e)}")
            raise
    
    def _find_existing_agent(self) -> Optional[Dict]:
        """Find existing agent in registry that matches current requirements."""
        try:
            if not os.path.exists(self.registry_path):
                return None
                
            with open(self.registry_path, 'r') as f:
                registry = json.load(f)
                
            # Look for matching agent
            for agent_record in registry.get('agents', []):
                if (agent_record.get('name') == self.agent_name and 
                    agent_record.get('model') == self.model and
                    agent_record.get('agent_type') == self.agent_type and
                    agent_record.get('status') == 'active'):
                    
                    # Verify agent still exists in Azure
                    if self._verify_agent_exists(agent_record['agent_id']):
                        return agent_record
                    else:
                        # Mark as inactive if not found
                        self._mark_agent_inactive(agent_record['agent_id'])
                        
            return None
            
        except Exception as e:
            logger.warning(f"Error finding existing agent: {str(e)}")
            return None
    
    def _verify_agent_exists(self, agent_id: str) -> bool:
        """Verify that agent still exists in Azure."""
        try:
            self.project_client.agents.get_agent(agent_id)
            return True
        except:
            return False
    
    def _register_agent(self, agent_id: str):
        """Register new agent in the registry."""
        try:
            registry = self._load_registry()
            
            agent_record = {
                'agent_id': agent_id,
                'name': self.agent_name,
                'agent_type': self.agent_type,
                'model': self.model,
                'instructions_hash': hash(self.instructions),
                'tools_count': len(self.tools),
                'created_at': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat(),
                'usage_count': 1,
                'status': 'active'
            }
            
            registry['agents'].append(agent_record)
            self._save_registry(registry)
            
        except Exception as e:
            logger.warning(f"Failed to register agent: {str(e)}")
    
    def _update_agent_registry(self, agent_id: str, reused: bool = False):
        """Update agent usage statistics."""
        try:
            registry = self._load_registry()
            
            for agent_record in registry['agents']:
                if agent_record['agent_id'] == agent_id:
                    agent_record['last_used'] = datetime.now().isoformat()
                    if reused:
                        agent_record['usage_count'] = agent_record.get('usage_count', 0) + 1
                    break
                    
            self._save_registry(registry)
            
        except Exception as e:
            logger.warning(f"Failed to update agent registry: {str(e)}")
    
    def _mark_agent_inactive(self, agent_id: str):
        """Mark agent as inactive."""
        try:
            registry = self._load_registry()
            
            for agent_record in registry['agents']:
                if agent_record['agent_id'] == agent_id:
                    agent_record['status'] = 'inactive'
                    break
                    
            self._save_registry(registry)
            
        except Exception as e:
            logger.warning(f"Failed to mark agent inactive: {str(e)}")
    
    def _load_registry(self) -> Dict:
        """Load agent registry from file."""
        try:
            if os.path.exists(self.registry_path):
                with open(self.registry_path, 'r') as f:
                    return json.load(f)
            else:
                return {'agents': [], 'created_at': datetime.now().isoformat()}
        except:
            return {'agents': [], 'created_at': datetime.now().isoformat()}
    
    def _save_registry(self, registry: Dict):
        """Save agent registry to file."""
        try:
            os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
            with open(self.registry_path, 'w') as f:
                json.dump(registry, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save registry: {str(e)}")
    
    def create_thread(self) -> str:
        """Create a new conversation thread."""
        try:
            self.thread = self.project_client.agents.create_thread()
            logger.info(f"📝 Created new thread: {self.thread.id}")
            return self.thread.id
        except Exception as e:
            logger.error(f"Failed to create thread: {str(e)}")
            raise
    
    def send_message(self, message: str, thread_id: str = None) -> str:
        """Send message to agent and get response."""
        try:
            if thread_id:
                thread = self.project_client.agents.get_thread(thread_id)
            elif self.thread:
                thread = self.thread
            else:
                thread = self.project_client.agents.create_thread()
                self.thread = thread
            
            # Send message
            message_obj = self.project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=message
            )
            
            # Run agent
            run = self.project_client.agents.create_run(
                thread_id=thread.id,
                assistant_id=self.agent.id
            )
            
            # Wait for completion
            while run.status in ["queued", "in_progress", "cancelling"]:
                time.sleep(1)
                run = self.project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
            
            if run.status == "completed":
                # Get response
                messages = self.project_client.agents.list_messages(thread_id=thread.id)
                return messages.data[0].content[0].text.value
            else:
                logger.error(f"Run failed with status: {run.status}")
                return f"Error: Run failed with status {run.status}"
                
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise
    
    def cleanup(self):
        """Clean up agent resources if needed."""
        try:
            # Update last used time
            if self.agent:
                self._update_agent_registry(self.agent.id)
            
            logger.info(f"🧹 Cleaned up agent: {self.agent_name}")
            
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")
    
    def get_agent_info(self) -> Dict:
        """Get agent information and statistics."""
        return {
            'agent_id': self.agent.id if self.agent else None,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'model': self.model,
            'is_reused': self.is_reused,
            'tools_count': len(self.tools),
            'thread_id': self.thread.id if self.thread else None
        }
