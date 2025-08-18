"""
Agent Communication Mixin
=========================

Mixin class that provides Redis-based communication capabilities to agents
so they can communicate with the supervisor.
"""

import logging
import threading
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone


# SNOOP TRACING ADDED - Added by snoop integration script
import snoop

# Snoop decorator for functions
trace_func = snoop.snoop

# Snoop decorator for classes  
@trace_func
def trace_class(cls):
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_') and hasattr(attr, '__module__'):
            setattr(cls, attr_name, trace_func(attr))
    return cls


try:
    from .simple_messaging import (
        SimpleMessaging, MessageType, send_task_response, send_task_progress,
        send_error_report, register_with_supervisor, send_heartbeat, send_status_update
    )
    MESSAGING_AVAILABLE = True
except ImportError:
    MESSAGING_AVAILABLE = False

logger = logging.getLogger(__name__)


@trace_class
class AgentCommunicationMixin:
    """
    Mixin that provides Redis communication capabilities to agents.
    
    Agents can inherit from this to automatically get:
    - Registration with supervisor
    - Task progress reporting
    - Error reporting
    - Heartbeat monitoring
    - Status updates
    """
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str],
                 supervisor_id: str = "backend-supervisor-coordinator"):
        """
        Initialize agent communication.
        
        Args:
            agent_id: Unique identifier for this agent
            agent_type: Type of agent (research, devops, testing, etc.)
            capabilities: List of agent capabilities
            supervisor_id: ID of the supervisor to communicate with
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.supervisor_id = supervisor_id
        self.current_tasks = {}
        self.communication_enabled = False
        
        # Initialize messaging if available
        if MESSAGING_AVAILABLE:
            try:
                self.messaging = SimpleMessaging(use_redis=True)
                self.communication_enabled = True
                logger.info(f"✅ Agent {agent_id} communication enabled via Redis")
                
                # Register with supervisor
                self._register_with_supervisor()
                
                # Start heartbeat thread
                self._start_heartbeat()
                
            except Exception as e:
                logger.warning(f"⚠️ Agent {agent_id} communication failed to initialize: {e}")
                self.messaging = None
        else:
            logger.info(f"ℹ️ Agent {agent_id} running without communication (messaging not available)")
    
    def _register_with_supervisor(self):
        """Register this agent with the supervisor."""
        if not self.communication_enabled:
            return
        
        try:
            success = register_with_supervisor(
                self.messaging, 
                self.agent_id,
                self.supervisor_id,
                self.agent_type,
                self.capabilities
            )
            
            if success:
                logger.info(f"✅ Agent {self.agent_id} registered with supervisor")
            else:
                logger.warning(f"⚠️ Agent {self.agent_id} registration failed")
                
        except Exception as e:
            logger.error(f"❌ Agent {self.agent_id} registration error: {e}")
    
    def _start_heartbeat(self):
        """Start heartbeat thread to keep supervisor informed."""
        if not self.communication_enabled:
            return
        
        @trace_func
        def heartbeat_loop():
            while self.communication_enabled:
                try:
                    send_heartbeat(
                        self.messaging,
                        self.agent_id,
                        self.supervisor_id,
                        current_tasks=len(self.current_tasks),
                        status="active"
                    )
                    time.sleep(30)  # Send heartbeat every 30 seconds
                except Exception as e:
                    logger.error(f"❌ Heartbeat error for {self.agent_id}: {e}")
                    time.sleep(60)  # Wait longer on error
        
        heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        logger.info(f"🔄 Started heartbeat for agent {self.agent_id}")
    
    @trace_func
    def report_task_started(self, task_id: str, task_description: str):
        """Report that a task has started."""
        if not self.communication_enabled:
            return
        
        self.current_tasks[task_id] = {
            "description": task_description,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "in_progress"
        }
        
        try:
            send_status_update(
                self.messaging,
                self.agent_id,
                self.supervisor_id,
                {
                    "task_started": {
                        "task_id": task_id,
                        "description": task_description,
                        "started_at": self.current_tasks[task_id]["started_at"]
                    }
                }
            )
            logger.info(f"📤 Agent {self.agent_id} reported task started: {task_id}")
        except Exception as e:
            logger.error(f"❌ Failed to report task start: {e}")
    
    @trace_func
    def report_task_progress(self, task_id: str, progress_percent: float, details: str = ""):
        """Report progress on a task."""
        if not self.communication_enabled or task_id not in self.current_tasks:
            return
        
        try:
            send_task_progress(
                self.messaging,
                self.agent_id,
                self.supervisor_id,
                task_id,
                progress_percent,
                details
            )
            logger.info(f"📊 Agent {self.agent_id} reported progress: {task_id} at {progress_percent}%")
        except Exception as e:
            logger.error(f"❌ Failed to report task progress: {e}")
    
    @trace_func
    def report_task_completed(self, task_id: str, results: Dict[str, Any]):
        """Report that a task has been completed."""
        if not self.communication_enabled:
            return
        
        try:
            send_task_response(
                self.messaging,
                self.agent_id,
                self.supervisor_id,
                task_id,
                results
            )
            
            # Update local task status
            if task_id in self.current_tasks:
                self.current_tasks[task_id]["status"] = "completed"
                self.current_tasks[task_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"✅ Agent {self.agent_id} reported task completed: {task_id}")
        except Exception as e:
            logger.error(f"❌ Failed to report task completion: {e}")
    
    @trace_func
    def report_task_error(self, task_id: str, error_message: str, error_details: Dict[str, Any] = None):
        """Report an error with a task."""
        if not self.communication_enabled:
            return
        
        try:
            send_error_report(
                self.messaging,
                self.agent_id,
                self.supervisor_id,
                task_id,
                error_message,
                error_details
            )
            
            # Update local task status
            if task_id in self.current_tasks:
                self.current_tasks[task_id]["status"] = "error"
                self.current_tasks[task_id]["error"] = error_message
            
            logger.error(f"❌ Agent {self.agent_id} reported task error: {task_id} - {error_message}")
        except Exception as e:
            logger.error(f"❌ Failed to report task error: {e}")
    
    @trace_func
    def report_status_change(self, new_status: str, details: Dict[str, Any] = None):
        """Report a general status change to the supervisor."""
        if not self.communication_enabled:
            return
        
        try:
            status_data = {
                "status": new_status,
                "details": details or {},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            send_status_update(
                self.messaging,
                self.agent_id,
                self.supervisor_id,
                {"status_change": status_data}
            )
            logger.info(f"📢 Agent {self.agent_id} reported status change: {new_status}")
        except Exception as e:
            logger.error(f"❌ Failed to report status change: {e}")
    
    @trace_func
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics for this agent."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "supervisor_id": self.supervisor_id,
            "communication_enabled": self.communication_enabled,
            "current_tasks": len(self.current_tasks),
            "task_list": list(self.current_tasks.keys())
        }
    
    # Convenience methods with simpler names for backward compatibility
    @trace_func
    def send_progress_update(self, task_id: str, progress_percentage: float, 
                           current_step: str = "", details: Dict[str, Any] = None):
        """Send progress update to supervisor."""
        full_details = details or {}
        full_details.update({
            "progress_percentage": progress_percentage,
            "current_step": current_step
        })
        self.report_task_progress(task_id, progress_percentage, current_step)
    
    @trace_func
    def send_error_report(self, error_type: str, error_message: str, 
                         task_id: str = None, severity: str = "medium"):
        """Send error report to supervisor."""
        error_details = {
            "error_type": error_type,
            "error_message": error_message,
            "severity": severity
        }
        if task_id:
            self.report_task_error(task_id, error_message, error_details)
        else:
            self.report_status_change("error", error_details)
    
    @trace_func
    def send_task_response(self, task_id: str, status: str, result: Dict[str, Any]):
        """Send task completion response to supervisor."""
        if status == "completed":
            self.report_task_completed(task_id, result)
        else:
            self.report_task_error(task_id, f"Task {status}", {"final_status": status})
    
    @trace_func
    def register_with_supervisor(self, supervisor_id: str = None):
        """Register with supervisor."""
        if supervisor_id:
            self.supervisor_id = supervisor_id
        
        if not self.communication_enabled:
            self._enable_communication()
        
        # Registration is automatic when communication is enabled
        return {"status": "registered", "supervisor_id": self.supervisor_id}
    
    @trace_func
    def send_heartbeat(self, supervisor_id: str = None, status: str = "active", 
                      current_task: str = None):
        """Send heartbeat to supervisor."""
        heartbeat_details = {
            "status": status,
            "uptime": getattr(self, 'uptime', 0),
            "current_task": current_task
        }
        self.report_status_change("heartbeat", heartbeat_details)
        return {"status": "sent", "heartbeat_id": f"hb_{int(time.time())}"}
    
    @trace_func
    def shutdown_communication(self):
        """Shutdown agent communication gracefully."""
        if not self.communication_enabled:
            return
        
        try:
            # Report shutdown status
            self.report_status_change("shutting_down", {"reason": "agent_shutdown"})
            
            # Disable communication
            self.communication_enabled = False
            
            logger.info(f"🔌 Agent {self.agent_id} communication shutdown")
        except Exception as e:
            logger.error(f"❌ Error during communication shutdown: {e}")


# Enhanced Agent Base Class
@trace_class
class CommunicatingAgent(AgentCommunicationMixin):
    """
    Base class for agents that need to communicate with supervisor.
    
    Combines the communication mixin with a basic agent structure.
    """
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str],
                 supervisor_id: str = "backend-supervisor-coordinator"):
        """Initialize communicating agent."""
        super().__init__(agent_id, agent_type, capabilities, supervisor_id)
        self.is_busy = False
    
    @trace_func
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with automatic progress reporting.
        
        Override this method in subclasses to implement specific task logic.
        """
        task_id = task.get("task_id", f"task_{int(time.time())}")
        task_data = task
        
        self.is_busy = True
        self.report_task_started(task_id, task_data.get("description", "Unknown task"))
        
        try:
            # Report initial progress
            self.report_task_progress(task_id, 0.0, "Task started")
            
            # Simulate task execution (override this in subclasses)
            result = self._perform_task(task_data)
            
            # Report completion
            self.report_task_progress(task_id, 100.0, "Task completed")
            self.report_task_completed(task_id, result)
            
            return result
            
        except Exception as e:
            self.report_task_error(task_id, str(e), {"exception_type": type(e).__name__})
            raise
        finally:
            self.is_busy = False
    
    def _perform_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override this method in subclasses to implement specific task logic.
        
        Args:
            task_data: Data for the task to perform
            
        Returns:
            Task results
        """
        return {"status": "completed", "message": "Base task implementation"}


# Utility functions for agents
@trace_func
def create_agent_id(agent_type: str, instance_number: int = None) -> str:
    """Create a unique agent ID."""
    timestamp = int(time.time())
    if instance_number is not None:
        return f"{agent_type}_{instance_number}_{timestamp}"
    else:
        return f"{agent_type}_{timestamp}"


@trace_func
def get_supervisor_messages(messaging: SimpleMessaging, agent_id: str, limit: int = 10) -> List:
    """Get messages from supervisor for this agent."""
    if not messaging:
        return []
    
    try:
        messages = messaging.get_messages(agent_id, limit)
        supervisor_messages = [
            msg for msg in messages 
            if msg.message_type == MessageType.TASK_REQUEST and "supervisor" in msg.from_agent
        ]
        return supervisor_messages
    except Exception as e:
        logger.error(f"Failed to get supervisor messages: {e}")
        return []
