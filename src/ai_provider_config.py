# src/ai_provider_config.py - Updated AI Provider Configuration
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class AIProviderConfig:
    """Centralized AI provider configuration with fallbacks"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.working_providers = []
        self._test_providers()
    
    def _initialize_providers(self) -> Dict[str, Dict]:
        """Initialize provider configurations"""
        return {
            'groq': {
                'api_key': os.getenv('GROQ_API_KEY'),
                'models': [
                    'llama3-8b-8192',
                    'llama3-70b-8192', 
                    'gemma2-9b-it',
                    'mixtral-8x7b-32768'
                ],
                'default_model': 'llama3-8b-8192',
                'available': False
            },
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'models': [
                    'gpt-3.5-turbo',
                    'gpt-4',
                    'gpt-4-turbo'
                ],
                'default_model': 'gpt-3.5-turbo',
                'available': False
            },
            'gemini': {
                'api_key': os.getenv('GEMINI_API_KEY'),
                'models': [
                    'gemini-pro',
                    'gemini-pro-vision'
                ],
                'default_model': 'gemini-pro',
                'available': False
            },
            'anthropic': {
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                'models': [
                    'claude-3-haiku-20240307',
                    'claude-3-sonnet-20240229',
                    'claude-3-opus-20240229'
                ],
                'default_model': 'claude-3-haiku-20240307',
                'available': False
            }
        }
    
    def _test_providers(self):
        """Test which providers are available"""
        for provider_name, config in self.providers.items():
            if config['api_key'] and len(config['api_key']) > 10:
                try:
                    if provider_name == 'groq':
                        self._test_groq(config)
                    elif provider_name == 'gemini':
                        self._test_gemini(config)
                    # Add other provider tests as needed
                except Exception as e:
                    logger.debug(f"Provider {provider_name} test failed: {e}")
    
    def _test_groq(self, config: Dict):
        """Test Groq provider"""
        try:
            from groq import Groq
            client = Groq(api_key=config['api_key'])
            # Test with a simple call
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": "Hi"}],
                model=config['default_model'],
                max_tokens=5
            )
            if response.choices[0].message.content:
                config['available'] = True
                self.working_providers.append('groq')
                logger.info("✅ Groq provider is working")
        except Exception as e:
            logger.debug(f"Groq test failed: {e}")
    
    def _test_gemini(self, config: Dict):
        """Test Gemini provider"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=config['api_key'])
            model = genai.GenerativeModel(config['default_model'])
            response = model.generate_content("Hi")
            if response.text:
                config['available'] = True
                self.working_providers.append('gemini')
                logger.info("✅ Gemini provider is working")
        except Exception as e:
            logger.debug(f"Gemini test failed: {e}")
    
    def get_working_provider(self) -> Optional[str]:
        """Get first working provider"""
        return self.working_providers[0] if self.working_providers else None
    
    def get_provider_config(self, provider_name: str) -> Optional[Dict]:
        """Get configuration for specific provider"""
        return self.providers.get(provider_name)
    
    def is_provider_available(self, provider_name: str) -> bool:
        """Check if provider is available"""
        return provider_name in self.working_providers

# Global instance
ai_config = AIProviderConfig()
