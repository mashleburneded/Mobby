#!/usr/bin/env python3
"""
🔄 AI Provider Switcher

Easy switching between AI providers (Groq, Gemini, OpenAI, etc.)
for testing different models and performance comparison.
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from src.ai_provider_manager import AIProvider, ai_provider_manager, test_ai_provider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProviderSwitcher:
    def __init__(self):
        self.config_file = "config/ai_provider_config.json"
        self.ensure_config_exists()
        
    def ensure_config_exists(self):
        """Ensure AI provider config file exists"""
        os.makedirs("config", exist_ok=True)
        
        if not os.path.exists(self.config_file):
            default_config = {
                "current_provider": "groq",
                "providers": {
                    "groq": {
                        "enabled": True,
                        "api_key_env": "GROQ_API_KEY",
                        "default_model": "llama-3.1-70b-versatile",
                        "max_tokens": 4000,
                        "description": "Fast inference with Llama models"
                    },
                    "gemini": {
                        "enabled": True,
                        "api_key_env": "GEMINI_API_KEY",
                        "default_model": "gemini-1.5-flash",
                        "max_tokens": 4000,
                        "description": "Google's Gemini models"
                    },
                    "openai": {
                        "enabled": False,
                        "api_key_env": "OPENAI_API_KEY",
                        "default_model": "gpt-4o-mini",
                        "max_tokens": 4000,
                        "description": "OpenAI GPT models"
                    },
                    "anthropic": {
                        "enabled": False,
                        "api_key_env": "ANTHROPIC_API_KEY",
                        "default_model": "claude-3-haiku-20240307",
                        "max_tokens": 4000,
                        "description": "Anthropic Claude models"
                    }
                },
                "test_scenarios": [
                    "What's the price of Bitcoin?",
                    "Explain DeFi in simple terms",
                    "How do I secure my crypto wallet?",
                    "What are the best yield farming opportunities?",
                    "Analyze the current crypto market trends"
                ]
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"Created default AI provider config: {self.config_file}")
    
    def load_config(self) -> Dict[str, Any]:
        """Load AI provider configuration"""
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def save_config(self, config: Dict[str, Any]):
        """Save AI provider configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all available AI providers"""
        config = self.load_config()
        providers = {}
        
        for provider_name, provider_config in config["providers"].items():
            api_key_env = provider_config["api_key_env"]
            api_key_available = bool(os.getenv(api_key_env))
            
            providers[provider_name] = {
                "enabled": provider_config["enabled"],
                "model": provider_config["default_model"],
                "description": provider_config["description"],
                "api_key_available": api_key_available,
                "status": "✅ Ready" if (provider_config["enabled"] and api_key_available) else 
                         "🔑 Missing API Key" if provider_config["enabled"] else "❌ Disabled"
            }
        
        return providers
    
    def get_current_provider(self) -> str:
        """Get current active provider"""
        config = self.load_config()
        return config["current_provider"]
    
    def switch_provider(self, provider_name: str, model: Optional[str] = None) -> bool:
        """Switch to a different AI provider"""
        config = self.load_config()
        
        if provider_name not in config["providers"]:
            logger.error(f"Unknown provider: {provider_name}")
            return False
        
        provider_config = config["providers"][provider_name]
        
        # Check if provider is enabled
        if not provider_config["enabled"]:
            logger.error(f"Provider {provider_name} is disabled")
            return False
        
        # Check if API key is available
        api_key_env = provider_config["api_key_env"]
        if not os.getenv(api_key_env):
            logger.error(f"API key not found for {provider_name}. Set {api_key_env} environment variable.")
            return False
        
        # Update current provider
        config["current_provider"] = provider_name
        
        # Update model if specified
        if model:
            config["providers"][provider_name]["default_model"] = model
        
        self.save_config(config)
        
        # Switch in the AI provider manager
        from src.ai_provider_manager import switch_ai_provider
        success = switch_ai_provider(provider_name, model)
        
        if success:
            logger.info(f"✅ Switched to {provider_name} with model {config['providers'][provider_name]['default_model']}")
        else:
            logger.error(f"❌ Failed to switch to {provider_name}")
        
        return success
    
    async def test_provider(self, provider_name: str) -> Dict[str, Any]:
        """Test a specific AI provider"""
        config = self.load_config()
        
        if provider_name not in config["providers"]:
            return {"success": False, "error": f"Unknown provider: {provider_name}"}
        
        provider_config = config["providers"][provider_name]
        
        # Check prerequisites
        if not provider_config["enabled"]:
            return {"success": False, "error": f"Provider {provider_name} is disabled"}
        
        api_key_env = provider_config["api_key_env"]
        if not os.getenv(api_key_env):
            return {"success": False, "error": f"API key not found. Set {api_key_env}"}
        
        # Test the provider
        try:
            result = await test_ai_provider(provider_name)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """Test all enabled AI providers"""
        config = self.load_config()
        results = {}
        
        for provider_name, provider_config in config["providers"].items():
            if provider_config["enabled"]:
                logger.info(f"Testing {provider_name}...")
                results[provider_name] = await self.test_provider(provider_name)
            else:
                results[provider_name] = {"success": False, "error": "Provider disabled"}
        
        return results
    
    async def benchmark_providers(self, test_queries: Optional[list] = None) -> Dict[str, Any]:
        """Benchmark all providers with test queries"""
        config = self.load_config()
        test_queries = test_queries or config["test_scenarios"]
        
        results = {}
        original_provider = self.get_current_provider()
        
        for provider_name, provider_config in config["providers"].items():
            if not provider_config["enabled"]:
                continue
                
            api_key_env = provider_config["api_key_env"]
            if not os.getenv(api_key_env):
                continue
            
            logger.info(f"Benchmarking {provider_name}...")
            
            # Switch to this provider
            if not self.switch_provider(provider_name):
                continue
            
            provider_results = {
                "model": provider_config["default_model"],
                "responses": [],
                "avg_response_time": 0,
                "success_rate": 0
            }
            
            total_time = 0
            successful_responses = 0
            
            for query in test_queries:
                try:
                    import time
                    start_time = time.time()
                    
                    # Generate response using current provider
                    from src.ai_provider_manager import generate_ai_response
                    messages = [
                        {"role": "system", "content": "You are a helpful crypto assistant."},
                        {"role": "user", "content": query}
                    ]
                    
                    response = await generate_ai_response(messages)
                    response_time = time.time() - start_time
                    
                    if response and len(response.strip()) > 10:
                        successful_responses += 1
                    
                    provider_results["responses"].append({
                        "query": query,
                        "response": response[:200] + "..." if len(response) > 200 else response,
                        "response_time": response_time,
                        "success": bool(response and len(response.strip()) > 10)
                    })
                    
                    total_time += response_time
                    
                except Exception as e:
                    provider_results["responses"].append({
                        "query": query,
                        "response": f"Error: {e}",
                        "response_time": 0,
                        "success": False
                    })
            
            provider_results["avg_response_time"] = total_time / len(test_queries) if test_queries else 0
            provider_results["success_rate"] = successful_responses / len(test_queries) if test_queries else 0
            
            results[provider_name] = provider_results
        
        # Switch back to original provider
        self.switch_provider(original_provider)
        
        return results
    
    def enable_provider(self, provider_name: str) -> bool:
        """Enable a provider"""
        config = self.load_config()
        
        if provider_name not in config["providers"]:
            logger.error(f"Unknown provider: {provider_name}")
            return False
        
        config["providers"][provider_name]["enabled"] = True
        self.save_config(config)
        
        logger.info(f"✅ Enabled provider: {provider_name}")
        return True
    
    def disable_provider(self, provider_name: str) -> bool:
        """Disable a provider"""
        config = self.load_config()
        
        if provider_name not in config["providers"]:
            logger.error(f"Unknown provider: {provider_name}")
            return False
        
        config["providers"][provider_name]["enabled"] = False
        self.save_config(config)
        
        logger.info(f"❌ Disabled provider: {provider_name}")
        return True
    
    def update_model(self, provider_name: str, model: str) -> bool:
        """Update default model for a provider"""
        config = self.load_config()
        
        if provider_name not in config["providers"]:
            logger.error(f"Unknown provider: {provider_name}")
            return False
        
        config["providers"][provider_name]["default_model"] = model
        self.save_config(config)
        
        logger.info(f"✅ Updated {provider_name} model to: {model}")
        return True

def print_providers_table(providers: Dict[str, Dict[str, Any]]):
    """Print providers in a nice table format"""
    print("\n🤖 AI Providers Status:")
    print("=" * 80)
    print(f"{'Provider':<12} {'Model':<25} {'Status':<20} {'Description'}")
    print("-" * 80)
    
    for name, info in providers.items():
        print(f"{name:<12} {info['model']:<25} {info['status']:<20} {info['description']}")
    print()

async def main():
    """Main CLI interface for AI provider switching"""
    switcher = AIProviderSwitcher()
    
    if len(os.sys.argv) < 2:
        print("🔄 AI Provider Switcher")
        print("=" * 40)
        print("Usage:")
        print("  python ai_provider_switcher.py list                    # List all providers")
        print("  python ai_provider_switcher.py switch <provider>       # Switch provider")
        print("  python ai_provider_switcher.py test <provider>         # Test provider")
        print("  python ai_provider_switcher.py test-all                # Test all providers")
        print("  python ai_provider_switcher.py benchmark               # Benchmark all providers")
        print("  python ai_provider_switcher.py enable <provider>       # Enable provider")
        print("  python ai_provider_switcher.py disable <provider>      # Disable provider")
        print("  python ai_provider_switcher.py current                 # Show current provider")
        print()
        
        providers = switcher.list_providers()
        print_providers_table(providers)
        
        current = switcher.get_current_provider()
        print(f"🎯 Current Provider: {current}")
        return
    
    command = os.sys.argv[1].lower()
    
    if command == "list":
        providers = switcher.list_providers()
        print_providers_table(providers)
        
    elif command == "current":
        current = switcher.get_current_provider()
        print(f"🎯 Current Provider: {current}")
        
    elif command == "switch":
        if len(os.sys.argv) < 3:
            print("❌ Usage: python ai_provider_switcher.py switch <provider>")
            return
        
        provider = os.sys.argv[2]
        model = os.sys.argv[3] if len(os.sys.argv) > 3 else None
        
        success = switcher.switch_provider(provider, model)
        if not success:
            print(f"❌ Failed to switch to {provider}")
        
    elif command == "test":
        if len(os.sys.argv) < 3:
            print("❌ Usage: python ai_provider_switcher.py test <provider>")
            return
        
        provider = os.sys.argv[2]
        result = await switcher.test_provider(provider)
        
        if result["success"]:
            print(f"✅ {provider} test passed")
            if "response_time" in result:
                print(f"⏱️  Response time: {result['response_time']:.2f}s")
        else:
            print(f"❌ {provider} test failed: {result['error']}")
    
    elif command == "test-all":
        print("🧪 Testing all providers...")
        results = await switcher.test_all_providers()
        
        for provider, result in results.items():
            if result["success"]:
                print(f"✅ {provider}: PASS")
            else:
                print(f"❌ {provider}: FAIL - {result['error']}")
    
    elif command == "benchmark":
        print("📊 Benchmarking all providers...")
        results = await switcher.benchmark_providers()
        
        print("\n📈 Benchmark Results:")
        print("=" * 80)
        print(f"{'Provider':<12} {'Model':<25} {'Avg Time':<12} {'Success Rate'}")
        print("-" * 80)
        
        for provider, result in results.items():
            avg_time = f"{result['avg_response_time']:.2f}s"
            success_rate = f"{result['success_rate']:.1%}"
            print(f"{provider:<12} {result['model']:<25} {avg_time:<12} {success_rate}")
    
    elif command == "enable":
        if len(os.sys.argv) < 3:
            print("❌ Usage: python ai_provider_switcher.py enable <provider>")
            return
        
        provider = os.sys.argv[2]
        switcher.enable_provider(provider)
    
    elif command == "disable":
        if len(os.sys.argv) < 3:
            print("❌ Usage: python ai_provider_switcher.py disable <provider>")
            return
        
        provider = os.sys.argv[2]
        switcher.disable_provider(provider)
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())