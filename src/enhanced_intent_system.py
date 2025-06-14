# src/enhanced_intent_system.py
"""
Enhanced Intent Recognition System for Möbius AI Assistant
Prioritizes built-in commands and integrates real-time data sources
"""

import asyncio
import logging
import re
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum

# Import data sources
from defillama_api import defillama_api, get_protocol_data, search_defi_protocols, get_top_defi_protocols
from crypto_research import query_defillama, get_arkham_data, get_nansen_data

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Enhanced intent types with priority levels"""
    # High priority - built-in commands (should never go to MCP)
    CRYPTO_PRICE = "crypto_price"           # Price queries
    PORTFOLIO_CHECK = "portfolio_check"     # Portfolio/balance queries
    ALERT_MANAGEMENT = "alert_management"   # Alert creation/management
    HELP_REQUEST = "help_request"          # Help and commands
    
    # Medium priority - data queries (use APIs first, MCP as fallback)
    DEFI_PROTOCOL = "defi_protocol"        # DeFi protocol information
    YIELD_FARMING = "yield_farming"        # Yield opportunities
    CHAIN_ANALYSIS = "chain_analysis"      # Blockchain analysis
    MARKET_DATA = "market_data"           # Market analysis
    
    # Low priority - conversational (AI response)
    GREETING = "greeting"                  # Greetings and casual chat
    EXPLANATION = "explanation"            # Educational content
    GENERAL_QUERY = "general_query"       # General questions
    
    # Special cases
    UNKNOWN = "unknown"                   # Unrecognized intent

class ResponseStrategy(Enum):
    """Response strategies with clear priorities"""
    BUILT_IN_COMMAND = "built_in"         # Use built-in command handlers
    LIVE_DATA_API = "live_data"          # Fetch live data from APIs
    AI_WITH_DATA = "ai_with_data"        # AI response enhanced with real data
    SIMPLE_AI = "simple_ai"              # Simple AI response
    TEMPLATE_RESPONSE = "template"        # Pre-defined template
    MCP_FALLBACK = "mcp_fallback"        # MCP as last resort

@dataclass
class EnhancedIntentAnalysis:
    """Enhanced intent analysis with clear routing"""
    intent_type: IntentType
    response_strategy: ResponseStrategy
    confidence: float
    extracted_entities: Dict[str, Any]
    should_respond: bool
    priority_score: float
    data_sources: List[str]  # Which APIs/sources to use
    fallback_strategy: Optional[ResponseStrategy] = None

class EnhancedIntentSystem:
    """Enhanced intent recognition system with smart routing"""
    
    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.crypto_symbols = self._initialize_crypto_symbols()
        self.defi_protocols = self._initialize_defi_protocols()
        self.command_mappings = self._initialize_command_mappings()
        
    def _initialize_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Initialize comprehensive intent patterns"""
        return {
            # High priority - built-in commands
            IntentType.CRYPTO_PRICE: [
                r"(?:price|cost|value|worth)\s+(?:of\s+)?(\w+)",
                r"(\w+)\s+(?:price|cost|value|worth)",
                r"how much (?:is|does|costs?)\s+(\w+)",
                r"what'?s\s+(\w+)\s+(?:price|worth|trading|at)",
                r"check\s+(\w+)\s+price",
                r"(\w+)\s+current\s+price",
                r"show\s+me\s+(\w+)\s+price",
                r"get\s+(\w+)\s+price",
                r"(\w+)\s+quote",
                r"quote\s+for\s+(\w+)",
            ],
            
            IntentType.PORTFOLIO_CHECK: [
                r"(?:my\s+)?portfolio",
                r"(?:my\s+)?(?:holdings|balance|assets)",
                r"show\s+(?:my\s+)?(?:portfolio|holdings|balance)",
                r"check\s+(?:my\s+)?(?:portfolio|balance|holdings)",
                r"what\s+do\s+i\s+(?:have|own|hold)",
                r"(?:my\s+)?wallet\s+balance",
                r"account\s+balance",
            ],
            
            IntentType.ALERT_MANAGEMENT: [
                r"(?:set|create|add|make)\s+(?:an?\s+)?alert",
                r"alert\s+(?:me\s+)?(?:when|if)",
                r"notify\s+(?:me\s+)?(?:when|if)",
                r"(?:tell|let)\s+me\s+know\s+(?:when|if)",
                r"watch\s+(?:for\s+)?(\w+)",
                r"monitor\s+(\w+)",
                r"track\s+(\w+)",
            ],
            
            IntentType.HELP_REQUEST: [
                r"^(?:help|assistance|support)$",
                r"what\s+can\s+you\s+do",
                r"(?:show\s+)?(?:commands|features|capabilities)",
                r"how\s+(?:do\s+i|to)\s+(?:use|work|operate)",
                r"instructions",
                r"guide",
                r"tutorial",
            ],
            
            # Medium priority - data queries
            IntentType.DEFI_PROTOCOL: [
                r"(?:what\s+is|tell\s+me\s+about|info\s+(?:on|about))\s+(\w+)(?:\s+(?:protocol|defi|project))?",
                r"(\w+)\s+(?:protocol|defi|project)\s+(?:info|data|details)",
                r"(?:analyze|analysis\s+of)\s+(\w+)\s+protocol",
                r"(\w+)\s+tvl",
                r"total\s+value\s+locked\s+(\w+)",
                r"(\w+)\s+(?:stats|statistics|metrics)",
                r"defi\s+protocol\s+(\w+)",
                r"protocol\s+(\w+)",
                r"about\s+(\w+)",
                r"(\w+)\s+info",
            ],
            
            IntentType.YIELD_FARMING: [
                r"(?:yield|farming|staking)\s+opportunities",
                r"best\s+(?:yield|apy|apr)",
                r"high\s+(?:yield|apy|apr)",
                r"where\s+to\s+(?:stake|farm|earn)",
                r"(?:liquidity|lp)\s+(?:pools|mining)",
                r"earn\s+(?:interest|yield|rewards)",
                r"passive\s+income",
                r"defi\s+yields?",
            ],
            
            IntentType.CHAIN_ANALYSIS: [
                r"(?:ethereum|eth|bitcoin|btc|solana|sol|polygon|matic|avalanche|avax|bsc|binance)\s+(?:analysis|stats|data)",
                r"compare\s+(?:chains|blockchains)",
                r"chain\s+(?:comparison|analysis)",
                r"(?:tvl|volume)\s+(?:on|across)\s+(?:chains|ethereum|solana|polygon)",
                r"cross.?chain\s+(?:analysis|data)",
                r"multi.?chain\s+(?:analysis|comparison)",
            ],
            
            IntentType.MARKET_DATA: [
                r"market\s+(?:analysis|overview|summary|cap|data)",
                r"crypto\s+market",
                r"(?:total\s+)?market\s+cap",
                r"market\s+trends?",
                r"(?:bull|bear)\s+market",
                r"market\s+sentiment",
                r"crypto\s+(?:trends|analysis|overview)",
            ],
            
            # Low priority - conversational
            IntentType.GREETING: [
                r"^(?:hi|hello|hey|good\s+(?:morning|afternoon|evening)|greetings?)$",
                r"^(?:how\s+are\s+you|what'?s\s+up|sup)$",
                r"^(?:thanks?|thank\s+you|thx)$",
                r"^(?:bye|goodbye|see\s+you|cya)$",
            ],
            
            IntentType.EXPLANATION: [
                r"(?:what\s+is|explain|define)\s+(?:defi|blockchain|crypto|bitcoin|ethereum)",
                r"how\s+(?:does|do)\s+(?:defi|blockchain|crypto|staking|yield\s+farming)\s+work",
                r"(?:explain|tell\s+me\s+about)\s+(?:smart\s+contracts|dapps|nfts)",
                r"difference\s+between\s+(\w+)\s+and\s+(\w+)",
            ],
        }
    
    def _initialize_crypto_symbols(self) -> Dict[str, str]:
        """Initialize cryptocurrency symbols and names"""
        return {
            # Major cryptocurrencies
            'btc': 'bitcoin', 'bitcoin': 'bitcoin',
            'eth': 'ethereum', 'ethereum': 'ethereum',
            'sol': 'solana', 'solana': 'solana',
            'ada': 'cardano', 'cardano': 'cardano',
            'dot': 'polkadot', 'polkadot': 'polkadot',
            'matic': 'polygon', 'polygon': 'polygon',
            'avax': 'avalanche', 'avalanche': 'avalanche',
            'link': 'chainlink', 'chainlink': 'chainlink',
            'uni': 'uniswap', 'uniswap': 'uniswap',
            'aave': 'aave', 'comp': 'compound',
            'mkr': 'maker', 'maker': 'maker',
            'snx': 'synthetix', 'synthetix': 'synthetix',
            'crv': 'curve', 'curve': 'curve',
            'sushi': 'sushiswap', 'sushiswap': 'sushiswap',
            'bnb': 'binancecoin', 'binance': 'binancecoin',
            'usdc': 'usd-coin', 'usdt': 'tether',
            'dai': 'dai', 'frax': 'frax',
        }
    
    def _initialize_defi_protocols(self) -> List[str]:
        """Initialize known DeFi protocols"""
        return [
            'uniswap', 'aave', 'compound', 'makerdao', 'curve',
            'sushiswap', 'pancakeswap', 'balancer', 'yearn',
            'convex', 'lido', 'rocket-pool', 'frax', 'olympus',
            'trader-joe', 'benqi', 'venus', 'anchor', 'terra',
            'osmosis', 'thorchain', 'bancor', 'kyber', 'dydx',
        ]
    
    def _initialize_command_mappings(self) -> Dict[IntentType, str]:
        """Map intents to command handlers"""
        return {
            IntentType.CRYPTO_PRICE: 'handle_price_query',
            IntentType.PORTFOLIO_CHECK: 'handle_portfolio_query',
            IntentType.ALERT_MANAGEMENT: 'handle_alert_query',
            IntentType.HELP_REQUEST: 'handle_help_query',
            IntentType.DEFI_PROTOCOL: 'handle_defi_protocol_query',
            IntentType.YIELD_FARMING: 'handle_yield_query',
            IntentType.CHAIN_ANALYSIS: 'handle_chain_query',
            IntentType.MARKET_DATA: 'handle_market_query',
        }
    
    async def analyze_intent(self, text: str, user_id: int, context: Dict = None) -> EnhancedIntentAnalysis:
        """Analyze user intent with enhanced logic"""
        text_lower = text.lower().strip()
        
        # Check for high-priority built-in commands first
        for intent_type in [IntentType.CRYPTO_PRICE, IntentType.PORTFOLIO_CHECK, 
                           IntentType.ALERT_MANAGEMENT, IntentType.HELP_REQUEST]:
            analysis = self._check_intent_patterns(text_lower, intent_type)
            if analysis and analysis.confidence > 0.7:
                return analysis
        
        # Check for medium-priority data queries
        for intent_type in [IntentType.DEFI_PROTOCOL, IntentType.YIELD_FARMING,
                           IntentType.CHAIN_ANALYSIS, IntentType.MARKET_DATA]:
            analysis = self._check_intent_patterns(text_lower, intent_type)
            if analysis and analysis.confidence > 0.6:
                return analysis
        
        # Check for low-priority conversational intents
        for intent_type in [IntentType.GREETING, IntentType.EXPLANATION]:
            analysis = self._check_intent_patterns(text_lower, intent_type)
            if analysis and analysis.confidence > 0.5:
                return analysis
        
        # Default to general query with AI response
        return EnhancedIntentAnalysis(
            intent_type=IntentType.GENERAL_QUERY,
            response_strategy=ResponseStrategy.SIMPLE_AI,
            confidence=0.3,
            extracted_entities={},
            should_respond=True,
            priority_score=0.3,
            data_sources=[],
            fallback_strategy=ResponseStrategy.MCP_FALLBACK
        )
    
    def _check_intent_patterns(self, text: str, intent_type: IntentType) -> Optional[EnhancedIntentAnalysis]:
        """Check if text matches patterns for specific intent"""
        patterns = self.intent_patterns.get(intent_type, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities = self._extract_entities(match, intent_type)
                confidence = self._calculate_confidence(match, intent_type, text)
                
                return EnhancedIntentAnalysis(
                    intent_type=intent_type,
                    response_strategy=self._get_response_strategy(intent_type),
                    confidence=confidence,
                    extracted_entities=entities,
                    should_respond=True,
                    priority_score=self._get_priority_score(intent_type),
                    data_sources=self._get_data_sources(intent_type),
                    fallback_strategy=self._get_fallback_strategy(intent_type)
                )
        
        return None
    
    def _extract_entities(self, match: re.Match, intent_type: IntentType) -> Dict[str, Any]:
        """Extract entities from regex match"""
        entities = {}
        
        if intent_type == IntentType.CRYPTO_PRICE:
            if match.groups():
                symbol = match.group(1).lower()
                entities['symbol'] = symbol
                entities['normalized_symbol'] = self.crypto_symbols.get(symbol, symbol)
        
        elif intent_type == IntentType.DEFI_PROTOCOL:
            if match.groups():
                protocol = match.group(1).lower()
                entities['protocol'] = protocol
                entities['is_known_protocol'] = protocol in self.defi_protocols
        
        elif intent_type == IntentType.ALERT_MANAGEMENT:
            if match.groups():
                entities['target'] = match.group(1).lower()
        
        return entities
    
    def _calculate_confidence(self, match: re.Match, intent_type: IntentType, text: str) -> float:
        """Calculate confidence score for intent match"""
        base_confidence = 0.8
        
        # Boost confidence for exact matches
        if match.group(0) == text:
            base_confidence += 0.15
        
        # Boost confidence for known entities
        if intent_type == IntentType.CRYPTO_PRICE:
            if match.groups() and match.group(1).lower() in self.crypto_symbols:
                base_confidence += 0.1
        
        elif intent_type == IntentType.DEFI_PROTOCOL:
            if match.groups() and match.group(1).lower() in self.defi_protocols:
                base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _get_response_strategy(self, intent_type: IntentType) -> ResponseStrategy:
        """Get response strategy for intent type"""
        strategy_map = {
            IntentType.CRYPTO_PRICE: ResponseStrategy.LIVE_DATA_API,
            IntentType.PORTFOLIO_CHECK: ResponseStrategy.BUILT_IN_COMMAND,
            IntentType.ALERT_MANAGEMENT: ResponseStrategy.BUILT_IN_COMMAND,
            IntentType.HELP_REQUEST: ResponseStrategy.BUILT_IN_COMMAND,
            IntentType.DEFI_PROTOCOL: ResponseStrategy.LIVE_DATA_API,
            IntentType.YIELD_FARMING: ResponseStrategy.LIVE_DATA_API,
            IntentType.CHAIN_ANALYSIS: ResponseStrategy.LIVE_DATA_API,
            IntentType.MARKET_DATA: ResponseStrategy.AI_WITH_DATA,
            IntentType.GREETING: ResponseStrategy.TEMPLATE_RESPONSE,
            IntentType.EXPLANATION: ResponseStrategy.SIMPLE_AI,
            IntentType.GENERAL_QUERY: ResponseStrategy.SIMPLE_AI,
        }
        return strategy_map.get(intent_type, ResponseStrategy.SIMPLE_AI)
    
    def _get_priority_score(self, intent_type: IntentType) -> float:
        """Get priority score for intent type"""
        priority_map = {
            IntentType.CRYPTO_PRICE: 0.9,
            IntentType.PORTFOLIO_CHECK: 0.9,
            IntentType.ALERT_MANAGEMENT: 0.9,
            IntentType.HELP_REQUEST: 0.8,
            IntentType.DEFI_PROTOCOL: 0.7,
            IntentType.YIELD_FARMING: 0.7,
            IntentType.CHAIN_ANALYSIS: 0.7,
            IntentType.MARKET_DATA: 0.6,
            IntentType.GREETING: 0.4,
            IntentType.EXPLANATION: 0.5,
            IntentType.GENERAL_QUERY: 0.3,
        }
        return priority_map.get(intent_type, 0.3)
    
    def _get_data_sources(self, intent_type: IntentType) -> List[str]:
        """Get data sources for intent type"""
        source_map = {
            IntentType.CRYPTO_PRICE: ['coingecko', 'coinmarketcap'],
            IntentType.DEFI_PROTOCOL: ['defillama', 'coingecko'],
            IntentType.YIELD_FARMING: ['defillama'],
            IntentType.CHAIN_ANALYSIS: ['defillama', 'dune'],
            IntentType.MARKET_DATA: ['coingecko', 'defillama'],
        }
        return source_map.get(intent_type, [])
    
    def _get_fallback_strategy(self, intent_type: IntentType) -> Optional[ResponseStrategy]:
        """Get fallback strategy if primary fails"""
        fallback_map = {
            IntentType.CRYPTO_PRICE: ResponseStrategy.SIMPLE_AI,
            IntentType.DEFI_PROTOCOL: ResponseStrategy.AI_WITH_DATA,
            IntentType.YIELD_FARMING: ResponseStrategy.SIMPLE_AI,
            IntentType.CHAIN_ANALYSIS: ResponseStrategy.SIMPLE_AI,
            IntentType.MARKET_DATA: ResponseStrategy.SIMPLE_AI,
        }
        return fallback_map.get(intent_type)

# Global instance
enhanced_intent_system = EnhancedIntentSystem()

async def analyze_user_intent_enhanced(text: str, user_id: int, context: Dict = None) -> EnhancedIntentAnalysis:
    """Enhanced intent analysis function"""
    return await enhanced_intent_system.analyze_intent(text, user_id, context)