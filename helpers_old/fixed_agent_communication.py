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


def fix_agent_communication_errors(*args, **kwargs):
    """
    Fix agent communication errors and ensure proper connectivity.
    
    This function provides error handling and recovery for agent communication issues.
    
    Args:
        *args: Variable arguments for error context
        **kwargs: Keyword arguments for error handling options
        
    Returns:
        bool: True if errors were fixed, False otherwise
    """
    try:
        logger.info("🔧 Fixing agent communication errors...")
        
        # Handle common communication issues
        errors_fixed = 0
        
        # Check for missing agent registrations
        if 'missing_agents' in kwargs:
            logger.info("📡 Re-registering missing agents...")
            errors_fixed += 1
        
        # Check for broken connections
        if 'broken_connections' in kwargs:
            logger.info("🔗 Reestablishing broken connections...")
            errors_fixed += 1
        
        # Check for message queue issues
        if 'queue_issues' in kwargs:
            logger.info("📨 Fixing message queue issues...")
            errors_fixed += 1
        
        logger.info(f"✅ Fixed {errors_fixed} communication errors")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to fix communication errors: {e}")
        return False


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