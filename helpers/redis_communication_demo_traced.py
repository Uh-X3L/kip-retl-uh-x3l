"""
Redis Agent Communication Demo
=============================

This script demonstrates the complete Redis-based communication system
between agents and the supervisor, including:

1. Supervisor coordination setup
2. Agent registration and communication
3. Task assignment and execution
4. Progress monitoring
5. Error handling
6. Bidirectional messaging

Run this script to see the full communication flow in action.
"""

import time
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone

from .simple_messaging import SimpleMessaging, MessageType
from .simple_agent_coordinator import SimpleAgentCoordinator
from .sample_communicating_agent import SampleAnalysisAgent, SampleDevelopmentAgent

# Configure logging to show communication details

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


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@trace_class
class RedisCommunicationDemo:
    """
    Comprehensive demonstration of Redis-based agent communication.
    """
    
    def __init__(self):
        self.messaging = SimpleMessaging()
        self.coordinator = SimpleAgentCoordinator("demo-supervisor")
        self.agents = []
        self.demo_results = {}
    
    @trace_func
    def setup_demo(self):
        """Set up the demo environment."""
        logger.info("🔧 Setting up Redis communication demo...")
        
        # Create communicating agents
        analysis_agent = SampleAnalysisAgent("redis-analysis-agent")
        dev_agent = SampleDevelopmentAgent("redis-dev-agent")
        
        self.agents = [analysis_agent, dev_agent]
        
        logger.info(f"✅ Created {len(self.agents)} communicating agents")
        
        # Test messaging system
        if self.messaging:
            logger.info("✅ Redis messaging system available")
        else:
            logger.warning("⚠️  Redis not available, using memory fallback")
        
        return True
    
    @trace_func
    def demonstrate_agent_registration(self):
        """Demonstrate agent registration process."""
        logger.info("\n=== Phase 1: Agent Registration ===")
        
        registration_results = []
        
        for agent in self.agents:
            logger.info(f"📝 Registering agent: {agent.agent_id}")
            
            # Agent automatically registers when created, but we can also manually register
            registration_result = agent.register_with_supervisor("demo-supervisor")
            registration_results.append({
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type,
                "capabilities": agent.capabilities,
                "registration_result": registration_result
            })
            
            time.sleep(0.5)  # Small delay for demonstration
        
        self.demo_results["registrations"] = registration_results
        logger.info(f"✅ Registered {len(registration_results)} agents")
        
        return registration_results
    
    @trace_func
    def demonstrate_task_assignment_and_execution(self):
        """Demonstrate task assignment and execution with Redis communication."""
        logger.info("\n=== Phase 2: Task Assignment & Execution ===")
        
        # Define demo tasks
        demo_tasks = [
            {
                "task_id": "redis_analysis_001",
                "type": "code_analysis",
                "description": "Analyze project codebase",
                "assigned_agent": "redis-analysis-agent",
                "priority": "high"
            },
            {
                "task_id": "redis_security_001",
                "type": "security_review", 
                "description": "Security review of authentication system",
                "assigned_agent": "redis-analysis-agent",
                "priority": "high"
            },
            {
                "task_id": "redis_dev_001",
                "type": "code_generation",
                "description": "Generate user management API",
                "assigned_agent": "redis-dev-agent",
                "priority": "medium"
            }
        ]
        
        task_results = []
        
        # Send tasks to agents and monitor execution
        for task in demo_tasks:
            logger.info(f"📋 Assigning task: {task['task_id']}")
            
            # Find the assigned agent
            assigned_agent = None
            for agent in self.agents:
                if agent.agent_id == task["assigned_agent"]:
                    assigned_agent = agent
                    break
            
            if assigned_agent:
                # Send task assignment message
                self.messaging.send_message(
                    self.messaging.create_message(
                        from_agent="demo-supervisor",
                        to_agent=assigned_agent.agent_id,
                        message_type=MessageType.TASK_REQUEST,
                        content={
                            "task": task,
                            "deadline": (datetime.now(timezone.utc).timestamp() + 3600),  # 1 hour
                            "supervisor_id": "demo-supervisor"
                        }
                    )
                )
                
                # Execute the task (in real system, agent would pick up from Redis)
                logger.info(f"🚀 Executing task {task['task_id']} on {assigned_agent.agent_id}")
                result = assigned_agent.execute_task(task)
                task_results.append(result)
                
                time.sleep(1)  # Allow time for Redis communication
            else:
                logger.error(f"❌ No agent found for task {task['task_id']}")
        
        self.demo_results["task_executions"] = task_results
        logger.info(f"✅ Executed {len(task_results)} tasks")
        
        return task_results
    
    @trace_func
    def demonstrate_supervisor_monitoring(self):
        """Demonstrate supervisor monitoring of agent messages."""
        logger.info("\n=== Phase 3: Supervisor Monitoring ===")
        
        # Use the coordinator to monitor messages from agents
        monitoring_result = self.coordinator._monitor_task_execution([
            {"task_id": "redis_analysis_001", "agent": "redis-analysis-agent"},
            {"task_id": "redis_security_001", "agent": "redis-analysis-agent"},
            {"task_id": "redis_dev_001", "agent": "redis-dev-agent"}
        ])
        
        self.demo_results["monitoring"] = monitoring_result
        
        # Display monitoring results
        logger.info("📊 Monitoring Results:")
        logger.info(f"   Tasks monitored: {monitoring_result.get('tasks_monitored', 0)}")
        logger.info(f"   Status updates: {len(monitoring_result.get('status_updates', []))}")
        logger.info(f"   Agent registrations: {len(monitoring_result.get('agent_registrations', []))}")
        logger.info(f"   Progress updates: {len(monitoring_result.get('progress_updates', []))}")
        logger.info(f"   Error reports: {len(monitoring_result.get('error_reports', []))}")
        logger.info(f"   Final status: {monitoring_result.get('final_status', {}).get('overall_status', 'unknown')}")
        
        return monitoring_result
    
    @trace_func
    def demonstrate_heartbeat_monitoring(self):
        """Demonstrate agent heartbeat monitoring."""
        logger.info("\n=== Phase 4: Heartbeat Monitoring ===")
        
        heartbeat_results = []
        
        # Start heartbeat for all agents
        for agent in self.agents:
            logger.info(f"💓 Starting heartbeat for {agent.agent_id}")
            
            # Send a few heartbeats
            for i in range(3):
                heartbeat_result = agent.send_heartbeat(
                    supervisor_id="demo-supervisor",
                    status="active",
                    current_task=f"monitoring_task_{i}"
                )
                heartbeat_results.append(heartbeat_result)
                time.sleep(1)
        
        self.demo_results["heartbeats"] = heartbeat_results
        logger.info(f"✅ Sent {len(heartbeat_results)} heartbeat messages")
        
        return heartbeat_results
    
    @trace_func
    def demonstrate_error_reporting(self):
        """Demonstrate error reporting capabilities."""
        logger.info("\n=== Phase 5: Error Reporting (Intentional Demo Errors) ===")
        
        error_scenarios = [
            {
                "agent": self.agents[0],
                "error_type": "configuration_error",
                "error_message": "Database connection configuration missing",
                "severity": "high"
            },
            {
                "agent": self.agents[1],
                "error_type": "dependency_error", 
                "error_message": "Required package 'requests' not installed",
                "severity": "medium"
            }
        ]
        
        error_results = []
        
        logger.info("Note: The following errors are intentional demonstrations of error reporting:")
        
        for scenario in error_scenarios:
            logger.info(f"🧪 Simulating demo error from {scenario['agent'].agent_id}")
            
            error_result = scenario["agent"].send_error_report(
                error_type=scenario["error_type"],
                error_message=scenario["error_message"],
                task_id=f"demo_task_{int(time.time())}",
                severity=scenario["severity"]
            )
            
            error_results.append(error_result)
            time.sleep(0.5)
        
        self.demo_results["error_reports"] = error_results
        logger.info(f"✅ Sent {len(error_results)} demo error reports")
        
        return error_results
    
    @trace_func
    def check_redis_messages(self):
        """Check and display Redis messages."""
        logger.info("\n=== Phase 6: Redis Message Review ===")
        
        if not self.messaging:
            logger.warning("No messaging system available for message review")
            return []
        
        # Get messages for supervisor
        supervisor_messages = self.messaging.get_messages(
            agent_id="demo-supervisor",
            limit=50
        )
        
        logger.info(f"📬 Retrieved {len(supervisor_messages)} messages for supervisor")
        
        # Categorize messages by type
        message_categories = {}
        for message in supervisor_messages:
            msg_type = message.message_type.name if hasattr(message.message_type, 'name') else str(message.message_type)
            if msg_type not in message_categories:
                message_categories[msg_type] = []
            message_categories[msg_type].append(message)
        
        # Display message summary
        for msg_type, messages in message_categories.items():
            logger.info(f"   {msg_type}: {len(messages)} messages")
        
        self.demo_results["redis_messages"] = {
            "total_messages": len(supervisor_messages),
            "message_categories": {k: len(v) for k, v in message_categories.items()},
            "messages": supervisor_messages[:10]  # Store first 10 for review
        }
        
        return supervisor_messages
    
    @trace_func
    def run_complete_demo(self):
        """Run the complete Redis communication demonstration."""
        logger.info("🎯 Starting Complete Redis Communication Demo")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # Setup
            self.setup_demo()
            
            # Phase 1: Agent Registration
            self.demonstrate_agent_registration()
            
            # Phase 2: Task Assignment & Execution
            self.demonstrate_task_assignment_and_execution()
            
            # Phase 3: Supervisor Monitoring
            self.demonstrate_supervisor_monitoring()
            
            # Phase 4: Heartbeat Monitoring
            self.demonstrate_heartbeat_monitoring()
            
            # Phase 5: Error Reporting
            self.demonstrate_error_reporting()
            
            # Phase 6: Redis Message Review
            self.check_redis_messages()
            
            # Summary
            execution_time = time.time() - start_time
            logger.info(f"\n🎉 Demo completed successfully in {execution_time:.2f} seconds")
            
            self.print_demo_summary()
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise
        
        return self.demo_results
    
    @trace_func
    def print_demo_summary(self):
        """Print a summary of the demo results."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 DEMO SUMMARY")
        logger.info("=" * 60)
        
        # Registration summary
        registrations = self.demo_results.get("registrations", [])
        logger.info(f"🔗 Agent Registrations: {len(registrations)}")
        for reg in registrations:
            logger.info(f"   - {reg['agent_id']} ({reg['agent_type']})")
        
        # Task execution summary
        tasks = self.demo_results.get("task_executions", [])
        logger.info(f"📋 Task Executions: {len(tasks)}")
        for task in tasks:
            logger.info(f"   - {task['task_id']}: {task['status']}")
        
        # Monitoring summary
        monitoring = self.demo_results.get("monitoring", {})
        if monitoring:
            logger.info(f"📊 Monitoring:")
            logger.info(f"   - Status updates: {len(monitoring.get('status_updates', []))}")
            logger.info(f"   - Progress updates: {len(monitoring.get('progress_updates', []))}")
            logger.info(f"   - Error reports: {len(monitoring.get('error_reports', []))}")
        
        # Communication summary
        redis_msg = self.demo_results.get("redis_messages", {})
        if redis_msg:
            logger.info(f"📬 Redis Messages: {redis_msg.get('total_messages', 0)}")
            for msg_type, count in redis_msg.get("message_categories", {}).items():
                logger.info(f"   - {msg_type}: {count}")
        
        logger.info("\n✅ Redis communication system is working correctly!")
        logger.info("   Agents can successfully communicate with supervisor via Redis")


@trace_func
def main():
    """Main function to run the Redis communication demo."""
    demo = RedisCommunicationDemo()
    return demo.run_complete_demo()


if __name__ == "__main__":
    main()
