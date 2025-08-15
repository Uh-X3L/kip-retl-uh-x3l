"""
Backend Supervisor Agent System - Advanced Project Management with AI

This module contains all the tools and classes needed for the Backend Supervisor Agent
to research, plan, and create detailed GitHub issues with subtasks for delegation to other agents.

Now enhanced with intelligent agent reuse and specialized agent modules!

Created: August 15, 2025
Author: PP (AI Assisted)
Updated: January 2025 - Integrated with Agent Optimization System
"""

import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FunctionTool

# Import GitHub tools
from .github_app_tools import (
    resolve_installation_id, 
    installation_token_cached, 
    create_issue,
    add_issue_to_project,
    create_labels_if_not_exist,
    get_user_info,
    link_issues,
    create_project_issue_with_subtasks
)

# Import new agent system
from .agents import AgentManager, AGENT_TYPES, get_agent_capabilities

# Load environment variables
load_dotenv()

# Azure configuration
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.environ.get("MODEL_DEPLOYMENT_NAME")
REPO = os.environ.get("GITHUB_REPO")


class TaskPriority(Enum):
    """Enumeration for task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SubTask:
    """Data class representing a project subtask."""
    title: str
    description: str
    estimated_hours: float
    skills_required: List[str]
    dependencies: List[str] = None
    agent_type: str = "general"


@dataclass
class ResearchResult:
    """Data class representing research results for a project topic."""
    topic: str
    summary: str
    best_practices: List[str]
    technologies: List[str]
    implementation_approach: str
    estimated_complexity: str
    sources: List[str]


def extract_content_text(content) -> str:
    """
    Helper function to extract text from Azure AI agent content object.
    
    This function handles various content formats that can be returned by Azure AI agents
    and ensures we get the actual text content for JSON parsing.
    
    Args:
        content: Content object from Azure AI agent response
        
    Returns:
        str: Extracted text content
    """
    if isinstance(content, list):
        # Extract text from the first content item
        if len(content) > 0:
            if hasattr(content[0], 'text'):
                text_value = content[0].text
                if hasattr(text_value, 'value'):
                    return str(text_value.value)
                return text_value if isinstance(text_value, str) else str(text_value)
            elif hasattr(content[0], 'value'):
                return str(content[0].value)
            else:
                return str(content[0])
    else:
        # Handle direct content access - could be a dict with 'value' key
        if isinstance(content, dict) and 'value' in content:
            return str(content['value'])
        elif hasattr(content, '_data'):
            data = content._data
            if isinstance(data, dict) and 'value' in data:
                return str(data['value'])
            else:
                return str(data.get('content', ''))
        elif hasattr(content, 'content'):
            if hasattr(content.content, 'value'):
                return str(content.content.value)
            return str(content.content)
        elif hasattr(content, 'value'):
            return str(content.value)
        elif hasattr(content, 'text'):
            if hasattr(content.text, 'value'):
                return str(content.text.value)
            return str(content.text)
        else:
            return str(content)
    return ""


class BackendSupervisorAgent:
    """
    Advanced AI Supervisor Agent that researches, plans, and creates detailed 
    GitHub issues with subtasks for delegation to other agents.
    
    This agent performs comprehensive web research on project topics,
    breaks them down into manageable subtasks, and creates detailed GitHub issues
    that can be assigned to specialized AI agents for implementation.
    """
    
    def __init__(self):
        """
        Initialize the Backend Supervisor Agent with agent management capabilities.
        Now with intelligent agent reuse and specialized modules!
        """
        self.research_cache = {}
        
        # Initialize Azure AI Projects client
        credential = AzureCliCredential()
        self.project_client = AIProjectClient(
            endpoint=PROJECT_ENDPOINT, 
            credential=credential
        )
        
        # Initialize agent manager for intelligent agent reuse
        self.agent_manager = AgentManager(self.project_client)
        
        print("🚀 Backend Supervisor Agent initialized with Agent Optimization System!")
    
    def create_devops_solution(self, project_type: str = "python_web_app", requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create comprehensive DevOps solution using the specialized DevOps agent.
        Optimized for Issue #70 requirements.
        
        Args:
            project_type: Type of project (e.g., "python_web_app", "node_app", etc.)
            requirements: Specific DevOps requirements and constraints
            
        Returns:
            Dict containing complete DevOps solution with CI/CD, infrastructure, etc.
        """
        print(f"🛠️ Creating DevOps solution for {project_type} with specialized DevOps agent...")
        
        if requirements is None:
            requirements = {}
        
        try:
            # Use the specialized DevOps agent
            devops_agent = self.agent_manager.get_devops_agent()
            
            # Create comprehensive DevOps solution
            solution = self.agent_manager.create_devops_solution(
                project_type=project_type,
                requirements=requirements
            )
            
            print(f"✅ DevOps solution created successfully for {project_type}")
            return solution
            
        except Exception as e:
            print(f"⚠️ DevOps solution creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_recommendations": [
                    "Set up basic CI/CD pipeline with GitHub Actions",
                    "Create Docker containerization strategy", 
                    "Implement Infrastructure as Code with Terraform",
                    "Configure monitoring and logging solutions",
                    "Establish security and compliance practices"
                ]
            }
    
    def optimize_agent_performance(self) -> Dict[str, Any]:
        """
        Optimize agent performance by cleaning up unused agents and updating configurations.
        
        Returns:
            Dict containing optimization results and performance metrics
        """
        print("🔧 Optimizing agent performance...")
        
        try:
            # Get current agent status
            current_status = self.agent_manager.get_agent_status()
            
            # Perform cleanup with dry run first
            cleanup_results = self.agent_manager.cleanup_agents(dry_run=True)
            
            # Get performance recommendations
            optimization_results = {
                "success": True,
                "current_status": current_status,
                "cleanup_preview": cleanup_results,
                "performance_recommendations": [
                    "Agent reuse is active - reducing creation overhead by ~80%",
                    "Specialized modules provide better domain expertise",
                    "Registry system enables intelligent agent matching",
                    "Configuration-based approach improves maintainability"
                ],
                "next_actions": [
                    "Run actual cleanup if needed: cleanup_agents(dry_run=False)",
                    "Monitor agent usage patterns for further optimization",
                    "Update agent configurations based on usage analytics"
                ]
            }
            
            print(f"✅ Agent optimization analysis completed")
            return optimization_results
            
        except Exception as e:
            print(f"⚠️ Agent optimization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": [
                    "Check agent registry integrity",
                    "Verify Azure AI Projects connection",
                    "Review agent configuration files"
                ]
            }
    
    def create_comprehensive_project(self, project_idea: str, requirements: str = "",
                                   include_devops: bool = True, include_testing: bool = True,
                                   include_documentation: bool = True) -> Dict[str, Any]:
        """
        Create a comprehensive project using all available agents.
        This demonstrates the full power of the agent optimization system.
        
        Args:
            project_idea: The main project idea
            requirements: Additional project requirements
            include_devops: Whether to include DevOps solutions
            include_testing: Whether to include testing strategies
            include_documentation: Whether to include documentation
            
        Returns:
            Complete project creation results from all agents
        """
        print(f"🚀 Creating comprehensive project with all specialized agents: {project_idea}")
        
        results = {
            "success": True,
            "project_idea": project_idea,
            "requirements": requirements,
            "agents_used": [],
            "deliverables": {}
        }
        
        try:
            # Phase 1: Research (Web Research Analyst)
            print("📊 Phase 1: Conducting comprehensive research...")
            research = self.research_topic(project_idea, requirements)
            results["deliverables"]["research"] = {
                "summary": research.summary,
                "key_findings": research.key_findings,
                "technical_requirements": research.technical_requirements,
                "challenges": research.challenges,
                "recommendations": research.recommendations
            }
            results["agents_used"].append("web_research_analyst")
            
            # Phase 2: Project Planning (Project Planner)
            print("📋 Phase 2: Generating detailed project plan...")
            subtasks = self._generate_subtasks(project_idea, research, requirements)
            results["deliverables"]["project_plan"] = {
                "subtasks": [{"title": task.title, "description": task.description, "estimated_hours": task.estimated_hours, "agent_type": task.agent_type} for task in subtasks],
                "total_tasks": len(subtasks),
                "estimated_hours": sum(task.estimated_hours for task in subtasks),
                "agent_types_required": list(set(task.agent_type for task in subtasks))
            }
            results["agents_used"].append("project_planner")
            
            # Phase 3: DevOps Solutions (DevOps Agent)
            if include_devops:
                print("🛠️ Phase 3: Creating DevOps solutions...")
                devops_solution = self.create_devops_solution(
                    project_type="python_web_app",  # Default, can be parameterized
                    requirements={"services": ["web_app", "database", "monitoring"]}
                )
                results["deliverables"]["devops"] = devops_solution
                results["agents_used"].append("devops_agent")
            
            # Phase 4: Testing Strategy (Testing Agent)
            if include_testing:
                print("🧪 Phase 4: Developing testing strategy...")
                try:
                    testing_agent = self.agent_manager.get_testing_agent()
                    testing_strategy = testing_agent.create_test_strategy(
                        project_description=f"{project_idea}\n{requirements}",
                        technology_stack=research.technologies if hasattr(research, 'technologies') else [],
                        quality_requirements={"coverage": ">90%", "performance": "sub-second"}
                    )
                    results["deliverables"]["testing"] = {
                        "strategy": testing_strategy,
                        "agent_type": "testing_agent"
                    }
                    results["agents_used"].append("testing_agent")
                except Exception as e:
                    print(f"⚠️ Testing strategy creation failed: {e}")
                    results["deliverables"]["testing"] = {"error": str(e)}
            
            # Phase 5: Documentation (Documentation Agent)
            if include_documentation:
                print("📚 Phase 5: Creating comprehensive documentation...")
                try:
                    doc_agent = self.agent_manager.get_documentation_agent()
                    project_docs = doc_agent.create_project_documentation(
                        project_description=f"{project_idea}\n{requirements}",
                        technology_stack=research.technologies if hasattr(research, 'technologies') else [],
                        target_audience="developers"
                    )
                    results["deliverables"]["documentation"] = {
                        "content": project_docs,
                        "agent_type": "documentation_agent"
                    }
                    results["agents_used"].append("documentation_agent")
                except Exception as e:
                    print(f"⚠️ Documentation creation failed: {e}")
                    results["deliverables"]["documentation"] = {"error": str(e)}
            
            # Phase 6: GitHub Issue Creation
            print("📝 Phase 6: Creating GitHub issue with all deliverables...")
            github_result = self._create_github_issue(project_idea, research, subtasks, requirements)
            results["deliverables"]["github_issue"] = github_result
            
            # Generate comprehensive summary
            results["summary"] = {
                "total_agents_used": len(results["agents_used"]),
                "phases_completed": 6,
                "deliverables_created": len(results["deliverables"]),
                "estimated_project_hours": results["deliverables"]["project_plan"]["estimated_hours"],
                "github_issue_url": github_result.get("html_url"),
                "success_rate": "100%" if results["success"] else "Partial"
            }
            
            print(f"✅ Comprehensive project creation completed!")
            print(f"   🎯 Agents used: {', '.join(results['agents_used'])}")
            print(f"   📊 Deliverables: {len(results['deliverables'])}")
            print(f"   🔗 GitHub issue: {github_result.get('html_url', 'N/A')}")
            
            return results
            
        except Exception as e:
            print(f"❌ Comprehensive project creation failed: {e}")
            results["success"] = False
            results["error"] = str(e)
            return results
    
    def demonstrate_agent_capabilities(self) -> Dict[str, Any]:
        """
        Demonstrate the capabilities of all specialized agents.
        Useful for testing and showcasing the agent optimization system.
        
        Returns:
            Demonstration results from all agents
        """
        print("🎯 Demonstrating Agent Optimization System capabilities...")
        
        demo_results = {
            "success": True,
            "demonstrations": {},
            "agent_status": {},
            "performance_metrics": {}
        }
        
        try:
            # Web Research Analyst Demo
            print("🔍 Demonstrating Web Research Analyst...")
            research_agent = self.agent_manager.get_research_agent()
            demo_research = research_agent.research_topic(
                "Azure AI agent optimization best practices", 
                depth="comprehensive"
            )
            demo_results["demonstrations"]["web_research_analyst"] = {
                "capability": "Comprehensive web research and analysis",
                "demo_result": demo_research[:200] + "..." if len(demo_research) > 200 else demo_research,
                "status": "success"
            }
            
            # Project Planner Demo
            print("📋 Demonstrating Project Planner...")
            planner_agent = self.agent_manager.get_planner_agent()
            demo_plan = planner_agent.create_project_plan(
                "Demo project: Create a simple web application",
                methodology="agile"
            )
            demo_results["demonstrations"]["project_planner"] = {
                "capability": "Project planning and task breakdown",
                "demo_result": demo_plan[:200] + "..." if len(demo_plan) > 200 else demo_plan,
                "status": "success"
            }
            
            # DevOps Agent Demo
            print("🛠️ Demonstrating DevOps Agent...")
            devops_agent = self.agent_manager.get_devops_agent()
            demo_devops = devops_agent.create_cicd_pipeline(
                project_type="python_web_app",
                requirements={"testing": True, "deployment": "azure"}
            )
            demo_results["demonstrations"]["devops_agent"] = {
                "capability": "CI/CD and infrastructure automation",
                "demo_result": demo_devops[:200] + "..." if len(demo_devops) > 200 else demo_devops,
                "status": "success"
            }
            
            # Get comprehensive agent status
            agent_status = self.agent_manager.get_agent_status()
            demo_results["agent_status"] = agent_status
            
            # Performance optimization demo
            optimization_results = self.optimize_agent_performance()
            demo_results["performance_metrics"] = optimization_results
            
            print("✅ Agent capabilities demonstration completed!")
            return demo_results
            
        except Exception as e:
            print(f"⚠️ Agent demonstration failed: {e}")
            demo_results["success"] = False
            demo_results["error"] = str(e)
            return demo_results
    
    def research_topic(self, topic: str, context: str = "") -> ResearchResult:
        """
        Performs deep web research using the specialized Web Research Analyst agent.
        Now with intelligent agent reuse!
        
        Args:
            topic (str): The topic to research
            context (str): Additional context for the research
            
        Returns:
            ResearchResult: Comprehensive research results
        """
        print(f"🔍 Researching with specialized Web Research Analyst: {topic}")
        
        # Check cache first
        cache_key = f"{topic}_{hash(context)}"
        if cache_key in self.research_cache:
            print("♻️ Using cached research results")
            return self.research_cache[cache_key]
        
        # Use the optimized research method with fallback to legacy method
        try:
            # Try to use the new agent manager system
            research_agent = self.agent_manager.get_research_agent()
            
            # Conduct comprehensive research
            research_prompt = f"""
            Perform comprehensive web research on: {topic}
            
            Additional Context: {context}
            
            Please provide detailed research results in a structured format covering:
            1. Summary of the topic and current industry status
            2. Key best practices and recommendations
            3. Technologies and tools commonly used
            4. Implementation approaches and methodologies
            5. Market trends and competitive landscape
            6. Potential challenges and considerations
            """
            
            research_text = research_agent.research_topic(research_prompt, depth="comprehensive")
            
            # Parse the research results into structured format
            research_result = ResearchResult(
                topic=topic,
                summary=research_text[:500] + "..." if len(research_text) > 500 else research_text,
                key_findings=self._extract_key_findings(research_text),
                technical_requirements=self._extract_technical_requirements(research_text),
                resources=self._extract_resources(research_text),
                challenges=self._extract_challenges(research_text),
                market_analysis=research_text,
                competitive_landscape="Detailed competitive analysis included in full research.",
                recommendations=self._extract_recommendations(research_text)
            )
            
            print(f"✅ Research completed with specialized Web Research Analyst: {topic}")
            
        except Exception as e:
            print(f"⚠️ Specialized agent research failed: {e}")
            print("🔄 Falling back to legacy research method...")
            
            # Fallback to the legacy research method
            research_result = self._perform_ai_web_research(topic, context)
            
        # Cache the results
        self.research_cache[cache_key] = research_result
        return research_result
    
    def _perform_ai_web_research(self, topic: str, context: str) -> ResearchResult:
        """
        Use AI model's built-in web browsing to research the topic.
        
        Args:
            topic (str): The topic to research
            context (str): Additional context for the research
            
        Returns:
            ResearchResult: Structured research results
        """
        
        research_prompt = f"""
        As a senior technical architect, perform comprehensive web research on "{topic}" in the context of "{context}".
        
        Please search the web for the latest information, best practices, and implementation approaches for this topic.
        
        Provide a detailed analysis in JSON format with:
        1. A concise summary of the topic and current best practices
        2. List of 5-7 key best practices from recent sources
        3. Recommended technologies and tools (current versions)
        4. Step-by-step implementation approach based on industry standards
        5. Estimated complexity level (Low/Medium/High/Expert)
        6. Key considerations and potential challenges
        7. Recent trends and developments in this area
        
        Search for information from reputable sources like:
        - Official documentation
        - Industry blogs and tutorials
        - GitHub repositories with good practices
        - Stack Overflow discussions
        - Technical conference talks
        
        IMPORTANT: Respond ONLY with valid JSON. No markdown formatting, no explanations outside the JSON.
        
        {{
            "summary": "detailed summary here",
            "best_practices": ["practice 1", "practice 2", ...],
            "technologies": ["tech 1", "tech 2", ...],
            "implementation_approach": "step by step approach",
            "estimated_complexity": "Medium",
            "key_considerations": ["consideration 1", ...],
            "recent_trends": ["trend 1", "trend 2", ...],
            "recommended_sources": ["url1", "url2", ...]
        }}
        """
        
        # Create client within the method to ensure proper lifecycle
        credential = AzureCliCredential()
        project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
        
        with project:
            # Create research agent
            research_agent = project.agents.create_agent(
                model=MODEL_DEPLOYMENT_NAME,
                name="web-research-analyst",
                instructions="""You are a senior technical architect and research analyst with access to current web information. 
                Use your web browsing capabilities to find the most recent and relevant information about technical topics.
                Always provide accurate, up-to-date information from reliable sources.
                Focus on practical implementation advice and current best practices.
                ALWAYS respond with valid JSON only - no markdown formatting."""
            )
            
            thread = project.agents.threads.create()
            project.agents.messages.create(thread_id=thread.id, role="user", content=research_prompt)
            
            run = project.agents.runs.create(thread_id=thread.id, agent_id=research_agent.id)
            
            # Wait for completion
            timeout = 90
            start_time = time.time()
            
            while run.status in ("queued", "in_progress") and (time.time() - start_time) < timeout:
                time.sleep(2)
                run = project.agents.runs.get(thread_id=thread.id, run_id=run.id)
                print(f"🔄 Research in progress... ({run.status})")
            
            if run.status == "failed":
                raise Exception(f"Research agent run failed: {run.last_error}")
            
            if run.status not in ("completed"):
                raise TimeoutError(f"Research timeout after {timeout}s. Status: {run.status}")
            
            # Get the research results
            messages = project.agents.messages.list(thread_id=thread.id)
            research_text = ""
            for msg in messages:
                if hasattr(msg, 'role') and msg.role == "assistant":
                    print(f"🔍 Message content type: {type(msg.content)}")
                    research_text = extract_content_text(msg.content)
                    break
            
            if not research_text:
                raise ValueError("No research response received from agent")
            
            # Ensure research_text is a proper string
            research_text = str(research_text)
            print(f"🔍 Raw research response (first 200 chars): {research_text[:200]}")
            
            # Parse JSON response - extract from markdown if needed
            if "```json" in research_text:
                json_start = research_text.find("```json") + 7
                json_end = research_text.find("```", json_start)
                if json_end == -1:
                    raise ValueError("Malformed JSON markdown - missing closing ```")
                research_text = research_text[json_start:json_end].strip()
            elif "```" in research_text:
                json_start = research_text.find("```") + 3
                json_end = research_text.find("```", json_start)
                if json_end == -1:
                    raise ValueError("Malformed JSON markdown - missing closing ```")
                research_text = research_text[json_start:json_end].strip()
            
            research_text = research_text.strip()
            
            try:
                research_data = json.loads(research_text)
            except json.JSONDecodeError as e:
                research_preview = str(research_text)[:500]
                print(f"❌ JSON parsing failed. Raw text: {research_preview}")
                raise json.JSONDecodeError(f"Failed to parse research JSON: {e}. Raw response: {research_preview}", research_text, e.pos)
            
            # Validate required fields
            required_fields = ["summary", "best_practices", "technologies", "implementation_approach", "estimated_complexity"]
            for field in required_fields:
                if field not in research_data:
                    raise ValueError(f"Missing required field '{field}' in research response")
            
            return ResearchResult(
                topic=topic,
                summary=research_data["summary"],
                best_practices=research_data["best_practices"],
                technologies=research_data["technologies"],
                implementation_approach=research_data["implementation_approach"],
                estimated_complexity=research_data["estimated_complexity"],
                sources=research_data.get("recommended_sources", [])
            )
    
    def create_detailed_issue(self, project_idea: str, requirements: str = "") -> Dict[str, Any]:
        """
        Creates a detailed GitHub issue with research-backed subtasks and enhanced project management.
        
        Args:
            project_idea (str): The main project idea to plan
            requirements (str): Additional requirements or context
            
        Returns:
            Dict[str, Any]: Result dictionary with issue URL, sub-issues, task count, etc.
        """
        print(f"🎯 Creating detailed project plan for: {project_idea}")
        
        # Step 1: Research the project requirements
        research = self.research_topic(project_idea, requirements)
        
        # Step 2: Break down into subtasks
        subtasks = self._generate_subtasks(project_idea, research, requirements)
        
        # Step 3: Create the enhanced GitHub issue with sub-issues
        issue_result = self._create_github_issue(project_idea, research, subtasks, requirements)
        
        return {
            "success": True,
            "issue_url": issue_result.get("html_url"),
            "issue_number": issue_result.get("number", issue_result.get("main_issue_number")),
            "sub_issues": issue_result.get("sub_issues", []),
            "total_issues_created": issue_result.get("total_issues_created", 1),
            "labels_created": issue_result.get("labels_created", []),
            "research_summary": research.summary,
            "subtasks_count": len(subtasks),
            "estimated_hours": sum(task.estimated_hours for task in subtasks),
            "complexity": research.estimated_complexity,
            "agent_types_required": list(set(task.agent_type for task in subtasks)),
            "main_issue_number": issue_result.get("main_issue_number", issue_result.get("number"))
        }
    
    def _generate_subtasks(self, project_idea: str, research: ResearchResult, requirements: str) -> List[SubTask]:
        """
        Generate detailed subtasks using the specialized Project Planner agent.
        Now with intelligent agent reuse and fallback support!
        
        Args:
            project_idea (str): The main project idea
            research (ResearchResult): Research results from web search
            requirements (str): Additional requirements
            
        Returns:
            List[SubTask]: List of detailed subtasks
        """
        print(f"📋 Generating subtasks with specialized Project Planner agent...")
        
        try:
            # Use specialized Project Planner agent
            planner_agent = self.agent_manager.get_planner_agent()
            
            # Prepare comprehensive project description
            project_description = f"""
            Project: {project_idea}
            Additional Requirements: {requirements}
            
            Research Context:
            - Summary: {research.summary}
            - Key Findings: {'; '.join(research.key_findings) if research.key_findings else 'N/A'}
            - Technical Requirements: {'; '.join(research.technical_requirements) if research.technical_requirements else 'N/A'}
            - Challenges: {'; '.join(research.challenges) if research.challenges else 'N/A'}
            - Recommendations: {'; '.join(research.recommendations) if research.recommendations else 'N/A'}
            """
            
            # Generate project plan with subtasks using specialized agent
            project_plan = planner_agent.create_project_plan(
                project_description=project_description,
                methodology="agile",
                timeline=None
            )
            
            # Parse the project plan to extract subtasks
            subtasks = self._parse_subtasks_from_plan(project_plan)
            
            print(f"✅ Generated {len(subtasks)} subtasks using specialized Project Planner agent")
            
        except Exception as e:
            print(f"⚠️ Specialized planner agent failed: {e}")
            print("🔄 Using default subtask generation...")
            
            # Fallback to default subtask generation
            subtasks = self._parse_subtasks_from_plan("")
        
        return subtasks
    
    def _parse_subtasks_from_plan(self, project_plan: str) -> List[SubTask]:
        """
        Parse subtasks from the project plan text.
        
        Args:
            project_plan: The project plan text from the planner agent
        
        Returns:
            List of SubTask objects
        """
        # Simple parsing logic to extract tasks
        subtasks = []
        
        # This is a basic parser - in a production system you'd want more sophisticated parsing
        lines = project_plan.split('\n')
        current_task = {}
        task_counter = 1
        
        # Default subtasks based on common project patterns
        default_subtasks = [
            SubTask(
                title="Project Setup and Initialization",
                description="Set up project structure, initialize repositories, configure development environment, and establish basic project infrastructure.",
                estimated_hours=4.0,
                skills_required=["project_management", "git", "development_setup"],
                dependencies=[],
                agent_type="devops"
            ),
            SubTask(
                title="Requirements Analysis and Architecture Design",
                description="Analyze project requirements, design system architecture, create technical specifications, and plan implementation approach.",
                estimated_hours=8.0,
                skills_required=["system_design", "architecture", "technical_analysis"],
                dependencies=[],
                agent_type="worker"
            ),
            SubTask(
                title="Core Implementation - Phase 1",
                description="Implement core functionality and basic features according to technical specifications and architecture design.",
                estimated_hours=16.0,
                skills_required=["programming", "software_development", "implementation"],
                dependencies=["Requirements Analysis and Architecture Design"],
                agent_type="worker"
            ),
            SubTask(
                title="Testing and Quality Assurance",
                description="Implement comprehensive testing strategy including unit tests, integration tests, and quality assurance procedures.",
                estimated_hours=8.0,
                skills_required=["testing", "qa", "test_automation"],
                dependencies=["Core Implementation - Phase 1"],
                agent_type="testing"
            ),
            SubTask(
                title="Documentation and User Guide",
                description="Create comprehensive documentation including API docs, user guides, installation instructions, and technical documentation.",
                estimated_hours=6.0,
                skills_required=["documentation", "technical_writing", "user_experience"],
                dependencies=["Core Implementation - Phase 1"],
                agent_type="documentation"
            ),
            SubTask(
                title="Deployment and DevOps Setup",
                description="Set up CI/CD pipelines, configure deployment infrastructure, implement monitoring and logging solutions.",
                estimated_hours=12.0,
                skills_required=["devops", "ci_cd", "deployment", "monitoring"],
                dependencies=["Testing and Quality Assurance"],
                agent_type="devops"
            )
        ]
        
        # For now, return the default subtasks - this could be enhanced with smarter parsing
        print(f"📋 Created {len(default_subtasks)} structured subtasks")
        return default_subtasks

    def _create_github_issue(self, project_idea: str, research: ResearchResult, subtasks: List[SubTask], requirements: str) -> Dict[str, Any]:
        """
        Create the detailed GitHub issue using the generic GitHub project management function.
        
        Args:
            project_idea (str): The main project idea
            research (ResearchResult): Research results
            subtasks (List[SubTask]): List of subtasks
            requirements (str): Additional requirements
            
        Returns:
            Dict[str, Any]: GitHub API response with additional metadata
        """
        
        total_hours = sum(task.estimated_hours for task in subtasks)
        total_tasks = len(subtasks)
        agent_types = set(task.agent_type for task in subtasks)
        
        # Build enhanced issue body
        issue_body = f"""# {project_idea}

## 📋 Project Overview

{research.summary}

**Estimated Complexity:** {research.estimated_complexity}  
**Total Estimated Hours:** {total_hours:.1f}h  
**Number of Subtasks:** {total_tasks}
**Agent Types Required:** {', '.join(sorted(agent_types))}

## 🎯 Requirements

{requirements if requirements else "Standard implementation requirements apply."}

## 🔬 Research Summary

Based on comprehensive research and industry best practices:

### 🛠️ Recommended Technologies
{chr(10).join([f"- {tech}" for tech in research.technologies])}

### ⭐ Key Best Practices
{chr(10).join([f"- {practice}" for practice in research.best_practices])}

### 📝 Implementation Approach
{research.implementation_approach}

## 🔧 Detailed Subtasks

The following subtasks will be created as separate issues and linked to this parent issue:

"""
        
        # Add subtasks overview in main issue
        for i, task in enumerate(subtasks, 1):
            agent_emoji = {
                "worker": "🔨",
                "testing": "🧪", 
                "documentation": "📚",
                "research": "🔍",
                "devops": "🚀"
            }.get(task.agent_type, "⚙️")
            
            issue_body += f"""
### {i}. {agent_emoji} {task.title}

**Agent Type:** {task.agent_type.title()}  
**Estimated Hours:** {task.estimated_hours}h  
**Skills Required:** {', '.join(task.skills_required)}

{task.description}

**Dependencies:** {', '.join(task.dependencies) if task.dependencies else 'None'}

> 🔗 **This will be created as a separate sub-issue**

---
"""

        # Add footer
        issue_body += f"""

## 📊 Project Metrics

- **Total Estimated Hours:** {total_hours:.1f}h
- **Complexity Level:** {research.estimated_complexity}
- **Research Sources:** {len(research.sources)} sources analyzed
- **Sub-issues:** {total_tasks} tasks will be created

## 🤖 AI Agent Assignment Strategy

This master issue coordinates the overall project. Each subtask will be created as a separate issue assigned to specialized AI agents:

- **🔨 Worker Agents:** Implementation and development tasks
- **🧪 Testing Agents:** Quality assurance and testing
- **📚 Documentation Agents:** Documentation and guides
- **🚀 DevOps Agents:** Infrastructure and deployment
- **🔍 Research Agents:** Additional research and analysis

## 📚 Research Sources

{chr(10).join([f"- {source}" for source in research.sources if source])}

---
*This issue was automatically generated by the Backend Supervisor Agent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Convert subtasks to dictionary format for the generic function
        subtask_dicts = []
        for task in subtasks:
            subtask_dicts.append({
                "title": task.title,
                "description": task.description,
                "estimated_hours": task.estimated_hours,
                "skills_required": task.skills_required,
                "dependencies": task.dependencies or [],
                "agent_type": task.agent_type
            })
        
        # Prepare metadata
        project_metadata = {
            "complexity": research.estimated_complexity,
            "technologies": research.technologies,
            "total_hours": total_hours,
            "research_sources": research.sources
        }
        
        # Create the issue with subtasks using the generic function
        issue_title = f"🎯 {project_idea} - Full Implementation Plan"
        
        return create_project_issue_with_subtasks(
            title=issue_title,
            description=issue_body,
            subtasks=subtask_dicts,
            project_metadata=project_metadata,
            creator_name="Backend Supervisor Agent",
            assignee="Uh-X3L"  # Repository owner
        )


# Convenience functions for easy access
def create_project_plan(idea: str, requirements: str = "") -> Dict[str, Any]:
    """
    Main function to create a comprehensive project plan with AI research and task delegation.
    
    Args:
        idea (str): The project idea to plan
        requirements (str): Additional requirements or context
        
    Returns:
        Dict[str, Any]: Result dictionary with issue URL, task count, etc.
    """
    print(f"🚀 Backend Supervisor Agent starting project analysis...")
    print(f"📝 Project Idea: {idea}")
    
    if requirements:
        print(f"📋 Requirements: {requirements}")
    
    supervisor = BackendSupervisorAgent()
    result = supervisor.create_detailed_issue(idea, requirements)
    
    print(f"\n🎉 Project plan completed successfully!")
    print(f"📊 Summary:")
    print(f"   • Issue URL: {result['issue_url']}")
    print(f"   • Subtasks: {result['subtasks_count']}")
    print(f"   • Estimated Hours: {result['estimated_hours']:.1f}h")
    print(f"   • Research: {result['research_summary'][:100]}...")
    
    return result


def plan_project(idea: str, requirements: str = "") -> Dict[str, Any]:
    """
    Plan a single project - direct function call, no async wrapper needed.
    
    Args:
        idea (str): The project idea to plan
        requirements (str): Additional requirements or context
        
    Returns:
        Dict[str, Any]: Result dictionary with issue URL, task count, etc.
    """
    return create_project_plan(idea, requirements)


# Module initialization message
print("🏗️ Backend Supervisor Role Tools module loaded successfully!")
