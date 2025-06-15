#!/usr/bin/env python3

import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, 'src')

from universal_intent_executor import execute_intent_with_tools, cleanup_universal_executor

async def debug_portfolio():
    """Debug portfolio analysis"""
    print("🔍 DEBUGGING PORTFOLIO ANALYSIS")
    print("=" * 50)
    
    # Test portfolio analysis
    test_context = {
        'user_id': 12345,
        'portfolio': {'BTC': 0.5, 'ETH': 2.0, 'SOL': 10.0}
    }
    
    print("Testing portfolio analysis with context:")
    print(f"Portfolio: {test_context['portfolio']}")
    
    try:
        result = await execute_intent_with_tools(
            'analyze_portfolio',
            [],
            test_context
        )
        
        print(f"\n✅ Execution successful: {result.success}")
        print(f"⏱️  Execution time: {result.execution_time:.3f}s")
        print(f"🔧 Tools used: {len(result.tool_calls_made)}")
        
        # Show exactly which tools were called
        print(f"\n🔧 ACTUAL TOOLS EXECUTED:")
        for i, tool_call in enumerate(result.tool_calls_made, 1):
            print(f"   {i}. {tool_call}")
        
        if result.data:
            print(f"\n📊 Result structure:")
            print(f"Keys: {list(result.data.keys())}")
            
            if 'summary' in result.data:
                print(f"Summary keys: {list(result.data['summary'].keys())}")
                
                if 'portfolio_data' in result.data['summary']:
                    portfolio_data = result.data['summary']['portfolio_data']
                    print(f"Portfolio data keys: {list(portfolio_data.keys())}")
                    print(f"Has total_value: {'total_value' in portfolio_data}")
                    
                    if 'total_value' in portfolio_data:
                        print(f"Total value: {portfolio_data['total_value']}")
                    else:
                        print("❌ Missing total_value!")
                        print(f"Portfolio data: {portfolio_data}")
        else:
            print("❌ No result data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    await cleanup_universal_executor()

if __name__ == "__main__":
    asyncio.run(debug_portfolio())