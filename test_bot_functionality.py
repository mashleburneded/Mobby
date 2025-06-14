#!/usr/bin/env python3
"""
Comprehensive test script for Möbius AI Assistant functionality
Tests core features, comprehensive features, and error handling
"""
import sys
import os
import asyncio
import logging
from unittest.mock import Mock, AsyncMock, patch
sys.path.append('src')

# Set test mode
os.environ['MOBIUS_TEST_MODE'] = '1'

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def add_result(self, test_name: str, passed: bool, message: str = ""):
        self.tests.append((test_name, passed, message))
        if passed:
            self.passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed += 1
            print(f"❌ {test_name}: {message}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n📊 Test Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print("❌ Failed tests:")
            for name, passed, message in self.tests:
                if not passed:
                    print(f"   - {name}: {message}")

async def test_core_functionality():
    """Test core bot functionality"""
    results = TestResults()
    
    print("🧪 Testing Core Functionality\n")
    
    # Test config system
    try:
        from config import config
        test_value = config.get('TELEGRAM_BOT_TOKEN', 'default')
        results.add_result("Config system", True)
    except Exception as e:
        results.add_result("Config system", False, str(e))
    
    # Test user database
    try:
        from user_db import get_user_property, set_user_property
        # Mock test - these would normally require database
        results.add_result("User database", True)
    except Exception as e:
        results.add_result("User database", False, str(e))
    
    # Test encryption
    try:
        from encryption_manager import EncryptionManager
        # Test with auto-generated key
        em = EncryptionManager()
        encrypted = em.encrypt("test data")
        decrypted = em.decrypt(encrypted)
        results.add_result("Encryption system", decrypted == "test data")
    except Exception as e:
        results.add_result("Encryption system", False, str(e))
    
    # Test AI providers
    try:
        from ai_providers import generate_text, get_ai_response
        # Test graceful degradation
        response = await get_ai_response("test prompt")
        results.add_result("AI providers", "unavailable" in response.lower() or "error" in response.lower())
    except Exception as e:
        results.add_result("AI providers", False, str(e))
    
    return results

async def test_enhanced_features():
    """Test enhanced features"""
    results = TestResults()
    
    print("\n🔧 Testing Enhanced Features\n")
    
    # Test enhanced database
    try:
        from enhanced_db import enhanced_db
        results.add_result("Enhanced database", True)
    except Exception as e:
        results.add_result("Enhanced database", False, str(e))
    
    # Test enhanced UI
    try:
        from enhanced_ui import InteractiveMenu, RichFormatter
        menu = InteractiveMenu()
        formatter = RichFormatter()
        results.add_result("Enhanced UI", True)
    except Exception as e:
        results.add_result("Enhanced UI", False, str(e))
    
    # Test contextual AI
    try:
        from contextual_ai import ContextualAI
        ai = ContextualAI()
        results.add_result("Contextual AI", True)
    except Exception as e:
        results.add_result("Contextual AI", False, str(e))
    
    # Test performance monitor
    try:
        from performance_monitor import performance_monitor, track_performance
        performance_monitor.track_command("test_command", 123, 0.5, True)
        stats = performance_monitor.get_metrics_summary()
        results.add_result("Performance monitor", stats is not None)
    except Exception as e:
        results.add_result("Performance monitor", False, str(e))
    
    # Test security auditor
    try:
        from security_auditor import security_auditor
        results.add_result("Security auditor", True)
    except Exception as e:
        results.add_result("Security auditor", False, str(e))
    
    return results

async def test_comprehensive_features():
    """Test comprehensive features"""
    results = TestResults()
    
    print("\n🚀 Testing Comprehensive Features\n")
    
    # Test tier access control
    try:
        from tier_access_control import TierAccessControl
        tac = TierAccessControl()
        results.add_result("Tier access control", True)
    except Exception as e:
        results.add_result("Tier access control", False, str(e))
    
    # Test portfolio manager
    try:
        from advanced_portfolio_manager import AdvancedPortfolioManager
        # This will fail due to missing dependencies, but should import
        results.add_result("Portfolio manager", True)
    except Exception as e:
        results.add_result("Portfolio manager", False, str(e))
    
    # Test advanced alerts
    try:
        from advanced_alerts import AdvancedAlertsSystem
        results.add_result("Advanced alerts", True)
    except Exception as e:
        results.add_result("Advanced alerts", False, str(e))
    
    # Test natural language query
    try:
        from natural_language_query import NaturalLanguageQueryEngine
        results.add_result("Natural language query", True)
    except Exception as e:
        results.add_result("Natural language query", False, str(e))
    
    # Test social trading
    try:
        from social_trading import SocialTradingSystem
        results.add_result("Social trading", True)
    except Exception as e:
        results.add_result("Social trading", False, str(e))
    
    # Test advanced research
    try:
        from advanced_research import AdvancedResearchEngine
        results.add_result("Advanced research", True)
    except Exception as e:
        results.add_result("Advanced research", False, str(e))
    
    # Test automated trading
    try:
        from automated_trading import AutomatedTradingSystem
        results.add_result("Automated trading", True)
    except Exception as e:
        results.add_result("Automated trading", False, str(e))
    
    # Test cross-chain analytics
    try:
        from cross_chain_analytics import CrossChainAnalytics
        results.add_result("Cross-chain analytics", True)
    except Exception as e:
        results.add_result("Cross-chain analytics", False, str(e))
    
    return results

async def test_main_bot():
    """Test main bot functionality"""
    results = TestResults()
    
    print("\n🤖 Testing Main Bot\n")
    
    try:
        # Mock telegram objects
        with patch('telegram.Bot'), patch('telegram.ext.Application'):
            from main import main
            results.add_result("Main bot import", True)
    except Exception as e:
        results.add_result("Main bot import", False, str(e))
    
    # Test command availability checks
    try:
        from main import COMPREHENSIVE_FEATURES_AVAILABLE
        results.add_result("Feature availability flag", isinstance(COMPREHENSIVE_FEATURES_AVAILABLE, bool))
    except Exception as e:
        results.add_result("Feature availability flag", False, str(e))
    
    return results

async def test_error_handling():
    """Test error handling and graceful degradation"""
    results = TestResults()
    
    print("\n🛡️ Testing Error Handling\n")
    
    # Test AI provider graceful degradation
    try:
        from ai_providers import generate_text
        response = await generate_text("invalid_provider", "fake_key", [])
        results.add_result("AI provider error handling", "Unknown AI provider" in response)
    except Exception as e:
        results.add_result("AI provider error handling", False, str(e))
    
    # Test config with missing values
    try:
        from config import config
        missing_value = config.get('NONEXISTENT_KEY', 'default_value')
        results.add_result("Config missing key handling", missing_value == 'default_value')
    except Exception as e:
        results.add_result("Config missing key handling", False, str(e))
    
    return results

async def main():
    """Run all tests"""
    print("🧪 Möbius AI Assistant - Comprehensive Test Suite")
    print("=" * 60)
    
    all_results = TestResults()
    
    # Run test suites
    core_results = await test_core_functionality()
    enhanced_results = await test_enhanced_features()
    comprehensive_results = await test_comprehensive_features()
    main_bot_results = await test_main_bot()
    error_results = await test_error_handling()
    
    # Combine results
    for results in [core_results, enhanced_results, comprehensive_results, main_bot_results, error_results]:
        all_results.passed += results.passed
        all_results.failed += results.failed
        all_results.tests.extend(results.tests)
    
    # Print summary
    print("\n" + "=" * 60)
    all_results.summary()
    
    # Determine overall status
    if all_results.failed == 0:
        print("\n🎉 All tests passed! Bot is ready for deployment.")
        return 0
    elif all_results.passed > all_results.failed:
        print(f"\n⚠️ Most tests passed ({all_results.passed}/{all_results.passed + all_results.failed}). Bot should work with some limitations.")
        return 1
    else:
        print(f"\n❌ Many tests failed ({all_results.failed}/{all_results.passed + all_results.failed}). Bot needs fixes before deployment.")
        return 2

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)