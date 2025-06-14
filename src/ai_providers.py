# src/ai_providers.py
import logging
import asyncio
from typing import List, Dict, Optional, Any
from config import config

# Import AI providers with error handling
try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)

async def generate_text(provider: str, api_key: str, messages: list, model: str = None, base_url: str = None) -> str:
    if not api_key: 
        return f"Error: API key for the active provider ('{provider}') is not set. An admin must set it via `/set_api_key`."
    
    logger.info(f"Generating text with provider: {provider}")
    try:
        if provider == 'groq':
            if not GROQ_AVAILABLE:
                return f"Error: Groq provider not available. Install with: pip install groq"
            client = groq.AsyncGroq(api_key=api_key)
            response = await client.chat.completions.create(
                messages=messages, 
                model=model or "llama3-70b-8192"
            )
            return response.choices[0].message.content
            
        elif provider == 'openai' or provider == 'openai_hosted':
            if not OPENAI_AVAILABLE:
                return f"Error: OpenAI provider not available. Install with: pip install openai"
            client = openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
            response = await client.chat.completions.create(
                messages=messages, 
                model=model or "gpt-4-turbo"
            )
            return response.choices[0].message.content
            
        elif provider == 'gemini':
            if not GEMINI_AVAILABLE:
                return f"Error: Gemini provider not available. Install with: pip install google-generativeai"
            genai.configure(api_key=api_key)
            model_instance = genai.GenerativeModel(model or "gemini-1.5-pro-latest")
            system_instruction = next((msg['content'] for msg in messages if msg['role'] == 'system'), None)
            if system_instruction: 
                model_instance.system_instruction = system_instruction
            user_content = [msg['content'] for msg in messages if msg['role'] == 'user']
            response = await model_instance.generate_content_async(user_content)
            return response.text
            
        elif provider == 'anthropic':
            if not ANTHROPIC_AVAILABLE:
                return f"Error: Anthropic provider not available. Install with: pip install anthropic"
            client = anthropic.AsyncAnthropic(api_key=api_key)
            system_prompt = next((msg['content'] for msg in messages if msg['role'] == 'system'), "")
            user_messages = [msg for msg in messages if msg['role'] == 'user']
            response = await client.messages.create(
                model=model or "claude-3-sonnet-20240229", 
                max_tokens=4096,
                system=system_prompt, 
                messages=user_messages
            )
            return response.content[0].text
        else: 
            return f"Error: Unknown AI provider '{provider}'."
            
    except Exception as e:
        logger.error(f"Error with AI provider '{provider}': {e}")
        return f"An exception occurred while communicating with {provider}. Check the API key and model availability."

# Wrapper function for backward compatibility
async def get_ai_response(prompt: str, user_id: int = 0) -> str:
    """
    Wrapper function for backward compatibility with existing code.
    Uses default provider settings.
    """
    try:
        # Check if any AI providers are available
        if not any([GROQ_AVAILABLE, OPENAI_AVAILABLE, GEMINI_AVAILABLE, ANTHROPIC_AVAILABLE]):
            return "AI features unavailable: No AI providers installed. Install with: pip install groq openai google-generativeai anthropic"
        
        # Default to a simple message format
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant for crypto and DeFi analysis."},
            {"role": "user", "content": prompt}
        ]
        
        # Use first available provider as default
        provider = "groq" if GROQ_AVAILABLE else "openai" if OPENAI_AVAILABLE else "gemini" if GEMINI_AVAILABLE else "anthropic"
        api_key = config.get(f'{provider.upper()}_API_KEY', '')
        
        return await generate_text(provider, api_key, messages)
    except Exception as e:
        logger.error(f"Error in get_ai_response wrapper: {e}")
        return f"AI response unavailable: {str(e)}"
