#!/usr/bin/env python3
"""
Simple Agent System Demo
========================

Demonstrates the simplified integration between:
- BackendSupervisorAgent for strategic planning
- Specialized agents from agents/ folder
- Simple messaging for coordination

This shows how the complex agent communication system has been simplified
to focus on essential coordination functionality.
"""

import sys
import os
import time

# Add helpers to path

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


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))

@trace_func
if __name__ == "__main__":
    main()
