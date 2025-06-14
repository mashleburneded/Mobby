#!/usr/bin/env python3
"""
Test Enhanced Bot with Real Telegram Integration
Tests the enhanced intent system with actual bot functionality
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_enhanced_message_processing():
    """Test enhanced message processing without full Telegram setup"""
    print("🧪 Testing Enhanced Message Processing")
    print("=" * 50)
    
    try:
        from enhanced_intent_system import analyze_user_intent_enhanced
        from enhanced_response_handler import handle_enhanced_response
        
        # Test cases that should work well
        test_messages = [
            "BTC price",
            "What's the price of ethereum?",
            "Tell me about Uniswap",
            "Hello",
            "Help me",
            "Best yield opportunities",
            "Show my portfolio",
            "Set an alert for BTC",
        ]
        
        results = []
        
        for message in test_messages:
            print(f"\n🔍 Processing: '{message}'")
            
            try:
                # Analyze intent
                analysis = await analyze_user_intent_enhanced(message, 12345)
                print(f"   Intent: {analysis.intent_type.value}")
                print(f"   Strategy: {analysis.response_strategy.value}")
                print(f"   Confidence: {analysis.confidence:.2f}")
                print(f"   Entities: {analysis.extracted_entities}")
                
                # Generate response
                response = await handle_enhanced_response(analysis, message, 12345)
                print(f"   Response Type: {response.get('type', 'unknown')}")
                
                # Show response message (truncated)
                message_text = response.get('message', '')
                if message_text:
                    if len(message_text) > 150:
                        message_text = message_text[:150] + "..."
                    print(f"   Response: {message_text}")
                
                results.append({
                    "message": message,
                    "intent": analysis.intent_type.value,
                    "strategy": analysis.response_strategy.value,
                    "confidence": analysis.confidence,
                    "response_type": response.get('type'),
                    "success": response.get('type') != 'error'
                })
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append({
                    "message": message,
                    "error": str(e),
                    "success": False
                })
        
        # Summary
        successful = sum(1 for r in results if r.get('success', False))
        total = len(results)
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        print(f"\n📊 Processing Results: {successful}/{total} ({success_rate:.1f}%)")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in enhanced message processing test: {e}")
        return []

async def test_real_data_fetching():
    """Test real data fetching capabilities"""
    print("\n🧪 Testing Real Data Fetching")
    print("=" * 50)
    
    try:
        from enhanced_response_handler import enhanced_response_handler
        
        # Test crypto price fetching
        print("🔍 Testing Bitcoin price...")
        btc_entities = {'symbol': 'btc', 'normalized_symbol': 'bitcoin'}
        btc_response = await enhanced_response_handler._fetch_crypto_price(btc_entities)
        
        if btc_response.get('type') == 'price_data':
            data = btc_response.get('data', {})
            print(f"   ✅ Bitcoin: ${data.get('price', 0):,.2f} ({data.get('change_24h', 0):+.2f}%)")
        else:
            print(f"   ❌ Bitcoin price fetch failed: {btc_response.get('message', 'Unknown error')}")
        
        # Test Ethereum price
        print("\n🔍 Testing Ethereum price...")
        eth_entities = {'symbol': 'ethereum', 'normalized_symbol': 'ethereum'}
        eth_response = await enhanced_response_handler._fetch_crypto_price(eth_entities)
        
        if eth_response.get('type') == 'price_data':
            data = eth_response.get('data', {})
            print(f"   ✅ Ethereum: ${data.get('price', 0):,.2f} ({data.get('change_24h', 0):+.2f}%)")
        else:
            print(f"   ❌ Ethereum price fetch failed: {eth_response.get('message', 'Unknown error')}")
        
        # Test DeFi protocol data
        print("\n🔍 Testing DeFi protocol data...")
        try:
            from defillama_api import defillama_api
            protocols = await defillama_api.get_protocols()
            
            if protocols and len(protocols) > 0:
                print(f"   ✅ DeFiLlama API working: {len(protocols)} protocols available")
                
                # Test top protocols
                top_protocols = await defillama_api.get_top_protocols(3)
                if top_protocols:
                    print("   Top 3 DeFi Protocols:")
                    for i, protocol in enumerate(top_protocols, 1):
                        name = protocol.get('name', 'Unknown')
                        tvl = protocol.get('tvl', 0) or 0
                        print(f"   {i}. {name}: ${tvl:,.0f}")
                
            else:
                print("   ❌ No protocols data available")
                
        except Exception as e:
            print(f"   ❌ DeFiLlama API error: {e}")
        
        return {
            "btc_price": btc_response.get('type') == 'price_data',
            "eth_price": eth_response.get('type') == 'price_data',
            "defillama_api": bool(protocols) if 'protocols' in locals() else False
        }
        
    except Exception as e:
        print(f"❌ Error in real data fetching test: {e}")
        return {}

async def test_intent_accuracy():
    """Test intent recognition accuracy with edge cases"""
    print("\n🧪 Testing Intent Recognition Accuracy")
    print("=" * 50)
    
    try:
        from enhanced_intent_system import analyze_user_intent_enhanced, IntentType
        
        # Test cases with expected intents
        test_cases = [
            # Crypto prices - should be high confidence
            ("bitcoin price", IntentType.CRYPTO_PRICE),
            ("what's BTC worth", IntentType.CRYPTO_PRICE),
            ("ETH cost", IntentType.CRYPTO_PRICE),
            
            # DeFi protocols - should be recognized
            ("tell me about uniswap", IntentType.DEFI_PROTOCOL),
            ("aave protocol info", IntentType.DEFI_PROTOCOL),
            ("compound stats", IntentType.DEFI_PROTOCOL),
            
            # Yield farming
            ("best yields", IntentType.YIELD_FARMING),
            ("high apy opportunities", IntentType.YIELD_FARMING),
            
            # Greetings
            ("hello", IntentType.GREETING),
            ("hi", IntentType.GREETING),
            
            # Help
            ("help", IntentType.HELP_REQUEST),
            ("what can you do", IntentType.HELP_REQUEST),
            
            # Portfolio
            ("my portfolio", IntentType.PORTFOLIO_CHECK),
            ("show balance", IntentType.PORTFOLIO_CHECK),
        ]
        
        correct = 0
        total = len(test_cases)
        
        for text, expected_intent in test_cases:
            analysis = await analyze_user_intent_enhanced(text, 12345)
            is_correct = analysis.intent_type == expected_intent
            
            status = "✅" if is_correct else "❌"
            print(f"{status} '{text}' -> {analysis.intent_type.value} (expected: {expected_intent.value})")
            
            if is_correct:
                correct += 1
        
        accuracy = (correct / total) * 100
        print(f"\n📊 Intent Accuracy: {correct}/{total} ({accuracy:.1f}%)")
        
        return accuracy
        
    except Exception as e:
        print(f"❌ Error in intent accuracy test: {e}")
        return 0

async def main():
    """Run all enhanced bot tests"""
    print("🚀 Starting Enhanced Bot Tests")
    print("=" * 60)
    
    # Test enhanced message processing
    processing_results = await test_enhanced_message_processing()
    
    # Test real data fetching
    data_results = await test_real_data_fetching()
    
    # Test intent accuracy
    intent_accuracy = await test_intent_accuracy()
    
    # Overall summary
    print("\n📊 Overall Test Summary")
    print("=" * 60)
    
    if processing_results:
        processing_success = sum(1 for r in processing_results if r.get('success', False))
        processing_total = len(processing_results)
        print(f"Message Processing: {processing_success}/{processing_total} ({(processing_success/processing_total)*100:.1f}%)")
    
    if data_results:
        data_success = sum(1 for v in data_results.values() if v)
        data_total = len(data_results)
        print(f"Real Data Fetching: {data_success}/{data_total} ({(data_success/data_total)*100:.1f}%)")
    
    print(f"Intent Recognition Accuracy: {intent_accuracy:.1f}%")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if intent_accuracy >= 90:
        print("✅ Intent recognition is excellent!")
    elif intent_accuracy >= 80:
        print("⚠️  Intent recognition is good but could be improved")
    else:
        print("❌ Intent recognition needs significant improvement")
    
    if data_results and data_results.get('btc_price') and data_results.get('eth_price'):
        print("✅ Crypto price fetching is working well!")
    else:
        print("❌ Crypto price fetching needs attention")
    
    if data_results and data_results.get('defillama_api'):
        print("✅ DeFiLlama integration is working!")
    else:
        print("❌ DeFiLlama integration needs fixing")
    
    print("\n✅ Enhanced bot testing completed!")

if __name__ == "__main__":
    asyncio.run(main())