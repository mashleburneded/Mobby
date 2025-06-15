#!/usr/bin/env python3
"""
Comprehensive test for all Möbius AI Assistant commands
Tests every command handler and callback to ensure they work properly
"""

import sys
import os
import asyncio
from unittest.mock import Mock, AsyncMock
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set test mode
os.environ['MOBIUS_TEST_MODE'] = '1'

# Configure logging
logging.basicConfig(level=logging.ERROR)

def create_mock_update_context():
    """Create mock update and context objects"""
    # Mock update
    update = Mock()
    update.effective_user = Mock()
    update.effective_user.id = 12345
    update.effective_user.username = "testuser"
    update.effective_user.first_name = "Test"
    update.effective_chat = Mock()
    update.effective_chat.id = 12345
    update.effective_chat.type = "private"
    update.effective_message = Mock()
    update.effective_message.reply_text = AsyncMock()
    update.effective_message.edit_text = AsyncMock()
    update.callback_query = Mock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.edit_message_text = AsyncMock()
    
    # Mock context
    context = Mock()
    context.args = []
    context.bot_data = {
        'message_store': {},
        'lock': asyncio.Lock(),
        'encryption_manager': Mock()
    }
    context.user_data = {}
    context.chat_data = {}
    
    return update, context

async def test_command(command_name, command_func):
    """Test a single command"""
    try:
        update, context = create_mock_update_context()
        
        # Test with no arguments
        context.args = []
        result = await command_func(update, context)
        
        # Test with arguments if applicable
        if command_name in ['research', 'ask', 'llama', 'arkham', 'nansen', 'alert', 'topic']:
            context.args = ['test', 'argument']
            result = await command_func(update, context)
        
        return True, None
        
    except Exception as e:
        return False, str(e)

async def test_callback_handler(callback_name, callback_func):
    """Test a callback handler"""
    try:
        update, context = create_mock_update_context()
        update.callback_query.data = f"{callback_name}_test"
        
        result = await callback_func(update, context)
        return True, None
        
    except Exception as e:
        return False, str(e)

async def main():
    """Run comprehensive command tests"""
    print("🧪 Testing All Möbius AI Assistant Commands\n")
    
    # Import main module
    try:
        import main
        print("✅ Main module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import main module: {e}")
        return
    
    # Define all commands to test
    commands_to_test = [
        ('start', main.start_command),
        ('help', main.help_command),
        ('summarynow', main.summarynow_command),
        ('ask', main.ask_command),
        ('research', main.research_command),
        ('social', main.social_command),
        ('multichain', main.multichain_command),
        ('portfolio', main.portfolio_command),
        ('alerts', main.alerts_command),
        ('premium', main.premium_command),
        ('status', main.status_command),
        ('llama', main.llama_command),
        ('arkham', main.arkham_command),
        ('nansen', main.nansen_command),
        ('alert', main.alert_command),
        ('create_wallet', main.create_wallet_command),
        ('menu', main.menu_command),
        ('mymentions', main.mymentions_command),
        ('topic', main.topic_command),
        ('weekly_summary', main.weekly_summary_command),
        ('whosaid', main.whosaid_command),
        ('schedule', main.schedule_command),
        ('set_calendly', main.set_calendly_command),
    ]
    
    # Define callback handlers to test
    callbacks_to_test = [
        ('plan_selection', main.plan_selection),
    ]
    
    # Import UI callback handler
    try:
        from ui_enhancements import handle_callback_query
        callbacks_to_test.append(('handle_callback_query', handle_callback_query))
    except Exception as e:
        print(f"⚠️ Could not import UI callback handler: {e}")
    
    print(f"\n🔍 Testing {len(commands_to_test)} commands...")
    
    passed_commands = 0
    failed_commands = []
    
    for command_name, command_func in commands_to_test:
        success, error = await test_command(command_name, command_func)
        if success:
            print(f"✅ /{command_name}")
            passed_commands += 1
        else:
            print(f"❌ /{command_name}: {error}")
            failed_commands.append((command_name, error))
    
    print(f"\n🔍 Testing {len(callbacks_to_test)} callback handlers...")
    
    passed_callbacks = 0
    failed_callbacks = []
    
    for callback_name, callback_func in callbacks_to_test:
        success, error = await test_callback_handler(callback_name, callback_func)
        if success:
            print(f"✅ {callback_name}")
            passed_callbacks += 1
        else:
            print(f"❌ {callback_name}: {error}")
            failed_callbacks.append((callback_name, error))
    
    # Test UI components
    print(f"\n🔍 Testing UI components...")
    try:
        from ui_enhancements import SmartKeyboard, create_smart_help_menu
        
        # Test keyboard creation
        main_menu = SmartKeyboard.create_main_menu()
        help_menu = create_smart_help_menu()
        
        print("✅ UI keyboard creation")
        passed_ui = 1
        failed_ui = []
        
    except Exception as e:
        print(f"❌ UI components: {e}")
        passed_ui = 0
        failed_ui = [("UI components", str(e))]
    
    # Summary
    total_commands = len(commands_to_test)
    total_callbacks = len(callbacks_to_test)
    total_ui = 1
    total_tests = total_commands + total_callbacks + total_ui
    total_passed = passed_commands + passed_callbacks + passed_ui
    
    print(f"\n{'='*50}")
    print(f"COMPREHENSIVE TEST RESULTS")
    print(f"{'='*50}")
    print(f"Commands: {passed_commands}/{total_commands} passed")
    print(f"Callbacks: {passed_callbacks}/{total_callbacks} passed")
    print(f"UI Components: {passed_ui}/{total_ui} passed")
    print(f"Overall: {total_passed}/{total_tests} tests passed")
    
    if failed_commands:
        print(f"\n❌ Failed Commands:")
        for cmd, error in failed_commands:
            print(f"  - /{cmd}: {error}")
    
    if failed_callbacks:
        print(f"\n❌ Failed Callbacks:")
        for cb, error in failed_callbacks:
            print(f"  - {cb}: {error}")
    
    if failed_ui:
        print(f"\n❌ Failed UI:")
        for ui, error in failed_ui:
            print(f"  - {ui}: {error}")
    
    if total_passed == total_tests:
        print(f"\n🎉 ALL TESTS PASSED! Bot is fully functional.")
        return True
    else:
        print(f"\n⚠️ {total_tests - total_passed} tests failed. Issues need to be fixed.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)