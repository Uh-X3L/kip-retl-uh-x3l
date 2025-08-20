"""
Snoop-Traced Enhanced Base Agent
==============================

This is an enhanced version of your base agent that integrates with the snoop
tracing system for comprehensive execution monitoring and debugging.
"""

import time
import redis
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Import snoop tracing
from .snoop_enhanced_logger import (
    snoop_trace, snoop_trace_class, get_snoop_logger,
    initialize_snoop_tracing
)

# Import your existing modules
try:
    from ..helpers.logging.comprehensive_execution_logger import (
        log_method, start_operation, end_operation, log_step,
        LogLevel, ExecutionStatus, get_execution_logger
    )
    COMPREHENSIVE_LOGGING_AVAILABLE = True
except ImportError:
    print("⚠️ Comprehensive execution logger not available")
    COMPREHENSIVE_LOGGING_AVAILABLE = False

try:
    from ..helpers.agent_communication.optimized_redis_messaging import OptimizedRedisMessaging
    REDIS_MESSAGING_AVAILABLE = True
except ImportError:
    print("⚠️ Redis messaging not available")
    REDIS_MESSAGING_AVAILABLE = False

@snoop_trace_class
class SnoopTracedBaseAgent:
    """
    Enhanced base agent with comprehensive snoop tracing for debugging and monitoring.
    
    This agent provides:
    - Line-by-line execution tracing
    - Method call hierarchy visualization
    - Variable state monitoring
    - Redis message tracing
    - Performance metrics
    - Complete execution flow visibility
    """
    
    def __init__(self, agent_name: str, agent_type: str = "base_agent", 
                 redis_config: Dict[str, Any] = None, 
                 enable_tracing: bool = True,
                 log_dir: str = "logs"):
        """
        Initialize the snoop-traced base agent.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type of the agent
            redis_config: Redis configuration
            enable_tracing: Enable snoop tracing
            log_dir: Directory for logs
        """
        # Initialize snoop tracing if not already done
        if enable_tracing and not get_snoop_logger():
            initialize_snoop_tracing(
                session_name=f"{agent_name}_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                log_dir=log_dir
            )
        
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.enable_tracing = enable_tracing
        self.log_dir = Path(log_dir)
        
        # Agent state
        self.state = "initialized"
        self.task_queue = []
        self.results_cache = {}
        self.performance_metrics = {
            "tasks_completed": 0,
            "total_execution_time": 0.0,
            "average_task_time": 0.0,
            "redis_messages_sent": 0,
            "redis_messages_received": 0
        }
        
        # Initialize Redis messaging if available
        self.redis_messaging = None
        if REDIS_MESSAGING_AVAILABLE and redis_config:
            self.redis_messaging = OptimizedRedisMessaging(**redis_config)
        
        # Log initialization
        if COMPREHENSIVE_LOGGING_AVAILABLE:
            self.operation_id = start_operation(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                operation_type="agent_initialization",
                inputs={
                    "tracing_enabled": self.enable_tracing,
                    "redis_available": REDIS_MESSAGING_AVAILABLE,
                    "log_dir": str(self.log_dir)
                }
            )
        
        print(f"🤖 SNOOP-TRACED AGENT INITIALIZED: {self.agent_name}")
        print(f"   📊 Type: {self.agent_type}")
        print(f"   🔍 Tracing Enabled: {self.enable_tracing}")
        print(f"   📡 Redis Available: {REDIS_MESSAGING_AVAILABLE}")
    
    @snoop_trace
    def add_task(self, task: Dict[str, Any]) -> str:
        """
        Add a task to the agent's queue with full tracing.
        
        Args:
            task: Task dictionary containing task details
            
        Returns:
            str: Task ID
        """
        task_id = f"task_{len(self.task_queue)}_{int(time.time())}"
        
        enhanced_task = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "agent_name": self.agent_name,
            "status": "queued",
            **task
        }
        
        self.task_queue.append(enhanced_task)
        
        if COMPREHENSIVE_LOGGING_AVAILABLE:
            log_step(f"Task Added: {task_id}", {
                "task_details": enhanced_task,
                "queue_length": len(self.task_queue)
            }, LogLevel.INFO)
        
        print(f"📋 Task added: {task_id}")
        return task_id
    
    @snoop_trace
    def execute_task(self, task_id: str = None) -> Dict[str, Any]:
        """
        Execute a task with comprehensive tracing.
        
        Args:
            task_id: Specific task ID to execute, or None for next in queue
            
        Returns:
            Dict[str, Any]: Task execution results
        """
        start_time = time.time()
        
        # Find task to execute
        task_to_execute = None
        if task_id:
            # Find specific task
            for task in self.task_queue:
                if task["task_id"] == task_id:
                    task_to_execute = task
                    break
        else:
            # Get next task in queue
            if self.task_queue:
                task_to_execute = self.task_queue[0]
        
        if not task_to_execute:
            return {"error": "No task found to execute", "task_id": task_id}
        
        # Start operation tracking
        operation_id = None
        if COMPREHENSIVE_LOGGING_AVAILABLE:
            operation_id = start_operation(
                agent_name=self.agent_name,
                agent_type=self.agent_type,
                operation_type="task_execution",
                inputs=task_to_execute
            )
        
        try:
            print(f"🚀 Executing task: {task_to_execute['task_id']}")
            
            # Update task status
            task_to_execute["status"] = "executing"
            task_to_execute["execution_start"] = datetime.now().isoformat()
            
            # Execute the actual task logic (this is where you'd add your specific logic)
            result = self._process_task(task_to_execute)
            
            # Update task status
            task_to_execute["status"] = "completed"
            task_to_execute["execution_end"] = datetime.now().isoformat()
            task_to_execute["result"] = result
            
            # Remove from queue
            if task_to_execute in self.task_queue:
                self.task_queue.remove(task_to_execute)
            
            # Cache result
            self.results_cache[task_to_execute["task_id"]] = result
            
            # Update metrics
            execution_time = time.time() - start_time
            self.performance_metrics["tasks_completed"] += 1
            self.performance_metrics["total_execution_time"] += execution_time
            self.performance_metrics["average_task_time"] = (
                self.performance_metrics["total_execution_time"] / 
                self.performance_metrics["tasks_completed"]
            )
            
            if COMPREHENSIVE_LOGGING_AVAILABLE:
                log_step(f"Task Completed: {task_to_execute['task_id']}", {
                    "execution_time": execution_time,
                    "result": result
                }, LogLevel.INFO)
                
                end_operation(
                    operation_id=operation_id,
                    outputs=result,
                    status=ExecutionStatus.COMPLETED
                )
            
            print(f"✅ Task completed: {task_to_execute['task_id']} ({execution_time:.3f}s)")
            
            return {
                "success": True,
                "task_id": task_to_execute["task_id"],
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Update task status
            task_to_execute["status"] = "failed"
            task_to_execute["error"] = str(e)
            task_to_execute["execution_end"] = datetime.now().isoformat()
            
            if COMPREHENSIVE_LOGGING_AVAILABLE:
                end_operation(
                    operation_id=operation_id,
                    outputs={"error": str(e)},
                    status=ExecutionStatus.FAILED,
                    error=str(e)
                )
            
            print(f"❌ Task failed: {task_to_execute['task_id']} - {e}")
            
            return {
                "success": False,
                "task_id": task_to_execute["task_id"],
                "error": str(e),
                "execution_time": execution_time
            }
    
    @snoop_trace
    def _process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the actual task logic. Override this in subclasses.
        
        Args:
            task: Task to process
            
        Returns:
            Dict[str, Any]: Processing result
        """
        # Default task processing - override in subclasses
        task_type = task.get("type", "unknown")
        
        if task_type == "simple_computation":
            return self._handle_simple_computation(task)
        elif task_type == "data_processing":
            return self._handle_data_processing(task)
        elif task_type == "redis_message":
            return self._handle_redis_message(task)
        else:
            return {
                "processed": True,
                "task_type": task_type,
                "message": f"Task {task['task_id']} processed by {self.agent_name}"
            }
    
    @snoop_trace
    def _handle_simple_computation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle simple computation tasks."""
        data = task.get("data", {})
        operation = data.get("operation", "add")
        values = data.get("values", [])
        
        if operation == "add":
            result = sum(values)
        elif operation == "multiply":
            result = 1
            for value in values:
                result *= value
        else:
            result = f"Unknown operation: {operation}"
        
        return {
            "computation_result": result,
            "operation": operation,
            "input_values": values
        }
    
    @snoop_trace
    def _handle_data_processing(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data processing tasks."""
        data = task.get("data", [])
        processing_type = task.get("processing_type", "count")
        
        if processing_type == "count":
            result = len(data)
        elif processing_type == "filter_positive":
            result = [x for x in data if isinstance(x, (int, float)) and x > 0]
        elif processing_type == "statistics":
            if data:
                result = {
                    "count": len(data),
                    "sum": sum(data) if all(isinstance(x, (int, float)) for x in data) else "N/A",
                    "avg": sum(data) / len(data) if data and all(isinstance(x, (int, float)) for x in data) else "N/A"
                }
            else:
                result = {"count": 0, "sum": 0, "avg": 0}
        else:
            result = f"Unknown processing type: {processing_type}"
        
        return {
            "processing_result": result,
            "processing_type": processing_type,
            "input_data_length": len(data)
        }
    
    @snoop_trace
    def _handle_redis_message(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Redis messaging tasks."""
        if not self.redis_messaging:
            return {"error": "Redis messaging not available"}
        
        action = task.get("action", "send")
        
        if action == "send":
            message = task.get("message", {})
            channel = task.get("channel", "default")
            
            success = self.redis_messaging.send_message(
                channel=channel,
                message=message,
                sender=self.agent_name
            )
            
            if success:
                self.performance_metrics["redis_messages_sent"] += 1
            
            return {
                "redis_action": "send",
                "success": success,
                "channel": channel,
                "message_sent": message
            }
            
        elif action == "receive":
            channel = task.get("channel", "default")
            timeout = task.get("timeout", 5)
            
            messages = self.redis_messaging.receive_messages(
                channel=channel,
                timeout=timeout
            )
            
            self.performance_metrics["redis_messages_received"] += len(messages)
            
            return {
                "redis_action": "receive",
                "channel": channel,
                "messages_received": messages,
                "message_count": len(messages)
            }
        
        return {"error": f"Unknown Redis action: {action}"}
    
    @snoop_trace
    def send_message(self, channel: str, message: Dict[str, Any]) -> bool:
        """
        Send a message via Redis with tracing.
        
        Args:
            channel: Redis channel
            message: Message to send
            
        Returns:
            bool: Success status
        """
        if not self.redis_messaging:
            print("⚠️ Redis messaging not available")
            return False
        
        success = self.redis_messaging.send_message(
            channel=channel,
            message=message,
            sender=self.agent_name
        )
        
        if success:
            self.performance_metrics["redis_messages_sent"] += 1
            
            if COMPREHENSIVE_LOGGING_AVAILABLE:
                log_step(f"Redis Message Sent", {
                    "channel": channel,
                    "message": message
                }, LogLevel.INFO)
        
        return success
    
    @snoop_trace
    def receive_messages(self, channel: str, timeout: int = 5) -> List[Dict[str, Any]]:
        """
        Receive messages from Redis with tracing.
        
        Args:
            channel: Redis channel
            timeout: Timeout in seconds
            
        Returns:
            List[Dict[str, Any]]: Received messages
        """
        if not self.redis_messaging:
            print("⚠️ Redis messaging not available")
            return []
        
        messages = self.redis_messaging.receive_messages(
            channel=channel,
            timeout=timeout
        )
        
        self.performance_metrics["redis_messages_received"] += len(messages)
        
        if COMPREHENSIVE_LOGGING_AVAILABLE:
            log_step(f"Redis Messages Received", {
                "channel": channel,
                "message_count": len(messages),
                "messages": messages
            }, LogLevel.INFO)
        
        return messages
    
    @snoop_trace
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive performance metrics.
        
        Returns:
            Dict[str, Any]: Performance metrics
        """
        metrics = {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "current_state": self.state,
            "queue_length": len(self.task_queue),
            "cached_results": len(self.results_cache),
            **self.performance_metrics
        }
        
        # Add snoop logger metrics if available
        snoop_logger = get_snoop_logger()
        if snoop_logger:
            snoop_summary = snoop_logger.get_trace_summary()
            metrics["tracing_metrics"] = snoop_summary
        
        return metrics
    
    @snoop_trace
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get comprehensive agent status.
        
        Returns:
            Dict[str, Any]: Agent status
        """
        return {
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "state": self.state,
            "task_queue_length": len(self.task_queue),
            "pending_tasks": [task["task_id"] for task in self.task_queue],
            "completed_tasks": list(self.results_cache.keys()),
            "performance_metrics": self.performance_metrics,
            "redis_available": REDIS_MESSAGING_AVAILABLE,
            "tracing_enabled": self.enable_tracing,
            "timestamp": datetime.now().isoformat()
        }
    
    @snoop_trace
    def shutdown(self) -> Dict[str, Any]:
        """
        Gracefully shutdown the agent with final tracing summary.
        
        Returns:
            Dict[str, Any]: Shutdown summary
        """
        print(f"🛑 Shutting down agent: {self.agent_name}")
        
        # Finalize any pending operations
        if COMPREHENSIVE_LOGGING_AVAILABLE and hasattr(self, 'operation_id'):
            end_operation(
                operation_id=self.operation_id,
                outputs=self.get_performance_metrics(),
                status=ExecutionStatus.COMPLETED
            )
        
        # Get final metrics
        final_metrics = self.get_performance_metrics()
        
        # Close Redis connections
        if self.redis_messaging:
            try:
                self.redis_messaging.close()
            except:
                pass
        
        self.state = "shutdown"
        
        print(f"✅ Agent {self.agent_name} shutdown completed")
        
        return {
            "shutdown_status": "completed",
            "final_metrics": final_metrics,
            "timestamp": datetime.now().isoformat()
        }

# Convenience function to create a traced agent
def create_traced_agent(agent_name: str, agent_type: str = "base_agent", 
                       redis_config: Dict[str, Any] = None,
                       enable_tracing: bool = True) -> SnoopTracedBaseAgent:
    """
    Create a new snoop-traced base agent.
    
    Args:
        agent_name: Name of the agent
        agent_type: Type of the agent
        redis_config: Redis configuration
        enable_tracing: Enable snoop tracing
        
    Returns:
        SnoopTracedBaseAgent: Initialized traced agent
    """
    return SnoopTracedBaseAgent(
        agent_name=agent_name,
        agent_type=agent_type,
        redis_config=redis_config,
        enable_tracing=enable_tracing
    )

print("🤖 Snoop-Traced Enhanced Base Agent loaded successfully!")
print("   🔍 Features: Complete execution tracing, Redis messaging, Performance monitoring")
print("   🚀 Usage: create_traced_agent() to start comprehensive agent tracing")
