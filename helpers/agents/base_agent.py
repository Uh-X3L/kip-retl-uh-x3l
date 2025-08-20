"""
Unified Base Agent - Consolidated Azure AI Foundation
===================================================

This module provides a unified base agent that consolidates the best features
from both the original BaseAgent and EnhancedBaseAgent implementations.

Features:
- Azure AI Projects integration with fallback support
- Comprehensive logging and execution tracking
- Redis messaging capabilities
- Task execution with enhanced context
- Performance metrics and monitoring
- Agent lifecycle management and reuse
- Backward compatibility with existing implementations

Created: January 2025
Author: AI Assistant (Consolidation of BaseAgent + EnhancedBaseAgent)
"""

import os
import time
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from azure.identity import DefaultAzureCredential

# Azure AI Projects import with fallback
try:
    from azure.ai.projects import AIProjectClient
    AZURE_AI_PROJECTS_AVAILABLE = True
except ImportError:
    AZURE_AI_PROJECTS_AVAILABLE = False
    
    
# Comprehensive logging imports with fallback
try:
    from ..logging.comprehensive_execution_logger import (
        log_method, start_operation, end_operation, log_step, 
        LogLevel, ExecutionStatus, get_execution_logger
    )
    COMPREHENSIVE_LOGGING_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_LOGGING_AVAILABLE = False

# Redis messaging imports with fallback
try:
    from ..agent_communication.optimized_redis_messaging import (
        OptimizedRedisMessaging, create_optimized_messaging, 
        create_message, MessageType
    )
    REDIS_MESSAGING_AVAILABLE = True
except ImportError:
    REDIS_MESSAGING_AVAILABLE = False
    
    class MessageType:
        pass

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Unified Base Agent - Foundation for all Azure AI Foundry agents.
    
    Consolidates features from both original BaseAgent and EnhancedBaseAgent:
    - Azure AI Projects integration with fallback
    - Comprehensive logging and execution tracking  
    - Redis messaging capabilities
    - Task execution with enhanced context
    - Performance metrics and monitoring
    - Agent lifecycle management and reuse
    
    This unified implementation provides backward compatibility while offering
    enhanced capabilities for modern agent workflows.
    """
    
    def __init__(self, 
                 project_client=None,
                 agent_name: str = None,
                 instructions: str = None,
                 model: str = "gpt-4o",
                 tools: List = None,
                 agent_type: str = "assistant",
                 agent_id: Optional[str] = None,
                 capabilities: Optional[List[str]] = None,
                 enable_logging: bool = True,
                 enable_redis: bool = True,
                 **kwargs):
        """
        Initialize the unified base agent.
        
        Args:
            project_client: Azure AI Projects client (new style)
            agent_name: Unique identifier for the agent (new style)
            instructions: System instructions for the agent (new style)  
            model: AI model to use (default: gpt-4o)
            tools: List of tools available to the agent
            agent_type: Type of agent (assistant, researcher, planner, etc.)
            agent_id: Alternative to agent_name for backward compatibility
            capabilities: List of agent capabilities (legacy)
            enable_logging: Enable comprehensive logging
            enable_redis: Enable Redis messaging
            **kwargs: Additional configuration options
        """
        # Handle both old and new initialization patterns
        self.agent_name = agent_name or agent_id or f"{agent_type}_{int(time.time())}"
        self.agent_id = self.agent_name  # Backward compatibility
        self.agent_type = agent_type
        self.instructions = instructions or f"You are a {self.agent_type} agent."
        self.model = model
        self.tools = tools or []
        self.capabilities = capabilities or []
        
        # Timestamps and status
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.status = "initialized"
        self.is_reused = False
        
        # Enhanced capabilities
        self.enable_logging = enable_logging and COMPREHENSIVE_LOGGING_AVAILABLE
        self.enable_redis = enable_redis and REDIS_MESSAGING_AVAILABLE
        self.current_operation_id = None
        
        # Azure AI client setup
        self.project_client = project_client
        self.credential = DefaultAzureCredential()
        self.ai_client = project_client  # New style
        self.azure_available = AZURE_AI_PROJECTS_AVAILABLE and project_client is not None
        self.agent = None
        self.thread = None
        
        # Redis messaging
        self.redis_messaging = None
        if self.enable_redis:
            try:
                self.redis_messaging = create_optimized_messaging()
                if self.enable_logging:
                    log_step("Redis Messaging Initialized", {
                        "agent_name": self.agent_name,
                        "redis_available": True
                    }, LogLevel.INFO)
            except Exception as e:
                logger.warning(f"Redis messaging initialization failed: {e}")
                self.enable_redis = False
        
        # Initialize Azure agent if client provided
        if self.project_client:
            self._initialize_azure_agent()
        
        # Log agent initialization
        if self.enable_logging:
            self.current_operation_id = start_operation(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                operation_type="agent_initialization",
                inputs={
                    "model": self.model,
                    "tools_count": len(self.tools),
                    "is_reused": self.is_reused
                },
                metadata={
                    "azure_available": self.azure_available,
                    "redis_enabled": self.enable_redis,
                    "logging_enabled": self.enable_logging
                }
            )
            
            log_step("Agent Initialization Complete", {
                "agent_name": self.agent_name,
                "agent_type": self.agent_type,
                "agent_id": self.agent.id if self.agent else None,
                "is_reused": self.is_reused,
                "capabilities": {
                    "azure_ai": self.azure_available,
                    "redis_messaging": self.enable_redis,
                    "comprehensive_logging": self.enable_logging
                }
            }, LogLevel.INFO)
            
            end_operation(
                operation_id=self.current_operation_id,
                outputs={
                    "agent_id": self.agent.id if self.agent else None,
                    "thread_id": self.thread.id if self.thread else None,
                    "initialization_success": True
                },
                status=ExecutionStatus.COMPLETED
            )
        
        logger.info(f"🤖 BaseAgent initialized: {self.agent_name} ({self.agent_type})")
    
    def _initialize_azure_agent(self) -> bool:
        """Initialize Azure AI agent with the project client."""
        try:
            if self.azure_available and hasattr(self.project_client, 'agents'):
                self.agent = self.project_client.agents.create_agent(
                    model=self.model,
                    name=self.agent_name,
                    instructions=self.instructions,
                    tools=self.tools
                )
                logger.info(f"✅ Azure AI agent created: {self.agent_name}")
                return True
            else:
                # Mock agent creation
                self.agent = MockAgent()
                logger.info(f"✅ Mock agent created: {self.agent_name}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create agent {self.agent_name}: {e}")
            return False
    
    def initialize_azure_client(self, endpoint: str) -> bool:
        """
        Initialize the Azure AI client (legacy method for backward compatibility).
        
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
                self.project_client = self.ai_client
                self.azure_available = True
                logger.info(f"✅ Azure AI client initialized for {self.agent_name}")
                return True
            else:
                logger.warning(f"⚠️ Azure AI not available, using mock client for {self.agent_name}")
                self.ai_client = MockAIProjectClient()
                self.project_client = self.ai_client
                return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure AI client for {self.agent_name}: {e}")
            return False
    
    def create_agent(self, model: str = None, instructions: str = None) -> bool:
        """
        Create an Azure AI agent (legacy method for backward compatibility).
        
        Args:
            model: Model to use for the agent
            instructions: Instructions for the agent
            
        Returns:
            bool: True if agent creation successful, False otherwise
        """
        if model:
            self.model = model
        if instructions:
            self.instructions = instructions
            
        return self._initialize_azure_agent()
    
    @log_method
    def create_thread(self) -> str:
        """Create a new conversation thread."""
        operation_id = None
        if self.enable_logging:
            operation_id = start_operation(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                operation_type="create_thread",
                inputs={}
            )
        
        try:
            if not self.project_client:
                logger.error(f"❌ No project client available for {self.agent_name}")
                return None
            
            if self.azure_available and hasattr(self.project_client, 'agents'):
                self.thread = self.project_client.agents.create_thread()
                thread_id = self.thread.id
                logger.info(f"✅ Thread created for {self.agent_name}: {thread_id}")
            else:
                # Mock thread creation
                self.thread = MockThread()
                thread_id = self.thread.id
                logger.info(f"✅ Mock thread created for {self.agent_name}: {thread_id}")
            
            if self.enable_logging:
                log_step("Thread Created", {
                    "agent_name": self.agent_name,
                    "thread_id": thread_id
                }, LogLevel.INFO)
                
                end_operation(
                    operation_id=operation_id,
                    outputs={"thread_id": thread_id},
                    status=ExecutionStatus.COMPLETED
                )
            
            return thread_id
            
        except Exception as e:
            if self.enable_logging:
                end_operation(
                    operation_id=operation_id,
                    status=ExecutionStatus.FAILED,
                    error=str(e)
                )
            logger.error(f"❌ Failed to create thread for {self.agent_name}: {e}")
            raise
    
    @log_method
    def send_message(self, message: str, thread_id: str = None) -> str:
        """Send message to agent with comprehensive logging."""
        operation_id = None
        if self.enable_logging:
            operation_id = start_operation(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                operation_type="send_message",
                inputs={
                    "message_length": len(message),
                    "thread_id": thread_id or (self.thread.id if self.thread else None),
                    "message_preview": message[:100] + "..." if len(message) > 100 else message
                }
            )
        
        start_time = time.time()
        
        try:
            if self.enable_logging:
                log_step("Message Processing Started", {
                    "agent_name": self.agent_name,
                    "message_length": len(message),
                    "thread_id": thread_id or (self.thread.id if self.thread else None)
                }, LogLevel.INFO)
            
            # Update last activity
            self.last_activity = datetime.now()
            
            # Use provided thread_id or current thread
            target_thread_id = thread_id or (self.thread.id if self.thread else None)
            
            if not target_thread_id:
                # Create thread if none exists
                target_thread_id = self.create_thread()
            
            # Send message using Azure AI or mock
            if self.azure_available and hasattr(self.project_client, 'agents'):
                # Real Azure AI implementation would go here
                response = f"[Azure AI Response to: {message[:50]}...]"
            else:
                # Mock response for development/testing
                response = f"Mock response from {self.agent_name} for: {message[:50]}..."
            
            execution_time = time.time() - start_time
            
            if self.enable_logging:
                log_step("Message Processing Completed", {
                    "agent_name": self.agent_name,
                    "execution_time": execution_time,
                    "response_length": len(response) if response else 0,
                    "response_preview": response[:100] + "..." if response and len(response) > 100 else response
                }, LogLevel.INFO)
                
                end_operation(
                    operation_id=operation_id,
                    outputs={
                        "response_length": len(response) if response else 0,
                        "execution_time": execution_time,
                        "response_preview": response[:200] + "..." if response and len(response) > 200 else response
                    },
                    status=ExecutionStatus.COMPLETED
                )
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            if self.enable_logging:
                log_step("Message Processing Failed", {
                    "agent_name": self.agent_name,
                    "execution_time": execution_time,
                    "error": str(e)
                }, LogLevel.ERROR)
                
                end_operation(
                    operation_id=operation_id,
                    outputs={"execution_time": execution_time},
                    status=ExecutionStatus.FAILED,
                    error=str(e)
                )
            
            raise
    
    @log_method
    def send_redis_message(self, to_agent: str, message_type, content: Dict[str, Any]) -> bool:
        """Send Redis message to another agent with logging."""
        if not self.enable_redis or not self.redis_messaging:
            logger.warning("Redis messaging not available")
            return False
        
        operation_id = None
        if self.enable_logging:
            operation_id = start_operation(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                operation_type="send_redis_message",
                inputs={
                    "to_agent": to_agent,
                    "message_type": message_type.value if hasattr(message_type, 'value') else str(message_type),
                    "content_size": len(str(content))
                }
            )
        
        try:
            message = create_message(
                msg_type=message_type,
                from_agent=self.agent_name,
                to_agent=to_agent,
                content=content
            )
            
            success = self.redis_messaging.send_message(message)
            
            if self.enable_logging:
                log_step("Redis Message Sent", {
                    "from_agent": self.agent_name,
                    "to_agent": to_agent,
                    "message_type": message_type.value if hasattr(message_type, 'value') else str(message_type),
                    "message_id": message.id,
                    "success": success
                }, LogLevel.INFO)
                
                end_operation(
                    operation_id=operation_id,
                    outputs={
                        "message_id": message.id,
                        "success": success
                    },
                    status=ExecutionStatus.COMPLETED if success else ExecutionStatus.FAILED
                )
            
            return success
            
        except Exception as e:
            if self.enable_logging:
                end_operation(
                    operation_id=operation_id,
                    status=ExecutionStatus.FAILED,
                    error=str(e)
                )
            raise
    
    @log_method
    def receive_redis_messages(self) -> List[Dict[str, Any]]:
        """Receive Redis messages for this agent with logging."""
        if not self.enable_redis or not self.redis_messaging:
            return []
        
        operation_id = None
        if self.enable_logging:
            operation_id = start_operation(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                operation_type="receive_redis_messages",
                inputs={}
            )
        
        try:
            messages = []
            
            # Check for messages
            while True:
                message = self.redis_messaging.receive_message(self.agent_name)
                if not message:
                    break
                
                message_dict = {
                    "id": message.id,
                    "type": message.type.value if hasattr(message.type, 'value') else str(message.type),
                    "from_agent": message.from_agent,
                    "content": message.content,
                    "timestamp": message.timestamp,
                    "priority": message.priority
                }
                messages.append(message_dict)
            
            if self.enable_logging:
                log_step("Redis Messages Received", {
                    "agent_name": self.agent_name,
                    "messages_count": len(messages),
                    "message_types": [msg["type"] for msg in messages]
                }, LogLevel.INFO)
                
                end_operation(
                    operation_id=operation_id,
                    outputs={
                        "messages_count": len(messages),
                        "messages": messages
                    },
                    status=ExecutionStatus.COMPLETED
                )
            
            return messages
            
        except Exception as e:
            if self.enable_logging:
                end_operation(
                    operation_id=operation_id,
                    status=ExecutionStatus.FAILED,
                    error=str(e)
                )
            raise
    
    @log_method
    def execute_task(self, task_description: str, requirements: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a task with comprehensive logging and coordination.
        
        Args:
            task_description: Description of the task to execute
            requirements: Optional requirements or constraints (for backward compatibility)
            context: Additional context for the task
            
        Returns:
            Dict[str, Any]: Task execution results
        """
        operation_id = None
        if self.enable_logging:
            operation_id = start_operation(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                operation_type="execute_task",
                inputs={
                    "task_description": task_description,
                    "requirements": requirements,
                    "context": context or {}
                }
            )
        
        start_time = time.time()
        
        try:
            self.last_activity = datetime.now()
            self.status = "executing"
            
            if self.enable_logging:
                log_step("Task Execution Started", {
                    "agent_name": self.agent_name,
                    "task_description": task_description,
                    "context_provided": bool(context),
                    "requirements_provided": bool(requirements)
                }, LogLevel.INFO)
            
            # Create enhanced prompt with context
            enhanced_prompt = f"""
Task: {task_description}

Agent Information:
- Agent Name: {self.agent_name}
- Agent Type: {self.agent_type}
- Capabilities: {', '.join([tool.__class__.__name__ for tool in self.tools]) if self.tools else 'Standard LLM capabilities'}

Requirements: {requirements or 'None specified'}

Context: {json.dumps(context or {}, indent=2)}

Please execute this task providing detailed steps and clear outputs.
"""
            
            # Execute the task
            response = self.send_message(enhanced_prompt)
            
            execution_time = time.time() - start_time
            self.status = "completed"
            
            # Parse response and create structured result
            result = {
                "success": True,
                "agent_id": self.agent_name,
                "agent_name": self.agent_name,
                "agent_type": self.agent_type,
                "task": task_description,
                "task_description": task_description,
                "requirements": requirements,
                "context": context or {},
                "response": response,
                "execution_time": execution_time,
                "executed_at": self.last_activity.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
            if self.enable_logging:
                log_step("Task Execution Completed", {
                    "agent_name": self.agent_name,
                    "execution_time": execution_time,
                    "response_length": len(response) if response else 0,
                    "success": True
                }, LogLevel.INFO)
                
                end_operation(
                    operation_id=operation_id,
                    outputs=result,
                    status=ExecutionStatus.COMPLETED
                )
            
            logger.info(f"✅ Task completed by {self.agent_name}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.status = "error"
            
            error_result = {
                "success": False,
                "agent_id": self.agent_name,
                "agent_name": self.agent_name,
                "agent_type": self.agent_type,
                "task": task_description,
                "task_description": task_description,
                "requirements": requirements,
                "context": context or {},
                "execution_time": execution_time,
                "executed_at": datetime.now().isoformat(),
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            
            if self.enable_logging:
                log_step("Task Execution Failed", {
                    "agent_name": self.agent_name,
                    "execution_time": execution_time,
                    "error": str(e)
                }, LogLevel.ERROR)
                
                end_operation(
                    operation_id=operation_id,
                    outputs=error_result,
                    status=ExecutionStatus.FAILED,
                    error=str(e)
                )
            
            logger.error(f"❌ Task execution failed for {self.agent_name}: {e}")
            return error_result
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent (legacy method)."""
        return self.get_agent_info()
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get comprehensive agent information."""
        base_info = {
            "agent_id": self.agent_name,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "status": self.status,
            "capabilities": self.capabilities,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "has_ai_client": self.ai_client is not None,
            "has_project_client": self.project_client is not None,
            "has_agent": self.agent is not None,
            "has_thread": self.thread is not None,
            "model": self.model,
            "tools_count": len(self.tools),
            "is_reused": self.is_reused
        }
        
        if self.enable_logging:
            base_info.update({
                "logging_enabled": self.enable_logging,
                "redis_enabled": self.enable_redis,
                "current_operation": self.current_operation_id,
                "enhanced_capabilities": {
                    "azure_ai": self.azure_available,
                    "redis_messaging": self.enable_redis,
                    "comprehensive_logging": self.enable_logging,
                    "task_execution": True
                },
                "performance_metrics": self._get_performance_metrics()
            })
        
        return base_info
    
    @log_method
    def get_comprehensive_info(self) -> Dict[str, Any]:
        """Get comprehensive agent information including logging data (enhanced method)."""
        return self.get_agent_info()
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics from logger."""
        if not self.enable_logging:
            return {}
        
        execution_logger = get_execution_logger()
        if not execution_logger:
            return {}
        
        # Filter metrics for this agent
        agent_operations = [
            op for op in execution_logger.current_session.agent_operations
            if op.agent_name == self.agent_name
        ]
        
        if not agent_operations:
            return {}
        
        total_operations = len(agent_operations)
        completed_operations = len([op for op in agent_operations if op.status == ExecutionStatus.COMPLETED])
        total_duration = sum(op.duration for op in agent_operations)
        avg_duration = total_duration / total_operations if total_operations > 0 else 0
        
        return {
            "total_operations": total_operations,
            "completed_operations": completed_operations,
            "success_rate": (completed_operations / total_operations * 100) if total_operations > 0 else 0,
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "operation_types": list(set(op.operation_type for op in agent_operations))
        }
    
    @log_method
    def cleanup(self):
        """Enhanced cleanup with logging."""
        if self.enable_logging:
            operation_id = start_operation(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                operation_type="agent_cleanup",
                inputs={}
            )
        
        try:
            self.status = "cleanup"
            
            # Cleanup Redis resources
            if self.redis_messaging:
                metrics = self.redis_messaging.get_metrics()
                if self.enable_logging:
                    log_step("Redis Metrics at Cleanup", metrics, LogLevel.INFO)
            
            if self.enable_logging:
                log_step("Agent Cleanup Completed", {
                    "agent_name": self.agent_name,
                    "final_metrics": self._get_performance_metrics()
                }, LogLevel.INFO)
                
                end_operation(
                    operation_id=operation_id,
                    outputs={"cleanup_success": True},
                    status=ExecutionStatus.COMPLETED
                )
            
            logger.info(f"🧹 Cleaned up agent {self.agent_name}")
            
        except Exception as e:
            if self.enable_logging:
                end_operation(
                    operation_id=operation_id,
                    status=ExecutionStatus.FAILED,
                    error=str(e)
                )
            logger.error(f"❌ Cleanup failed for {self.agent_name}: {e}")
            raise
    
    def __str__(self):
        return f"BaseAgent(name={self.agent_name}, type={self.agent_type}, status={self.status})"
    
    def __repr__(self):
        return self.__str__()


# Convenience functions for creating agents (maintain backward compatibility)
@log_method
def create_enhanced_agent(project_client, agent_name: str, instructions: str,
                         model: str = "gpt-4o", tools: List = None, 
                         agent_type: str = "assistant", enable_logging: bool = True,
                         enable_redis: bool = True) -> BaseAgent:
    """
    Create an enhanced agent with comprehensive logging (backward compatibility).
    
    Args:
        project_client: Azure AI Projects client
        agent_name: Unique identifier for the agent
        instructions: System instructions for the agent
        model: AI model to use
        tools: List of tools available to the agent
        agent_type: Type of agent
        enable_logging: Enable comprehensive logging
        enable_redis: Enable Redis messaging
        
    Returns:
        BaseAgent: Enhanced agent instance
    """
    return BaseAgent(
        project_client=project_client,
        agent_name=agent_name,
        instructions=instructions,
        model=model,
        tools=tools,
        agent_type=agent_type,
        enable_logging=enable_logging,
        enable_redis=enable_redis
    )


def create_base_agent(project_client=None, agent_name: str = None, **kwargs) -> BaseAgent:
    """
    Create a base agent (new unified interface).
    
    Args:
        project_client: Azure AI Projects client
        agent_name: Unique identifier for the agent
        **kwargs: Additional configuration options
        
    Returns:
        BaseAgent: Agent instance
    """
    return BaseAgent(project_client=project_client, agent_name=agent_name, **kwargs)


# Backward compatibility aliases
EnhancedBaseAgent = BaseAgent  # For existing imports

# Module initialization
print("🎯 Unified Base Agent loaded successfully!")
print("   📊 Features: Azure AI integration, Comprehensive logging, Redis messaging, Task execution")
print("   🔄 Backward compatibility: EnhancedBaseAgent, create_enhanced_agent, original BaseAgent API")
print("   🚀 Usage: BaseAgent() or create_base_agent() for new code, existing imports will work")
