#!/usr/bin/env python3
"""
Test the memory system specifically
"""

import asyncio
import sys
import os
sys.path.append('src')

async def test_memory_system():
    """Test the memory system"""
    print("🧠 Testing Memory System")
    print("=" * 50)
    
    try:
        # Import and initialize
        from agent_memory_database import (
            agent_memory, get_conversation_flow, analyze_user_intent,
            get_response_template, get_learning_insights, record_performance
        )
        
        print("✅ Memory system imported successfully")
        
        # Test intent analysis
        print("\n📊 Testing Intent Analysis:")
        test_cases = [
            "What's the price of Bitcoin?",
            "Show me my portfolio",
            "Set an alert for ETH at $3000",
            "Random text that doesn't match anything"
        ]
        
        for text in test_cases:
            intent, confidence = analyze_user_intent(text)
            print(f"  '{text}' → {intent} ({confidence:.2f})")
        
        # Test conversation flows
        print("\n🔄 Testing Conversation Flows:")
        flow = get_conversation_flow("get_crypto_price")
        if flow:
            print(f"✅ Flow found: {flow.intent}")
            print(f"   Patterns: {len(flow.user_input_patterns)}")
            print(f"   Actions: {len(flow.expected_actions)}")
            print(f"   Templates: {len(flow.response_templates)}")
        else:
            print("❌ No flow found")
        
        # Test response templates
        print("\n📝 Testing Response Templates:")
        template = get_response_template("get_crypto_price", {
            "token": "BTC",
            "price": "50000",
            "change_24h": "+5.2%"
        })
        print(f"Template: {template[:100]}...")
        
        # Test learning insights
        print("\n💡 Testing Learning Insights:")
        insights = get_learning_insights()
        print(f"✅ Found {len(insights)} insights")
        for insight in insights[:2]:
            print(f"  • {insight['insight'][:80]}...")
        
        # Test performance recording
        print("\n📈 Testing Performance Recording:")
        record_performance("test_flow", 1.5, True, None, 0.9)
        record_performance("test_flow", 2.1, False, "timeout", 0.3)
        print("✅ Performance metrics recorded")
        
        print("\n🎉 All memory system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Memory system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_memory_system())
    sys.exit(0 if success else 1)