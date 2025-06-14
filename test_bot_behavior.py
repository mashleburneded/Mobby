#!/usr/bin/env python3
"""
Comprehensive Bot Behavior Test
Tests actual user scenarios and response quality
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, List, Any

sys.path.append('src')

class BehaviorTestSuite:
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    async def test_scenario(self, name: str, user_input: str, expected_behavior: str, 
                           provider: str = "groq") -> Dict[str, Any]:
        """Test a specific user scenario"""
        print(f"\n🎭 Testing: {name}")
        print(f"👤 User: {user_input}")
        print(f"🎯 Expected: {expected_behavior}")
        
        try:
            from ai_provider_manager import switch_ai_provider, generate_ai_response
            from agent_memory_database import analyze_user_intent
            
            # Switch to specified provider
            switch_ai_provider(provider)
            
            # Analyze intent
            intent, confidence = analyze_user_intent(user_input)
            print(f"🧠 Intent: {intent} (confidence: {confidence:.2f})")
            
            # Generate response
            messages = [
                {"role": "system", "content": "You are Möbius, a helpful crypto trading assistant. Be informative, accurate, and user-friendly."},
                {"role": "user", "content": user_input}
            ]
            
            start_time = time.time()
            response = await generate_ai_response(messages)
            response_time = time.time() - start_time
            
            print(f"🤖 Bot: {response}")
            print(f"⏱️  Time: {response_time:.2f}s")
            
            # Evaluate response quality
            evaluation = self._evaluate_response(user_input, response, expected_behavior)
            
            result = {
                "scenario": name,
                "user_input": user_input,
                "expected_behavior": expected_behavior,
                "intent": intent,
                "confidence": confidence,
                "response": response,
                "response_time": response_time,
                "evaluation": evaluation,
                "provider": provider
            }
            
            if evaluation["overall_score"] >= 7:
                print(f"✅ PASS (Score: {evaluation['overall_score']}/10)")
                self.passed += 1
            else:
                print(f"❌ FAIL (Score: {evaluation['overall_score']}/10)")
                self.failed += 1
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.failed += 1
            return {"error": str(e)}
    
    def _evaluate_response(self, user_input: str, response: str, expected_behavior: str) -> Dict[str, Any]:
        """Evaluate response quality"""
        if not response:
            return {"overall_score": 0, "issues": ["No response generated"]}
        
        evaluation = {
            "relevance": 0,
            "accuracy": 0,
            "helpfulness": 0,
            "tone": 0,
            "completeness": 0,
            "issues": [],
            "strengths": []
        }
        
        response_lower = response.lower()
        user_lower = user_input.lower()
        expected_lower = expected_behavior.lower()
        
        # Check relevance (does it address the user's question?)
        if any(word in response_lower for word in user_lower.split() if len(word) > 3):
            evaluation["relevance"] += 5
            evaluation["strengths"].append("Addresses user's topic")
        
        # Check for crypto-specific accuracy
        crypto_terms = ["bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain", "defi", "price", "trading"]
        if any(term in user_lower for term in crypto_terms):
            if any(term in response_lower for term in crypto_terms):
                evaluation["accuracy"] += 3
                evaluation["strengths"].append("Uses appropriate crypto terminology")
        
        # Check helpfulness (provides actionable information)
        helpful_indicators = ["you can", "try", "here's how", "steps", "recommend", "suggest"]
        if any(indicator in response_lower for indicator in helpful_indicators):
            evaluation["helpfulness"] += 3
            evaluation["strengths"].append("Provides actionable advice")
        
        # Check tone (friendly and professional)
        if len(response) > 20 and not any(word in response_lower for word in ["error", "cannot", "unable", "sorry"]):
            evaluation["tone"] += 2
            evaluation["strengths"].append("Positive and confident tone")
        
        # Check completeness (not too short, not too long)
        if 50 <= len(response) <= 500:
            evaluation["completeness"] += 2
            evaluation["strengths"].append("Appropriate response length")
        elif len(response) < 20:
            evaluation["issues"].append("Response too short")
        elif len(response) > 1000:
            evaluation["issues"].append("Response too long")
        
        # Check for specific expected behaviors
        if "price" in expected_lower and "price" in response_lower:
            evaluation["accuracy"] += 2
        if "portfolio" in expected_lower and "portfolio" in response_lower:
            evaluation["accuracy"] += 2
        if "alert" in expected_lower and "alert" in response_lower:
            evaluation["accuracy"] += 2
        
        # Calculate overall score
        total_score = sum(evaluation[key] for key in ["relevance", "accuracy", "helpfulness", "tone", "completeness"])
        evaluation["overall_score"] = min(10, total_score)
        
        return evaluation

async def run_behavior_tests():
    """Run comprehensive behavior tests"""
    suite = BehaviorTestSuite()
    
    print("🎭 MÖBIUS BOT BEHAVIOR TEST SUITE")
    print("🔬 Testing real user scenarios and response quality")
    print("=" * 80)
    
    # Test scenarios covering different user intents and complexity levels
    scenarios = [
        {
            "name": "Basic Price Query",
            "input": "What's the price of Bitcoin?",
            "expected": "Should provide current BTC price information",
            "provider": "groq"
        },
        {
            "name": "Portfolio Request",
            "input": "Show me my crypto portfolio",
            "expected": "Should explain how to view portfolio or ask for more info",
            "provider": "groq"
        },
        {
            "name": "Price Alert Setup",
            "input": "Set an alert when ETH reaches $4000",
            "expected": "Should guide user through alert setup process",
            "provider": "gemini"
        },
        {
            "name": "DeFi Explanation",
            "input": "What is DeFi and how does it work?",
            "expected": "Should provide clear explanation of decentralized finance",
            "provider": "gemini"
        },
        {
            "name": "Trading Advice",
            "input": "Should I buy Bitcoin now or wait?",
            "expected": "Should provide balanced analysis without financial advice",
            "provider": "groq"
        },
        {
            "name": "Technical Analysis",
            "input": "Analyze the current market trend for Ethereum",
            "expected": "Should provide market analysis or explain how to get it",
            "provider": "gemini"
        },
        {
            "name": "Wallet Help",
            "input": "How do I create a secure crypto wallet?",
            "expected": "Should provide wallet creation guidance and security tips",
            "provider": "groq"
        },
        {
            "name": "Complex Query",
            "input": "Compare the performance of Bitcoin vs Ethereum over the last month and suggest which one has better potential",
            "expected": "Should provide comparative analysis or explain how to get this data",
            "provider": "gemini"
        },
        {
            "name": "Casual Conversation",
            "input": "Hey, what's up? How's the crypto market today?",
            "expected": "Should respond naturally and provide market overview",
            "provider": "groq"
        },
        {
            "name": "Error Handling",
            "input": "Show me the price of INVALIDCOIN123",
            "expected": "Should handle unknown token gracefully and suggest alternatives",
            "provider": "gemini"
        }
    ]
    
    print(f"\n🧪 Running {len(scenarios)} behavior test scenarios...")
    
    # Run all scenarios
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}/{len(scenarios)}")
        await suite.test_scenario(
            scenario["name"],
            scenario["input"],
            scenario["expected"],
            scenario["provider"]
        )
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("🏆 BEHAVIOR TEST RESULTS")
    print(f"{'='*80}")
    
    total_tests = len(scenarios)
    success_rate = (suite.passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"📊 Overall Results:")
    print(f"   ✅ Passed: {suite.passed}/{total_tests}")
    print(f"   ❌ Failed: {suite.failed}/{total_tests}")
    print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    # Analyze by provider
    groq_results = [r for r in suite.test_results if r.get("provider") == "groq"]
    gemini_results = [r for r in suite.test_results if r.get("provider") == "gemini"]
    
    if groq_results:
        groq_avg_score = sum(r["evaluation"]["overall_score"] for r in groq_results) / len(groq_results)
        groq_avg_time = sum(r["response_time"] for r in groq_results) / len(groq_results)
        print(f"\n🤖 Groq Performance:")
        print(f"   Average Score: {groq_avg_score:.1f}/10")
        print(f"   Average Time: {groq_avg_time:.2f}s")
    
    if gemini_results:
        gemini_avg_score = sum(r["evaluation"]["overall_score"] for r in gemini_results) / len(gemini_results)
        gemini_avg_time = sum(r["response_time"] for r in gemini_results) / len(gemini_results)
        print(f"\n🧠 Gemini 2.0 Flash Performance:")
        print(f"   Average Score: {gemini_avg_score:.1f}/10")
        print(f"   Average Time: {gemini_avg_time:.2f}s")
    
    # Show detailed analysis
    print(f"\n📋 Detailed Analysis:")
    
    high_performers = [r for r in suite.test_results if r.get("evaluation", {}).get("overall_score", 0) >= 8]
    low_performers = [r for r in suite.test_results if r.get("evaluation", {}).get("overall_score", 0) < 6]
    
    if high_performers:
        print(f"\n✅ High-performing scenarios ({len(high_performers)}):")
        for result in high_performers:
            score = result["evaluation"]["overall_score"]
            print(f"   • {result['scenario']}: {score}/10")
    
    if low_performers:
        print(f"\n❌ Areas for improvement ({len(low_performers)}):")
        for result in low_performers:
            score = result["evaluation"]["overall_score"]
            issues = result["evaluation"]["issues"]
            print(f"   • {result['scenario']}: {score}/10")
            for issue in issues:
                print(f"     - {issue}")
    
    # Save detailed report
    report = {
        "timestamp": time.time(),
        "total_scenarios": total_tests,
        "passed": suite.passed,
        "failed": suite.failed,
        "success_rate": success_rate,
        "detailed_results": suite.test_results,
        "summary": {
            "groq_performance": {
                "avg_score": groq_avg_score if groq_results else 0,
                "avg_time": groq_avg_time if groq_results else 0,
                "test_count": len(groq_results)
            },
            "gemini_performance": {
                "avg_score": gemini_avg_score if gemini_results else 0,
                "avg_time": gemini_avg_time if gemini_results else 0,
                "test_count": len(gemini_results)
            }
        }
    }
    
    with open("behavior_test_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved: behavior_test_report.json")
    
    # Final assessment
    if success_rate >= 80:
        print(f"\n🎉 EXCELLENT! Bot behavior is production-ready")
        print(f"✅ The bot handles user scenarios appropriately")
        print(f"✅ Responses are relevant and helpful")
        print(f"✅ Both Groq and Gemini providers are working well")
    elif success_rate >= 60:
        print(f"\n⚠️  GOOD but needs improvement")
        print(f"✅ Basic functionality works")
        print(f"⚠️  Some scenarios need better handling")
    else:
        print(f"\n❌ NEEDS SIGNIFICANT IMPROVEMENT")
        print(f"❌ Many scenarios are not handled properly")
        print(f"❌ Response quality needs work")
    
    return success_rate >= 70

if __name__ == "__main__":
    try:
        success = asyncio.run(run_behavior_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        sys.exit(1)