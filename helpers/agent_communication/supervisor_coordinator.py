"""
Supervisor Coordinator
======================

Manages task delegation, agent coordination, and workflow orchestration.
This is the main coordination layer for autonomous agent communication.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
import uuid

from .message_protocol import (
    AgentMessage, MessageType, MessagePriority, AgentRole,
    TaskRequest, TaskResponse, StatusUpdate,
    create_task_request_message, create_broadcast_message
)
from .queue_manager import MessageQueueManager
from .agent_registry import AgentRegistry, AgentInfo


@dataclass
class TaskAssignment:
    """Represents a task assignment to an agent"""
    task_id: str
    agent_id: str
    task_type: str
    description: str
    parameters: Dict[str, Any]
    priority: MessagePriority
    created_at: str
    deadline: Optional[str] = None
    status: str = "pending"  # pending, assigned, in_progress, completed, failed
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class SupervisorCoordinator:
    """Main coordinator for autonomous agent communication and task management"""
    
    def __init__(
        self,
        supervisor_id: str = "supervisor-main",
        queue_manager: Optional[MessageQueueManager] = None,
        agent_registry: Optional[AgentRegistry] = None
    ):
        """
        Initialize the supervisor coordinator.
        
        Args:
            supervisor_id: Unique ID for this supervisor instance
            queue_manager: Message queue manager instance
            agent_registry: Agent registry instance
        """
        self.supervisor_id = supervisor_id
        self.queue_manager = queue_manager or MessageQueueManager()
        self.agent_registry = agent_registry or AgentRegistry()
        
        # Task tracking
        self.active_tasks: Dict[str, TaskAssignment] = {}
        self.task_callbacks: Dict[str, Callable] = {}
        
        # Performance tracking
        self.metrics = {
            "tasks_assigned": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_completion_time": 0.0
        }
        
        # Register this supervisor
        self._register_supervisor()
        
        logging.info(f"SupervisorCoordinator initialized: {self.supervisor_id}")
    
    def _register_supervisor(self) -> bool:
        """Register this supervisor in the agent registry"""
        return self.agent_registry.register_agent(
            agent_id=self.supervisor_id,
            agent_role=AgentRole.SUPERVISOR,
            capabilities=[
                "task_coordination",
                "agent_management",
                "workflow_orchestration", 
                "load_balancing",
                "error_handling"
            ],
            max_concurrent_tasks=20,  # Supervisors can handle many coordination tasks
            metadata={
                "coordinator_version": "1.0.0",
                "startup_time": datetime.now(timezone.utc).isoformat()
            }
        )
    
    def assign_task(
        self,
        task_type: str,
        description: str,
        parameters: Dict[str, Any],
        required_capabilities: Optional[List[str]] = None,
        priority: MessagePriority = MessagePriority.MEDIUM,
        deadline: Optional[str] = None,
        preferred_agent: Optional[str] = None,
        callback: Optional[Callable] = None
    ) -> Optional[str]:
        """
        Assign a task to an appropriate agent.
        
        Args:
            task_type: Type of task to assign
            description: Human-readable description of the task
            parameters: Task parameters and data
            required_capabilities: List of required agent capabilities
            priority: Task priority level
            deadline: Optional deadline for task completion
            preferred_agent: Preferred agent ID (if available)
            callback: Optional callback function for task completion
            
        Returns:
            str: Task ID if assignment was successful, None otherwise
        """
        try:
            task_id = str(uuid.uuid4())
            
            # Find an appropriate agent
            target_agent = self._find_best_agent(
                required_capabilities or [],
                preferred_agent
            )
            
            if not target_agent:
                logging.error(f"No suitable agent found for task: {task_type}")
                return None
            
            # Create task assignment
            assignment = TaskAssignment(
                task_id=task_id,
                agent_id=target_agent.agent_id,
                task_type=task_type,
                description=description,
                parameters=parameters,
                priority=priority,
                deadline=deadline,
                created_at=datetime.now(timezone.utc).isoformat()
            )
            
            # Create and send task request message
            task_request = TaskRequest(
                task_id=task_id,
                task_type=task_type,
                description=description,
                parameters=parameters,
                deadline=deadline,
                required_capabilities=required_capabilities or []
            )
            
            message = create_task_request_message(
                from_agent=self.supervisor_id,
                to_agent=target_agent.agent_id,
                task_request=task_request,
                priority=priority
            )
            
            # Send the message
            if self.queue_manager.send_message(message):
                self.active_tasks[task_id] = assignment
                if callback:
                    self.task_callbacks[task_id] = callback
                
                self.metrics["tasks_assigned"] += 1
                assignment.status = "assigned"
                
                logging.info(f"✅ Task assigned: {task_id} → {target_agent.agent_id}")
                logging.info(f"   Type: {task_type}, Priority: {priority.value}")
                
                return task_id
            else:
                logging.error(f"Failed to send task message: {task_id}")
                return None
                
        except Exception as e:
            logging.error(f"Failed to assign task: {e}")
            return None
    
    def _find_best_agent(
        self,
        required_capabilities: List[str],
        preferred_agent: Optional[str] = None
    ) -> Optional[AgentInfo]:
        """Find the best available agent for a task"""
        
        # Check if preferred agent is available and suitable
        if preferred_agent:
            agent = self.agent_registry.get_agent(preferred_agent)
            if agent and agent.is_available():
                # Check capabilities if specified
                if not required_capabilities or all(cap in agent.capabilities for cap in required_capabilities):
                    return agent
        
        # Find available agents with required capabilities
        available_agents = self.agent_registry.find_available_agents(
            required_capabilities=required_capabilities,
            agent_role=AgentRole.WORKER,  # Default to worker agents
            max_results=10
        )
        
        if not available_agents:
            logging.warning(f"No available agents found with capabilities: {required_capabilities}")
            return None
        
        # Return the agent with the lowest load
        return available_agents[0]  # Already sorted by load factor
    
    def process_incoming_messages(self, max_messages: int = 10) -> int:
        """
        Process incoming messages for this supervisor.
        
        Args:
            max_messages: Maximum number of messages to process
            
        Returns:
            int: Number of messages processed
        """
        try:
            messages = self.queue_manager.get_messages(
                agent_id=self.supervisor_id,
                limit=max_messages
            )
            
            processed_count = 0
            for message in messages:
                if self._process_message(message):
                    self.queue_manager.mark_processed(
                        message.message_id,
                        self.supervisor_id
                    )
                    processed_count += 1
            
            if processed_count > 0:
                logging.info(f"📨 Processed {processed_count} messages")
            
            return processed_count
            
        except Exception as e:
            logging.error(f"Failed to process incoming messages: {e}")
            return 0
    
    def _process_message(self, message: AgentMessage) -> bool:
        """Process a single incoming message"""
        try:
            if message.message_type == MessageType.TASK_RESPONSE:
                return self._handle_task_response(message)
            elif message.message_type == MessageType.STATUS_UPDATE:
                return self._handle_status_update(message)
            elif message.message_type == MessageType.ERROR_REPORT:
                return self._handle_error_report(message)
            elif message.message_type == MessageType.HEARTBEAT:
                return self._handle_heartbeat(message)
            else:
                logging.warning(f"Unhandled message type: {message.message_type.value}")
                return True  # Mark as processed to avoid reprocessing
                
        except Exception as e:
            logging.error(f"Failed to process message {message.message_id}: {e}")
            return False
    
    def _handle_task_response(self, message: AgentMessage) -> bool:
        """Handle a task response from an agent"""
        try:
            content = message.content
            task_id = content.get('task_id')
            
            if not task_id or task_id not in self.active_tasks:
                logging.warning(f"Received response for unknown task: {task_id}")
                return True
            
            assignment = self.active_tasks[task_id]
            response_status = content.get('status', 'unknown')
            
            # Update task assignment
            assignment.status = response_status
            assignment.progress = content.get('progress', 1.0)
            assignment.result = content.get('result')
            assignment.error_message = content.get('error_message')
            
            logging.info(f"📋 Task response: {task_id} → {response_status}")
            
            # Handle completion
            if response_status in ['completed', 'failed']:
                self._complete_task(task_id, assignment)
            
            # Execute callback if provided
            if task_id in self.task_callbacks:
                try:
                    self.task_callbacks[task_id](assignment)
                except Exception as e:
                    logging.error(f"Task callback failed for {task_id}: {e}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to handle task response: {e}")
            return False
    
    def _handle_status_update(self, message: AgentMessage) -> bool:
        """Handle an agent status update"""
        try:
            content = message.content
            agent_id = message.from_agent
            
            # Update agent registry with new status
            self.agent_registry.update_heartbeat(
                agent_id=agent_id,
                status=content.get('status', 'active'),
                current_tasks=content.get('current_task_count', 0),
                metadata=content.get('metadata', {})
            )
            
            logging.debug(f"📊 Status update from {agent_id}: {content.get('status')}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to handle status update: {e}")
            return False
    
    def _handle_error_report(self, message: AgentMessage) -> bool:
        """Handle an error report from an agent"""
        try:
            content = message.content
            agent_id = message.from_agent
            error_type = content.get('error_type', 'unknown')
            error_message = content.get('error_message', 'No details provided')
            
            logging.error(f"❌ Error report from {agent_id}: {error_type}")
            logging.error(f"   Details: {error_message}")
            
            # If this is related to a task, mark it as failed
            task_id = content.get('task_id')
            if task_id and task_id in self.active_tasks:
                assignment = self.active_tasks[task_id]
                assignment.status = 'failed'
                assignment.error_message = error_message
                self._complete_task(task_id, assignment)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to handle error report: {e}")
            return False
    
    def _handle_heartbeat(self, message: AgentMessage) -> bool:
        """Handle a heartbeat message from an agent"""
        try:
            content = message.content
            agent_id = message.from_agent
            
            # Update agent registry
            self.agent_registry.update_heartbeat(
                agent_id=agent_id,
                status=content.get('status', 'active'),
                current_tasks=content.get('current_tasks', 0),
                metadata=content
            )
            
            logging.debug(f"💓 Heartbeat from {agent_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to handle heartbeat: {e}")
            return False
    
    def _complete_task(self, task_id: str, assignment: TaskAssignment) -> None:
        """Complete a task and update metrics"""
        try:
            # Calculate completion time
            start_time = datetime.fromisoformat(assignment.created_at.replace('Z', '+00:00'))
            completion_time = datetime.now(timezone.utc)
            duration = (completion_time - start_time).total_seconds() / 3600  # hours
            
            # Update metrics
            if assignment.status == 'completed':
                self.metrics["tasks_completed"] += 1
                
                # Update average completion time
                current_avg = self.metrics["average_completion_time"]
                completed_count = self.metrics["tasks_completed"]
                self.metrics["average_completion_time"] = (
                    (current_avg * (completed_count - 1) + duration) / completed_count
                )
            else:
                self.metrics["tasks_failed"] += 1
            
            # Remove from active tasks (optionally keep in history)
            del self.active_tasks[task_id]
            
            # Remove callback
            if task_id in self.task_callbacks:
                del self.task_callbacks[task_id]
            
            logging.info(f"🏁 Task completed: {task_id} ({assignment.status}) in {duration:.2f}h")
            
        except Exception as e:
            logging.error(f"Failed to complete task {task_id}: {e}")
    
    def broadcast_message(self, content: Dict[str, Any], message_type: MessageType = MessageType.BROADCAST) -> bool:
        """Send a broadcast message to all agents"""
        try:
            message = create_broadcast_message(
                from_agent=self.supervisor_id,
                content=content,
                message_type=message_type
            )
            
            return self.queue_manager.send_message(message)
            
        except Exception as e:
            logging.error(f"Failed to send broadcast message: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task"""
        if task_id in self.active_tasks:
            assignment = self.active_tasks[task_id]
            return {
                "task_id": task_id,
                "agent_id": assignment.agent_id,
                "status": assignment.status,
                "progress": assignment.progress,
                "created_at": assignment.created_at,
                "deadline": assignment.deadline,
                "result": assignment.result,
                "error_message": assignment.error_message
            }
        return None
    
    def get_coordination_stats(self) -> Dict[str, Any]:
        """Get statistics about coordination performance"""
        active_tasks = len(self.active_tasks)
        agent_stats = self.agent_registry.get_registry_stats()
        queue_stats = self.queue_manager.get_queue_stats()
        
        return {
            "supervisor_id": self.supervisor_id,
            "active_tasks": active_tasks,
            "metrics": self.metrics.copy(),
            "agent_registry": agent_stats,
            "message_queue": queue_stats,
            "uptime": datetime.now(timezone.utc).isoformat()
        }
    
    def cleanup_and_maintenance(self) -> Dict[str, int]:
        """Perform cleanup and maintenance tasks"""
        try:
            results = {}
            
            # Cleanup stale agents
            results["stale_agents_cleaned"] = self.agent_registry.cleanup_stale_agents()
            
            # Cleanup expired messages
            results["expired_messages_cleaned"] = self.queue_manager.cleanup_expired_messages()
            
            # Check for stuck tasks (tasks that haven't been updated in a while)
            stuck_tasks = []
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=2)
            
            for task_id, assignment in list(self.active_tasks.items()):
                task_time = datetime.fromisoformat(assignment.created_at.replace('Z', '+00:00'))
                if task_time < cutoff_time and assignment.status in ['pending', 'assigned']:
                    stuck_tasks.append(task_id)
            
            results["stuck_tasks_found"] = len(stuck_tasks)
            
            # Optionally reassign stuck tasks
            for task_id in stuck_tasks:
                logging.warning(f"Found stuck task: {task_id}")
                # Could implement reassignment logic here
            
            if any(results.values()):
                logging.info(f"🧹 Maintenance completed: {results}")
            
            return results
            
        except Exception as e:
            logging.error(f"Failed to perform maintenance: {e}")
            return {"error": str(e)}
    
    def shutdown(self) -> bool:
        """Gracefully shutdown the supervisor"""
        try:
            # Send shutdown notification to all agents
            self.broadcast_message({
                "type": "supervisor_shutdown",
                "supervisor_id": self.supervisor_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "active_tasks": len(self.active_tasks)
            })
            
            logging.info(f"🔄 Supervisor {self.supervisor_id} shutting down...")
            logging.info(f"   Active tasks: {len(self.active_tasks)}")
            logging.info(f"   Total tasks assigned: {self.metrics['tasks_assigned']}")
            logging.info(f"   Total tasks completed: {self.metrics['tasks_completed']}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to shutdown gracefully: {e}")
            return False


# Convenience functions for common workflows
def create_simple_coordinator(supervisor_id: str = "supervisor-main") -> SupervisorCoordinator:
    """Create a supervisor coordinator with default configuration"""
    return SupervisorCoordinator(supervisor_id=supervisor_id)


def assign_code_review_task(
    coordinator: SupervisorCoordinator,
    repository: str,
    pull_request: int,
    priority: MessagePriority = MessagePriority.MEDIUM
) -> Optional[str]:
    """Assign a code review task to an appropriate agent"""
    return coordinator.assign_task(
        task_type="code_review",
        description=f"Review pull request #{pull_request} in {repository}",
        parameters={
            "repository": repository,
            "pull_request": pull_request,
            "review_guidelines": "standard"
        },
        required_capabilities=["code_review", "python"],
        priority=priority
    )


def assign_testing_task(
    coordinator: SupervisorCoordinator,
    test_suite: str,
    test_parameters: Dict[str, Any],
    priority: MessagePriority = MessagePriority.HIGH
) -> Optional[str]:
    """Assign a testing task to a testing agent"""
    return coordinator.assign_task(
        task_type="automated_testing",
        description=f"Execute test suite: {test_suite}",
        parameters=test_parameters,
        required_capabilities=["testing", "test_automation"],
        priority=priority
    )
