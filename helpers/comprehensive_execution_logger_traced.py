"""
Comprehensive Execution Logger - Detailed Agent and Method Tracking System
=========================================================================

This module provides comprehensive logging for all agent operations, method calls,
inputs, outputs, and execution details. It integrates with the existing agent
system and Redis messaging to provide detailed execution traces.

Features:
- Method call tracing with input/output capture
- Agent operation logging with timing
- Redis message flow tracking
- Execution context preservation
- Detailed performance metrics
- Step-by-step execution history
- Error tracking and debugging support
"""

import json
import time
import uuid
import logging
import functools
import inspect
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import traceback
import sys
import os

# Thread-local storage for execution context

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


_local = threading.local()

@trace_class
class LogLevel(Enum):
    """Log levels for execution tracking."""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@trace_class
class ExecutionStatus(Enum):
    """Execution status tracking."""
    STARTED = "STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"

@dataclass
@trace_class
class MethodCall:
    """Detailed method call information."""
    call_id: str
    method_name: str
    class_name: str
    module_name: str
    timestamp: str
    execution_time: float = 0.0
    status: ExecutionStatus = ExecutionStatus.STARTED
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Any = None
    error: Optional[str] = None
    stack_trace: Optional[str] = None
    memory_usage: Optional[float] = None
    agent_context: Optional[Dict[str, Any]] = field(default_factory=dict)

@dataclass
@trace_class
class AgentOperation:
    """Agent-specific operation tracking."""
    operation_id: str
    agent_name: str
    agent_type: str
    operation_type: str
    timestamp: str
    duration: float = 0.0
    status: ExecutionStatus = ExecutionStatus.STARTED
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Any = None
    method_calls: List[MethodCall] = field(default_factory=list)
    messages_sent: List[Dict[str, Any]] = field(default_factory=list)
    messages_received: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
@trace_class
class ExecutionSession:
    """Complete execution session tracking."""
    session_id: str
    session_name: str
    start_time: str
    end_time: Optional[str] = None
    total_duration: float = 0.0
    status: ExecutionStatus = ExecutionStatus.STARTED
    agent_operations: List[AgentOperation] = field(default_factory=list)
    method_calls: List[MethodCall] = field(default_factory=list)
    redis_messages: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    execution_summary: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    warning_count: int = 0

@trace_class
class ComprehensiveExecutionLogger:
    """
    Comprehensive logging system for detailed execution tracking.
    """
    
    def __init__(self, log_dir: str = "logs", session_name: str = None):
        """
        Initialize the comprehensive execution logger.
        
        Args:
            log_dir: Directory to store log files
            session_name: Name for the current execution session
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize session
        self.current_session = ExecutionSession(
            session_id=str(uuid.uuid4()),
            session_name=session_name or f"execution_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=datetime.now(timezone.utc).isoformat()
        )
        
        # Setup logging
        self._setup_logging()
        
        # Performance tracking
        self.method_call_stack = []
        self.operation_stack = []
        
        # Redis message tracking
        self.redis_logger = None
        
        print(f"🎯 COMPREHENSIVE EXECUTION LOGGER STARTED")
        print(f"   📊 Session ID: {self.current_session.session_id}")
        print(f"   📁 Session Name: {self.current_session.session_name}")
        print(f"   🕐 Start Time: {self.current_session.start_time}")
        print(f"   📂 Log Directory: {self.log_dir}")
    
    def _setup_logging(self):
        """Setup detailed logging configuration."""
        # Create session-specific log file
        log_file = self.log_dir / f"{self.current_session.session_name}.log"
        
        # Configure logger
        self.logger = logging.getLogger(f"execution_logger_{self.current_session.session_id}")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    @trace_func
    def start_agent_operation(self, agent_name: str, agent_type: str, 
                            operation_type: str, inputs: Dict[str, Any] = None,
                            metadata: Dict[str, Any] = None) -> str:
        """
        Start tracking an agent operation.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type of agent (worker, testing, etc.)
            operation_type: Type of operation being performed
            inputs: Operation inputs
            metadata: Additional metadata
            
        Returns:
            str: Operation ID for tracking
        """
        operation = AgentOperation(
            operation_id=str(uuid.uuid4()),
            agent_name=agent_name,
            agent_type=agent_type,
            operation_type=operation_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            inputs=inputs or {},
            metadata=metadata or {}
        )
        
        self.current_session.agent_operations.append(operation)
        self.operation_stack.append(operation)
        
        self.logger.info(f"🚀 AGENT OPERATION STARTED: {operation_type}")
        self.logger.info(f"   🤖 Agent: {agent_name} ({agent_type})")
        self.logger.info(f"   🆔 Operation ID: {operation.operation_id}")
        self.logger.info(f"   📥 Inputs: {json.dumps(inputs or {}, indent=2)}")
        
        return operation.operation_id
    
    @trace_func
    def end_agent_operation(self, operation_id: str, outputs: Any = None, 
                          status: ExecutionStatus = ExecutionStatus.COMPLETED,
                          error: str = None):
        """
        End tracking an agent operation.
        
        Args:
            operation_id: Operation ID to end
            outputs: Operation outputs
            status: Final status
            error: Error message if failed
        """
        # Find operation
        operation = None
        for op in self.current_session.agent_operations:
            if op.operation_id == operation_id:
                operation = op
                break
        
        if not operation:
            self.logger.warning(f"Operation {operation_id} not found")
            return
        
        # Update operation
        operation.status = status
        operation.outputs = outputs
        operation.error = error
        operation.duration = (datetime.now(timezone.utc) - 
                             datetime.fromisoformat(operation.timestamp.replace('Z', '+00:00'))).total_seconds()
        
        # Remove from stack
        if self.operation_stack and self.operation_stack[-1].operation_id == operation_id:
            self.operation_stack.pop()
        
        status_emoji = "✅" if status == ExecutionStatus.COMPLETED else "❌"
        self.logger.info(f"{status_emoji} AGENT OPERATION ENDED: {operation.operation_type}")
        self.logger.info(f"   🤖 Agent: {operation.agent_name}")
        self.logger.info(f"   ⏱️ Duration: {operation.duration:.3f}s")
        self.logger.info(f"   📊 Status: {status.value}")
        if outputs:
            self.logger.info(f"   📤 Outputs: {json.dumps(outputs, indent=2) if isinstance(outputs, (dict, list)) else str(outputs)}")
        if error:
            self.logger.error(f"   ❌ Error: {error}")
    
    @trace_func
    def log_method_call(self, func: Callable) -> Callable:
        """
        Decorator to log method calls with detailed information.
        
        Args:
            func: Function to wrap
            
        Returns:
            Callable: Wrapped function with logging
        """
        @functools.wraps(func)
        @trace_func
        def wrapper(*args, **kwargs):
            # Create method call record
            call_id = str(uuid.uuid4())
            method_call = MethodCall(
                call_id=call_id,
                method_name=func.__name__,
                class_name=args[0].__class__.__name__ if args and hasattr(args[0], '__class__') else 'function',
                module_name=func.__module__,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            # Capture inputs (be careful with sensitive data)
            try:
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                # Sanitize inputs (remove large objects, sensitive data)
                inputs = {}
                for name, value in bound_args.arguments.items():
                    if name == 'self':
                        inputs[name] = f"<{value.__class__.__name__} instance>"
                    elif isinstance(value, (str, int, float, bool, list, dict)):
                        # Limit string length
                        if isinstance(value, str) and len(value) > 500:
                            inputs[name] = f"{value[:500]}... (truncated)"
                        else:
                            inputs[name] = value
                    else:
                        inputs[name] = f"<{type(value).__name__}>"
                
                method_call.inputs = inputs
            except Exception as e:
                method_call.inputs = {"error": f"Could not capture inputs: {str(e)}"}
            
            # Add agent context if available
            if hasattr(args[0], 'agent_name'):
                method_call.agent_context = {
                    'agent_name': getattr(args[0], 'agent_name', 'unknown'),
                    'agent_type': getattr(args[0], 'agent_type', 'unknown')
                }
            
            self.current_session.method_calls.append(method_call)
            self.method_call_stack.append(method_call)
            
            self.logger.debug(f"🔧 METHOD CALL STARTED: {method_call.class_name}.{method_call.method_name}")
            self.logger.debug(f"   🆔 Call ID: {call_id}")
            self.logger.debug(f"   📥 Inputs: {json.dumps(method_call.inputs, indent=2)}")
            
            start_time = time.time()
            
            try:
                # Execute the method
                result = func(*args, **kwargs)
                
                # Calculate execution time
                execution_time = time.time() - start_time
                method_call.execution_time = execution_time
                method_call.status = ExecutionStatus.COMPLETED
                
                # Capture outputs (sanitize)
                if isinstance(result, (str, int, float, bool, list, dict)):
                    if isinstance(result, str) and len(result) > 1000:
                        method_call.outputs = f"{result[:1000]}... (truncated)"
                    else:
                        method_call.outputs = result
                else:
                    method_call.outputs = f"<{type(result).__name__}>"
                
                self.logger.debug(f"✅ METHOD CALL COMPLETED: {method_call.class_name}.{method_call.method_name}")
                self.logger.debug(f"   ⏱️ Execution Time: {execution_time:.3f}s")
                self.logger.debug(f"   📤 Output: {method_call.outputs}")
                
                return result
                
            except Exception as e:
                # Handle errors
                execution_time = time.time() - start_time
                method_call.execution_time = execution_time
                method_call.status = ExecutionStatus.FAILED
                method_call.error = str(e)
                method_call.stack_trace = traceback.format_exc()
                
                self.current_session.error_count += 1
                
                self.logger.error(f"❌ METHOD CALL FAILED: {method_call.class_name}.{method_call.method_name}")
                self.logger.error(f"   ⏱️ Execution Time: {execution_time:.3f}s")
                self.logger.error(f"   ❌ Error: {str(e)}")
                self.logger.error(f"   📋 Stack Trace: {traceback.format_exc()}")
                
                raise
            
            finally:
                # Remove from stack
                if self.method_call_stack and self.method_call_stack[-1].call_id == call_id:
                    self.method_call_stack.pop()
        
        return wrapper
    
    @trace_func
    def log_redis_message(self, message_type: str, from_agent: str, to_agent: str, 
                         content: Dict[str, Any], direction: str = "sent"):
        """
        Log Redis message flow.
        
        Args:
            message_type: Type of message
            from_agent: Sender agent
            to_agent: Receiver agent
            content: Message content
            direction: 'sent' or 'received'
        """
        message_log = {
            'message_id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'type': message_type,
            'from_agent': from_agent,
            'to_agent': to_agent,
            'direction': direction,
            'content': content,
            'session_id': self.current_session.session_id
        }
        
        self.current_session.redis_messages.append(message_log)
        
        direction_emoji = "📤" if direction == "sent" else "📥"
        self.logger.info(f"{direction_emoji} REDIS MESSAGE {direction.upper()}: {message_type}")
        self.logger.info(f"   🤖 From: {from_agent} → To: {to_agent}")
        self.logger.info(f"   📋 Content: {json.dumps(content, indent=2)}")
        
        # Update current operation if available
        if self.operation_stack:
            current_op = self.operation_stack[-1]
            if direction == "sent":
                current_op.messages_sent.append(message_log)
            else:
                current_op.messages_received.append(message_log)
    
    @trace_func
    def add_step_log(self, step_name: str, details: Dict[str, Any], level: LogLevel = LogLevel.INFO):
        """
        Add a step-by-step execution log.
        
        Args:
            step_name: Name of the step
            details: Step details
            level: Log level
        """
        step_log = {
            'step_id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'step_name': step_name,
            'details': details,
            'level': level.value,
            'session_id': self.current_session.session_id
        }
        
        # Add to current operation or session
        if self.operation_stack:
            if 'steps' not in self.operation_stack[-1].metadata:
                self.operation_stack[-1].metadata['steps'] = []
            self.operation_stack[-1].metadata['steps'].append(step_log)
        
        emoji = {"TRACE": "🔍", "DEBUG": "🐛", "INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "CRITICAL": "🚨"}
        step_emoji = emoji.get(level.value, "📋")
        
        self.logger.log(
            getattr(logging, level.value),
            f"{step_emoji} STEP: {step_name}"
        )
        self.logger.log(
            getattr(logging, level.value),
            f"   📋 Details: {json.dumps(details, indent=2)}"
        )
    
    @trace_func
    def end_session(self) -> Dict[str, Any]:
        """
        End the current execution session and generate summary.
        
        Returns:
            Dict[str, Any]: Session summary
        """
        self.current_session.end_time = datetime.now(timezone.utc).isoformat()
        self.current_session.total_duration = (
            datetime.now(timezone.utc) - 
            datetime.fromisoformat(self.current_session.start_time.replace('Z', '+00:00'))
        ).total_seconds()
        
        # Generate performance metrics
        self.current_session.performance_metrics = self._generate_performance_metrics()
        
        # Generate execution summary
        self.current_session.execution_summary = self._generate_execution_summary()
        
        # Mark as completed
        self.current_session.status = ExecutionStatus.COMPLETED
        
        # Save session to file
        self._save_session_to_file()
        
        # Print summary
        self._print_session_summary()
        
        return asdict(self.current_session)
    
    def _generate_performance_metrics(self) -> Dict[str, Any]:
        """Generate detailed performance metrics."""
        total_method_calls = len(self.current_session.method_calls)
        completed_calls = len([c for c in self.current_session.method_calls if c.status == ExecutionStatus.COMPLETED])
        failed_calls = len([c for c in self.current_session.method_calls if c.status == ExecutionStatus.FAILED])
        
        total_operations = len(self.current_session.agent_operations)
        completed_operations = len([o for o in self.current_session.agent_operations if o.status == ExecutionStatus.COMPLETED])
        
        avg_method_time = 0
        if self.current_session.method_calls:
            total_method_time = sum(c.execution_time for c in self.current_session.method_calls)
            avg_method_time = total_method_time / len(self.current_session.method_calls)
        
        return {
            'total_duration': self.current_session.total_duration,
            'total_method_calls': total_method_calls,
            'completed_method_calls': completed_calls,
            'failed_method_calls': failed_calls,
            'method_success_rate': (completed_calls / total_method_calls * 100) if total_method_calls > 0 else 0,
            'average_method_execution_time': avg_method_time,
            'total_agent_operations': total_operations,
            'completed_agent_operations': completed_operations,
            'operation_success_rate': (completed_operations / total_operations * 100) if total_operations > 0 else 0,
            'total_redis_messages': len(self.current_session.redis_messages),
            'error_count': self.current_session.error_count,
            'warning_count': self.current_session.warning_count
        }
    
    def _generate_execution_summary(self) -> Dict[str, Any]:
        """Generate execution summary."""
        agent_stats = {}
        for operation in self.current_session.agent_operations:
            agent_name = operation.agent_name
            if agent_name not in agent_stats:
                agent_stats[agent_name] = {
                    'total_operations': 0,
                    'completed_operations': 0,
                    'total_duration': 0,
                    'operation_types': set()
                }
            
            agent_stats[agent_name]['total_operations'] += 1
            if operation.status == ExecutionStatus.COMPLETED:
                agent_stats[agent_name]['completed_operations'] += 1
            agent_stats[agent_name]['total_duration'] += operation.duration
            agent_stats[agent_name]['operation_types'].add(operation.operation_type)
        
        # Convert sets to lists for JSON serialization
        for stats in agent_stats.values():
            stats['operation_types'] = list(stats['operation_types'])
        
        return {
            'session_name': self.current_session.session_name,
            'session_duration': self.current_session.total_duration,
            'agents_involved': list(agent_stats.keys()),
            'agent_statistics': agent_stats,
            'execution_flow': [
                {
                    'type': 'operation',
                    'timestamp': op.timestamp,
                    'agent': op.agent_name,
                    'operation': op.operation_type,
                    'status': op.status.value,
                    'duration': op.duration
                }
                for op in self.current_session.agent_operations
            ]
        }
    
    def _save_session_to_file(self):
        """Save complete session data to JSON file."""
        session_file = self.log_dir / f"{self.current_session.session_name}_complete.json"
        
        try:
            with open(session_file, 'w') as f:
                json.dump(asdict(self.current_session), f, indent=2, default=str)
            
            self.logger.info(f"💾 Session data saved to: {session_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save session data: {str(e)}")
    
    def _print_session_summary(self):
        """Print detailed session summary."""
        print(f"\n🎯 COMPREHENSIVE EXECUTION SESSION SUMMARY")
        print(f"=" * 80)
        print(f"📊 Session: {self.current_session.session_name}")
        print(f"🆔 Session ID: {self.current_session.session_id}")
        print(f"⏱️ Total Duration: {self.current_session.total_duration:.2f} seconds")
        print(f"📊 Status: {self.current_session.status.value}")
        
        metrics = self.current_session.performance_metrics
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   🔧 Method Calls: {metrics['total_method_calls']} (Success: {metrics['method_success_rate']:.1f}%)")
        print(f"   🤖 Agent Operations: {metrics['total_agent_operations']} (Success: {metrics['operation_success_rate']:.1f}%)")
        print(f"   📨 Redis Messages: {metrics['total_redis_messages']}")
        print(f"   ⚡ Avg Method Time: {metrics['average_method_execution_time']:.3f}s")
        print(f"   ❌ Errors: {metrics['error_count']}")
        print(f"   ⚠️ Warnings: {metrics['warning_count']}")
        
        summary = self.current_session.execution_summary
        print(f"\n🤖 AGENT ACTIVITY:")
        for agent_name, stats in summary['agent_statistics'].items():
            success_rate = (stats['completed_operations'] / stats['total_operations'] * 100) if stats['total_operations'] > 0 else 0
            print(f"   • {agent_name}: {stats['total_operations']} ops ({success_rate:.1f}% success, {stats['total_duration']:.2f}s)")
        
        print(f"\n📂 LOG FILES:")
        print(f"   📄 Session Log: {self.log_dir}/{self.current_session.session_name}.log")
        print(f"   📊 Complete Data: {self.log_dir}/{self.current_session.session_name}_complete.json")
        print(f"\n✅ COMPREHENSIVE EXECUTION LOGGING COMPLETED!")

# Global logger instance
_global_logger: Optional[ComprehensiveExecutionLogger] = None

@trace_func
def initialize_execution_logger(session_name: str = None, log_dir: str = "logs") -> ComprehensiveExecutionLogger:
    """
    Initialize the global execution logger.
    
    Args:
        session_name: Name for the execution session
        log_dir: Directory for log files
        
    Returns:
        ComprehensiveExecutionLogger: Initialized logger
    """
    global _global_logger
    _global_logger = ComprehensiveExecutionLogger(log_dir=log_dir, session_name=session_name)
    return _global_logger

@trace_func
def get_execution_logger() -> Optional[ComprehensiveExecutionLogger]:
    """Get the global execution logger."""
    return _global_logger

@trace_func
def log_method(func: Callable) -> Callable:
    """
    Decorator for logging method calls.
    
    Args:
        func: Function to wrap
        
    Returns:
        Callable: Wrapped function
    """
    if _global_logger:
        return _global_logger.log_method_call(func)
    else:
        # Return original function if no logger
        return func

@trace_func
def start_operation(agent_name: str, agent_type: str, operation_type: str, 
                   inputs: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> str:
    """
    Start tracking an agent operation.
    
    Args:
        agent_name: Name of the agent
        agent_type: Type of agent
        operation_type: Type of operation
        inputs: Operation inputs
        metadata: Additional metadata
        
    Returns:
        str: Operation ID
    """
    if _global_logger:
        return _global_logger.start_agent_operation(agent_name, agent_type, operation_type, inputs, metadata)
    return str(uuid.uuid4())

@trace_func
def end_operation(operation_id: str, outputs: Any = None, 
                 status: ExecutionStatus = ExecutionStatus.COMPLETED, error: str = None):
    """
    End tracking an agent operation.
    
    Args:
        operation_id: Operation ID to end
        outputs: Operation outputs
        status: Final status
        error: Error message if failed
    """
    if _global_logger:
        _global_logger.end_agent_operation(operation_id, outputs, status, error)

@trace_func
def log_step(step_name: str, details: Dict[str, Any], level: LogLevel = LogLevel.INFO):
    """
    Log an execution step.
    
    Args:
        step_name: Name of the step
        details: Step details
        level: Log level
    """
    if _global_logger:
        _global_logger.add_step_log(step_name, details, level)

@trace_func
def log_redis_message(message_type: str, from_agent: str, to_agent: str, 
                     content: Dict[str, Any], direction: str = "sent"):
    """
    Log a Redis message.
    
    Args:
        message_type: Type of message
        from_agent: Sender agent
        to_agent: Receiver agent
        content: Message content
        direction: 'sent' or 'received'
    """
    if _global_logger:
        _global_logger.log_redis_message(message_type, from_agent, to_agent, content, direction)

@trace_func
def finalize_execution_logging() -> Optional[Dict[str, Any]]:
    """
    Finalize execution logging and return summary.
    
    Returns:
        Optional[Dict[str, Any]]: Execution summary
    """
    if _global_logger:
        return _global_logger.end_session()
    return None

# Module initialization
print("🎯 Comprehensive Execution Logger module loaded successfully!")
print("   📊 Features: Method tracing, Agent operations, Redis messages, Performance metrics")
print("   🚀 Usage: initialize_execution_logger() to start comprehensive logging")
