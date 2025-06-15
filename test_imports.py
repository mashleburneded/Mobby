#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""
import sys
import os
sys.path.append('src')

# Set test mode to avoid config errors
os.environ['MOBIUS_TEST_MODE'] = '1'

def test_import(module_name):
    try:
        __import__(module_name)
        print(f'✅ {module_name} imports successfully')
        return True
    except Exception as e:
        print(f'❌ {module_name} import error: {e}')
        return False

def main():
    print("🧪 Testing imports for Möbius AI Assistant\n")
    
    # Core modules that should always work
    core_modules = [
        'config',
        'user_db', 
        'encryption_manager',
        'ai_providers'
    ]
    
    # Enhanced modules (may need dependencies)
    enhanced_modules = [
        'enhanced_db',
        'enhanced_ui',
        'contextual_ai',
        'performance_monitor',
        'security_auditor'
    ]
    
    # Comprehensive feature modules
    comprehensive_modules = [
        'tier_access_control',
        'advanced_portfolio_manager',
        'advanced_alerts',
        'natural_language_query',
        'social_trading',
        'advanced_research',
        'automated_trading',
        'cross_chain_analytics'
    ]
    
    print("📦 Core Modules:")
    core_success = all(test_import(module) for module in core_modules)
    
    print("\n🔧 Enhanced Modules:")
    enhanced_success = all(test_import(module) for module in enhanced_modules)
    
    print("\n🚀 Comprehensive Feature Modules:")
    comprehensive_success = all(test_import(module) for module in comprehensive_modules)
    
    print(f"\n📊 Results:")
    print(f"Core Modules: {'✅ PASS' if core_success else '❌ FAIL'}")
    print(f"Enhanced Modules: {'✅ PASS' if enhanced_success else '❌ FAIL'}")
    print(f"Comprehensive Modules: {'✅ PASS' if comprehensive_success else '❌ FAIL'}")
    
    if core_success:
        print("\n🎉 Bot can run with basic functionality!")
        if not enhanced_success or not comprehensive_success:
            print("💡 Install missing dependencies for full features:")
            print("   pip install -r requirements.txt")
    else:
        print("\n⚠️ Core functionality issues detected!")
        print("💡 Install core dependencies:")
        print("   ./install_dependencies.sh")

if __name__ == "__main__":
    main()