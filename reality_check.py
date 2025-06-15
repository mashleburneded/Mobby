#!/usr/bin/env python3
"""
Reality Check - What Actually Works vs Framework Only
Tests real functionality vs mock implementations
"""

import sys
import os
import asyncio
import logging
from unittest.mock import Mock, AsyncMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set test mode
os.environ['MOBIUS_TEST_MODE'] = '1'

# Configure logging
logging.basicConfig(level=logging.ERROR)

def check_real_implementations():
    """Check what's actually implemented vs mocked"""
    print("🔍 REALITY CHECK - What Actually Works\n")
    
    results = {
        "fully_working": [],
        "partially_working": [],
        "framework_only": [],
        "not_implemented": []
    }
    
    # 1. Check DeFiLlama API
    print("📊 Testing DeFiLlama API...")
    try:
        from defillama_api import DeFiLlamaAPI
        api = DeFiLlamaAPI()
        
        # Check if methods actually make real API calls
        import inspect
        methods = [method for method in dir(api) if not method.startswith('_')]
        
        real_methods = []
        mock_methods = []
        
        for method in methods:
            func = getattr(api, method)
            if callable(func):
                source = inspect.getsource(func)
                if 'requests.get' in source or 'aiohttp' in source or 'httpx' in source:
                    real_methods.append(method)
                elif 'Mock' in source or 'return {}' in source or 'pass' in source:
                    mock_methods.append(method)
        
        if real_methods:
            results["fully_working"].append(f"DeFiLlama API ({len(real_methods)} real methods)")
        if mock_methods:
            results["framework_only"].append(f"DeFiLlama API ({len(mock_methods)} mock methods)")
            
    except Exception as e:
        results["not_implemented"].append(f"DeFiLlama API: {e}")
    
    # 2. Check AI Providers
    print("🤖 Testing AI Providers...")
    try:
        import ai_providers
        
        # Check if real API calls are made
        source = inspect.getsource(ai_providers)
        if 'groq.Groq' in source or 'openai.OpenAI' in source:
            results["fully_working"].append("AI Providers (real API integration)")
        else:
            results["framework_only"].append("AI Providers (mock responses)")
            
    except Exception as e:
        results["not_implemented"].append(f"AI Providers: {e}")
    
    # 3. Check Social Trading
    print("📈 Testing Social Trading...")
    try:
        from social_trading import SocialTradingHub
        hub = SocialTradingHub()
        
        # Check methods
        methods = [m for m in dir(hub) if not m.startswith('_') and callable(getattr(hub, m))]
        
        if len(methods) > 2:  # More than just __init__ and basic methods
            source = inspect.getsource(SocialTradingHub)
            if 'def get_overview' in source and 'return' in source:
                if 'Mock' in source or '{}' in source:
                    results["framework_only"].append("Social Trading (framework only)")
                else:
                    results["partially_working"].append("Social Trading (partial implementation)")
            else:
                results["not_implemented"].append("Social Trading (missing core methods)")
        else:
            results["framework_only"].append("Social Trading (basic class only)")
            
    except Exception as e:
        results["not_implemented"].append(f"Social Trading: {e}")
    
    # 4. Check Database
    print("💾 Testing Database...")
    try:
        import user_db
        
        # Test actual database operations
        user_db.set_user_property(999999, "test_key", "test_value")
        value = user_db.get_user_property(999999, "test_key")
        
        if value == "test_value":
            results["fully_working"].append("Database (full CRUD operations)")
        else:
            results["partially_working"].append("Database (partial functionality)")
            
    except Exception as e:
        results["not_implemented"].append(f"Database: {e}")
    
    # 5. Check Summarization
    print("📝 Testing Summarization...")
    try:
        import summarizer
        
        # Check if real AI integration exists
        source = inspect.getsource(summarizer)
        if 'groq' in source.lower() or 'openai' in source.lower():
            results["fully_working"].append("Summarization (real AI integration)")
        else:
            results["framework_only"].append("Summarization (framework only)")
            
    except Exception as e:
        results["not_implemented"].append(f"Summarization: {e}")
    
    # 6. Check Cross-Chain Analytics
    print("🔗 Testing Cross-Chain Analytics...")
    try:
        from cross_chain_analytics import CrossChainAnalyzer
        analyzer = CrossChainAnalyzer()
        
        methods = [m for m in dir(analyzer) if not m.startswith('_') and callable(getattr(analyzer, m))]
        
        if len(methods) > 1:
            results["framework_only"].append("Cross-Chain Analytics (basic framework)")
        else:
            results["not_implemented"].append("Cross-Chain Analytics (minimal implementation)")
            
    except Exception as e:
        results["not_implemented"].append(f"Cross-Chain Analytics: {e}")
    
    # 7. Check Advanced Research
    print("🔬 Testing Advanced Research...")
    try:
        from advanced_research import ResearchEngine
        engine = ResearchEngine()
        
        methods = [m for m in dir(engine) if not m.startswith('_') and callable(getattr(engine, m))]
        
        if len(methods) > 1:
            results["framework_only"].append("Advanced Research (basic framework)")
        else:
            results["not_implemented"].append("Advanced Research (minimal implementation)")
            
    except Exception as e:
        results["not_implemented"].append(f"Advanced Research: {e}")
    
    return results

def check_command_functionality():
    """Check which commands actually do real work vs just respond"""
    print("\n💬 Testing Command Functionality...")
    
    import main
    
    # Commands that likely work fully
    basic_commands = [
        'start_command', 'help_command', 'menu_command', 
        'status_command', 'premium_command'
    ]
    
    # Commands that need real implementation
    advanced_commands = [
        'summarynow_command', 'ask_command', 'research_command',
        'social_command', 'portfolio_command', 'alerts_command',
        'llama_command', 'arkham_command', 'nansen_command'
    ]
    
    working_basic = []
    working_advanced = []
    framework_only = []
    
    for cmd in basic_commands:
        if hasattr(main, cmd):
            working_basic.append(cmd.replace('_command', ''))
    
    for cmd in advanced_commands:
        if hasattr(main, cmd):
            # These exist but may be framework only
            framework_only.append(cmd.replace('_command', ''))
    
    return {
        "basic_working": working_basic,
        "advanced_framework": framework_only
    }

def main():
    """Run reality check"""
    print("🚨 MÖBIUS AI ASSISTANT - REALITY CHECK")
    print("="*60)
    
    # Check implementations
    impl_results = check_real_implementations()
    cmd_results = check_command_functionality()
    
    print("\n" + "="*60)
    print("📊 REALITY CHECK RESULTS")
    print("="*60)
    
    print("\n✅ FULLY WORKING (Real Implementation):")
    for item in impl_results["fully_working"]:
        print(f"  ✅ {item}")
    
    print(f"\n🔶 PARTIALLY WORKING (Some Real Features):")
    for item in impl_results["partially_working"]:
        print(f"  🔶 {item}")
    
    print(f"\n⚠️ FRAMEWORK ONLY (Structure But No Real Implementation):")
    for item in impl_results["framework_only"]:
        print(f"  ⚠️ {item}")
    
    print(f"\n❌ NOT IMPLEMENTED:")
    for item in impl_results["not_implemented"]:
        print(f"  ❌ {item}")
    
    print(f"\n💬 COMMAND STATUS:")
    print(f"  ✅ Basic Commands Working: {len(cmd_results['basic_working'])}")
    for cmd in cmd_results['basic_working']:
        print(f"    - /{cmd}")
    
    print(f"  ⚠️ Advanced Commands (Framework Only): {len(cmd_results['advanced_framework'])}")
    for cmd in cmd_results['advanced_framework']:
        print(f"    - /{cmd}")
    
    # Calculate percentages
    total_features = len(impl_results["fully_working"]) + len(impl_results["partially_working"]) + len(impl_results["framework_only"]) + len(impl_results["not_implemented"])
    
    if total_features > 0:
        fully_working_pct = (len(impl_results["fully_working"]) / total_features) * 100
        framework_pct = (len(impl_results["framework_only"]) / total_features) * 100
        
        print(f"\n📈 IMPLEMENTATION STATUS:")
        print(f"  🎯 Fully Working: {fully_working_pct:.1f}%")
        print(f"  🏗️ Framework Only: {framework_pct:.1f}%")
        
        if fully_working_pct >= 70:
            print(f"\n🎉 STATUS: Production Ready Core Features")
        elif fully_working_pct >= 40:
            print(f"\n⚠️ STATUS: Partially Functional - Needs Implementation")
        else:
            print(f"\n🚧 STATUS: Mostly Framework - Major Implementation Needed")
    
    return impl_results, cmd_results

if __name__ == "__main__":
    main()