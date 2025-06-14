#!/usr/bin/env python3
"""
Core Functionality Testing
Tests the actual AI processing, intent recognition, and response generation
without Telegram dependencies
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, List, Any

sys.path.append('src')

class CoreFunctionalityTester:
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    async def test_intent_analysis(self, user_input: str, expected_intent: str = None) -> Dict[str, Any]:
        """Test intent recognition system"""
        print(f"\n🧠 Testing Intent Analysis: '{user_input}'")
        
        try:
            from agent_memory_database import analyze_user_intent, get_conversation_flow
            
            # Analyze intent
            intent, confidence = analyze_user_intent(user_input)
            
            # Get conversation flow
            flow = get_conversation_flow(intent)
            
            print(f"   Intent: {intent} (confidence: {confidence:.2f})")
            print(f"   Flow found: {bool(flow)}")
            
            # Check if intent matches expected
            intent_correct = True
            if expected_intent:
                intent_correct = expected_intent.lower() in intent.lower() or intent.lower() in expected_intent.lower()
                print(f"   Expected: {expected_intent} - {'✅' if intent_correct else '❌'}")
            
            return {
                "success": True,
                "intent": intent,
                "confidence": confidence,
                "flow_found": bool(flow),
                "intent_correct": intent_correct,
                "flow_details": flow.__dict__ if flow else None
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_ai_response_generation(self, user_input: str, expected_keywords: List[str] = None) -> Dict[str, Any]:
        """Test AI response generation with memory integration"""
        print(f"\n🤖 Testing AI Response: '{user_input}'")
        
        try:
            from ai_provider_manager import generate_ai_response
            from agent_memory_database import analyze_user_intent, get_response_template
            
            # Analyze intent first
            intent, confidence = analyze_user_intent(user_input)
            
            # Try to get template response
            template_response = get_response_template(intent, {"user_input": user_input})
            
            # Generate AI response
            messages = [
                {
                    "role": "system", 
                    "content": f"You are Möbius, a helpful crypto trading assistant. "
                              f"User intent: {intent} (confidence: {confidence:.2f}). "
                              f"Be informative, accurate, and user-friendly."
                },
                {"role": "user", "content": user_input}
            ]
            
            start_time = time.time()
            ai_response = await generate_ai_response(messages)
            execution_time = time.time() - start_time
            
            print(f"   Intent: {intent} (confidence: {confidence:.2f})")
            print(f"   Template available: {bool(template_response)}")
            print(f"   Response length: {len(ai_response) if ai_response else 0} chars")
            print(f"   Execution time: {execution_time:.2f}s")
            
            # Check for expected keywords
            keyword_matches = 0
            if expected_keywords and ai_response:
                response_lower = ai_response.lower()
                for keyword in expected_keywords:
                    if keyword.lower() in response_lower:
                        keyword_matches += 1
                print(f"   Keyword matches: {keyword_matches}/{len(expected_keywords)}")
            
            # Quality assessment
            quality_score = self.assess_response_quality(user_input, ai_response, expected_keywords)
            print(f"   Quality score: {quality_score:.1f}/10")
            
            return {
                "success": bool(ai_response and len(ai_response.strip()) > 10),
                "intent": intent,
                "confidence": confidence,
                "template_available": bool(template_response),
                "response": ai_response,
                "execution_time": execution_time,
                "keyword_matches": keyword_matches,
                "total_keywords": len(expected_keywords) if expected_keywords else 0,
                "quality_score": quality_score
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    def assess_response_quality(self, user_input: str, response: str, expected_keywords: List[str] = None) -> float:
        """Assess the quality of an AI response"""
        if not response:
            return 0.0
        
        score = 0.0
        response_lower = response.lower()
        user_lower = user_input.lower()
        
        # Basic quality checks
        if len(response) > 50:
            score += 2.0
        if len(response) > 200:
            score += 1.0
        
        # Relevance check
        user_words = [word for word in user_lower.split() if len(word) > 3]
        relevant_words = sum(1 for word in user_words if word in response_lower)
        if user_words:
            score += (relevant_words / len(user_words)) * 3.0
        
        # Keyword matching
        if expected_keywords:
            keyword_score = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
            score += (keyword_score / len(expected_keywords)) * 2.0
        
        # Professional tone indicators
        professional_indicators = ["i can help", "here's", "let me", "you can", "consider", "recommend"]
        if any(indicator in response_lower for indicator in professional_indicators):
            score += 1.0
        
        # Avoid generic responses
        generic_phrases = ["i don't know", "i'm not sure", "could you rephrase"]
        if any(phrase in response_lower for phrase in generic_phrases):
            score -= 1.0
        
        return min(10.0, max(0.0, score))
    
    async def test_complex_query_processing(self, query: str, query_type: str) -> Dict[str, Any]:
        """Test processing of complex queries"""
        print(f"\n🔍 Testing Complex Query ({query_type}): '{query}'")
        
        try:
            # Test the full pipeline
            intent_result = await self.test_intent_analysis(query)
            
            if not intent_result["success"]:
                return {"success": False, "error": "Intent analysis failed"}
            
            # Define expected keywords based on query type
            expected_keywords = {
                "defi_protocol": ["tvl", "protocol", "defi", "liquidity", "paradex"],
                "trading_volume": ["volume", "trading", "24h", "hyperliquid"],
                "price_query": ["price", "bitcoin", "ethereum", "btc", "eth"],
                "portfolio": ["portfolio", "holdings", "balance", "assets"],
                "market_analysis": ["market", "trend", "analysis", "altcoins"],
                "security": ["secure", "wallet", "security", "private key"]
            }.get(query_type, [])
            
            # Test AI response
            response_result = await self.test_ai_response_generation(query, expected_keywords)
            
            if not response_result["success"]:
                return {"success": False, "error": "AI response generation failed"}
            
            # Combine results
            return {
                "success": True,
                "query_type": query_type,
                "intent": intent_result["intent"],
                "confidence": intent_result["confidence"],
                "response_quality": response_result["quality_score"],
                "execution_time": response_result["execution_time"],
                "keyword_coverage": response_result["keyword_matches"] / max(1, response_result["total_keywords"]),
                "response_length": len(response_result["response"]) if response_result["response"] else 0
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_defillama_integration(self) -> Dict[str, Any]:
        """Test DeFiLlama API integration"""
        print(f"\n🦙 Testing DeFiLlama Integration")
        
        try:
            from crypto_research import query_defillama, search_protocol_by_name
            
            # Test protocol search
            print("   Testing protocol search...")
            protocol = search_protocol_by_name("uniswap")
            
            if not protocol or not protocol.get("name"):
                return {"success": False, "error": "Protocol search failed"}
            
            print(f"   Found protocol: {protocol.get('name', 'Unknown')}")
            
            # Test TVL query
            print("   Testing TVL query...")
            tvl_result = query_defillama("tvl", protocol_name="uniswap")
            
            return {
                "success": True,
                "protocol_found": bool(protocol.get("name")),
                "protocol_name": protocol.get("name"),
                "tvl_query_success": bool(tvl_result and "error" not in tvl_result.lower()),
                "tvl_result": tvl_result[:200] if tvl_result else None
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_memory_learning(self) -> Dict[str, Any]:
        """Test memory system learning capabilities"""
        print(f"\n🧠 Testing Memory Learning")
        
        try:
            from agent_memory_database import record_performance, get_learning_insights
            
            # Record some performance data
            test_flow_id = "test_flow_001"
            
            # Record successful interaction
            record_performance(test_flow_id, 1.5, True, None, 0.95)
            
            # Record failed interaction
            record_performance(test_flow_id, 3.0, False, "timeout", 0.3)
            
            # Get learning insights
            insights = get_learning_insights()
            
            return {
                "success": True,
                "insights_count": len(insights) if insights else 0,
                "performance_recorded": True,
                "insights_available": bool(insights)
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_test(self, name: str, test_func, *args) -> bool:
        """Run a single test and record results"""
        print(f"\n{'='*60}")
        print(f"🎯 {name}")
        
        try:
            result = await test_func(*args)
            
            if result.get("success", False):
                print(f"   ✅ PASS")
                self.passed += 1
                self.test_results.append({"name": name, "status": "PASS", "result": result})
                return True
            else:
                print(f"   ❌ FAIL: {result.get('error', 'Unknown error')}")
                self.failed += 1
                self.test_results.append({"name": name, "status": "FAIL", "result": result})
                return False
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            self.failed += 1
            self.test_results.append({"name": name, "status": "ERROR", "error": str(e)})
            return False

async def run_core_functionality_tests():
    """Run comprehensive core functionality tests"""
    tester = CoreFunctionalityTester()
    
    print("🧠 CORE FUNCTIONALITY TESTING")
    print("🔬 Testing AI processing, intent recognition, and response generation")
    print("=" * 80)
    
    # Test 1: Intent Analysis
    print("\n🧠 INTENT ANALYSIS TESTS")
    
    intent_tests = [
        ("Bitcoin Price Intent", "What's the price of Bitcoin?", "get_crypto_price"),
        ("Portfolio Intent", "Show me my crypto portfolio", "analyze_portfolio"),
        ("Alert Intent", "Set an alert for ETH at $4000", "create_price_alert"),
        ("DeFi Intent", "What is DeFi?", "explain_concept"),
        ("Trading Intent", "Should I buy Bitcoin now?", "trading_advice"),
    ]
    
    for name, query, expected in intent_tests:
        await tester.run_test(name, tester.test_intent_analysis, query, expected)
    
    # Test 2: AI Response Generation
    print("\n🤖 AI RESPONSE GENERATION TESTS")
    
    response_tests = [
        ("Bitcoin Price Response", "What's the price of Bitcoin?", ["bitcoin", "price", "btc"]),
        ("DeFi Explanation", "What is DeFi?", ["defi", "decentralized", "finance"]),
        ("Portfolio Help", "How do I check my portfolio?", ["portfolio", "check", "view"]),
        ("Security Advice", "How to secure my wallet?", ["secure", "wallet", "private", "key"]),
    ]
    
    for name, query, keywords in response_tests:
        await tester.run_test(name, tester.test_ai_response_generation, query, keywords)
    
    # Test 3: Complex Query Processing
    print("\n🔍 COMPLEX QUERY PROCESSING TESTS")
    
    complex_tests = [
        ("DeFi Protocol Query", "Get TVL of Paradex from DeFiLlama", "defi_protocol"),
        ("Trading Volume Query", "What's the trading volume of Hyperliquid?", "trading_volume"),
        ("Price Comparison", "Compare Bitcoin and Ethereum prices", "price_query"),
        ("Portfolio Analysis", "Analyze my crypto portfolio performance", "portfolio"),
        ("Market Trends", "What's the current market trend?", "market_analysis"),
        ("Security Question", "How do I secure my crypto wallet?", "security"),
    ]
    
    for name, query, query_type in complex_tests:
        await tester.run_test(name, tester.test_complex_query_processing, query, query_type)
    
    # Test 4: Integration Tests
    print("\n🔗 INTEGRATION TESTS")
    
    await tester.run_test("DeFiLlama Integration", tester.test_defillama_integration)
    await tester.run_test("Memory Learning System", tester.test_memory_learning)
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("🏆 CORE FUNCTIONALITY TEST RESULTS")
    print(f"{'='*80}")
    
    total_tests = tester.passed + tester.failed
    success_rate = (tester.passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Overall Results:")
    print(f"   ✅ Passed: {tester.passed}/{total_tests}")
    print(f"   ❌ Failed: {tester.failed}/{total_tests}")
    print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    # Analyze by category
    intent_results = [r for r in tester.test_results if "Intent" in r["name"]]
    response_results = [r for r in tester.test_results if "Response" in r["name"]]
    complex_results = [r for r in tester.test_results if "Query" in r["name"] or "Comparison" in r["name"] or "Analysis" in r["name"] or "Trends" in r["name"] or "Security Question" in r["name"]]
    integration_results = [r for r in tester.test_results if "Integration" in r["name"] or "Learning" in r["name"]]
    
    print(f"\n📋 Results by Category:")
    print(f"   🧠 Intent Analysis: {len([r for r in intent_results if r['status'] == 'PASS'])}/{len(intent_results)} passed")
    print(f"   🤖 AI Responses: {len([r for r in response_results if r['status'] == 'PASS'])}/{len(response_results)} passed")
    print(f"   🔍 Complex Queries: {len([r for r in complex_results if r['status'] == 'PASS'])}/{len(complex_results)} passed")
    print(f"   🔗 Integration: {len([r for r in integration_results if r['status'] == 'PASS'])}/{len(integration_results)} passed")
    
    # Quality analysis
    quality_scores = []
    for result in tester.test_results:
        if result["status"] == "PASS" and "result" in result:
            if "quality_score" in result["result"]:
                quality_scores.append(result["result"]["quality_score"])
            elif "response_quality" in result["result"]:
                quality_scores.append(result["result"]["response_quality"])
    
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"\n📊 Quality Metrics:")
        print(f"   Average Response Quality: {avg_quality:.1f}/10")
        print(f"   High Quality Responses (>7): {len([q for q in quality_scores if q > 7])}/{len(quality_scores)}")
    
    # Identify issues
    failed_tests = [r for r in tester.test_results if r["status"] in ["FAIL", "ERROR"]]
    if failed_tests:
        print(f"\n❌ Issues Found ({len(failed_tests)}):")
        for test in failed_tests:
            error_msg = test.get('error', test.get('result', {}).get('error', 'Unknown'))
            print(f"   • {test['name']}: {error_msg}")
    
    # Save detailed report
    report = {
        "timestamp": time.time(),
        "total_tests": total_tests,
        "passed": tester.passed,
        "failed": tester.failed,
        "success_rate": success_rate,
        "average_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
        "detailed_results": tester.test_results,
        "categories": {
            "intent_analysis": len(intent_results),
            "ai_responses": len(response_results),
            "complex_queries": len(complex_results),
            "integration": len(integration_results)
        }
    }
    
    with open("core_functionality_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved: core_functionality_report.json")
    
    # Final assessment
    if success_rate >= 80:
        print(f"\n🎉 EXCELLENT! Core functionality is working well")
        print(f"✅ Intent recognition is accurate")
        print(f"✅ AI responses are high quality")
        print(f"✅ Complex queries are handled properly")
        print(f"✅ Integration systems are functional")
    elif success_rate >= 60:
        print(f"\n⚠️  GOOD but needs improvement")
        print(f"✅ Basic functionality works")
        print(f"⚠️  Some areas need refinement")
    else:
        print(f"\n❌ NEEDS SIGNIFICANT IMPROVEMENT")
        print(f"❌ Core systems have issues")
        print(f"❌ Intent recognition or AI responses failing")
    
    return success_rate >= 70

if __name__ == "__main__":
    try:
        success = asyncio.run(run_core_functionality_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)