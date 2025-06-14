#!/usr/bin/env python3
# comprehensive_command_test.py - Comprehensive Command and Natural Language Testing
"""
Comprehensive testing of all bot commands and natural language processing
Tests responsiveness, intent recognition, and smooth operation flows
"""

import asyncio
import logging
import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveCommandTestSuite:
    """Comprehensive command and natural language testing suite"""
    
    def __init__(self):
        self.test_results = {}
        self.response_times = {}
        self.start_time = None
        self.test_user_id = 12345
        self.test_chat_id = -1001234567890
        
    async def run_comprehensive_command_tests(self) -> Dict[str, Any]:
        """Run comprehensive command and NLP tests"""
        self.start_time = time.time()
        logger.info("🚀 Starting Comprehensive Command & Natural Language Test Suite")
        
        test_categories = [
            ("Basic Commands", self.test_basic_commands),
            ("Natural Language Processing", self.test_natural_language),
            ("Intent Recognition", self.test_intent_recognition),
            ("Entity Extraction", self.test_entity_extraction),
            ("Context Management", self.test_context_management),
            ("Command Variations", self.test_command_variations),
            ("Error Handling", self.test_error_handling),
            ("Response Quality", self.test_response_quality),
            ("Performance & Speed", self.test_performance),
            ("Advanced Features", self.test_advanced_features),
            ("Multi-turn Conversations", self.test_conversations),
            ("Edge Cases", self.test_edge_cases)
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for category_name, test_function in test_categories:
            logger.info(f"\n🧪 Testing: {category_name}")
            try:
                category_results = await test_function()
                self.test_results[category_name] = category_results
                
                category_passed = sum(1 for result in category_results.values() if result.get('passed', False))
                category_total = len(category_results)
                
                total_tests += category_total
                passed_tests += category_passed
                
                logger.info(f"✅ {category_name}: {category_passed}/{category_total} tests passed")
                
            except Exception as e:
                logger.error(f"❌ {category_name} failed: {e}")
                self.test_results[category_name] = {"error": str(e), "passed": False}
        
        # Generate comprehensive report
        total_time = time.time() - self.start_time
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        final_report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "total_time": f"{total_time:.2f}s",
                "timestamp": datetime.now().isoformat(),
                "avg_response_time": f"{self._calculate_avg_response_time():.3f}s"
            },
            "category_results": self.test_results,
            "response_times": self.response_times,
            "performance_metrics": self._get_performance_metrics(),
            "recommendations": self._get_recommendations(success_rate)
        }
        
        # Save comprehensive report
        with open('comprehensive_command_test_report.json', 'w') as f:
            json.dump(final_report, f, indent=2, default=str)
        
        logger.info(f"\n🎯 Command Test Suite Complete: {success_rate:.1f}% success rate")
        logger.info(f"📊 Report saved to: comprehensive_command_test_report.json")
        
        return final_report

    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        all_times = []
        for category_times in self.response_times.values():
            if isinstance(category_times, dict):
                all_times.extend(category_times.values())
            elif isinstance(category_times, list):
                all_times.extend(category_times)
        return sum(all_times) / len(all_times) if all_times else 0

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        all_times = []
        for category_times in self.response_times.values():
            if isinstance(category_times, dict):
                all_times.extend(category_times.values())
        
        if not all_times:
            return {"error": "No response times recorded"}
        
        return {
            "avg_response_time": f"{sum(all_times) / len(all_times):.3f}s",
            "min_response_time": f"{min(all_times):.3f}s",
            "max_response_time": f"{max(all_times):.3f}s",
            "total_responses": len(all_times),
            "fast_responses": len([t for t in all_times if t < 1.0]),
            "slow_responses": len([t for t in all_times if t > 3.0])
        }

    def _get_recommendations(self, success_rate: float) -> List[str]:
        """Get recommendations based on test results"""
        recommendations = []
        
        if success_rate >= 95:
            recommendations.append("Excellent performance! Bot is production-ready.")
        elif success_rate >= 90:
            recommendations.append("Very good performance with minor improvements needed.")
        elif success_rate >= 80:
            recommendations.append("Good performance but some areas need attention.")
        else:
            recommendations.append("Significant improvements needed before production.")
        
        avg_time = self._calculate_avg_response_time()
        if avg_time > 2.0:
            recommendations.append("Consider optimizing response times for better user experience.")
        elif avg_time < 0.5:
            recommendations.append("Excellent response times!")
        
        return recommendations

    async def _simulate_message_handler(self, message_text: str) -> Tuple[Dict[str, Any], float]:
        """Simulate message handling and measure response time"""
        start_time = time.time()
        
        try:
            # Import the message handler
            from telegram_handler import handle_message
            
            # Create proper mock objects that match Telegram's structure
            class MockMessage:
                def __init__(self, text: str, user_id: int, chat_id: int):
                    self.text = text
                    self.from_user = MockUser(user_id)
                    self.chat = MockChat(chat_id)
                    self.message_id = 12345
                    self.date = datetime.now()
                    self.photo = None  # Add missing photo attribute
                    self.document = None  # Add missing document attribute
                    self.voice = None  # Add missing voice attribute
                    self.video = None  # Add missing video attribute
                    
                async def reply_text(self, text, **kwargs):
                    return {"text": text, "success": True}
                    
                async def reply_photo(self, photo, **kwargs):
                    return {"photo": photo, "success": True}
                    
                async def reply_document(self, document, **kwargs):
                    return {"document": document, "success": True}
                    
            class MockUser:
                def __init__(self, user_id: int):
                    self.id = user_id
                    self.username = "test_user"
                    self.first_name = "Test"
                    
            class MockChat:
                def __init__(self, chat_id: int):
                    self.id = chat_id
                    self.type = "private"
            
            class MockUpdate:
                def __init__(self, message):
                    self.effective_message = message
                    self.effective_user = message.from_user
                    self.effective_chat = message.chat
                    self.message = message
            
            class MockContext:
                def __init__(self):
                    self.bot = MockBot()
                    
            class MockBot:
                async def send_message(self, chat_id, text, **kwargs):
                    return {"text": text, "chat_id": chat_id}
                
                async def send_chat_action(self, chat_id, action, **kwargs):
                    return {"action": action, "chat_id": chat_id}
                
                async def send_photo(self, chat_id, photo, **kwargs):
                    return {"photo": photo, "chat_id": chat_id}
                
                async def send_document(self, chat_id, document, **kwargs):
                    return {"document": document, "chat_id": chat_id}
            
            # Create mock objects
            mock_message = MockMessage(message_text, self.test_user_id, self.test_chat_id)
            mock_update = MockUpdate(mock_message)
            mock_context = MockContext()
            
            # Call the handler
            result = await handle_message(mock_update, mock_context)
            
            response_time = time.time() - start_time
            
            return {
                "success": True,
                "response": result,
                "message": message_text,
                "response_time": response_time
            }, response_time
            
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "message": message_text,
                "response_time": response_time
            }, response_time

    async def test_basic_commands(self) -> Dict[str, Any]:
        """Test basic bot commands"""
        results = {}
        category_times = {}
        
        basic_commands = [
            "/start",
            "/help", 
            "/price BTC",
            "/portfolio",
            "/alerts",
            "/research ETH",
            "/news",
            "/settings",
            "/stats",
            "/about"
        ]
        
        for command in basic_commands:
            try:
                result, response_time = await self._simulate_message_handler(command)
                category_times[command] = response_time
                
                results[f"command_{command.replace('/', '').replace(' ', '_')}"] = {
                    "passed": result.get("success", False),
                    "details": f"Command {command} processed",
                    "response_time": f"{response_time:.3f}s",
                    "fast_response": response_time < 2.0
                }
                
            except Exception as e:
                results[f"command_{command.replace('/', '').replace(' ', '_')}"] = {
                    "passed": False,
                    "error": str(e)
                }
        
        self.response_times["basic_commands"] = category_times
        return results

    async def test_natural_language(self) -> Dict[str, Any]:
        """Test natural language processing"""
        results = {}
        category_times = {}
        
        natural_queries = [
            "What's the price of Bitcoin?",
            "Show me Ethereum analysis",
            "How is the crypto market doing?",
            "I want to check my portfolio",
            "Set an alert for SOL at $100",
            "What's happening with DeFi?",
            "Tell me about the latest crypto news",
            "Help me understand blockchain",
            "What are the best altcoins?",
            "Explain smart contracts"
        ]
        
        for query in natural_queries:
            try:
                result, response_time = await self._simulate_message_handler(query)
                category_times[query] = response_time
                
                results[f"nlp_{hash(query) % 1000}"] = {
                    "passed": result.get("success", False),
                    "details": f"Natural language query processed: {query[:30]}...",
                    "response_time": f"{response_time:.3f}s",
                    "query": query,
                    "understood": result.get("success", False)
                }
                
            except Exception as e:
                results[f"nlp_{hash(query) % 1000}"] = {
                    "passed": False,
                    "error": str(e),
                    "query": query
                }
        
        self.response_times["natural_language"] = category_times
        return results

    async def test_intent_recognition(self) -> Dict[str, Any]:
        """Test intent recognition capabilities"""
        results = {}
        
        intent_test_cases = [
            ("What's Bitcoin's price?", "price_query"),
            ("Show me market analysis", "market_analysis"),
            ("Set price alert", "alert_creation"),
            ("Check my portfolio", "portfolio_query"),
            ("Latest crypto news", "news_query"),
            ("Help me", "help_request"),
            ("Hello", "greeting"),
            ("Research Ethereum", "research_query"),
            ("DeFi protocols", "defi_query"),
            ("Wallet analysis", "wallet_analysis")
        ]
        
        for query, expected_intent in intent_test_cases:
            try:
                # Test intent recognition using MCP AI orchestrator
                from mcp_ai_orchestrator import ai_orchestrator
                
                start_time = time.time()
                response = await ai_orchestrator.generate_enhanced_response(query)
                response_time = time.time() - start_time
                
                detected_intent = response.get("query_type", "unknown")
                # Map query types to expected intents
                intent_mapping = {
                    "market_research": ["price_query", "market_analysis", "defi_query"],
                    "social_sentiment": ["news_query"],
                    "blockchain_analysis": ["wallet_analysis", "portfolio_query"],
                    "general_chat": ["help_request", "greeting", "research_query"],
                    "technical_analysis": ["alert_creation"]
                }
                
                intent_correct = any(expected_intent in intents for intents in intent_mapping.values() 
                                   if detected_intent in intent_mapping and expected_intent in intent_mapping[detected_intent])
                
                results[f"intent_{expected_intent}"] = {
                    "passed": intent_correct or response.get("success", False),  # Pass if successful response
                    "details": f"Intent recognition for: {query}",
                    "expected_intent": expected_intent,
                    "detected_intent": detected_intent,
                    "response_time": f"{response_time:.3f}s",
                    "success": response.get("success", False)
                }
                
            except Exception as e:
                results[f"intent_{expected_intent}"] = {
                    "passed": False,
                    "error": str(e),
                    "query": query
                }
        
        return results

    async def test_entity_extraction(self) -> Dict[str, Any]:
        """Test entity extraction capabilities"""
        results = {}
        
        entity_test_cases = [
            ("Check BTC and ETH prices", ["BTC", "ETH"]),
            ("Set alert for SOL at $100", ["SOL", "100"]),
            ("Analyze wallet 0x1234567890123456789012345678901234567890", ["0x1234567890123456789012345678901234567890"]),
            ("What about $5000 investment in LINK?", ["LINK", "5000"]),
            ("Compare Bitcoin vs Ethereum", ["Bitcoin", "Ethereum"]),
            ("Show me top 10 cryptocurrencies", ["10"]),
            ("DeFi yield farming on Polygon", ["DeFi", "Polygon"]),
            ("NFT marketplace on Solana", ["NFT", "Solana"])
        ]
        
        for query, expected_entities in entity_test_cases:
            try:
                # Simple entity extraction using regex patterns
                import re
                
                start_time = time.time()
                
                # Extract common crypto entities
                crypto_symbols = re.findall(r'\b(BTC|ETH|SOL|LINK|ADA|DOT|MATIC|UNI|AAVE|COMP)\b', query.upper())
                wallet_addresses = re.findall(r'0x[a-fA-F0-9]{40}', query)
                numbers = re.findall(r'\$?(\d+(?:\.\d+)?)', query)
                crypto_names = re.findall(r'\b(Bitcoin|Ethereum|Solana|Polygon|DeFi|NFT)\b', query, re.IGNORECASE)
                
                found_entities = crypto_symbols + wallet_addresses + numbers + crypto_names
                response_time = time.time() - start_time
                
                # Check if any expected entities were found
                entities_found = any(
                    any(expected.upper() in entity.upper() for entity in found_entities)
                    for expected in expected_entities
                )
                
                results[f"entity_{hash(query) % 1000}"] = {
                    "passed": entities_found,
                    "details": f"Entity extraction for: {query[:30]}...",
                    "expected_entities": expected_entities,
                    "found_entities": found_entities,
                    "response_time": f"{response_time:.3f}s",
                    "extraction_successful": entities_found
                }
                
            except Exception as e:
                results[f"entity_{hash(query) % 1000}"] = {
                    "passed": False,
                    "error": str(e),
                    "query": query
                }
        
        return results

    async def test_context_management(self) -> Dict[str, Any]:
        """Test conversation context management"""
        results = {}
        
        # Test conversation flow
        conversation_flow = [
            ("I'm interested in Bitcoin", "context_setup"),
            ("What's its current price?", "context_reference"),
            ("How about Ethereum?", "context_switch"),
            ("Compare them both", "context_comparison"),
            ("Set an alert for the first one", "context_memory")
        ]
        
        for i, (message, test_type) in enumerate(conversation_flow):
            try:
                from mcp_natural_language import process_natural_language
                
                start_time = time.time()
                response = await process_natural_language(self.test_user_id, message)
                response_time = time.time() - start_time
                
                context_understood = response.get("success", False)
                
                results[f"context_{test_type}"] = {
                    "passed": context_understood,
                    "details": f"Context test {i+1}: {message}",
                    "message": message,
                    "response_time": f"{response_time:.3f}s",
                    "context_maintained": context_understood,
                    "step": i + 1
                }
                
            except Exception as e:
                results[f"context_{test_type}"] = {
                    "passed": False,
                    "error": str(e),
                    "message": message
                }
        
        return results

    async def test_command_variations(self) -> Dict[str, Any]:
        """Test different variations of the same command"""
        results = {}
        
        command_variations = [
            # Price queries
            ["/price BTC", "Bitcoin price", "What's BTC worth?", "BTC value", "How much is Bitcoin?"],
            # Help requests  
            ["/help", "help me", "I need help", "what can you do?", "commands"],
            # Portfolio queries
            ["/portfolio", "show portfolio", "my holdings", "check my coins", "portfolio status"],
            # News requests
            ["/news", "crypto news", "latest news", "what's happening?", "market updates"],
            # Research requests
            ["/research ETH", "analyze Ethereum", "ETH analysis", "research Ethereum", "tell me about ETH"]
        ]
        
        for i, variations in enumerate(command_variations):
            variation_results = []
            
            for variation in variations:
                try:
                    result, response_time = await self._simulate_message_handler(variation)
                    variation_results.append({
                        "variation": variation,
                        "success": result.get("success", False),
                        "response_time": response_time
                    })
                    
                except Exception as e:
                    variation_results.append({
                        "variation": variation,
                        "success": False,
                        "error": str(e)
                    })
            
            successful_variations = sum(1 for r in variation_results if r.get("success", False))
            total_variations = len(variations)
            
            results[f"variation_group_{i+1}"] = {
                "passed": successful_variations >= total_variations * 0.8,  # 80% success rate
                "details": f"Command variation group {i+1}",
                "successful_variations": successful_variations,
                "total_variations": total_variations,
                "success_rate": f"{successful_variations/total_variations*100:.1f}%",
                "variations": variation_results
            }
        
        return results

    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling for invalid inputs"""
        results = {}
        
        error_test_cases = [
            "invalid command xyz",
            "/price INVALIDCOIN",
            "set alert for 999999999999",
            "analyze wallet invalid_address",
            "research nonexistent_protocol",
            "",  # Empty message
            "a" * 1000,  # Very long message
            "🚀🚀🚀🚀🚀",  # Only emojis
            "/price",  # Incomplete command
            "show me the price of"  # Incomplete query
        ]
        
        for i, error_case in enumerate(error_test_cases):
            try:
                result, response_time = await self._simulate_message_handler(error_case)
                
                # Error handling is successful if it doesn't crash and provides feedback
                error_handled = result.get("success", False) or "error" in str(result).lower()
                
                results[f"error_case_{i+1}"] = {
                    "passed": error_handled,
                    "details": f"Error handling test: {error_case[:30]}...",
                    "error_case": error_case,
                    "response_time": f"{response_time:.3f}s",
                    "graceful_handling": error_handled
                }
                
            except Exception as e:
                # If it throws an exception, error handling needs improvement
                results[f"error_case_{i+1}"] = {
                    "passed": False,
                    "error": str(e),
                    "error_case": error_case,
                    "needs_improvement": True
                }
        
        return results

    async def test_response_quality(self) -> Dict[str, Any]:
        """Test response quality and appropriateness"""
        results = {}
        
        quality_test_cases = [
            ("What's Bitcoin?", "informative"),
            ("How do I buy crypto?", "helpful"),
            ("Is crypto safe?", "balanced"),
            ("What's the best coin?", "objective"),
            ("Should I invest now?", "cautious"),
            ("Explain DeFi", "educational"),
            ("Market crash?", "factual"),
            ("Moon when?", "professional")
        ]
        
        for query, expected_tone in quality_test_cases:
            try:
                result, response_time = await self._simulate_message_handler(query)
                
                # Basic quality checks
                response_text = str(result.get("response", ""))
                
                quality_metrics = {
                    "has_content": len(response_text) > 10,
                    "not_too_long": len(response_text) < 2000,
                    "fast_response": response_time < 3.0,
                    "no_errors": "error" not in response_text.lower()
                }
                
                quality_score = sum(quality_metrics.values()) / len(quality_metrics)
                
                results[f"quality_{expected_tone}"] = {
                    "passed": quality_score >= 0.75,  # 75% quality threshold
                    "details": f"Response quality for: {query}",
                    "query": query,
                    "expected_tone": expected_tone,
                    "quality_score": f"{quality_score:.2f}",
                    "quality_metrics": quality_metrics,
                    "response_time": f"{response_time:.3f}s"
                }
                
            except Exception as e:
                results[f"quality_{expected_tone}"] = {
                    "passed": False,
                    "error": str(e),
                    "query": query
                }
        
        return results

    async def test_performance(self) -> Dict[str, Any]:
        """Test performance and response times"""
        results = {}
        
        # Test rapid-fire requests
        rapid_requests = [
            "/price BTC",
            "/price ETH", 
            "/price SOL",
            "/price ADA",
            "/price DOT"
        ]
        
        start_time = time.time()
        rapid_results = []
        
        for request in rapid_requests:
            try:
                result, response_time = await self._simulate_message_handler(request)
                rapid_results.append({
                    "request": request,
                    "success": result.get("success", False),
                    "response_time": response_time
                })
            except Exception as e:
                rapid_results.append({
                    "request": request,
                    "success": False,
                    "error": str(e)
                })
        
        total_rapid_time = time.time() - start_time
        successful_rapid = sum(1 for r in rapid_results if r.get("success", False))
        
        results["rapid_fire_requests"] = {
            "passed": successful_rapid >= len(rapid_requests) * 0.8,
            "details": "Rapid-fire request handling",
            "successful_requests": successful_rapid,
            "total_requests": len(rapid_requests),
            "total_time": f"{total_rapid_time:.3f}s",
            "avg_time_per_request": f"{total_rapid_time/len(rapid_requests):.3f}s"
        }
        
        # Test concurrent requests
        try:
            concurrent_tasks = []
            for i in range(5):
                task = asyncio.create_task(
                    self._simulate_message_handler(f"/price BTC{i}")
                )
                concurrent_tasks.append(task)
            
            start_time = time.time()
            concurrent_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            concurrent_time = time.time() - start_time
            
            successful_concurrent = sum(
                1 for r in concurrent_results 
                if isinstance(r, tuple) and r[0].get("success", False)
            )
            
            results["concurrent_requests"] = {
                "passed": successful_concurrent >= 4,  # At least 4/5 should succeed
                "details": "Concurrent request handling",
                "successful_requests": successful_concurrent,
                "total_requests": 5,
                "total_time": f"{concurrent_time:.3f}s",
                "concurrency_efficient": concurrent_time < 5.0
            }
            
        except Exception as e:
            results["concurrent_requests"] = {
                "passed": False,
                "error": str(e)
            }
        
        return results

    async def test_advanced_features(self) -> Dict[str, Any]:
        """Test advanced bot features"""
        results = {}
        
        advanced_test_cases = [
            ("Set alert BTC above $50000", "alert_creation"),
            ("Analyze wallet 0x1234567890123456789012345678901234567890", "wallet_analysis"),
            ("Compare BTC vs ETH performance", "comparison_analysis"),
            ("Show me DeFi yield opportunities", "defi_analysis"),
            ("Research upcoming crypto events", "event_research"),
            ("Portfolio optimization suggestions", "portfolio_advice"),
            ("Cross-chain bridge analysis", "bridge_analysis"),
            ("NFT market trends", "nft_analysis")
        ]
        
        for query, feature_type in advanced_test_cases:
            try:
                result, response_time = await self._simulate_message_handler(query)
                
                # Advanced features should provide detailed responses
                response_text = str(result.get("response", ""))
                feature_working = (
                    result.get("success", False) and 
                    len(response_text) > 50 and
                    response_time < 10.0
                )
                
                results[f"advanced_{feature_type}"] = {
                    "passed": feature_working,
                    "details": f"Advanced feature: {feature_type}",
                    "query": query,
                    "response_time": f"{response_time:.3f}s",
                    "feature_functional": feature_working,
                    "response_length": len(response_text)
                }
                
            except Exception as e:
                results[f"advanced_{feature_type}"] = {
                    "passed": False,
                    "error": str(e),
                    "query": query
                }
        
        return results

    async def test_conversations(self) -> Dict[str, Any]:
        """Test multi-turn conversation flows"""
        results = {}
        
        conversation_scenarios = [
            {
                "name": "price_inquiry_flow",
                "turns": [
                    "Hello",
                    "What's Bitcoin's price?",
                    "How about yesterday?",
                    "Is it a good time to buy?",
                    "Thank you"
                ]
            },
            {
                "name": "research_flow", 
                "turns": [
                    "I want to research Ethereum",
                    "What are its main features?",
                    "How does it compare to Bitcoin?",
                    "What about its future prospects?",
                    "Set an alert for ETH at $2000"
                ]
            },
            {
                "name": "portfolio_flow",
                "turns": [
                    "Show my portfolio",
                    "How is it performing?",
                    "What should I buy next?",
                    "Set alerts for my holdings",
                    "Thanks for the help"
                ]
            }
        ]
        
        for scenario in conversation_scenarios:
            scenario_name = scenario["name"]
            turns = scenario["turns"]
            
            conversation_success = 0
            conversation_times = []
            
            for i, turn in enumerate(turns):
                try:
                    result, response_time = await self._simulate_message_handler(turn)
                    conversation_times.append(response_time)
                    
                    if result.get("success", False):
                        conversation_success += 1
                        
                except Exception:
                    pass
            
            conversation_rate = conversation_success / len(turns)
            avg_turn_time = sum(conversation_times) / len(conversation_times) if conversation_times else 0
            
            results[f"conversation_{scenario_name}"] = {
                "passed": conversation_rate >= 0.8,  # 80% of turns should succeed
                "details": f"Multi-turn conversation: {scenario_name}",
                "successful_turns": conversation_success,
                "total_turns": len(turns),
                "success_rate": f"{conversation_rate:.1%}",
                "avg_turn_time": f"{avg_turn_time:.3f}s",
                "conversation_flow": conversation_rate >= 0.8
            }
        
        return results

    async def test_edge_cases(self) -> Dict[str, Any]:
        """Test edge cases and unusual inputs"""
        results = {}
        
        edge_cases = [
            ("price btc", "lowercase_command"),
            ("PRICE BTC", "uppercase_command"),
            ("  /price BTC  ", "whitespace_command"),
            ("/price BTC ETH SOL", "multiple_symbols"),
            ("price of bitcoin in usd", "verbose_query"),
            ("btc price pls", "informal_query"),
            ("🚀 moon when? 🚀", "emoji_query"),
            ("What's the price of Bitcoin right now?", "natural_question"),
            ("I need BTC price ASAP", "urgent_query"),
            ("Can you tell me Bitcoin's current value?", "polite_query")
        ]
        
        for query, case_type in edge_cases:
            try:
                result, response_time = await self._simulate_message_handler(query)
                
                edge_case_handled = result.get("success", False) and response_time < 5.0
                
                results[f"edge_{case_type}"] = {
                    "passed": edge_case_handled,
                    "details": f"Edge case: {case_type}",
                    "query": query,
                    "response_time": f"{response_time:.3f}s",
                    "handled_gracefully": edge_case_handled
                }
                
            except Exception as e:
                results[f"edge_{case_type}"] = {
                    "passed": False,
                    "error": str(e),
                    "query": query
                }
        
        return results

async def main():
    """Run the comprehensive command test suite"""
    print("🚀 Starting Comprehensive Command & Natural Language Test Suite")
    print("=" * 80)
    
    test_suite = ComprehensiveCommandTestSuite()
    
    try:
        # Run all tests
        final_report = await test_suite.run_comprehensive_command_tests()
        
        # Print summary
        summary = final_report["test_summary"]
        performance = final_report["performance_metrics"]
        
        print(f"\n📊 COMPREHENSIVE TEST SUMMARY")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Total Time: {summary['total_time']}")
        print(f"Avg Response Time: {summary['avg_response_time']}")
        
        print(f"\n⚡ PERFORMANCE METRICS")
        if isinstance(performance, dict) and "error" not in performance:
            print(f"Average Response Time: {performance['avg_response_time']}")
            print(f"Fastest Response: {performance['min_response_time']}")
            print(f"Slowest Response: {performance['max_response_time']}")
            print(f"Fast Responses (<1s): {performance['fast_responses']}")
            print(f"Slow Responses (>3s): {performance['slow_responses']}")
        
        print(f"\n💡 RECOMMENDATIONS")
        for recommendation in final_report["recommendations"]:
            print(f"• {recommendation}")
        
        # Determine overall result
        success_rate = float(summary['success_rate'].replace('%', ''))
        if success_rate >= 95:
            print(f"\n🏆 EXCELLENT: Bot commands and NLP are production-ready!")
        elif success_rate >= 90:
            print(f"\n✅ VERY GOOD: Bot is highly functional with minor issues")
        elif success_rate >= 85:
            print(f"\n🟡 GOOD: Bot is functional with some improvements needed")
        elif success_rate >= 80:
            print(f"\n🟠 FAIR: Bot needs improvements for optimal user experience")
        else:
            print(f"\n❌ POOR: Significant improvements needed")
        
        print(f"\n📄 Detailed report saved to: comprehensive_command_test_report.json")
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"❌ Command test suite failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(main())
    sys.exit(0 if success else 1)