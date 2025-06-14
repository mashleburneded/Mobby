# src/real_natural_language_fix.py
"""
REAL Natural Language Fix - Actually works with existing commands
No exaggerated claims, just practical improvements that work
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Types of commands the bot can handle"""
    PRICE = "price"
    PORTFOLIO = "portfolio"
    RESEARCH = "research"
    HELP = "help"
    SUMMARY = "summary"
    ALERTS = "alerts"
    STATUS = "status"
    LLAMA = "llama"
    ARKHAM = "arkham"
    NANSEN = "nansen"
    SOCIAL = "social"
    UNKNOWN = "unknown"

@dataclass
class ParsedCommand:
    """Result of parsing natural language"""
    command_type: CommandType
    parameters: Dict[str, Any]
    confidence: float
    original_text: str
    suggested_command: str

class RealNaturalLanguageProcessor:
    """Actually working natural language processor for existing commands"""

    def __init__(self):
        # Real patterns that actually work with existing commands
        self.command_patterns = {
            CommandType.PRICE: [
                # Price queries
                r"(?:what'?s|show|get|tell me|check)\s+(?:the\s+)?(?:current\s+)?price\s+(?:of\s+|for\s+)?(\w+)",
                r"(\w+)\s+price(?:\s+(?:now|today|current|latest))?",
                r"how much (?:is|does|costs?)\s+(\w+)(?:\s+(?:worth|cost|trading|going for))?",
                r"price\s+(?:of|for)\s+(\w+)",
                r"(\w+)\s+(?:current|latest|today'?s)\s+(?:price|value|cost)",
                r"how\s+much\s+for\s+one\s+(\w+)",
                r"(\w+)\s+(?:price\s+)?check",
                r"what'?s\s+(\w+)\s+trading\s+at",
                r"give\s+me\s+the\s+latest\s+(\w+)\s+price",
                r"(\w+)\s+value\s+(?:now|today)",
            ],

            CommandType.PORTFOLIO: [
                r"(?:show|check|view|display)\s+(?:my\s+)?portfolio",
                r"(?:my\s+)?portfolio(?:\s+(?:status|overview|summary))?",
                r"how\s+(?:is|are)\s+(?:my\s+)?(?:portfolio|investments?|holdings?)\s+(?:doing|performing)",
                r"portfolio\s+(?:performance|analysis|review)",
                r"(?:show|view)\s+my\s+(?:crypto\s+)?assets",
                r"investment\s+overview",
                r"portfolio\s+status\s+report",
                r"my\s+crypto\s+investments",
                r"(?:check|view)\s+(?:my\s+)?(?:holdings|investments)",
                r"investment\s+summary",
                r"portfolio\s+breakdown",
            ],

            CommandType.RESEARCH: [
                r"(?:research|analyze|tell me about|info on|information about)\s+(\w+)",
                r"what\s+(?:is|are)\s+(\w+)(?:\s+(?:token|coin|crypto))?",
                r"(\w+)\s+(?:research|analysis|info|information)",
                r"(?:give me|show me)\s+(?:info|information|details)\s+(?:on|about)\s+(\w+)",
            ],

            CommandType.HELP: [
                r"^(?:help|assistance|what can you do|commands?)$",
                r"how\s+(?:do\s+i|to)\s+(?:use|work with)\s+(?:this|you|the bot)",
                r"(?:show|list)\s+(?:commands?|features?|capabilities)",
            ],

            CommandType.SUMMARY: [
                r"(?:summarize|summary)\s+(?:today|conversation|chat|messages?)",
                r"(?:generate|create|make)\s+(?:a\s+)?summary",
                r"(?:daily|today'?s)\s+summary",
                r"what\s+(?:happened|was discussed)\s+today",
            ],

            CommandType.ALERTS: [
                r"(?:show|check|view|list)\s+(?:my\s+)?alerts?",
                r"(?:manage|edit|delete)\s+alerts?",
                r"alert\s+(?:settings?|management|list)",
                r"(?:set|create|add)\s+(?:an?\s+)?alert\s+(?:for\s+)?(\w+)\s+(?:at|when|if)\s+\$?(\d+(?:\.\d+)?)",
            ],

            CommandType.STATUS: [
                r"(?:bot\s+)?status",
                r"how\s+(?:are\s+you|is\s+the\s+bot)\s+(?:doing|working)",
                r"(?:system\s+)?(?:health|status|info)",
            ],

            CommandType.LLAMA: [
                r"(?:llama|defillama)\s+(?:protocol\s+)?(\w+)",
                r"(?:defi\s+)?protocol\s+(\w+)",
                r"(\w+)\s+(?:protocol|defi)\s+(?:info|data|stats)",
            ],

            # Add yield/DeFi patterns
            'yield': [
                r'find\s+yield\s+opportunities',
                r'best\s+yield\s+farming\s+options',
                r'high\s+apy\s+staking',
                r'defi\s+yield\s+opportunities',
                r'where\s+can\s+i\s+earn\s+yield',
                r'show\s+me\s+farming\s+opportunities',
                r'best\s+staking\s+rewards',
                r'liquidity\s+mining\s+options',
                r'yield\s+farming',
                r'staking\s+rewards',
                r'farming\s+opportunities',
                r'earn\s+yield',
                r'apy\s+opportunities',
                r'defi\s+farming',
                r'yield\s+(?:farming|opportunities)',
                r'(?:find|show|get)\s+yield',
                r'(?:best|high)\s+(?:apy|yield)',
                r'(?:staking|farming)\s+(?:rewards|opportunities)',
            ],
        }

        # Common crypto symbols and their variations
        self.crypto_symbols = {
            'bitcoin': 'BTC', 'btc': 'BTC',
            'ethereum': 'ETH', 'eth': 'ETH', 'ether': 'ETH',
            'solana': 'SOL', 'sol': 'SOL',
            'cardano': 'ADA', 'ada': 'ADA',
            'polkadot': 'DOT', 'dot': 'DOT',
            'chainlink': 'LINK', 'link': 'LINK',
            'polygon': 'MATIC', 'matic': 'MATIC',
            'avalanche': 'AVAX', 'avax': 'AVAX',
            'uniswap': 'UNI', 'uni': 'UNI',
            'aave': 'AAVE',
            'compound': 'COMP', 'comp': 'COMP',
        }

    def parse_natural_language(self, text: str) -> ParsedCommand:
        """Parse natural language into command and parameters"""
        text = text.lower().strip()

        # Try to match each command type
        for command_type, patterns in self.command_patterns.items():
            # Handle yield patterns specially
            if command_type == 'yield':
                for pattern in patterns:
                    if re.search(pattern, text):
                        return ParsedCommand(
                            command_type='yield',
                            command_string='/yield',
                            parameters=[],
                            confidence=0.8,
                            entities=[]
                        )
                continue
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return self._create_parsed_command(command_type, match, text)

        # If no pattern matches, try keyword-based detection
        return self._fallback_keyword_detection(text)

    def _create_parsed_command(self, command_type: CommandType, match: re.Match, original_text: str) -> ParsedCommand:
        """Create a parsed command from a regex match"""
        parameters = {}
        confidence = 0.8

        if command_type == CommandType.PRICE:
            # Extract cryptocurrency symbol
            if match.groups():
                symbol = match.group(1).lower()
                normalized_symbol = self.crypto_symbols.get(symbol, symbol.upper())
                parameters['symbol'] = normalized_symbol
                suggested_command = f"/price {normalized_symbol}"
            else:
                suggested_command = "/price BTC"

        elif command_type == CommandType.RESEARCH:
            if match.groups():
                token = match.group(1).lower()
                normalized_token = self.crypto_symbols.get(token, token.upper())
                parameters['token'] = normalized_token
                suggested_command = f"/research {normalized_token}"
            else:
                suggested_command = "/research BTC"

        elif command_type == CommandType.ALERTS:
            if len(match.groups()) >= 2:
                symbol = match.group(1).lower()
                price = match.group(2)
                normalized_symbol = self.crypto_symbols.get(symbol, symbol.upper())
                parameters['symbol'] = normalized_symbol
                parameters['price'] = float(price)
                suggested_command = f"/alert {normalized_symbol} {price}"
            else:
                suggested_command = "/alerts"

        elif command_type == CommandType.LLAMA:
            if match.groups():
                protocol = match.group(1).lower()
                parameters['protocol'] = protocol
                suggested_command = f"/llama protocol {protocol}"
            else:
                suggested_command = "/llama"

        else:
            # Simple commands without parameters
            command_map = {
                CommandType.PORTFOLIO: "/portfolio",
                CommandType.HELP: "/help",
                CommandType.SUMMARY: "/summarynow",
                CommandType.STATUS: "/status",
            }
            suggested_command = command_map.get(command_type, "/help")

        return ParsedCommand(
            command_type=command_type,
            parameters=parameters,
            confidence=confidence,
            original_text=original_text,
            suggested_command=suggested_command
        )

    def _fallback_keyword_detection(self, text: str) -> ParsedCommand:
        """Fallback keyword-based detection"""
        words = text.split()

        # Check for crypto symbols
        for word in words:
            if word in self.crypto_symbols:
                # If we find a crypto symbol, assume it's a price query
                normalized_symbol = self.crypto_symbols[word]
                return ParsedCommand(
                    command_type=CommandType.PRICE,
                    parameters={'symbol': normalized_symbol},
                    confidence=0.6,
                    original_text=text,
                    suggested_command=f"/price {normalized_symbol}"
                )

        # Check for common keywords
        if any(word in text for word in ['portfolio', 'holdings', 'investments']):
            return ParsedCommand(
                command_type=CommandType.PORTFOLIO,
                parameters={},
                confidence=0.5,
                original_text=text,
                suggested_command="/portfolio"
            )

        if any(word in text for word in ['help', 'commands', 'what can you do']):
            return ParsedCommand(
                command_type=CommandType.HELP,
                parameters={},
                confidence=0.7,
                original_text=text,
                suggested_command="/help"
            )

        # Default to unknown
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            parameters={},
            confidence=0.0,
            original_text=text,
            suggested_command="/help"
        )

    def convert_to_command(self, parsed: ParsedCommand) -> str:
        """Convert parsed command back to a bot command"""
        return parsed.suggested_command

# Global instance
real_nlp = RealNaturalLanguageProcessor()

def process_natural_language_message(text: str) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Process natural language and return whether it should be converted to a command

    Returns:
        (should_convert, command_string, metadata)
    """
    parsed = real_nlp.parse_natural_language(text)

    # Only convert if confidence is reasonable
    if parsed.confidence >= 0.5:
        return True, parsed.suggested_command, {
            'command_type': parsed.command_type.value,
            'parameters': parsed.parameters,
            'confidence': parsed.confidence,
            'original_text': parsed.original_text
        }

    return False, "", {
        'command_type': 'unknown',
        'confidence': parsed.confidence,
        'original_text': text
    }

def get_natural_language_examples() -> List[str]:
    """Get examples of natural language that the bot understands"""
    return [
        "What's the price of Bitcoin?",
        "Show me my portfolio",
        "Research Ethereum for me",
        "Set an alert for BTC at $50000",
        "Tell me about Uniswap protocol",
        "Summarize today's conversation",
        "How much is SOL worth?",
        "Check my alerts",
        "What can you do?",
        "Bot status"
    ]

# Test function
async def test_natural_language_processing():
    """Test the natural language processing"""
    test_cases = [
        "What's the price of Bitcoin?",
        "Show me my portfolio",
        "Research Ethereum",
        "Tell me about Uniswap",
        "Help",
        "BTC price",
        "Set alert for ETH at $3000",
        "How much is Solana worth?",
        "Portfolio status",
        "Bot status"
    ]

    print("Testing Natural Language Processing:")
    print("=" * 50)

    for text in test_cases:
        should_convert, command, metadata = process_natural_language_message(text)

        if should_convert:
            print(f"✅ '{text}' -> {command} (confidence: {metadata['confidence']:.2f})")
        else:
            print(f"❌ '{text}' -> No conversion (confidence: {metadata['confidence']:.2f})")

    print("\nNatural Language Examples:")
    for example in get_natural_language_examples():
        print(f"  • {example}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_natural_language_processing())