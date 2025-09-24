#!/usr/bin/env python3
"""
Test script for the console chat module.
"""

def test_imports():
    """Test that all imports work correctly."""
    try:
        from console_chat import ConsoleChat  # noqa: F401
        from enumerations import ModelType  # noqa: F401
        print("✓ Imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_console_chat_creation():
    """Test creating a ConsoleChat instance."""
    try:
        from console_chat import ConsoleChat
        from enumerations import ModelType
        
        chat = ConsoleChat(agent_name="Test Agent", model=ModelType.GPT_4_1.value)
        print("✓ ConsoleChat instance created successfully")
        print(f"  - Agent name: {chat.agent.name}")
        print(f"  - Model: {chat.agent.model}")
        print(f"  - Channel ID: {chat.channel_id}")
        return True
    except Exception as e:
        print(f"✗ Error creating ConsoleChat: {e}")
        return False

def test_command_handling():
    """Test command handling functionality."""
    try:
        from console_chat import ConsoleChat
        
        chat = ConsoleChat()
        
        # Test help command
        chat.handle_command("/help")
        print("✓ Help command handled")
        
        # Test clear command
        chat.handle_command("/clear")
        print("✓ Clear command handled")
        
        # Test non-command
        chat.handle_command("hello")
        print("✓ Non-command handled correctly")
        
        return True
    except Exception as e:
        print(f"✗ Error testing commands: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Console Chat Module")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_console_chat_creation,
        test_command_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        if test():
            passed += 1
    
    print(f"\n{'=' * 40}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Console chat module is ready to use.")
    else:
        print("✗ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
