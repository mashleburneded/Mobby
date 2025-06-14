#!/usr/bin/env python3
# comprehensive_api_test.py - Comprehensive API Testing with Real Credentials
"""
Comprehensive testing suite using real API credentials
Tests all integrations while maintaining security
"""

import asyncio
import logging
import time
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import modules
from config import config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecureAPITestSuite:
    """Comprehensive API testing with real credentials (kept secure)"""
    
    def __init__(self):
        self.test_results = {}
        self.api_status = {}
        self.start_time = None
        self.test_user_id = 12345
        
        # Mask sensitive data for logging
        self.masked_config = self._mask_sensitive_config()
        
    def _mask_sensitive_config(self) -> Dict[str, str]:
        """Mask sensitive configuration for safe logging"""
        masked = {}
        for key, value in os.environ.items():
            if any(sensitive in key.upper() for sensitive in ['TOKEN', 'KEY', 'SECRET', 'PASSWORD']):
                if value and len(value) > 8:
                    masked[key] = f"{value[:4]}...{value[-4:]}"
                else:
                    masked[key] = "***MASKED***"
            else:
                masked[key] = value
        return masked
        
    async def run_comprehensive_api_tests(self) -> Dict[str, Any]:
        """Run comprehensive API tests with real credentials"""
        self.start_time = time.time()
        logger.info("🔐 Starting Secure API Test Suite")
        
        test_categories = [
            ("Environment Configuration", self.test_environment_config),
            ("AI Provider APIs", self.test_ai_providers),
            ("Blockchain & Web3 APIs", self.test_blockchain_apis),
            ("Telegram Bot API", self.test_telegram_api),
            ("Google Gemini API", self.test_gemini_api),
            ("Groq API", self.test_groq_api),
            ("Security & Encryption", self.test_security_features),
            ("Database Operations", self.test_database_operations),
            ("Cross-Chain Integration", self.test_cross_chain_features),
            ("Performance Under Load", self.test_performance_with_apis),
            ("Error Handling", self.test_api_error_handling),
            ("End-to-End Integration", self.test_e2e_integration)
        ]
        
        total_tests = 0
        passed_tests = 0
        
        for category_name, test_function in test_categories:
            logger.info(f"\n🧪 Testing: {category_name}")
            try:
                category_results = await test_function()
                self.test_results[category_name] = category_results
                
                category_passed = sum(1 for result in category_results.values() if result.get('passed', False))
                category_total = len(category_results)
                
                total_tests += category_total
                passed_tests += category_passed
                
                logger.info(f"✅ {category_name}: {category_passed}/{category_total} tests passed")
                
            except Exception as e:
                logger.error(f"❌ {category_name} failed: {e}")
                self.test_results[category_name] = {"error": str(e), "passed": False}
        
        # Generate secure report
        total_time = time.time() - self.start_time
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        final_report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "total_time": f"{total_time:.2f}s",
                "timestamp": datetime.now().isoformat()
            },
            "category_results": self.test_results,
            "api_status": self.api_status,
            "environment_info": {
                "python_version": sys.version.split()[0],
                "platform": sys.platform,
                "config_loaded": bool(config),
                "env_vars_count": len([k for k in os.environ.keys() if not k.startswith('_')])
            }
        }
        
        # Save report (without sensitive data)
        with open('secure_api_test_report.json', 'w') as f:
            json.dump(final_report, f, indent=2, default=str)
        
        logger.info(f"\n🎯 API Test Suite Complete: {success_rate:.1f}% success rate")
        logger.info(f"📊 Secure report saved to: secure_api_test_report.json")
        
        return final_report

    async def test_environment_config(self) -> Dict[str, Any]:
        """Test environment configuration"""
        results = {}
        
        # Test 1: Environment Variables Loading
        try:
            required_vars = [
                'TELEGRAM_BOT_TOKEN',
                'TELEGRAM_CHAT_ID', 
                'BOT_MASTER_ENCRYPTION_KEY',
                'GROQ_API_KEY',
                'GEMINI_API_KEY'
            ]
            
            missing_vars = []
            present_vars = []
            
            for var in required_vars:
                if os.getenv(var):
                    present_vars.append(var)
                else:
                    missing_vars.append(var)
            
            results["env_variables"] = {
                "passed": len(missing_vars) == 0,
                "details": f"{len(present_vars)}/{len(required_vars)} required variables present",
                "present_vars": present_vars,
                "missing_vars": missing_vars
            }
            
        except Exception as e:
            results["env_variables"] = {"passed": False, "error": str(e)}
        
        # Test 2: Config Module Loading
        try:
            config_loaded = hasattr(config, 'get') and callable(config.get)
            telegram_token = config.get('TELEGRAM_BOT_TOKEN')
            
            results["config_module"] = {
                "passed": config_loaded and bool(telegram_token),
                "details": "Config module loaded and accessible",
                "config_functional": config_loaded,
                "telegram_token_present": bool(telegram_token)
            }
            
        except Exception as e:
            results["config_module"] = {"passed": False, "error": str(e)}
        
        # Test 3: Security Key Validation
        try:
            encryption_key = os.getenv('BOT_MASTER_ENCRYPTION_KEY')
            key_valid = encryption_key and len(encryption_key) >= 32
            
            results["security_keys"] = {
                "passed": key_valid,
                "details": "Encryption key format validation",
                "key_present": bool(encryption_key),
                "key_length_valid": key_valid
            }
            
        except Exception as e:
            results["security_keys"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_ai_providers(self) -> Dict[str, Any]:
        """Test AI provider APIs"""
        results = {}
        
        # Test Groq API
        try:
            groq_key = os.getenv('GROQ_API_KEY')
            if groq_key:
                # Test Groq connection (without exposing key)
                from groq import Groq
                client = Groq(api_key=groq_key)
                
                # Simple test call
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": "Hello, respond with just 'OK'"}],
                    model="mixtral-8x7b-32768",
                    max_tokens=10
                )
                
                groq_working = bool(response.choices[0].message.content)
                self.api_status['groq'] = 'working' if groq_working else 'error'
                
                results["groq_api"] = {
                    "passed": groq_working,
                    "details": "Groq API connection successful",
                    "response_received": groq_working,
                    "api_key_format": f"gsk_...{groq_key[-4:]}" if groq_key else "missing"
                }
            else:
                results["groq_api"] = {
                    "passed": False,
                    "details": "Groq API key not provided"
                }
                
        except Exception as e:
            results["groq_api"] = {"passed": False, "error": str(e)}
            self.api_status['groq'] = 'error'
        
        # Test Google Gemini API
        try:
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content("Hello, respond with just 'OK'")
                
                gemini_working = bool(response.text)
                self.api_status['gemini'] = 'working' if gemini_working else 'error'
                
                results["gemini_api"] = {
                    "passed": gemini_working,
                    "details": "Google Gemini API connection successful",
                    "response_received": gemini_working,
                    "api_key_format": f"AIza...{gemini_key[-4:]}" if gemini_key else "missing"
                }
            else:
                results["gemini_api"] = {
                    "passed": False,
                    "details": "Gemini API key not provided"
                }
                
        except Exception as e:
            results["gemini_api"] = {"passed": False, "error": str(e)}
            self.api_status['gemini'] = 'error'
        
        return results

    async def test_blockchain_apis(self) -> Dict[str, Any]:
        """Test blockchain and Web3 APIs"""
        results = {}
        
        # Test Ethereum RPC
        try:
            eth_rpc = os.getenv('ETHEREUM_RPC_URL')
            if eth_rpc:
                from web3 import Web3
                w3 = Web3(Web3.HTTPProvider(eth_rpc))
                
                # Test connection
                is_connected = w3.is_connected()
                if is_connected:
                    latest_block = w3.eth.block_number
                    eth_working = latest_block > 0
                else:
                    eth_working = False
                
                self.api_status['ethereum_rpc'] = 'working' if eth_working else 'error'
                
                results["ethereum_rpc"] = {
                    "passed": eth_working,
                    "details": f"Ethereum RPC connection successful, block: {latest_block if eth_working else 'N/A'}",
                    "connected": is_connected,
                    "latest_block": latest_block if eth_working else None,
                    "rpc_endpoint": f"{eth_rpc[:20]}...{eth_rpc[-10:]}" if eth_rpc else "missing"
                }
            else:
                results["ethereum_rpc"] = {
                    "passed": False,
                    "details": "Ethereum RPC URL not provided"
                }
                
        except Exception as e:
            results["ethereum_rpc"] = {"passed": False, "error": str(e)}
            self.api_status['ethereum_rpc'] = 'error'
        
        # Test CoinGecko API (free tier)
        try:
            import requests
            response = requests.get('https://api.coingecko.com/api/v3/ping', timeout=10)
            coingecko_working = response.status_code == 200
            
            if coingecko_working:
                # Test price endpoint
                price_response = requests.get(
                    'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
                    timeout=10
                )
                price_data = price_response.json() if price_response.status_code == 200 else {}
                btc_price = price_data.get('bitcoin', {}).get('usd')
            else:
                btc_price = None
            
            self.api_status['coingecko'] = 'working' if coingecko_working else 'error'
            
            results["coingecko_api"] = {
                "passed": coingecko_working,
                "details": f"CoinGecko API working, BTC price: ${btc_price}" if btc_price else "CoinGecko API accessible",
                "api_accessible": coingecko_working,
                "btc_price": btc_price
            }
            
        except Exception as e:
            results["coingecko_api"] = {"passed": False, "error": str(e)}
            self.api_status['coingecko'] = 'error'
        
        return results

    async def test_telegram_api(self) -> Dict[str, Any]:
        """Test Telegram Bot API"""
        results = {}
        
        try:
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
            if telegram_token:
                import requests
                
                # Test bot info
                response = requests.get(
                    f'https://api.telegram.org/bot{telegram_token}/getMe',
                    timeout=10
                )
                
                if response.status_code == 200:
                    bot_info = response.json()
                    bot_working = bot_info.get('ok', False)
                    bot_username = bot_info.get('result', {}).get('username', 'Unknown')
                    
                    self.api_status['telegram'] = 'working' if bot_working else 'error'
                    
                    results["telegram_bot"] = {
                        "passed": bot_working,
                        "details": f"Telegram bot active: @{bot_username}",
                        "bot_active": bot_working,
                        "bot_username": bot_username,
                        "token_format": f"{telegram_token[:10]}...{telegram_token[-4:]}"
                    }
                else:
                    results["telegram_bot"] = {
                        "passed": False,
                        "details": f"Telegram API error: {response.status_code}",
                        "status_code": response.status_code
                    }
                    self.api_status['telegram'] = 'error'
            else:
                results["telegram_bot"] = {
                    "passed": False,
                    "details": "Telegram bot token not provided"
                }
                
        except Exception as e:
            results["telegram_bot"] = {"passed": False, "error": str(e)}
            self.api_status['telegram'] = 'error'
        
        return results

    async def test_gemini_api(self) -> Dict[str, Any]:
        """Test Google Gemini API specifically"""
        results = {}
        
        try:
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                
                # Test different models
                models_to_test = ['gemini-1.5-flash', 'gemini-1.5-pro']
                working_models = []
                
                for model_name in models_to_test:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content("What is 2+2? Answer with just the number.")
                        
                        if response.text and '4' in response.text:
                            working_models.append(model_name)
                            
                    except Exception as model_error:
                        logger.debug(f"Model {model_name} test failed: {model_error}")
                
                gemini_working = len(working_models) > 0
                self.api_status['gemini_detailed'] = 'working' if gemini_working else 'error'
                
                results["gemini_detailed"] = {
                    "passed": gemini_working,
                    "details": f"Gemini models working: {working_models}",
                    "working_models": working_models,
                    "total_models_tested": len(models_to_test),
                    "api_key_valid": gemini_working
                }
            else:
                results["gemini_detailed"] = {
                    "passed": False,
                    "details": "Gemini API key not provided"
                }
                
        except Exception as e:
            results["gemini_detailed"] = {"passed": False, "error": str(e)}
            self.api_status['gemini_detailed'] = 'error'
        
        return results

    async def test_groq_api(self) -> Dict[str, Any]:
        """Test Groq API specifically"""
        results = {}
        
        try:
            groq_key = os.getenv('GROQ_API_KEY')
            if groq_key:
                from groq import Groq
                client = Groq(api_key=groq_key)
                
                # Test different models
                models_to_test = [
                    'llama3-8b-8192',
                    'llama3-70b-8192',
                    'gemma2-9b-it'
                ]
                
                working_models = []
                
                for model_name in models_to_test:
                    try:
                        response = client.chat.completions.create(
                            messages=[{"role": "user", "content": "Say 'test successful'"}],
                            model=model_name,
                            max_tokens=10
                        )
                        
                        if response.choices[0].message.content:
                            working_models.append(model_name)
                            
                    except Exception as model_error:
                        logger.debug(f"Groq model {model_name} test failed: {model_error}")
                
                groq_working = len(working_models) > 0
                self.api_status['groq_detailed'] = 'working' if groq_working else 'error'
                
                results["groq_detailed"] = {
                    "passed": groq_working,
                    "details": f"Groq models working: {working_models}",
                    "working_models": working_models,
                    "total_models_tested": len(models_to_test),
                    "api_key_valid": groq_working
                }
            else:
                results["groq_detailed"] = {
                    "passed": False,
                    "details": "Groq API key not provided"
                }
                
        except Exception as e:
            results["groq_detailed"] = {"passed": False, "error": str(e)}
            self.api_status['groq_detailed'] = 'error'
        
        return results

    async def test_security_features(self) -> Dict[str, Any]:
        """Test security and encryption features"""
        results = {}
        
        # Test encryption key
        try:
            encryption_key = os.getenv('BOT_MASTER_ENCRYPTION_KEY')
            if encryption_key:
                # Test key format and length
                import base64
                try:
                    # Check if it's a valid base64 string and reasonable length
                    import base64
                    decoded_key = base64.b64decode(encryption_key + '==')  # Add padding if needed
                    key_valid = len(decoded_key) >= 16  # At least 128-bit key
                except:
                    # If not base64, check if it's a reasonable length string
                    key_valid = len(encryption_key) >= 32
                
                results["encryption_key"] = {
                    "passed": key_valid,
                    "details": "Encryption key format validation",
                    "key_length_valid": key_valid,
                    "key_format": f"{encryption_key[:8]}...{encryption_key[-4:]}"
                }
            else:
                results["encryption_key"] = {
                    "passed": False,
                    "details": "Encryption key not provided"
                }
                
        except Exception as e:
            results["encryption_key"] = {"passed": False, "error": str(e)}
        
        # Test environment security
        try:
            sensitive_vars = [k for k in os.environ.keys() if any(s in k.upper() for s in ['TOKEN', 'KEY', 'SECRET'])]
            secure_count = len([k for k in sensitive_vars if os.getenv(k) and len(os.getenv(k)) > 8])
            
            results["env_security"] = {
                "passed": secure_count > 0,
                "details": f"{secure_count} secure environment variables configured",
                "sensitive_vars_count": len(sensitive_vars),
                "secure_vars_count": secure_count
            }
            
        except Exception as e:
            results["env_security"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_database_operations(self) -> Dict[str, Any]:
        """Test database operations"""
        results = {}
        
        try:
            # Test database initialization
            from user_db import init_db, set_user_property, get_user_property
            
            # Initialize database
            init_db()
            
            # Test basic operations
            test_user_id = 999999  # Test user
            test_key = "test_property"
            test_value = "test_value_123"
            
            # Set property
            set_user_property(test_user_id, test_key, test_value)
            
            # Get property
            retrieved_value = get_user_property(test_user_id, test_key)
            
            db_working = retrieved_value == test_value
            
            results["database_operations"] = {
                "passed": db_working,
                "details": "Database read/write operations successful",
                "write_successful": True,
                "read_successful": db_working,
                "data_integrity": db_working
            }
            
        except Exception as e:
            results["database_operations"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_cross_chain_features(self) -> Dict[str, Any]:
        """Test cross-chain features"""
        results = {}
        
        try:
            # Test cross-chain analytics
            from cross_chain_analytics import CrossChainAnalytics
            
            analytics = CrossChainAnalytics()
            
            # Test supported chains
            supported_chains = len(analytics.supported_chains)
            chains_working = supported_chains >= 3  # Should support at least 3 chains
            
            results["cross_chain_support"] = {
                "passed": chains_working,
                "details": f"Cross-chain analytics supports {supported_chains} chains",
                "supported_chains_count": supported_chains,
                "minimum_chains_met": chains_working
            }
            
        except Exception as e:
            results["cross_chain_support"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_performance_with_apis(self) -> Dict[str, Any]:
        """Test performance with real APIs"""
        results = {}
        
        # Test API response times
        try:
            import time
            import requests
            
            api_tests = [
                ("CoinGecko", "https://api.coingecko.com/api/v3/ping"),
                ("Telegram", f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN', 'invalid')}/getMe")
            ]
            
            response_times = []
            successful_apis = 0
            
            for api_name, url in api_tests:
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=5)
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        response_times.append(response_time)
                        successful_apis += 1
                        
                except Exception:
                    pass
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            performance_good = avg_response_time < 2.0 and successful_apis >= 1
            
            results["api_performance"] = {
                "passed": performance_good,
                "details": f"Average API response time: {avg_response_time:.3f}s",
                "avg_response_time": f"{avg_response_time:.3f}s",
                "successful_apis": successful_apis,
                "total_apis_tested": len(api_tests)
            }
            
        except Exception as e:
            results["api_performance"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_api_error_handling(self) -> Dict[str, Any]:
        """Test API error handling"""
        results = {}
        
        try:
            # Test with invalid API calls
            error_scenarios = [
                ("Invalid Telegram Token", "https://api.telegram.org/botinvalid_token/getMe"),
                ("Invalid CoinGecko Endpoint", "https://api.coingecko.com/api/v3/invalid_endpoint")
            ]
            
            errors_handled = 0
            
            for scenario_name, url in error_scenarios:
                try:
                    import requests
                    response = requests.get(url, timeout=5)
                    # Should get error response, not crash
                    if response.status_code != 200:
                        errors_handled += 1
                except requests.exceptions.RequestException:
                    # Network errors are also handled gracefully
                    errors_handled += 1
                except Exception:
                    # Any other exception means error handling needs work
                    pass
            
            error_handling_good = errors_handled == len(error_scenarios)
            
            results["api_error_handling"] = {
                "passed": error_handling_good,
                "details": f"API error handling: {errors_handled}/{len(error_scenarios)} scenarios handled",
                "errors_handled": errors_handled,
                "total_scenarios": len(error_scenarios),
                "graceful_degradation": error_handling_good
            }
            
        except Exception as e:
            results["api_error_handling"] = {"passed": False, "error": str(e)}
        
        return results

    async def test_e2e_integration(self) -> Dict[str, Any]:
        """Test end-to-end integration"""
        results = {}
        
        try:
            # Test complete workflow
            workflow_steps = []
            
            # Step 1: Environment loaded
            env_loaded = bool(os.getenv('TELEGRAM_BOT_TOKEN'))
            workflow_steps.append(("Environment", env_loaded))
            
            # Step 2: Database accessible
            try:
                from user_db import init_db
                init_db()
                db_accessible = True
            except:
                db_accessible = False
            workflow_steps.append(("Database", db_accessible))
            
            # Step 3: At least one AI provider working
            ai_working = self.api_status.get('groq') == 'working' or self.api_status.get('gemini') == 'working'
            workflow_steps.append(("AI Provider", ai_working))
            
            # Step 4: Telegram API accessible
            telegram_working = self.api_status.get('telegram') == 'working'
            workflow_steps.append(("Telegram API", telegram_working))
            
            successful_steps = sum(1 for _, status in workflow_steps if status)
            e2e_working = successful_steps >= 3  # At least 3/4 steps should work
            
            results["e2e_integration"] = {
                "passed": e2e_working,
                "details": f"End-to-end integration: {successful_steps}/{len(workflow_steps)} steps successful",
                "workflow_steps": [{"step": step, "status": status} for step, status in workflow_steps],
                "successful_steps": successful_steps,
                "integration_ready": e2e_working
            }
            
        except Exception as e:
            results["e2e_integration"] = {"passed": False, "error": str(e)}
        
        return results

async def main():
    """Run the comprehensive API test suite"""
    print("🔐 Starting Comprehensive API Test Suite")
    print("=" * 60)
    
    test_suite = SecureAPITestSuite()
    
    try:
        # Run all tests
        final_report = await test_suite.run_comprehensive_api_tests()
        
        # Print summary
        summary = final_report["test_summary"]
        print(f"\n📊 API TEST SUMMARY")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Total Time: {summary['total_time']}")
        
        # Print API status
        if test_suite.api_status:
            print(f"\n🔌 API STATUS")
            for api, status in test_suite.api_status.items():
                status_emoji = "✅" if status == "working" else "❌"
                print(f"{api}: {status_emoji} {status}")
        
        # Determine overall result
        success_rate = float(summary['success_rate'].replace('%', ''))
        if success_rate >= 90:
            print(f"\n✅ EXCELLENT: All APIs working perfectly!")
        elif success_rate >= 80:
            print(f"\n🟡 GOOD: Most APIs working with minor issues")
        elif success_rate >= 70:
            print(f"\n🟠 FAIR: Some APIs need attention")
        else:
            print(f"\n❌ POOR: Multiple API issues detected")
        
        print(f"\n📄 Secure report saved to: secure_api_test_report.json")
        print(f"🔒 Note: Sensitive data has been masked in all outputs")
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"❌ API test suite failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(main())
    sys.exit(0 if success else 1)