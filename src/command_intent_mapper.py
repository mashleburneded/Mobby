# src/command_intent_mapper.py
"""
Command-Intent Mapping System for Möbius AI Assistant
Maps natural language intents to specific commands and provides intelligent routing
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CommandMapping:
    """Mapping between intent and command"""
    command: str
    confidence_threshold: float
    natural_language_patterns: List[str]
    example_phrases: List[str]
    parameters_extraction: Optional[Dict[str, str]] = None

class CommandIntentMapper:
    """Maps natural language intents to specific bot commands"""
    
    def __init__(self):
        self.command_mappings = self._initialize_command_mappings()
        self.intent_to_command = self._build_intent_mapping()
        
    def _initialize_command_mappings(self) -> Dict[str, CommandMapping]:
        """Initialize comprehensive command mappings"""
        return {
            # Core commands
            "help": CommandMapping(
                command="help",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(help|assistance|support|guide|how to|tutorial)",
                    r"(what can you do|capabilities|features|commands)",
                    r"(show me|tell me).*?(commands|options|features)"
                ],
                example_phrases=[
                    "I need help",
                    "What can you do?",
                    "Show me the commands",
                    "How do I use this bot?"
                ]
            ),
            
            "menu": CommandMapping(
                command="menu",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(menu|options|main menu|show menu)",
                    r"(what.*options|available.*features)",
                    r"(navigation|browse|explore)"
                ],
                example_phrases=[
                    "Show me the menu",
                    "What are my options?",
                    "Main menu please"
                ]
            ),
            
            # Price and market data
            "price": CommandMapping(
                command="research",  # Maps to research command for price data
                confidence_threshold=0.7,
                natural_language_patterns=[
                    r"(price|cost|value|worth).*?(btc|bitcoin|eth|ethereum|\$\w+|\w+coin)",
                    r"(how much|what'?s the price|current price|latest price)",
                    r"(check price|get price|price of|show price)"
                ],
                example_phrases=[
                    "What's the price of Bitcoin?",
                    "Check ETH price",
                    "How much is Solana worth?",
                    "Show me BTC value"
                ],
                parameters_extraction={
                    "symbol": r"(BTC|ETH|SOL|ADA|DOT|LINK|UNI|AAVE|MATIC|AVAX|ATOM|NEAR|FTM|ALGO|XRP|LTC|BCH|bitcoin|ethereum|solana|cardano|polkadot|chainlink|uniswap|aave|polygon|avalanche|cosmos|near|fantom|algorand|ripple|litecoin|bitcoin cash)"
                }
            ),
            
            # Portfolio management
            "portfolio": CommandMapping(
                command="portfolio",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(portfolio|holdings|balance|assets|investments)",
                    r"(my (coins|tokens|crypto|investments))",
                    r"(track|monitor|watch).*?(portfolio|holdings)",
                    r"(show|check|view).*?(portfolio|holdings|balance)"
                ],
                example_phrases=[
                    "Show my portfolio",
                    "Check my holdings",
                    "View my crypto balance",
                    "Track my investments"
                ]
            ),
            
            # Alerts and notifications
            "alerts": CommandMapping(
                command="alert",
                confidence_threshold=0.7,
                natural_language_patterns=[
                    r"(alert|notify|notification|remind).*?(when|if|price)",
                    r"(set.*?alert|create.*?alert|add.*?alert)",
                    r"(tell me when|let me know when|notify me when)",
                    r"(watch|monitor).*?(price|value|change)"
                ],
                example_phrases=[
                    "Alert me when BTC hits $100k",
                    "Set an alert for ETH at $3000",
                    "Notify me when Solana goes up 10%",
                    "Tell me when Bitcoin drops below $50k"
                ],
                parameters_extraction={
                    "symbol": r"(BTC|ETH|SOL|ADA|DOT|LINK|UNI|AAVE|MATIC|AVAX|bitcoin|ethereum|solana|cardano|polkadot|chainlink|uniswap|aave|polygon|avalanche)",
                    "price": r"\$[\d,]+(?:\.\d{2})?",
                    "percentage": r"\d+(?:\.\d+)?%"
                }
            ),
            
            # Research and analysis
            "research": CommandMapping(
                command="research",
                confidence_threshold=0.7,
                natural_language_patterns=[
                    r"(research|analyze|analysis|study|investigate)",
                    r"(market.*?(analysis|research|data|trends))",
                    r"(fundamental|technical).*?(analysis|research)",
                    r"(tell me about|what is|explain).*?(protocol|project|coin|token)"
                ],
                example_phrases=[
                    "Research Uniswap",
                    "Analyze the DeFi market",
                    "Tell me about Solana",
                    "What is Ethereum?"
                ],
                parameters_extraction={
                    "protocol": r"(uniswap|aave|compound|makerdao|curve|sushiswap|pancakeswap|1inch|yearn|synthetix|balancer|convex|frax|lido|rocket pool|ethereum|bitcoin|solana|cardano|polkadot|avalanche|polygon|fantom|near|cosmos|algorand|chainlink|the graph|filecoin|helium|internet computer|theta|vechain|elrond|harmony|zilliqa|enjin|basic attention token|decentraland|sandbox|axie infinity|gala|illuvium|star atlas)"
                }
            ),
            
            # Social and community
            "social": CommandMapping(
                command="social",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(social|community|twitter|discord|telegram)",
                    r"(sentiment|buzz|trending|viral)",
                    r"(what.*people.*saying|community.*thinks)"
                ],
                example_phrases=[
                    "Check social sentiment",
                    "What's trending on crypto Twitter?",
                    "Community sentiment analysis"
                ]
            ),
            
            # Multi-chain analysis
            "multichain": CommandMapping(
                command="multichain",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(multi.?chain|cross.?chain|bridge|interoperability)",
                    r"(compare.*chains|chain.*comparison)",
                    r"(ethereum.*solana|btc.*eth|polygon.*avalanche)"
                ],
                example_phrases=[
                    "Compare Ethereum and Solana",
                    "Multi-chain analysis",
                    "Cross-chain opportunities"
                ]
            ),
            
            # Summaries and reports
            "summary": CommandMapping(
                command="summarynow",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(summary|summarize|recap|overview)",
                    r"(what.*happened|key.*points|highlights)",
                    r"(daily.*summary|weekly.*digest|market.*recap)"
                ],
                example_phrases=[
                    "Give me a summary",
                    "What happened today?",
                    "Market recap please",
                    "Summarize the conversation"
                ]
            ),
            
            # Mentions and search
            "mentions": CommandMapping(
                command="mymentions",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(mention|mentioned|talked about|discussed)",
                    r"(find.*mention|search.*mention|who.*said)",
                    r"(when.*mentioned|where.*mentioned)"
                ],
                example_phrases=[
                    "Find my mentions",
                    "Who mentioned me?",
                    "Search for mentions",
                    "When was I mentioned?"
                ]
            ),
            
            # Status and health
            "status": CommandMapping(
                command="status",
                confidence_threshold=0.9,
                natural_language_patterns=[
                    r"(status|health|working|online|available)",
                    r"(bot.*status|system.*status|are you.*working)",
                    r"(check.*status|system.*health)"
                ],
                example_phrases=[
                    "Bot status",
                    "Are you working?",
                    "System health check",
                    "Is everything online?"
                ]
            ),
            
            # Premium features
            "premium": CommandMapping(
                command="premium",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(premium|upgrade|subscription|pro|paid)",
                    r"(advanced.*features|premium.*features)",
                    r"(how.*upgrade|subscription.*plans)"
                ],
                example_phrases=[
                    "Premium features",
                    "How to upgrade?",
                    "Subscription plans",
                    "Advanced features"
                ]
            ),
            
            # Wallet and DeFi
            "wallet": CommandMapping(
                command="create_wallet",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(wallet|create.*wallet|new.*wallet)",
                    r"(defi|yield.*farming|liquidity.*mining)",
                    r"(staking|lending|borrowing)"
                ],
                example_phrases=[
                    "Create a wallet",
                    "DeFi opportunities",
                    "Yield farming options",
                    "Staking rewards"
                ]
            ),
            
            # Scheduling and calendar
            "schedule": CommandMapping(
                command="schedule",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(schedule|calendar|meeting|appointment)",
                    r"(book.*time|set.*meeting|calendly)",
                    r"(available.*times|schedule.*call)"
                ],
                example_phrases=[
                    "Schedule a meeting",
                    "Book a call",
                    "Set up appointment",
                    "Check availability"
                ]
            ),
            
            # Additional commands
            "topic": CommandMapping(
                command="topic",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(topic|subject|theme|discussion)",
                    r"(what.*topic|current.*topic|change.*topic)",
                    r"(talk about|discuss|focus on)"
                ],
                example_phrases=[
                    "What's the current topic?",
                    "Change topic to DeFi",
                    "Let's talk about NFTs"
                ]
            ),
            
            "weekly_summary": CommandMapping(
                command="weekly_summary",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(weekly.*summary|week.*recap|weekly.*digest)",
                    r"(this.*week|past.*week|week.*overview)",
                    r"(weekly.*report|week.*highlights)"
                ],
                example_phrases=[
                    "Weekly summary",
                    "What happened this week?",
                    "Weekly market recap"
                ]
            ),
            
            "whosaid": CommandMapping(
                command="whosaid",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(who.*said|who.*mentioned|who.*talked)",
                    r"(find.*who|search.*who|locate.*who)",
                    r"(attribution|source|original.*speaker)"
                ],
                example_phrases=[
                    "Who said that?",
                    "Find who mentioned Bitcoin",
                    "Who was talking about DeFi?"
                ]
            ),
            
            "llama": CommandMapping(
                command="llama",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(llama|llama.*ai|meta.*llama)",
                    r"(advanced.*ai|llama.*model|meta.*ai)"
                ],
                example_phrases=[
                    "Use Llama AI",
                    "Switch to Llama model",
                    "Advanced AI analysis"
                ]
            ),
            
            "arkham": CommandMapping(
                command="arkham",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(arkham|arkham.*intelligence|blockchain.*analytics)",
                    r"(on.*chain.*analysis|wallet.*tracking|address.*analysis)"
                ],
                example_phrases=[
                    "Arkham analysis",
                    "On-chain intelligence",
                    "Wallet tracking"
                ]
            ),
            
            "nansen": CommandMapping(
                command="nansen",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(nansen|nansen.*analytics|smart.*money)",
                    r"(whale.*tracking|smart.*money.*analysis)"
                ],
                example_phrases=[
                    "Nansen analytics",
                    "Smart money tracking",
                    "Whale analysis"
                ]
            ),
            
            "set_calendly": CommandMapping(
                command="set_calendly",
                confidence_threshold=0.8,
                natural_language_patterns=[
                    r"(set.*calendly|calendly.*link|calendly.*url)",
                    r"(configure.*calendar|setup.*calendly)"
                ],
                example_phrases=[
                    "Set Calendly link",
                    "Configure calendar",
                    "Setup Calendly integration"
                ]
            ),
            
            "mcp_status": CommandMapping(
                command="mcp_status",
                confidence_threshold=0.9,
                natural_language_patterns=[
                    r"(mcp.*status|server.*status|system.*status)",
                    r"(backend.*status|service.*health|infrastructure)"
                ],
                example_phrases=[
                    "MCP server status",
                    "Check system health",
                    "Backend status"
                ]
            )
        }
    
    def _build_intent_mapping(self) -> Dict[str, str]:
        """Build reverse mapping from intent to command"""
        mapping = {}
        for intent, command_mapping in self.command_mappings.items():
            mapping[intent] = command_mapping.command
        return mapping
    
    def map_intent_to_command(self, intent: str, text: str, confidence: float) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Map an intent to a specific command with parameters"""
        
        # Direct intent mapping
        if intent in self.command_mappings:
            command_mapping = self.command_mappings[intent]
            
            # Check confidence threshold
            if confidence >= command_mapping.confidence_threshold:
                # Extract parameters if defined
                parameters = {}
                if command_mapping.parameters_extraction:
                    parameters = self._extract_parameters(text, command_mapping.parameters_extraction)
                
                return command_mapping.command, parameters
        
        # Pattern-based fallback mapping
        for intent_name, command_mapping in self.command_mappings.items():
            for pattern in command_mapping.natural_language_patterns:
                if re.search(pattern, text.lower()):
                    # Extract parameters
                    parameters = {}
                    if command_mapping.parameters_extraction:
                        parameters = self._extract_parameters(text, command_mapping.parameters_extraction)
                    
                    return command_mapping.command, parameters
        
        return None
    
    def _extract_parameters(self, text: str, extraction_patterns: Dict[str, str]) -> Dict[str, Any]:
        """Extract parameters from text using regex patterns"""
        parameters = {}
        
        for param_name, pattern in extraction_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if len(matches) == 1:
                    parameters[param_name] = matches[0]
                else:
                    parameters[param_name] = matches
        
        return parameters
    
    def get_command_suggestions(self, intent: str) -> List[str]:
        """Get example phrases for a given intent"""
        if intent in self.command_mappings:
            return self.command_mappings[intent].example_phrases
        return []
    
    def get_all_intents(self) -> List[str]:
        """Get all available intents"""
        return list(self.command_mappings.keys())
    
    def get_command_for_intent(self, intent: str) -> Optional[str]:
        """Get the command name for a given intent"""
        return self.intent_to_command.get(intent)

# Global instance
command_intent_mapper = CommandIntentMapper()

def map_natural_language_to_command(intent: str, text: str, confidence: float) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Main function to map natural language to commands"""
    return command_intent_mapper.map_intent_to_command(intent, text, confidence)

def get_command_suggestions_for_intent(intent: str) -> List[str]:
    """Get suggestions for a given intent"""
    return command_intent_mapper.get_command_suggestions(intent)

def demo_map_natural_language_to_command(text: str) -> Dict[str, Any]:
    """Demo function to map natural language to commands"""
    # Simple pattern matching for demo
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['price', 'cost', 'value']):
        return {
            "success": True,
            "command": "price",
            "confidence": 0.8,
            "parameters": {"symbol": "BTC" if "bitcoin" in text_lower else "ETH"}
        }
    elif any(word in text_lower for word in ['alert', 'notify', 'notification']):
        return {
            "success": True,
            "command": "alert",
            "confidence": 0.9,
            "parameters": {}
        }
    elif any(word in text_lower for word in ['trending', 'trend', 'popular']):
        return {
            "success": True,
            "command": "trending",
            "confidence": 0.8,
            "parameters": {}
        }
    elif any(word in text_lower for word in ['summary', 'overview', 'recap']):
        return {
            "success": True,
            "command": "summary",
            "confidence": 0.7,
            "parameters": {}
        }
    elif any(word in text_lower for word in ['portfolio', 'holdings', 'balance']):
        return {
            "success": True,
            "command": "portfolio",
            "confidence": 0.8,
            "parameters": {}
        }
    elif any(word in text_lower for word in ['news', 'updates', 'latest']):
        return {
            "success": True,
            "command": "news",
            "confidence": 0.7,
            "parameters": {}
        }
    elif any(word in text_lower for word in ['tvl', 'defi', 'protocol', 'hyperliquid', 'uniswap']):
        return {
            "success": True,
            "command": "defi",
            "confidence": 0.8,
            "parameters": {"protocol": "hyperliquid" if "hyperliquid" in text_lower else "general"}
        }
    else:
        return {"success": False}