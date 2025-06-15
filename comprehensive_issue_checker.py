#!/usr/bin/env python3
"""
Comprehensive Issue Checker for Möbius AI Assistant
Checks for all types of runtime issues, warnings, and potential problems
"""
import os
import sys
import warnings
import asyncio
import logging
import traceback
from unittest.mock import patch

# Capture warnings
warnings.filterwarnings('error')

# Set up test environment
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token_123'
os.environ['TELEGRAM_CHAT_ID'] = '123456789'
os.environ['MASTER_KEY'] = 'test_master_key_for_testing_only'
os.environ['MOBIUS_TEST_MODE'] = '1'

sys.path.append('src')

class ComprehensiveIssueChecker:
    def __init__(self):
        self.issues = []
        self.warnings_caught = []
        
    def add_issue(self, category: str, description: str, severity: str = "WARNING", fix_suggestion: str = None):
        self.issues.append({
            'category': category,
            'description': description,
            'severity': severity,
            'fix_suggestion': fix_suggestion
        })
        
    def check_telegram_bot_issues(self):
        """Check for Telegram bot specific issues"""
        print("🤖 Checking Telegram Bot Issues...")
        
        try:
            # Check for ConversationHandler warnings
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                
                # Import main to trigger any warnings
                import main
                
                # Check for PTBUserWarning
                for warning in w:
                    if "PTBUserWarning" in str(warning.category):
                        self.add_issue(
                            "Telegram Bot", 
                            f"PTBUserWarning: {warning.message}",
                            "WARNING",
                            "Add per_message=True to ConversationHandler and CallbackQueryHandler"
                        )
                        
        except Exception as e:
            self.add_issue("Telegram Bot", f"Error checking telegram bot issues: {e}", "ERROR")
    
    def check_performance_decorator_issues(self):
        """Check for performance decorator issues"""
        print("⚡ Checking Performance Decorator Issues...")
        
        try:
            from performance_monitor import track_performance
            
            # Test the decorator with a mock function
            @track_performance.track_command("test")
            async def test_function(update, context):
                return "test"
            
            # Try to call it with mock arguments
            class MockUpdate:
                class MockUser:
                    id = 12345
                effective_user = MockUser()
            
            class MockContext:
                pass
            
            # Test if the decorator works correctly
            async def test_decorator():
                try:
                    result = await test_function(MockUpdate(), MockContext())
                    print("✅ Performance decorator works correctly")
                    return True
                except Exception as e:
                    self.add_issue(
                        "Performance", 
                        f"Performance decorator error: {e}",
                        "ERROR",
                        "Fix track_function method in PerformanceDecorator class"
                    )
                    return False
            
            # Run the test
            asyncio.run(test_decorator())
            
        except Exception as e:
            self.add_issue("Performance", f"Error testing performance decorator: {e}", "ERROR")
    
    def check_mock_feature_issues(self):
        """Check for MockFeature implementation issues"""
        print("🎭 Checking MockFeature Issues...")
        
        try:
            # Test if MockFeature has all required methods
            from main import MockFeature
            
            mock = MockFeature()
            required_methods = [
                'process_query',
                'get_portfolio_overview', 
                'create_alert',
                'check_feature_access'
            ]
            
            for method in required_methods:
                if not hasattr(mock, method):
                    self.add_issue(
                        "Mock Feature",
                        f"MockFeature missing method: {method}",
                        "ERROR",
                        f"Add {method} method to MockFeature class"
                    )
                else:
                    # Test if method is callable
                    if not callable(getattr(mock, method)):
                        self.add_issue(
                            "Mock Feature",
                            f"MockFeature method {method} is not callable",
                            "ERROR",
                            f"Make {method} a proper method in MockFeature class"
                        )
            
            print("✅ MockFeature implementation checked")
            
        except Exception as e:
            self.add_issue("Mock Feature", f"Error checking MockFeature: {e}", "ERROR")
    
    def check_whop_integration_issues(self):
        """Check for Whop API integration issues"""
        print("💳 Checking Whop Integration Issues...")
        
        try:
            # Check if both old and new Whop config options are handled
            from config import config
            
            has_api_key = config.get('WHOP_API_KEY') is not None
            has_bearer_token = config.get('WHOP_BEARER_TOKEN') is not None
            
            if not has_api_key and not has_bearer_token:
                self.add_issue(
                    "Whop Integration",
                    "No Whop authentication configured",
                    "WARNING",
                    "Set WHOP_API_KEY (recommended) or WHOP_BEARER_TOKEN in environment"
                )
            elif has_bearer_token and not has_api_key:
                self.add_issue(
                    "Whop Integration",
                    "Using deprecated WHOP_BEARER_TOKEN",
                    "WARNING",
                    "Migrate to WHOP_API_KEY for better security"
                )
            else:
                print("✅ Whop integration configuration looks good")
                
        except Exception as e:
            self.add_issue("Whop Integration", f"Error checking Whop integration: {e}", "ERROR")
    
    def check_async_await_issues(self):
        """Check for async/await related issues"""
        print("🔄 Checking Async/Await Issues...")
        
        try:
            # Test contextual AI initialization
            from contextual_ai import ContextualAI
            
            # Test without event loop
            try:
                ai = ContextualAI()
                print("✅ ContextualAI initializes without event loop")
            except Exception as e:
                self.add_issue("Async", f"ContextualAI initialization error: {e}", "ERROR")
            
            # Test with event loop
            async def test_with_loop():
                try:
                    ai = ContextualAI()
                    if hasattr(ai, 'start_cleanup_task'):
                        ai.start_cleanup_task()
                    print("✅ ContextualAI works with event loop")
                    return True
                except Exception as e:
                    self.add_issue("Async", f"ContextualAI with loop error: {e}", "ERROR")
                    return False
            
            # Run async test
            result = asyncio.run(test_with_loop())
            
        except Exception as e:
            self.add_issue("Async", f"Failed to test async functionality: {e}", "ERROR")
    
    def check_import_and_dependency_issues(self):
        """Check for import and dependency issues"""
        print("📦 Checking Import and Dependency Issues...")
        
        try:
            # Test ccxt imports
            try:
                import ccxt
                
                # Check for coinbasepro vs coinbase
                if hasattr(ccxt, 'coinbase'):
                    print("✅ ccxt.coinbase available")
                elif hasattr(ccxt, 'coinbasepro'):
                    self.add_issue(
                        "Import", 
                        "Using deprecated coinbasepro exchange",
                        "WARNING",
                        "Update code to use ccxt.coinbase instead of ccxt.coinbasepro"
                    )
                else:
                    self.add_issue("Import", "No Coinbase exchange available in ccxt", "WARNING")
                    
            except ImportError:
                print("ℹ️ ccxt not installed (optional dependency)")
            
            # Test other optional dependencies
            optional_deps = ['groq', 'openai', 'google.generativeai', 'anthropic']
            missing_deps = []
            
            for dep in optional_deps:
                try:
                    __import__(dep)
                except ImportError:
                    missing_deps.append(dep)
            
            if missing_deps:
                self.add_issue(
                    "Dependencies",
                    f"Optional dependencies missing: {', '.join(missing_deps)}",
                    "INFO",
                    "Install with: pip install groq openai google-generativeai anthropic"
                )
            
        except Exception as e:
            self.add_issue("Import", f"Error checking imports: {e}", "ERROR")
    
    def check_error_handling_issues(self):
        """Check for error handling issues"""
        print("🛡️ Checking Error Handling Issues...")
        
        try:
            # Check if main.py has error handlers
            with open('src/main.py', 'r') as f:
                content = f.read()
                
            if 'add_error_handler' not in content:
                self.add_issue(
                    "Error Handling",
                    "No error handler registered in main application",
                    "ERROR",
                    "Add application.add_error_handler(error_handler) to main.py"
                )
            else:
                print("✅ Error handler found in main application")
                
        except Exception as e:
            self.add_issue("Error Handling", f"Error checking error handlers: {e}", "ERROR")
    
    def check_security_issues(self):
        """Check for security-related issues"""
        print("🔒 Checking Security Issues...")
        
        try:
            # Check for hardcoded secrets
            import glob
            
            suspicious_patterns = [
                'password = ',
                'secret = ',
                'token = ',
                'key = ',
                'api_key = '
            ]
            
            for file_path in glob.glob('src/*.py'):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    for pattern in suspicious_patterns:
                        if pattern in content.lower():
                            # Check if it's actually hardcoded (not from config)
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if pattern in line.lower() and 'config.get' not in line and '#' not in line:
                                    self.add_issue(
                                        "Security",
                                        f"Potential hardcoded secret in {file_path}:{i+1}",
                                        "WARNING",
                                        "Use config.get() or environment variables instead"
                                    )
                except Exception:
                    continue
            
            print("✅ Security check completed")
            
        except Exception as e:
            self.add_issue("Security", f"Error checking security: {e}", "ERROR")
    
    def run_all_checks(self):
        """Run all comprehensive issue checks"""
        print("🔍 Möbius AI Assistant - Comprehensive Issue Checker")
        print("=" * 70)
        
        self.check_telegram_bot_issues()
        self.check_performance_decorator_issues()
        self.check_mock_feature_issues()
        self.check_whop_integration_issues()
        self.check_async_await_issues()
        self.check_import_and_dependency_issues()
        self.check_error_handling_issues()
        self.check_security_issues()
        
        print("\n" + "=" * 70)
        print("📊 Comprehensive Issues Summary")
        
        if not self.issues:
            print("🎉 No issues found! Bot is in excellent condition.")
            return True
        
        # Group issues by severity
        errors = [i for i in self.issues if i['severity'] == 'ERROR']
        warnings = [i for i in self.issues if i['severity'] == 'WARNING']
        info = [i for i in self.issues if i['severity'] == 'INFO']
        
        if errors:
            print(f"\n❌ ERRORS ({len(errors)}) - Must be fixed:")
            for issue in errors:
                print(f"   - {issue['category']}: {issue['description']}")
                if issue.get('fix_suggestion'):
                    print(f"     💡 Fix: {issue['fix_suggestion']}")
        
        if warnings:
            print(f"\n⚠️ WARNINGS ({len(warnings)}) - Should be addressed:")
            for issue in warnings:
                print(f"   - {issue['category']}: {issue['description']}")
                if issue.get('fix_suggestion'):
                    print(f"     💡 Fix: {issue['fix_suggestion']}")
        
        if info:
            print(f"\nℹ️ INFO ({len(info)}) - Optional improvements:")
            for issue in info:
                print(f"   - {issue['category']}: {issue['description']}")
                if issue.get('fix_suggestion'):
                    print(f"     💡 Suggestion: {issue['fix_suggestion']}")
        
        print(f"\n📈 Total Issues: {len(self.issues)} ({len(errors)} errors, {len(warnings)} warnings, {len(info)} info)")
        
        return len(errors) == 0

def main():
    checker = ComprehensiveIssueChecker()
    success = checker.run_all_checks()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)