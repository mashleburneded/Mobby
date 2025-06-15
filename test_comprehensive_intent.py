#!/usr/bin/env python3
"""
Comprehensive Intent Recognition Test
"""

import asyncio
import sys
import os
sys.path.append('/workspace/mody/src')

from enhanced_intent_system import analyze_user_intent_enhanced, IntentType, ResponseStrategy

async def test_comprehensive_intent_recognition():
    """Test all intent types with various queries"""
    
    test_cases = [
        # CRYPTO_PRICE tests
        ("BTC price", IntentType.CRYPTO_PRICE),
        ("ETH value", IntentType.CRYPTO_PRICE),
        ("bitcoin", IntentType.CRYPTO_PRICE),
        ("price of solana", IntentType.CRYPTO_PRICE),
        ("what is the price of ethereum", IntentType.CRYPTO_PRICE),
        
        # PORTFOLIO_CHECK tests
        ("portfolio", IntentType.PORTFOLIO_CHECK),
        ("my holdings", IntentType.PORTFOLIO_CHECK),
        ("show my balance", IntentType.PORTFOLIO_CHECK),
        ("what do I have", IntentType.PORTFOLIO_CHECK),
        
        # ALERT_MANAGEMENT tests
        ("alerts", IntentType.ALERT_MANAGEMENT),
        ("set alert", IntentType.ALERT_MANAGEMENT),
        ("notify me when", IntentType.ALERT_MANAGEMENT),
        ("create alert", IntentType.ALERT_MANAGEMENT),
        
        # HELP_REQUEST tests
        ("help", IntentType.HELP_REQUEST),
        ("what can you do", IntentType.HELP_REQUEST),
        ("commands", IntentType.HELP_REQUEST),
        ("how do I use this", IntentType.HELP_REQUEST),
        
        # DEFI_PROTOCOL tests
        ("uniswap", IntentType.DEFI_PROTOCOL),
        ("what is aave", IntentType.DEFI_PROTOCOL),
        ("compound info", IntentType.DEFI_PROTOCOL),
        ("tell me about maker", IntentType.DEFI_PROTOCOL),
        
        # YIELD_FARMING tests
        ("yield opportunities", IntentType.YIELD_FARMING),
        ("best apy", IntentType.YIELD_FARMING),
        ("where to stake", IntentType.YIELD_FARMING),
        
        # GREETING tests
        ("hello", IntentType.GREETING),
        ("hi", IntentType.GREETING),
        ("good morning", IntentType.GREETING),
        ("thanks", IntentType.GREETING),
        
        # EXPLANATION tests
        ("what is defi", IntentType.EXPLANATION),
        ("explain blockchain", IntentType.EXPLANATION),
        ("how does staking work", IntentType.EXPLANATION),
        
        # GENERAL_QUERY tests
        ("can you help me", IntentType.GENERAL_QUERY),
        ("i want to know", IntentType.GENERAL_QUERY),
        ("tell me about", IntentType.GENERAL_QUERY),
    ]
    
    print("🧪 COMPREHENSIVE INTENT RECOGNITION TEST")
    print("=" * 60)
    
    success_count = 0
    total_count = len(test_cases)
    
    intent_type_counts = {}
    
    for text, expected_intent in test_cases:
        try:
            analysis = await analyze_user_intent_enhanced(text, 12345, {})
            
            intent_match = analysis.intent_type == expected_intent
            
            if intent_match:
                success_count += 1
                status = "✅"
            else:
                status = "❌"
            
            # Count by intent type
            if expected_intent not in intent_type_counts:
                intent_type_counts[expected_intent] = {'total': 0, 'success': 0}
            intent_type_counts[expected_intent]['total'] += 1
            if intent_match:
                intent_type_counts[expected_intent]['success'] += 1
            
            print(f"{status} '{text}' -> Expected: {expected_intent.value}, Got: {analysis.intent_type.value} (conf: {analysis.confidence:.2f})")
            
        except Exception as e:
            print(f"❌ ERROR | '{text}': {e}")
    
    print("\n" + "=" * 60)
    print("📊 RESULTS BY INTENT TYPE:")
    print("=" * 60)
    
    for intent_type, counts in intent_type_counts.items():
        success_rate = (counts['success'] / counts['total']) * 100
        print(f"{intent_type.value:20} | {counts['success']:2}/{counts['total']:2} ({success_rate:5.1f}%)")
    
    overall_success_rate = (success_count / total_count) * 100
    print(f"\n🎯 OVERALL: {success_count}/{total_count} tests passed ({overall_success_rate:.1f}%)")
    
    if overall_success_rate >= 90:
        print("🎉 EXCELLENT! Intent recognition is working comprehensively!")
        return True
    elif overall_success_rate >= 75:
        print("✅ GOOD! Most intents are working, some fine-tuning needed.")
        return True
    else:
        print("❌ NEEDS WORK! Intent recognition has major issues.")
        return False

async def test_conversation_flow():
    """Test the actual conversation flow"""
    print("\n🔄 TESTING CONVERSATION FLOW")
    print("=" * 40)
    
    try:
        # Test if enhanced response handler works
        from enhanced_response_handler import handle_enhanced_response
        from enhanced_intent_system import EnhancedIntentAnalysis, IntentType, ResponseStrategy
        
        # Test a simple price query
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
        
        response = await handle_enhanced_response(analysis, "BTC price", 12345, {})
        
        if response and response.get('message'):
            print("✅ Conversation flow is working!")
            print(f"   Response type: {response.get('type')}")
            print(f"   Message preview: {response['message'][:100]}...")
            return True
        else:
            print("❌ Conversation flow failed!")
            print(f"   Response: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing conversation flow: {e}")
        return False

async def main():
    """Run comprehensive tests"""
    print("🔍 COMPREHENSIVE INTENT & CONVERSATION TEST")
    print("=" * 70)
    
    intent_ok = await test_comprehensive_intent_recognition()
    flow_ok = await test_conversation_flow()
    
    print("\n🎯 FINAL RESULTS:")
    print("=" * 20)
    print(f"Intent Recognition: {'✅ WORKING' if intent_ok else '❌ BROKEN'}")
    print(f"Conversation Flow:  {'✅ WORKING' if flow_ok else '❌ BROKEN'}")
    
    if intent_ok and flow_ok:
        print("\n🎉 ALL SYSTEMS ARE WORKING!")
        print("The bot should now properly recognize intents and hold conversations!")
        return True
    else:
        print("\n⚠️ Some systems still need work!")
        return False

if __name__ == "__main__":
    asyncio.run(main())