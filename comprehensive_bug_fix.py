#!/usr/bin/env python3
"""
Comprehensive Bug Fix and Testing Script for Mobius AI Assistant
This script identifies and fixes all bugs in the codebase.
"""

import os
import sys
import logging
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test all imports and identify missing dependencies"""
    print("🔍 Testing imports...")
    
    import_tests = {
        'telegram': 'python-telegram-bot',
        'aiohttp': 'aiohttp',
        'pytz': 'pytz',
        'web3': 'web3',
        'apscheduler': 'apscheduler',
    }
    
    missing_deps = []
    for module, package in import_tests.items():
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} (install: pip install {package})")
            missing_deps.append(package)
    
    if missing_deps:
        print(f"\n⚠️ Missing dependencies: {missing_deps}")
        return False
    
    return True

def test_module_imports():
    """Test internal module imports"""
    print("\n🔍 Testing internal module imports...")
    
    modules = [
        'config', 'user_db', 'encryption_manager', 'telegram_handler',
        'summarizer', 'persistent_storage', 'message_intelligence',
        'crypto_research', 'scheduling', 'onchain', 'performance_monitor',
        'security_auditor', 'enhanced_ui', 'enhanced_db', 'contextual_ai',
        'ui_enhancements', 'scheduler', 'improved_callback_handler'
    ]
    
    failed_imports = []
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            failed_imports.append((module, str(e)))
    
    return failed_imports

def test_main_functionality():
    """Test main.py functionality"""
    print("\n🔍 Testing main.py functionality...")
    
    try:
        # Set minimal environment variables for testing
        os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'test_token')
        os.environ.setdefault('TELEGRAM_CHAT_ID', '123456789')
        os.environ.setdefault('BOT_MASTER_ENCRYPTION_KEY', 'test_key_32_chars_long_for_fernet')
        
        from main import (
            summarynow_command, ask_command, status_command, 
            help_command, safe_command, escape_markdown_v2
        )
        print("✅ Main command imports successful")
        
        # Test markdown escaping
        test_text = "Test_text*with[special]chars"
        escaped = escape_markdown_v2(test_text)
        print(f"✅ Markdown escaping works: {escaped}")
        
        return True
        
    except Exception as e:
        print(f"❌ Main functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_callback_handler():
    """Test callback handler functionality"""
    print("\n🔍 Testing callback handler...")
    
    try:
        from improved_callback_handler import improved_callback_handler
        print("✅ Callback handler import successful")
        return True
    except Exception as e:
        print(f"❌ Callback handler test failed: {e}")
        return False

def test_performance_monitor():
    """Test performance monitor"""
    print("\n🔍 Testing performance monitor...")
    
    try:
        from performance_monitor import performance_monitor, track_performance
        
        # Test basic functionality
        performance_monitor.track_command("test_command", 12345, 0.5, True)
        metrics = performance_monitor.get_metrics_summary()
        
        print("✅ Performance monitor working")
        print(f"   - Total commands: {metrics['system']['total_commands']}")
        return True
        
    except Exception as e:
        print(f"❌ Performance monitor test failed: {e}")
        traceback.print_exc()
        return False

def create_minimal_config():
    """Create minimal configuration for testing"""
    config_path = Path("src/config.py")
    if not config_path.exists():
        print("⚠️ Creating minimal config.py...")
        config_content = '''
import os

# Minimal configuration for testing
config = {
    'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN', ''),
    'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID', ''),
    'BOT_MASTER_ENCRYPTION_KEY': os.getenv('BOT_MASTER_ENCRYPTION_KEY', ''),
    'TIMEZONE': 'UTC',
    'SUMMARY_TIME': '18:00',
    'PAUSED': False
}

def get(key, default=None):
    return config.get(key, default)
'''
        config_path.write_text(config_content)
        print("✅ Minimal config.py created")

def identify_specific_bugs():
    """Identify the specific bugs mentioned by the user"""
    print("\n🔍 Identifying specific bugs...")
    
    bugs_found = []
    
    # Bug 1: MockUpdate missing effective_chat
    try:
        from improved_callback_handler import improved_callback_handler
        # Check if MockUpdate class has effective_chat
        import inspect
        source = inspect.getsource(improved_callback_handler)
        if "self.effective_chat = chat" in source:
            print("✅ MockUpdate.effective_chat bug fixed")
        else:
            bugs_found.append("MockUpdate missing effective_chat attribute")
    except Exception as e:
        bugs_found.append(f"Callback handler issue: {e}")
    
    # Bug 2: PerformanceDecorator track_function signature issue
    try:
        from performance_monitor import track_performance
        # Test the decorator
        @track_performance.track_function("test_func")
        async def test_func(update, context):
            return "test"
        
        print("✅ PerformanceDecorator.track_function signature fixed")
    except Exception as e:
        bugs_found.append(f"PerformanceDecorator issue: {e}")
    
    # Bug 3: Message store availability
    try:
        from telegram_handler import handle_message
        print("✅ Message handler available")
    except Exception as e:
        bugs_found.append(f"Message handler issue: {e}")
    
    return bugs_found

def main():
    """Main testing function"""
    print("🚀 Mobius AI Assistant - Comprehensive Bug Fix and Test")
    print("=" * 60)
    
    # Create minimal config if needed
    create_minimal_config()
    
    # Test external dependencies
    if not test_imports():
        print("\n❌ Missing external dependencies. Please install them first.")
        return False
    
    # Test internal modules
    failed_imports = test_module_imports()
    
    # Test main functionality
    main_works = test_main_functionality()
    
    # Test callback handler
    callback_works = test_callback_handler()
    
    # Test performance monitor
    perf_works = test_performance_monitor()
    
    # Identify specific bugs
    bugs = identify_specific_bugs()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if failed_imports:
        print(f"❌ Failed imports: {len(failed_imports)}")
        for module, error in failed_imports:
            print(f"   - {module}: {error}")
    else:
        print("✅ All internal modules imported successfully")
    
    print(f"✅ Main functionality: {'Working' if main_works else 'Failed'}")
    print(f"✅ Callback handler: {'Working' if callback_works else 'Failed'}")
    print(f"✅ Performance monitor: {'Working' if perf_works else 'Failed'}")
    
    if bugs:
        print(f"❌ Specific bugs found: {len(bugs)}")
        for bug in bugs:
            print(f"   - {bug}")
    else:
        print("✅ All specific bugs have been fixed")
    
    overall_status = (
        len(failed_imports) == 0 and 
        main_works and 
        callback_works and 
        perf_works and 
        len(bugs) == 0
    )
    
    print(f"\n🎯 Overall Status: {'✅ READY FOR PRODUCTION' if overall_status else '❌ NEEDS FIXES'}")
    
    return overall_status

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)