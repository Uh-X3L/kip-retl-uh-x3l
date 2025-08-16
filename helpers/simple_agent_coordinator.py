#!/usr/bin/env python3
"""
Simple Agent Coordinator
========================

Clean integration between BackendSupervisorAgent, specialized agents from agents/ folder,
and Redis messaging. Simplified approach focusing on essential coordination.
"""

import os
import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Import simplified messaging
try:
    from .simple_messaging import SimpleMessaging, MessageType, MessagePriority, send_task_to_agent, SimpleMessage
    MESSAGING_AVAILABLE = True
except ImportError:
    MESSAGING_AVAILABLE = False
    logging.warning("Simple messaging not available")

# Import existing agents from agents/ folder
try:
    from agents import AgentManager, AGENT_TYPES
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    logging.debug("Agents module not available - using simplified coordination mode")

# Import backend supervisor
try:
    from backend_supervisor_role_tools import BackendSupervisorAgent
    SUPERVISOR_AVAILABLE = True
except ImportError:
    SUPERVISOR_AVAILABLE = False
    logging.debug("Backend supervisor not available - using simplified coordination mode")

# Import Azure AI Projects
try:
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    from azure.ai.projects import AIProjectClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logging.debug("Azure AI Projects not available - using simplified coordination mode")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleAgentCoordinator:
    """
    Simplified agent coordinator that integrates:
    - BackendSupervisorAgent for strategic planning
    - Specialized agents from agents/ folder for task execution  
    - Redis messaging for coordination (optional)
    """
    
    def __init__(self, coordinator_id: str = "simple-coordinator"):
        """Initialize the simple agent coordinator."""
        self.coordinator_id = coordinator_id
        self.active_tasks = {}
        self.completed_tasks = {}
        
        # Initialize messaging (optional)
        self.messaging = None
        if MESSAGING_AVAILABLE:
            try:
                self.messaging = SimpleMessaging(use_redis=True)
                logger.info("✅ Simple messaging enabled")
            except Exception as e:
                logger.info(f"ℹ️ Using memory messaging: {e}")
                self.messaging = SimpleMessaging(use_redis=False)
        
        # Initialize Azure and agents
        self.agent_manager = None
        if AZURE_AVAILABLE and AGENTS_AVAILABLE:
            try:
                # Use environment variables or default
                project_endpoint = os.getenv("PROJECT_ENDPOINT")
                if project_endpoint:
                    credential = DefaultAzureCredential()
                    self.project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
                    self.agent_manager = AgentManager(self.project_client)
                    logger.info("✅ Azure AI agents enabled")
            except Exception as e:
                logger.warning(f"Azure agents unavailable: {e}")
        
        # Initialize supervisor
        self.supervisor = None
        if SUPERVISOR_AVAILABLE:
            try:
                self.supervisor = BackendSupervisorAgent()
                logger.info("✅ Backend supervisor enabled") 
            except Exception as e:
                logger.warning(f"Supervisor unavailable: {e}")
        
        logger.info(f"🎯 Simple Agent Coordinator '{coordinator_id}' ready")
    
    def coordinate_project(self, project_idea: str, requirements: str = "") -> Dict[str, Any]:
        """
        Coordinate a complete project using supervisor + specialized agents.
        
        Args:
            project_idea: The project to coordinate
            requirements: Additional project requirements
            
        Returns:
            Coordination results with task assignments and progress
        """
        logger.info(f"🚀 Coordinating project: {project_idea}")
        
        coordination_result = {
            "project_id": f"proj_{int(time.time())}",
            "project_idea": project_idea,
            "requirements": requirements,
            "status": "started",
            "phases": {},
            "agents_used": [],
            "task_assignments": [],
            "start_time": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Phase 1: Supervisor Strategic Planning
            logger.info("📋 Phase 1: Strategic planning with supervisor...")
            if self.supervisor:
                planning_result = self.supervisor.create_comprehensive_project(
                    project_idea=project_idea,
                    requirements=requirements
                )
                coordination_result["phases"]["strategic_planning"] = planning_result
                coordination_result["agents_used"].append("backend_supervisor")
                
                # Extract subtasks for agent delegation
                subtasks = planning_result.get("deliverables", {}).get("project_plan", {}).get("subtasks", [])
            else:
                # Fallback: create basic subtasks
                subtasks = self._create_basic_subtasks(project_idea, requirements)
                coordination_result["phases"]["strategic_planning"] = {
                    "status": "fallback_mode",
                    "subtasks_created": len(subtasks)
                }
            
            # Phase 2: Task Delegation to Specialized Agents
            logger.info("🎯 Phase 2: Delegating tasks to specialized agents...")
            if self.agent_manager and subtasks:
                delegation_results = self._delegate_tasks_to_agents(subtasks, coordination_result["project_id"])
                coordination_result["phases"]["task_delegation"] = delegation_results
                coordination_result["task_assignments"] = delegation_results.get("assignments", [])
            else:
                coordination_result["phases"]["task_delegation"] = {
                    "status": "skipped",
                    "reason": "No agent manager or subtasks available"
                }
            
            # Phase 3: Coordination and Monitoring
            logger.info("📊 Phase 3: Coordination monitoring...")
            if self.messaging and coordination_result["task_assignments"]:
                monitoring_result = self._monitor_task_execution(coordination_result["task_assignments"])
                coordination_result["phases"]["monitoring"] = monitoring_result
            else:
                coordination_result["phases"]["monitoring"] = {
                    "status": "no_messaging",
                    "message": "Task monitoring requires Redis messaging"
                }
            
            # Final status
            coordination_result["status"] = "completed"
            coordination_result["end_time"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"✅ Project coordination completed: {project_idea}")
            return coordination_result
            
        except Exception as e:
            logger.error(f"❌ Project coordination failed: {e}")
            coordination_result["status"] = "failed"
            coordination_result["error"] = str(e)
            coordination_result["end_time"] = datetime.now(timezone.utc).isoformat()
            return coordination_result
    
    def _create_basic_subtasks(self, project_idea: str, requirements: str) -> List[Dict[str, Any]]:
        """Create basic subtasks when supervisor is unavailable."""
        return [
            {
                "title": "Project Setup",
                "description": f"Set up basic project structure for {project_idea}",
                "estimated_hours": 2.0,
                "agent_type": "worker",
                "skills_required": ["setup", "configuration"]
            },
            {
                "title": "Core Implementation", 
                "description": f"Implement main functionality for {project_idea}",
                "estimated_hours": 8.0,
                "agent_type": "worker",
                "skills_required": ["programming", "development"]
            },
            {
                "title": "Testing and Validation",
                "description": f"Test and validate {project_idea}",
                "estimated_hours": 3.0,
                "agent_type": "testing",
                "skills_required": ["testing", "validation"]
            }
        ]
    
    def _delegate_tasks_to_agents(self, subtasks: List[Dict[str, Any]], project_id: str) -> Dict[str, Any]:
        """Delegate subtasks to appropriate specialized agents."""
        logger.info(f"🎯 Delegating {len(subtasks)} tasks to specialized agents...")
        
        delegation_result = {
            "total_tasks": len(subtasks),
            "assignments": [],
            "agent_assignments": {},
            "delegation_time": datetime.now(timezone.utc).isoformat()
        }
        
        for i, subtask in enumerate(subtasks):
            task_id = f"{project_id}_task_{i+1}"
            agent_type = subtask.get("agent_type", "worker")
            
            try:
                # Get appropriate agent based on task type
                assigned_agent = self._get_agent_for_task(agent_type, subtask)
                
                if assigned_agent:
                    # Create task assignment
                    assignment = {
                        "task_id": task_id,
                        "task_title": subtask.get("title", "Untitled Task"),
                        "task_description": subtask.get("description", ""),
                        "agent_type": agent_type,
                        "agent_id": assigned_agent.get("agent_id", f"{agent_type}_agent"),
                        "estimated_hours": subtask.get("estimated_hours", 1.0),
                        "skills_required": subtask.get("skills_required", []),
                        "status": "assigned",
                        "assigned_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    delegation_result["assignments"].append(assignment)
                    
                    # Track agent workload
                    agent_key = assignment["agent_id"]
                    if agent_key not in delegation_result["agent_assignments"]:
                        delegation_result["agent_assignments"][agent_key] = []
                    delegation_result["agent_assignments"][agent_key].append(task_id)
                    
                    # Send task via messaging if available
                    if self.messaging:
                        self._send_task_assignment(assignment)
                    
                    logger.info(f"✅ Task '{subtask.get('title')}' assigned to {agent_type}")
                else:
                    logger.warning(f"⚠️ No agent available for task type: {agent_type}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to assign task {task_id}: {e}")
        
        delegation_result["successful_assignments"] = len(delegation_result["assignments"])
        return delegation_result
    
    def _get_agent_for_task(self, agent_type: str, subtask: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get appropriate agent for a task type."""
        if not self.agent_manager:
            return {"agent_id": f"mock_{agent_type}_agent", "type": "mock"}
        
        try:
            # Map task types to agent manager methods
            agent_mapping = {
                "research": self.agent_manager.get_research_agent,
                "planning": self.agent_manager.get_planner_agent, 
                "devops": self.agent_manager.get_devops_agent,
                "worker": self.agent_manager.get_worker_agent,
                "testing": self.agent_manager.get_testing_agent,
                "documentation": self.agent_manager.get_documentation_agent
            }
            
            # Get agent from manager
            agent_getter = agent_mapping.get(agent_type, self.agent_manager.get_worker_agent)
            agent = agent_getter()
            
            if agent:
                return {
                    "agent_id": f"{agent_type}_{int(time.time())}",
                    "agent_instance": agent,
                    "type": agent_type,
                    "capabilities": subtask.get("skills_required", [])
                }
            
        except Exception as e:
            logger.error(f"Failed to get agent for type {agent_type}: {e}")
        
        return None
    
    def _send_task_assignment(self, assignment: Dict[str, Any]):
        """Send task assignment via messaging system."""
        if not self.messaging:
            return
        
        try:
            # Create task assignment using simplified messaging
            task_data = {
                "task_id": assignment["task_id"],
                "title": assignment["task_title"],
                "description": assignment["task_description"],
                "estimated_hours": assignment["estimated_hours"],
                "skills_required": assignment["skills_required"],
                "coordinator_id": self.coordinator_id
            }
            
            success = send_task_to_agent(
                self.messaging,
                self.coordinator_id,
                assignment["agent_id"],
                task_data
            )
            
            if success:
                logger.info(f"📨 Task assignment sent to {assignment['agent_id']}")
            else:
                logger.warning(f"⚠️ Failed to send task assignment to {assignment['agent_id']}")
                
        except Exception as e:
            logger.error(f"❌ Error sending task assignment: {e}")
    
    def _monitor_task_execution(self, task_assignments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Monitor task execution through messaging."""
        logger.info("📊 Starting task execution monitoring...")
        
        monitoring_result = {
            "monitoring_start": datetime.now(timezone.utc).isoformat(),
            "tasks_monitored": len(task_assignments),
            "status_updates": [],
            "completion_status": {},
            "agent_registrations": [],
            "progress_updates": [],
            "error_reports": []
        }
        
        if not self.messaging:
            monitoring_result["status"] = "no_messaging_available"
            return monitoring_result
        
        # Enhanced monitoring loop for agent communication
        monitor_duration = 30  # seconds (increased for better agent communication)
        check_interval = 3    # seconds
        
        for check in range(monitor_duration // check_interval):
            try:
                # Check for all types of messages from agents
                messages = self.messaging.get_messages(
                    agent_id=self.coordinator_id,
                    limit=50  # Increased to handle more agent messages
                )
                
                for message in messages:
                    if message.message_type == MessageType.TASK_RESPONSE:
                        self._process_task_response(message, monitoring_result)
                    elif message.message_type == MessageType.STATUS_UPDATE:
                        self._process_status_update(message, monitoring_result)
                    elif message.message_type == MessageType.AGENT_REGISTRATION:
                        self._process_agent_registration(message, monitoring_result)
                    elif message.message_type == MessageType.TASK_PROGRESS:
                        self._process_task_progress(message, monitoring_result)
                    elif message.message_type == MessageType.ERROR_REPORT:
                        self._process_error_report(message, monitoring_result)
                    elif message.message_type == MessageType.AGENT_HEARTBEAT:
                        self._process_agent_heartbeat(message, monitoring_result)
                
                time.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error during monitoring check {check}: {e}")
        
        monitoring_result["monitoring_end"] = datetime.now(timezone.utc).isoformat()
        monitoring_result["final_status"] = self._calculate_final_status(monitoring_result)
        
        return monitoring_result
    
    def _process_task_response(self, message: SimpleMessage, monitoring_result: Dict[str, Any]):
        """Process task completion response from agent."""
        try:
            task_data = message.content.get("response", {}).get("task_result", {})
            task_id = task_data.get("task_id", "unknown")
            
            response_record = {
                "type": "task_completion",
                "task_id": task_id,
                "agent_id": message.from_agent,
                "status": task_data.get("status", "completed"),
                "execution_time": task_data.get("execution_time", 0),
                "results": task_data.get("results", {}),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            monitoring_result["status_updates"].append(response_record)
            monitoring_result["completion_status"][task_id] = response_record
            
            logger.info(f"✅ Task {task_id} completed by {message.from_agent}")
            
        except Exception as e:
            logger.error(f"Error processing task response: {e}")
    
    def _process_status_update(self, message: SimpleMessage, monitoring_result: Dict[str, Any]):
        """Process status update from agent."""
        try:
            status_record = {
                "type": "status_update",
                "agent_id": message.from_agent,
                "status": message.content.get("status", {}).get("status", "unknown"),
                "details": message.content.get("status", {}).get("details", {}),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            monitoring_result["status_updates"].append(status_record)
            logger.info(f"📊 Status update from {message.from_agent}: {status_record['status']}")
            
        except Exception as e:
            logger.error(f"Error processing status update: {e}")
    
    def _calculate_final_status(self, monitoring_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final coordination status."""
        completed_tasks = len(monitoring_result["completion_status"])
        total_tasks = monitoring_result["tasks_monitored"]
        error_count = len(monitoring_result.get("error_reports", []))
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "status_updates_received": len(monitoring_result["status_updates"]),
            "error_reports": error_count,
            "agent_registrations": len(monitoring_result.get("agent_registrations", [])),
            "progress_updates": len(monitoring_result.get("progress_updates", [])),
            "overall_status": "failed" if error_count > completed_tasks else 
                             "completed" if completed_tasks == total_tasks else "partial"
        }
    
    def _process_agent_registration(self, message: SimpleMessage, result: Dict[str, Any]) -> None:
        """Process agent registration message."""
        try:
            registration_data = {
                "timestamp": message.created_at,
                "agent_id": message.from_agent,
                "agent_type": message.content.get("agent_type"),
                "capabilities": message.content.get("capabilities", []),
                "status": "registered",
                "metadata": getattr(message, 'metadata', {})
            }
            
            result["agent_registrations"].append(registration_data)
            logger.info(f"🔗 Agent registered: {message.from_agent} ({message.content.get('agent_type')})")
            
        except Exception as e:
            logger.error(f"Error processing agent registration: {e}")

    def _process_task_progress(self, message: SimpleMessage, result: Dict[str, Any]) -> None:
        """Process task progress update from an agent."""
        try:
            progress_data = {
                "timestamp": message.created_at,
                "agent_id": message.from_agent,
                "task_id": message.content.get("task_id"),
                "progress_percentage": message.content.get("progress_percentage"),
                "current_step": message.content.get("current_step"),
                "details": message.content.get("details"),
                "metadata": getattr(message, 'metadata', {})
            }
            
            result["progress_updates"].append(progress_data)
            logger.info(f"⏳ Progress from {message.from_agent}: {message.content.get('progress_percentage', 0)}% - {message.content.get('current_step')}")
            
        except Exception as e:
            logger.error(f"Error processing task progress: {e}")

    def _process_error_report(self, message: SimpleMessage, result: Dict[str, Any]) -> None:
        """Process error report from an agent."""
        try:
            error_data = {
                "timestamp": message.created_at,
                "agent_id": message.from_agent,
                "error_type": message.content.get("error_type"),
                "error_message": message.content.get("error_message"),
                "task_id": message.content.get("task_id"),
                "severity": message.content.get("severity", "medium"),
                "metadata": getattr(message, 'metadata', {})
            }
            
            result["error_reports"].append(error_data)
            logger.error(f"❌ Error report from {message.from_agent}: {message.content.get('error_type')} - {message.content.get('error_message')}")
            
        except Exception as e:
            logger.error(f"Error processing error report: {e}")

    def _process_agent_heartbeat(self, message: SimpleMessage, result: Dict[str, Any]) -> None:
        """Process heartbeat from an agent."""
        try:
            # Track heartbeats in a separate structure for health monitoring
            if "agent_heartbeats" not in result:
                result["agent_heartbeats"] = {}
            
            result["agent_heartbeats"][message.from_agent] = {
                "last_heartbeat": message.created_at,
                "status": message.content.get("status"),
                "uptime": message.content.get("uptime"),
                "current_task": message.content.get("current_task")
            }
            
            logger.debug(f"💓 Heartbeat from {message.from_agent} - Status: {message.content.get('status')}")
            
        except Exception as e:
            logger.error(f"Error processing agent heartbeat: {e}")
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status."""
        return {
            "coordinator_id": self.coordinator_id,
            "messaging_available": self.messaging is not None,
            "agents_available": self.agent_manager is not None,
            "supervisor_available": self.supervisor is not None,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "capabilities": {
                "simple_messaging": MESSAGING_AVAILABLE,
                "azure_agents": AZURE_AVAILABLE and AGENTS_AVAILABLE,
                "backend_supervisor": SUPERVISOR_AVAILABLE
            }
        }
    
    def quick_demo(self) -> Dict[str, Any]:
        """Run a quick demonstration of the coordination system."""
        logger.info("🎯 Running quick coordination demo...")
        
        demo_project = "Simple Python Web API"
        demo_requirements = "Create a basic REST API with user authentication"
        
        return self.coordinate_project(demo_project, demo_requirements)


def main():
    """Main function to demonstrate the simple agent coordinator."""
    print("=== Simple Agent Coordinator Demo ===")
    
    # Initialize coordinator
    coordinator = SimpleAgentCoordinator("demo-coordinator")
    
    # Show status
    status = coordinator.get_coordination_status()
    print(f"\n📊 Coordinator Status:")
    print(f"   Messaging: {status['messaging_available']}")
    print(f"   Agents: {status['agents_available']}")
    print(f"   Supervisor: {status['supervisor_available']}")
    
    # Run demo
    print(f"\n🚀 Running coordination demo...")
    demo_result = coordinator.quick_demo()
    
    print(f"\n✅ Demo completed!")
    print(f"   Project: {demo_result['project_idea']}")
    print(f"   Status: {demo_result['status']}")
    print(f"   Phases completed: {len(demo_result['phases'])}")
    print(f"   Agents used: {', '.join(demo_result['agents_used'])}")
    
    if demo_result.get("task_assignments"):
        print(f"   Tasks assigned: {len(demo_result['task_assignments'])}")
    
    return demo_result


if __name__ == "__main__":
    main()
