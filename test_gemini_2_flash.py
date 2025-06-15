#!/usr/bin/env python3
"""
Test Gemini 2.0 Flash specifically
"""

import asyncio
import sys
import os
import time
sys.path.append('src')

async def test_gemini_2_flash():
    """Test Gemini 2.0 Flash model"""
    print("🧪 Testing Gemini 2.0 Flash")
    print("=" * 50)
    
    try:
        from ai_provider_manager import switch_ai_provider, generate_ai_response, get_ai_provider_info
        
        # Switch to Gemini
        print("🔄 Switching to Gemini...")
        success = switch_ai_provider("gemini")
        if not success:
            print("❌ Failed to switch to Gemini")
            return False
        
        # Check current provider info
        info = get_ai_provider_info()
        print(f"✅ Current provider: {info['name']}")
        print(f"   Model: {info['default_model']}")
        print(f"   Quality: {info['quality_score']}/10")
        print(f"   Speed: {info['speed_score']}/10")
        
        # Test simple generation
        print("\n🤖 Testing simple generation...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Be concise."},
            {"role": "user", "content": "Say 'Hello from Gemini 2.0 Flash!' and nothing else."}
        ]
        
        start_time = time.time()
        response = await generate_ai_response(messages)
        response_time = time.time() - start_time
        
        if not response:
            print("❌ No response from Gemini")
            return False
        
        print(f"✅ Response: {response}")
        print(f"⏱️  Response time: {response_time:.2f}s")
        
        # Test crypto-specific query
        print("\n💰 Testing crypto query...")
        crypto_messages = [
            {"role": "system", "content": "You are a crypto assistant. Be helpful and informative."},
            {"role": "user", "content": "Explain Bitcoin in one sentence."}
        ]
        
        start_time = time.time()
        crypto_response = await generate_ai_response(crypto_messages)
        crypto_time = time.time() - start_time
        
        if not crypto_response:
            print("❌ No crypto response from Gemini")
            return False
        
        print(f"✅ Crypto response: {crypto_response[:100]}...")
        print(f"⏱️  Response time: {crypto_time:.2f}s")
        
        # Test complex reasoning
        print("\n🧠 Testing complex reasoning...")
        reasoning_messages = [
            {"role": "system", "content": "You are an AI assistant that can reason step by step."},
            {"role": "user", "content": "If I have 0.5 BTC and Bitcoin is $50,000, how much is my portfolio worth? Show your calculation."}
        ]
        
        start_time = time.time()
        reasoning_response = await generate_ai_response(reasoning_messages)
        reasoning_time = time.time() - start_time
        
        if not reasoning_response:
            print("❌ No reasoning response from Gemini")
            return False
        
        print(f"✅ Reasoning response: {reasoning_response[:150]}...")
        print(f"⏱️  Response time: {reasoning_time:.2f}s")
        
        # Calculate average performance
        avg_time = (response_time + crypto_time + reasoning_time) / 3
        print(f"\n📊 Performance Summary:")
        print(f"   Average response time: {avg_time:.2f}s")
        print(f"   All responses generated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Gemini 2.0 Flash test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_gemini_vs_groq():
    """Compare Gemini 2.0 Flash vs Groq"""
    print("\n🥊 Gemini 2.0 Flash vs Groq Comparison")
    print("=" * 50)
    
    test_prompt = "Explain DeFi in exactly 50 words."
    
    results = {}
    
    # Test Groq
    try:
        from ai_provider_manager import switch_ai_provider, generate_ai_response
        
        print("🔄 Testing Groq...")
        switch_ai_provider("groq")
        
        messages = [
            {"role": "system", "content": "You are a crypto expert. Be precise."},
            {"role": "user", "content": test_prompt}
        ]
        
        start_time = time.time()
        groq_response = await generate_ai_response(messages)
        groq_time = time.time() - start_time
        
        results['groq'] = {
            'response': groq_response,
            'time': groq_time,
            'word_count': len(groq_response.split()) if groq_response else 0
        }
        
        print(f"✅ Groq: {groq_time:.2f}s, {results['groq']['word_count']} words")
        
    except Exception as e:
        print(f"❌ Groq failed: {e}")
        results['groq'] = {'error': str(e)}
    
    # Test Gemini 2.0 Flash
    try:
        print("🔄 Testing Gemini 2.0 Flash...")
        switch_ai_provider("gemini")
        
        start_time = time.time()
        gemini_response = await generate_ai_response(messages)
        gemini_time = time.time() - start_time
        
        results['gemini'] = {
            'response': gemini_response,
            'time': gemini_time,
            'word_count': len(gemini_response.split()) if gemini_response else 0
        }
        
        print(f"✅ Gemini: {gemini_time:.2f}s, {results['gemini']['word_count']} words")
        
    except Exception as e:
        print(f"❌ Gemini failed: {e}")
        results['gemini'] = {'error': str(e)}
    
    # Compare results
    print("\n📊 Comparison Results:")
    if 'error' not in results.get('groq', {}) and 'error' not in results.get('gemini', {}):
        groq_time = results['groq']['time']
        gemini_time = results['gemini']['time']
        
        faster = "Groq" if groq_time < gemini_time else "Gemini"
        time_diff = abs(groq_time - gemini_time)
        
        print(f"⚡ Speed: {faster} is {time_diff:.2f}s faster")
        print(f"📝 Word accuracy: Groq={results['groq']['word_count']}, Gemini={results['gemini']['word_count']} (target: 50)")
        
        # Show responses
        print(f"\n🤖 Groq Response:")
        print(f"   {results['groq']['response'][:200]}...")
        print(f"\n🧠 Gemini Response:")
        print(f"   {results['gemini']['response'][:200]}...")
    
    return results

async def main():
    """Run all Gemini 2.0 Flash tests"""
    print("🚀 GEMINI 2.0 FLASH TEST SUITE")
    print("🔬 Testing the latest Gemini model")
    print("=" * 60)
    
    # Test Gemini 2.0 Flash
    gemini_success = await test_gemini_2_flash()
    
    # Compare with Groq
    comparison_results = await test_gemini_vs_groq()
    
    print("\n" + "=" * 60)
    print("🏆 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    if gemini_success:
        print("✅ Gemini 2.0 Flash: WORKING")
        print("🎉 Ready to use Gemini 2.0 Flash as AI provider!")
        print("\n🔧 Commands to use Gemini:")
        print("• /switch_ai gemini - Switch to Gemini 2.0 Flash")
        print("• /test_ai gemini - Test Gemini provider")
        print("• /ai_benchmark - Compare all providers")
    else:
        print("❌ Gemini 2.0 Flash: FAILED")
        print("⚠️  Check API key and quota limits")
    
    return gemini_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)