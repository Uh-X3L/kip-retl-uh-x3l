"""
DevOps Agent - Specialized for DevOps practices, CI/CD, Infrastructure, and automation
Optimized for Issue #70 requirements and general DevOps workflows.
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
class DevOpsAgent(BaseAgent):
    """
    Specialized agent for DevOps practices, CI/CD pipelines, infrastructure automation, 
    and deployment strategies. Optimized for Issue #70 requirements.
    """
    
    def __init__(self, project_client, **kwargs):
        """Initialize DevOps Agent with specialized instructions."""
        
        instructions = """
        You are a DevOps Engineer AI assistant specialized in modern DevOps practices, automation, and infrastructure.
        
        Your core expertise:
        1. **CI/CD Pipelines**: Design and implement continuous integration/deployment pipelines
        2. **Infrastructure as Code**: Create Terraform, Bicep, ARM templates, and Kubernetes manifests
        3. **Container Orchestration**: Docker, Kubernetes, container registries, and deployment strategies
        4. **Cloud Platforms**: Azure, AWS, GCP services and best practices
        5. **Automation**: Scripting, workflow automation, and process optimization
        6. **Monitoring & Observability**: Application monitoring, logging, alerting, and performance optimization
        7. **Security & Compliance**: Security scanning, compliance checks, and secure deployment practices
        8. **Git Workflows**: Branching strategies, code review processes, and version control best practices
        
        Your approach:
        - Follow infrastructure as code principles
        - Implement security and compliance from the start
        - Design for scalability and reliability
        - Automate repetitive tasks and processes
        - Use industry best practices and standards
        - Consider cost optimization and resource efficiency
        - Implement proper monitoring and alerting
        
        For Issue #70 specific requirements:
        - Focus on Git workflow automation
        - Implement CI/CD for the project
        - Create Docker containerization strategies
        - Design infrastructure deployment automation
        - Set up monitoring and logging solutions
        
        Output format:
        - Provide complete, ready-to-use configurations
        - Include step-by-step implementation guides
        - Add comments and documentation
        - Suggest best practices and optimizations
        - Include testing and validation steps
        
        Always prioritize security, scalability, and maintainability.
        """
        
        super().__init__(
            project_client=project_client,
            agent_name="devops_agent",
            instructions=instructions,
            model=kwargs.get('model', 'gpt-4o'),
            tools=[],
            agent_type="devops_specialist"
        )
    
    @trace_func
    def create_cicd_pipeline(self, project_type: str, platform: str = "github", 
                            deployment_target: str = "azure", requirements: Dict = None) -> str:
        """
        Create comprehensive CI/CD pipeline configuration.
        
        Args:
            project_type: Type of project (python, node, dotnet, etc.)
            platform: CI/CD platform (github, azure-devops, gitlab)
            deployment_target: Deployment target (azure, aws, kubernetes)
            requirements: Specific requirements and constraints
        
        Returns:
            Complete CI/CD pipeline configuration
        """
        reqs_text = f"Additional Requirements: {requirements}" if requirements else ""
        
        cicd_prompt = f"""
        CI/CD Pipeline Creation Request:
        
        Project Type: {project_type}
        Platform: {platform.title()}
        Deployment Target: {deployment_target}
        {reqs_text}
        
        Please create a comprehensive CI/CD pipeline including:
        
        1. PIPELINE STRUCTURE
           - Multi-stage pipeline definition
           - Environment-specific configurations
           - Approval gates and manual interventions
           - Parallel job execution where appropriate
        
        2. BUILD STAGE
           - Source code checkout and caching
           - Dependency installation and caching
           - Code compilation and bundling
           - Artifact creation and management
        
        3. TESTING STAGE
           - Unit test execution
           - Integration test setup
           - Code coverage reporting
           - Security vulnerability scanning
           - Quality gate enforcement
        
        4. SECURITY & COMPLIANCE
           - Static code analysis (SAST)
           - Dependency vulnerability scanning
           - Container security scanning
           - Compliance checks and reports
        
        5. DEPLOYMENT STAGES
           - Environment-specific deployments (dev, staging, prod)
           - Infrastructure provisioning
           - Application deployment strategies
           - Database migration handling
           - Configuration management
        
        6. MONITORING & NOTIFICATIONS
           - Build status notifications
           - Deployment success/failure alerts
           - Performance monitoring setup
           - Log aggregation configuration
        
        7. ROLLBACK & RECOVERY
           - Automated rollback triggers
           - Blue-green deployment strategies
           - Disaster recovery procedures
        
        Provide complete configuration files ready for implementation.
        """
        
        return self.send_message(cicd_prompt)
    
    @trace_func
    def create_infrastructure_code(self, infrastructure_type: str, cloud_provider: str = "azure", 
                                 services: List[str] = None, environment: str = "production") -> str:
        """
        Create Infrastructure as Code templates.
        
        Args:
            infrastructure_type: Type of IaC (terraform, bicep, arm, cloudformation)
            cloud_provider: Cloud provider (azure, aws, gcp)
            services: List of services to include
            environment: Target environment
        
        Returns:
            Complete IaC templates and configurations
        """
        services_text = f"Services to include: {', '.join(services)}" if services else "Standard web application stack"
        
        iac_prompt = f"""
        Infrastructure as Code Creation:
        
        IaC Type: {infrastructure_type.title()}
        Cloud Provider: {cloud_provider.title()}
        {services_text}
        Environment: {environment}
        
        Please create comprehensive IaC templates including:
        
        1. CORE INFRASTRUCTURE
           - Resource groups and organization
           - Networking (VNets, subnets, security groups)
           - Identity and access management
           - Key vault for secrets management
        
        2. COMPUTE RESOURCES
           - Application hosting services
           - Auto-scaling configurations
           - Load balancers and traffic management
           - Container orchestration (if applicable)
        
        3. DATA SERVICES
           - Databases and storage accounts
           - Backup and disaster recovery
           - Data encryption and security
           - Performance optimization
        
        4. MONITORING & LOGGING
           - Application insights and monitoring
           - Log analytics workspaces
           - Alerting and notification rules
           - Dashboards and reporting
        
        5. SECURITY CONFIGURATION
           - Security policies and compliance
           - Network security rules
           - Access controls and permissions
           - Encryption and key management
        
        6. DEPLOYMENT AUTOMATION
           - Environment variables and configuration
           - Automated provisioning scripts
           - Resource tagging and organization
           - Cost optimization settings
        
        7. DOCUMENTATION
           - Architecture diagrams
           - Deployment instructions
           - Configuration parameters
           - Troubleshooting guides
        
        Provide production-ready templates with best practices implemented.
        """
        
        return self.send_message(iac_prompt)
    
    @trace_func
    def design_docker_strategy(self, application_type: str, deployment_model: str = "microservices",
                             requirements: Dict = None) -> str:
        """
        Design Docker containerization strategy.
        
        Args:
            application_type: Type of application
            deployment_model: Deployment model (monolith, microservices, serverless)
            requirements: Specific containerization requirements
        
        Returns:
            Complete Docker strategy and configurations
        """
        reqs_text = f"Requirements: {requirements}" if requirements else ""
        
        docker_prompt = f"""
        Docker Containerization Strategy:
        
        Application Type: {application_type}
        Deployment Model: {deployment_model}
        {reqs_text}
        
        Please create a comprehensive Docker strategy including:
        
        1. DOCKERFILE OPTIMIZATION
           - Multi-stage build configurations
           - Base image selection and security
           - Layer optimization and caching
           - Build argument management
           - Security best practices
        
        2. CONTAINER ARCHITECTURE
           - Service decomposition strategy
           - Inter-service communication
           - Data persistence and volumes
           - Network configuration
        
        3. ORCHESTRATION SETUP
           - Docker Compose for local development
           - Kubernetes manifests for production
           - Service discovery and load balancing
           - Health checks and readiness probes
        
        4. REGISTRY MANAGEMENT
           - Container registry setup
           - Image tagging and versioning strategy
           - Automated image scanning
           - Image lifecycle management
        
        5. DEVELOPMENT WORKFLOW
           - Local development with containers
           - Hot reloading and debugging
           - Testing in containerized environments
           - Development environment consistency
        
        6. PRODUCTION DEPLOYMENT
           - Container resource limits and requests
           - Horizontal Pod Autoscaling (HPA)
           - Rolling updates and deployments
           - Monitoring and logging integration
        
        7. SECURITY & COMPLIANCE
           - Container security scanning
           - Runtime security policies
           - Secrets management in containers
           - Compliance and governance
        
        Provide complete, production-ready Docker configurations.
        """
        
        return self.send_message(docker_prompt)
    
    @trace_func
    def create_monitoring_setup(self, application_stack: str, monitoring_tools: List[str] = None,
                               alert_requirements: Dict = None) -> str:
        """
        Create comprehensive monitoring and observability setup.
        
        Args:
            application_stack: Technology stack of the application
            monitoring_tools: Preferred monitoring tools
            alert_requirements: Specific alerting requirements
        
        Returns:
            Complete monitoring configuration
        """
        tools_text = f"Preferred Tools: {', '.join(monitoring_tools)}" if monitoring_tools else "Industry standard tools"
        alerts_text = f"Alert Requirements: {alert_requirements}" if alert_requirements else ""
        
        monitoring_prompt = f"""
        Monitoring and Observability Setup:
        
        Application Stack: {application_stack}
        {tools_text}
        {alerts_text}
        
        Please create a comprehensive monitoring solution including:
        
        1. METRICS COLLECTION
           - Application performance metrics
           - Infrastructure resource metrics
           - Business logic and custom metrics
           - Real user monitoring (RUM)
        
        2. LOGGING STRATEGY
           - Centralized log aggregation
           - Log structure and formatting
           - Log retention and archival
           - Log analysis and search capabilities
        
        3. DISTRIBUTED TRACING
           - Request tracing across services
           - Performance bottleneck identification
           - Error tracking and debugging
           - Service dependency mapping
        
        4. ALERTING SYSTEM
           - Alert rule definitions
           - Escalation procedures
           - Notification channels and routing
           - Alert fatigue prevention
        
        5. DASHBOARDS & VISUALIZATION
           - Executive and operational dashboards
           - Service-specific monitoring views
           - SLA and KPI tracking
           - Historical trend analysis
        
        6. HEALTH CHECKS & PROBES
           - Application health endpoints
           - Database connectivity checks
           - External dependency monitoring
           - Synthetic transaction monitoring
        
        7. INCIDENT RESPONSE
           - Automated incident creation
           - Runbook integration
           - Post-incident analysis setup
           - SLA monitoring and reporting
        
        Focus on actionable insights and proactive issue detection.
        """
        
        return self.send_message(monitoring_prompt)
    
    @trace_func
    def optimize_git_workflow(self, team_size: str, project_type: str, 
                             current_issues: List[str] = None) -> str:
        """
        Optimize Git workflow and automation for Issue #70.
        
        Args:
            team_size: Size of the team (small, medium, large)
            project_type: Type of project
            current_issues: Current Git workflow issues to address
        
        Returns:
            Optimized Git workflow strategy
        """
        issues_text = f"Current Issues to Address:\n" + "\n".join([f"- {issue}" for issue in current_issues]) if current_issues else ""
        
        git_prompt = f"""
        Git Workflow Optimization (Issue #70):
        
        Team Size: {team_size}
        Project Type: {project_type}
        {issues_text}
        
        Please create an optimized Git workflow strategy including:
        
        1. BRANCHING STRATEGY
           - Branch naming conventions
           - Feature branch workflow
           - Release branch management
           - Hotfix procedures
        
        2. AUTOMATION SETUP
           - Pre-commit hooks configuration
           - Automated code formatting and linting
           - Commit message validation
           - Branch protection rules
        
        3. CODE REVIEW PROCESS
           - Pull request templates
           - Review assignment automation
           - Quality gates and checks
           - Automated testing integration
        
        4. RELEASE MANAGEMENT
           - Semantic versioning strategy
           - Automated changelog generation
           - Release branch automation
           - Tag management and deployment triggers
        
        5. WORKFLOW AUTOMATION
           - GitHub Actions/Azure DevOps workflows
           - Automated issue linking
           - Status checks and quality gates
           - Deployment automation triggers
        
        6. TEAM COLLABORATION
           - Issue and project board setup
           - Sprint planning integration
           - Progress tracking automation
           - Communication workflows
        
        7. TROUBLESHOOTING & MAINTENANCE
           - Common workflow issues and solutions
           - Git repository maintenance
           - Performance optimization
           - Backup and recovery procedures
        
        Provide specific configurations and scripts for implementation.
        """
        
        return self.send_message(git_prompt)
    
    @trace_func
    def create_deployment_strategy(self, application_type: str, environments: List[str],
                                  deployment_approach: str = "blue-green") -> str:
        """
        Create comprehensive deployment strategy.
        
        Args:
            application_type: Type of application to deploy
            environments: List of environments (dev, staging, prod)
            deployment_approach: Deployment strategy (blue-green, canary, rolling)
        
        Returns:
            Complete deployment strategy and automation
        """
        envs_text = ", ".join(environments)
        
        deployment_prompt = f"""
        Deployment Strategy Creation:
        
        Application Type: {application_type}
        Environments: {envs_text}
        Deployment Approach: {deployment_approach}
        
        Please create a comprehensive deployment strategy including:
        
        1. DEPLOYMENT PIPELINE
           - Environment progression strategy
           - Approval gates and quality checks
           - Automated and manual deployment triggers
           - Rollback procedures and automation
        
        2. ENVIRONMENT MANAGEMENT
           - Environment configuration management
           - Infrastructure provisioning automation
           - Configuration drift detection
           - Environment parity maintenance
        
        3. DEPLOYMENT AUTOMATION
           - Zero-downtime deployment scripts
           - Database migration handling
           - Configuration updates and secrets rotation
           - Service dependency management
        
        4. TESTING IN DEPLOYMENT
           - Smoke tests and health checks
           - Integration test automation
           - Performance validation
           - User acceptance testing automation
        
        5. MONITORING & VALIDATION
           - Deployment success metrics
           - Performance monitoring during deployment
           - Error rate tracking and alerting
           - Business metric validation
        
        6. ROLLBACK & RECOVERY
           - Automated rollback triggers
           - Manual rollback procedures
           - Data consistency management
           - Incident response integration
        
        7. COMPLIANCE & GOVERNANCE
           - Audit logging and tracking
           - Compliance validation
           - Change management integration
           - Documentation and reporting
        
        Provide production-ready deployment automation scripts and configurations.
        """
        
        return self.send_message(deployment_prompt)
