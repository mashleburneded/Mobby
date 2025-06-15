#!/usr/bin/env python3
"""
Test script for the fixed Möbius AI Assistant
Tests core functionality and imports
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    try:
        # Test core imports
        from config import config
        print("✅ Config imported successfully")
        
        from user_db import init_db
        print("✅ User DB imported successfully")
        
        from encryption_manager import EncryptionManager
        print("✅ Encryption manager imported successfully")
        
        from summarizer import generate_daily_summary
        print("✅ Summarizer imported successfully")
        
        # Test enhanced features
        from social_trading import social_trading_hub
        print("✅ Social trading hub imported successfully")
        
        from advanced_research import research_engine
        print("✅ Research engine imported successfully")
        
        from cross_chain_analytics import cross_chain_analyzer
        print("✅ Cross-chain analyzer imported successfully")
        
        from ui_enhancements import SmartKeyboard, create_smart_help_menu
        print("✅ UI enhancements imported successfully")
        
        # Test main module
        from main import main, help_command, summarynow_command
        print("✅ Main module imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\n🧪 Testing database...")
    
    try:
        from user_db import init_db, set_user_property, get_user_property
        
        # Initialize database
        init_db()
        print("✅ Database initialized successfully")
        
        # Test user properties
        test_user_id = 12345
        set_user_property(test_user_id, 'test_key', 'test_value')
        value = get_user_property(test_user_id, 'test_key')
        
        if value == 'test_value':
            print("✅ Database operations working")
            return True
        else:
            print("❌ Database operations failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_features():
    """Test feature availability"""
    print("\n🧪 Testing features...")
    
    try:
        from social_trading import social_trading_hub
        from advanced_research import research_engine
        from cross_chain_analytics import cross_chain_analyzer
        
        # Test social trading
        result = social_trading_hub.get_overview(12345)
        print("✅ Social trading hub accessible")
        
        # Test research engine
        result = research_engine.process_query(12345, "test query")
        print("✅ Research engine accessible")
        
        # Test cross-chain analyzer
        result = cross_chain_analyzer.process_command(12345, "portfolio", [])
        print("✅ Cross-chain analyzer accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Feature test failed: {e}")
        return False

def test_ui():
    """Test UI components"""
    print("\n🧪 Testing UI components...")
    
    try:
        from ui_enhancements import SmartKeyboard, create_smart_help_menu
        
        # Test keyboard creation
        keyboard = SmartKeyboard.create_main_menu()
        print("✅ Main menu keyboard created")
        
        help_keyboard = create_smart_help_menu()
        print("✅ Help menu keyboard created")
        
        return True
        
    except Exception as e:
        print(f"❌ UI test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Fixed Möbius AI Assistant\n")
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Features", test_features),
        ("UI Components", test_ui)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    print(f"\n{'='*50}")
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Bot is ready to run.")
        print("\n📋 Next steps:")
        print("1. Set up your .env file with required tokens")
        print("2. Run: python src/main.py")
        print("3. Test with /start command in Telegram")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)