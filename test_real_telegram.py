#!/usr/bin/env python3
"""
Test Real Telegram Integration
Tests the enhanced bot with actual Telegram API
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_telegram_connection():
    """Test Telegram bot connection"""
    print("🧪 Testing Telegram Bot Connection")
    print("=" * 50)
    
    try:
        from telegram import Bot
        from config import config
        
        # Get bot token
        bot_token = config.get('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            print("❌ No Telegram bot token found in config")
            return False
        
        # Create bot instance
        bot = Bot(token=bot_token)
        
        # Test connection
        print("🔍 Testing bot connection...")
        me = await bot.get_me()
        
        print(f"✅ Bot connected successfully!")
        print(f"   Bot Name: {me.first_name}")
        print(f"   Username: @{me.username}")
        print(f"   Bot ID: {me.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Telegram: {e}")
        return False

async def test_enhanced_message_simulation():
    """Simulate message processing without sending to Telegram"""
    print("\n🧪 Testing Enhanced Message Processing (Simulation)")
    print("=" * 50)
    
    try:
        from enhanced_intent_system import analyze_user_intent_enhanced
        from enhanced_response_handler import handle_enhanced_response
        
        # Test messages that users might send
        test_messages = [
            "BTC price",
            "What's ethereum worth?",
            "Tell me about Uniswap",
            "Hello Möbius",
            "Help",
            "Show my portfolio",
            "Best yield farming opportunities",
        ]
        
        print("Testing message processing with enhanced system...")
        
        for message in test_messages:
            print(f"\n📨 Message: '{message}'")
            
            try:
                # Analyze intent
                analysis = await analyze_user_intent_enhanced(message, 12345)
                print(f"   🎯 Intent: {analysis.intent_type.value}")
                print(f"   🔄 Strategy: {analysis.response_strategy.value}")
                print(f"   📊 Confidence: {analysis.confidence:.2f}")
                
                # Generate response
                response = await handle_enhanced_response(analysis, message, 12345)
                print(f"   📤 Response Type: {response.get('type', 'unknown')}")
                
                # Show first part of response
                response_text = response.get('message', '')
                if response_text:
                    preview = response_text[:100] + "..." if len(response_text) > 100 else response_text
                    print(f"   💬 Response: {preview}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in message simulation: {e}")
        return False

async def test_api_endpoints():
    """Test external API endpoints"""
    print("\n🧪 Testing External API Endpoints")
    print("=" * 50)
    
    results = {}
    
    # Test CoinGecko API
    print("🔍 Testing CoinGecko API...")
    try:
        import requests
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=10)
        if response.status_code == 200:
            data = response.json()
            btc_price = data.get('bitcoin', {}).get('usd', 0)
            print(f"   ✅ CoinGecko API working - BTC: ${btc_price:,.2f}")
            results['coingecko'] = True
        else:
            print(f"   ❌ CoinGecko API error: {response.status_code}")
            results['coingecko'] = False
    except Exception as e:
        print(f"   ❌ CoinGecko API error: {e}")
        results['coingecko'] = False
    
    # Test DeFiLlama API
    print("\n🔍 Testing DeFiLlama API...")
    try:
        response = requests.get("https://api.llama.fi/protocols", timeout=10)
        if response.status_code == 200:
            data = response.json()
            protocol_count = len(data) if data else 0
            print(f"   ✅ DeFiLlama API working - {protocol_count} protocols")
            results['defillama'] = True
        else:
            print(f"   ❌ DeFiLlama API error: {response.status_code}")
            results['defillama'] = False
    except Exception as e:
        print(f"   ❌ DeFiLlama API error: {e}")
        results['defillama'] = False
    
    return results

async def test_configuration():
    """Test bot configuration"""
    print("\n🧪 Testing Bot Configuration")
    print("=" * 50)
    
    try:
        from config import config
        
        # Check essential config
        essential_keys = [
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHAT_ID',
            'GROQ_API_KEY',
            'GEMINI_API_KEY'
        ]
        
        config_status = {}
        
        for key in essential_keys:
            value = config.get(key)
            has_value = bool(value and value != 'your_api_key_here')
            status = "✅" if has_value else "❌"
            print(f"   {status} {key}: {'Set' if has_value else 'Missing/Default'}")
            config_status[key] = has_value
        
        return config_status
        
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        return {}

async def main():
    """Run all tests"""
    print("🚀 Starting Real Telegram Integration Tests")
    print("=" * 60)
    
    # Test configuration
    config_results = await test_configuration()
    
    # Test Telegram connection
    telegram_connected = await test_telegram_connection()
    
    # Test message processing
    message_processing = await test_enhanced_message_simulation()
    
    # Test API endpoints
    api_results = await test_api_endpoints()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    
    print("Configuration:")
    for key, status in config_results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {key}")
    
    print(f"\nTelegram Connection: {'✅' if telegram_connected else '❌'}")
    print(f"Message Processing: {'✅' if message_processing else '❌'}")
    
    print("\nAPI Endpoints:")
    for api, status in api_results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {api.title()}")
    
    # Overall status
    all_essential = (
        telegram_connected and 
        message_processing and 
        api_results.get('coingecko', False)
    )
    
    print(f"\n🎯 Overall Status: {'✅ Ready for deployment!' if all_essential else '⚠️  Needs attention'}")
    
    if all_essential:
        print("\n🚀 Your bot is ready! You can now:")
        print("   1. Run the bot: python src/main.py")
        print("   2. Test in Telegram with commands like:")
        print("      • 'BTC price'")
        print("      • 'Tell me about Uniswap'")
        print("      • 'Hello'")
        print("      • 'Help'")
    else:
        print("\n🔧 To fix issues:")
        if not telegram_connected:
            print("   • Check your TELEGRAM_BOT_TOKEN in .env")
        if not api_results.get('coingecko', False):
            print("   • Check internet connection for API access")
        if not message_processing:
            print("   • Check dependencies are installed")

if __name__ == "__main__":
    asyncio.run(main())