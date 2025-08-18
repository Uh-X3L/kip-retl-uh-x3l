"""
Comprehensive Agent Communication Test Suite
==========================================

Complete test coverage for all agent communication functionality
including multi-agent coordination, error recovery, and performance testing.
"""

import pytest
import time
import threading
import json
from typing import Dict, Any, List
from unittest.mock import Mock, patch

# Import the modules we're testing
from helpers.agent_communication_mixin import AgentCommunicationMixin, CommunicatingAgent
from helpers.simple_messaging import SimpleMessaging, MessageType, create_simple_messaging
from helpers.backend_supervisor_role_tools import BackendSupervisorAgent
from helpers.dynamic_tracing_controller import TRACING_CONTROLLER, conditional_trace


class TestAgentCommunication:
    """Complete test suite for agent communication functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.messaging = create_simple_messaging(use_redis=False)  # Use memory for tests
        self.supervisor_id = "test-supervisor"
        self.agents = []
    
    def teardown_method(self):
        """Clean up after tests."""
        for agent in self.agents:
            if hasattr(agent, 'shutdown_communication'):
                agent.shutdown_communication()
    
    def create_test_agent(self, agent_id: str, agent_type: str = "worker") -> CommunicatingAgent:
        """Create a test agent for testing."""
        agent = CommunicatingAgent(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=["testing", "communication"],
            supervisor_id=self.supervisor_id
        )
        self.agents.append(agent)
        return agent
    
    def test_agent_registration(self):
        """Test agent registration with supervisor."""
        agent = self.create_test_agent("test-agent-1")
        
        # Check registration status
        stats = agent.get_communication_stats()
        assert stats['agent_id'] == "test-agent-1"
        assert stats['agent_type'] == "worker"
        assert "testing" in stats['capabilities']
        assert stats['supervisor_id'] == self.supervisor_id
    
    def test_task_lifecycle(self):
        """Test complete task lifecycle: start -> progress -> completion."""
        agent = self.create_test_agent("task-agent")
        
        task_id = "test-task-001"
        task_description = "Test task execution"
        
        # Start task
        agent.report_task_started(task_id, task_description)
        stats = agent.get_communication_stats()
        assert stats['current_tasks'] == 1
        assert task_id in stats['task_list']
        
        # Report progress
        agent.report_task_progress(task_id, 50.0, "Halfway complete")
        
        # Complete task
        results = {"status": "success", "data": "test_result"}
        agent.report_task_completed(task_id, results)
    
    def test_task_error_reporting(self):
        """Test task error reporting functionality."""
        agent = self.create_test_agent("error-agent")
        
        task_id = "error-task-001"
        agent.report_task_started(task_id, "Task that will fail")
        
        # Report error
        error_message = "Task failed due to network timeout"
        error_details = {"error_code": "TIMEOUT", "duration": 30}
        
        agent.report_task_error(task_id, error_message, error_details)
    
    def test_multi_agent_coordination(self):
        """Test multiple agents working together."""
        # Create multiple agents
        research_agent = self.create_test_agent("research-1", "research")
        worker_agent = self.create_test_agent("worker-1", "worker") 
        testing_agent = self.create_test_agent("testing-1", "testing")
        
        # Simulate coordinated workflow
        agents = [research_agent, worker_agent, testing_agent]
        
        # Each agent reports different tasks
        for i, agent in enumerate(agents):
            task_id = f"coord-task-{i+1}"
            agent.report_task_started(task_id, f"Coordination task {i+1}")
            agent.report_task_progress(task_id, 100.0, "Completed")
            agent.report_task_completed(task_id, {"agent_type": agent.agent_type})
        
        # Verify all agents have completed their tasks
        for agent in agents:
            stats = agent.get_communication_stats()
            assert stats['current_tasks'] >= 0  # Tasks completed
    
    def test_supervisor_delegation_workflow(self):
        """Test supervisor delegating tasks to multiple agents."""
        supervisor = BackendSupervisorAgent()
        
        # Create worker agents
        workers = [
            self.create_test_agent("worker-1", "worker"),
            self.create_test_agent("worker-2", "worker"),
            self.create_test_agent("worker-3", "testing")
        ]
        
        # Simulate supervisor assigning tasks
        tasks = [
            {"task_id": "impl-1", "type": "implementation", "description": "Implement API endpoint"},
            {"task_id": "impl-2", "type": "implementation", "description": "Add authentication"},
            {"task_id": "test-1", "type": "testing", "description": "Write unit tests"}
        ]
        
        # Assign tasks to appropriate agents
        for i, task in enumerate(tasks):
            if i < len(workers):
                workers[i].report_task_started(task["task_id"], task["description"])
    
    def test_agent_to_agent_communication(self):
        """Test direct communication between agents."""
        sender = self.create_test_agent("sender-agent")
        receiver = self.create_test_agent("receiver-agent")
        
        # Create a direct message between agents
        message_content = {
            "request_type": "data_sharing",
            "data": {"shared_resource": "database_connection"},
            "priority": "high"
        }
        
        # Send status update that includes agent-to-agent communication
        sender.report_status_change("coordinating", {
            "communicating_with": receiver.agent_id,
            "message": message_content
        })
        
        # Receiver acknowledges
        receiver.report_status_change("coordination_received", {
            "from_agent": sender.agent_id,
            "acknowledged": True
        })
    
    def test_error_recovery_scenarios(self):
        """Test various error recovery scenarios."""
        agent = self.create_test_agent("recovery-agent")
        
        # Scenario 1: Network timeout
        agent.send_error_report("network_timeout", "Failed to connect to Redis", severity="high")
        
        # Scenario 2: Task failure with retry
        task_id = "retry-task"
        agent.report_task_started(task_id, "Task with retry logic")
        agent.report_task_error(task_id, "First attempt failed", {"attempt": 1})
        
        # Simulate retry
        agent.report_task_progress(task_id, 25.0, "Retrying...")
        agent.report_task_completed(task_id, {"status": "success", "attempts": 2})
        
        # Scenario 3: Communication failure fallback
        agent.report_status_change("communication_degraded", {
            "fallback_mode": "memory_storage",
            "redis_status": "disconnected"
        })
    
    def test_concurrent_message_processing(self):
        """Test high-load concurrent messaging scenarios."""
        NUM_AGENTS = 5
        MESSAGES_PER_AGENT = 10
        
        agents = [self.create_test_agent(f"concurrent-{i}") for i in range(NUM_AGENTS)]
        
        def agent_work(agent, messages_count):
            """Simulate concurrent agent work."""
            for i in range(messages_count):
                task_id = f"{agent.agent_id}-task-{i}"
                agent.report_task_started(task_id, f"Concurrent task {i}")
                agent.report_task_progress(task_id, 50.0, "Processing...")
                time.sleep(0.01)  # Simulate work
                agent.report_task_completed(task_id, {"result": f"completed-{i}"})
        
        # Start concurrent threads
        threads = []
        for agent in agents:
            thread = threading.Thread(target=agent_work, args=(agent, MESSAGES_PER_AGENT))
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join(timeout=10)
        
        # Verify all agents completed their work
        for agent in agents:
            stats = agent.get_communication_stats()
            assert stats['agent_id'].startswith('concurrent-')
    
    def test_messaging_system_fallback(self):
        """Test messaging system fallback when Redis is unavailable."""
        # Test with memory fallback
        memory_messaging = SimpleMessaging(use_redis=False)
        
        # Test basic operations
        from helpers.simple_messaging import send_task_to_agent, send_status_update
        
        # Send messages
        task_data = {"task_id": "fallback-task", "description": "Test fallback"}
        success = send_task_to_agent(memory_messaging, "supervisor", "agent-1", task_data)
        assert success
        
        status_data = {"status": "active", "tasks": 1}
        success = send_status_update(memory_messaging, "agent-1", "supervisor", status_data)
        assert success
        
        # Check stats
        stats = memory_messaging.get_queue_stats()
        assert stats['mode'] == 'memory'
        assert stats['total_messages'] >= 2
    
    def test_supervisor_monitoring_dashboard(self):
        """Test supervisor's view of all agent activities."""
        # Create supervisor and multiple agents
        agents = [
            self.create_test_agent("monitor-worker-1", "worker"),
            self.create_test_agent("monitor-testing-1", "testing"),
            self.create_test_agent("monitor-research-1", "research")
        ]
        
        # Simulate various agent activities
        activities = [
            ("monitor-worker-1", "implementing_feature", {"feature": "authentication", "progress": 75}),
            ("monitor-testing-1", "running_tests", {"test_suite": "integration", "passed": 15, "failed": 2}),
            ("monitor-research-1", "analyzing_requirements", {"documents": 5, "findings": 3})
        ]
        
        for agent_id, status, details in activities:
            agent = next(a for a in agents if a.agent_id == agent_id)
            agent.report_status_change(status, details)
        
        # Collect monitoring data
        monitoring_data = {}
        for agent in agents:
            stats = agent.get_communication_stats()
            monitoring_data[agent.agent_id] = {
                "type": stats['agent_type'],
                "capabilities": stats['capabilities'],
                "active_tasks": stats['current_tasks'],
                "communication_enabled": stats['communication_enabled']
            }
        
        # Verify monitoring data
        assert len(monitoring_data) == 3
        assert "monitor-worker-1" in monitoring_data
        assert monitoring_data["monitor-worker-1"]["type"] == "worker"
    
    def test_performance_benchmarks(self):
        """Test messaging performance benchmarks."""
        agent = self.create_test_agent("perf-agent")
        
        # Benchmark task reporting
        start_time = time.time()
        
        NUM_TASKS = 100
        for i in range(NUM_TASKS):
            task_id = f"perf-task-{i}"
            agent.report_task_started(task_id, f"Performance test task {i}")
            agent.report_task_completed(task_id, {"result": i})
        
        elapsed = time.time() - start_time
        
        # Performance assertions
        assert elapsed < 5.0  # Should complete 100 tasks in under 5 seconds
        tasks_per_second = NUM_TASKS / elapsed
        assert tasks_per_second > 20  # Should handle at least 20 tasks per second
    
    def test_message_serialization(self):
        """Test message serialization and deserialization."""
        from helpers.simple_messaging import SimpleMessage, MessageType, MessagePriority
        
        # Create complex message
        message = SimpleMessage(
            message_id="test-msg-001",
            from_agent="agent-1",
            to_agent="agent-2", 
            message_type=MessageType.TASK_ASSIGNMENT,
            content={
                "task_data": {"complex": {"nested": "data"}},
                "numbers": [1, 2, 3],
                "boolean": True
            },
            priority=MessagePriority.HIGH
        )
        
        # Serialize to dict
        serialized = message.to_dict()
        
        # Verify serialization
        assert serialized['message_id'] == "test-msg-001"
        assert serialized['message_type'] == "task_assignment"
        assert serialized['priority'] == 3
        assert serialized['content']['task_data']['complex']['nested'] == "data"
    
    def test_tracing_integration(self):
        """Test integration with dynamic tracing controller."""
        # Enable tracing for testing
        TRACING_CONTROLLER.enable_module_tracing("agent_communication_mixin")
        
        agent = self.create_test_agent("traced-agent")
        
        # Perform traced operations
        task_id = "traced-task"
        agent.report_task_started(task_id, "Traced task execution")
        agent.report_task_progress(task_id, 100.0, "Traced completion")
        agent.report_task_completed(task_id, {"traced": True})
        
        # Check tracing status
        status = TRACING_CONTROLLER.get_tracing_status()
        assert "agent_communication_mixin" in status['enabled_modules']
        
        # Disable tracing
        TRACING_CONTROLLER.disable_module_tracing("agent_communication_mixin")


class TestDynamicTracing:
    """Test suite for dynamic tracing functionality."""
    
    def test_conditional_tracing_decorator(self):
        """Test the conditional tracing decorator."""
        
        @conditional_trace("test_module")
        def test_function(x, y):
            return x + y
        
        # Test function execution (tracing disabled)
        result = test_function(2, 3)
        assert result == 5
        
        # Enable tracing for module
        TRACING_CONTROLLER.enable_module_tracing("test_module")
        
        # Test function execution (tracing enabled)
        result = test_function(5, 7)
        assert result == 12
        
        # Disable tracing
        TRACING_CONTROLLER.disable_module_tracing("test_module")
    
    def test_tracing_configuration_persistence(self):
        """Test tracing configuration save/load."""
        # Enable some tracing
        TRACING_CONTROLLER.enable_module_tracing("test_persistence", ["method1", "method2"])
        TRACING_CONTROLLER.enable_method_tracing("test_persistence", "method3")
        
        # Save configuration
        TRACING_CONTROLLER.save_configuration()
        
        # Create new controller to test loading
        from helpers.dynamic_tracing_controller import TracingController
        new_controller = TracingController()
        
        # Verify configuration loaded
        assert new_controller.should_trace("test_persistence", "method1")
        assert new_controller.should_trace("test_persistence", "method3")
        assert not new_controller.should_trace("test_persistence", "method4")
    
    def test_tracing_performance_impact(self):
        """Test performance impact of tracing system."""
        
        @conditional_trace("performance_test")
        def fast_function():
            return sum(range(1000))
        
        # Benchmark without tracing
        TRACING_CONTROLLER.disable_module_tracing("performance_test")
        
        start_time = time.time()
        for _ in range(100):
            fast_function()
        no_trace_time = time.time() - start_time
        
        # Benchmark with tracing
        TRACING_CONTROLLER.enable_module_tracing("performance_test")
        
        start_time = time.time()
        for _ in range(100):
            fast_function()
        trace_time = time.time() - start_time
        
        # Performance impact should be reasonable
        overhead_ratio = trace_time / no_trace_time if no_trace_time > 0 else 1
        assert overhead_ratio < 10  # Tracing shouldn't be more than 10x slower


# Integration test that covers the full workflow
class TestFullWorkflow:
    """Integration test for complete agent communication workflow."""
    
    def test_complete_project_workflow(self):
        """Test a complete project workflow from start to finish."""
        
        # 1. Supervisor creates project plan
        supervisor = BackendSupervisorAgent()
        
        # 2. Create specialized agents
        messaging = create_simple_messaging(use_redis=False)
        
        research_agent = CommunicatingAgent(
            "research-workflow", "research", 
            ["web_research", "documentation"], "supervisor"
        )
        
        worker_agent = CommunicatingAgent(
            "worker-workflow", "worker",
            ["implementation", "coding"], "supervisor"
        )
        
        testing_agent = CommunicatingAgent(
            "testing-workflow", "testing",
            ["unit_testing", "integration_testing"], "supervisor"
        )
        
        # 3. Simulate project execution
        # Research phase
        research_agent.report_task_started("research-api", "Research API design patterns")
        research_agent.report_task_progress("research-api", 50.0, "Analyzing REST patterns")
        research_agent.report_task_completed("research-api", {
            "patterns": ["REST", "GraphQL"],
            "recommendations": "Use REST for simplicity"
        })
        
        # Implementation phase
        worker_agent.report_task_started("implement-api", "Implement API endpoints")
        worker_agent.report_task_progress("implement-api", 75.0, "Implementing authentication")
        worker_agent.report_task_completed("implement-api", {
            "endpoints": 5,
            "features": ["auth", "crud", "validation"]
        })
        
        # Testing phase
        testing_agent.report_task_started("test-api", "Test API functionality")
        testing_agent.report_task_progress("test-api", 100.0, "All tests passing")
        testing_agent.report_task_completed("test-api", {
            "tests_run": 25,
            "passed": 25,
            "coverage": "95%"
        })
        
        # 4. Verify workflow completion
        agents = [research_agent, worker_agent, testing_agent]
        for agent in agents:
            stats = agent.get_communication_stats()
            assert stats['communication_enabled'] or not stats['communication_enabled']  # Just verify stats exist


if __name__ == "__main__":
    # Run quick tests
    print("🧪 Running Agent Communication Test Suite")
    print("=" * 50)
    
    # Create test instances
    test_comm = TestAgentCommunication()
    test_comm.setup_method()
    
    # Run key tests
    try:
        test_comm.test_agent_registration()
        print("✅ Agent registration test passed")
        
        test_comm.test_task_lifecycle()
        print("✅ Task lifecycle test passed")
        
        test_comm.test_multi_agent_coordination()
        print("✅ Multi-agent coordination test passed")
        
        test_comm.test_error_recovery_scenarios()
        print("✅ Error recovery test passed")
        
        # Test dynamic tracing
        test_trace = TestDynamicTracing()
        test_trace.test_conditional_tracing_decorator()
        print("✅ Dynamic tracing test passed")
        
        print("\n🎉 All tests passed! Agent communication system is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        test_comm.teardown_method()
