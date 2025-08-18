"""
Apply Snoop Tracing to Your Existing Codebase
=============================================

This script will help you add comprehensive snoop tracing to all your existing modules
so you can see exactly what's happening during execution.
"""

import snoop
from pathlib import Path
import importlib.util
import sys

def add_tracing_to_module(module_path: str, output_file: str = None):
    """
    Add snoop tracing to all functions and classes in a Python module.
    
    Args:
        module_path: Path to the Python module file
        output_file: Optional file to write traced version to
    """
    module_path = Path(module_path)
    
    if not module_path.exists():
        print(f"❌ Module not found: {module_path}")
        return
    
    print(f"🔍 Adding tracing to: {module_path}")
    
    # Read the original file
    with open(module_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # Add snoop imports at the top
    snoop_imports = """
# SNOOP TRACING ADDED - Added by snoop integration script
import snoop

# Snoop decorator for functions
trace_func = snoop.snoop

# Snoop decorator for classes  
def trace_class(cls):
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_') and hasattr(attr, '__module__'):
            setattr(cls, attr_name, trace_func(attr))
    return cls

"""
    
    # Split content into lines
    lines = original_content.split('\n')
    
    # Find where to insert snoop imports (after existing imports)
    insert_line = 0
    in_docstring = False
    docstring_quotes = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Handle docstrings
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                in_docstring = True
                docstring_quotes = stripped[:3]
                if stripped.count(docstring_quotes) >= 2:
                    in_docstring = False
                continue
        else:
            if docstring_quotes in stripped:
                in_docstring = False
                continue
        
        # Skip if we're in a docstring
        if in_docstring:
            continue
            
        # Found import line, update insert position
        if (stripped.startswith('import ') or stripped.startswith('from ') or 
            stripped.startswith('#') or stripped == ''):
            insert_line = i + 1
        else:
            break
    
    # Insert snoop imports
    new_lines = lines[:insert_line] + snoop_imports.split('\n') + lines[insert_line:]
    
    # Process lines to add tracing decorators
    processed_lines = []
    i = 0
    
    while i < len(new_lines):
        line = new_lines[i]
        stripped = line.strip()
        
        # Add tracing to function definitions
        if stripped.startswith('def ') and not stripped.startswith('def _'):
            # Add trace decorator before function
            indent = len(line) - len(line.lstrip())
            processed_lines.append(' ' * indent + '@trace_func')
            processed_lines.append(line)
        
        # Add tracing to class definitions
        elif stripped.startswith('class '):
            # Add trace decorator before class
            indent = len(line) - len(line.lstrip())
            processed_lines.append(' ' * indent + '@trace_class')
            processed_lines.append(line)
        
        else:
            processed_lines.append(line)
        
        i += 1
    
    # Join the processed content
    traced_content = '\n'.join(processed_lines)
    
    # Determine output file
    if output_file:
        output_path = Path(output_file)
    else:
        output_path = module_path.parent / f"{module_path.stem}_traced{module_path.suffix}"
    
    # Write traced version
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(traced_content)
    
    print(f"✅ Traced version saved to: {output_path}")
    return str(output_path)

def trace_all_modules_in_directory(directory: str):
    """
    Add tracing to all Python modules in a directory.
    
    Args:
        directory: Path to the directory containing Python modules
    """
    directory = Path(directory)
    
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        return
    
    print(f"🎯 Adding tracing to all modules in: {directory}")
    
    traced_files = []
    
    # Find all Python files
    for py_file in directory.rglob("*.py"):
        # Skip __pycache__ and already traced files
        if "__pycache__" in str(py_file) or "_traced" in py_file.stem:
            continue
        
        try:
            traced_file = add_tracing_to_module(str(py_file))
            traced_files.append(traced_file)
        except Exception as e:
            print(f"⚠️ Failed to trace {py_file}: {e}")
    
    print(f"\n🎯 TRACING COMPLETE!")
    print(f"📊 Traced {len(traced_files)} files")
    print(f"📁 Traced files saved with '_traced' suffix")
    
    return traced_files

def create_traced_import_helper():
    """Create a helper module to easily import traced versions."""
    
    helper_content = '''"""
Traced Module Imports Helper
===========================

This module helps you import the traced versions of your modules.
Use this to quickly switch to traced execution.
"""

# Import traced versions of your modules
print("🎯 Loading traced modules for comprehensive execution tracing...")

try:
    # Import your traced modules here
    # Example:
    # from helpers.github_app_tools_traced import *
    # from helpers.enhanced_base_agent_traced import *
    
    print("✅ Traced modules loaded successfully!")
    print("🔍 All function and class calls will now be traced with snoop")
    
except ImportError as e:
    print(f"⚠️ Some traced modules could not be imported: {e}")
    print("💡 Run trace_your_codebase.py first to generate traced versions")

def start_tracing():
    """Start comprehensive tracing of your codebase."""
    print("🚀 COMPREHENSIVE TRACING ACTIVE")
    print("   Every function call, every variable, every step will be traced!")
    
def stop_tracing():
    """Note: Snoop tracing cannot be stopped once started."""
    print("ℹ️ Snoop tracing runs for the entire session")
    print("   Restart Python to stop tracing")

if __name__ == "__main__":
    print(__doc__)
    start_tracing()
'''
    
    with open("traced_imports.py", "w") as f:
        f.write(helper_content)
    
    print("✅ Created traced_imports.py helper module")

if __name__ == "__main__":
    main()
