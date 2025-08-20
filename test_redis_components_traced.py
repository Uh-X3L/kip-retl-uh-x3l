"""
Test Redis Communication Components
==================================

This script tests each component individually to identify and fix issues.
"""

import sys
import traceback


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


@trace_func
def test_simple_messaging():
    """Test the simple messaging system."""
    print("1. Testing Simple Messaging...")
    try:
        from helpers.agent_communication.simple_messaging import SimpleMessaging, MessageType
        
        messaging = SimpleMessaging()
        print(f"   ✅ SimpleMessaging created: {type(messaging)}")
        
        # Test message creation
        message = messaging.create_message(
            from_agent="test-sender",
            to_agent="test-receiver", 
            message_type=MessageType.STATUS_UPDATE,
            content={"status": "testing"}
        )
        print(f"   ✅ Message created: {message.message_id}")
        
        # Test sending message
        result = messaging.send_message(message)
        print(f"   ✅ Message sent: {result}")
        
        # Test getting messages
        messages = messaging.get_messages(agent_id="test-receiver", limit=10)
        print(f"   ✅ Retrieved {len(messages)} messages")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Simple Messaging failed: {e}")
        traceback.print_exc()
        return False

@trace_func
def test_agent_communication_mixin():
    """Test the agent communication mixin."""
    print("\n2. Testing Agent Communication Mixin...")
    try:
        from helpers.agent_communication.agent_communication_mixin import AgentCommunicationMixin, CommunicatingAgent
        
        # Test CommunicatingAgent (mixin requires params through this class)
        agent = CommunicatingAgent(
            agent_id="test-agent",
            agent_type="test_agent",
            capabilities=["testing"]
        )
        print(f"   ✅ CommunicatingAgent created: {agent.agent_id}")
        
        # Test registration
        reg_result = agent.register_with_supervisor("test-supervisor")
        print(f"   ✅ Registration result: {reg_result}")
        
        # Test heartbeat
        heartbeat_result = agent.send_heartbeat("test-supervisor", "active")
        print(f"   ✅ Heartbeat result: {heartbeat_result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Agent Communication Mixin failed: {e}")
        traceback.print_exc()
        return False

@trace_func
def test_sample_agents():
    """Test the sample communicating agents."""
    print("\n3. Testing Sample Communicating Agents...")
    try:
        from helpers_old.sample_communicating_agent import SampleAnalysisAgent, SampleDevelopmentAgent
        
        # Test analysis agent
        analysis_agent = SampleAnalysisAgent("test-analysis")
        print(f"   ✅ SampleAnalysisAgent created: {analysis_agent.agent_id}")
        
        # Test development agent
        dev_agent = SampleDevelopmentAgent("test-dev")
        print(f"   ✅ SampleDevelopmentAgent created: {dev_agent.agent_id}")
        
        # Test task execution
        test_task = {
            "task_id": "test_task_001",
            "type": "code_analysis",
            "description": "Test task"
        }
        
        result = analysis_agent.execute_task(test_task)
        print(f"   ✅ Task executed: {result['status']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Sample Agents failed: {e}")
        traceback.print_exc()
        return False

@trace_func
def test_simple_coordinator():
    """Test the simple agent coordinator."""
    print("\n4. Testing Simple Agent Coordinator...")
    try:
        from helpers_old.simple_agent_coordinator import SimpleAgentCoordinator
        
        coordinator = SimpleAgentCoordinator("test-coordinator")
        print(f"   ✅ SimpleAgentCoordinator created: {coordinator.coordinator_id}")
        
        # Test status
        status = coordinator.get_coordination_status()
        print(f"   ✅ Coordinator status: {status['messaging_available']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Simple Coordinator failed: {e}")
        traceback.print_exc()
        return False

@trace_func
def test_redis_demo():
    """Test the Redis communication demo."""
    print("\n5. Testing Redis Communication Demo...")
    try:
        from helpers_old.redis_communication_demo import RedisCommunicationDemo
        
        demo = RedisCommunicationDemo()
        print(f"   ✅ RedisCommunicationDemo created")
        
        # Test setup
        setup_result = demo.setup_demo()
        print(f"   ✅ Demo setup: {setup_result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Redis Demo failed: {e}")
        traceback.print_exc()
        return False

@trace_func
def main():
    """Run all component tests."""
    print("🧪 Testing Redis Communication Components")
    print("=" * 50)
    
    tests = [
        test_simple_messaging,
        test_agent_communication_mixin,
        test_sample_agents,
        test_simple_coordinator,
        test_redis_demo
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f"   ✅ Passed: {success_count}/{total_count}")
    print(f"   ❌ Failed: {total_count - success_count}/{total_count}")
    
    if all(results):
        print("\n🎉 All tests passed! Redis communication system is ready.")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
