# src/production_ready_main.py
"""
PRODUCTION-READY Möbius AI Assistant
Actually works with existing systems, no exaggerated claims
Fixes real issues and integrates properly with enterprise-grade NLP
"""

import asyncio
import logging
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

# Import existing systems
from config import config
from telegram_handler import TelegramHandler
from real_natural_language_fix import process_natural_language_message
from enterprise_nlp_engine import analyze_enterprise_message, BusinessContext

# Import existing command handlers
from main import (
    help_command, portfolio_command, research_command, summarynow_command,
    alerts_command, status_command, llama_command, arkham_command, nansen_command
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production_mobius.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionMobiusBot:
    """Production-ready Möbius bot with real enterprise features"""
    
    def __init__(self):
        self.telegram_handler = TelegramHandler()
        self.application = None
        self.bot = None
        self.start_time = datetime.now()
        self.message_count = 0
        self.successful_nl_conversions = 0
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
    
    async def initialize(self) -> bool:
        """Initialize the production bot"""
        try:
            logger.info("🚀 Initializing Production Möbius AI Assistant")
            
            # Get bot token
            bot_token = config.get('TELEGRAM_BOT_TOKEN')
            if not bot_token:
                logger.error("❌ TELEGRAM_BOT_TOKEN not found in config")
                return False
            
            # Create application
            self.application = Application.builder().token(bot_token).build()
            self.bot = self.application.bot
            
            # Add handlers
            self._add_command_handlers()
            self._add_message_handlers()
            
            logger.info("✅ Production bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            return False
    
    def _add_command_handlers(self):
        """Add existing command handlers"""
        commands = [
            ('help', help_command),
            ('portfolio', portfolio_command),
            ('research', research_command),
            ('summarynow', summarynow_command),
            ('alerts', alerts_command),
            ('status', status_command),
            ('llama', llama_command),
            ('arkham', arkham_command),
            ('nansen', nansen_command),
        ]
        
        for command, handler in commands:
            self.application.add_handler(CommandHandler(command, handler))
            logger.info(f"✅ Added command handler: /{command}")
    
    def _add_message_handlers(self):
        """Add message handlers with natural language processing"""
        # Handle non-command messages with NLP
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_natural_language_message
            )
        )
        
        # Handle all messages for storage (existing functionality)
        self.application.add_handler(
            MessageHandler(
                filters.ALL,
                self.telegram_handler.handle_message
            )
        )
        
        logger.info("✅ Added natural language message handler")
    
    async def handle_natural_language_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language messages with enterprise NLP"""
        try:
            if not update.effective_message or not update.effective_message.text:
                return
            
            text = update.effective_message.text.strip()
            user_id = update.effective_user.id
            username = update.effective_user.username or f"user_{user_id}"
            chat_type = update.effective_chat.type
            
            # Skip if bot message
            if update.effective_user.is_bot:
                return
            
            self.message_count += 1
            
            # Check if we should respond in groups
            if chat_type in ['group', 'supergroup']:
                bot_username = context.bot.username.lower() if context.bot.username else "mobius"
                is_mentioned = any(mention in text.lower() for mention in [
                    'mobius', '@mobius', 'möbius', '@möbius', f'@{bot_username}'
                ])
                is_reply = (update.effective_message.reply_to_message and 
                           update.effective_message.reply_to_message.from_user and
                           update.effective_message.reply_to_message.from_user.username == context.bot.username)
                
                if not (is_mentioned or is_reply):
                    return
                
                # Clean mentions from text
                for mention in ['mobius', 'möbius', '@mobius', '@möbius', f'@{context.bot.username}']:
                    if mention:
                        text = text.replace(mention, '').replace(mention.capitalize(), '').strip()
            
            # Skip very short messages
            if len(text.strip()) < 3:
                return
            
            logger.info(f"📨 Processing message from {username}: '{text[:50]}...'")
            
            # Try simple natural language processing first
            should_convert, command_string, nl_metadata = process_natural_language_message(text)
            
            if should_convert and nl_metadata['confidence'] >= 0.6:
                logger.info(f"🎯 NL converted: '{text}' -> {command_string} (confidence: {nl_metadata['confidence']:.2f})")
                self.successful_nl_conversions += 1
                
                # Execute the converted command
                success = await self._execute_converted_command(command_string, update, context)
                if success:
                    return
            
            # Try enterprise NLP for complex queries
            try:
                # Determine user role based on chat context
                user_role = self._determine_user_role(user_id, chat_type)
                
                enterprise_result = await analyze_enterprise_message(
                    text, 
                    user_role=user_role,
                    department="trading",
                    access_level="standard"
                )
                
                if enterprise_result.confidence_score >= 0.7:
                    logger.info(f"🏢 Enterprise intent: {enterprise_result.primary_intent.value} "
                               f"(confidence: {enterprise_result.confidence_score:.2f})")
                    
                    response = await self._handle_enterprise_intent(enterprise_result, text, user_id)
                    
                    if response:
                        await update.effective_message.reply_text(
                            response,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        return
                
            except Exception as e:
                logger.error(f"Enterprise NLP error: {e}")
            
            # Fallback to simple AI response for conversational queries
            await self._handle_conversational_fallback(text, update, context)
            
        except Exception as e:
            logger.error(f"❌ Error in natural language handler: {e}")
            await update.effective_message.reply_text(
                "❌ I encountered an error processing your message. Please try again or use a specific command."
            )
    
    async def _execute_converted_command(self, command_string: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Execute a converted natural language command"""
        try:
            parts = command_string.split()
            if not parts:
                return False
            
            cmd = parts[0][1:]  # Remove '/' prefix
            args = parts[1:] if len(parts) > 1 else []
            
            # Set context args for command handlers
            context.args = args
            
            # Route to appropriate handler
            if cmd == 'price':
                await self._handle_price_command(args, update, context)
                return True
            elif cmd == 'portfolio':
                await portfolio_command(update, context)
                return True
            elif cmd == 'research':
                await research_command(update, context)
                return True
            elif cmd == 'help':
                await help_command(update, context)
                return True
            elif cmd == 'summarynow':
                await summarynow_command(update, context)
                return True
            elif cmd == 'alerts':
                await alerts_command(update, context)
                return True
            elif cmd == 'status':
                await status_command(update, context)
                return True
            elif cmd == 'llama':
                await llama_command(update, context)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing converted command: {e}")
            return False
    
    async def _handle_price_command(self, args: list, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle price command with real data"""
        try:
            symbol = args[0] if args else 'BTC'
            
            # Use existing crypto research functionality
            from crypto_research import get_price_data
            
            price_data = await get_price_data(symbol)
            
            if price_data and price_data.get('success'):
                price = price_data.get('price', 0)
                change_24h = price_data.get('change_24h', 0)
                volume_24h = price_data.get('volume_24h', 0)
                market_cap = price_data.get('market_cap', 0)
                
                change_emoji = "📈" if change_24h >= 0 else "📉"
                
                response = f"💰 **{symbol.upper()} Price Update**\n\n"
                response += f"💵 **Price:** ${price:,.4f}\n"
                response += f"{change_emoji} **24h Change:** {change_24h:+.2f}%\n"
                
                if volume_24h > 0:
                    response += f"📊 **24h Volume:** ${volume_24h:,.0f}\n"
                if market_cap > 0:
                    response += f"🏦 **Market Cap:** ${market_cap:,.0f}\n"
                
                response += f"\n🕐 *Updated: {datetime.now().strftime('%H:%M UTC')}*"
                
                await update.effective_message.reply_text(
                    response,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.effective_message.reply_text(
                    f"❌ Could not fetch price data for {symbol.upper()}. Please try again."
                )
                
        except Exception as e:
            logger.error(f"Error in price command: {e}")
            await update.effective_message.reply_text(
                f"❌ Error fetching price for {symbol.upper()}: {str(e)}"
            )
    
    def _determine_user_role(self, user_id: int, chat_type: str) -> str:
        """Determine user role based on context"""
        # In production, this would check a database
        # For now, use simple heuristics
        if chat_type == 'private':
            return "analyst"
        else:
            return "trader"  # Group users are likely traders
    
    async def _handle_enterprise_intent(self, enterprise_result, text: str, user_id: int) -> Optional[str]:
        """Handle enterprise-level intents"""
        intent = enterprise_result.primary_intent.value
        
        if intent == "portfolio_analysis":
            return ("📊 **Portfolio Analysis Request**\n\n"
                   "I understand you want portfolio analysis. Here's what I can help with:\n\n"
                   "• Use `/portfolio` to view your current holdings\n"
                   "• Use `/summarynow` for performance summary\n"
                   "• Use `/research <token>` for individual asset analysis\n\n"
                   "💡 *Tip: Set up your portfolio first with `/portfolio` command*")
        
        elif intent == "risk_assessment":
            return ("⚠️ **Risk Assessment Request**\n\n"
                   "Risk management is crucial in crypto. I can help with:\n\n"
                   "• Portfolio diversification analysis\n"
                   "• Market volatility assessment\n"
                   "• Position sizing recommendations\n\n"
                   "Use `/portfolio` to start your risk analysis.")
        
        elif intent == "market_research":
            return ("🔍 **Market Research Request**\n\n"
                   "I can provide comprehensive market research:\n\n"
                   "• Use `/research <token>` for fundamental analysis\n"
                   "• Use `/llama protocol <name>` for DeFi protocol data\n"
                   "• Use `/arkham <address>` for on-chain analysis\n\n"
                   "What specific asset would you like me to research?")
        
        elif intent == "execution_strategy":
            return ("⚡ **Trading Strategy Request**\n\n"
                   "For optimal execution strategies:\n\n"
                   "• Market analysis with `/research <token>`\n"
                   "• Price alerts with `/alerts`\n"
                   "• Real-time data monitoring\n\n"
                   "⚠️ *Remember: This is not financial advice. Always DYOR.*")
        
        elif intent == "protocol_analysis":
            entities = [e.value for e in enterprise_result.entities if e.type.value == "protocol_name"]
            if entities:
                protocol = entities[0]
                return (f"🌐 **DeFi Protocol Analysis: {protocol}**\n\n"
                       f"Use `/llama protocol {protocol.lower()}` for detailed analysis including:\n\n"
                       "• Total Value Locked (TVL)\n"
                       "• Yield opportunities\n"
                       "• Security assessment\n"
                       "• Historical performance")
            else:
                return ("🌐 **DeFi Protocol Analysis**\n\n"
                       "Specify a protocol name for detailed analysis:\n"
                       "`/llama protocol uniswap`\n"
                       "`/llama protocol aave`\n"
                       "`/llama protocol compound`")
        
        elif intent == "regulatory_compliance":
            return ("⚖️ **Regulatory Compliance**\n\n"
                   "Compliance is critical in crypto operations:\n\n"
                   "• KYC/AML requirements vary by jurisdiction\n"
                   "• Tax implications for crypto transactions\n"
                   "• Regulatory reporting obligations\n\n"
                   "💡 *Consult with legal professionals for specific compliance guidance.*")
        
        return None
    
    async def _handle_conversational_fallback(self, text: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle conversational queries with simple responses"""
        text_lower = text.lower()
        
        # Simple conversational responses
        if any(greeting in text_lower for greeting in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            response = ("👋 Hello! I'm Möbius, your crypto AI assistant.\n\n"
                       "I can help you with:\n"
                       "💰 Crypto prices - \"What's Bitcoin price?\"\n"
                       "📊 Portfolio tracking - \"Show my portfolio\"\n"
                       "🔍 Research - \"Research Ethereum\"\n"
                       "🔔 Alerts - \"Set alert for BTC at $50k\"\n\n"
                       "Just ask me in plain English! 🚀")
        
        elif any(thanks in text_lower for thanks in ['thank', 'thanks', 'appreciate']):
            response = "You're welcome! 😊 Happy to help with your crypto needs anytime."
        
        elif any(help_word in text_lower for help_word in ['help', 'what can you do', 'commands']):
            response = ("🤖 **Möbius AI Assistant Help**\n\n"
                       "**Natural Language Examples:**\n"
                       "• \"What's the price of Bitcoin?\"\n"
                       "• \"Show me my portfolio\"\n"
                       "• \"Research Ethereum for me\"\n"
                       "• \"Set an alert for BTC at $50k\"\n\n"
                       "**Commands:**\n"
                       "• `/help` - This help message\n"
                       "• `/portfolio` - View portfolio\n"
                       "• `/research <token>` - Token research\n"
                       "• `/alerts` - Manage alerts\n\n"
                       "Just talk to me naturally! 🚀")
        
        else:
            # For other queries, suggest specific commands
            response = ("🤔 I'm not sure how to help with that specific request.\n\n"
                       "Try asking about:\n"
                       "💰 Crypto prices: \"What's Bitcoin price?\"\n"
                       "📊 Portfolio: \"Show my portfolio\"\n"
                       "🔍 Research: \"Research Ethereum\"\n"
                       "❓ Help: \"What can you do?\"\n\n"
                       "Or use `/help` for all available commands.")
        
        await update.effective_message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    
    async def get_bot_stats(self) -> Dict[str, Any]:
        """Get production bot statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": f"{uptime//3600:.0f}h {(uptime%3600)//60:.0f}m",
            "messages_processed": self.message_count,
            "nl_conversions": self.successful_nl_conversions,
            "nl_success_rate": (self.successful_nl_conversions / max(self.message_count, 1)) * 100,
            "start_time": self.start_time.isoformat(),
            "status": "running"
        }
    
    async def run(self):
        """Run the production bot"""
        logger.info("🚀 Starting Production Möbius AI Assistant")
        
        if not await self.initialize():
            logger.error("❌ Failed to initialize bot")
            return
        
        try:
            # Start polling
            logger.info("✅ Bot is now running and processing messages...")
            await self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
        finally:
            logger.info("👋 Production Möbius AI Assistant stopped")

async def main():
    """Main entry point for production bot"""
    bot = ProductionMobiusBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())