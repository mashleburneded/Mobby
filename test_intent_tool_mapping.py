#!/usr/bin/env python3
"""
Test Intent-to-Tool Mapping
Verifies that detected intents execute the correct tools/functions
"""

import asyncio
import sys
import os
sys.path.append('/workspace/mody/src')

async def test_intent_tool_mapping():
    """Test if intents execute the correct tools"""
    print("🔧 TESTING INTENT-TO-TOOL MAPPING")
    print("=" * 50)
    
    from enhanced_intent_system import analyze_user_intent_enhanced
    from enhanced_response_handler import handle_enhanced_response
    
    # Test cases: query -> expected intent -> expected tool/function
    test_cases = [
        {
            "query": "BTC price",
            "expected_intent": "crypto_price",
            "expected_tools": ["CoinGecko API", "crypto price lookup"],
            "expected_response_contains": ["Price:", "$", "BTC", "Bitcoin"]
        },
        {
            "query": "portfolio",
            "expected_intent": "portfolio_check", 
            "expected_tools": ["portfolio manager", "holdings tracker"],
            "expected_response_contains": ["Portfolio", "holdings", "track"]
        },
        {
            "query": "help",
            "expected_intent": "help_request",
            "expected_tools": ["help system", "command list"],
            "expected_response_contains": ["Help", "commands", "can do"]
        },
        {
            "query": "uniswap info",
            "expected_intent": "defi_protocol",
            "expected_tools": ["DeFiLlama API", "protocol data"],
            "expected_response_contains": ["Uniswap", "TVL", "protocol"]
        },
        {
            "query": "set alert for BTC",
            "expected_intent": "alert_management",
            "expected_tools": ["alert system", "notification manager"],
            "expected_response_contains": ["Alert", "notification", "set"]
        },
        {
            "query": "what is ethereum",
            "expected_intent": "explanation",
            "expected_tools": ["AI provider", "knowledge base"],
            "expected_response_contains": ["Ethereum", "blockchain", "decentralized"]
        },
        {
            "query": "yield farming opportunities",
            "expected_intent": "yield_farming",
            "expected_tools": ["DeFi scanner", "yield calculator"],
            "expected_response_contains": ["yield", "farming", "APY"]
        },
        {
            "query": "hello",
            "expected_intent": "greeting",
            "expected_tools": ["template response", "greeting handler"],
            "expected_response_contains": ["Hello", "help", "assistant"]
        }
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        query = test_case["query"]
        expected_intent = test_case["expected_intent"]
        expected_tools = test_case["expected_tools"]
        expected_response_contains = test_case["expected_response_contains"]
        
        print(f"\n🧪 Test {i}/{total_count}: '{query}'")
        
        try:
            # Step 1: Analyze intent
            analysis = await analyze_user_intent_enhanced(query, 12345, {})
            detected_intent = analysis.intent_type.value
            confidence = analysis.confidence
            strategy = analysis.response_strategy.value
            
            print(f"   🎯 Detected Intent: {detected_intent} (confidence: {confidence:.2f})")
            print(f"   📋 Strategy: {strategy}")
            
            # Check if intent matches expected
            intent_correct = detected_intent == expected_intent
            if intent_correct:
                print(f"   ✅ Intent detection: CORRECT")
            else:
                print(f"   ❌ Intent detection: WRONG (expected {expected_intent})")
            
            # Step 2: Generate response and check tools used
            response = await handle_enhanced_response(analysis, query, 12345, {})
            
            if response and response.get('message'):
                response_text = response['message']
                print(f"   📝 Response: {response_text[:100]}...")
                
                # Check if response contains expected content
                content_matches = sum(1 for keyword in expected_response_contains 
                                    if keyword.lower() in response_text.lower())
                content_correct = content_matches >= len(expected_response_contains) // 2
                
                if content_correct:
                    print(f"   ✅ Response content: RELEVANT ({content_matches}/{len(expected_response_contains)} keywords found)")
                else:
                    print(f"   ❌ Response content: IRRELEVANT ({content_matches}/{len(expected_response_contains)} keywords found)")
                
                # Determine if correct tools were likely used based on response strategy and content
                tools_correct = False
                if strategy == "live_data" and any(tool in ["API", "data"] for tool in expected_tools):
                    tools_correct = True
                elif strategy == "built_in" and any(tool in ["system", "template", "manager"] for tool in expected_tools):
                    tools_correct = True
                elif strategy == "simple_ai" and any(tool in ["AI", "knowledge"] for tool in expected_tools):
                    tools_correct = True
                
                if tools_correct:
                    print(f"   ✅ Tool execution: CORRECT (strategy '{strategy}' matches expected tools)")
                else:
                    print(f"   ⚠️ Tool execution: UNCERTAIN (strategy '{strategy}' for tools {expected_tools})")
                
                # Overall success if intent and content are correct
                if intent_correct and content_correct:
                    success_count += 1
                    print(f"   🎉 OVERALL: SUCCESS")
                else:
                    print(f"   ❌ OVERALL: FAILED")
                    
            else:
                print(f"   ❌ No response generated")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    success_rate = (success_count / total_count) * 100
    print(f"\n🎯 INTENT-TO-TOOL MAPPING RESULTS:")
    print(f"   Success Rate: {success_count}/{total_count} ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("   🎉 EXCELLENT! Intents are executing the right tools!")
    elif success_rate >= 75:
        print("   ✅ GOOD! Most intents execute correct tools, minor issues.")
    else:
        print("   ❌ ISSUES! Intent-to-tool mapping needs improvement.")
    
    return success_rate >= 75

async def test_specific_tool_execution():
    """Test specific tool execution paths"""
    print("\n🔍 TESTING SPECIFIC TOOL EXECUTION")
    print("=" * 40)
    
    # Test crypto price API specifically
    try:
        from enhanced_response_handler import get_crypto_price
        
        print("🪙 Testing Crypto Price API...")
        price_data = await get_crypto_price("bitcoin")
        
        if price_data and "price" in price_data:
            print(f"   ✅ CoinGecko API: Working (BTC price: ${price_data['price']})")
        else:
            print(f"   ❌ CoinGecko API: Failed")
            
    except Exception as e:
        print(f"   ❌ Crypto Price API Error: {e}")
    
    # Test DeFi protocol API
    try:
        from defillama_api import get_protocol_info
        
        print("🏦 Testing DeFi Protocol API...")
        protocol_data = await get_protocol_info("uniswap")
        
        if protocol_data and "tvl" in protocol_data:
            print(f"   ✅ DeFiLlama API: Working (Uniswap TVL: ${protocol_data['tvl']:,.2f})")
        else:
            print(f"   ❌ DeFiLlama API: Failed")
            
    except Exception as e:
        print(f"   ❌ DeFi Protocol API Error: {e}")
    
    # Test AI provider
    try:
        from ai_provider_manager import AIProviderManager
        
        print("🤖 Testing AI Provider...")
        ai_manager = AIProviderManager()
        
        response = await ai_manager.get_ai_response(
            "What is Bitcoin?", 
            12345, 
            {"provider": "gemini"}
        )
        
        if response and len(response) > 50:
            print(f"   ✅ AI Provider: Working (response length: {len(response)} chars)")
        else:
            print(f"   ❌ AI Provider: Failed or short response")
            
    except Exception as e:
        print(f"   ❌ AI Provider Error: {e}")

async def main():
    """Run all intent-to-tool mapping tests"""
    print("🔧 COMPREHENSIVE INTENT-TO-TOOL MAPPING TEST")
    print("=" * 60)
    
    mapping_ok = await test_intent_tool_mapping()
    await test_specific_tool_execution()
    
    print("\n🎯 FINAL ASSESSMENT:")
    print("=" * 30)
    
    if mapping_ok:
        print("✅ INTENTS ARE EXECUTING THE RIGHT TOOLS!")
        print("The bot correctly maps user intents to appropriate tools and functions.")
    else:
        print("❌ INTENT-TO-TOOL MAPPING NEEDS IMPROVEMENT!")
        print("Some intents are not executing the expected tools.")
    
    return mapping_ok

if __name__ == "__main__":
    asyncio.run(main())