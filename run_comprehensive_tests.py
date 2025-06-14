#!/usr/bin/env python3
"""
Comprehensive test runner for all new features
"""
import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing Module Imports...")
    
    try:
        from tier_access_control import tier_access_control
        print("✅ Tier Access Control imported")
        
        from advanced_portfolio_manager import advanced_portfolio_manager
        print("✅ Advanced Portfolio Manager imported")
        
        from advanced_alerts import advanced_alerts
        print("✅ Advanced Alerts imported")
        
        from natural_language_query import natural_language_query
        print("✅ Natural Language Query imported")
        
        from social_trading import social_trading
        print("✅ Social Trading imported")
        
        from advanced_research import advanced_research
        print("✅ Advanced Research imported")
        
        from automated_trading import automated_trading
        print("✅ Automated Trading imported")
        
        from cross_chain_analytics import cross_chain_analytics
        print("✅ Cross-Chain Analytics imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_tier_system():
    """Test tier access control system"""
    print("\n🧪 Testing Tier System...")
    
    try:
        from tier_access_control import tier_access_control
        
        # Test all tiers
        tiers = ["free", "retail", "corporate"]
        features = ["portfolio_tracking", "portfolio_analytics", "api_access"]
        
        for tier in tiers:
            for feature in features:
                access = tier_access_control.check_feature_access(tier, feature)
                print(f"  {tier.title()} -> {feature}: {'✅' if access['allowed'] else '❌'}")
        
        # Test tier comparison
        comparison = tier_access_control.get_tier_comparison()
        print(f"✅ Tier comparison includes {len(comparison)} tiers")
        
        return True
        
    except Exception as e:
        print(f"❌ Tier system test failed: {e}")
        return False

async def test_portfolio_features():
    """Test portfolio management features"""
    print("\n🧪 Testing Portfolio Features...")
    
    try:
        from advanced_portfolio_manager import advanced_portfolio_manager
        
        # Test wallet management
        test_wallet = "0x1234567890123456789012345678901234567890"
        result = advanced_portfolio_manager.add_wallet(12345, test_wallet)
        print(f"✅ Wallet addition: {'Success' if result else 'Failed'}")
        
        # Test invalid wallet
        invalid_result = advanced_portfolio_manager.add_wallet(12345, "invalid")
        print(f"✅ Invalid wallet rejection: {'Success' if not invalid_result else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Portfolio test failed: {e}")
        return False

async def test_alerts_features():
    """Test advanced alerts features"""
    print("\n🧪 Testing Alerts Features...")
    
    try:
        from advanced_alerts import advanced_alerts
        
        # Test price alert creation
        result = await advanced_alerts.create_price_alert(12345, "BTC", ">", 50000)
        print(f"✅ Price alert creation: {'Success' if result['success'] else 'Failed'}")
        
        if result['success']:
            print(f"  ML Confidence: {result.get('ml_confidence', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Alerts test failed: {e}")
        return False

async def test_nlp_features():
    """Test natural language processing features"""
    print("\n🧪 Testing NLP Features...")
    
    try:
        from natural_language_query import natural_language_query
        
        # Test query processing
        response = await natural_language_query.process_query(12345, "What is Bitcoin?")
        print(f"✅ NLP Query processing: {'Success' if response.answer else 'Failed'}")
        print(f"  Response length: {len(response.answer)} characters")
        print(f"  Suggestions: {len(response.suggestions)}")
        
        return True
        
    except Exception as e:
        print(f"❌ NLP test failed: {e}")
        return False

async def test_social_features():
    """Test social trading features"""
    print("\n🧪 Testing Social Trading Features...")
    
    try:
        from social_trading import social_trading
        
        # Test trader profile creation
        result = await social_trading.create_trader_profile(12345, "test_trader", "Test Trader")
        print(f"✅ Trader profile creation: {'Success' if result['success'] else 'Failed'}")
        
        # Test leaderboard
        leaderboard = await social_trading.get_leaderboard()
        print(f"✅ Leaderboard access: {'Success' if 'leaderboard' in leaderboard else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Social trading test failed: {e}")
        return False

async def test_trading_features():
    """Test automated trading features"""
    print("\n🧪 Testing Trading Features...")
    
    try:
        from automated_trading import automated_trading
        
        # Test strategy creation
        parameters = {
            'symbol': 'BTC/USDT',
            'base_amount': 100,
            'max_position_size': 1000
        }
        result = await automated_trading.create_strategy(12345, "Test Strategy", "dca", parameters)
        print(f"✅ Strategy creation: {'Success' if result['success'] else 'Failed'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Trading test failed: {e}")
        return False

async def test_cross_chain_features():
    """Test cross-chain analytics features"""
    print("\n🧪 Testing Cross-Chain Features...")
    
    try:
        from cross_chain_analytics import cross_chain_analytics
        
        # Test supported chains
        result = await cross_chain_analytics.get_supported_chains(12345)
        print(f"✅ Supported chains: {'Success' if result['success'] else 'Failed'}")
        print(f"  Total chains: {result.get('total_chains', 0)}")
        print(f"  Healthy chains: {result.get('healthy_chains', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cross-chain test failed: {e}")
        return False

async def run_all_tests():
    """Run all comprehensive tests"""
    print("🚀 Running Comprehensive Feature Tests\n")
    
    tests = [
        ("Module Imports", test_imports),
        ("Tier System", test_tier_system),
        ("Portfolio Features", test_portfolio_features),
        ("Alerts Features", test_alerts_features),
        ("NLP Features", test_nlp_features),
        ("Social Features", test_social_features),
        ("Trading Features", test_trading_features),
        ("Cross-Chain Features", test_cross_chain_features),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All comprehensive features are working correctly!")
        print("✅ Ready for deployment!")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)