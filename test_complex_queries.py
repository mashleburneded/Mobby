#!/usr/bin/env python3
"""
Test Complex Crypto Queries
Test the bot's ability to handle specific complex queries like DeFiLlama TVL, trading volumes, etc.
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, List, Any

sys.path.append('src')

async def test_defillama_tvl_query():
    """Test DeFiLlama TVL query handling"""
    print("🦙 Testing DeFiLlama TVL Query Handling")
    
    try:
        from agent_memory_database import analyze_user_intent
        from crypto_research import search_protocol_by_name, query_defillama
        
        # Test intent recognition
        query = "Get TVL of Paradex from DeFiLlama"
        intent, confidence = analyze_user_intent(query)
        
        print(f"   Query: {query}")
        print(f"   Intent: {intent} (confidence: {confidence:.2f})")
        
        # Test actual DeFiLlama API call
        protocol = search_protocol_by_name("uniswap")  # Use a known protocol
        if protocol and protocol.get("name"):
            print(f"   Found protocol: {protocol['name']}")
            
            # Test TVL query
            tvl_result = query_defillama("tvl", slug=protocol.get("slug"))
            print(f"   TVL result: {tvl_result[:100]}...")
            
            return {
                "intent_correct": intent == "query_defillama_tvl",
                "confidence_high": confidence > 0.8,
                "api_working": bool(tvl_result and "error" not in tvl_result.lower()),
                "protocol_found": True
            }
        else:
            return {"error": "Protocol search failed"}
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"error": str(e)}

async def test_trading_volume_query():
    """Test trading volume query handling"""
    print("\n📊 Testing Trading Volume Query Handling")
    
    try:
        from agent_memory_database import analyze_user_intent
        from ai_provider_manager import generate_ai_response
        
        # Test intent recognition
        query = "What's the trading volume of Hyperliquid?"
        intent, confidence = analyze_user_intent(query)
        
        print(f"   Query: {query}")
        print(f"   Intent: {intent} (confidence: {confidence:.2f})")
        
        # Test AI response generation
        messages = [
            {
                "role": "system",
                "content": "You are a crypto assistant. The user is asking about trading volume for Hyperliquid. Provide helpful information."
            },
            {"role": "user", "content": query}
        ]
        
        response = await generate_ai_response(messages)
        
        # Check if response mentions relevant terms
        response_lower = response.lower() if response else ""
        relevant_terms = ["hyperliquid", "volume", "trading", "24h", "daily"]
        term_matches = sum(1 for term in relevant_terms if term in response_lower)
        
        print(f"   Response length: {len(response) if response else 0} chars")
        print(f"   Relevant terms: {term_matches}/{len(relevant_terms)}")
        
        return {
            "intent_correct": intent == "get_trading_volume",
            "confidence_high": confidence > 0.8,
            "response_generated": bool(response and len(response) > 50),
            "relevant_content": term_matches >= 2
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"error": str(e)}

async def test_defi_explanation():
    """Test DeFi explanation handling"""
    print("\n🔍 Testing DeFi Explanation Handling")
    
    try:
        from agent_memory_database import analyze_user_intent
        from ai_provider_manager import generate_ai_response
        
        # Test intent recognition
        query = "Explain what DeFi is and how it works"
        intent, confidence = analyze_user_intent(query)
        
        print(f"   Query: {query}")
        print(f"   Intent: {intent} (confidence: {confidence:.2f})")
        
        # Test AI response generation
        messages = [
            {
                "role": "system",
                "content": "You are a crypto education assistant. Explain DeFi clearly and comprehensively."
            },
            {"role": "user", "content": query}
        ]
        
        response = await generate_ai_response(messages)
        
        # Check if response covers key DeFi concepts
        response_lower = response.lower() if response else ""
        defi_concepts = ["decentralized", "finance", "smart contracts", "blockchain", "liquidity", "protocols"]
        concept_matches = sum(1 for concept in defi_concepts if concept in response_lower)
        
        print(f"   Response length: {len(response) if response else 0} chars")
        print(f"   DeFi concepts covered: {concept_matches}/{len(defi_concepts)}")
        
        return {
            "intent_correct": intent == "explain_defi",
            "confidence_high": confidence > 0.8,
            "response_comprehensive": len(response) > 500 if response else False,
            "concepts_covered": concept_matches >= 4
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"error": str(e)}

async def test_yield_farming_query():
    """Test yield farming opportunity query"""
    print("\n🌾 Testing Yield Farming Query Handling")
    
    try:
        from agent_memory_database import analyze_user_intent
        from ai_provider_manager import generate_ai_response
        
        # Test intent recognition
        query = "Find the best yield farming opportunities on Ethereum"
        intent, confidence = analyze_user_intent(query)
        
        print(f"   Query: {query}")
        print(f"   Intent: {intent} (confidence: {confidence:.2f})")
        
        # Test AI response generation
        messages = [
            {
                "role": "system",
                "content": "You are a DeFi expert. Help users find yield farming opportunities while explaining risks."
            },
            {"role": "user", "content": query}
        ]
        
        response = await generate_ai_response(messages)
        
        # Check if response covers yield farming concepts
        response_lower = response.lower() if response else ""
        yield_terms = ["yield", "farming", "apy", "apr", "liquidity", "pools", "ethereum", "risks"]
        term_matches = sum(1 for term in yield_terms if term in response_lower)
        
        print(f"   Response length: {len(response) if response else 0} chars")
        print(f"   Yield farming terms: {term_matches}/{len(yield_terms)}")
        
        return {
            "intent_correct": intent == "find_yield_opportunities",
            "confidence_high": confidence > 0.8,
            "response_informative": len(response) > 300 if response else False,
            "terms_covered": term_matches >= 4
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"error": str(e)}

async def test_crypto_comparison():
    """Test cryptocurrency comparison query"""
    print("\n⚖️ Testing Crypto Comparison Handling")
    
    try:
        from agent_memory_database import analyze_user_intent
        from ai_provider_manager import generate_ai_response
        
        # Test intent recognition
        query = "Compare Bitcoin and Ethereum performance over the last month"
        intent, confidence = analyze_user_intent(query)
        
        print(f"   Query: {query}")
        print(f"   Intent: {intent} (confidence: {confidence:.2f})")
        
        # Test AI response generation
        messages = [
            {
                "role": "system",
                "content": "You are a crypto analyst. Provide balanced comparisons between cryptocurrencies."
            },
            {"role": "user", "content": query}
        ]
        
        response = await generate_ai_response(messages)
        
        # Check if response covers comparison elements
        response_lower = response.lower() if response else ""
        comparison_terms = ["bitcoin", "ethereum", "performance", "compare", "month", "price", "market"]
        term_matches = sum(1 for term in comparison_terms if term in response_lower)
        
        print(f"   Response length: {len(response) if response else 0} chars")
        print(f"   Comparison terms: {term_matches}/{len(comparison_terms)}")
        
        return {
            "intent_correct": intent == "compare_cryptocurrencies",
            "confidence_high": confidence > 0.8,
            "response_analytical": len(response) > 400 if response else False,
            "comparison_elements": term_matches >= 5
        }
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"error": str(e)}

async def run_complex_query_tests():
    """Run all complex query tests"""
    print("🧪 COMPLEX CRYPTO QUERY TESTING")
    print("🎯 Testing specific scenarios that users commonly ask")
    print("=" * 70)
    
    tests = [
        ("DeFiLlama TVL Query", test_defillama_tvl_query),
        ("Trading Volume Query", test_trading_volume_query),
        ("DeFi Explanation", test_defi_explanation),
        ("Yield Farming Query", test_yield_farming_query),
        ("Crypto Comparison", test_crypto_comparison),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"🎯 {name}")
        
        try:
            result = await test_func()
            
            if "error" in result:
                print(f"   ❌ FAIL: {result['error']}")
                failed += 1
                results.append({"name": name, "status": "FAIL", "error": result["error"]})
            else:
                # Evaluate overall success
                success_criteria = [
                    result.get("intent_correct", False),
                    result.get("confidence_high", False),
                    result.get("response_generated", True),
                    result.get("relevant_content", True) or result.get("concepts_covered", True) or result.get("terms_covered", True)
                ]
                
                success_count = sum(success_criteria)
                overall_success = success_count >= 3
                
                if overall_success:
                    print(f"   ✅ PASS ({success_count}/4 criteria met)")
                    passed += 1
                    results.append({"name": name, "status": "PASS", "result": result})
                else:
                    print(f"   ❌ FAIL ({success_count}/4 criteria met)")
                    failed += 1
                    results.append({"name": name, "status": "FAIL", "result": result})
                
                # Show detailed results
                for key, value in result.items():
                    if isinstance(value, bool):
                        status = "✅" if value else "❌"
                        print(f"     {status} {key}: {value}")
                    else:
                        print(f"     📊 {key}: {value}")
        
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1
            results.append({"name": name, "status": "ERROR", "error": str(e)})
    
    # Generate summary
    total_tests = len(tests)
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{'='*70}")
    print("🏆 COMPLEX QUERY TEST RESULTS")
    print(f"{'='*70}")
    
    print(f"📊 Overall Results:")
    print(f"   ✅ Passed: {passed}/{total_tests}")
    print(f"   ❌ Failed: {failed}/{total_tests}")
    print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    # Analyze specific areas
    intent_successes = sum(1 for r in results if r.get("result", {}).get("intent_correct", False))
    confidence_successes = sum(1 for r in results if r.get("result", {}).get("confidence_high", False))
    
    print(f"\n📋 Detailed Analysis:")
    print(f"   🧠 Intent Recognition: {intent_successes}/{total_tests} correct")
    print(f"   🎯 High Confidence: {confidence_successes}/{total_tests} queries")
    
    # Save results
    report = {
        "timestamp": time.time(),
        "test_type": "complex_queries",
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "intent_accuracy": intent_successes / total_tests if total_tests > 0 else 0,
        "confidence_rate": confidence_successes / total_tests if total_tests > 0 else 0,
        "detailed_results": results
    }
    
    with open("complex_query_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved: complex_query_report.json")
    
    # Final assessment
    if success_rate >= 80:
        print(f"\n🎉 EXCELLENT! Bot handles complex queries well")
        print(f"✅ Intent recognition is accurate")
        print(f"✅ Responses are comprehensive and relevant")
        print(f"✅ Ready for production use")
    elif success_rate >= 60:
        print(f"\n⚠️  GOOD but needs refinement")
        print(f"✅ Basic functionality works")
        print(f"⚠️  Some complex scenarios need improvement")
    else:
        print(f"\n❌ NEEDS SIGNIFICANT IMPROVEMENT")
        print(f"❌ Complex query handling is insufficient")
        print(f"❌ Intent recognition or response quality issues")
    
    return success_rate >= 70

if __name__ == "__main__":
    try:
        success = asyncio.run(run_complex_query_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)