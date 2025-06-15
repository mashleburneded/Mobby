# src/improved_callback_handler.py
"""
Improved callback handler that actually executes commands instead of just showing instructions
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

async def improved_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries and execute actual commands"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    try:
        # Import command functions
        from main import (
            mymentions_command, summarynow_command, help_command, 
            status_command, ask_command, research_command
        )
        
        # Create a mock update object that works with existing command functions
        class MockMessage:
            def __init__(self, chat, user):
                self.chat = chat
                self.user = user
                
            async def reply_text(self, text, **kwargs):
                try:
                    await query.edit_message_text(text, **kwargs)
                except Exception:
                    # If edit fails, send new message
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=text,
                        **kwargs
                    )
        
        class MockUpdate:
            def __init__(self, user, chat):
                self.effective_user = user
                self.effective_chat = chat
                self.message = MockMessage(chat, user)
        
        mock_update = MockUpdate(update.effective_user, query.message.chat)
        
        if data == "cmd_menu":
            from ui_enhancements import SmartKeyboard
            keyboard = SmartKeyboard.create_main_menu()
            await query.edit_message_text(
                "🤖 *Möbius AI Assistant \\- Main Menu*\n\n"
                "Choose an option below:",
                reply_markup=keyboard,
                parse_mode="MarkdownV2"
            )
        
        elif data == "cmd_mymentions":
            # Execute the actual mymentions command
            await mymentions_command(mock_update, context)
        
        elif data == "cmd_summarynow":
            # Execute the actual summarynow command
            await summarynow_command(mock_update, context)
        
        elif data == "cmd_help":
            # Execute the actual help command
            await help_command(mock_update, context)
        
        elif data == "cmd_status":
            # Execute the actual status command
            await status_command(mock_update, context)
        
        elif data == "cmd_ask":
            await query.edit_message_text(
                "🤖 *Ask AI Assistant*\n\n"
                "Please type: `/ask <your question>`\n\n"
                "Example: `/ask What is the current TVL of Uniswap?`\n\n"
                "Or click below for quick questions:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📊 Market Overview", callback_data="ask_market")],
                    [InlineKeyboardButton("🔥 Top Gainers", callback_data="ask_gainers")],
                    [InlineKeyboardButton("📉 Top Losers", callback_data="ask_losers")],
                    [InlineKeyboardButton("⬅️ Back to Menu", callback_data="cmd_menu")]
                ]),
                parse_mode="MarkdownV2"
            )
        
        elif data == "cmd_research":
            # Create research menu
            research_keyboard = [
                [
                    InlineKeyboardButton("📊 DeFiLlama Data", callback_data="research_llama"),
                    InlineKeyboardButton("🔍 Arkham Intel", callback_data="research_arkham")
                ],
                [
                    InlineKeyboardButton("🏷️ Nansen Labels", callback_data="research_nansen"),
                    InlineKeyboardButton("📈 Token Analysis", callback_data="research_token")
                ],
                [
                    InlineKeyboardButton("⬅️ Back to Menu", callback_data="cmd_menu")
                ]
            ]
            await query.edit_message_text(
                "🔬 *DeFi Research Hub*\n\n"
                "Choose your research tool:",
                reply_markup=InlineKeyboardMarkup(research_keyboard),
                parse_mode="MarkdownV2"
            )
        
        elif data == "cmd_topic":
            await query.edit_message_text(
                "🔍 *Topic Search*\n\n"
                "Please type: `/topic <keyword>`\n\n"
                "Example: `/topic bitcoin`\n\n"
                "Or search for popular topics:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🪙 Bitcoin", callback_data="topic_bitcoin")],
                    [InlineKeyboardButton("💎 Ethereum", callback_data="topic_ethereum")],
                    [InlineKeyboardButton("🔥 DeFi", callback_data="topic_defi")],
                    [InlineKeyboardButton("⬅️ Back to Menu", callback_data="cmd_menu")]
                ]),
                parse_mode="MarkdownV2"
            )
        
        elif data == "cmd_whosaid":
            await query.edit_message_text(
                "🔎 *Who Said?*\n\n"
                "Please type: `/whosaid <keyword>`\n\n"
                "Example: `/whosaid ethereum`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Menu", callback_data="cmd_menu")]
                ]),
                parse_mode="MarkdownV2"
            )
        
        elif data == "cmd_social":
            await query.edit_message_text(
                "👥 *Social Trading Hub*\n\n"
                "Connect with other traders and share insights\\.\n\n"
                "Use `/social` commands for trading features\\.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Menu", callback_data="cmd_menu")]
                ]),
                parse_mode="MarkdownV2"
            )
        
        elif data == "cmd_multichain":
            await query.edit_message_text(
                "🌉 *Cross\\-Chain Analytics*\n\n"
                "Analyze assets across multiple blockchains\\.\n\n"
                "Use `/multichain` commands for cross\\-chain features\\.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Menu", callback_data="cmd_menu")]
                ]),
                parse_mode="MarkdownV2"
            )
        
        elif data == "cmd_portfolio":
            await query.edit_message_text(
                "📊 *Portfolio Manager*\n\n"
                "Track and manage your crypto portfolio\\.\n\n"
                "Use `/portfolio` commands for portfolio features\\.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Menu", callback_data="cmd_menu")]
                ]),
                parse_mode="MarkdownV2"
            )
        
        elif data == "cmd_alerts":
            await query.edit_message_text(
                "🔔 *Alert System*\n\n"
                "Set up price and activity alerts\\.\n\n"
                "Use `/alert` commands to manage alerts\\.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Menu", callback_data="cmd_menu")]
                ]),
                parse_mode="MarkdownV2"
            )
        
        # Research sub-commands
        elif data == "research_llama":
            await query.edit_message_text(
                "📊 *DeFiLlama Research*\n\n"
                "Please type: `/llama <type> <slug>`\n\n"
                "Examples:\n"
                "• `/llama protocols` \\- Top protocols\n"
                "• `/llama chains` \\- All chains\n"
                "• `/llama tvl ethereum` \\- Ethereum TVL",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Research", callback_data="cmd_research")]
                ]),
                parse_mode="MarkdownV2"
            )
        
        elif data == "research_arkham":
            await query.edit_message_text(
                "🔍 *Arkham Intelligence*\n\n"
                "Please type: `/arkham <query>`\n\n"
                "Example: `/arkham 0x123...abc`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Research", callback_data="cmd_research")]
                ]),
                parse_mode="MarkdownV2"
            )
        
        elif data == "research_nansen":
            await query.edit_message_text(
                "🏷️ *Nansen Labels*\n\n"
                "Please type: `/nansen <address>`\n\n"
                "Example: `/nansen 0x123...abc`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Research", callback_data="cmd_research")]
                ]),
                parse_mode="MarkdownV2"
            )
        
        # Quick ask commands
        elif data == "ask_market":
            context.args = ["What", "is", "the", "current", "crypto", "market", "overview?"]
            await ask_command(mock_update, context)
        
        elif data == "ask_gainers":
            context.args = ["What", "are", "the", "top", "crypto", "gainers", "today?"]
            await ask_command(mock_update, context)
        
        elif data == "ask_losers":
            context.args = ["What", "are", "the", "top", "crypto", "losers", "today?"]
            await ask_command(mock_update, context)
        
        # Topic quick searches
        elif data == "topic_bitcoin":
            context.args = ["bitcoin"]
            from main import topic_command
            await topic_command(mock_update, context)
        
        elif data == "topic_ethereum":
            context.args = ["ethereum"]
            from main import topic_command
            await topic_command(mock_update, context)
        
        elif data == "topic_defi":
            context.args = ["defi"]
            from main import topic_command
            await topic_command(mock_update, context)
        
        else:
            await query.edit_message_text(
                "❌ Unknown command\\. Please try again\\.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="cmd_menu")]
                ]),
                parse_mode="MarkdownV2"
            )
    
    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        try:
            await query.edit_message_text(
                f"❌ Error: {str(e)[:100]}\\.\\.\\.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Main Menu", callback_data="cmd_menu")]
                ]),
                parse_mode="MarkdownV2"
            )
        except Exception:
            # Last resort - send a new message
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ An error occurred. Please try again."
            )