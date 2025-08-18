"""
Dynamic Tracing Controller
=========================

A sophisticated tracing system that enables/disables execution tracing
at runtime without code duplication.
"""

import os
import json
import functools
import threading
from typing import Dict, Any, List, Optional, Set, Callable
from pathlib import Path
import logging

# Import snoop for tracing
try:
    import snoop
    SNOOP_AVAILABLE = True
except ImportError:
    SNOOP_AVAILABLE = False

logger = logging.getLogger(__name__)


class TracingController:
    """
    Global tracing controller that manages execution tracing across the entire codebase
    without requiring duplicate files.
    """
    
    def __init__(self, config_file: str = "tracing_config.json"):
        """Initialize the tracing controller."""
        self.config_file = config_file
        self.global_enabled = False
        self.module_settings = {}
        self.method_settings = {}
        self.class_settings = {}
        self.excluded_modules = set()
        self.excluded_methods = set()
        self._lock = threading.RLock()
        self._traced_functions = {}
        
        # Load configuration
        self.load_configuration()
        
        # Snoop configuration
        if SNOOP_AVAILABLE:
            try:
                # Try different column configurations and get the snoop decorator
                try:
                    config = snoop.Config(
                        prefix="🔍 ",
                        columns=['time', 'file', 'function', 'line']
                    )
                    self.snoop_config = config.snoop
                except Exception:
                    try:
                        config = snoop.Config(
                            prefix="🔍 ",
                            columns=['time', 'line']
                        )
                        self.snoop_config = config.snoop
                    except Exception:
                        # Fallback to basic configuration
                        config = snoop.Config(prefix="🔍 ")
                        self.snoop_config = config.snoop
            except Exception as e:
                logger.warning(f"Snoop config failed, using basic snoop: {e}")
                self.snoop_config = snoop.snoop
        else:
            self.snoop_config = None
        
        logger.info(f"✅ Dynamic Tracing Controller initialized")
    
    def load_configuration(self):
        """Load tracing configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                self.global_enabled = config.get('global_enabled', False)
                self.module_settings = config.get('modules', {})
                self.method_settings = config.get('methods', {})
                self.class_settings = config.get('classes', {})
                self.excluded_modules = set(config.get('excluded_modules', []))
                self.excluded_methods = set(config.get('excluded_methods', []))
                
                logger.info(f"📋 Loaded tracing configuration from {self.config_file}")
            else:
                logger.info(f"💡 No configuration file found, using defaults")
                self.create_default_configuration()
        except Exception as e:
            logger.error(f"❌ Error loading tracing configuration: {e}")
            self.create_default_configuration()
    
    def save_configuration(self):
        """Save current configuration to file."""
        try:
            config = {
                'global_enabled': self.global_enabled,
                'modules': self.module_settings,
                'methods': self.method_settings,
                'classes': self.class_settings,
                'excluded_modules': list(self.excluded_modules),
                'excluded_methods': list(self.excluded_methods)
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"💾 Saved tracing configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"❌ Error saving configuration: {e}")
    
    def create_default_configuration(self):
        """Create default tracing configuration."""
        self.global_enabled = False
        self.module_settings = {
            "agent_communication_mixin": {
                "enabled": True,
                "methods": ["send_message", "receive_message", "report_task_progress"]
            },
            "simple_messaging": {
                "enabled": True,
                "methods": ["send_message", "get_messages", "create_task_message"]
            },
            "backend_supervisor_role_tools": {
                "enabled": False,
                "methods": ["create_detailed_issue", "research_topic"]
            }
        }
        self.method_settings = {}
        self.class_settings = {}
        self.excluded_modules = {"__pycache__", "test_*", "*_test"}
        self.excluded_methods = {"__init__", "__repr__", "__str__"}
    
    def enable_global_tracing(self):
        """Enable tracing globally."""
        with self._lock:
            self.global_enabled = True
            logger.info("🌐 Global tracing ENABLED")
            self.save_configuration()
    
    def disable_global_tracing(self):
        """Disable tracing globally."""
        with self._lock:
            self.global_enabled = False
            logger.info("🌐 Global tracing DISABLED")
            self.save_configuration()
    
    def enable_module_tracing(self, module_name: str, methods: List[str] = None):
        """Enable tracing for a specific module."""
        with self._lock:
            if module_name not in self.module_settings:
                self.module_settings[module_name] = {}
            
            self.module_settings[module_name]['enabled'] = True
            if methods:
                self.module_settings[module_name]['methods'] = methods
            
            logger.info(f"📦 Module tracing ENABLED: {module_name}")
            self.save_configuration()
    
    def disable_module_tracing(self, module_name: str):
        """Disable tracing for a specific module."""
        with self._lock:
            if module_name in self.module_settings:
                self.module_settings[module_name]['enabled'] = False
            
            logger.info(f"📦 Module tracing DISABLED: {module_name}")
            self.save_configuration()
    
    def enable_method_tracing(self, module_name: str, method_name: str):
        """Enable tracing for a specific method."""
        with self._lock:
            key = f"{module_name}.{method_name}"
            self.method_settings[key] = True
            
            logger.info(f"🔧 Method tracing ENABLED: {key}")
            self.save_configuration()
    
    def disable_method_tracing(self, module_name: str, method_name: str):
        """Disable tracing for a specific method."""
        with self._lock:
            key = f"{module_name}.{method_name}"
            self.method_settings[key] = False
            
            logger.info(f"🔧 Method tracing DISABLED: {key}")
            self.save_configuration()
    
    def should_trace(self, module_name: str, method_name: str = None, class_name: str = None) -> bool:
        """
        Determine if tracing should be enabled for the given context.
        
        Priority order:
        1. Specific method setting
        2. Module method list
        3. Module enabled setting
        4. Global enabled setting
        """
        with self._lock:
            # Check exclusions first
            if module_name in self.excluded_modules:
                return False
            
            if method_name and method_name in self.excluded_methods:
                return False
            
            # Check specific method setting
            if method_name:
                method_key = f"{module_name}.{method_name}"
                if method_key in self.method_settings:
                    return self.method_settings[method_key]
            
            # Check module settings
            if module_name in self.module_settings:
                module_config = self.module_settings[module_name]
                
                if not module_config.get('enabled', False):
                    return False
                
                # Check method list if specified
                if method_name and 'methods' in module_config:
                    methods = module_config['methods']
                    if methods != ["*"] and method_name not in methods:
                        return False
                
                return True
            
            # Fall back to global setting
            return self.global_enabled
    
    def get_tracing_status(self) -> Dict[str, Any]:
        """Get current tracing status."""
        with self._lock:
            return {
                'global_enabled': self.global_enabled,
                'modules_count': len(self.module_settings),
                'enabled_modules': [
                    name for name, config in self.module_settings.items() 
                    if config.get('enabled', False)
                ],
                'method_overrides': len(self.method_settings),
                'excluded_modules': list(self.excluded_modules),
                'snoop_available': SNOOP_AVAILABLE
            }
    
    def get_traced_function(self, func: Callable, module_name: str) -> Callable:
        """Get traced version of function, caching for performance."""
        func_key = f"{module_name}.{func.__name__}"
        
        if func_key not in self._traced_functions:
            if SNOOP_AVAILABLE and self.snoop_config:
                self._traced_functions[func_key] = self.snoop_config(func)
            else:
                self._traced_functions[func_key] = func
        
        return self._traced_functions[func_key]


# Global instance
TRACING_CONTROLLER = TracingController()


def conditional_trace(module_name: str = None, auto_module: bool = True):
    """
    Decorator that conditionally applies snoop tracing based on configuration.
    
    Args:
        module_name: Name of the module (auto-detected if None)
        auto_module: Whether to auto-detect module name from function
    """
    def decorator(func: Callable) -> Callable:
        # Auto-detect module name if not provided
        detected_module = module_name
        if auto_module and not detected_module:
            detected_module = func.__module__.split('.')[-1] if hasattr(func, '__module__') else 'unknown'
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if TRACING_CONTROLLER.should_trace(detected_module, func.__name__):
                if SNOOP_AVAILABLE:
                    traced_func = TRACING_CONTROLLER.get_traced_function(func, detected_module)
                    return traced_func(*args, **kwargs)
                else:
                    # Fallback logging when snoop not available
                    logger.info(f"🔍 Tracing: {detected_module}.{func.__name__} called")
                    result = func(*args, **kwargs)
                    logger.info(f"🔍 Tracing: {detected_module}.{func.__name__} completed")
                    return result
            else:
                return func(*args, **kwargs)
        
        # Store metadata for introspection
        wrapper._traced = True
        wrapper._module_name = detected_module
        wrapper._original_func = func
        
        return wrapper
    return decorator


def trace_class(module_name: str = None, methods: List[str] = None):
    """
    Class decorator that applies conditional tracing to all methods.
    
    Args:
        module_name: Name of the module
        methods: List of method names to trace (None = all public methods)
    """
    def class_decorator(cls):
        detected_module = module_name or cls.__module__.split('.')[-1]
        
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            
            # Only trace specified methods or all public methods
            if callable(attr) and not attr_name.startswith('_'):
                if methods is None or attr_name in methods:
                    traced_method = conditional_trace(detected_module)(attr)
                    setattr(cls, attr_name, traced_method)
        
        return cls
    return class_decorator


# Convenience functions
def enable_agent_communication_tracing():
    """Enable tracing for all agent communication modules."""
    modules = [
        "agent_communication_mixin",
        "simple_messaging", 
        "optimized_redis_messaging",
        "backend_supervisor_role_tools"
    ]
    
    for module in modules:
        TRACING_CONTROLLER.enable_module_tracing(module)
    
    logger.info("🚀 Agent communication tracing ENABLED")


def disable_all_tracing():
    """Disable all tracing."""
    TRACING_CONTROLLER.disable_global_tracing()
    for module in TRACING_CONTROLLER.module_settings:
        TRACING_CONTROLLER.disable_module_tracing(module)
    
    logger.info("🛑 All tracing DISABLED")


def enable_debug_mode():
    """Enable comprehensive tracing for debugging."""
    TRACING_CONTROLLER.enable_global_tracing()
    logger.info("🐛 Debug mode ENABLED - all functions will be traced")


def get_tracing_summary() -> str:
    """Get a formatted summary of current tracing status."""
    status = TRACING_CONTROLLER.get_tracing_status()
    
    summary = f"""
🔍 Dynamic Tracing Status:
{'='*50}
Global Enabled: {'✅ Yes' if status['global_enabled'] else '❌ No'}
Snoop Available: {'✅ Yes' if status['snoop_available'] else '❌ No'}
Modules Configured: {status['modules_count']}
Enabled Modules: {', '.join(status['enabled_modules']) if status['enabled_modules'] else 'None'}
Method Overrides: {status['method_overrides']}
Excluded Modules: {', '.join(status['excluded_modules']) if status['excluded_modules'] else 'None'}
"""
    return summary


# Quick setup functions
def quick_setup_for_debugging():
    """Quick setup for debugging agent communication."""
    enable_agent_communication_tracing()
    TRACING_CONTROLLER.enable_module_tracing("github_app_tools", ["create_issue", "open_pr"])
    logger.info("🚀 Quick debugging setup complete!")


def quick_setup_for_production():
    """Quick setup for production (minimal tracing)."""
    disable_all_tracing()
    # Only enable critical error reporting
    TRACING_CONTROLLER.enable_method_tracing("agent_communication_mixin", "report_task_error")
    TRACING_CONTROLLER.enable_method_tracing("simple_messaging", "send_error_report")
    logger.info("🏭 Production setup complete!")
