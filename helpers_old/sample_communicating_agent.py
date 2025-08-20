"""
Sample Communicating Agent
=========================

This demonstrates how to use the AgentCommunicationMixin to create agents
that can communicate with the supervisor via Redis messaging.

This serves as both:
1. A working example of Redis agent communication
2. A template for converting existing agents to use Redis communication
"""

import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ..helpers.agent_communication.agent_communication_mixin import CommunicatingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SampleAnalysisAgent(CommunicatingAgent):
    """
    Sample agent that demonstrates Redis communication capabilities.
    
    This agent simulates code analysis tasks while showing how to:
    - Register with the supervisor
    - Send progress updates during task execution
    - Report errors when they occur
    - Send task completion responses
    """
    
    def __init__(self, agent_id: str = "analysis-agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="analysis_agent",
            capabilities=["code_analysis", "security_review", "performance_analysis"]
        )
        
        self.analysis_tools = {
            "static_analysis": True,
            "security_scan": True,
            "performance_check": True,
            "dependency_audit": True
        }
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an analysis task with full communication to supervisor.
        
        This method demonstrates the full lifecycle of agent communication:
        1. Task received and validated
        2. Progress updates sent during execution
        3. Error reporting if issues occur
        4. Final task completion response
        """
        task_id = task.get("task_id", f"task_{int(time.time())}")
        task_type = task.get("type", "unknown")
        
        logger.info(f"🔍 Starting {task_type} analysis task: {task_id}")
        
        try:
            # Send initial progress update
            self.send_progress_update(
                task_id=task_id,
                progress_percentage=0,
                current_step="Initializing analysis",
                details={"task_type": task_type, "tools_available": list(self.analysis_tools.keys())}
            )
            
            # Simulate different types of analysis
            if task_type == "code_analysis":
                return self._perform_code_analysis(task, task_id)
            elif task_type == "security_review":
                return self._perform_security_review(task, task_id)
            elif task_type == "performance_analysis":
                return self._perform_performance_analysis(task, task_id)
            else:
                # Report error for unknown task type
                self.send_error_report(
                    error_type="unknown_task_type",
                    error_message=f"Unknown task type: {task_type}",
                    task_id=task_id,
                    severity="medium"
                )
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": f"Unknown task type: {task_type}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            # Report any unexpected errors
            self.send_error_report(
                error_type="execution_error",
                error_message=str(e),
                task_id=task_id,
                severity="high"
            )
            raise
    
    def _perform_code_analysis(self, task: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """Perform code analysis with progress updates."""
        logger.info(f"🔍 Performing code analysis for task {task_id}")
        
        steps = [
            ("Scanning source files", 20),
            ("Analyzing code structure", 40),
            ("Checking coding standards", 60),
            ("Generating analysis report", 80),
            ("Finalizing results", 100)
        ]
        
        results = {
            "files_analyzed": 0,
            "issues_found": [],
            "recommendations": []
        }
        
        for step_name, progress in steps:
            # Send progress update for each step
            self.send_progress_update(
                task_id=task_id,
                progress_percentage=progress,
                current_step=step_name,
                details={"files_scanned": results["files_analyzed"]}
            )
            
            # Simulate work
            time.sleep(1)
            
            # Simulate findings based on step
            if "scanning" in step_name.lower():
                results["files_analyzed"] = 25
            elif "analyzing" in step_name.lower():
                results["issues_found"].append({
                    "type": "complexity",
                    "severity": "medium",
                    "message": "High cyclomatic complexity detected in function process_data()"
                })
            elif "standards" in step_name.lower():
                results["recommendations"].append("Consider using type hints for better code clarity")
        
        # Send final task completion
        final_result = {
            "task_id": task_id,
            "status": "completed",
            "analysis_type": "code_analysis",
            "results": results,
            "execution_time": 5.0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Send the completion response to supervisor
        self.send_task_response(
            task_id=task_id,
            status="completed",
            result=final_result
        )
        
        return final_result
    
    def _perform_security_review(self, task: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """Perform security review with progress updates."""
        logger.info(f"🔒 Performing security review for task {task_id}")
        
        steps = [
            ("Scanning for vulnerabilities", 25),
            ("Checking dependencies", 50),
            ("Analyzing authentication", 75),
            ("Generating security report", 100)
        ]
        
        security_findings = []
        
        for step_name, progress in steps:
            self.send_progress_update(
                task_id=task_id,
                progress_percentage=progress,
                current_step=step_name
            )
            
            time.sleep(1)
            
            # Simulate security findings
            if "vulnerabilities" in step_name.lower():
                security_findings.append({
                    "type": "injection",
                    "severity": "high",
                    "description": "Potential SQL injection vulnerability detected"
                })
            elif "dependencies" in step_name.lower():
                security_findings.append({
                    "type": "outdated_dependency",
                    "severity": "medium",
                    "description": "3 dependencies have known security vulnerabilities"
                })
        
        final_result = {
            "task_id": task_id,
            "status": "completed",
            "analysis_type": "security_review",
            "results": {
                "vulnerabilities_found": len(security_findings),
                "findings": security_findings,
                "risk_level": "medium"
            },
            "execution_time": 4.0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.send_task_response(
            task_id=task_id,
            status="completed",
            result=final_result
        )
        
        return final_result
    
    def _perform_performance_analysis(self, task: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """Perform performance analysis with simulated error."""
        logger.info(f"⚡ Performing performance analysis for task {task_id}")
        
        # Simulate an error during performance analysis
        self.send_progress_update(
            task_id=task_id,
            progress_percentage=30,
            current_step="Profiling application performance"
        )
        
        time.sleep(1)
        
        # Simulate a performance monitoring error
        self.send_error_report(
            error_type="monitoring_failure",
            error_message="Performance monitoring tools are not available",
            task_id=task_id,
            severity="medium"
        )
        
        # Still complete the task with limited results
        final_result = {
            "task_id": task_id,
            "status": "completed_with_warnings",
            "analysis_type": "performance_analysis",
            "results": {
                "basic_metrics": {"response_time": "~200ms", "memory_usage": "~150MB"},
                "warnings": ["Full performance profiling unavailable"]
            },
            "execution_time": 2.0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.send_task_response(
            task_id=task_id,
            status="completed_with_warnings",
            result=final_result
        )
        
        return final_result


class SampleDevelopmentAgent(CommunicatingAgent):
    """
    Sample development agent demonstrating code generation tasks.
    """
    
    def __init__(self, agent_id: str = "development-agent"):
        super().__init__(
            agent_id=agent_id,
            agent_type="development_agent",
            capabilities=["code_generation", "api_development", "testing"]
        )
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a development task."""
        task_id = task.get("task_id", f"dev_task_{int(time.time())}")
        task_type = task.get("type", "code_generation")
        
        logger.info(f"💻 Starting development task: {task_id}")
        
        # Send initial progress
        self.send_progress_update(
            task_id=task_id,
            progress_percentage=0,
            current_step="Setting up development environment"
        )
        
        # Simulate development work
        development_steps = [
            ("Creating project structure", 20),
            ("Generating core modules", 40),
            ("Implementing business logic", 60),
            ("Adding error handling", 80),
            ("Running tests", 100)
        ]
        
        for step_name, progress in development_steps:
            self.send_progress_update(
                task_id=task_id,
                progress_percentage=progress,
                current_step=step_name
            )
            time.sleep(0.8)
        
        # Complete the task
        final_result = {
            "task_id": task_id,
            "status": "completed",
            "task_type": task_type,
            "results": {
                "files_created": ["app.py", "models.py", "utils.py", "tests.py"],
                "lines_of_code": 450,
                "test_coverage": "85%"
            },
            "execution_time": 4.0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.send_task_response(
            task_id=task_id,
            status="completed",
            result=final_result
        )
        
        return final_result


def demo_agent_communication():
    """
    Demonstrate the Redis communication capabilities of the agents.
    """
    print("=== Agent Communication Demo ===")
    print("This demo shows agents communicating with supervisor via Redis")
    print()
    
    # Create analysis agent
    analysis_agent = SampleAnalysisAgent("demo-analysis-agent")
    
    # Create development agent
    dev_agent = SampleDevelopmentAgent("demo-dev-agent")
    
    print(f"✅ Created agents:")
    print(f"   - {analysis_agent.agent_id} ({analysis_agent.agent_type})")
    print(f"   - {dev_agent.agent_id} ({dev_agent.agent_type})")
    print()
    
    # Demo tasks
    demo_tasks = [
        {
            "task_id": "analysis_001",
            "type": "code_analysis",
            "description": "Analyze codebase for quality and standards"
        },
        {
            "task_id": "security_001", 
            "type": "security_review",
            "description": "Review code for security vulnerabilities"
        },
        {
            "task_id": "dev_001",
            "type": "code_generation",
            "description": "Generate API endpoints for user management"
        }
    ]
    
    print("🚀 Executing demo tasks...")
    print("   (Watch the logs for Redis communication messages)")
    print()
    
    # Execute tasks
    for task in demo_tasks:
        print(f"📋 Executing: {task['description']}")
        
        if "analysis" in task["type"] or "security" in task["type"]:
            result = analysis_agent.execute_task(task)
        else:
            result = dev_agent.execute_task(task)
        
        print(f"   ✅ {task['task_id']}: {result['status']}")
        print()
    
    print("🎯 Demo completed!")
    print()
    print("Check the Redis messages to see the full communication flow:")
    print("   - Agent registrations")
    print("   - Task progress updates")
    print("   - Error reports")
    print("   - Task completion responses")
    print("   - Heartbeat messages")


if __name__ == "__main__":
    demo_agent_communication()
