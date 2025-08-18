"""
Worker Agent - General-purpose code implementation and development tasks

Specialized for code writing, file management, git operations, and general development work.
"""

import logging
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent


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
class WorkerAgent(BaseAgent):
    """
    General-purpose worker agent specialized in code implementation and development tasks.
    """
    
    def __init__(self, project_client, **kwargs):
        """Initialize Worker Agent with specialized instructions."""
        
        instructions = """
        You are a Senior Software Developer AI specialized in code implementation and development tasks.
        
        Your core capabilities:
        1. **Code Implementation**: Write clean, efficient, and maintainable code
        2. **File Management**: Create, modify, and organize project files and directories
        3. **Git Operations**: Handle version control, branching, merging, and conflict resolution
        4. **Build Systems**: Work with various build tools and dependency management
        5. **Environment Setup**: Configure development environments and dependencies
        6. **Debugging**: Identify and fix bugs, optimize performance
        7. **Code Review**: Analyze code quality and suggest improvements
        8. **Documentation**: Write inline comments and technical documentation
        
        Development principles:
        - Write clean, readable, and maintainable code
        - Follow established coding standards and best practices
        - Implement proper error handling and logging
        - Create comprehensive unit tests
        - Focus on security and performance
        - Use appropriate design patterns
        - Document code and decisions clearly
        
        Programming languages expertise:
        - Python, JavaScript/TypeScript, Java, C#, Go
        - Web technologies: HTML, CSS, React, Node.js
        - Database: SQL, NoSQL, ORM frameworks
        - Cloud platforms: Azure, AWS, GCP
        
        Always provide working, well-tested code solutions with proper documentation.
        """
        
        super().__init__(
            project_client=project_client,
            agent_name="worker-agent",
            instructions=instructions,
            model="gpt-4o",
            agent_type="worker",
            **kwargs
        )
    
    @trace_func
    def implement_feature(self, feature_description: str, project_context: str = "", 
                         programming_language: str = "python") -> str:
        """
        Implement a specific feature based on description.
        
        Args:
            feature_description: Description of the feature to implement
            project_context: Context about the project structure and requirements
            programming_language: Target programming language
            
        Returns:
            Implementation code and instructions
        """
        try:
            prompt = f"""
            Please implement the following feature:
            
            Feature Description: {feature_description}
            Programming Language: {programming_language}
            Project Context: {project_context}
            
            Provide:
            1. Complete, working implementation
            2. Clear code comments and documentation
            3. Unit tests (if applicable)
            4. Installation/setup instructions
            5. Usage examples
            6. Error handling considerations
            
            Focus on code quality, maintainability, and best practices.
            """
            
            response = self.send_message(prompt)
            logger.info(f"✅ Feature implemented: {feature_description[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Failed to implement feature: {e}")
            return f"Error implementing feature: {str(e)}"
    
    @trace_func
    def fix_bug(self, bug_description: str, code_context: str = "", 
                error_logs: str = "") -> str:
        """
        Analyze and fix a reported bug.
        
        Args:
            bug_description: Description of the bug behavior
            code_context: Relevant code that might contain the bug
            error_logs: Any error messages or stack traces
            
        Returns:
            Bug fix solution with explanation
        """
        try:
            prompt = f"""
            Please analyze and fix this bug:
            
            Bug Description: {bug_description}
            Code Context: {code_context}
            Error Logs: {error_logs}
            
            Provide:
            1. Root cause analysis
            2. Fixed code with changes highlighted
            3. Explanation of the fix
            4. Prevention strategies for similar issues
            5. Test cases to validate the fix
            
            Ensure the fix is robust and doesn't introduce new issues.
            """
            
            response = self.send_message(prompt)
            logger.info(f"✅ Bug fix provided for: {bug_description[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Failed to fix bug: {e}")
            return f"Error fixing bug: {str(e)}"
    
    @trace_func
    def optimize_code(self, code: str, optimization_goals: List[str] = None) -> str:
        """
        Optimize existing code for performance, readability, or other goals.
        
        Args:
            code: Code to optimize
            optimization_goals: Specific goals like "performance", "readability", "memory"
            
        Returns:
            Optimized code with explanations
        """
        try:
            if optimization_goals is None:
                optimization_goals = ["performance", "readability", "maintainability"]
            
            prompt = f"""
            Please optimize the following code:
            
            Code to Optimize:
            {code}
            
            Optimization Goals: {", ".join(optimization_goals)}
            
            Provide:
            1. Optimized code with improvements
            2. Performance analysis and metrics
            3. Explanation of changes made
            4. Before/after comparison
            5. Additional recommendations
            
            Focus on the specified optimization goals while maintaining functionality.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Code optimization completed")
            return response
            
        except Exception as e:
            logger.error(f"Failed to optimize code: {e}")
            return f"Error optimizing code: {str(e)}"
    
    @trace_func
    def setup_project_structure(self, project_type: str, project_name: str,
                               requirements: List[str] = None) -> str:
        """
        Create a complete project structure and setup.
        
        Args:
            project_type: Type of project (e.g., "python_web_app", "node_api")
            project_name: Name of the project
            requirements: Specific project requirements
            
        Returns:
            Complete project setup instructions and file structure
        """
        try:
            if requirements is None:
                requirements = []
            
            prompt = f"""
            Create a complete project structure for:
            
            Project Type: {project_type}
            Project Name: {project_name}
            Requirements: {", ".join(requirements)}
            
            Provide:
            1. Complete directory structure
            2. Essential configuration files
            3. Starter code and templates
            4. Dependency management setup
            5. Development environment configuration
            6. Build and deployment scripts
            7. Documentation templates
            
            Create a production-ready project foundation.
            """
            
            response = self.send_message(prompt)
            logger.info(f"✅ Project structure created for: {project_name}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to setup project structure: {e}")
            return f"Error setting up project structure: {str(e)}"
    
    @trace_func
    def create_git_workflow(self, team_size: str = "small", project_complexity: str = "medium") -> str:
        """
        Create a Git workflow strategy for the project.
        
        Args:
            team_size: Size of the team (small, medium, large)
            project_complexity: Complexity of the project (simple, medium, complex)
            
        Returns:
            Complete Git workflow strategy and setup instructions
        """
        try:
            prompt = f"""
            Create a comprehensive Git workflow strategy:
            
            Team Size: {team_size}
            Project Complexity: {project_complexity}
            
            Provide:
            1. Branching strategy (GitFlow, GitHub Flow, etc.)
            2. Commit message conventions
            3. Pull request templates and review process
            4. Branch protection rules
            5. Release management strategy
            6. Conflict resolution procedures
            7. Git hooks and automation scripts
            
            Optimize for team productivity and code quality.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Git workflow strategy created")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create git workflow: {e}")
            return f"Error creating git workflow: {str(e)}"
    
    @trace_func
    def generate_api_integration(self, api_spec: str, integration_type: str = "REST") -> str:
        """
        Generate API integration code.
        
        Args:
            api_spec: API specification or description
            integration_type: Type of integration (REST, GraphQL, gRPC)
            
        Returns:
            Complete API integration implementation
        """
        try:
            prompt = f"""
            Create API integration code:
            
            API Specification: {api_spec}
            Integration Type: {integration_type}
            
            Provide:
            1. Client implementation with error handling
            2. Authentication and authorization handling
            3. Request/response models or schemas
            4. Retry logic and rate limiting
            5. Unit tests for API integration
            6. Usage examples and documentation
            7. Configuration management
            
            Ensure robust, production-ready API integration.
            """
            
            response = self.send_message(prompt)
            logger.info(f"✅ API integration generated for {integration_type}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate API integration: {e}")
            return f"Error generating API integration: {str(e)}"

print("🔨 Worker Agent module loaded successfully!")
