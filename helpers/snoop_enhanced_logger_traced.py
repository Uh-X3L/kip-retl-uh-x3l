"""
Snoop-Enhanced Comprehensive Execution Logger
============================================

This module integrates the snoop library with your comprehensive execution logger
to provide detailed line-by-line execution tracing, method calls, inputs, outputs,
and complete execution flow visualization.

Features:
- Line-by-line execution tracing with snoop
- Method call hierarchy visualization
- Variable watching and change tracking
- Execution timing and performance metrics
- Visual call stack representation
- Real-time execution monitoring
- Detailed input/output capture
- Integration with existing logging system
"""

import snoop
import sys
import os
import time
import json
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from contextlib import contextmanager

# Import the comprehensive execution logger

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


try:
    from .comprehensive_execution_logger import (
        ComprehensiveExecutionLogger, initialize_execution_logger,
        log_method, start_operation, end_operation, log_step,
        LogLevel, ExecutionStatus, get_execution_logger
    )
    COMPREHENSIVE_LOGGING_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_LOGGING_AVAILABLE = False

@trace_class
class SnoopEnhancedLogger:
    """
    Enhanced logger that combines snoop tracing with comprehensive execution logging.
    """
    
    def __init__(self, session_name: str = None, log_dir: str = "logs", 
                 enable_snoop: bool = True, trace_all_modules: bool = False):
        """
        Initialize the snoop-enhanced logger.
        
        Args:
            session_name: Name for the execution session
            log_dir: Directory for log files
            enable_snoop: Enable snoop tracing
            trace_all_modules: Whether to trace all modules or just specific ones
        """
        self.session_name = session_name or f"snoop_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.enable_snoop = enable_snoop
        self.trace_all_modules = trace_all_modules
        
        # Initialize comprehensive logger if available
        self.comprehensive_logger = None
        if COMPREHENSIVE_LOGGING_AVAILABLE:
            self.comprehensive_logger = initialize_execution_logger(
                session_name=self.session_name,
                log_dir=str(self.log_dir)
            )
        
        # Snoop configuration
        self.snoop_output_file = self.log_dir / f"{self.session_name}_snoop_trace.log"
        self.snoop_config = None
        
        if self.enable_snoop:
            self._setup_snoop()
        
        # Execution tracking
        self.traced_functions = set()
        self.active_traces = {}
        
        print(f"🎯 SNOOP-ENHANCED COMPREHENSIVE LOGGER STARTED")
        print(f"   📊 Session: {self.session_name}")
        print(f"   📁 Log Directory: {self.log_dir}")
        print(f"   🔍 Snoop Enabled: {self.enable_snoop}")
        print(f"   📋 Snoop Output: {self.snoop_output_file}")
        if self.comprehensive_logger:
            print(f"   🎯 Comprehensive Logging: Enabled")
    
    def _setup_snoop(self):
        """Setup snoop configuration for detailed tracing."""
        try:
            # Create custom snoop config
            self.snoop_config = snoop.Config(
                # Output to file
                out=open(self.snoop_output_file, 'w', encoding='utf-8'),
                # Color for better readability
                color=True,
                # Show variable values
                depth=2,
                # Prefix for easier identification
                prefix='🔍 SNOOP: ',
                # Watch variables
                watch=(
                    snoop.utils.Watch('self', 'self.__class__.__name__') if hasattr(snoop.utils, 'Watch') else None
                ),
                # Include more context
                columns=('time', 'thread', 'file', 'line', 'function'),
                # Better formatting
                width=120
            )
            
            print(f"✅ Snoop configuration initialized")
            
        except Exception as e:
            print(f"⚠️ Snoop setup failed: {e}")
            self.enable_snoop = False
    
    @trace_func
    def trace_function(self, func: Callable) -> Callable:
        """
        Enhanced function decorator that combines snoop tracing with comprehensive logging.
        
        Args:
            func: Function to trace
            
        Returns:
            Callable: Wrapped function with enhanced tracing
        """
        if not self.enable_snoop or not self.snoop_config:
            # Fallback to basic logging if snoop not available
            if COMPREHENSIVE_LOGGING_AVAILABLE:
                return log_method(func)
            return func
        
        # Apply snoop tracing
        snooped_func = self.snoop_config(func)
        
        # Add to traced functions
        func_name = f"{func.__module__}.{func.__qualname__}"
        self.traced_functions.add(func_name)
        
        # Wrap with comprehensive logging if available
        if COMPREHENSIVE_LOGGING_AVAILABLE:
            return log_method(snooped_func)
        
        return snooped_func
    
    @trace_func
    def trace_class(self, cls):
        """
        Trace all methods in a class.
        
        Args:
            cls: Class to trace
            
        Returns:
            Class with traced methods
        """
        if not self.enable_snoop:
            return cls
        
        # Get all methods in the class
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                # Apply tracing to the method
                traced_method = self.trace_function(attr)
                setattr(cls, attr_name, traced_method)
        
        print(f"🎯 Class {cls.__name__} fully traced")
        return cls
    
    @trace_func
    def trace_module(self, module_name: str):
        """
        Trace all functions in a specific module.
        
        Args:
            module_name: Name of the module to trace
        """
        if not self.enable_snoop:
            return
        
        try:
            import importlib
            module = importlib.import_module(module_name)
            
            traced_count = 0
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and not attr_name.startswith('_'):
                    traced_func = self.trace_function(attr)
                    setattr(module, attr_name, traced_func)
                    traced_count += 1
            
            print(f"🎯 Module {module_name} traced ({traced_count} functions)")
            
        except Exception as e:
            print(f"⚠️ Failed to trace module {module_name}: {e}")
    
    @trace_func
    def enable_comprehensive_tracing(self):
        """
        Enable comprehensive tracing for your entire codebase.
        """
        if not self.enable_snoop:
            print("⚠️ Snoop not enabled, cannot start comprehensive tracing")
            return
        
        print("🚀 ENABLING COMPREHENSIVE CODEBASE TRACING")
        print("=" * 60)
        
        # Trace your specific modules
        modules_to_trace = [
            'helpers.enhanced_base_agent',
            'helpers.comprehensive_execution_logger',
            'helpers.optimized_redis_messaging',
            'helpers.backend_supervisor_role_tools',
            'helpers.github_app_tools',
            'helpers.agents.base_agent',
            'helpers.agents.worker_agent',
            'helpers.agents.testing_agent',
            'helpers.agents.devops_agent',
            'helpers.agents.documentation_agent'
        ]
        
        traced_modules = 0
        for module_name in modules_to_trace:
            try:
                self.trace_module(module_name)
                traced_modules += 1
            except:
                print(f"⚠️ Could not trace module: {module_name}")
        
        print(f"✅ Comprehensive tracing enabled for {traced_modules} modules")
        
        # Also enable system-wide tracing if requested
        if self.trace_all_modules:
            self._enable_system_wide_tracing()
    
    def _enable_system_wide_tracing(self):
        """Enable system-wide Python tracing (use with caution)."""
        print("🌐 Enabling system-wide tracing (this may be verbose!)")
        
        @trace_func
        def trace_calls(frame, event, arg):
            if event == 'call':
                filename = frame.f_code.co_filename
                # Only trace files in your project directory
                if 'kip-retl-uh-x3l' in filename:
                    func_name = frame.f_code.co_name
                    line_no = frame.f_lineno
                    print(f"🔍 CALL: {filename}:{line_no} -> {func_name}()")
            return trace_calls
        
        sys.settrace(trace_calls)
    
    @contextmanager
    @trace_func
    def trace_execution(self, operation_name: str):
        """
        Context manager for tracing a specific execution block.
        
        Args:
            operation_name: Name of the operation being traced
        """
        operation_id = None
        
        if self.comprehensive_logger:
            operation_id = start_operation(
                agent_name="TRACER",
                agent_type="execution_tracer",
                operation_type=operation_name,
                inputs={"trace_enabled": self.enable_snoop}
            )
        
        start_time = time.time()
        
        try:
            if self.enable_snoop:
                print(f"🎯 STARTING TRACED EXECUTION: {operation_name}")
                print(f"   📋 Snoop Output: {self.snoop_output_file}")
            
            yield
            
            execution_time = time.time() - start_time
            
            if self.comprehensive_logger:
                log_step(f"Traced Execution Completed: {operation_name}", {
                    "execution_time": execution_time,
                    "traced_functions": len(self.traced_functions)
                }, LogLevel.INFO)
                
                end_operation(
                    operation_id=operation_id,
                    outputs={
                        "execution_time": execution_time,
                        "success": True
                    },
                    status=ExecutionStatus.COMPLETED
                )
            
            print(f"✅ TRACED EXECUTION COMPLETED: {operation_name} ({execution_time:.3f}s)")
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            if self.comprehensive_logger:
                end_operation(
                    operation_id=operation_id,
                    outputs={"execution_time": execution_time},
                    status=ExecutionStatus.FAILED,
                    error=str(e)
                )
            
            print(f"❌ TRACED EXECUTION FAILED: {operation_name} ({execution_time:.3f}s)")
            print(f"   Error: {e}")
            raise
    
    @trace_func
    def get_trace_summary(self) -> Dict[str, Any]:
        """Get a summary of all tracing activity."""
        summary = {
            "session_name": self.session_name,
            "snoop_enabled": self.enable_snoop,
            "traced_functions_count": len(self.traced_functions),
            "traced_functions": list(self.traced_functions),
            "snoop_output_file": str(self.snoop_output_file),
            "log_directory": str(self.log_dir)
        }
        
        if self.comprehensive_logger:
            comprehensive_summary = self.comprehensive_logger.current_session.execution_summary
            summary.update({
                "comprehensive_logging": True,
                "execution_summary": comprehensive_summary
            })
        
        return summary
    
    @trace_func
    def view_snoop_output(self, lines: int = 50):
        """
        View the most recent snoop output.
        
        Args:
            lines: Number of lines to show from the end
        """
        if not self.snoop_output_file.exists():
            print("📋 No snoop output file found yet")
            return
        
        try:
            with open(self.snoop_output_file, 'r', encoding='utf-8') as f:
                content = f.readlines()
            
            print(f"📋 SNOOP OUTPUT (last {lines} lines):")
            print("=" * 60)
            
            for line in content[-lines:]:
                print(line.rstrip())
                
        except Exception as e:
            print(f"⚠️ Error reading snoop output: {e}")
    
    @trace_func
    def finalize_tracing(self) -> Dict[str, Any]:
        """
        Finalize tracing and return complete summary.
        
        Returns:
            Dict[str, Any]: Complete tracing summary
        """
        print(f"\n🎯 FINALIZING SNOOP-ENHANCED TRACING")
        print("=" * 60)
        
        # Close snoop output file
        if self.snoop_config and hasattr(self.snoop_config, 'out'):
            try:
                self.snoop_config.out.close()
            except:
                pass
        
        # Finalize comprehensive logging
        comprehensive_summary = None
        if self.comprehensive_logger:
            comprehensive_summary = self.comprehensive_logger.end_session()
        
        # Generate final summary
        final_summary = self.get_trace_summary()
        if comprehensive_summary:
            final_summary['comprehensive_summary'] = comprehensive_summary
        
        # Save summary to file
        summary_file = self.log_dir / f"{self.session_name}_final_summary.json"
        try:
            with open(summary_file, 'w') as f:
                json.dump(final_summary, f, indent=2, default=str)
            print(f"💾 Final summary saved to: {summary_file}")
        except Exception as e:
            print(f"⚠️ Could not save summary: {e}")
        
        print(f"📊 TRACING SUMMARY:")
        print(f"   🔍 Traced Functions: {len(self.traced_functions)}")
        print(f"   📄 Snoop Output: {self.snoop_output_file}")
        print(f"   📊 Summary File: {summary_file}")
        
        if comprehensive_summary:
            metrics = comprehensive_summary.get('performance_metrics', {})
            print(f"   🎯 Total Operations: {metrics.get('total_agent_operations', 0)}")
            print(f"   ⏱️ Total Duration: {metrics.get('total_duration', 0):.2f}s")
        
        print(f"\n✅ SNOOP-ENHANCED TRACING COMPLETED!")
        
        return final_summary

# Global snoop-enhanced logger
_global_snoop_logger: Optional[SnoopEnhancedLogger] = None

@trace_func
def initialize_snoop_tracing(session_name: str = None, log_dir: str = "logs",
                           enable_comprehensive: bool = True, trace_all_modules: bool = False) -> SnoopEnhancedLogger:
    """
    Initialize global snoop-enhanced tracing.
    
    Args:
        session_name: Name for the session
        log_dir: Directory for logs
        enable_comprehensive: Enable comprehensive logging
        trace_all_modules: Trace all Python modules (warning: very verbose)
        
    Returns:
        SnoopEnhancedLogger: Initialized logger
    """
    global _global_snoop_logger
    _global_snoop_logger = SnoopEnhancedLogger(
        session_name=session_name,
        log_dir=log_dir,
        enable_snoop=True,
        trace_all_modules=trace_all_modules
    )
    return _global_snoop_logger

@trace_func
def get_snoop_logger() -> Optional[SnoopEnhancedLogger]:
    """Get the global snoop logger."""
    return _global_snoop_logger

@trace_func
def snoop_trace(func: Callable) -> Callable:
    """
    Decorator for snoop tracing functions.
    
    Args:
        func: Function to trace
        
    Returns:
        Callable: Traced function
    """
    if _global_snoop_logger:
        return _global_snoop_logger.trace_function(func)
    else:
        # Fallback to basic snoop if no global logger
        return snoop.snoop(func)

@trace_func
def snoop_trace_class(cls):
    """
    Decorator for tracing all methods in a class.
    
    Args:
        cls: Class to trace
        
    Returns:
        Class with traced methods
    """
    if _global_snoop_logger:
        return _global_snoop_logger.trace_class(cls)
    else:
        # Fallback to basic snoop
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                setattr(cls, attr_name, snoop.snoop(attr))
        return cls

@trace_func
def start_comprehensive_tracing():
    """Start comprehensive tracing of the entire codebase."""
    if _global_snoop_logger:
        _global_snoop_logger.enable_comprehensive_tracing()
    else:
        print("⚠️ No snoop logger initialized. Call initialize_snoop_tracing() first.")

@trace_func
def finalize_snoop_tracing() -> Optional[Dict[str, Any]]:
    """Finalize snoop tracing and return summary."""
    if _global_snoop_logger:
        return _global_snoop_logger.finalize_tracing()
    return None

@trace_func
def view_trace_output(lines: int = 50):
    """View recent trace output."""
    if _global_snoop_logger:
        _global_snoop_logger.view_snoop_output(lines)
    else:
        print("⚠️ No snoop logger initialized.")

# Module initialization
print("🎯 Snoop-Enhanced Comprehensive Logger loaded successfully!")
print("   🔍 Features: Line-by-line tracing, Method tracking, Variable watching")
print("   🚀 Usage: initialize_snoop_tracing() to start comprehensive code tracing")
