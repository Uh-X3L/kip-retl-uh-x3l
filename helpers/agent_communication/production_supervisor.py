#!/usr/bin/env python3
"""
Production Azure AI Supervisor Coordinator
==========================================

Real integration between BackendSupervisorAgent, Azure AI Foundry agents,
and Redis messaging for production-ready multi-agent coordination.
"""

import sys
import os
import logging
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import Redis messaging
from message_protocol import AgentMessage, MessageType, MessagePriority
from queue_manager import MessageQueueManager

# Import Azure components
try:
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    from azure.ai.projects import AIProjectClient
    from agents.agent_manager import AgentManager
    AZURE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Azure components not available: {e}")
    AZURE_AVAILABLE = False

# Import backend supervisor (should always work)
try:
    from backend_supervisor_role_tools import BackendSupervisorAgent, create_project_plan
    SUPERVISOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Backend supervisor not available: {e}")
    SUPERVISOR_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ProductionSupervisorCoordinator:
    """
    Production-ready supervisor that combines BackendSupervisorAgent with Azure AI agents
    and Redis messaging for comprehensive project coordination.
    """
    
    def __init__(self, supervisor_id: str = "production-supervisor-001"):
        """
        Initialize the production supervisor coordinator.
        
        Args:
            supervisor_id: Unique identifier for this supervisor
        """
        self.supervisor_id = supervisor_id
        self.azure_available = AZURE_AVAILABLE
        self.supervisor_available = SUPERVISOR_AVAILABLE
        
        # Initialize Redis messaging
        try:
            self.queue_manager = MessageQueueManager(use_mock=False)
            logger.info("✅ Connected to Redis for supervisor coordination")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable ({e}), using mock mode")
            self.queue_manager = MessageQueueManager(use_mock=True)
        
        # Initialize Azure components if available
        self.project_client = None
        self.agent_manager = None
        self.supervisor = None
        
        if self.azure_available:
            self._initialize_azure_components()
        
        # Initialize backend supervisor (works without Azure)
        if SUPERVISOR_AVAILABLE:
            self.supervisor = BackendSupervisorAgent()
        else:
            self.supervisor = None
            logger.warning("⚠️ Backend supervisor not available")
        
        # Coordination state
        self.active_projects = {}
        self.agent_pool = {}
        self.coordination_metrics = {
            "projects_coordinated": 0,
            "tasks_delegated": 0,
            "messages_processed": 0,
            "agents_managed": 0,
            "start_time": datetime.now(timezone.utc)
        }
        
        logger.info(f"🎯 Production Supervisor Coordinator '{supervisor_id}' initialized")
        self._register_supervisor()
    
    def _initialize_azure_components(self):
        """Initialize Azure AI components if credentials are available"""
        try:
            # Check for required environment variables
            project_endpoint = os.getenv("PROJECT_ENDPOINT")
            if not project_endpoint:
                logger.warning("PROJECT_ENDPOINT not set, skipping Azure AI initialization")
                return
            
            # Initialize Azure credential and client
            credential = AzureCliCredential()
            self.project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
            
            # Initialize agent manager with project client
            self.agent_manager = AgentManager(self.project_client)
            
            logger.info("✅ Azure AI components initialized successfully")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Azure components: {e}")
            self.azure_available = False
    
    def _register_supervisor(self):
        """Register this supervisor in the messaging system"""
        try:
            # Send registration message
            registration = AgentMessage(
                message_id=f"reg_{int(time.time())}",
                from_agent=self.supervisor_id,
                to_agent=None,  # Broadcast
                message_type=MessageType.STATUS_UPDATE,
                content={
                    "action": "supervisor_registration",
                    "capabilities": [
                        "project_planning",
                        "task_coordination",
                        "agent_management",
                        "research_and_analysis"
                    ],
                    "azure_enabled": self.azure_available,
                    "max_concurrent_projects": 5
                },
                priority=MessagePriority.HIGH
            )
            
            self.queue_manager.send_message(registration)
            
            # Send heartbeat
            self._send_heartbeat()
            
        except Exception as e:
            logger.error(f"Failed to register supervisor: {e}")
    
    def coordinate_full_project(self, project_idea: str, requirements: str = "") -> Dict[str, Any]:
        """
        Coordinate a complete project from research to execution using all available capabilities.
        
        Args:
            project_idea: High-level project description
            requirements: Additional requirements and constraints
        
        Returns:
            Comprehensive coordination results
        """
        project_id = f"proj_{int(time.time())}"
        logger.info(f"🚀 Starting full project coordination: {project_id}")
        logger.info(f"📋 Project: {project_idea}")
        
        coordination_result = {
            "project_id": project_id,
            "project_idea": project_idea,
            "requirements": requirements,
            "success": False,
            "phases": {},
            "timeline": [],
            "messages_sent": [],
            "agents_involved": [],
            "start_time": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Phase 1: High-Level Planning (BackendSupervisorAgent)
            logger.info("📊 Phase 1: Strategic Planning and Research")
            planning_result = self._execute_strategic_planning(project_idea, requirements)
            coordination_result["phases"]["strategic_planning"] = planning_result
            coordination_result["timeline"].append({
                "phase": "strategic_planning",
                "status": "completed" if planning_result.get("success") else "failed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            if not planning_result.get("success"):
                coordination_result["error"] = "Strategic planning failed"
                return coordination_result
            
            # Phase 2: Task Delegation (AI Agents via Redis)
            if self.azure_available:
                logger.info("🤖 Phase 2: AI Agent Task Delegation")
                delegation_result = self._execute_agent_delegation(planning_result, project_id)
                coordination_result["phases"]["agent_delegation"] = delegation_result
                coordination_result["timeline"].append({
                    "phase": "agent_delegation",
                    "status": "completed" if delegation_result.get("success") else "failed",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                # Track agents involved
                coordination_result["agents_involved"] = delegation_result.get("agents_assigned", [])
            else:
                logger.info("⚠️ Skipping AI agent delegation (Azure not available)")
                coordination_result["phases"]["agent_delegation"] = {
                    "success": False,
                    "reason": "Azure AI not available"
                }
            
            # Phase 3: Coordination and Monitoring
            logger.info("📊 Phase 3: Coordination and Monitoring")
            monitoring_result = self._execute_coordination_monitoring(project_id)
            coordination_result["phases"]["coordination_monitoring"] = monitoring_result
            coordination_result["timeline"].append({
                "phase": "coordination_monitoring",
                "status": "completed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Phase 4: Results Integration
            logger.info("🔄 Phase 4: Results Integration")
            integration_result = self._integrate_project_results(coordination_result)
            coordination_result["phases"]["results_integration"] = integration_result
            coordination_result["timeline"].append({
                "phase": "results_integration",
                "status": "completed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            coordination_result["success"] = True
            coordination_result["end_time"] = datetime.now(timezone.utc).isoformat()
            
            # Update metrics
            self.coordination_metrics["projects_coordinated"] += 1
            
            # Store project for monitoring
            self.active_projects[project_id] = coordination_result
            
            logger.info(f"✅ Project coordination completed: {project_id}")
            
        except Exception as e:
            logger.error(f"❌ Project coordination failed: {e}")
            coordination_result["error"] = str(e)
            coordination_result["end_time"] = datetime.now(timezone.utc).isoformat()
        
        return coordination_result
    
    def _execute_strategic_planning(self, project_idea: str, requirements: str) -> Dict[str, Any]:
        """Execute strategic planning using BackendSupervisorAgent"""
        try:
            logger.info("🔍 Executing research and strategic planning...")
            
            # Use the supervisor to create comprehensive project plan
            planning_result = self.supervisor.create_detailed_issue(project_idea, requirements)
            
            if planning_result.get("success"):
                # Send planning completion message via Redis
                planning_message = AgentMessage(
                    message_id=f"planning_{int(time.time())}",
                    from_agent=self.supervisor_id,
                    to_agent=None,  # Broadcast
                    message_type=MessageType.STATUS_UPDATE,
                    content={
                        "action": "planning_completed",
                        "project_idea": project_idea,
                        "github_issue": planning_result.get("issue_url"),
                        "subtasks_count": planning_result.get("subtasks_count", 0),
                        "estimated_hours": planning_result.get("estimated_hours", 0),
                        "complexity": planning_result.get("complexity", "Medium")
                    }
                )
                
                self.queue_manager.send_message(planning_message)
                
                logger.info(f"✅ Strategic planning completed: {planning_result.get('subtasks_count', 0)} subtasks")
                
                return {
                    "success": True,
                    "planning_data": planning_result,
                    "message_sent": planning_message.message_id
                }
            else:
                return {
                    "success": False,
                    "error": "Planning failed",
                    "details": planning_result
                }
                
        except Exception as e:
            logger.error(f"Strategic planning error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_agent_delegation(self, planning_result: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Delegate tasks to Azure AI agents via Redis messaging"""
        try:
            logger.info("🤖 Delegating tasks to AI agents...")
            
            planning_data = planning_result.get("planning_data", {})
            agent_types = planning_data.get("agent_types_required", ["worker", "testing", "documentation"])
            
            delegation_result = {
                "success": True,
                "agents_assigned": [],
                "tasks_delegated": [],
                "messages_sent": []
            }
            
            # Create tasks for each required agent type
            for i, agent_type in enumerate(agent_types):
                try:
                    # Get appropriate agent
                    agent = self._get_or_create_agent(agent_type)
                    
                    if not agent:
                        logger.warning(f"Could not get agent for type: {agent_type}")
                        continue
                    
                    # Create task request as dict
                    task_request = {
                        "task_id": f"{project_id}_task_{i}",
                        "task_type": agent_type,
                        "description": f"Execute {agent_type} responsibilities for project: {planning_data.get('project_idea', 'Unknown')}",
                        "parameters": {
                            "project_id": project_id,
                            "github_issue": planning_data.get("issue_url"),
                            "complexity": planning_data.get("complexity", "Medium"),
                            "estimated_hours": planning_data.get("estimated_hours", 40) / len(agent_types),
                            "project_context": planning_result.get("planning_data", {}).get("project_idea", ""),
                            "specific_instructions": self._generate_agent_instructions(agent_type, planning_data)
                        }
                    }
                    
                    # Send task via Redis
                    task_message = AgentMessage(
                        message_id=f"task_{project_id}_{i}",
                        from_agent=self.supervisor_id,
                        to_agent=agent.agent_name if hasattr(agent, 'agent_name') else f"{agent_type}_agent",
                        message_type=MessageType.TASK_REQUEST,
                        content={"task_request": task_request},
                        priority=MessagePriority.HIGH
                    )
                    
                    success = self.queue_manager.send_message(task_message)
                    
                    if success:
                        delegation_result["agents_assigned"].append(agent_type)
                        delegation_result["tasks_delegated"].append(task_request["task_id"])
                        delegation_result["messages_sent"].append(task_message.message_id)
                        
                        self.coordination_metrics["tasks_delegated"] += 1
                        
                        logger.info(f"✅ Delegated {agent_type} task to agent")
                    else:
                        logger.error(f"❌ Failed to send task to {agent_type} agent")
                
                except Exception as e:
                    logger.error(f"Error delegating to {agent_type} agent: {e}")
            
            return delegation_result
            
        except Exception as e:
            logger.error(f"Agent delegation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_coordination_monitoring(self, project_id: str) -> Dict[str, Any]:
        """Monitor and coordinate ongoing project execution"""
        try:
            logger.info("📊 Monitoring project coordination...")
            
            monitoring_result = {
                "messages_processed": 0,
                "responses_received": 0,
                "status_updates": [],
                "active_agents": set()
            }
            
            # Check for incoming messages
            messages = self.queue_manager.get_messages(
                agent_id=self.supervisor_id,
                limit=20,
                block_ms=3000  # Wait 3 seconds for messages
            )
            
            for message in messages:
                try:
                    monitoring_result["messages_processed"] += 1
                    self.coordination_metrics["messages_processed"] += 1
                    
                    if message.message_type == MessageType.TASK_RESPONSE:
                        monitoring_result["responses_received"] += 1
                        monitoring_result["active_agents"].add(message.from_agent)
                        
                        response_content = message.content.get("task_response", {})
                        monitoring_result["status_updates"].append({
                            "agent": message.from_agent,
                            "task_id": response_content.get("task_id"),
                            "status": response_content.get("status"),
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        
                        logger.info(f"📥 Received response from {message.from_agent}")
                    
                    elif message.message_type == MessageType.STATUS_UPDATE:
                        content = message.content
                        monitoring_result["status_updates"].append({
                            "agent": message.from_agent,
                            "action": content.get("action"),
                            "details": content,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        
                        logger.info(f"📊 Status update from {message.from_agent}: {content.get('action')}")
                    
                    # Mark message as processed
                    self.queue_manager.mark_processed(message.message_id, self.supervisor_id)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
            
            monitoring_result["active_agents"] = list(monitoring_result["active_agents"])
            return monitoring_result
            
        except Exception as e:
            logger.error(f"Coordination monitoring error: {e}")
            return {
                "error": str(e),
                "messages_processed": 0
            }
    
    def _integrate_project_results(self, coordination_result: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate and summarize project coordination results"""
        try:
            logger.info("🔄 Integrating project results...")
            
            # Gather data from all phases
            planning = coordination_result.get("phases", {}).get("strategic_planning", {})
            delegation = coordination_result.get("phases", {}).get("agent_delegation", {})
            monitoring = coordination_result.get("phases", {}).get("coordination_monitoring", {})
            
            integration_summary = {
                "project_status": "coordinated",
                "planning_success": planning.get("success", False),
                "delegation_success": delegation.get("success", False),
                "total_tasks_delegated": len(delegation.get("tasks_delegated", [])),
                "total_agents_involved": len(delegation.get("agents_assigned", [])),
                "total_messages_processed": monitoring.get("messages_processed", 0),
                "responses_received": monitoring.get("responses_received", 0),
                "github_issue": planning.get("planning_data", {}).get("issue_url"),
                "completion_summary": self._generate_completion_summary(coordination_result)
            }
            
            # Send integration complete message
            integration_message = AgentMessage(
                message_id=f"integration_{int(time.time())}",
                from_agent=self.supervisor_id,
                to_agent=None,  # Broadcast
                message_type=MessageType.STATUS_UPDATE,
                content={
                    "action": "project_integration_complete",
                    "project_id": coordination_result["project_id"],
                    "integration_summary": integration_summary
                }
            )
            
            self.queue_manager.send_message(integration_message)
            
            return integration_summary
            
        except Exception as e:
            logger.error(f"Results integration error: {e}")
            return {"error": str(e)}
    
    def _get_or_create_agent(self, agent_type: str):
        """Get or create an Azure AI agent for the given type"""
        if not self.azure_available or not self.agent_manager:
            return None
        
        try:
            if agent_type == "worker":
                return self.agent_manager.get_worker_agent()
            elif agent_type == "testing":
                return self.agent_manager.get_testing_agent()
            elif agent_type == "documentation":
                return self.agent_manager.get_documentation_agent()
            elif agent_type == "research":
                return self.agent_manager.get_research_agent()
            elif agent_type == "devops":
                return self.agent_manager.get_devops_agent()
            else:
                return self.agent_manager.get_worker_agent()
        except Exception as e:
            logger.error(f"Failed to get {agent_type} agent: {e}")
            return None
    
    def _generate_agent_instructions(self, agent_type: str, planning_data: Dict[str, Any]) -> str:
        """Generate specific instructions for different agent types"""
        base_context = f"""
Project: {planning_data.get('project_idea', 'Unknown Project')}
Complexity: {planning_data.get('complexity', 'Medium')}
GitHub Issue: {planning_data.get('issue_url', 'Not available')}
Total Estimated Hours: {planning_data.get('estimated_hours', 'Unknown')}

"""
        
        if agent_type == "worker":
            return base_context + """
Your role: Implementation and Development
Focus on:
- Code architecture and implementation
- Core functionality development
- Integration between components
- Performance optimization
- Code quality and best practices

Provide detailed implementation plans and code examples."""
        
        elif agent_type == "testing":
            return base_context + """
Your role: Quality Assurance and Testing
Focus on:
- Test strategy and planning
- Unit, integration, and end-to-end testing
- Test automation setup
- Quality metrics and reporting
- Bug identification and resolution

Provide comprehensive testing frameworks and strategies."""
        
        elif agent_type == "documentation":
            return base_context + """
Your role: Documentation and Communication
Focus on:
- User documentation and guides
- API documentation
- Developer documentation
- Deployment guides
- Best practices documentation

Provide clear, comprehensive documentation plans."""
        
        elif agent_type == "devops":
            return base_context + """
Your role: DevOps and Infrastructure
Focus on:
- CI/CD pipeline setup
- Infrastructure as code
- Deployment strategies
- Monitoring and logging
- Security and compliance

Provide deployment and infrastructure guidance."""
        
        else:
            return base_context + "Provide expert guidance for your specialized domain."
    
    def _generate_completion_summary(self, coordination_result: Dict[str, Any]) -> str:
        """Generate a human-readable completion summary"""
        project_idea = coordination_result.get("project_idea", "Unknown Project")
        
        planning = coordination_result.get("phases", {}).get("strategic_planning", {})
        delegation = coordination_result.get("phases", {}).get("agent_delegation", {})
        monitoring = coordination_result.get("phases", {}).get("coordination_monitoring", {})
        
        summary = f"""
Project Coordination Summary for: {project_idea}

✅ Strategic Planning: {'Completed' if planning.get('success') else 'Failed'}
   • GitHub issue created: {planning.get('planning_data', {}).get('issue_url', 'No')}
   • Subtasks identified: {planning.get('planning_data', {}).get('subtasks_count', 0)}

🤖 Agent Delegation: {'Completed' if delegation.get('success') else 'Failed or Skipped'}
   • Agents assigned: {len(delegation.get('agents_assigned', []))}
   • Tasks delegated: {len(delegation.get('tasks_delegated', []))}

📊 Coordination Monitoring:
   • Messages processed: {monitoring.get('messages_processed', 0)}
   • Agent responses: {monitoring.get('responses_received', 0)}

The project has been successfully coordinated across multiple AI agents using Redis messaging.
All components are working together to deliver the requested solution.
"""
        return summary.strip()
    
    def _send_heartbeat(self):
        """Send coordinator heartbeat"""
        try:
            heartbeat_data = {
                "status": "active",
                "active_projects": len(self.active_projects),
                "coordination_metrics": self.coordination_metrics.copy(),
                "azure_available": self.azure_available
            }
            
            # Convert set to list for JSON serialization
            heartbeat_data["coordination_metrics"]["agents_managed"] = len(self.coordination_metrics.get("agents_managed", 0))
            
            self.queue_manager.update_agent_heartbeat(self.supervisor_id, heartbeat_data)
            
        except Exception as e:
            logger.warning(f"Failed to send heartbeat: {e}")
    
    def get_supervisor_status(self) -> Dict[str, Any]:
        """Get comprehensive supervisor status"""
        return {
            "supervisor_id": self.supervisor_id,
            "azure_available": self.azure_available,
            "active_projects": len(self.active_projects),
            "coordination_metrics": self.coordination_metrics.copy(),
            "queue_connected": self.queue_manager.is_connected(),
            "queue_stats": self.queue_manager.get_queue_stats(),
            "uptime_seconds": (datetime.now(timezone.utc) - self.coordination_metrics["start_time"]).total_seconds()
        }
    
    def cleanup(self):
        """Clean up supervisor resources"""
        try:
            logger.info("🧹 Cleaning up Production Supervisor Coordinator...")
            
            # Send final heartbeat
            self._send_heartbeat()
            
            # Cleanup agent manager
            if self.agent_manager and hasattr(self.agent_manager, 'shutdown'):
                self.agent_manager.shutdown()
            
            logger.info("✅ Production Supervisor Coordinator cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during supervisor cleanup: {e}")


def run_production_coordination_demo():
    """Run a demonstration of the production coordination system"""
    print("🎯 Production Azure AI Supervisor Coordination Demo")
    print("=" * 70)
    
    supervisor = ProductionSupervisorCoordinator("production-demo-supervisor")
    
    try:
        # Example project coordination
        project_idea = "Build a REST API for a task management system with authentication"
        requirements = """
        Requirements:
        - Use Python FastAPI framework
        - JWT authentication
        - PostgreSQL database
        - Docker containerization
        - Comprehensive testing
        - API documentation
        - CI/CD pipeline
        """
        
        print(f"📋 Project: {project_idea}")
        print(f"📝 Requirements: {requirements.strip()}")
        print()
        
        # Coordinate the project
        result = supervisor.coordinate_full_project(project_idea, requirements)
        
        if result["success"]:
            print("✅ Project coordination completed successfully!")
            print(f"🆔 Project ID: {result['project_id']}")
            print(f"🤖 Agents involved: {len(result['agents_involved'])}")
            
            # Show phase results
            phases = result.get("phases", {})
            for phase_name, phase_data in phases.items():
                status = "✅" if phase_data.get("success") else "❌"
                print(f"{status} {phase_name.replace('_', ' ').title()}")
            
            # Show timeline
            print(f"\n⏱️ Execution Timeline:")
            for event in result.get("timeline", []):
                print(f"   • {event['phase']}: {event['status']} at {event['timestamp']}")
            
            # Show GitHub integration
            planning = phases.get("strategic_planning", {})
            if planning.get("success"):
                planning_data = planning.get("planning_data", {})
                github_url = planning_data.get("issue_url")
                if github_url:
                    print(f"\n🔗 GitHub Issue: {github_url}")
                    print(f"📊 Subtasks: {planning_data.get('subtasks_count', 0)}")
                    print(f"⏱️ Estimated Hours: {planning_data.get('estimated_hours', 0)}")
            
            # Show completion summary
            integration = phases.get("results_integration", {})
            if integration.get("completion_summary"):
                print(f"\n📋 Summary:")
                print(integration["completion_summary"])
        
        else:
            print(f"❌ Project coordination failed: {result.get('error', 'Unknown error')}")
            print(f"🔍 Check phases for details: {list(result.get('phases', {}).keys())}")
        
        # Show final supervisor status
        print(f"\n📊 Supervisor Status:")
        status = supervisor.get_supervisor_status()
        metrics = status.get("coordination_metrics", {})
        print(f"   • Projects coordinated: {metrics.get('projects_coordinated', 0)}")
        print(f"   • Tasks delegated: {metrics.get('tasks_delegated', 0)}")
        print(f"   • Messages processed: {metrics.get('messages_processed', 0)}")
        print(f"   • Azure available: {status.get('azure_available', False)}")
        print(f"   • Queue connected: {status.get('queue_connected', False)}")
        print(f"   • Uptime: {status.get('uptime_seconds', 0):.1f}s")
        
    finally:
        supervisor.cleanup()
    
    print("\n🏁 Production Coordination Demo Complete!")


if __name__ == "__main__":
    run_production_coordination_demo()
