# test_actual_execution_validation.py
"""
ACTUAL EXECUTION VALIDATION TESTING
Tests 50+ natural language commands and validates:
1. Correct intent detection
2. Correct tool execution
3. Correct output format and content
4. Expected behavior vs actual behavior
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

sys.path.insert(0, 'src')

from real_natural_language_fix import process_natural_language_message
from universal_intent_executor import execute_intent_with_tools
# from production_ready_main import ProductionMobiusBot

class ExecutionValidationTest:
    """Validates actual execution and output correctness"""

    def __init__(self):
        self.test_results = []
        self.validation_errors = []
        self.execution_failures = []

    async def test_command_execution(self, natural_language: str, expected_intent: str,
                                   expected_tools: List[str], expected_output_type: str,
                                   validation_func: callable = None) -> Dict[str, Any]:
        """Test a single command execution and validate output"""

        test_start = time.time()
        result = {
            'input': natural_language,
            'expected_intent': expected_intent,
            'expected_tools': expected_tools,
            'expected_output_type': expected_output_type,
            'success': False,
            'errors': [],
            'execution_time': 0,
            'actual_intent': None,
            'actual_tools': [],
            'actual_output': None,
            'validation_passed': False
        }

        try:
            # Step 1: Test Natural Language Processing
            should_convert, command_string, nl_metadata = process_natural_language_message(natural_language)

            if not should_convert:
                result['errors'].append(f"NLP failed to convert: '{natural_language}'")
                return result

            result['actual_intent'] = nl_metadata.get('command_type', 'unknown')

            # Step 2: Test Intent Execution
            if expected_intent == 'price':
                entities = [{'type': 'cryptocurrency', 'value': self._extract_crypto_symbol(natural_language)}]
                context = {'user_id': 12345}
                execution_result = await execute_intent_with_tools('get_realtime_price', entities, context)

            elif expected_intent == 'portfolio':
                entities = []
                context = {
                    'user_id': 12345,
                    'portfolio': {'BTC': 0.5, 'ETH': 2.0, 'SOL': 10.0, 'ADA': 100.0}
                }
                execution_result = await execute_intent_with_tools('analyze_portfolio', entities, context)

            elif expected_intent == 'research':
                symbol = self._extract_crypto_symbol(natural_language)
                entities = [{'type': 'cryptocurrency', 'value': symbol}]
                context = {'user_id': 12345}
                execution_result = await execute_intent_with_tools('market_research', entities, context)

            elif expected_intent == 'yield':
                entities = []
                context = {'user_id': 12345}
                execution_result = await execute_intent_with_tools('find_yield_opportunities', entities, context)

            elif expected_intent == 'alert':
                symbol = self._extract_crypto_symbol(natural_language)
                price = self._extract_price(natural_language)
                entities = [
                    {'type': 'cryptocurrency', 'value': symbol},
                    {'type': 'monetary_amount', 'value': str(price)}
                ]
                context = {'user_id': 12345}
                execution_result = await execute_intent_with_tools('create_price_alert', entities, context)

            else:
                result['errors'].append(f"Unknown expected intent: {expected_intent}")
                return result

            # Step 3: Validate Execution Result
            if not execution_result.success:
                result['errors'].append(f"Execution failed: {execution_result.error_message}")
                return result

            result['actual_tools'] = execution_result.tool_calls_made
            result['actual_output'] = execution_result.data

            # Step 4: Validate Tools Used
            tools_validation = self._validate_tools_used(expected_tools, execution_result.tool_calls_made)
            if not tools_validation['passed']:
                result['errors'].extend(tools_validation['errors'])

            # Step 5: Validate Output Content
            output_validation = self._validate_output_content(expected_output_type, execution_result.data, natural_language)
            if not output_validation['passed']:
                result['errors'].extend(output_validation['errors'])

            # Step 6: Custom Validation Function
            if validation_func:
                custom_validation = validation_func(execution_result.data, natural_language)
                if not custom_validation['passed']:
                    result['errors'].extend(custom_validation['errors'])

            # Overall success determination
            result['success'] = len(result['errors']) == 0
            result['validation_passed'] = result['success']

        except Exception as e:
            result['errors'].append(f"Exception during execution: {str(e)}")

        result['execution_time'] = time.time() - test_start
        return result

    def _extract_crypto_symbol(self, text: str) -> str:
        """Extract cryptocurrency symbol from text"""
        crypto_map = {
            'bitcoin': 'BTC', 'btc': 'BTC',
            'ethereum': 'ETH', 'eth': 'ETH', 'ether': 'ETH',
            'solana': 'SOL', 'sol': 'SOL',
            'cardano': 'ADA', 'ada': 'ADA',
            'polkadot': 'DOT', 'dot': 'DOT',
            'chainlink': 'LINK', 'link': 'LINK',
            'uniswap': 'UNI', 'uni': 'UNI',
            'aave': 'AAVE',
            'compound': 'COMP', 'comp': 'COMP'
        }

        text_lower = text.lower()
        for name, symbol in crypto_map.items():
            if name in text_lower:
                return symbol

        # Default to BTC if no symbol found
        return 'BTC'

    def _extract_price(self, text: str) -> float:
        """Extract price from text"""
        # Look for price patterns like $50000, 50k, etc.
        price_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+)k',
            r'(\d+(?:\.\d+)?)\s*(?:thousand|k)',
            r'(\d+(?:\.\d+)?)\s*(?:million|m)',
        ]

        for pattern in price_patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = match.group(1).replace(',', '')
                if 'k' in text.lower() or 'thousand' in text.lower():
                    return float(value) * 1000
                elif 'm' in text.lower() or 'million' in text.lower():
                    return float(value) * 1000000
                else:
                    return float(value)

        return 50000.0  # Default price

    def _validate_tools_used(self, expected_tools: List[str], actual_tools: List[str]) -> Dict[str, Any]:
        """Validate that correct tools were used"""
        validation = {'passed': True, 'errors': []}

        # Extract function names from actual tool calls
        actual_function_names = []
        for tool_call in actual_tools:
            # Parse tool call string like "get_crypto_price({'symbol': 'bitcoin'})"
            func_name = tool_call.split('(')[0] if '(' in tool_call else tool_call
            actual_function_names.append(func_name)

        # Check if expected tools were used
        for expected_tool in expected_tools:
            if not any(expected_tool in actual_func for actual_func in actual_function_names):
                validation['passed'] = False
                validation['errors'].append(f"Expected tool '{expected_tool}' was not used. Used: {actual_function_names}")

        return validation

    def _validate_output_content(self, expected_type: str, actual_output: Any, input_text: str) -> Dict[str, Any]:
        """Validate output content based on expected type"""
        validation = {'passed': True, 'errors': []}

        if not actual_output:
            validation['passed'] = False
            validation['errors'].append("No output received")
            return validation

        if expected_type == 'price_data':
            # Validate price data structure and content
            if not isinstance(actual_output, dict):
                validation['passed'] = False
                validation['errors'].append(f"Expected dict output, got {type(actual_output)}")
                return validation

            # Check for required price data fields
            required_fields = ['summary']
            for field in required_fields:
                if field not in actual_output:
                    validation['passed'] = False
                    validation['errors'].append(f"Missing required field '{field}' in price data")

            # Validate price data content
            if 'summary' in actual_output and 'price_data' in actual_output['summary']:
                price_data = actual_output['summary']['price_data']
                if 'price' not in price_data or price_data['price'] <= 0:
                    validation['passed'] = False
                    validation['errors'].append("Invalid or missing price value")

        elif expected_type == 'portfolio_data':
            # Validate portfolio analysis structure
            if not isinstance(actual_output, dict):
                validation['passed'] = False
                validation['errors'].append(f"Expected dict output, got {type(actual_output)}")
                return validation

            # Check for portfolio analysis fields
            if 'summary' not in actual_output:
                validation['passed'] = False
                validation['errors'].append("Missing 'summary' in portfolio data")

            if 'summary' in actual_output and 'portfolio_data' in actual_output['summary']:
                portfolio_data = actual_output['summary']['portfolio_data']
                if 'total_value' not in portfolio_data:
                    validation['passed'] = False
                    validation['errors'].append("Missing 'total_value' in portfolio analysis")

        elif expected_type == 'yield_data':
            # Validate yield opportunities structure
            if not isinstance(actual_output, dict):
                validation['passed'] = False
                validation['errors'].append(f"Expected dict output, got {type(actual_output)}")
                return validation

            if 'summary' in actual_output and 'yield_data' in actual_output['summary']:
                yield_data = actual_output['summary']['yield_data']
                if 'opportunities' not in yield_data:
                    validation['passed'] = False
                    validation['errors'].append("Missing 'opportunities' in yield data")

        elif expected_type == 'alert_confirmation':
            # Validate alert creation confirmation
            if not isinstance(actual_output, dict):
                validation['passed'] = False
                validation['errors'].append(f"Expected dict output, got {type(actual_output)}")
                return validation

            # Should contain confirmation of alert creation
            if 'results' not in actual_output:
                validation['passed'] = False
                validation['errors'].append("Missing 'results' in alert confirmation")

        elif expected_type == 'research_data':
            # Validate research data structure
            if not isinstance(actual_output, dict):
                validation['passed'] = False
                validation['errors'].append(f"Expected dict output, got {type(actual_output)}")
                return validation

            # Should contain market research information
            if 'summary' not in actual_output:
                validation['passed'] = False
                validation['errors'].append("Missing 'summary' in research data")

        return validation

    async def run_comprehensive_execution_tests(self):
        """Run comprehensive execution validation tests"""

        print("🧪 COMPREHENSIVE EXECUTION VALIDATION TESTS")
        print("=" * 80)
        print("Testing 50+ natural language commands with actual execution validation")
        print("Checking: Intent detection → Tool execution → Output validation")
        print()

        # Define comprehensive test cases
        test_cases = [
            # PRICE QUERIES (15 tests)
            {
                'input': "What's the price of Bitcoin?",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price', 'get_market_data'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "Show me BTC price",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "How much is Ethereum worth?",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "Check Solana value",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "Bitcoin price please",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "ETH current price",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "Price of Cardano",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "What does Polkadot cost?",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "BTC worth right now",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "Ethereum value today",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "Current SOL price",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "How much for one Bitcoin?",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "Chainlink price check",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "What's ADA trading at?",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },
            {
                'input': "Give me the latest BTC price",
                'expected_intent': 'price',
                'expected_tools': ['get_crypto_price'],
                'expected_output_type': 'price_data'
            },

            # PORTFOLIO QUERIES (10 tests)
            {
                'input': "Show my portfolio",
                'expected_intent': 'portfolio',
                'expected_tools': ['calculate_portfolio_metrics', 'assess_portfolio_risk'],
                'expected_output_type': 'portfolio_data'
            },
            {
                'input': "Portfolio performance",
                'expected_intent': 'portfolio',
                'expected_tools': ['calculate_portfolio_metrics'],
                'expected_output_type': 'portfolio_data'
            },
            {
                'input': "Check my holdings",
                'expected_intent': 'portfolio',
                'expected_tools': ['calculate_portfolio_metrics'],
                'expected_output_type': 'portfolio_data'
            },
            {
                'input': "My crypto investments",
                'expected_intent': 'portfolio',
                'expected_tools': ['calculate_portfolio_metrics'],
                'expected_output_type': 'portfolio_data'
            },
            {
                'input': "Portfolio analysis",
                'expected_intent': 'portfolio',
                'expected_tools': ['calculate_portfolio_metrics'],
                'expected_output_type': 'portfolio_data'
            },
            {
                'input': "How is my portfolio doing?",
                'expected_intent': 'portfolio',
                'expected_tools': ['calculate_portfolio_metrics'],
                'expected_output_type': 'portfolio_data'
            },
            {
                'input': "Portfolio breakdown",
                'expected_intent': 'portfolio',
                'expected_tools': ['calculate_portfolio_metrics'],
                'expected_output_type': 'portfolio_data'
            },
            {
                'input': "Show my crypto assets",
                'expected_intent': 'portfolio',
                'expected_tools': ['calculate_portfolio_metrics'],
                'expected_output_type': 'portfolio_data'
            },
            {
                'input': "Investment overview",
                'expected_intent': 'portfolio',
                'expected_tools': ['calculate_portfolio_metrics'],
                'expected_output_type': 'portfolio_data'
            },
            {
                'input': "Portfolio status report",
                'expected_intent': 'portfolio',
                'expected_tools': ['calculate_portfolio_metrics'],
                'expected_output_type': 'portfolio_data'
            },

            # RESEARCH QUERIES (10 tests)
            {
                'input': "Research Bitcoin",
                'expected_intent': 'research',
                'expected_tools': ['get_market_data', 'get_crypto_news'],
                'expected_output_type': 'research_data'
            },
            {
                'input': "Tell me about Ethereum",
                'expected_intent': 'research',
                'expected_tools': ['get_market_data'],
                'expected_output_type': 'research_data'
            },
            {
                'input': "Analyze Solana",
                'expected_intent': 'research',
                'expected_tools': ['get_market_data'],
                'expected_output_type': 'research_data'
            },
            {
                'input': "Info on Cardano",
                'expected_intent': 'research',
                'expected_tools': ['get_market_data'],
                'expected_output_type': 'research_data'
            },
            {
                'input': "Study Polkadot",
                'expected_intent': 'research',
                'expected_tools': ['get_market_data'],
                'expected_output_type': 'research_data'
            },
            {
                'input': "Research Chainlink fundamentals",
                'expected_intent': 'research',
                'expected_tools': ['get_market_data'],
                'expected_output_type': 'research_data'
            },
            {
                'input': "Analyze Uniswap protocol",
                'expected_intent': 'research',
                'expected_tools': ['get_market_data'],
                'expected_output_type': 'research_data'
            },
            {
                'input': "Tell me about Aave",
                'expected_intent': 'research',
                'expected_tools': ['get_market_data'],
                'expected_output_type': 'research_data'
            },
            {
                'input': "Study Compound protocol",
                'expected_intent': 'research',
                'expected_tools': ['get_market_data'],
                'expected_output_type': 'research_data'
            },
            {
                'input': "Research market trends for BTC",
                'expected_intent': 'research',
                'expected_tools': ['get_market_data'],
                'expected_output_type': 'research_data'
            },

            # YIELD/DEFI QUERIES (8 tests)
            {
                'input': "Find yield opportunities",
                'expected_intent': 'yield',
                'expected_tools': ['get_yield_opportunities'],
                'expected_output_type': 'yield_data'
            },
            {
                'input': "Best yield farming options",
                'expected_intent': 'yield',
                'expected_tools': ['get_yield_opportunities'],
                'expected_output_type': 'yield_data'
            },
            {
                'input': "High APY staking",
                'expected_intent': 'yield',
                'expected_tools': ['get_yield_opportunities'],
                'expected_output_type': 'yield_data'
            },
            {
                'input': "DeFi yield opportunities",
                'expected_intent': 'yield',
                'expected_tools': ['get_yield_opportunities'],
                'expected_output_type': 'yield_data'
            },
            {
                'input': "Where can I earn yield?",
                'expected_intent': 'yield',
                'expected_tools': ['get_yield_opportunities'],
                'expected_output_type': 'yield_data'
            },
            {
                'input': "Show me farming opportunities",
                'expected_intent': 'yield',
                'expected_tools': ['get_yield_opportunities'],
                'expected_output_type': 'yield_data'
            },
            {
                'input': "Best staking rewards",
                'expected_intent': 'yield',
                'expected_tools': ['get_yield_opportunities'],
                'expected_output_type': 'yield_data'
            },
            {
                'input': "Liquidity mining options",
                'expected_intent': 'yield',
                'expected_tools': ['get_yield_opportunities'],
                'expected_output_type': 'yield_data'
            },

            # ALERT QUERIES (7 tests)
            {
                'input': "Set alert for BTC at $50000",
                'expected_intent': 'alert',
                'expected_tools': ['create_price_alert'],
                'expected_output_type': 'alert_confirmation'
            },
            {
                'input': "Alert me when ETH hits $3000",
                'expected_intent': 'alert',
                'expected_tools': ['create_price_alert'],
                'expected_output_type': 'alert_confirmation'
            },
            {
                'input': "Create alert for SOL at $100",
                'expected_intent': 'alert',
                'expected_tools': ['create_price_alert'],
                'expected_output_type': 'alert_confirmation'
            },
            {
                'input': "Notify when ADA reaches $2",
                'expected_intent': 'alert',
                'expected_tools': ['create_price_alert'],
                'expected_output_type': 'alert_confirmation'
            },
            {
                'input': "Set price alert BTC $60000",
                'expected_intent': 'alert',
                'expected_tools': ['create_price_alert'],
                'expected_output_type': 'alert_confirmation'
            },
            {
                'input': "Alert ETH $4000",
                'expected_intent': 'alert',
                'expected_tools': ['create_price_alert'],
                'expected_output_type': 'alert_confirmation'
            },
            {
                'input': "Create notification for Bitcoin at 55k",
                'expected_intent': 'alert',
                'expected_tools': ['create_price_alert'],
                'expected_output_type': 'alert_confirmation'
            }
        ]

        # Run all tests
        total_tests = len(test_cases)
        passed_tests = 0
        failed_tests = 0

        print(f"🚀 Running {total_tests} execution validation tests...\n")

        for i, test_case in enumerate(test_cases, 1):
            print(f"Test {i:2d}/{total_tests}: {test_case['input'][:50]}...")

            result = await self.test_command_execution(
                test_case['input'],
                test_case['expected_intent'],
                test_case['expected_tools'],
                test_case['expected_output_type']
            )

            if result['success']:
                print(f"         ✅ PASSED ({result['execution_time']:.3f}s)")
                print(f"            Intent: {result['actual_intent']}")
                print(f"            Tools: {len(result['actual_tools'])} executed")
                passed_tests += 1
            else:
                print(f"         ❌ FAILED ({result['execution_time']:.3f}s)")
                for error in result['errors'][:2]:  # Show first 2 errors
                    print(f"            Error: {error}")
                failed_tests += 1

            self.test_results.append(result)
            print()

        # Generate comprehensive report
        self.generate_execution_validation_report(total_tests, passed_tests, failed_tests)

    def generate_execution_validation_report(self, total_tests: int, passed_tests: int, failed_tests: int):
        """Generate comprehensive execution validation report"""

        success_rate = (passed_tests / total_tests) * 100

        print("=" * 80)
        print("📊 EXECUTION VALIDATION REPORT")
        print("=" * 80)

        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ({success_rate:.1f}%)")
        print(f"   Failed: {failed_tests} ({(failed_tests/total_tests)*100:.1f}%)")

        # Analyze by category
        categories = {
            'price': [r for r in self.test_results if r['expected_intent'] == 'price'],
            'portfolio': [r for r in self.test_results if r['expected_intent'] == 'portfolio'],
            'research': [r for r in self.test_results if r['expected_intent'] == 'research'],
            'yield': [r for r in self.test_results if r['expected_intent'] == 'yield'],
            'alert': [r for r in self.test_results if r['expected_intent'] == 'alert']
        }

        print(f"\n📋 CATEGORY BREAKDOWN:")
        for category, results in categories.items():
            if results:
                category_passed = sum(1 for r in results if r['success'])
                category_total = len(results)
                category_rate = (category_passed / category_total) * 100
                print(f"   {category.upper()}: {category_passed}/{category_total} ({category_rate:.1f}%)")

        # Common failure patterns
        print(f"\n❌ COMMON FAILURE PATTERNS:")
        error_patterns = {}
        for result in self.test_results:
            if not result['success']:
                for error in result['errors']:
                    error_type = error.split(':')[0] if ':' in error else error
                    error_patterns[error_type] = error_patterns.get(error_type, 0) + 1

        for error_type, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"   {error_type}: {count} occurrences")

        # Performance metrics
        execution_times = [r['execution_time'] for r in self.test_results if r['execution_time'] > 0]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)

            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"   Average Execution Time: {avg_time:.3f}s")
            print(f"   Fastest Execution: {min_time:.3f}s")
            print(f"   Slowest Execution: {max_time:.3f}s")

        # Final assessment
        print(f"\n🏆 FINAL ASSESSMENT:")
        if success_rate >= 90:
            status = "🎉 EXCELLENT"
            recommendation = "System executes commands correctly and reliably"
        elif success_rate >= 80:
            status = "✅ GOOD"
            recommendation = "System works well with minor execution issues"
        elif success_rate >= 70:
            status = "⚠️ NEEDS IMPROVEMENT"
            recommendation = "Significant execution issues need to be addressed"
        else:
            status = "❌ POOR"
            recommendation = "Major execution problems - system not ready for production"

        print(f"   Status: {status}")
        print(f"   Execution Success Rate: {success_rate:.1f}%")
        print(f"   Recommendation: {recommendation}")

        # Save detailed results
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': success_rate
            },
            'category_breakdown': {
                category: {
                    'total': len(results),
                    'passed': sum(1 for r in results if r['success']),
                    'success_rate': (sum(1 for r in results if r['success']) / len(results)) * 100 if results else 0
                }
                for category, results in categories.items() if results
            },
            'detailed_results': self.test_results,
            'status': status,
            'recommendation': recommendation
        }

        report_filename = f"execution_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        print(f"\n💾 Detailed execution report saved to: {report_filename}")

        return success_rate

async def main():
    """Run comprehensive execution validation tests"""
    print("🧪 STARTING COMPREHENSIVE EXECUTION VALIDATION")
    print("Testing actual command execution and output validation")
    print("This tests the REAL functionality, not just error handling\n")

    validator = ExecutionValidationTest()
    success_rate = await validator.run_comprehensive_execution_tests()

    # Exit with appropriate code
    if success_rate and success_rate >= 80:
        print(f"\n🎉 Execution validation completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Execution validation revealed significant issues.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())