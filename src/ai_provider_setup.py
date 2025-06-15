#!/usr/bin/env python3
"""
AI PROVIDER SETUP SYSTEM
========================
Comprehensive AI provider setup with support for multiple providers and automatic model selection.
"""

import logging
from typing import Dict, List, Tuple, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from user_db import set_user_property, get_user_property

logger = logging.getLogger(__name__)

# Conversation states
CHOOSE_PROVIDER, ENTER_API_KEY, CONFIRM_SETUP = range(3)

class AIProviderSetup:
    """Comprehensive AI provider setup system"""
    
    def __init__(self):
        self.providers = {
            'groq': {
                'name': 'Groq',
                'description': 'Fast inference with Llama models',
                'models': {
                    'general': 'meta-llama/Llama-4-Scout-17B-16E-Instruct',
                    'complex': 'DeepSeek-R1-Distill-Llama-70B'
                },
                'context_limit': 32768,
                'api_url': 'https://api.groq.com/openai/v1/chat/completions',
                'signup_url': 'https://console.groq.com/'
            },
            'openai': {
                'name': 'OpenAI',
                'description': 'GPT models with excellent reasoning',
                'models': {
                    'general': 'gpt-4o-mini',
                    'complex': 'gpt-4o'
                },
                'context_limit': 128000,
                'api_url': 'https://api.openai.com/v1/chat/completions',
                'signup_url': 'https://platform.openai.com/'
            },
            'gemini': {
                'name': 'Google Gemini',
                'description': 'Google\'s advanced AI with large context',
                'models': {
                    'experimental': 'gemini-2.5-pro-experimental-03-25',
                    'preview': 'gemini-2.5-pro-preview-06-05',
                    'flash': 'gemini-2.5-flash-preview-05-20',
                    'fallback': 'gemini-2.0-flash'
                },
                'context_limit': 500000,
                'api_url': 'https://generativelanguage.googleapis.com/v1beta/models/',
                'signup_url': 'https://ai.google.dev/'
            },
            'anthropic': {
                'name': 'Anthropic Claude',
                'description': 'Claude models with strong reasoning',
                'models': {
                    'general': 'claude-3-5-haiku-20241022',
                    'complex': 'claude-3-5-sonnet-20241022'
                },
                'context_limit': 200000,
                'api_url': 'https://api.anthropic.com/v1/messages',
                'signup_url': 'https://console.anthropic.com/'
            },
            'openrouter': {
                'name': 'OpenRouter',
                'description': 'Access to multiple AI models',
                'models': {
                    'general': 'meta-llama/llama-3.1-8b-instruct:free',
                    'complex': 'anthropic/claude-3.5-sonnet'
                },
                'context_limit': 32768,
                'api_url': 'https://openrouter.ai/api/v1/chat/completions',
                'signup_url': 'https://openrouter.ai/'
            }
        }
    
    async def start_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start AI provider setup process"""
        keyboard = []
        
        for provider_id, provider_info in self.providers.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"🤖 {provider_info['name']} - {provider_info['description']}", 
                    callback_data=f"setup_provider_{provider_id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="setup_cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🚀 **AI Provider Setup**\n\n"
            "Choose your preferred AI provider:\n\n"
            "**Recommendations:**\n"
            "• **Groq**: Fast and free, great for general use\n"
            "• **Gemini**: Large context window (500k tokens), free tier available\n"
            "• **OpenAI**: Most reliable, requires paid account\n"
            "• **Claude**: Excellent reasoning, requires paid account\n"
            "• **OpenRouter**: Access to many models, pay-per-use\n\n"
            "Select a provider to continue:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return CHOOSE_PROVIDER
    
    async def handle_provider_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle provider selection"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "setup_cancel":
            await query.edit_message_text("❌ AI provider setup cancelled.")
            return ConversationHandler.END
        
        provider_id = query.data.replace("setup_provider_", "")
        context.user_data['selected_provider'] = provider_id
        
        provider_info = self.providers[provider_id]
        
        # Special handling for Gemini free tier
        if provider_id == 'gemini':
            await self.handle_gemini_setup(query, context, provider_info)
        else:
            await self.handle_standard_setup(query, context, provider_info)
        
        return ENTER_API_KEY
    
    async def handle_gemini_setup(self, query, context: ContextTypes.DEFAULT_TYPE, provider_info: Dict):
        """Handle Gemini-specific setup with model selection"""
        keyboard = [
            [InlineKeyboardButton("🆓 Free Tier (Recommended)", callback_data="gemini_free")],
            [InlineKeyboardButton("💳 Paid Tier", callback_data="gemini_paid")],
            [InlineKeyboardButton("🔙 Back", callback_data="setup_back")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🤖 **{provider_info['name']} Setup**\n\n"
            f"{provider_info['description']}\n\n"
            "**Free Tier Models (Recommended):**\n"
            "• Gemini 2.5 Pro Experimental (2 RPM, 170k TPM)\n"
            "• Gemini 2.5 Pro Preview (2 RPM, 150k TPM)\n"
            "• Gemini 2.5 Flash Preview (3 RPM, 150k TPM)\n"
            "• Gemini 2.0 Flash (10 RPM, 750k TPM) - Fallback\n\n"
            "**Context Limit:** 500,000 tokens\n\n"
            "Choose your tier:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_standard_setup(self, query, context: ContextTypes.DEFAULT_TYPE, provider_info: Dict):
        """Handle standard provider setup"""
        await query.edit_message_text(
            f"🤖 **{provider_info['name']} Setup**\n\n"
            f"{provider_info['description']}\n\n"
            f"**Context Limit:** {provider_info['context_limit']:,} tokens\n"
            f"**API URL:** {provider_info['api_url']}\n\n"
            f"**Get your API key:**\n"
            f"1. Visit: {provider_info['signup_url']}\n"
            f"2. Create an account or sign in\n"
            f"3. Generate an API key\n"
            f"4. Send it here (it will be encrypted)\n\n"
            "**Send your API key now:**",
            parse_mode='Markdown'
        )
    
    async def handle_api_key(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle API key input"""
        api_key = update.message.text.strip()
        provider_id = context.user_data.get('selected_provider')
        
        if not provider_id:
            await update.message.reply_text("❌ Setup session expired. Please start again with /setup_ai")
            return ConversationHandler.END
        
        # Validate API key format
        if not self.validate_api_key(provider_id, api_key):
            await update.message.reply_text(
                "❌ Invalid API key format. Please check and try again.\n"
                "Send your API key:"
            )
            return ENTER_API_KEY
        
        # Store API key securely
        user_id = update.effective_user.id
        set_user_property(user_id, f'{provider_id}_api_key', api_key)
        set_user_property(user_id, 'ai_provider', provider_id)
        
        # Set default model based on provider
        if provider_id == 'gemini':
            set_user_property(user_id, 'ai_model', 'gemini-2.5-pro-experimental-03-25')
        elif provider_id == 'groq':
            set_user_property(user_id, 'ai_model', 'meta-llama/Llama-4-Scout-17B-16E-Instruct')
        else:
            default_model = self.providers[provider_id]['models']['general']
            set_user_property(user_id, 'ai_model', default_model)
        
        # Delete the API key message for security
        try:
            await update.message.delete()
        except:
            pass
        
        provider_name = self.providers[provider_id]['name']
        
        await update.message.reply_text(
            f"✅ **{provider_name} Setup Complete!**\n\n"
            f"🔐 API key stored securely\n"
            f"🤖 Provider: {provider_name}\n"
            f"📊 Context limit: {self.providers[provider_id]['context_limit']:,} tokens\n\n"
            "You can now use AI features! Try:\n"
            "• `/ask <question>` - Ask anything\n"
            "• `/research <protocol>` - Research crypto protocols\n"
            "• Natural language queries in chat\n\n"
            "Use `/setup_ai` anytime to change providers.",
            parse_mode='Markdown'
        )
        
        return ConversationHandler.END
    
    def validate_api_key(self, provider_id: str, api_key: str) -> bool:
        """Validate API key format"""
        if not api_key or len(api_key) < 10:
            return False
        
        # Provider-specific validation
        if provider_id == 'openai' and not api_key.startswith('sk-'):
            return False
        elif provider_id == 'anthropic' and not api_key.startswith('sk-ant-'):
            return False
        elif provider_id == 'groq' and not api_key.startswith('gsk_'):
            return False
        
        return True
    
    async def cancel_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel setup process"""
        await update.message.reply_text("❌ AI provider setup cancelled.")
        return ConversationHandler.END

# Global instance
ai_setup = AIProviderSetup()

# Conversation handler
def get_ai_setup_conversation_handler():
    """Get the conversation handler for AI setup"""
    return ConversationHandler(
        entry_points=[CommandHandler('setup_ai', ai_setup.start_setup)],
        states={
            CHOOSE_PROVIDER: [CallbackQueryHandler(ai_setup.handle_provider_choice)],
            ENTER_API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ai_setup.handle_api_key)],
        },
        fallbacks=[CommandHandler('cancel', ai_setup.cancel_setup)],
        conversation_timeout=300  # 5 minutes
    )