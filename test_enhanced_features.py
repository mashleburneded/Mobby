#!/usr/bin/env python3
"""
Test Enhanced Features Implementation
Tests the new enhanced NLP, caching, and async processing features
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, Any

# Add src directory to path
sys.path.insert(0, 'src')

from enhanced_nlp_patterns import (
    enhanced_nlp_engine, 
    analyze_enhanced_intent, 
    get_enhanced_pattern_stats,
    IntentCategory
)
from intelligent_cache import (
    intelligent_cache,
    cache_price_data,
    cache_market_data,
    cache_analysis,
    get_cache_stats,
    cleanup_cache
)
from async_processing_pipeline import (
    async_pipeline,
    process_message_async,
    get_pipeline_stats,
    cleanup_pipeline
)

class EnhancedFeaturesTest:
    """Test enhanced features implementation"""
    
    def __init__(self):
        self.test_results = []
    
    async def run_all_tests(self):
        """Run all enhanced feature tests"""
        print("🚀 TESTING ENHANCED FEATURES")
        print("=" * 60)
        
        # Test enhanced NLP patterns
        await self.test_enhanced_nlp()
        
        # Test intelligent caching
        await self.test_intelligent_caching()
        
        # Test async processing pipeline
        await self.test_async_pipeline()
        
        # Generate summary report
        self.generate_summary_report()
        
        # Cleanup
        await self.cleanup_all()
    
    async def test_enhanced_nlp(self):
        """Test enhanced NLP pattern recognition"""
        print("\n📝 TESTING ENHANCED NLP PATTERNS")
        print("-" * 40)
        
        test_cases = [
            # Trading patterns
            ("long BTC at $45000", IntentCategory.TRADING, 0.9),
            ("short ETH when $3000", IntentCategory.TRADING, 0.9),
            ("scalp trade SOL", IntentCategory.TRADING, 0.85),
            ("DCA into Bitcoin", IntentCategory.TRADING, 0.85),
            ("take profit at $50000", IntentCategory.TRADING, 0.8),
            
            # DeFi patterns
            ("stake ETH on Lido", IntentCategory.STAKING, 0.9),
            ("provide liquidity to ETH/USDC", IntentCategory.LIQUIDITY, 0.85),
            ("farm rewards on Compound", IntentCategory.YIELD, 0.85),
            ("bridge USDC to Polygon", IntentCategory.BRIDGE, 0.8),
            
            # Technical analysis
            ("RSI for BTC", IntentCategory.INDICATORS, 0.9),
            ("MACD for Ethereum", IntentCategory.INDICATORS, 0.9),
            ("support levels for SOL", IntentCategory.TECHNICAL, 0.85),
            
            # Social sentiment
            ("social sentiment for Bitcoin", IntentCategory.SOCIAL, 0.85),
            ("fear index for crypto", IntentCategory.SENTIMENT, 0.85),
            
            # Institutional
            ("compliance check for BTC", IntentCategory.COMPLIANCE, 0.9),
            ("risk assessment for portfolio", IntentCategory.RISK, 0.85),
        ]
        
        passed = 0
        total = len(test_cases)
        
        for i, (text, expected_intent, min_confidence) in enumerate(test_cases, 1):
            try:
                intent_str, confidence, entities = analyze_enhanced_intent(text)
                intent = IntentCategory(intent_str)
                
                success = (intent == expected_intent and confidence >= min_confidence)
                status = "✅ PASS" if success else "❌ FAIL"
                
                print(f"  {i:2d}. {text}")
                print(f"      Expected: {expected_intent.value} (≥{min_confidence})")
                print(f"      Got: {intent.value} ({confidence:.2f}) {status}")
                
                if success:
                    passed += 1
                
                self.test_results.append({
                    'category': 'Enhanced NLP',
                    'test': text,
                    'expected': expected_intent.value,
                    'actual': intent.value,
                    'confidence': confidence,
                    'passed': success
                })
                
            except Exception as e:
                print(f"  {i:2d}. {text}")
                print(f"      ❌ ERROR: {e}")
                self.test_results.append({
                    'category': 'Enhanced NLP',
                    'test': text,
                    'error': str(e),
                    'passed': False
                })
        
        success_rate = (passed / total) * 100
        print(f"\n📊 Enhanced NLP Results: {passed}/{total} ({success_rate:.1f}%)")
        
        # Show pattern coverage
        coverage = get_enhanced_pattern_stats()
        print(f"📋 Pattern Coverage: {sum(coverage.values())} patterns across {len(coverage)} intents")
        for intent, count in sorted(coverage.items()):
            print(f"   {intent}: {count} patterns")
    
    async def test_intelligent_caching(self):
        """Test intelligent caching system"""
        print("\n💾 TESTING INTELLIGENT CACHING")
        print("-" * 40)
        
        # Test cache operations
        test_cases = [
            ("Price Data Caching", self._test_price_caching),
            ("Market Data Caching", self._test_market_caching),
            ("Analysis Caching", self._test_analysis_caching),
            ("Cache Invalidation", self._test_cache_invalidation),
            ("Cache Statistics", self._test_cache_stats),
        ]
        
        for test_name, test_func in test_cases:
            try:
                print(f"\n  Testing {test_name}...")
                result = await test_func()
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                print(f"  {status} {test_name}: {result.get('message', '')}")
                
                self.test_results.append({
                    'category': 'Intelligent Caching',
                    'test': test_name,
                    'passed': result['success'],
                    'details': result
                })
                
            except Exception as e:
                print(f"  ❌ ERROR {test_name}: {e}")
                self.test_results.append({
                    'category': 'Intelligent Caching',
                    'test': test_name,
                    'error': str(e),
                    'passed': False
                })
    
    async def _test_price_caching(self) -> Dict[str, Any]:
        """Test price data caching"""
        call_count = 0
        
        async def mock_price_fetch():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate API call
            return {'price': 45000, 'timestamp': time.time()}
        
        # First call should fetch data
        start_time = time.time()
        result1 = await cache_price_data('BTC', mock_price_fetch)
        time1 = time.time() - start_time
        
        # Second call should use cache
        start_time = time.time()
        result2 = await cache_price_data('BTC', mock_price_fetch)
        time2 = time.time() - start_time
        
        # Verify caching worked
        cache_hit = (call_count == 1 and time2 < time1 * 0.5)
        
        return {
            'success': cache_hit,
            'message': f"Cache hit: {cache_hit}, calls: {call_count}, times: {time1:.3f}s vs {time2:.3f}s"
        }
    
    async def _test_market_caching(self) -> Dict[str, Any]:
        """Test market data caching"""
        call_count = 0
        
        async def mock_market_fetch():
            nonlocal call_count
            call_count += 1
            return {'volume': 1000000, 'market_cap': 850000000000}
        
        # Test different symbols get different cache entries
        result1 = await cache_market_data('BTC', mock_market_fetch)
        result2 = await cache_market_data('ETH', mock_market_fetch)
        result3 = await cache_market_data('BTC', mock_market_fetch)  # Should use cache
        
        # Should have 2 calls (BTC and ETH), third BTC call uses cache
        success = (call_count == 2)
        
        return {
            'success': success,
            'message': f"Market data caching: {call_count} calls for 3 requests"
        }
    
    async def _test_analysis_caching(self) -> Dict[str, Any]:
        """Test analysis caching"""
        call_count = 0
        
        async def mock_analysis():
            nonlocal call_count
            call_count += 1
            return {'analysis': 'bullish', 'confidence': 0.8}
        
        # Test analysis caching
        result1 = await cache_analysis('technical', 'BTC', mock_analysis)
        result2 = await cache_analysis('technical', 'BTC', mock_analysis)  # Should use cache
        result3 = await cache_analysis('fundamental', 'BTC', mock_analysis)  # Different type
        
        # Should have 2 calls (different analysis types)
        success = (call_count == 2)
        
        return {
            'success': success,
            'message': f"Analysis caching: {call_count} calls for 3 requests"
        }
    
    async def _test_cache_invalidation(self) -> Dict[str, Any]:
        """Test cache invalidation"""
        call_count = 0
        
        async def mock_fetch():
            nonlocal call_count
            call_count += 1
            return {'data': f'value_{call_count}'}
        
        # Cache some data
        result1 = await cache_price_data('TEST', mock_fetch)
        
        # Invalidate cache by type
        from intelligent_cache import CacheType
        await intelligent_cache.invalidate_type(CacheType.PRICE)
        
        # Next call should fetch again
        result2 = await cache_price_data('TEST', mock_fetch)
        
        success = (call_count == 2 and result1['data'] != result2['data'])
        
        return {
            'success': success,
            'message': f"Cache invalidation: {call_count} calls, different results: {result1['data']} vs {result2['data']}"
        }
    
    async def _test_cache_stats(self) -> Dict[str, Any]:
        """Test cache statistics"""
        stats = await get_cache_stats()
        
        required_fields = ['size', 'hit_rate', 'hits', 'misses']
        has_all_fields = all(field in stats for field in required_fields)
        
        return {
            'success': has_all_fields,
            'message': f"Cache stats: {stats}"
        }
    
    async def test_async_pipeline(self):
        """Test async processing pipeline"""
        print("\n⚡ TESTING ASYNC PROCESSING PIPELINE")
        print("-" * 40)
        
        test_messages = [
            "What's the price of Bitcoin?",
            "Show my portfolio performance",
            "Find yield opportunities",
            "Research Ethereum fundamentals",
            "Set alert for BTC at $50000"
        ]
        
        total_tests = len(test_messages)
        passed_tests = 0
        
        for i, message in enumerate(test_messages, 1):
            try:
                print(f"\n  {i}. Processing: '{message}'")
                
                start_time = time.time()
                result, metrics = await process_message_async(message, user_id=12345)
                execution_time = time.time() - start_time
                
                success = result.get('success', False)
                status = "✅ PASS" if success else "❌ FAIL"
                
                print(f"     {status} Total time: {execution_time:.3f}s")
                print(f"     Parallel efficiency: {metrics.parallel_efficiency:.1%}")
                print(f"     Success rate: {metrics.success_rate:.1%}")
                print(f"     Bottleneck: {metrics.bottleneck_stage.value if metrics.bottleneck_stage else 'None'}")
                
                if success:
                    passed_tests += 1
                
                self.test_results.append({
                    'category': 'Async Pipeline',
                    'test': message,
                    'passed': success,
                    'execution_time': execution_time,
                    'parallel_efficiency': metrics.parallel_efficiency,
                    'success_rate': metrics.success_rate
                })
                
            except Exception as e:
                print(f"     ❌ ERROR: {e}")
                self.test_results.append({
                    'category': 'Async Pipeline',
                    'test': message,
                    'error': str(e),
                    'passed': False
                })
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📊 Async Pipeline Results: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Show pipeline stats
        stats = await get_pipeline_stats()
        print(f"📋 Pipeline Stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED FEATURES TEST SUMMARY")
        print("=" * 60)
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0, 'failed': 0}
            
            categories[category]['total'] += 1
            if result['passed']:
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
        
        # Print category summaries
        overall_total = 0
        overall_passed = 0
        
        for category, stats in categories.items():
            success_rate = (stats['passed'] / stats['total']) * 100
            status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            
            print(f"\n{status} {category}:")
            print(f"   Total Tests: {stats['total']}")
            print(f"   Passed: {stats['passed']}")
            print(f"   Failed: {stats['failed']}")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            overall_total += stats['total']
            overall_passed += stats['passed']
        
        # Overall summary
        overall_success_rate = (overall_passed / overall_total) * 100 if overall_total > 0 else 0
        overall_status = "🎉 EXCELLENT" if overall_success_rate >= 90 else "✅ GOOD" if overall_success_rate >= 80 else "⚠️ NEEDS WORK"
        
        print(f"\n🏆 OVERALL RESULTS:")
        print(f"   Status: {overall_status}")
        print(f"   Total Tests: {overall_total}")
        print(f"   Passed: {overall_passed}")
        print(f"   Failed: {overall_total - overall_passed}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        
        # Save detailed report
        report_filename = f"enhanced_features_report_{int(time.time())}.json"
        with open(report_filename, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'summary': {
                    'overall_success_rate': overall_success_rate,
                    'total_tests': overall_total,
                    'passed_tests': overall_passed,
                    'categories': categories
                },
                'detailed_results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_filename}")
    
    async def cleanup_all(self):
        """Cleanup all resources"""
        print("\n🧹 Cleaning up resources...")
        try:
            await cleanup_cache()
            await cleanup_pipeline()
            print("✅ Cleanup completed successfully")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

async def main():
    """Run enhanced features tests"""
    print("🚀 ENHANCED FEATURES TESTING SUITE")
    print("Testing new NLP patterns, caching, and async processing")
    print("=" * 60)
    
    tester = EnhancedFeaturesTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())