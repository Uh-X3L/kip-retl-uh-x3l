#!/usr/bin/env python3
"""
Complete Task Execution System - End-to-End with Full Tracing
============================================================

This script demonstrates the complete workflow using all functionality available
in the codebase for comprehensive task management, execution, and tracing.

Features:
- Backend Supervisor Agent for project planning and GitHub issue creation
- Dynamic tracing controller for runtime execution monitoring
- Agent communication system with Redis messaging
- Enhanced base agents with comprehensive logging
- Web research and analysis capabilities
- Complete execution visibility with snoop tracing
- Error handling and recovery mechanisms

Usage:
    python complete_task_execution_system.py
"""

import os
import sys
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path

# Add helpers to path
sys.path.append(str(Path(__file__).parent / "helpers"))

# Import all available functionality
print("🚀 INITIALIZING COMPLETE TASK EXECUTION SYSTEM")
print("=" * 65)

# 1. Backend Supervisor Agent (with Azure AI Foundry fallback)
try:
    from helpers.backend_supervisor_role_tools import (
        BackendSupervisorAgent, 
        TaskPriority, 
        SubTask, 
        ResearchResult,
        plan_project, 
        create_project_plan
    )
    print("✅ Backend Supervisor Agent loaded")
    SUPERVISOR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Original Backend Supervisor failed: {e}")
    try:
        # Fallback to Azure AI Foundry compatible supervisor
        from helpers.azure_foundry_supervisor import (
            BackendSupervisorAgent,
            TaskPriority,
            SubTask,
            ResearchResult
        )
        print("✅ Azure AI Foundry Backend Supervisor loaded")
        SUPERVISOR_AVAILABLE = True
    except ImportError as e2:
        print(f"❌ Both Backend Supervisor implementations failed: {e2}")
        SUPERVISOR_AVAILABLE = False

# 2. Dynamic Tracing Controller
try:
    from helpers.dynamic_tracing_controller import (
        TracingController,
        TRACING_CONTROLLER,
        conditional_trace,
        trace_class,
        enable_agent_communication_tracing,
        disable_all_tracing,
        enable_debug_mode,
        get_tracing_summary,
        quick_setup_for_debugging
    )
    print("✅ Dynamic Tracing Controller loaded")
    TRACING_AVAILABLE = True
except ImportError as e:
    print(f"❌ Dynamic Tracing Controller failed: {e}")
    TRACING_AVAILABLE = False

# 3. Agent Communication System
try:
    from helpers.simple_messaging import (
        SimpleMessaging, MessageType, MessagePriority, SimpleMessage,
        create_simple_messaging, send_task_to_agent, send_status_update
    )
    from helpers.agent_communication_mixin import AgentCommunicationMixin
    print("✅ Agent Communication System loaded")
    MESSAGING_AVAILABLE = True
except ImportError as e:
    print(f"❌ Agent Communication System failed: {e}")
    MESSAGING_AVAILABLE = False

# 4. Enhanced Base Agent
try:
    from helpers.enhanced_base_agent import EnhancedBaseAgent, create_enhanced_agent
    print("✅ Enhanced Base Agent loaded")
    ENHANCED_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"❌ Enhanced Base Agent failed: {e}")
    ENHANCED_AGENT_AVAILABLE = False

# 5. Specialized Agents
try:
    from helpers.agents.web_research_analyst import WebResearchAnalyst
    from helpers.agents.project_planner import ProjectPlanner
    from helpers.agents.devops_agent import DevOpsAgent
    from helpers.agents.worker_agent import WorkerAgent
    from helpers.agents.testing_agent import TestingAgent
    from helpers.agents.documentation_agent import DocumentationAgent
    print("✅ Specialized Agents loaded")
    SPECIALIZED_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some specialized agents not available: {e}")
    SPECIALIZED_AGENTS_AVAILABLE = False

# 6. Redis Messaging
try:
    from helpers.optimized_redis_messaging import OptimizedRedisMessaging
    from helpers.enhanced_redis_messaging import EnhancedRedisMessaging
    print("✅ Redis Messaging loaded")
    REDIS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Redis messaging not available: {e}")
    REDIS_AVAILABLE = False

# 7. Comprehensive Execution Logger
try:
    from helpers.comprehensive_execution_logger import (
        ComprehensiveExecutionLogger, ExecutionSession, log_method, 
        log_agent_operation, log_redis_message
    )
    print("✅ Comprehensive Execution Logger loaded")
    LOGGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Comprehensive Logger not available: {e}")
    LOGGER_AVAILABLE = False

# 8. Fixed Agent Communication
try:
    from helpers.fixed_agent_communication import (
        create_communication_enabled_agent,
        fix_agent_communication_errors,
        EnhancedAgentMixin
    )
    print("✅ Fixed Agent Communication loaded")
    FIXED_COMMUNICATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Fixed Agent Communication not available: {e}")
    FIXED_COMMUNICATION_AVAILABLE = False

# 9. Azure AI Compatibility Layer
try:
    from helpers.azure_ai_compatibility import (
        fix_azure_ai_projects_api,
        create_fallback_project_client,
        diagnose_and_fix_api_issues
    )
    print("✅ Azure AI Compatibility Layer loaded")
    AZURE_COMPATIBILITY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Azure AI Compatibility not available: {e}")
    AZURE_COMPATIBILITY_AVAILABLE = False

print(f"\n📊 SYSTEM COMPONENTS STATUS:")
print(f"   🎯 Backend Supervisor: {'✅' if SUPERVISOR_AVAILABLE else '❌'}")
print(f"   📊 Dynamic Tracing: {'✅' if TRACING_AVAILABLE else '❌'}")
print(f"   💬 Agent Communication: {'✅' if MESSAGING_AVAILABLE else '❌'}")
print(f"   🤖 Enhanced Agents: {'✅' if ENHANCED_AGENT_AVAILABLE else '❌'}")
print(f"   🔧 Specialized Agents: {'✅' if SPECIALIZED_AGENTS_AVAILABLE else '❌'}")
print(f"   🔴 Redis Messaging: {'✅' if REDIS_AVAILABLE else '❌'}")
print(f"   📝 Execution Logger: {'✅' if LOGGER_AVAILABLE else '❌'}")
print(f"   🔄 Fixed Communication: {'✅' if FIXED_COMMUNICATION_AVAILABLE else '❌'}")
print(f"   🔧 Azure AI Compatibility: {'✅' if AZURE_COMPATIBILITY_AVAILABLE else '❌'}")

# Run Azure AI compatibility diagnostics
if AZURE_COMPATIBILITY_AVAILABLE:
    print(f"\n🔍 RUNNING AZURE AI COMPATIBILITY DIAGNOSTICS...")
    try:
        diagnosis = diagnose_and_fix_api_issues()
        print(f"📊 API Compatibility Status:")
        for fix in diagnosis["api_compatibility"]["fixes_applied"][:3]:  # Show first 3 fixes
            print(f"   ✅ {fix}")
        if diagnosis["critical_issues"]:
            print(f"⚠️ Critical Issues Found:")
            for issue in diagnosis["critical_issues"]:
                print(f"   ❌ {issue}")
        if diagnosis["recommendations"]:
            print(f"💡 Recommendations:")
            for rec in diagnosis["recommendations"][:2]:  # Show first 2 recommendations
                print(f"   🔧 {rec}")
    except Exception as e:
        print(f"⚠️ Diagnostics failed: {e}")

# Configure logging with Unicode support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('task_execution_system.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Set encoding for stdout to handle Unicode characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
elif hasattr(sys.stdout, 'buffer'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

logger = logging.getLogger(__name__)


# Conditional decorator that handles missing tracing gracefully
def conditional_trace(module_name: str = None):
    """Conditional tracing decorator that works even if tracing is not available."""
    def decorator(func_or_class):
        if TRACING_AVAILABLE:
            try:
                from helpers.dynamic_tracing_controller import conditional_trace as actual_conditional_trace
                return actual_conditional_trace(module_name)(func_or_class)
            except Exception:
                # If tracing fails, just return the original function/class
                return func_or_class
        else:
            # If tracing not available, just return the original function/class
            return func_or_class
    return decorator


# @conditional_trace("complete_task_execution_system")  # Temporarily disabled for debugging
class CompleteTaskExecutionSystem:
    """
    Complete task execution system that orchestrates all available functionality
    for end-to-end task management, execution, and monitoring.
    """
    
    def __init__(self):
        """Initialize the complete task execution system."""
        self.system_id = f"task_system_{int(time.time())}"
        self.supervisor = None
        self.messaging = None
        self.agents = {}
        self.execution_log = []
        self.tracing_enabled = False
        
        # Error tracking
        self.errors = []
        self.warnings = []
        self.critical_failures = 0
        self.initialization_success = True
        
        print(f"\n🎯 INITIALIZING TASK EXECUTION SYSTEM: {self.system_id}")
        print("=" * 60)
        
        # Initialize components with strict error checking
        try:
            print("🔧 Step 1: Initializing tracing...")
            self._initialize_tracing()
            print("✅ Step 1 completed")
            
            print("🔧 Step 2: Initializing supervisor...")
            self._initialize_supervisor()
            print("✅ Step 2 completed")
            
            print("🔧 Step 3: Initializing messaging...")
            self._initialize_messaging()
            print("✅ Step 3 completed")
            
            print("🔧 Step 4: Initializing agents...")
            self._initialize_agents()
            print("✅ Step 4 completed")
            
            print("🔧 Step 5: Validating system readiness...")
            # Validate system readiness
            self._validate_system_readiness()
            print("✅ Step 5 completed")
            
        except Exception as e:
            self.initialization_success = False
            self._log_error(f"System initialization failed: {e}", critical=True)
            print(f"🚨 Initialization failed at step with error: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Failed to initialize task execution system: {e}")
    
    def _log_error(self, message: str, critical: bool = False):
        """Log an error and track it in the system."""
        if critical:
            self.critical_failures += 1
            self.errors.append(f"CRITICAL: {message}")
            logger.error(f"CRITICAL ERROR: {message}")
            print(f"🚨 CRITICAL ERROR: {message}")
        else:
            self.errors.append(message)
            logger.error(message)
            print(f"❌ ERROR: {message}")
    
    def _log_warning(self, message: str):
        """Log a warning and track it in the system."""
        self.warnings.append(message)
        logger.warning(message)
        print(f"⚠️ WARNING: {message}")
    
    def _validate_system_readiness(self):
        """Validate that the system is ready for task execution."""
        print(f"\n🔍 VALIDATING SYSTEM READINESS...")
        
        # Check CRITICAL components - these are REQUIRED for system operation
        critical_missing = []
        
        if not SUPERVISOR_AVAILABLE or self.supervisor is None:
            critical_missing.append("Backend Supervisor Agent")
        
        if not MESSAGING_AVAILABLE or self.messaging is None:
            critical_missing.append("Redis Messaging System")
        
        if not SPECIALIZED_AGENTS_AVAILABLE or len(self.agents) == 0:
            critical_missing.append("Specialized Agents")
            
        # Azure AI is required for real operations
        if self.supervisor and (not hasattr(self.supervisor, 'azure_available') or not self.supervisor.azure_available):
            critical_missing.append("Azure AI Foundry")
            
        # Check for critical failures
        if critical_missing:
            error_msg = f"CRITICAL SYSTEM COMPONENTS MISSING: {', '.join(critical_missing)}"
            self._log_error(error_msg, critical=True)
            self._log_error("System cannot operate without these essential components", critical=True)
        
        # Stop if we have critical failures
        if self.critical_failures > 0:
            raise RuntimeError(f"System has {self.critical_failures} critical failures - cannot proceed")
        
        print(f"✅ All critical components validated - System ready for production task execution")
        print(f"   Errors: {len(self.errors)}, Warnings: {len(self.warnings)}, Critical: {self.critical_failures}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        # System is healthy ONLY if all critical components are working
        healthy = (
            self.critical_failures == 0 and 
            self.supervisor is not None and
            self.messaging is not None and
            len(self.agents) > 0 and
            hasattr(self.supervisor, 'azure_available') and 
            self.supervisor.azure_available
        )
        
        return {
            "healthy": healthy,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "critical_failures": self.critical_failures,
            "error_details": self.errors[-5:],  # Last 5 errors
            "warning_details": self.warnings[-5:],  # Last 5 warnings
            "components_available": {
                "supervisor": self.supervisor is not None,
                "messaging": self.messaging is not None,
                "tracing": self.tracing_enabled,
                "agents": len(self.agents)
            }
        }
        
    @conditional_trace()
    def _initialize_tracing(self):
        """Initialize the dynamic tracing system."""
        if not TRACING_AVAILABLE:
            self._log_warning("Tracing not available - continuing without tracing")
            return
            
        try:
            # Enable agent communication tracing
            enable_agent_communication_tracing()
            
            # Configure tracing for this session
            TRACING_CONTROLLER.enable_module_tracing("complete_task_execution_system")
            TRACING_CONTROLLER.enable_module_tracing("backend_supervisor_role_tools")
            TRACING_CONTROLLER.enable_module_tracing("simple_messaging")
            
            self.tracing_enabled = True
            print("✅ Dynamic tracing system initialized and enabled")
            print(f"📊 Tracing status: {get_tracing_summary()}")
            
        except Exception as e:
            self._log_error(f"Tracing initialization failed: {e}")
            self.tracing_enabled = False
    
    @conditional_trace()
    def _initialize_supervisor(self):
        """Initialize the Backend Supervisor Agent."""
        if not SUPERVISOR_AVAILABLE:
            self._log_error("Backend Supervisor not available - core functionality missing", critical=True)
            return
            
        try:
            self.supervisor = BackendSupervisorAgent()
            
            # Check if Azure AI is properly configured for real agent operations
            if not hasattr(self.supervisor, 'azure_available') or not self.supervisor.azure_available:
                self._log_error("Azure AI Foundry not available - system requires Azure AI for agent operations", critical=True)
                return
                
            if not hasattr(self.supervisor, 'project_client') or self.supervisor.project_client is None:
                self._log_error("Azure AI Projects client not initialized - PROJECT_ENDPOINT or credentials missing", critical=True)
                return
                
            print("✅ Backend Supervisor Agent initialized with Azure AI")
        except Exception as e:
            self._log_error(f"Supervisor initialization failed: {e}", critical=True)
            self.supervisor = None
    
    @conditional_trace()
    def _initialize_messaging(self):
        """Initialize the messaging system."""
        if not MESSAGING_AVAILABLE:
            self._log_error("Messaging system not available - agent coordination impossible", critical=True)
            return
            
        try:
            # Try Redis first, require it for production system
            if not REDIS_AVAILABLE:
                self._log_error("Redis not available - system requires Redis for messaging", critical=True)
                return
                
            self.messaging = create_simple_messaging(use_redis=True)
            
            # Verify Redis connection is actually working
            if not self.messaging or not hasattr(self.messaging, 'redis_client'):
                self._log_error("Redis messaging initialization failed - no Redis connection", critical=True)
                self.messaging = None
                return
                
            print(f"✅ Messaging system initialized with Redis")
        except Exception as e:
            self._log_error(f"Messaging initialization failed: {e}", critical=True)
            self.messaging = None
    
    @conditional_trace()
    def _initialize_agents(self):
        """Initialize specialized agents if available."""
        if not SPECIALIZED_AGENTS_AVAILABLE:
            self._log_error("Specialized agents not available - system requires agent modules", critical=True)
            return
            
        if self.supervisor is None:
            self._log_error("Cannot initialize agents without supervisor - supervisor initialization failed", critical=True)
            return
            
        try:
            # Initialize available specialized agents
            agent_configs = [
                ("web_research", "research", WebResearchAnalyst),
                ("project_planner", "planning", ProjectPlanner),
                ("devops", "devops", DevOpsAgent),
                ("worker", "implementation", WorkerAgent),
                ("testing", "testing", TestingAgent),
                ("documentation", "documentation", DocumentationAgent)
            ]
            
            successful_agents = 0
            
            for agent_id, agent_type, agent_class in agent_configs:
                try:
                    # Get project_client from supervisor for agent initialization
                    project_client = getattr(self.supervisor, 'project_client', None)
                    
                    # Use Azure AI Foundry client if available, otherwise skip
                    if project_client is None and hasattr(self.supervisor, 'client'):
                        # Try Azure AI Foundry client instead
                        project_client = getattr(self.supervisor, 'client', None)
                    
                    if project_client is None:
                        self._log_warning(f"No Azure AI client available for {agent_type} agent - creating with communication only")
                        # Create agent with fixed communication system
                        if FIXED_COMMUNICATION_AVAILABLE:
                            agent = create_communication_enabled_agent(
                                agent_class,
                                project_client=None,  # Will be handled gracefully
                                agent_id=agent_id,
                                agent_type=agent_type,
                                capabilities=[agent_type, "communication"],
                                supervisor_id="backend-supervisor"
                            )
                            self.agents[agent_id] = agent
                            successful_agents += 1
                            print(f"✅ {agent_type.title()} Agent initialized with communication: {agent_id}")
                        continue
                    
                    # Try to create agent with fixed communication system
                    if FIXED_COMMUNICATION_AVAILABLE:
                        agent = create_communication_enabled_agent(
                            agent_class,
                            project_client=project_client,
                            agent_id=agent_id,
                            agent_type=agent_type,
                            capabilities=[agent_type, "communication"],
                            supervisor_id="backend-supervisor"
                        )
                    else:
                        # Fallback to basic agent creation
                        try:
                            agent = agent_class(
                                project_client=project_client,
                                agent_id=agent_id,
                                agent_type=agent_type
                            )
                        except TypeError:
                            agent = agent_class(project_client=project_client)
                    
                    self.agents[agent_id] = agent
                    successful_agents += 1
                    print(f"✅ {agent_type.title()} Agent initialized: {agent_id}")
                    
                except Exception as e:
                    self._log_warning(f"Failed to initialize {agent_type} agent: {e}")
                    # Don't mark as critical since communication agents can still work
            
            if successful_agents == 0:
                self._log_error("No agents successfully initialized - system cannot function", critical=True)
            else:
                print(f"✅ Successfully initialized {successful_agents}/{len(agent_configs)} agents")
                    
        except Exception as e:
            self._log_error(f"Agent initialization failed: {e}", critical=True)
    
    @conditional_trace()
    def create_and_execute_task(self, task_description: str, requirements: str = "") -> Dict[str, Any]:
        """
        Complete end-to-end task creation and execution workflow.
        
        Args:
            task_description: Description of the task to create and execute
            requirements: Additional requirements and specifications
            
        Returns:
            Dict containing execution results and metrics
        """
        print(f"\n🚀 STARTING END-TO-END TASK EXECUTION")
        print("=" * 50)
        print(f"📝 Task: {task_description}")
        print(f"📋 Requirements: {requirements or 'None specified'}")
        
        # Check system health before proceeding
        health = self.get_system_health()
        if not health["healthy"]:
            error_msg = f"System is not healthy - {health['errors']} errors, {health['critical_failures']} critical failures"
            self._log_error(error_msg, critical=True)
            return {
                "task_description": task_description,
                "requirements": requirements,
                "start_time": datetime.now(timezone.utc).isoformat(),
                "end_time": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": error_msg,
                "phases": [],
                "system_health": health
            }
        
        execution_results = {
            "task_description": task_description,
            "requirements": requirements,
            "start_time": datetime.now(timezone.utc).isoformat(),
            "phases": [],
            "success": False,
            "error": None,
            "phase_failures": 0
        }
        
        try:
            # Phase 1: Project Planning with Supervisor
            planning_result = self._phase_1_planning(task_description, requirements)
            execution_results["phases"].append(planning_result)
            if not planning_result.get("success"):
                execution_results["phase_failures"] += 1
                self._log_error("Phase 1 (Planning) failed")
            
            # Phase 2: Agent Communication Setup
            communication_result = self._phase_2_communication(planning_result)
            execution_results["phases"].append(communication_result)
            if not communication_result.get("success"):
                execution_results["phase_failures"] += 1
                self._log_error("Phase 2 (Communication) failed")
            
            # Phase 3: Task Distribution and Execution
            execution_result = self._phase_3_execution(planning_result, communication_result)
            execution_results["phases"].append(execution_result)
            if not execution_result.get("success"):
                execution_results["phase_failures"] += 1
                self._log_error("Phase 3 (Execution) failed")
            
            # Phase 4: Monitoring and Progress Tracking
            monitoring_result = self._phase_4_monitoring(execution_result)
            execution_results["phases"].append(monitoring_result)
            if not monitoring_result.get("success"):
                execution_results["phase_failures"] += 1
                self._log_error("Phase 4 (Monitoring) failed")
            
            # Phase 5: Results Consolidation
            consolidation_result = self._phase_5_consolidation()
            execution_results["phases"].append(consolidation_result)
            if not consolidation_result.get("success"):
                execution_results["phase_failures"] += 1
                self._log_error("Phase 5 (Consolidation) failed")
            
            # Determine overall success based on phase failures
            if execution_results["phase_failures"] == 0:
                execution_results["success"] = True
                print(f"\n🎉 TASK EXECUTION COMPLETED SUCCESSFULLY!")
            elif execution_results["phase_failures"] <= 2:
                execution_results["success"] = True
                self._log_warning(f"Task completed with {execution_results['phase_failures']} phase failures")
                print(f"\n⚠️ TASK EXECUTION COMPLETED WITH WARNINGS ({execution_results['phase_failures']} phase failures)")
            else:
                execution_results["success"] = False
                self._log_error(f"Task failed with {execution_results['phase_failures']} phase failures", critical=True)
                print(f"\n❌ TASK EXECUTION FAILED ({execution_results['phase_failures']} phase failures)")
            
            execution_results["end_time"] = datetime.now(timezone.utc).isoformat()
            
        except Exception as e:
            execution_results["error"] = str(e)
            execution_results["end_time"] = datetime.now(timezone.utc).isoformat()
            execution_results["success"] = False
            self._log_error(f"Task execution failed with exception: {e}", critical=True)
            print(f"\n🚨 TASK EXECUTION FAILED: {e}")
            logger.exception("Task execution failed")
            
        return execution_results
    
    @conditional_trace()
    def _phase_1_planning(self, task_description: str, requirements: str) -> Dict[str, Any]:
        """Phase 1: Project planning and GitHub issue creation."""
        print(f"\n📋 PHASE 1: PROJECT PLANNING AND ISSUE CREATION")
        print("-" * 50)
        
        phase_result = {
            "phase": "planning",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "success": False
        }
        
        try:
            if not self.supervisor:
                raise Exception("Backend Supervisor not available")
            
            # Create detailed project plan
            print(f"🎯 Creating detailed project plan...")
            planning_result = self.supervisor.create_detailed_issue(task_description, requirements)
            
            phase_result.update({
                "github_issue_url": planning_result.get("issue_url"),
                "issue_number": planning_result.get("issue_number"),
                "subtasks_count": planning_result.get("subtasks_count", 0),
                "estimated_hours": planning_result.get("estimated_hours", 0),
                "agent_types_required": planning_result.get("agent_types_required", []),
                "success": True
            })
            
            print(f"✅ Project planning completed!")
            print(f"   🔗 GitHub Issue: {planning_result.get('issue_url')}")
            print(f"   📊 Subtasks: {planning_result.get('subtasks_count', 0)}")
            print(f"   ⏱️ Estimated Hours: {planning_result.get('estimated_hours', 0)}")
            print(f"   🤖 Agent Types: {', '.join(planning_result.get('agent_types_required', []))}")
            
        except Exception as e:
            phase_result["error"] = str(e)
            print(f"❌ Planning phase failed: {e}")
            
        phase_result["end_time"] = datetime.now(timezone.utc).isoformat()
        return phase_result
    
    @conditional_trace()
    def _phase_2_communication(self, planning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Agent communication setup and coordination."""
        print(f"\n💬 PHASE 2: AGENT COMMUNICATION SETUP")
        print("-" * 50)
        
        phase_result = {
            "phase": "communication",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "agents_registered": 0,
            "messages_sent": 0
        }
        
        try:
            if not self.messaging:
                print("⚠️ Messaging system not available - skipping communication setup")
                phase_result["success"] = True
                phase_result["skip_reason"] = "No messaging system"
                phase_result["end_time"] = datetime.now(timezone.utc).isoformat()
                return phase_result
            
            # Register available agents with supervisor
            print(f"📡 Registering agents with supervisor...")
            
            for agent_id, agent in self.agents.items():
                try:
                    if hasattr(agent, 'register_with_supervisor'):
                        agent.register_with_supervisor()
                        phase_result["agents_registered"] += 1
                        print(f"✅ Registered {agent_id} agent")
                    else:
                        print(f"⚠️ {agent_id} agent doesn't support communication")
                        
                except Exception as e:
                    print(f"❌ Failed to register {agent_id}: {e}")
            
            # Send initial coordination messages
            if planning_result.get("success") and phase_result["agents_registered"] > 0:
                print(f"📨 Sending coordination messages...")
                
                coordination_message = {
                    "task_description": planning_result.get("task_description", ""),
                    "github_issue": planning_result.get("github_issue_url"),
                    "subtasks_count": planning_result.get("subtasks_count", 0),
                    "agent_types_needed": planning_result.get("agent_types_required", [])
                }
                
                for agent_id in self.agents.keys():
                    try:
                        success = send_task_to_agent(
                            self.messaging, 
                            "task-coordinator", 
                            agent_id, 
                            coordination_message
                        )
                        if success:
                            phase_result["messages_sent"] += 1
                            
                    except Exception as e:
                        print(f"❌ Failed to send message to {agent_id}: {e}")
            
            phase_result["success"] = True
            print(f"✅ Communication setup completed!")
            print(f"   📡 Agents registered: {phase_result['agents_registered']}")
            print(f"   📨 Messages sent: {phase_result['messages_sent']}")
            
        except Exception as e:
            phase_result["error"] = str(e)
            print(f"❌ Communication phase failed: {e}")
            
        phase_result["end_time"] = datetime.now(timezone.utc).isoformat()
        return phase_result
    
    @conditional_trace()
    def _phase_3_execution(self, planning_result: Dict[str, Any], communication_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Real task distribution and execution with actual agent work."""
        print(f"\n⚡ PHASE 3: REAL TASK EXECUTION")
        print("-" * 50)
        
        phase_result = {
            "phase": "execution",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "tasks_executed": 0,
            "execution_details": [],
            "deliverables": []
        }
        
        try:
            # Get real task details from planning phase
            main_task = planning_result.get("task_description", "")
            requirements = planning_result.get("requirements", "")
            github_issue_url = planning_result.get("github_issue_url", "")
            subtasks_count = planning_result.get("subtasks_count", 0)
            agent_types_needed = planning_result.get("agent_types_required", [])
            
            print(f"🎯 Executing {subtasks_count} real subtasks...")
            print(f"🤖 Required agent types: {', '.join(agent_types_needed)}")
            print(f"📋 Main task: {main_task}")
            
            # Create specific subtasks based on the main task and requirements
            specific_subtasks = self._create_specific_subtasks(main_task, requirements, agent_types_needed)
            
            # Execute each subtask with the appropriate agent
            for i, subtask_info in enumerate(specific_subtasks, 1):
                task_detail = {
                    "task_number": i,
                    "agent_type": subtask_info["agent_type"],
                    "subtask_description": subtask_info["description"],
                    "start_time": datetime.now(timezone.utc).isoformat(),
                    "success": False,
                    "deliverables": []
                }
                
                try:
                    print(f"   🔧 Task {i}: {subtask_info['description']}")
                    print(f"   🤖 Using {subtask_info['agent_type']} agent...")
                    
                    # Find the appropriate agent
                    available_agent = self._find_agent_for_type(subtask_info["agent_type"])
                    
                    if available_agent:
                        agent_id_used = self._get_agent_id(available_agent)
                        
                        # Execute REAL work with the agent
                        execution_result = self._execute_real_task_with_agent(
                            available_agent, 
                            subtask_info,
                            main_task,
                            requirements,
                            github_issue_url
                        )
                        
                        if execution_result["success"]:
                            task_detail["success"] = True
                            task_detail["agent_used"] = agent_id_used
                            task_detail["deliverables"] = execution_result.get("deliverables", [])
                            task_detail["result_summary"] = execution_result.get("summary", "")
                            phase_result["tasks_executed"] += 1
                            phase_result["deliverables"].extend(execution_result.get("deliverables", []))
                            
                            print(f"   ✅ Task {i} completed successfully")
                            if execution_result.get("deliverables"):
                                print(f"      📦 Deliverables: {len(execution_result['deliverables'])} items")
                                
                            # Send real progress update
                            if self.messaging:
                                progress_data = {
                                    "task_number": i,
                                    "progress": 100,
                                    "status": "completed",
                                    "agent_type": subtask_info["agent_type"],
                                    "deliverables": execution_result.get("deliverables", []),
                                    "summary": execution_result.get("summary", "")
                                }
                                send_status_update(self.messaging, agent_id_used, "task-coordinator", progress_data)
                        else:
                            task_detail["error"] = execution_result.get("error", "Unknown execution failure")
                            print(f"   ❌ Task {i} failed: {task_detail['error']}")
                        
                    else:
                        task_detail["error"] = f"No {subtask_info['agent_type']} agent available"
                        print(f"   ❌ Task {i}: No {subtask_info['agent_type']} agent available")
                        
                except Exception as e:
                    task_detail["error"] = str(e)
                    print(f"   ❌ Task {i} failed with exception: {e}")
                    logger.exception(f"Task {i} execution failed")
                
                task_detail["end_time"] = datetime.now(timezone.utc).isoformat()
                phase_result["execution_details"].append(task_detail)
            
            # Calculate real success metrics
            successful_tasks = sum(1 for task in phase_result["execution_details"] if task.get("success"))
            total_deliverables = len(phase_result["deliverables"])
            
            phase_result["success"] = successful_tasks > 0
            print(f"✅ Real task execution completed!")
            print(f"   ⚡ Tasks executed successfully: {successful_tasks}/{len(specific_subtasks)}")
            print(f"   📦 Total deliverables produced: {total_deliverables}")
            print(f"   📊 Success rate: {(successful_tasks/max(len(specific_subtasks), 1)*100):.1f}%")
            
        except Exception as e:
            phase_result["error"] = str(e)
            print(f"❌ Real execution phase failed: {e}")
            logger.exception("Phase 3 execution failed")
            
        phase_result["end_time"] = datetime.now(timezone.utc).isoformat()
        return phase_result
    
    def _create_specific_subtasks(self, main_task: str, requirements: str, agent_types_needed: List[str]) -> List[Dict[str, Any]]:
        """Create specific, actionable subtasks for each agent type based on the main task."""
        subtasks = []
        
        # Map agent types to specific subtasks based on the main task
        task_lower = main_task.lower()
        req_lower = requirements.lower()
        
        for agent_type in agent_types_needed:
            if "research" in agent_type or agent_type == "web_research":
                subtasks.append({
                    "agent_type": agent_type,
                    "description": f"Research and analyze: {main_task}",
                    "specific_requirements": "Gather comprehensive information, identify key issues, and provide analysis",
                    "expected_deliverables": ["research_report", "analysis_summary", "recommendations"]
                })
            
            elif "planning" in agent_type or agent_type == "project_planner":
                subtasks.append({
                    "agent_type": agent_type,
                    "description": f"Create detailed implementation plan for: {main_task}",
                    "specific_requirements": "Break down into actionable steps, estimate timelines, identify dependencies",
                    "expected_deliverables": ["project_plan", "timeline", "resource_requirements"]
                })
            
            elif "devops" in agent_type:
                subtasks.append({
                    "agent_type": agent_type,
                    "description": f"Setup infrastructure and deployment for: {main_task}",
                    "specific_requirements": "Configure CI/CD, setup environments, ensure scalability",
                    "expected_deliverables": ["infrastructure_config", "deployment_scripts", "monitoring_setup"]
                })
            
            elif "worker" in agent_type or "implementation" in agent_type:
                subtasks.append({
                    "agent_type": agent_type,
                    "description": f"Implement core functionality for: {main_task}",
                    "specific_requirements": "Write code, implement features, ensure functionality meets requirements",
                    "expected_deliverables": ["implementation_code", "feature_modules", "integration_points"]
                })
            
            elif "testing" in agent_type:
                subtasks.append({
                    "agent_type": agent_type,
                    "description": f"Create comprehensive test suite for: {main_task}",
                    "specific_requirements": "Unit tests, integration tests, performance tests, validation",
                    "expected_deliverables": ["test_suite", "test_reports", "quality_metrics"]
                })
            
            elif "documentation" in agent_type:
                subtasks.append({
                    "agent_type": agent_type,
                    "description": f"Create comprehensive documentation for: {main_task}",
                    "specific_requirements": "Technical docs, user guides, API documentation, architecture docs",
                    "expected_deliverables": ["technical_documentation", "user_guides", "api_docs"]
                })
            
            else:
                # Generic subtask for unknown agent types
                subtasks.append({
                    "agent_type": agent_type,
                    "description": f"Perform {agent_type} work for: {main_task}",
                    "specific_requirements": requirements,
                    "expected_deliverables": [f"{agent_type}_output", "results_summary"]
                })
        
        return subtasks
    
    def _find_agent_for_type(self, agent_type: str) -> Any:
        """Find the best available agent for the specified type."""
        # Direct match first
        for agent_id, agent in self.agents.items():
            if agent_type in agent_id or (hasattr(agent, 'agent_type') and agent.agent_type == agent_type):
                return agent
        
        # Fuzzy match based on capabilities
        for agent_id, agent in self.agents.items():
            if any(keyword in agent_id for keyword in agent_type.split('_')):
                return agent
        
        return None
    
    def _get_agent_id(self, agent: Any) -> str:
        """Get the ID of an agent."""
        for agent_id, stored_agent in self.agents.items():
            if stored_agent == agent:
                return agent_id
        return "unknown_agent"
    
    def _execute_real_task_with_agent(self, agent: Any, subtask_info: Dict[str, Any], 
                                    main_task: str, requirements: str, github_issue_url: str) -> Dict[str, Any]:
        """Execute a real task with the specified agent and return actual results."""
        execution_result = {
            "success": False,
            "deliverables": [],
            "summary": "",
            "error": None
        }
        
        try:
            print(f"      🚀 Starting real execution with {subtask_info['agent_type']} agent...")
            
            # Prepare comprehensive task prompt
            task_prompt = self._create_comprehensive_task_prompt({
                "main_task": main_task,
                "subtask_description": subtask_info["description"],
                "requirements": requirements,
                "github_issue_url": github_issue_url,
                "expected_deliverables": subtask_info.get("expected_deliverables", []),
                "specific_requirements": subtask_info.get("specific_requirements", "")
            })
            
            # Execute task using the correct Azure AI agent method
            result = None
            
            # Method 1: Use Azure AI agent's send_message method (most common)
            if hasattr(agent, 'send_message'):
                print(f"      📧 Using agent.send_message() for real AI execution...")
                result = agent.send_message(task_prompt)
                print(f"      ✅ Agent responded with {len(str(result))} characters")
                
            # Method 2: Try agent-specific execution methods
            elif hasattr(agent, 'execute_task'):
                print(f"      🎯 Using agent.execute_task() method...")
                result = agent.execute_task(task_prompt)
                
            elif hasattr(agent, 'perform_task'):
                print(f"      🎯 Using agent.perform_task() method...")
                result = agent.perform_task(task_prompt)
                
            elif hasattr(agent, 'run_task'):
                print(f"      🎯 Using agent.run_task() method...")
                result = agent.run_task(task_prompt)
            
            # Method 3: Try Azure AI chat functionality
            elif hasattr(agent, 'chat'):
                print(f"      💬 Using agent.chat() method...")
                result = agent.chat(task_prompt)
            
            # Method 4: Try callable agent
            elif hasattr(agent, '__call__'):
                print(f"      📞 Using callable agent...")
                result = agent(task_prompt)
                
            else:
                # If no methods available, provide informative error
                available_methods = [method for method in dir(agent) if not method.startswith('_') and callable(getattr(agent, method))]
                raise Exception(f"Agent has no recognized execution methods. Available methods: {available_methods[:10]}")
            
            # Process the result
            if result:
                execution_result["success"] = True
                execution_result["summary"] = self._extract_summary_from_result(result)
                execution_result["deliverables"] = self._extract_deliverables_from_result(result, subtask_info)
                
                print(f"      ✅ Agent execution completed successfully")
                print(f"      📋 Summary: {execution_result['summary'][:100]}...")
                print(f"      📦 Generated {len(execution_result['deliverables'])} deliverable(s)")
                
            else:
                execution_result["error"] = "Agent returned no result"
                print(f"      ⚠️ Agent returned empty result")
                
        except Exception as e:
            execution_result["error"] = f"Agent execution failed: {str(e)}"
            print(f"      ❌ Agent execution failed: {e}")
            logger.exception(f"Agent execution failed for {subtask_info['agent_type']}")
        
        return execution_result
    
    def _create_task_prompt(self, task_context: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for the agent."""
        return f"""
Task: {task_context['subtask_description']}

Main Project: {task_context['main_task']}

Requirements:
{task_context['specific_requirements']}

Overall Requirements:
{task_context['requirements']}

Expected Deliverables:
{', '.join(task_context.get('expected_deliverables', []))}

GitHub Issue: {task_context.get('github_issue_url', 'Not available')}

Please provide a comprehensive response that addresses all requirements and produces the expected deliverables.
"""
    
    def _create_comprehensive_task_prompt(self, task_context: Dict[str, Any]) -> str:
        """Create a comprehensive task prompt for generic execution."""
        return f"""
You are tasked with: {task_context['subtask_description']}

CONTEXT:
- Main Project: {task_context['main_task']}
- Specific Requirements: {task_context['specific_requirements']}
- Overall Requirements: {task_context['requirements']}

EXPECTED DELIVERABLES:
{chr(10).join(f"- {deliverable}" for deliverable in task_context.get('expected_deliverables', []))}

INSTRUCTIONS:
1. Analyze the task thoroughly
2. Create a detailed plan of action
3. Produce the expected deliverables
4. Provide a comprehensive summary of your work

Please provide a structured response with clear sections for each deliverable.
"""
    
    def _extract_summary_from_result(self, result: Any) -> str:
        """Extract a summary from the agent's result."""
        if isinstance(result, dict):
            return result.get('summary', result.get('description', str(result)[:200]))
        elif isinstance(result, str):
            return result[:200] + "..." if len(result) > 200 else result
        else:
            return str(result)[:200]
    
    def _extract_deliverables_from_result(self, result: Any, subtask_info: Dict[str, Any]) -> List[str]:
        """Extract deliverables from the agent's result."""
        deliverables = []
        
        if isinstance(result, dict):
            # Look for explicit deliverables
            if 'deliverables' in result:
                deliverables.extend(result['deliverables'])
            else:
                # Extract based on expected deliverables
                expected = subtask_info.get('expected_deliverables', [])
                for expected_item in expected:
                    if expected_item in result:
                        deliverables.append(f"{expected_item}: {str(result[expected_item])[:100]}")
                
                # If no specific deliverables found, use the whole result
                if not deliverables:
                    deliverables.append(f"{subtask_info['agent_type']}_output: {str(result)[:100]}")
        
        elif isinstance(result, str):
            # For string results, create a single deliverable
            deliverables.append(f"{subtask_info['agent_type']}_result: {result[:100]}")
        
        else:
            deliverables.append(f"{subtask_info['agent_type']}_output: {str(result)[:100]}")
        
        return deliverables
    
    @conditional_trace()
    def _phase_4_monitoring(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Monitoring and progress tracking."""
        print(f"\n📊 PHASE 4: MONITORING AND PROGRESS TRACKING")
        print("-" * 50)
        
        phase_result = {
            "phase": "monitoring",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "metrics_collected": 0
        }
        
        try:
            # Collect execution metrics
            tasks_executed = execution_result.get("tasks_executed", 0)
            execution_details = execution_result.get("execution_details", [])
            
            print(f"📈 Collecting execution metrics...")
            
            # Performance metrics
            successful_tasks = sum(1 for task in execution_details if task.get("success"))
            failed_tasks = len(execution_details) - successful_tasks
            
            metrics = {
                "total_tasks": len(execution_details),
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": (successful_tasks / max(len(execution_details), 1)) * 100,
                "average_execution_time": self._calculate_average_execution_time(execution_details)
            }
            
            phase_result["metrics"] = metrics
            phase_result["metrics_collected"] = len(metrics)
            
            print(f"📊 Execution Metrics:")
            print(f"   ✅ Successful tasks: {successful_tasks}")
            print(f"   ❌ Failed tasks: {failed_tasks}")
            print(f"   📈 Success rate: {metrics['success_rate']:.1f}%")
            print(f"   ⏱️ Avg execution time: {metrics['average_execution_time']:.2f}s")
            
            # Log tracing summary if available
            if self.tracing_enabled:
                print(f"\n🔍 Tracing Summary:")
                print(f"   {get_tracing_summary()}")
            
            phase_result["success"] = True
            
        except Exception as e:
            phase_result["error"] = str(e)
            print(f"❌ Monitoring phase failed: {e}")
            
        phase_result["end_time"] = datetime.now(timezone.utc).isoformat()
        return phase_result
    
    @conditional_trace()
    def _phase_5_consolidation(self) -> Dict[str, Any]:
        """Phase 5: Results consolidation and cleanup."""
        print(f"\n📋 PHASE 5: RESULTS CONSOLIDATION")
        print("-" * 50)
        
        phase_result = {
            "phase": "consolidation",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "success": False
        }
        
        try:
            print(f"📝 Consolidating execution results...")
            
            # Generate execution summary
            summary = {
                "system_id": self.system_id,
                "components_used": {
                    "supervisor": self.supervisor is not None,
                    "messaging": self.messaging is not None,
                    "tracing": self.tracing_enabled,
                    "agents_count": len(self.agents)
                },
                "execution_log_entries": len(self.execution_log)
            }
            
            phase_result["summary"] = summary
            
            print(f"📊 System Summary:")
            print(f"   🎯 Backend Supervisor: {'✅' if summary['components_used']['supervisor'] else '❌'}")
            print(f"   💬 Messaging System: {'✅' if summary['components_used']['messaging'] else '❌'}")
            print(f"   🔍 Tracing System: {'✅' if summary['components_used']['tracing'] else '❌'}")
            print(f"   🤖 Agents Available: {summary['components_used']['agents_count']}")
            
            # Save execution log
            log_file = f"execution_log_{self.system_id}.json"
            try:
                import json
                with open(log_file, 'w') as f:
                    json.dump({
                        "system_id": self.system_id,
                        "summary": summary,
                        "execution_log": self.execution_log
                    }, f, indent=2)
                print(f"💾 Execution log saved: {log_file}")
            except Exception as e:
                print(f"⚠️ Failed to save execution log: {e}")
            
            phase_result["success"] = True
            
        except Exception as e:
            phase_result["error"] = str(e)
            print(f"❌ Consolidation phase failed: {e}")
            
        phase_result["end_time"] = datetime.now(timezone.utc).isoformat()
        return phase_result
    
    @conditional_trace()
    def _calculate_average_execution_time(self, execution_details: List[Dict[str, Any]]) -> float:
        """Calculate average execution time from execution details."""
        if not execution_details:
            return 0.0
        
        total_time = 0.0
        count = 0
        
        for task in execution_details:
            start_time = task.get("start_time")
            end_time = task.get("end_time")
            
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration = (end_dt - start_dt).total_seconds()
                    total_time += duration
                    count += 1
                except Exception:
                    continue
        
        return total_time / max(count, 1)
    
    @conditional_trace()
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and component availability."""
        return {
            "system_id": self.system_id,
            "components": {
                "backend_supervisor": self.supervisor is not None,
                "messaging_system": self.messaging is not None,
                "tracing_enabled": self.tracing_enabled,
                "agents_available": list(self.agents.keys()),
                "agents_count": len(self.agents)
            },
            "capabilities": {
                "project_planning": SUPERVISOR_AVAILABLE,
                "dynamic_tracing": TRACING_AVAILABLE,
                "agent_communication": MESSAGING_AVAILABLE,
                "redis_messaging": REDIS_AVAILABLE,
                "specialized_agents": SPECIALIZED_AGENTS_AVAILABLE,
                "comprehensive_logging": LOGGER_AVAILABLE
            }
        }


@conditional_trace("main")
def main():
    """Main execution function."""
    print("\n🎉 COMPLETE TASK EXECUTION SYSTEM DEMO")
    print("=" * 65)
    
    try:
        # Initialize the complete system
        print("🔧 Creating CompleteTaskExecutionSystem instance...")
        system = CompleteTaskExecutionSystem()
        print("✅ System instance created successfully")
        
        # Show system health
        print("🔧 Getting system health...")
        health = system.get_system_health()
        print("✅ System health retrieved successfully")
        print(f"\n📊 SYSTEM HEALTH STATUS:")
        print(f"   Overall Health: {'✅ HEALTHY' if health['healthy'] else '🚨 UNHEALTHY'}")
        print(f"   Errors: {health['errors']}")
        print(f"   Warnings: {health['warnings']}")
        print(f"   Critical Failures: {health['critical_failures']}")
        
        if health['error_details']:
            print(f"   Recent Errors: {health['error_details']}")
        
        # Show component status
        print(f"\n📊 COMPONENT STATUS:")
        status = system.get_system_status()
        for component, available in status["capabilities"].items():
            print(f"   {component}: {'✅' if available else '❌'}")
        
        # Check if system is ready for task execution
        if not health["healthy"]:
            print(f"\n🚨 SYSTEM NOT READY FOR TASK EXECUTION")
            print(f"❌ System has {health['critical_failures']} critical failures and {health['errors']} errors")
            print(f"\n🔧 REQUIRED COMPONENTS FOR SYSTEM OPERATION:")
            print(f"   • Azure AI Foundry - Set PROJECT_ENDPOINT environment variable")
            print(f"   • Azure CLI Authentication - Run 'az login'")
            print(f"   • Redis Server - Install and start Redis")
            print(f"   • All specialized agent modules")
            print(f"   • Backend supervisor with Azure AI integration")
            print(f"\n💡 This is a production system that requires all components to be properly configured.")
            print(f"❌ Mock implementations are not allowed - system will not proceed with missing components")
            return {"success": False, "error": "System not healthy - missing critical components", "health": health}
        
        # Example task execution
        task_description = "Comprehensive Codebase Analysis and Refactoring"
        requirements = """
        Requirements:
        - Scan the whole codebase for issues and redundancies
        - Fix what is wrong and remove unnecessary code
        - Unify scattered code into main functions and methods in complete_task_execution_system
        - Absorb functionality from extra files into the main system
        - Remove redundant files after absorption
        - Validate repository structure and optimize organization
        - Consolidate duplicate functionality across modules
        - Ensure proper import structure and dependencies
        - Implement best practices for code organization
        - Create a clean, maintainable codebase architecture
        """
        
        print(f"\n🚀 EXECUTING SAMPLE TASK:")
        print(f"📝 Task: {task_description}")
        print(f"📋 Requirements: Comprehensive codebase cleanup and refactoring")
        
        # Execute the complete workflow
        execution_results = system.create_and_execute_task(task_description, requirements)
        
        # Display final results with honest assessment
        print(f"\n📊 FINAL EXECUTION RESULTS:")
        print("=" * 50)
        
        if execution_results['success']:
            if execution_results.get('phase_failures', 0) == 0:
                print(f"✅ SUCCESS: Task completed successfully with no failures")
            else:
                print(f"⚠️ PARTIAL SUCCESS: Task completed with {execution_results.get('phase_failures', 0)} phase failures")
        else:
            print(f"❌ FAILURE: Task execution failed")
            
        print(f"⏱️ Total Phases: {len(execution_results['phases'])}")
        print(f"🕐 Duration: {execution_results.get('start_time', '')} → {execution_results.get('end_time', '')}")
        
        if execution_results.get("error"):
            print(f"❌ Error: {execution_results['error']}")
        
        if execution_results.get("phase_failures", 0) > 0:
            print(f"⚠️ Phase Failures: {execution_results['phase_failures']}")
        
        # Show phase results with honest status
        print(f"\n📋 PHASE RESULTS:")
        for i, phase in enumerate(execution_results['phases'], 1):
            phase_name = phase.get('phase', f'Phase {i}')
            phase_success = phase.get('success', False)
            phase_error = phase.get('error', '')
            status_icon = '✅' if phase_success else '❌'
            print(f"   Phase {i} ({phase_name}): {status_icon}")
            if phase_error:
                print(f"      Error: {phase_error}")
        
        # Show final system health
        final_health = system.get_system_health()
        if final_health['errors'] > health['errors'] or final_health['critical_failures'] > health['critical_failures']:
            print(f"\n⚠️ SYSTEM HEALTH DEGRADED DURING EXECUTION:")
            print(f"   New Errors: {final_health['errors'] - health['errors']}")
            print(f"   New Critical Failures: {final_health['critical_failures'] - health['critical_failures']}")
        
        # Show tracing summary if available
        if system.tracing_enabled:
            print(f"\n🔍 FINAL TRACING SUMMARY:")
            print(f"   {get_tracing_summary()}")
        
        print(f"\n🎉 COMPLETE TASK EXECUTION SYSTEM DEMO FINISHED!")
        print(f"📝 Check execution logs for detailed information")
        
        return execution_results
        
    except Exception as e:
        print(f"\n🚨 SYSTEM INITIALIZATION FAILED: {e}")
        if 'logger' in locals():
            logger.exception("System initialization failed")
        return {"success": False, "error": f"System initialization failed: {e}"}


if __name__ == "__main__":
    try:
        results = main()
    except KeyboardInterrupt:
        print(f"\n⚠️ Execution interrupted by user")
    except Exception as e:
        print(f"\n❌ System execution failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n👋 Task Execution System shutting down...")
