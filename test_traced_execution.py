"""
Test Traced Module Execution
============================

This demonstrates how to run your traced modules to see complete execution tracing.
"""

# Import the traced version of your GitHub app tools
print("🎯 Importing traced GitHub app tools...")

try:
    # Import a traced module to demonstrate
    import sys
    sys.path.append('helpers')
    
    # Let's test the traced simple messaging module
    print("📋 Testing traced simple messaging...")
    from helpers.simple_messaging_traced import *
    
    print("✅ Traced module imported successfully!")
    print("🔍 Now every function call will be traced line by line!")
    
except ImportError as e:
    print(f"⚠️ Could not import traced module: {e}")
    print("💡 Let's create a simple test instead...")
    
    # Simple traced function for testing
    import snoop
    
    @snoop.snoop
    def traced_test_function(a, b, c):
        """Test function that will be traced."""
        print(f"Input parameters: a={a}, b={b}, c={c}")
        
        # Some computations
        sum_ab = a + b
        product = sum_ab * c
        
        # Some conditional logic
        if product > 100:
            result = product / 2
            status = "large"
        else:
            result = product * 2
            status = "small"
        
        # Return dict
        return {
            "sum_ab": sum_ab,
            "product": product,
            "result": result,
            "status": status
        }
    
    @snoop.snoop  
    def traced_data_processor(data_list):
        """Process a list of data with complete tracing."""
        print(f"Processing {len(data_list)} items...")
        
        results = []
        for i, item in enumerate(data_list):
            if isinstance(item, (int, float)):
                processed = item ** 2
                results.append(processed)
                print(f"Item {i}: {item} -> {processed}")
            else:
                results.append(str(item).upper())
                print(f"Item {i}: {item} -> {str(item).upper()}")
        
        total = sum(x for x in results if isinstance(x, (int, float)))
        average = total / len([x for x in results if isinstance(x, (int, float))]) if any(isinstance(x, (int, float)) for x in results) else 0
        
        return {
            "original_data": data_list,
            "processed_results": results,
            "total": total,
            "average": average
        }
    
    print("\n🔍 RUNNING TRACED FUNCTION TESTS")
    print("=" * 50)
    
    # Test 1: Simple computation with tracing
    print("\n📋 Test 1: Traced computation function")
    result1 = traced_test_function(10, 20, 3)
    print(f"Result: {result1}")
    
    # Test 2: Data processing with tracing  
    print("\n📋 Test 2: Traced data processing function")
    test_data = [1, 2.5, "hello", 4, "world", 10, 7.2]
    result2 = traced_data_processor(test_data)
    print(f"Processing result: {result2}")
    
    print("\n✅ TRACED EXECUTION COMPLETED!")
    print("🎯 As you can see, snoop shows:")
    print("   • Every line being executed")
    print("   • All variable values")
    print("   • Function calls and returns")
    print("   • Complete execution flow")
    
print("\n🚀 HOW TO USE TRACING IN YOUR CODEBASE:")
print("=" * 50)
print("1. All your modules now have '_traced' versions")
print("2. Import the traced versions instead of originals")
print("3. Run your code normally - every step will be traced!")
print("\n💡 Examples:")
print("   from helpers.github_app_tools_traced import GitHubAppTools")
print("   from helpers.enhanced_base_agent_traced import EnhancedBaseAgent")
print("   # Now all methods are traced!")
print("\n🔍 Every function call, variable change, and execution step will be visible!")
