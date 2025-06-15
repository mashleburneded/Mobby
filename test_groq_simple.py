#!/usr/bin/env python3
"""
Simple test for Groq API with your key
"""

import asyncio
import sys
import os
sys.path.append('src')

async def test_groq_direct():
    """Test Groq API directly"""
    try:
        import groq
        from config import config
        
        api_key = config.get('GROQ_API_KEY')
        print(f"🔑 API Key: {api_key[:20]}..." if api_key else "❌ No API key")
        
        if not api_key:
            return False
        
        client = groq.AsyncGroq(api_key=api_key)
        
        response = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from Groq!' and nothing else."}
            ],
            model="llama3-70b-8192",
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ Groq Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Groq test failed: {e}")
        return False

async def test_ai_provider_manager():
    """Test AI provider manager with Groq"""
    try:
        from ai_provider_manager import generate_ai_response, switch_ai_provider
        
        # Switch to Groq
        success = switch_ai_provider("groq")
        print(f"🔄 Switch to Groq: {'✅' if success else '❌'}")
        
        if not success:
            return False
        
        # Test generation
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from AI Provider Manager!' and nothing else."}
        ]
        
        response = await generate_ai_response(messages)
        print(f"✅ AI Manager Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ AI Provider Manager test failed: {e}")
        return False

async def main():
    print("🧪 Testing Groq Integration")
    print("=" * 50)
    
    # Test direct Groq
    print("\n1. Testing Groq API directly...")
    groq_direct = await test_groq_direct()
    
    # Test AI Provider Manager
    print("\n2. Testing AI Provider Manager...")
    ai_manager = await test_ai_provider_manager()
    
    print("\n" + "=" * 50)
    print("📊 Results:")
    print(f"✅ Groq Direct: {'PASS' if groq_direct else 'FAIL'}")
    print(f"✅ AI Manager: {'PASS' if ai_manager else 'FAIL'}")
    
    if groq_direct and ai_manager:
        print("\n🎉 All Groq tests passed!")
        return True
    else:
        print("\n❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)