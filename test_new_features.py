#!/usr/bin/env python3
"""
Test script for new memory database and AI provider features
"""

import asyncio
import sys
import os
sys.path.append('src')

def test_memory_database():
    """Test the agent memory database"""
    print("🧠 Testing Agent Memory Database...")
    
    try:
        from agent_memory_database import (
            agent_memory, get_conversation_flow, analyze_user_intent,
            get_response_template, get_learning_insights
        )
        
        # Test intent analysis
        test_inputs = [
            "What's the price of Bitcoin?",
            "Show me my portfolio",
            "Set an alert for ETH at $3000",
            "Analyze the market for Solana"
        ]
        
        print("📊 Intent Analysis Results:")
        for text in test_inputs:
            intent, confidence = analyze_user_intent(text)
            print(f"  '{text}' → {intent} ({confidence:.2f})")
        
        # Test conversation flows
        flow = get_conversation_flow("get_crypto_price")
        if flow:
            print(f"✅ Conversation flow loaded: {flow.intent}")
            print(f"   Patterns: {len(flow.user_input_patterns)}")
            print(f"   Actions: {len(flow.expected_actions)}")
        
        # Test learning insights
        insights = get_learning_insights()
        print(f"✅ Learning insights: {len(insights)} available")
        
        print("✅ Memory Database: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Memory Database test failed: {e}")
        return False

def test_ai_provider_manager():
    """Test the AI provider manager"""
    print("\n🤖 Testing AI Provider Manager...")
    
    try:
        from ai_provider_manager import (
            ai_provider_manager, list_ai_providers, get_ai_provider_info
        )
        
        # Test provider listing
        providers = list_ai_providers()
        print(f"📋 Available providers: {list(providers.keys())}")
        
        # Test current provider info
        current_info = get_ai_provider_info()
        print(f"✅ Current provider: {current_info['name']}")
        print(f"   Model: {current_info['default_model']}")
        print(f"   Quality: {current_info['quality_score']}/10")
        print(f"   Speed: {current_info['speed_score']}/10")
        
        # Test provider capabilities
        for provider_name, info in providers.items():
            status = "🟢" if info['available'] else "🔴"
            print(f"  {status} {info['name']}: {info['default_model']}")
        
        print("✅ AI Provider Manager: All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ AI Provider Manager test failed: {e}")
        return False

async def test_ai_generation():
    """Test AI text generation with fallback"""
    print("\n⚡ Testing AI Generation...")
    
    try:
        from ai_provider_manager import generate_ai_response
        
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from Möbius AI!' and nothing else."}
        ]
        
        print("🔄 Testing AI response generation...")
        response = await generate_ai_response(test_messages)
        print(f"✅ AI Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Generation test failed: {e}")
        return False

def test_database_initialization():
    """Test database initialization"""
    print("\n🗄️ Testing Database Initialization...")
    
    try:
        import sqlite3
        from pathlib import Path
        
        # Check if databases exist
        db_files = [
            "data/agent_memory.db",
            "data/user_data.sqlite",
            "data/conversation_intelligence.db"
        ]
        
        for db_file in db_files:
            if Path(db_file).exists():
                print(f"✅ Database exists: {db_file}")
                
                # Test connection
                with sqlite3.connect(db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    print(f"   Tables: {len(tables)} found")
            else:
                print(f"⚠️  Database not found: {db_file}")
        
        print("✅ Database Initialization: Tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing Configuration...")
    
    try:
        from config import config
        
        # Test required config values
        required_keys = [
            'TELEGRAM_BOT_TOKEN',
            'BOT_MASTER_ENCRYPTION_KEY',
            'AI_PROVIDER'
        ]
        
        for key in required_keys:
            value = config.get(key)
            if value:
                print(f"✅ {key}: Configured")
            else:
                print(f"⚠️  {key}: Not configured")
        
        # Test AI provider config
        ai_provider = config.get('AI_PROVIDER', 'groq')
        print(f"🤖 Active AI Provider: {ai_provider}")
        
        print("✅ Configuration: Tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Möbius AI Assistant - New Features Test Suite")
    print("=" * 60)
    
    tests = [
        test_configuration,
        test_database_initialization,
        test_memory_database,
        test_ai_provider_manager,
        test_ai_generation
    ]
    
    results = []
    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                result = await test()
            else:
                result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! New features are ready to use.")
        print("\n🔧 Quick Start Commands:")
        print("• /memory_status - Check memory database")
        print("• /ai_providers - View AI providers")
        print("• /switch_ai gemini - Switch to Gemini")
        print("• /memory_train beginner - Run training")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return all(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)