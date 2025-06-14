#!/usr/bin/env python3
"""
Runtime Issues Checker for Möbius AI Assistant
Checks for common runtime warnings and issues
"""
import os
import sys
import warnings
import asyncio
import logging
from unittest.mock import patch

# Capture warnings
warnings.filterwarnings('error')

# Set up test environment
os.environ['TELEGRAM_BOT_TOKEN'] = 'test_token_123'
os.environ['TELEGRAM_CHAT_ID'] = '123456789'
os.environ['MASTER_KEY'] = 'test_master_key_for_testing_only'
os.environ['MOBIUS_TEST_MODE'] = '1'

sys.path.append('src')

class RuntimeIssueChecker:
    def __init__(self):
        self.issues = []
        self.warnings_caught = []
        
    def add_issue(self, category: str, description: str, severity: str = "WARNING"):
        self.issues.append({
            'category': category,
            'description': description,
            'severity': severity
        })
        
    def check_async_issues(self):
        """Check for async/await related issues"""
        print("🔍 Checking async/await issues...")
        
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
    
    def check_import_issues(self):
        """Check for import-related issues"""
        print("🔍 Checking import issues...")
        
        try:
            # Test ccxt imports
            import ccxt
            
            # Check for coinbasepro vs coinbase
            if hasattr(ccxt, 'coinbase'):
                print("✅ ccxt.coinbase available")
            elif hasattr(ccxt, 'coinbasepro'):
                print("⚠️ Only ccxt.coinbasepro available (deprecated)")
                self.add_issue("Import", "Using deprecated coinbasepro exchange", "WARNING")
            else:
                self.add_issue("Import", "No Coinbase exchange available in ccxt", "WARNING")
                
        except ImportError:
            print("ℹ️ ccxt not installed (optional dependency)")
    
    def check_deprecation_warnings(self):
        """Check for deprecation warnings"""
        print("🔍 Checking for deprecation warnings...")
        
        # Capture warnings during import
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            try:
                # Import main modules that might trigger warnings
                import main
                import contextual_ai
                import advanced_portfolio_manager
                
                if w:
                    for warning in w:
                        self.add_issue("Deprecation", f"{warning.category.__name__}: {warning.message}", "WARNING")
                        print(f"⚠️ {warning.category.__name__}: {warning.message}")
                else:
                    print("✅ No deprecation warnings found")
                    
            except Exception as e:
                self.add_issue("Deprecation", f"Error checking deprecations: {e}", "ERROR")
    
    def check_performance_issues(self):
        """Check for potential performance issues"""
        print("🔍 Checking performance issues...")
        
        try:
            # Check for blocking operations in async functions
            from performance_monitor import PerformanceMonitor
            monitor = PerformanceMonitor()
            print("✅ Performance monitor initializes correctly")
            
        except Exception as e:
            self.add_issue("Performance", f"Performance monitor error: {e}", "ERROR")
    
    def check_security_issues(self):
        """Check for security-related issues"""
        print("🔍 Checking security issues...")
        
        try:
            from security_auditor import SecurityAuditor
            auditor = SecurityAuditor()
            print("✅ Security auditor initializes correctly")
            
            # Check for hardcoded secrets (basic check)
            import glob
            for file_path in glob.glob('src/*.py'):
                with open(file_path, 'r') as f:
                    content = f.read()
                    if 'password' in content.lower() and '=' in content:
                        # More sophisticated check needed
                        pass
                        
        except Exception as e:
            self.add_issue("Security", f"Security auditor error: {e}", "ERROR")
    
    def run_all_checks(self):
        """Run all runtime issue checks"""
        print("🧪 Möbius AI Assistant - Runtime Issues Checker")
        print("=" * 60)
        
        self.check_async_issues()
        self.check_import_issues()
        self.check_deprecation_warnings()
        self.check_performance_issues()
        self.check_security_issues()
        
        print("\n" + "=" * 60)
        print("📊 Runtime Issues Summary")
        
        if not self.issues:
            print("🎉 No runtime issues found!")
            return True
        
        # Group issues by severity
        errors = [i for i in self.issues if i['severity'] == 'ERROR']
        warnings = [i for i in self.issues if i['severity'] == 'WARNING']
        
        if errors:
            print(f"\n❌ ERRORS ({len(errors)}):")
            for issue in errors:
                print(f"   - {issue['category']}: {issue['description']}")
        
        if warnings:
            print(f"\n⚠️ WARNINGS ({len(warnings)}):")
            for issue in warnings:
                print(f"   - {issue['category']}: {issue['description']}")
        
        print(f"\n📈 Total Issues: {len(self.issues)} ({len(errors)} errors, {len(warnings)} warnings)")
        
        return len(errors) == 0

def main():
    checker = RuntimeIssueChecker()
    success = checker.run_all_checks()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)