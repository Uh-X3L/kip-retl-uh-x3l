"""
Enhanced Base Agent with Comprehensive Logging Integration
==========================================================

This module extends the base agent functionality to include comprehensive
execution logging, detailed method tracking, and agent operation monitoring.
All agent operations, method calls, inputs, outputs, and timing are captured.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import comprehensive execution logger
try:
    from ..helpers.logging.comprehensive_execution_logger import (
        log_method, start_operation, end_operation, log_step, 
        LogLevel, ExecutionStatus, get_execution_logger
    )
    COMPREHENSIVE_LOGGING_AVAILABLE = True
except ImportError:
    # Fallback decorators if logger not available
    def log_method(func):
        return func
    def start_operation(*args, **kwargs):
        return "mock_operation_id"
    def end_operation(*args, **kwargs):
        pass
    def log_step(*args, **kwargs):
        pass
    COMPREHENSIVE_LOGGING_AVAILABLE = False

# Import optimized messaging
try:
    from ..helpers.agent_communication.optimized_redis_messaging import (
        OptimizedRedisMessaging, create_optimized_messaging, 
        create_message, MessageType
    )
    REDIS_MESSAGING_AVAILABLE = True
except ImportError:
    REDIS_MESSAGING_AVAILABLE = False

# Import base agent
from .agents.base_agent import BaseAgent as OriginalBaseAgent

logger = logging.getLogger(__name__)

class EnhancedBaseAgent(OriginalBaseAgent):
    """
    Enhanced Base Agent with comprehensive logging and Redis messaging integration.
    """
    
    def __init__(self, project_client, agent_name: str, instructions: str, 
                 model: str = "gpt-4o", tools: List = None, agent_type: str = "assistant",
                 enable_logging: bool = True, enable_redis: bool = True):
        """
        Initialize enhanced agent with comprehensive logging capabilities.
        
        Args:
            project_client: Azure AI Projects client
            agent_name: Unique identifier for the agent
            instructions: System instructions for the agent
            model: AI model to use
            tools: List of tools available to the agent
            agent_type: Type of agent (assistant, researcher, planner, etc.)
            enable_logging: Enable comprehensive logging
            enable_redis: Enable Redis messaging
        """
        # Initialize parent class
        super().__init__(project_client, agent_name, instructions, model, tools, agent_type)
        
        # Enhanced capabilities
        self.enable_logging = enable_logging and COMPREHENSIVE_LOGGING_AVAILABLE
        self.enable_redis = enable_redis and REDIS_MESSAGING_AVAILABLE
        
        # Current operation tracking
        self.current_operation_id = None
        
        # Redis messaging
        self.redis_messaging = None
        if self.enable_redis:
            try:
                self.redis_messaging = create_optimized_messaging()
                log_step("Redis Messaging Initialized", {
                    "agent_name": self.agent_name,
                    "redis_available": True
                }, LogLevel.INFO)
            except Exception as e:
                logger.warning(f"Redis messaging initialization failed: {e}")
                self.enable_redis = False
        
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
    
    @log_method
    def create_thread(self) -> str:
        """Create a new conversation thread with logging."""
        operation_id = None
        if self.enable_logging:
            operation_id = start_operation(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                operation_type="create_thread",
                inputs={}
            )
        
        try:
            thread_id = super().create_thread()
            
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
            
            # Send message using parent method
            response = super().send_message(message, thread_id)
            
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
    def send_redis_message(self, to_agent: str, message_type: MessageType, content: Dict[str, Any]) -> bool:
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
                    "message_type": message_type.value,
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
                    "message_type": message_type.value,
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
                    "type": message.type.value,
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
    def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a task with comprehensive logging and coordination.
        
        Args:
            task_description: Description of the task to execute
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
                    "context": context or {}
                }
            )
        
        start_time = time.time()
        
        try:
            if self.enable_logging:
                log_step("Task Execution Started", {
                    "agent_name": self.agent_name,
                    "task_description": task_description,
                    "context_provided": bool(context)
                }, LogLevel.INFO)
            
            # Create enhanced prompt with context
            enhanced_prompt = f"""
Task: {task_description}

Agent Information:
- Agent Name: {self.agent_name}
- Agent Type: {self.agent_type}
- Capabilities: {', '.join([tool.__class__.__name__ for tool in self.tools]) if self.tools else 'Standard LLM capabilities'}

Context: {json.dumps(context or {}, indent=2)}

Please execute this task providing detailed steps and clear outputs.
"""
            
            # Execute the task
            response = self.send_message(enhanced_prompt)
            
            execution_time = time.time() - start_time
            
            # Parse response and create structured result
            result = {
                "task_description": task_description,
                "agent_name": self.agent_name,
                "agent_type": self.agent_type,
                "execution_time": execution_time,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "context": context or {}
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
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            error_result = {
                "task_description": task_description,
                "agent_name": self.agent_name,
                "agent_type": self.agent_type,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e),
                "context": context or {}
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
            
            return error_result
    
    @log_method
    def get_comprehensive_info(self) -> Dict[str, Any]:
        """Get comprehensive agent information including logging data."""
        base_info = super().get_agent_info()
        
        enhanced_info = {
            **base_info,
            "logging_enabled": self.enable_logging,
            "redis_enabled": self.enable_redis,
            "current_operation": self.current_operation_id,
            "capabilities": {
                "azure_ai": self.azure_available,
                "redis_messaging": self.enable_redis,
                "comprehensive_logging": self.enable_logging,
                "task_execution": True
            },
            "performance_metrics": self._get_performance_metrics()
        }
        
        return enhanced_info
    
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
            # Call parent cleanup
            super().cleanup()
            
            # Additional cleanup for enhanced features
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
            
        except Exception as e:
            if self.enable_logging:
                end_operation(
                    operation_id=operation_id,
                    status=ExecutionStatus.FAILED,
                    error=str(e)
                )
            raise

# Convenience function for creating enhanced agents
@log_method
def create_enhanced_agent(project_client, agent_name: str, instructions: str,
                         model: str = "gpt-4o", tools: List = None, 
                         agent_type: str = "assistant", enable_logging: bool = True,
                         enable_redis: bool = True) -> EnhancedBaseAgent:
    """
    Create an enhanced agent with comprehensive logging.
    
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
        EnhancedBaseAgent: Enhanced agent instance
    """
    return EnhancedBaseAgent(
        project_client=project_client,
        agent_name=agent_name,
        instructions=instructions,
        model=model,
        tools=tools,
        agent_type=agent_type,
        enable_logging=enable_logging,
        enable_redis=enable_redis
    )

# Module initialization
print("🎯 Enhanced Base Agent with Comprehensive Logging loaded successfully!")
print("   📊 Features: Method logging, Operation tracking, Redis messaging, Task execution")
print("   🚀 Usage: create_enhanced_agent() for comprehensive logging capabilities")
