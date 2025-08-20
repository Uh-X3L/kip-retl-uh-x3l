"""
Quick Redis Communication Test
=============================

A simple test to verify Redis communication is working correctly.
"""

from helpers_old.sample_communicating_agent import SampleAnalysisAgent, SampleDevelopmentAgent


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
def quick_redis_test():
    """Quick test of Redis communication system."""
    print('🧪 Quick Redis Communication Test')
    print('=' * 40)
    
    # Create a communicating agent
    agent = SampleAnalysisAgent('test-redis-agent')
    print(f'✅ Created: {agent.agent_id}')
    
    # Execute a simple task
    task = {
        'task_id': 'quick_test_001',
        'type': 'code_analysis',
        'description': 'Quick Redis test'
    }
    
    print(f'🚀 Executing task: {task["task_id"]}')
    result = agent.execute_task(task)
    print(f'✅ Result: {result["status"]}')
    
    print('\n🎉 Redis communication system working!')
    return result

if __name__ == "__main__":
    quick_redis_test()
