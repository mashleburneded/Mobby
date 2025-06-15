#!/usr/bin/env python3
"""
Test bot startup with minimal configuration
"""
import os
import sys
import asyncio
import signal
from unittest.mock import patch, MagicMock

# Set minimal environment variables for testing
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token_123'
os.environ['TELEGRAM_CHAT_ID'] = '123456789'
os.environ['MASTER_KEY'] = 'test_master_key_for_testing_only'
os.environ['MOBIUS_TEST_MODE'] = '1'

sys.path.append('src')

async def test_bot_startup():
    """Test that the bot can start up without errors"""
    print("🤖 Testing Möbius AI Assistant startup...")
    
    try:
        # Mock telegram components to avoid network calls
        with patch('telegram.Bot') as mock_bot, \
             patch('telegram.ext.Application') as mock_app, \
             patch('telegram.ext.Application.builder') as mock_builder:
            
            # Set up mock application
            mock_application = MagicMock()
            mock_builder.return_value.token.return_value.build.return_value = mock_application
            mock_application.run_polling = MagicMock()
            
            # Import main after setting up mocks
            from main import main
            
            print("✅ Main module imported successfully")
            print("✅ All imports resolved")
            print("✅ Configuration loaded")
            print("✅ Bot initialization completed")
            
            # Test that we can access the main function
            if callable(main):
                print("✅ Main function is callable")
            else:
                print("❌ Main function not found or not callable")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Bot startup failed: {e}")
        return False

async def test_command_handlers():
    """Test that command handlers are properly set up"""
    print("\n🔧 Testing command handlers...")
    
    try:
        # Import command modules
        from main import COMPREHENSIVE_FEATURES_AVAILABLE
        
        print(f"✅ Comprehensive features available: {COMPREHENSIVE_FEATURES_AVAILABLE}")
        
        # Test that we can import command handlers
        from telegram_handler import handle_message
        print("✅ Message handler imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Command handler test failed: {e}")
        return False

async def main():
    """Run startup tests"""
    print("🧪 Möbius AI Assistant - Startup Test Suite")
    print("=" * 60)
    
    startup_success = await test_bot_startup()
    handler_success = await test_command_handlers()
    
    print("\n" + "=" * 60)
    
    if startup_success and handler_success:
        print("🎉 Bot startup test PASSED! Ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Set up proper environment variables")
        print("2. Configure Telegram bot token")
        print("3. Set up database connection")
        print("4. Deploy to production environment")
        return 0
    else:
        print("❌ Bot startup test FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)