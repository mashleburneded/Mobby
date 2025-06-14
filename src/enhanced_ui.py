# src/enhanced_ui.py
"""
Enhanced UI components for Möbius AI Assistant.
Implements interactive keyboards, rich formatting, and responsive design.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class InteractiveMenu:
    """
    Interactive menu system with callback handling and state management.
    Provides secure, responsive UI components for complex interactions.
    """
    
    def __init__(self):
        self._menu_handlers: Dict[str, Callable] = {}
        self._menu_states: Dict[int, Dict] = {}  # user_id -> state
        self._menu_timeouts: Dict[int, float] = {}  # user_id -> timeout
        
    def register_menu_handler(self, callback_prefix: str, handler: Callable):
        """Register a callback handler for menu interactions"""
        self._menu_handlers[callback_prefix] = handler
    
    async def create_crypto_research_menu(self) -> InlineKeyboardMarkup:
        """Create interactive crypto research menu"""
        keyboard = [
            [
                InlineKeyboardButton("📊 TVL Data", callback_data="crypto_tvl"),
                InlineKeyboardButton("💰 Revenue", callback_data="crypto_revenue")
            ],
            [
                InlineKeyboardButton("🚀 Recent Raises", callback_data="crypto_raises"),
                InlineKeyboardButton("📈 Price Data", callback_data="crypto_price")
            ],
            [
                InlineKeyboardButton("🔍 Arkham Search", callback_data="crypto_arkham"),
                InlineKeyboardButton("🏷️ Nansen Labels", callback_data="crypto_nansen")
            ],
            [
                InlineKeyboardButton("⚠️ Set Alert", callback_data="crypto_alert"),
                InlineKeyboardButton("❌ Cancel", callback_data="menu_cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def create_admin_menu(self) -> InlineKeyboardMarkup:
        """Create administrative control menu"""
        keyboard = [
            [
                InlineKeyboardButton("🔑 API Keys", callback_data="admin_api_keys"),
                InlineKeyboardButton("🤖 AI Provider", callback_data="admin_ai_provider")
            ],
            [
                InlineKeyboardButton("⏰ Schedule", callback_data="admin_schedule"),
                InlineKeyboardButton("📊 Metrics", callback_data="admin_metrics")
            ],
            [
                InlineKeyboardButton("🔒 Security", callback_data="admin_security"),
                InlineKeyboardButton("⚙️ System", callback_data="admin_system")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="menu_cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def create_subscription_menu(self, current_tier: str) -> InlineKeyboardMarkup:
        """Create subscription management menu"""
        keyboard = []
        
        # Current tier display
        tier_emoji = {"free": "🆓", "retail": "⭐", "corporate": "💎"}
        current_emoji = tier_emoji.get(current_tier, "❓")
        
        if current_tier != "retail":
            keyboard.append([InlineKeyboardButton(f"⭐ Upgrade to Retail", callback_data="sub_upgrade_retail")])
        
        if current_tier != "corporate":
            keyboard.append([InlineKeyboardButton(f"💎 Upgrade to Corporate", callback_data="sub_upgrade_corporate")])
        
        keyboard.extend([
            [InlineKeyboardButton("📊 Usage Stats", callback_data="sub_usage")],
            [InlineKeyboardButton("💳 Billing Info", callback_data="sub_billing")],
            [InlineKeyboardButton("❌ Close", callback_data="menu_cancel")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    async def create_wallet_menu(self) -> InlineKeyboardMarkup:
        """Create wallet management menu"""
        keyboard = [
            [
                InlineKeyboardButton("🆕 Create New Wallet", callback_data="wallet_create"),
                InlineKeyboardButton("📥 Import Wallet", callback_data="wallet_import")
            ],
            [
                InlineKeyboardButton("💰 Check Balance", callback_data="wallet_balance"),
                InlineKeyboardButton("📤 Send Transaction", callback_data="wallet_send")
            ],
            [
                InlineKeyboardButton("📋 Transaction History", callback_data="wallet_history"),
                InlineKeyboardButton("🔗 Add to Watchlist", callback_data="wallet_watch")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="menu_cancel")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def create_pagination_menu(self, current_page: int, total_pages: int, 
                                   callback_prefix: str) -> InlineKeyboardMarkup:
        """Create pagination controls"""
        keyboard = []
        
        # Navigation row
        nav_row = []
        if current_page > 1:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"{callback_prefix}_page_{current_page-1}"))
        
        nav_row.append(InlineKeyboardButton(f"📄 {current_page}/{total_pages}", callback_data="page_info"))
        
        if current_page < total_pages:
            nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"{callback_prefix}_page_{current_page+1}"))
        
        keyboard.append(nav_row)
        
        # Quick jump row (for large datasets)
        if total_pages > 5:
            jump_row = []
            if current_page > 3:
                jump_row.append(InlineKeyboardButton("⏮️ First", callback_data=f"{callback_prefix}_page_1"))
            if current_page < total_pages - 2:
                jump_row.append(InlineKeyboardButton("⏭️ Last", callback_data=f"{callback_prefix}_page_{total_pages}"))
            if jump_row:
                keyboard.append(jump_row)
        
        keyboard.append([InlineKeyboardButton("❌ Close", callback_data="menu_cancel")])
        
        return InlineKeyboardMarkup(keyboard)

class RichFormatter:
    """
    Rich text formatting utilities for enhanced message presentation.
    Provides consistent, secure formatting with emoji and markdown support.
    """
    
    @staticmethod
    def format_crypto_data(data: Dict[str, Any], title: str) -> str:
        """Format cryptocurrency data with rich presentation"""
        if not data:
            return f"❌ **{title}**\n\nNo data available."
        
        formatted = f"📊 **{title}**\n\n"
        
        # Handle different data types
        if "tvl" in data:
            tvl = data["tvl"]
            if isinstance(tvl, (int, float)):
                formatted += f"💰 **Total Value Locked:** ${tvl:,.2f}\n"
            elif isinstance(tvl, dict):
                formatted += f"💰 **TVL:** ${tvl.get('current', 0):,.2f}\n"
                if 'change_24h' in tvl:
                    change = tvl['change_24h']
                    emoji = "📈" if change >= 0 else "📉"
                    formatted += f"{emoji} **24h Change:** {change:+.2f}%\n"
        
        if "revenue" in data:
            revenue = data["revenue"]
            formatted += f"💵 **Revenue:** ${revenue:,.2f}\n"
        
        if "price" in data:
            price = data["price"]
            formatted += f"💲 **Price:** ${price:.6f}\n"
        
        # Add timestamp
        formatted += f"\n🕐 **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
        
        return formatted
    
    @staticmethod
    def format_wallet_info(address: str, data: Dict[str, Any]) -> str:
        """Format wallet information with security considerations"""
        # Truncate address for security
        short_address = f"{address[:6]}...{address[-4:]}"
        
        formatted = f"👛 **Wallet Analysis**\n\n"
        formatted += f"📍 **Address:** `{short_address}`\n\n"
        
        if "balance" in data:
            formatted += f"💰 **Balance:** {data['balance']:.6f} ETH\n"
        
        if "labels" in data and data["labels"]:
            formatted += f"🏷️ **Labels:** {', '.join(data['labels'])}\n"
        
        if "transactions" in data:
            tx_count = data["transactions"]
            formatted += f"📊 **Transactions:** {tx_count:,}\n"
        
        if "risk_score" in data:
            risk = data["risk_score"]
            risk_emoji = "🟢" if risk < 30 else "🟡" if risk < 70 else "🔴"
            formatted += f"{risk_emoji} **Risk Score:** {risk}/100\n"
        
        return formatted
    
    @staticmethod
    def format_alert_summary(alerts: List[Dict[str, Any]]) -> str:
        """Format alert summary with status indicators"""
        if not alerts:
            return "📭 **No Active Alerts**\n\nYou haven't set up any wallet alerts yet."
        
        formatted = f"⚠️ **Active Alerts ({len(alerts)})**\n\n"
        
        for i, alert in enumerate(alerts[:10], 1):  # Limit to 10 for readability
            address = alert.get("address", "Unknown")
            short_addr = f"{address[:6]}...{address[-4:]}"
            amount = alert.get("amount", 0)
            status_emoji = "🟢" if alert.get("active", True) else "🔴"
            
            formatted += f"{status_emoji} **Alert {i}**\n"
            formatted += f"   📍 `{short_addr}`\n"
            formatted += f"   💰 Threshold: ${amount:,.2f}\n\n"
        
        if len(alerts) > 10:
            formatted += f"... and {len(alerts) - 10} more alerts\n"
        
        return formatted
    
    @staticmethod
    def format_performance_metrics(metrics: Dict[str, Any]) -> str:
        """Format system performance metrics"""
        formatted = "📊 **System Performance**\n\n"
        
        system = metrics.get("system", {})
        formatted += f"⏱️ **Uptime:** {system.get('uptime_seconds', 0)/3600:.1f} hours\n"
        formatted += f"👥 **Active Users:** {system.get('active_users', 0)}\n"
        formatted += f"⚡ **Commands Processed:** {system.get('total_commands', 0):,}\n"
        formatted += f"❌ **Errors:** {system.get('total_errors', 0)}\n\n"
        
        performance = metrics.get("performance", {})
        avg_time = performance.get("avg_response_time", 0)
        formatted += f"🚀 **Avg Response Time:** {avg_time:.3f}s\n\n"
        
        # Top commands
        top_commands = performance.get("top_commands", [])
        if top_commands:
            formatted += "🔥 **Most Used Commands:**\n"
            for cmd, count in top_commands[:5]:
                formatted += f"   • `/{cmd}`: {count:,} uses\n"
        
        return formatted
    
    @staticmethod
    def format_security_summary(security_data: Dict[str, Any]) -> str:
        """Format security summary for admin view"""
        formatted = "🔒 **Security Summary**\n\n"
        
        summary = security_data.get("summary", {})
        formatted += f"📊 **Events (Last Hour):** {summary.get('total_events_last_hour', 0)}\n"
        formatted += f"⚠️ **High Risk Events:** {summary.get('high_risk_events', 0)}\n"
        formatted += f"🚫 **Failed Logins:** {summary.get('failed_authentications', 0)}\n"
        formatted += f"🕵️ **Suspicious IPs:** {summary.get('suspicious_ips_count', 0)}\n\n"
        
        # Risk breakdown
        risk_breakdown = security_data.get("risk_breakdown", {})
        if risk_breakdown:
            formatted += "📈 **Risk Level Breakdown:**\n"
            for level, count in risk_breakdown.items():
                emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(level, "⚪")
                formatted += f"   {emoji} {level.title()}: {count}\n"
        
        return formatted
    
    @staticmethod
    def create_progress_bar(current: int, total: int, width: int = 20) -> str:
        """Create a visual progress bar"""
        if total == 0:
            return "▱" * width
        
        filled = int((current / total) * width)
        bar = "▰" * filled + "▱" * (width - filled)
        percentage = (current / total) * 100
        
        return f"{bar} {percentage:.1f}%"
    
    @staticmethod
    def format_error_message(error_type: str, message: str, show_details: bool = False) -> str:
        """Format error messages with consistent styling"""
        emoji_map = {
            "auth": "🔐",
            "permission": "🚫", 
            "rate_limit": "⏱️",
            "api": "🌐",
            "validation": "⚠️",
            "system": "⚙️"
        }
        
        emoji = emoji_map.get(error_type, "❌")
        formatted = f"{emoji} **Error**\n\n{message}"
        
        if show_details:
            formatted += f"\n\n🔍 **Error Type:** {error_type}"
            formatted += f"\n⏰ **Time:** {datetime.now().strftime('%H:%M:%S UTC')}"
        
        return formatted

class ProgressIndicator:
    """
    Progress indicator for long-running operations.
    Provides real-time feedback to users during processing.
    """
    
    def __init__(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
        self.context = context
        self.chat_id = chat_id
        self.message_id = message_id
        self._current_step = 0
        self._total_steps = 0
        self._is_active = False
    
    async def start(self, total_steps: int, initial_message: str = "⚙️ Processing..."):
        """Start progress tracking"""
        self._total_steps = total_steps
        self._current_step = 0
        self._is_active = True
        
        await self.context.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=initial_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def update(self, step_message: str, increment: int = 1):
        """Update progress with new step"""
        if not self._is_active:
            return
        
        self._current_step += increment
        progress_bar = RichFormatter.create_progress_bar(self._current_step, self._total_steps)
        
        message = f"⚙️ **Processing...**\n\n{progress_bar}\n\n{step_message}"
        
        try:
            await self.context.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.warning(f"Failed to update progress indicator: {e}")
    
    async def complete(self, final_message: str):
        """Complete progress tracking"""
        self._is_active = False
        
        try:
            await self.context.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text=final_message,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.warning(f"Failed to complete progress indicator: {e}")

# Global instances
interactive_menu = InteractiveMenu()
rich_formatter = RichFormatter()