"""
Unit Tests for Autonomous Agent Communication System
===================================================

These tests verify the functionality of the agent communication system
components including message protocol, queue management, agent registry,
and supervisor coordination.

Run with: python -m pytest test_agent_communication.py -v
"""

import unittest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from helpers.agent_communication import (
    AgentMessage, MessageType, MessagePriority, AgentRole,
    TaskRequest, TaskResponse, create_task_request_message,
    MessageQueueManager, AgentRegistry, SupervisorCoordinator
)
from helpers.agent_communication.agent_registry import AgentInfo


class TestMessageProtocol(unittest.TestCase):
    """Test the message protocol implementation"""
    
    def test_agent_message_creation(self):
        """Test AgentMessage creation and serialization"""
        msg = AgentMessage(
            message_id="test-001",
            from_agent="sender",
            to_agent="receiver",
            message_type=MessageType.TASK_REQUEST,
            content={"task": "test"},
            priority=MessagePriority.HIGH
        )
        
        self.assertEqual(msg.message_id, "test-001")
        self.assertEqual(msg.from_agent, "sender")
        self.assertEqual(msg.to_agent, "receiver")
        self.assertEqual(msg.message_type, MessageType.TASK_REQUEST)
        self.assertEqual(msg.priority, MessagePriority.HIGH)
        self.assertIsInstance(msg.timestamp, datetime)
    
    def test_message_serialization(self):
        """Test JSON serialization and deserialization"""
        original = AgentMessage(
            message_id="test-002",
            from_agent="sender",
            to_agent="receiver",
            message_type=MessageType.STATUS_UPDATE,
            content={"status": "running"},
            priority=MessagePriority.MEDIUM
        )
        
        # Serialize to JSON
        json_data = original.to_json()
        self.assertIsInstance(json_data, str)
        
        # Deserialize from JSON
        restored = AgentMessage.from_json(json_data)
        
        # Verify all fields match
        self.assertEqual(original.message_id, restored.message_id)
        self.assertEqual(original.from_agent, restored.from_agent)
        self.assertEqual(original.to_agent, restored.to_agent)
        self.assertEqual(original.message_type, restored.message_type)
        self.assertEqual(original.content, restored.content)
        self.assertEqual(original.priority, restored.priority)
    
    def test_task_request_creation(self):
        """Test TaskRequest creation"""
        task = TaskRequest(
            task_id="task-001",
            task_type="code_review",
            description="Review the code",
            parameters={"files": ["test.py"]},
            required_capabilities=["python"],
            estimated_duration=3600,
            priority=MessagePriority.HIGH
        )
        
        self.assertEqual(task.task_id, "task-001")
        self.assertEqual(task.task_type, "code_review")
        self.assertIn("python", task.required_capabilities)
        self.assertEqual(task.priority, MessagePriority.HIGH)
    
    def test_task_response_creation(self):
        """Test TaskResponse creation"""
        response = TaskResponse(
            task_id="task-001",
            agent_id="worker-001",
            status="completed",
            result={"success": True, "output": "Code looks good"},
            execution_time=1800,
            completion_percentage=100
        )
        
        self.assertEqual(response.task_id, "task-001")
        self.assertEqual(response.agent_id, "worker-001")
        self.assertEqual(response.status, "completed")
        self.assertEqual(response.completion_percentage, 100)
    
    def test_create_task_request_message(self):
        """Test helper function for creating task request messages"""
        msg = create_task_request_message(
            from_agent="supervisor",
            to_agent="worker",
            task_type="testing",
            description="Run tests",
            parameters={"coverage": "80%"},
            required_capabilities=["testing"]
        )
        
        self.assertEqual(msg.message_type, MessageType.TASK_REQUEST)
        self.assertEqual(msg.from_agent, "supervisor")
        self.assertEqual(msg.to_agent, "worker")
        self.assertIn("task_type", msg.content)
        self.assertEqual(msg.content["task_type"], "testing")


class TestMessageQueueManager(unittest.TestCase):
    """Test the message queue management"""
    
    def setUp(self):
        """Setup test queue manager in mock mode"""
        self.queue = MessageQueueManager(use_mock=True)
    
    def test_send_and_receive_message(self):
        """Test basic message sending and receiving"""
        msg = AgentMessage(
            message_id="queue-test-001",
            from_agent="sender",
            to_agent="receiver",
            message_type=MessageType.HEARTBEAT,
            content={"status": "alive"}
        )
        
        # Send message
        success = self.queue.send_message(msg)
        self.assertTrue(success)
        
        # Receive messages
        messages = self.queue.get_messages("receiver", limit=10)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message_id, "queue-test-001")
    
    def test_message_processing(self):
        """Test marking messages as processed"""
        msg = AgentMessage(
            message_id="process-test-001",
            from_agent="sender",
            to_agent="receiver",
            message_type=MessageType.TASK_REQUEST,
            content={"task": "test"}
        )
        
        # Send and receive
        self.queue.send_message(msg)
        messages = self.queue.get_messages("receiver", limit=1)
        self.assertEqual(len(messages), 1)
        
        # Mark as processed
        success = self.queue.mark_processed("process-test-001", "receiver")
        self.assertTrue(success)
        
        # Should not receive processed messages
        messages = self.queue.get_messages("receiver", limit=10)
        self.assertEqual(len(messages), 0)
    
    def test_message_priority_ordering(self):
        """Test that messages are returned in priority order"""
        messages_to_send = [
            ("low-msg", MessagePriority.LOW),
            ("critical-msg", MessagePriority.CRITICAL),
            ("medium-msg", MessagePriority.MEDIUM),
            ("high-msg", MessagePriority.HIGH)
        ]
        
        # Send messages in random order
        for msg_id, priority in messages_to_send:
            msg = AgentMessage(
                message_id=msg_id,
                from_agent="sender",
                to_agent="receiver",
                message_type=MessageType.TASK_REQUEST,
                content={"task": "test"},
                priority=priority
            )
            self.queue.send_message(msg)
        
        # Receive messages - should be in priority order
        received = self.queue.get_messages("receiver", limit=10)
        self.assertEqual(len(received), 4)
        
        # Verify priority order (CRITICAL, HIGH, MEDIUM, LOW)
        priorities = [msg.priority for msg in received]
        expected = [MessagePriority.CRITICAL, MessagePriority.HIGH, 
                   MessagePriority.MEDIUM, MessagePriority.LOW]
        self.assertEqual(priorities, expected)
    
    def test_queue_statistics(self):
        """Test queue statistics reporting"""
        # Send some test messages
        for i in range(5):
            msg = AgentMessage(
                message_id=f"stats-test-{i}",
                from_agent="sender",
                to_agent="receiver",
                message_type=MessageType.HEARTBEAT,
                content={"test": i}
            )
            self.queue.send_message(msg)
        
        stats = self.queue.get_queue_stats()
        self.assertIn("total_messages", stats)
        self.assertIn("pending_messages", stats)
        self.assertIn("processed_messages", stats)
        self.assertGreaterEqual(stats["total_messages"], 5)


class TestAgentRegistry(unittest.TestCase):
    """Test the agent registry functionality"""
    
    def setUp(self):
        """Setup test registry in mock mode"""
        self.registry = AgentRegistry(use_mock=True)
    
    def test_agent_registration(self):
        """Test basic agent registration"""
        success = self.registry.register_agent(
            agent_id="test-agent-001",
            agent_role=AgentRole.WORKER,
            capabilities=["python", "testing"],
            max_concurrent_tasks=3
        )
        self.assertTrue(success)
        
        # Verify agent is registered
        agents = self.registry.find_available_agents(
            required_capabilities=["python"],
            max_results=10
        )
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0].agent_id, "test-agent-001")
    
    def test_capability_matching(self):
        """Test finding agents by capabilities"""
        # Register agents with different capabilities
        agents_data = [
            ("python-dev", ["python", "django", "postgresql"]),
            ("js-dev", ["javascript", "react", "nodejs"]),
            ("devops", ["terraform", "azure", "kubernetes"]),
            ("fullstack", ["python", "javascript", "react", "postgresql"])
        ]
        
        for agent_id, capabilities in agents_data:
            self.registry.register_agent(
                agent_id=agent_id,
                agent_role=AgentRole.WORKER,
                capabilities=capabilities,
                max_concurrent_tasks=2
            )
            self.registry.update_heartbeat(agent_id, status='active')
        
        # Test capability matching
        test_cases = [
            (["python"], 2),  # python-dev, fullstack
            (["javascript", "react"], 2),  # js-dev, fullstack
            (["terraform"], 1),  # devops
            (["python", "postgresql"], 2),  # python-dev, fullstack
            (["nonexistent"], 0)  # no matches
        ]
        
        for required_caps, expected_count in test_cases:
            found = self.registry.find_available_agents(
                required_capabilities=required_caps,
                max_results=10
            )
            self.assertEqual(len(found), expected_count,
                           f"Expected {expected_count} agents for {required_caps}, got {len(found)}")
    
    def test_load_balancing(self):
        """Test load balancing functionality"""
        # Register multiple agents with same capabilities
        for i in range(3):
            agent_id = f"worker-{i}"
            self.registry.register_agent(
                agent_id=agent_id,
                agent_role=AgentRole.WORKER,
                capabilities=["python"],
                max_concurrent_tasks=5
            )
            # Simulate different load levels
            self.registry.update_heartbeat(agent_id, status='active', current_tasks=i)
        
        # Find best agent (should be worker-0 with 0 tasks)
        best = self.registry.find_best_agent(required_capabilities=["python"])
        self.assertIsNotNone(best)
        self.assertEqual(best.agent_id, "worker-0")
        self.assertEqual(best.current_tasks, 0)
    
    def test_heartbeat_updates(self):
        """Test agent heartbeat and status tracking"""
        agent_id = "heartbeat-test"
        
        # Register agent
        self.registry.register_agent(
            agent_id=agent_id,
            agent_role=AgentRole.WORKER,
            capabilities=["testing"],
            max_concurrent_tasks=1
        )
        
        # Update heartbeat
        success = self.registry.update_heartbeat(
            agent_id=agent_id,
            status='active',
            current_tasks=1
        )
        self.assertTrue(success)
        
        # Find agent and verify status
        agents = self.registry.find_available_agents(
            required_capabilities=["testing"],
            max_results=10
        )
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0].status, 'active')
        self.assertEqual(agents[0].current_tasks, 1)
    
    def test_registry_statistics(self):
        """Test registry statistics reporting"""
        # Register agents with different roles and statuses
        test_agents = [
            ("supervisor-1", AgentRole.SUPERVISOR, "active"),
            ("worker-1", AgentRole.WORKER, "active"),
            ("worker-2", AgentRole.WORKER, "busy"),
            ("tester-1", AgentRole.TESTER, "inactive")
        ]
        
        for agent_id, role, status in test_agents:
            self.registry.register_agent(
                agent_id=agent_id,
                agent_role=role,
                capabilities=["general"],
                max_concurrent_tasks=2
            )
            self.registry.update_heartbeat(agent_id, status=status)
        
        stats = self.registry.get_registry_stats()
        self.assertEqual(stats["total_agents"], 4)
        self.assertEqual(stats["by_role"][AgentRole.WORKER.value], 2)
        self.assertEqual(stats["by_role"][AgentRole.SUPERVISOR.value], 1)
        self.assertEqual(stats["by_status"]["active"], 2)


class TestSupervisorCoordinator(unittest.TestCase):
    """Test the supervisor coordination functionality"""
    
    def setUp(self):
        """Setup test coordinator"""
        self.coordinator = SupervisorCoordinator("test-supervisor", use_mock=True)
        
        # Register some test worker agents
        test_workers = [
            ("worker-python", ["python", "backend"]),
            ("worker-js", ["javascript", "frontend"]),
            ("worker-devops", ["terraform", "azure"])
        ]
        
        for agent_id, capabilities in test_workers:
            self.coordinator.agent_registry.register_agent(
                agent_id=agent_id,
                agent_role=AgentRole.WORKER,
                capabilities=capabilities,
                max_concurrent_tasks=3
            )
            self.coordinator.agent_registry.update_heartbeat(agent_id, status='active')
    
    def test_task_assignment(self):
        """Test basic task assignment"""
        task_id = self.coordinator.assign_task(
            task_type="backend_development",
            description="Create API endpoints",
            parameters={"framework": "fastapi"},
            required_capabilities=["python", "backend"],
            priority=MessagePriority.HIGH
        )
        
        self.assertIsNotNone(task_id)
        self.assertIn(task_id, self.coordinator.active_tasks)
        
        # Verify task was assigned to correct agent
        task_info = self.coordinator.active_tasks[task_id]
        self.assertEqual(task_info["agent_id"], "worker-python")
    
    def test_task_assignment_no_suitable_agent(self):
        """Test task assignment when no suitable agent is available"""
        task_id = self.coordinator.assign_task(
            task_type="mobile_development",
            description="Create mobile app",
            parameters={"platform": "ios"},
            required_capabilities=["swift", "ios"],  # No agent has these
            priority=MessagePriority.MEDIUM
        )
        
        self.assertIsNone(task_id)
    
    def test_message_processing(self):
        """Test processing incoming messages"""
        # Create a task response message
        response_msg = AgentMessage(
            message_id="response-001",
            from_agent="worker-python",
            to_agent=self.coordinator.supervisor_id,
            message_type=MessageType.TASK_RESPONSE,
            content={
                "task_id": "test-task-001",
                "status": "completed",
                "result": {"success": True},
                "completion_percentage": 100
            }
        )
        
        # Send the message
        self.coordinator.queue_manager.send_message(response_msg)
        
        # Process incoming messages
        processed_count = self.coordinator.process_incoming_messages()
        self.assertGreaterEqual(processed_count, 1)
    
    def test_coordination_statistics(self):
        """Test coordination statistics reporting"""
        # Assign a few tasks
        for i in range(3):
            self.coordinator.assign_task(
                task_type="test_task",
                description=f"Test task {i}",
                parameters={"test": True},
                required_capabilities=["python"],
                priority=MessagePriority.MEDIUM
            )
        
        stats = self.coordinator.get_coordination_stats()
        self.assertIn("active_tasks", stats)
        self.assertIn("active_agents", stats)
        self.assertIn("metrics", stats)
        self.assertEqual(stats["active_tasks"], 3)
        self.assertEqual(stats["metrics"]["tasks_assigned"], 3)
    
    def test_broadcast_message(self):
        """Test broadcasting messages to all agents"""
        message_content = {
            "announcement": "System maintenance scheduled",
            "timestamp": datetime.now().isoformat()
        }
        
        success = self.coordinator.broadcast_message(
            message_type=MessageType.STATUS_UPDATE,
            content=message_content,
            priority=MessagePriority.HIGH
        )
        self.assertTrue(success)
        
        # Verify messages were sent to all registered agents
        for agent_id in ["worker-python", "worker-js", "worker-devops"]:
            messages = self.coordinator.queue_manager.get_messages(agent_id, limit=10)
            found_broadcast = any(
                msg.content.get("announcement") == "System maintenance scheduled"
                for msg in messages
            )
            self.assertTrue(found_broadcast, f"Broadcast not received by {agent_id}")
    
    def test_cleanup_and_maintenance(self):
        """Test maintenance operations"""
        # Create some test data
        self.coordinator.assign_task(
            task_type="maintenance_test",
            description="Test maintenance",
            parameters={},
            required_capabilities=["python"],
            priority=MessagePriority.LOW
        )
        
        # Run maintenance
        results = self.coordinator.cleanup_and_maintenance()
        
        self.assertIn("inactive_agents_removed", results)
        self.assertIn("old_messages_cleaned", results)
        self.assertIn("stale_tasks_handled", results)
        self.assertIsInstance(results["inactive_agents_removed"], int)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from task assignment to completion"""
        # Setup
        coordinator = SupervisorCoordinator("integration-test", use_mock=True)
        
        # Register a worker agent
        worker_id = "integration-worker"
        coordinator.agent_registry.register_agent(
            agent_id=worker_id,
            agent_role=AgentRole.WORKER,
            capabilities=["integration", "testing"],
            max_concurrent_tasks=1
        )
        coordinator.agent_registry.update_heartbeat(worker_id, status='active')
        
        # Assign a task
        task_id = coordinator.assign_task(
            task_type="integration_test",
            description="Run integration tests",
            parameters={"test_suite": "full"},
            required_capabilities=["integration"],
            priority=MessagePriority.HIGH
        )
        
        self.assertIsNotNone(task_id)
        
        # Simulate task completion by sending response message
        response = AgentMessage(
            message_id="integration-response",
            from_agent=worker_id,
            to_agent=coordinator.supervisor_id,
            message_type=MessageType.TASK_RESPONSE,
            content={
                "task_id": task_id,
                "status": "completed",
                "result": {"tests_passed": 42, "tests_failed": 0},
                "completion_percentage": 100
            }
        )
        
        coordinator.queue_manager.send_message(response)
        
        # Process the response
        processed = coordinator.process_incoming_messages()
        self.assertGreaterEqual(processed, 1)
        
        # Verify task completion
        task_status = coordinator.get_task_status(task_id)
        self.assertIsNotNone(task_status)
        self.assertEqual(task_status["status"], "completed")
    
    def test_error_handling_workflow(self):
        """Test error handling in the complete system"""
        coordinator = SupervisorCoordinator("error-test", use_mock=True)
        
        # Register a worker agent
        worker_id = "error-worker"
        coordinator.agent_registry.register_agent(
            agent_id=worker_id,
            agent_role=AgentRole.WORKER,
            capabilities=["error_prone"],
            max_concurrent_tasks=1
        )
        coordinator.agent_registry.update_heartbeat(worker_id, status='active')
        
        # Send an error report
        error_msg = AgentMessage(
            message_id="error-report",
            from_agent=worker_id,
            to_agent=coordinator.supervisor_id,
            message_type=MessageType.ERROR_REPORT,
            content={
                "error_type": "task_execution_failure",
                "error_message": "Test error condition",
                "task_id": "failed-task",
                "timestamp": datetime.now().isoformat()
            },
            priority=MessagePriority.CRITICAL
        )
        
        coordinator.queue_manager.send_message(error_msg)
        
        # Process the error
        processed = coordinator.process_incoming_messages()
        self.assertGreaterEqual(processed, 1)
        
        # System should continue functioning
        stats = coordinator.get_coordination_stats()
        self.assertIsInstance(stats, dict)


if __name__ == "__main__":
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run all tests
    unittest.main(verbosity=2)
