# src/enhanced_main.py
"""
Enhanced Main Bot with Industrial-Grade Systems
Integrates all advanced systems: intent analysis, conversation memory, AI provider switching, error recovery
"""

import asyncio
import logging
import sys
import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

# Import all enhanced systems
from advanced_intent_analyzer import analyze_advanced_intent, IntentCategory
from conversation_memory import (
    conversation_memory, ConversationMessage, 
    get_conversation_context, store_conversation_message
)
from intelligent_ai_provider import execute_with_intelligent_fallback, set_user_ai_preference
from error_recovery_system import execute_with_recovery, get_system_health
from enhanced_response_handler import handle_enhanced_response
from telegram_handler import TelegramHandler
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_mobby.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EnhancedMobiusBot:
    """Enhanced Möbius AI Assistant with industrial-grade capabilities"""
    
    def __init__(self):
        self.telegram_handler = None
        self.bot_info = None
        self.start_time = datetime.now()
        self.message_count = 0
        self.error_count = 0
        self.user_sessions = {}
        
    async def initialize(self):
        """Initialize all bot systems"""
        logger.info("🚀 Initializing Enhanced Möbius AI Assistant")
        
        try:
            # Initialize Telegram handler
            self.telegram_handler = TelegramHandler()
            await self.telegram_handler.initialize()
            self.bot_info = await self.telegram_handler.get_bot_info()
            
            logger.info(f"✅ Bot initialized: @{self.bot_info.username}")
            
            # Check system health
            health = await get_system_health()
            logger.info(f"✅ System health: {health.get('overall_health', 'unknown')}")
            
            # Create necessary directories
            os.makedirs('logs', exist_ok=True)
            os.makedirs('data', exist_ok=True)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            return False
    
    async def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message with enhanced systems"""
        try:
            self.message_count += 1
            start_time = datetime.now()
            
            # Extract message information
            user_id = message_data.get('user_id')
            text = message_data.get('text', '')
            message_id = message_data.get('message_id')
            chat_id = message_data.get('chat_id')
            
            logger.info(f"📨 Processing message from user {user_id}: '{text[:50]}...'")
            
            # Get conversation context
            context = await get_conversation_context(user_id)
            
            # Analyze intent with advanced system
            intent_analysis = await analyze_advanced_intent(text, user_id, {
                "conversation_history": context.get("short_term_messages", []),
                "user_preferences": context.get("user_profile", {}),
                "chat_id": chat_id
            })
            
            logger.info(f"🎯 Intent: {intent_analysis.primary_intent.intent_name} "
                       f"(confidence: {intent_analysis.confidence_score:.2f})")
            
            # Handle the response based on intent category
            response = await self._handle_intent_response(intent_analysis, text, user_id, context)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Store conversation message
            conversation_message = ConversationMessage(
                message_id=f"{user_id}_{message_id}_{int(datetime.now().timestamp())}",
                user_id=user_id,
                timestamp=start_time,
                text=text,
                intent=intent_analysis.primary_intent.intent_name,
                entities=[asdict(entity) for entity in intent_analysis.entities],
                sentiment=asdict(intent_analysis.sentiment),
                response_text=response.get('message', ''),
                response_time=processing_time,
                success=response.get('type') != 'error',
                feedback_score=None
            )
            
            await store_conversation_message(conversation_message)
            
            # Add metadata to response
            response.update({
                "processing_time": processing_time,
                "intent": intent_analysis.primary_intent.intent_name,
                "confidence": intent_analysis.confidence_score,
                "message_count": self.message_count
            })
            
            logger.info(f"✅ Response generated in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Error processing message: {e}")
            
            return {
                "type": "error",
                "message": "I encountered an error processing your message. Please try again.",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
            }
    
    async def _handle_intent_response(self, intent_analysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle response based on intent category with priority routing"""
        
        intent_category = intent_analysis.primary_intent.category
        intent_name = intent_analysis.primary_intent.intent_name
        
        # Priority 1: Emergency and Security
        if intent_category in [IntentCategory.EMERGENCY, IntentCategory.SECURITY_ALERT]:
            return await self._handle_emergency_response(intent_analysis, text, user_id)
        
        # Priority 2: Built-in Commands (Price queries, Portfolio, Alerts)
        elif intent_category in [
            IntentCategory.PRICE_QUERY, 
            IntentCategory.PORTFOLIO_MANAGEMENT, 
            IntentCategory.ALERT_MANAGEMENT
        ]:
            return await self._handle_builtin_command(intent_analysis, text, user_id, context)
        
        # Priority 3: Data Analysis (Market, Technical, DeFi)
        elif intent_category in [
            IntentCategory.MARKET_ANALYSIS,
            IntentCategory.TECHNICAL_ANALYSIS,
            IntentCategory.DEFI_OPERATIONS,
            IntentCategory.YIELD_FARMING,
            IntentCategory.RISK_ASSESSMENT
        ]:
            return await self._handle_data_analysis(intent_analysis, text, user_id, context)
        
        # Priority 4: Trading Operations
        elif intent_category == IntentCategory.TRADING_EXECUTION:
            return await self._handle_trading_operations(intent_analysis, text, user_id, context)
        
        # Priority 5: Educational and News
        elif intent_category in [
            IntentCategory.EDUCATION,
            IntentCategory.NEWS_ANALYSIS,
            IntentCategory.SOCIAL_SENTIMENT
        ]:
            return await self._handle_educational_content(intent_analysis, text, user_id, context)
        
        # Priority 6: General Conversation
        else:
            return await self._handle_general_conversation(intent_analysis, text, user_id, context)
    
    async def _handle_emergency_response(self, intent_analysis, text: str, user_id: int) -> Dict[str, Any]:
        """Handle emergency and security alerts"""
        return {
            "type": "emergency",
            "message": "🚨 **Security Alert Detected**\n\n"
                      "If you're experiencing a security issue:\n"
                      "• **Never share your private keys**\n"
                      "• **Disconnect suspicious apps immediately**\n"
                      "• **Contact official support channels**\n"
                      "• **Move funds to a secure wallet**\n\n"
                      "For immediate help, contact the official support of your wallet or exchange.",
            "urgency": "high"
        }
    
    async def _handle_builtin_command(self, intent_analysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle built-in commands with real data"""
        try:
            # Use enhanced response handler for real data
            return await handle_enhanced_response(intent_analysis, text, user_id)
            
        except Exception as e:
            logger.error(f"Error in built-in command handler: {e}")
            return {
                "type": "error",
                "message": "Unable to process your request at the moment. Please try again.",
                "fallback": True
            }
    
    async def _handle_data_analysis(self, intent_analysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle data analysis requests"""
        try:
            # Use enhanced response handler with error recovery
            async def analysis_operation():
                return await handle_enhanced_response(intent_analysis, text, user_id)
            
            result = await execute_with_recovery("data_analysis", analysis_operation)
            
            if result.get("type") == "success":
                return result["data"]
            else:
                return result
                
        except Exception as e:
            logger.error(f"Error in data analysis: {e}")
            return {
                "type": "degraded",
                "message": "Data analysis is temporarily unavailable. Here's what I can tell you:\n\n"
                          "• Check official websites for the latest information\n"
                          "• Use multiple sources to verify data\n"
                          "• Consider market volatility in your decisions",
                "suggestion": "Try asking a simpler question or check back in a few minutes."
            }
    
    async def _handle_trading_operations(self, intent_analysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle trading-related operations"""
        # Get user profile for personalized advice
        user_profile = context.get("user_profile")
        experience_level = getattr(user_profile, 'experience_level', 'beginner') if user_profile else 'beginner'
        
        # Use AI provider for trading advice
        ai_context = {
            "user_id": user_id,
            "experience_level": experience_level,
            "intent": intent_analysis.primary_intent.intent_name,
            "entities": [asdict(e) for e in intent_analysis.entities],
            "urgency": intent_analysis.sentiment.type.value
        }
        
        try:
            ai_response = await execute_with_intelligent_fallback(
                f"Provide trading advice for: {text}. User experience: {experience_level}. "
                f"Include risk warnings and be specific about current market conditions.",
                ai_context,
                user_id
            )
            
            if ai_response.get("type") == "success":
                # Add trading disclaimer
                disclaimer = "\n\n⚠️ **Trading Disclaimer**: This is not financial advice. " \
                           "Always do your own research and never invest more than you can afford to lose."
                
                return {
                    "type": "trading_advice",
                    "message": ai_response.get("message", "") + disclaimer,
                    "provider": ai_response.get("provider_used", "unknown")
                }
            else:
                return ai_response
                
        except Exception as e:
            logger.error(f"Error in trading operations: {e}")
            return {
                "type": "error",
                "message": "Trading advice is temporarily unavailable. Please consult multiple sources and never invest more than you can afford to lose."
            }
    
    async def _handle_educational_content(self, intent_analysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle educational and news content"""
        try:
            # Use AI provider for educational content
            ai_context = {
                "user_id": user_id,
                "intent": intent_analysis.primary_intent.intent_name,
                "educational": True,
                "quality_requirement": 0.8
            }
            
            ai_response = await execute_with_intelligent_fallback(
                f"Provide educational content about: {text}. "
                f"Make it clear, accurate, and appropriate for crypto beginners to advanced users.",
                ai_context,
                user_id
            )
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error in educational content: {e}")
            return {
                "type": "educational",
                "message": "Educational content is temporarily unavailable. "
                          "Please check official documentation or educational resources like:\n"
                          "• CoinGecko Learn\n"
                          "• Binance Academy\n"
                          "• Ethereum.org\n"
                          "• DeFi Pulse"
            }
    
    async def _handle_general_conversation(self, intent_analysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle general conversation"""
        intent_name = intent_analysis.primary_intent.intent_name
        
        # Template responses for common interactions
        if intent_name == "greeting":
            user_profile = context.get("user_profile")
            name = getattr(user_profile, 'username', 'there') if user_profile else 'there'
            
            return {
                "type": "greeting",
                "message": f"👋 Hello {name}! I'm Möbius, your crypto AI assistant.\n\n"
                          "I can help you with:\n"
                          "💰 **Crypto prices** - 'BTC price'\n"
                          "📊 **Portfolio tracking** - 'Show my portfolio'\n"
                          "🔔 **Price alerts** - 'Alert me when BTC hits $50k'\n"
                          "🌾 **DeFi opportunities** - 'Best yields'\n"
                          "📈 **Market analysis** - 'Bitcoin technical analysis'\n\n"
                          "What would you like to know?"
            }
        
        elif intent_name == "gratitude":
            return {
                "type": "gratitude",
                "message": "You're welcome! 😊 I'm here whenever you need crypto insights or assistance."
            }
        
        elif intent_name == "help_request":
            return {
                "type": "help",
                "message": "🤖 **Möbius AI Assistant - Help**\n\n"
                          "**What I can do:**\n\n"
                          "💰 **Crypto Prices**\n"
                          "• `BTC price` - Get Bitcoin price\n"
                          "• `ETH price` - Get Ethereum price\n"
                          "• `Compare BTC vs ETH` - Price comparison\n\n"
                          "📊 **Portfolio Management**\n"
                          "• `Show my portfolio` - Portfolio overview\n"
                          "• `Add 100 USDC to portfolio` - Track holdings\n"
                          "• `Portfolio optimization` - Rebalancing advice\n\n"
                          "🔔 **Price Alerts**\n"
                          "• `Alert me when BTC hits $50k` - Set price alerts\n"
                          "• `Show my alerts` - View active alerts\n\n"
                          "🌾 **DeFi & Yield**\n"
                          "• `Best yield opportunities` - Find high APY\n"
                          "• `Is Aave safe?` - Protocol security\n"
                          "• `Uniswap vs SushiSwap` - Protocol comparison\n\n"
                          "📈 **Market Analysis**\n"
                          "• `Bitcoin technical analysis` - TA insights\n"
                          "• `Market sentiment` - Current market mood\n"
                          "• `Crypto news impact` - News analysis\n\n"
                          "🎓 **Education**\n"
                          "• `What is DeFi?` - Learn crypto concepts\n"
                          "• `How does staking work?` - Educational content\n\n"
                          "Just ask me anything about crypto! 🚀"
            }
        
        else:
            # Use AI for other general conversation
            try:
                ai_context = {
                    "user_id": user_id,
                    "conversational": True,
                    "cost_sensitivity": 0.8  # Use cost-effective provider
                }
                
                ai_response = await execute_with_intelligent_fallback(
                    f"Respond conversationally to: {text}. Keep it friendly and crypto-focused.",
                    ai_context,
                    user_id
                )
                
                return ai_response
                
            except Exception as e:
                logger.error(f"Error in general conversation: {e}")
                return {
                    "type": "fallback",
                    "message": "I'm not sure how to help with that. Could you rephrase your question or ask about crypto prices, DeFi, or portfolio management?"
                }
    
    async def handle_telegram_message(self, update_data: Dict[str, Any]):
        """Handle incoming Telegram message"""
        try:
            message = update_data.get('message', {})
            
            # Extract message data
            message_data = {
                "user_id": message.get('from', {}).get('id'),
                "text": message.get('text', ''),
                "message_id": message.get('message_id'),
                "chat_id": message.get('chat', {}).get('id'),
                "username": message.get('from', {}).get('username', ''),
                "first_name": message.get('from', {}).get('first_name', ''),
                "chat_type": message.get('chat', {}).get('type', 'private')
            }
            
            # Check if message should be processed (mentions, replies, private chat)
            should_process = await self._should_process_message(message_data)
            
            if not should_process:
                return
            
            # Process the message
            response = await self.process_message(message_data)
            
            # Send response via Telegram
            if response and response.get('message'):
                await self.telegram_handler.send_message(
                    chat_id=message_data['chat_id'],
                    text=response['message'],
                    parse_mode='Markdown'
                )
            
        except Exception as e:
            logger.error(f"Error handling Telegram message: {e}")
    
    async def _should_process_message(self, message_data: Dict[str, Any]) -> bool:
        """Determine if message should be processed"""
        chat_type = message_data.get('chat_type', 'private')
        text = message_data.get('text', '').lower()
        
        # Always process private messages
        if chat_type == 'private':
            return True
        
        # In groups, only process if bot is mentioned or replied to
        if chat_type in ['group', 'supergroup']:
            bot_username = self.bot_info.username.lower() if self.bot_info else 'mobius'
            
            # Check for mentions
            if f'@{bot_username}' in text or 'mobius' in text:
                return True
            
            # Check for replies (would need reply_to_message data)
            # This is a simplified check
            return False
        
        return False
    
    async def get_bot_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Get system health
        health = await get_system_health()
        
        return {
            "uptime_seconds": uptime,
            "uptime_formatted": f"{uptime//3600:.0f}h {(uptime%3600)//60:.0f}m",
            "messages_processed": self.message_count,
            "errors_encountered": self.error_count,
            "success_rate": ((self.message_count - self.error_count) / max(self.message_count, 1)) * 100,
            "system_health": health.get("overall_health", "unknown"),
            "start_time": self.start_time.isoformat()
        }
    
    async def run(self):
        """Run the enhanced bot"""
        logger.info("🚀 Starting Enhanced Möbius AI Assistant")
        
        # Initialize systems
        if not await self.initialize():
            logger.error("❌ Failed to initialize bot")
            return
        
        # Start Telegram polling
        try:
            await self.telegram_handler.start_polling(self.handle_telegram_message)
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")
        finally:
            logger.info("👋 Enhanced Möbius AI Assistant stopped")

async def main():
    """Main entry point"""
    bot = EnhancedMobiusBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())