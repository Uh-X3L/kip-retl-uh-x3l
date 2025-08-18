"""
Agent Manager - High-level interface for managing all Azure AI agents
Provides unified access to all agent types with intelligent routing and management.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from .agent_registry import AgentRegistry
from .web_research_analyst import WebResearchAnalyst
from .project_planner import ProjectPlanner
from .devops_agent import DevOpsAgent
from .worker_agent import WorkerAgent
from .testing_agent import TestingAgent
from .documentation_agent import DocumentationAgent


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


logger = logging.getLogger(__name__)

@trace_class
class AgentManager:
    """
    High-level manager for all Azure AI agents.
    Provides unified interface and intelligent routing to specialized agents.
    """
    
    def __init__(self, project_client):
        """Initialize the agent manager."""
        self.project_client = project_client
        self.registry = AgentRegistry(project_client)
        self.active_agents = {}
    
    @trace_func
    def get_research_agent(self, **kwargs) -> WebResearchAnalyst:
        """Get or create a Web Research Analyst agent."""
        agent_key = "web_research_analyst"
        
        if agent_key not in self.active_agents:
            self.active_agents[agent_key] = self.registry.get_agent("web_research_analyst", **kwargs)
        
        return self.active_agents[agent_key]
    
    @trace_func
    def get_planner_agent(self, **kwargs) -> ProjectPlanner:
        """Get or create a Project Planner agent."""
        agent_key = "project_planner"
        
        if agent_key not in self.active_agents:
            self.active_agents[agent_key] = self.registry.get_agent("project_planner", **kwargs)
        
        return self.active_agents[agent_key]
    
    @trace_func
    def get_devops_agent(self, **kwargs) -> DevOpsAgent:
        """Get or create a DevOps agent."""
        agent_key = "devops_agent"
        
        if agent_key not in self.active_agents:
            self.active_agents[agent_key] = self.registry.get_agent("devops_agent", **kwargs)
        
        return self.active_agents[agent_key]
    
    @trace_func
    def get_worker_agent(self, **kwargs) -> WorkerAgent:
        """Get or create a Worker agent."""
        agent_key = "worker_agent"
        
        if agent_key not in self.active_agents:
            self.active_agents[agent_key] = self.registry.get_agent("worker_agent", **kwargs)
        
        return self.active_agents[agent_key]
    
    @trace_func
    def get_testing_agent(self, **kwargs) -> TestingAgent:
        """Get or create a Testing agent."""
        agent_key = "testing_agent"
        
        if agent_key not in self.active_agents:
            self.active_agents[agent_key] = self.registry.get_agent("testing_agent", **kwargs)
        
        return self.active_agents[agent_key]
    
    @trace_func
    def get_documentation_agent(self, **kwargs) -> DocumentationAgent:
        """Get or create a Documentation agent."""
        agent_key = "documentation_agent"
        
        if agent_key not in self.active_agents:
            self.active_agents[agent_key] = self.registry.get_agent("documentation_agent", **kwargs)
        
        return self.active_agents[agent_key]
    
    @trace_func
    def research_and_plan_project(self, project_description: str, research_depth: str = "comprehensive",
                                 methodology: str = "agile", timeline: str = None) -> Dict[str, Any]:
        """
        Conduct research and create project plan using multiple agents.
        
        Args:
            project_description: Description of the project
            research_depth: Depth of research to conduct
            methodology: Project methodology to use
            timeline: Desired timeline
        
        Returns:
            Combined research and planning results
        """
        try:
            logger.info(f"🚀 Starting research and planning for: {project_description[:100]}...")
            
            # Phase 1: Research
            research_agent = self.get_research_agent()
            research_results = research_agent.research_topic(
                topic=project_description,
                depth=research_depth
            )
            
            # Phase 2: Planning based on research
            planning_agent = self.get_planner_agent()
            project_plan = planning_agent.create_project_plan(
                project_description=f"{project_description}\n\nResearch Context:\n{research_results}",
                timeline=timeline,
                methodology=methodology
            )
            
            return {
                "success": True,
                "research_results": research_results,
                "project_plan": project_plan,
                "agents_used": ["web_research_analyst", "project_planner"],
                "methodology": methodology,
                "research_depth": research_depth
            }
            
        except Exception as e:
            logger.error(f"Failed to research and plan project: {e}")
            return {
                "success": False,
                "error": str(e),
                "agents_used": []
            }
    
    @trace_func
    def create_devops_solution(self, project_type: str, requirements: Dict = None) -> Dict[str, Any]:
        """
        Create comprehensive DevOps solution for a project.
        
        Args:
            project_type: Type of project
            requirements: Specific DevOps requirements
        
        Returns:
            Complete DevOps solution
        """
        try:
            logger.info(f"🔧 Creating DevOps solution for {project_type}...")
            
            devops_agent = self.get_devops_agent()
            
            # Create comprehensive DevOps solutions
            solutions = {}
            
            # CI/CD Pipeline
            solutions["cicd_pipeline"] = devops_agent.create_cicd_pipeline(
                project_type=project_type,
                requirements=requirements
            )
            
            # Infrastructure as Code
            solutions["infrastructure"] = devops_agent.create_infrastructure_code(
                infrastructure_type="terraform",
                services=requirements.get("services", []) if requirements else []
            )
            
            # Docker Strategy
            solutions["docker_strategy"] = devops_agent.design_docker_strategy(
                application_type=project_type,
                requirements=requirements
            )
            
            # Monitoring Setup
            solutions["monitoring"] = devops_agent.create_monitoring_setup(
                application_stack=project_type,
                alert_requirements=requirements.get("alerts") if requirements else None
            )
            
            # Git Workflow Optimization
            solutions["git_workflow"] = devops_agent.optimize_git_workflow(
                team_size=requirements.get("team_size", "small") if requirements else "small",
                project_type=project_type,
                current_issues=requirements.get("git_issues", []) if requirements else []
            )
            
            return {
                "success": True,
                "solutions": solutions,
                "agent_used": "devops_agent",
                "project_type": project_type
            }
            
        except Exception as e:
            logger.error(f"Failed to create DevOps solution: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_used": "devops_agent"
            }
    
    @trace_func
    def analyze_project_with_all_agents(self, project_description: str, 
                                       include_devops: bool = True) -> Dict[str, Any]:
        """
        Analyze project with all available agents for comprehensive insights.
        
        Args:
            project_description: Description of the project
            include_devops: Whether to include DevOps analysis
        
        Returns:
            Complete multi-agent analysis
        """
        try:
            logger.info(f"🎯 Comprehensive analysis for: {project_description[:100]}...")
            
            results = {
                "success": True,
                "agents_used": [],
                "analysis": {}
            }
            
            # Research Analysis
            research_agent = self.get_research_agent()
            results["analysis"]["research"] = {
                "market_research": research_agent.research_topic(
                    topic=f"Market analysis for: {project_description}",
                    depth="comprehensive"
                ),
                "competitive_analysis": research_agent.competitive_analysis(
                    company_or_product=project_description
                ),
                "industry_trends": research_agent.industry_trends_analysis(
                    industry=project_description.split()[0] if project_description else "technology"
                )
            }
            results["agents_used"].append("web_research_analyst")
            
            # Planning Analysis
            planning_agent = self.get_planner_agent()
            results["analysis"]["planning"] = {
                "project_plan": planning_agent.create_project_plan(
                    project_description=project_description,
                    methodology="agile"
                ),
                "risk_assessment": planning_agent.assess_project_risks(
                    project_description=project_description
                ),
                "milestone_roadmap": planning_agent.create_milestone_roadmap(
                    project_description=project_description
                )
            }
            results["agents_used"].append("project_planner")
            
            # DevOps Analysis (if requested)
            if include_devops:
                devops_agent = self.get_devops_agent()
                results["analysis"]["devops"] = {
                    "deployment_strategy": devops_agent.create_deployment_strategy(
                        application_type=project_description,
                        environments=["dev", "staging", "production"]
                    ),
                    "infrastructure_recommendations": devops_agent.create_infrastructure_code(
                        infrastructure_type="terraform",
                        services=["web_app", "database", "monitoring"]
                    )
                }
                results["agents_used"].append("devops_agent")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to analyze project with all agents: {e}")
            return {
                "success": False,
                "error": str(e),
                "agents_used": []
            }
    
    @trace_func
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all active agents."""
        try:
            status = {
                "active_agents": {},
                "registry_stats": self.registry.get_agent_statistics(),
                "manager_stats": {
                    "cached_agents": len(self.active_agents),
                    "agent_types_cached": list(self.active_agents.keys())
                }
            }
            
            # Get info for each active agent
            for agent_key, agent in self.active_agents.items():
                status["active_agents"][agent_key] = agent.get_agent_info()
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get agent status: {e}")
            return {"error": str(e)}
    
    @trace_func
    def cleanup_agents(self, dry_run: bool = False) -> Dict[str, Any]:
        """Clean up inactive agents and optimize performance."""
        try:
            logger.info("🧹 Starting agent cleanup...")
            
            # Clean up registry
            cleanup_report = self.registry.cleanup_inactive_agents(dry_run=dry_run)
            
            # Optimize registry
            optimization_report = self.registry.optimize_registry()
            
            # Clear cached agents if not dry run
            if not dry_run:
                cleared_cache = len(self.active_agents)
                self.active_agents.clear()
            else:
                cleared_cache = 0
            
            return {
                "success": True,
                "cleanup_report": cleanup_report,
                "optimization_report": optimization_report,
                "cleared_cache_count": cleared_cache,
                "dry_run": dry_run
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup agents: {e}")
            return {
                "success": False,
                "error": str(e),
                "dry_run": dry_run
            }
    
    @trace_func
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive report of all agent activities."""
        try:
            # Get usage report from registry
            usage_report = self.registry.generate_usage_report()
            
            # Add manager-level information
            manager_info = f"""
## Manager Status

**Active Agent Cache:** {len(self.active_agents)} agents
**Cached Agent Types:** {', '.join(self.active_agents.keys()) if self.active_agents else 'None'}

## Available Agent Types

1. **Web Research Analyst** - Market research, competitive analysis, industry trends
2. **Project Planner** - Project planning, risk assessment, resource allocation
3. **DevOps Agent** - CI/CD, infrastructure, deployment strategies

## Agent Capabilities

### Research Agent
- Deep market research and analysis
- Competitive landscape evaluation  
- Industry trend identification
- Fact-checking and verification

### Planning Agent
- Comprehensive project planning
- Sprint planning and management
- Risk assessment and mitigation
- Resource optimization

### DevOps Agent
- CI/CD pipeline design
- Infrastructure as Code templates
- Container orchestration strategies
- Monitoring and deployment automation

"""
            
            return usage_report + manager_info
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {e}")
            return f"Error generating report: {str(e)}"
    
    @trace_func
    def shutdown(self):
        """Properly shutdown all agents and clean up resources."""
        try:
            logger.info("🔌 Shutting down Agent Manager...")
            
            # Cleanup all active agents
            for agent_key, agent in self.active_agents.items():
                try:
                    agent.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up agent {agent_key}: {e}")
            
            # Clear cache
            self.active_agents.clear()
            
            logger.info("✅ Agent Manager shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.shutdown()
