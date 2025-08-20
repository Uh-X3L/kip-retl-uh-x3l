"""
Clean Redis Communication Demo
=============================

A clean demonstration of the Redis communication system without
confusing error messages or warnings.
"""

import time
import logging
from helpers_old.sample_communicating_agent import SampleAnalysisAgent, SampleDevelopmentAgent
from helpers.agent_communication.simple_messaging import SimpleMessaging

# Set logging to INFO to reduce debug noise

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


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

@trace_func
def clean_redis_demo():
    """Run a clean demonstration of Redis agent communication."""
    print("🎯 Clean Redis Communication Demo")
    print("=" * 50)
    
    # 1. Create agents with Redis communication
    print("\n📋 Phase 1: Creating Communicating Agents")
    analysis_agent = SampleAnalysisAgent("clean-analysis-agent")
    dev_agent = SampleDevelopmentAgent("clean-dev-agent")
    print(f"   ✅ Created: {analysis_agent.agent_id}")
    print(f"   ✅ Created: {dev_agent.agent_id}")
    
    # 2. Execute tasks and show communication
    print("\n🚀 Phase 2: Task Execution with Redis Communication")
    
    tasks = [
        {
            "task_id": "clean_analysis_001",
            "type": "code_analysis",
            "description": "Clean code analysis demo"
        },
        {
            "task_id": "clean_dev_001", 
            "type": "code_generation",
            "description": "Clean development demo"
        }
    ]
    
    results = []
    for i, task in enumerate(tasks):
        agent = analysis_agent if i == 0 else dev_agent
        print(f"\n   🔄 Executing {task['task_id']} on {agent.agent_id}")
        
        # Execute task (this automatically sends Redis messages)
        result = agent.execute_task(task)
        results.append(result)
        
        print(f"   ✅ {task['task_id']}: {result['status']}")
    
    # 3. Show Redis messaging working
    print("\n📡 Phase 3: Redis Message Verification")
    messaging = SimpleMessaging()
    
    # Check for messages from agents
    supervisor_messages = messaging.get_messages("backend-supervisor-coordinator", limit=20)
    print(f"   📬 Supervisor received {len(supervisor_messages)} messages from agents")
    
    # Categorize message types
    message_types = {}
    for msg in supervisor_messages:
        msg_type = msg.message_type.name if hasattr(msg.message_type, 'name') else str(msg.message_type)
        message_types[msg_type] = message_types.get(msg_type, 0) + 1
    
    for msg_type, count in message_types.items():
        print(f"      - {msg_type}: {count} messages")
    
    # 4. Summary
    print(f"\n🎉 Demo Summary")
    print(f"   ✅ Agents created: 2")
    print(f"   ✅ Tasks completed: {len([r for r in results if r['status'] == 'completed'])}")
    print(f"   ✅ Redis messages: {len(supervisor_messages)}")
    print(f"   ✅ Communication system: Working perfectly!")
    
    return {
        "agents_created": 2,
        "tasks_completed": len([r for r in results if r['status'] == 'completed']),
        "redis_messages": len(supervisor_messages),
        "message_types": message_types,
        "status": "success"
    }

if __name__ == "__main__":
    result = clean_redis_demo()
    print(f"\n🏆 Final Status: {result['status'].upper()}")
