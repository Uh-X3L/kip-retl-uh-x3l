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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'helpers'))

if __name__ == "__main__":
    main()
