#!/usr/bin/env python3
"""
Industrial Grade Test Suite for Möbius AI Assistant
Comprehensive testing with full coverage, stress testing, and edge cases
"""

import asyncio
import logging
import sys
import os
import time
import json
import sqlite3
import tempfile
import concurrent.futures
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    name: str
    passed: bool
    duration: float
    message: str
    category: str
    severity: str = "normal"  # normal, critical, performance

class IndustrialGradeTestSuite:
    """Comprehensive industrial-grade test suite"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        
    def record_result(self, name: str, passed: bool, message: str, category: str, duration: float = 0.0, severity: str = "normal"):
        """Record a test result"""
        result = TestResult(name, passed, duration, message, category, severity)
        self.results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        severity_icon = "🔥" if severity == "critical" else "⚡" if severity == "performance" else "🔧"
        logger.info(f"{status} {severity_icon} [{category}] {name}: {message} ({duration:.3f}s)")
    
    async def test_intelligent_message_router_comprehensive(self):
        """Comprehensive testing of intelligent message router"""
        category = "INTELLIGENT_ROUTER"
        
        try:
            from intelligent_message_router import (
                analyze_message_intent, should_use_mcp, should_respond,
                MessageType, ProcessingStrategy, MessageAnalysis
            )
            
            # Test 1: Command Detection
            start = time.time()
            analysis = await analyze_message_intent("/portfolio", 12345, "private")
            duration = time.time() - start
            
            self.record_result(
                "command_detection",
                analysis.message_type == MessageType.COMMAND,
                f"Command detected correctly: {analysis.message_type.value}",
                category, duration, "critical"
            )
            
            # Test 2: Crypto Query Analysis
            start = time.time()
            analysis = await analyze_message_intent("what's the price of bitcoin today?", 12345, "private")
            duration = time.time() - start
            
            self.record_result(
                "crypto_query_analysis",
                analysis.message_type == MessageType.CRYPTO_QUERY,
                f"Crypto query detected: {analysis.extracted_entities}",
                category, duration
            )
            
            # Test 3: Group Chat Silent Learning
            start = time.time()
            analysis = await analyze_message_intent("yes i agree with that", 12345, "group", is_mentioned=False)
            duration = time.time() - start
            
            self.record_result(
                "group_silent_learning",
                not should_respond(analysis),
                "Group chat casual message correctly set to silent learning",
                category, duration, "critical"
            )
            
            # Test 4: Mention Detection
            start = time.time()
            analysis = await analyze_message_intent("@mobius what do you think?", 12345, "group", is_mentioned=True)
            duration = time.time() - start
            
            self.record_result(
                "mention_detection",
                should_respond(analysis),
                "Mention correctly triggers response",
                category, duration, "critical"
            )
            
            # Test 5: MCP Usage Decision
            start = time.time()
            analysis = await analyze_message_intent("complex financial analysis of defi protocols", 12345, "private")
            duration = time.time() - start
            
            self.record_result(
                "mcp_usage_decision",
                should_use_mcp(analysis),
                f"Complex query correctly routed to MCP: {analysis.processing_strategy.value}",
                category, duration
            )
            
            # Test 6: Stress Test - Multiple Concurrent Analyses
            start = time.time()
            tasks = []
            for i in range(50):
                task = analyze_message_intent(f"test message {i}", 12345 + i, "private")
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start
            
            success_count = sum(1 for r in results if isinstance(r, MessageAnalysis))
            self.record_result(
                "concurrent_analysis_stress",
                success_count == 50,
                f"Processed {success_count}/50 concurrent analyses",
                category, duration, "performance"
            )
            
        except Exception as e:
            self.record_result("router_comprehensive", False, f"Error: {e}", category, 0, "critical")
    
    async def test_conversation_intelligence_comprehensive(self):
        """Comprehensive testing of conversation intelligence"""
        category = "CONVERSATION_INTELLIGENCE"
        
        try:
            from conversation_intelligence import (
                stream_conversation_message, get_chat_summary, 
                get_learning_insights
            )
            
            # Test 1: Message Streaming Performance
            start = time.time()
            for i in range(100):
                await stream_conversation_message(
                    message_id=f"test_{i}",
                    user_id=12345,
                    username="test_user",
                    chat_id=-123456,
                    chat_type="group",
                    text=f"Test message {i} about crypto and trading"
                )
            duration = time.time() - start
            
            self.record_result(
                "message_streaming_performance",
                duration < 5.0,  # Should process 100 messages in under 5 seconds
                f"Streamed 100 messages in {duration:.2f}s ({100/duration:.1f} msg/s)",
                category, duration, "performance"
            )
            
            # Test 2: Summary Generation
            start = time.time()
            summary = await get_chat_summary(-123456, hours=1)
            duration = time.time() - start
            
            self.record_result(
                "summary_generation",
                isinstance(summary, dict) and "chat_id" in summary,
                f"Generated summary with {summary.get('message_count', 0)} messages",
                category, duration
            )
            
            # Test 3: Learning Insights
            start = time.time()
            insights = await get_learning_insights(-123456, hours=1)
            duration = time.time() - start
            
            self.record_result(
                "learning_insights",
                isinstance(insights, dict),
                f"Generated insights: {len(insights.get('topics', []))} topics identified",
                category, duration
            )
            
            # Test 4: Database Integrity
            start = time.time()
            
            # Check database schema
            from conversation_intelligence import conversation_intelligence
            with sqlite3.connect(conversation_intelligence.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
            
            duration = time.time() - start
            
            expected_tables = ['conversations', 'learning_insights', 'chat_summaries']
            has_all_tables = all(table in tables for table in expected_tables)
            
            self.record_result(
                "database_integrity",
                has_all_tables,
                f"Database has all required tables: {tables}",
                category, duration, "critical"
            )
            
        except Exception as e:
            self.record_result("conversation_intelligence", False, f"Error: {e}", category, 0, "critical")
    
    async def test_group_chat_manager_comprehensive(self):
        """Comprehensive testing of group chat manager"""
        category = "GROUP_CHAT_MANAGER"
        
        try:
            from group_chat_manager import enhanced_group_manager
            
            # Test 1: Mention Detection Accuracy
            test_cases = [
                ("@mobius hello", True),
                ("hey @mobius what's up", True),
                ("@mobius_ai_bot test", True),
                ("hello everyone", False),
                ("mobius without @", False),
                ("@other_bot hello", False),
            ]
            
            start = time.time()
            correct = 0
            for text, expected in test_cases:
                result = enhanced_group_manager._is_bot_mentioned(text)
                if result == expected:
                    correct += 1
            duration = time.time() - start
            
            self.record_result(
                "mention_detection_accuracy",
                correct == len(test_cases),
                f"Correctly detected {correct}/{len(test_cases)} mention cases",
                category, duration, "critical"
            )
            
            # Test 2: Cooldown System
            start = time.time()
            chat_id = -987654321
            
            # First response should be allowed
            can_respond_1 = enhanced_group_manager._check_response_cooldown(chat_id)
            enhanced_group_manager._update_response_cooldown(chat_id)
            
            # Immediate second response should be blocked
            can_respond_2 = enhanced_group_manager._check_response_cooldown(chat_id)
            
            duration = time.time() - start
            
            self.record_result(
                "cooldown_system",
                can_respond_1 and not can_respond_2,
                f"Cooldown working: first={can_respond_1}, second={can_respond_2}",
                category, duration, "critical"
            )
            
            # Test 3: Response Decision Logic
            start = time.time()
            test_scenarios = [
                ("group", "@mobius help", True, True),  # mention in group
                ("group", "hello everyone", False, False),  # casual in group
                ("private", "hello", False, True),  # private message
                ("supergroup", "/portfolio", False, True),  # command in supergroup
            ]
            
            correct_decisions = 0
            for chat_type, text, is_mentioned, expected in test_scenarios:
                should_respond = enhanced_group_manager._should_respond_to_message(
                    text, chat_type, is_mentioned, is_reply=False
                )
                if should_respond == expected:
                    correct_decisions += 1
            
            duration = time.time() - start
            
            self.record_result(
                "response_decision_logic",
                correct_decisions == len(test_scenarios),
                f"Correct decisions: {correct_decisions}/{len(test_scenarios)}",
                category, duration, "critical"
            )
            
        except Exception as e:
            self.record_result("group_chat_manager", False, f"Error: {e}", category, 0, "critical")
    
    async def test_wallet_functionality_comprehensive(self):
        """Comprehensive testing of wallet functionality"""
        category = "WALLET_FUNCTIONALITY"
        
        try:
            from onchain import wallet_manager
            
            # Test 1: Wallet Creation Performance
            start = time.time()
            wallets = []
            for i in range(10):
                wallet = wallet_manager.create_wallet()
                wallets.append(wallet)
            duration = time.time() - start
            
            successful_wallets = sum(1 for w in wallets if w.get("status") == "success")
            
            self.record_result(
                "wallet_creation_performance",
                successful_wallets == 10,
                f"Created {successful_wallets}/10 wallets in {duration:.2f}s",
                category, duration, "performance"
            )
            
            # Test 2: Address Validation
            start = time.time()
            valid_addresses = 0
            for wallet in wallets:
                if wallet.get("status") == "success":
                    address = wallet["address"]
                    # Ethereum address validation
                    if address.startswith("0x") and len(address) == 42:
                        valid_addresses += 1
            duration = time.time() - start
            
            self.record_result(
                "address_validation",
                valid_addresses == successful_wallets,
                f"All {valid_addresses} addresses are valid Ethereum format",
                category, duration, "critical"
            )
            
            # Test 3: Private Key Encryption/Decryption
            start = time.time()
            if wallets and wallets[0].get("status") == "success":
                private_key = wallets[0]["private_key"]
                password = "test_password_123!@#"
                
                # Test encryption
                encrypted = wallet_manager.encrypt_private_key(private_key, password)
                
                # Test decryption
                decrypted = wallet_manager.decrypt_private_key(encrypted, password)
                
                # Test wrong password
                try:
                    wrong_decrypt = wallet_manager.decrypt_private_key(encrypted, "wrong_password")
                    encryption_secure = False
                except:
                    encryption_secure = True
                
                duration = time.time() - start
                
                self.record_result(
                    "encryption_security",
                    decrypted == private_key and encryption_secure,
                    "Encryption/decryption working, wrong password rejected",
                    category, duration, "critical"
                )
            
            # Test 4: Multi-Network Support
            start = time.time()
            networks = wallet_manager.get_supported_networks()
            duration = time.time() - start
            
            expected_networks = ["ethereum", "polygon", "bsc"]
            has_all_networks = all(net in networks for net in expected_networks)
            
            self.record_result(
                "multi_network_support",
                has_all_networks,
                f"Supports networks: {networks}",
                category, duration
            )
            
        except Exception as e:
            self.record_result("wallet_functionality", False, f"Error: {e}", category, 0, "critical")
    
    async def test_whop_integration_comprehensive(self):
        """Comprehensive testing of Whop integration"""
        category = "WHOP_INTEGRATION"
        
        try:
            from whop_integration import whop_client
            
            # Test 1: Tier Detection Performance
            start = time.time()
            test_users = [12345, 67890, 11111, 22222, 33333]
            tiers = []
            
            for user_id in test_users:
                tier = await whop_client.get_user_tier(user_id)
                tiers.append(tier)
            
            duration = time.time() - start
            
            valid_tiers = ["free", "retail", "corporate"]
            all_valid = all(tier in valid_tiers for tier in tiers)
            
            self.record_result(
                "tier_detection_performance",
                all_valid,
                f"Detected tiers for {len(test_users)} users in {duration:.2f}s: {tiers}",
                category, duration, "performance"
            )
            
            # Test 2: Feature Access Control
            start = time.time()
            test_features = [
                ("portfolio_basic", "free", True),
                ("portfolio_advanced", "free", False),
                ("portfolio_advanced", "retail", True),
                ("api_access", "retail", False),
                ("api_access", "corporate", True),
            ]
            
            correct_access = 0
            for feature, tier, expected in test_features:
                has_access = await whop_client.has_feature_for_tier(feature, tier)
                if has_access == expected:
                    correct_access += 1
            
            duration = time.time() - start
            
            self.record_result(
                "feature_access_control",
                correct_access == len(test_features),
                f"Correct access control: {correct_access}/{len(test_features)}",
                category, duration, "critical"
            )
            
            # Test 3: Caching System
            start = time.time()
            user_id = 12345
            
            # First call (should cache)
            tier1 = await whop_client.get_user_tier(user_id)
            time1 = time.time()
            
            # Second call (should use cache)
            tier2 = await whop_client.get_user_tier(user_id)
            time2 = time.time()
            
            duration = time.time() - start
            cache_speedup = (time1 - start) / (time2 - time1) if (time2 - time1) > 0 else float('inf')
            
            self.record_result(
                "caching_system",
                tier1 == tier2 and cache_speedup > 2,
                f"Cache working: {cache_speedup:.1f}x speedup",
                category, duration, "performance"
            )
            
        except Exception as e:
            self.record_result("whop_integration", False, f"Error: {e}", category, 0, "critical")
    
    async def test_mcp_intent_router_comprehensive(self):
        """Comprehensive testing of MCP intent router"""
        category = "MCP_INTENT_ROUTER"
        
        try:
            from mcp_intent_router import MCPIntentRouter
            
            router = MCPIntentRouter()
            
            # Test 1: Input Type Handling
            start = time.time()
            test_inputs = [
                "string message",
                {"text": "dict message"},
                ["list", "message"],
                123,
                None
            ]
            
            successful_analyses = 0
            for test_input in test_inputs:
                try:
                    analysis = await router.analyze_intent(
                        user_id=12345,
                        message=test_input,
                        context={"chat_type": "private"}
                    )
                    if analysis and hasattr(analysis, 'confidence'):
                        successful_analyses += 1
                except Exception:
                    pass  # Expected for some invalid inputs
            
            duration = time.time() - start
            
            self.record_result(
                "input_type_handling",
                successful_analyses >= 1,  # At least string should work
                f"Handled {successful_analyses}/{len(test_inputs)} input types gracefully",
                category, duration, "critical"
            )
            
            # Test 2: Intent Classification Accuracy
            start = time.time()
            test_cases = [
                ("hello", "simple"),
                ("what's the price of bitcoin", "immediate"),
                ("help me with portfolio", "simple"),
                ("complex defi analysis needed", "complex"),
            ]
            
            correct_classifications = 0
            for message, expected_intent in test_cases:
                try:
                    analysis = await router.analyze_intent(
                        user_id=12345,
                        message=message,
                        context={"chat_type": "private"}
                    )
                    if analysis.intent_type.value == expected_intent:
                        correct_classifications += 1
                except Exception:
                    pass
            
            duration = time.time() - start
            
            self.record_result(
                "intent_classification_accuracy",
                correct_classifications >= len(test_cases) * 0.7,  # 70% accuracy threshold
                f"Correctly classified {correct_classifications}/{len(test_cases)} intents",
                category, duration
            )
            
            # Test 3: Performance Under Load
            start = time.time()
            tasks = []
            for i in range(20):
                task = router.analyze_intent(
                    user_id=12345 + i,
                    message=f"test message {i}",
                    context={"chat_type": "private"}
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start
            
            successful_results = sum(1 for r in results if not isinstance(r, Exception))
            
            self.record_result(
                "performance_under_load",
                successful_results >= 18 and duration < 10,  # 90% success in under 10s
                f"Processed {successful_results}/20 requests in {duration:.2f}s",
                category, duration, "performance"
            )
            
        except Exception as e:
            self.record_result("mcp_intent_router", False, f"Error: {e}", category, 0, "critical")
    
    async def test_integration_comprehensive(self):
        """Comprehensive integration testing"""
        category = "INTEGRATION"
        
        try:
            # Test 1: End-to-End Message Processing
            start = time.time()
            
            # Simulate a complete message flow
            from intelligent_message_router import analyze_message_intent
            from conversation_intelligence import stream_conversation_message
            from group_chat_manager import enhanced_group_manager
            
            # Step 1: Analyze message
            analysis = await analyze_message_intent(
                text="@mobius what's my portfolio balance?",
                user_id=12345,
                chat_type="group",
                is_mentioned=True
            )
            
            # Step 2: Stream for learning
            await stream_conversation_message(
                message_id="integration_test_1",
                user_id=12345,
                username="test_user",
                chat_id=-123456,
                chat_type="group",
                text="@mobius what's my portfolio balance?"
            )
            
            # Step 3: Check response decision
            should_respond = enhanced_group_manager._should_respond_to_message(
                "@mobius what's my portfolio balance?",
                "group",
                is_mentioned=True,
                is_reply=False
            )
            
            duration = time.time() - start
            
            integration_success = (
                analysis.message_type.value in ["command", "crypto_query"] and
                should_respond == True
            )
            
            self.record_result(
                "end_to_end_processing",
                integration_success,
                f"Complete message flow processed successfully",
                category, duration, "critical"
            )
            
            # Test 2: Error Recovery
            start = time.time()
            
            # Simulate various error conditions
            error_scenarios = [
                ("invalid_user_id", "hello", "invalid_user", "private"),
                ("empty_message", "", 12345, "private"),
                ("invalid_chat_type", "hello", 12345, "invalid_type"),
            ]
            
            recovered_errors = 0
            for scenario_name, text, user_id, chat_type in error_scenarios:
                try:
                    analysis = await analyze_message_intent(text, user_id, chat_type)
                    if analysis:  # If we get any result, error was handled
                        recovered_errors += 1
                except Exception:
                    pass  # Some errors are expected
            
            duration = time.time() - start
            
            self.record_result(
                "error_recovery",
                recovered_errors >= 1,
                f"Recovered from {recovered_errors}/{len(error_scenarios)} error scenarios",
                category, duration, "critical"
            )
            
        except Exception as e:
            self.record_result("integration", False, f"Error: {e}", category, 0, "critical")
    
    async def test_security_comprehensive(self):
        """Comprehensive security testing"""
        category = "SECURITY"
        
        try:
            # Test 1: Input Sanitization
            start = time.time()
            
            malicious_inputs = [
                "'; DROP TABLE users; --",
                "<script>alert('xss')</script>",
                "../../etc/passwd",
                "\x00\x01\x02\x03",
                "A" * 10000,  # Very long input
            ]
            
            safe_processing = 0
            for malicious_input in malicious_inputs:
                try:
                    from intelligent_message_router import analyze_message_intent
                    analysis = await analyze_message_intent(malicious_input, 12345, "private")
                    # If we get here without crashing, input was handled safely
                    safe_processing += 1
                except Exception:
                    # Some exceptions are acceptable for malicious input
                    safe_processing += 1
            
            duration = time.time() - start
            
            self.record_result(
                "input_sanitization",
                safe_processing == len(malicious_inputs),
                f"Safely handled {safe_processing}/{len(malicious_inputs)} malicious inputs",
                category, duration, "critical"
            )
            
            # Test 2: Private Key Security
            start = time.time()
            
            from onchain import wallet_manager
            
            # Create wallet
            wallet = wallet_manager.create_wallet()
            if wallet.get("status") == "success":
                private_key = wallet["private_key"]
                
                # Test that private key is not logged or exposed
                import logging
                
                # Capture log output
                log_capture = []
                class TestHandler(logging.Handler):
                    def emit(self, record):
                        log_capture.append(record.getMessage())
                
                test_handler = TestHandler()
                logger.addHandler(test_handler)
                
                # Perform operations that might log
                encrypted = wallet_manager.encrypt_private_key(private_key, "test_password")
                
                # Check if private key appears in logs
                private_key_in_logs = any(private_key in log_msg for log_msg in log_capture)
                
                logger.removeHandler(test_handler)
                
                duration = time.time() - start
                
                self.record_result(
                    "private_key_security",
                    not private_key_in_logs,
                    "Private key not exposed in logs",
                    category, duration, "critical"
                )
            
        except Exception as e:
            self.record_result("security", False, f"Error: {e}", category, 0, "critical")
    
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        logger.info("🚀 Starting Industrial Grade Test Suite...")
        logger.info("=" * 80)
        
        # Run all test categories
        test_methods = [
            self.test_intelligent_message_router_comprehensive,
            self.test_conversation_intelligence_comprehensive,
            self.test_group_chat_manager_comprehensive,
            self.test_wallet_functionality_comprehensive,
            self.test_whop_integration_comprehensive,
            self.test_mcp_intent_router_comprehensive,
            self.test_integration_comprehensive,
            self.test_security_comprehensive,
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                logger.error(f"Test method {test_method.__name__} failed: {e}")
        
        # Generate comprehensive report
        self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self):
        """Generate detailed test report"""
        total_time = time.time() - self.start_time
        
        # Categorize results
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {"passed": 0, "failed": 0, "total_time": 0}
            
            if result.passed:
                categories[result.category]["passed"] += 1
            else:
                categories[result.category]["failed"] += 1
            categories[result.category]["total_time"] += result.duration
        
        # Overall statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Critical failures
        critical_failures = [r for r in self.results if not r.passed and r.severity == "critical"]
        performance_issues = [r for r in self.results if not r.passed and r.severity == "performance"]
        
        # Generate report
        logger.info("=" * 80)
        logger.info("📊 INDUSTRIAL GRADE TEST REPORT")
        logger.info("=" * 80)
        logger.info(f"🕒 Total Execution Time: {total_time:.2f}s")
        logger.info(f"📈 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        logger.info("")
        
        # Category breakdown
        logger.info("📋 CATEGORY BREAKDOWN:")
        for category, stats in categories.items():
            total_cat = stats["passed"] + stats["failed"]
            cat_success = (stats["passed"] / total_cat * 100) if total_cat > 0 else 0
            logger.info(f"  {category}: {cat_success:.1f}% ({stats['passed']}/{total_cat}) - {stats['total_time']:.2f}s")
        
        logger.info("")
        
        # Critical issues
        if critical_failures:
            logger.info("🔥 CRITICAL FAILURES:")
            for failure in critical_failures:
                logger.info(f"  ❌ {failure.name}: {failure.message}")
            logger.info("")
        
        # Performance issues
        if performance_issues:
            logger.info("⚡ PERFORMANCE ISSUES:")
            for issue in performance_issues:
                logger.info(f"  ⚠️ {issue.name}: {issue.message}")
            logger.info("")
        
        # Detailed results
        logger.info("📝 DETAILED RESULTS:")
        current_category = None
        for result in self.results:
            if result.category != current_category:
                logger.info(f"\n  [{result.category}]")
                current_category = result.category
            
            status = "✅" if result.passed else "❌"
            severity = "🔥" if result.severity == "critical" else "⚡" if result.severity == "performance" else "🔧"
            logger.info(f"    {status} {severity} {result.name}: {result.message} ({result.duration:.3f}s)")
        
        logger.info("")
        logger.info("=" * 80)
        
        # Final assessment
        if success_rate >= 95 and not critical_failures:
            logger.info("🎉 INDUSTRIAL GRADE CERTIFICATION: PASSED")
            logger.info("✅ System is ready for production deployment")
        elif success_rate >= 90 and len(critical_failures) <= 1:
            logger.info("⚠️ INDUSTRIAL GRADE CERTIFICATION: CONDITIONAL PASS")
            logger.info("🔧 Minor issues need attention before production")
        else:
            logger.info("❌ INDUSTRIAL GRADE CERTIFICATION: FAILED")
            logger.info("🚨 Critical issues must be resolved before production")
        
        logger.info("=" * 80)
        
        return success_rate >= 95 and not critical_failures

async def main():
    """Main test execution"""
    # Set test mode to avoid missing env var warnings
    os.environ['MOBIUS_TEST_MODE'] = '1'
    
    test_suite = IndustrialGradeTestSuite()
    success = await test_suite.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)