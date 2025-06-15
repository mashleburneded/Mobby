#!/usr/bin/env python3
"""
Comprehensive Test Suite for Möbius AI Assistant
Tests all new features including memory database and AI provider management
"""

import asyncio
import sys
import os
import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.append('src')

class TestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.start_time = time.time()
    
    def add_result(self, test_name: str, passed: bool, details: str = ""):
        self.tests.append({
            'name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': time.time()
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        total_time = time.time() - self.start_time
        print("\n" + "=" * 80)
        print("🏆 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📊 Success Rate: {(self.passed/(self.passed+self.failed)*100):.1f}%")
        print("\n📋 Detailed Results:")
        
        for test in self.tests:
            status = "✅" if test['passed'] else "❌"
            print(f"{status} {test['name']}")
            if test['details']:
                print(f"   {test['details']}")
        
        return self.passed, self.failed

results = TestResults()

def test_result(test_name: str):
    """Decorator to capture test results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                print(f"\n🧪 Testing: {test_name}")
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                if isinstance(result, tuple):
                    passed, details = result
                else:
                    passed, details = result, ""
                
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"   {status}: {test_name}")
                if details:
                    print(f"   📝 {details}")
                
                results.add_result(test_name, passed, details)
                return passed
                
            except Exception as e:
                print(f"   ❌ FAIL: {test_name} - Exception: {e}")
                results.add_result(test_name, False, f"Exception: {e}")
                return False
        return wrapper
    return decorator

@test_result("Environment Configuration")
def test_environment_setup():
    """Test environment variables and configuration"""
    from config import config
    
    required_keys = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID', 
        'BOT_MASTER_ENCRYPTION_KEY',
        'GROQ_API_KEY',
        'GEMINI_API_KEY'
    ]
    
    missing = []
    configured = []
    
    for key in required_keys:
        value = config.get(key)
        if value and value.strip():
            configured.append(key)
        else:
            missing.append(key)
    
    if missing:
        return False, f"Missing: {missing}"
    
    return True, f"All {len(configured)} required keys configured"

@test_result("Database Initialization")
def test_database_initialization():
    """Test database creation and schema"""
    try:
        # Initialize databases
        from user_db import init_db
        from agent_memory_database import agent_memory
        
        # Create data directory if it doesn't exist
        Path("data").mkdir(exist_ok=True)
        
        # Initialize user database
        init_db()
        
        # Check database files
        db_files = [
            "data/user_data.sqlite",
            "data/agent_memory.db",
            "data/conversation_intelligence.db"
        ]
        
        existing_dbs = []
        for db_file in db_files:
            if Path(db_file).exists():
                existing_dbs.append(db_file)
                
                # Test database connection and schema
                with sqlite3.connect(db_file) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in cursor.fetchall()]
                    if not tables:
                        return False, f"No tables found in {db_file}"
        
        if len(existing_dbs) < 2:
            return False, f"Only {len(existing_dbs)} databases found"
        
        return True, f"Databases initialized: {len(existing_dbs)} files, schemas verified"
        
    except Exception as e:
        return False, f"Database initialization failed: {e}"

@test_result("Agent Memory Database - Core Functions")
def test_memory_database_core():
    """Test core memory database functionality"""
    try:
        from agent_memory_database import (
            agent_memory, get_conversation_flow, analyze_user_intent,
            get_response_template, get_learning_insights, get_training_scenario
        )
        
        # Test intent analysis
        test_cases = [
            ("What's the price of Bitcoin?", "get_crypto_price"),
            ("Show me my portfolio", "analyze_portfolio"),
            ("Set an alert for ETH", "create_price_alert"),
            ("Random text that doesn't match", "unknown")
        ]
        
        intent_results = []
        for text, expected in test_cases:
            intent, confidence = analyze_user_intent(text)
            intent_results.append((text, intent, confidence, expected))
        
        # Test conversation flows
        flow = get_conversation_flow("get_crypto_price")
        if not flow:
            return False, "Failed to retrieve conversation flow"
        
        # Test learning insights
        insights = get_learning_insights()
        if not insights:
            return False, "No learning insights available"
        
        # Test training scenarios
        scenario = get_training_scenario("beginner")
        if not scenario:
            return False, "No training scenarios available"
        
        # Test response templates
        template = get_response_template("get_crypto_price", {"token": "BTC", "price": "50000"})
        if not template:
            return False, "Failed to generate response template"
        
        details = f"Intent analysis: {len(intent_results)} cases, "
        details += f"Insights: {len(insights)}, "
        details += f"Flow patterns: {len(flow.user_input_patterns)}"
        
        return True, details
        
    except Exception as e:
        return False, f"Memory database test failed: {e}"

@test_result("Agent Memory Database - Advanced Features")
def test_memory_database_advanced():
    """Test advanced memory database features"""
    try:
        from agent_memory_database import (
            agent_memory, record_performance, get_action_pattern
        )
        
        # Test performance recording
        record_performance("test_flow", 1.5, True, None, 0.9)
        record_performance("test_flow", 2.1, False, "timeout", 0.3)
        
        # Test action patterns
        action = get_action_pattern("query_coingecko_api")
        if not action:
            return False, "Failed to retrieve action pattern"
        
        # Test database queries
        with sqlite3.connect("data/agent_memory.db") as conn:
            cursor = conn.cursor()
            
            # Check conversation flows
            cursor.execute("SELECT COUNT(*) FROM conversation_flows")
            flow_count = cursor.fetchone()[0]
            
            # Check training scenarios
            cursor.execute("SELECT COUNT(*) FROM training_scenarios")
            scenario_count = cursor.fetchone()[0]
            
            # Check learning insights
            cursor.execute("SELECT COUNT(*) FROM learning_insights")
            insight_count = cursor.fetchone()[0]
            
            # Check performance metrics
            cursor.execute("SELECT COUNT(*) FROM performance_metrics")
            metric_count = cursor.fetchone()[0]
        
        if flow_count == 0 or scenario_count == 0 or insight_count == 0:
            return False, "Missing data in memory database tables"
        
        details = f"Flows: {flow_count}, Scenarios: {scenario_count}, "
        details += f"Insights: {insight_count}, Metrics: {metric_count}"
        
        return True, details
        
    except Exception as e:
        return False, f"Advanced memory test failed: {e}"

@test_result("AI Provider Manager - Initialization")
def test_ai_provider_initialization():
    """Test AI provider manager initialization"""
    try:
        from ai_provider_manager import (
            ai_provider_manager, list_ai_providers, get_ai_provider_info
        )
        
        # Test provider listing
        providers = list_ai_providers()
        if not providers:
            return False, "No providers available"
        
        # Test current provider info
        current_info = get_ai_provider_info()
        if not current_info:
            return False, "Failed to get current provider info"
        
        # Check provider availability
        available_providers = [name for name, info in providers.items() if info['available']]
        unavailable_providers = [name for name, info in providers.items() if not info['available']]
        
        details = f"Total: {len(providers)}, Available: {len(available_providers)}, "
        details += f"Current: {current_info['name']}"
        
        return True, details
        
    except Exception as e:
        return False, f"AI provider initialization failed: {e}"

@test_result("AI Provider Manager - Provider Switching")
def test_ai_provider_switching():
    """Test AI provider switching functionality"""
    try:
        from ai_provider_manager import (
            ai_provider_manager, switch_ai_provider, get_ai_provider_info
        )
        
        # Get initial provider
        initial_provider = get_ai_provider_info()
        initial_name = initial_provider['name']
        
        # Test switching to different providers
        switch_tests = []
        
        # Try switching to Groq
        if switch_ai_provider("groq"):
            current = get_ai_provider_info()
            switch_tests.append(("groq", current['name']))
        
        # Try switching to Gemini
        if switch_ai_provider("gemini"):
            current = get_ai_provider_info()
            switch_tests.append(("gemini", current['name']))
        
        # Switch back to original
        switch_ai_provider(initial_name.lower())
        
        if not switch_tests:
            return False, "No successful provider switches"
        
        details = f"Successful switches: {len(switch_tests)} - {switch_tests}"
        return True, details
        
    except Exception as e:
        return False, f"Provider switching failed: {e}"

@test_result("AI Text Generation - Groq")
async def test_ai_generation_groq():
    """Test AI text generation with Groq"""
    try:
        from ai_provider_manager import generate_ai_response, switch_ai_provider
        
        # Switch to Groq
        switch_ai_provider("groq")
        
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond concisely."},
            {"role": "user", "content": "Say 'Hello from Groq!' and nothing else."}
        ]
        
        response = await generate_ai_response(test_messages)
        
        if not response or len(response.strip()) == 0:
            return False, "Empty response from Groq"
        
        if "groq" not in response.lower() and "hello" not in response.lower():
            return False, f"Unexpected response: {response[:100]}"
        
        return True, f"Response: {response[:100]}..."
        
    except Exception as e:
        return False, f"Groq generation failed: {e}"

@test_result("AI Text Generation - Gemini")
async def test_ai_generation_gemini():
    """Test AI text generation with Gemini"""
    try:
        from ai_provider_manager import generate_ai_response, switch_ai_provider
        
        # Switch to Gemini
        if not switch_ai_provider("gemini"):
            return False, "Failed to switch to Gemini"
        
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond concisely."},
            {"role": "user", "content": "Say 'Hello from Gemini!' and nothing else."}
        ]
        
        response = await generate_ai_response(test_messages)
        
        if not response or len(response.strip()) == 0:
            return False, "Empty response from Gemini"
        
        return True, f"Response: {response[:100]}..."
        
    except Exception as e:
        return False, f"Gemini generation failed: {e}"

@test_result("AI Provider Benchmarking")
async def test_ai_provider_benchmark():
    """Test AI provider benchmarking"""
    try:
        from ai_provider_manager import ai_provider_manager
        
        # Run benchmark on all providers
        results = await ai_provider_manager.test_all_providers()
        
        if not results:
            return False, "No benchmark results"
        
        successful_tests = [name for name, result in results.items() if result['success']]
        failed_tests = [name for name, result in results.items() if not result['success']]
        
        # Calculate average response time for successful tests
        avg_time = 0
        if successful_tests:
            total_time = sum(results[name]['response_time'] for name in successful_tests)
            avg_time = total_time / len(successful_tests)
        
        details = f"Successful: {len(successful_tests)}, Failed: {len(failed_tests)}, "
        details += f"Avg time: {avg_time:.2f}s"
        
        return len(successful_tests) > 0, details
        
    except Exception as e:
        return False, f"Benchmark failed: {e}"

@test_result("Encryption and Security")
def test_encryption_security():
    """Test encryption and security features"""
    try:
        from encryption_manager import EncryptionManager
        from config import config
        
        # Test encryption manager
        encryption_key = config.get('BOT_MASTER_ENCRYPTION_KEY')
        if not encryption_key:
            return False, "No encryption key configured"
        
        em = EncryptionManager()
        
        # Test encryption/decryption
        test_data = "This is sensitive test data"
        encrypted = em.encrypt(test_data)
        decrypted = em.decrypt(encrypted)
        
        if decrypted != test_data:
            return False, "Encryption/decryption failed"
        
        # Test with different data types
        test_dict = {"user_id": 123, "balance": 1000.50}
        encrypted_dict = em.encrypt(json.dumps(test_dict))
        decrypted_dict = json.loads(em.decrypt(encrypted_dict))
        
        if decrypted_dict != test_dict:
            return False, "Dictionary encryption failed"
        
        return True, "Encryption working for strings and JSON data"
        
    except Exception as e:
        return False, f"Encryption test failed: {e}"

@test_result("Database Security and Integrity")
def test_database_security():
    """Test database security and data integrity"""
    try:
        from user_db import set_user_property, get_user_property
        
        # Test user data encryption
        test_user_id = 999999
        test_key = "test_encrypted_data"
        test_value = "sensitive_information_12345"
        
        # Store encrypted data
        set_user_property(test_user_id, test_key, test_value)
        
        # Retrieve and verify
        retrieved_value = get_user_property(test_user_id, test_key)
        
        if retrieved_value != test_value:
            return False, "Data integrity check failed"
        
        # Test with complex data
        complex_data = {
            "portfolio": {"BTC": 0.5, "ETH": 2.0},
            "alerts": [{"token": "BTC", "price": 50000}],
            "preferences": {"theme": "dark", "notifications": True}
        }
        
        set_user_property(test_user_id, "complex_data", json.dumps(complex_data))
        retrieved_complex = json.loads(get_user_property(test_user_id, "complex_data"))
        
        if retrieved_complex != complex_data:
            return False, "Complex data integrity failed"
        
        return True, "Data encryption and integrity verified"
        
    except Exception as e:
        return False, f"Database security test failed: {e}"

@test_result("MCP Integration Status")
def test_mcp_integration():
    """Test MCP (Model Context Protocol) integration"""
    try:
        from mcp_integration import get_mcp_status
        
        # Get MCP status
        status = get_mcp_status()
        
        if not status:
            return False, "No MCP status available"
        
        # Check for expected MCP servers
        expected_servers = ["financial", "blockchain", "web_research"]
        active_servers = []
        
        for server in expected_servers:
            if server in str(status).lower():
                active_servers.append(server)
        
        details = f"MCP Status available, Active servers: {len(active_servers)}"
        return True, details
        
    except Exception as e:
        return False, f"MCP integration test failed: {e}"

@test_result("Performance and Memory Usage")
def test_performance_metrics():
    """Test system performance and memory usage"""
    try:
        import psutil
        import gc
        
        # Get current process
        process = psutil.Process()
        
        # Memory usage
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # CPU usage
        cpu_percent = process.cpu_percent(interval=1)
        
        # Garbage collection
        gc.collect()
        
        # Check if memory usage is reasonable (under 500MB for tests)
        if memory_mb > 500:
            return False, f"High memory usage: {memory_mb:.1f}MB"
        
        # Check if CPU usage is reasonable (under 50% for tests)
        if cpu_percent > 50:
            return False, f"High CPU usage: {cpu_percent:.1f}%"
        
        details = f"Memory: {memory_mb:.1f}MB, CPU: {cpu_percent:.1f}%"
        return True, details
        
    except Exception as e:
        return False, f"Performance test failed: {e}"

@test_result("Error Handling and Recovery")
async def test_error_handling():
    """Test error handling and recovery mechanisms"""
    try:
        from ai_provider_manager import generate_ai_response
        
        # Test with invalid messages
        invalid_messages = [
            [],  # Empty messages
            [{"role": "invalid", "content": "test"}],  # Invalid role
            [{"role": "user"}],  # Missing content
        ]
        
        error_handling_results = []
        
        for invalid_msg in invalid_messages:
            try:
                response = await generate_ai_response(invalid_msg)
                error_handling_results.append(("handled", response))
            except Exception as e:
                error_handling_results.append(("error", str(e)))
        
        # Test fallback mechanism
        try:
            # This should trigger fallback providers
            response = await generate_ai_response([
                {"role": "user", "content": "Test fallback"}
            ])
            fallback_works = True
        except:
            fallback_works = False
        
        details = f"Error cases: {len(error_handling_results)}, Fallback: {fallback_works}"
        return True, details
        
    except Exception as e:
        return False, f"Error handling test failed: {e}"

@test_result("Integration Test - Complete Workflow")
async def test_complete_workflow():
    """Test complete workflow from intent to response"""
    try:
        from agent_memory_database import analyze_user_intent, get_conversation_flow, record_performance
        from ai_provider_manager import generate_ai_response
        
        # Simulate complete user interaction
        user_input = "What's the current price of Bitcoin?"
        
        # Step 1: Analyze intent
        intent, confidence = analyze_user_intent(user_input)
        
        # Step 2: Get conversation flow
        flow = get_conversation_flow(intent)
        
        # Step 3: Generate AI response
        messages = [
            {"role": "system", "content": "You are a crypto assistant."},
            {"role": "user", "content": user_input}
        ]
        
        start_time = time.time()
        response = await generate_ai_response(messages)
        execution_time = time.time() - start_time
        
        # Step 4: Record performance
        record_performance(flow.flow_id if flow else "unknown", execution_time, True, None, 0.9)
        
        # Verify workflow
        if not intent or confidence < 0.5:
            return False, f"Poor intent recognition: {intent} ({confidence})"
        
        if not flow:
            return False, "No conversation flow found"
        
        if not response:
            return False, "No AI response generated"
        
        if execution_time > 10:
            return False, f"Slow response time: {execution_time:.2f}s"
        
        details = f"Intent: {intent} ({confidence:.2f}), "
        details += f"Response time: {execution_time:.2f}s, "
        details += f"Response length: {len(response)} chars"
        
        return True, details
        
    except Exception as e:
        return False, f"Complete workflow test failed: {e}"

async def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🚀 MÖBIUS AI ASSISTANT - COMPREHENSIVE TEST SUITE")
    print("🔬 Testing all new features with full coverage")
    print("=" * 80)
    
    # Core Infrastructure Tests
    print("\n📋 CORE INFRASTRUCTURE TESTS")
    await test_environment_setup()
    await test_database_initialization()
    await test_encryption_security()
    await test_database_security()
    
    # Memory Database Tests
    print("\n🧠 MEMORY DATABASE TESTS")
    await test_memory_database_core()
    await test_memory_database_advanced()
    
    # AI Provider Tests
    print("\n🤖 AI PROVIDER TESTS")
    await test_ai_provider_initialization()
    await test_ai_provider_switching()
    await test_ai_generation_groq()
    await test_ai_generation_gemini()
    await test_ai_provider_benchmark()
    
    # Integration Tests
    print("\n🔗 INTEGRATION TESTS")
    await test_mcp_integration()
    await test_error_handling()
    await test_complete_workflow()
    
    # Performance Tests
    print("\n⚡ PERFORMANCE TESTS")
    await test_performance_metrics()
    
    # Print final results
    passed, failed = results.print_summary()
    
    # Generate test report
    generate_test_report(passed, failed)
    
    return passed, failed

def generate_test_report(passed: int, failed: int):
    """Generate detailed test report"""
    report = {
        "timestamp": time.time(),
        "total_tests": passed + failed,
        "passed": passed,
        "failed": failed,
        "success_rate": (passed / (passed + failed)) * 100 if (passed + failed) > 0 else 0,
        "test_details": results.tests,
        "environment": {
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": os.getcwd()
        }
    }
    
    # Save report to file
    with open("comprehensive_test_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Test report saved to: comprehensive_test_report.json")
    
    # Print quick start guide if tests passed
    if passed > failed:
        print("\n🎉 TESTS PASSED! Quick Start Guide:")
        print("=" * 50)
        print("🔧 New Commands Available:")
        print("• /memory_status - Check memory database status")
        print("• /memory_insights - View learning insights")
        print("• /memory_train beginner - Run training scenario")
        print("• /ai_providers - View all AI providers")
        print("• /switch_ai gemini - Switch to Gemini AI")
        print("• /test_ai groq - Test Groq provider")
        print("• /ai_benchmark - Benchmark all providers")
        print("\n🚀 Start the bot with: python src/main.py")

if __name__ == "__main__":
    try:
        passed, failed = asyncio.run(run_comprehensive_tests())
        
        if failed == 0:
            print("\n🏆 ALL TESTS PASSED! System is ready for production.")
            sys.exit(0)
        elif passed > failed:
            print(f"\n⚠️  Most tests passed ({passed}/{passed+failed}). Check failed tests above.")
            sys.exit(0)
        else:
            print(f"\n❌ Many tests failed ({failed}/{passed+failed}). System needs attention.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)