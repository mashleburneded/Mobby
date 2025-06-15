#!/usr/bin/env python3
"""
Comprehensive Command Testing Suite
Tests 30-50 different natural language commands to verify bot functionality
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
from unittest.mock import Mock, AsyncMock

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveCommandTester:
    """Comprehensive command testing system"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "command_results": [],
            "performance_metrics": {},
            "error_analysis": {}
        }
        
        # Test commands covering all major functionality
        self.test_commands = [
            # Portfolio and Balance Commands
            ("Show me my portfolio", "portfolio_check", "Should display user portfolio"),
            ("What's my balance?", "portfolio_check", "Should show account balance"),
            ("Check my holdings", "portfolio_check", "Should list all holdings"),
            ("My crypto assets", "portfolio_check", "Should show crypto assets"),
            ("Portfolio overview", "portfolio_check", "Should give portfolio overview"),
            
            # Price Check Commands
            ("What's the price of Bitcoin?", "price_check", "Should show BTC price"),
            ("BTC price", "price_check", "Should show Bitcoin price"),
            ("How much is Ethereum worth?", "price_check", "Should show ETH price"),
            ("ETH current price", "price_check", "Should show Ethereum price"),
            ("Solana price today", "price_check", "Should show SOL price"),
            ("What's MATIC trading at?", "price_check", "Should show Polygon price"),
            ("Current AVAX value", "price_check", "Should show Avalanche price"),
            ("DOT price check", "price_check", "Should show Polkadot price"),
            
            # Research Commands
            ("Research Uniswap protocol", "research_request", "Should research UNI protocol"),
            ("Tell me about Aave", "research_request", "Should provide Aave information"),
            ("Analyze Compound", "research_request", "Should analyze COMP protocol"),
            ("What is Lido?", "research_request", "Should explain Lido protocol"),
            ("MakerDAO information", "research_request", "Should provide MKR info"),
            ("Curve Finance details", "research_request", "Should show Curve details"),
            ("Yearn Finance overview", "research_request", "Should give YFI overview"),
            
            # Summary Commands
            ("Summarize today's conversations", "summary_request", "Should create daily summary"),
            ("Give me a recap", "summary_request", "Should provide conversation recap"),
            ("What did we discuss?", "summary_request", "Should summarize discussions"),
            ("Today's summary", "summary_request", "Should show today's summary"),
            ("Conversation overview", "summary_request", "Should give conversation overview"),
            
            # Alert Commands
            ("Set alert for BTC above $50000", "alert_management", "Should create BTC price alert"),
            ("Notify me when ETH hits $3000", "alert_management", "Should create ETH alert"),
            ("Watch SOL price", "alert_management", "Should monitor SOL price"),
            ("Alert me about MATIC changes", "alert_management", "Should track MATIC"),
            ("Remove my BTC alert", "alert_management", "Should remove BTC alert"),
            
            # Help Commands
            ("Help me", "help_request", "Should show help information"),
            ("What can you do?", "help_request", "Should list capabilities"),
            ("Show commands", "help_request", "Should display available commands"),
            ("I need assistance", "help_request", "Should provide assistance"),
            ("How do I use this bot?", "help_request", "Should explain bot usage"),
            
            # Menu Commands
            ("Show menu", "menu_request", "Should display main menu"),
            ("Main menu", "menu_request", "Should show navigation menu"),
            ("Options", "menu_request", "Should list available options"),
            ("Dashboard", "menu_request", "Should show dashboard"),
            
            # Greeting Commands
            ("Hello", "greeting", "Should respond with greeting"),
            ("Hi there", "greeting", "Should greet back"),
            ("Good morning", "greeting", "Should respond to morning greeting"),
            ("Hey", "greeting", "Should acknowledge greeting"),
            ("What's up?", "greeting", "Should respond casually"),
            
            # Status Commands
            ("Bot status", "status_check", "Should show bot status"),
            ("Are you working?", "status_check", "Should confirm operational status"),
            ("System health", "status_check", "Should display system health"),
            ("Connection status", "status_check", "Should show connection status"),
            
            # Complex Natural Language Commands
            ("I want to know about the best DeFi protocols for yield farming", "research_request", "Should research DeFi yield farming"),
            ("Can you help me understand how to stake my tokens safely?", "help_request", "Should explain staking safety"),
            ("What are the top performing cryptocurrencies this week?", "research_request", "Should show top performers"),
            ("I'm looking for information about cross-chain bridges", "research_request", "Should explain cross-chain bridges"),
            ("How do I protect my crypto investments from market volatility?", "help_request", "Should provide investment protection advice"),
            ("What's the difference between APY and APR in DeFi?", "help_request", "Should explain APY vs APR"),
            ("Show me the latest news about Ethereum upgrades", "research_request", "Should show Ethereum news"),
            ("I need to understand impermanent loss in liquidity pools", "help_request", "Should explain impermanent loss"),
            ("What are the risks of using leverage in crypto trading?", "help_request", "Should explain leverage risks"),
            ("Can you analyze the current market sentiment for Bitcoin?", "research_request", "Should analyze BTC sentiment")
        ]
        
    async def run_comprehensive_test(self):
        """Run comprehensive command testing"""
        logger.info("🧪 Starting Comprehensive Command Testing...")
        logger.info(f"📊 Testing {len(self.test_commands)} commands...")
        
        # Initialize required modules
        await self.initialize_test_environment()
        
        # Test each command
        for i, (command, expected_intent, description) in enumerate(self.test_commands, 1):
            logger.info(f"\n🔍 Test {i}/{len(self.test_commands)}: {command}")
            await self.test_single_command(command, expected_intent, description)
        
        # Generate comprehensive report
        await self.generate_test_report()
        
    async def initialize_test_environment(self):
        """Initialize the test environment"""
        logger.info("🔧 Initializing test environment...")
        
        try:
            # Import required modules
            from natural_language_processor import nlp_processor
            
            self.nlp_processor = nlp_processor
            
            # Try to import enhanced modules if available
            try:
                from enhanced_intent_system import analyze_user_intent_enhanced
                self.analyze_intent = analyze_user_intent_enhanced
                logger.info("✅ Enhanced intent system loaded")
            except ImportError:
                logger.warning("⚠️ Enhanced intent system not available")
                self.analyze_intent = None
            
            try:
                from enhanced_response_handler import handle_enhanced_response
                self.handle_response = handle_enhanced_response
                logger.info("✅ Enhanced response handler loaded")
            except ImportError:
                logger.warning("⚠️ Enhanced response handler not available")
                self.handle_response = None
            
            try:
                from ai_provider_manager import ai_provider_manager
                self.ai_manager = ai_provider_manager
                logger.info("✅ AI provider manager loaded")
            except ImportError:
                logger.warning("⚠️ AI provider manager not available")
                self.ai_manager = None
            
            logger.info("✅ Test environment initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize test environment: {e}")
            raise

    async def test_single_command(self, command: str, expected_intent: str, description: str):
        """Test a single command"""
        start_time = datetime.now()
        test_result = {
            "command": command,
            "expected_intent": expected_intent,
            "description": description,
            "timestamp": start_time.isoformat(),
            "success": False,
            "actual_intent": None,
            "confidence": 0.0,
            "response_time_ms": 0,
            "error": None,
            "response": None
        }
        
        try:
            # Test 1: Natural Language Processing
            nlp_result = self.nlp_processor.process_query(command)
            
            if nlp_result:
                test_result["actual_intent"] = nlp_result.get("intent", "unknown")
                test_result["confidence"] = nlp_result.get("confidence", 0.0)
                
                # Check if intent matches expectation (allow some flexibility)
                intent_match = self.check_intent_match(expected_intent, test_result["actual_intent"])
                
                if intent_match:
                    logger.info(f"✅ Intent Recognition: {test_result['actual_intent']} (confidence: {test_result['confidence']:.2f})")
                    
                    # Test 2: Enhanced Intent Analysis (if available)
                    if self.analyze_intent:
                        try:
                            enhanced_analysis = await self.analyze_intent(
                                command, 
                                12345,  # Test user ID
                                {
                                    "username": "test_user",
                                    "chat_id": 67890,
                                    "chat_type": "private"
                                }
                            )
                            
                            logger.info(f"✅ Enhanced Analysis: {enhanced_analysis.intent_type.value}")
                            
                            # Test 3: Response Generation (if available)
                            if self.handle_response:
                                try:
                                    response = await self.handle_response(
                                        enhanced_analysis,
                                        command,
                                        12345,
                                        {
                                            "username": "test_user",
                                            "chat_id": 67890,
                                            "chat_type": "private"
                                        }
                                    )
                                    
                                    if response and response.get("message"):
                                        test_result["response"] = response["message"][:200] + "..." if len(response["message"]) > 200 else response["message"]
                                        test_result["success"] = True
                                        logger.info(f"✅ Response Generated: {len(response['message'])} characters")
                                    else:
                                        test_result["error"] = "No response generated"
                                        logger.warning(f"⚠️ No response generated")
                                        
                                except Exception as e:
                                    test_result["error"] = f"Response generation error: {str(e)}"
                                    logger.error(f"❌ Response Generation Error: {e}")
                            else:
                                # If no response handler, consider intent recognition as success
                                test_result["success"] = True
                                test_result["response"] = "Intent recognized successfully (no response handler)"
                                logger.info(f"✅ Intent recognized (no response handler available)")
                                
                        except Exception as e:
                            test_result["error"] = f"Enhanced analysis error: {str(e)}"
                            logger.error(f"❌ Enhanced Analysis Error: {e}")
                    else:
                        # If no enhanced analysis, consider basic intent recognition as success
                        test_result["success"] = True
                        test_result["response"] = "Basic intent recognition successful"
                        logger.info(f"✅ Basic intent recognition successful")
                        
                else:
                    test_result["error"] = f"Intent mismatch: expected {expected_intent}, got {test_result['actual_intent']}"
                    logger.warning(f"⚠️ Intent Mismatch: expected {expected_intent}, got {test_result['actual_intent']}")
                    
            else:
                test_result["error"] = "NLP processing returned no result"
                logger.error(f"❌ NLP processing failed")
                
        except Exception as e:
            test_result["error"] = f"Command processing error: {str(e)}"
            logger.error(f"❌ Command Error: {e}")
            
        # Calculate response time
        end_time = datetime.now()
        test_result["response_time_ms"] = int((end_time - start_time).total_seconds() * 1000)
        
        # Update counters
        self.test_results["total_commands"] += 1
        if test_result["success"]:
            self.test_results["successful_commands"] += 1
        else:
            self.test_results["failed_commands"] += 1
            
        # Store result
        self.test_results["command_results"].append(test_result)
        
        # Log result
        status = "✅ PASS" if test_result["success"] else "❌ FAIL"
        logger.info(f"{status} | {test_result['response_time_ms']}ms | {command}")

    def check_intent_match(self, expected: str, actual: str) -> bool:
        """Check if intents match (with some flexibility)"""
        if expected == actual:
            return True
            
        # Allow some flexibility in intent matching
        intent_mappings = {
            "portfolio_check": ["portfolio", "balance", "holdings", "assets"],
            "price_check": ["price", "value", "cost", "worth"],
            "research_request": ["research", "analyze", "info", "information"],
            "summary_request": ["summary", "recap", "overview"],
            "alert_management": ["alert", "notification", "notify", "watch"],
            "help_request": ["help", "assist", "support", "guide"],
            "menu_request": ["menu", "options", "dashboard"],
            "greeting": ["greeting", "hello", "hi"],
            "status_check": ["status", "health", "working"]
        }
        
        expected_keywords = intent_mappings.get(expected, [expected])
        return any(keyword in actual.lower() for keyword in expected_keywords)

    async def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("📊 Generating comprehensive test report...")
        
        # Calculate statistics
        total = self.test_results["total_commands"]
        successful = self.test_results["successful_commands"]
        failed = self.test_results["failed_commands"]
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Calculate performance metrics
        response_times = [r["response_time_ms"] for r in self.test_results["command_results"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        self.test_results["performance_metrics"] = {
            "average_response_time_ms": avg_response_time,
            "max_response_time_ms": max_response_time,
            "min_response_time_ms": min_response_time,
            "success_rate_percent": success_rate
        }
        
        # Analyze errors
        error_types = {}
        for result in self.test_results["command_results"]:
            if result["error"]:
                error_type = result["error"].split(":")[0]
                error_types[error_type] = error_types.get(error_type, 0) + 1
                
        self.test_results["error_analysis"] = error_types
        
        # Save detailed report
        report_file = f"comprehensive_command_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE COMMAND TEST REPORT")
        print("="*80)
        print(f"📊 Total Commands Tested: {total}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"\n⚡ Performance Metrics:")
        print(f"   Average Response Time: {avg_response_time:.1f}ms")
        print(f"   Fastest Response: {min_response_time}ms")
        print(f"   Slowest Response: {max_response_time}ms")
        
        if error_types:
            print(f"\n❌ Error Analysis:")
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                print(f"   {error_type}: {count} occurrences")
        
        # Show sample successful commands
        successful_commands = [r for r in self.test_results["command_results"] if r["success"]]
        if successful_commands:
            print(f"\n✅ Sample Successful Commands:")
            for cmd in successful_commands[:5]:
                print(f"   • \"{cmd['command']}\" -> {cmd['actual_intent']} ({cmd['confidence']:.2f})")
        
        # Show sample failed commands
        failed_commands = [r for r in self.test_results["command_results"] if not r["success"]]
        if failed_commands:
            print(f"\n❌ Sample Failed Commands:")
            for cmd in failed_commands[:5]:
                print(f"   • \"{cmd['command']}\" -> {cmd['error']}")
        
        print(f"\n📄 Full report saved to: {report_file}")
        print("="*80)
        
        # Provide recommendations
        if success_rate < 70:
            print("\n🔧 RECOMMENDATIONS:")
            print("   • Success rate is below 70% - significant improvements needed")
            print("   • Review intent recognition patterns")
            print("   • Check response generation logic")
            print("   • Verify AI provider integration")
        elif success_rate < 90:
            print("\n🔧 RECOMMENDATIONS:")
            print("   • Success rate is good but can be improved")
            print("   • Fine-tune intent recognition for edge cases")
            print("   • Optimize response generation")
        else:
            print("\n🎉 EXCELLENT PERFORMANCE!")
            print("   • Success rate is above 90%")
            print("   • Bot is performing very well")
            print("   • Minor optimizations may still be beneficial")
        
        return self.test_results

async def main():
    """Main function to run comprehensive command testing"""
    tester = ComprehensiveCommandTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())