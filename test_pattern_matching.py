#!/usr/bin/env python3
"""
Test pattern matching for built-in commands
"""
import re
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from intelligent_message_router import IntelligentMessageRouter

def test_price_patterns():
    """Test price command pattern matching"""
    router = IntelligentMessageRouter()
    
    test_cases = [
        "what's the price of bitcoin",
        "bitcoin price",
        "price of btc",
        "btc price",
        "how much is ethereum",
        "what's eth worth",
        "price bitcoin",
        "what is the price of solana",
        "sol price please",
        "check bitcoin price"
    ]
    
    print("🔍 Testing Price Command Pattern Matching:")
    print("=" * 50)
    
    for test_text in test_cases:
        result = router._check_built_in_commands(test_text.lower())
        if result:
            command, confidence, entities = result
            print(f"✅ '{test_text}' -> Command: {command}, Confidence: {confidence:.2f}, Entities: {entities}")
        else:
            print(f"❌ '{test_text}' -> No match")
    
    print("\n" + "=" * 50)

def test_full_analysis():
    """Test full message analysis"""
    router = IntelligentMessageRouter()
    
    test_cases = [
        ("what's the price of bitcoin", "private"),
        ("bitcoin price", "group"),
        ("hello there", "private"),
        ("thanks", "group"),
    ]
    
    print("🧠 Testing Full Message Analysis:")
    print("=" * 50)
    
    for text, chat_type in test_cases:
        import asyncio
        
        async def test_analysis():
            analysis = await router.analyze_message(
                text=text,
                user_id=12345,
                chat_type=chat_type,
                is_reply_to_bot=False,
                is_mentioned=True if chat_type == "group" else False
            )
            
            print(f"📝 '{text}' ({chat_type}):")
            print(f"   Type: {analysis.message_type.value}")
            print(f"   Strategy: {analysis.processing_strategy.value}")
            print(f"   Should Respond: {analysis.should_respond}")
            print(f"   Confidence: {analysis.confidence:.2f}")
            print(f"   Entities: {analysis.extracted_entities}")
            print()
        
        asyncio.run(test_analysis())

if __name__ == "__main__":
    test_price_patterns()
    test_full_analysis()