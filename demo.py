#!/usr/bin/env python3
"""
Demo script showing Möbius functionality.
This demonstrates the bot's capabilities without requiring Telegram setup.
"""

import sys
import asyncio
sys.path.append('src')

async def demo_crypto_research():
    """Demonstrate crypto research capabilities."""
    print("🔍 CRYPTO RESEARCH DEMO")
    print("=" * 50)
    
    from crypto_research import query_defillama
    
    # Test DeFiLlama queries
    protocols = ['lido', 'uniswap', 'aave']
    data_types = ['tvl', 'revenue']
    
    for protocol in protocols:
        for data_type in data_types:
            try:
                result = query_defillama(data_type, protocol)
                print(f"📊 {protocol.title()} {data_type.upper()}: {result}")
            except Exception as e:
                print(f"❌ Error querying {protocol} {data_type}: {e}")
    
    print()

def demo_wallet_creation():
    """Demonstrate secure wallet creation."""
    print("💰 WALLET CREATION DEMO")
    print("=" * 50)
    
    from onchain import create_wallet, encrypt_private_key, decrypt_private_key
    
    # Create a new wallet
    wallet = create_wallet()
    print(f"✅ New wallet created:")
    print(f"   Address: {wallet['address']}")
    print(f"   Private Key: {wallet['private_key'][:10]}...{wallet['private_key'][-10:]}")
    print(f"   Mnemonic: {' '.join(wallet['mnemonic'].split()[:3])}... (12 words total)")
    
    # Demonstrate encryption
    password = "secure_password_123"
    encrypted_pk = encrypt_private_key(wallet['private_key'], password)
    print(f"✅ Private key encrypted (length: {len(encrypted_pk)} bytes)")
    
    # Demonstrate decryption
    decrypted_pk = decrypt_private_key(encrypted_pk, password)
    if decrypted_pk == wallet['private_key']:
        print("✅ Private key successfully decrypted")
    else:
        print("❌ Decryption failed")
    
    print()

def demo_scheduling():
    """Demonstrate scheduling functionality."""
    print("🗓️ SCHEDULING DEMO")
    print("=" * 50)
    
    from scheduling import set_calendly_for_user, get_schedule_link_for_user
    from user_db import update_username_mapping
    
    # Simulate user setup
    user_id = 12345
    username = "demo_user"
    calendly_link = "https://calendly.com/demo-user/30min"
    
    # Update username mapping
    update_username_mapping(user_id, username)
    print(f"✅ Username mapping updated: {user_id} -> @{username}")
    
    # Set Calendly link
    result = set_calendly_for_user(user_id, calendly_link)
    print(f"✅ Calendly setup: {result}")
    
    # Retrieve Calendly link
    result = get_schedule_link_for_user(f"@{username}")
    print(f"✅ Calendly retrieval: {result}")
    
    print()

async def demo_ai_providers():
    """Demonstrate AI provider functionality."""
    print("🤖 AI PROVIDERS DEMO")
    print("=" * 50)
    
    from ai_providers import generate_text
    
    providers = ['groq', 'openai', 'gemini', 'anthropic']
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain DeFi in one sentence."}
    ]
    
    for provider in providers:
        try:
            # Test with empty API key (should show error message)
            result = await generate_text(provider, "", test_messages)
            print(f"🔑 {provider.title()}: {result[:80]}...")
        except Exception as e:
            print(f"❌ {provider.title()} error: {e}")
    
    print()

def demo_encryption():
    """Demonstrate encryption capabilities."""
    print("🔒 ENCRYPTION DEMO")
    print("=" * 50)
    
    from encryption_manager import EncryptionManager
    
    # Create encryption manager
    em = EncryptionManager()
    
    # Test messages
    messages = [
        "Secret trading strategy: Buy low, sell high",
        "Private key: 0x1234567890abcdef...",
        "Meeting notes: Discussed Q4 roadmap"
    ]
    
    encrypted_messages = []
    
    for i, msg in enumerate(messages):
        encrypted = em.encrypt(msg)
        encrypted_messages.append(encrypted)
        print(f"✅ Message {i+1} encrypted (length: {len(encrypted)} bytes)")
    
    # Demonstrate decryption
    print("\n🔓 Decrypting messages:")
    for i, encrypted in enumerate(encrypted_messages):
        decrypted = em.decrypt(encrypted)
        print(f"✅ Message {i+1}: {decrypted[:50]}...")
    
    # Demonstrate key rotation
    print("\n🔄 Testing key rotation:")
    em.rotate_key()
    print("✅ Encryption key rotated")
    
    # Old encrypted messages should no longer be decryptable
    try:
        em.decrypt(encrypted_messages[0])
        print("❌ Old message still decryptable (unexpected)")
    except Exception:
        print("✅ Old messages no longer decryptable (expected)")
    
    print()

def demo_configuration():
    """Demonstrate configuration management."""
    print("⚙️ CONFIGURATION DEMO")
    print("=" * 50)
    
    from config import config
    
    # Show current configuration
    print("Current configuration:")
    print(f"  AI Provider: {config.get('ACTIVE_AI_PROVIDER')}")
    print(f"  Timezone: {config.get('TIMEZONE')}")
    print(f"  Summary Time: {config.get('SUMMARY_TIME')}")
    print(f"  Paused: {config.get('PAUSED')}")
    
    # Demonstrate dynamic configuration
    print("\n🔧 Testing dynamic configuration:")
    
    # Change AI provider
    original_provider = config.get('ACTIVE_AI_PROVIDER')
    config.set('ACTIVE_AI_PROVIDER', 'openai')
    print(f"✅ AI provider changed to: {config.get('ACTIVE_AI_PROVIDER')}")
    
    # Change timezone
    config.set('TIMEZONE', 'America/New_York')
    print(f"✅ Timezone changed to: {config.get('TIMEZONE')}")
    
    # Restore original settings
    config.set('ACTIVE_AI_PROVIDER', original_provider)
    config.set('TIMEZONE', 'UTC')
    print("✅ Configuration restored")
    
    print()

async def main():
    """Run all demos."""
    print("🚀 MÖBIUS AI ASSISTANT DEMO")
    print("=" * 60)
    print("This demo showcases the bot's capabilities without requiring")
    print("Telegram setup or API keys.")
    print("=" * 60)
    print()
    
    # Run all demos
    await demo_crypto_research()
    demo_wallet_creation()
    demo_scheduling()
    await demo_ai_providers()
    demo_encryption()
    demo_configuration()
    
    print("🎉 DEMO COMPLETE")
    print("=" * 60)
    print("Möbius is ready for production deployment!")
    print("To get started:")
    print("1. Set up your Telegram bot token")
    print("2. Configure API keys for desired services")
    print("3. Run: python src/main.py")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())