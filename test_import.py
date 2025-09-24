#!/usr/bin/env python3
"""
Simple test script to verify all imports work correctly
"""

import os
import sys

def test_imports():
    """Test all the main imports."""
    print("=== Testing Imports ===\n")
    
    try:
        print("1. Testing proxy_config import...")
        from proxy_config import ProxyConfig
        print("✓ proxy_config imported successfully")
        
        # Test proxy config
        proxy_url = "http://osliani.figueiras:Dteam801*@proxy.desoft.cu:3128"
        config = ProxyConfig(proxy_url)
        print(f"   Proxy info: {config.get_proxy_info()}")
        
    except Exception as e:
        print(f"✗ Error importing proxy_config: {e}")
        return False
    
    try:
        print("\n2. Testing completions_v3 import...")
        from completions_v3 import Agent
        print("✓ completions_v3 imported successfully")
        
    except Exception as e:
        print(f"✗ Error importing completions_v3: {e}")
        return False
    
    try:
        print("\n3. Testing Agent creation with proxy...")
        agent = Agent(
            name="Test Agent",
            proxy_url="http://osliani.figueiras:Dteam801*@proxy.desoft.cu:3128"
        )
        print("✓ Agent created successfully with proxy")
        
    except Exception as e:
        print(f"✗ Error creating Agent: {e}")
        return False
    
    try:
        print("\n4. Testing console_chat import...")
        from console_chat import ConsoleChat
        print("✓ console_chat imported successfully")
        
    except Exception as e:
        print(f"✗ Error importing console_chat: {e}")
        return False
    
    print("\n=== All Tests Passed! ===")
    print("\nYour proxy configuration is ready to use!")
    print("\nNext steps:")
    print("1. Set your AVANGENIO_API_KEY in .env file")
    print("2. Run: python console_chat.py")
    print("3. Or set HTTP_PROXY environment variable")
    
    return True

if __name__ == "__main__":
    success = test_imports()
    if not success:
        sys.exit(1)
    
    print(f"\nPython version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
