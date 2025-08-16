#!/usr/bin/env python3
"""
Working Multi-Agent Supervisor Coordination Demo
===============================================

Demonstrates the integration concept between supervisor coordination 
and multi-agent task delegation using Redis messaging.
"""

import sys
import os
import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timezone

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from message_protocol import AgentMessage, MessageType, MessagePriority
from queue_manager import MessageQueueManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MockSupervisorAgent:
    """Mock supervisor that simulates the backend supervisor role tools functionality"""
    
    def __init__(self):
        self.project_templates = {
            "rest_api": {
                "complexity": "Medium",
                "estimated_hours": 80,
                "agent_types": ["worker", "testing", "documentation", "devops"],
                "subtasks": [
                    {"title": "API Architecture Design", "agent_type": "worker", "hours": 12},
                    {"title": "Database Schema Design", "agent_type": "worker", "hours": 8},
                    {"title": "Authentication Implementation", "agent_type": "worker", "hours": 16},
                    {"title": "Core API Endpoints", "agent_type": "worker", "hours": 20},
                    {"title": "Testing Framework Setup", "agent_type": "testing", "hours": 10},
                    {"title": "API Documentation", "agent_type": "documentation", "hours": 8},
                    {"title": "CI/CD Pipeline", "agent_type": "devops", "hours": 6}
                ]
            },
            "web_scraper": {
                "complexity": "Low",
                "estimated_hours": 40,
                "agent_types": ["worker", "testing", "documentation"],
                "subtasks": [
                    {"title": "Scraper Architecture", "agent_type": "worker", "hours": 10},
                    {"title": "Data Processing Pipeline", "agent_type": "worker", "hours": 15},
                    {"title": "Visualization Components", "agent_type": "worker", "hours": 8},
                    {"title": "Test Suite Creation", "agent_type": "testing", "hours": 5},
                    {"title": "User Documentation", "agent_type": "documentation", "hours": 2}
                ]
            }
        }
    
    def create_detailed_issue(self, project_idea: str, requirements: str = "") -> Dict[str, Any]:
        """Mock project planning that simulates BackendSupervisorAgent behavior"""
        logger.info(f"🔍 Analyzing project: {project_idea}")
        
        # Simple keyword matching to determine project type
        project_type = "rest_api" if "api" in project_idea.lower() else "web_scraper"
        template = self.project_templates[project_type]
        
        # Simulate GitHub issue creation
        mock_issue_url = f"https://github.com/mock-repo/issues/{int(time.time())}"
        
        return {
            "success": True,
            "issue_url": mock_issue_url,
            "subtasks_count": len(template["subtasks"]),
            "estimated_hours": template["estimated_hours"],
            "complexity": template["complexity"],
            "agent_types_required": template["agent_types"],
            "project_template": template,
            "research_summary": f"Comprehensive analysis completed for {project_type} project"
        }


class MockAzureAgent:
    """Mock Azure AI agent that simulates Azure AI Foundry agent behavior"""
    
    def __init__(self, agent_type: str, agent_id: str):
        self.agent_type = agent_type
        self.agent_name = agent_id
        self.capabilities = {
            "worker": ["implementation", "architecture", "coding"],
            "testing": ["test_design", "quality_assurance", "automation"],
            "documentation": ["technical_writing", "user_guides", "api_docs"],
            "devops": ["infrastructure", "deployment", "monitoring"]
        }.get(agent_type, ["general"])
    
    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate processing a task and returning results"""
        logger.info(f"🤖 {self.agent_name} processing task: {task_data.get('task_id')}")
        
        # Simulate some work time
        time.sleep(0.5)
        
        return {
            "status": "completed",
            "execution_time": 0.5,
            "result": f"{self.agent_type} task completed successfully",
            "deliverables": [
                f"{self.agent_type}_plan.md",
                f"{self.agent_type}_implementation.py"
            ],
            "next_steps": f"Ready for {self.agent_type} review and integration"
        }


class WorkingSupervisorCoordinator:
    """
    Working supervisor coordinator that demonstrates the full integration concept
    """
    
    def __init__(self, supervisor_id: str = "working-supervisor-001"):
        self.supervisor_id = supervisor_id
        
        # Initialize Redis messaging
        try:
            self.queue_manager = MessageQueueManager(use_mock=False)
            logger.info("✅ Connected to Redis for coordination")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable, using mock mode")
            self.queue_manager = MessageQueueManager(use_mock=True)
        
        # Initialize mock components
        self.supervisor = MockSupervisorAgent()
        self.agent_pool = {}
        
        # Coordination metrics
        self.coordination_stats = {
            "projects_coordinated": 0,
            "tasks_delegated": 0,
            "messages_processed": 0,
            "agents_active": 0,
            "start_time": datetime.now(timezone.utc)
        }
        
        logger.info(f"🎯 Working Supervisor Coordinator '{supervisor_id}' initialized")
        self._register_supervisor()
    
    def coordinate_project_with_supervisor(self, project_idea: str, requirements: str = "") -> Dict[str, Any]:
        """
        Demonstrate full project coordination workflow using supervisor + agents + Redis
        """
        project_id = f"coord_proj_{int(time.time())}"
        logger.info(f"🚀 Coordinating project: {project_id}")
        
        coordination_result = {
            "project_id": project_id,
            "project_idea": project_idea,
            "success": False,
            "phases": {},
            "coordination_flow": [],
            "messages_exchanged": [],
            "agents_involved": {}
        }
        
        try:
            # Phase 1: Supervisor Planning
            logger.info("📊 Phase 1: Supervisor Strategic Planning")
            planning_result = self.supervisor.create_detailed_issue(project_idea, requirements)
            coordination_result["phases"]["supervisor_planning"] = planning_result
            
            self._log_coordination_step(coordination_result, "supervisor_planning_complete", {
                "github_issue": planning_result.get("issue_url"),
                "subtasks_identified": planning_result.get("subtasks_count", 0)
            })
            
            if not planning_result.get("success"):
                coordination_result["error"] = "Supervisor planning failed"
                return coordination_result
            
            # Phase 2: Agent Provisioning and Task Delegation
            logger.info("🤖 Phase 2: Agent Provisioning and Task Delegation")
            delegation_result = self._provision_and_delegate_agents(planning_result, project_id)
            coordination_result["phases"]["agent_delegation"] = delegation_result
            coordination_result["agents_involved"] = delegation_result.get("agents_created", {})
            
            self._log_coordination_step(coordination_result, "agents_delegated", {
                "agents_count": len(delegation_result.get("agents_created", {})),
                "tasks_sent": len(delegation_result.get("messages_sent", []))
            })
            
            # Phase 3: Agent Coordination and Execution
            logger.info("⚡ Phase 3: Agent Execution and Coordination")
            execution_result = self._coordinate_agent_execution(delegation_result, project_id)
            coordination_result["phases"]["agent_execution"] = execution_result
            
            self._log_coordination_step(coordination_result, "execution_coordinated", {
                "responses_received": execution_result.get("responses_received", 0),
                "tasks_completed": execution_result.get("tasks_completed", 0)
            })
            
            # Phase 4: Results Integration
            logger.info("🔄 Phase 4: Results Integration and Reporting")
            integration_result = self._integrate_and_report_results(coordination_result)
            coordination_result["phases"]["results_integration"] = integration_result
            
            self._log_coordination_step(coordination_result, "results_integrated", {
                "final_deliverables": len(integration_result.get("deliverables", [])),
                "project_status": integration_result.get("status", "unknown")
            })
            
            coordination_result["success"] = True
            self.coordination_stats["projects_coordinated"] += 1
            
            logger.info(f"✅ Project coordination completed successfully: {project_id}")
            
        except Exception as e:
            logger.error(f"❌ Project coordination failed: {e}")
            coordination_result["error"] = str(e)
        
        return coordination_result
    
    def _provision_and_delegate_agents(self, planning_result: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Provision AI agents and delegate tasks via Redis messaging"""
        
        template = planning_result.get("project_template", {})
        agent_types = template.get("agent_types", [])
        subtasks = template.get("subtasks", [])
        
        delegation_result = {
            "agents_created": {},
            "tasks_delegated": [],
            "messages_sent": []
        }
        
        # Create agents for each required type
        for agent_type in agent_types:
            agent_id = f"{agent_type}_agent_{project_id}"
            agent = MockAzureAgent(agent_type, agent_id)
            self.agent_pool[agent_id] = agent
            delegation_result["agents_created"][agent_id] = {
                "type": agent_type,
                "capabilities": agent.capabilities
            }
            
            logger.info(f"🤖 Created {agent_type} agent: {agent_id}")
        
        # Delegate tasks to appropriate agents
        for i, subtask in enumerate(subtasks):
            agent_type = subtask["agent_type"]
            
            # Find appropriate agent
            target_agent = None
            for agent_id, agent in self.agent_pool.items():
                if agent.agent_type == agent_type:
                    target_agent = agent
                    break
            
            if not target_agent:
                logger.warning(f"No agent available for {agent_type} task")
                continue
            
            # Create task message
            task_data = {
                "task_id": f"{project_id}_task_{i}",
                "title": subtask["title"],
                "agent_type": agent_type,
                "estimated_hours": subtask["hours"],
                "project_context": planning_result.get("project_idea", ""),
                "github_issue": planning_result.get("issue_url"),
                "specific_requirements": self._generate_task_requirements(subtask)
            }
            
            # Send via Redis messaging
            task_message = AgentMessage(
                message_id=f"task_msg_{project_id}_{i}",
                from_agent=self.supervisor_id,
                to_agent=target_agent.agent_name,
                message_type=MessageType.TASK_REQUEST,
                content={"task_data": task_data},
                priority=MessagePriority.HIGH
            )
            
            success = self.queue_manager.send_message(task_message)
            
            if success:
                delegation_result["tasks_delegated"].append(task_data)
                delegation_result["messages_sent"].append(task_message.message_id)
                self.coordination_stats["tasks_delegated"] += 1
                
                logger.info(f"📨 Delegated task '{subtask['title']}' to {target_agent.agent_name}")
        
        self.coordination_stats["agents_active"] = len(delegation_result["agents_created"])
        return delegation_result
    
    def _coordinate_agent_execution(self, delegation_result: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Coordinate agent execution and collect responses"""
        
        execution_result = {
            "responses_received": 0,
            "tasks_completed": 0,
            "agent_results": {},
            "coordination_messages": []
        }
        
        # Simulate agents processing tasks and sending responses
        for task_data in delegation_result.get("tasks_delegated", []):
            task_id = task_data["task_id"]
            
            # Find the agent assigned to this task
            assigned_agent = None
            for agent_id, agent in self.agent_pool.items():
                if agent.agent_type == task_data["agent_type"]:
                    assigned_agent = agent
                    break
            
            if not assigned_agent:
                continue
            
            # Simulate agent processing
            task_result = assigned_agent.process_task(task_data)
            
            # Send response back via Redis
            response_message = AgentMessage(
                message_id=f"response_{task_id}",
                from_agent=assigned_agent.agent_name,
                to_agent=self.supervisor_id,
                message_type=MessageType.TASK_RESPONSE,
                content={
                    "task_id": task_id,
                    "task_response": task_result
                },
                priority=MessagePriority.MEDIUM
            )
            
            self.queue_manager.send_message(response_message)
            
            execution_result["agent_results"][assigned_agent.agent_name] = task_result
            execution_result["responses_received"] += 1
            
            if task_result.get("status") == "completed":
                execution_result["tasks_completed"] += 1
            
            logger.info(f"📥 Received response from {assigned_agent.agent_name}")
        
        # Check for incoming messages (responses)
        messages = self.queue_manager.get_messages(
            agent_id=self.supervisor_id,
            limit=20,
            message_types=[MessageType.TASK_RESPONSE],
            block_ms=2000
        )
        
        for message in messages:
            self.coordination_stats["messages_processed"] += 1
            execution_result["coordination_messages"].append({
                "from": message.from_agent,
                "type": message.message_type.value,
                "received_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Mark as processed
            self.queue_manager.mark_processed(message.message_id, self.supervisor_id)
        
        return execution_result
    
    def _integrate_and_report_results(self, coordination_result: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate results from all phases and create final report"""
        
        planning = coordination_result.get("phases", {}).get("supervisor_planning", {})
        delegation = coordination_result.get("phases", {}).get("agent_delegation", {})
        execution = coordination_result.get("phases", {}).get("agent_execution", {})
        
        integration_result = {
            "status": "success",
            "deliverables": [],
            "project_summary": {},
            "coordination_metrics": self.coordination_stats.copy(),
            "final_report": ""
        }
        
        # Collect deliverables from all agents
        for agent_result in execution.get("agent_results", {}).values():
            deliverables = agent_result.get("deliverables", [])
            integration_result["deliverables"].extend(deliverables)
        
        # Create project summary
        integration_result["project_summary"] = {
            "github_issue": planning.get("issue_url"),
            "total_subtasks": planning.get("subtasks_count", 0),
            "agents_deployed": len(delegation.get("agents_created", {})),
            "tasks_completed": execution.get("tasks_completed", 0),
            "total_deliverables": len(integration_result["deliverables"]),
            "project_complexity": planning.get("complexity", "Unknown"),
            "estimated_vs_actual": {
                "estimated_hours": planning.get("estimated_hours", 0),
                "coordination_time": (datetime.now(timezone.utc) - self.coordination_stats["start_time"]).total_seconds()
            }
        }
        
        # Generate final report
        integration_result["final_report"] = self._generate_final_report(coordination_result, integration_result)
        
        # Send completion notification
        completion_message = AgentMessage(
            message_id=f"completion_{int(time.time())}",
            from_agent=self.supervisor_id,
            to_agent=None,  # Broadcast
            message_type=MessageType.COMPLETION,
            content={
                "project_id": coordination_result["project_id"],
                "status": "completed",
                "summary": integration_result["project_summary"]
            },
            priority=MessagePriority.HIGH
        )
        
        self.queue_manager.send_message(completion_message)
        
        return integration_result
    
    def _generate_task_requirements(self, subtask: Dict[str, Any]) -> str:
        """Generate detailed requirements for a specific subtask"""
        requirements = f"""
Task: {subtask['title']}
Type: {subtask['agent_type']}
Estimated Effort: {subtask['hours']} hours

Requirements:
- Follow best practices for {subtask['agent_type']} tasks
- Ensure compatibility with overall project architecture
- Document all decisions and implementations
- Provide clear deliverables and next steps

Expected Deliverables:
- Implementation plan or code
- Documentation
- Test cases (if applicable)
- Integration guidelines
"""
        return requirements.strip()
    
    def _generate_final_report(self, coordination_result: Dict[str, Any], integration_result: Dict[str, Any]) -> str:
        """Generate comprehensive final report"""
        
        project_idea = coordination_result["project_idea"]
        summary = integration_result["project_summary"]
        metrics = integration_result["coordination_metrics"]
        
        report = f"""
# Project Coordination Report: {project_idea}

## 📊 Project Overview
- **GitHub Issue**: {summary.get('github_issue', 'N/A')}
- **Project Complexity**: {summary.get('project_complexity', 'Unknown')}
- **Total Subtasks**: {summary.get('total_subtasks', 0)}

## 🤖 Agent Coordination
- **Agents Deployed**: {summary.get('agents_deployed', 0)}
- **Tasks Completed**: {summary.get('tasks_completed', 0)}
- **Total Deliverables**: {summary.get('total_deliverables', 0)}

## 📈 Coordination Metrics
- **Projects Coordinated**: {metrics.get('projects_coordinated', 0)}
- **Tasks Delegated**: {metrics.get('tasks_delegated', 0)}
- **Messages Processed**: {metrics.get('messages_processed', 0)}
- **Active Agents**: {metrics.get('agents_active', 0)}

## 🔄 Coordination Flow
"""
        
        for step in coordination_result.get("coordination_flow", []):
            report += f"- **{step['action']}**: {step.get('details', {})}\n"
        
        report += f"""
## ✅ Project Status: {integration_result['status'].upper()}

This project was successfully coordinated using the integrated supervisor + multi-agent system with Redis messaging.
The BackendSupervisorAgent handled strategic planning, while specialized AI agents executed specific tasks
through coordinated Redis messaging channels.
"""
        
        return report.strip()
    
    def _log_coordination_step(self, coordination_result: Dict[str, Any], action: str, details: Dict[str, Any]):
        """Log coordination steps for tracking"""
        step = {
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details
        }
        
        if "coordination_flow" not in coordination_result:
            coordination_result["coordination_flow"] = []
        
        coordination_result["coordination_flow"].append(step)
        logger.info(f"📋 Coordination step: {action}")
    
    def _register_supervisor(self):
        """Register supervisor in the messaging system"""
        registration = AgentMessage(
            message_id=f"supervisor_reg_{int(time.time())}",
            from_agent=self.supervisor_id,
            to_agent=None,
            message_type=MessageType.STATUS_UPDATE,
            content={
                "action": "supervisor_registration",
                "capabilities": ["strategic_planning", "task_coordination", "project_management"],
                "max_concurrent_projects": 10
            }
        )
        
        self.queue_manager.send_message(registration)
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get comprehensive coordination status"""
        return {
            "supervisor_id": self.supervisor_id,
            "coordination_stats": self.coordination_stats.copy(),
            "active_agents": len(self.agent_pool),
            "queue_connected": self.queue_manager.is_connected(),
            "queue_stats": self.queue_manager.get_queue_stats()
        }


def demonstrate_supervisor_coordination():
    """Demonstrate the working supervisor coordination system"""
    
    print("🎯 Working Multi-Agent Supervisor Coordination Demo")
    print("=" * 70)
    print("🔧 Integration: BackendSupervisorAgent + Azure AI Agents + Redis Messaging")
    print()
    
    # Initialize coordinator
    coordinator = WorkingSupervisorCoordinator("demo-supervisor-001")
    
    try:
        # Example project
        project_idea = "Build a modern Python REST API with FastAPI"
        requirements = """
        Requirements:
        - FastAPI framework with async support
        - JWT authentication and authorization
        - PostgreSQL database with SQLAlchemy ORM
        - Docker containerization
        - Comprehensive testing (unit + integration)
        - OpenAPI documentation
        - CI/CD pipeline with GitHub Actions
        """
        
        print(f"📋 Project: {project_idea}")
        print(f"📝 Requirements: {requirements.strip()}")
        print()
        
        # Demonstrate full coordination
        result = coordinator.coordinate_project_with_supervisor(project_idea, requirements)
        
        if result["success"]:
            print("✅ Project coordination completed successfully!")
            print(f"🆔 Project ID: {result['project_id']}")
            
            # Show phase results
            phases = result.get("phases", {})
            print(f"\n🔄 Coordination Phases:")
            for phase_name, phase_data in phases.items():
                status = "✅" if phase_data.get("success", True) else "❌"
                print(f"  {status} {phase_name.replace('_', ' ').title()}")
            
            # Show agent involvement
            agents = result.get("agents_involved", {})
            print(f"\n🤖 Agents Involved ({len(agents)}):")
            for agent_id, agent_info in agents.items():
                print(f"  • {agent_id} ({agent_info['type']}) - {agent_info['capabilities']}")
            
            # Show coordination flow
            flow = result.get("coordination_flow", [])
            print(f"\n📊 Coordination Flow ({len(flow)} steps):")
            for step in flow:
                print(f"  • {step['action']}: {step.get('details', {})}")
            
            # Show final integration results
            integration = phases.get("results_integration", {})
            if integration:
                summary = integration.get("project_summary", {})
                print(f"\n📈 Project Summary:")
                print(f"  • GitHub Issue: {summary.get('github_issue', 'N/A')}")
                print(f"  • Total Subtasks: {summary.get('total_subtasks', 0)}")
                print(f"  • Agents Deployed: {summary.get('agents_deployed', 0)}")
                print(f"  • Tasks Completed: {summary.get('tasks_completed', 0)}")
                print(f"  • Deliverables: {summary.get('total_deliverables', 0)}")
                
                # Show final report excerpt
                final_report = integration.get("final_report", "")
                if final_report:
                    lines = final_report.split('\n')[:15]  # First 15 lines
                    print(f"\n📋 Final Report (excerpt):")
                    for line in lines:
                        if line.strip():
                            print(f"  {line}")
                    if len(final_report.split('\n')) > 15:
                        print(f"  ... (full report available)")
        
        else:
            print(f"❌ Project coordination failed: {result.get('error', 'Unknown error')}")
        
        # Show final coordinator status
        print(f"\n📊 Coordinator Status:")
        status = coordinator.get_coordination_status()
        stats = status.get("coordination_stats", {})
        print(f"  • Projects coordinated: {stats.get('projects_coordinated', 0)}")
        print(f"  • Tasks delegated: {stats.get('tasks_delegated', 0)}")
        print(f"  • Messages processed: {stats.get('messages_processed', 0)}")
        print(f"  • Active agents: {status.get('active_agents', 0)}")
        print(f"  • Queue connected: {status.get('queue_connected', False)}")
        
        queue_stats = status.get("queue_stats", {})
        if queue_stats:
            print(f"  • Queue mode: {queue_stats.get('mode', 'unknown')}")
            if queue_stats.get('mode') == 'redis':
                print(f"  • Messages in queue: {queue_stats.get('message_stream_length', 0)}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🏁 Multi-Agent Supervisor Coordination Demo Complete!")
    print("🎯 This demonstrates the integration of:")
    print("   • BackendSupervisorAgent for strategic planning")
    print("   • Azure AI agents for specialized task execution")
    print("   • Redis messaging for coordinated communication")
    print("   • Complete project lifecycle management")


if __name__ == "__main__":
    demonstrate_supervisor_coordination()
