#!/usr/bin/env python3
"""
Test Intent Recognition Fixes
"""

import asyncio
import sys
import os
sys.path.append('/workspace/mody/src')

from enhanced_intent_system import analyze_user_intent_enhanced, IntentType, ResponseStrategy

async def test_intent_recognition():
    """Test if intent recognition is working properly"""
    
    test_cases = [
        ("BTC price", IntentType.CRYPTO_PRICE, ResponseStrategy.LIVE_DATA_API),
        ("ETH price", IntentType.CRYPTO_PRICE, ResponseStrategy.LIVE_DATA_API),
        ("bitcoin", IntentType.CRYPTO_PRICE, ResponseStrategy.LIVE_DATA_API),
        ("solana price today", IntentType.CRYPTO_PRICE, ResponseStrategy.LIVE_DATA_API),
        ("price of DOT", IntentType.CRYPTO_PRICE, ResponseStrategy.LIVE_DATA_API),
        ("what is the price of ethereum", IntentType.CRYPTO_PRICE, ResponseStrategy.LIVE_DATA_API),
    ]
    
    print("🧪 TESTING INTENT RECOGNITION FIXES")
    print("=" * 50)
    
    success_count = 0
    total_count = len(test_cases)
    
    for text, expected_intent, expected_strategy in test_cases:
        try:
            analysis = await analyze_user_intent_enhanced(text, 12345, {})
            
            intent_match = analysis.intent_type == expected_intent
            strategy_match = analysis.response_strategy == expected_strategy
            
            status = "✅ PASS" if (intent_match and strategy_match) else "❌ FAIL"
            
            if intent_match and strategy_match:
                success_count += 1
            
            print(f"{status} | '{text}'")
            print(f"     Expected: {expected_intent.value} -> {expected_strategy.value}")
            print(f"     Got:      {analysis.intent_type.value} -> {analysis.response_strategy.value}")
            print(f"     Confidence: {analysis.confidence:.2f}")
            print(f"     Entities: {analysis.extracted_entities}")
            print()
            
        except Exception as e:
            print(f"❌ ERROR | '{text}': {e}")
            print()
    
    success_rate = (success_count / total_count) * 100
    print(f"📊 RESULTS: {success_count}/{total_count} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("✅ Intent recognition is working properly!")
        return True
    else:
        print("❌ Intent recognition still has issues!")
        return False

async def test_crypto_price_api():
    """Test if crypto price API is working"""
    print("\n🔍 TESTING CRYPTO PRICE API")
    print("=" * 30)
    
    try:
        from enhanced_response_handler import EnhancedResponseHandler
        from enhanced_intent_system import EnhancedIntentAnalysis, IntentType, ResponseStrategy
        
        handler = EnhancedResponseHandler()
        
        # Create a mock analysis for BTC price
        analysis = EnhancedIntentAnalysis(
            intent_type=IntentType.CRYPTO_PRICE,
            confidence=0.9,
            response_strategy=ResponseStrategy.LIVE_DATA_API,
            extracted_entities={'symbol': 'btc', 'normalized_symbol': 'bitcoin'},
            should_respond=True,
            priority_score=0.9,
            data_sources=['coingecko'],
            fallback_strategy=ResponseStrategy.SIMPLE_AI
        )
        
        result = await handler._fetch_crypto_price(analysis.extracted_entities)
        
        if result and result.get('type') != 'error':
            print("✅ Crypto price API is working!")
            print(f"   Result type: {result.get('type')}")
            if 'message' in result:
                print(f"   Message preview: {result['message'][:100]}...")
            return True
        else:
            print("❌ Crypto price API failed!")
            print(f"   Result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing crypto price API: {e}")
        return False

async def main():
    """Run all tests"""
    print("🔧 TESTING ALL FIXES")
    print("=" * 60)
    
    intent_ok = await test_intent_recognition()
    api_ok = await test_crypto_price_api()
    
    print("\n🎯 OVERALL RESULTS:")
    print("=" * 20)
    print(f"Intent Recognition: {'✅ FIXED' if intent_ok else '❌ BROKEN'}")
    print(f"Crypto Price API:  {'✅ WORKING' if api_ok else '❌ BROKEN'}")
    
    if intent_ok and api_ok:
        print("\n🎉 ALL CORE FIXES ARE WORKING!")
        return True
    else:
        print("\n⚠️ Some fixes still need work!")
        return False

if __name__ == "__main__":
    asyncio.run(main())