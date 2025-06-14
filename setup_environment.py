#!/usr/bin/env python3
"""
Environment Setup Script for Möbius AI Assistant
Generates required environment variables and validates setup
"""

import os
import base64
import secrets
from cryptography.fernet import Fernet

def generate_encryption_key():
    """Generate a secure encryption key for the bot"""
    return Fernet.generate_key().decode()

def create_env_file():
    """Create a sample .env file with required variables"""
    
    # Generate secure encryption key
    encryption_key = generate_encryption_key()
    
    env_content = f"""# Möbius AI Assistant Environment Configuration
# Copy this file to .env and fill in your actual values

# ===== REQUIRED TELEGRAM SETTINGS =====
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# ===== SECURITY & ENCRYPTION =====
BOT_MASTER_ENCRYPTION_KEY={encryption_key}

# ===== AI PROVIDERS (Optional - at least one recommended) =====
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_GEMINI_API_KEY_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# ===== BLOCKCHAIN & WEB3 (Optional) =====
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your_project_id
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/your_project_id
BSC_RPC_URL=https://bsc-dataseed.binance.org/

# ===== EXCHANGE APIS (Optional for live trading) =====
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
BYBIT_API_KEY=your_bybit_api_key
BYBIT_SECRET_KEY=your_bybit_secret_key

# ===== SOCIAL & NEWS APIS (Optional) =====
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
NEWS_API_KEY=your_news_api_key

# ===== DATABASE & STORAGE =====
DATABASE_PATH=data/user_data.sqlite
LOG_LEVEL=INFO

# ===== FEATURE FLAGS =====
ENABLE_SOCIAL_TRADING=true
ENABLE_CROSS_CHAIN=true
ENABLE_ADVANCED_ALERTS=true
ENABLE_LIVE_TRADING=false

# ===== PERFORMANCE SETTINGS =====
MAX_CONCURRENT_REQUESTS=10
CACHE_TTL_SECONDS=300
REQUEST_TIMEOUT_SECONDS=30
"""

    with open('.env.example', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.example file")
    print(f"🔑 Generated encryption key: {encryption_key}")
    print("\n📝 Next steps:")
    print("1. Copy .env.example to .env")
    print("2. Fill in your actual API keys and tokens")
    print("3. Run the bot with: python src/main.py")

def validate_environment():
    """Validate the current environment setup"""
    print("🔍 Validating Environment Setup...\n")
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID', 
        'BOT_MASTER_ENCRYPTION_KEY'
    ]
    
    optional_vars = [
        'GROQ_API_KEY',
        'OPENAI_API_KEY',
        'GEMINI_API_KEY',
        'ANTHROPIC_API_KEY'
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var}")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var}")
    
    if missing_required:
        print(f"\n❌ Missing required variables: {missing_required}")
        print("⚠️ Bot will not start without these!")
        return False
    
    if missing_optional:
        print(f"\n⚠️ Missing optional variables: {missing_optional}")
        print("💡 Some features may be limited without these")
    
    # Test encryption key
    try:
        key = os.getenv('BOT_MASTER_ENCRYPTION_KEY')
        if key:
            Fernet(key.encode())
            print("✅ Encryption key is valid")
        else:
            print("❌ No encryption key provided")
            return False
    except Exception as e:
        print(f"❌ Invalid encryption key: {e}")
        return False
    
    print("\n🎉 Environment validation passed!")
    return True

def main():
    """Main setup function"""
    print("🚀 Möbius AI Assistant Environment Setup\n")
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("📁 Found existing .env file")
        from dotenv import load_dotenv
        load_dotenv()
        validate_environment()
    else:
        print("📝 No .env file found, creating example...")
        create_env_file()
        print("\n💡 After setting up .env, run this script again to validate")

if __name__ == "__main__":
    main()