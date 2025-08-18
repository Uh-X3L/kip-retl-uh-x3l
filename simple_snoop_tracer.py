"""
Simple Snoop Tracing for Your Codebase
======================================

This is a simplified version that works reliably with snoop for line-by-line tracing.
Use this to trace everything happening in your codebase.
"""

import snoop
import time
from datetime import datetime
from typing import Any, Dict, List

# Simple snoop configuration for console output
import sys

# Create snoop instance for tracing
console_snoop = snoop.snoop

class SimpleTracer:
    """Simple tracer using snoop for complete execution visibility."""
    
    def __init__(self, session_name: str = None):
        self.session_name = session_name or f"trace_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.traced_functions = []
        print(f"🎯 SIMPLE TRACER STARTED: {self.session_name}")
    
    def trace(self, func):
        """Decorator to trace any function with snoop."""
        traced_func = console_snoop(func)
        self.traced_functions.append(func.__name__)
        print(f"📋 Tracing enabled for: {func.__name__}")
        return traced_func
    
    def trace_class(self, cls):
        """Trace all methods in a class."""
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                setattr(cls, attr_name, self.trace(attr))
        print(f"🎯 Class {cls.__name__} fully traced")
        return cls

# Global tracer instance
tracer = SimpleTracer()

# Convenient decorators
def trace_this(func):
    """Simple decorator to trace any function."""
    return tracer.trace(func)

def trace_class(cls):
    """Simple decorator to trace all methods in a class."""
    return tracer.trace_class(cls)

# Example usage functions
@trace_this
def example_traced_function(x: int, y: int) -> int:
    """Example function that will be traced line by line."""
    print(f"Computing {x} + {y}")
    result = x + y
    intermediate = result * 2
    final_result = intermediate - 5
    print(f"Final result: {final_result}")
    return final_result

@trace_class
class ExampleTracedClass:
    """Example class with all methods traced."""
    
    def __init__(self, name: str):
        self.name = name
        self.data = []
    
    def add_data(self, value: Any) -> None:
        """Add data with tracing."""
        self.data.append(value)
        print(f"Added {value} to {self.name}")
    
    def process_data(self) -> Dict[str, Any]:
        """Process data with tracing."""
        total = sum(x for x in self.data if isinstance(x, (int, float)))
        count = len(self.data)
        average = total / count if count > 0 else 0
        
        result = {
            "total": total,
            "count": count,
            "average": average,
            "data": self.data.copy()
        }
        
        return result

def demo_simple_tracing():
    """Demonstrate the simple tracing system."""
    print("\n" + "="*60)
    print("🎯 SIMPLE SNOOP TRACING DEMONSTRATION")
    print("="*60)
    
    # Test traced function
    print("\n📋 Testing traced function:")
    result1 = example_traced_function(10, 20)
    print(f"Function result: {result1}")
    
    # Test traced class
    print("\n📋 Testing traced class:")
    obj = ExampleTracedClass("TestObject")
    obj.add_data(100)
    obj.add_data(200)
    obj.add_data("hello")
    obj.add_data(300)
    
    processing_result = obj.process_data()
    print(f"Processing result: {processing_result}")
    
    print("\n✅ Simple tracing demo completed!")
    print(f"📊 Traced functions: {tracer.traced_functions}")
    
if __name__ == "__main__":
    demo_simple_tracing()

print("🎯 Simple Snoop Tracer loaded!")
print("📋 Usage:")
print("   @trace_this - to trace any function")
print("   @trace_class - to trace all methods in a class")
print("   demo_simple_tracing() - to run a demonstration")
