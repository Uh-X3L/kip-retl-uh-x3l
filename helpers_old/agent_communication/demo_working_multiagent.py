#!/usr/bin/env python3
"""
Working Multi-Agent Code Review Demo
===================================

Shows agents coordinating to analyze code - synchronous version that works.
"""

import sys
import os
import time
from pathlib import Path

# Add current directory to path for imports  
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from helpers_old.agent_communication import AgentMessage, MessageType, MessagePriority, MessageQueueManager
except ImportError:
    from message_protocol import AgentMessage, MessageType, MessagePriority
    from queue_manager import MessageQueueManager


class WorkingCodeAnalyzer:
    """Code analyzer that actually works synchronously"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
    
    def analyze_file(self, file_path: str) -> dict:
        """Analyze a Python file and return findings"""
        print(f"🔍 {self.agent_id} analyzing: {Path(file_path).name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            
            # Analyze content
            issues = []
            suggestions = []
            
            # Check for common issues
            if 'TODO' in content or 'FIXME' in content:
                issues.append("Contains TODO/FIXME comments")
            
            if len(code_lines) > 150:
                issues.append("File is large (>150 lines) - consider splitting")
            
            if not ('"""' in content or "'''" in content):
                issues.append("Missing docstrings")
            
            # Check for improvements
            if 'except:' in content:
                suggestions.append("Use specific exception types")
            
            if content.count('print(') > 5:
                suggestions.append("Consider using logging instead of print")
            
            if 'import *' in content:
                suggestions.append("Avoid wildcard imports")
            
            complexity = "high" if len(code_lines) > 100 else "medium" if len(code_lines) > 50 else "low"
            
            analysis = {
                "file": file_path,
                "total_lines": len(lines),
                "code_lines": len(code_lines),
                "complexity": complexity,
                "issues": issues,
                "suggestions": suggestions,
                "score": max(0, 100 - len(issues) * 10 - len(suggestions) * 5)
            }
            
            print(f"✅ {self.agent_id} found {len(issues)} issues, {len(suggestions)} suggestions")
            return analysis
            
        except Exception as e:
            print(f"❌ {self.agent_id} error analyzing {file_path}: {e}")
            return {"file": file_path, "error": str(e)}


class WorkingCodeImprover:
    """Code improver that generates specific recommendations"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
    
    def generate_improvements(self, analysis: dict) -> list:
        """Generate specific improvement recommendations"""
        file_path = analysis.get('file', '')
        file_name = Path(file_path).name
        
        print(f"🔧 {self.agent_id} generating improvements for: {file_name}")
        
        improvements = []
        
        # Generate specific improvements based on analysis
        for issue in analysis.get('issues', []):
            if "TODO/FIXME" in issue:
                improvements.append({
                    "type": "cleanup",
                    "priority": "medium",
                    "description": f"Review and resolve all TODO/FIXME comments in {file_name}",
                    "action": "Search for TODO and FIXME comments and either complete the work or create proper issue tickets"
                })
            
            if "large" in issue:
                improvements.append({
                    "type": "refactor",
                    "priority": "low",
                    "description": f"Break down {file_name} into smaller, focused modules",
                    "action": "Identify logical groupings and extract them into separate files"
                })
            
            if "docstrings" in issue:
                improvements.append({
                    "type": "documentation",
                    "priority": "high",
                    "description": f"Add comprehensive docstrings to {file_name}",
                    "action": "Add module docstring and docstrings for all functions and classes"
                })
        
        for suggestion in analysis.get('suggestions', []):
            if "exception" in suggestion:
                improvements.append({
                    "type": "error_handling",
                    "priority": "high",
                    "description": f"Improve exception handling in {file_name}",
                    "action": "Replace bare 'except:' clauses with specific exception types"
                })
            
            if "logging" in suggestion:
                improvements.append({
                    "type": "logging",
                    "priority": "medium",
                    "description": f"Replace print statements with proper logging in {file_name}",
                    "action": "Import logging module and replace print() calls with appropriate log levels"
                })
            
            if "wildcard" in suggestion:
                improvements.append({
                    "type": "imports",
                    "priority": "medium",
                    "description": f"Fix wildcard imports in {file_name}",
                    "action": "Replace 'from module import *' with specific imports"
                })
        
        print(f"✅ {self.agent_id} generated {len(improvements)} improvements")
        return improvements


class WorkingCoordinator:
    """Coordinator that manages the whole process"""
    
    def __init__(self, agent_id: str, queue_manager: MessageQueueManager):
        self.agent_id = agent_id
        self.queue = queue_manager
        self.analyzer = WorkingCodeAnalyzer("code_analyzer_001")
        self.improver = WorkingCodeImprover("code_improver_001")
    
    def coordinate_review(self, target_dir: str = "."):
        """Coordinate a complete code review"""
        print(f"🎯 {self.agent_id} coordinating code review of: {target_dir}")
        print("="*60)
        
        # Find Python files (limit for demo)
        python_files = [f for f in Path(target_dir).rglob("*.py") if f.is_file()][:3]
        
        if not python_files:
            print("❌ No Python files found")
            return
        
        print(f"📁 Files to analyze ({len(python_files)}):")
        for file in python_files:
            print(f"   • {file.name}")
        print()
        
        all_analyses = []
        all_improvements = []
        
        # Step 1: Analyze each file
        print("🔍 ANALYSIS PHASE")
        print("-" * 20)
        
        for file_path in python_files:
            analysis = self.analyzer.analyze_file(str(file_path))
            all_analyses.append(analysis)
            
            # Send analysis via message queue (for demonstration)
            analysis_msg = AgentMessage(
                message_id=f"analysis_{int(time.time())}",
                from_agent=self.analyzer.agent_id,
                to_agent=self.agent_id,
                message_type=MessageType.TASK_RESPONSE,
                content={"analysis": analysis}
            )
            self.queue.send_message(analysis_msg)
        
        print()
        
        # Step 2: Generate improvements
        print("🔧 IMPROVEMENT PHASE")
        print("-" * 20)
        
        for analysis in all_analyses:
            if 'error' not in analysis:
                improvements = self.improver.generate_improvements(analysis)
                all_improvements.extend(improvements)
                
                # Send improvements via message queue (for demonstration)
                improvement_msg = AgentMessage(
                    message_id=f"improvements_{int(time.time())}",
                    from_agent=self.improver.agent_id,
                    to_agent=self.agent_id,
                    message_type=MessageType.TASK_RESPONSE,
                    content={"improvements": improvements, "file": analysis.get('file')}
                )
                self.queue.send_message(improvement_msg)
        
        print()
        
        # Step 3: Generate comprehensive report
        self.generate_comprehensive_report(all_analyses, all_improvements)
    
    def generate_comprehensive_report(self, analyses: list, improvements: list):
        """Generate detailed final report"""
        print("📋 COMPREHENSIVE CODE REVIEW REPORT")
        print("="*60)
        
        # Summary statistics
        total_files = len(analyses)
        total_lines = sum(a.get('total_lines', 0) for a in analyses if 'error' not in a)
        total_code_lines = sum(a.get('code_lines', 0) for a in analyses if 'error' not in a)
        total_issues = sum(len(a.get('issues', [])) for a in analyses if 'error' not in a)
        total_suggestions = sum(len(a.get('suggestions', [])) for a in analyses if 'error' not in a)
        avg_score = sum(a.get('score', 0) for a in analyses if 'error' not in a) / max(1, total_files)
        
        print(f"📊 OVERVIEW:")
        print(f"   Files analyzed: {total_files}")
        print(f"   Total lines: {total_lines:,} ({total_code_lines:,} code)")
        print(f"   Issues found: {total_issues}")
        print(f"   Suggestions: {total_suggestions}")
        print(f"   Average quality score: {avg_score:.1f}/100")
        print()
        
        # File-by-file analysis
        print(f"🔍 DETAILED ANALYSIS:")
        for analysis in analyses:
            if 'error' in analysis:
                print(f"❌ {Path(analysis['file']).name}: {analysis['error']}")
                continue
            
            file_name = Path(analysis['file']).name
            score = analysis.get('score', 0)
            complexity = analysis.get('complexity', 'unknown')
            
            # Score-based emoji
            if score >= 90:
                emoji = "🟢"
            elif score >= 70:
                emoji = "🟡"
            else:
                emoji = "🔴"
            
            print(f"{emoji} {file_name} (Score: {score}/100, Complexity: {complexity})")
            print(f"   Lines: {analysis.get('total_lines', 0)} total, {analysis.get('code_lines', 0)} code")
            
            issues = analysis.get('issues', [])
            if issues:
                print(f"   Issues ({len(issues)}):")
                for issue in issues:
                    print(f"     • {issue}")
            
            suggestions = analysis.get('suggestions', [])
            if suggestions:
                print(f"   Suggestions ({len(suggestions)}):")
                for suggestion in suggestions:
                    print(f"     • {suggestion}")
            
            if not issues and not suggestions:
                print(f"   ✅ No issues found - code looks good!")
            print()
        
        # Improvement recommendations
        if improvements:
            print(f"🔧 IMPROVEMENT RECOMMENDATIONS ({len(improvements)} total):")
            
            # Group by priority
            high_priority = [i for i in improvements if i.get('priority') == 'high']
            medium_priority = [i for i in improvements if i.get('priority') == 'medium']
            low_priority = [i for i in improvements if i.get('priority') == 'low']
            
            for priority, items in [("HIGH", high_priority), ("MEDIUM", medium_priority), ("LOW", low_priority)]:
                if items:
                    emoji = "🔥" if priority == "HIGH" else "⚡" if priority == "MEDIUM" else "💡"
                    print(f"\n{emoji} {priority} PRIORITY ({len(items)} items):")
                    for item in items:
                        print(f"   • {item.get('description', 'No description')}")
                        if item.get('action'):
                            print(f"     Action: {item['action']}")
        else:
            print(f"✅ No improvements needed - excellent code quality!")
        
        print("\n" + "="*60)
        print(f"✅ Multi-agent code review completed!")
        print(f"📊 Used Redis messaging: {not self.queue.use_mock}")
        print("="*60)


def run_working_demo():
    """Run the working multi-agent demo"""
    print("🤖 Working Multi-Agent Code Review Demo")
    print("🚀 Agents will coordinate via Redis messaging")
    print()
    
    # Initialize queue manager
    try:
        queue = MessageQueueManager(use_mock=False)
        print("✅ Connected to Redis for agent coordination")
    except Exception as e:
        print(f"⚠️ Redis unavailable ({e}), using mock mode")
        queue = MessageQueueManager(use_mock=True)
    
    # Create and run coordinator
    coordinator = WorkingCoordinator("coordinator_001", queue)
    coordinator.coordinate_review(".")
    
    # Show message stats
    if hasattr(queue, 'redis_client') and not queue.use_mock:
        try:
            import subprocess
            result = subprocess.run(['docker', 'exec', 'redis-agent-comm', 'redis-cli', 'XLEN', 'agent_messages'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                msg_count = result.stdout.strip()
                print(f"\n📨 Total messages in Redis: {msg_count}")
        except:
            pass
    
    print("\n🏁 Demo completed successfully!")


if __name__ == "__main__":
    run_working_demo()
