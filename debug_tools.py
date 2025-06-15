#!/usr/bin/env python3

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, 'src')

from universal_intent_executor import execute_intent_with_tools, cleanup_universal_executor

async def debug_tools():
    """Debug which tools are being executed for different intents"""
    print("🔍 DEBUGGING TOOL EXECUTION")
    print("=" * 60)
    
    test_cases = [
        {
            'name': 'Price Query',
            'intent': 'get_realtime_price',
            'entities': [{'type': 'cryptocurrency', 'value': 'bitcoin'}],
            'context': {'user_id': 12345},
            'expected_tools': ['get_crypto_price', 'get_market_data']
        },
        {
            'name': 'Portfolio Analysis',
            'intent': 'analyze_portfolio',
            'entities': [],
            'context': {
                'user_id': 12345,
                'portfolio': {'BTC': 0.5, 'ETH': 2.0, 'SOL': 10.0}
            },
            'expected_tools': ['calculate_portfolio_metrics', 'assess_portfolio_risk']
        },
        {
            'name': 'Research',
            'intent': 'market_research',
            'entities': [{'type': 'cryptocurrency', 'value': 'ethereum'}],
            'context': {'user_id': 12345},
            'expected_tools': ['get_crypto_price', 'get_market_data', 'analyze_fundamentals']
        },
        {
            'name': 'Yield Opportunities',
            'intent': 'find_yield_opportunities',
            'entities': [],
            'context': {'user_id': 12345},
            'expected_tools': ['get_yield_opportunities']
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['name']}")
        print(f"   Intent: {test_case['intent']}")
        print(f"   Expected tools: {test_case['expected_tools']}")
        
        try:
            result = await execute_intent_with_tools(
                test_case['intent'],
                test_case['entities'],
                test_case['context']
            )
            
            print(f"   ✅ Success: {result.success}")
            print(f"   🔧 Tools executed ({len(result.tool_calls_made)}):")
            
            for j, tool_call in enumerate(result.tool_calls_made, 1):
                # Extract just the function name from the tool call
                tool_name = tool_call.split('(')[0] if '(' in tool_call else tool_call
                expected = "✅" if tool_name in test_case['expected_tools'] else "❓"
                print(f"      {j}. {expected} {tool_call}")
            
            # Check if all expected tools were called
            called_tools = [tc.split('(')[0] for tc in result.tool_calls_made]
            missing_tools = [tool for tool in test_case['expected_tools'] if tool not in called_tools]
            unexpected_tools = [tool for tool in called_tools if tool not in test_case['expected_tools']]
            
            if missing_tools:
                print(f"   ❌ Missing expected tools: {missing_tools}")
            if unexpected_tools:
                print(f"   ⚠️  Unexpected tools: {unexpected_tools}")
            if not missing_tools and not unexpected_tools:
                print(f"   🎯 Perfect tool match!")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Cleanup
    await cleanup_universal_executor()

if __name__ == "__main__":
    asyncio.run(debug_tools())