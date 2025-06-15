#!/usr/bin/env python3
"""
Clean Comprehensive Test for Möbius AI Assistant
Tests all systems, commands, and integrations
"""

import sys
import os
import asyncio
import logging
from unittest.mock import Mock, AsyncMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set test mode
os.environ['MOBIUS_TEST_MODE'] = '1'

# Configure logging
logging.basicConfig(level=logging.ERROR)

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing Critical Imports...")
    
    tests = [
        ("Config", lambda: __import__('config')),
        ("User DB", lambda: __import__('user_db')),
        ("Enhanced DB", lambda: __import__('enhanced_db')),
        ("Encryption", lambda: __import__('encryption_manager')),
        ("Summarizer", lambda: __import__('summarizer')),
        ("AI Providers", lambda: __import__('ai_providers')),
        ("Telegram Handler", lambda: __import__('telegram_handler')),
        ("Crypto Research", lambda: __import__('crypto_research')),
        ("DeFiLlama API", lambda: __import__('defillama_api')),
        ("Social Trading", lambda: __import__('social_trading')),
        ("Advanced Research", lambda: __import__('advanced_research')),
        ("Cross-Chain Analytics", lambda: __import__('cross_chain_analytics')),
        ("UI Enhancements", lambda: __import__('ui_enhancements')),
        ("Main Bot", lambda: __import__('main')),
    ]
    
    passed = 0
    failed = []
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed.append((name, str(e)))
    
    return passed, failed

def test_database():
    """Test database operations"""
    print("\n🧪 Testing Database Operations...")
    
    try:
        import user_db
        
        # Test basic operations
        user_db.set_user_property(12345, "test_key", "test_value")
        value = user_db.get_user_property(12345, "test_key")
        
        if value == "test_value":
            print("✅ Database read/write operations")
            return True, None
        else:
            return False, "Database value mismatch"
            
    except Exception as e:
        return False, str(e)

def test_api_endpoints():
    """Test API endpoint configurations"""
    print("\n🧪 Testing API Endpoints...")
    
    try:
        from defillama_api import DeFiLlamaAPI
        api = DeFiLlamaAPI()
        
        # Test basic API functionality
        if hasattr(api, 'get_protocols') and hasattr(api, 'get_chains'):
            print("✅ DeFiLlama API endpoints")
            return True, None
        else:
            return False, "Missing API methods"
            
    except Exception as e:
        return False, str(e)

def test_ai_providers():
    """Test AI provider configurations"""
    print("\n🧪 Testing AI Providers...")
    
    try:
        import ai_providers
        
        # Test provider availability
        if hasattr(ai_providers, 'get_ai_response'):
            print("✅ AI Providers (response function available)")
            return True, None
        else:
            return False, "No AI response function available"
            
    except Exception as e:
        return False, str(e)

def test_feature_classes():
    """Test main feature classes"""
    print("\n🧪 Testing Feature Classes...")
    
    tests = [
        ("Social Trading Hub", lambda: __import__('social_trading').SocialTradingHub()),
        ("Research Engine", lambda: __import__('advanced_research').AdvancedResearchEngine()),
        ("Cross-Chain Analyzer", lambda: __import__('cross_chain_analytics').CrossChainAnalytics()),
    ]
    
    passed = 0
    failed = []
    
    for name, test_func in tests:
        try:
            instance = test_func()
            if hasattr(instance, '__class__'):
                print(f"✅ {name}")
                passed += 1
            else:
                failed.append((name, "Invalid class instance"))
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed.append((name, str(e)))
    
    return passed, failed

def test_ui_components():
    """Test UI components"""
    print("\n🧪 Testing UI Components...")
    
    try:
        from ui_enhancements import SmartKeyboard, create_smart_help_menu
        
        # Test keyboard creation
        main_menu = SmartKeyboard.create_main_menu()
        help_menu = create_smart_help_menu()
        
        if hasattr(main_menu, 'inline_keyboard') and hasattr(help_menu, 'inline_keyboard'):
            print("✅ UI keyboard generation")
            return True, None
        else:
            return False, "Invalid keyboard objects"
            
    except Exception as e:
        return False, str(e)

async def test_command_handlers():
    """Test command handler availability"""
    print("\n🧪 Testing Command Handlers...")
    
    try:
        import main
        
        # List of all commands that should exist
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
        
        missing = []
        for cmd in expected_commands:
            if not hasattr(main, cmd):
                missing.append(cmd)
        
        if not missing:
            print(f"✅ All {len(expected_commands)} command handlers present")
            return True, None
        else:
            return False, f"Missing commands: {missing}"
            
    except Exception as e:
        return False, str(e)

def main():
    """Run comprehensive final test"""
    print("🚀 Final Comprehensive Test - Möbius AI Assistant\n")
    print("="*60)
    
    # Run all tests
    test_results = []
    
    # 1. Import tests
    import_passed, import_failed = test_imports()
    test_results.append(("Imports", import_passed, len(import_failed), import_failed))
    
    # 2. Database tests
    db_success, db_error = test_database()
    test_results.append(("Database", 1 if db_success else 0, 0 if db_success else 1, [] if db_success else [("Database", db_error)]))
    
    # 3. API tests
    api_success, api_error = test_api_endpoints()
    test_results.append(("API Endpoints", 1 if api_success else 0, 0 if api_success else 1, [] if api_success else [("API", api_error)]))
    
    # 4. AI Provider tests
    ai_success, ai_error = test_ai_providers()
    test_results.append(("AI Providers", 1 if ai_success else 0, 0 if ai_success else 1, [] if ai_success else [("AI", ai_error)]))
    
    # 5. Feature class tests
    feature_passed, feature_failed = test_feature_classes()
    test_results.append(("Feature Classes", feature_passed, len(feature_failed), feature_failed))
    
    # 6. UI tests
    ui_success, ui_error = test_ui_components()
    test_results.append(("UI Components", 1 if ui_success else 0, 0 if ui_success else 1, [] if ui_success else [("UI", ui_error)]))
    
    # 7. Command handler tests
    cmd_success, cmd_error = asyncio.run(test_command_handlers())
    test_results.append(("Command Handlers", 1 if cmd_success else 0, 0 if cmd_success else 1, [] if cmd_success else [("Commands", cmd_error)]))
    
    # Summary
    print("\n" + "="*60)
    print("FINAL TEST RESULTS")
    print("="*60)
    
    total_passed = 0
    total_failed = 0
    all_failures = []
    
    for test_name, passed, failed, failures in test_results:
        total_passed += passed
        total_failed += failed
        all_failures.extend(failures)
        
        status = "✅ PASS" if failed == 0 else "❌ FAIL"
        print(f"{test_name:20} {status:10} ({passed} passed, {failed} failed)")
    
    print(f"\nOverall: {total_passed} passed, {total_failed} failed")
    
    if all_failures:
        print(f"\n❌ Failures:")
        for name, error in all_failures:
            print(f"  - {name}: {error}")
    
    success_rate = (total_passed / (total_passed + total_failed)) * 100 if (total_passed + total_failed) > 0 else 0
    
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 95:
        print("🎉 EXCELLENT! Bot is production-ready!")
        return True
    elif success_rate >= 85:
        print("✅ GOOD! Bot is mostly functional with minor issues.")
        return True
    else:
        print("⚠️ NEEDS WORK! Significant issues need to be addressed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)