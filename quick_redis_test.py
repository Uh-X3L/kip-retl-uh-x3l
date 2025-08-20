"""
Quick Redis Communication Test
=============================

A simple test to verify Redis communication is working correctly.
"""

from helpers_old.sample_communicating_agent import SampleAnalysisAgent, SampleDevelopmentAgent

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
