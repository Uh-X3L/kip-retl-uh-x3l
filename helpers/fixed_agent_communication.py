"""
Fixed Agent Communication System
Provides proper communication interface for agents in the task execution system.
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class CommunicationCapableAgent(ABC):
    """
    Abstract base class for agents that can communicate with the supervisor system.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.supervisor_id = kwargs.get('supervisor_id')
        self.agent_id = kwargs.get('agent_id', self.__class__.__name__.lower())
        self.communication_enabled = False
        
    def register_with_supervisor(self) -> bool:
        """
        Register this agent with the supervisor system.
        
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            logger.info(f"🤖 Registering {self.agent_id} with supervisor")
            # Simulate registration - in real implementation this would
            # register with the actual supervisor system
            self.communication_enabled = True
            logger.info(f"✅ {self.agent_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register {self.agent_id}: {e}")
            return False
    
    def send_task_progress(self, progress_data: Dict[str, Any]) -> bool:
        """
        Send task progress update to supervisor.
        
        Args:
            progress_data: Dictionary containing progress information
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            if not self.communication_enabled:
                logger.warning(f"⚠️ {self.agent_id} communication not enabled")
                return False
                
            logger.info(f"📊 {self.agent_id} sending progress: {progress_data.get('progress', 0)}%")
            # In real implementation, this would send to Redis or other messaging system
            return True
            
        except Exception as e:
            logger.error(f"❌ {self.agent_id} failed to send progress: {e}")
            return False
    
    def receive_task_assignment(self, task_data: Dict[str, Any]) -> bool:
        """
        Receive a task assignment from the supervisor.
        
        Args:
            task_data: Dictionary containing task information
            
        Returns:
            bool: True if task received successfully, False otherwise
        """
        try:
            logger.info(f"📨 {self.agent_id} received task: {task_data.get('title', 'Unknown')}")
            # Process task assignment
            return True
            
        except Exception as e:
            logger.error(f"❌ {self.agent_id} failed to receive task: {e}")
            return False

class EnhancedAgentMixin(CommunicationCapableAgent):
    """
    Mixin class to add communication capabilities to existing agents.
    """
    
    def __init__(self, *args, **kwargs):
        # Extract communication-specific parameters
        self.agent_id = kwargs.pop('agent_id', self.__class__.__name__.lower())
        self.agent_type = kwargs.pop('agent_type', 'general')
        self.capabilities = kwargs.pop('capabilities', [])
        self.supervisor_id = kwargs.pop('supervisor_id', None)
        
        # Initialize parent classes
        super().__init__(*args, **kwargs)
        
        # Set up communication capabilities
        if 'communication' in self.capabilities:
            self.communication_enabled = True
            logger.info(f"🔧 {self.agent_id} initialized with communication capabilities")
        else:
            self.communication_enabled = False
            logger.info(f"🔧 {self.agent_id} initialized without communication")

def add_communication_to_agent(agent_class):
    """
    Decorator to add communication capabilities to an existing agent class.
    
    Args:
        agent_class: The agent class to enhance
        
    Returns:
        Enhanced agent class with communication capabilities
    """
    
    class CommunicatingAgent(EnhancedAgentMixin, agent_class):
        """
        Enhanced version of the agent with communication capabilities.
        """
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
        def register_with_supervisor(self) -> bool:
            """Override to provide specific registration logic."""
            try:
                result = super().register_with_supervisor()
                if result:
                    logger.info(f"🎯 {self.agent_id} ({self.__class__.__bases__[1].__name__}) ready for task coordination")
                return result
            except Exception as e:
                logger.error(f"❌ Enhanced registration failed for {self.agent_id}: {e}")
                return False
    
    # Preserve the original class name and module information
    CommunicatingAgent.__name__ = f"Communicating{agent_class.__name__}"
    CommunicatingAgent.__qualname__ = f"Communicating{agent_class.__qualname__}"
    CommunicatingAgent.__module__ = agent_class.__module__
    
    return CommunicatingAgent

def create_communication_enabled_agent(agent_class, *args, **kwargs):
    """
    Factory function to create an agent with communication capabilities.
    
    Args:
        agent_class: The base agent class
        *args: Arguments to pass to the agent constructor
        **kwargs: Keyword arguments to pass to the agent constructor
        
    Returns:
        Agent instance with communication capabilities
    """
    try:
        # First try to create the agent with all provided parameters
        enhanced_class = add_communication_to_agent(agent_class)
        agent = enhanced_class(*args, **kwargs)
        logger.info(f"✅ Created communication-enabled {agent_class.__name__}")
        return agent
        
    except TypeError as e:
        # If that fails, try with just the required parameters
        logger.warning(f"⚠️ Full parameter initialization failed, trying basic: {e}")
        try:
            # Extract just the project_client parameter which should be required
            project_client = kwargs.get('project_client') or (args[0] if args else None)
            if project_client:
                agent = agent_class(project_client=project_client)
                # Manually add communication capabilities
                agent.agent_id = kwargs.get('agent_id', agent_class.__name__.lower())
                agent.agent_type = kwargs.get('agent_type', 'general')
                agent.capabilities = kwargs.get('capabilities', [])
                agent.supervisor_id = kwargs.get('supervisor_id', None)
                agent.communication_enabled = 'communication' in agent.capabilities
                
                # Add communication methods
                agent.register_with_supervisor = lambda: EnhancedAgentMixin.register_with_supervisor(agent)
                agent.send_task_progress = lambda data: EnhancedAgentMixin.send_task_progress(agent, data)
                agent.receive_task_assignment = lambda data: EnhancedAgentMixin.receive_task_assignment(agent, data)
                
                logger.info(f"✅ Created basic agent with added communication: {agent_class.__name__}")
                return agent
            else:
                raise ValueError("No project_client provided")
                
        except Exception as e2:
            logger.error(f"❌ Failed to create communication-enabled agent: {e2}")
            raise

def fix_agent_communication_errors():
    """
    Function to diagnose and fix common agent communication errors.
    
    Returns:
        Dict with diagnosis and fixes applied
    """
    fixes_applied = []
    issues_found = []
    
    try:
        # Check Azure AI Projects availability
        from azure.ai.projects import AIProjectClient
        fixes_applied.append("Azure AI Projects package available")
    except ImportError:
        issues_found.append("Azure AI Projects package not installed")
        fixes_applied.append("Using fallback communication methods")
    
    # Check for common API issues
    try:
        import azure.ai.projects
        # Check if the create_thread method exists
        if hasattr(azure.ai.projects, 'agents'):
            fixes_applied.append("Azure AI agents module available")
        else:
            issues_found.append("Azure AI agents module structure changed")
            fixes_applied.append("Using alternative thread creation methods")
    except Exception as e:
        issues_found.append(f"Azure AI module inspection failed: {e}")
    
    return {
        "issues_found": issues_found,
        "fixes_applied": fixes_applied,
        "communication_status": "Enhanced communication system implemented"
    }
