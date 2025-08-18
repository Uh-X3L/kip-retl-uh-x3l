#!/usr/bin/env python3
"""
Simple Agent System Demo
========================

Demonstrates the simplified integration between:
- BackendSupervisorAgent for strategic planning
- Specialized agents from agents/ folder
- Simple messaging for coordination

This shows how the complex agent communication system has been simplified
to focus on essential coordination functionality.
"""

import sys
import os
import time

# Add helpers to path

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


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))

@trace_func
def main():
    print("=== Simple Agent System Demo ===")
    print()
    
    # Test 1: Simple Messaging
    print("📨 Testing Simple Messaging...")
    try:
        from simple_messaging import SimpleMessaging, MessageType
        
        messaging = SimpleMessaging(use_redis=False)  # Use memory mode for demo
        
        # Create and send a test message
        message = messaging.create_task_message(
            from_agent="coordinator",
            to_agent="worker_agent", 
            task_data={"task": "test_task", "description": "Test task for demo"}
        )
        
        success = messaging.send_message(message)
        print(f"   ✅ Message sent: {success}")
        
        # Retrieve messages
        messages = messaging.get_messages("worker_agent")
        print(f"   📬 Messages received: {len(messages)}")
        
        # Show stats
        stats = messaging.get_queue_stats()
        print(f"   📊 Queue stats: {stats}")
        
    except ImportError as e:
        print(f"   ⚠️ Simple messaging not available: {e}")
    
    print()
    
    # Test 2: Simple Agent Coordinator
    print("🎯 Testing Simple Agent Coordinator...")
    try:
        from simple_agent_coordinator import SimpleAgentCoordinator
        
        coordinator = SimpleAgentCoordinator("demo-coordinator")
        
        # Show coordinator status
        status = coordinator.get_coordination_status()
        print(f"   📊 Coordinator Status:")
        print(f"      Messaging: {status['messaging_available']}")
        print(f"      Agents: {status['agents_available']}")
        print(f"      Supervisor: {status['supervisor_available']}")
        
        # Run a quick coordination demo
        print("   🚀 Running coordination demo...")
        demo_result = coordinator.quick_demo()
        
        print(f"   ✅ Demo result:")
        print(f"      Project: {demo_result['project_idea']}")
        print(f"      Status: {demo_result['status']}")
        print(f"      Phases: {len(demo_result['phases'])}")
        print(f"      Agents used: {', '.join(demo_result['agents_used'])}")
        
        if demo_result.get('task_assignments'):
            print(f"      Tasks assigned: {len(demo_result['task_assignments'])}")
        
    except ImportError as e:
        print(f"   ⚠️ Simple coordinator not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Coordinator demo failed: {e}")
    
    print()
    
    # Test 3: Backend Supervisor with Coordination
    print("🧠 Testing Backend Supervisor Integration...")
    try:
        # Import with fallback for missing Azure dependencies
        try:
            from backend_supervisor_role_tools import BackendSupervisorAgent
            supervisor = BackendSupervisorAgent()
            supervisor_available = True
        except Exception as e:
            print(f"   ⚠️ Backend supervisor creation failed: {e}")
            supervisor_available = False
        
        if supervisor_available:
            print("   ✅ Backend supervisor initialized")
            
            # Test the new coordination method
            if hasattr(supervisor, 'coordinate_comprehensive_project'):
                print("   🎯 Testing coordinated project creation...")
                
                project_result = supervisor.coordinate_comprehensive_project(
                    project_idea="Simple REST API",
                    requirements="Create a basic Python REST API with authentication"
                )
                
                print(f"   📊 Coordination result:")
                print(f"      Status: {project_result.get('status', 'unknown')}")
                if 'phases' in project_result:
                    print(f"      Phases completed: {len(project_result['phases'])}")
                if 'agents_used' in project_result:
                    print(f"      Agents used: {', '.join(project_result['agents_used'])}")
            else:
                print("   ℹ️ Coordination method not available, using fallback")
        
    except ImportError as e:
        print(f"   ⚠️ Backend supervisor not available: {e}")
    except Exception as e:
        print(f"   ⚠️ Backend supervisor test failed: {e}")
    
    print()
    
    # Test 4: Agents Module
    print("🤖 Testing Agents Module...")
    try:
        from agents import AgentManager, AGENT_TYPES, get_agent_capabilities
        
        print(f"   📋 Available agent types: {list(AGENT_TYPES.values())}")
        
        capabilities = get_agent_capabilities()
        print(f"   💡 Agent capabilities:")
        for agent_type, info in capabilities.items():
            print(f"      {agent_type}: {info['description']}")
        
        # Try to create agent manager (may fail without Azure)
        try:
            # This would require Azure credentials
            print("   ℹ️ Agent manager requires Azure credentials for full functionality")
        except Exception as e:
            print(f"   ⚠️ Agent manager creation requires Azure setup: {e}")
        
    except ImportError as e:
        print(f"   ⚠️ Agents module not available: {e}")
    
    print()
    
    # Summary
    print("📋 Summary:")
    print("   This simplified system provides:")
    print("   • ✅ Simple messaging (Redis or memory-based)")
    print("   • ✅ Agent coordination with task delegation")
    print("   • ✅ Integration with BackendSupervisorAgent")
    print("   • ✅ Specialized agents from agents/ folder")
    print("   • ✅ Fallback modes when components unavailable")
    print()
    print("   The complex agent communication system has been simplified to:")
    print("   • 📨 Essential messaging only (simple_messaging.py)")
    print("   • 🎯 Clean coordination logic (simple_agent_coordinator.py)")
    print("   • 🧠 Direct integration with existing supervisor and agents")
    print("   • 🔧 No duplication between communication and agent systems")
    print()
    print("✅ Demo completed!")


if __name__ == "__main__":
    main()
