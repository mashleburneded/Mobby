#!/usr/bin/env python3
"""
UI Fixes Test Script for Möbius AI Assistant
Tests all callback handlers and markdown formatting
"""

import asyncio
import logging
from unittest.mock import Mock, AsyncMock
from telegram import Update, CallbackQuery, User, Message, Chat
from telegram.ext import ContextTypes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_callback_handlers():
    """Test all callback handlers for proper markdown formatting"""
    
    # Import the handler
    try:
        from src.ui_enhancements import handle_callback_query
    except ImportError:
        logger.error("Could not import handle_callback_query")
        return False
    
    # Create mock objects
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
    
    # Test callback queries
    test_callbacks = [
        "cmd_menu",
        "cmd_help", 
        "cmd_mymentions",
        "cmd_summarynow",
        "cmd_topic",
        "cmd_whosaid",
        "cmd_research",
        "cmd_ask",
        "cmd_social",
        "cmd_multichain",
        "cmd_portfolio",
        "cmd_alerts",
        "cmd_status",
        "plan_free",
        "help_summary",
        "help_research",
        "help_social",
        "help_multichain",
        "help_ai",
        "help_settings"
    ]
    
    success_count = 0
    total_count = len(test_callbacks)
    
    for callback_data in test_callbacks:
        try:
            # Create mock callback query
            callback_query = Mock(spec=CallbackQuery)
            callback_query.data = callback_data
            callback_query.message = message
            callback_query.from_user = user
            callback_query.answer = AsyncMock()
            callback_query.edit_message_text = AsyncMock()
            
            # Create mock update
            update = Mock(spec=Update)
            update.callback_query = callback_query
            update.effective_user = user
            update.effective_chat = chat
            
            # Create mock context
            context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            # Test the handler
            await handle_callback_query(update, context)
            
            # Check if the handler was called without errors
            callback_query.answer.assert_called_once()
            callback_query.edit_message_text.assert_called_once()
            
            logger.info(f"✅ {callback_data}: SUCCESS")
            success_count += 1
            
        except Exception as e:
            logger.error(f"❌ {callback_data}: FAILED - {e}")
    
    logger.info(f"\n📊 Test Results: {success_count}/{total_count} callbacks working")
    return success_count == total_count

def test_markdown_escaping():
    """Test markdown escaping function"""
    try:
        from src.ui_enhancements import escape_markdown
        
        test_cases = [
            ("Hello_world", "Hello\\_world"),
            ("Test*bold*", "Test\\*bold\\*"),
            ("Link[text](url)", "Link\\[text\\]\\(url\\)"),
            ("Code`snippet`", "Code\\`snippet\\`"),
            ("Special chars: <>", "Special chars: \\<\\>"),
            ("Normal text", "Normal text")
        ]
        
        success_count = 0
        for input_text, expected in test_cases:
            result = escape_markdown(input_text)
            if result == expected:
                logger.info(f"✅ Escape test: '{input_text}' -> '{result}'")
                success_count += 1
            else:
                logger.error(f"❌ Escape test: '{input_text}' -> '{result}' (expected: '{expected}')")
        
        logger.info(f"\n📊 Markdown Escape Results: {success_count}/{len(test_cases)} tests passed")
        return success_count == len(test_cases)
        
    except ImportError:
        logger.error("Could not import escape_markdown function")
        return False

def test_keyboard_creation():
    """Test keyboard creation functions"""
    try:
        from src.ui_enhancements import SmartKeyboard, create_smart_help_menu
        
        # Test main menu creation
        main_menu = SmartKeyboard.create_main_menu()
        if main_menu and main_menu.inline_keyboard:
            logger.info("✅ Main menu keyboard created successfully")
            main_menu_success = True
        else:
            logger.error("❌ Main menu keyboard creation failed")
            main_menu_success = False
        
        # Test help menu creation
        help_menu = create_smart_help_menu()
        if help_menu and help_menu.inline_keyboard:
            logger.info("✅ Help menu keyboard created successfully")
            help_menu_success = True
        else:
            logger.error("❌ Help menu keyboard creation failed")
            help_menu_success = False
        
        return main_menu_success and help_menu_success
        
    except ImportError as e:
        logger.error(f"Could not import keyboard functions: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("🧪 Starting UI Fixes Test Suite")
    logger.info("=" * 50)
    
    # Test 1: Keyboard Creation
    logger.info("\n1️⃣ Testing Keyboard Creation...")
    keyboard_test = test_keyboard_creation()
    
    # Test 2: Markdown Escaping
    logger.info("\n2️⃣ Testing Markdown Escaping...")
    escape_test = test_markdown_escaping()
    
    # Test 3: Callback Handlers
    logger.info("\n3️⃣ Testing Callback Handlers...")
    callback_test = await test_callback_handlers()
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📋 TEST SUMMARY:")
    logger.info(f"Keyboard Creation: {'✅ PASS' if keyboard_test else '❌ FAIL'}")
    logger.info(f"Markdown Escaping: {'✅ PASS' if escape_test else '❌ FAIL'}")
    logger.info(f"Callback Handlers: {'✅ PASS' if callback_test else '❌ FAIL'}")
    
    all_passed = keyboard_test and escape_test and callback_test
    logger.info(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        logger.info("\n🎉 UI fixes are working correctly!")
        logger.info("The callback query parsing errors should now be resolved.")
    else:
        logger.info("\n⚠️ Some issues remain. Check the error messages above.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())