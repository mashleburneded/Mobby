#!/usr/bin/env python3
"""
ENHANCED MESSAGE HANDLER
========================
Improved message handling with better natural language processing and error handling.
"""

import logging
import asyncio
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes

from improved_nlp_processor import process_natural_language_query
from comprehensive_error_handler import handle_errors

logger = logging.getLogger(__name__)

class EnhancedMessageHandler:
    """Enhanced message handler with improved NLP and error handling"""
    
    def __init__(self):
        self.processing_times = {}
    
    @handle_errors(default_return=None)
    async def handle_natural_language_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language queries with improved processing"""
        try:
            if not update.effective_message or not update.effective_message.text:
                return
            
            text = update.effective_message.text.strip()
            chat_type = update.effective_chat.type
            user_id = update.effective_user.id
            
            # Skip bot messages
            if update.effective_user.is_bot:
                return
            
            # Process the query
            query_result = process_natural_language_query(text)
            
            # Only respond if we have high confidence or it's a direct message
            if query_result.confidence < 0.5 and chat_type in ['group', 'supergroup']:
                return
            
            # Show processing message for complex queries
            processing_msg = None
            if query_result.protocol_name:
                processing_msg = await update.message.reply_text(
                    f"🔍 Looking up {query_result.protocol_name}... Please wait."
                )
            
            # Execute the appropriate action
            await self.execute_query_action(update, context, query_result)
            
            # Delete processing message
            if processing_msg:
                try:
                    await processing_msg.delete()
                except:
                    pass  # Ignore if we can't delete
                    
        except Exception as e:
            logger.error(f"Error in natural language query handler: {e}")
            if update.effective_message:
                await update.effective_message.reply_text(
                    "❌ I had trouble processing your request. Please try using a specific command like `/research <protocol>`"
                )
    
    async def execute_query_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query_result):
        """Execute the appropriate action based on query result"""
        try:
            # Import here to avoid circular imports
            from crypto_research import search_protocol, get_protocol_tvl
            
            if not query_result.protocol_name:
                await update.message.reply_text(
                    "🤖 I understand you're looking for information. Try using:\n"
                    "• `/research <protocol>` - Research a specific protocol\n"
                    "• `/help` - See all available commands"
                )
                return
            
            protocol_name = query_result.protocol_name
            
            if query_result.intent == 'tvl_request':
                # Handle TVL requests
                tvl_data = await get_protocol_tvl(protocol_name)
                if tvl_data:
                    await update.message.reply_text(
                        f"📊 **{protocol_name.title()} TVL**\n\n"
                        f"💰 Total Value Locked: ${tvl_data.get('tvl', 'N/A'):,.2f}\n"
                        f"📈 24h Change: {tvl_data.get('change_24h', 'N/A')}%\n"
                        f"🔗 Chain: {tvl_data.get('chain', 'N/A')}"
                    )
                else:
                    await update.message.reply_text(
                        f"❌ Could not find TVL data for '{protocol_name}'. Please check the spelling or try a different protocol."
                    )
            
            elif query_result.intent in ['price_request', 'volume_request', 'research_request']:
                # Handle general research requests
                # Set up context args for research command
                context.args = [protocol_name]
                
                # Import and call research command
                from main_ultimate_fixed import research_command
                await research_command(update, context)
            
            else:
                # Fallback
                await update.message.reply_text(
                    f"🤖 I understand you're asking about {protocol_name}. Try using `/research {protocol_name}` for detailed information."
                )
                
        except Exception as e:
            logger.error(f"Error executing query action: {e}")
            await update.message.reply_text(
                f"❌ Error processing your request for {query_result.protocol_name or 'unknown protocol'}. Please try again or use `/help` for available commands."
            )

# Global instance
enhanced_handler = EnhancedMessageHandler()

async def handle_enhanced_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main enhanced message handler function"""
    await enhanced_handler.handle_natural_language_query(update, context)