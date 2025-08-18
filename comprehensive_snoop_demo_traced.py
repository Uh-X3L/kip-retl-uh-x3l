"""
Comprehensive Snoop Tracing Demo
===============================

This script demonstrates the complete snoop tracing system for your codebase.
It will show you exactly what's happening during execution with line-by-line
tracing, method calls, inputs, outputs, and complete execution flow.
"""

import time
import json
from pathlib import Path

# Import the snoop tracing system
from helpers.snoop_enhanced_logger import (

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


    initialize_snoop_tracing, start_comprehensive_tracing,
    snoop_trace, get_snoop_logger, view_trace_output,
    finalize_snoop_tracing
)

# Import the traced base agent
from helpers.snoop_traced_base_agent import create_traced_agent, SnoopTracedBaseAgent

@snoop_trace
@trace_func
def demo_computation(x: int, y: int, operation: str = "add") -> dict:
    """Demo function that will be traced line by line."""
    print(f"🧮 Starting computation: {x} {operation} {y}")
    
    if operation == "add":
        result = x + y
        operation_symbol = "+"
    elif operation == "multiply":
        result = x * y
        operation_symbol = "*"
    elif operation == "power":
        result = x ** y
        operation_symbol = "**"
    else:
        result = None
        operation_symbol = "?"
    
    computation_details = {
        "input_x": x,
        "input_y": y,
        "operation": operation,
        "operation_symbol": operation_symbol,
        "result": result,
        "timestamp": time.time()
    }
    
    print(f"✅ Computation completed: {x} {operation_symbol} {y} = {result}")
    
    return computation_details

@snoop_trace
@trace_func
def demo_data_processing(data_list: list) -> dict:
    """Demo function for processing data with tracing."""
    print(f"📊 Processing data list with {len(data_list)} items")
    
    # Filter positive numbers
    positive_numbers = []
    negative_numbers = []
    other_items = []
    
    for item in data_list:
        if isinstance(item, (int, float)):
            if item > 0:
                positive_numbers.append(item)
            else:
                negative_numbers.append(item)
        else:
            other_items.append(item)
    
    # Calculate statistics
    if positive_numbers:
        stats = {
            "count": len(positive_numbers),
            "sum": sum(positive_numbers),
            "average": sum(positive_numbers) / len(positive_numbers),
            "min": min(positive_numbers),
            "max": max(positive_numbers)
        }
    else:
        stats = {"count": 0, "sum": 0, "average": 0, "min": None, "max": None}
    
    processing_result = {
        "original_data": data_list,
        "positive_numbers": positive_numbers,
        "negative_numbers": negative_numbers,
        "other_items": other_items,
        "statistics": stats,
        "processing_timestamp": time.time()
    }
    
    print(f"✅ Data processing completed: {stats['count']} positive numbers found")
    
    return processing_result

@snoop_trace
@trace_func
def run_comprehensive_demo():
    """
    Run a comprehensive demonstration of snoop tracing capabilities.
    """
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE SNOOP TRACING DEMONSTRATION")
    print("="*80)
    
    # Step 1: Initialize snoop tracing
    print("\n📋 STEP 1: Initializing Snoop Tracing")
    print("-" * 40)
    
    session_name = f"demo_session_{int(time.time())}"
    snoop_logger = initialize_snoop_tracing(
        session_name=session_name,
        log_dir="logs",
        enable_comprehensive=True,
        trace_all_modules=False
    )
    
    print(f"✅ Snoop tracing initialized for session: {session_name}")
    
    # Step 2: Enable comprehensive tracing
    print("\n📋 STEP 2: Enabling Comprehensive Tracing")
    print("-" * 40)
    
    start_comprehensive_tracing()
    
    # Step 3: Create traced agents
    print("\n📋 STEP 3: Creating Traced Agents")
    print("-" * 40)
    
    # Create multiple agents to show multi-agent tracing
    agent1 = create_traced_agent("ComputationAgent", "computation_agent")
    agent2 = create_traced_agent("DataProcessingAgent", "data_processing_agent")
    
    print(f"✅ Created traced agents: {agent1.agent_name}, {agent2.agent_name}")
    
    # Step 4: Execute traced computations
    print("\n📋 STEP 4: Executing Traced Computations")
    print("-" * 40)
    
    # Simple computations
    computation_results = []
    
    # Addition
    result1 = demo_computation(15, 25, "add")
    computation_results.append(result1)
    
    # Multiplication
    result2 = demo_computation(7, 8, "multiply")
    computation_results.append(result2)
    
    # Power operation
    result3 = demo_computation(2, 10, "power")
    computation_results.append(result3)
    
    print(f"✅ Completed {len(computation_results)} traced computations")
    
    # Step 5: Execute traced data processing
    print("\n📋 STEP 5: Executing Traced Data Processing")
    print("-" * 40)
    
    # Create test data
    test_data = [1, -5, 3.14, "hello", 42, -2.5, "world", 100, 0, 7.5]
    
    processing_result = demo_data_processing(test_data)
    
    print(f"✅ Data processing completed")
    
    # Step 6: Agent task execution with tracing
    print("\n📋 STEP 6: Agent Task Execution with Tracing")
    print("-" * 40)
    
    # Add tasks to agents
    task1_id = agent1.add_task({
        "type": "simple_computation",
        "data": {
            "operation": "add",
            "values": [10, 20, 30, 40, 50]
        }
    })
    
    task2_id = agent1.add_task({
        "type": "simple_computation", 
        "data": {
            "operation": "multiply",
            "values": [2, 3, 4]
        }
    })
    
    task3_id = agent2.add_task({
        "type": "data_processing",
        "data": [1, 2, 3, 4, 5, -1, -2, 10, 15],
        "processing_type": "statistics"
    })
    
    task4_id = agent2.add_task({
        "type": "data_processing",
        "data": [-5, -10, 1, 2, 3, 100, 200],
        "processing_type": "filter_positive"
    })
    
    print(f"✅ Added 4 tasks to agents")
    
    # Execute tasks with tracing
    task_results = []
    
    result1 = agent1.execute_task(task1_id)
    task_results.append(result1)
    
    result2 = agent1.execute_task(task2_id)
    task_results.append(result2)
    
    result3 = agent2.execute_task(task3_id)
    task_results.append(result3)
    
    result4 = agent2.execute_task(task4_id)
    task_results.append(result4)
    
    print(f"✅ Executed {len(task_results)} traced tasks")
    
    # Step 7: Performance metrics and status
    print("\n📋 STEP 7: Performance Metrics and Status")
    print("-" * 40)
    
    agent1_metrics = agent1.get_performance_metrics()
    agent2_metrics = agent2.get_performance_metrics()
    
    print(f"📊 Agent1 Metrics: {agent1_metrics['tasks_completed']} tasks, {agent1_metrics['average_task_time']:.3f}s avg")
    print(f"📊 Agent2 Metrics: {agent2_metrics['tasks_completed']} tasks, {agent2_metrics['average_task_time']:.3f}s avg")
    
    # Step 8: View trace output
    print("\n📋 STEP 8: Viewing Trace Output")
    print("-" * 40)
    
    print("🔍 Recent trace output (last 30 lines):")
    view_trace_output(lines=30)
    
    # Step 9: Generate comprehensive summary
    print("\n📋 STEP 9: Generating Comprehensive Summary")
    print("-" * 40)
    
    # Get trace summary
    trace_summary = snoop_logger.get_trace_summary()
    
    print(f"📊 EXECUTION SUMMARY:")
    print(f"   🔍 Traced Functions: {trace_summary['traced_functions_count']}")
    print(f"   📄 Snoop Output File: {trace_summary['snoop_output_file']}")
    print(f"   🎯 Session Name: {trace_summary['session_name']}")
    
    # Combine all results
    demo_summary = {
        "session_info": {
            "session_name": session_name,
            "execution_timestamp": time.time(),
            "demo_duration": time.time() - demo_start_time
        },
        "computation_results": computation_results,
        "data_processing_result": processing_result,
        "task_execution_results": task_results,
        "agent1_metrics": agent1_metrics,
        "agent2_metrics": agent2_metrics,
        "trace_summary": trace_summary
    }
    
    # Save demo summary
    summary_file = Path("logs") / f"{session_name}_demo_summary.json"
    summary_file.parent.mkdir(exist_ok=True)
    
    try:
        with open(summary_file, 'w') as f:
            json.dump(demo_summary, f, indent=2, default=str)
        print(f"💾 Demo summary saved to: {summary_file}")
    except Exception as e:
        print(f"⚠️ Could not save demo summary: {e}")
    
    # Step 10: Cleanup and finalization
    print("\n📋 STEP 10: Cleanup and Finalization")
    print("-" * 40)
    
    # Shutdown agents
    agent1_shutdown = agent1.shutdown()
    agent2_shutdown = agent2.shutdown()
    
    print(f"✅ Agents shutdown completed")
    
    # Finalize tracing
    final_summary = finalize_snoop_tracing()
    
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE SNOOP TRACING DEMONSTRATION COMPLETED")
    print("="*80)
    print(f"📊 Total Demo Duration: {time.time() - demo_start_time:.2f} seconds")
    print(f"📁 Log Directory: logs/")
    print(f"📄 Snoop Trace File: {trace_summary['snoop_output_file']}")
    print(f"💾 Demo Summary: {summary_file}")
    
    if final_summary:
        metrics = final_summary.get('comprehensive_summary', {}).get('performance_metrics', {})
        print(f"🎯 Total Operations Traced: {metrics.get('total_agent_operations', 0)}")
        print(f"⏱️ Total Execution Time: {metrics.get('total_duration', 0):.2f}s")
    
    print("\n🔍 To view detailed trace output, check the snoop trace file above!")
    print("🚀 All code execution has been traced with line-by-line details!")
    
    return demo_summary

if __name__ == "__main__":
    # Record demo start time
    demo_start_time = time.time()
    
    print("🚀 Starting Comprehensive Snoop Tracing Demo...")
    print("   This will trace EVERYTHING that happens during execution!")
    print("   You'll be able to see every line of code, every method call,")
    print("   every input, every output, and every variable change!")
    
    try:
        summary = run_comprehensive_demo()
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        
        # Still try to view trace output
        try:
            print("\n🔍 Viewing trace output despite error:")
            view_trace_output(lines=20)
        except:
            pass
    
    print("\n🎯 Demo finished. Check the logs directory for detailed trace files!")
