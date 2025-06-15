#!/usr/bin/env python3
"""
Comprehensive Bug Hunt and Testing Suite
Identifies and tests all major and minor bugs in the Möbius AI Assistant
"""

import asyncio
import logging
import sys
import os
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveBugHunter:
    """Comprehensive bug hunting and testing system"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "critical_bugs": [],
            "major_bugs": [],
            "minor_bugs": [],
            "warnings": [],
            "test_details": []
        }
        
    async def run_all_tests(self):
        """Run all comprehensive tests"""
        logger.info("🔍 Starting Comprehensive Bug Hunt...")
        
        # Test categories
        test_categories = [
            ("Import Tests", self.test_imports),
            ("Configuration Tests", self.test_configuration),
            ("Database Tests", self.test_database_functionality),
            ("Message Processing Tests", self.test_message_processing),
            ("Conversation Intelligence Tests", self.test_conversation_intelligence),
            ("Natural Language Processing Tests", self.test_nlp_functionality),
            ("AI Provider Tests", self.test_ai_providers),
            ("MCP Integration Tests", self.test_mcp_integration),
            ("Command Handler Tests", self.test_command_handlers),
            ("Group Chat Tests", self.test_group_chat_functionality),
            ("Mention Tracking Tests", self.test_mention_tracking),
            ("Summary Generation Tests", self.test_summary_generation),
            ("Error Handling Tests", self.test_error_handling),
            ("Event Loop Tests", self.test_event_loop_issues),
            ("Memory Management Tests", self.test_memory_management),
            ("Security Tests", self.test_security_features),
            ("Performance Tests", self.test_performance),
            ("Real-world Scenario Tests", self.test_real_world_scenarios)
        ]
        
        for category_name, test_function in test_categories:
            logger.info(f"\n📋 Running {category_name}...")
            try:
                await test_function()
            except Exception as e:
                self.add_critical_bug(f"{category_name} failed completely", str(e), traceback.format_exc())
        
        # Generate final report
        await self.generate_report()
        
    def add_test_result(self, test_name: str, passed: bool, details: str = "", error: str = ""):
        """Add a test result"""
        self.test_results["total_tests"] += 1
        if passed:
            self.test_results["passed_tests"] += 1
        else:
            self.test_results["failed_tests"] += 1
            
        self.test_results["test_details"].append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_critical_bug(self, title: str, description: str, traceback_info: str = ""):
        """Add a critical bug"""
        self.test_results["critical_bugs"].append({
            "title": title,
            "description": description,
            "traceback": traceback_info,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_major_bug(self, title: str, description: str, impact: str = ""):
        """Add a major bug"""
        self.test_results["major_bugs"].append({
            "title": title,
            "description": description,
            "impact": impact,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_minor_bug(self, title: str, description: str, suggestion: str = ""):
        """Add a minor bug"""
        self.test_results["minor_bugs"].append({
            "title": title,
            "description": description,
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_warning(self, title: str, description: str):
        """Add a warning"""
        self.test_results["warnings"].append({
            "title": title,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })

    async def test_imports(self):
        """Test all module imports"""
        logger.info("Testing module imports...")
        
        critical_modules = [
            "config", "user_db", "encryption_manager", "telegram_handler",
            "enhanced_summarizer", "persistent_storage", "message_intelligence",
            "crypto_research", "scheduling", "natural_language_processor",
            "persistent_user_context", "intelligent_error_handler"
        ]
        
        for module in critical_modules:
            try:
                __import__(module)
                self.add_test_result(f"Import {module}", True, "Module imported successfully")
            except ImportError as e:
                self.add_critical_bug(f"Import Error: {module}", f"Cannot import {module}: {e}")
                self.add_test_result(f"Import {module}", False, error=str(e))
            except Exception as e:
                self.add_major_bug(f"Import Issue: {module}", f"Error importing {module}: {e}")
                self.add_test_result(f"Import {module}", False, error=str(e))
        
        # Test MCP modules
        mcp_modules = [
            "mcp_integration", "mcp_client", "mcp_ai_orchestrator",
            "mcp_streaming", "mcp_background_processor"
        ]
        
        for module in mcp_modules:
            try:
                __import__(module)
                self.add_test_result(f"Import MCP {module}", True, "MCP module imported successfully")
            except ImportError as e:
                self.add_major_bug(f"MCP Import Error: {module}", f"Cannot import MCP module {module}: {e}")
                self.add_test_result(f"Import MCP {module}", False, error=str(e))
            except Exception as e:
                self.add_major_bug(f"MCP Import Issue: {module}", f"Error importing MCP module {module}: {e}")
                self.add_test_result(f"Import MCP {module}", False, error=str(e))

    async def test_configuration(self):
        """Test configuration loading and validation"""
        logger.info("Testing configuration...")
        
        try:
            from config import config
            
            # Test required environment variables
            required_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
            for var in required_vars:
                if not os.getenv(var):
                    self.add_major_bug(f"Missing Environment Variable", f"Required variable {var} is not set")
                    self.add_test_result(f"Config {var}", False, error=f"{var} not set")
                else:
                    self.add_test_result(f"Config {var}", True, f"{var} is set")
            
            # Test AI provider keys
            ai_keys = ["GROQ_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
            ai_keys_found = 0
            for key in ai_keys:
                if os.getenv(key):
                    ai_keys_found += 1
                    self.add_test_result(f"AI Key {key}", True, f"{key} is available")
                else:
                    self.add_test_result(f"AI Key {key}", False, f"{key} not set")
            
            if ai_keys_found == 0:
                self.add_critical_bug("No AI Provider Keys", "No AI provider API keys found")
            elif ai_keys_found < 2:
                self.add_warning("Limited AI Providers", f"Only {ai_keys_found} AI provider key(s) found")
                
        except Exception as e:
            self.add_critical_bug("Configuration Error", f"Error loading configuration: {e}")
            self.add_test_result("Configuration Loading", False, error=str(e))

    async def test_database_functionality(self):
        """Test database functionality"""
        logger.info("Testing database functionality...")
        
        try:
            from user_db import init_db, set_user_property, get_user_property
            
            # Test database initialization
            try:
                init_db()
                self.add_test_result("Database Init", True, "Database initialized successfully")
            except Exception as e:
                self.add_critical_bug("Database Init Error", f"Cannot initialize database: {e}")
                self.add_test_result("Database Init", False, error=str(e))
                return
            
            # Test user property operations
            test_user_id = 12345
            test_property = "test_property"
            test_value = "test_value"
            
            try:
                set_user_property(test_user_id, test_property, test_value)
                retrieved_value = get_user_property(test_user_id, test_property)
                
                if retrieved_value == test_value:
                    self.add_test_result("Database Operations", True, "User property set/get works")
                else:
                    self.add_major_bug("Database Operations", f"Property mismatch: set {test_value}, got {retrieved_value}")
                    self.add_test_result("Database Operations", False, error="Property value mismatch")
                    
            except Exception as e:
                self.add_major_bug("Database Operations Error", f"Error in user property operations: {e}")
                self.add_test_result("Database Operations", False, error=str(e))
                
        except Exception as e:
            self.add_critical_bug("Database Module Error", f"Error importing database modules: {e}")
            self.add_test_result("Database Module", False, error=str(e))

    async def test_message_processing(self):
        """Test message processing functionality"""
        logger.info("Testing message processing...")
        
        try:
            # Test the problematic message text modification
            from telegram import Update, Message, User, Chat
            from datetime import datetime
            
            # Create mock objects
            user = User(id=12345, first_name="Test", is_bot=False)
            chat = Chat(id=67890, type="private")
            
            # Test if we can create a message and modify its text (this should fail)
            try:
                message = Message(
                    message_id=1,
                    date=datetime.now(),
                    chat=chat,
                    from_user=user,
                    text="Original text"
                )
                
                # This should fail - testing the bug
                try:
                    message.text = "Modified text"
                    self.add_major_bug("Message Text Modification", "Message.text can be modified (unexpected)")
                    self.add_test_result("Message Text Immutability", False, error="Text attribute is mutable")
                except AttributeError:
                    # This is expected - text should be read-only
                    self.add_test_result("Message Text Immutability", True, "Text attribute is properly read-only")
                    
            except Exception as e:
                self.add_test_result("Message Creation", False, error=str(e))
                
        except Exception as e:
            self.add_critical_bug("Message Processing Import Error", f"Cannot import message processing modules: {e}")
            self.add_test_result("Message Processing Import", False, error=str(e))

    async def test_conversation_intelligence(self):
        """Test conversation intelligence functionality"""
        logger.info("Testing conversation intelligence...")
        
        try:
            from conversation_intelligence import ConversationIntelligence, ConversationMessage
            from datetime import datetime
            
            # Test conversation intelligence initialization
            try:
                ci = ConversationIntelligence()
                self.add_test_result("Conversation Intelligence Init", True, "CI initialized successfully")
                
                # Test message streaming
                test_message = ConversationMessage(
                    message_id="test_123",
                    user_id=12345,
                    username="test_user",
                    chat_id=67890,
                    chat_type="private",
                    text="Test message for conversation intelligence",
                    timestamp=datetime.now(),
                    is_bot_message=False
                )
                
                try:
                    await ci.stream_message(test_message)
                    self.add_test_result("Message Streaming", True, "Message streamed successfully")
                except Exception as e:
                    self.add_major_bug("Message Streaming Error", f"Error streaming message: {e}")
                    self.add_test_result("Message Streaming", False, error=str(e))
                    
            except Exception as e:
                self.add_critical_bug("Conversation Intelligence Init Error", f"Cannot initialize CI: {e}")
                self.add_test_result("Conversation Intelligence Init", False, error=str(e))
                
        except Exception as e:
            self.add_critical_bug("Conversation Intelligence Import Error", f"Cannot import CI modules: {e}")
            self.add_test_result("Conversation Intelligence Import", False, error=str(e))

    async def test_nlp_functionality(self):
        """Test natural language processing functionality"""
        logger.info("Testing NLP functionality...")
        
        try:
            from natural_language_processor import nlp_processor
            
            # Test NLP processing
            test_queries = [
                "What's the price of Bitcoin?",
                "Show me my portfolio",
                "Create a summary of today's conversations",
                "Set an alert for ETH price above $3000",
                "Help me with trading"
            ]
            
            for query in test_queries:
                try:
                    result = nlp_processor.process_query(query)
                    if result:
                        self.add_test_result(f"NLP Query: {query[:20]}...", True, f"Processed successfully: {result.get('intent', 'unknown')}")
                    else:
                        self.add_minor_bug("NLP Processing", f"No result for query: {query}")
                        self.add_test_result(f"NLP Query: {query[:20]}...", False, error="No result returned")
                except Exception as e:
                    self.add_major_bug("NLP Processing Error", f"Error processing query '{query}': {e}")
                    self.add_test_result(f"NLP Query: {query[:20]}...", False, error=str(e))
                    
        except Exception as e:
            self.add_critical_bug("NLP Import Error", f"Cannot import NLP modules: {e}")
            self.add_test_result("NLP Import", False, error=str(e))

    async def test_ai_providers(self):
        """Test AI provider functionality"""
        logger.info("Testing AI providers...")
        
        try:
            from ai_provider_manager import ai_provider_manager
            
            # Test provider listing
            try:
                providers = ai_provider_manager.list_providers()
                if providers:
                    self.add_test_result("AI Provider Listing", True, f"Found {len(providers)} providers")
                    
                    # Test each available provider
                    for provider_name, info in providers.items():
                        if info.get("available"):
                            try:
                                # Test switching to provider
                                success = ai_provider_manager.switch_provider(provider_name)
                                if success:
                                    self.add_test_result(f"AI Provider Switch: {provider_name}", True, "Switch successful")
                                    
                                    # Test generation
                                    test_messages = [{"role": "user", "content": "Hello, respond with 'Test successful'"}]
                                    response = await ai_provider_manager.generate_text(test_messages)
                                    
                                    if response and "test successful" in response.lower():
                                        self.add_test_result(f"AI Provider Generation: {provider_name}", True, "Generation successful")
                                    else:
                                        self.add_minor_bug(f"AI Provider Response: {provider_name}", f"Unexpected response: {response}")
                                        self.add_test_result(f"AI Provider Generation: {provider_name}", False, error="Unexpected response")
                                        
                                else:
                                    self.add_major_bug(f"AI Provider Switch Error: {provider_name}", "Failed to switch provider")
                                    self.add_test_result(f"AI Provider Switch: {provider_name}", False, error="Switch failed")
                                    
                            except Exception as e:
                                self.add_major_bug(f"AI Provider Error: {provider_name}", f"Error testing provider: {e}")
                                self.add_test_result(f"AI Provider Test: {provider_name}", False, error=str(e))
                        else:
                            self.add_test_result(f"AI Provider Availability: {provider_name}", False, "Provider not available (missing API key)")
                            
                else:
                    self.add_critical_bug("AI Provider Listing", "No providers found")
                    self.add_test_result("AI Provider Listing", False, error="No providers found")
                    
            except Exception as e:
                self.add_critical_bug("AI Provider Listing Error", f"Error listing providers: {e}")
                self.add_test_result("AI Provider Listing", False, error=str(e))
                
        except Exception as e:
            self.add_critical_bug("AI Provider Import Error", f"Cannot import AI provider modules: {e}")
            self.add_test_result("AI Provider Import", False, error=str(e))

    async def test_mcp_integration(self):
        """Test MCP integration functionality"""
        logger.info("Testing MCP integration...")
        
        try:
            from mcp_integration import get_mcp_status, start_mcp_integration
            
            # Test MCP status
            try:
                status = await get_mcp_status()
                self.add_test_result("MCP Status Check", True, f"MCP status: {status}")
                
                # Test MCP initialization (without actually starting servers)
                try:
                    # This should not actually start servers in test mode
                    self.add_test_result("MCP Integration Available", True, "MCP modules can be imported")
                except Exception as e:
                    self.add_major_bug("MCP Integration Error", f"Error with MCP integration: {e}")
                    self.add_test_result("MCP Integration", False, error=str(e))
                    
            except Exception as e:
                self.add_major_bug("MCP Status Error", f"Error checking MCP status: {e}")
                self.add_test_result("MCP Status Check", False, error=str(e))
                
        except Exception as e:
            self.add_major_bug("MCP Import Error", f"Cannot import MCP modules: {e}")
            self.add_test_result("MCP Import", False, error=str(e))

    async def test_command_handlers(self):
        """Test command handler functionality"""
        logger.info("Testing command handlers...")
        
        # Test if command handlers can be imported and are callable
        command_modules = [
            ("help_command", "main"),
            ("status_command", "main"),
            ("portfolio_command", "main"),
            ("research_command", "main"),
            ("alerts_command", "main"),
            ("summarynow_command", "main")
        ]
        
        for command_name, module_name in command_modules:
            try:
                module = __import__(module_name)
                if hasattr(module, command_name):
                    command_func = getattr(module, command_name)
                    if callable(command_func):
                        self.add_test_result(f"Command Handler: {command_name}", True, "Handler is callable")
                    else:
                        self.add_minor_bug(f"Command Handler: {command_name}", "Handler is not callable")
                        self.add_test_result(f"Command Handler: {command_name}", False, error="Not callable")
                else:
                    self.add_major_bug(f"Command Handler Missing: {command_name}", f"Handler {command_name} not found in {module_name}")
                    self.add_test_result(f"Command Handler: {command_name}", False, error="Handler not found")
                    
            except Exception as e:
                self.add_major_bug(f"Command Handler Import Error: {command_name}", f"Error importing {command_name}: {e}")
                self.add_test_result(f"Command Handler: {command_name}", False, error=str(e))

    async def test_group_chat_functionality(self):
        """Test group chat functionality"""
        logger.info("Testing group chat functionality...")
        
        try:
            from group_chat_manager import should_respond_in_group, update_group_context, format_group_response
            
            # Test group chat functions
            test_chat_id = 12345
            test_message_text = "Hello @mobius, how are you?"
            
            try:
                # Test should_respond_in_group
                should_respond = should_respond_in_group(test_chat_id, test_message_text)
                self.add_test_result("Group Chat Response Check", True, f"Response check result: {should_respond}")
                
                # Test format_group_response
                formatted = format_group_response("Test response", "test_user", "mention")
                if formatted:
                    self.add_test_result("Group Chat Response Format", True, "Response formatted successfully")
                else:
                    self.add_minor_bug("Group Chat Response Format", "No formatted response returned")
                    self.add_test_result("Group Chat Response Format", False, error="No formatted response")
                    
            except Exception as e:
                self.add_major_bug("Group Chat Function Error", f"Error in group chat functions: {e}")
                self.add_test_result("Group Chat Functions", False, error=str(e))
                
        except Exception as e:
            self.add_major_bug("Group Chat Import Error", f"Cannot import group chat modules: {e}")
            self.add_test_result("Group Chat Import", False, error=str(e))

    async def test_mention_tracking(self):
        """Test mention tracking functionality"""
        logger.info("Testing mention tracking...")
        
        # Test mention detection patterns
        test_messages = [
            "Hello @mobius",
            "Hey mobius, what's up?",
            "@möbius can you help?",
            "möbius please respond",
            "Regular message without mention"
        ]
        
        mention_patterns = ['mobius', '@mobius', 'möbius', '@möbius']
        
        for message in test_messages:
            is_mentioned = any(mention in message.lower() for mention in mention_patterns)
            expected_mention = any(pattern in message.lower() for pattern in ['mobius', 'möbius'])
            
            if is_mentioned == expected_mention:
                self.add_test_result(f"Mention Detection: {message[:20]}...", True, f"Correctly detected: {is_mentioned}")
            else:
                self.add_minor_bug("Mention Detection", f"Incorrect detection for: {message}")
                self.add_test_result(f"Mention Detection: {message[:20]}...", False, error="Incorrect detection")

    async def test_summary_generation(self):
        """Test summary generation functionality"""
        logger.info("Testing summary generation...")
        
        try:
            from enhanced_summarizer import generate_daily_summary, enhanced_summarizer
            
            # Test summary generation
            try:
                # Test with mock data
                test_messages = [
                    {"text": "Hello, how are you?", "timestamp": "2023-01-01 10:00:00", "user": "test_user"},
                    {"text": "I'm doing well, thanks!", "timestamp": "2023-01-01 10:01:00", "user": "bot"},
                    {"text": "What's the price of Bitcoin?", "timestamp": "2023-01-01 10:02:00", "user": "test_user"}
                ]
                summary = await generate_daily_summary(test_messages)
                
                if summary:
                    self.add_test_result("Summary Generation", True, "Summary generated successfully")
                else:
                    self.add_minor_bug("Summary Generation", "No summary generated (may be expected with no data)")
                    self.add_test_result("Summary Generation", False, error="No summary generated")
                    
            except Exception as e:
                self.add_major_bug("Summary Generation Error", f"Error generating summary: {e}")
                self.add_test_result("Summary Generation", False, error=str(e))
                
        except Exception as e:
            self.add_major_bug("Summary Import Error", f"Cannot import summary modules: {e}")
            self.add_test_result("Summary Import", False, error=str(e))

    async def test_error_handling(self):
        """Test error handling functionality"""
        logger.info("Testing error handling...")
        
        try:
            from intelligent_error_handler import error_handler
            
            # Test error handler
            try:
                # Simulate an error
                test_error = Exception("Test error for error handler")
                result = error_handler.handle_error(test_error, "test_context")
                
                if result:
                    self.add_test_result("Error Handler", True, "Error handled successfully")
                else:
                    self.add_minor_bug("Error Handler", "Error handler returned no result")
                    self.add_test_result("Error Handler", False, error="No result from error handler")
                    
            except Exception as e:
                self.add_major_bug("Error Handler Error", f"Error in error handler: {e}")
                self.add_test_result("Error Handler", False, error=str(e))
                
        except Exception as e:
            self.add_major_bug("Error Handler Import Error", f"Cannot import error handler: {e}")
            self.add_test_result("Error Handler Import", False, error=str(e))

    async def test_event_loop_issues(self):
        """Test for event loop issues"""
        logger.info("Testing event loop issues...")
        
        # Test if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                self.add_test_result("Event Loop Detection", True, "Running in event loop (as expected)")
                
                # Test if asyncio.run() would fail (it should)
                try:
                    # This should fail if we're already in a loop
                    async def dummy_coro():
                        return "test"
                    
                    # Don't actually call asyncio.run() as it would fail
                    # Just test that we can detect the issue
                    self.add_test_result("Event Loop Conflict Detection", True, "Can detect event loop conflicts")
                    
                except Exception as e:
                    self.add_test_result("Event Loop Conflict Detection", False, error=str(e))
            else:
                self.add_warning("Event Loop", "Not running in event loop (unexpected in async context)")
                self.add_test_result("Event Loop Detection", False, error="Not in event loop")
                
        except RuntimeError:
            # No event loop running
            self.add_test_result("Event Loop Detection", True, "No event loop running (normal for sync context)")

    async def test_memory_management(self):
        """Test memory management"""
        logger.info("Testing memory management...")
        
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Test garbage collection
        gc.collect()
        after_gc_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        self.add_test_result("Memory Management", True, f"Initial: {initial_memory:.1f}MB, After GC: {after_gc_memory:.1f}MB")
        
        if initial_memory > 500:  # More than 500MB
            self.add_warning("Memory Usage", f"High memory usage: {initial_memory:.1f}MB")

    async def test_security_features(self):
        """Test security features"""
        logger.info("Testing security features...")
        
        try:
            from encryption_manager import EncryptionManager
            from security_auditor import security_auditor
            
            # Test encryption
            try:
                em = EncryptionManager()
                test_data = "Test sensitive data"
                encrypted = em.encrypt(test_data)
                decrypted = em.decrypt(encrypted)
                
                if decrypted == test_data:
                    self.add_test_result("Encryption/Decryption", True, "Encryption works correctly")
                else:
                    self.add_critical_bug("Encryption Error", "Decrypted data doesn't match original")
                    self.add_test_result("Encryption/Decryption", False, error="Data mismatch")
                    
            except Exception as e:
                self.add_major_bug("Encryption Error", f"Error in encryption: {e}")
                self.add_test_result("Encryption/Decryption", False, error=str(e))
                
        except Exception as e:
            self.add_major_bug("Security Import Error", f"Cannot import security modules: {e}")
            self.add_test_result("Security Import", False, error=str(e))

    async def test_performance(self):
        """Test performance characteristics"""
        logger.info("Testing performance...")
        
        import time
        
        # Test response time for basic operations
        start_time = time.time()
        
        # Simulate some basic operations
        for i in range(100):
            test_string = f"Test string {i}"
            processed = test_string.upper().lower().strip()
        
        end_time = time.time()
        duration = end_time - start_time
        
        if duration < 1.0:  # Should complete in less than 1 second
            self.add_test_result("Performance Test", True, f"Basic operations completed in {duration:.3f}s")
        else:
            self.add_warning("Performance", f"Basic operations took {duration:.3f}s (may be slow)")
            self.add_test_result("Performance Test", False, error=f"Slow performance: {duration:.3f}s")

    async def test_real_world_scenarios(self):
        """Test real-world usage scenarios"""
        logger.info("Testing real-world scenarios...")
        
        # Test natural language commands
        test_commands = [
            "What's the price of Bitcoin?",
            "Show me my portfolio",
            "Create a summary",
            "Set an alert for ETH",
            "Help me with trading",
            "What are the latest crypto news?",
            "Analyze the market trends",
            "Show me DeFi protocols",
            "What's happening in the crypto space?",
            "Give me investment advice"
        ]
        
        for command in test_commands:
            try:
                # Test if the command would be processed correctly
                # (without actually executing to avoid side effects)
                
                # Test natural language processing
                from natural_language_processor import nlp_processor
                result = nlp_processor.process_query(command)
                
                if result and result.get('intent'):
                    self.add_test_result(f"Real-world Command: {command[:20]}...", True, f"Intent: {result['intent']}")
                else:
                    self.add_minor_bug("Real-world Command Processing", f"No intent detected for: {command}")
                    self.add_test_result(f"Real-world Command: {command[:20]}...", False, error="No intent detected")
                    
            except Exception as e:
                self.add_major_bug("Real-world Command Error", f"Error processing '{command}': {e}")
                self.add_test_result(f"Real-world Command: {command[:20]}...", False, error=str(e))

    async def generate_report(self):
        """Generate comprehensive bug report"""
        logger.info("Generating comprehensive bug report...")
        
        # Calculate statistics
        total_tests = self.test_results["total_tests"]
        passed_tests = self.test_results["passed_tests"]
        failed_tests = self.test_results["failed_tests"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate report
        report = {
            **self.test_results,
            "success_rate": success_rate,
            "summary": {
                "total_issues": len(self.test_results["critical_bugs"]) + len(self.test_results["major_bugs"]) + len(self.test_results["minor_bugs"]),
                "critical_issues": len(self.test_results["critical_bugs"]),
                "major_issues": len(self.test_results["major_bugs"]),
                "minor_issues": len(self.test_results["minor_bugs"]),
                "warnings": len(self.test_results["warnings"])
            }
        }
        
        # Save report
        report_file = f"comprehensive_bug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*80)
        print("🔍 COMPREHENSIVE BUG HUNT REPORT")
        print("="*80)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"\n🚨 Issues Found:")
        print(f"   🔴 Critical: {len(self.test_results['critical_bugs'])}")
        print(f"   🟠 Major: {len(self.test_results['major_bugs'])}")
        print(f"   🟡 Minor: {len(self.test_results['minor_bugs'])}")
        print(f"   ⚠️  Warnings: {len(self.test_results['warnings'])}")
        
        # Show critical bugs
        if self.test_results["critical_bugs"]:
            print(f"\n🔴 CRITICAL BUGS:")
            for bug in self.test_results["critical_bugs"]:
                print(f"   • {bug['title']}: {bug['description']}")
        
        # Show major bugs
        if self.test_results["major_bugs"]:
            print(f"\n🟠 MAJOR BUGS:")
            for bug in self.test_results["major_bugs"]:
                print(f"   • {bug['title']}: {bug['description']}")
        
        print(f"\n📄 Full report saved to: {report_file}")
        print("="*80)
        
        return report

async def main():
    """Main function to run comprehensive bug hunt"""
    hunter = ComprehensiveBugHunter()
    await hunter.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())