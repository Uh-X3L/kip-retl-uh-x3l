"""
Integrated Execution Visualization using Existing Libraries
===========================================================

This module integrates the best existing Python libraries for execution tracing
and visualization, eliminating the need to reinvent the wheel while providing
comprehensive method tracking, inputs/outputs, and visual workflow rendering.

Libraries used:
- snoop: Detailed method execution tracing
- viztracer: Visual timeline and call hierarchy
- icecream: Quick debugging and variable inspection
- loguru: Beautiful structured logging

Features:
- Zero-config execution tracing
- Visual timeline in browser
- Method call hierarchy
- Input/output capture
- Performance metrics
- Interactive exploration
"""

import functools
import time
import json
from typing import Dict, Any, Callable, Optional
from pathlib import Path

# Import existing libraries with fallbacks

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
    import snoop
    from snoop import pp
    SNOOP_AVAILABLE = True
except ImportError:
    SNOOP_AVAILABLE = False
    @trace_func
    def snoop(func):
        return func
    @trace_func
    def pp(obj):
        return str(obj)

try:
    from viztracer import VizTracer
    VIZTRACER_AVAILABLE = True
except ImportError:
    VIZTRACER_AVAILABLE = False
    @trace_class
    class VizTracer:
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

try:
    from icecream import ic
    ICECREAM_AVAILABLE = True
    ic.configureOutput(prefix='🔍 DEBUG: ')
except ImportError:
    ICECREAM_AVAILABLE = False
    @trace_func
    def ic(*args):
        print("DEBUG:", *args)

try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    import logging
    logger = logging.getLogger(__name__)

@trace_class
class ExecutionVisualizer:
    """
    Comprehensive execution visualizer using existing libraries.
    """
    
    def __init__(self, output_dir: str = "execution_traces", session_name: str = None):
        """
        Initialize the execution visualizer.
        
        Args:
            output_dir: Directory for output files
            session_name: Name for this execution session
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.session_name = session_name or f"execution_{int(time.time())}"
        self.tracer = None
        self.active = False
        
        # Configure snoop if available
        if SNOOP_AVAILABLE:
            self.snoop_config = snoop.Config(
                output=self.output_dir / f"{self.session_name}_detailed.log",
                color=True,
                prefix="🔧 ",
                columns="time,thread,file,function,line",
            )
        
        # Configure loguru if available
        if LOGURU_AVAILABLE:
            logger.add(
                self.output_dir / f"{self.session_name}_structured.log",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
                level="DEBUG",
                rotation="10 MB"
            )
        
        print(f"🎯 EXECUTION VISUALIZER INITIALIZED")
        print(f"   📊 Session: {self.session_name}")
        print(f"   📁 Output: {self.output_dir}")
        print(f"   🔧 Snoop: {'✅' if SNOOP_AVAILABLE else '❌'}")
        print(f"   📈 VizTracer: {'✅' if VIZTRACER_AVAILABLE else '❌'}")
        print(f"   🧊 IceCream: {'✅' if ICECREAM_AVAILABLE else '❌'}")
        print(f"   📝 Loguru: {'✅' if LOGURU_AVAILABLE else '❌'}")
    
    @trace_func
    def start_session(self, include_timeline: bool = True):
        """
        Start a comprehensive tracing session.
        
        Args:
            include_timeline: Whether to include visual timeline tracing
        """
        if self.active:
            return
        
        if include_timeline and VIZTRACER_AVAILABLE:
            self.tracer = VizTracer(
                output_file=str(self.output_dir / f"{self.session_name}_timeline.html"),
                tracer_entries=1000000,
                verbose=0,
                max_stack_depth=50
            )
            self.tracer.__enter__()
        
        self.active = True
        
        if LOGURU_AVAILABLE:
            logger.info("🚀 Execution session started", session=self.session_name)
        
        print(f"🚀 EXECUTION TRACING STARTED")
        print(f"   📊 Session: {self.session_name}")
        if self.tracer:
            print(f"   📈 Timeline will be saved to: {self.session_name}_timeline.html")
    
    @trace_func
    def end_session(self):
        """End the tracing session and generate reports."""
        if not self.active:
            return
        
        if self.tracer:
            self.tracer.__exit__(None, None, None)
        
        self.active = False
        
        if LOGURU_AVAILABLE:
            logger.info("🏁 Execution session ended", session=self.session_name)
        
        # Generate summary report
        self._generate_summary_report()
        
        print(f"🏁 EXECUTION TRACING COMPLETED")
        print(f"   📊 Session: {self.session_name}")
        print(f"   📁 Files generated:")
        if VIZTRACER_AVAILABLE:
            print(f"      📈 Timeline: {self.session_name}_timeline.html")
        if SNOOP_AVAILABLE:
            print(f"      🔧 Detailed log: {self.session_name}_detailed.log")
        if LOGURU_AVAILABLE:
            print(f"      📝 Structured log: {self.session_name}_structured.log")
        print(f"      📋 Summary: {self.session_name}_summary.json")
    
    @trace_func
    def trace_method(self, include_args: bool = True, include_return: bool = True):
        """
        Decorator for comprehensive method tracing.
        
        Args:
            include_args: Whether to log method arguments
            include_return: Whether to log return values
        """
        @trace_func
        def decorator(func: Callable) -> Callable:
            # Apply snoop decorator if available
            if SNOOP_AVAILABLE:
                func = self.snoop_config(func)
            
            @functools.wraps(func)
            @trace_func
            def wrapper(*args, **kwargs):
                method_name = f"{func.__module__}.{func.__qualname__}"
                
                # Log method entry
                if LOGURU_AVAILABLE:
                    entry_data = {
                        "event": "method_entry",
                        "method": method_name,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs)
                    }
                    
                    if include_args:
                        # Sanitize arguments for logging
                        safe_args = []
                        for i, arg in enumerate(args):
                            if i == 0 and hasattr(arg, '__class__'):  # self parameter
                                safe_args.append(f"<{arg.__class__.__name__}>")
                            elif isinstance(arg, (str, int, float, bool)):
                                safe_args.append(arg)
                            else:
                                safe_args.append(f"<{type(arg).__name__}>")
                        
                        safe_kwargs = {}
                        for k, v in kwargs.items():
                            if isinstance(v, (str, int, float, bool)):
                                safe_kwargs[k] = v
                            else:
                                safe_kwargs[k] = f"<{type(v).__name__}>"
                        
                        entry_data["args"] = safe_args
                        entry_data["kwargs"] = safe_kwargs
                    
                    logger.debug("🔧 Method called", **entry_data)
                
                # Debug with icecream
                if ICECREAM_AVAILABLE and include_args:
                    ic(f"Calling {method_name}", args[:3], kwargs)
                
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Log successful completion
                    if LOGURU_AVAILABLE:
                        completion_data = {
                            "event": "method_success",
                            "method": method_name,
                            "execution_time": execution_time
                        }
                        
                        if include_return:
                            if isinstance(result, (str, int, float, bool, list, dict)):
                                if isinstance(result, str) and len(result) > 200:
                                    completion_data["return_value"] = result[:200] + "..."
                                else:
                                    completion_data["return_value"] = result
                            else:
                                completion_data["return_type"] = type(result).__name__
                        
                        logger.debug("✅ Method completed", **completion_data)
                    
                    if ICECREAM_AVAILABLE:
                        ic(f"Completed {method_name}", f"{execution_time:.3f}s")
                    
                    return result
                
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    # Log error
                    if LOGURU_AVAILABLE:
                        logger.error("❌ Method failed", 
                                   method=method_name,
                                   execution_time=execution_time,
                                   error=str(e),
                                   error_type=type(e).__name__)
                    
                    if ICECREAM_AVAILABLE:
                        ic(f"Failed {method_name}", str(e))
                    
                    raise
            
            return wrapper
        return decorator
    
    @trace_func
    def log_step(self, step_name: str, details: Dict[str, Any] = None):
        """
        Log an execution step with details.
        
        Args:
            step_name: Name of the step
            details: Additional details about the step
        """
        if LOGURU_AVAILABLE:
            logger.info("📋 Step executed", step=step_name, details=details or {})
        
        if ICECREAM_AVAILABLE:
            ic(f"Step: {step_name}", details)
        
        print(f"📋 STEP: {step_name}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    @trace_func
    def debug_variable(self, **variables):
        """
        Debug variables with automatic name detection.
        
        Args:
            **variables: Variables to debug
        """
        if ICECREAM_AVAILABLE:
            for name, value in variables.items():
                ic(f"{name} = {value}")
        
        if LOGURU_AVAILABLE:
            logger.debug("🔍 Variables", **variables)
    
    def _generate_summary_report(self):
        """Generate a summary report of the execution session."""
        summary = {
            "session_name": self.session_name,
            "timestamp": time.time(),
            "output_directory": str(self.output_dir),
            "libraries_used": {
                "snoop": SNOOP_AVAILABLE,
                "viztracer": VIZTRACER_AVAILABLE,
                "icecream": ICECREAM_AVAILABLE,
                "loguru": LOGURU_AVAILABLE
            },
            "files_generated": []
        }
        
        # Check which files were generated
        for file_path in self.output_dir.glob(f"{self.session_name}*"):
            summary["files_generated"].append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "type": file_path.suffix
            })
        
        # Save summary
        summary_file = self.output_dir / f"{self.session_name}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

# Global visualizer instance
_global_visualizer: Optional[ExecutionVisualizer] = None

@trace_func
def initialize_visualizer(output_dir: str = "execution_traces", 
                         session_name: str = None) -> ExecutionVisualizer:
    """
    Initialize the global execution visualizer.
    
    Args:
        output_dir: Directory for output files
        session_name: Name for this execution session
        
    Returns:
        ExecutionVisualizer: Initialized visualizer
    """
    global _global_visualizer
    _global_visualizer = ExecutionVisualizer(output_dir, session_name)
    return _global_visualizer

@trace_func
def start_tracing(include_timeline: bool = True):
    """Start execution tracing."""
    if _global_visualizer:
        _global_visualizer.start_session(include_timeline)

@trace_func
def end_tracing():
    """End execution tracing."""
    if _global_visualizer:
        _global_visualizer.end_session()

@trace_func
def trace_execution(include_args: bool = True, include_return: bool = True):
    """
    Decorator for method execution tracing.
    
    Args:
        include_args: Whether to log method arguments
        include_return: Whether to log return values
    """
    @trace_func
    def decorator(func: Callable) -> Callable:
        if _global_visualizer:
            return _global_visualizer.trace_method(include_args, include_return)(func)
        return func
    return decorator

@trace_func
def log_step(step_name: str, **details):
    """Log an execution step."""
    if _global_visualizer:
        _global_visualizer.log_step(step_name, details)

@trace_func
def debug_vars(**variables):
    """Debug variables with automatic name detection."""
    if _global_visualizer:
        _global_visualizer.debug_variable(**variables)

# Installation helper
@trace_func
def install_required_libraries():
    """Helper to install all required libraries."""
    libraries = ["snoop", "viztracer", "icecream", "loguru"]
    
    print("📦 INSTALLATION COMMANDS:")
    print(f"pip install {' '.join(libraries)}")
    print("\n🎯 USAGE EXAMPLE:")
    print("""
from execution_visualizer import initialize_visualizer, start_tracing, trace_execution, log_step, end_tracing

# Initialize
visualizer = initialize_visualizer(session_name="my_session")
start_tracing(include_timeline=True)

# Decorate your methods
@trace_execution(include_args=True, include_return=True)
@trace_func
def my_method(param1, param2):
    log_step("Processing started", param1=param1, param2=param2)
    result = param1 + param2
    log_step("Processing completed", result=result)
    return result

# Your code here
my_method(10, 20)

# End tracing
end_tracing()

# Check output files in execution_traces/ directory
""")

if __name__ == "__main__":
    install_required_libraries()

# Module initialization
print("🎯 Execution Visualizer with Existing Libraries loaded!")
print("   📊 Uses: snoop, viztracer, icecream, loguru")
print("   🚀 Call install_required_libraries() to see installation commands")
