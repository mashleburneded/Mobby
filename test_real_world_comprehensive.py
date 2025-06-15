#!/usr/bin/env python3
"""
Comprehensive Real-World Testing Suite
Tests the bot with realistic user interactions to find bugs and edge cases
"""

import asyncio
import sys
import os
import time
import json
import random
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add src directory to path
sys.path.insert(0, 'src')

# Import core functionality
from real_natural_language_fix import process_natural_language_message
from universal_intent_executor import execute_intent_with_tools, cleanup_universal_executor
from public_data_sources import cleanup_public_data_manager
from comprehensive_nlp_patterns import analyze_comprehensive_intent, get_comprehensive_pattern_stats
from ai_provider_manager import ai_provider_manager
from message_storage import MessageStorage
from summarizer import generate_daily_summary

class RealWorldTestSuite:
    """Comprehensive real-world testing suite"""
    
    def __init__(self):
        self.test_results = []
        self.bugs_found = []
        self.performance_metrics = []
        self.user_scenarios = self._initialize_user_scenarios()
        self.message_storage = MessageStorage('test_real_world.db')
        
    def _initialize_user_scenarios(self) -> List[Dict]:
        """Initialize realistic user scenarios"""
        return [
            {
                'name': 'Crypto Newbie',
                'profile': {
                    'experience': 'beginner',
                    'interests': ['bitcoin', 'ethereum', 'learning'],
                    'risk_tolerance': 'low',
                    'typical_queries': [
                        "What is Bitcoin?",
                        "How do I buy crypto?",
                        "Is Bitcoin safe?",
                        "What's the difference between Bitcoin and Ethereum?",
                        "Should I invest in crypto?",
                        "What's a wallet?",
                        "How much should I invest?",
                        "What's DeFi?",
                        "Is crypto legal?",
                        "What are the risks?"
                    ]
                }
            },
            {
                'name': 'Active Day Trader',
                'profile': {
                    'experience': 'advanced',
                    'interests': ['trading', 'technical_analysis', 'scalping'],
                    'risk_tolerance': 'high',
                    'typical_queries': [
                        "BTC price now",
                        "Set stop loss at $42000",
                        "RSI for ETH",
                        "Volume spike on SOL",
                        "Breakout on AVAX",
                        "Short BTC at $45000",
                        "MACD divergence on ETH",
                        "Support levels for BTC",
                        "Fibonacci retracement SOL",
                        "Market sentiment now"
                    ]
                }
            },
            {
                'name': 'DeFi Yield Farmer',
                'profile': {
                    'experience': 'intermediate',
                    'interests': ['defi', 'yield_farming', 'staking'],
                    'risk_tolerance': 'medium',
                    'typical_queries': [
                        "Best yield farming opportunities",
                        "Stake ETH on Lido",
                        "Aave lending rates",
                        "Impermanent loss calculator",
                        "Bridge to Polygon",
                        "Curve pool APY",
                        "Compound vs Aave",
                        "Liquidity mining rewards",
                        "Gas fees for DeFi",
                        "Yield farming risks"
                    ]
                }
            },
            {
                'name': 'Portfolio Investor',
                'profile': {
                    'experience': 'intermediate',
                    'interests': ['portfolio', 'long_term', 'diversification'],
                    'risk_tolerance': 'medium',
                    'typical_queries': [
                        "Show my portfolio",
                        "Portfolio performance",
                        "Rebalance suggestions",
                        "Risk assessment",
                        "Diversification analysis",
                        "DCA strategy",
                        "Asset allocation",
                        "Portfolio optimization",
                        "Tax implications",
                        "Long-term outlook"
                    ]
                }
            },
            {
                'name': 'Institutional Analyst',
                'profile': {
                    'experience': 'expert',
                    'interests': ['institutional', 'compliance', 'research'],
                    'risk_tolerance': 'low',
                    'typical_queries': [
                        "Institutional adoption trends",
                        "Regulatory compliance check",
                        "Large order execution",
                        "Market microstructure",
                        "Liquidity analysis",
                        "Counterparty risk",
                        "Treasury management",
                        "ESG crypto investments",
                        "Custody solutions",
                        "Regulatory updates"
                    ]
                }
            },
            {
                'name': 'Technical Analyst',
                'profile': {
                    'experience': 'advanced',
                    'interests': ['technical_analysis', 'charts', 'patterns'],
                    'risk_tolerance': 'medium',
                    'typical_queries': [
                        "Chart analysis BTC",
                        "Head and shoulders pattern",
                        "Elliott wave count",
                        "Bollinger bands squeeze",
                        "Volume profile analysis",
                        "Ichimoku cloud signals",
                        "Harmonic patterns",
                        "Market structure",
                        "Trend analysis",
                        "Pattern recognition"
                    ]
                }
            },
            {
                'name': 'News Trader',
                'profile': {
                    'experience': 'intermediate',
                    'interests': ['news', 'events', 'sentiment'],
                    'risk_tolerance': 'high',
                    'typical_queries': [
                        "Latest crypto news",
                        "Market moving events",
                        "Social sentiment BTC",
                        "Fear and greed index",
                        "Regulatory news",
                        "Whale movements",
                        "Exchange flows",
                        "Twitter sentiment",
                        "News impact analysis",
                        "Event calendar"
                    ]
                }
            },
            {
                'name': 'Arbitrage Trader',
                'profile': {
                    'experience': 'expert',
                    'interests': ['arbitrage', 'cross_chain', 'efficiency'],
                    'risk_tolerance': 'medium',
                    'typical_queries': [
                        "Arbitrage opportunities",
                        "Cross-exchange spreads",
                        "Bridge costs analysis",
                        "MEV opportunities",
                        "Flash loan strategies",
                        "Statistical arbitrage",
                        "Triangular arbitrage",
                        "Funding rate arbitrage",
                        "Latency arbitrage",
                        "Risk-free profits"
                    ]
                }
            }
        ]
    
    async def run_comprehensive_real_world_tests(self):
        """Run comprehensive real-world testing scenarios"""
        print("🌍 COMPREHENSIVE REAL-WORLD TESTING SUITE")
        print("=" * 60)
        print("Testing realistic user interactions to find bugs and edge cases")
        print("=" * 60)
        
        # Test each user scenario
        for scenario in self.user_scenarios:
            await self._test_user_scenario(scenario)
        
        # Test edge cases and error conditions
        await self._test_edge_cases()
        
        # Test conversation flows
        await self._test_conversation_flows()
        
        # Test performance under load
        await self._test_performance_scenarios()
        
        # Test AI provider switching
        await self._test_ai_provider_scenarios()
        
        # Test data source failures
        await self._test_data_source_failures()
        
        # Generate comprehensive report
        self._generate_comprehensive_report()
        
        # Cleanup
        await self._cleanup_tests()
    
    async def _test_user_scenario(self, scenario: Dict):
        """Test a specific user scenario"""
        print(f"\n👤 TESTING USER SCENARIO: {scenario['name']}")
        print("-" * 40)
        
        profile = scenario['profile']
        queries = profile['typical_queries']
        
        scenario_results = {
            'scenario': scenario['name'],
            'total_queries': len(queries),
            'successful_queries': 0,
            'failed_queries': 0,
            'bugs_found': [],
            'performance_issues': [],
            'response_times': []
        }
        
        for i, query in enumerate(queries, 1):
            print(f"  {i:2d}. Testing: '{query}'")
            
            start_time = time.time()
            try:
                # Test with comprehensive NLP
                intent, confidence, entities = await analyze_comprehensive_intent(
                    query, 
                    user_context={
                        'experience_level': profile['experience'],
                        'interests': profile['interests'],
                        'risk_tolerance': profile['risk_tolerance']
                    }
                )
                
                # Test with original processing
                should_convert, command_string, metadata = process_natural_language_message(query)
                
                # Test tool execution if applicable
                if should_convert:
                    result = await execute_intent_with_tools(intent, entities, {})
                    execution_success = result.get('success', False)
                else:
                    execution_success = True  # No execution needed
                
                response_time = time.time() - start_time
                scenario_results['response_times'].append(response_time)
                
                # Validate results
                issues = self._validate_query_result(query, intent, confidence, entities, execution_success, response_time)
                
                if issues:
                    scenario_results['bugs_found'].extend(issues)
                    scenario_results['failed_queries'] += 1
                    print(f"      ❌ Issues found: {len(issues)}")
                    for issue in issues:
                        print(f"         - {issue}")
                else:
                    scenario_results['successful_queries'] += 1
                    print(f"      ✅ Success ({response_time:.3f}s, confidence: {confidence:.2f})")
                
                # Check for performance issues
                if response_time > 2.0:
                    perf_issue = f"Slow response: {response_time:.3f}s for '{query}'"
                    scenario_results['performance_issues'].append(perf_issue)
                    print(f"      ⚠️ Performance issue: {perf_issue}")
                
            except Exception as e:
                response_time = time.time() - start_time
                error_msg = f"Exception in query '{query}': {e}"
                scenario_results['bugs_found'].append(error_msg)
                scenario_results['failed_queries'] += 1
                print(f"      💥 Exception: {e}")
        
        # Calculate scenario success rate
        success_rate = (scenario_results['successful_queries'] / scenario_results['total_queries']) * 100
        print(f"\n  📊 Scenario Results:")
        print(f"     Success Rate: {success_rate:.1f}% ({scenario_results['successful_queries']}/{scenario_results['total_queries']})")
        print(f"     Avg Response Time: {sum(scenario_results['response_times'])/len(scenario_results['response_times']):.3f}s")
        print(f"     Bugs Found: {len(scenario_results['bugs_found'])}")
        print(f"     Performance Issues: {len(scenario_results['performance_issues'])}")
        
        self.test_results.append(scenario_results)
    
    def _validate_query_result(self, query: str, intent: str, confidence: float, entities: Dict, execution_success: bool, response_time: float) -> List[str]:
        """Validate query result and return list of issues"""
        issues = []
        
        # Check confidence threshold
        if confidence < 0.5:
            issues.append(f"Low confidence: {confidence:.2f} for query '{query}'")
        
        # Check intent appropriateness
        expected_intents = self._get_expected_intents(query)
        if expected_intents and intent not in expected_intents:
            issues.append(f"Unexpected intent '{intent}' for query '{query}', expected one of {expected_intents}")
        
        # Check entity extraction
        expected_entities = self._get_expected_entities(query)
        for expected_entity in expected_entities:
            if expected_entity not in entities:
                issues.append(f"Missing entity '{expected_entity}' for query '{query}'")
        
        # Check execution success for actionable queries
        if self._is_actionable_query(query) and not execution_success:
            issues.append(f"Execution failed for actionable query '{query}'")
        
        # Check response time
        if response_time > 5.0:
            issues.append(f"Extremely slow response: {response_time:.3f}s for query '{query}'")
        
        return issues
    
    def _get_expected_intents(self, query: str) -> List[str]:
        """Get expected intents for a query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['price', 'cost', 'value', 'worth']):
            return ['price', 'trading', 'market_data']
        elif any(word in query_lower for word in ['portfolio', 'holdings', 'balance']):
            return ['portfolio', 'asset_allocation']
        elif any(word in query_lower for word in ['stake', 'staking', 'yield', 'farm']):
            return ['staking', 'yield_farming', 'defi']
        elif any(word in query_lower for word in ['rsi', 'macd', 'chart', 'technical']):
            return ['technical_analysis', 'indicators']
        elif any(word in query_lower for word in ['news', 'sentiment', 'social']):
            return ['news_analysis', 'social_sentiment']
        
        return []  # No specific expectation
    
    def _get_expected_entities(self, query: str) -> List[str]:
        """Get expected entities for a query"""
        entities = []
        
        # Check for cryptocurrency mentions
        crypto_symbols = ['btc', 'bitcoin', 'eth', 'ethereum', 'sol', 'solana', 'ada', 'cardano']
        for symbol in crypto_symbols:
            if symbol in query.lower():
                entities.append('cryptocurrency')
                break
        
        # Check for price mentions
        if any(char.isdigit() for char in query) and '$' in query:
            entities.append('price')
        
        # Check for platform mentions
        platforms = ['aave', 'compound', 'uniswap', 'lido', 'curve']
        for platform in platforms:
            if platform in query.lower():
                entities.append('platform')
                break
        
        return entities
    
    def _is_actionable_query(self, query: str) -> bool:
        """Check if query requires tool execution"""
        actionable_keywords = [
            'show', 'get', 'find', 'calculate', 'analyze', 'check',
            'price', 'portfolio', 'stake', 'yield', 'chart'
        ]
        return any(keyword in query.lower() for keyword in actionable_keywords)
    
    async def _test_edge_cases(self):
        """Test edge cases and error conditions"""
        print(f"\n🔍 TESTING EDGE CASES & ERROR CONDITIONS")
        print("-" * 40)
        
        edge_cases = [
            # Empty and whitespace
            "",
            "   ",
            "\n\t\r",
            
            # Very long inputs
            "a" * 1000,
            "What is Bitcoin? " * 100,
            
            # Special characters
            "!@#$%^&*()_+{}|:<>?",
            "🚀🌙💎🙌📈📉💰",
            "Bitcoin 💰 to the 🌙!",
            
            # Mixed languages (if supported)
            "¿Qué es Bitcoin?",
            "Qu'est-ce que Bitcoin?",
            "Was ist Bitcoin?",
            "ビットコインとは何ですか？",
            
            # SQL injection attempts
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM passwords",
            
            # XSS attempts
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            
            # Command injection
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& shutdown -h now",
            
            # Buffer overflow attempts
            "A" * 10000,
            "\x00" * 100,
            
            # Unicode edge cases
            "\u0000\u0001\u0002",
            "🏴‍☠️🏳️‍🌈🏳️‍⚧️",
            
            # Malformed queries
            "show me the price of",
            "stake on",
            "buy sell buy sell",
            "price price price",
            
            # Contradictory queries
            "buy and sell BTC",
            "long and short ETH",
            "bullish bearish market",
            
            # Nonsensical queries
            "colorless green ideas sleep furiously",
            "the purple elephant dances with quantum",
            "blockchain moon lambo wen sir",
            
            # Extremely specific queries
            "show me the exact price of Bitcoin at 14:32:17 UTC on March 15th 2024",
            "calculate the impermanent loss for a 0.000001 ETH / 0.000002 USDC pool",
            
            # Ambiguous queries
            "it",
            "that thing",
            "you know what I mean",
            "the usual",
            
            # Time-sensitive queries
            "price now",
            "what happened yesterday",
            "tomorrow's prediction",
            "next week's forecast",
            
            # Recursive queries
            "show me how to show me how to show me",
            "explain explaining explanations",
            
            # Null bytes and control characters
            "Bitcoin\x00price",
            "ETH\x1F\x7Fprice",
        ]
        
        edge_case_results = {
            'total_cases': len(edge_cases),
            'handled_gracefully': 0,
            'caused_errors': 0,
            'security_issues': 0,
            'performance_issues': 0
        }
        
        for i, case in enumerate(edge_cases, 1):
            print(f"  {i:2d}. Testing edge case: '{case[:50]}{'...' if len(case) > 50 else ''}'")
            
            start_time = time.time()
            try:
                # Test comprehensive NLP
                intent, confidence, entities = await analyze_comprehensive_intent(case)
                
                # Test original processing
                should_convert, command_string, metadata = process_natural_language_message(case)
                
                response_time = time.time() - start_time
                
                # Check for security issues
                if self._check_security_issues(case, intent, entities):
                    edge_case_results['security_issues'] += 1
                    print(f"      🚨 Security issue detected")
                    self.bugs_found.append(f"Security issue with input: '{case[:100]}'")
                
                # Check for performance issues
                if response_time > 3.0:
                    edge_case_results['performance_issues'] += 1
                    print(f"      ⚠️ Performance issue: {response_time:.3f}s")
                    self.bugs_found.append(f"Performance issue with input: '{case[:100]}' - {response_time:.3f}s")
                
                edge_case_results['handled_gracefully'] += 1
                print(f"      ✅ Handled gracefully ({response_time:.3f}s)")
                
            except Exception as e:
                response_time = time.time() - start_time
                edge_case_results['caused_errors'] += 1
                print(f"      ❌ Caused error: {e}")
                self.bugs_found.append(f"Error with edge case '{case[:100]}': {e}")
        
        print(f"\n  📊 Edge Case Results:")
        print(f"     Handled Gracefully: {edge_case_results['handled_gracefully']}/{edge_case_results['total_cases']}")
        print(f"     Caused Errors: {edge_case_results['caused_errors']}")
        print(f"     Security Issues: {edge_case_results['security_issues']}")
        print(f"     Performance Issues: {edge_case_results['performance_issues']}")
        
        self.test_results.append(edge_case_results)
    
    def _check_security_issues(self, input_text: str, intent: str, entities: Dict) -> bool:
        """Check for potential security issues"""
        # Check if malicious input was processed as valid
        malicious_patterns = [
            r"<script",
            r"javascript:",
            r"DROP\s+TABLE",
            r"UNION\s+SELECT",
            r"rm\s+-rf",
            r"shutdown",
            r"\x00"
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                # If malicious input resulted in high confidence, it's a security issue
                if intent != 'general' or any(malicious in str(entities) for malicious in ['script', 'drop', 'union']):
                    return True
        
        return False
    
    async def _test_conversation_flows(self):
        """Test realistic conversation flows"""
        print(f"\n💬 TESTING CONVERSATION FLOWS")
        print("-" * 40)
        
        conversation_flows = [
            {
                'name': 'Portfolio Management Flow',
                'messages': [
                    "Show me my portfolio",
                    "What's my biggest holding?",
                    "How is BTC performing?",
                    "Should I rebalance?",
                    "What's the risk level?",
                    "Add more ETH to portfolio",
                    "Calculate new allocation",
                    "Set alerts for major changes"
                ]
            },
            {
                'name': 'DeFi Exploration Flow',
                'messages': [
                    "What is DeFi?",
                    "How do I start yield farming?",
                    "Show me Aave rates",
                    "Compare with Compound",
                    "What about impermanent loss?",
                    "How to stake ETH?",
                    "Lido vs Rocket Pool?",
                    "Calculate potential returns"
                ]
            },
            {
                'name': 'Trading Decision Flow',
                'messages': [
                    "BTC price now",
                    "Show me the chart",
                    "What's the RSI?",
                    "Any support levels?",
                    "Market sentiment?",
                    "Should I buy now?",
                    "Set stop loss at $40000",
                    "Alert me if it breaks $45000"
                ]
            },
            {
                'name': 'Learning Flow',
                'messages': [
                    "What is Bitcoin?",
                    "How does blockchain work?",
                    "What's the difference between Bitcoin and Ethereum?",
                    "What are smart contracts?",
                    "How do I buy crypto safely?",
                    "What's a hardware wallet?",
                    "Explain DeFi simply",
                    "What are the main risks?"
                ]
            }
        ]
        
        for flow in conversation_flows:
            print(f"\n  🔄 Testing: {flow['name']}")
            
            flow_results = {
                'flow_name': flow['name'],
                'total_messages': len(flow['messages']),
                'successful_messages': 0,
                'context_maintained': True,
                'response_times': [],
                'issues': []
            }
            
            conversation_context = []
            
            for i, message in enumerate(flow['messages'], 1):
                print(f"    {i}. '{message}'")
                
                start_time = time.time()
                try:
                    # Store message for context
                    message_data = {
                        'message_id': i,
                        'chat_id': -12345,
                        'user_id': 12345,
                        'username': 'test_user',
                        'text': message,
                        'timestamp': time.time()
                    }
                    self.message_storage.store_message(message_data)
                    conversation_context.append(message)
                    
                    # Process with context
                    intent, confidence, entities = await analyze_comprehensive_intent(
                        message,
                        user_context={'recent_messages': conversation_context[-3:]}  # Last 3 messages
                    )
                    
                    response_time = time.time() - start_time
                    flow_results['response_times'].append(response_time)
                    
                    # Check if context is maintained
                    if i > 1 and not self._check_context_maintained(conversation_context, intent, entities):
                        flow_results['context_maintained'] = False
                        flow_results['issues'].append(f"Context lost at message {i}: '{message}'")
                    
                    flow_results['successful_messages'] += 1
                    print(f"       ✅ Success ({response_time:.3f}s, {intent}, {confidence:.2f})")
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    flow_results['issues'].append(f"Error at message {i}: {e}")
                    print(f"       ❌ Error: {e}")
            
            # Test conversation summarization
            try:
                messages = self.message_storage.get_messages_for_period(-12345, 1)
                if messages:
                    summary = await generate_daily_summary(messages)
                    print(f"    📝 Generated summary: {len(summary)} characters")
                else:
                    flow_results['issues'].append("No messages retrieved for summarization")
            except Exception as e:
                flow_results['issues'].append(f"Summarization error: {e}")
            
            success_rate = (flow_results['successful_messages'] / flow_results['total_messages']) * 100
            avg_response_time = sum(flow_results['response_times']) / len(flow_results['response_times']) if flow_results['response_times'] else 0
            
            print(f"    📊 Flow Results:")
            print(f"       Success Rate: {success_rate:.1f}%")
            print(f"       Context Maintained: {'✅' if flow_results['context_maintained'] else '❌'}")
            print(f"       Avg Response Time: {avg_response_time:.3f}s")
            print(f"       Issues: {len(flow_results['issues'])}")
            
            self.test_results.append(flow_results)
    
    def _check_context_maintained(self, conversation: List[str], current_intent: str, current_entities: Dict) -> bool:
        """Check if conversation context is maintained"""
        if len(conversation) < 2:
            return True
        
        # Simple heuristic: if previous message mentioned a crypto and current message uses "it" or similar,
        # the current entities should include that crypto
        previous_message = conversation[-2].lower()
        current_message = conversation[-1].lower()
        
        # Check for pronouns that should reference previous context
        pronouns = ['it', 'that', 'this', 'them', 'they']
        if any(pronoun in current_message for pronoun in pronouns):
            # Should have context from previous message
            crypto_symbols = ['btc', 'bitcoin', 'eth', 'ethereum', 'sol', 'solana']
            previous_crypto = None
            for symbol in crypto_symbols:
                if symbol in previous_message:
                    previous_crypto = symbol
                    break
            
            if previous_crypto and 'cryptocurrency' not in current_entities:
                return False  # Context not maintained
        
        return True
    
    async def _test_performance_scenarios(self):
        """Test performance under various load scenarios"""
        print(f"\n⚡ TESTING PERFORMANCE SCENARIOS")
        print("-" * 40)
        
        # Concurrent requests test
        print("  Testing concurrent requests...")
        concurrent_queries = [
            "BTC price",
            "ETH price", 
            "SOL price",
            "Portfolio analysis",
            "Yield opportunities"
        ] * 5  # 25 concurrent requests
        
        start_time = time.time()
        try:
            tasks = [analyze_comprehensive_intent(query) for query in concurrent_queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            concurrent_time = time.time() - start_time
            successful_concurrent = sum(1 for r in results if not isinstance(r, Exception))
            
            print(f"    ✅ Concurrent test: {successful_concurrent}/{len(concurrent_queries)} successful in {concurrent_time:.3f}s")
            
            if concurrent_time > 10.0:
                self.bugs_found.append(f"Poor concurrent performance: {concurrent_time:.3f}s for {len(concurrent_queries)} requests")
                
        except Exception as e:
            print(f"    ❌ Concurrent test failed: {e}")
            self.bugs_found.append(f"Concurrent test failure: {e}")
        
        # Memory stress test
        print("  Testing memory usage...")
        try:
            large_queries = ["What is Bitcoin? " * 100] * 50
            
            start_time = time.time()
            for query in large_queries:
                await analyze_comprehensive_intent(query)
            
            memory_test_time = time.time() - start_time
            print(f"    ✅ Memory test: {len(large_queries)} large queries in {memory_test_time:.3f}s")
            
        except Exception as e:
            print(f"    ❌ Memory test failed: {e}")
            self.bugs_found.append(f"Memory test failure: {e}")
        
        # Rapid-fire test
        print("  Testing rapid-fire requests...")
        try:
            rapid_queries = ["BTC price"] * 100
            
            start_time = time.time()
            for query in rapid_queries:
                await analyze_comprehensive_intent(query)
            
            rapid_time = time.time() - start_time
            print(f"    ✅ Rapid-fire test: {len(rapid_queries)} requests in {rapid_time:.3f}s")
            
            if rapid_time > 30.0:
                self.bugs_found.append(f"Poor rapid-fire performance: {rapid_time:.3f}s for {len(rapid_queries)} requests")
                
        except Exception as e:
            print(f"    ❌ Rapid-fire test failed: {e}")
            self.bugs_found.append(f"Rapid-fire test failure: {e}")
    
    async def _test_ai_provider_scenarios(self):
        """Test AI provider switching scenarios"""
        print(f"\n🤖 TESTING AI PROVIDER SCENARIOS")
        print("-" * 40)
        
        # Test provider switching
        original_provider = ai_provider_manager.current_provider
        
        providers_to_test = ['groq', 'gemini']
        
        for provider in providers_to_test:
            print(f"  Testing with {provider}...")
            
            try:
                # Switch provider
                switch_success = ai_provider_manager.switch_provider(provider)
                if not switch_success:
                    print(f"    ❌ Failed to switch to {provider}")
                    self.bugs_found.append(f"Failed to switch to AI provider: {provider}")
                    continue
                
                # Test basic functionality
                test_queries = [
                    "What is Bitcoin?",
                    "BTC price now",
                    "Show portfolio"
                ]
                
                provider_success = 0
                for query in test_queries:
                    try:
                        intent, confidence, entities = await analyze_comprehensive_intent(query)
                        if confidence > 0.5:
                            provider_success += 1
                    except Exception as e:
                        self.bugs_found.append(f"Error with {provider} on query '{query}': {e}")
                
                success_rate = (provider_success / len(test_queries)) * 100
                print(f"    ✅ {provider}: {success_rate:.1f}% success rate")
                
                if success_rate < 80:
                    self.bugs_found.append(f"Poor performance with {provider}: {success_rate:.1f}% success rate")
                
            except Exception as e:
                print(f"    ❌ Error testing {provider}: {e}")
                self.bugs_found.append(f"Error testing AI provider {provider}: {e}")
        
        # Restore original provider
        ai_provider_manager.switch_provider(original_provider.value)
    
    async def _test_data_source_failures(self):
        """Test behavior when data sources fail"""
        print(f"\n📊 TESTING DATA SOURCE FAILURE SCENARIOS")
        print("-" * 40)
        
        # Test with network-dependent queries that might fail
        network_queries = [
            "BTC price from CoinGecko",
            "ETH market data",
            "DeFi TVL data",
            "Yield farming rates",
            "Social sentiment"
        ]
        
        for query in network_queries:
            print(f"  Testing: '{query}'")
            
            try:
                start_time = time.time()
                intent, confidence, entities = await analyze_comprehensive_intent(query)
                
                # Try to execute if it's actionable
                if self._is_actionable_query(query):
                    result = await execute_intent_with_tools(intent, entities, {})
                    
                    # Check if graceful fallback occurred
                    if not result.get('success', False):
                        if 'fallback' in str(result).lower() or 'error' in str(result).lower():
                            print(f"    ✅ Graceful fallback handled")
                        else:
                            print(f"    ⚠️ Failed without graceful fallback")
                            self.bugs_found.append(f"No graceful fallback for query: '{query}'")
                    else:
                        print(f"    ✅ Successful execution")
                else:
                    print(f"    ✅ Non-actionable query handled")
                
                response_time = time.time() - start_time
                if response_time > 10.0:
                    self.bugs_found.append(f"Timeout issue with query: '{query}' - {response_time:.3f}s")
                
            except Exception as e:
                print(f"    ❌ Exception: {e}")
                self.bugs_found.append(f"Exception with data source query '{query}': {e}")
    
    def _generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE REAL-WORLD TEST REPORT")
        print("=" * 60)
        
        # Calculate overall statistics
        total_tests = sum(result.get('total_queries', result.get('total_cases', result.get('total_messages', 1))) for result in self.test_results)
        total_successful = sum(result.get('successful_queries', result.get('handled_gracefully', result.get('successful_messages', 0))) for result in self.test_results)
        overall_success_rate = (total_successful / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {total_successful}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        print(f"   Bugs Found: {len(self.bugs_found)}")
        
        # Categorize bugs
        bug_categories = {
            'Security': [],
            'Performance': [],
            'Functionality': [],
            'Integration': [],
            'Edge Cases': []
        }
        
        for bug in self.bugs_found:
            if any(word in bug.lower() for word in ['security', 'injection', 'xss', 'malicious']):
                bug_categories['Security'].append(bug)
            elif any(word in bug.lower() for word in ['performance', 'slow', 'timeout', 'concurrent']):
                bug_categories['Performance'].append(bug)
            elif any(word in bug.lower() for word in ['provider', 'switch', 'data source']):
                bug_categories['Integration'].append(bug)
            elif any(word in bug.lower() for word in ['edge case', 'special character', 'unicode']):
                bug_categories['Edge Cases'].append(bug)
            else:
                bug_categories['Functionality'].append(bug)
        
        print(f"\n🐛 BUGS BY CATEGORY:")
        for category, bugs in bug_categories.items():
            if bugs:
                print(f"   {category}: {len(bugs)} issues")
                for bug in bugs[:3]:  # Show first 3
                    print(f"     - {bug[:80]}{'...' if len(bug) > 80 else ''}")
                if len(bugs) > 3:
                    print(f"     ... and {len(bugs) - 3} more")
        
        # Performance analysis
        all_response_times = []
        for result in self.test_results:
            if 'response_times' in result:
                all_response_times.extend(result['response_times'])
        
        if all_response_times:
            avg_response_time = sum(all_response_times) / len(all_response_times)
            max_response_time = max(all_response_times)
            min_response_time = min(all_response_times)
            
            print(f"\n⚡ PERFORMANCE ANALYSIS:")
            print(f"   Average Response Time: {avg_response_time:.3f}s")
            print(f"   Fastest Response: {min_response_time:.3f}s")
            print(f"   Slowest Response: {max_response_time:.3f}s")
            print(f"   Total Responses: {len(all_response_times)}")
        
        # Pattern statistics
        try:
            pattern_stats = get_comprehensive_pattern_stats()
            print(f"\n🧠 NLP PATTERN STATISTICS:")
            print(f"   Total Patterns: {pattern_stats['total_patterns']}")
            print(f"   Total Intents: {pattern_stats['total_intents']}")
            print(f"   Intent Distribution: {len(pattern_stats['intent_distribution'])} categories")
        except Exception as e:
            print(f"\n⚠️ Could not get pattern statistics: {e}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if overall_success_rate < 90:
            print("   🔴 CRITICAL: Overall success rate below 90% - needs immediate attention")
        elif overall_success_rate < 95:
            print("   🟡 WARNING: Overall success rate below 95% - improvement needed")
        else:
            print("   🟢 GOOD: Overall success rate above 95%")
        
        if len(bug_categories['Security']) > 0:
            print("   🚨 SECURITY: Security issues found - immediate fix required")
        
        if len(bug_categories['Performance']) > 5:
            print("   ⚡ PERFORMANCE: Multiple performance issues - optimization needed")
        
        if avg_response_time > 1.0:
            print("   🐌 SPEED: Average response time > 1s - performance tuning needed")
        
        # Save detailed report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_success_rate': overall_success_rate,
            'total_tests': total_tests,
            'total_successful': total_successful,
            'bugs_found': self.bugs_found,
            'bug_categories': bug_categories,
            'test_results': self.test_results,
            'performance_metrics': {
                'avg_response_time': avg_response_time if all_response_times else 0,
                'max_response_time': max_response_time if all_response_times else 0,
                'min_response_time': min_response_time if all_response_times else 0,
                'total_responses': len(all_response_times)
            }
        }
        
        report_filename = f"real_world_test_report_{int(time.time())}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved to: {report_filename}")
        
        # Final assessment
        if overall_success_rate >= 95 and len(self.bugs_found) < 5:
            print(f"\n🎉 ASSESSMENT: EXCELLENT - System is production ready")
        elif overall_success_rate >= 90 and len(self.bugs_found) < 10:
            print(f"\n✅ ASSESSMENT: GOOD - Minor issues to address")
        elif overall_success_rate >= 80:
            print(f"\n⚠️ ASSESSMENT: NEEDS WORK - Significant issues found")
        else:
            print(f"\n❌ ASSESSMENT: POOR - Major issues require immediate attention")
    
    async def _cleanup_tests(self):
        """Cleanup test resources"""
        print(f"\n🧹 Cleaning up test resources...")
        try:
            await cleanup_universal_executor()
            await cleanup_public_data_manager()
            
            # Clean up test database
            if os.path.exists('test_real_world.db'):
                os.remove('test_real_world.db')
            
            print("✅ Cleanup completed successfully")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

async def main():
    """Run comprehensive real-world tests"""
    print("🌍 COMPREHENSIVE REAL-WORLD TESTING SUITE")
    print("Testing the bot with realistic user interactions")
    print("=" * 60)
    
    test_suite = RealWorldTestSuite()
    await test_suite.run_comprehensive_real_world_tests()

if __name__ == "__main__":
    asyncio.run(main())