"""
Demo: Traced Function Execution
==============================

This demonstrates how to use traced execution with your existing functions.
"""

print("🎯 TESTING TRACED FUNCTION EXECUTION")
print("=" * 50)

# Let's test with a simple traced function
import snoop

@snoop.snoop
def demo_traced_github_function():
    """Demo function showing how GitHub app tools would be traced."""
    
    print("🔧 Starting GitHub App authentication process...")
    
    # Simulate checking environment variables
    app_id = "12345"
    repo = "user/repo"
    
    # Simulate JWT creation process
    import time
    now = int(time.time())
    payload_data = {
        "iat": now - 60,
        "exp": now + 540,
        "iss": app_id
    }
    
    print(f"📋 Creating JWT payload: {payload_data}")
    
    # Simulate token processing
    jwt_token = f"jwt_token_for_{app_id}"
    
    # Simulate API headers
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ai-foundry-agent/1.0"
    }
    
    print(f"🔑 Generated headers: {headers}")
    
    # Simulate installation ID lookup
    installation_id = 12345678
    
    result = {
        "app_id": app_id,
        "repo": repo,
        "jwt_token": jwt_token,
        "installation_id": installation_id,
        "headers": headers,
        "status": "success"
    }
    
    print(f"✅ Authentication result: {result}")
    
    return result

@snoop.snoop
def demo_traced_data_processing():
    """Demo function showing data processing with complete tracing."""
    
    print("📊 Starting data processing...")
    
    # Sample data processing
    raw_data = [1, 2, 3, 4, 5, "hello", 6, 7, "world", 8, 9, 10]
    
    # Filter numbers
    numbers = []
    strings = []
    
    for item in raw_data:
        if isinstance(item, (int, float)):
            numbers.append(item)
        else:
            strings.append(str(item))
    
    # Calculate statistics
    total = sum(numbers)
    count = len(numbers)
    average = total / count if count > 0 else 0
    
    # Process strings
    processed_strings = [s.upper() for s in strings]
    
    # Create final result
    result = {
        "original_data": raw_data,
        "numbers": numbers,
        "strings": strings,
        "processed_strings": processed_strings,
        "statistics": {
            "total": total,
            "count": count,
            "average": average
        }
    }
    
    print(f"✅ Processing complete: {result}")
    
    return result

# Run the traced functions
print("\n📋 DEMO 1: Traced GitHub Function")
result1 = demo_traced_github_function()

print("\n📋 DEMO 2: Traced Data Processing")
result2 = demo_traced_data_processing()

print(f"\n✅ TRACING DEMONSTRATION COMPLETED!")
print("🔍 As you can see, snoop shows:")
print("   • Every line number being executed")
print("   • All variable assignments and values")
print("   • Function calls and returns")
print("   • Complete execution flow with timestamps")
print("   • Variable watching - see exactly what changes")

print(f"\n🚀 TO TRACE YOUR ACTUAL CODEBASE:")
print("1. Import any function from the '_traced' modules")
print("2. All the functions are already decorated with @snoop.snoop")
print("3. Run your code normally - every step will be traced!")

print(f"\n📋 Example with your actual code:")
print("   # Import traced functions")
print("   from helpers.github_app_tools_traced import get_installation_token")
print("   from helpers.enhanced_base_agent_traced import EnhancedBaseAgent")
print("   ")
print("   # Use them normally - they'll be traced automatically!")
print("   token = get_installation_token(12345)")
print("   agent = EnhancedBaseAgent('MyAgent')")

print(f"\n🎯 Now you can trace EVERYTHING in your codebase!")
print("Every function call, every variable change, every execution step!")
