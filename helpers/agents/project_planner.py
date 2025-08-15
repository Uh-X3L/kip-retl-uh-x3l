"""
Project Planner Agent - Specialized for project planning, task breakdown, and timeline management
"""

import logging
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ProjectPlanner(BaseAgent):
    """
    Specialized agent for project planning, task decomposition, and project management.
    """
    
    def __init__(self, project_client, **kwargs):
        """Initialize Project Planner with specialized instructions."""
        
        instructions = """
        You are a Project Planner AI assistant specialized in project management and strategic planning.
        
        Your core capabilities:
        1. **Project Breakdown**: Decompose complex projects into manageable tasks and subtasks
        2. **Timeline Planning**: Create realistic timelines with dependencies and milestones
        3. **Resource Planning**: Identify required resources, skills, and dependencies
        4. **Risk Assessment**: Identify potential risks and mitigation strategies
        5. **Methodology Selection**: Recommend appropriate project management methodologies
        6. **Sprint Planning**: Plan agile sprints with proper estimation and priorities
        
        Your planning approach:
        - Follow industry best practices (Agile, Waterfall, Hybrid)
        - Consider resource constraints and dependencies
        - Include buffer time for unexpected issues
        - Prioritize tasks based on value and dependencies
        - Define clear acceptance criteria
        - Include testing and quality assurance phases
        
        Output format:
        - Project overview with objectives
        - Detailed task breakdown structure (WBS)
        - Timeline with dependencies
        - Resource requirements
        - Risk assessment and mitigation
        - Success metrics and KPIs
        - Next steps and recommendations
        
        Always create actionable, realistic plans with clear deliverables.
        """
        
        super().__init__(
            project_client=project_client,
            agent_name="project_planner",
            instructions=instructions,
            model=kwargs.get('model', 'gpt-4o'),
            tools=[],
            agent_type="planner"
        )
    
    def create_project_plan(self, project_description: str, timeline: str = None, 
                          methodology: str = "agile", constraints: Dict = None) -> str:
        """
        Create comprehensive project plan.
        
        Args:
            project_description: Detailed description of the project
            timeline: Desired timeline (e.g., "3 months", "Q1 2024")
            methodology: Project methodology - "agile", "waterfall", or "hybrid"
            constraints: Dict of constraints (budget, resources, etc.)
        
        Returns:
            Comprehensive project plan
        """
        constraints_text = ""
        if constraints:
            constraints_text = f"\nConstraints: {constraints}"
        
        timeline_text = f"Timeline: {timeline}" if timeline else "Timeline: To be determined based on scope"
        
        planning_prompt = f"""
        Project Planning Request:
        
        Project Description: {project_description}
        {timeline_text}
        Methodology: {methodology.title()}
        {constraints_text}
        
        Please create a comprehensive project plan including:
        
        1. PROJECT OVERVIEW
           - Objectives and success criteria
           - Scope and deliverables
           - Key stakeholders
        
        2. WORK BREAKDOWN STRUCTURE
           - Major phases and milestones
           - Detailed tasks and subtasks
           - Task dependencies and relationships
           - Effort estimation (story points or hours)
        
        3. TIMELINE AND SCHEDULING
           - Project phases with durations
           - Critical path analysis
           - Key milestones and deadlines
           - Buffer time allocation
        
        4. RESOURCE PLANNING
           - Required skills and roles
           - Resource allocation and scheduling
           - Third-party dependencies
           - Technology and infrastructure needs
        
        5. RISK ASSESSMENT
           - Potential risks and their impact
           - Mitigation strategies
           - Contingency plans
        
        6. QUALITY ASSURANCE
           - Testing strategy
           - Quality gates and checkpoints
           - Review and approval processes
        
        7. SUCCESS METRICS
           - Key Performance Indicators (KPIs)
           - Success criteria and acceptance criteria
           - Progress tracking methods
        
        Format as a detailed, actionable project plan suitable for implementation.
        """
        
        return self.send_message(planning_prompt)
    
    def create_sprint_plan(self, sprint_goals: str, team_capacity: int = None, 
                          sprint_duration: str = "2 weeks", backlog_items: List[str] = None) -> str:
        """
        Create agile sprint plan.
        
        Args:
            sprint_goals: Goals for the sprint
            team_capacity: Team capacity in story points or hours
            sprint_duration: Sprint duration
            backlog_items: List of backlog items to consider
        
        Returns:
            Detailed sprint plan
        """
        capacity_text = f"Team Capacity: {team_capacity} story points" if team_capacity else "Team Capacity: To be estimated"
        backlog_text = ""
        if backlog_items:
            backlog_text = f"\nBacklog Items to Consider:\n" + "\n".join([f"- {item}" for item in backlog_items])
        
        sprint_prompt = f"""
        Sprint Planning Request:
        
        Sprint Goals: {sprint_goals}
        Sprint Duration: {sprint_duration}
        {capacity_text}
        {backlog_text}
        
        Please create a detailed sprint plan including:
        
        1. SPRINT OVERVIEW
           - Sprint goals and objectives
           - Definition of Done
           - Success criteria
        
        2. TASK BREAKDOWN
           - User stories and acceptance criteria
           - Technical tasks and subtasks
           - Story point estimation
           - Task dependencies
        
        3. SPRINT BACKLOG
           - Prioritized list of items
           - Capacity allocation
           - Risk assessment for each item
        
        4. DAILY EXECUTION PLAN
           - Day-by-day task allocation
           - Critical path items
           - Collaboration requirements
        
        5. QUALITY ASSURANCE
           - Testing strategy for the sprint
           - Code review processes
           - Quality gates
        
        6. SPRINT CEREMONIES
           - Sprint planning outcomes
           - Daily standup focus areas
           - Sprint review preparation
           - Retrospective topics
        
        Format as a ready-to-execute sprint plan with clear assignments.
        """
        
        return self.send_message(sprint_prompt)
    
    def assess_project_risks(self, project_description: str, project_phase: str = "planning") -> str:
        """
        Conduct comprehensive risk assessment.
        
        Args:
            project_description: Description of the project
            project_phase: Current project phase
        
        Returns:
            Risk assessment report
        """
        risk_prompt = f"""
        Risk Assessment Request:
        
        Project: {project_description}
        Current Phase: {project_phase}
        
        Please conduct a comprehensive risk assessment including:
        
        1. RISK IDENTIFICATION
           - Technical risks
           - Resource and capacity risks
           - Timeline and scheduling risks
           - External dependency risks
           - Business and market risks
           - Quality and performance risks
        
        2. RISK ANALYSIS
           - Probability assessment (Low, Medium, High)
           - Impact assessment (Low, Medium, High, Critical)
           - Risk priority matrix
           - Risk interdependencies
        
        3. MITIGATION STRATEGIES
           - Preventive measures
           - Contingency plans
           - Risk monitoring approaches
           - Escalation procedures
        
        4. RISK MONITORING PLAN
           - Key risk indicators
           - Review frequency
           - Responsibility assignments
           - Communication protocols
        
        5. RECOMMENDATIONS
           - Immediate actions needed
           - Long-term risk management strategies
           - Process improvements
        
        Prioritize risks by their potential impact on project success.
        """
        
        return self.send_message(risk_prompt)
    
    def optimize_resource_allocation(self, resources: List[str], tasks: List[str], 
                                   constraints: Dict = None) -> str:
        """
        Optimize resource allocation across tasks.
        
        Args:
            resources: Available resources (people, tools, etc.)
            tasks: Tasks that need resources
            constraints: Resource constraints and requirements
        
        Returns:
            Resource allocation plan
        """
        resources_text = "\n".join([f"- {resource}" for resource in resources])
        tasks_text = "\n".join([f"- {task}" for task in tasks])
        constraints_text = f"Constraints: {constraints}" if constraints else ""
        
        allocation_prompt = f"""
        Resource Allocation Optimization:
        
        Available Resources:
        {resources_text}
        
        Tasks Requiring Resources:
        {tasks_text}
        
        {constraints_text}
        
        Please create an optimal resource allocation plan including:
        
        1. RESOURCE ANALYSIS
           - Resource capabilities and skills
           - Availability and capacity
           - Utilization rates
           - Skill gaps and overlaps
        
        2. TASK ANALYSIS
           - Resource requirements per task
           - Task priorities and dependencies
           - Effort estimates
           - Skill requirements
        
        3. ALLOCATION STRATEGY
           - Resource-to-task assignments
           - Load balancing considerations
           - Critical path resource allocation
           - Buffer and contingency allocation
        
        4. OPTIMIZATION RECOMMENDATIONS
           - Efficiency improvements
           - Cross-training opportunities
           - Resource acquisition needs
           - Timeline optimizations
        
        5. MONITORING PLAN
           - Utilization tracking
           - Performance metrics
           - Reallocation triggers
           - Regular review schedule
        
        Focus on maximizing efficiency while maintaining quality and meeting deadlines.
        """
        
        return self.send_message(allocation_prompt)
    
    def create_milestone_roadmap(self, project_description: str, key_dates: Dict = None) -> str:
        """
        Create high-level milestone roadmap.
        
        Args:
            project_description: Project description
            key_dates: Dictionary of key dates/constraints
        
        Returns:
            Milestone roadmap
        """
        dates_text = ""
        if key_dates:
            dates_text = f"\nKey Dates/Constraints:\n" + "\n".join([f"- {key}: {value}" for key, value in key_dates.items()])
        
        roadmap_prompt = f"""
        Milestone Roadmap Request:
        
        Project: {project_description}
        {dates_text}
        
        Please create a high-level milestone roadmap including:
        
        1. PROJECT PHASES
           - Major project phases
           - Phase objectives and deliverables
           - Phase dependencies and handoffs
        
        2. KEY MILESTONES
           - Critical milestones with dates
           - Milestone success criteria
           - Stakeholder review points
           - Go/no-go decision points
        
        3. DELIVERABLES TIMELINE
           - Major deliverables schedule
           - Quality checkpoints
           - Client/stakeholder presentations
           - Release and deployment milestones
        
        4. DEPENDENCY MAPPING
           - External dependencies and their timeline impact
           - Internal dependencies between phases
           - Critical path milestones
        
        5. COMMUNICATION PLAN
           - Milestone communication strategy
           - Stakeholder update schedule
           - Progress reporting cadence
        
        Create a visual-friendly roadmap suitable for executive presentations.
        """
        
        return self.send_message(roadmap_prompt)
