"""
Documentation Agent - Specialized for technical writing and documentation generation

Focused on creating comprehensive, user-friendly documentation including API docs,
user guides, tutorials, and technical specifications.
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
class DocumentationAgent(BaseAgent):
    """
    Specialized agent for technical documentation and content creation.
    """
    
    def __init__(self, project_client, **kwargs):
        """Initialize Documentation Agent with specialized instructions."""
        
        instructions = """
        You are a Senior Technical Writer and Documentation Specialist AI focused on creating comprehensive, accessible documentation.
        
        Your core expertise:
        1. **Technical Writing**: Clear, concise, and user-focused technical content
        2. **API Documentation**: Comprehensive API reference guides with examples
        3. **User Guides**: Step-by-step tutorials and how-to guides
        4. **Code Documentation**: Inline comments, docstrings, and code explanations
        5. **Architecture Documentation**: System design and architecture diagrams
        6. **Installation Guides**: Setup instructions for different environments
        7. **Troubleshooting**: Problem-solving guides and FAQ sections
        8. **Knowledge Base**: Searchable documentation and knowledge management
        
        Documentation principles:
        - User-centered design and accessibility
        - Clear structure and logical organization
        - Comprehensive yet concise content
        - Practical examples and use cases
        - Regular updates and maintenance
        - Multiple formats and media types
        - SEO and discoverability optimization
        
        Content formats expertise:
        - Markdown, reStructuredText, AsciiDoc
        - HTML, PDF, and interactive formats
        - API specifications: OpenAPI/Swagger, GraphQL
        - Diagram tools: Mermaid, PlantUML, Draw.io
        - Documentation platforms: GitBook, Confluence, Notion
        
        Always create documentation that enables users to be successful and productive.
        """
        
        super().__init__(
            project_client=project_client,
            agent_name="documentation-writer",
            instructions=instructions,
            model="gpt-4o",
            agent_type="documentation",
            **kwargs
        )
    
    @trace_func
    def create_project_documentation(self, project_description: str,
                                   technology_stack: List[str] = None,
                                   target_audience: str = "developers") -> str:
        """
        Create comprehensive project documentation.
        
        Args:
            project_description: Description of the project
            technology_stack: Technologies used in the project
            target_audience: Primary audience for the documentation
            
        Returns:
            Complete project documentation structure and content
        """
        try:
            if technology_stack is None:
                technology_stack = []
            
            prompt = f"""
            Create comprehensive project documentation:
            
            Project Description: {project_description}
            Technology Stack: {", ".join(technology_stack)}
            Target Audience: {target_audience}
            
            Provide:
            1. README.md with project overview and quick start
            2. Installation and setup guide
            3. Architecture and system design documentation
            4. API reference (if applicable)
            5. User guide with tutorials and examples
            6. Development guide for contributors
            7. Deployment and configuration guide
            8. Troubleshooting and FAQ section
            9. Changelog and version history template
            10. Contributing guidelines and code of conduct
            
            Create documentation that is comprehensive, accessible, and maintainable.
            """
            
            response = self.send_message(prompt)
            logger.info(f"✅ Project documentation created for: {project_description[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create project documentation: {e}")
            return f"Error creating project documentation: {str(e)}"
    
    @trace_func
    def generate_api_documentation(self, api_specification: str,
                                  api_type: str = "REST",
                                  documentation_format: str = "OpenAPI") -> str:
        """
        Generate comprehensive API documentation.
        
        Args:
            api_specification: API specification or description
            api_type: Type of API (REST, GraphQL, gRPC)
            documentation_format: Format for documentation (OpenAPI, AsyncAPI, etc.)
            
        Returns:
            Complete API documentation with examples
        """
        try:
            prompt = f"""
            Generate comprehensive API documentation:
            
            API Specification: {api_specification}
            API Type: {api_type}
            Documentation Format: {documentation_format}
            
            Provide:
            1. API overview and introduction
            2. Authentication and authorization guide
            3. Complete endpoint documentation with examples
            4. Request/response schemas and models
            5. Error codes and handling
            6. Rate limiting and usage guidelines
            7. SDK and client library examples
            8. Interactive API explorer setup
            9. Versioning and migration guides
            10. Testing and validation examples
            
            Include practical examples and use cases for each endpoint.
            """
            
            response = self.send_message(prompt)
            logger.info(f"✅ API documentation generated for {api_type} API")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate API documentation: {e}")
            return f"Error generating API documentation: {str(e)}"
    
    @trace_func
    def create_user_guide(self, application_description: str,
                         user_personas: List[str] = None,
                         key_features: List[str] = None) -> str:
        """
        Create comprehensive user guide and tutorials.
        
        Args:
            application_description: Description of the application
            user_personas: Different types of users
            key_features: Main features to document
            
        Returns:
            Complete user guide with tutorials and examples
        """
        try:
            if user_personas is None:
                user_personas = ["end_user", "administrator"]
            if key_features is None:
                key_features = []
            
            prompt = f"""
            Create comprehensive user guide:
            
            Application: {application_description}
            User Personas: {", ".join(user_personas)}
            Key Features: {", ".join(key_features)}
            
            Provide:
            1. Getting started guide for new users
            2. Feature-by-feature tutorials with screenshots
            3. Step-by-step workflows for common tasks
            4. Advanced usage scenarios and tips
            5. Troubleshooting guide for common issues
            6. Frequently asked questions (FAQ)
            7. Glossary of terms and concepts
            8. Video tutorial scripts (if applicable)
            9. User onboarding checklist
            10. Support and help resources
            
            Structure content for different skill levels and use cases.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ User guide created")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create user guide: {e}")
            return f"Error creating user guide: {str(e)}"
    
    @trace_func
    def document_code_architecture(self, codebase_description: str,
                                 architecture_patterns: List[str] = None,
                                 diagram_format: str = "mermaid") -> str:
        """
        Create architecture documentation with diagrams.
        
        Args:
            codebase_description: Description of the codebase and system
            architecture_patterns: Architecture patterns used
            diagram_format: Format for diagrams (mermaid, plantuml, etc.)
            
        Returns:
            Complete architecture documentation with diagrams
        """
        try:
            if architecture_patterns is None:
                architecture_patterns = []
            
            prompt = f"""
            Create comprehensive architecture documentation:
            
            Codebase: {codebase_description}
            Architecture Patterns: {", ".join(architecture_patterns)}
            Diagram Format: {diagram_format}
            
            Provide:
            1. System architecture overview and principles
            2. High-level system diagram
            3. Component architecture and interactions
            4. Data flow and processing diagrams
            5. Database schema and relationships
            6. API and service integration architecture
            7. Deployment and infrastructure architecture
            8. Security architecture and data flow
            9. Scalability and performance considerations
            10. Architecture decision records (ADRs)
            
            Include both visual diagrams and detailed explanations.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Architecture documentation created")
            return response
            
        except Exception as e:
            logger.error(f"Failed to document code architecture: {e}")
            return f"Error documenting code architecture: {str(e)}"
    
    @trace_func
    def generate_deployment_guide(self, deployment_description: str,
                                 deployment_environments: List[str] = None,
                                 infrastructure_type: str = "cloud") -> str:
        """
        Create comprehensive deployment and operations guide.
        
        Args:
            deployment_description: Description of the deployment process
            deployment_environments: Target environments (dev, staging, prod)
            infrastructure_type: Type of infrastructure (cloud, on-premise, hybrid)
            
        Returns:
            Complete deployment guide with step-by-step instructions
        """
        try:
            if deployment_environments is None:
                deployment_environments = ["development", "staging", "production"]
            
            prompt = f"""
            Create comprehensive deployment guide:
            
            Deployment: {deployment_description}
            Environments: {", ".join(deployment_environments)}
            Infrastructure: {infrastructure_type}
            
            Provide:
            1. Deployment overview and prerequisites
            2. Environment-specific configuration guides
            3. Step-by-step deployment procedures
            4. Infrastructure provisioning instructions
            5. Database migration and setup guides
            6. Configuration management and secrets
            7. Monitoring and logging setup
            8. Rollback and disaster recovery procedures
            9. Performance tuning and optimization
            10. Maintenance and update procedures
            
            Include automation scripts and best practices for each environment.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Deployment guide created")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate deployment guide: {e}")
            return f"Error generating deployment guide: {str(e)}"
    
    @trace_func
    def create_troubleshooting_guide(self, common_issues: List[str] = None,
                                   system_components: List[str] = None,
                                   log_formats: List[str] = None) -> str:
        """
        Create comprehensive troubleshooting and problem-solving guide.
        
        Args:
            common_issues: List of common problems users face
            system_components: Main system components that can fail
            log_formats: Types of logs and their formats
            
        Returns:
            Complete troubleshooting guide with diagnostic procedures
        """
        try:
            if common_issues is None:
                common_issues = []
            if system_components is None:
                system_components = []
            if log_formats is None:
                log_formats = []
            
            prompt = f"""
            Create comprehensive troubleshooting guide:
            
            Common Issues: {", ".join(common_issues)}
            System Components: {", ".join(system_components)}
            Log Formats: {", ".join(log_formats)}
            
            Provide:
            1. Troubleshooting methodology and approach
            2. Common issues and their solutions
            3. Error message interpretation guide
            4. Log analysis and debugging techniques
            5. Performance troubleshooting procedures
            6. Network and connectivity issues
            7. Database and data integrity problems
            8. Security and authentication issues
            9. Diagnostic tools and commands
            10. When to escalate and get help
            
            Structure as searchable reference with clear problem-solution pairs.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Troubleshooting guide created")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create troubleshooting guide: {e}")
            return f"Error creating troubleshooting guide: {str(e)}"
    
    @trace_func
    def generate_code_documentation(self, code: str, documentation_style: str = "docstring",
                                   programming_language: str = "python") -> str:
        """
        Generate comprehensive code documentation and comments.
        
        Args:
            code: Source code to document
            documentation_style: Style of documentation (docstring, javadoc, jsdoc)
            programming_language: Programming language of the code
            
        Returns:
            Well-documented code with comprehensive comments
        """
        try:
            prompt = f"""
            Generate comprehensive code documentation:
            
            Programming Language: {programming_language}
            Documentation Style: {documentation_style}
            
            Source Code:
            {code}
            
            Provide:
            1. Comprehensive function/method documentation
            2. Class and module documentation
            3. Parameter and return value descriptions
            4. Usage examples for key functions
            5. Code comments explaining complex logic
            6. Type hints and annotations (if applicable)
            7. Error handling documentation
            8. Performance considerations and notes
            9. Dependencies and requirements
            10. Integration examples and patterns
            
            Follow language-specific documentation conventions and best practices.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Code documentation generated")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate code documentation: {e}")
            return f"Error generating code documentation: {str(e)}"
    
    @trace_func
    def create_changelog(self, version_history: str, change_categories: List[str] = None) -> str:
        """
        Create well-structured changelog and release notes.
        
        Args:
            version_history: Description of changes and versions
            change_categories: Categories of changes (features, fixes, breaking)
            
        Returns:
            Well-formatted changelog with release notes
        """
        try:
            if change_categories is None:
                change_categories = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
            
            prompt = f"""
            Create comprehensive changelog:
            
            Version History: {version_history}
            Change Categories: {", ".join(change_categories)}
            
            Provide:
            1. Well-structured changelog format
            2. Version numbering and semantic versioning
            3. Release date and version information
            4. Categorized changes (features, fixes, breaking changes)
            5. Migration guides for breaking changes
            6. Known issues and limitations
            7. Contributor acknowledgments
            8. Links to detailed documentation
            9. Upgrade instructions
            10. Future roadmap highlights
            
            Follow Keep a Changelog format and semantic versioning principles.
            """
            
            response = self.send_message(prompt)
            logger.info("✅ Changelog created")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create changelog: {e}")
            return f"Error creating changelog: {str(e)}"

print("📚 Documentation Agent module loaded successfully!")
