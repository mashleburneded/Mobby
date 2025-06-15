#!/usr/bin/env python3
"""
CLI Startup Script for Möbius AI Assistant
Allows switching AI providers and models from command line
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_provider_manager import ai_provider_manager, AIProvider
from config import config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_argument_parser():
    """Setup command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Möbius AI Assistant - Advanced Crypto/DeFi AI Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_startup.py --provider gemini --model gemini-2.0-flash
  python cli_startup.py --provider groq --model llama-3.1-70b-versatile
  python cli_startup.py --provider openai --model gpt-4o
  python cli_startup.py --list-providers
  python cli_startup.py --test-providers
        """
    )
    
    # AI Provider options
    parser.add_argument(
        "--provider", "-p",
        choices=["groq", "gemini", "openai", "anthropic", "openrouter"],
        help="AI provider to use (default: groq)"
    )
    
    parser.add_argument(
        "--model", "-m",
        help="Specific model to use (depends on provider)"
    )
    
    parser.add_argument(
        "--list-providers", "-l",
        action="store_true",
        help="List all available providers and models"
    )
    
    parser.add_argument(
        "--test-providers", "-t",
        action="store_true",
        help="Test all available providers"
    )
    
    # Bot configuration
    parser.add_argument(
        "--telegram-token",
        help="Telegram bot token (overrides env var)"
    )
    
    parser.add_argument(
        "--chat-id",
        help="Telegram chat ID (overrides env var)"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching for this session"
    )
    
    parser.add_argument(
        "--enhanced-nlp",
        action="store_true",
        default=True,
        help="Enable enhanced NLP patterns (default: True)"
    )
    
    parser.add_argument(
        "--async-processing",
        action="store_true",
        default=True,
        help="Enable async processing pipeline (default: True)"
    )
    
    return parser

def print_banner():
    """Print startup banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🤖 MÖBIUS AI ASSISTANT                    ║
║                Advanced Crypto/DeFi AI Bot                   ║
║                                                              ║
║  🧠 Enhanced NLP  💾 Smart Caching  ⚡ Async Processing     ║
║  📊 Multi-Source Data  🔄 AI Provider Switching             ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def list_providers():
    """List all available providers and models"""
    print("\n🤖 AVAILABLE AI PROVIDERS & MODELS")
    print("=" * 50)
    
    providers_info = ai_provider_manager.list_providers()
    
    for provider_name, info in providers_info.items():
        status = "✅ ACTIVE" if info["current"] else "⚪ AVAILABLE" if info["available"] else "❌ UNAVAILABLE"
        print(f"\n{status} {info['name']} ({provider_name})")
        print(f"   Default Model: {info['default_model']}")
        print(f"   Available Models:")
        for model in info['available_models']:
            print(f"     • {model}")
        print(f"   Max Tokens: {info['max_tokens']:,}")
        print(f"   Rate Limit: {info['rate_limit_rpm']} RPM")
        print(f"   Quality: {info['quality_score']}/10")
        print(f"   Speed: {info['speed_score']}/10")
        print(f"   Reliability: {info['reliability_score']}/10")

async def test_providers():
    """Test all available providers"""
    print("\n🧪 TESTING AI PROVIDERS")
    print("=" * 30)
    
    test_message = [{"role": "user", "content": "Hello! Please respond with 'Test successful' if you can read this."}]
    
    providers_info = ai_provider_manager.list_providers()
    
    for provider_name, info in providers_info.items():
        if not info["available"]:
            print(f"❌ {info['name']}: Not available (missing API key)")
            continue
        
        print(f"\n🔄 Testing {info['name']}...")
        
        try:
            # Switch to provider
            success = ai_provider_manager.switch_provider(provider_name)
            if not success:
                print(f"❌ {info['name']}: Failed to switch")
                continue
            
            # Test generation
            response = await ai_provider_manager.generate_text(test_message)
            
            if response and "test successful" in response.lower():
                print(f"✅ {info['name']}: Working correctly")
            else:
                print(f"⚠️ {info['name']}: Responded but unexpected output")
                print(f"   Response: {response[:100]}...")
                
        except Exception as e:
            print(f"❌ {info['name']}: Error - {e}")

def validate_environment():
    """Validate environment setup"""
    print("\n🔍 VALIDATING ENVIRONMENT")
    print("=" * 30)
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID"
    ]
    
    optional_vars = [
        "GROQ_API_KEY",
        "GEMINI_API_KEY", 
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY"
    ]
    
    issues = []
    
    # Check required variables
    for var in required_vars:
        if not os.getenv(var):
            issues.append(f"❌ Missing required: {var}")
        else:
            print(f"✅ {var}: Set")
    
    # Check optional variables
    ai_keys_found = 0
    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
            ai_keys_found += 1
        else:
            print(f"⚪ {var}: Not set")
    
    if ai_keys_found == 0:
        issues.append("⚠️ No AI provider API keys found")
    
    if issues:
        print(f"\n⚠️ ENVIRONMENT ISSUES:")
        for issue in issues:
            print(f"   {issue}")
        return False
    
    print(f"\n✅ Environment validation passed!")
    return True

async def start_bot(args):
    """Start the bot with specified configuration"""
    print("\n🚀 STARTING MÖBIUS AI ASSISTANT")
    print("=" * 35)
    
    # Apply configuration
    if args.provider:
        print(f"🔄 Switching to {args.provider}...")
        success = ai_provider_manager.switch_provider(args.provider, args.model)
        if success:
            print(f"✅ Successfully switched to {args.provider}")
            if args.model:
                print(f"   Model: {args.model}")
        else:
            print(f"❌ Failed to switch to {args.provider}")
            return False
    
    # Show current configuration
    current_info = ai_provider_manager.get_provider_info()
    print(f"\n📋 CURRENT CONFIGURATION:")
    print(f"   AI Provider: {current_info['name']}")
    print(f"   Model: {current_info['default_model']}")
    print(f"   Max Tokens: {current_info['max_tokens']:,}")
    print(f"   Enhanced NLP: {'✅ Enabled' if args.enhanced_nlp else '❌ Disabled'}")
    print(f"   Async Processing: {'✅ Enabled' if args.async_processing else '❌ Disabled'}")
    print(f"   Caching: {'❌ Disabled' if args.no_cache else '✅ Enabled'}")
    
    # Import and start the main bot
    try:
        print(f"\n🤖 Initializing bot components...")
        
        # Import main bot module
        from main import main as start_main_bot
        
        print(f"✅ Bot components loaded successfully")
        print(f"🚀 Starting Telegram bot...")
        print(f"📱 Bot is now running and listening for messages!")
        print(f"💡 Send a message to test the bot")
        print(f"\n🛑 Press Ctrl+C to stop the bot")
        
        # Start the main bot
        await start_main_bot()
        
    except KeyboardInterrupt:
        print(f"\n\n🛑 Bot stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        return False

async def main():
    """Main CLI function"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        print("🐛 Debug logging enabled")
    
    print_banner()
    
    # Handle special commands
    if args.list_providers:
        list_providers()
        return
    
    if args.test_providers:
        await test_providers()
        return
    
    # Validate environment
    if not validate_environment():
        print(f"\n❌ Environment validation failed. Please fix the issues above.")
        sys.exit(1)
    
    # Override environment variables if provided
    if args.telegram_token:
        os.environ["TELEGRAM_BOT_TOKEN"] = args.telegram_token
    
    if args.chat_id:
        os.environ["TELEGRAM_CHAT_ID"] = args.chat_id
    
    # Start the bot
    success = await start_bot(args)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)