#!/usr/bin/env python3
# direct_bot_test.py - Direct Bot Functionality Test
"""
Direct testing of bot functionality without mocking
Tests natural language processing and command responsiveness
"""

import asyncio
import logging
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DirectBotTestSuite:
    """Direct bot functionality testing"""
    
    def __init__(self):
        self.test_user_id = 12345
        self.results = {}
        
    async def run_direct_tests(self):
        """Run direct bot functionality tests"""
        logger.info("🚀 Starting Direct Bot Functionality Tests")
        
        test_categories = [
            ("Natural Language Processing", self.test_nlp_direct),
            ("AI Provider Integration", self.test_ai_providers),
            ("Database Operations", self.test_database_direct),
            ("MCP Infrastructure", self.test_mcp_direct),
            ("Cross-Chain Analytics", self.test_cross_chain_direct),
            ("Response Generation", self.test_response_generation)
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for category_name, test_function in test_categories:
            logger.info(f"\n🧪 Testing: {category_name}")
            try:
                category_results = await test_function()
                self.results[category_name] = category_results
                
                category_passed = sum(1 for result in category_results.values() if result.get('passed', False))
                category_total = len(category_results)
                
                total_tests += category_total
                passed_tests += category_passed
                
                logger.info(f"✅ {category_name}: {category_passed}/{category_total} tests passed")
                
            except Exception as e:
                logger.error(f"❌ {category_name} failed: {e}")
                self.results[category_name] = {"error": str(e), "passed": False}
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"\n🎯 Direct Bot Test Complete: {success_rate:.1f}% success rate")
        logger.info(f"📊 Total: {passed_tests}/{total_tests} tests passed")
        
        return success_rate >= 80

    async def test_nlp_direct(self):
        """Test natural language processing directly"""
        results = {}
        
        try:
            from mcp_natural_language import process_natural_language, initialize_nlp_processor
            
            # Initialize NLP processor
            await initialize_nlp_processor()
            
            # Test various natural language queries
            test_queries = [
                "What's Bitcoin's price?",
                "Show me Ethereum analysis", 
                "Help me understand DeFi",
                "Set an alert for SOL",
                "Check my portfolio"
            ]
            
            successful_queries = 0
            
            for query in test_queries:
                try:
                    start_time = time.time()
                    response = await process_natural_language(self.test_user_id, query)
                    response_time = time.time() - start_time
                    
                    if response.get("success") and response_time < 5.0:
                        successful_queries += 1
                        
                    logger.info(f"  Query: '{query}' -> {response.get('intent', 'unknown')} ({response_time:.3f}s)")
                    
                except Exception as e:
                    logger.warning(f"  Query failed: '{query}' -> {e}")
            
            results["nlp_query_processing"] = {
                "passed": successful_queries >= len(test_queries) * 0.8,
                "details": f"NLP query processing: {successful_queries}/{len(test_queries)} successful",
                "successful_queries": successful_queries,
                "total_queries": len(test_queries)
            }
            
        except Exception as e:
            results["nlp_query_processing"] = {"passed": False, "error": str(e)}
        
        # Test intent recognition
        try:
            from mcp_natural_language import process_natural_language
            
            intent_tests = [
                ("What's Bitcoin's price?", "price_query"),
                ("Analyze the market", "market_analysis"),
                ("Hello", "greeting")
            ]
            
            correct_intents = 0
            
            for query, expected_intent in intent_tests:
                try:
                    response = await process_natural_language(self.test_user_id, query)
                    detected_intent = response.get("intent")
                    
                    if detected_intent == expected_intent:
                        correct_intents += 1
                        
                    logger.info(f"  Intent: '{query}' -> Expected: {expected_intent}, Got: {detected_intent}")
                    
                except Exception as e:
                    logger.warning(f"  Intent test failed: {e}")
            
            results["intent_recognition"] = {
                "passed": correct_intents >= len(intent_tests) * 0.6,  # 60% accuracy
                "details": f"Intent recognition: {correct_intents}/{len(intent_tests)} correct",
                "correct_intents": correct_intents,
                "total_tests": len(intent_tests)
            }
            
        except Exception as e:
            results["intent_recognition"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_ai_providers(self):
        """Test AI provider integration"""
        results = {}
        
        # Test Groq API
        try:
            from groq import Groq
            groq_key = os.getenv('GROQ_API_KEY')
            
            if groq_key:
                client = Groq(api_key=groq_key)
                
                start_time = time.time()
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": "Explain Bitcoin in one sentence."}],
                    model="llama3-8b-8192",
                    max_tokens=50
                )
                response_time = time.time() - start_time
                
                groq_working = bool(response.choices[0].message.content)
                
                results["groq_integration"] = {
                    "passed": groq_working and response_time < 10.0,
                    "details": f"Groq API integration: {'working' if groq_working else 'failed'}",
                    "response_time": f"{response_time:.3f}s",
                    "response_received": groq_working
                }
                
                logger.info(f"  Groq API: {response.choices[0].message.content[:50]}...")
                
            else:
                results["groq_integration"] = {
                    "passed": False,
                    "details": "Groq API key not provided"
                }
                
        except Exception as e:
            results["groq_integration"] = {"passed": False, "error": str(e)}
        
        # Test Gemini API
        try:
            import google.generativeai as genai
            gemini_key = os.getenv('GEMINI_API_KEY')
            
            if gemini_key:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                start_time = time.time()
                response = model.generate_content("Explain Ethereum in one sentence.")
                response_time = time.time() - start_time
                
                gemini_working = bool(response.text)
                
                results["gemini_integration"] = {
                    "passed": gemini_working and response_time < 10.0,
                    "details": f"Gemini API integration: {'working' if gemini_working else 'failed'}",
                    "response_time": f"{response_time:.3f}s",
                    "response_received": gemini_working
                }
                
                logger.info(f"  Gemini API: {response.text[:50]}...")
                
            else:
                results["gemini_integration"] = {
                    "passed": False,
                    "details": "Gemini API key not provided"
                }
                
        except Exception as e:
            results["gemini_integration"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_database_direct(self):
        """Test database operations directly"""
        results = {}
        
        # Test basic database operations
        try:
            from user_db import init_db, set_user_property, get_user_property
            
            # Initialize database
            init_db()
            
            # Test write operation
            test_key = "test_direct_key"
            test_value = "test_direct_value"
            
            set_user_property(self.test_user_id, test_key, test_value)
            
            # Test read operation
            retrieved_value = get_user_property(self.test_user_id, test_key)
            
            db_working = retrieved_value == test_value
            
            results["basic_database_ops"] = {
                "passed": db_working,
                "details": f"Database operations: {'working' if db_working else 'failed'}",
                "write_successful": True,
                "read_successful": db_working,
                "data_integrity": db_working
            }
            
            logger.info(f"  Database: Write/Read test {'passed' if db_working else 'failed'}")
            
        except Exception as e:
            results["basic_database_ops"] = {"passed": False, "error": str(e)}
        
        # Test enhanced database
        try:
            from enhanced_db import enhanced_db
            
            # Test enhanced database connection
            enhanced_working = enhanced_db is not None
            
            results["enhanced_database"] = {
                "passed": enhanced_working,
                "details": f"Enhanced database: {'initialized' if enhanced_working else 'failed'}",
                "database_available": enhanced_working
            }
            
            logger.info(f"  Enhanced DB: {'initialized' if enhanced_working else 'failed'}")
            
        except Exception as e:
            results["enhanced_database"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_mcp_direct(self):
        """Test MCP infrastructure directly"""
        results = {}
        
        # Test MCP client initialization
        try:
            from mcp_client import mcp_client, initialize_mcp
            
            mcp_initialized = await initialize_mcp()
            
            results["mcp_initialization"] = {
                "passed": mcp_initialized,
                "details": f"MCP client: {'initialized' if mcp_initialized else 'failed'}",
                "client_ready": mcp_initialized
            }
            
            logger.info(f"  MCP Client: {'initialized' if mcp_initialized else 'failed'}")
            
        except Exception as e:
            results["mcp_initialization"] = {"passed": False, "error": str(e)}
        
        # Test MCP tool calls
        try:
            from mcp_client import mcp_client
            
            # Test financial tool
            start_time = time.time()
            response = await mcp_client.call_tool("financial", "get_crypto_prices", {"symbols": ["BTC"]})
            response_time = time.time() - start_time
            
            tool_working = response.get("success") or response.get("fallback")
            
            results["mcp_tool_calls"] = {
                "passed": tool_working and response_time < 5.0,
                "details": f"MCP tool calls: {'working' if tool_working else 'failed'}",
                "response_time": f"{response_time:.3f}s",
                "tool_functional": tool_working
            }
            
            logger.info(f"  MCP Tools: {'working' if tool_working else 'failed'} ({response_time:.3f}s)")
            
        except Exception as e:
            results["mcp_tool_calls"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_cross_chain_direct(self):
        """Test cross-chain analytics directly"""
        results = {}
        
        try:
            from cross_chain_analytics import CrossChainAnalytics, CrossChainAnalyzer
            
            # Test CrossChainAnalytics
            analytics = CrossChainAnalytics()
            supported_chains = len(analytics.supported_chains)
            
            results["cross_chain_analytics"] = {
                "passed": supported_chains >= 3,
                "details": f"Cross-chain analytics: {supported_chains} chains supported",
                "supported_chains": supported_chains,
                "analytics_functional": supported_chains >= 3
            }
            
            # Test CrossChainAnalyzer
            analyzer = CrossChainAnalyzer()
            analyzer_working = hasattr(analyzer, 'analyze_cross_chain_activity')
            
            results["cross_chain_analyzer"] = {
                "passed": analyzer_working,
                "details": f"Cross-chain analyzer: {'working' if analyzer_working else 'failed'}",
                "analyzer_functional": analyzer_working
            }
            
            logger.info(f"  Cross-chain: {supported_chains} chains, analyzer {'working' if analyzer_working else 'failed'}")
            
        except Exception as e:
            results["cross_chain_analytics"] = {"passed": False, "error": str(e)}
            results["cross_chain_analyzer"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_response_generation(self):
        """Test response generation capabilities"""
        results = {}
        
        # Test AI orchestrator
        try:
            from mcp_ai_orchestrator import ai_orchestrator, initialize_ai_orchestrator
            
            await initialize_ai_orchestrator()
            
            # Test query classification
            test_query = "What's Bitcoin's price?"
            start_time = time.time()
            query_type = await ai_orchestrator.classify_query(test_query)
            classification_time = time.time() - start_time
            
            classification_working = query_type is not None
            
            results["ai_orchestrator"] = {
                "passed": classification_working and classification_time < 3.0,
                "details": f"AI orchestrator: {'working' if classification_working else 'failed'}",
                "classification_time": f"{classification_time:.3f}s",
                "query_type": str(query_type) if query_type else None
            }
            
            logger.info(f"  AI Orchestrator: Query '{test_query}' -> {query_type} ({classification_time:.3f}s)")
            
        except Exception as e:
            results["ai_orchestrator"] = {"passed": False, "error": str(e)}
        
        # Test fallback responses
        try:
            from fallback_responses import fallback_generator
            
            fallback_response = fallback_generator.get_fallback_response('price_query', {'symbol': 'BTC'})
            fallback_working = len(fallback_response) > 10
            
            results["fallback_responses"] = {
                "passed": fallback_working,
                "details": f"Fallback responses: {'working' if fallback_working else 'failed'}",
                "response_length": len(fallback_response),
                "fallback_functional": fallback_working
            }
            
            logger.info(f"  Fallback: Generated {len(fallback_response)} char response")
            
        except Exception as e:
            results["fallback_responses"] = {"passed": False, "error": str(e)}
        
        return results

async def main():
    """Run direct bot tests"""
    print("🚀 Starting Direct Bot Functionality Tests")
    print("=" * 60)
    
    test_suite = DirectBotTestSuite()
    
    try:
        success = await test_suite.run_direct_tests()
        
        if success:
            print(f"\n✅ SUCCESS: Bot functionality is working well!")
            print(f"🚀 Ready for natural language interactions and command processing")
        else:
            print(f"\n⚠️ PARTIAL SUCCESS: Some functionality needs attention")
            print(f"🔧 Check the test results above for specific issues")
        
        return success
        
    except Exception as e:
        print(f"❌ Direct test suite failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)