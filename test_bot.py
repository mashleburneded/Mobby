#!/usr/bin/env python3
"""
Test script to verify the bot can initialize without errors.
This tests all imports and basic functionality without connecting to Telegram.
"""

import sys
import os
sys.path.append('src')

def test_imports():
    """Test that all modules can be imported successfully."""
    print("🧪 Testing imports...")
    
    try:
        from config import config
        print("✅ Config module imported")
        
        from user_db import init_db
        print("✅ User DB module imported")
        
        from encryption_manager import EncryptionManager
        print("✅ Encryption manager imported")
        
        from ai_providers import generate_text
        print("✅ AI providers module imported")
        
        from crypto_research import query_defillama, get_arkham_data, get_nansen_data
        print("✅ Crypto research module imported")
        
        from scheduling import set_calendly_for_user, get_schedule_link_for_user
        print("✅ Scheduling module imported")
        
        from onchain import create_wallet
        print("✅ Onchain module imported")
        
        from summarizer import generate_daily_summary
        print("✅ Summarizer module imported")
        
        from telegram_handler import handle_message
        print("✅ Telegram handler imported")
        
        from persistent_storage import save_summary, get_summaries_for_week
        print("✅ Persistent storage imported")
        
        # Test main module import (but don't run it)
        import main
        print("✅ Main module imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key components."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test database initialization
        from user_db import init_db
        init_db()
        print("✅ Database initialization")
        
        # Test encryption
        from encryption_manager import EncryptionManager
        em = EncryptionManager()
        test_msg = "Test message"
        encrypted = em.encrypt(test_msg)
        decrypted = em.decrypt(encrypted)
        assert decrypted == test_msg
        print("✅ Encryption/decryption")
        
        # Test wallet creation
        from onchain import create_wallet
        wallet = create_wallet()
        assert 'address' in wallet and 'private_key' in wallet and 'mnemonic' in wallet
        print("✅ Wallet creation")
        
        # Test DeFiLlama
        from crypto_research import query_defillama
        result = query_defillama('tvl', 'lido')
        assert 'TVL' in result
        print("✅ DeFiLlama integration")
        
        # Test Calendly validation
        from scheduling import set_calendly_for_user
        result = set_calendly_for_user(12345, 'https://calendly.com/test')
        assert 'successfully' in result
        print("✅ Calendly validation")
        
        return True
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading and validation."""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import config
        
        # Check required config values
        required_keys = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'BOT_MASTER_ENCRYPTION_KEY']
        for key in required_keys:
            value = config.get(key)
            if not value or value.startswith('YOUR_'):
                print(f"⚠️  {key} not configured (expected for testing)")
            else:
                print(f"✅ {key} configured")
        
        # Check optional config structure
        ai_keys = config.get('AI_API_KEYS') or {}
        crypto_keys = config.get('CRYPTO_API_KEYS') or {}
        
        expected_ai_providers = ['groq', 'openai', 'gemini', 'anthropic']
        expected_crypto_apis = ['arkham', 'nansen']
        
        for provider in expected_ai_providers:
            if provider in ai_keys:
                print(f"✅ AI provider {provider} configured")
        
        for api in expected_crypto_apis:
            if api in crypto_keys:
                print(f"✅ Crypto API {api} configured")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Möbius Bot Tests\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_configuration),
        ("Functionality Tests", test_basic_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name}")
        print('='*50)
        
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! Möbius is ready to deploy.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration and dependencies.")
        return 1

if __name__ == "__main__":
    sys.exit(main())