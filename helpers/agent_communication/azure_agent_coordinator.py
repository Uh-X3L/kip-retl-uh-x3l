#!/usr/bin/env python3
"""
Azure AI Agent Coordinator with Redis Messaging
===============================================

Integrates Azure AI Foundry agents with Redis messaging system to create
a sophisticated multi-agent coordination system with supervisor capabilities.
"""

import sys
import os
import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import Redis messaging system
from message_protocol import AgentMessage, MessageType, MessagePriority, TaskRequest, TaskResponse
from queue_manager import MessageQueueManager

# Import Azure AI agents
from agents.agent_manager import AgentManager
from agents.base_agent import BaseAgent

# Import backend supervisor tools
from backend_supervisor_role_tools import BackendSupervisorAgent, SubTask, ResearchResult, TaskPriority

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AzureAgentCoordinator:
    """
    Advanced coordinator that manages Azure AI Foundry agents via Redis messaging.
    Uses BackendSupervisorAgent for high-level project planning and task coordination.
    """
    
    def __init__(self, project_client, coordinator_id: str = "azure-agent-coordinator"):
        """
        Initialize the Azure Agent Coordinator.
        
        Args:
            project_client: Azure AI Projects client
            coordinator_id: Unique identifier for this coordinator
        """
        self.coordinator_id = coordinator_id
        self.project_client = project_client
        
        # Initialize Redis messaging
        try:
            self.queue_manager = MessageQueueManager(use_mock=False)
            logger.info("✅ Connected to Redis for agent coordination")
        except Exception as e:
            logger.warning(f"⚠️ Redis unavailable ({e}), using mock mode")
            self.queue_manager = MessageQueueManager(use_mock=True)
        
        # Initialize Azure AI agent manager
        self.agent_manager = AgentManager(project_client)
        
        # Initialize backend supervisor for high-level planning
        self.supervisor = BackendSupervisorAgent()
        
        # Active tasks and agent assignments
        self.active_tasks = {}
        self.agent_assignments = {}
        
        # Performance metrics
        self.coordination_stats = {
            "tasks_assigned": 0,
            "tasks_completed": 0,
            "messages_processed": 0,
            "agents_coordinated": set(),
            "start_time": datetime.now(timezone.utc)
        }
        
        logger.info(f"🎯 Azure Agent Coordinator '{coordinator_id}' initialized")
        
        # Send initial heartbeat
        self._send_heartbeat()
    
    def plan_and_coordinate_project(self, project_idea: str, requirements: str = "") -> Dict[str, Any]:
        """
        Use the supervisor to plan a project and coordinate its execution across AI agents.
        
        Args:
            project_idea: High-level project description
            requirements: Additional requirements or constraints
        
        Returns:
            Dictionary with project plan and coordination results
        """
        logger.info(f"🚀 Planning and coordinating project: {project_idea}")
        
        try:
            # Step 1: Use supervisor to research and create detailed plan
            project_plan = self.supervisor.create_detailed_issue(project_idea, requirements)
            
            if not project_plan.get("success"):
                return {
                    "success": False,
                    "error": "Failed to create project plan",
                    "details": project_plan
                }
            
            # Step 2: Parse subtasks from the plan
            subtasks = self._extract_subtasks_from_plan(project_plan)
            
            # Step 3: Assign subtasks to appropriate Azure AI agents
            coordination_results = self._coordinate_subtasks(subtasks, project_idea)
            
            # Step 4: Monitor and manage execution
            execution_results = self._monitor_execution(coordination_results)
            
            return {
                "success": True,
                "project_plan": project_plan,
                "subtasks_count": len(subtasks),
                "coordination_results": coordination_results,
                "execution_results": execution_results,
                "github_issue": project_plan.get("issue_url"),
                "estimated_hours": project_plan.get("estimated_hours", 0),
                "agents_involved": list(coordination_results.get("agent_assignments", {}).keys())
            }
            
        except Exception as e:
            logger.error(f"❌ Project coordination failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "project_idea": project_idea
            }
    
    def _extract_subtasks_from_plan(self, project_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable subtasks from supervisor's project plan"""
        
        # In a real implementation, we'd parse the GitHub issue content
        # For now, we'll simulate based on typical project structures
        subtasks = []
        
        # Get basic info from plan
        complexity = project_plan.get("complexity", "Medium")
        total_hours = project_plan.get("estimated_hours", 40)
        agent_types = project_plan.get("agent_types_required", ["worker", "testing", "documentation"])
        
        # Create representative subtasks based on the plan
        base_tasks = [
            {
                "title": "Project Setup and Architecture",
                "description": "Set up project structure, dependencies, and core architecture",
                "agent_type": "worker",
                "estimated_hours": total_hours * 0.15,
                "skills": ["architecture", "setup", "planning"],
                "priority": "high"
            },
            {
                "title": "Core Implementation",
                "description": "Implement main features and functionality",
                "agent_type": "worker", 
                "estimated_hours": total_hours * 0.5,
                "skills": ["development", "implementation"],
                "priority": "high"
            },
            {
                "title": "Testing Strategy",
                "description": "Create comprehensive test suite and validation",
                "agent_type": "testing",
                "estimated_hours": total_hours * 0.2,
                "skills": ["testing", "quality_assurance"],
                "priority": "medium"
            },
            {
                "title": "Documentation Creation",
                "description": "Create user and developer documentation",
                "agent_type": "documentation",
                "estimated_hours": total_hours * 0.15,
                "skills": ["documentation", "technical_writing"],
                "priority": "medium"
            }
        ]
        
        # Only include tasks for agent types that are required
        for task in base_tasks:
            if task["agent_type"] in agent_types:
                subtasks.append(task)
        
        logger.info(f"📋 Extracted {len(subtasks)} actionable subtasks from plan")
        return subtasks
    
    def _coordinate_subtasks(self, subtasks: List[Dict[str, Any]], project_context: str) -> Dict[str, Any]:
        """
        Coordinate subtasks by assigning them to appropriate Azure AI agents.
        """
        logger.info(f"🎯 Coordinating {len(subtasks)} subtasks across AI agents")
        
        coordination_results = {
            "agent_assignments": {},
            "task_messages": [],
            "coordination_timeline": []
        }
        
        for i, subtask in enumerate(subtasks):
            try:
                # Determine appropriate agent type
                agent_type = subtask.get("agent_type", "worker")
                
                # Get the right Azure AI agent
                agent = self._get_agent_for_task(agent_type)
                
                if not agent:
                    logger.warning(f"⚠️ No suitable agent found for task: {subtask['title']}")
                    continue
                
                # Create task request message
                task_request = TaskRequest(
                    task_id=f"task_{int(time.time())}_{i}",
                    task_type=agent_type,
                    description=f"{subtask['title']}: {subtask['description']}",
                    parameters={
                        "project_context": project_context,
                        "estimated_hours": subtask.get("estimated_hours", 4),
                        "skills_required": subtask.get("skills", []),
                        "priority": subtask.get("priority", "medium"),
                        "agent_instructions": self._create_agent_instructions(subtask, project_context)
                    }
                )
                
                # Send task via Redis messaging
                message = AgentMessage(
                    message_id=f"coord_msg_{int(time.time())}_{i}",
                    from_agent=self.coordinator_id,
                    to_agent=agent.agent_name,
                    message_type=MessageType.TASK_REQUEST,
                    content={"task_request": task_request.__dict__},
                    priority=MessagePriority.HIGH if subtask.get("priority") == "high" else MessagePriority.MEDIUM
                )
                
                success = self.queue_manager.send_message(message)
                
                if success:
                    # Track assignment
                    agent_id = agent.agent_name
                    if agent_id not in coordination_results["agent_assignments"]:
                        coordination_results["agent_assignments"][agent_id] = []
                    
                    coordination_results["agent_assignments"][agent_id].append({
                        "task_id": task_request.task_id,
                        "title": subtask["title"],
                        "estimated_hours": subtask.get("estimated_hours", 4),
                        "message_id": message.message_id,
                        "assigned_at": datetime.now(timezone.utc).isoformat()
                    })
                    
                    coordination_results["task_messages"].append(message.message_id)
                    
                    # Update stats
                    self.coordination_stats["tasks_assigned"] += 1
                    self.coordination_stats["agents_coordinated"].add(agent_id)
                    
                    logger.info(f"✅ Assigned task '{subtask['title']}' to {agent_id}")
                else:
                    logger.error(f"❌ Failed to send task '{subtask['title']}' to {agent.agent_name}")
                
            except Exception as e:
                logger.error(f"❌ Error coordinating subtask '{subtask.get('title', 'Unknown')}': {e}")
        
        coordination_results["coordination_timeline"].append({
            "action": "subtasks_assigned",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tasks_count": len(subtasks),
            "agents_involved": len(coordination_results["agent_assignments"])
        })
        
        logger.info(f"🎯 Coordination complete: {len(coordination_results['agent_assignments'])} agents assigned")
        return coordination_results
    
    def _get_agent_for_task(self, agent_type: str) -> Optional[BaseAgent]:
        """
        Get the appropriate Azure AI agent for a given task type.
        """
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
            elif agent_type == "planning":
                return self.agent_manager.get_planner_agent()
            else:
                # Default to worker agent
                return self.agent_manager.get_worker_agent()
        except Exception as e:
            logger.error(f"❌ Failed to get agent for type '{agent_type}': {e}")
            return None
    
    def _create_agent_instructions(self, subtask: Dict[str, Any], project_context: str) -> str:
        """
        Create detailed instructions for an agent based on the subtask.
        """
        instructions = f"""
Task: {subtask['title']}

Description: {subtask['description']}

Project Context: {project_context}

Requirements:
- Estimated effort: {subtask.get('estimated_hours', 4)} hours
- Skills needed: {', '.join(subtask.get('skills', []))}
- Priority: {subtask.get('priority', 'medium')}

Please provide:
1. Detailed implementation plan
2. Key considerations and dependencies
3. Potential challenges and mitigation strategies
4. Deliverables and success criteria
5. Timeline and milestones

Use your expertise to provide comprehensive guidance for this task.
"""
        return instructions.strip()
    
    def _monitor_execution(self, coordination_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor the execution of assigned tasks by processing agent responses.
        """
        logger.info("📊 Monitoring task execution...")
        
        execution_results = {
            "responses_received": 0,
            "tasks_completed": 0,
            "agents_responded": set(),
            "response_summary": [],
            "monitoring_start": datetime.now(timezone.utc).isoformat()
        }
        
        # Check for responses from agents
        try:
            # Get messages addressed to this coordinator
            messages = self.queue_manager.get_messages(
                agent_id=self.coordinator_id,
                limit=20,
                message_types=[MessageType.TASK_RESPONSE],
                block_ms=5000  # Wait up to 5 seconds for responses
            )
            
            for message in messages:
                try:
                    if message.message_type == MessageType.TASK_RESPONSE:
                        response_content = message.content
                        agent_id = message.from_agent
                        
                        execution_results["responses_received"] += 1
                        execution_results["agents_responded"].add(agent_id)
                        
                        # Process the response
                        task_response = response_content.get("task_response", {})
                        
                        response_summary = {
                            "agent_id": agent_id,
                            "task_id": task_response.get("task_id", "unknown"),
                            "status": task_response.get("status", "unknown"),
                            "execution_time": task_response.get("execution_time", 0),
                            "result_summary": str(task_response.get("result", ""))[:200],
                            "received_at": datetime.now(timezone.utc).isoformat()
                        }
                        
                        execution_results["response_summary"].append(response_summary)
                        
                        if task_response.get("status") == "completed":
                            execution_results["tasks_completed"] += 1
                            self.coordination_stats["tasks_completed"] += 1
                        
                        # Mark message as processed
                        self.queue_manager.mark_processed(
                            message.message_id,
                            self.coordinator_id,
                            "processed"
                        )
                        
                        logger.info(f"📥 Received response from {agent_id} for task {task_response.get('task_id', 'unknown')}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing response message: {e}")
            
            self.coordination_stats["messages_processed"] += len(messages)
            
        except Exception as e:
            logger.error(f"❌ Error monitoring execution: {e}")
        
        execution_results["monitoring_end"] = datetime.now(timezone.utc).isoformat()
        logger.info(f"📊 Monitoring complete: {execution_results['responses_received']} responses, {execution_results['tasks_completed']} completed")
        
        return execution_results
    
    def _send_heartbeat(self):
        """Send heartbeat to indicate coordinator is active"""
        try:
            heartbeat_info = {
                "status": "active",
                "active_tasks": len(self.active_tasks),
                "coordination_stats": {
                    **self.coordination_stats,
                    "agents_coordinated": len(self.coordination_stats["agents_coordinated"])
                }
            }
            
            self.queue_manager.update_agent_heartbeat(self.coordinator_id, heartbeat_info)
        except Exception as e:
            logger.warning(f"Failed to send heartbeat: {e}")
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the coordination system"""
        try:
            queue_stats = self.queue_manager.get_queue_stats()
            agent_status = self.agent_manager.get_agent_status()
            
            return {
                "coordinator_id": self.coordinator_id,
                "coordination_stats": {
                    **self.coordination_stats,
                    "agents_coordinated": list(self.coordination_stats["agents_coordinated"]),
                    "uptime_seconds": (datetime.now(timezone.utc) - self.coordination_stats["start_time"]).total_seconds()
                },
                "queue_stats": queue_stats,
                "azure_agent_status": agent_status,
                "active_tasks": len(self.active_tasks),
                "is_connected": self.queue_manager.is_connected()
            }
        except Exception as e:
            logger.error(f"Failed to get coordination status: {e}")
            return {"error": str(e)}
    
    def cleanup(self):
        """Clean up resources and connections"""
        try:
            logger.info("🧹 Cleaning up Azure Agent Coordinator...")
            
            # Send final heartbeat
            self._send_heartbeat()
            
            # Cleanup queue manager
            if hasattr(self.queue_manager, 'cleanup_expired_messages'):
                self.queue_manager.cleanup_expired_messages()
            
            # Cleanup agent manager
            if hasattr(self.agent_manager, 'shutdown'):
                self.agent_manager.shutdown()
            
            logger.info("✅ Azure Agent Coordinator cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


async def demonstrate_azure_coordination(project_client):
    """
    Demonstrate the Azure AI agent coordination with Redis messaging.
    """
    print("🚀 Azure AI Agent Coordination Demo")
    print("=" * 60)
    
    # Initialize coordinator
    coordinator = AzureAgentCoordinator(project_client, "demo-coordinator-001")
    
    try:
        # Example project to coordinate
        project_idea = "Create a Python web scraping tool with data visualization"
        requirements = "Use modern frameworks, include error handling, and provide comprehensive documentation"
        
        print(f"📋 Project: {project_idea}")
        print(f"📝 Requirements: {requirements}")
        print()
        
        # Plan and coordinate the project
        result = coordinator.plan_and_coordinate_project(project_idea, requirements)
        
        if result["success"]:
            print("✅ Project coordination successful!")
            print(f"📊 Subtasks: {result['subtasks_count']}")
            print(f"🤖 Agents involved: {len(result['agents_involved'])}")
            print(f"⏱️ Estimated hours: {result['estimated_hours']:.1f}")
            print(f"🔗 GitHub issue: {result.get('github_issue', 'N/A')}")
            
            # Show coordination details
            coordination = result.get("coordination_results", {})
            print(f"\n🎯 Agent Assignments:")
            for agent, tasks in coordination.get("agent_assignments", {}).items():
                print(f"   • {agent}: {len(tasks)} tasks")
                for task in tasks:
                    print(f"     - {task['title']} ({task['estimated_hours']}h)")
            
            # Show execution results
            execution = result.get("execution_results", {})
            print(f"\n📥 Execution Monitoring:")
            print(f"   • Responses received: {execution.get('responses_received', 0)}")
            print(f"   • Tasks completed: {execution.get('tasks_completed', 0)}")
            print(f"   • Agents responded: {len(execution.get('agents_responded', set()))}")
            
        else:
            print(f"❌ Project coordination failed: {result.get('error', 'Unknown error')}")
        
        # Show final status
        print(f"\n📊 Final Coordination Status:")
        status = coordinator.get_coordination_status()
        stats = status.get("coordination_stats", {})
        print(f"   • Tasks assigned: {stats.get('tasks_assigned', 0)}")
        print(f"   • Tasks completed: {stats.get('tasks_completed', 0)}")
        print(f"   • Messages processed: {stats.get('messages_processed', 0)}")
        print(f"   • Agents coordinated: {stats.get('agents_coordinated', 0)}")
        print(f"   • Uptime: {stats.get('uptime_seconds', 0):.1f}s")
        
        queue_stats = status.get("queue_stats", {})
        print(f"   • Queue mode: {queue_stats.get('mode', 'unknown')}")
        print(f"   • Queue connected: {status.get('is_connected', False)}")
        
    finally:
        # Cleanup
        coordinator.cleanup()
    
    print("\n🏁 Azure AI Agent Coordination Demo Complete!")


def run_azure_coordination_demo():
    """Entry point for running the coordination demo"""
    try:
        # Note: In a real implementation, you would initialize the Azure project client here
        # For demo purposes, we'll simulate it
        class MockProjectClient:
            def __init__(self):
                pass
        
        project_client = MockProjectClient()
        
        # Run the demonstration
        asyncio.run(demonstrate_azure_coordination(project_client))
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_azure_coordination_demo()
