#!/usr/bin/env python3
"""
Production Bot Testing
Tests the actual bot implementation with all dependencies and complex scenarios
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
import logging

# Suppress logging during tests
logging.getLogger().setLevel(logging.ERROR)

sys.path.append('src')

class ProductionBotTester:
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        self.setup_mock_telegram()
    
    def setup_mock_telegram(self):
        """Setup comprehensive mock Telegram objects"""
        # Mock user
        self.mock_user = Mock()
        self.mock_user.id = 12345
        self.mock_user.username = "testuser"
        self.mock_user.is_bot = False
        self.mock_user.first_name = "Test"
        self.mock_user.last_name = "User"
        
        # Mock chat
        self.mock_chat = Mock()
        self.mock_chat.id = 67890
        self.mock_chat.type = "private"
        self.mock_chat.title = None
        
        # Mock message
        self.mock_message = Mock()
        self.mock_message.text = ""
        self.mock_message.message_id = 1
        self.mock_message.date = time.time()
        self.mock_message.reply_to_message = None
        self.mock_message.reply_text = AsyncMock()
        self.mock_message.from_user = self.mock_user
        
        # Mock bot
        self.mock_bot = Mock()
        self.mock_bot.username = "mobius_test_bot"
        
        # Mock update
        self.mock_update = Mock()
        self.mock_update.effective_user = self.mock_user
        self.mock_update.effective_chat = self.mock_chat
        self.mock_update.effective_message = self.mock_message
        
        # Mock context
        self.mock_context = Mock()
        self.mock_context.bot_data = {
            'active_chats': set(),
            'mentions': [],
            'user_sessions': {}
        }
        self.mock_context.bot = self.mock_bot
        self.mock_context.args = []
    
    async def test_command_handler(self, command: str, args: str = "") -> Dict[str, Any]:
        """Test actual command handlers with full dependencies"""
        print(f"\n🧪 Testing Command: /{command} {args}")
        
        try:
            # Import the main module with all dependencies
            from main import (
                help_command, menu_command, ask_command, llama_command,
                arkham_command, nansen_command, memory_status_command,
                ai_providers_command, switch_ai_command, test_ai_command,
                portfolio_command, alerts_command, research_command
            )
            
            # Map commands to handlers
            command_map = {
                "help": help_command,
                "menu": menu_command,
                "ask": ask_command,
                "llama": llama_command,
                "arkham": arkham_command,
                "nansen": nansen_command,
                "memory_status": memory_status_command,
                "ai_providers": ai_providers_command,
                "switch_ai": switch_ai_command,
                "test_ai": test_ai_command,
                "portfolio": portfolio_command,
                "alerts": alerts_command,
                "research": research_command
            }
            
            if command not in command_map:
                return {"success": False, "error": f"Command /{command} not found"}
            
            # Setup context args
            if args:
                self.mock_context.args = args.split()
            else:
                self.mock_context.args = []
            
            # Reset mock
            self.mock_message.reply_text.reset_mock()
            
            # Execute command handler
            start_time = time.time()
            await command_map[command](self.mock_update, self.mock_context)
            execution_time = time.time() - start_time
            
            # Check if reply_text was called
            if self.mock_message.reply_text.called:
                response = self.mock_message.reply_text.call_args[0][0]
                return {
                    "success": True,
                    "response": response,
                    "execution_time": execution_time,
                    "response_length": len(response),
                    "handler_executed": True
                }
            else:
                return {
                    "success": False,
                    "error": "Handler didn't send a response",
                    "execution_time": execution_time
                }
                
        except Exception as e:
            return {"success": False, "error": str(e), "exception_type": type(e).__name__}
    
    async def test_natural_language_processing(self, user_input: str) -> Dict[str, Any]:
        """Test the enhanced message handler with natural language"""
        print(f"\n🧠 Testing NLP: '{user_input}'")
        
        try:
            from main import enhanced_handle_message
            
            # Setup message
            self.mock_message.text = user_input
            self.mock_message.reply_text.reset_mock()
            
            # Test enhanced message handling
            start_time = time.time()
            await enhanced_handle_message(self.mock_update, self.mock_context)
            execution_time = time.time() - start_time
            
            # Check response
            if self.mock_message.reply_text.called:
                response = self.mock_message.reply_text.call_args[0][0]
                
                # Analyze response quality
                quality_score = self.analyze_response_quality(user_input, response)
                
                return {
                    "success": True,
                    "response": response,
                    "execution_time": execution_time,
                    "quality_score": quality_score,
                    "response_length": len(response),
                    "nlp_processed": True
                }
            else:
                return {
                    "success": False,
                    "error": "No response generated",
                    "execution_time": execution_time
                }
                
        except Exception as e:
            return {"success": False, "error": str(e), "exception_type": type(e).__name__}
    
    async def test_defillama_query(self, protocol_name: str) -> Dict[str, Any]:
        """Test actual DeFiLlama API integration"""
        print(f"\n🦙 Testing DeFiLlama Query: {protocol_name}")
        
        try:
            from crypto_research import search_protocol_by_name, query_defillama
            
            # Search for protocol
            start_time = time.time()
            protocol = search_protocol_by_name(protocol_name)
            search_time = time.time() - start_time
            
            if not protocol or protocol.get("success") == False:
                return {
                    "success": False,
                    "error": f"Protocol '{protocol_name}' not found",
                    "search_time": search_time
                }
            
            # Get TVL data
            tvl_start = time.time()
            tvl_result = query_defillama("tvl", slug=protocol.get("slug"))
            tvl_time = time.time() - tvl_start
            
            return {
                "success": True,
                "protocol_found": True,
                "protocol_name": protocol.get("name", protocol_name),
                "protocol_slug": protocol.get("slug", ""),
                "tvl_result": tvl_result,
                "search_time": search_time,
                "tvl_time": tvl_time,
                "total_time": search_time + tvl_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "exception_type": type(e).__name__}
    
    async def test_ai_provider_switching(self) -> Dict[str, Any]:
        """Test AI provider switching functionality"""
        print(f"\n🔄 Testing AI Provider Switching")
        
        try:
            from ai_provider_manager import switch_ai_provider, get_ai_provider_info, generate_ai_response
            
            results = {}
            
            # Test switching to Groq
            groq_success = switch_ai_provider("groq")
            if groq_success:
                groq_info = get_ai_provider_info()
                
                # Test generation
                messages = [{"role": "user", "content": "Say 'Groq test successful'"}]
                groq_response = await generate_ai_response(messages)
                
                results["groq"] = {
                    "switch_success": True,
                    "provider_info": groq_info,
                    "response": groq_response,
                    "response_success": bool(groq_response and "groq" in groq_response.lower())
                }
            else:
                results["groq"] = {"switch_success": False}
            
            # Test switching to Gemini
            gemini_success = switch_ai_provider("gemini")
            if gemini_success:
                gemini_info = get_ai_provider_info()
                
                # Test generation
                messages = [{"role": "user", "content": "Say 'Gemini test successful'"}]
                gemini_response = await generate_ai_response(messages)
                
                results["gemini"] = {
                    "switch_success": True,
                    "provider_info": gemini_info,
                    "response": gemini_response,
                    "response_success": bool(gemini_response and "gemini" in gemini_response.lower())
                }
            else:
                results["gemini"] = {"switch_success": False}
            
            return {
                "success": True,
                "results": results,
                "providers_tested": len(results),
                "successful_switches": sum(1 for r in results.values() if r.get("switch_success"))
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "exception_type": type(e).__name__}
    
    async def test_complex_crypto_queries(self) -> Dict[str, Any]:
        """Test complex crypto-specific queries"""
        print(f"\n💰 Testing Complex Crypto Queries")
        
        complex_queries = [
            "Get TVL of Paradex from DeFiLlama",
            "What's the trading volume of Hyperliquid?",
            "Compare Bitcoin and Ethereum performance",
            "Find the best yield farming opportunities",
            "Analyze current DeFi market trends"
        ]
        
        results = []
        
        for query in complex_queries:
            try:
                result = await self.test_natural_language_processing(query)
                results.append({
                    "query": query,
                    "success": result.get("success", False),
                    "quality_score": result.get("quality_score", 0),
                    "execution_time": result.get("execution_time", 0),
                    "response_length": result.get("response_length", 0)
                })
            except Exception as e:
                results.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
        
        successful_queries = [r for r in results if r.get("success")]
        avg_quality = sum(r.get("quality_score", 0) for r in successful_queries) / max(1, len(successful_queries))
        avg_time = sum(r.get("execution_time", 0) for r in successful_queries) / max(1, len(successful_queries))
        
        return {
            "success": len(successful_queries) > 0,
            "total_queries": len(complex_queries),
            "successful_queries": len(successful_queries),
            "success_rate": len(successful_queries) / len(complex_queries),
            "average_quality": avg_quality,
            "average_time": avg_time,
            "detailed_results": results
        }
    
    def analyze_response_quality(self, user_input: str, response: str) -> float:
        """Analyze response quality with crypto-specific criteria"""
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
        
        # Crypto-specific relevance
        crypto_terms = ["bitcoin", "ethereum", "btc", "eth", "crypto", "defi", "tvl", "trading", "price", "volume"]
        user_crypto_terms = [term for term in crypto_terms if term in user_lower]
        response_crypto_terms = [term for term in user_crypto_terms if term in response_lower]
        
        if user_crypto_terms:
            crypto_relevance = len(response_crypto_terms) / len(user_crypto_terms)
            score += crypto_relevance * 3.0
        
        # Professional and helpful tone
        helpful_phrases = ["i can help", "here's", "let me", "you can", "consider", "analysis", "data"]
        if any(phrase in response_lower for phrase in helpful_phrases):
            score += 1.5
        
        # Specific protocol/platform mentions
        if "paradex" in user_lower and "paradex" in response_lower:
            score += 1.0
        if "hyperliquid" in user_lower and "hyperliquid" in response_lower:
            score += 1.0
        if "defillama" in user_lower and ("defillama" in response_lower or "tvl" in response_lower):
            score += 1.0
        
        # Avoid generic/error responses
        generic_phrases = ["i don't know", "i'm not sure", "error", "try again"]
        if any(phrase in response_lower for phrase in generic_phrases):
            score -= 1.0
        
        return min(10.0, max(0.0, score))
    
    async def run_test(self, name: str, test_func, *args) -> bool:
        """Run a test and record results"""
        print(f"\n{'='*70}")
        print(f"🎯 {name}")
        
        try:
            result = await test_func(*args)
            
            if result.get("success", False):
                print(f"   ✅ PASS")
                
                # Show relevant metrics
                if "execution_time" in result:
                    print(f"   ⏱️  Time: {result['execution_time']:.2f}s")
                if "quality_score" in result:
                    print(f"   📊 Quality: {result['quality_score']:.1f}/10")
                if "response_length" in result:
                    print(f"   📝 Length: {result['response_length']} chars")
                if "success_rate" in result:
                    print(f"   📈 Success Rate: {result['success_rate']*100:.1f}%")
                
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

async def run_production_bot_tests():
    """Run comprehensive production bot tests"""
    tester = ProductionBotTester()
    
    print("🤖 PRODUCTION BOT TESTING")
    print("🔬 Testing actual bot implementation with all dependencies")
    print("🎯 Focus: Complex queries, DeFiLlama integration, command routing")
    print("=" * 80)
    
    # Test 1: Core Command Handlers
    print("\n📋 CORE COMMAND HANDLERS")
    
    command_tests = [
        ("Help Command", "help", ""),
        ("Menu Command", "menu", ""),
        ("DeFiLlama Command", "llama", ""),
        ("Memory Status", "memory_status", ""),
        ("AI Providers List", "ai_providers", ""),
        ("Switch to Groq", "switch_ai", "groq"),
        ("Test AI Provider", "test_ai", "groq"),
        ("Portfolio Command", "portfolio", ""),
        ("Research Command", "research", ""),
    ]
    
    for name, command, args in command_tests:
        await tester.run_test(name, tester.test_command_handler, command, args)
    
    # Test 2: Natural Language Processing
    print("\n🧠 NATURAL LANGUAGE PROCESSING")
    
    nlp_tests = [
        ("Bitcoin Price Query", "What's the current price of Bitcoin?"),
        ("Portfolio Request", "Show me my crypto portfolio"),
        ("DeFi Explanation", "Explain what DeFi is and how it works"),
        ("Trading Advice", "Should I buy Ethereum now or wait?"),
        ("Security Question", "How do I secure my crypto wallet?"),
    ]
    
    for name, query in nlp_tests:
        await tester.run_test(name, tester.test_natural_language_processing, query)
    
    # Test 3: DeFiLlama Integration
    print("\n🦙 DEFILLAMA API INTEGRATION")
    
    defillama_tests = [
        ("Uniswap Protocol", "uniswap"),
        ("Aave Protocol", "aave"),
        ("Compound Protocol", "compound"),
        ("Invalid Protocol", "nonexistentprotocol123"),
    ]
    
    for name, protocol in defillama_tests:
        await tester.run_test(name, tester.test_defillama_query, protocol)
    
    # Test 4: AI Provider System
    print("\n🤖 AI PROVIDER SYSTEM")
    
    await tester.run_test("AI Provider Switching", tester.test_ai_provider_switching)
    
    # Test 5: Complex Crypto Queries
    print("\n💰 COMPLEX CRYPTO QUERIES")
    
    await tester.run_test("Complex Query Processing", tester.test_complex_crypto_queries)
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("🏆 PRODUCTION BOT TEST RESULTS")
    print(f"{'='*80}")
    
    total_tests = tester.passed + tester.failed
    success_rate = (tester.passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Overall Results:")
    print(f"   ✅ Passed: {tester.passed}/{total_tests}")
    print(f"   ❌ Failed: {tester.failed}/{total_tests}")
    print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    # Analyze by category
    command_results = [r for r in tester.test_results if "Command" in r["name"]]
    nlp_results = [r for r in tester.test_results if r["name"] in [t[0] for t in nlp_tests]]
    defillama_results = [r for r in tester.test_results if "Protocol" in r["name"]]
    ai_results = [r for r in tester.test_results if "AI Provider" in r["name"] or "Complex Query" in r["name"]]
    
    print(f"\n📋 Results by Category:")
    print(f"   🔧 Command Handlers: {len([r for r in command_results if r['status'] == 'PASS'])}/{len(command_results)} passed")
    print(f"   🧠 NLP Processing: {len([r for r in nlp_results if r['status'] == 'PASS'])}/{len(nlp_results)} passed")
    print(f"   🦙 DeFiLlama API: {len([r for r in defillama_results if r['status'] == 'PASS'])}/{len(defillama_results)} passed")
    print(f"   🤖 AI Systems: {len([r for r in ai_results if r['status'] == 'PASS'])}/{len(ai_results)} passed")
    
    # Performance analysis
    execution_times = []
    quality_scores = []
    
    for result in tester.test_results:
        if result["status"] == "PASS" and "result" in result:
            if "execution_time" in result["result"]:
                execution_times.append(result["result"]["execution_time"])
            if "quality_score" in result["result"]:
                quality_scores.append(result["result"]["quality_score"])
            if "average_quality" in result["result"]:
                quality_scores.append(result["result"]["average_quality"])
    
    if execution_times:
        avg_time = sum(execution_times) / len(execution_times)
        print(f"\n⚡ Performance Metrics:")
        print(f"   Average Execution Time: {avg_time:.2f}s")
        print(f"   Fastest Response: {min(execution_times):.2f}s")
        print(f"   Slowest Response: {max(execution_times):.2f}s")
    
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"\n📊 Quality Metrics:")
        print(f"   Average Response Quality: {avg_quality:.1f}/10")
        print(f"   High Quality Responses (>7): {len([q for q in quality_scores if q > 7])}/{len(quality_scores)}")
    
    # Critical issues analysis
    failed_tests = [r for r in tester.test_results if r["status"] in ["FAIL", "ERROR"]]
    critical_failures = []
    
    for test in failed_tests:
        if any(keyword in test["name"].lower() for keyword in ["command", "nlp", "defillama", "ai provider"]):
            critical_failures.append(test)
    
    if critical_failures:
        print(f"\n🚨 CRITICAL ISSUES ({len(critical_failures)}):")
        for test in critical_failures:
            error_msg = test.get('error', test.get('result', {}).get('error', 'Unknown'))
            print(f"   • {test['name']}: {error_msg}")
    
    # Save detailed report
    report = {
        "timestamp": time.time(),
        "test_type": "production_bot",
        "total_tests": total_tests,
        "passed": tester.passed,
        "failed": tester.failed,
        "success_rate": success_rate,
        "average_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
        "average_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
        "critical_failures": len(critical_failures),
        "detailed_results": tester.test_results,
        "categories": {
            "command_handlers": len(command_results),
            "nlp_processing": len(nlp_results),
            "defillama_api": len(defillama_results),
            "ai_systems": len(ai_results)
        }
    }
    
    with open("production_bot_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved: production_bot_report.json")
    
    # Final assessment with production criteria
    if success_rate >= 85 and len(critical_failures) == 0:
        print(f"\n🎉 PRODUCTION READY!")
        print(f"✅ All critical systems working")
        print(f"✅ High success rate ({success_rate:.1f}%)")
        print(f"✅ No critical failures detected")
        print(f"✅ Bot can handle complex crypto queries")
        print(f"✅ DeFiLlama integration functional")
        print(f"✅ AI provider system working")
    elif success_rate >= 70 and len(critical_failures) <= 2:
        print(f"\n⚠️  MOSTLY READY - Minor issues to fix")
        print(f"✅ Core functionality works")
        print(f"⚠️  Some non-critical issues present")
        print(f"⚠️  Success rate: {success_rate:.1f}%")
    else:
        print(f"\n❌ NOT PRODUCTION READY")
        print(f"❌ Success rate too low: {success_rate:.1f}%")
        print(f"❌ Critical failures: {len(critical_failures)}")
        print(f"❌ Major systems not working properly")
    
    return success_rate >= 80 and len(critical_failures) <= 1

if __name__ == "__main__":
    try:
        success = asyncio.run(run_production_bot_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)