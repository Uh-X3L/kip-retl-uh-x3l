#!/usr/bin/env python3
"""
Multi-Agent Code Review Demo
===========================

Demonstrates multiple AI agents coordinating to analyze and improve code.
Shows real agent collaboration using Redis messaging.
"""

import sys
import os
import time
import asyncio
import json
from pathlib import Path

# Add current directory to path for imports

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
sys.path.insert(0, current_dir)

from message_protocol import AgentMessage, MessageType, MessagePriority
from queue_manager import MessageQueueManager


@trace_class
class CodeAnalyzerAgent:
    """Agent that analyzes code files for issues and improvements"""
    
    def __init__(self, agent_id: str, queue_manager: MessageQueueManager):
        self.agent_id = agent_id
        self.queue = queue_manager
        self.capabilities = ["code_analysis", "python", "best_practices"]
        self.is_running = False
    
    @trace_func
    def analyze_file(self, file_path: str) -> dict:
        """Analyze a code file and return findings"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Simple code analysis (in real scenario, this would use AI/LLM)
            issues = []
            suggestions = []
            
            lines = code.split('\n')
            
            # Check for common issues
            if any('TODO' in line or 'FIXME' in line for line in lines):
                issues.append("Contains TODO/FIXME comments that need attention")
            
            if len([line for line in lines if line.strip()]) > 200:
                issues.append("File is quite large (>200 lines) - consider splitting")
            
            if not any('"""' in line or "'''" in line for line in lines):
                issues.append("Missing docstrings - add module/function documentation")
            
            # Check for potential improvements
            if 'except:' in code:
                suggestions.append("Use specific exception types instead of bare except")
            
            if code.count('print(') > 3:
                suggestions.append("Consider using logging instead of print statements")
            
            if 'import *' in code:
                suggestions.append("Avoid wildcard imports - import specific functions")
            
            return {
                "file": file_path,
                "lines_of_code": len([line for line in lines if line.strip()]),
                "issues": issues,
                "suggestions": suggestions,
                "complexity": "high" if len(lines) > 150 else "medium" if len(lines) > 50 else "low"
            }
            
        except Exception as e:
            return {
                "file": file_path,
                "error": f"Failed to analyze: {str(e)}"
            }
    
    async def process_messages(self):
        """Process incoming analysis requests"""
        print(f"📊 {self.agent_id} started - ready for code analysis tasks")
        
        while self.is_running:
            try:
                messages = self.queue.get_messages(self.agent_id, limit=5)
                
                for message in messages:
                    if message.message_type == MessageType.TASK_REQUEST:
                        await self.handle_analysis_request(message)
                        self.queue.mark_processed(message.message_id, self.agent_id)
                
                await asyncio.sleep(2)  # Check for new messages every 2 seconds
                
            except Exception as e:
                print(f"❌ {self.agent_id} error: {e}")
                await asyncio.sleep(5)
    
    async def handle_analysis_request(self, message: AgentMessage):
        """Handle a code analysis request"""
        task_data = message.content
        file_path = task_data.get('file_path')
        
        print(f"🔍 {self.agent_id} analyzing: {file_path}")
        
        # Simulate analysis time
        await asyncio.sleep(1)
        
        analysis = self.analyze_file(file_path)
        
        # Send results back
        response = AgentMessage(
            message_id=f"analysis_{int(time.time())}_{self.agent_id}",
            from_agent=self.agent_id,
            to_agent=message.from_agent,
            message_type=MessageType.TASK_RESPONSE,
            content={
                "task_id": task_data.get('task_id'),
                "analysis": analysis,
                "agent_capabilities": self.capabilities
            },
            parent_message_id=message.message_id
        )
        
        self.queue.send_message(response)
        print(f"✅ {self.agent_id} completed analysis of {file_path}")


@trace_class
class CodeFixerAgent:
    """Agent that suggests and applies code improvements"""
    
    def __init__(self, agent_id: str, queue_manager: MessageQueueManager):
        self.agent_id = agent_id
        self.queue = queue_manager
        self.capabilities = ["code_improvement", "refactoring", "python"]
        self.is_running = False
    
    @trace_func
    def generate_improvements(self, analysis: dict) -> list:
        """Generate specific improvement suggestions based on analysis"""
        improvements = []
        
        file_path = analysis.get('file', '')
        issues = analysis.get('issues', [])
        suggestions = analysis.get('suggestions', [])
        
        for issue in issues:
            if "TODO/FIXME" in issue:
                improvements.append({
                    "type": "cleanup",
                    "description": f"Review and resolve TODO/FIXME comments in {file_path}",
                    "priority": "medium"
                })
            
            if "large" in issue:
                improvements.append({
                    "type": "refactor",
                    "description": f"Consider splitting {file_path} into smaller modules",
                    "priority": "low"
                })
            
            if "docstrings" in issue:
                improvements.append({
                    "type": "documentation",
                    "description": f"Add comprehensive docstrings to {file_path}",
                    "priority": "high"
                })
        
        for suggestion in suggestions:
            if "exception" in suggestion:
                improvements.append({
                    "type": "error_handling",
                    "description": f"Improve exception handling in {file_path}",
                    "priority": "high"
                })
            
            if "logging" in suggestion:
                improvements.append({
                    "type": "logging",
                    "description": f"Replace print statements with proper logging in {file_path}",
                    "priority": "medium"
                })
        
        return improvements
    
    async def process_messages(self):
        """Process incoming improvement requests"""
        print(f"🔧 {self.agent_id} started - ready to suggest improvements")
        
        while self.is_running:
            try:
                messages = self.queue.get_messages(self.agent_id, limit=5)
                
                for message in messages:
                    if message.message_type == MessageType.TASK_REQUEST:
                        await self.handle_improvement_request(message)
                        self.queue.mark_processed(message.message_id, self.agent_id)
                
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"❌ {self.agent_id} error: {e}")
                await asyncio.sleep(5)
    
    async def handle_improvement_request(self, message: AgentMessage):
        """Handle a code improvement request"""
        task_data = message.content
        analysis = task_data.get('analysis', {})
        
        print(f"🔧 {self.agent_id} generating improvements for: {analysis.get('file', 'unknown')}")
        
        # Simulate improvement generation time
        await asyncio.sleep(1.5)
        
        improvements = self.generate_improvements(analysis)
        
        # Send results back
        response = AgentMessage(
            message_id=f"improvements_{int(time.time())}_{self.agent_id}",
            from_agent=self.agent_id,
            to_agent=message.from_agent,
            message_type=MessageType.TASK_RESPONSE,
            content={
                "task_id": task_data.get('task_id'),
                "file": analysis.get('file'),
                "improvements": improvements,
                "agent_capabilities": self.capabilities
            },
            parent_message_id=message.message_id
        )
        
        self.queue.send_message(response)
        print(f"✅ {self.agent_id} generated {len(improvements)} improvements")


@trace_class
class CoordinatorAgent:
    """Supervisor agent that coordinates the code review process"""
    
    def __init__(self, agent_id: str, queue_manager: MessageQueueManager):
        self.agent_id = agent_id
        self.queue = queue_manager
        self.capabilities = ["coordination", "task_management", "code_review"]
        self.active_tasks = {}
        self.results = {}
    
    async def coordinate_code_review(self, target_directory: str):
        """Coordinate a multi-agent code review of a directory"""
        print(f"🎯 {self.agent_id} starting code review of: {target_directory}")
        
        # Find Python files to analyze (limit to first 3 for demo)
        python_files = list(Path(target_directory).rglob("*.py"))[:3]
        if not python_files:
            print(f"❌ No Python files found in {target_directory}")
            return
        
        print(f"📁 Found {len(python_files)} Python files to analyze (limited to 3 for demo)")
        for file in python_files:
            print(f"   • {file.name}")
        
        # Step 1: Send analysis tasks to analyzer agents
        analysis_tasks = []
        for i, file_path in enumerate(python_files):
            task_id = f"analysis_task_{i}_{int(time.time())}"
            
            task_message = AgentMessage(
                message_id=f"coord_{task_id}",
                from_agent=self.agent_id,
                to_agent="code_analyzer_001",  # Send to analyzer
                message_type=MessageType.TASK_REQUEST,
                content={
                    "task_id": task_id,
                    "task_type": "code_analysis",
                    "file_path": str(file_path),
                    "description": f"Analyze {file_path.name} for issues and improvements"
                },
                priority=MessagePriority.HIGH
            )
            
            success = self.queue.send_message(task_message)
            print(f"📤 Sent analysis task for {file_path.name}: {success}")
            
            analysis_tasks.append(task_id)
            self.active_tasks[task_id] = {"type": "analysis", "file": str(file_path), "status": "pending"}
        
        print(f"📤 Sent {len(analysis_tasks)} analysis tasks")
        
        # Step 2: Wait for analysis results and coordinate improvements
        await self.monitor_and_coordinate_tasks(analysis_tasks)
        
        # Step 3: Generate final report
        await self.generate_final_report()
    
    async def monitor_and_coordinate_tasks(self, task_ids: list):
        """Monitor task progress and coordinate follow-up work"""
        completed_analyses = 0
        improvement_tasks = []
        max_wait_time = 30  # Maximum wait time in seconds
        start_time = time.time()
        
        print(f"⏳ Waiting for {len(task_ids)} analysis tasks to complete...")
        
        while completed_analyses < len(task_ids) and (time.time() - start_time) < max_wait_time:
            messages = self.queue.get_messages(self.agent_id, limit=10)
            
            for message in messages:
                if message.message_type == MessageType.TASK_RESPONSE:
                    task_id = message.content.get('task_id')
                    if task_id in task_ids:
                        await self.handle_task_response(message, improvement_tasks)
                        completed_analyses += 1
                        print(f"✅ Task {completed_analyses}/{len(task_ids)} completed")
                        self.queue.mark_processed(message.message_id, self.agent_id)
            
            await asyncio.sleep(0.5)  # Check more frequently
        
        if completed_analyses < len(task_ids):
            print(f"⚠️ Timeout: Only {completed_analyses}/{len(task_ids)} analysis tasks completed")
        else:
            print(f"✅ All {len(task_ids)} analysis tasks completed")
        
        # Wait for improvement suggestions (with timeout)
        if improvement_tasks:
            print(f"⏳ Waiting for {len(improvement_tasks)} improvement tasks...")
            completed_improvements = 0
            improvement_start = time.time()
            
            while (completed_improvements < len(improvement_tasks) and 
                   (time.time() - improvement_start) < max_wait_time):
                messages = self.queue.get_messages(self.agent_id, limit=10)
                
                for message in messages:
                    if (message.message_type == MessageType.TASK_RESPONSE and 
                        message.content.get('task_id') in improvement_tasks):
                        await self.handle_improvement_response(message)
                        completed_improvements += 1
                        print(f"✅ Improvement {completed_improvements}/{len(improvement_tasks)} completed")
                        self.queue.mark_processed(message.message_id, self.agent_id)
                
                await asyncio.sleep(0.5)
            
            if completed_improvements < len(improvement_tasks):
                print(f"⚠️ Timeout: Only {completed_improvements}/{len(improvement_tasks)} improvement tasks completed")
    
    async def handle_task_response(self, message: AgentMessage, improvement_tasks: list):
        """Handle analysis response and request improvements if needed"""
        content = message.content
        task_id = content.get('task_id')
        analysis = content.get('analysis', {})
        
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "completed"
            self.results[task_id] = analysis
            
            file_path = analysis.get('file', '')
            issues = len(analysis.get('issues', []))
            suggestions = len(analysis.get('suggestions', []))
            
            print(f"📊 Analysis complete: {Path(file_path).name} - {issues} issues, {suggestions} suggestions")
            
            # If there are issues/suggestions, request improvements
            if issues > 0 or suggestions > 0:
                improvement_task_id = f"improvement_{task_id}"
                
                improvement_message = AgentMessage(
                    message_id=f"coord_improve_{improvement_task_id}",
                    from_agent=self.agent_id,
                    to_agent="code_fixer_001",
                    message_type=MessageType.TASK_REQUEST,
                    content={
                        "task_id": improvement_task_id,
                        "task_type": "code_improvement",
                        "analysis": analysis,
                        "description": f"Generate improvements for {Path(file_path).name}"
                    },
                    priority=MessagePriority.MEDIUM
                )
                
                self.queue.send_message(improvement_message)
                improvement_tasks.append(improvement_task_id)
                self.active_tasks[improvement_task_id] = {"type": "improvement", "file": file_path, "status": "pending"}
    
    async def handle_improvement_response(self, message: AgentMessage):
        """Handle improvement response"""
        content = message.content
        task_id = content.get('task_id')
        improvements = content.get('improvements', [])
        file_path = content.get('file', '')
        
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "completed"
            self.results[task_id] = {"improvements": improvements, "file": file_path}
            
            print(f"🔧 Improvements ready: {Path(file_path).name} - {len(improvements)} suggestions")
    
    async def generate_final_report(self):
        """Generate and display final code review report"""
        print("\n" + "="*60)
        print("📋 FINAL CODE REVIEW REPORT")
        print("="*60)
        
        total_files = 0
        total_issues = 0
        total_suggestions = 0
        total_improvements = 0
        
        # Summary statistics
        for task_id, result in self.results.items():
            if 'issues' in result:  # Analysis result
                total_files += 1
                total_issues += len(result.get('issues', []))
                total_suggestions += len(result.get('suggestions', []))
            elif 'improvements' in result:  # Improvement result
                total_improvements += len(result.get('improvements', []))
        
        print(f"📊 SUMMARY:")
        print(f"   Files analyzed: {total_files}")
        print(f"   Issues found: {total_issues}")
        print(f"   Suggestions: {total_suggestions}")
        print(f"   Improvements generated: {total_improvements}")
        
        # Detailed results
        print(f"\n📝 DETAILED RESULTS:")
        
        for task_id, result in self.results.items():
            if 'issues' in result:  # Analysis result
                file_name = Path(result.get('file', '')).name
                print(f"\n🔍 {file_name}:")
                print(f"   Lines of code: {result.get('lines_of_code', 'unknown')}")
                print(f"   Complexity: {result.get('complexity', 'unknown')}")
                
                if result.get('issues'):
                    print(f"   Issues ({len(result['issues'])}):")
                    for issue in result['issues']:
                        print(f"     • {issue}")
                
                if result.get('suggestions'):
                    print(f"   Suggestions ({len(result['suggestions'])}):")
                    for suggestion in result['suggestions']:
                        print(f"     • {suggestion}")
        
        # Improvement recommendations
        print(f"\n🔧 IMPROVEMENT RECOMMENDATIONS:")
        
        for task_id, result in self.results.items():
            if 'improvements' in result:
                file_name = Path(result.get('file', '')).name
                improvements = result.get('improvements', [])
                
                if improvements:
                    print(f"\n🎯 {file_name}:")
                    for improvement in improvements:
                        priority = improvement.get('priority', 'medium')
                        emoji = "🔥" if priority == "high" else "⚡" if priority == "medium" else "💡"
                        print(f"   {emoji} [{priority.upper()}] {improvement.get('description', '')}")
        
        print("\n" + "="*60)
        print("✅ Code review completed by AI agent coordination!")
        print("="*60)


async def run_multi_agent_demo():
    """Run the multi-agent code review demonstration"""
    print("🤖 Multi-Agent Code Review System Starting...")
    print("="*50)
    
    # Initialize Redis connection
    try:
        queue = MessageQueueManager(use_mock=False)
        print("✅ Connected to Redis for agent coordination")
    except Exception as e:
        print(f"⚠️ Redis unavailable ({e}), using mock mode")
        queue = MessageQueueManager(use_mock=True)
    
    # Create agent instances
    coordinator = CoordinatorAgent("coordinator_001", queue)
    analyzer = CodeAnalyzerAgent("code_analyzer_001", queue)
    fixer = CodeFixerAgent("code_fixer_001", queue)
    
    # Start agent processing tasks
    agents = [
        asyncio.create_task(analyzer.process_messages()),
        asyncio.create_task(fixer.process_messages())
    ]
    
    # Start the agents
    analyzer.is_running = True
    fixer.is_running = True
    
    try:
        # Run the code review coordination
        target_dir = "helpers/agent_communication"
        await coordinator.coordinate_code_review(target_dir)
        
        # Let agents finish any remaining work
        await asyncio.sleep(2)
        
    finally:
        # Stop all agents
        analyzer.is_running = False
        fixer.is_running = False
        
        # Cancel background tasks
        for task in agents:
            task.cancel()
        
        print("\n🏁 Multi-agent demo completed!")


if __name__ == "__main__":
    asyncio.run(run_multi_agent_demo())
