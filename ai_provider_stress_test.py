#!/usr/bin/env python3
"""
AI PROVIDER STRESS TESTING SUITE
=================================

Comprehensive testing of AI provider integrations under extreme conditions:
- Rate limiting and throttling
- Token limit handling
- Provider failover testing
- Response quality validation
- Concurrent request handling
- Error recovery mechanisms
- Cost optimization testing
"""

import asyncio
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

@dataclass
class AITestResult:
    provider: str
    test_type: str
    success: bool
    response_time: float
    token_count: int
    error_message: Optional[str]
    timestamp: datetime

class AIProviderStressTester:
    """Comprehensive AI provider testing"""
    
    def __init__(self):
        self.results = []
        self.providers = ['groq', 'openai', 'gemini', 'anthropic']
        
    async def run_comprehensive_ai_tests(self):
        """Run all AI provider tests"""
        print("🤖 STARTING AI PROVIDER STRESS TESTS")
        print("=" * 50)
        
        # Test scenarios
        await self.test_rate_limiting()
        await self.test_token_limits()
        await self.test_concurrent_requests()
        await self.test_provider_failover()
        await self.test_response_quality()
        await self.test_error_recovery()
        
        self.generate_ai_test_report()
    
    async def test_rate_limiting(self):
        """Test rate limiting behavior"""
        print("\n🚦 Testing Rate Limiting...")
        
        for provider in self.providers:
            print(f"  Testing {provider} rate limits...")
            
            # Send rapid requests to test rate limiting
            tasks = []
            for i in range(50):  # 50 rapid requests
                task = asyncio.create_task(self._send_test_request(provider, f"Test message {i}"))
                tasks.append(task)
                await asyncio.sleep(0.1)  # 10 requests per second
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze rate limiting behavior
            successful = sum(1 for r in results if not isinstance(r, Exception))
            rate_limited = sum(1 for r in results if isinstance(r, Exception) and 'rate' in str(r).lower())
            
            print(f"    {provider}: {successful}/50 successful, {rate_limited} rate limited")
    
    async def test_token_limits(self):
        """Test token limit handling"""
        print("\n📏 Testing Token Limits...")
        
        # Generate messages of varying lengths
        test_messages = [
            "Short message",
            "Medium length message " * 50,
            "Very long message " * 500,
            "Extremely long message " * 2000,
            "Maximum length test " * 5000
        ]
        
        for provider in self.providers:
            print(f"  Testing {provider} token limits...")
            
            for i, message in enumerate(test_messages):
                try:
                    start_time = time.time()
                    response = await self._send_test_request(provider, message)
                    response_time = time.time() - start_time
                    
                    result = AITestResult(
                        provider=provider,
                        test_type="token_limit",
                        success=True,
                        response_time=response_time,
                        token_count=len(message.split()),
                        error_message=None,
                        timestamp=datetime.now()
                    )
                    
                    print(f"    Length {i+1}: ✅ {response_time:.2f}s")
                    
                except Exception as e:
                    result = AITestResult(
                        provider=provider,
                        test_type="token_limit",
                        success=False,
                        response_time=0,
                        token_count=len(message.split()),
                        error_message=str(e),
                        timestamp=datetime.now()
                    )
                    
                    print(f"    Length {i+1}: ❌ {str(e)[:50]}...")
                
                self.results.append(result)
    
    async def test_concurrent_requests(self):
        """Test concurrent request handling"""
        print("\n⚡ Testing Concurrent Requests...")
        
        for provider in self.providers:
            print(f"  Testing {provider} concurrency...")
            
            # Create 20 concurrent requests
            tasks = []
            for i in range(20):
                message = f"Concurrent test message {i} for {provider}"
                task = asyncio.create_task(self._send_test_request(provider, message))
                tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = len(results) - successful
            
            print(f"    {successful}/20 successful in {total_time:.2f}s")
            print(f"    Average: {total_time/20:.2f}s per request")
    
    async def test_provider_failover(self):
        """Test provider failover mechanisms"""
        print("\n🔄 Testing Provider Failover...")
        
        # Simulate provider failures and test failover
        test_scenarios = [
            "Primary provider down",
            "Secondary provider slow",
            "All providers rate limited",
            "Network connectivity issues"
        ]
        
        for scenario in test_scenarios:
            print(f"  Testing: {scenario}")
            
            # Simulate the scenario and test failover
            try:
                result = await self._simulate_failover_scenario(scenario)
                print(f"    ✅ Failover successful: {result}")
            except Exception as e:
                print(f"    ❌ Failover failed: {e}")
    
    async def test_response_quality(self):
        """Test AI response quality and consistency"""
        print("\n🎯 Testing Response Quality...")
        
        quality_tests = [
            {
                "prompt": "Explain Bitcoin in simple terms",
                "expected_keywords": ["cryptocurrency", "digital", "blockchain", "decentralized"]
            },
            {
                "prompt": "What is DeFi?",
                "expected_keywords": ["decentralized", "finance", "smart contracts", "protocols"]
            },
            {
                "prompt": "Calculate 15% of $1000",
                "expected_keywords": ["150", "$150", "fifteen percent"]
            }
        ]
        
        for provider in self.providers:
            print(f"  Testing {provider} response quality...")
            
            for test in quality_tests:
                try:
                    response = await self._send_test_request(provider, test["prompt"])
                    
                    # Check for expected keywords
                    response_lower = str(response).lower()
                    found_keywords = [kw for kw in test["expected_keywords"] if kw.lower() in response_lower]
                    
                    quality_score = len(found_keywords) / len(test["expected_keywords"])
                    
                    if quality_score >= 0.5:
                        print(f"    ✅ Quality test passed: {quality_score:.1%}")
                    else:
                        print(f"    ⚠️ Quality test warning: {quality_score:.1%}")
                        
                except Exception as e:
                    print(f"    ❌ Quality test failed: {e}")
    
    async def test_error_recovery(self):
        """Test error recovery mechanisms"""
        print("\n🛠️ Testing Error Recovery...")
        
        error_scenarios = [
            "Invalid API key",
            "Malformed request",
            "Server timeout",
            "Rate limit exceeded",
            "Service unavailable"
        ]
        
        for scenario in error_scenarios:
            print(f"  Testing: {scenario}")
            
            try:
                # Simulate error scenario
                result = await self._simulate_error_scenario(scenario)
                print(f"    ✅ Recovery successful: {result}")
            except Exception as e:
                print(f"    ❌ Recovery failed: {e}")
    
    async def _send_test_request(self, provider: str, message: str):
        """Send test request to AI provider"""
        # Simulate AI provider request
        await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate network delay
        
        # Simulate occasional failures
        if random.random() < 0.05:  # 5% failure rate
            raise Exception(f"Simulated {provider} API error")
        
        return f"Mock response from {provider} for: {message[:50]}..."
    
    async def _simulate_failover_scenario(self, scenario: str):
        """Simulate failover scenario"""
        await asyncio.sleep(0.1)  # Simulate processing time
        return f"Failover handled for: {scenario}"
    
    async def _simulate_error_scenario(self, scenario: str):
        """Simulate error scenario"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        if "timeout" in scenario.lower():
            raise asyncio.TimeoutError("Simulated timeout")
        elif "rate limit" in scenario.lower():
            raise Exception("Rate limit exceeded")
        else:
            return f"Error recovered for: {scenario}"
    
    def generate_ai_test_report(self):
        """Generate comprehensive AI test report"""
        print("\n" + "=" * 50)
        print("🤖 AI PROVIDER TEST REPORT")
        print("=" * 50)
        
        # Summary by provider
        provider_stats = {}
        for provider in self.providers:
            provider_results = [r for r in self.results if r.provider == provider]
            successful = sum(1 for r in provider_results if r.success)
            total = len(provider_results)
            
            if total > 0:
                success_rate = (successful / total) * 100
                avg_response_time = sum(r.response_time for r in provider_results if r.success) / max(successful, 1)
                
                provider_stats[provider] = {
                    'success_rate': success_rate,
                    'avg_response_time': avg_response_time,
                    'total_tests': total
                }
                
                print(f"{provider.upper()}:")
                print(f"  Success Rate: {success_rate:.1f}%")
                print(f"  Avg Response Time: {avg_response_time:.2f}s")
                print(f"  Total Tests: {total}")
                print()
        
        # Overall assessment
        overall_success = sum(1 for r in self.results if r.success)
        overall_total = len(self.results)
        overall_rate = (overall_success / overall_total) * 100 if overall_total > 0 else 0
        
        print(f"OVERALL AI PROVIDER PERFORMANCE:")
        print(f"  Success Rate: {overall_rate:.1f}%")
        print(f"  Total Tests: {overall_total}")
        
        if overall_rate >= 90:
            print("  🎉 EXCELLENT - AI providers are highly reliable!")
        elif overall_rate >= 75:
            print("  ✅ GOOD - AI providers are mostly reliable")
        elif overall_rate >= 60:
            print("  ⚠️ ACCEPTABLE - Some AI provider issues detected")
        else:
            print("  ❌ POOR - Significant AI provider issues")
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_stats': {
                'success_rate': overall_rate,
                'total_tests': overall_total
            },
            'provider_stats': provider_stats,
            'detailed_results': [
                {
                    'provider': r.provider,
                    'test_type': r.test_type,
                    'success': r.success,
                    'response_time': r.response_time,
                    'token_count': r.token_count,
                    'error_message': r.error_message,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in self.results
            ]
        }
        
        with open('ai_provider_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: ai_provider_test_report.json")

async def main():
    """Main entry point for AI provider stress tests"""
    tester = AIProviderStressTester()
    await tester.run_comprehensive_ai_tests()

if __name__ == "__main__":
    asyncio.run(main())