"""
Backend Supervisor Agent System - Advanced Project Management with AI

This module contains all the tools and classes needed for the Backend Supervisor Agent
to research, plan, and create detailed GitHub issues with subtasks for delegation to other agents.

Created: August 15, 2025
Author: PP (AI Assisted)
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
    link_issues
)

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
        """Initialize the Backend Supervisor Agent with an empty research cache."""
        self.research_cache = {}
    
    def research_topic(self, topic: str, context: str = "") -> ResearchResult:
        """
        Performs deep web research using the model's built-in web access capabilities.
        
        Args:
            topic (str): The topic to research
            context (str): Additional context for the research
            
        Returns:
            ResearchResult: Comprehensive research results
        """
        print(f"🔍 Researching: {topic}")
        
        # Check cache first
        cache_key = f"{topic}_{hash(context)}"
        if cache_key in self.research_cache:
            print("✅ Using cached research results")
            return self.research_cache[cache_key]
        
        # Use AI model for research
        research_result = self._perform_ai_web_research(topic, context)
        
        # Cache the results
        self.research_cache[cache_key] = research_result
        
        print(f"✅ Research completed for: {topic}")
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
            "issue_number": issue_result.get("number"),
            "sub_issues": issue_result.get("sub_issues", []),
            "total_issues_created": issue_result.get("total_issues_created", 1),
            "labels_created": issue_result.get("labels_created", []),
            "research_summary": research.summary,
            "subtasks_count": len(subtasks),
            "estimated_hours": sum(task.estimated_hours for task in subtasks),
            "complexity": research.estimated_complexity,
            "agent_types_required": list(set(task.agent_type for task in subtasks))
        }
    
    def _generate_subtasks(self, project_idea: str, research: ResearchResult, requirements: str) -> List[SubTask]:
        """
        Generate detailed subtasks based on web research.
        
        Args:
            project_idea (str): The main project idea
            research (ResearchResult): Research results from web search
            requirements (str): Additional requirements
            
        Returns:
            List[SubTask]: List of detailed subtasks
        """
        
        subtask_prompt = f"""
        As an expert project manager with access to current web information, break down the following project into detailed, actionable subtasks.
        
        Project: {project_idea}
        Requirements: {requirements}
        
        Research Summary: {research.summary}
        Best Practices: {', '.join(research.best_practices)}
        Technologies: {', '.join(research.technologies)}
        Complexity: {research.estimated_complexity}
        
        Create 8-15 specific, actionable subtasks that follow current industry standards. For each subtask:
        1. Clear, action-oriented title
        2. Detailed description (2-3 sentences) with specific deliverables
        3. Realistic time estimates based on current development practices
        4. Required skills and expertise
        5. Agent type assignment (worker/testing/documentation/research/devops)
        6. Clear dependencies between tasks
        
        Consider modern development practices like:
        - Infrastructure as Code
        - Containerization
        - CI/CD pipelines
        - Security scanning
        - Performance monitoring
        - Documentation as code
        
        IMPORTANT: Respond ONLY with valid JSON array. No markdown formatting, no explanations.
        
        [
            {{
                "title": "Task title here",
                "description": "Detailed description here",
                "estimated_hours": 4.0,
                "skills_required": ["skill1", "skill2"],
                "agent_type": "worker",
                "dependencies": ["other task title if any"]
            }}
        ]
        """
        
        # Create client within the method to ensure proper lifecycle
        credential = AzureCliCredential()
        project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=credential)
        
        with project:
            planning_agent = project.agents.create_agent(
                model=MODEL_DEPLOYMENT_NAME,
                name="project-planner-web",
                instructions="""You are an expert project manager with web access to current best practices.
                Use web research to ensure your task breakdowns follow the latest industry standards.
                Provide realistic estimates based on current development practices and tooling.
                ALWAYS respond with valid JSON only - no markdown formatting."""
            )
            
            thread = project.agents.threads.create()
            project.agents.messages.create(thread_id=thread.id, role="user", content=subtask_prompt)
            
            run = project.agents.runs.create(thread_id=thread.id, agent_id=planning_agent.id)
            
            # Wait for planning completion
            timeout = 60
            start_time = time.time()
            
            while run.status in ("queued", "in_progress") and (time.time() - start_time) < timeout:
                time.sleep(2)
                run = project.agents.runs.get(thread_id=thread.id, run_id=run.id)
                print(f"🔄 Generating subtasks... ({run.status})")
            
            if run.status == "failed":
                raise Exception(f"Subtask generation failed: {run.last_error}")
                
            if run.status not in ("completed"):
                raise TimeoutError(f"Subtask generation timeout after {timeout}s. Status: {run.status}")
            
            # Extract subtasks
            messages = project.agents.messages.list(thread_id=thread.id)
            subtasks_text = ""
            for msg in messages:
                if hasattr(msg, 'role') and msg.role == "assistant":
                    subtasks_text = extract_content_text(msg.content)
                    break
            
            if not subtasks_text:
                raise ValueError("No subtasks response received from planning agent")
            
            subtasks_text = str(subtasks_text)
            print(f"🔍 Raw subtasks response (first 200 chars): {subtasks_text[:200]}")
            
            # Parse subtasks JSON - extract from markdown if needed
            if "```json" in subtasks_text:
                json_start = subtasks_text.find("```json") + 7
                json_end = subtasks_text.find("```", json_start)
                if json_end == -1:
                    raise ValueError("Malformed subtasks JSON markdown - missing closing ```")
                subtasks_text = subtasks_text[json_start:json_end].strip()
            elif "```" in subtasks_text:
                json_start = subtasks_text.find("```") + 3
                json_end = subtasks_text.find("```", json_start)
                if json_end == -1:
                    raise ValueError("Malformed subtasks JSON markdown - missing closing ```")
                subtasks_text = subtasks_text[json_start:json_end].strip()
            
            subtasks_text = subtasks_text.strip()
            
            try:
                subtasks_data = json.loads(subtasks_text)
            except json.JSONDecodeError as e:
                subtasks_preview = str(subtasks_text)[:500]
                print(f"❌ Subtasks JSON parsing failed. Raw text: {subtasks_preview}")
                raise json.JSONDecodeError(f"Failed to parse subtasks JSON: {e}. Raw response: {subtasks_preview}", subtasks_text, e.pos)
            
            if not isinstance(subtasks_data, list):
                raise ValueError(f"Expected JSON array for subtasks, got {type(subtasks_data)}")
            
            if len(subtasks_data) == 0:
                raise ValueError("No subtasks generated by planning agent")
            
            subtasks = []
            for i, task_data in enumerate(subtasks_data):
                if not isinstance(task_data, dict):
                    raise ValueError(f"Subtask {i} is not a valid object: {task_data}")
                
                # Validate required fields
                required_fields = ["title", "description", "estimated_hours", "skills_required", "agent_type"]
                for field in required_fields:
                    if field not in task_data:
                        raise ValueError(f"Subtask {i} missing required field '{field}'")
                
                subtask = SubTask(
                    title=task_data["title"],
                    description=task_data["description"],
                    estimated_hours=float(task_data["estimated_hours"]),
                    skills_required=task_data["skills_required"],
                    dependencies=task_data.get("dependencies", []),
                    agent_type=task_data["agent_type"]
                )
                subtasks.append(subtask)
            
            print(f"✅ Generated {len(subtasks)} subtasks")
            return subtasks

    def _create_github_issue(self, project_idea: str, research: ResearchResult, subtasks: List[SubTask], requirements: str) -> Dict[str, Any]:
        """
        Create the detailed GitHub issue with enhanced project management features.
        
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
        
        # Get GitHub tokens
        inst_id = resolve_installation_id()
        tok = installation_token_cached(inst_id)
        
        # 🏷️ Create project-specific labels if they don't exist
        project_labels = [
            {"name": "backend-supervisor", "color": "7f00ff", "description": "Created by Backend Supervisor Agent"},
            {"name": f"complexity-{research.estimated_complexity.lower()}", "color": self._get_complexity_color(research.estimated_complexity), "description": f"Project complexity: {research.estimated_complexity}"},
            {"name": "ai-project", "color": "00d4aa", "description": "AI-managed project"},
            {"name": "has-subtasks", "color": "ffa500", "description": "Parent issue with sub-issues"}
        ]
        
        # Add agent-type specific labels
        agent_types = set(task.agent_type for task in subtasks)
        for agent_type in agent_types:
            project_labels.append({
                "name": f"needs-{agent_type}",
                "color": self._get_agent_color(agent_type),
                "description": f"Requires {agent_type} agent"
            })
        
        print("🏷️ Creating project labels...")
        created_labels = create_labels_if_not_exist(tok, project_labels)
        
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
        
        # Add subtasks with checkboxes (main issue overview)
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

        # 📝 Create the main GitHub issue with enhanced features
        issue_title = f"🎯 {project_idea} - Full Implementation Plan"
        
        # Backend Bot assignment (you can change this to your bot's username)
        assignees = ["backend-bot"] if get_user_info(tok, "backend-bot") else None
        if not assignees:
            print("⚠️ 'backend-bot' user not found, creating issue without assignee")
        
        print("📝 Creating main project issue...")
        result = create_issue(
            tok, 
            title=issue_title, 
            body=issue_body,
            assignees=assignees,
            labels=[label["name"] for label in project_labels if label["name"] in created_labels]
        )
        
        main_issue_number = result["number"]
        print(f"✅ Created main issue #{main_issue_number}: {result.get('html_url')}")
        
        # 🎯 Create sub-issues for each subtask
        print(f"🔄 Creating {len(subtasks)} sub-issues...")
        sub_issue_numbers = []
        
        for i, task in enumerate(subtasks, 1):
            sub_issue_title = f"{self._get_agent_emoji(task.agent_type)} {task.title}"
            
            sub_issue_body = f"""## 🎯 Subtask Details

**Parent Issue:** #{main_issue_number}
**Agent Type:** {task.agent_type.title()}
**Estimated Hours:** {task.estimated_hours}h
**Skills Required:** {', '.join(task.skills_required)}

### 📝 Description
{task.description}

### ✅ Acceptance Criteria
- [ ] Task implementation completed
- [ ] Code follows project standards
- [ ] Tests passing (if applicable)
- [ ] Documentation updated (if applicable)
- [ ] Peer review completed
- [ ] Integration with main project verified

### 🔗 Dependencies
{chr(10).join([f"- {dep}" for dep in task.dependencies]) if task.dependencies else "None"}

### 📊 Task Metadata
- **Complexity:** Individual task within {research.estimated_complexity} project
- **Technology Stack:** {', '.join(research.technologies[:3])}...
- **Priority:** {self._determine_task_priority(task, i, len(subtasks))}

---
*Sub-issue created by Backend Supervisor Agent*
"""

            # Create sub-issue with appropriate labels
            sub_labels = [
                "backend-supervisor",
                f"agent-{task.agent_type}",
                "subtask",
                f"complexity-{research.estimated_complexity.lower()}"
            ]
            
            sub_result = create_issue(
                tok,
                title=sub_issue_title,
                body=sub_issue_body,
                labels=sub_labels
            )
            
            sub_issue_numbers.append(sub_result["number"])
            print(f"  ✅ Created sub-issue #{sub_result['number']}: {task.title}")
        
        # 🔗 Link all sub-issues to the main issue
        print("🔗 Linking sub-issues to main issue...")
        link_issues(tok, main_issue_number, sub_issue_numbers, "subtask")
        
        # 📋 Try to add to project (optional - will fail gracefully if project doesn't exist)
        project_id = os.environ.get("GITHUB_PROJECT_ID")
        if project_id:
            try:
                print(f"📋 Adding main issue to project #{project_id}...")
                add_issue_to_project(tok, main_issue_number, int(project_id), "To Do")
                print("✅ Added main issue to project")
            except Exception as e:
                print(f"⚠️ Could not add to project: {e}")
        
        # Return enhanced result with sub-issue information
        return {
            **result,
            "sub_issues": [{"number": num} for num in sub_issue_numbers],
            "total_issues_created": len(sub_issue_numbers) + 1,
            "labels_created": created_labels,
            "main_issue_number": main_issue_number
        }
    
    def _get_complexity_color(self, complexity: str) -> str:
        """Get color code for complexity label."""
        colors = {
            "low": "28a745",
            "medium": "ffc107", 
            "high": "fd7e14",
            "expert": "dc3545"
        }
        return colors.get(complexity.lower(), "6c757d")
    
    def _get_agent_color(self, agent_type: str) -> str:
        """Get color code for agent type label."""
        colors = {
            "worker": "0366d6",
            "testing": "28a745",
            "documentation": "6f42c1",
            "research": "e36209",
            "devops": "d73a49"
        }
        return colors.get(agent_type, "6c757d")
    
    def _get_agent_emoji(self, agent_type: str) -> str:
        """Get emoji for agent type."""
        emojis = {
            "worker": "🔨",
            "testing": "🧪",
            "documentation": "📚", 
            "research": "🔍",
            "devops": "🚀"
        }
        return emojis.get(agent_type, "⚙️")
    
    def _determine_task_priority(self, task: SubTask, position: int, total: int) -> str:
        """Determine task priority based on position and dependencies."""
        if task.dependencies:
            return "High"  # Tasks with dependencies are high priority
        elif position <= total * 0.3:
            return "High"  # First 30% of tasks
        elif position <= total * 0.7:
            return "Medium" # Middle 40% of tasks
        else:
            return "Low"   # Last 30% of tasks


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
