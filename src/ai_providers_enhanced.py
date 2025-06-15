# src/ai_providers_enhanced.py
"""
Enhanced AI Providers with comprehensive support for multiple providers,
automatic fallbacks, rate limiting, and intelligent model selection.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from config import config
from user_db import get_user_property, set_user_property

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    name: str
    rpm: int  # Requests per minute
    tpm: int  # Tokens per minute
    rpd: int  # Requests per day
    context_limit: int
    is_fallback: bool = False

@dataclass
class ProviderConfig:
    name: str
    models: Dict[str, ModelConfig]
    api_base: Optional[str] = None
    requires_key: bool = True

# Provider configurations
PROVIDER_CONFIGS = {
    'gemini': ProviderConfig(
        name='gemini',
        models={
            'gemini-2.5-pro-experimental-03-25': ModelConfig(
                name='gemini-2.5-pro-experimental-03-25',
                rpm=2, tpm=170000, rpd=750000, context_limit=500000
            ),
            'gemini-2.5-pro-preview-06-05': ModelConfig(
                name='gemini-2.5-pro-preview-06-05',
                rpm=2, tpm=150000, rpd=15, context_limit=500000
            ),
            'gemini-2.5-flash-preview-05-20': ModelConfig(
                name='gemini-2.5-flash-preview-05-20',
                rpm=3, tpm=150000, rpd=15, context_limit=500000
            ),
            'gemini-2.0-flash': ModelConfig(
                name='gemini-2.0-flash',
                rpm=10, tpm=750000, rpd=1000, context_limit=500000,
                is_fallback=True
            )
        }
    ),
    'groq': ProviderConfig(
        name='groq',
        models={
            'meta-llama/Llama-4-Scout-17B-16E-Instruct': ModelConfig(
                name='meta-llama/Llama-4-Scout-17B-16E-Instruct',
                rpm=30, tpm=6000, rpd=14400, context_limit=8192
            ),
            'DeepSeek-R1-Distill-Llama-70B': ModelConfig(
                name='DeepSeek-R1-Distill-Llama-70B',
                rpm=30, tpm=6000, rpd=14400, context_limit=8192
            )
        }
    ),
    'openai': ProviderConfig(
        name='openai',
        models={
            'gpt-4o': ModelConfig(
                name='gpt-4o',
                rpm=500, tpm=30000, rpd=10000, context_limit=128000
            ),
            'gpt-4o-mini': ModelConfig(
                name='gpt-4o-mini',
                rpm=500, tpm=200000, rpd=10000, context_limit=128000
            )
        }
    ),
    'anthropic': ProviderConfig(
        name='anthropic',
        models={
            'claude-3-5-sonnet-20241022': ModelConfig(
                name='claude-3-5-sonnet-20241022',
                rpm=50, tpm=40000, rpd=1000, context_limit=200000
            ),
            'claude-3-5-haiku-20241022': ModelConfig(
                name='claude-3-5-haiku-20241022',
                rpm=50, tpm=50000, rpd=1000, context_limit=200000
            )
        }
    )
}

class RateLimiter:
    """Advanced rate limiter with per-model tracking"""
    
    def __init__(self):
        self.usage_history: Dict[str, List[Tuple[datetime, int]]] = {}
        self.daily_usage: Dict[str, Dict[str, int]] = {}
        self.lock = asyncio.Lock()
    
    async def can_make_request(self, provider: str, model: str, estimated_tokens: int) -> bool:
        """Check if request can be made within rate limits"""
        async with self.lock:
            key = f"{provider}:{model}"
            now = datetime.now()
            
            # Initialize if not exists
            if key not in self.usage_history:
                self.usage_history[key] = []
            if key not in self.daily_usage:
                self.daily_usage[key] = {'requests': 0, 'date': now.date()}
            
            # Reset daily counter if new day
            if self.daily_usage[key]['date'] != now.date():
                self.daily_usage[key] = {'requests': 0, 'date': now.date()}
            
            # Get model config
            if provider not in PROVIDER_CONFIGS:
                # For testing or unknown providers, allow requests
                return True
            
            model_config = PROVIDER_CONFIGS[provider].models.get(model)
            if not model_config:
                # For unknown models, allow requests
                return True
            
            # Clean old entries (older than 1 minute)
            minute_ago = now - timedelta(minutes=1)
            self.usage_history[key] = [
                (timestamp, tokens) for timestamp, tokens in self.usage_history[key]
                if timestamp > minute_ago
            ]
            
            # Check rate limits
            current_rpm = len(self.usage_history[key])
            current_tpm = sum(tokens for _, tokens in self.usage_history[key])
            current_rpd = self.daily_usage[key]['requests']
            
            if (current_rpm >= model_config.rpm or 
                current_tpm + estimated_tokens > model_config.tpm or
                current_rpd >= model_config.rpd):
                return False
            
            # Record usage
            self.usage_history[key].append((now, estimated_tokens))
            self.daily_usage[key]['requests'] += 1
            
            return True
    
    def record_request(self, provider: str, model: str, tokens_used: int):
        """Record a completed request for rate limiting tracking"""
        key = f"{provider}:{model}"
        now = datetime.now()
        
        # Initialize if not exists
        if key not in self.usage_history:
            self.usage_history[key] = []
        if key not in self.daily_usage:
            self.daily_usage[key] = {'requests': 0, 'date': now.date()}
        
        # Reset daily counter if new day
        if self.daily_usage[key]['date'] != now.date():
            self.daily_usage[key] = {'requests': 0, 'date': now.date()}
        
        # Record the request
        self.usage_history[key].append((now, tokens_used))
        self.daily_usage[key]['requests'] += 1
        
        # Clean old entries (older than 1 minute)
        minute_ago = now - timedelta(minutes=1)
        self.usage_history[key] = [
            (timestamp, tokens) for timestamp, tokens in self.usage_history[key]
            if timestamp > minute_ago
        ]
    
    async def get_wait_time(self, provider: str, model: str) -> int:
        """Get estimated wait time in seconds"""
        key = f"{provider}:{model}"
        if key not in self.usage_history:
            return 0
        
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Find oldest entry in current minute
        recent_entries = [
            timestamp for timestamp, _ in self.usage_history[key]
            if timestamp > minute_ago
        ]
        
        if not recent_entries:
            return 0
        
        oldest_entry = min(recent_entries)
        wait_time = 60 - (now - oldest_entry).seconds
        return max(0, wait_time)

class AIProviderManager:
    """Manages multiple AI providers with intelligent fallbacks"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.provider_health: Dict[str, bool] = {}
        self.last_health_check: Dict[str, datetime] = {}
    
    async def get_user_provider_config(self, user_id: int) -> Tuple[str, str, str]:
        """Get user's configured provider, model, and API key"""
        provider = get_user_property(user_id, 'ai_provider') or 'groq'
        model = get_user_property(user_id, 'ai_model')
        api_key = get_user_property(user_id, f'{provider}_api_key')
        
        # Set default model if not configured
        if not model and provider in PROVIDER_CONFIGS:
            default_models = {
                'gemini': 'gemini-2.5-pro-experimental-03-25',
                'groq': 'meta-llama/Llama-4-Scout-17B-16E-Instruct',
                'openai': 'gpt-4o-mini',
                'anthropic': 'claude-3-5-haiku-20241022'
            }
            model = default_models.get(provider)
        
        return provider, model, api_key
    
    def should_use_complex_model(self, query: str) -> bool:
        """Determine if query requires complex reasoning model"""
        complex_indicators = [
            'calculate', 'math', 'equation', 'formula', 'solve',
            'analyze', 'compare', 'evaluate', 'reasoning',
            'logic', 'problem', 'complex', 'detailed'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in complex_indicators)
    
    async def select_optimal_model(self, user_id: int, query: str) -> Tuple[str, str, str]:
        """Select optimal model based on query complexity and availability"""
        provider, configured_model, api_key = await self.get_user_provider_config(user_id)
        
        if not api_key:
            # Fallback to free providers
            provider = 'groq'
            api_key = config.get('GROQ_API_KEY', '')
        
        # For Groq, switch models based on complexity
        if provider == 'groq':
            if self.should_use_complex_model(query):
                model = 'DeepSeek-R1-Distill-Llama-70B'
            else:
                model = 'meta-llama/Llama-4-Scout-17B-16E-Instruct'
        else:
            model = configured_model
        
        return provider, model, api_key
    
    def select_optimal_provider(self, query_complexity: str = "medium") -> str:
        """Select optimal provider based on performance and availability"""
        # Simple provider selection logic
        available_providers = ['groq', 'gemini', 'openai', 'anthropic']
        
        # Check for API keys and return first available
        for provider in available_providers:
            api_key = config.get(f'{provider.upper()}_API_KEY')
            if api_key:
                return provider
        
        # Default fallback
        return 'groq'
    
    async def get_fallback_model(self, provider: str, current_model: str) -> Optional[Tuple[str, str]]:
        """Get fallback model when rate limited"""
        if provider == 'gemini':
            # Try fallback models in order
            fallback_order = [
                'gemini-2.5-pro-preview-06-05',
                'gemini-2.5-flash-preview-05-20',
                'gemini-2.0-flash'
            ]
            
            for fallback_model in fallback_order:
                if fallback_model != current_model:
                    estimated_tokens = 1000  # Conservative estimate
                    if await self.rate_limiter.can_make_request(provider, fallback_model, estimated_tokens):
                        return provider, fallback_model
        
        # Try different provider as ultimate fallback
        if provider != 'groq':
            groq_key = config.get('GROQ_API_KEY')
            if groq_key:
                return 'groq', 'meta-llama/Llama-4-Scout-17B-16E-Instruct'
        
        return None
    
    async def make_ai_request(self, provider: str, model: str, api_key: str, messages: List[Dict]) -> Optional[str]:
        """Make AI request to specific provider"""
        try:
            if provider == 'gemini':
                return await self._call_gemini(model, api_key, messages)
            elif provider == 'groq':
                return await self._call_groq(model, api_key, messages)
            elif provider == 'openai':
                return await self._call_openai(model, api_key, messages)
            elif provider == 'anthropic':
                return await self._call_anthropic(model, api_key, messages)
            else:
                logger.error(f"Unknown provider: {provider}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling {provider} with {model}: {e}")
            return None
    
    async def _call_gemini(self, model: str, api_key: str, messages: List[Dict]) -> Optional[str]:
        """Call Google Gemini API with proper configuration"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=api_key)
            
            # Configure model with proper settings
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            
            # Handle different model configurations
            if "experimental" in model:
                generation_config["temperature"] = 1.0
            elif "flash" in model:
                generation_config["max_output_tokens"] = 4096
            
            model_instance = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config
            )
            
            # Convert messages to Gemini format
            system_instruction = None
            user_content = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_instruction = msg['content']
                elif msg['role'] == 'user':
                    user_content.append(msg['content'])
            
            if system_instruction:
                model_instance = genai.GenerativeModel(
                    model_name=model,
                    generation_config=generation_config,
                    system_instruction=system_instruction
                )
            
            # Generate content
            prompt = "\n".join(user_content)
            response = await model_instance.generate_content_async(prompt)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None
    
    async def _call_groq(self, model: str, api_key: str, messages: List[Dict]) -> Optional[str]:
        """Call Groq API"""
        try:
            import groq
            
            client = groq.AsyncGroq(api_key=api_key)
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=4096,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return None
    
    async def _call_openai(self, model: str, api_key: str, messages: List[Dict]) -> Optional[str]:
        """Call OpenAI API"""
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=api_key)
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=4096,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    async def _call_anthropic(self, model: str, api_key: str, messages: List[Dict]) -> Optional[str]:
        """Call Anthropic Claude API"""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            # Separate system and user messages
            system_prompt = ""
            user_messages = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                else:
                    user_messages.append(msg)
            
            response = await client.messages.create(
                model=model,
                max_tokens=4096,
                system=system_prompt,
                messages=user_messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return None
    
    async def query_with_fallback(self, query: str, user_id: int = 0) -> str:
        """Query AI with automatic fallback to other providers"""
        try:
            # Get user's preferred provider
            provider, model, api_key = await self.get_user_provider_config(user_id)
            
            if not api_key:
                return "❌ No AI provider configured. Use /setup_ai to configure."
            
            # Prepare messages
            messages = [{"role": "user", "content": query}]
            
            # Try primary provider
            response = await self.make_ai_request(provider, model, api_key, messages)
            if response:
                return response
            
            # Try fallback providers
            fallback_providers = ['groq', 'openai', 'gemini', 'anthropic']
            for fallback_provider in fallback_providers:
                if fallback_provider == provider:
                    continue  # Skip the one we already tried
                
                fallback_api_key = get_user_property(user_id, f'{fallback_provider}_api_key')
                if not fallback_api_key:
                    continue
                
                # Get default model for fallback provider
                default_models = {
                    'groq': 'meta-llama/Llama-4-Scout-17B-16E-Instruct',
                    'openai': 'gpt-4o-mini',
                    'gemini': 'gemini-2.0-flash',
                    'anthropic': 'claude-3-5-haiku-20241022'
                }
                fallback_model = default_models.get(fallback_provider)
                
                if fallback_model:
                    response = await self.make_ai_request(fallback_provider, fallback_model, fallback_api_key, messages)
                    if response:
                        logger.info(f"Successfully used fallback provider: {fallback_provider}")
                        return response
            
            return "❌ All AI providers failed. Please check your configuration or try again later."
            
        except Exception as e:
            logger.error(f"Error in query_with_fallback: {e}")
            return f"❌ Error processing AI request: {str(e)}"

# Global instance
ai_manager = AIProviderManager()

async def get_ai_response(query: str, user_id: int = 0) -> str:
    """Main function to get AI response with intelligent provider selection"""
    try:
        # Select optimal model
        provider, model, api_key = await ai_manager.select_optimal_model(user_id, query)
        
        if not api_key:
            return (
                "❌ **AI Provider Not Configured**\n\n"
                "Please set up your AI provider using `/setup_ai` command.\n"
                "Supported providers: Groq, OpenAI, Gemini, Claude"
            )
        
        # Estimate tokens (rough)
        estimated_tokens = len(query.split()) * 1.3 + 500  # Conservative estimate
        
        # Check rate limits
        if not await ai_manager.rate_limiter.can_make_request(provider, model, int(estimated_tokens)):
            # Try fallback
            fallback = await ai_manager.get_fallback_model(provider, model)
            if fallback:
                provider, model = fallback
                logger.info(f"Using fallback model: {provider}:{model}")
            else:
                wait_time = await ai_manager.rate_limiter.get_wait_time(provider, model)
                return (
                    f"⏳ **Rate Limit Reached**\n\n"
                    f"Please wait approximately {wait_time} seconds before trying again.\n"
                    f"Provider: {provider.title()}\n"
                    f"Model: {model}"
                )
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": (
                    "You are Möbius, an advanced AI assistant specialized in cryptocurrency, "
                    "DeFi, and blockchain analysis. Provide accurate, helpful, and concise responses. "
                    "Use markdown formatting for better readability."
                )
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        # Make the request
        response = await ai_manager.make_ai_request(provider, model, api_key, messages)
        
        if response:
            return response
        else:
            return (
                "❌ **AI Request Failed**\n\n"
                "There was an issue processing your request. Please try again.\n"
                f"Provider: {provider.title()}\n"
                f"Model: {model}"
            )
            
    except Exception as e:
        logger.error(f"Error in get_ai_response: {e}")
        return (
            "❌ **Unexpected Error**\n\n"
            "An unexpected error occurred while processing your request. "
            "Please try again or contact support if the issue persists."
        )

async def test_api_key(provider: str, api_key: str) -> bool:
    """Test if API key is valid for the provider"""
    try:
        test_messages = [
            {"role": "user", "content": "Hello, please respond with 'API key is working'"}
        ]
        
        response = await ai_manager.make_ai_request(provider, 
                                                  list(PROVIDER_CONFIGS[provider].models.keys())[0], 
                                                  api_key, 
                                                  test_messages)
        
        return response is not None and "working" in response.lower()
        
    except Exception as e:
        logger.error(f"Error testing API key for {provider}: {e}")
        return False

async def get_provider_status() -> Dict[str, Any]:
    """Get status of all configured providers"""
    status = {}
    
    for provider_name, provider_config in PROVIDER_CONFIGS.items():
        provider_status = {
            "name": provider_name,
            "models": list(provider_config.models.keys()),
            "healthy": True,
            "rate_limits": {}
        }
        
        # Check rate limits for each model
        for model_name, model_config in provider_config.models.items():
            key = f"{provider_name}:{model_name}"
            wait_time = await ai_manager.rate_limiter.get_wait_time(provider_name, model_name)
            
            provider_status["rate_limits"][model_name] = {
                "rpm": model_config.rpm,
                "tpm": model_config.tpm,
                "rpd": model_config.rpd,
                "wait_time": wait_time,
                "available": wait_time == 0
            }
        
        status[provider_name] = provider_status
    
    return status