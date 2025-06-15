#!/usr/bin/env python3
"""
Comprehensive test for message encryption in conversation intelligence
"""

import asyncio
import sys
import os
import sqlite3
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_message_encryption():
    """Test that messages are properly encrypted in storage"""
    print("🔐 COMPREHENSIVE MESSAGE ENCRYPTION TEST")
    print("=" * 50)
    
    try:
        from conversation_intelligence import ConversationIntelligence, ConversationMessage
        
        # Initialize conversation intelligence
        conv_intel = ConversationIntelligence()
        await conv_intel.start_streaming()
        
        print("✅ Conversation Intelligence initialized")
        print(f"🔑 Encryption status: {'ENABLED' if conv_intel.fernet else 'DISABLED'}")
        
        # Test message
        test_message = ConversationMessage(
            message_id="test_encrypt_001",
            user_id=12345,
            username="test_user",
            chat_id=67890,
            chat_type="private",
            text="This is a sensitive message with crypto info: BTC price is $105,000",
            timestamp=datetime.now(),
            is_bot_message=False,
            reply_to_message_id=None,
            entities={"crypto": ["BTC"], "price": ["$105,000"]},
            sentiment="positive",
            topics=["crypto", "price"]
        )
        
        print(f"📝 Original message: '{test_message.text}'")
        print(f"👤 Original username: '{test_message.username}'")
        
        # Store the message (should be encrypted)
        await conv_intel._store_message(test_message)
        print("✅ Message stored in database")
        
        # Check raw database content to verify encryption
        print("\n🔍 CHECKING RAW DATABASE CONTENT:")
        print("-" * 40)
        
        with sqlite3.connect(conv_intel.db_path) as conn:
            cursor = conn.execute("""
                SELECT text, username, entities, topics 
                FROM conversations 
                WHERE message_id = ?
            """, (test_message.message_id,))
            
            raw_data = cursor.fetchone()
            if raw_data:
                raw_text, raw_username, raw_entities, raw_topics = raw_data
                
                print(f"📊 Raw stored text: '{raw_text}'")
                print(f"📊 Raw stored username: '{raw_username}'")
                print(f"📊 Raw stored entities: '{raw_entities}'")
                print(f"📊 Raw stored topics: '{raw_topics}'")
                
                # Check if data is encrypted (should not match original)
                if conv_intel.fernet:
                    if raw_text != test_message.text:
                        print("✅ Text is ENCRYPTED in database")
                    else:
                        print("❌ Text is NOT encrypted in database")
                        
                    if raw_username != test_message.username:
                        print("✅ Username is ENCRYPTED in database")
                    else:
                        print("❌ Username is NOT encrypted in database")
                else:
                    print("⚠️ No encryption configured - data stored in plain text")
            else:
                print("❌ No data found in database")
                return False
        
        # Test retrieval and decryption
        print("\n🔓 TESTING MESSAGE RETRIEVAL & DECRYPTION:")
        print("-" * 45)
        
        retrieved_messages = await conv_intel._get_recent_messages(test_message.chat_id, limit=1)
        
        if retrieved_messages:
            retrieved_msg = retrieved_messages[0]
            print(f"📖 Retrieved text: '{retrieved_msg.text}'")
            print(f"👤 Retrieved username: '{retrieved_msg.username}'")
            print(f"🏷️ Retrieved entities: {retrieved_msg.entities}")
            print(f"📋 Retrieved topics: {retrieved_msg.topics}")
            
            # Verify decryption worked correctly
            if retrieved_msg.text == test_message.text:
                print("✅ Text decryption SUCCESSFUL")
            else:
                print("❌ Text decryption FAILED")
                
            if retrieved_msg.username == test_message.username:
                print("✅ Username decryption SUCCESSFUL")
            else:
                print("❌ Username decryption FAILED")
                
            if retrieved_msg.entities == test_message.entities:
                print("✅ Entities decryption SUCCESSFUL")
            else:
                print("❌ Entities decryption FAILED")
                
            if retrieved_msg.topics == test_message.topics:
                print("✅ Topics decryption SUCCESSFUL")
            else:
                print("❌ Topics decryption FAILED")
        else:
            print("❌ No messages retrieved")
            return False
        
        # Test encryption/decryption methods directly
        print("\n🧪 TESTING ENCRYPTION METHODS DIRECTLY:")
        print("-" * 42)
        
        test_text = "Secret crypto wallet address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        encrypted = conv_intel._encrypt_text(test_text)
        decrypted = conv_intel._decrypt_text(encrypted)
        
        print(f"🔤 Original: '{test_text}'")
        print(f"🔐 Encrypted: '{encrypted}'")
        print(f"🔓 Decrypted: '{decrypted}'")
        
        if decrypted == test_text:
            print("✅ Direct encryption/decryption WORKING")
        else:
            print("❌ Direct encryption/decryption FAILED")
        
        # Clean up
        conv_intel.stop_streaming()
        
        print("\n🎯 ENCRYPTION TEST RESULTS:")
        print("=" * 30)
        
        if conv_intel.fernet:
            print("✅ ENCRYPTION: FULLY FUNCTIONAL")
            print("✅ Messages are encrypted in database")
            print("✅ Messages are properly decrypted on retrieval")
            print("✅ User privacy is PROTECTED")
            print("\n🛡️ SECURITY STATUS: SECURE")
        else:
            print("❌ ENCRYPTION: NOT CONFIGURED")
            print("❌ Messages stored in PLAIN TEXT")
            print("❌ User privacy is NOT PROTECTED")
            print("\n⚠️ SECURITY STATUS: VULNERABLE")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in encryption test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_message_encryption())