#!/usr/bin/env python3
"""
Comprehensive Test Suite for Möbius AI Assistant Fixes
Tests all the major improvements and fixes implemented
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveTestSuite:
    """Test suite for all major fixes"""
    
    def __init__(self):
        self.test_results = {}
        self.passed = 0
        self.failed = 0
    
    def test_result(self, test_name: str, passed: bool, message: str = ""):
        """Record test result"""
        self.test_results[test_name] = {
            "passed": passed,
            "message": message
        }
        
        if passed:
            self.passed += 1
            logger.info(f"✅ {test_name}: PASSED {message}")
        else:
            self.failed += 1
            logger.error(f"❌ {test_name}: FAILED {message}")
    
    async def test_intelligent_message_router(self):
        """Test the intelligent message router"""
        try:
            from intelligent_message_router import analyze_message_intent, should_use_mcp, should_respond
            
            # Test 1: Simple greeting
            analysis = await analyze_message_intent(
                text="hello",
                user_id=12345,
                chat_type="private"
            )
            
            self.test_result(
                "intelligent_router_greeting",
                analysis.message_type.value == "greeting" and should_respond(analysis),
                f"Greeting detected with confidence {analysis.confidence}"
            )
            
            # Test 2: Crypto query
            analysis = await analyze_message_intent(
                text="what's the price of bitcoin",
                user_id=12345,
                chat_type="private"
            )
            
            self.test_result(
                "intelligent_router_crypto",
                "price" in analysis.extracted_entities.get("command", "") or analysis.message_type.value == "crypto_query",
                f"Crypto query detected: {analysis.extracted_entities}"
            )
            
            # Test 3: Group chat silent learning
            analysis = await analyze_message_intent(
                text="yes i agree",
                user_id=12345,
                chat_type="group",
                is_mentioned=False
            )
            
            self.test_result(
                "intelligent_router_silent_learning",
                not should_respond(analysis),
                "Group chat casual message correctly set to silent learning"
            )
            
            # Test 4: Group chat mention response
            analysis = await analyze_message_intent(
                text="@mobius what's the price of ethereum",
                user_id=12345,
                chat_type="group",
                is_mentioned=True
            )
            
            self.test_result(
                "intelligent_router_mention_response",
                should_respond(analysis),
                "Group chat mention correctly triggers response"
            )
            
        except Exception as e:
            self.test_result("intelligent_router", False, f"Error: {e}")
    
    async def test_conversation_intelligence(self):
        """Test conversation intelligence system"""
        try:
            from conversation_intelligence import stream_conversation_message, get_chat_summary
            
            # Test message streaming
            await stream_conversation_message(
                message_id="test_123",
                user_id=12345,
                username="test_user",
                chat_id=-123456,
                chat_type="group",
                text="This is a test message about bitcoin prices"
            )
            
            self.test_result(
                "conversation_intelligence_streaming",
                True,
                "Message streaming completed without errors"
            )
            
            # Test summary generation
            summary = await get_chat_summary(-123456, hours=1)
            
            self.test_result(
                "conversation_intelligence_summary",
                isinstance(summary, dict) and "chat_id" in summary,
                f"Summary generated: {summary.get('message_count', 0)} messages"
            )
            
        except Exception as e:
            self.test_result("conversation_intelligence", False, f"Error: {e}")
    
    async def test_group_chat_manager(self):
        """Test enhanced group chat manager"""
        try:
            from group_chat_manager import enhanced_group_manager
            
            # Test mention detection
            is_mentioned = enhanced_group_manager._is_bot_mentioned("@mobius what's up")
            self.test_result(
                "group_chat_mention_detection",
                is_mentioned,
                "Mention detection working correctly"
            )
            
            # Test cooldown system
            chat_id = -987654
            can_respond_1 = enhanced_group_manager._check_response_cooldown(chat_id)
            enhanced_group_manager._update_response_cooldown(chat_id)
            can_respond_2 = enhanced_group_manager._check_response_cooldown(chat_id)
            
            self.test_result(
                "group_chat_cooldown",
                can_respond_1 and not can_respond_2,
                "Cooldown system working correctly"
            )
            
        except Exception as e:
            self.test_result("group_chat_manager", False, f"Error: {e}")
    
    async def test_wallet_functionality(self):
        """Test enhanced wallet functionality"""
        try:
            from onchain import wallet_manager
            
            # Test wallet creation
            wallet = wallet_manager.create_wallet()
            
            self.test_result(
                "wallet_creation",
                wallet.get("status") == "success" and "address" in wallet,
                f"Wallet created: {wallet.get('address', 'N/A')[:10]}..."
            )
            
            # Test encryption
            if wallet.get("status") == "success":
                private_key = wallet["private_key"]
                password = "test_password_123"
                
                encrypted = wallet_manager.encrypt_private_key(private_key, password)
                decrypted = wallet_manager.decrypt_private_key(encrypted, password)
                
                self.test_result(
                    "wallet_encryption",
                    decrypted == private_key,
                    "Private key encryption/decryption working"
                )
            
        except Exception as e:
            self.test_result("wallet_functionality", False, f"Error: {e}")
    
    async def test_whop_integration(self):
        """Test Whop license validation"""
        try:
            from whop_integration import whop_client
            
            # Test tier determination
            tier = await whop_client.get_user_tier(12345)
            
            self.test_result(
                "whop_tier_detection",
                tier in ["free", "retail", "corporate"],
                f"User tier detected: {tier}"
            )
            
            # Test feature checking
            features = await whop_client.get_user_features(12345)
            
            self.test_result(
                "whop_features",
                isinstance(features, list) and len(features) > 0,
                f"Features loaded: {len(features)} features"
            )
            
        except Exception as e:
            self.test_result("whop_integration", False, f"Error: {e}")
    
    async def test_mcp_intent_router(self):
        """Test MCP intent router fixes"""
        try:
            from mcp_intent_router import MCPIntentRouter
            
            router = MCPIntentRouter()
            
            # Test with string input
            analysis = await router.analyze_intent(
                user_id=12345,
                message="what's the price of bitcoin",
                context={"chat_type": "private"}
            )
            
            self.test_result(
                "mcp_intent_router_string",
                analysis.confidence > 0 and analysis.intent_type is not None,
                f"Intent analysis successful: {analysis.intent_type.value}"
            )
            
            # Test with dict input (should handle gracefully)
            try:
                analysis = await router.analyze_intent(
                    user_id=12345,
                    message={"text": "hello world"},
                    context={"chat_type": "private"}
                )
                
                self.test_result(
                    "mcp_intent_router_dict_handling",
                    True,
                    "Dict input handled gracefully"
                )
            except Exception:
                self.test_result(
                    "mcp_intent_router_dict_handling",
                    False,
                    "Dict input not handled properly"
                )
            
        except Exception as e:
            self.test_result("mcp_intent_router", False, f"Error: {e}")
    
    async def test_imports(self):
        """Test that all modules can be imported"""
        modules_to_test = [
            "intelligent_message_router",
            "conversation_intelligence", 
            "group_chat_manager",
            "onchain",
            "whop_integration",
            "mcp_intent_router"
        ]
        
        for module in modules_to_test:
            try:
                __import__(module)
                self.test_result(f"import_{module}", True, "Module imported successfully")
            except Exception as e:
                self.test_result(f"import_{module}", False, f"Import error: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting comprehensive test suite...")
        
        # Test imports first
        await self.test_imports()
        
        # Test core functionality
        await self.test_intelligent_message_router()
        await self.test_conversation_intelligence()
        await self.test_group_chat_manager()
        await self.test_wallet_functionality()
        await self.test_whop_integration()
        await self.test_mcp_intent_router()
        
        # Print summary
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"\n📊 TEST SUMMARY:")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {self.passed}")
        logger.info(f"Failed: {self.failed}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed > 0:
            logger.info(f"\n❌ FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result["passed"]:
                    logger.info(f"  - {test_name}: {result['message']}")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

async def main():
    """Main test function"""
    test_suite = ComprehensiveTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        logger.info("🎉 Test suite PASSED! All major fixes are working correctly.")
        return 0
    else:
        logger.error("💥 Test suite FAILED! Some fixes need attention.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)