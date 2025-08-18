"""
Azure AI Agents Module - Specialized agents for different workflows

This module provides a comprehensive agent system with intelligent reuse capabilities:

- BaseAgent: Foundation class with Azure agent reuse logic
- WebResearchAnalyst: Specialized for research and competitive analysis  
- ProjectPlanner: Specialized for project planning and management
- DevOpsAgent: Specialized for CI/CD, infrastructure, and deployment
- AgentRegistry: Centralized agent management and reuse system
- AgentManager: High-level interface for all agent operations

Usage:
```python
from helpers.agents import AgentManager

# Initialize with Azure AI Projects client
with AgentManager(project_client) as manager:
    # Get specialized agents
    research_agent = manager.get_research_agent()
    planner_agent = manager.get_planner_agent()
    devops_agent = manager.get_devops_agent()
    
    # Use high-level workflows
    results = manager.research_and_plan_project(
        project_description="Build a web application",
        research_depth="comprehensive"
    )
    
    # Get DevOps solutions
    devops_solution = manager.create_devops_solution(
        project_type="python_web_app"
    )
```

Key Features:
- ♻️ Intelligent agent reuse to avoid redundant creation
- 📊 Comprehensive usage tracking and analytics  
- 🧹 Automatic cleanup of inactive agents
- 🎯 Specialized agents for different domains
- 🔄 Multi-agent workflows for complex tasks
- 📈 Performance optimization and monitoring
"""

from .base_agent import BaseAgent
from .web_research_analyst import WebResearchAnalyst
from .project_planner import ProjectPlanner
from .devops_agent import DevOpsAgent
from .agent_registry import AgentRegistry
from .agent_manager import AgentManager


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


__version__ = "1.0.0"

__all__ = [
    "BaseAgent",
    "WebResearchAnalyst", 
    "ProjectPlanner",
    "DevOpsAgent",
    "AgentRegistry",
    "AgentManager"
]

# Agent type constants for easy reference
AGENT_TYPES = {
    "RESEARCH": "web_research_analyst",
    "PLANNER": "project_planner", 
    "DEVOPS": "devops_agent",
    "RESEARCHER": "researcher",  # alias
    "SPECIALIST": "devops_specialist"  # alias
}

# Quick access functions
@trace_func
def create_agent_manager(project_client):
    """
    Create and return an AgentManager instance.
    
    Args:
        project_client: Azure AI Projects client
    
    Returns:
        AgentManager instance
    """
    return AgentManager(project_client)

@trace_func
def get_available_agent_types():
    """Get list of available agent types."""
    return list(AGENT_TYPES.values())

@trace_func
def get_agent_capabilities():
    """Get description of agent capabilities."""
    return {
        "web_research_analyst": {
            "description": "Specialized for web research, competitive analysis, and market insights",
            "capabilities": [
                "Deep market research",
                "Competitive analysis", 
                "Industry trend analysis",
                "Fact verification",
                "Resource curation"
            ]
        },
        "project_planner": {
            "description": "Specialized for project planning, task management, and strategic planning",
            "capabilities": [
                "Project breakdown and planning",
                "Sprint planning and management", 
                "Risk assessment and mitigation",
                "Resource optimization",
                "Timeline and milestone planning"
            ]
        },
        "devops_agent": {
            "description": "Specialized for DevOps practices, CI/CD, and infrastructure automation",
            "capabilities": [
                "CI/CD pipeline design",
                "Infrastructure as Code",
                "Container orchestration",
                "Deployment strategies", 
                "Monitoring and observability",
                "Git workflow optimization"
            ]
        }
    }
