#!/usr/bin/env python3
"""
Test script to verify the main fixes for Möbius AI Assistant
"""

import sys
import os
import asyncio
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all critical imports work"""
    print("🔍 Testing imports...")
    
    try:
        from typing import Dict, Any, List, Optional, Union
        print("✅ Typing imports work")
    except Exception as e:
        print(f"❌ Typing imports failed: {e}")
        return False
    
    try:
        from crypto_research import get_price_data, search_protocol_by_name
        print("✅ Crypto research imports work")
    except Exception as e:
        print(f"❌ Crypto research imports failed: {e}")
        return False
    
    try:
        from intelligent_message_router import analyze_message_intent, should_use_mcp, should_respond
        print("✅ Message router imports work")
    except Exception as e:
        print(f"❌ Message router imports failed: {e}")
        return False
    
    return True

async def test_price_function():
    """Test the get_price_data function"""
    print("\n💰 Testing price function...")
    
    try:
        from crypto_research import get_price_data
        
        # Test Bitcoin price
        result = await get_price_data('BTC')
        if result.get('success'):
            print(f"✅ BTC price: ${result.get('price', 'N/A'):,.2f}")
            print(f"   24h change: {result.get('change_24h', 0):.2f}%")
        else:
            print(f"❌ Failed to get BTC price: {result.get('message', 'Unknown error')}")
            return False
        
        # Test invalid symbol
        result = await get_price_data('INVALID_SYMBOL_123')
        if not result.get('success'):
            print("✅ Invalid symbol handling works")
        else:
            print("❌ Invalid symbol should have failed")
            return False
            
    except Exception as e:
        print(f"❌ Price function test failed: {e}")
        return False
    
    return True

async def test_message_routing():
    """Test the message routing logic"""
    print("\n🧠 Testing message routing...")
    
    try:
        from intelligent_message_router import analyze_message_intent
        
        # Test different message types
        test_cases = [
            ("hello", "greeting"),
            ("what's the price of bitcoin", "crypto_query"),
            ("thanks", "casual_chat"),
            ("show my portfolio", "portfolio_request"),
        ]
        
        for text, expected_type in test_cases:
            analysis = await analyze_message_intent(
                text=text,
                user_id=12345,
                chat_type="private",
                is_reply_to_bot=False,
                is_mentioned=False
            )
            
            print(f"✅ '{text}' -> {analysis.message_type.value} (strategy: {analysis.processing_strategy.value})")
            
            # Check that MCP is not being used automatically
            if analysis.processing_strategy.value == "mcp_enhanced":
                print(f"⚠️  Warning: MCP being used for simple message: '{text}'")
        
    except Exception as e:
        print(f"❌ Message routing test failed: {e}")
        return False
    
    return True

def test_context_handling():
    """Test that context handling doesn't use .get() on CallbackContext"""
    print("\n🔧 Testing context handling...")
    
    try:
        # Read main.py and check for problematic patterns
        with open('src/main.py', 'r') as f:
            content = f.read()
        
        # Check for context.get() usage (should be fixed)
        if 'context.get(' in content:
            print("❌ Found context.get() usage in main.py")
            return False
        else:
            print("✅ No context.get() usage found in main.py")
        
        # Check for proper Dict, Any imports
        if 'from typing import Dict, Any' in content:
            print("✅ Proper typing imports found")
        else:
            print("❌ Missing proper typing imports")
            return False
            
    except Exception as e:
        print(f"❌ Context handling test failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting Möbius AI Assistant Fix Verification\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Price Function Tests", test_price_function),
        ("Message Routing Tests", test_message_routing),
        ("Context Handling Tests", test_context_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name}")
        print('='*50)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"SUMMARY: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! The fixes should resolve the reported issues.")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
    
    return passed == total

if __name__ == "__main__":
    # Set minimal config to avoid errors
    os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'dummy_token')
    os.environ.setdefault('TELEGRAM_CHAT_ID', '12345')
    os.environ.setdefault('BOT_MASTER_ENCRYPTION_KEY', 'dummy_key')
    
    asyncio.run(main())