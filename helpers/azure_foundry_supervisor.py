"""
Azure AI Foundry Backend Supervisor Agent System
This module provides Azure AI Foundry compatible implementation for the task execution system.

Uses Azure AI Foundry endpoints directly with OpenAI SDK instead of azure-ai-projects package.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
import openai

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

# Load environment variables
load_dotenv()

# Azure AI Foundry configuration
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.environ.get("MODEL_DEPLOYMENT_NAME", "o3-mini")
AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
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

class AzureFoundryAgent:
    """
    Azure AI Foundry compatible agent implementation using OpenAI SDK
    """
    
    def __init__(self, name: str, role: str, capabilities: List[str]):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.azure_available = self._check_azure_availability()
        
        if self.azure_available:
            self.client = self._initialize_openai_client()
        else:
            self.client = None
            
    def _check_azure_availability(self) -> bool:
        """Check if Azure AI Foundry is properly configured"""
        try:
            # Check required environment variables
            if not PROJECT_ENDPOINT:
                print("❌ PROJECT_ENDPOINT not found in environment variables")
                return False
                
            if not AZURE_TENANT_ID:
                print("❌ AZURE_TENANT_ID not found in environment variables")
                return False
                
            # Validate PROJECT_ENDPOINT format
            if not PROJECT_ENDPOINT.startswith("https://") or "azure.com" not in PROJECT_ENDPOINT:
                print(f"❌ Invalid PROJECT_ENDPOINT format: {PROJECT_ENDPOINT}")
                return False
                
            print(f"✅ Azure AI Foundry configuration validated")
            print(f"   - Endpoint: {PROJECT_ENDPOINT}")
            print(f"   - Model: {MODEL_DEPLOYMENT_NAME}")
            print(f"   - Tenant: {AZURE_TENANT_ID}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking Azure availability: {e}")
            return False
    
    def _initialize_openai_client(self):
        """Initialize OpenAI client for Azure AI Foundry"""
        try:
            # Use Azure credentials
            credential = DefaultAzureCredential()
            
            # Get token for Azure AI services
            token = credential.get_token("https://cognitiveservices.azure.com/.default")
            
            # Initialize OpenAI client with Azure endpoint
            client = openai.AzureOpenAI(
                azure_endpoint=PROJECT_ENDPOINT.replace("/api/projects/AI-ETL-PP", ""),
                api_key=token.token,
                api_version="2024-10-21"
            )
            
            print(f"✅ Azure OpenAI client initialized for {self.name}")
            return client
            
        except Exception as e:
            print(f"❌ Failed to initialize Azure OpenAI client: {e}")
            return None
    
    def call_model(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """
        Call Azure AI Foundry model using OpenAI SDK
        """
        if not self.azure_available or not self.client:
            return self._mock_response(messages[-1]["content"])
        
        try:
            # Prepare the request
            request_params = {
                "model": MODEL_DEPLOYMENT_NAME,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
            
            # Make the API call
            response = self.client.chat.completions.create(**request_params)
            
            return {
                "choices": [{
                    "message": {
                        "content": response.choices[0].message.content,
                        "tool_calls": response.choices[0].message.tool_calls if hasattr(response.choices[0].message, 'tool_calls') else None
                    }
                }]
            }
            
        except Exception as e:
            print(f"❌ Error calling Azure AI Foundry model: {e}")
            return self._mock_response(messages[-1]["content"])
    
    def _mock_response(self, user_message: str) -> Dict:
        """Generate a mock response when Azure AI is not available"""
        mock_content = f"""
I understand you want me to help with: {user_message[:100]}...

However, I'm currently operating in mock mode because Azure AI Foundry is not fully configured.
To enable full functionality, please ensure:

1. Azure AI Foundry project is properly set up
2. All environment variables are configured
3. Azure authentication is working

For now, I can provide this simulated response to help with testing the system architecture.
"""
        
        return {
            "choices": [{
                "message": {
                    "content": mock_content,
                    "tool_calls": None
                }
            }]
        }

class BackendSupervisorAgent(AzureFoundryAgent):
    """
    Main Backend Supervisor Agent using Azure AI Foundry
    """
    
    def __init__(self):
        super().__init__(
            name="Backend Supervisor",
            role="Project Research, Planning, and Task Creation",
            capabilities=[
                "Project research and analysis",
                "GitHub issue creation and management", 
                "Task decomposition and planning",
                "Technology stack evaluation",
                "Team coordination and delegation"
            ]
        )
        
        # Agent specializations
        self.specialized_agents = {
            "research": AzureFoundryAgent("Research Agent", "Information gathering and analysis", ["web_research", "documentation_analysis"]),
            "planning": AzureFoundryAgent("Planning Agent", "Project planning and estimation", ["task_breakdown", "timeline_estimation"]),
            "devops": AzureFoundryAgent("DevOps Agent", "Infrastructure and deployment", ["ci_cd", "cloud_deployment", "monitoring"]),
            "worker": AzureFoundryAgent("Worker Agent", "Code implementation", ["coding", "testing", "debugging"]),
            "testing": AzureFoundryAgent("Testing Agent", "Quality assurance", ["test_planning", "automation", "validation"]),
            "documentation": AzureFoundryAgent("Documentation Agent", "Technical writing", ["documentation", "tutorials", "guides"])
        }
        
        print(f"🤖 Backend Supervisor Agent initialized")
        print(f"   - Azure Available: {self.azure_available}")
        print(f"   - Specialized Agents: {len(self.specialized_agents)}")
    
    def research_topic(self, topic: str, scope: str = "comprehensive") -> ResearchResult:
        """
        Research a given topic using Azure AI Foundry
        """
        print(f"🔍 Researching: {topic}")
        
        research_prompt = f"""
        As an expert research agent, please conduct comprehensive research on: {topic}
        
        Scope: {scope}
        
        Please provide:
        1. A detailed summary of the topic
        2. Best practices and recommendations
        3. Relevant technologies and tools
        4. Implementation approaches
        5. Complexity estimation (Low/Medium/High)
        6. Key considerations and potential challenges
        
        Format your response as a structured analysis that can guide project planning.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert research agent specializing in technology research and analysis."},
            {"role": "user", "content": research_prompt}
        ]
        
        response = self.specialized_agents["research"].call_model(messages)
        content = response["choices"][0]["message"]["content"]
        
        # Parse the response (simplified for now)
        research_result = ResearchResult(
            topic=topic,
            summary=content[:500] + "..." if len(content) > 500 else content,
            best_practices=["Best practice 1", "Best practice 2", "Best practice 3"],
            technologies=["Technology 1", "Technology 2"],
            implementation_approach="Recommended approach based on research",
            estimated_complexity="Medium",
            sources=["Azure AI Foundry Research", "Expert Analysis"]
        )
        
        print(f"✅ Research completed for: {topic}")
        return research_result
    
    def create_implementation_plan(self, research_result: ResearchResult, requirements: Dict[str, Any]) -> List[SubTask]:
        """
        Create detailed implementation plan with subtasks
        """
        print(f"📋 Creating implementation plan for: {research_result.topic}")
        
        planning_prompt = f"""
        Based on the research for {research_result.topic}, create a detailed implementation plan.
        
        Research Summary: {research_result.summary}
        Requirements: {json.dumps(requirements, indent=2)}
        
        Please create a list of subtasks that includes:
        1. Task title and description
        2. Estimated hours
        3. Required skills
        4. Dependencies
        5. Recommended agent type (research/planning/devops/worker/testing/documentation)
        
        Format as actionable subtasks that can be converted to GitHub issues.
        """
        
        messages = [
            {"role": "system", "content": "You are an expert project planning agent specializing in breaking down complex projects into manageable subtasks."},
            {"role": "user", "content": planning_prompt}
        ]
        
        response = self.specialized_agents["planning"].call_model(messages)
        content = response["choices"][0]["message"]["content"]
        
        # Create sample subtasks (in real implementation, parse from AI response)
        subtasks = [
            SubTask(
                title=f"Research and Planning for {research_result.topic}",
                description="Complete initial research and create detailed project plan",
                estimated_hours=8.0,
                skills_required=["research", "planning"],
                agent_type="research"
            ),
            SubTask(
                title=f"Core Implementation for {research_result.topic}",
                description="Implement the main functionality and features",
                estimated_hours=16.0,
                skills_required=["programming", "architecture"],
                agent_type="worker"
            ),
            SubTask(
                title=f"Testing and Validation for {research_result.topic}",
                description="Create and execute comprehensive test suite",
                estimated_hours=6.0,
                skills_required=["testing", "qa"],
                agent_type="testing"
            ),
            SubTask(
                title=f"Documentation for {research_result.topic}",
                description="Create comprehensive documentation and guides",
                estimated_hours=4.0,
                skills_required=["technical_writing"],
                agent_type="documentation"
            )
        ]
        
        print(f"✅ Implementation plan created with {len(subtasks)} subtasks")
        return subtasks
    
    def execute_task_workflow(self, task_description: str, requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute complete task workflow from research to GitHub issue creation
        """
        if requirements is None:
            requirements = {}
            
        print(f"🚀 Starting task workflow: {task_description}")
        
        try:
            # Phase 1: Research
            research_result = self.research_topic(task_description)
            
            # Phase 2: Planning  
            subtasks = self.create_implementation_plan(research_result, requirements)
            
            # Phase 3: GitHub Issue Creation (if configured)
            github_issue = None
            if REPO and all([os.getenv("GITHUB_APP_ID"), os.getenv("GITHUB_INSTALLATION_ID")]):
                try:
                    github_issue = self.create_github_issue(task_description, research_result, subtasks)
                    print(f"✅ GitHub issue created: {github_issue.get('html_url', 'N/A')}")
                except Exception as e:
                    print(f"⚠️ GitHub issue creation failed: {e}")
            
            # Phase 4: Return results
            workflow_result = {
                "task_description": task_description,
                "research": research_result.__dict__,
                "subtasks": [task.__dict__ for task in subtasks],
                "github_issue": github_issue,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Task workflow completed successfully")
            return workflow_result
            
        except Exception as e:
            print(f"❌ Task workflow failed: {e}")
            return {
                "task_description": task_description,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def create_github_issue(self, task_description: str, research_result: ResearchResult, subtasks: List[SubTask]) -> Dict[str, Any]:
        """
        Create GitHub issue with research and subtasks
        """
        print(f"📝 Creating GitHub issue for: {task_description}")
        
        # Prepare issue content
        issue_body = f"""
# {task_description}

## Research Summary
{research_result.summary}

## Implementation Approach
{research_result.implementation_approach}

## Technologies
{', '.join(research_result.technologies)}

## Subtasks
"""
        
        for i, subtask in enumerate(subtasks, 1):
            issue_body += f"""
### {i}. {subtask.title}
- **Description**: {subtask.description}
- **Estimated Hours**: {subtask.estimated_hours}
- **Skills Required**: {', '.join(subtask.skills_required)}
- **Agent Type**: {subtask.agent_type}
"""
        
        # Create the issue
        issue_data = {
            "title": f"[SUPERVISOR] {task_description}",
            "body": issue_body,
            "labels": ["supervisor-task", "planning", research_result.estimated_complexity.lower()]
        }
        
        # Use GitHub tools to create issue
        repo_parts = REPO.split('/')
        owner, repo = repo_parts[0], repo_parts[1]
        
        github_issue = create_issue(owner, repo, issue_data)
        return github_issue
