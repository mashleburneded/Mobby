# src/ai_provider_manager.py
"""
AI Provider Manager - Easy Provider Switching and Configuration
Supports Groq, Gemini, OpenAI, Anthropic, and other providers with seamless switching
"""

import logging
import asyncio
import json
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from config import config

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Supported AI providers"""
    GROQ = "groq"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"

@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""
    name: str
    api_key_env: str
    default_model: str
    available_models: List[str]
    max_tokens: int
    supports_streaming: bool
    supports_function_calling: bool
    rate_limit_rpm: int
    cost_per_1k_tokens: float
    quality_score: float  # 1-10 rating
    speed_score: float    # 1-10 rating
    reliability_score: float  # 1-10 rating

@dataclass
class ModelCapabilities:
    """Model capabilities and specifications"""
    context_length: int
    supports_vision: bool
    supports_code: bool
    supports_math: bool
    supports_reasoning: bool
    language_support: List[str]
    specializations: List[str]

class AIProviderManager:
    """Manages AI providers and enables easy switching"""
    
    def __init__(self):
        self.providers = self._initialize_providers()
        self.current_provider = AIProvider(config.get('AI_PROVIDER', 'groq'))
        self.fallback_providers = [AIProvider.GROQ, AIProvider.GEMINI, AIProvider.OPENAI]
        self.provider_clients = {}
        self._initialize_clients()
        logger.info(f"AI Provider Manager initialized with {self.current_provider.value} as primary")
    
    def _initialize_providers(self) -> Dict[AIProvider, ProviderConfig]:
        """Initialize provider configurations"""
        return {
            AIProvider.GROQ: ProviderConfig(
                name="Groq",
                api_key_env="GROQ_API_KEY",
                default_model="llama3-70b-8192",
                available_models=[
                    "llama3-70b-8192",
                    "llama3-8b-8192",
                    "mixtral-8x7b-32768",
                    "gemma-7b-it",
                    "gemma2-9b-it"
                ],
                max_tokens=8192,
                supports_streaming=True,
                supports_function_calling=True,
                rate_limit_rpm=30,
                cost_per_1k_tokens=0.0001,
                quality_score=8.5,
                speed_score=9.5,
                reliability_score=8.0
            ),
            
            AIProvider.GEMINI: ProviderConfig(
                name="Google Gemini",
                api_key_env="GEMINI_API_KEY",
                default_model="gemini-2.0-flash-exp",
                available_models=[
                    "gemini-2.0-flash-exp",
                    "gemini-2.0-flash",
                    "gemini-1.5-pro",
                    "gemini-1.5-flash",
                    "gemini-pro",
                    "gemini-pro-vision"
                ],
                max_tokens=32768,
                supports_streaming=True,
                supports_function_calling=True,
                rate_limit_rpm=60,
                cost_per_1k_tokens=0.001,
                quality_score=9.5,
                speed_score=9.5,
                reliability_score=9.5
            ),
            
            AIProvider.OPENAI: ProviderConfig(
                name="OpenAI",
                api_key_env="OPENAI_API_KEY",
                default_model="gpt-4-turbo",
                available_models=[
                    "gpt-4-turbo",
                    "gpt-4",
                    "gpt-3.5-turbo",
                    "gpt-4-vision-preview"
                ],
                max_tokens=4096,
                supports_streaming=True,
                supports_function_calling=True,
                rate_limit_rpm=500,
                cost_per_1k_tokens=0.01,
                quality_score=9.5,
                speed_score=7.0,
                reliability_score=9.5
            ),
            
            AIProvider.ANTHROPIC: ProviderConfig(
                name="Anthropic Claude",
                api_key_env="ANTHROPIC_API_KEY",
                default_model="claude-3-sonnet-20240229",
                available_models=[
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229",
                    "claude-3-haiku-20240307"
                ],
                max_tokens=4096,
                supports_streaming=True,
                supports_function_calling=False,
                rate_limit_rpm=50,
                cost_per_1k_tokens=0.003,
                quality_score=9.2,
                speed_score=7.5,
                reliability_score=9.0
            ),
            
            AIProvider.OPENROUTER: ProviderConfig(
                name="OpenRouter",
                api_key_env="OPENROUTER_API_KEY",
                default_model="anthropic/claude-3-sonnet",
                available_models=[
                    "anthropic/claude-3-opus",
                    "anthropic/claude-3-sonnet",
                    "openai/gpt-4-turbo",
                    "meta-llama/llama-3-70b-instruct",
                    "google/gemini-pro"
                ],
                max_tokens=4096,
                supports_streaming=True,
                supports_function_calling=True,
                rate_limit_rpm=200,
                cost_per_1k_tokens=0.005,
                quality_score=8.8,
                speed_score=8.0,
                reliability_score=8.5
            )
        }
    
    def _initialize_clients(self):
        """Initialize API clients for available providers"""
        for provider in self.providers:
            try:
                self.provider_clients[provider] = self._create_client(provider)
                logger.info(f"Initialized {provider.value} client")
            except Exception as e:
                logger.warning(f"Failed to initialize {provider.value} client: {e}")
    
    def _create_client(self, provider: AIProvider):
        """Create API client for specific provider"""
        config_obj = self.providers[provider]
        api_key = os.getenv(config_obj.api_key_env)
        
        if not api_key:
            raise ValueError(f"API key not found for {provider.value}")
        
        if provider == AIProvider.GROQ:
            try:
                import groq
                return groq.AsyncGroq(api_key=api_key)
            except ImportError:
                raise ImportError("groq package not installed. Run: pip install groq")
        
        elif provider == AIProvider.GEMINI:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                return genai
            except ImportError:
                raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        elif provider == AIProvider.OPENAI:
            try:
                import openai
                return openai.AsyncOpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        
        elif provider == AIProvider.ANTHROPIC:
            try:
                import anthropic
                return anthropic.AsyncAnthropic(api_key=api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        elif provider == AIProvider.OPENROUTER:
            try:
                import openai
                return openai.AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1"
                )
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        
        else:
            raise ValueError(f"Unsupported provider: {provider.value}")
    
    async def generate_text(self, messages: List[Dict[str, str]], 
                          provider: Optional[AIProvider] = None,
                          model: Optional[str] = None,
                          max_tokens: Optional[int] = None,
                          temperature: float = 0.7,
                          stream: bool = False) -> str:
        """Generate text using specified or current provider"""
        
        provider = provider or self.current_provider
        config_obj = self.providers[provider]
        model = model or config_obj.default_model
        max_tokens = max_tokens or config_obj.max_tokens
        
        try:
            if provider not in self.provider_clients:
                self.provider_clients[provider] = self._create_client(provider)
            
            client = self.provider_clients[provider]
            
            if provider == AIProvider.GROQ:
                response = await client.chat.completions.create(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream
                )
                content = response.choices[0].message.content
                return content if content else "I'm having trouble generating a response right now."
            
            elif provider == AIProvider.GEMINI:
                # Convert messages to Gemini format
                gemini_messages = self._convert_to_gemini_format(messages)
                model_obj = client.GenerativeModel(model)
                response = await model_obj.generate_content_async(
                    gemini_messages,
                    generation_config={
                        "max_output_tokens": max_tokens,
                        "temperature": temperature
                    }
                )
                content = response.text
                return content if content else "I'm having trouble generating a response right now."
            
            elif provider == AIProvider.OPENAI:
                response = await client.chat.completions.create(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream
                )
                content = response.choices[0].message.content
                return content if content else "I'm having trouble generating a response right now."
            
            elif provider == AIProvider.ANTHROPIC:
                # Convert messages to Anthropic format
                system_message = ""
                user_messages = []
                
                for msg in messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    else:
                        user_messages.append(msg)
                
                response = await client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_message,
                    messages=user_messages
                )
                content = response.content[0].text
                return content if content else "I'm having trouble generating a response right now."
            
            elif provider == AIProvider.OPENROUTER:
                response = await client.chat.completions.create(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream
                )
                content = response.choices[0].message.content
                return content if content else "I'm having trouble generating a response right now."
            
        except Exception as e:
            logger.error(f"Error with {provider.value}: {e}")
            
            # Try fallback providers
            for fallback in self.fallback_providers:
                if fallback != provider and fallback in self.provider_clients:
                    try:
                        logger.info(f"Trying fallback provider: {fallback.value}")
                        return await self.generate_text(messages, fallback, None, max_tokens, temperature, stream)
                    except Exception as fallback_error:
                        logger.error(f"Fallback {fallback.value} also failed: {fallback_error}")
                        continue
            
            # If all providers fail, return a fallback message
            logger.error(f"All AI providers failed. Last error: {e}")
            return "I'm experiencing technical difficulties with AI services. Please try again in a moment."
    
    def _convert_to_gemini_format(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI format messages to Gemini format"""
        formatted_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                formatted_messages.append(f"System: {content}")
            elif role == "user":
                formatted_messages.append(f"User: {content}")
            elif role == "assistant":
                formatted_messages.append(f"Assistant: {content}")
        
        return "\n\n".join(formatted_messages)
    
    async def get_ai_response(self, text: str, provider: str = None, **kwargs) -> str:
        """Get AI response for a text input (compatibility method)"""
        messages = [{"role": "user", "content": text}]
        provider_enum = AIProvider(provider) if provider else None
        return await self.generate_text(messages, provider_enum, **kwargs)
    
    def switch_provider(self, provider: Union[str, AIProvider], model: Optional[str] = None) -> bool:
        """Switch to a different AI provider"""
        try:
            if isinstance(provider, str):
                provider = AIProvider(provider)
            
            if provider not in self.providers:
                logger.error(f"Unsupported provider: {provider.value}")
                return False
            
            # Test the provider
            if provider not in self.provider_clients:
                self.provider_clients[provider] = self._create_client(provider)
            
            # Update current provider
            old_provider = self.current_provider
            self.current_provider = provider
            
            # Update config
            config.set('AI_PROVIDER', provider.value)
            if model:
                config.set('AI_MODEL', model)
            
            logger.info(f"Switched AI provider from {old_provider.value} to {provider.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch to {provider}: {e}")
            return False
    
    def get_provider_info(self, provider: Optional[AIProvider] = None) -> Dict[str, Any]:
        """Get information about a provider"""
        provider = provider or self.current_provider
        config_obj = self.providers[provider]
        
        return {
            "name": config_obj.name,
            "current": provider == self.current_provider,
            "available": provider in self.provider_clients,
            "default_model": config_obj.default_model,
            "available_models": config_obj.available_models,
            "max_tokens": config_obj.max_tokens,
            "supports_streaming": config_obj.supports_streaming,
            "supports_function_calling": config_obj.supports_function_calling,
            "rate_limit_rpm": config_obj.rate_limit_rpm,
            "cost_per_1k_tokens": config_obj.cost_per_1k_tokens,
            "quality_score": config_obj.quality_score,
            "speed_score": config_obj.speed_score,
            "reliability_score": config_obj.reliability_score
        }
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all available providers with their info"""
        return {
            provider.value: self.get_provider_info(provider)
            for provider in self.providers
        }
    
    def get_best_provider_for_task(self, task_type: str) -> AIProvider:
        """Recommend best provider for specific task type"""
        task_preferences = {
            "speed": lambda p: p.speed_score,
            "quality": lambda p: p.quality_score,
            "reliability": lambda p: p.reliability_score,
            "cost": lambda p: 10 - p.cost_per_1k_tokens * 1000,  # Lower cost = higher score
            "reasoning": lambda p: p.quality_score * 0.7 + p.reliability_score * 0.3,
            "coding": lambda p: p.quality_score if "code" in p.name.lower() else p.quality_score * 0.8,
            "conversation": lambda p: p.speed_score * 0.6 + p.quality_score * 0.4
        }
        
        if task_type not in task_preferences:
            task_type = "quality"  # Default to quality
        
        scoring_func = task_preferences[task_type]
        
        best_provider = max(
            self.providers.keys(),
            key=lambda p: scoring_func(self.providers[p]) if p in self.provider_clients else 0
        )
        
        return best_provider
    
    async def test_provider(self, provider: AIProvider) -> Dict[str, Any]:
        """Test a provider's functionality and performance"""
        import time
        
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello, this is a test!' and nothing else."}
        ]
        
        start_time = time.time()
        try:
            response = await self.generate_text(test_messages, provider)
            end_time = time.time()
            
            return {
                "provider": provider.value,
                "success": True,
                "response_time": end_time - start_time,
                "response": response,
                "error": None
            }
        except Exception as e:
            end_time = time.time()
            return {
                "provider": provider.value,
                "success": False,
                "response_time": end_time - start_time,
                "response": None,
                "error": str(e)
            }
    
    async def test_all_providers(self) -> Dict[str, Dict[str, Any]]:
        """Test all available providers"""
        results = {}
        for provider in self.providers:
            if provider in self.provider_clients:
                results[provider.value] = await self.test_provider(provider)
        return results
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for providers"""
        # This would typically read from a database or log files
        # For now, return mock data
        return {
            "current_provider": self.current_provider.value,
            "total_requests": 1000,
            "provider_breakdown": {
                "groq": {"requests": 600, "success_rate": 0.98, "avg_response_time": 0.5},
                "gemini": {"requests": 300, "success_rate": 0.96, "avg_response_time": 0.8},
                "openai": {"requests": 100, "success_rate": 0.99, "avg_response_time": 1.2}
            },
            "cost_analysis": {
                "total_cost": 15.50,
                "cost_by_provider": {
                    "groq": 2.30,
                    "gemini": 8.20,
                    "openai": 5.00
                }
            }
        }

# Global instance
ai_provider_manager = AIProviderManager()

# Convenience functions
async def generate_ai_response(messages: List[Dict[str, str]], 
                             provider: Optional[str] = None,
                             model: Optional[str] = None,
                             **kwargs) -> str:
    """Generate AI response using current or specified provider"""
    provider_enum = AIProvider(provider) if provider else None
    return await ai_provider_manager.generate_text(messages, provider_enum, model, **kwargs)

def switch_ai_provider(provider: str, model: Optional[str] = None) -> bool:
    """Switch AI provider"""
    return ai_provider_manager.switch_provider(provider, model)

def get_ai_provider_info(provider: Optional[str] = None) -> Dict[str, Any]:
    """Get AI provider information"""
    provider_enum = AIProvider(provider) if provider else None
    return ai_provider_manager.get_provider_info(provider_enum)

def list_ai_providers() -> Dict[str, Dict[str, Any]]:
    """List all AI providers"""
    return ai_provider_manager.list_providers()

async def test_ai_provider(provider: str) -> Dict[str, Any]:
    """Test specific AI provider"""
    return await ai_provider_manager.test_provider(AIProvider(provider))

async def test_all_ai_providers() -> Dict[str, Dict[str, Any]]:
    """Test all AI providers"""
    return await ai_provider_manager.test_all_providers()