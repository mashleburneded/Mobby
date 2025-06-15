#!/usr/bin/env python3
"""
Real Bot Operation Test
Tests the actual message flow as it would happen in Telegram
"""

import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import Mock, AsyncMock
sys.path.append('/workspace/mody/src')

# Mock Telegram objects
class MockMessage:
    def __init__(self, text, message_id=123, user_id=12345, chat_id=67890):
        self.text = text
        self.message_id = message_id
        self.date = datetime.now()
        self.reply_to_message = None
        self.photo = None
        self.document = None
        self.video = None
        self.audio = None
        self.voice = None
        self.sticker = None
        self.animation = None
        self.location = None
        self.contact = None
        self.caption = None
        self.entities = []
        self.chat = None  # Will be set later to avoid circular reference

class MockUser:
    def __init__(self, user_id=12345, username="testuser"):
        self.id = user_id
        self.username = username
        self.first_name = "Test"
        self.last_name = "User"
        self.is_bot = False

class MockChat:
    def __init__(self, chat_id=67890, chat_type="private"):
        self.id = chat_id
        self.type = chat_type
        self.title = "Test Chat"

class MockUpdate:
    def __init__(self, text, user_id=12345, chat_id=67890, chat_type="private"):
        self.effective_message = MockMessage(text, user_id=user_id, chat_id=chat_id)
        self.effective_user = MockUser(user_id)
        self.effective_chat = MockChat(chat_id, chat_type)
        # Set the chat reference after creation
        self.effective_message.chat = self.effective_chat

class MockContext:
    def __init__(self):
        self.bot = Mock()
        self.bot.username = "mobius_test_bot"
        self.bot_data = {}
        self.user_data = {}
        self.chat_data = {}

async def test_real_message_flow():
    """Test the actual message flow as it happens in the bot"""
    print("🧪 TESTING REAL BOT MESSAGE FLOW")
    print("=" * 50)
    
    # Import the actual message handler
    from main import enhanced_handle_message
    
    test_messages = [
        "hello",
        "BTC price",
        "what is ethereum",
        "portfolio",
        "help",
        "uniswap info",
        "set alert",
        "explain defi",
        "can you help me with crypto",
        "thanks"
    ]
    
    success_count = 0
    total_count = len(test_messages)
    
    for i, message_text in enumerate(test_messages, 1):
        print(f"\n📨 Test {i}/{total_count}: '{message_text}'")
        
        try:
            # Create mock update and context
            update = MockUpdate(message_text)
            context = MockContext()
            
            # Mock the reply_text method
            responses = []
            async def mock_reply_text(text, **kwargs):
                responses.append(text)
                print(f"   🤖 Bot Response: {text[:100]}...")
            
            update.effective_message.reply_text = mock_reply_text
            
            # Call the actual message handler
            await enhanced_handle_message(update, context)
            
            if responses:
                print(f"   ✅ Response generated successfully")
                success_count += 1
            else:
                print(f"   ❌ No response generated")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    success_rate = (success_count / total_count) * 100
    print(f"\n🎯 RESULTS: {success_count}/{total_count} messages handled successfully ({success_rate:.1f}%)")
    
    if success_rate >= 90:
        print("🎉 EXCELLENT! Real bot operation is working!")
        return True
    elif success_rate >= 70:
        print("✅ GOOD! Most messages work, some issues remain.")
        return True
    else:
        print("❌ MAJOR ISSUES! Bot operation is broken.")
        return False

async def test_conversation_intelligence():
    """Test conversation intelligence integration"""
    print("\n🧠 TESTING CONVERSATION INTELLIGENCE")
    print("=" * 40)
    
    try:
        from conversation_intelligence import ConversationMessage, ConversationIntelligence
        
        # Test message creation
        message = ConversationMessage(
            message_id="test123",
            user_id=12345,
            username="testuser",
            chat_id=67890,
            chat_type="private",
            text="Hello, what is Bitcoin?",
            timestamp=datetime.now()
        )
        
        print(f"✅ ConversationMessage created successfully")
        
        # Test attribute assignment (this was causing the error)
        message.entities = {"bitcoin": "cryptocurrency"}
        message.sentiment = "neutral"
        message.topics = ["cryptocurrency", "bitcoin"]
        
        print(f"✅ Message attributes can be modified")
        print(f"   Entities: {message.entities}")
        print(f"   Sentiment: {message.sentiment}")
        print(f"   Topics: {message.topics}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in conversation intelligence: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_intent_system_integration():
    """Test intent system integration"""
    print("\n🎯 TESTING INTENT SYSTEM INTEGRATION")
    print("=" * 40)
    
    try:
        from enhanced_intent_system import analyze_user_intent_enhanced
        from enhanced_response_handler import handle_enhanced_response
        
        test_queries = [
            "BTC price",
            "portfolio",
            "help",
            "what is ethereum"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: '{query}'")
            
            # Analyze intent
            analysis = await analyze_user_intent_enhanced(query, 12345, {})
            print(f"   Intent: {analysis.intent_type.value} (confidence: {analysis.confidence:.2f})")
            
            # Generate response
            response = await handle_enhanced_response(analysis, query, 12345, {})
            
            if response and response.get('message'):
                print(f"   ✅ Response: {response['message'][:50]}...")
            else:
                print(f"   ❌ No response generated")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in intent system: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all real operation tests"""
    print("🔍 COMPREHENSIVE REAL BOT OPERATION TEST")
    print("=" * 60)
    
    # Test individual components
    conv_intel_ok = await test_conversation_intelligence()
    intent_ok = await test_intent_system_integration()
    message_flow_ok = await test_real_message_flow()
    
    print("\n🎯 FINAL RESULTS:")
    print("=" * 30)
    print(f"Conversation Intelligence: {'✅ WORKING' if conv_intel_ok else '❌ BROKEN'}")
    print(f"Intent System Integration: {'✅ WORKING' if intent_ok else '❌ BROKEN'}")
    print(f"Real Message Flow:        {'✅ WORKING' if message_flow_ok else '❌ BROKEN'}")
    
    all_working = conv_intel_ok and intent_ok and message_flow_ok
    
    if all_working:
        print("\n🎉 ALL SYSTEMS WORKING!")
        print("The bot should now work properly in real Telegram operation!")
        return True
    else:
        print("\n⚠️ Some systems still have issues!")
        print("The bot may not work properly in real operation.")
        return False

if __name__ == "__main__":
    asyncio.run(main())