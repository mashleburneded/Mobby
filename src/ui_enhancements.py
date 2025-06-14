# src/ui_enhancements.py - Clean UI Enhancement Module
import logging
from datetime import datetime
from typing import List, Dict, Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

class SmartKeyboard:
    """Smart keyboard generator for smooth UI interactions"""
    
    @staticmethod
    def create_command_keyboard(commands: List[Dict[str, str]], columns: int = 2) -> InlineKeyboardMarkup:
        """Create clickable command keyboard"""
        keyboard = []
        row = []
        
        for i, cmd in enumerate(commands):
            button = InlineKeyboardButton(
                text=cmd.get('text', 'Unknown'),
                callback_data=cmd.get('callback_data', 'unknown')
            )
            row.append(button)
            
            # Create new row when reaching column limit
            if len(row) == columns or i == len(commands) - 1:
                keyboard.append(row)
                row = []
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_main_menu() -> InlineKeyboardMarkup:
        """Create main menu keyboard"""
        commands = [
            {'text': '📊 Research', 'callback_data': 'cmd_research'},
            {'text': '💰 Portfolio', 'callback_data': 'cmd_portfolio'},
            {'text': '🔔 Alerts', 'callback_data': 'cmd_alerts'},
            {'text': '📝 Summary', 'callback_data': 'cmd_summary'},
            {'text': '🤖 AI Chat', 'callback_data': 'cmd_ai'},
            {'text': '⚙️ Settings', 'callback_data': 'cmd_settings'},
            {'text': 'ℹ️ Help', 'callback_data': 'cmd_help'},
            {'text': '📈 Status', 'callback_data': 'cmd_status'}
        ]
        return SmartKeyboard.create_command_keyboard(commands, columns=2)
    
    @staticmethod
    def create_research_menu() -> InlineKeyboardMarkup:
        """Create research menu keyboard"""
        commands = [
            {'text': '🔍 Token Research', 'callback_data': 'research_token'},
            {'text': '📊 DeFiLlama', 'callback_data': 'research_defillama'},
            {'text': '🕵️ Arkham', 'callback_data': 'research_arkham'},
            {'text': '📈 Nansen', 'callback_data': 'research_nansen'},
            {'text': '🌐 Cross-Chain', 'callback_data': 'research_crosschain'},
            {'text': '🔙 Back to Menu', 'callback_data': 'cmd_menu'}
        ]
        return SmartKeyboard.create_command_keyboard(commands, columns=2)
    
    @staticmethod
    def create_portfolio_menu() -> InlineKeyboardMarkup:
        """Create portfolio menu keyboard"""
        commands = [
            {'text': '📊 View Portfolio', 'callback_data': 'portfolio_view'},
            {'text': '➕ Add Wallet', 'callback_data': 'portfolio_add'},
            {'text': '📈 Analytics', 'callback_data': 'portfolio_analytics'},
            {'text': '⚖️ Risk Assessment', 'callback_data': 'portfolio_risk'},
            {'text': '🔙 Back to Menu', 'callback_data': 'cmd_menu'}
        ]
        return SmartKeyboard.create_command_keyboard(commands, columns=2)
    
    @staticmethod
    def create_alerts_menu() -> InlineKeyboardMarkup:
        """Create alerts menu keyboard"""
        commands = [
            {'text': '🔔 View Alerts', 'callback_data': 'alerts_view'},
            {'text': '➕ Add Alert', 'callback_data': 'alerts_add'},
            {'text': '🗑️ Remove Alert', 'callback_data': 'alerts_remove'},
            {'text': '⚙️ Alert Settings', 'callback_data': 'alerts_settings'},
            {'text': '🔙 Back to Menu', 'callback_data': 'cmd_menu'}
        ]
        return SmartKeyboard.create_command_keyboard(commands, columns=2)
    
    @staticmethod
    def create_pagination_keyboard(current_page: int, total_pages: int, prefix: str = "page") -> InlineKeyboardMarkup:
        """Create pagination keyboard"""
        keyboard = []
        
        # Navigation row
        nav_row = []
        if current_page > 1:
            nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"{prefix}_{current_page-1}"))
        
        nav_row.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="page_info"))
        
        if current_page < total_pages:
            nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"{prefix}_{current_page+1}"))
        
        keyboard.append(nav_row)
        
        # Quick jump row (for more than 5 pages)
        if total_pages > 5:
            jump_row = []
            if current_page > 3:
                jump_row.append(InlineKeyboardButton("1", callback_data=f"{prefix}_1"))
                if current_page > 4:
                    jump_row.append(InlineKeyboardButton("...", callback_data="page_info"))
            
            # Show current page and neighbors
            for page in range(max(1, current_page-1), min(total_pages+1, current_page+2)):
                if page != current_page:
                    jump_row.append(InlineKeyboardButton(str(page), callback_data=f"{prefix}_{page}"))
            
            if current_page < total_pages - 2:
                if current_page < total_pages - 3:
                    jump_row.append(InlineKeyboardButton("...", callback_data="page_info"))
                jump_row.append(InlineKeyboardButton(str(total_pages), callback_data=f"{prefix}_{total_pages}"))
            
            if jump_row:
                keyboard.append(jump_row)
        
        return InlineKeyboardMarkup(keyboard)

def create_smart_help_menu() -> InlineKeyboardMarkup:
    """Create smart help menu with categorized commands"""
    commands = [
        {'text': '💬 Basic Commands', 'callback_data': 'help_basic'},
        {'text': '🔍 Research Commands', 'callback_data': 'help_research'},
        {'text': '💰 Portfolio Commands', 'callback_data': 'help_portfolio'},
        {'text': '🔔 Alert Commands', 'callback_data': 'help_alerts'},
        {'text': '🤖 AI Commands', 'callback_data': 'help_ai'},
        {'text': '⚙️ Admin Commands', 'callback_data': 'help_admin'},
        {'text': '🔙 Back to Menu', 'callback_data': 'cmd_menu'}
    ]
    return SmartKeyboard.create_command_keyboard(commands, columns=2)

def create_confirmation_keyboard(action: str, item_id: str = "") -> InlineKeyboardMarkup:
    """Create confirmation keyboard for destructive actions"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{item_id}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{action}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_tier_selection_keyboard() -> InlineKeyboardMarkup:
    """Create tier selection keyboard for subscription"""
    commands = [
        {'text': '🆓 Free Tier', 'callback_data': 'tier_free'},
        {'text': '💰 Premium Retail', 'callback_data': 'tier_retail'},
        {'text': '🏢 Premium Corporate', 'callback_data': 'tier_corporate'},
        {'text': 'ℹ️ Compare Tiers', 'callback_data': 'tier_compare'}
    ]
    return SmartKeyboard.create_command_keyboard(commands, columns=1)

class UIFormatter:
    """Format text and data for better UI presentation"""
    
    @staticmethod
    def format_price(price: float, currency: str = "USD") -> str:
        """Format price with appropriate precision"""
        if price >= 1000000:
            return f"${price/1000000:.2f}M"
        elif price >= 1000:
            return f"${price/1000:.2f}K"
        elif price >= 1:
            return f"${price:.2f}"
        else:
            return f"${price:.6f}"
    
    @staticmethod
    def format_percentage(percentage: float) -> str:
        """Format percentage with color indicators"""
        if percentage > 0:
            return f"🟢 +{percentage:.2f}%"
        elif percentage < 0:
            return f"🔴 {percentage:.2f}%"
        else:
            return f"⚪ {percentage:.2f}%"
    
    @staticmethod
    def format_large_number(number: float) -> str:
        """Format large numbers with appropriate suffixes"""
        if number >= 1e12:
            return f"{number/1e12:.2f}T"
        elif number >= 1e9:
            return f"{number/1e9:.2f}B"
        elif number >= 1e6:
            return f"{number/1e6:.2f}M"
        elif number >= 1e3:
            return f"{number/1e3:.2f}K"
        else:
            return f"{number:.2f}"
    
    @staticmethod
    def format_timestamp(timestamp: datetime) -> str:
        """Format timestamp for display"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds//3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds//60}m ago"
        else:
            return "Just now"
    
    @staticmethod
    def create_progress_bar(current: int, total: int, length: int = 10) -> str:
        """Create a text-based progress bar"""
        if total == 0:
            return "▱" * length
        
        filled = int((current / total) * length)
        bar = "▰" * filled + "▱" * (length - filled)
        percentage = (current / total) * 100
        
        return f"{bar} {percentage:.1f}%"
    
    @staticmethod
    def format_table(data: List[Dict], headers: List[str], max_width: int = 30) -> str:
        """Format data as a simple table"""
        if not data or not headers:
            return "No data available"
        
        # Calculate column widths
        col_widths = []
        for header in headers:
            max_len = len(header)
            for row in data:
                value = str(row.get(header, ""))
                max_len = max(max_len, len(value))
            col_widths.append(min(max_len, max_width))
        
        # Create table
        table = []
        
        # Header row
        header_row = " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers))
        table.append(header_row)
        table.append("-" * len(header_row))
        
        # Data rows
        for row in data:
            data_row = " | ".join(
                str(row.get(header, "")).ljust(col_widths[i])[:col_widths[i]]
                for i, header in enumerate(headers)
            )
            table.append(data_row)
        
        return "```\n" + "\n".join(table) + "\n```"

class MessageTemplates:
    """Pre-defined message templates for common responses"""
    
    @staticmethod
    def error_message(error: str, suggestion: str = None) -> str:
        """Standard error message template"""
        message = f"❌ **Error:** {error}"
        if suggestion:
            message += f"\n\n💡 **Suggestion:** {suggestion}"
        return message
    
    @staticmethod
    def success_message(action: str, details: str = None) -> str:
        """Standard success message template"""
        message = f"✅ **Success:** {action}"
        if details:
            message += f"\n\n{details}"
        return message
    
    @staticmethod
    def loading_message(action: str) -> str:
        """Loading message template"""
        return f"⏳ {action}... Please wait."
    
    @staticmethod
    def feature_unavailable(feature: str, tier: str = None) -> str:
        """Feature unavailable message"""
        message = f"🔒 **{feature}** is not available"
        if tier:
            message += f" in your current tier.\n\nUpgrade to **{tier}** to access this feature."
        else:
            message += " at the moment."
        return message
    
    @staticmethod
    def welcome_message(user_name: str) -> str:
        """Welcome message template"""
        return f"""
🚀 **Welcome to Möbius AI Assistant, {user_name}!**

I'm your intelligent crypto companion, ready to help you with:

• 💬 Natural language conversations
• 📊 Crypto research and analysis  
• 📈 Portfolio tracking
• 🔔 Price alerts
• 📝 Conversation summaries
• 🤖 AI-powered insights

**Quick Start:**
• Type `/menu` to see all options
• Type `/help` for detailed help
• Just talk to me naturally!

Ready to explore the crypto world together? 🌟
"""