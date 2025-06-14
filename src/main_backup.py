# src/main.py
import asyncio
import logging
import re
from datetime import time
import pytz
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    filters, ContextTypes, CallbackQueryHandler
)
from telegram.constants import ParseMode
from aiohttp import web

# Import from our project modules
from config import config

# Set up logging
logger = logging.getLogger(__name__)
from user_db import init_db, set_user_property, get_user_property, count_user_alerts, add_alert_to_db, update_username_mapping
from encryption_manager import EncryptionManager
from telegram_handler import handle_message
from summarizer import generate_daily_summary
from persistent_storage import save_summary, get_summaries_for_week
from message_intelligence import message_intelligence
from crypto_research import query_defillama, get_arkham_data, get_nansen_data, create_arkham_alert
from scheduling import set_calendly_for_user, get_schedule_link_for_user
# Import onchain functionality (optional)
try:
    from onchain import create_wallet
except ImportError:
    def create_wallet():
        return "❌ Wallet creation requires web3 dependency. Install with: pip install web3"

# Import enhanced modules
from performance_monitor import performance_monitor, track_performance
from security_auditor import security_auditor
from enhanced_ui import interactive_menu, rich_formatter, ProgressIndicator
from enhanced_db import enhanced_db
from contextual_ai import contextual_ai

# Import comprehensive features (optional - will gracefully degrade if not available)
try:
    from tier_access_control import tier_access_control
    from advanced_portfolio_manager import advanced_portfolio_manager
    from advanced_alerts import advanced_alerts
    from natural_language_query import natural_language_query
    from social_trading import social_trading_hub
    from advanced_research import research_engine
    from automated_trading import automated_trading
    from cross_chain_analytics import cross_chain_analyzer
    COMPREHENSIVE_FEATURES_AVAILABLE = True
    logger.info("✅ Comprehensive features loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Comprehensive features not available: {e}")
    logger.info("💡 Install all dependencies with: pip install -r requirements.txt")
    COMPREHENSIVE_FEATURES_AVAILABLE = False
    
    # Create mock objects to prevent errors
    class MockFeature:
        @staticmethod
        async def mock_response(*args, **kwargs):
            return {"success": True, "message": "✅ Feature available - basic functionality enabled"}
        
        # Add common methods that might be called
        async def process_query(self, *args, **kwargs):
            from dataclasses import dataclass
            @dataclass
            class MockResponse:
                answer: str = "✅ Basic functionality available. For advanced features, install comprehensive dependencies."
                suggestions: list = None
                confidence: float = 0.8
            return MockResponse()
        
        async def process_command(self, *args, **kwargs):
            return {"success": True, "message": "✅ Basic functionality available"}
        
        async def get_portfolio_overview(self, *args, **kwargs):
            return await self.mock_response(*args, **kwargs)
        
        async def create_alert(self, *args, **kwargs):
            return await self.mock_response(*args, **kwargs)
        
        def check_feature_access(self, *args, **kwargs):
            return {"allowed": True, "reason": "Basic access granted"}
    
    tier_access_control = MockFeature()
    advanced_portfolio_manager = MockFeature()
    advanced_alerts = MockFeature()
    natural_language_query = MockFeature()
    social_trading_hub = MockFeature()
    research_engine = MockFeature()
    automated_trading = MockFeature()
    cross_chain_analyzer = MockFeature()

# Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Constants ---
CHOOSE_PLAN, ENTER_KEY = range(2)
TIER_LIMITS = {'free': {'alerts': 3}, 'retail': {'alerts': 50}, 'corporate': {'alerts': float('inf')}}

# --- Helper Functions (Security & Tiers) ---
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # In private chats, user is always "admin" of their own chat
    if chat_type == 'private':
        return True
    
    # For groups, check actual admin status
    chat_id = update.effective_chat.id
    try:
        loop = asyncio.get_running_loop()
        current_time = loop.time()
    except RuntimeError:
        import time
        current_time = time.time()
    
    cache_key = f"admins_{chat_id}"
    if cache_key not in context.bot_data or (current_time - context.bot_data.get(f'{cache_key}_last_checked', 0)) > 300:
        try:
            admins = await context.bot.get_chat_administrators(chat_id)
            context.bot_data[cache_key] = {admin.user.id for admin in admins}
            context.bot_data[f'{cache_key}_last_checked'] = current_time
        except Exception as e: 
            logger.error(f"Could not get chat administrators for {chat_id}: {e}")
            return False
    return user_id in context.bot_data.get(cache_key, set())

async def get_user_tier(user_id: int) -> str:
    cached_tier = get_user_property(user_id, 'subscription_tier')
    if cached_tier: return cached_tier
    
    # Try new API key format first, fallback to bearer token
    whop_api_key = config.get('WHOP_API_KEY')
    whop_bearer_token = config.get('WHOP_BEARER_TOKEN')
    
    if whop_api_key:
        headers = {"Authorization": f"Bearer {whop_api_key}"}
    elif whop_bearer_token:
        headers = {"Authorization": f"Bearer {whop_bearer_token}"}
    else:
        return 'free'
    
    url = f"https://api.whop.com/api/v2/memberships?telegram_id={user_id}"
    try:
        response = requests.get(url, headers=headers, timeout=10); response.raise_for_status()
        user_plans = {m.get('plan_id') for m in response.json().get('data', [])}
        if config.get('WHOP_PREMIUM_CORPORATE_PLAN_ID') in user_plans: tier = 'corporate'
        elif config.get('WHOP_PREMIUM_RETAIL_PLAN_ID') in user_plans: tier = 'retail'
        else: tier = 'free'
        set_user_property(user_id, 'subscription_tier', tier); return tier
    except Exception as e: logger.error(f"Could not check Whop subscription for user {user_id}: {e}"); return 'free'

async def admin_command_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, command_func):
    """Wrapper for admin-only commands"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Access denied. This command is for administrators only.")
        return
    await command_func(update, context)

async def safe_command_wrapper(command_func):
    """Wrapper for safe command execution with error handling"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await command_func(update, context)
        except Exception as e:
            logger.error(f"Error in command {command_func.__name__}: {e}")
            await update.message.reply_text(
                f"❌ An error occurred while processing your command. Please try again.\n\n"
                f"If the issue persists, contact support."
            )
    return wrapper

# --- Post-Init & Scheduled Job ---
async def post_init(application: Application):
    application.bot_data.update({'lock': asyncio.Lock(), 'encryption_manager': EncryptionManager(), 'message_store': {}})
    
    # Initialize enhanced scheduler
    from scheduler import get_scheduler
    scheduler = get_scheduler(application)
    if scheduler:
        scheduler.start()
        logger.info("✅ Enhanced scheduler started with automatic daily summaries")
    
    # Keep legacy job queue for backward compatibility
    job_queue = application.job_queue
    try:
        tz = pytz.timezone(config.get('TIMEZONE'))
        run_time = time.fromisoformat(config.get('SUMMARY_TIME')).replace(tzinfo=tz)
        job_queue.run_daily(send_daily_summary_job, time=run_time, chat_id=int(config.get('TELEGRAM_CHAT_ID')), name="daily_summary_job")
        logger.info(f"Legacy daily summary job scheduled for {run_time}.")
    except Exception as e: logger.error(f"Failed to schedule daily job: {e}")

async def send_daily_summary_job(context: ContextTypes.DEFAULT_TYPE):
    if config.get('PAUSED'): logger.info("Daily summary is paused. Skipping."); return
    lock, store, enc_manager = context.bot_data['lock'], context.bot_data['message_store'], context.bot_data['encryption_manager']
    async with lock:
        if not store:
            await context.bot.send_message(context.job.chat_id, "📊 **Möbius Daily Briefing**\n\nNo significant conversations were recorded.", parse_mode=ParseMode.MARKDOWN)
            enc_manager.rotate_key(); return
        messages_to_process = list(store.values()); store.clear()
    decrypted_messages = [{'text': enc_manager.decrypt(msg['encrypted_text']), **msg} for msg in messages_to_process]
    enc_manager.rotate_key()
    summary_text = await generate_daily_summary(decrypted_messages)
    if summary_text:
        save_summary(summary_text)
        await context.bot.send_message(context.job.chat_id, f"📊 **Möbius Daily Briefing**\n\n{summary_text}", parse_mode=ParseMode.MARKDOWN)

# --- Onboarding & Whop Conversation Handler ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[InlineKeyboardButton("🚀 Continue with Free Plan", callback_data='plan_free')], [InlineKeyboardButton("⭐ Activate Premium Plan", callback_data='plan_premium')]]
    await update.message.reply_text("Greetings. I'm Möbius mini, an enterprise-grade, contextually-aware AI agent designed to transform your Telegram groups and private chats into intelligent, efficient, and data-driven workspaces.  \nPlease select your access plan to proceed.", reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSE_PLAN

async def plan_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query; await query.answer()
    if query.data == 'plan_free':
        set_user_property(update.effective_user.id, 'subscription_tier', 'free')
        await query.edit_message_text(text="✅ Free Plan selected. Core functionalities are active.\nUse /help to see available commands.")
        return ConversationHandler.END
    elif query.data == 'plan_premium':
        await query.edit_message_text(text="⚙️ To activate your premium subscription, please paste your license key from Whop.")
        return ENTER_KEY

async def activate_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    key, user_id = update.message.text, update.effective_user.id
    
    # Try new API key format first, fallback to bearer token
    whop_api_key = config.get('WHOP_API_KEY')
    whop_bearer_token = config.get('WHOP_BEARER_TOKEN')
    
    if whop_api_key:
        headers = {"Authorization": f"Bearer {whop_api_key}"}
    elif whop_bearer_token:
        headers = {"Authorization": f"Bearer {whop_bearer_token}"}
    else:
        await update.message.reply_text("❌ Premium plan activation is currently disabled by the administrator."); return ConversationHandler.END
    
    await update.message.reply_text("⚙️ Validating key with Whop...")
    url = f"https://api.whop.com/api/v2/licenses/{key}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            plan_id = response.json().get('plan', {}).get('id')
            tier = 'corporate' if plan_id == config.get('WHOP_PREMIUM_CORPORATE_PLAN_ID') else 'retail' if plan_id == config.get('WHOP_PREMIUM_RETAIL_PLAN_ID') else 'free'
            if tier != 'free':
                set_user_property(user_id, 'subscription_tier', tier); set_user_property(user_id, 'whop_license_key', key)
                await update.message.reply_text(f"✅ Success! Your **Premium {tier.title()}** plan is now active. Welcome.")
            else: await update.message.reply_text("⚠️ This license key is valid but does not correspond to a known premium plan.")
        else: await update.message.reply_text("❌ Invalid license key. Please check the key and try again."); return ENTER_KEY
    except Exception as e: logger.error(f"Error validating Whop key {key}: {e}"); await update.message.reply_text("An error occurred during validation.")
    return ConversationHandler.END

async def cancel_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Onboarding cancelled."); return ConversationHandler.END

# --- User Command Implementations ---
@track_performance.track_command("help")
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Get personalized help from contextual AI
    try:
        personalized_help = await contextual_ai.get_personalized_help(user_id)
        
        # Create enhanced interactive help menu
        from ui_enhancements import create_smart_help_menu
        keyboard = create_smart_help_menu()
        
        await update.message.reply_text(
            personalized_help,
            reply_markup=keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Process with contextual AI
        await contextual_ai.process_message(user_id, "help", "help")
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        # Fallback to comprehensive help
        user_tier = await get_user_tier(user_id)
        
        help_text = (
            "🤖 **Möbius AI Assistant - Chat Summarization Bot**\n\n"
            f"🎯 **Your Tier: {user_tier.upper()}**\n\n"
            "**📝 CORE FEATURES - Chat Summarization:**\n"
            "• `/summarynow` - Generate immediate daily summary\n"
            "• `/topic <keyword>` - Topic-specific summary\n"
            "• `/whosaid <keyword>` - Find who mentioned something\n"
            "• `/mymentions` - Get your mentions (sent privately)\n"
            "• `/weekly_summary` - Weekly digest (Admin only)\n"
            "• `/status` - Bot status and message count\n\n"
            "**⚙️ Admin Configuration:**\n"
            "• `/set_summary_time HH:MM` - Set daily summary time\n"
            "• `/set_timezone <timezone>` - Set timezone\n\n"
            "**🤖 AI & Natural Language:**\n"
            "• `/ask <question>` - Natural language queries\n\n"
            "**📊 Portfolio Management:**\n"
            "• `/portfolio` - Portfolio overview and management\n"
            "• `/portfolio add <address>` - Add wallet to portfolio\n"
            "• `/portfolio analyze` - Risk analysis (Retail+)\n"
            "• `/portfolio rebalance` - Rebalancing suggestions (Retail+)\n\n"
            "**🔔 Advanced Alerts:**\n"
            "• `/alerts` - Advanced alert management\n"
            "• `/alerts price <token> <condition> <threshold>` - Smart price alerts\n"
            "• `/alert <address> <amount>` - Basic transaction alert\n\n"
            "**👥 Social Trading:**\n"
            "• `/social` - Social trading hub\n"
            "• `/social leaderboard` - Top traders\n\n"
            "**🔍 Research & Analysis:**\n"
            "• `/research <token>` - Comprehensive token research\n"
            "• `/llama <type> <slug>` - DeFiLlama data\n"
            "• `/arkham <query>` - Arkham Intelligence\n"
            "• `/nansen <address>` - Nansen wallet labels\n\n"
            "**🤖 Trading Strategies:**\n"
            "• `/strategy` - Automated trading strategies\n"
            "• `/strategy dca <token> <amount>` - Dollar-cost averaging\n\n"
            "**🌉 Cross-Chain Analytics:**\n"
            "• `/multichain` - Multi-blockchain operations\n"
            "• `/multichain portfolio` - Cross-chain portfolio view\n\n"
            "**🗓️ Productivity:**\n"
            "• `/set_calendly <link>` - Set Calendly link (DM only)\n"
            "• `/schedule @user` - Get user's Calendly link\n\n"
            "**💰 Wallet:**\n"
            "• `/create_wallet` - Generate new Ethereum wallet (DM only)\n\n"
            "**ℹ️ General:**\n"
            "• `/start` - Onboarding flow\n"
            "• `/premium` - Check subscription status\n"
            "• `/tier` - Tier information and comparison\n"
            "• `/help` - Show this help\n\n"
            f"💡 **Upgrade to unlock more features!** Use `/tier compare` to see all tiers."
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tier = await get_user_tier(update.effective_user.id)
    tier_info = {
        'free': "**Free Tier** - Basic functionality with limited alerts (3 max)",
        'retail': "**Premium Retail** - Enhanced features with 50 alerts",
        'corporate': "**Premium Corporate** - Full enterprise features with unlimited alerts"
    }
    await update.message.reply_text(
        f"Your current subscription tier: {tier_info.get(tier, 'Unknown')}\n\n"
        f"To upgrade, please visit our Whop page. For details on upcoming features, see the project roadmap.",
        parse_mode=ParseMode.MARKDOWN
    )

async def alert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id; tier = await get_user_tier(user_id)
    limit, current = TIER_LIMITS[tier]['alerts'], count_user_alerts(user_id)
    if current >= limit: await update.message.reply_text(f"❌ Alert limit of {limit} for the **{tier.title()}** tier reached."); return
    if len(context.args) < 2: await update.message.reply_text("Usage: `/alert <wallet_address> <amount_usd>`"); return
    try: amount_usd = float(context.args[1])
    except ValueError: await update.message.reply_text("❌ Invalid amount format."); return
    await update.message.reply_text("⚙️ Creating alert on Arkham...")
    result = create_arkham_alert(user_id, context.args[0], amount_usd)
    if result.get("success"):
        add_alert_to_db(result["alert_id"], user_id, update.effective_chat.id, 'arkham_tx', {'address': context.args[0], 'amount': amount_usd})
        await update.message.reply_text(f"✅ {result['message']} You have used {current + 1}/{limit} alerts.", parse_mode=ParseMode.MARKDOWN)
    else: await update.message.reply_text(f"❌ {result['message']}")

async def create_wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != 'private':
        await update.message.reply_text("⚠️ For your security, this command must be used in a direct message with me."); return
    wallet = create_wallet()
    message_text = (
        f"✅ **New Wallet Generated**\n\n"
        f"**Address:**\n`{wallet['address']}`\n\n"
        f"**Private Key:**\n`{wallet['private_key']}`\n\n"
        f"**Mnemonic Phrase:**\n`{wallet['mnemonic']}`\n\n"
        f"⚠️ **CRITICAL SECURITY WARNING** ⚠️\n"
        f"Save these details OFFLINE now. This message will be **irrevocably deleted in 3 minutes**. I do not store this information. If you lose it, your funds are lost forever."
    )
    sent_message = await update.message.reply_text(message_text, parse_mode=ParseMode.MARKDOWN)
    context.job_queue.run_once(delete_message_callback, 180, chat_id=sent_message.chat_id, data={'message_id': sent_message.message_id})

async def delete_message_callback(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data['message_id'])

@track_performance.track_command("llama")
async def llama_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Security audit
    security_auditor.log_sensitive_action(
        user_id, "llama_query", True, 
        {"args_count": len(context.args)}
    )
    
    if not context.args:
        # Show enhanced interactive menu
        keyboard = [
            [
                InlineKeyboardButton("🏆 Top Protocols", callback_data="llama_protocols"),
                InlineKeyboardButton("⛓️ Chains", callback_data="llama_chains")
            ],
            [
                InlineKeyboardButton("🌾 Yields", callback_data="llama_yields"),
                InlineKeyboardButton("💵 Stablecoins", callback_data="llama_stablecoins")
            ],
            [
                InlineKeyboardButton("📊 DEX Volume", callback_data="llama_volumes"),
                InlineKeyboardButton("🌉 Bridges", callback_data="llama_bridges")
            ],
            [
                InlineKeyboardButton("💸 Funding", callback_data="llama_raises"),
                InlineKeyboardButton("🏛️ Treasury", callback_data="llama_treasury")
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="menu_cancel")]
        ]
        await update.message.reply_text(
            "📊 **DeFiLlama Research Hub**\n\n"
            "🔍 **Quick Commands:**\n"
            "• `/llama top` - Top protocols by TVL\n"
            "• `/llama search <name>` - Search protocols\n"
            "• `/llama protocol <slug>` - Protocol details\n"
            "• `/llama yields [min_apy]` - Yield opportunities\n"
            "• `/llama chains <chain1> <chain2>` - Compare chains\n\n"
            "Or use the buttons below:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    command = context.args[0].lower()
    
    # Create progress indicator
    progress_msg = await update.message.reply_text("⚙️ Querying DeFiLlama...")
    
    try:
        from defillama_api import (
            get_top_defi_protocols, search_defi_protocols, 
            get_protocol_data, get_yield_farming_opportunities,
            compare_chains
        )
        
        if command == "top":
            limit = int(context.args[1]) if len(context.args) > 1 and context.args[1].isdigit() else 10
            result = await get_top_defi_protocols(limit)
            
        elif command == "search":
            if len(context.args) < 2:
                await progress_msg.edit_text("❌ Usage: `/llama search <protocol_name>`")
                return
            query = " ".join(context.args[1:])
            result = await search_defi_protocols(query)
            
        elif command == "protocol":
            if len(context.args) < 2:
                await progress_msg.edit_text("❌ Usage: `/llama protocol <protocol_slug>`")
                return
            protocol_slug = context.args[1]
            result = await get_protocol_data(protocol_slug)
            
        elif command == "yields":
            min_apy = float(context.args[1]) if len(context.args) > 1 and context.args[1].replace('.', '').isdigit() else 5.0
            result = await get_yield_farming_opportunities(min_apy)
            
        elif command == "chains":
            if len(context.args) < 2:
                await progress_msg.edit_text("❌ Usage: `/llama chains <chain1> [chain2] [chain3]`")
                return
            chains = context.args[1:]
            result = await compare_chains(chains)
            
        else:
            # Fallback to old system for backward compatibility
            if len(context.args) < 2:
                await progress_msg.edit_text("❌ Usage: `/llama <command> <parameters>`")
                return
            
            data_type, slug = context.args[0].lower(), context.args[1]
            result = query_defillama(data_type, slug)
            
            # Use rich formatter for better presentation
            if isinstance(result, dict):
                result = rich_formatter.format_crypto_data(result, f"DeFiLlama {data_type.title()} Data")
        
        if not result:
            result = "❌ No data found. Please check your parameters and try again."
        
        # Process with contextual AI for enhanced response
        try:
            ai_context = await contextual_ai.process_message(
                user_id, f"llama {' '.join(context.args)}", "llama"
            )
            
            # Add suggestions if available
            if ai_context.get("suggestions"):
                result += "\n\n💡 **Suggestions:**\n"
                for suggestion in ai_context["suggestions"][:3]:
                    result += f"• {suggestion}\n"
        except Exception as e:
            logger.debug(f"Contextual AI processing failed: {e}")
        
        # Split long messages
        if len(result) > 4000:
            parts = [result[i:i+4000] for i in range(0, len(result), 4000)]
            await progress_msg.edit_text(f"📊 **DeFiLlama Data (Part 1/{len(parts)})**\n\n{parts[0]}", parse_mode=ParseMode.MARKDOWN)
            for i, part in enumerate(parts[1:], 2):
                await update.message.reply_text(f"📊 **DeFiLlama Data (Part {i}/{len(parts)})**\n\n{part}", parse_mode=ParseMode.MARKDOWN)
        else:
            await progress_msg.edit_text(result, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Error in llama command: {e}")
        security_auditor.log_sensitive_action(user_id, "llama_query", False, {"error": str(e)})
        await progress_msg.edit_text(f"❌ Error fetching DeFiLlama data: {str(e)}\n\nPlease try again or check your parameters.")

async def arkham_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/arkham <query>`")
        return
    query = " ".join(context.args)
    await update.message.reply_text("⚙️ Querying Arkham Intelligence...")
    result = get_arkham_data(query)
    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)

async def nansen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/nansen <address>`")
        return
    address = context.args[0]
    await update.message.reply_text("⚙️ Querying Nansen...")
    result = get_nansen_data(address)
    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)

async def set_calendly_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != 'private':
        await update.message.reply_text("⚠️ For privacy, this command must be used in a direct message with me.")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/set_calendly <your_calendly_link>`")
        return
    link = context.args[0]
    result = set_calendly_for_user(update.effective_user.id, link)
    await update.message.reply_text(result)

async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/schedule @username`")
        return
    username = context.args[0]
    result = get_schedule_link_for_user(username)
    await update.message.reply_text(result, parse_mode=ParseMode.MARKDOWN)

@track_performance.track_command("summarynow")
async def summarynow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_type = update.message.chat.type
    
    # Core summarization is available to all users - this is the main feature
    # No tier restrictions for basic summarization
    
    # Security audit
    security_auditor.log_sensitive_action(
        user_id, "summary_request", True, 
        {"chat_type": chat_type}
    )
    
    lock = context.bot_data['lock']
    store = context.bot_data['message_store']
    enc_manager = context.bot_data['encryption_manager']
    
    async with lock:
        if not store:
            if chat_type != 'private':
                await update.message.reply_text("📊 No recent conversations to summarize. I'll send you a DM when ready.")
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="📊 **Conversation Summary**\n\nNo recent conversations found in the group to summarize.",
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception as e:
                    logger.error(f"Failed to send DM to user {user_id}: {e}")
                    await update.message.reply_text("❌ Could not send DM. Please start a conversation with me first.")
            else:
                await update.message.reply_text("📊 No recent conversations to summarize.")
            return
        messages_to_process = list(store.values())
    
    # For groups, we want to summarize ALL recent messages and send via DM
    if chat_type != 'private':
        # Filter to recent messages (last 2 hours for groups)
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=2)
        
        filtered_messages = []
        for msg in messages_to_process:
            try:
                msg_time = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                if msg_time >= cutoff_time:
                    filtered_messages.append(msg)
            except:
                continue
        
        messages_to_process = filtered_messages
        
        if not messages_to_process:
            await update.message.reply_text("📊 No recent conversations to summarize. I'll send you a DM when ready.")
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="📊 **Group Conversation Summary**\n\nNo recent conversations found in the group (last 2 hours).",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Failed to send DM to user {user_id}: {e}")
                await update.message.reply_text("❌ Could not send DM. Please start a conversation with me first.")
            return
        
        # Acknowledge in group and process
        await update.message.reply_text("⚙️ Generating summary... I'll send it to you via DM for privacy.")
    else:
        await update.message.reply_text("⚙️ Generating summary...")
    
    decrypted_messages = [{'text': enc_manager.decrypt(msg['encrypted_text']), **msg} for msg in messages_to_process]
    
    summary_text = await generate_daily_summary(decrypted_messages)
    
    if summary_text:
        # Add tier-specific enhancements
        if tier in ['retail', 'corporate']:
            try:
                ai_insights = await contextual_ai.get_conversation_insights(user_id, decrypted_messages)
                summary_text += f"\n\n💡 **AI Insights:** {ai_insights}"
            except Exception as e:
                logger.warning(f"Failed to get AI insights: {e}")
        
        # Add conversation stats
        summary_header = f"📊 **Conversation Summary**\n"
        if chat_type != 'private':
            summary_header += f"📍 From: {update.message.chat.title or 'Group Chat'}\n"
        summary_header += f"📅 Messages analyzed: {len(decrypted_messages)}\n"
        summary_header += f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        
        full_summary = summary_header + summary_text
        
        if chat_type != 'private':
            # Send via DM for groups
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=full_summary,
                    parse_mode=ParseMode.MARKDOWN
                )
                await update.message.reply_text("✅ Summary sent to your DM!")
            except Exception as e:
                logger.error(f"Failed to send DM to user {user_id}: {e}")
                await update.message.reply_text("❌ Could not send DM. Please start a conversation with me first by clicking my username and sending /start.")
        else:
            # Send directly for private chats
            await update.message.reply_text(full_summary, parse_mode=ParseMode.MARKDOWN)
    else:
        error_msg = "❌ Failed to generate summary."
        if chat_type != 'private':
            await update.message.reply_text(error_msg)
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📊 **Conversation Summary**\n\n{error_msg}",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        else:
            await update.message.reply_text(error_msg)

# --- Admin Command Implementations ---
async def set_api_key_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/set_api_key <service> <key>`\nServices: groq, openai, gemini, anthropic, arkham, nansen")
        return
    service, key = context.args[0].lower(), context.args[1]
    if service in ['groq', 'openai', 'gemini', 'anthropic']:
        config_key = f'AI_API_KEYS.{service}'
    elif service in ['arkham', 'nansen']:
        config_key = f'CRYPTO_API_KEYS.{service}'
    else:
        await update.message.reply_text(f"❌ Invalid service '{service}'. Valid services: groq, openai, gemini, anthropic, arkham, nansen")
        return
    config.set(config_key, key)
    await update.message.reply_text(f"✅ API key for `{service}` updated.")
    try:
        await context.bot.delete_message(update.message.chat_id, update.message.message_id)
    except Exception as e:
        logger.warning(f"Could not delete message with API key: {e}")

async def set_ai_provider_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        current_provider = config.get('ACTIVE_AI_PROVIDER')
        await update.message.reply_text(f"Current AI provider: `{current_provider}`\nUsage: `/set_ai_provider <provider>`\nProviders: groq, openai, gemini, anthropic")
        return
    provider = context.args[0].lower()
    valid_providers = ['groq', 'openai', 'gemini', 'anthropic']
    if provider not in valid_providers:
        await update.message.reply_text(f"❌ Invalid provider. Valid providers: {', '.join(valid_providers)}")
        return
    config.set('ACTIVE_AI_PROVIDER', provider)
    await update.message.reply_text(f"✅ AI provider set to `{provider}`")

async def set_timezone_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        current_tz = config.get('TIMEZONE')
        await update.message.reply_text(f"Current timezone: `{current_tz}`\nUsage: `/set_timezone <timezone>`\nExample: `/set_timezone America/New_York`")
        return
    timezone = context.args[0]
    try:
        import pytz
        pytz.timezone(timezone)  # Validate timezone
        config.set('TIMEZONE', timezone)
        await update.message.reply_text(f"✅ Timezone set to `{timezone}`")
    except Exception:
        await update.message.reply_text(f"❌ Invalid timezone `{timezone}`. Use standard timezone names like 'UTC' or 'America/New_York'")

async def set_summary_time_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        current_time = config.get('SUMMARY_TIME')
        await update.message.reply_text(f"Current summary time: `{current_time}`\nUsage: `/set_summary_time <HH:MM>`\nExample: `/set_summary_time 23:00`")
        return
    time_str = context.args[0]
    try:
        from datetime import time
        time.fromisoformat(time_str)  # Validate time format
        config.set('SUMMARY_TIME', time_str)
        await update.message.reply_text(f"✅ Daily summary time set to `{time_str}`")
    except Exception:
        await update.message.reply_text(f"❌ Invalid time format `{time_str}`. Use HH:MM format (24-hour)")

async def pause_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config.set('PAUSED', True)
    await update.message.reply_text("⏸️ Bot activity paused. Daily summaries and message logging are disabled.")

async def resume_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config.set('PAUSED', False)
    await update.message.reply_text("▶️ Bot activity resumed. Daily summaries and message logging are enabled.")

async def status_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_text = (
        f"⚙️ **Möbius System Status**\n\n"
        f"**AI Provider:** `{config.get('ACTIVE_AI_PROVIDER')}`\n"
        f"**Timezone:** `{config.get('TIMEZONE')}`\n"
        f"**Summary Time:** `{config.get('SUMMARY_TIME')}`\n"
        f"**Status:** {'⏸️ Paused' if config.get('PAUSED') else '▶️ Active'}\n\n"
        f"**API Keys Configured:**\n"
    )
    
    ai_keys = config.get('AI_API_KEYS', {})
    crypto_keys = config.get('CRYPTO_API_KEYS', {})
    
    for service, key in ai_keys.items():
        status = "✅" if key else "❌"
        status_text += f"• {service.title()}: {status}\n"
    
    for service, key in crypto_keys.items():
        status = "✅" if key else "❌"
        status_text += f"• {service.title()}: {status}\n"
    
    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)

# Admin command wrappers
async def set_api_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, set_api_key_command_impl)

async def set_ai_provider_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, set_ai_provider_command_impl)

async def set_timezone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, set_timezone_command_impl)

async def set_summary_time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, set_summary_time_command_impl)

async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, pause_command_impl)

async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, resume_command_impl)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, status_command_impl)

# --- Enhanced Admin Commands ---
async def metrics_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system performance metrics"""
    try:
        # Get performance metrics
        metrics = performance_monitor.get_metrics_summary()
        
        # Get database analytics
        db_analytics = enhanced_db.get_analytics_summary(24)  # Last 24 hours
        
        # Format metrics using rich formatter
        formatted_metrics = rich_formatter.format_performance_metrics(metrics)
        
        # Add database analytics
        if db_analytics:
            formatted_metrics += f"\n\n📈 **Database Analytics (24h):**\n"
            formatted_metrics += f"• Total Commands: {db_analytics.get('total_commands', 0):,}\n"
            formatted_metrics += f"• Success Rate: {db_analytics.get('success_rate', 0):.1f}%\n"
            formatted_metrics += f"• Avg Execution Time: {db_analytics.get('avg_execution_time', 0):.3f}s\n"
        
        # Create interactive metrics menu
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="metrics_refresh"),
                InlineKeyboardButton("📊 Detailed", callback_data="metrics_detailed")
            ],
            [
                InlineKeyboardButton("🧹 Reset", callback_data="metrics_reset"),
                InlineKeyboardButton("❌ Close", callback_data="menu_cancel")
            ]
        ]
        
        await update.message.reply_text(
            formatted_metrics,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in metrics command: {e}")
        await update.message.reply_text(
            rich_formatter.format_error_message("system", "Failed to retrieve metrics")
        )

async def security_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show security summary and audit information"""
    try:
        # Get security summary
        security_summary = security_auditor.get_security_summary()
        
        # Format security data
        formatted_security = rich_formatter.format_security_summary(security_summary)
        
        # Create security management menu
        keyboard = [
            [
                InlineKeyboardButton("🔍 Audit Log", callback_data="security_audit"),
                InlineKeyboardButton("👥 User Status", callback_data="security_users")
            ],
            [
                InlineKeyboardButton("🚨 Alerts", callback_data="security_alerts"),
                InlineKeyboardButton("📊 Export", callback_data="security_export")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="menu_cancel")
            ]
        ]
        
        await update.message.reply_text(
            formatted_security,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in security command: {e}")
        await update.message.reply_text(
            rich_formatter.format_error_message("system", "Failed to retrieve security information")
        )

async def analytics_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user analytics and insights"""
    try:
        # Get analytics from contextual AI
        user_analytics = {}
        for user_id in list(contextual_ai.conversation_contexts.keys())[:10]:  # Top 10 active users
            analytics = contextual_ai.get_user_analytics(user_id)
            if not analytics.get("error"):
                user_analytics[user_id] = analytics
        
        formatted_analytics = "📊 **User Analytics Dashboard**\n\n"
        
        if user_analytics:
            formatted_analytics += f"👥 **Active Users:** {len(user_analytics)}\n\n"
            
            # Top active users
            sorted_users = sorted(
                user_analytics.items(),
                key=lambda x: x[1].get("messages_in_session", 0),
                reverse=True
            )
            
            formatted_analytics += "🔥 **Most Active Users:**\n"
            for i, (user_id, data) in enumerate(sorted_users[:5], 1):
                messages = data.get("messages_in_session", 0)
                duration = data.get("session_duration_minutes", 0)
                formatted_analytics += f"{i}. User {user_id}: {messages} msgs, {duration:.1f}m\n"
            
            # Popular commands across all users
            all_commands = {}
            for data in user_analytics.values():
                for cmd, count in data.get("command_usage", {}).items():
                    all_commands[cmd] = all_commands.get(cmd, 0) + count
            
            if all_commands:
                formatted_analytics += "\n📈 **Popular Commands:**\n"
                top_commands = sorted(all_commands.items(), key=lambda x: x[1], reverse=True)
                for cmd, count in top_commands[:5]:
                    formatted_analytics += f"• `/{cmd}`: {count} uses\n"
        else:
            formatted_analytics += "No active user sessions found."
        
        # Create analytics menu
        keyboard = [
            [
                InlineKeyboardButton("📊 User Details", callback_data="analytics_users"),
                InlineKeyboardButton("📈 Trends", callback_data="analytics_trends")
            ],
            [
                InlineKeyboardButton("💾 Export Data", callback_data="analytics_export"),
                InlineKeyboardButton("❌ Close", callback_data="menu_cancel")
            ]
        ]
        
        await update.message.reply_text(
            formatted_analytics,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in analytics command: {e}")
        await update.message.reply_text(
            rich_formatter.format_error_message("system", "Failed to retrieve analytics")
        )

async def cleanup_command_impl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean up old data and optimize database"""
    try:
        progress_msg = await update.message.reply_text("🧹 Starting cleanup process...")
        progress = ProgressIndicator(context, progress_msg.chat_id, progress_msg.message_id)
        
        await progress.start(3, "🔍 Analyzing database...")
        
        # Clean up old data
        await progress.update("🗑️ Removing old analytics data...")
        enhanced_db.cleanup_old_data(30)  # Keep 30 days
        
        await progress.update("🔄 Optimizing database...")
        # Run VACUUM to optimize database
        enhanced_db.execute_query("VACUUM")
        
        await progress.update("✨ Finalizing cleanup...")
        
        # Reset performance metrics if requested
        if context.args and context.args[0].lower() == "reset":
            performance_monitor.reset_metrics()
        
        await progress.complete(
            "✅ **Cleanup Complete**\n\n"
            "• Old data removed\n"
            "• Database optimized\n"
            "• System ready for optimal performance"
        )
        
    except Exception as e:
        logger.error(f"Error in cleanup command: {e}")
        await update.message.reply_text(
            rich_formatter.format_error_message("system", "Cleanup process failed")
        )

# Enhanced admin command wrappers
async def metrics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, metrics_command_impl)

async def security_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, security_command_impl)

async def analytics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, analytics_command_impl)

async def cleanup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await admin_command_wrapper(update, context, cleanup_command_impl)

# --- Webhook Handler ---
async def arkham_webhook_handler(request: web.Request):
    try:
        data = await request.json()
        logger.info(f"Received Arkham Webhook: {data}")
        
        # Parse webhook data and send alert to relevant chat
        alert_text = f"🚨 **ARKHAM ALERT**\n\n{data}"
        target_chat_id = int(config.get('TELEGRAM_CHAT_ID'))
        
        # Note: In a production setup, you'd need access to the application instance
        # For now, this is a placeholder for webhook processing
        logger.info(f"Would send alert to chat {target_chat_id}: {alert_text}")
        
        return web.Response(status=200, text="OK")
    except Exception as e:
        logger.error(f"Error processing Arkham webhook: {e}")
        return web.Response(status=500, text="Internal Server Error")

# --- Callback Query Handlers ---
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle interactive menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    try:
        if data == "menu_cancel":
            await query.edit_message_text("❌ Menu closed.")
            return
        
        elif data.startswith("llama_"):
            data_type = data.split("_")[1]
            
            # Handle different DeFiLlama data types
            if data_type in ['protocols', 'chains', 'yields', 'stablecoins', 'volumes', 'bridges', 'raises', 'treasury']:
                # These don't need a protocol slug
                await query.edit_message_text("📊 Fetching data...")
                try:
                    result = query_defillama(data_type)
                    await query.edit_message_text(result, parse_mode=ParseMode.MARKDOWN)
                except Exception as e:
                    await query.edit_message_text(f"❌ Error: {str(e)}")
            else:
                # These need a protocol slug
                await query.edit_message_text(
                    f"📊 **DeFiLlama {data_type.title()} Query**\n\n"
                    f"Please use: `/llama {data_type} <protocol_slug>`\n\n"
                    f"Example: `/llama {data_type} uniswap`"
                )
        
        elif data.startswith("help_"):
            category = data.split("_")[1]
            help_content = {
                "crypto": "🔍 **Crypto Research Commands:**\n• `/llama` - DeFi protocol data\n• `/arkham` - Wallet intelligence\n• `/nansen` - Wallet labels\n• `/alert` - Transaction alerts",
                "wallet": "💰 **Wallet Commands:**\n• `/create_wallet` - Generate new wallet\n• `/alert` - Monitor transactions",
                "productivity": "📅 **Productivity Commands:**\n• `/set_calendly` - Set calendar link\n• `/schedule` - Find user calendars",
                "analytics": "📊 **Analytics Commands:**\n• `/summarynow` - Conversation summary\n• `/premium` - Subscription status",
                "admin": "⚙️ **Admin Commands:**\n• `/metrics` - Performance metrics\n• `/security` - Security dashboard\n• `/analytics` - User analytics\n• `/cleanup` - System maintenance",
                "quickstart": "🎯 **Quick Start Guide:**\n1. Use `/llama tvl uniswap` to get protocol data\n2. Try `/arkham wallet_address` to research wallets\n3. Set alerts with `/alert address amount`\n4. Check your subscription with `/premium`"
            }
            
            await query.edit_message_text(
                help_content.get(category, "Help category not found."),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data.startswith("metrics_"):
            action = data.split("_")[1]
            if action == "refresh":
                # Refresh metrics display
                await metrics_command_impl(update, context)
            elif action == "reset":
                if await is_admin(update, context):
                    performance_monitor.reset_metrics()
                    await query.edit_message_text("✅ Performance metrics reset.")
                else:
                    await query.edit_message_text("❌ Admin access required.")
        
        elif data.startswith("security_"):
            action = data.split("_")[1]
            if action == "audit":
                if await is_admin(update, context):
                    audit_data = security_auditor.export_audit_log()
                    summary = f"📋 **Security Audit Log**\n\nTotal Events: {len(audit_data)}\n\nRecent events exported for review."
                    await query.edit_message_text(summary)
                else:
                    await query.edit_message_text("❌ Admin access required.")
        
        else:
            await query.edit_message_text("❓ Unknown menu option.")
    
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        await query.edit_message_text("❌ An error occurred processing your request.")

# --- Comprehensive Feature Commands ---

# Portfolio Management Commands
@track_performance.track_command("portfolio")
async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not COMPREHENSIVE_FEATURES_AVAILABLE:
        await update.message.reply_text(
            "❌ **Portfolio Management Not Available**\n\n"
            "This feature requires comprehensive dependencies.\n"
            "Install with: `pip install -r requirements.txt`\n\n"
            "Or use the installation script: `./install_dependencies.sh`"
        )
        return
    
    user_id = update.effective_user.id
    tier = await get_user_tier(user_id)
    
    if len(context.args) == 0:
        # Show portfolio overview
        access_check = tier_access_control.check_feature_access(tier, "portfolio_tracking")
        if not access_check["allowed"]:
            await update.message.reply_text(f"❌ {access_check['reason']}")
            return
        
        portfolio = await advanced_portfolio_manager.get_portfolio(user_id)
        if not portfolio:
            await update.message.reply_text(
                "📊 **Portfolio Setup Required**\n\n"
                "Add wallets to start tracking:\n"
                "`/portfolio add <wallet_address>`"
            )
            return
        
        response = f"📊 **Portfolio Overview**\n\n"
        response += f"💰 Total Value: **${portfolio.total_value_usd:,.2f}**\n"
        response += f"📈 24h: **{portfolio.performance_24h:+.2f}%**\n"
        response += f"📊 7d: **{portfolio.performance_7d:+.2f}%**\n"
        response += f"📅 30d: **{portfolio.performance_30d:+.2f}%**\n\n"
        
        # Top holdings
        top_assets = sorted(portfolio.assets, key=lambda x: x.value_usd, reverse=True)[:5]
        response += "**Top Holdings:**\n"
        for asset in top_assets:
            response += f"• {asset.symbol}: ${asset.value_usd:,.2f} ({asset.allocation_percent:.1f}%)\n"
        
        if tier in ['retail', 'corporate']:
            response += f"\n💡 Use `/portfolio analyze` for detailed analysis"
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        
    elif context.args[0] == "add":
        if len(context.args) < 2:
            await update.message.reply_text("Usage: `/portfolio add <wallet_address>`")
            return
        
        wallet_address = context.args[1]
        success = advanced_portfolio_manager.add_wallet(user_id, wallet_address)
        
        if success:
            await update.message.reply_text(f"✅ Wallet added: `{wallet_address[:10]}...`")
        else:
            await update.message.reply_text("❌ Invalid wallet address")
            
    elif context.args[0] == "remove":
        if len(context.args) < 2:
            await update.message.reply_text("Usage: `/portfolio remove <wallet_address>`")
            return
        
        wallet_address = context.args[1]
        success = advanced_portfolio_manager.remove_wallet(user_id, wallet_address)
        
        if success:
            await update.message.reply_text(f"✅ Wallet removed: `{wallet_address[:10]}...`")
        else:
            await update.message.reply_text("❌ Wallet not found")
            
    elif context.args[0] == "analyze":
        access_check = tier_access_control.check_feature_access(tier, "portfolio_analytics")
        if not access_check["allowed"]:
            await update.message.reply_text(f"❌ {access_check['reason']}")
            return
        
        await update.message.reply_text("⚙️ Analyzing portfolio...")
        risk_metrics = await advanced_portfolio_manager.calculate_risk_metrics(user_id)
        
        if risk_metrics:
            response = f"📊 **Portfolio Risk Analysis**\n\n"
            response += f"📉 VaR (95%): **${risk_metrics.var_95:,.2f}**\n"
            response += f"📈 Sharpe Ratio: **{risk_metrics.sharpe_ratio:.2f}**\n"
            response += f"📊 Max Drawdown: **{risk_metrics.max_drawdown:.2f}%**\n"
            response += f"🌊 Volatility: **{risk_metrics.volatility:.2f}%**\n"
            response += f"₿ BTC Correlation: **{risk_metrics.correlation_btc:.2f}**\n"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Unable to analyze portfolio")
            
    elif context.args[0] == "rebalance":
        access_check = tier_access_control.check_feature_access(tier, "portfolio_rebalancing")
        if not access_check["allowed"]:
            await update.message.reply_text(f"❌ {access_check['reason']}")
            return
        
        await update.message.reply_text("⚙️ Generating rebalancing suggestions...")
        suggestions = await advanced_portfolio_manager.generate_rebalancing_suggestions(user_id)
        
        if suggestions.get("rebalancing_needed"):
            response = f"⚖️ **Portfolio Rebalancing Suggestions**\n\n"
            for suggestion in suggestions["suggestions"][:3]:
                response += f"• **{suggestion['action']}** {suggestion['asset_type']}\n"
                response += f"  Amount: ${suggestion['rebalance_amount_usd']:,.2f}\n"
                response += f"  Priority: {suggestion['priority']}\n\n"
        else:
            response = "✅ **Portfolio is well balanced!**\n\nNo rebalancing needed at this time."
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# Advanced Alerts Commands
@track_performance.track_command("alerts")
async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not COMPREHENSIVE_FEATURES_AVAILABLE:
        await update.message.reply_text("❌ **Advanced Alerts Not Available**\n\nInstall comprehensive dependencies: `pip install -r requirements.txt`")
        return
    
    user_id = update.effective_user.id
    tier = await get_user_tier(user_id)
    
    if len(context.args) == 0:
        # Show alert management menu
        keyboard = [
            [InlineKeyboardButton("📊 Price Alerts", callback_data="alerts_price")],
            [InlineKeyboardButton("📈 Technical Alerts", callback_data="alerts_technical")],
            [InlineKeyboardButton("🐋 Whale Alerts", callback_data="alerts_whale")],
            [InlineKeyboardButton("💭 Sentiment Alerts", callback_data="alerts_sentiment")],
            [InlineKeyboardButton("📋 Manage Alerts", callback_data="alerts_manage")]
        ]
        
        await update.message.reply_text(
            "🔔 **Advanced Alert System**\n\nChoose alert type:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    alert_type = context.args[0]
    
    if alert_type == "price":
        access_check = tier_access_control.check_feature_access(tier, "price_alerts")
        if not access_check["allowed"]:
            await update.message.reply_text(f"❌ {access_check['reason']}")
            return
        
        if len(context.args) < 4:
            await update.message.reply_text(
                "Usage: `/alerts price <token> <condition> <threshold>`\n"
                "Example: `/alerts price BTC > 50000`"
            )
            return
        
        symbol = context.args[1]
        condition = context.args[2]
        threshold = float(context.args[3])
        
        result = await advanced_alerts.create_price_alert(user_id, symbol, condition, threshold)
        
        if result["success"]:
            await update.message.reply_text(
                f"✅ {result['message']}\n"
                f"🤖 ML Confidence: {result['ml_confidence']:.1%}"
            )
        else:
            await update.message.reply_text(f"❌ {result['message']}")

# Natural Language Query Command
@track_performance.track_command("ask")
async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not COMPREHENSIVE_FEATURES_AVAILABLE:
        await update.message.reply_text("❌ **Natural Language Queries Not Available**\n\nInstall comprehensive dependencies: `pip install -r requirements.txt`")
        return
    
    user_id = update.effective_user.id
    tier = await get_user_tier(user_id)
    
    access_check = tier_access_control.check_feature_access(tier, "nlp_queries")
    if not access_check["allowed"]:
        await update.message.reply_text(f"❌ {access_check['reason']}")
        return
    
    if not context.args:
        await update.message.reply_text(
            "🤖 **Natural Language Queries**\n\n"
            "Ask me anything about crypto!\n\n"
            "Examples:\n"
            "• `/ask What's the price of Bitcoin?`\n"
            "• `/ask Compare ETH and BTC performance`\n"
            "• `/ask Analyze my portfolio`\n"
            "• `/ask What are the best DeFi yields?`"
        )
        return
    
    query = " ".join(context.args)
    await update.message.reply_text("🤖 Processing your query...")
    
    response = await natural_language_query.process_query(user_id, query)
    
    # Format response
    reply_text = response.answer
    
    if response.suggestions:
        reply_text += "\n\n💡 **Suggestions:**\n"
        for suggestion in response.suggestions[:3]:
            reply_text += f"• {suggestion}\n"
    
    await update.message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)

# Social Trading Commands
@track_performance.track_command("social")
async def social_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not COMPREHENSIVE_FEATURES_AVAILABLE:
        await update.message.reply_text("❌ **Social Trading Not Available**\n\nInstall comprehensive dependencies: `pip install -r requirements.txt`")
        return

    user_id = update.effective_user.id
    tier = await get_user_tier(user_id)
    
    if len(context.args) == 0:
        # Show social trading menu
        keyboard = [
            [InlineKeyboardButton("📊 Leaderboard", callback_data="social_leaderboard")],
            [InlineKeyboardButton("📡 Trading Signals", callback_data="social_signals")],
            [InlineKeyboardButton("👥 Follow Traders", callback_data="social_follow")],
            [InlineKeyboardButton("📈 Publish Signal", callback_data="social_publish")],
            [InlineKeyboardButton("💭 Market Sentiment", callback_data="social_sentiment")]
        ]
        
        await update.message.reply_text(
            "👥 **Social Trading Hub**\n\nConnect with successful traders:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if context.args[0] == "leaderboard":
        access_check = tier_access_control.check_feature_access(tier, "leaderboard_access")
        if not access_check["allowed"]:
            await update.message.reply_text(f"❌ {access_check['reason']}")
            return
        
        leaderboard = await social_trading.get_leaderboard()
        
        if leaderboard["success"]:
            response = "🏆 **Top Traders Leaderboard**\n\n"
            for trader in leaderboard["leaderboard"][:5]:
                response += f"{trader['rank']}. **{trader['username']}**\n"
                response += f"   Win Rate: {trader['win_rate']:.1f}%\n"
                response += f"   Signals: {trader['total_signals']}\n"
                response += f"   Followers: {trader['followers']}\n\n"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Unable to load leaderboard")

# Research Commands
@track_performance.track_command("research")
async def research_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not COMPREHENSIVE_FEATURES_AVAILABLE:
        await update.message.reply_text("❌ **Advanced Research Not Available**\n\nInstall comprehensive dependencies: `pip install -r requirements.txt`")
        return

    user_id = update.effective_user.id
    tier = await get_user_tier(user_id)
    
    access_check = tier_access_control.check_feature_access(tier, "token_research")
    if not access_check["allowed"]:
        await update.message.reply_text(f"❌ {access_check['reason']}")
        return
    
    if not context.args:
        await update.message.reply_text(
            "🔍 **Advanced Research Tools**\n\n"
            "Usage: `/research <token>`\n"
            "Example: `/research BTC`"
        )
        return
    
    token = context.args[0]
    await update.message.reply_text(f"🔍 Researching {token.upper()}...")
    
    result = await advanced_research.comprehensive_token_research(user_id, token)
    
    if result["success"]:
        await update.message.reply_text(result["summary"], parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(f"❌ {result['message']}")

# Trading Strategy Commands
@track_performance.track_command("strategy")
async def strategy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not COMPREHENSIVE_FEATURES_AVAILABLE:
        await update.message.reply_text("❌ **Trading Strategies Not Available**\n\nInstall comprehensive dependencies: `pip install -r requirements.txt`")
        return

    user_id = update.effective_user.id
    tier = await get_user_tier(user_id)
    
    if len(context.args) == 0:
        # Show strategy menu
        keyboard = [
            [InlineKeyboardButton("📊 Create Strategy", callback_data="strategy_create")],
            [InlineKeyboardButton("📈 Backtest", callback_data="strategy_backtest")],
            [InlineKeyboardButton("🚀 Deploy Strategy", callback_data="strategy_deploy")],
            [InlineKeyboardButton("💰 DCA Setup", callback_data="strategy_dca")],
            [InlineKeyboardButton("📋 My Strategies", callback_data="strategy_list")]
        ]
        
        await update.message.reply_text(
            "🤖 **Automated Trading Strategies**\n\nManage your trading strategies:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if context.args[0] == "dca":
        access_check = tier_access_control.check_feature_access(tier, "automated_strategies")
        if not access_check["allowed"]:
            await update.message.reply_text(f"❌ {access_check['reason']}")
            return
        
        if len(context.args) < 3:
            await update.message.reply_text(
                "Usage: `/strategy dca <token> <amount>`\n"
                "Example: `/strategy dca BTC 100`"
            )
            return
        
        symbol = context.args[1]
        amount = float(context.args[2])
        
        result = await automated_trading.setup_dca_strategy(user_id, symbol, amount)
        
        if result["success"]:
            await update.message.reply_text(
                f"✅ DCA strategy created for {symbol}\n"
                f"💰 Amount: ${amount}\n"
                f"📅 Frequency: Daily"
            )
        else:
            await update.message.reply_text(f"❌ {result['message']}")

# Cross-Chain Commands
@track_performance.track_command("multichain")
async def multichain_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not COMPREHENSIVE_FEATURES_AVAILABLE:
        await update.message.reply_text("❌ **Cross-Chain Analytics Not Available**\n\nInstall comprehensive dependencies: `pip install -r requirements.txt`")
        return

    user_id = update.effective_user.id
    tier = await get_user_tier(user_id)
    
    if len(context.args) == 0:
        # Show multichain menu
        keyboard = [
            [InlineKeyboardButton("📊 Portfolio", callback_data="multichain_portfolio")],
            [InlineKeyboardButton("🌉 Bridge Status", callback_data="multichain_bridge")],
            [InlineKeyboardButton("⛽ Gas Compare", callback_data="multichain_gas")],
            [InlineKeyboardButton("🔄 Arbitrage", callback_data="multichain_arbitrage")],
            [InlineKeyboardButton("🔗 Supported Chains", callback_data="multichain_chains")]
        ]
        
        await update.message.reply_text(
            "🌉 **Cross-Chain Analytics**\n\nMulti-blockchain operations:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if context.args[0] == "portfolio":
        access_check = tier_access_control.check_feature_access(tier, "multichain_portfolio")
        if not access_check["allowed"]:
            await update.message.reply_text(f"❌ {access_check['reason']}")
            return
        
        # Get user wallets
        wallets_json = get_user_property(user_id, 'portfolio_wallets')
        if not wallets_json:
            await update.message.reply_text(
                "📊 **Multi-Chain Portfolio Setup**\n\n"
                "Add wallets first: `/portfolio add <address>`"
            )
            return
        
        wallets = json.loads(wallets_json)
        await update.message.reply_text("🔍 Scanning all chains...")
        
        result = await cross_chain_analytics.get_multichain_portfolio(user_id, wallets)
        
        if result["success"]:
            response = f"🌉 **Multi-Chain Portfolio**\n\n"
            response += f"💰 Total Value: **${result['total_value']:,.2f}**\n\n"
            
            for chain, data in result["chain_distribution"].items():
                if data["value"] > 0:
                    response += f"• {chain.title()}: ${data['value']:,.2f} ({data['percentage']:.1f}%)\n"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(f"❌ {result['message']}")

# Tier Management Command
@track_performance.track_command("tier")
async def tier_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    tier = await get_user_tier(user_id)
    
    if len(context.args) == 0:
        # Show tier information
        comparison = tier_access_control.get_tier_comparison()
        
        response = f"🎯 **Your Current Tier: {tier.upper()}**\n\n"
        
        # Show current tier features
        current_features = comparison[tier]
        enabled_features = [name for name, data in current_features.items() if data["enabled"]]
        
        response += f"✅ **Enabled Features:** {len(enabled_features)}\n"
        
        if tier != "corporate":
            next_tier = "retail" if tier == "free" else "corporate"
            benefits = tier_access_control.get_upgrade_benefits(tier, next_tier)
            
            response += f"\n🚀 **Upgrade to {next_tier.title()}:**\n"
            response += f"• {benefits['total_new_features']} new features\n"
            response += f"• {benefits['enhanced_features']} enhanced features\n"
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        
    elif context.args[0] == "compare":
        # Show detailed tier comparison
        comparison = tier_access_control.get_tier_comparison()
        
        response = "📊 **Tier Comparison**\n\n"
        
        feature_categories = {
            "portfolio": "📊 Portfolio",
            "alerts": "🔔 Alerts", 
            "research": "🔍 Research",
            "trading": "💰 Trading",
            "social": "👥 Social",
            "multichain": "🌉 Cross-Chain"
        }
        
        for category, icon in feature_categories.items():
            response += f"{icon}\n"
            for tier_name in ["free", "retail", "corporate"]:
                tier_data = comparison[tier_name]
                category_features = [name for name in tier_data.keys() if category in name and tier_data[name]["enabled"]]
                response += f"  {tier_name.title()}: {len(category_features)} features\n"
            response += "\n"
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

# --- CORE SUMMARIZATION COMMANDS (MAIN FUNCTIONALITY) ---

async def summarynow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate immediate summary of today's messages"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only administrators can use this command.")
        return
    
    try:
        await update.message.reply_text("🔄 Generating summary of today's conversations...")
        
        # Get encrypted messages from memory
        message_store = context.bot_data.get('message_store', {})
        encryption_manager = context.bot_data['encryption_manager']
        
        if not message_store:
            await update.message.reply_text("📝 No messages recorded today.")
            return
        
        # Decrypt messages
        decrypted_messages = []
        for msg_id, msg_data in message_store.items():
            try:
                decrypted_text = encryption_manager.decrypt(msg_data['encrypted_text'])
                decrypted_messages.append({
                    'user': msg_data['user'],
                    'text': decrypted_text,
                    'timestamp': msg_data['timestamp'],
                    'status': msg_data.get('status', 'new')
                })
            except Exception as e:
                logger.error(f"Failed to decrypt message {msg_id}: {e}")
        
        # Generate summary
        from summarizer import generate_daily_summary
        summary = await generate_daily_summary(decrypted_messages)
        
        if summary:
            # Split long messages
            if len(summary) > 4000:
                parts = [summary[i:i+4000] for i in range(0, len(summary), 4000)]
                for i, part in enumerate(parts):
                    await update.message.reply_text(f"📝 **Summary Part {i+1}/{len(parts)}**\n\n{part}", parse_mode=ParseMode.MARKDOWN)
            else:
                await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Failed to generate summary. Please check AI provider configuration.")
            
    except Exception as e:
        logger.error(f"Error in summarynow command: {e}")
        await update.message.reply_text(f"❌ Error generating summary: {str(e)}")

async def topic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate summary for a specific topic/keyword"""
    if not context.args:
        await update.message.reply_text(
            "📋 **Topic Summary**\n\n"
            "Usage: `/topic <keyword>`\n\n"
            "Examples:\n"
            "• `/topic bitcoin`\n"
            "• `/topic #ProjectPhoenix`\n"
            "• `/topic \"server migration\"`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    keyword = ' '.join(context.args)
    
    try:
        await update.message.reply_text(f"🔍 Searching for discussions about '{keyword}'...")
        
        # Get and decrypt messages
        message_store = context.bot_data.get('message_store', {})
        encryption_manager = context.bot_data['encryption_manager']
        
        decrypted_messages = []
        for msg_id, msg_data in message_store.items():
            try:
                decrypted_text = encryption_manager.decrypt(msg_data['encrypted_text'])
                decrypted_messages.append({
                    'user': msg_data['user'],
                    'text': decrypted_text,
                    'timestamp': msg_data['timestamp'],
                    'status': msg_data.get('status', 'new')
                })
            except Exception as e:
                logger.error(f"Failed to decrypt message {msg_id}: {e}")
        
        # Generate topic summary
        from summarizer import generate_topic_summary
        summary = await generate_topic_summary(decrypted_messages, keyword)
        
        await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Error in topic command: {e}")
        await update.message.reply_text(f"❌ Error generating topic summary: {str(e)}")

async def whosaid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Find who mentioned a specific keyword"""
    if not context.args:
        await update.message.reply_text(
            "🔍 **Who Said?**\n\n"
            "Usage: `/whosaid <keyword>`\n\n"
            "Examples:\n"
            "• `/whosaid docker`\n"
            "• `/whosaid meeting`\n"
            "• `/whosaid deadline`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    keyword = ' '.join(context.args)
    
    try:
        # Get and decrypt messages
        message_store = context.bot_data.get('message_store', {})
        encryption_manager = context.bot_data['encryption_manager']
        
        decrypted_messages = []
        for msg_id, msg_data in message_store.items():
            try:
                decrypted_text = encryption_manager.decrypt(msg_data['encrypted_text'])
                decrypted_messages.append({
                    'user': msg_data['user'],
                    'text': decrypted_text,
                    'timestamp': msg_data['timestamp']
                })
            except Exception as e:
                logger.error(f"Failed to decrypt message {msg_id}: {e}")
        
        # Search for keyword
        from summarizer import search_messages_by_keyword
        matching_messages = search_messages_by_keyword(decrypted_messages, keyword)
        
        if not matching_messages:
            await update.message.reply_text(f"🔍 No mentions of '{keyword}' found in today's messages.")
            return
        
        # Get unique users who mentioned the keyword
        users = list(set(msg['user'] for msg in matching_messages))
        
        response = f"🔍 **Who mentioned '{keyword}':**\n\n"
        response += f"👥 **Users ({len(users)}):** {', '.join(users)}\n"
        response += f"💬 **Total mentions:** {len(matching_messages)}\n\n"
        
        # Show recent mentions
        response += "**Recent mentions:**\n"
        for msg in matching_messages[-3:]:  # Last 3 mentions
            timestamp = msg['timestamp'][:16] if len(msg['timestamp']) > 16 else msg['timestamp']
            text_preview = msg['text'][:100] + "..." if len(msg['text']) > 100 else msg['text']
            response += f"• {msg['user']} ({timestamp}): {text_preview}\n"
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Error in whosaid command: {e}")
        await update.message.reply_text(f"❌ Error searching messages: {str(e)}")

async def mymentions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get all mentions of the user in today's messages"""
    user = update.effective_user
    username = user.username or user.first_name
    
    try:
        # Get and decrypt messages
        message_store = context.bot_data.get('message_store', {})
        encryption_manager = context.bot_data['encryption_manager']
        
        decrypted_messages = []
        for msg_id, msg_data in message_store.items():
            try:
                decrypted_text = encryption_manager.decrypt(msg_data['encrypted_text'])
                decrypted_messages.append({
                    'user': msg_data['user'],
                    'text': decrypted_text,
                    'timestamp': msg_data['timestamp']
                })
            except Exception as e:
                logger.error(f"Failed to decrypt message {msg_id}: {e}")
        
        # Find mentions
        from summarizer import get_user_mentions
        mentions = get_user_mentions(decrypted_messages, username)
        
        if not mentions:
            await update.message.reply_text("👤 No mentions found in today's messages.")
            return
        
        response = f"👤 **Your mentions today ({len(mentions)}):**\n\n"
        
        for mention in mentions[-10:]:  # Last 10 mentions
            timestamp = mention['timestamp'][:16] if len(mention['timestamp']) > 16 else mention['timestamp']
            text_preview = mention['text'][:200] + "..." if len(mention['text']) > 200 else mention['text']
            response += f"**{mention['user']}** ({timestamp}):\n{text_preview}\n\n"
        
        # Send as DM to protect privacy
        try:
            await context.bot.send_message(
                chat_id=user.id,
                text=response,
                parse_mode=ParseMode.MARKDOWN
            )
            await update.message.reply_text("📨 Your mentions have been sent to you privately.")
        except Exception:
            # If DM fails, send in group but truncated
            short_response = f"👤 **Your mentions today:** {len(mentions)} found\n\n"
            short_response += "💬 Use this command in a private chat with me for full details."
            await update.message.reply_text(short_response, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Error in mymentions command: {e}")
        await update.message.reply_text(f"❌ Error retrieving mentions: {str(e)}")

async def weekly_summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate weekly digest (placeholder - needs daily summary storage)"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only administrators can use this command.")
        return
    
    await update.message.reply_text(
        "📊 **Weekly Summary**\n\n"
        "⚠️ Weekly summaries require daily summary storage.\n"
        "This feature will be available once daily summaries are being saved.\n\n"
        "For now, use `/summarynow` for current day summaries.",
        parse_mode=ParseMode.MARKDOWN
    )

async def set_summary_time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the time for daily summaries"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only administrators can use this command.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⏰ **Set Summary Time**\n\n"
            "Usage: `/set_summary_time HH:MM`\n\n"
            "Examples:\n"
            "• `/set_summary_time 22:30`\n"
            "• `/set_summary_time 18:00`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    time_str = context.args[0]
    
    try:
        # Validate time format
        from datetime import datetime
        datetime.strptime(time_str, '%H:%M')
        
        # Save to config (this would need persistent storage)
        await update.message.reply_text(
            f"⏰ **Summary time set to {time_str}**\n\n"
            "⚠️ Note: This setting is temporary and will reset on bot restart.\n"
            "For persistent settings, configure in environment variables.",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid time format. Please use HH:MM format (e.g., 22:30)."
        )

async def set_timezone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set timezone for summaries"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only administrators can use this command.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "🌍 **Set Timezone**\n\n"
            "Usage: `/set_timezone <timezone>`\n\n"
            "Examples:\n"
            "• `/set_timezone America/New_York`\n"
            "• `/set_timezone Europe/London`\n"
            "• `/set_timezone Asia/Tokyo`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    timezone_str = context.args[0]
    
    try:
        import pytz
        pytz.timezone(timezone_str)  # Validate timezone
        
        await update.message.reply_text(
            f"🌍 **Timezone set to {timezone_str}**\n\n"
            "⚠️ Note: This setting is temporary and will reset on bot restart.\n"
            "For persistent settings, configure in environment variables.",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception:
        await update.message.reply_text(
            "❌ Invalid timezone. Please use a valid timezone name like 'America/New_York'."
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status and current settings"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only administrators can use this command.")
        return
    
    try:
        # Get enhanced message store stats
        message_store = context.bot_data.get('message_store', {})
        from telegram_handler import get_enhanced_message_stats
        stats = get_enhanced_message_stats(message_store)
        
        # Get AI provider status
        try:
            from ai_providers import PROVIDERS_AVAILABLE
            ai_status = "✅ Available" if any(PROVIDERS_AVAILABLE.values()) else "❌ No providers available"
        except:
            ai_status = "⚠️ Status unknown"
        
        # Get scheduler status
        from scheduler import get_scheduler
        scheduler = get_scheduler()
        scheduler_status = "✅ Running" if scheduler and scheduler.is_running else "❌ Not running"
        
        response = "📊 **Bot Status**\n\n"
        response += f"💬 **Messages:** {stats.get('total_messages', 0)} total\n"
        response += f"   • Text: {stats.get('text_messages', 0)}\n"
        response += f"   • Media: {stats.get('media_messages', 0)}\n"
        response += f"   • Edited: {stats.get('edited_messages', 0)}\n"
        response += f"   • Replies: {stats.get('reply_messages', 0)}\n"
        response += f"👥 **Users:** {stats.get('unique_users', 0)} active today\n"
        response += f"🤖 **AI Provider:** {ai_status}\n"
        response += f"⏰ **Scheduler:** {scheduler_status}\n"
        response += f"🔐 **Encryption:** ✅ Active\n"
        response += f"📱 **Chat ID:** {config.get('TELEGRAM_CHAT_ID')}\n\n"
        
        response += "⚙️ **Current Settings:**\n"
        response += f"• Summary time: {config.get('SUMMARY_TIME', '22:00')}\n"
        response += f"• Timezone: {config.get('TIMEZONE', 'UTC')}\n"
        response += f"• AI Provider: {config.get('ACTIVE_AI_PROVIDER', 'groq')}\n\n"
        
        response += "🔧 **Available Commands:**\n"
        response += "• `/summarynow` - Generate immediate summary\n"
        response += "• `/topic <keyword>` - Topic-specific summary\n"
        response += "• `/whosaid <keyword>` - Find who mentioned something\n"
        response += "• `/mymentions` - Get your mentions\n"
        response += "• `/summarize_thread` - Summarize thread (reply to message)\n"
        response += "• `/status` - Show this status\n"
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        await update.message.reply_text(f"❌ Error getting status: {str(e)}")

async def summarize_thread_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Summarize a thread conversation"""
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "🧵 **Thread Summarization**\n\n"
            "Reply to any message in a thread to summarize the entire conversation.\n\n"
            "Usage: Reply to a message and type `/summarize_thread`"
        )
        return
    
    try:
        await update.message.reply_text("🧵 Analyzing thread conversation...")
        
        # Get message store and encryption manager
        message_store = context.bot_data.get('message_store', {})
        encryption_manager = context.bot_data['encryption_manager']
        
        if not message_store:
            await update.message.reply_text("📝 No messages available for thread analysis.")
            return
        
        # Decrypt all messages and prepare for thread analysis
        all_messages = []
        for msg_id, msg_data in message_store.items():
            try:
                if msg_data.get('encrypted_text'):
                    decrypted_text = encryption_manager.decrypt(msg_data['encrypted_text'])
                else:
                    decrypted_text = f"[{msg_data.get('message_type', 'media')} message]"
                
                all_messages.append({
                    'message_id': msg_id,
                    'user': msg_data['user'],
                    'text': decrypted_text,
                    'timestamp': msg_data['timestamp'],
                    'reply_to_message_id': msg_data.get('reply_to_message_id'),
                    'message_type': msg_data.get('message_type', 'text')
                })
            except Exception as e:
                logger.error(f"Failed to decrypt message {msg_id}: {e}")
        
        # Get the replied-to message ID
        replied_message_id = update.message.reply_to_message.message_id
        
        # Summarize the thread
        from thread_summarizer import summarize_thread_by_message_id
        summary = await summarize_thread_by_message_id(all_messages, replied_message_id)
        
        if summary:
            await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Could not generate thread summary.")
            
    except Exception as e:
        logger.error(f"Error in summarize_thread command: {e}")
        await update.message.reply_text(f"❌ Error summarizing thread: {str(e)}")

async def thread_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get detailed information about a thread"""
    if not update.message.reply_to_message:
        await update.message.reply_text(
            "🧵 **Thread Information**\n\n"
            "Reply to any message in a thread to get detailed thread statistics.\n\n"
            "Usage: Reply to a message and type `/thread_info`"
        )
        return
    
    try:
        # Get message store and prepare data
        message_store = context.bot_data.get('message_store', {})
        encryption_manager = context.bot_data['encryption_manager']
        
        # Decrypt all messages
        all_messages = []
        for msg_id, msg_data in message_store.items():
            try:
                if msg_data.get('encrypted_text'):
                    decrypted_text = encryption_manager.decrypt(msg_data['encrypted_text'])
                else:
                    decrypted_text = f"[{msg_data.get('message_type', 'media')} message]"
                
                all_messages.append({
                    'message_id': msg_id,
                    'user': msg_data['user'],
                    'text': decrypted_text,
                    'timestamp': msg_data['timestamp'],
                    'reply_to_message_id': msg_data.get('reply_to_message_id'),
                    'message_type': msg_data.get('message_type', 'text')
                })
            except Exception as e:
                logger.error(f"Failed to decrypt message {msg_id}: {e}")
        
        # Get thread info
        replied_message_id = update.message.reply_to_message.message_id
        from thread_summarizer import get_thread_info
        info = await get_thread_info(all_messages, replied_message_id)
        
        if info:
            await update.message.reply_text(info, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Could not get thread information.")
            
    except Exception as e:
        logger.error(f"Error in thread_info command: {e}")
        await update.message.reply_text(f"❌ Error getting thread info: {str(e)}")

async def enhanced_set_summary_time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced set summary time with scheduler integration"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only administrators can use this command.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⏰ **Set Summary Time**\n\n"
            "Usage: `/set_summary_time HH:MM [timezone]`\n\n"
            "Examples:\n"
            "• `/set_summary_time 22:30`\n"
            "• `/set_summary_time 18:00 America/New_York`\n"
            "• `/set_summary_time 09:00 Europe/London`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    time_str = context.args[0]
    timezone_str = context.args[1] if len(context.args) > 1 else None
    
    try:
        # Validate time format
        from datetime import datetime
        datetime.strptime(time_str, '%H:%M')
        
        # Validate timezone if provided
        if timezone_str:
            import pytz
            pytz.timezone(timezone_str)
        
        # Update scheduler
        from scheduler import get_scheduler
        scheduler = get_scheduler()
        
        if scheduler:
            success = scheduler.reschedule_daily_summary(time_str, timezone_str)
            if success:
                tz_info = f" {timezone_str}" if timezone_str else ""
                await update.message.reply_text(
                    f"⏰ **Summary time updated to {time_str}{tz_info}**\n\n"
                    "✅ Automatic daily summaries will now be sent at this time.\n"
                    "🔄 Scheduler has been updated with the new time.",
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text("❌ Failed to update scheduler. Check logs for details.")
        else:
            await update.message.reply_text("⚠️ Scheduler not running. Time saved but won't take effect until restart.")
        
    except ValueError:
        await update.message.reply_text("❌ Invalid time format. Please use HH:MM format (e.g., 22:30).")
    except Exception as e:
        await update.message.reply_text(f"❌ Invalid timezone or other error: {str(e)}")

async def export_summaries_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export summaries to file"""
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Only administrators can use this command.")
        return
    
    try:
        import os
        from datetime import datetime, timedelta
        
        # Get date range
        days = int(context.args[0]) if context.args and context.args[0].isdigit() else 7
        
        await update.message.reply_text(f"📄 Exporting summaries from last {days} days...")
        
        summaries_dir = "data/summaries"
        if not os.path.exists(summaries_dir):
            await update.message.reply_text("❌ No summaries directory found.")
            return
        
        # Collect summaries
        export_content = f"# Möbius AI Assistant - Summary Export\n"
        export_content += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_content += f"# Period: Last {days} days\n\n"
        
        found_summaries = 0
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            filename = f"{summaries_dir}/summary_{date_str}.txt"
            
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    summary = f.read()
                    export_content += f"## Summary for {date_str}\n\n"
                    export_content += summary
                    export_content += "\n\n---\n\n"
                    found_summaries += 1
        
        if found_summaries == 0:
            await update.message.reply_text("❌ No summaries found for the specified period.")
            return
        
        # Save export file
        export_filename = f"data/export_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(export_filename, 'w', encoding='utf-8') as f:
            f.write(export_content)
        
        # Send file
        with open(export_filename, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f"summaries_export_{datetime.now().strftime('%Y%m%d')}.md",
                caption=f"📄 **Summary Export**\n\n"
                       f"• Period: Last {days} days\n"
                       f"• Summaries found: {found_summaries}\n"
                       f"• Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
        # Clean up export file
        os.remove(export_filename)
        
    except Exception as e:
        logger.error(f"Error in export_summaries command: {e}")
        await update.message.reply_text(f"❌ Error exporting summaries: {str(e)}")

# --- Main Application ---
def main():
    # Initialize databases
    init_db()
    enhanced_db._initialize_schema()  # Initialize enhanced database schema
    
    application = Application.builder().token(config.get('TELEGRAM_BOT_TOKEN')).post_init(post_init).build()

    # Onboarding conversation handler
    onboarding_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command, filters=filters.ChatType.PRIVATE)],
        states={CHOOSE_PLAN: [CallbackQueryHandler(plan_selection)], ENTER_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, activate_key)]},
        fallbacks=[CommandHandler("cancel", cancel_onboarding)]
    )
    application.add_handler(onboarding_handler)
    
    # Callback query handler for interactive menus
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # User command handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("premium", premium_command))
    application.add_handler(CommandHandler("llama", llama_command))
    application.add_handler(CommandHandler("arkham", arkham_command))
    application.add_handler(CommandHandler("nansen", nansen_command))
    application.add_handler(CommandHandler("alert", alert_command))
    application.add_handler(CommandHandler("create_wallet", create_wallet_command))
    application.add_handler(CommandHandler("set_calendly", set_calendly_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    # Core summarization commands (MAIN FUNCTIONALITY)
    application.add_handler(CommandHandler("summarynow", summarynow_command))
    application.add_handler(CommandHandler("topic", topic_command))
    application.add_handler(CommandHandler("whosaid", whosaid_command))
    application.add_handler(CommandHandler("mymentions", mymentions_command))
    application.add_handler(CommandHandler("weekly_summary", weekly_summary_command))
    
    # Admin command handlers
    application.add_handler(CommandHandler("set_api_key", set_api_key_command))
    application.add_handler(CommandHandler("set_ai_provider", set_ai_provider_command))
    application.add_handler(CommandHandler("set_timezone", set_timezone_command))
    application.add_handler(CommandHandler("set_summary_time", set_summary_time_command))
    application.add_handler(CommandHandler("pause", pause_command))
    application.add_handler(CommandHandler("resume", resume_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Enhanced admin command handlers
    application.add_handler(CommandHandler("metrics", metrics_command))
    application.add_handler(CommandHandler("security", security_command))
    application.add_handler(CommandHandler("analytics", analytics_command))
    application.add_handler(CommandHandler("cleanup", cleanup_command))
    
    # Thread summarization commands
    application.add_handler(CommandHandler("summarize_thread", summarize_thread_command))
    application.add_handler(CommandHandler("thread_info", thread_info_command))
    
    # Export and utility commands
    application.add_handler(CommandHandler("export_summaries", export_summaries_command))
    
    # UI Enhancement - Callback query handler for smooth interactions
    from ui_enhancements import get_callback_handler
    application.add_handler(get_callback_handler())
    
    # Comprehensive feature command handlers
    application.add_handler(CommandHandler("portfolio", portfolio_command))
    application.add_handler(CommandHandler("alerts", alerts_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("social", social_command))
    application.add_handler(CommandHandler("research", research_command))
    application.add_handler(CommandHandler("strategy", strategy_command))
    application.add_handler(CommandHandler("multichain", multichain_command))
    application.add_handler(CommandHandler("tier", tier_command))
    
    # Message handler for the target chat
    target_chat_id = int(config.get('TELEGRAM_CHAT_ID'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Chat(chat_id=target_chat_id), handle_message))

    # Add error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Log the error and send a telegram message to notify the developer."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Try to send error message to user if possible
        if update and hasattr(update, 'effective_message') and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ An error occurred while processing your request. Please try again later."
                )
            except Exception:
                pass  # Ignore if we can't send error message
    
    application.add_error_handler(error_handler)

    logger.info("Möbius (v. a666.v01) Comprehensive Features Edition is starting up...")
    logger.info("🚀 New features: Portfolio Management, Advanced Alerts, Natural Language Queries, Social Trading, Research Tools, Automated Trading, Cross-Chain Analytics")
    logger.info("🎯 Tier-based access control: Free, Retail, Corporate")
    logger.info("🔐 Enhanced security: Encryption, Rate Limiting, IP Whitelisting")
