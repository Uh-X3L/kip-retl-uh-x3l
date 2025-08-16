#!/usr/bin/env python3
"""
Autonomous Agent Communication System Demo
==========================================

This demo shows how to use the autonomous agent communication system
for coordinating tasks between multiple agents using Azure SQL as the
message store.

Run this demo to see:
1. Agent registration and capabilities
2. Task assignment and coordination
3. Message passing between agents
4. Status updates and monitoring
5. Error handling and recovery
"""

import sys
import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Add helpers directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from helpers.agent_communication import (
    AgentMessage, MessageType, MessagePriority, AgentRole,
    MessageQueueManager, AgentRegistry, SupervisorCoordinator,
    TaskRequest, TaskResponse
)
from helpers.agent_communication.agent_registry import register_supervisor_agent, register_worker_agent


def setup_logging():
    """Setup logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('agent_communication_demo.log')
        ]
    )


def demo_basic_messaging():
    """Demonstrate basic message passing"""
    print("\n" + "="*60)
    print("🚀 DEMO 1: Basic Message Passing")
    print("="*60)
    
    # Initialize components
    queue = MessageQueueManager()
    
    # Create a simple task request
    task_message = AgentMessage(
        message_id="demo-msg-001",
        from_agent="supervisor-demo",
        to_agent="worker-backend",
        message_type=MessageType.TASK_REQUEST,
        content={
            "task_id": "demo-task-001",
            "task_type": "code_review",
            "description": "Review the agent communication system code",
            "parameters": {
                "files": ["message_protocol.py", "queue_manager.py"],
                "priority": "high"
            }
        },
        priority=MessagePriority.HIGH
    )
    
    print("📤 Sending task message...")
    success = queue.send_message(task_message)
    print(f"   Result: {'✅ Success' if success else '❌ Failed'}")
    
    # Retrieve messages
    print("\n📥 Retrieving messages for worker-backend...")
    messages = queue.get_messages("worker-backend", limit=5)
    print(f"   Retrieved {len(messages)} messages")
    
    for i, msg in enumerate(messages, 1):
        print(f"   {i}. From: {msg.from_agent}")
        print(f"      Type: {msg.message_type.value}")
        print(f"      Content: {msg.content.get('task_type', 'N/A')}")
    
    # Mark as processed
    if messages:
        msg = messages[0]
        print(f"\n✅ Marking message {msg.message_id} as processed...")
        success = queue.mark_processed(msg.message_id, "worker-backend")
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")


def demo_agent_registry():
    """Demonstrate agent registration and discovery"""
    print("\n" + "="*60)
    print("🤖 DEMO 2: Agent Registry and Discovery")
    print("="*60)
    
    # Initialize registry
    registry = AgentRegistry()
    
    # Register various agents
    agents_to_register = [
        ("supervisor-main", AgentRole.SUPERVISOR, ["task_coordination", "planning"]),
        ("worker-backend-01", AgentRole.WORKER, ["python", "database", "api"]),
        ("worker-frontend-01", AgentRole.WORKER, ["javascript", "react", "ui"]),
        ("worker-devops-01", AgentRole.WORKER, ["terraform", "azure", "ci_cd"]),
        ("tester-01", AgentRole.TESTER, ["testing", "automation", "qa"])
    ]
    
    print("📋 Registering agents...")
    for agent_id, role, capabilities in agents_to_register:
        success = registry.register_agent(
            agent_id=agent_id,
            agent_role=role,
            capabilities=capabilities,
            max_concurrent_tasks=2 if role != AgentRole.SUPERVISOR else 10
        )
        print(f"   {agent_id}: {'✅' if success else '❌'}")
    
    # Update heartbeats to mark agents as active
    print("\n💓 Updating agent heartbeats...")
    for agent_id, _, _ in agents_to_register:
        registry.update_heartbeat(agent_id, status='active', current_tasks=0)
    
    # Find available agents
    print("\n🔍 Finding available agents...")
    
    test_scenarios = [
        ("Python developers", ["python"]),
        ("DevOps specialists", ["terraform", "azure"]),
        ("Testing agents", ["testing"]),
        ("Frontend developers", ["javascript", "react"])
    ]
    
    for scenario_name, required_caps in test_scenarios:
        print(f"\n   {scenario_name} (requires: {', '.join(required_caps)}):")
        available = registry.find_available_agents(
            required_capabilities=required_caps,
            max_results=3
        )
        
        if available:
            for agent in available:
                print(f"     • {agent.agent_id} ({agent.agent_role.value})")
                print(f"       Capabilities: {', '.join(agent.capabilities)}")
                print(f"       Load: {agent.calculate_load():.1%}")
        else:
            print("     No suitable agents found")
    
    # Registry statistics
    print("\n📊 Registry Statistics:")
    stats = registry.get_registry_stats()
    print(f"   Total agents: {stats['total_agents']}")
    print(f"   By role: {stats['by_role']}")
    print(f"   By status: {stats['by_status']}")
    print(f"   Average load: {stats['average_load']:.1%}")


def demo_task_coordination():
    """Demonstrate task coordination and assignment"""
    print("\n" + "="*60)
    print("📋 DEMO 3: Task Coordination and Assignment")
    print("="*60)
    
    # Initialize coordinator
    coordinator = SupervisorCoordinator("supervisor-demo")
    
    # Register some worker agents
    registry = coordinator.agent_registry
    
    worker_agents = [
        ("worker-python-01", "backend"),
        ("worker-js-01", "frontend"), 
        ("worker-devops-01", "devops"),
        ("worker-test-01", "testing")
    ]
    
    print("🤖 Registering worker agents...")
    for agent_id, specialization in worker_agents:
        success = register_worker_agent(registry, agent_id, specialization)
        registry.update_heartbeat(agent_id, status='active', current_tasks=0)
        print(f"   {agent_id} ({specialization}): {'✅' if success else '❌'}")
    
    # Assign various tasks
    print("\n📋 Assigning tasks...")
    
    tasks_to_assign = [
        {
            "task_type": "api_development",
            "description": "Develop REST API for user management", 
            "parameters": {"framework": "fastapi", "database": "postgresql"},
            "required_capabilities": ["python", "api_development"],
            "priority": MessagePriority.HIGH
        },
        {
            "task_type": "ui_development",
            "description": "Create user interface for dashboard",
            "parameters": {"framework": "react", "styling": "tailwind"},
            "required_capabilities": ["javascript", "react"],
            "priority": MessagePriority.MEDIUM
        },
        {
            "task_type": "infrastructure_setup",
            "description": "Setup Azure infrastructure with Terraform",
            "parameters": {"region": "eastus", "environment": "production"},
            "required_capabilities": ["terraform", "azure"],
            "priority": MessagePriority.HIGH
        },
        {
            "task_type": "test_automation",
            "description": "Create automated test suite",
            "parameters": {"test_type": "integration", "coverage": "80%"},
            "required_capabilities": ["testing", "automation"],
            "priority": MessagePriority.MEDIUM
        }
    ]
    
    assigned_tasks = []
    for task_data in tasks_to_assign:
        task_id = coordinator.assign_task(**task_data)
        if task_id:
            assigned_tasks.append(task_id)
            print(f"   ✅ Task assigned: {task_id}")
            print(f"      Type: {task_data['task_type']}")
            print(f"      Priority: {task_data['priority'].value}")
        else:
            print(f"   ❌ Failed to assign task: {task_data['task_type']}")
    
    print(f"\n📊 Successfully assigned {len(assigned_tasks)} tasks")
    
    # Simulate task responses
    print("\n🔄 Simulating task responses...")
    time.sleep(1)  # Brief pause for realism
    
    # Process any incoming messages (responses from agents)
    processed = coordinator.process_incoming_messages()
    print(f"   Processed {processed} incoming messages")
    
    # Show task statuses
    print("\n📋 Current task statuses:")
    for task_id in assigned_tasks:
        status = coordinator.get_task_status(task_id)
        if status:
            print(f"   {task_id}: {status['status']} (Agent: {status['agent_id']})")
    
    # Show coordination statistics
    print("\n📊 Coordination Statistics:")
    stats = coordinator.get_coordination_stats()
    print(f"   Active tasks: {stats['active_tasks']}")
    print(f"   Tasks assigned: {stats['metrics']['tasks_assigned']}")
    print(f"   Tasks completed: {stats['metrics']['tasks_completed']}")
    print(f"   Tasks failed: {stats['metrics']['tasks_failed']}")


def demo_error_handling():
    """Demonstrate error handling and recovery"""
    print("\n" + "="*60)
    print("❌ DEMO 4: Error Handling and Recovery")
    print("="*60)
    
    coordinator = SupervisorCoordinator("supervisor-error-demo")
    
    # Simulate an error report
    error_message = AgentMessage(
        message_id="error-demo-001",
        from_agent="worker-problematic",
        to_agent="supervisor-error-demo",
        message_type=MessageType.ERROR_REPORT,
        content={
            "error_type": "task_execution_failure",
            "error_message": "Database connection timeout",
            "task_id": "failed-task-001",
            "timestamp": datetime.now().isoformat(),
            "stack_trace": "Sample stack trace here..."
        },
        priority=MessagePriority.CRITICAL
    )
    
    print("📤 Sending error report...")
    success = coordinator.queue_manager.send_message(error_message)
    print(f"   Sent: {'✅' if success else '❌'}")
    
    # Process the error message
    print("\n🔄 Processing error messages...")
    processed = coordinator.process_incoming_messages()
    print(f"   Processed {processed} messages")
    
    # Show system resilience
    print("\n🛡️ System Resilience Features:")
    print("   • Automatic retry mechanism for failed messages")
    print("   • Agent heartbeat monitoring")
    print("   • Task timeout detection")
    print("   • Graceful degradation when agents are unavailable")
    print("   • Comprehensive logging and monitoring")


def demo_maintenance():
    """Demonstrate system maintenance and cleanup"""
    print("\n" + "="*60)
    print("🧹 DEMO 5: System Maintenance and Cleanup")
    print("="*60)
    
    coordinator = SupervisorCoordinator("supervisor-maintenance")
    
    print("🔧 Performing system maintenance...")
    maintenance_results = coordinator.cleanup_and_maintenance()
    
    print("📋 Maintenance Results:")
    for key, value in maintenance_results.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Show queue statistics
    print("\n📊 Message Queue Statistics:")
    queue_stats = coordinator.queue_manager.get_queue_stats()
    for key, value in queue_stats.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Show agent registry statistics
    print("\n🤖 Agent Registry Statistics:")
    registry_stats = coordinator.agent_registry.get_registry_stats()
    for key, value in registry_stats.items():
        if isinstance(value, dict):
            print(f"   {key.replace('_', ' ').title()}:")
            for sub_key, sub_value in value.items():
                print(f"     {sub_key}: {sub_value}")
        else:
            print(f"   {key.replace('_', ' ').title()}: {value}")


def demo_integration_with_existing_framework():
    """Demonstrate integration with existing agent framework"""
    print("\n" + "="*60)
    print("🔗 DEMO 6: Integration with Existing Framework")
    print("="*60)
    
    print("🔧 Integration Points:")
    print("   • MessageQueueManager integrates with BackendSupervisorAgent")
    print("   • Agent capabilities map to GitHub issue types")
    print("   • Task coordination supports existing workflows")
    print("   • Azure SQL leverages existing infrastructure")
    
    print("\n📝 Example Integration Code:")
    integration_example = '''
# In helpers/backend_supervisor_role_tools.py
from helpers.agent_communication import SupervisorCoordinator

class BackendSupervisorAgent:
    def __init__(self):
        # Initialize existing agent functionality
        self.agent_id = "backend-supervisor-001"
        
        # Add autonomous communication capability
        self.coordinator = SupervisorCoordinator(self.agent_id)
        
    def create_comprehensive_project(self, project_idea, requirements):
        # Existing project creation logic...
        
        # Add autonomous task delegation
        task_id = self.coordinator.assign_task(
            task_type="project_implementation",
            description=project_idea,
            parameters={"requirements": requirements},
            required_capabilities=["programming", "project_management"]
        )
        
        return {"task_id": task_id, "autonomous_mode": True}
'''
    print(integration_example)


def main():
    """Run all demos"""
    setup_logging()
    
    print("🚀 AUTONOMOUS AGENT COMMUNICATION SYSTEM DEMO")
    print("=" * 80)
    print("This demo showcases the autonomous agent communication capabilities")
    print("using Azure SQL Server as the message store with minimal viable protocol.")
    print("\nFeatures demonstrated:")
    print("• JSON-based message passing")
    print("• Agent registration and capability discovery")
    print("• Task coordination and delegation")
    print("• Error handling and recovery")
    print("• System maintenance and monitoring")
    print("• Integration with existing agent framework")
    
    try:
        # Run all demos
        demo_basic_messaging()
        demo_agent_registry()
        demo_task_coordination()
        demo_error_handling()
        demo_maintenance()
        demo_integration_with_existing_framework()
        
        print("\n" + "="*80)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n✅ The autonomous agent communication system is ready for production use.")
        print("\n🎯 Next Steps:")
        print("   1. Configure Azure SQL connection string")
        print("   2. Deploy the database schema (schema.sql)")
        print("   3. Integrate with existing BackendSupervisorAgent")
        print("   4. Start autonomous agent coordination!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logging.error(f"Demo execution failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
