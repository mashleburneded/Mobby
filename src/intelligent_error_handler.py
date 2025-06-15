# src/intelligent_error_handler.py
"""
Intelligent Error Handler and User Correction System
Handles user input errors, provides corrections, and learns from mistakes
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Correction:
    original: str
    suggested: str
    confidence: float
    correction_type: str
    explanation: str

class IntelligentErrorHandler:
    """Handles user input errors and provides intelligent corrections"""
    
    def __init__(self):
        # Common token symbols and their variations
        self.token_mappings = {
            'bitcoin': ['BTC', 'bitcoin', 'btc', 'Bitcoin'],
            'ethereum': ['ETH', 'ethereum', 'eth', 'Ethereum', 'ether'],
            'solana': ['SOL', 'solana', 'sol', 'Solana'],
            'cardano': ['ADA', 'cardano', 'ada', 'Cardano'],
            'polkadot': ['DOT', 'polkadot', 'dot', 'Polkadot'],
            'chainlink': ['LINK', 'chainlink', 'link', 'Chainlink'],
            'polygon': ['MATIC', 'polygon', 'matic', 'Polygon'],
            'avalanche': ['AVAX', 'avalanche', 'avax', 'Avalanche'],
            'binance': ['BNB', 'binance', 'bnb', 'Binance'],
            'ripple': ['XRP', 'ripple', 'xrp', 'Ripple'],
        }
        
        # Command mappings
        self.command_mappings = {
            'portfolio': ['portfolio', 'wallet', 'balance', 'holdings', 'positions'],
            'research': ['research', 'analyze', 'analysis', 'info', 'information', 'details'],
            'summary': ['summary', 'summarize', 'recap', 'overview'],
            'alerts': ['alerts', 'notifications', 'notify', 'watch', 'monitor'],
            'help': ['help', 'commands', 'what can you do', 'options'],
            'status': ['status', 'health', 'online', 'working']
        }
        
        # Common typos and corrections
        self.typo_corrections = {
            'portolio': 'portfolio',
            'portfollio': 'portfolio',
            'reserach': 'research',
            'researh': 'research',
            'sumary': 'summary',
            'sumarize': 'summarize',
            'alrts': 'alerts',
            'notifcations': 'notifications',
            'bitcon': 'bitcoin',
            'etherium': 'ethereum',
            'solanna': 'solana'
        }
        
        # Context-aware corrections
        self.context_corrections = {
            'price': {
                'missing_token': "I'd be happy to check the price! Which token are you interested in? (e.g., Bitcoin, Ethereum, Solana)",
                'invalid_token': "I couldn't find that token. Did you mean one of these popular tokens: BTC, ETH, SOL, ADA, DOT?"
            },
            'portfolio': {
                'no_data': "I don't see any portfolio data yet. Would you like help setting up portfolio tracking?",
                'access_denied': "Portfolio features require account setup. Would you like me to help you get started?"
            },
            'research': {
                'missing_token': "I'd love to research something for you! Please specify which token or topic you'd like me to analyze.",
                'invalid_token': "I couldn't find information on that token. Could you double-check the symbol or try a different one?"
            }
        }
    
    def detect_and_correct_input(self, user_input: str, context: Dict = None) -> Optional[Correction]:
        """Detect errors in user input and suggest corrections"""
        
        # Check for typos first
        typo_correction = self.check_typos(user_input)
        if typo_correction:
            return typo_correction
        
        # Check for token name issues
        token_correction = self.check_token_names(user_input)
        if token_correction:
            return token_correction
        
        # Check for command issues
        command_correction = self.check_commands(user_input)
        if command_correction:
            return command_correction
        
        # Check for context-specific issues
        if context:
            context_correction = self.check_context_issues(user_input, context)
            if context_correction:
                return context_correction
        
        return None
    
    def check_typos(self, text: str) -> Optional[Correction]:
        """Check for common typos and suggest corrections"""
        words = text.lower().split()
        
        for word in words:
            if word in self.typo_corrections:
                corrected = self.typo_corrections[word]
                corrected_text = text.replace(word, corrected)
                
                return Correction(
                    original=text,
                    suggested=corrected_text,
                    confidence=0.9,
                    correction_type="typo",
                    explanation=f"Did you mean '{corrected}' instead of '{word}'?"
                )
        
        return None
    
    def check_token_names(self, text: str) -> Optional[Correction]:
        """Check for token name issues and suggest corrections"""
        # Extract potential token mentions
        words = re.findall(r'\b[A-Za-z]+\b', text.lower())
        
        for word in words:
            # Check if it's a partial match for a known token
            best_match = None
            best_score = 0
            
            for token_name, variations in self.token_mappings.items():
                for variation in variations:
                    similarity = SequenceMatcher(None, word, variation.lower()).ratio()
                    if similarity > best_score and similarity > 0.6:
                        best_score = similarity
                        best_match = variation
            
            if best_match and best_score > 0.6:
                corrected_text = text.replace(word, best_match)
                return Correction(
                    original=text,
                    suggested=corrected_text,
                    confidence=best_score,
                    correction_type="token_name",
                    explanation=f"Did you mean '{best_match}' instead of '{word}'?"
                )
        
        return None
    
    def check_commands(self, text: str) -> Optional[Correction]:
        """Check for command-related issues"""
        text_lower = text.lower()
        
        # Check for partial command matches
        for command, variations in self.command_mappings.items():
            for variation in variations:
                if variation in text_lower:
                    # Suggest the proper command format
                    if command == 'research' and not any(token in text_lower for token in ['btc', 'eth', 'bitcoin', 'ethereum']):
                        return Correction(
                            original=text,
                            suggested=f"research BTC",
                            confidence=0.8,
                            correction_type="incomplete_command",
                            explanation="Research command needs a token symbol. Try 'research BTC' or 'research Ethereum'"
                        )
        
        return None
    
    def check_context_issues(self, text: str, context: Dict) -> Optional[Correction]:
        """Check for context-specific issues"""
        intent = context.get('intent', '')
        
        if intent == 'price_check':
            # Check if token is missing
            if not any(token in text.lower() for token_list in self.token_mappings.values() for token in token_list):
                return Correction(
                    original=text,
                    suggested="What's the price of Bitcoin?",
                    confidence=0.7,
                    correction_type="missing_context",
                    explanation=self.context_corrections['price']['missing_token']
                )
        
        elif intent == 'research_request':
            # Check if research topic is missing
            if len(text.split()) < 3:  # Very short research request
                return Correction(
                    original=text,
                    suggested="research Ethereum",
                    confidence=0.7,
                    correction_type="missing_context",
                    explanation=self.context_corrections['research']['missing_token']
                )
        
        return None
    
    def suggest_alternatives(self, failed_command: str, available_commands: List[str]) -> List[str]:
        """Suggest alternative commands when user input fails"""
        suggestions = []
        
        for command in available_commands:
            similarity = SequenceMatcher(None, failed_command.lower(), command.lower()).ratio()
            if similarity > 0.4:
                suggestions.append((command, similarity))
        
        # Sort by similarity and return top 3
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [cmd for cmd, _ in suggestions[:3]]
    
    def generate_helpful_error_message(self, error_type: str, context: Dict = None) -> str:
        """Generate helpful error messages with suggestions"""
        
        if error_type == "command_not_found":
            return (
                "🤔 I didn't understand that command. Here's what I can help with:\n\n"
                "💬 **Natural Language** (just talk to me!):\n"
                "• \"Show me my portfolio\"\n"
                "• \"What's Bitcoin's price?\"\n"
                "• \"Research Ethereum\"\n\n"
                "📝 **Commands**:\n"
                "• `/portfolio` - View your holdings\n"
                "• `/research <token>` - Token analysis\n"
                "• `/summarynow` - Chat summary\n"
                "• `/help` - Full command list"
            )
        
        elif error_type == "invalid_token":
            return (
                "🔍 I couldn't find that token. Try these popular ones:\n\n"
                "🪙 **Major Tokens**:\n"
                "• Bitcoin (BTC)\n"
                "• Ethereum (ETH)\n"
                "• Solana (SOL)\n"
                "• Cardano (ADA)\n\n"
                "💡 **Tip**: Use the full name or symbol (e.g., 'Bitcoin' or 'BTC')"
            )
        
        elif error_type == "missing_parameters":
            command = context.get('command', 'command') if context else 'command'
            return (
                f"📝 The `{command}` command needs more information.\n\n"
                f"**Examples**:\n"
                f"• `/{command} BTC` - for Bitcoin\n"
                f"• `/{command} Ethereum` - for Ethereum\n\n"
                f"💬 **Or just say**: \"Research Bitcoin\" or \"Check Ethereum price\""
            )
        
        elif error_type == "rate_limit":
            return (
                "⏳ I'm processing a lot of requests right now. Please wait a moment and try again.\n\n"
                "💡 **While you wait**, you can:\n"
                "• Use `/status` to check bot health\n"
                "• Use `/help` to explore features\n"
                "• Ask me questions about crypto in general"
            )
        
        elif error_type == "api_error":
            return (
                "🔧 I'm having trouble connecting to external services right now.\n\n"
                "🔄 **Please try**:\n"
                "• Waiting a moment and trying again\n"
                "• Using a different command\n"
                "• Checking `/status` for system health\n\n"
                "💬 I can still help with general questions and conversation!"
            )
        
        else:
            return (
                "❓ Something went wrong, but I'm here to help!\n\n"
                "🤖 **Try**:\n"
                "• Rephrasing your request\n"
                "• Using `/help` for available commands\n"
                "• Just talking to me naturally\n\n"
                "💬 I understand natural language, so feel free to ask in your own words!"
            )
    
    def learn_from_correction(self, user_id: int, original: str, corrected: str, accepted: bool):
        """Learn from user corrections to improve future suggestions"""
        from persistent_user_context import user_context_manager
        
        if accepted:
            # Save successful correction
            user_context_manager.save_correction(user_id, original, corrected, "accepted")
            
            # Learn preference if it's a token name
            words = corrected.split()
            for word in words:
                if word.upper() in ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'LINK', 'MATIC', 'AVAX']:
                    user_context_manager.learn_preference(
                        user_id, 
                        f"preferred_token_format_{word.lower()}", 
                        word.upper(), 
                        "correction", 
                        0.8
                    )
        else:
            # Save rejected correction to avoid suggesting it again
            user_context_manager.save_correction(user_id, original, corrected, "rejected")
    
    def handle_error(self, error: Exception, context: str = None) -> Dict[str, any]:
        """Handle errors and provide user-friendly responses"""
        try:
            error_type = type(error).__name__
            error_message = str(error)
            
            # Generate user-friendly error message
            if "API" in error_message or "rate limit" in error_message.lower():
                user_message = "🔄 I'm experiencing high demand right now. Please try again in a moment."
                suggestion = "Wait a few seconds and try your request again."
            elif "network" in error_message.lower() or "connection" in error_message.lower():
                user_message = "🌐 I'm having trouble connecting to external services. Please try again."
                suggestion = "Check your internet connection and try again."
            elif "timeout" in error_message.lower():
                user_message = "⏱️ That request took too long. Let me try a simpler approach."
                suggestion = "Try breaking your request into smaller parts."
            elif "permission" in error_message.lower() or "unauthorized" in error_message.lower():
                user_message = "🔒 I don't have permission to access that resource."
                suggestion = "Contact an administrator if you need access to this feature."
            else:
                user_message = "❌ Something went wrong. Let me try to help you differently."
                suggestion = "Try rephrasing your request or use the /help command."
            
            return {
                "handled": True,
                "user_message": user_message,
                "suggestion": suggestion,
                "error_type": error_type,
                "context": context,
                "timestamp": str(logger.handlers[0].formatter.formatTime(logger.makeRecord("", 0, "", 0, "", (), None)) if logger.handlers else "")
            }
            
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
            return {
                "handled": False,
                "user_message": "❌ I encountered an unexpected error. Please try again.",
                "suggestion": "Use the /help command for assistance.",
                "error_type": "ErrorHandlerError",
                "context": context
            }

# Global instance
error_handler = IntelligentErrorHandler()