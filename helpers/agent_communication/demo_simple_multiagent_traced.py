#!/usr/bin/env python3
"""
Simple Multi-Agent Code Review Demo
===================================

Shows multiple agents coordinating via Redis messaging to analyze code.
Simplified version to avoid import issues.
"""

import sys
import os
import time
import asyncio
import json
from pathlib import Path

# Add current and parent directories to path for imports

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


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

try:
    from helpers.agent_communication import AgentMessage, MessageType, MessagePriority, MessageQueueManager
except ImportError:
    # If that fails, try direct imports
    from message_protocol import AgentMessage, MessageType, MessagePriority
    from queue_manager import MessageQueueManager


@trace_class
class SimpleAnalyzerAgent:
    """Simple agent that analyzes code files"""
    
    def __init__(self, agent_id: str, queue_manager: MessageQueueManager):
        self.agent_id = agent_id
        self.queue = queue_manager
        self.is_running = False
    
    @trace_func
    def quick_analyze(self, file_path: str) -> dict:
        """Quick analysis of a code file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            
            analysis = {
                "file": file_path,
                "total_lines": len(lines),
                "code_lines": len(code_lines),
                "has_docstrings": '"""' in content or "'''" in content,
                "has_todos": 'TODO' in content or 'FIXME' in content,
                "complexity": "high" if len(code_lines) > 100 else "medium" if len(code_lines) > 50 else "low"
            }
            
            # Generate simple recommendations
            recommendations = []
            if not analysis["has_docstrings"]:
                recommendations.append("Add docstrings for better documentation")
            if analysis["has_todos"]:
                recommendations.append("Review and resolve TODO/FIXME comments")
            if analysis["complexity"] == "high":
                recommendations.append("Consider breaking this file into smaller modules")
            
            analysis["recommendations"] = recommendations
            return analysis
            
        except Exception as e:
            return {"file": file_path, "error": str(e)}
    
    async def process_messages(self):
        """Process analysis requests"""
        print(f"🔍 {self.agent_id} started - ready for analysis")
        
        while self.is_running:
            try:
                messages = self.queue.get_messages(self.agent_id, limit=5)
                
                for message in messages:
                    if message.message_type == MessageType.TASK_REQUEST:
                        print(f"📊 {self.agent_id} received task: {message.content.get('file_path', 'unknown')}")
                        
                        # Simulate processing time
                        await asyncio.sleep(0.5)
                        
                        # Analyze the file
                        file_path = message.content.get('file_path')
                        analysis = self.quick_analyze(file_path)
                        
                        # Send response
                        response = AgentMessage(
                            message_id=f"response_{int(time.time())}_{self.agent_id}",
                            from_agent=self.agent_id,
                            to_agent=message.from_agent,
                            message_type=MessageType.TASK_RESPONSE,
                            content={
                                "task_id": message.content.get('task_id'),
                                "analysis": analysis
                            },
                            parent_message_id=message.message_id
                        )
                        
                        self.queue.send_message(response)
                        print(f"✅ {self.agent_id} completed analysis of {Path(file_path).name}")
                        
                        self.queue.mark_processed(message.message_id, self.agent_id)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ {self.agent_id} error: {e}")
                await asyncio.sleep(2)


@trace_class
class SimpleCoordinator:
    """Simple coordinator that manages the review process"""
    
    def __init__(self, agent_id: str, queue_manager: MessageQueueManager):
        self.agent_id = agent_id
        self.queue = queue_manager
        self.results = {}
    
    async def run_code_review(self, target_dir: str = "."):
        """Run a coordinated code review"""
        print(f"🎯 {self.agent_id} starting code review of: {target_dir}")
        
        # Find Python files (limit to 3 for demo)
        python_files = [f for f in Path(target_dir).rglob("*.py") if f.is_file()][:3]
        
        if not python_files:
            print("❌ No Python files found")
            return
        
        print(f"📁 Found {len(python_files)} files to analyze:")
        for file in python_files:
            print(f"   • {file.name}")
        
        # Send analysis tasks
        task_ids = []
        for i, file_path in enumerate(python_files):
            task_id = f"task_{i}_{int(time.time())}"
            task_ids.append(task_id)
            
            task_msg = AgentMessage(
                message_id=f"coord_{task_id}",
                from_agent=self.agent_id,
                to_agent="analyzer_001",
                message_type=MessageType.TASK_REQUEST,
                content={
                    "task_id": task_id,
                    "file_path": str(file_path),
                    "task_type": "code_analysis"
                },
                priority=MessagePriority.HIGH
            )
            
            success = self.queue.send_message(task_msg)
            print(f"📤 Sent task for {file_path.name}: {success}")
        
        # Wait for results
        print(f"⏳ Waiting for {len(task_ids)} analysis results...")
        
        completed = 0
        start_time = time.time()
        timeout = 20  # 20 second timeout
        
        while completed < len(task_ids) and (time.time() - start_time) < timeout:
            messages = self.queue.get_messages(self.agent_id, limit=10)
            
            for message in messages:
                if message.message_type == MessageType.TASK_RESPONSE:
                    task_id = message.content.get('task_id')
                    if task_id in task_ids:
                        self.results[task_id] = message.content.get('analysis', {})
                        completed += 1
                        print(f"✅ Received result {completed}/{len(task_ids)}")
                        self.queue.mark_processed(message.message_id, self.agent_id)
            
            await asyncio.sleep(0.5)
        
        # Generate report
        await self.generate_report()
    
    async def generate_report(self):
        """Generate final report"""
        print("\n" + "="*50)
        print("📋 CODE REVIEW REPORT")
        print("="*50)
        
        total_lines = 0
        total_files = len(self.results)
        total_recommendations = 0
        
        for task_id, analysis in self.results.items():
            if 'error' in analysis:
                print(f"❌ Error analyzing file: {analysis['error']}")
                continue
            
            file_name = Path(analysis.get('file', '')).name
            lines = analysis.get('total_lines', 0)
            code_lines = analysis.get('code_lines', 0)
            complexity = analysis.get('complexity', 'unknown')
            recommendations = analysis.get('recommendations', [])
            
            total_lines += lines
            total_recommendations += len(recommendations)
            
            print(f"\n🔍 {file_name}:")
            print(f"   Lines: {lines} (Code: {code_lines})")
            print(f"   Complexity: {complexity}")
            print(f"   Has docstrings: {'✅' if analysis.get('has_docstrings') else '❌'}")
            print(f"   Has TODOs: {'⚠️' if analysis.get('has_todos') else '✅'}")
            
            if recommendations:
                print(f"   Recommendations ({len(recommendations)}):")
                for rec in recommendations:
                    print(f"     • {rec}")
            else:
                print(f"   Recommendations: ✅ Looks good!")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Files analyzed: {total_files}")
        print(f"   Total lines: {total_lines}")
        print(f"   Total recommendations: {total_recommendations}")
        
        print("\n" + "="*50)
        print("✅ Multi-agent code review completed!")
        print("="*50)


async def run_simple_demo():
    """Run the simplified multi-agent demo"""
    print("🤖 Simple Multi-Agent Code Review Demo")
    print("="*40)
    
    # Initialize queue manager
    try:
        queue = MessageQueueManager(use_mock=False)
        print("✅ Connected to Redis")
    except Exception as e:
        print(f"⚠️ Using mock mode: {e}")
        queue = MessageQueueManager(use_mock=True)
    
    # Create agents
    coordinator = SimpleCoordinator("coordinator_001", queue)
    analyzer = SimpleAnalyzerAgent("analyzer_001", queue)
    
    # Start analyzer in background
    analyzer.is_running = True
    analyzer_task = asyncio.create_task(analyzer.process_messages())
    
    try:
        # Run the demo
        await coordinator.run_code_review(".")
        
        # Let agents finish
        await asyncio.sleep(1)
        
    finally:
        # Stop agents
        analyzer.is_running = False
        analyzer_task.cancel()
        
        print("\n🏁 Demo completed!")


if __name__ == "__main__":
    asyncio.run(run_simple_demo())
