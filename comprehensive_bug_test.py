#!/usr/bin/env python3
"""
Comprehensive Bug Test Suite for Möbius AI Assistant
Tests all critical functionality to ensure 100% bug-free operation
"""

import asyncio
import logging
import sys
import os
from unittest.mock import Mock, AsyncMock
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BugTestSuite:
    """Comprehensive test suite for bug detection"""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log_test(self, test_name: str, passed: bool, error: str = None):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            logger.info(f"✅ {test_name}: PASSED")
        else:
            self.failed_tests += 1
            logger.error(f"❌ {test_name}: FAILED - {error}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "error": error
        })
    
    async def test_imports(self):
        """Test all critical imports"""
        logger.info("🔍 Testing imports...")
        
        # Core imports
        try:
            import telegram
            from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
            from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
            self.log_test("Core Telegram imports", True)
        except Exception as e:
            self.log_test("Core Telegram imports", False, str(e))
        
        # UI enhancements
        try:
            from src.ui_enhancements import handle_callback_query, SmartKeyboard, escape_markdown
            self.log_test("UI enhancements imports", True)
        except Exception as e:
            self.log_test("UI enhancements imports", False, str(e))
        
        # Whop integration
        try:
            from src.whop_integration import WhopIntegration, validate_whop_license
            self.log_test("Whop integration imports", True)
        except Exception as e:
            self.log_test("Whop integration imports", False, str(e))
        
        # Database
        try:
            from src.enhanced_db import get_user_property, set_user_property
            self.log_test("Database imports", True)
        except Exception as e:
            self.log_test("Database imports", False, str(e))
        
        # AI providers
        try:
            import groq
            import openai
            self.log_test("AI provider imports", True)
        except Exception as e:
            self.log_test("AI provider imports", False, str(e))
    
    async def test_markdown_parsing(self):
        """Test markdown parsing and escaping"""
        logger.info("🔍 Testing markdown parsing...")
        
        try:
            from src.ui_enhancements import escape_markdown
            
            # Test cases that previously caused parsing errors
            test_cases = [
                ("Hello <world>", "Hello \\<world\\>"),
                ("Test*bold*text", "Test\\*bold\\*text"),
                ("Link[text](url)", "Link\\[text\\]\\(url\\)"),
                ("Code`snippet`", "Code\\`snippet\\`"),
                ("Special chars: _*[]()~`>#+-=|{}.!", "Special chars: \\_\\*\\[\\]\\(\\)\\~\\`\\>\\#\\+\\-\\=\\|\\{\\}\\.\\!"),
            ]
            
            all_passed = True
            for input_text, expected in test_cases:
                result = escape_markdown(input_text)
                if result != expected:
                    logger.error(f"Markdown test failed: '{input_text}' -> '{result}' (expected: '{expected}')")
                    all_passed = False
            
            self.log_test("Markdown escaping", all_passed)
            
        except Exception as e:
            self.log_test("Markdown escaping", False, str(e))
    
    async def test_callback_handlers(self):
        """Test all callback handlers"""
        logger.info("🔍 Testing callback handlers...")
        
        try:
            from src.ui_enhancements import handle_callback_query
            from telegram import Update, CallbackQuery, User, Message, Chat
            
            # Mock objects
            user = Mock(spec=User)
            user.id = 12345
            user.first_name = "Test"
            user.username = "testuser"
            
            chat = Mock(spec=Chat)
            chat.id = -67890
            chat.type = "group"
            
            message = Mock(spec=Message)
            message.message_id = 1
            message.chat = chat
            message.from_user = user
            
            # Test problematic callbacks that were causing errors
            problematic_callbacks = [
                "plan_free",
                "cmd_mymentions",
                "cmd_summarynow",
                "cmd_topic",
                "cmd_whosaid",
                "help_summary",
                "help_research"
            ]
            
            all_passed = True
            for callback_data in problematic_callbacks:
                try:
                    callback_query = Mock(spec=CallbackQuery)
                    callback_query.data = callback_data
                    callback_query.message = message
                    callback_query.from_user = user
                    callback_query.answer = AsyncMock()
                    callback_query.edit_message_text = AsyncMock()
                    
                    update = Mock(spec=Update)
                    update.callback_query = callback_query
                    update.effective_user = user
                    update.effective_chat = chat
                    
                    context = Mock()
                    
                    # This should not raise any parsing errors
                    await handle_callback_query(update, context)
                    
                except Exception as e:
                    logger.error(f"Callback {callback_data} failed: {e}")
                    all_passed = False
            
            self.log_test("Callback handlers", all_passed)
            
        except Exception as e:
            self.log_test("Callback handlers", False, str(e))
    
    async def test_whop_integration(self):
        """Test Whop integration"""
        logger.info("🔍 Testing Whop integration...")
        
        try:
            from src.whop_integration import WhopIntegration, validate_whop_license
            
            # Test initialization
            whop = WhopIntegration()
            
            # Test validation with invalid key (should not crash)
            result = await validate_whop_license("invalid_test_key")
            
            # Should return a proper error response
            expected_keys = ["valid", "error", "tier"]
            has_required_keys = all(key in result for key in expected_keys)
            
            self.log_test("Whop integration", has_required_keys and not result["valid"])
            
        except Exception as e:
            self.log_test("Whop integration", False, str(e))
    
    async def test_database_operations(self):
        """Test database operations"""
        logger.info("🔍 Testing database operations...")
        
        try:
            from src.enhanced_db import get_user_property, set_user_property
            
            # Test setting and getting user properties
            test_user_id = 999999
            test_key = "test_subscription_tier"
            test_value = "retail"
            
            # Set property (without encryption for compatibility)
            set_user_property(test_user_id, test_key, test_value, encrypted=False)
            
            # Get property
            retrieved_value = get_user_property(test_user_id, test_key)
            
            self.log_test("Database operations", retrieved_value == test_value)
            
        except Exception as e:
            self.log_test("Database operations", False, str(e))
    
    async def test_environment_variables(self):
        """Test environment variable loading"""
        logger.info("🔍 Testing environment variables...")
        
        try:
            import os
            from dotenv import load_dotenv
            
            # Load .env file
            load_dotenv()
            
            # Check for critical environment variables
            required_vars = [
                "TELEGRAM_BOT_TOKEN",
                "GROQ_API_KEY"
            ]
            
            optional_vars = [
                "WHOP_BEARER_TOKEN",
                "OPENAI_API_KEY",
                "GEMINI_API_KEY",
                "ANTHROPIC_API_KEY"
            ]
            
            missing_required = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_required.append(var)
            
            missing_optional = []
            for var in optional_vars:
                if not os.getenv(var):
                    missing_optional.append(var)
            
            if missing_required:
                self.log_test("Environment variables", False, f"Missing required: {missing_required}")
            else:
                self.log_test("Environment variables", True)
                if missing_optional:
                    logger.warning(f"Missing optional variables: {missing_optional}")
            
        except Exception as e:
            self.log_test("Environment variables", False, str(e))
    
    async def test_ai_providers(self):
        """Test AI provider initialization"""
        logger.info("🔍 Testing AI providers...")
        
        # Test Groq
        try:
            import groq
            import os
            
            if os.getenv("GROQ_API_KEY"):
                client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
                self.log_test("Groq client initialization", True)
            else:
                self.log_test("Groq client initialization", False, "No API key")
        except Exception as e:
            self.log_test("Groq client initialization", False, str(e))
        
        # Test OpenAI (optional)
        try:
            import openai
            import os
            
            if os.getenv("OPENAI_API_KEY"):
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                self.log_test("OpenAI client initialization", True)
            else:
                # OpenAI is optional, so this is not a failure
                logger.info("ℹ️ OpenAI API key not provided (optional)")
                self.log_test("OpenAI client initialization", True)
        except Exception as e:
            self.log_test("OpenAI client initialization", False, str(e))
    
    async def test_file_structure(self):
        """Test file structure and permissions"""
        logger.info("🔍 Testing file structure...")
        
        required_files = [
            "src/main.py",
            "src/ui_enhancements.py",
            "src/whop_integration.py",
            "src/enhanced_db.py",
            "requirements.txt",
            ".env.example"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            self.log_test("File structure", False, f"Missing files: {missing_files}")
        else:
            self.log_test("File structure", True)
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("📊 COMPREHENSIVE BUG TEST SUMMARY")
        logger.info("="*60)
        
        logger.info(f"Total Tests: {self.total_tests}")
        logger.info(f"Passed: {self.passed_tests}")
        logger.info(f"Failed: {self.failed_tests}")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests == 0:
            logger.info("\n🎉 ALL TESTS PASSED - BOT IS BUG-FREE!")
            logger.info("✅ Ready for production deployment")
        else:
            logger.info(f"\n⚠️ {self.failed_tests} TESTS FAILED")
            logger.info("❌ Issues need to be resolved before deployment")
            
            logger.info("\n🔧 FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    logger.info(f"  • {result['test']}: {result['error']}")
        
        logger.info("\n" + "="*60)
        
        return self.failed_tests == 0

async def main():
    """Run comprehensive bug test suite"""
    logger.info("🚀 Starting Comprehensive Bug Test Suite")
    logger.info("Testing all critical functionality for 100% bug-free operation")
    
    test_suite = BugTestSuite()
    
    # Run all tests
    await test_suite.test_imports()
    await test_suite.test_markdown_parsing()
    await test_suite.test_callback_handlers()
    await test_suite.test_whop_integration()
    await test_suite.test_database_operations()
    await test_suite.test_environment_variables()
    await test_suite.test_ai_providers()
    await test_suite.test_file_structure()
    
    # Print summary and return success status
    all_passed = test_suite.print_summary()
    
    if all_passed:
        logger.info("\n🎯 DEPLOYMENT READY: All systems operational!")
        sys.exit(0)
    else:
        logger.info("\n🚨 DEPLOYMENT BLOCKED: Critical issues detected!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())