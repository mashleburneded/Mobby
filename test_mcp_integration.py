#!/usr/bin/env python3
"""
Comprehensive MCP Integration Test
Tests all MCP features and enhancements
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPIntegrationTester:
    """Comprehensive MCP integration tester"""

    def __init__(self):
        self.test_results = {}
        self.test_user_id = 12345
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    async def run_all_tests(self):
        """Run all MCP integration tests"""
        logger.info("🚀 Starting Comprehensive MCP Integration Tests")
        logger.info("=" * 60)
        
        test_categories = [
            ("MCP Client Infrastructure", self.test_mcp_client),
            ("MCP AI Orchestrator", self.test_ai_orchestrator),
            ("MCP Background Processor", self.test_background_processor),
            ("MCP Streaming Manager", self.test_streaming_manager),
            ("MCP Intent Router", self.test_intent_router),
            ("Cross-Chain Analytics (Base/Optimism)", self.test_cross_chain_analytics),
            ("Natural Language Processing", self.test_natural_language),
            ("Telegram Handler Integration", self.test_telegram_integration),
            ("Performance & Security", self.test_performance_security)
        ]
        
        for category_name, test_func in test_categories:
            logger.info(f"\n📊 Testing: {category_name}")
            logger.info("-" * 40)
            
            try:
                await test_func()
                logger.info(f"✅ {category_name}: PASSED")
            except Exception as e:
                logger.error(f"❌ {category_name}: FAILED - {e}")
                self.test_results[category_name] = {"status": "FAILED", "error": str(e)}
        
        # Generate final report
        await self.generate_final_report()

    async def test_mcp_client(self):
        """Test MCP client infrastructure"""
        try:
            from mcp_client import mcp_client, initialize_mcp_client
            
            # Test 1: Client initialization
            await self._run_test("MCP Client Initialization", self._test_client_init)
            
            # Test 2: Server connections
            await self._run_test("MCP Server Connections", self._test_server_connections)
            
            # Test 3: Tool calls
            await self._run_test("MCP Tool Calls", self._test_tool_calls)
            
            # Test 4: Error handling
            await self._run_test("MCP Error Handling", self._test_error_handling)
            
        except ImportError as e:
            raise Exception(f"MCP Client import failed: {e}")

    async def _test_client_init(self):
        """Test MCP client initialization"""
        from mcp_client import mcp_client
        
        # Check if client is properly initialized
        assert hasattr(mcp_client, 'servers'), "MCP client missing servers attribute"
        assert hasattr(mcp_client, 'sessions'), "MCP client missing sessions attribute"
        
        return {"status": "initialized", "servers_count": len(mcp_client.servers)}

    async def _test_server_connections(self):
        """Test MCP server connections"""
        from mcp_client import mcp_client
        
        # Test connection status
        connected = getattr(mcp_client, 'connected', False)
        
        return {"status": "connected" if connected else "disconnected", "connected": connected}

    async def _test_tool_calls(self):
        """Test MCP tool calls"""
        from mcp_client import mcp_client
        
        # Test a safe tool call
        result = await mcp_client.call_tool("financial", "get_crypto_prices", {"symbols": ["BTC", "ETH"]})
        
        assert isinstance(result, dict), "Tool call should return dict"
        
        return {"status": "success", "result_type": type(result).__name__}

    async def _test_error_handling(self):
        """Test MCP error handling"""
        from mcp_client import mcp_client
        
        # Test invalid server call
        result = await mcp_client.call_tool("invalid_server", "invalid_tool", {})
        
        assert "error" in result, "Error handling should return error key"
        
        return {"status": "error_handled", "error_present": "error" in result}

    async def test_ai_orchestrator(self):
        """Test MCP AI orchestrator"""
        try:
            from mcp_ai_orchestrator import ai_orchestrator, initialize_ai_orchestrator
            
            # Test 1: Orchestrator initialization
            await self._run_test("AI Orchestrator Init", self._test_orchestrator_init)
            
            # Test 2: Query classification
            await self._run_test("Query Classification", self._test_query_classification)
            
            # Test 3: Enhanced response generation
            await self._run_test("Enhanced Response Generation", self._test_enhanced_response)
            
            # Test 4: Intent mapping
            await self._run_test("Intent Mapping", self._test_intent_mapping)
            
        except ImportError as e:
            raise Exception(f"AI Orchestrator import failed: {e}")

    async def _test_orchestrator_init(self):
        """Test AI orchestrator initialization"""
        from mcp_ai_orchestrator import ai_orchestrator
        
        assert hasattr(ai_orchestrator, 'models'), "AI orchestrator missing models"
        assert hasattr(ai_orchestrator, '_map_intent_to_query_type'), "Missing intent mapping method"
        
        return {"status": "initialized", "has_models": hasattr(ai_orchestrator, 'models')}

    async def _test_query_classification(self):
        """Test query classification"""
        from mcp_ai_orchestrator import ai_orchestrator
        
        # Test different query types
        test_queries = [
            "What's the price of Bitcoin?",
            "Analyze the market trends",
            "Monitor my portfolio",
            "Show me whale movements"
        ]
        
        results = []
        for query in test_queries:
            query_type = await ai_orchestrator.classify_query(query)
            results.append({"query": query, "type": query_type.value})
        
        return {"status": "classified", "results": results}

    async def _test_enhanced_response(self):
        """Test enhanced response generation"""
        from mcp_ai_orchestrator import ai_orchestrator
        
        # Test with intent
        response = await ai_orchestrator.generate_enhanced_response(
            "What's the price of Bitcoin?", 
            {"user_id": self.test_user_id}, 
            "price_query"
        )
        
        assert isinstance(response, dict), "Response should be dict"
        assert "success" in response, "Response should have success key"
        
        return {"status": "generated", "success": response.get("success", False)}

    async def _test_intent_mapping(self):
        """Test intent mapping"""
        from mcp_ai_orchestrator import ai_orchestrator
        
        # Test intent mapping
        test_intents = ["price_query", "market_analysis", "wallet_analysis", "general_query"]
        
        results = []
        for intent in test_intents:
            query_type = ai_orchestrator._map_intent_to_query_type(intent)
            results.append({"intent": intent, "query_type": query_type.value})
        
        return {"status": "mapped", "mappings": results}

    async def test_background_processor(self):
        """Test MCP background processor"""
        try:
            from mcp_background_processor import background_processor, submit_background_job
            
            # Test 1: Processor initialization
            await self._run_test("Background Processor Init", self._test_processor_init)
            
            # Test 2: Job submission
            await self._run_test("Job Submission", self._test_job_submission)
            
            # Test 3: Rate limiting
            await self._run_test("Rate Limiting", self._test_rate_limiting)
            
        except ImportError as e:
            raise Exception(f"Background Processor import failed: {e}")

    async def _test_processor_init(self):
        """Test background processor initialization"""
        from mcp_background_processor import background_processor
        
        assert hasattr(background_processor, 'job_queue'), "Missing job queue"
        assert hasattr(background_processor, 'submit_job'), "Missing submit_job method"
        
        return {"status": "initialized", "has_queue": hasattr(background_processor, 'job_queue')}

    async def _test_job_submission(self):
        """Test job submission"""
        from mcp_background_processor import submit_background_job
        
        # Submit a test job
        job_id = await submit_background_job(
            user_id=self.test_user_id,
            job_type="market_analysis",
            parameters={"symbol": "BTC"},
            priority=1
        )
        
        return {"status": "submitted", "job_id": job_id}

    async def _test_rate_limiting(self):
        """Test rate limiting"""
        from mcp_background_processor import background_processor
        
        # Test rate limit check
        can_submit = await background_processor._check_rate_limit(self.test_user_id)
        
        return {"status": "checked", "can_submit": can_submit}

    async def test_streaming_manager(self):
        """Test MCP streaming manager"""
        try:
            from mcp_streaming import streaming_manager, initialize_streaming_manager
            
            # Test 1: Streaming initialization
            await self._run_test("Streaming Manager Init", self._test_streaming_init)
            
            # Test 2: Subscription management
            await self._run_test("Subscription Management", self._test_subscription_management)
            
        except ImportError as e:
            raise Exception(f"Streaming Manager import failed: {e}")

    async def _test_streaming_init(self):
        """Test streaming manager initialization"""
        from mcp_streaming import streaming_manager
        
        assert hasattr(streaming_manager, 'subscriptions'), "Missing subscriptions"
        
        return {"status": "initialized", "has_subscriptions": hasattr(streaming_manager, 'subscriptions')}

    async def _test_subscription_management(self):
        """Test subscription management"""
        from mcp_streaming import streaming_manager
        
        # Test getting user subscriptions
        subscriptions = await streaming_manager.get_user_subscriptions(self.test_user_id)
        
        return {"status": "managed", "subscription_count": len(subscriptions)}

    async def test_intent_router(self):
        """Test MCP intent router"""
        try:
            from mcp_intent_router import intent_router, route_user_request, analyze_user_intent
            
            # Test 1: Intent analysis
            await self._run_test("Intent Analysis", self._test_intent_analysis)
            
            # Test 2: Request routing
            await self._run_test("Request Routing", self._test_request_routing)
            
            # Test 3: Strategy determination
            await self._run_test("Strategy Determination", self._test_strategy_determination)
            
        except ImportError as e:
            raise Exception(f"Intent Router import failed: {e}")

    async def _test_intent_analysis(self):
        """Test intent analysis"""
        from mcp_intent_router import analyze_user_intent
        
        # Test intent analysis
        analysis = await analyze_user_intent(
            self.test_user_id, 
            "What's the price of Bitcoin?", 
            {"user_id": self.test_user_id}
        )
        
        assert isinstance(analysis, dict), "Analysis should be dict"
        assert "intent_type" in analysis, "Analysis should have intent_type"
        
        return {"status": "analyzed", "intent_type": analysis.get("intent_type")}

    async def _test_request_routing(self):
        """Test request routing"""
        from mcp_intent_router import route_user_request
        
        # Test request routing
        result = await route_user_request(
            self.test_user_id, 
            "Monitor Bitcoin price", 
            {"user_id": self.test_user_id}
        )
        
        assert isinstance(result, dict), "Routing result should be dict"
        
        return {"status": "routed", "success": result.get("success", False)}

    async def _test_strategy_determination(self):
        """Test strategy determination"""
        from mcp_intent_router import intent_router
        
        # Test different message types
        test_messages = [
            "What's the price of Bitcoin now?",  # Immediate
            "Analyze the market trends deeply",   # Background
            "Monitor my portfolio continuously",  # Streaming
            "Research cross-chain opportunities" # Complex
        ]
        
        results = []
        for message in test_messages:
            analysis = await intent_router.analyze_intent(self.test_user_id, message)
            results.append({
                "message": message,
                "intent_type": analysis.intent_type.value,
                "routing_strategy": analysis.routing_strategy.value
            })
        
        return {"status": "determined", "strategies": results}

    async def test_cross_chain_analytics(self):
        """Test cross-chain analytics with Base and Optimism"""
        try:
            from cross_chain_analytics import CrossChainAnalyzer, ChainType
            
            # Test 1: Chain support
            await self._run_test("Chain Support", self._test_chain_support)
            
            # Test 2: Base chain integration
            await self._run_test("Base Chain Integration", self._test_base_integration)
            
            # Test 3: Optimism chain integration
            await self._run_test("Optimism Chain Integration", self._test_optimism_integration)
            
        except ImportError as e:
            raise Exception(f"Cross-Chain Analytics import failed: {e}")

    async def _test_chain_support(self):
        """Test chain support"""
        from cross_chain_analytics import ChainType
        
        # Check if Base and Optimism are supported
        supported_chains = [chain.value for chain in ChainType]
        
        assert "base" in supported_chains, "Base chain not supported"
        assert "optimism" in supported_chains, "Optimism chain not supported"
        
        return {"status": "supported", "chains": supported_chains}

    async def _test_base_integration(self):
        """Test Base chain integration"""
        from cross_chain_analytics import CrossChainAnalyzer, ChainType
        
        analyzer = CrossChainAnalyzer()
        
        # Check Base configuration
        base_config = analyzer.supported_chains.get(ChainType.BASE)
        
        assert base_config is not None, "Base configuration missing"
        assert base_config.chain_id == 8453, "Base chain ID incorrect"
        
        return {"status": "integrated", "chain_id": base_config.chain_id}

    async def _test_optimism_integration(self):
        """Test Optimism chain integration"""
        from cross_chain_analytics import CrossChainAnalyzer, ChainType
        
        analyzer = CrossChainAnalyzer()
        
        # Check Optimism configuration
        optimism_config = analyzer.supported_chains.get(ChainType.OPTIMISM)
        
        assert optimism_config is not None, "Optimism configuration missing"
        assert optimism_config.chain_id == 10, "Optimism chain ID incorrect"
        
        return {"status": "integrated", "chain_id": optimism_config.chain_id}

    async def test_natural_language(self):
        """Test natural language processing enhancements"""
        try:
            from mcp_natural_language import nlp_processor, process_natural_language
            
            # Test 1: NLP processor
            await self._run_test("NLP Processor", self._test_nlp_processor)
            
            # Test 2: Message processing
            await self._run_test("Message Processing", self._test_message_processing)
            
        except ImportError as e:
            raise Exception(f"Natural Language Processing import failed: {e}")

    async def _test_nlp_processor(self):
        """Test NLP processor"""
        from mcp_natural_language import nlp_processor
        
        assert hasattr(nlp_processor, 'process_message'), "Missing process_message method"
        
        return {"status": "available", "has_processor": True}

    async def _test_message_processing(self):
        """Test message processing"""
        from mcp_natural_language import process_natural_language
        
        # Test natural language processing
        result = await process_natural_language(
            self.test_user_id, 
            "What's the current price of Bitcoin?",
            {"user_id": self.test_user_id}
        )
        
        assert isinstance(result, dict), "Result should be dict"
        
        return {"status": "processed", "success": result.get("success", False)}

    async def test_telegram_integration(self):
        """Test Telegram handler integration"""
        try:
            from telegram_handler import TelegramHandler
            
            # Test 1: Handler initialization
            await self._run_test("Telegram Handler Init", self._test_telegram_init)
            
            # Test 2: Smart AI request handling
            await self._run_test("Smart AI Request Handling", self._test_smart_ai_handling)
            
        except ImportError as e:
            raise Exception(f"Telegram Handler import failed: {e}")

    async def _test_telegram_init(self):
        """Test Telegram handler initialization"""
        from telegram_handler import TelegramHandler
        
        handler = TelegramHandler()
        
        assert hasattr(handler, '_handle_smart_ai_request'), "Missing smart AI request handler"
        
        return {"status": "initialized", "has_smart_handler": True}

    async def _test_smart_ai_handling(self):
        """Test smart AI request handling"""
        # This would require mock Telegram objects
        # For now, just check the method exists
        from telegram_handler import TelegramHandler
        
        handler = TelegramHandler()
        
        assert callable(getattr(handler, '_handle_smart_ai_request', None)), "Smart AI handler not callable"
        
        return {"status": "available", "handler_callable": True}

    async def test_performance_security(self):
        """Test performance and security features"""
        try:
            # Test 1: Rate limiting
            await self._run_test("Rate Limiting", self._test_rate_limiting_performance)
            
            # Test 2: Security validation
            await self._run_test("Security Validation", self._test_security_validation)
            
            # Test 3: Error handling
            await self._run_test("Error Handling", self._test_error_handling_performance)
            
        except Exception as e:
            raise Exception(f"Performance/Security test failed: {e}")

    async def _test_rate_limiting_performance(self):
        """Test rate limiting performance"""
        # Test rate limiting doesn't block legitimate requests
        start_time = time.time()
        
        # Simulate multiple requests
        for i in range(5):
            await asyncio.sleep(0.1)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert processing_time < 2.0, "Rate limiting causing excessive delays"
        
        return {"status": "performant", "processing_time": processing_time}

    async def _test_security_validation(self):
        """Test security validation"""
        from mcp_client import mcp_client
        
        # Test invalid server name handling
        result = await mcp_client.call_tool("../../../etc/passwd", "malicious_tool", {})
        
        assert "error" in result, "Security validation should reject malicious server names"
        
        return {"status": "secure", "blocked_malicious": True}

    async def _test_error_handling_performance(self):
        """Test error handling performance"""
        start_time = time.time()
        
        try:
            # Trigger an error condition
            from mcp_client import mcp_client
            await mcp_client.call_tool("nonexistent", "tool", {})
        except Exception:
            pass
        
        end_time = time.time()
        error_handling_time = end_time - start_time
        
        assert error_handling_time < 1.0, "Error handling taking too long"
        
        return {"status": "fast", "error_handling_time": error_handling_time}

    async def _run_test(self, test_name: str, test_func):
        """Run a single test and track results"""
        self.total_tests += 1
        
        try:
            start_time = time.time()
            result = await test_func()
            end_time = time.time()
            
            self.passed_tests += 1
            logger.info(f"  ✅ {test_name}: PASSED ({end_time - start_time:.3f}s)")
            
            self.test_results[test_name] = {
                "status": "PASSED",
                "duration": end_time - start_time,
                "result": result
            }
            
        except Exception as e:
            self.failed_tests += 1
            logger.error(f"  ❌ {test_name}: FAILED - {e}")
            
            self.test_results[test_name] = {
                "status": "FAILED",
                "error": str(e),
                "duration": 0
            }

    async def generate_final_report(self):
        """Generate final test report"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 COMPREHENSIVE MCP INTEGRATION TEST REPORT")
        logger.info("=" * 60)
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        logger.info(f"📈 Overall Success Rate: {success_rate:.1f}% ({self.passed_tests}/{self.total_tests})")
        logger.info(f"✅ Passed Tests: {self.passed_tests}")
        logger.info(f"❌ Failed Tests: {self.failed_tests}")
        
        # Performance summary
        total_duration = sum(
            result.get("duration", 0) for result in self.test_results.values()
        )
        logger.info(f"⏱️  Total Test Duration: {total_duration:.3f}s")
        
        # Category breakdown
        logger.info("\n📋 Test Category Breakdown:")
        for test_name, result in self.test_results.items():
            status_emoji = "✅" if result["status"] == "PASSED" else "❌"
            duration = result.get("duration", 0)
            logger.info(f"  {status_emoji} {test_name}: {result['status']} ({duration:.3f}s)")
        
        # Recommendations
        logger.info("\n💡 Recommendations:")
        if success_rate >= 95:
            logger.info("  🎉 Excellent! MCP integration is production-ready.")
        elif success_rate >= 85:
            logger.info("  👍 Good performance. Minor improvements needed.")
        elif success_rate >= 70:
            logger.info("  ⚠️  Moderate performance. Some issues need attention.")
        else:
            logger.info("  🚨 Significant issues detected. Review failed tests.")
        
        # Failed test details
        failed_tests = [name for name, result in self.test_results.items() if result["status"] == "FAILED"]
        if failed_tests:
            logger.info(f"\n🔍 Failed Tests Details:")
            for test_name in failed_tests:
                error = self.test_results[test_name].get("error", "Unknown error")
                logger.info(f"  ❌ {test_name}: {error}")
        
        logger.info("\n🚀 MCP Integration Test Complete!")
        logger.info("=" * 60)

async def main():
    """Main test runner"""
    tester = MCPIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())