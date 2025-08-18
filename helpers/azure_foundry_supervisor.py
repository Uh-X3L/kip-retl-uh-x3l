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
