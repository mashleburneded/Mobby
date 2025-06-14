#!/usr/bin/env python3
"""
Test Enhanced Intent System and Response Handler
Tests the new prioritized intent recognition and real data integration
"""

import asyncio
import logging
import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_enhanced_intent_system():
    """Test the enhanced intent recognition system"""
    print("🧪 Testing Enhanced Intent System")
    print("=" * 50)
    
    try:
        from enhanced_intent_system import analyze_user_intent_enhanced, IntentType, ResponseStrategy
        
        test_cases = [
            # High priority - crypto prices
            ("BTC price", IntentType.CRYPTO_PRICE, ResponseStrategy.LIVE_DATA_API),
            ("What's the price of ethereum?", IntentType.CRYPTO_PRICE, ResponseStrategy.LIVE_DATA_API),
            ("How much is SOL worth?", IntentType.CRYPTO_PRICE, ResponseStrategy.LIVE_DATA_API),
            
            # Portfolio queries
            ("Show my portfolio", IntentType.PORTFOLIO_CHECK, ResponseStrategy.BUILT_IN_COMMAND),
            ("Check my balance", IntentType.PORTFOLIO_CHECK, ResponseStrategy.BUILT_IN_COMMAND),
            
            # DeFi protocols
            ("Tell me about Uniswap protocol", IntentType.DEFI_PROTOCOL, ResponseStrategy.LIVE_DATA_API),
            ("Aave stats", IntentType.DEFI_PROTOCOL, ResponseStrategy.LIVE_DATA_API),
            
            # Yield farming
            ("Best yield opportunities", IntentType.YIELD_FARMING, ResponseStrategy.LIVE_DATA_API),
            ("High APY pools", IntentType.YIELD_FARMING, ResponseStrategy.LIVE_DATA_API),
            
            # Greetings
            ("Hello", IntentType.GREETING, ResponseStrategy.TEMPLATE_RESPONSE),
            ("Hi there", IntentType.GREETING, ResponseStrategy.TEMPLATE_RESPONSE),
            
            # Help
            ("Help", IntentType.HELP_REQUEST, ResponseStrategy.BUILT_IN_COMMAND),
            ("What can you do?", IntentType.HELP_REQUEST, ResponseStrategy.BUILT_IN_COMMAND),
        ]
        
        results = []
        
        for text, expected_intent, expected_strategy in test_cases:
            try:
                analysis = await analyze_user_intent_enhanced(text, 12345)
                
                intent_match = analysis.intent_type == expected_intent
                strategy_match = analysis.response_strategy == expected_strategy
                
                status = "✅" if intent_match and strategy_match else "❌"
                
                print(f"{status} '{text}'")
                print(f"   Expected: {expected_intent.value} -> {expected_strategy.value}")
                print(f"   Got:      {analysis.intent_type.value} -> {analysis.response_strategy.value}")
                print(f"   Confidence: {analysis.confidence:.2f}")
                print(f"   Entities: {analysis.extracted_entities}")
                print()
                
                results.append({
                    "text": text,
                    "expected_intent": expected_intent.value,
                    "actual_intent": analysis.intent_type.value,
                    "expected_strategy": expected_strategy.value,
                    "actual_strategy": analysis.response_strategy.value,
                    "confidence": analysis.confidence,
                    "intent_match": intent_match,
                    "strategy_match": strategy_match,
                    "overall_match": intent_match and strategy_match
                })
                
            except Exception as e:
                print(f"❌ Error testing '{text}': {e}")
                results.append({
                    "text": text,
                    "error": str(e),
                    "overall_match": False
                })
        
        # Calculate success rate
        successful = sum(1 for r in results if r.get('overall_match', False))
        total = len(results)
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        print(f"📊 Intent Recognition Results: {successful}/{total} ({success_rate:.1f}%)")
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing intent system: {e}")
        return []

async def test_enhanced_response_handler():
    """Test the enhanced response handler"""
    print("\n🧪 Testing Enhanced Response Handler")
    print("=" * 50)
    
    try:
        from enhanced_intent_system import analyze_user_intent_enhanced
        from enhanced_response_handler import handle_enhanced_response
        
        test_queries = [
            "BTC price",
            "Tell me about Uniswap",
            "Best yield opportunities",
            "Hello",
            "Help",
            "What's the price of ethereum?",
        ]
        
        results = []
        
        for query in test_queries:
            try:
                print(f"🔍 Testing: '{query}'")
                
                # Analyze intent
                analysis = await analyze_user_intent_enhanced(query, 12345)
                print(f"   Intent: {analysis.intent_type.value} (confidence: {analysis.confidence:.2f})")
                print(f"   Strategy: {analysis.response_strategy.value}")
                
                # Get response
                response = await handle_enhanced_response(analysis, query, 12345)
                
                print(f"   Response Type: {response.get('type', 'unknown')}")
                message = response.get('message', '')
                if len(message) > 100:
                    message = message[:100] + "..."
                print(f"   Message: {message}")
                print()
                
                results.append({
                    "query": query,
                    "intent": analysis.intent_type.value,
                    "strategy": analysis.response_strategy.value,
                    "confidence": analysis.confidence,
                    "response_type": response.get('type'),
                    "has_message": bool(response.get('message')),
                    "success": response.get('type') != 'error'
                })
                
            except Exception as e:
                print(f"❌ Error testing '{query}': {e}")
                results.append({
                    "query": query,
                    "error": str(e),
                    "success": False
                })
        
        # Calculate success rate
        successful = sum(1 for r in results if r.get('success', False))
        total = len(results)
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        print(f"📊 Response Handler Results: {successful}/{total} ({success_rate:.1f}%)")
        
        return results
        
    except Exception as e:
        print(f"❌ Error testing response handler: {e}")
        return []

async def test_live_data_integration():
    """Test live data integration"""
    print("\n🧪 Testing Live Data Integration")
    print("=" * 50)
    
    try:
        from enhanced_response_handler import enhanced_response_handler
        
        # Test crypto price fetching
        print("🔍 Testing crypto price fetching...")
        price_entities = {'symbol': 'bitcoin', 'normalized_symbol': 'bitcoin'}
        price_response = await enhanced_response_handler._fetch_crypto_price(price_entities)
        
        print(f"   Price Response Type: {price_response.get('type')}")
        if price_response.get('type') == 'price_data':
            data = price_response.get('data', {})
            print(f"   Symbol: {data.get('symbol')}")
            print(f"   Price: ${data.get('price', 0):,.4f}")
            print(f"   24h Change: {data.get('change_24h', 0):+.2f}%")
        
        # Test DeFi protocol data
        print("\n🔍 Testing DeFi protocol data...")
        defi_entities = {'protocol': 'uniswap', 'is_known_protocol': True}
        defi_response = await enhanced_response_handler._fetch_defi_protocol_data(defi_entities)
        
        print(f"   DeFi Response Type: {defi_response.get('type')}")
        if defi_response.get('message'):
            message = defi_response.get('message', '')
            if len(message) > 200:
                message = message[:200] + "..."
            print(f"   Message: {message}")
        
        # Test yield opportunities
        print("\n🔍 Testing yield opportunities...")
        yield_response = await enhanced_response_handler._fetch_yield_opportunities("best yields")
        
        print(f"   Yield Response Type: {yield_response.get('type')}")
        if yield_response.get('message'):
            message = yield_response.get('message', '')
            if len(message) > 200:
                message = message[:200] + "..."
            print(f"   Message: {message}")
        
        return {
            "price_test": price_response.get('type') == 'price_data',
            "defi_test": defi_response.get('type') in ['defi_protocol', 'defi_search'],
            "yield_test": yield_response.get('type') in ['yield_opportunities', 'error']
        }
        
    except Exception as e:
        print(f"❌ Error testing live data integration: {e}")
        return {}

async def test_defillama_api():
    """Test DeFiLlama API integration"""
    print("\n🧪 Testing DeFiLlama API")
    print("=" * 50)
    
    try:
        from defillama_api import defillama_api
        
        # Test protocols
        print("🔍 Testing protocols...")
        protocols = await defillama_api.get_protocols()
        if protocols:
            print(f"   ✅ Got {len(protocols)} protocols")
            if len(protocols) > 0:
                sample = protocols[0]
                print(f"   Sample: {sample.get('name', 'Unknown')} - TVL: ${sample.get('tvl', 0):,.0f}")
        else:
            print("   ❌ No protocols data")
        
        # Test top protocols
        print("\n🔍 Testing top protocols...")
        top_protocols = await defillama_api.get_top_protocols(5)
        if top_protocols:
            print(f"   ✅ Got {len(top_protocols)} top protocols")
            for i, protocol in enumerate(top_protocols[:3], 1):
                name = protocol.get('name', 'Unknown')
                tvl = protocol.get('tvl', 0)
                print(f"   {i}. {name}: ${tvl:,.0f}")
        else:
            print("   ❌ No top protocols data")
        
        # Test search
        print("\n🔍 Testing protocol search...")
        search_results = await defillama_api.search_protocols("uniswap")
        if search_results:
            print(f"   ✅ Found {len(search_results)} results for 'uniswap'")
            if len(search_results) > 0:
                result = search_results[0]
                print(f"   Top result: {result.get('name', 'Unknown')}")
        else:
            print("   ❌ No search results")
        
        return {
            "protocols": bool(protocols),
            "top_protocols": bool(top_protocols),
            "search": bool(search_results)
        }
        
    except Exception as e:
        print(f"❌ Error testing DeFiLlama API: {e}")
        return {}

async def main():
    """Run all tests"""
    print("🚀 Starting Enhanced System Tests")
    print("=" * 60)
    
    # Test results
    test_results = {}
    
    # Test intent system
    intent_results = await test_enhanced_intent_system()
    test_results['intent_system'] = intent_results
    
    # Test response handler
    response_results = await test_enhanced_response_handler()
    test_results['response_handler'] = response_results
    
    # Test live data integration
    data_results = await test_live_data_integration()
    test_results['live_data'] = data_results
    
    # Test DeFiLlama API
    api_results = await test_defillama_api()
    test_results['defillama_api'] = api_results
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    
    if intent_results:
        intent_success = sum(1 for r in intent_results if r.get('overall_match', False))
        intent_total = len(intent_results)
        print(f"Intent Recognition: {intent_success}/{intent_total} ({(intent_success/intent_total)*100:.1f}%)")
    
    if response_results:
        response_success = sum(1 for r in response_results if r.get('success', False))
        response_total = len(response_results)
        print(f"Response Handler: {response_success}/{response_total} ({(response_success/response_total)*100:.1f}%)")
    
    if data_results:
        data_success = sum(1 for v in data_results.values() if v)
        data_total = len(data_results)
        print(f"Live Data Integration: {data_success}/{data_total} ({(data_success/data_total)*100:.1f}%)")
    
    if api_results:
        api_success = sum(1 for v in api_results.values() if v)
        api_total = len(api_results)
        print(f"DeFiLlama API: {api_success}/{api_total} ({(api_success/api_total)*100:.1f}%)")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"enhanced_system_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    print("\n✅ Enhanced system testing completed!")

if __name__ == "__main__":
    asyncio.run(main())