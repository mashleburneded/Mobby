#!/usr/bin/env python3
"""
Real Bot Scenario Testing
Tests actual command routing, intent mapping, and complex query handling
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock

sys.path.append('src')

class RealBotTester:
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        self.setup_mock_telegram()
    
    def setup_mock_telegram(self):
        """Setup mock Telegram objects for testing"""
        self.mock_update = Mock()
        self.mock_context = Mock()
        
        # Mock user
        self.mock_user = Mock()
        self.mock_user.id = 12345
        self.mock_user.username = "testuser"
        self.mock_user.is_bot = False
        
        # Mock chat
        self.mock_chat = Mock()
        self.mock_chat.id = 67890
        self.mock_chat.type = "private"
        
        # Mock message
        self.mock_message = Mock()
        self.mock_message.text = ""
        self.mock_message.message_id = 1
        self.mock_message.date = time.time()
        self.mock_message.reply_to_message = None
        self.mock_message.reply_text = AsyncMock()
        
        # Setup update structure
        self.mock_update.effective_user = self.mock_user
        self.mock_update.effective_chat = self.mock_chat
        self.mock_update.effective_message = self.mock_message
        
        # Setup context
        self.mock_context.bot_data = {}
        self.mock_context.bot = Mock()
        self.mock_context.bot.username = "mobius_test_bot"
    
    async def test_command_routing(self, command: str, args: str = "") -> Dict[str, Any]:
        """Test if commands are properly routed to handlers"""
        print(f"\n🧪 Testing Command: /{command} {args}")
        
        try:
            # Import main module to get command handlers
            from main import (
                help_command, menu_command, ask_command, llama_command,
                arkham_command, nansen_command, memory_status_command,
                ai_providers_command, switch_ai_command
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
                "switch_ai": switch_ai_command
            }
            
            if command not in command_map:
                return {"success": False, "error": f"Command /{command} not found in handlers"}
            
            # Setup context args
            if args:
                self.mock_context.args = args.split()
            else:
                self.mock_context.args = []
            
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
                    "handler_found": True
                }
            else:
                return {
                    "success": False,
                    "error": "Handler didn't send a response",
                    "execution_time": execution_time
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_intent_recognition(self, user_input: str) -> Dict[str, Any]:
        """Test intent recognition and routing"""
        print(f"\n🧠 Testing Intent: '{user_input}'")
        
        try:
            from agent_memory_database import analyze_user_intent, get_conversation_flow
            from main import process_ai_response
            
            # Test intent analysis
            intent, confidence = analyze_user_intent(user_input)
            
            # Get conversation flow
            flow = get_conversation_flow(intent)
            
            # Test AI response processing
            start_time = time.time()
            response = await process_ai_response(user_input, 12345, "testuser")
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "intent": intent,
                "confidence": confidence,
                "flow_found": bool(flow),
                "response": response,
                "execution_time": execution_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_complex_query_handling(self, query: str, expected_type: str) -> Dict[str, Any]:
        """Test complex queries that should trigger specific handlers"""
        print(f"\n🔍 Testing Complex Query: '{query}'")
        print(f"   Expected Type: {expected_type}")
        
        try:
            # Test if the query gets routed correctly
            from main import enhanced_handle_message
            
            # Setup message
            self.mock_message.text = query
            
            # Test enhanced message handling
            start_time = time.time()
            await enhanced_handle_message(self.mock_update, self.mock_context)
            execution_time = time.time() - start_time
            
            # Check response
            if self.mock_message.reply_text.called:
                response = self.mock_message.reply_text.call_args[0][0]
                
                # Analyze response quality
                quality_score = self.analyze_response_quality(query, response, expected_type)
                
                return {
                    "success": True,
                    "response": response,
                    "execution_time": execution_time,
                    "quality_score": quality_score,
                    "response_length": len(response)
                }
            else:
                return {
                    "success": False,
                    "error": "No response generated",
                    "execution_time": execution_time
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_response_quality(self, query: str, response: str, expected_type: str) -> float:
        """Analyze the quality of the response"""
        score = 0.0
        
        # Basic checks
        if len(response) > 20:
            score += 2.0
        
        # Check for relevant keywords based on expected type
        query_lower = query.lower()
        response_lower = response.lower()
        
        if expected_type == "defi_protocol":
            if any(word in response_lower for word in ["tvl", "protocol", "defi", "liquidity"]):
                score += 3.0
            if "paradex" in query_lower and "paradex" in response_lower:
                score += 2.0
        
        elif expected_type == "trading_volume":
            if any(word in response_lower for word in ["volume", "trading", "24h", "daily"]):
                score += 3.0
            if "hyperliquid" in query_lower and "hyperliquid" in response_lower:
                score += 2.0
        
        elif expected_type == "price_query":
            if any(word in response_lower for word in ["price", "$", "usd", "value"]):
                score += 3.0
        
        elif expected_type == "portfolio":
            if any(word in response_lower for word in ["portfolio", "holdings", "balance"]):
                score += 3.0
        
        # Check for helpful tone
        if any(phrase in response_lower for phrase in ["i can help", "let me", "here's", "you can"]):
            score += 1.0
        
        # Check for error handling
        if "error" in response_lower or "sorry" in response_lower:
            if "try again" in response_lower or "rephrase" in response_lower:
                score += 1.0  # Good error handling
            else:
                score -= 1.0  # Poor error handling
        
        return min(10.0, score)
    
    async def test_scenario(self, name: str, test_func, *args) -> bool:
        """Run a test scenario and record results"""
        print(f"\n{'='*60}")
        print(f"🎯 {name}")
        
        try:
            result = await test_func(*args)
            
            if result.get("success", False):
                print(f"   ✅ PASS")
                if "response" in result:
                    print(f"   📝 Response: {result['response'][:100]}...")
                if "execution_time" in result:
                    print(f"   ⏱️  Time: {result['execution_time']:.2f}s")
                if "quality_score" in result:
                    print(f"   📊 Quality: {result['quality_score']:.1f}/10")
                
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

async def run_real_bot_tests():
    """Run comprehensive real bot scenario tests"""
    tester = RealBotTester()
    
    print("🤖 REAL BOT SCENARIO TESTING")
    print("🔬 Testing actual command routing, intent mapping, and complex queries")
    print("=" * 80)
    
    # Test 1: Command Routing
    print("\n📋 COMMAND ROUTING TESTS")
    
    command_tests = [
        ("Help Command", "help", ""),
        ("Menu Command", "menu", ""),
        ("DeFiLlama Command", "llama", ""),
        ("Arkham Command", "arkham", ""),
        ("Memory Status", "memory_status", ""),
        ("AI Providers", "ai_providers", ""),
        ("Switch AI Provider", "switch_ai", "groq"),
    ]
    
    for name, command, args in command_tests:
        await tester.test_scenario(name, tester.test_command_routing, command, args)
    
    # Test 2: Intent Recognition
    print("\n🧠 INTENT RECOGNITION TESTS")
    
    intent_tests = [
        ("Bitcoin Price Query", "What's the price of Bitcoin?"),
        ("Portfolio Request", "Show me my crypto portfolio"),
        ("Price Alert Setup", "Set an alert for ETH at $4000"),
        ("DeFi Question", "What is DeFi?"),
        ("Trading Advice", "Should I buy Bitcoin now?"),
    ]
    
    for name, query in intent_tests:
        await tester.test_scenario(name, tester.test_intent_recognition, query)
    
    # Test 3: Complex Query Handling
    print("\n🔍 COMPLEX QUERY HANDLING TESTS")
    
    complex_tests = [
        ("DeFi Protocol TVL Query", "Get TVL of Paradex from DeFiLlama", "defi_protocol"),
        ("Trading Volume Query", "What's the trading volume of Hyperliquid?", "trading_volume"),
        ("Multi-part Crypto Query", "Compare Bitcoin and Ethereum prices and tell me which has better potential", "price_query"),
        ("Portfolio Analysis", "Analyze my crypto portfolio performance", "portfolio"),
        ("Market Trend Analysis", "What's the current market trend for altcoins?", "market_analysis"),
        ("Yield Farming Query", "Find the best yield farming opportunities on Ethereum", "defi_protocol"),
        ("Wallet Security", "How do I secure my crypto wallet from hackers?", "security_advice"),
        ("Error Handling Test", "Show me the price of INVALIDCOIN123", "error_handling"),
    ]
    
    for name, query, expected_type in complex_tests:
        await tester.test_scenario(name, tester.test_complex_query_handling, query, expected_type)
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("🏆 REAL BOT TEST RESULTS")
    print(f"{'='*80}")
    
    total_tests = tester.passed + tester.failed
    success_rate = (tester.passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Overall Results:")
    print(f"   ✅ Passed: {tester.passed}/{total_tests}")
    print(f"   ❌ Failed: {tester.failed}/{total_tests}")
    print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    # Analyze by category
    command_results = [r for r in tester.test_results if "Command" in r["name"]]
    intent_results = [r for r in tester.test_results if r["name"] in [t[0] for t in intent_tests]]
    complex_results = [r for r in tester.test_results if r["name"] in [t[0] for t in complex_tests]]
    
    print(f"\n📋 Results by Category:")
    print(f"   🔧 Command Routing: {len([r for r in command_results if r['status'] == 'PASS'])}/{len(command_results)} passed")
    print(f"   🧠 Intent Recognition: {len([r for r in intent_results if r['status'] == 'PASS'])}/{len(intent_results)} passed")
    print(f"   🔍 Complex Queries: {len([r for r in complex_results if r['status'] == 'PASS'])}/{len(complex_results)} passed")
    
    # Identify issues
    failed_tests = [r for r in tester.test_results if r["status"] in ["FAIL", "ERROR"]]
    if failed_tests:
        print(f"\n❌ Issues Found ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   • {test['name']}: {test.get('error', test.get('result', {}).get('error', 'Unknown'))}")
    
    # Save detailed report
    report = {
        "timestamp": time.time(),
        "total_tests": total_tests,
        "passed": tester.passed,
        "failed": tester.failed,
        "success_rate": success_rate,
        "detailed_results": tester.test_results,
        "categories": {
            "command_routing": len(command_results),
            "intent_recognition": len(intent_results),
            "complex_queries": len(complex_results)
        }
    }
    
    with open("real_bot_test_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved: real_bot_test_report.json")
    
    # Final assessment
    if success_rate >= 80:
        print(f"\n🎉 EXCELLENT! Bot is handling real scenarios well")
        print(f"✅ Commands are properly routed")
        print(f"✅ Intent recognition is working")
        print(f"✅ Complex queries are handled appropriately")
    elif success_rate >= 60:
        print(f"\n⚠️  GOOD but needs improvement")
        print(f"✅ Basic functionality works")
        print(f"⚠️  Some complex scenarios need better handling")
    else:
        print(f"\n❌ NEEDS SIGNIFICANT WORK")
        print(f"❌ Many scenarios are failing")
        print(f"❌ Command routing or intent recognition issues")
    
    return success_rate >= 70

if __name__ == "__main__":
    try:
        success = asyncio.run(run_real_bot_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)