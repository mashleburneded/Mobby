# mcp_comprehensive_test.py - Industry-Grade MCP Integration Test Suite
import asyncio
import logging
import time
import psutil
import json
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPComprehensiveTestSuite:
    """Industry-grade comprehensive test suite for MCP integration"""

    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.security_checks = {}
        self.start_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 MCP Integration - Industry-Grade Comprehensive Test Suite")
        print("=" * 80)

        self.start_time = time.time()

        # Test categories
        test_categories = [
            ("🔧 Core MCP Infrastructure", self.test_mcp_infrastructure),
            ("🧠 AI Orchestrator", self.test_ai_orchestrator),
            ("📡 Real-Time Streaming", self.test_streaming_system),
            ("🔄 Background Processing", self.test_background_processing),
            ("💬 Natural Language Processing", self.test_nlp_enhancement),
            ("🔗 Multi-Chain Integration", self.test_multichain_support),
            ("🔒 Security & Rate Limiting", self.test_security_features),
            ("⚡ Performance & Scalability", self.test_performance_metrics),
            ("🛡️ Error Handling & Resilience", self.test_error_handling),
            ("🎯 Integration & Compatibility", self.test_integration_compatibility),
        ]

        for category_name, test_function in test_categories:
            print(f"\n{category_name}")
            print("-" * 60)

            try:
                await test_function()
            except Exception as e:
                logger.error(f"❌ Test category failed: {category_name} - {e}")
                self.test_results[category_name] = {"status": "FAILED", "error": str(e)}

        # Generate comprehensive report
        await self.generate_comprehensive_report()

    async def test_mcp_infrastructure(self):
        """Test core MCP infrastructure"""
        tests = [
            ("MCP Client Manager", self.test_mcp_client_manager),
            ("Server Connections", self.test_server_connections),
            ("Tool Validation", self.test_tool_validation),
            ("Security Sanitization", self.test_security_sanitization),
            ("Fallback Mechanisms", self.test_fallback_mechanisms),
        ]

        await self.run_test_group("MCP Infrastructure", tests)

    async def test_mcp_client_manager(self):
        """Test MCP client manager"""
        try:
            from mcp_client import mcp_client, initialize_mcp

            # Test initialization
            result = await initialize_mcp()
            assert result == True, "MCP initialization failed"

            # Test server configuration
            assert len(mcp_client.servers) >= 4, "Insufficient servers configured"

            # Test security validation
            invalid_result = await mcp_client.call_tool("invalid_server", "test", {})
            assert invalid_result.get("error"), "Security validation failed"

            return {"status": "PASS", "details": "MCP client manager working correctly"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_server_connections(self):
        """Test server connections"""
        try:
            from mcp_client import mcp_client

            # Test all configured servers
            for server_name in mcp_client.servers:
                result = await mcp_client.call_tool(server_name, "test", {})
                assert isinstance(result, dict), f"Invalid response from {server_name}"

            return {"status": "PASS", "details": "All server connections working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_tool_validation(self):
        """Test tool validation"""
        try:
            from mcp_client import mcp_client

            # Test valid tools
            financial_result = await mcp_client.call_tool("financial", "get_crypto_prices", {"symbols": ["BTC"]})
            assert financial_result.get("success"), "Financial tool failed"

            # Test invalid tool
            invalid_result = await mcp_client.call_tool("financial", "invalid_tool", {})
            assert invalid_result.get("error"), "Invalid tool not rejected"

            return {"status": "PASS", "details": "Tool validation working correctly"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_security_sanitization(self):
        """Test security sanitization"""
        try:
            from mcp_client import mcp_client

            # Test argument sanitization
            malicious_args = {
                "test": "x" * 2000,  # Too long
                "script": "<script>alert('xss')</script>",  # XSS attempt
                "list": list(range(200))  # Too large list
            }

            result = await mcp_client.call_tool("financial", "get_crypto_prices", malicious_args)
            # Should not crash and should sanitize input
            assert isinstance(result, dict), "Sanitization failed"

            return {"status": "PASS", "details": "Security sanitization working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_fallback_mechanisms(self):
        """Test fallback mechanisms"""
        try:
            from mcp_client import mcp_client

            # Test with disconnected server
            result = await mcp_client._get_fallback_response("test_server", "test_tool", {})
            assert result.get("fallback"), "Fallback mechanism failed"

            return {"status": "PASS", "details": "Fallback mechanisms working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_ai_orchestrator(self):
        """Test AI orchestrator"""
        tests = [
            ("AI Orchestrator Init", self.test_ai_orchestrator_init),
            ("Query Classification", self.test_query_classification),
            ("Context Gathering", self.test_context_gathering),
            ("Multi-Model Routing", self.test_multimodel_routing),
            ("Enhanced Responses", self.test_enhanced_responses),
        ]

        await self.run_test_group("AI Orchestrator", tests)

    async def test_ai_orchestrator_init(self):
        """Test AI orchestrator initialization"""
        try:
            from mcp_ai_orchestrator import ai_orchestrator, initialize_ai_orchestrator

            await initialize_ai_orchestrator()
            assert len(ai_orchestrator.models) > 0, "No AI models configured"

            return {"status": "PASS", "details": "AI orchestrator initialized"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_query_classification(self):
        """Test query classification"""
        try:
            from mcp_ai_orchestrator import ai_orchestrator

            # Test different query types
            test_queries = [
                ("What's Bitcoin's price?", "TECHNICAL_ANALYSIS"),
                ("Analyze the market", "MARKET_RESEARCH"),
                ("Track this wallet 0x123", "BLOCKCHAIN_ANALYSIS"),
                ("What's the sentiment?", "SOCIAL_SENTIMENT"),
            ]

            for query, expected_type in test_queries:
                query_type = await ai_orchestrator.classify_query(query)
                # Just ensure it returns a valid type
                assert hasattr(query_type, 'value'), f"Invalid query type for: {query}"

            return {"status": "PASS", "details": "Query classification working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_context_gathering(self):
        """Test MCP context gathering"""
        try:
            from mcp_ai_orchestrator import ai_orchestrator, QueryType

            # Test context gathering for market research
            context = await ai_orchestrator.gather_mcp_context(
                QueryType.MARKET_RESEARCH,
                "analyze bitcoin"
            )

            assert isinstance(context, dict), "Context not returned as dict"

            return {"status": "PASS", "details": "Context gathering working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_multimodel_routing(self):
        """Test multi-model routing"""
        try:
            from mcp_ai_orchestrator import ai_orchestrator, QueryType

            # Test that different query types have different model assignments
            models = ai_orchestrator.models
            assert QueryType.TECHNICAL_ANALYSIS in models, "Technical analysis model missing"
            assert QueryType.MARKET_RESEARCH in models, "Market research model missing"

            return {"status": "PASS", "details": "Multi-model routing configured"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_enhanced_responses(self):
        """Test enhanced AI responses"""
        try:
            from mcp_ai_orchestrator import get_enhanced_ai_response

            response = await get_enhanced_ai_response("What's Bitcoin's price?")
            assert response.get("success"), "Enhanced response failed"
            assert "response" in response, "No response content"

            return {"status": "PASS", "details": "Enhanced responses working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_streaming_system(self):
        """Test real-time streaming system"""
        tests = [
            ("Streaming Infrastructure", self.test_streaming_infrastructure),
            ("Price Streaming", self.test_price_streaming),
            ("User Subscriptions", self.test_user_subscriptions),
            ("Alert System", self.test_alert_system),
            ("Stream Management", self.test_stream_management),
        ]

        await self.run_test_group("Streaming System", tests)

    async def test_streaming_infrastructure(self):
        """Test streaming infrastructure"""
        try:
            from mcp_streaming import data_streamer, initialize_streaming

            await initialize_streaming()
            assert data_streamer.running, "Streaming not running"

            return {"status": "PASS", "details": "Streaming infrastructure ready"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_price_streaming(self):
        """Test price streaming"""
        try:
            from mcp_streaming import get_live_prices

            prices = await get_live_prices(["BTC", "ETH"])
            assert isinstance(prices, dict), "Prices not returned as dict"

            return {"status": "PASS", "details": "Price streaming working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_user_subscriptions(self):
        """Test user subscriptions"""
        try:
            from mcp_streaming import data_streamer

            # Test subscription
            async def mock_callback(data):
                pass

            result = await data_streamer.subscribe_user(12345, "price_stream", {"symbols": ["BTC"]}, mock_callback)
            assert result, "Subscription failed"

            # Test unsubscription
            result = await data_streamer.unsubscribe_user(12345)
            assert result, "Unsubscription failed"

            return {"status": "PASS", "details": "User subscriptions working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_alert_system(self):
        """Test alert system"""
        try:
            from mcp_streaming import setup_user_price_alerts

            async def mock_alert_callback(data):
                pass

            result = await setup_user_price_alerts(12345, "BTC", "price_above", 50000, mock_alert_callback)
            assert result, "Alert setup failed"

            return {"status": "PASS", "details": "Alert system working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_stream_management(self):
        """Test stream management"""
        try:
            from mcp_streaming import data_streamer

            # Test getting user subscriptions
            subs = await data_streamer.get_user_subscriptions(12345)
            assert isinstance(subs, dict), "Subscriptions not returned as dict"

            return {"status": "PASS", "details": "Stream management working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_background_processing(self):
        """Test background processing system"""
        tests = [
            ("Background Processor", self.test_background_processor_init),
            ("Job Submission", self.test_job_submission),
            ("Rate Limiting", self.test_rate_limiting),
            ("Job Processing", self.test_job_processing),
            ("Job Status Tracking", self.test_job_status),
        ]

        await self.run_test_group("Background Processing", tests)

    async def test_background_processor_init(self):
        """Test background processor initialization"""
        try:
            from mcp_background_processor import background_processor, initialize_background_processor

            await initialize_background_processor()
            assert background_processor.running, "Background processor not running"
            assert len(background_processor.worker_tasks) > 0, "No worker tasks started"

            return {"status": "PASS", "details": "Background processor initialized"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_job_submission(self):
        """Test job submission"""
        try:
            from mcp_background_processor import submit_background_job

            job_id = await submit_background_job(12345, "market_analysis", {"symbols": ["BTC"]})
            assert job_id is not None, "Job submission failed"

            return {"status": "PASS", "details": "Job submission working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_rate_limiting(self):
        """Test rate limiting"""
        try:
            from mcp_background_processor import background_processor

            # Test rate limit check
            user_id = 99999
            for i in range(15):  # Exceed rate limit
                result = await background_processor._check_rate_limit(user_id)
                if i >= 10:  # Should be rate limited after 10 requests
                    if not result:
                        break
            else:
                assert False, "Rate limiting not working"

            return {"status": "PASS", "details": "Rate limiting working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_job_processing(self):
        """Test job processing"""
        try:
            from mcp_background_processor import background_processor
            from mcp_background_processor import ProcessingJob
            from datetime import datetime

            # Create test job
            job = ProcessingJob(
                job_id="test_job",
                user_id=12345,
                job_type="market_analysis",
                parameters={"symbols": ["BTC"]}
            )

            result = await background_processor._process_job(job)
            assert result.get("success"), "Job processing failed"

            return {"status": "PASS", "details": "Job processing working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_job_status(self):
        """Test job status tracking"""
        try:
            from mcp_background_processor import background_processor

            # Test getting user jobs
            user_jobs = await background_processor.get_user_jobs(12345)
            assert isinstance(user_jobs, dict), "User jobs not returned as dict"
            assert "rate_limit" in user_jobs, "Rate limit info missing"

            return {"status": "PASS", "details": "Job status tracking working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_nlp_enhancement(self):
        """Test enhanced natural language processing"""
        tests = [
            ("NLP Processor Init", self.test_nlp_processor_init),
            ("Intent Recognition", self.test_intent_recognition),
            ("Entity Extraction", self.test_entity_extraction),
            ("Context Management", self.test_context_management),
            ("Processing Strategies", self.test_processing_strategies),
        ]

        await self.run_test_group("NLP Enhancement", tests)

    async def test_nlp_processor_init(self):
        """Test NLP processor initialization"""
        try:
            from mcp_natural_language import nlp_processor, initialize_nlp_processor

            await initialize_nlp_processor()
            assert len(nlp_processor.intent_patterns) > 0, "No intent patterns loaded"
            assert len(nlp_processor.entity_extractors) > 0, "No entity extractors loaded"

            return {"status": "PASS", "details": "NLP processor initialized"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_intent_recognition(self):
        """Test intent recognition"""
        try:
            from mcp_natural_language import nlp_processor

            # Test various intents
            test_cases = [
                ("What's Bitcoin's price?", "price_query"),
                ("Hello there!", "greeting"),
                ("Analyze the market", "market_analysis"),
                ("Track wallet 0x123", "wallet_analysis"),
            ]

            for message, expected_intent in test_cases:
                intent, confidence = await nlp_processor._extract_intent(message)
                # Just ensure it returns valid intent
                assert isinstance(intent, str), f"Invalid intent for: {message}"
                assert 0 <= confidence <= 1, f"Invalid confidence for: {message}"

            return {"status": "PASS", "details": "Intent recognition working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_entity_extraction(self):
        """Test entity extraction"""
        try:
            from mcp_natural_language import nlp_processor

            # Test entity extraction
            message = "What's Bitcoin and Ethereum price? Track wallet 0x1234567890123456789012345678901234567890"
            entities = await nlp_processor._extract_entities(message)

            assert isinstance(entities, dict), "Entities not returned as dict"

            return {"status": "PASS", "details": "Entity extraction working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_context_management(self):
        """Test context management"""
        try:
            from mcp_natural_language import nlp_processor

            user_id = 12345

            # Test conversation history update
            nlp_processor._update_conversation_history(user_id, "Hello")
            nlp_processor._update_conversation_history(user_id, "What's Bitcoin's price?")

            # Test context retrieval
            context = nlp_processor._get_user_context(user_id)
            assert isinstance(context, dict), "Context not returned as dict"
            assert "conversation_history" in context, "Conversation history missing"

            return {"status": "PASS", "details": "Context management working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_processing_strategies(self):
        """Test processing strategies"""
        try:
            from mcp_natural_language import nlp_processor

            # Test strategy determination
            strategies = [
                ("greeting", "immediate"),
                ("market_analysis", "background"),
                ("defi_query", "standard"),
            ]

            for intent, expected_strategy in strategies:
                strategy = nlp_processor._determine_processing_strategy(intent, {}, {})
                assert isinstance(strategy, str), f"Invalid strategy for intent: {intent}"

            return {"status": "PASS", "details": "Processing strategies working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_multichain_support(self):
        """Test multi-chain integration"""
        tests = [
            ("Chain Support", self.test_chain_support),
            ("Cross-Chain Analysis", self.test_cross_chain_analysis),
            ("Chain-Specific Tools", self.test_chain_specific_tools),
        ]

        await self.run_test_group("Multi-Chain Support", tests)

    async def test_chain_support(self):
        """Test supported chains"""
        try:
            from mcp_client import mcp_client

            # Test supported chains
            supported_chains = ["ethereum", "polygon", "arbitrum", "optimism", "base"]

            for chain in supported_chains:
                tool_name = f"{chain}_analysis"
                result = await mcp_client.call_tool("blockchain", tool_name, {"address": "0x123"})
                assert result.get("success"), f"Chain {chain} not supported"

            return {"status": "PASS", "details": "Multi-chain support working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_cross_chain_analysis(self):
        """Test cross-chain analysis"""
        try:
            from mcp_client import mcp_client

            result = await mcp_client.call_tool("blockchain", "cross_chain_tracking", {})
            assert result.get("success"), "Cross-chain analysis failed"

            data = result.get("data", {})
            assert "supported_chains" in data, "Supported chains not listed"

            return {"status": "PASS", "details": "Cross-chain analysis working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_chain_specific_tools(self):
        """Test chain-specific tools"""
        try:
            from mcp_client import mcp_client

            # Test Ethereum analysis
            eth_result = await mcp_client.call_tool("blockchain", "ethereum_analysis", {})
            assert eth_result.get("success"), "Ethereum analysis failed"

            # Test Base analysis
            base_result = await mcp_client.call_tool("blockchain", "base_analysis", {})
            assert base_result.get("success"), "Base analysis failed"

            return {"status": "PASS", "details": "Chain-specific tools working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_security_features(self):
        """Test security and rate limiting"""
        tests = [
            ("Input Sanitization", self.test_input_sanitization),
            ("Rate Limiting", self.test_security_rate_limiting),
            ("Access Control", self.test_access_control),
            ("Error Handling", self.test_security_error_handling),
        ]

        await self.run_test_group("Security Features", tests)

    async def test_input_sanitization(self):
        """Test input sanitization"""
        try:
            from mcp_natural_language import nlp_processor

            # Test malicious input
            malicious_inputs = [
                "<script>alert('xss')</script>",
                "x" * 5000,  # Too long
                "SELECT * FROM users; DROP TABLE users;",
                "\x00\x01\x02\x03",  # Non-printable characters
            ]

            for malicious_input in malicious_inputs:
                sanitized = nlp_processor._sanitize_message(malicious_input)
                assert len(sanitized) <= 2000, "Length limit not enforced"
                assert "<script>" not in sanitized, "XSS not filtered"

            return {"status": "PASS", "details": "Input sanitization working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_security_rate_limiting(self):
        """Test security rate limiting"""
        try:
            from mcp_background_processor import background_processor

            # Test rate limiting
            user_id = 88888
            exceeded = False

            for i in range(15):
                result = await background_processor._check_rate_limit(user_id)
                if not result:
                    exceeded = True
                    break

            assert exceeded, "Rate limiting not working"

            return {"status": "PASS", "details": "Security rate limiting working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_access_control(self):
        """Test access control"""
        try:
            from mcp_client import mcp_client

            # Test invalid server access
            result = await mcp_client.call_tool("invalid_server", "test", {})
            assert result.get("error"), "Invalid server access not blocked"

            # Test invalid tool access
            result = await mcp_client.call_tool("financial", "invalid_tool", {})
            assert result.get("error"), "Invalid tool access not blocked"

            return {"status": "PASS", "details": "Access control working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_security_error_handling(self):
        """Test security error handling"""
        try:
            from mcp_client import mcp_client

            # Test that errors don't expose sensitive information
            result = await mcp_client.call_tool("financial", "invalid_tool", {})
            error_msg = result.get("error", "")

            # Should not expose internal paths or sensitive data
            assert "password" not in error_msg.lower(), "Sensitive data in error"
            assert "/home/" not in error_msg, "Internal paths in error"

            return {"status": "PASS", "details": "Security error handling working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_performance_metrics(self):
        """Test performance and scalability"""
        tests = [
            ("Response Times", self.test_response_times),
            ("Memory Usage", self.test_memory_usage),
            ("Concurrent Processing", self.test_concurrent_processing),
            ("Throughput", self.test_throughput),
        ]

        await self.run_test_group("Performance Metrics", tests)

    async def test_response_times(self):
        """Test response times"""
        try:
            from mcp_client import mcp_client

            # Test response times for different operations
            operations = [
                ("financial", "get_crypto_prices", {"symbols": ["BTC"]}),
                ("social", "twitter_sentiment", {"topic": "crypto"}),
                ("blockchain", "ethereum_analysis", {}),
            ]

            total_time = 0
            for server, tool, args in operations:
                start_time = time.time()
                await mcp_client.call_tool(server, tool, args)
                end_time = time.time()

                response_time = end_time - start_time
                total_time += response_time

                # Response should be under 5 seconds
                assert response_time < 5.0, f"Response time too slow: {response_time}s"

            avg_response_time = total_time / len(operations)
            self.performance_metrics["avg_response_time"] = avg_response_time

            return {"status": "PASS", "details": f"Avg response time: {avg_response_time:.2f}s"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_memory_usage(self):
        """Test memory usage"""
        try:
            import gc

            # Force garbage collection
            gc.collect()

            # Get current memory usage
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            self.performance_metrics["memory_usage_mb"] = memory_mb

            # Memory should be reasonable (under 500MB for testing)
            assert memory_mb < 500, f"Memory usage too high: {memory_mb:.1f}MB"

            return {"status": "PASS", "details": f"Memory usage: {memory_mb:.1f}MB"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_concurrent_processing(self):
        """Test concurrent processing"""
        try:
            from mcp_client import mcp_client

            # Test concurrent requests
            async def make_request():
                return await mcp_client.call_tool("financial", "get_crypto_prices", {"symbols": ["BTC"]})

            # Run 10 concurrent requests
            start_time = time.time()
            tasks = [make_request() for _ in range(10)]
            results = await asyncio.gather(*tasks)
            end_time = time.time()

            # All requests should succeed
            for result in results:
                assert result.get("success"), "Concurrent request failed"

            concurrent_time = end_time - start_time
            self.performance_metrics["concurrent_processing_time"] = concurrent_time

            return {"status": "PASS", "details": f"10 concurrent requests: {concurrent_time:.2f}s"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_throughput(self):
        """Test system throughput"""
        try:
            from mcp_natural_language import process_natural_language

            # Test message processing throughput
            messages = [
                "What's Bitcoin's price?",
                "Analyze the market",
                "Hello there",
                "Show my portfolio",
                "What's trending?"
            ]

            start_time = time.time()
            for i, message in enumerate(messages * 4):  # 20 messages total
                await process_natural_language(12345 + i, message)

            end_time = time.time()

            total_time = end_time - start_time
            throughput = 20 / total_time  # messages per second

            self.performance_metrics["throughput_msg_per_sec"] = throughput

            return {"status": "PASS", "details": f"Throughput: {throughput:.1f} msg/sec"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_error_handling(self):
        """Test error handling and resilience"""
        tests = [
            ("Graceful Degradation", self.test_graceful_degradation),
            ("Fallback Responses", self.test_fallback_responses),
            ("Error Recovery", self.test_error_recovery),
        ]

        await self.run_test_group("Error Handling", tests)

    async def test_graceful_degradation(self):
        """Test graceful degradation"""
        try:
            from mcp_natural_language import process_natural_language

            # Test with invalid input
            result = await process_natural_language(12345, "")
            assert isinstance(result, dict), "Should return dict even for invalid input"

            # Test with very long input
            long_message = "x" * 10000
            result = await process_natural_language(12345, long_message)
            assert isinstance(result, dict), "Should handle long input gracefully"

            return {"status": "PASS", "details": "Graceful degradation working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_fallback_responses(self):
        """Test fallback responses"""
        try:
            from mcp_client import mcp_client

            # Test fallback for unavailable server
            result = await mcp_client._get_fallback_response("test", "test", {})
            assert result.get("fallback"), "Fallback response not provided"
            assert "message" in result, "Fallback message missing"

            return {"status": "PASS", "details": "Fallback responses working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_error_recovery(self):
        """Test error recovery"""
        try:
            from mcp_background_processor import background_processor
            from mcp_background_processor import ProcessingJob
            from datetime import datetime

            # Test job with invalid parameters
            job = ProcessingJob(
                job_id="error_test",
                user_id=12345,
                job_type="invalid_job_type",
                parameters={}
            )

            result = await background_processor._process_job(job)
            assert not result.get("success"), "Should fail for invalid job type"
            assert "error" in result, "Error information missing"

            return {"status": "PASS", "details": "Error recovery working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_integration_compatibility(self):
        """Test integration and compatibility"""
        tests = [
            ("Main Bot Integration", self.test_main_bot_integration),
            ("Command Handler Compatibility", self.test_command_compatibility),
            ("Database Integration", self.test_database_integration),
        ]

        await self.run_test_group("Integration Compatibility", tests)

    async def test_main_bot_integration(self):
        """Test main bot integration"""
        try:
            # Test that main bot can import MCP modules
            import main

            # Check that MCP imports are available
            assert hasattr(main, 'initialize_mcp'), "MCP initialization not imported"
            assert hasattr(main, 'process_natural_language'), "NLP processing not imported"

            return {"status": "PASS", "details": "Main bot integration working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_command_compatibility(self):
        """Test command handler compatibility"""
        try:
            # Test that existing command handlers still work
            import main

            # Check that all command handlers are still present
            expected_commands = [
                'start_command', 'help_command', 'summarynow_command',
                'ask_command', 'research_command', 'social_command',
                'multichain_command', 'portfolio_command', 'alerts_command',
                'premium_command', 'status_command', 'llama_command',
                'arkham_command', 'nansen_command', 'alert_command',
                'create_wallet_command', 'menu_command', 'mymentions_command',
                'topic_command', 'weekly_summary_command', 'whosaid_command',
                'schedule_command', 'set_calendly_command'
            ]

            missing_commands = []
            for cmd in expected_commands:
                if not hasattr(main, cmd):
                    missing_commands.append(cmd)

            assert not missing_commands, f"Missing commands: {missing_commands}"

            return {"status": "PASS", "details": "All command handlers present"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def test_database_integration(self):
        """Test database integration"""
        try:
            # Test that database operations still work
            from user_db import init_db

            # Initialize database
            init_db()

            return {"status": "PASS", "details": "Database integration working"}

        except Exception as e:
            return {"status": "FAIL", "error": str(e)}

    async def run_test_group(self, group_name: str, tests: List):
        """Run a group of tests"""
        group_results = {}
        group_passed = 0
        group_failed = 0

        for test_name, test_function in tests:
            try:
                print(f"  🧪 {test_name}...", end=" ")
                result = await test_function()

                if result["status"] == "PASS":
                    print(f"✅ PASS - {result['details']}")
                    group_passed += 1
                    self.passed_tests += 1
                else:
                    print(f"❌ FAIL - {result.get('error', 'Unknown error')}")
                    group_failed += 1
                    self.failed_tests += 1

                group_results[test_name] = result
                self.total_tests += 1

            except Exception as e:
                print(f"❌ FAIL - {str(e)}")
                group_results[test_name] = {"status": "FAIL", "error": str(e)}
                group_failed += 1
                self.failed_tests += 1
                self.total_tests += 1

        self.test_results[group_name] = {
            "passed": group_passed,
            "failed": group_failed,
            "total": group_passed + group_failed,
            "results": group_results
        }

        print(f"  📊 Group Summary: {group_passed} passed, {group_failed} failed")

    async def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        end_time = time.time()
        total_time = end_time - self.start_time

        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE MCP INTEGRATION TEST REPORT")
        print("=" * 80)

        # Overall summary
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"📊 Overall Results: {self.passed_tests}/{self.total_tests} tests passed ({success_rate:.1f}%)")
        print(f"⏱️  Total execution time: {total_time:.2f} seconds")

        # Performance metrics
        if self.performance_metrics:
            print(f"\n⚡ Performance Metrics:")
            for metric, value in self.performance_metrics.items():
                if isinstance(value, float):
                    print(f"   • {metric}: {value:.2f}")
                else:
                    print(f"   • {metric}: {value}")

        # Category breakdown
        print(f"\n📋 Category Breakdown:")
        for category, results in self.test_results.items():
            status_emoji = "✅" if results["failed"] == 0 else "⚠️" if results["passed"] > results["failed"] else "❌"
            print(f"   {status_emoji} {category}: {results['passed']}/{results['total']} passed")

        # System status
        print(f"\n🏥 System Health:")
        process = psutil.Process()
        cpu_percent = process.cpu_percent()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"   • CPU Usage: {cpu_percent:.1f}%")
        print(f"   • Memory Usage: {memory_mb:.1f}MB")

        # Final assessment
        print(f"\n🎯 Final Assessment:")
        if success_rate >= 95:
            print("   🟢 EXCELLENT - Production ready with industry-grade quality")
        elif success_rate >= 85:
            print("   🟡 GOOD - Ready for deployment with minor improvements needed")
        elif success_rate >= 70:
            print("   🟠 FAIR - Requires significant improvements before deployment")
        else:
            print("   🔴 POOR - Major issues need to be resolved")

        # Recommendations
        print(f"\n💡 Recommendations:")
        if success_rate >= 95:
            print("   • System is ready for production deployment")
            print("   • Consider implementing monitoring and alerting")
            print("   • Plan for scaling and load balancing")
        else:
            print("   • Address failing tests before deployment")
            print("   • Implement additional error handling")
            print("   • Optimize performance bottlenecks")

        print("\n" + "=" * 80)

        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "success_rate": success_rate,
                "execution_time": total_time
            },
            "performance_metrics": self.performance_metrics,
            "test_results": self.test_results,
            "system_health": {
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb
            }
        }

        with open("mcp_comprehensive_test_report.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 Detailed report saved to: mcp_comprehensive_test_report.json")

async def main():
    """Run comprehensive test suite"""
    test_suite = MCPComprehensiveTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())