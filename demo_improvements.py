#!/usr/bin/env python3
"""
Demo script showing the comprehensive improvements to Möbius AI Assistant
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demo_conversational_ai():
    """Demonstrate the new conversational AI capabilities"""
    print("\n🧠 CONVERSATIONAL AI DEMO")
    print("=" * 50)
    
    try:
        from enhanced_natural_language import process_natural_language
        
        # Test realistic user scenarios
        conversations = [
            ("Hey Möbius, how are you?", "Natural greeting"),
            ("What's the TVL of Hyperliquid?", "DeFi data query"),
            ("Alert me when BTC hits $100k", "Natural command"),
            ("Show me trending crypto projects", "Market research"),
            ("Thanks for your help!", "Gratitude expression"),
        ]
        
        for text, description in conversations:
            print(f"\n👤 User: {text}")
            print(f"📝 Test: {description}")
            
            result = await process_natural_language(
                user_id=12345,
                text=text,
                context={"chat_type": "private", "username": "demo_user"}
            )
            
            if result.get("success"):
                response = result["response"]
                print(f"🤖 Möbius: {response.get('message', 'No message')}")
                print(f"🎯 Intent: {result.get('intent', 'unknown')}")
                print(f"📊 Confidence: {result.get('confidence', 0):.1f}")
                
                if "follow_up_suggestions" in response:
                    print(f"💡 Suggestions: {', '.join(response['follow_up_suggestions'][:2])}")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        print("\n✅ Conversational AI Demo Complete!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

async def demo_command_integration():
    """Demonstrate command integration from natural language"""
    print("\n🎯 COMMAND INTEGRATION DEMO")
    print("=" * 50)
    
    try:
        from command_intent_mapper import demo_map_natural_language_to_command
        
        # Test natural language to command mapping
        natural_requests = [
            "Show me the price of Bitcoin",
            "I want to set up an alert for Ethereum",
            "What's trending in crypto today?",
            "Give me a summary of the market",
            "Help me with portfolio tracking",
            "What's the latest crypto news?",
        ]
        
        for request in natural_requests:
            print(f"\n👤 User: {request}")
            
            result = demo_map_natural_language_to_command(request)
            
            if result["success"]:
                print(f"🎯 Mapped to: /{result['command']}")
                print(f"📊 Confidence: {result['confidence']:.1f}")
                if result.get("parameters"):
                    print(f"⚙️ Parameters: {result['parameters']}")
            else:
                print(f"❌ No command mapping found")
                
        print("\n✅ Command Integration Demo Complete!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

async def demo_group_chat_intelligence():
    """Demonstrate group chat intelligence"""
    print("\n👥 GROUP CHAT INTELLIGENCE DEMO")
    print("=" * 50)
    
    try:
        from group_chat_manager import should_respond_in_group, format_group_response
        
        # Mock update objects for testing
        class MockMessage:
            def __init__(self, text, user_id=12345):
                self.text = text
                self.from_user = MockUser(user_id)
                
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
                self.username = f"user_{user_id}"
                self.is_bot = False
                
        class MockChat:
            def __init__(self, chat_id):
                self.id = chat_id
                self.type = "supergroup"
                
        class MockUpdate:
            def __init__(self, text, chat_id=123, user_id=456):
                self.effective_message = MockMessage(text, user_id)
                self.effective_chat = MockChat(chat_id)
                self.effective_user = MockUser(user_id)
                
        class MockContext:
            def __init__(self):
                self.bot = MockBot()
                
        class MockBot:
            def __init__(self):
                self.username = "mobius_bot"
        
        # Test group chat scenarios
        scenarios = [
            ("@mobius what's the price of BTC?", "Direct mention"),
            ("Hey mobius, help me out", "Name mention"),
            ("Random group message", "No mention"),
            ("@mobius_bot show me trending coins", "Username mention"),
            ("Thanks möbius for the help!", "Name variant mention"),
        ]
        
        context = MockContext()
        
        for message_text, scenario in scenarios:
            print(f"\n👤 Group Message: {message_text}")
            print(f"📝 Scenario: {scenario}")
            
            update = MockUpdate(message_text)
            should_respond, reason = should_respond_in_group(update, context)
            
            print(f"🤖 Should Respond: {'✅ Yes' if should_respond else '❌ No'}")
            print(f"💭 Reason: {reason}")
            
            if should_respond:
                formatted = format_group_response(
                    "Here's the information you requested!",
                    "demo_user",
                    "direct"
                )
                print(f"📝 Formatted Response: {formatted}")
                
        print("\n✅ Group Chat Intelligence Demo Complete!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

async def demo_error_handling():
    """Demonstrate improved error handling"""
    print("\n🛡️ ERROR HANDLING DEMO")
    print("=" * 50)
    
    try:
        from enhanced_natural_language import process_natural_language
        
        # Test realistic edge cases
        error_scenarios = [
            ("What's the TVL of a non-existent protocol?", "Unknown protocol query"),
            ("", "Empty string"),
            ("🚀💎🌙", "Emoji only"),
            ("Tell me about crypto" * 50, "Very long input"),
        ]
        
        for test_input, description in error_scenarios:
            print(f"\n🧪 Testing: {description}")
            print(f"📝 Input: {repr(test_input)}")
            
            try:
                result = await process_natural_language(
                    user_id=12345,
                    text=test_input,
                    context={"chat_type": "private"}
                )
                
                if result.get("success"):
                    print("✅ Handled gracefully")
                else:
                    print(f"⚠️ Graceful failure: {result.get('fallback_response', 'No fallback')}")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                
        print("\n✅ Error Handling Demo Complete!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

async def main():
    """Run all improvement demos"""
    print("🚀 MÖBIUS AI ASSISTANT - COMPREHENSIVE IMPROVEMENTS DEMO")
    print("=" * 60)
    print("Demonstrating the transformation from basic bot to intelligent AI assistant")
    
    # Run all demos
    await demo_conversational_ai()
    await demo_command_integration()
    await demo_group_chat_intelligence()
    await demo_error_handling()
    
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETE - Möbius is now a professional AI assistant!")
    print("✨ Key improvements:")
    print("   • Natural conversation flow")
    print("   • Intelligent command integration")
    print("   • Smart group chat behavior")
    print("   • Robust error handling")
    print("   • Context-aware responses")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())