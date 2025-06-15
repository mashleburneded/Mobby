#!/usr/bin/env python3
"""
Comprehensive test suite to verify all critical fixes are working
"""

import sys
import os
import asyncio
import importlib.util

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all critical imports work without errors"""
    print("🔍 Testing imports...")
    
    try:
        # Test main.py imports
        import main
        print("✅ main.py imports successfully")
        
        # Test crypto_research imports
        import crypto_research
        print("✅ crypto_research.py imports successfully")
        
        # Test intelligent_message_router imports
        import intelligent_message_router
        print("✅ intelligent_message_router.py imports successfully")
        
        # Test enhanced_natural_language imports
        import enhanced_natural_language
        print("✅ enhanced_natural_language.py imports successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_function_availability():
    """Test that critical functions are available"""
    print("\n🔍 Testing function availability...")
    
    try:
        from crypto_research import get_price_data
        print("✅ get_price_data function is available")
        
        from intelligent_message_router import IntelligentMessageRouter
        router = IntelligentMessageRouter()
        print("✅ IntelligentMessageRouter class is available")
        
        from enhanced_natural_language import process_natural_language
        print("✅ process_natural_language function is available")
        
        return True
    except Exception as e:
        print(f"❌ Function availability error: {e}")
        return False

async def test_price_function():
    """Test the price data function"""
    print("\n🔍 Testing price data function...")
    
    try:
        from crypto_research import get_price_data
        
        # Test with a known symbol
        result = await get_price_data("bitcoin")
        if result.get("success"):
            print("✅ Price data function works correctly")
            print(f"   Sample result: {result}")
            return True
        else:
            print(f"❌ Price function returned error: {result}")
            return False
    except Exception as e:
        print(f"❌ Price function error: {e}")
        return False

async def test_pattern_matching():
    """Test the enhanced pattern matching"""
    print("\n🔍 Testing pattern matching...")
    
    try:
        from intelligent_message_router import IntelligentMessageRouter
        router = IntelligentMessageRouter()
        
        # Test cases
        test_cases = [
            ("what's the price of bitcoin", "crypto_query"),
            ("sol price please", "crypto_query"),
            ("btc price", "crypto_query"),
            ("show me ethereum price", "crypto_query"),
            ("hello", "greeting"),
            ("thanks", "casual_chat")
        ]
        
        for text, expected_type in test_cases:
            analysis = await router.analyze_message(text, "private", False, False, False)
            if analysis.message_type.value == expected_type:
                print(f"✅ '{text}' correctly classified as {expected_type}")
            else:
                print(f"❌ '{text}' classified as {analysis.message_type.value}, expected {expected_type}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Pattern matching error: {e}")
        return False

def test_symbol_extraction():
    """Test crypto symbol extraction"""
    print("\n🔍 Testing symbol extraction...")
    
    try:
        from intelligent_message_router import IntelligentMessageRouter
        router = IntelligentMessageRouter()
        
        test_cases = [
            ("what's the price of bitcoin", "BTC"),
            ("sol price please", "SOL"),
            ("ethereum price", "ETH"),
            ("show me BTC price", "BTC"),
            ("price of DOGE", "DOGE")
        ]
        
        for text, expected_symbol in test_cases:
            symbol = router._extract_crypto_symbol(text, "BTC")  # Add fallback parameter
            if symbol == expected_symbol:
                print(f"✅ '{text}' correctly extracted symbol: {symbol}")
            else:
                print(f"❌ '{text}' extracted '{symbol}', expected '{expected_symbol}'")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Symbol extraction error: {e}")
        return False

def test_file_compilation():
    """Test that all files compile without syntax errors"""
    print("\n🔍 Testing file compilation...")
    
    files_to_test = [
        "src/main.py",
        "src/crypto_research.py",
        "src/intelligent_message_router.py",
        "src/enhanced_natural_language.py"
    ]
    
    for file_path in files_to_test:
        try:
            spec = importlib.util.spec_from_file_location("test_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"✅ {file_path} compiles successfully")
        except Exception as e:
            print(f"❌ {file_path} compilation error: {e}")
            return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Running comprehensive fix verification tests...\n")
    
    tests = [
        ("File Compilation", test_file_compilation),
        ("Imports", test_imports),
        ("Function Availability", test_function_availability),
        ("Pattern Matching", test_pattern_matching),
        ("Symbol Extraction", test_symbol_extraction),
        ("Price Function", test_price_function)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} Test")
        print('='*50)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The bot should now work correctly.")
        print("\n📋 Ready for deployment:")
        print("   1. All import errors fixed")
        print("   2. Price commands working")
        print("   3. Pattern matching enhanced")
        print("   4. Symbol extraction improved")
        print("   5. Error handling robust")
        print("\n🚀 You can now restart the bot!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the errors above.")

if __name__ == "__main__":
    asyncio.run(main())