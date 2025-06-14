# src/ai_provider_switcher.py
"""
AI Provider Switching System for Möbius AI Assistant
Easy switching between different AI providers (Groq, Gemini, OpenAI, etc.)
"""

import logging
import json
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Supported AI providers"""
    GROQ = "groq"
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"

@dataclass
class ProviderConfig:
    """Configuration for an AI provider"""
    name: str
    api_key_env: str
    models: List[str]
    default_model: str
    max_tokens: int
    temperature: float
    supports_streaming: bool
    rate_limit_rpm: int
    cost_per_1k_tokens: float
    strengths: List[str]
    weaknesses: List[str]

class AIProviderSwitcher:
    """Manages switching between different AI providers"""
    
    def __init__(self, config_path: str = "data/ai_provider_config.json"):
        self.config_path = config_path
        self.provider_configs = {}
        self.current_provider = AIProvider.GROQ
        self.fallback_order = [AIProvider.GROQ, AIProvider.GEMINI, AIProvider.OPENAI]
        self.setup_provider_configs()
        self.load_user_preferences()
    
    def setup_provider_configs(self):
        """Setup configurations for all supported providers"""
        
        self.provider_configs = {
            AIProvider.GROQ: ProviderConfig(
                name="Groq",
                api_key_env="GROQ_API_KEY",
                models=["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
                default_model="llama3-70b-8192",
                max_tokens=8192,
                temperature=0.7,
                supports_streaming=True,
                rate_limit_rpm=30,
                cost_per_1k_tokens=0.0001,
                strengths=["Fast inference", "Good for real-time chat", "Cost effective", "Open source models"],
                weaknesses=["Limited model variety", "Newer service", "Rate limits"]
            ),
            
            AIProvider.GEMINI: ProviderConfig(
                name="Google Gemini",
                api_key_env="GEMINI_API_KEY",
                models=["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro"],
                default_model="gemini-pro",
                max_tokens=4096,
                temperature=0.7,
                supports_streaming=True,
                rate_limit_rpm=60,
                cost_per_1k_tokens=0.0005,
                strengths=["Multimodal capabilities", "Good reasoning", "Google integration", "Latest technology"],
                weaknesses=["Higher cost", "Newer API", "Limited availability"]
            ),
            
            AIProvider.OPENAI: ProviderConfig(
                name="OpenAI",
                api_key_env="OPENAI_API_KEY",
                models=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"],
                default_model="gpt-4-turbo",
                max_tokens=4096,
                temperature=0.7,
                supports_streaming=True,
                rate_limit_rpm=500,
                cost_per_1k_tokens=0.01,
                strengths=["Most mature", "Best general performance", "Extensive documentation", "Reliable"],
                weaknesses=["Expensive", "Rate limits", "Closed source"]
            ),
            
            AIProvider.ANTHROPIC: ProviderConfig(
                name="Anthropic Claude",
                api_key_env="ANTHROPIC_API_KEY",
                models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                default_model="claude-3-sonnet",
                max_tokens=4096,
                temperature=0.7,
                supports_streaming=True,
                rate_limit_rpm=50,
                cost_per_1k_tokens=0.008,
                strengths=["Safety focused", "Good reasoning", "Long context", "Helpful responses"],
                weaknesses=["Expensive", "Limited availability", "Conservative responses"]
            ),
            
            AIProvider.OPENROUTER: ProviderConfig(
                name="OpenRouter",
                api_key_env="OPENROUTER_API_KEY",
                models=["openai/gpt-4", "anthropic/claude-3-opus", "meta-llama/llama-3-70b"],
                default_model="openai/gpt-4",
                max_tokens=4096,
                temperature=0.7,
                supports_streaming=True,
                rate_limit_rpm=100,
                cost_per_1k_tokens=0.005,
                strengths=["Multiple models", "Competitive pricing", "Easy switching", "Good API"],
                weaknesses=["Third-party service", "Variable performance", "Dependency on other providers"]
            )
        }
    
    def load_user_preferences(self):
        """Load user preferences for AI provider selection"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    
                    # Load current provider
                    if 'current_provider' in config:
                        try:
                            self.current_provider = AIProvider(config['current_provider'])
                        except ValueError:
                            logger.warning(f"Invalid provider in config: {config['current_provider']}")
                    
                    # Load fallback order
                    if 'fallback_order' in config:
                        try:
                            self.fallback_order = [AIProvider(p) for p in config['fallback_order']]
                        except ValueError as e:
                            logger.warning(f"Invalid fallback order in config: {e}")
                            
        except Exception as e:
            logger.error(f"Error loading AI provider config: {e}")
    
    def save_user_preferences(self):
        """Save user preferences for AI provider selection"""
        try:
            Path(self.config_path).parent.mkdir(exist_ok=True)
            
            config = {
                'current_provider': self.current_provider.value,
                'fallback_order': [p.value for p in self.fallback_order],
                'last_updated': str(datetime.now())
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving AI provider config: {e}")
    
    def switch_provider(self, provider: str) -> bool:
        """Switch to a different AI provider"""
        try:
            new_provider = AIProvider(provider.lower())
            
            # Check if provider is available
            if not self.is_provider_available(new_provider):
                logger.warning(f"Provider {provider} is not available")
                return False
            
            old_provider = self.current_provider
            self.current_provider = new_provider
            
            # Update the actual AI provider manager
            try:
                from ai_provider_manager import ai_provider_manager
                success = ai_provider_manager.switch_provider(new_provider.value)
                
                if success:
                    self.save_user_preferences()
                    logger.info(f"Successfully switched from {old_provider.value} to {new_provider.value}")
                    return True
                else:
                    # Revert on failure
                    self.current_provider = old_provider
                    logger.error(f"Failed to switch to {provider}")
                    return False
                    
            except ImportError:
                logger.warning("AI provider manager not available, only updating switcher config")
                self.save_user_preferences()
                return True
                
        except ValueError:
            logger.error(f"Invalid provider: {provider}")
            return False
    
    def is_provider_available(self, provider: AIProvider) -> bool:
        """Check if a provider is available and configured"""
        try:
            from ai_provider_manager import ai_provider_manager
            return provider.value in ai_provider_manager.providers
        except ImportError:
            # Fallback check - just verify config exists
            return provider in self.provider_configs
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with their status"""
        providers = []
        
        for provider_enum, config in self.provider_configs.items():
            is_available = self.is_provider_available(provider_enum)
            is_current = provider_enum == self.current_provider
            
            providers.append({
                'id': provider_enum.value,
                'name': config.name,
                'available': is_available,
                'current': is_current,
                'models': config.models,
                'default_model': config.default_model,
                'strengths': config.strengths,
                'weaknesses': config.weaknesses,
                'cost_per_1k_tokens': config.cost_per_1k_tokens,
                'rate_limit_rpm': config.rate_limit_rpm
            })
        
        return providers
    
    def get_provider_recommendation(self, use_case: str) -> Dict[str, Any]:
        """Recommend the best provider for a specific use case"""
        
        recommendations = {
            'speed': AIProvider.GROQ,
            'cost': AIProvider.GROQ,
            'quality': AIProvider.OPENAI,
            'reasoning': AIProvider.ANTHROPIC,
            'multimodal': AIProvider.GEMINI,
            'general': AIProvider.OPENAI,
            'development': AIProvider.GROQ,
            'production': AIProvider.OPENAI
        }
        
        recommended = recommendations.get(use_case.lower(), AIProvider.GROQ)
        config = self.provider_configs[recommended]
        
        return {
            'provider': recommended.value,
            'name': config.name,
            'reason': f"Best for {use_case}",
            'available': self.is_provider_available(recommended),
            'strengths': config.strengths,
            'cost_per_1k_tokens': config.cost_per_1k_tokens
        }
    
    def auto_fallback(self) -> bool:
        """Automatically fallback to next available provider"""
        current_index = self.fallback_order.index(self.current_provider) if self.current_provider in self.fallback_order else -1
        
        for i in range(current_index + 1, len(self.fallback_order)):
            provider = self.fallback_order[i]
            if self.is_provider_available(provider):
                logger.info(f"Auto-falling back to {provider.value}")
                return self.switch_provider(provider.value)
        
        # If no fallback available, try any available provider
        for provider in AIProvider:
            if provider != self.current_provider and self.is_provider_available(provider):
                logger.info(f"Emergency fallback to {provider.value}")
                return self.switch_provider(provider.value)
        
        logger.error("No available AI providers for fallback")
        return False
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get current provider status and information"""
        config = self.provider_configs[self.current_provider]
        
        return {
            'current_provider': self.current_provider.value,
            'provider_name': config.name,
            'available': self.is_provider_available(self.current_provider),
            'default_model': config.default_model,
            'max_tokens': config.max_tokens,
            'supports_streaming': config.supports_streaming,
            'rate_limit_rpm': config.rate_limit_rpm,
            'cost_per_1k_tokens': config.cost_per_1k_tokens,
            'fallback_order': [p.value for p in self.fallback_order]
        }
    
    def update_fallback_order(self, new_order: List[str]) -> bool:
        """Update the fallback order for providers"""
        try:
            new_fallback = [AIProvider(p) for p in new_order]
            self.fallback_order = new_fallback
            self.save_user_preferences()
            logger.info(f"Updated fallback order: {new_order}")
            return True
        except ValueError as e:
            logger.error(f"Invalid fallback order: {e}")
            return False

# Global instance for easy access
ai_provider_switcher = AIProviderSwitcher()