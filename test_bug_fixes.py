#!/usr/bin/env python3
"""
Quick test to verify critical bug fixes
"""

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, 'src')

from comprehensive_nlp_patterns import analyze_comprehensive_intent
from universal_intent_executor import execute_intent_with_tools

async def test_critical_bug_fixes():
    """Test that critical bugs are fixed"""
    print("🔧 TESTING CRITICAL BUG FIXES")
    print("=" * 40)
    
    # Test 1: Import re issue
    print("1. Testing import re issue...")
    try:
        intent, confidence, entities = await analyze_comprehensive_intent("BTC price")
        print(f"   ✅ Import re fixed - got intent: {intent}")
    except Exception as e:
        print(f"   ❌ Import re still broken: {e}")
    
    # Test 2: ExecutionResult.get() issue
    print("2. Testing ExecutionResult.get() issue...")
    try:
        result = await execute_intent_with_tools("price", {"cryptocurrency": "BTC"}, {})
        success = result.get('success', False)
        print(f"   ✅ ExecutionResult.get() fixed - success: {success}")
    except Exception as e:
        print(f"   ❌ ExecutionResult.get() still broken: {e}")
    
    # Test 3: Intent recognition improvement
    print("3. Testing intent recognition...")
    test_queries = [
        "BTC price now",
        "RSI for ETH", 
        "show my portfolio",
        "what is Bitcoin"
    ]
    
    improved_count = 0
    for query in test_queries:
        try:
            intent, confidence, entities = await analyze_comprehensive_intent(query)
            if intent != 'general' and confidence > 0.7:
                improved_count += 1
                print(f"   ✅ '{query}' -> {intent} ({confidence:.2f})")
            else:
                print(f"   ⚠️ '{query}' -> {intent} ({confidence:.2f})")
        except Exception as e:
            print(f"   ❌ '{query}' -> Error: {e}")
    
    improvement_rate = (improved_count / len(test_queries)) * 100
    print(f"   Intent recognition improvement: {improvement_rate:.1f}%")
    
    # Test 4: Edge case handling
    print("4. Testing edge case handling...")
    edge_cases = ["", "   ", "!@#$%", "<script>alert('xss')</script>"]
    
    handled_count = 0
    for case in edge_cases:
        try:
            intent, confidence, entities = await analyze_comprehensive_intent(case)
            handled_count += 1
            print(f"   ✅ Edge case handled: '{case[:20]}...'")
        except Exception as e:
            print(f"   ❌ Edge case failed: '{case[:20]}...' - {e}")
    
    edge_handling_rate = (handled_count / len(edge_cases)) * 100
    print(f"   Edge case handling: {edge_handling_rate:.1f}%")
    
    print("\n📊 BUG FIX SUMMARY:")
    print(f"   Import re: {'✅ Fixed' if 'Import re fixed' in str(locals()) else '❌ Still broken'}")
    print(f"   ExecutionResult.get(): {'✅ Fixed' if 'ExecutionResult.get() fixed' in str(locals()) else '❌ Still broken'}")
    print(f"   Intent recognition: {improvement_rate:.1f}% improved")
    print(f"   Edge case handling: {edge_handling_rate:.1f}% success")
    
    if improvement_rate >= 75 and edge_handling_rate >= 75:
        print("\n🎉 CRITICAL BUGS SUCCESSFULLY FIXED!")
        return True
    else:
        print("\n⚠️ Some issues remain - needs more work")
        return False

if __name__ == "__main__":
    asyncio.run(test_critical_bug_fixes())