# src/enhanced_nlp.py
"""
Enhanced Natural Language Processing for better query understanding
Fixes issues with TVL queries and protocol name extraction
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class QueryIntent:
    intent_type: str
    confidence: float
    entities: Dict[str, str]
    protocol_name: Optional[str] = None
    metric_type: Optional[str] = None
    chain_name: Optional[str] = None

class EnhancedNLP:
    """Enhanced NLP processor with better entity extraction"""
    
    def __init__(self):
        # Enhanced protocol patterns - more comprehensive
        self.protocol_patterns = [
            # Direct protocol mentions
            r'\b(uniswap|aave|compound|makerdao|curve|balancer|sushiswap|pancakeswap)\b',
            r'\b(1inch|yearn|convex|frax|rocket\s*pool|eigenlayer|pendle|morpho)\b',
            r'\b(euler|radiant|venus|benqi|trader\s*joe|platypus|stargate)\b',
            r'\b(synapse|hop|across|celer|multichain|anyswap|thorchain)\b',
            r'\b(osmosis|juno|terra|anchor|mirror|astroport|prism|mars)\b',
            r'\b(kujira|comdex|crescent|sommelier|umee|stride|quicksilver)\b',
            r'\b(lido|ethereum|bitcoin|polygon|arbitrum|optimism|avalanche)\b',
            r'\b(fantom|harmony|cosmos|chainlink|solana|cardano|polkadot)\b',
            r'\b(hyperliquid|paradex|dydx|gmx|gains|kwenta|lyra|dopex)\b',
            r'\b(jupiter|raydium|orca|marinade|drift|mango|serum|phoenix)\b',
            r'\b(blur|opensea|x2y2|looksrare|foundation|superrare)\b'
        ]
        
        # TVL query patterns - more specific
        self.tvl_patterns = [
            r'(?i)(?:what.*?is.*?the.*?)?tvl.*?(?:of|for)\s+(\w+)',
            r'(?i)(?:what.*?is.*?)?(\w+).*?tvl',
            r'(?i)total.*?value.*?locked.*?(?:of|for|on)\s+(\w+)',
            r'(?i)(\w+).*?total.*?value.*?locked',
            r'(?i)tvl.*?(\w+)',
            r'(?i)(\w+).*?tvl.*?(?:data|info|information)',
            r'(?i)show.*?me.*?(?:the.*?)?tvl.*?(?:of|for)\s+(\w+)',
            r'(?i)get.*?tvl.*?(?:of|for)\s+(\w+)'
        ]
        
        # Gas price patterns
        self.gas_patterns = [
            r'(?i)gas.*?price.*?(?:on|for)\s+(\w+)',
            r'(?i)(\w+).*?gas.*?(?:price|fee|cost)',
            r'(?i)gas.*?(?:on|for)\s+(\w+)',
            r'(?i)(\w+).*?gas',
            r'(?i)gas.*?(\w+).*?chain'
        ]
        
        # Chain mappings for better recognition
        self.chain_mappings = {
            'eth': 'ethereum',
            'btc': 'bitcoin',
            'matic': 'polygon',
            'avax': 'avalanche',
            'ftm': 'fantom',
            'arb': 'arbitrum',
            'op': 'optimism',
            'bsc': 'binance smart chain',
            'sol': 'solana',
            'ada': 'cardano',
            'dot': 'polkadot',
            'atom': 'cosmos',
            'one': 'harmony',
            'near': 'near protocol'
        }
        
        # Protocol mappings for better recognition
        self.protocol_mappings = {
            'uni': 'uniswap',
            'sushi': 'sushiswap',
            'cake': 'pancakeswap',
            'crv': 'curve',
            'bal': 'balancer',
            'comp': 'compound',
            'mkr': 'makerdao',
            'yfi': 'yearn',
            'cvx': 'convex',
            'rpl': 'rocket pool',
            'eigen': 'eigenlayer',
            'pendle': 'pendle',
            'morpho': 'morpho',
            'euler': 'euler',
            'radiant': 'radiant',
            'venus': 'venus',
            'benqi': 'benqi',
            'joe': 'trader joe',
            'ptp': 'platypus',
            'stg': 'stargate',
            'syn': 'synapse',
            'hop': 'hop',
            'across': 'across',
            'celer': 'celer',
            'multi': 'multichain',
            'any': 'anyswap',
            'rune': 'thorchain',
            'osmo': 'osmosis',
            'juno': 'juno',
            'luna': 'terra',
            'anc': 'anchor',
            'mir': 'mirror',
            'astro': 'astroport',
            'prism': 'prism',
            'mars': 'mars',
            'kuji': 'kujira',
            'cmdx': 'comdex',
            'cre': 'crescent',
            'somm': 'sommelier',
            'umee': 'umee',
            'strd': 'stride',
            'qck': 'quicksilver'
        }
        
        # Stop words to ignore when extracting protocol names
        self.stop_words = {
            'what', 'is', 'the', 'of', 'for', 'on', 'in', 'at', 'to', 'from',
            'with', 'by', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over',
            'under', 'again', 'further', 'then', 'once', 'here', 'there',
            'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            'can', 'will', 'just', 'should', 'now', 'tvl', 'total', 'value',
            'locked', 'gas', 'price', 'fee', 'cost', 'show', 'me', 'get',
            'find', 'search', 'look', 'check', 'data', 'info', 'information'
        }
    
    def extract_protocol_name(self, text: str) -> Optional[str]:
        """Extract protocol name from text with improved accuracy"""
        # Input validation and security
        if not text or not isinstance(text, str):
            return None
        
        # Limit input length to prevent DoS
        if len(text) > 1000:
            text = text[:1000]
        
        # Remove dangerous characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\t\n\r')
        
        try:
            text_lower = text.lower().strip()
            
            # First, try direct protocol pattern matching
            for pattern in self.protocol_patterns:
                try:
                    matches = re.findall(pattern, text_lower, re.IGNORECASE)
                    if matches:
                        protocol = matches[0].strip()
                        # Clean up the protocol name
                        protocol = re.sub(r'\s+', ' ', protocol)
                        return self.protocol_mappings.get(protocol, protocol)
                except (re.error, AttributeError, IndexError):
                    continue
            
            # Try TVL-specific extraction
            for pattern in self.tvl_patterns:
                try:
                    match = re.search(pattern, text_lower)
                    if match:
                        potential_protocol = match.group(1).strip()
                        if potential_protocol not in self.stop_words and len(potential_protocol) > 1:
                            return self.protocol_mappings.get(potential_protocol, potential_protocol)
                except (re.error, AttributeError, IndexError):
                    continue
            
            # Fallback: extract any word that might be a protocol
            try:
                words = re.findall(r'\b\w+\b', text_lower)
                for word in words[:20]:  # Limit to first 20 words
                    if (word not in self.stop_words and 
                        len(word) > 2 and 
                        word in self.protocol_mappings):
                        return self.protocol_mappings[word]
            except (re.error, AttributeError):
                pass
            
            # Last resort: look for any capitalized words in original text
            try:
                capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', text)
                for word in capitalized_words[:10]:  # Limit to first 10 words
                    word_lower = word.lower()
                    if word_lower not in self.stop_words and len(word_lower) > 2:
                        return self.protocol_mappings.get(word_lower, word_lower)
            except (re.error, AttributeError):
                pass
            
        except Exception:
            # Catch any other unexpected errors
            pass
        
        return None
    
    def classify_intent(self, text: str) -> str:
        """Classify user intent from text"""
        if not text or not isinstance(text, str):
            return "unknown"
        
        text_lower = text.lower().strip()
        
        # Intent classification patterns
        intent_patterns = {
            'price_check': [
                r'\b(?:price|cost|value)\b',
                r'\b(?:how much|what\'?s the price)\b',
                r'\$\d+',
            ],
            'tvl_query': [
                r'\btvl\b',
                r'\btotal value locked\b',
                r'\bliquidity\b',
            ],
            'research_request': [
                r'\bresearch\b',
                r'\banalyze\b',
                r'\btell me about\b',
                r'\binfo(?:rmation)?\b',
            ],
            'summary_request': [
                r'\bsummar[iy]\b',
                r'\brecap\b',
                r'\boverview\b',
            ],
            'menu_request': [
                r'\bmenu\b',
                r'\bhelp\b',
                r'\bcommands\b',
                r'\boptions\b',
            ],
            'gas_prices': [
                r'\bgas\s+price\b',
                r'\bgas\s+fee\b',
                r'\bgwei\b',
            ],
            'greeting': [
                r'\b(?:hi|hello|hey)\b',
                r'\bgood\s+(?:morning|afternoon|evening)\b',
            ],
            'status_check': [
                r'\bstatus\b',
                r'\bhealth\b',
                r'\bcheck\b',
            ],
        }
        
        # Check each intent pattern
        for intent, patterns in intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        return "general_query"
    
    def extract_chain_name(self, text: str) -> Optional[str]:
        """Extract blockchain name from text"""
        text_lower = text.lower()
        
        # Try gas-specific patterns first
        for pattern in self.gas_patterns:
            match = re.search(pattern, text_lower)
            if match:
                potential_chain = match.group(1).strip()
                if potential_chain not in self.stop_words:
                    return self.chain_mappings.get(potential_chain, potential_chain)
        
        # Check for direct chain mentions
        for short_name, full_name in self.chain_mappings.items():
            if short_name in text_lower or full_name in text_lower:
                return full_name
        
        return None
    
    def detect_intent(self, text: str) -> QueryIntent:
        """Detect intent and extract entities from text"""
        text_lower = text.lower().strip()
        
        # TVL queries
        if any(keyword in text_lower for keyword in ['tvl', 'total value locked', 'total value']):
            protocol_name = self.extract_protocol_name(text)
            return QueryIntent(
                intent_type='tvl_query',
                confidence=0.9 if protocol_name else 0.6,
                entities={'protocol': protocol_name} if protocol_name else {},
                protocol_name=protocol_name,
                metric_type='tvl'
            )
        
        # Gas price queries
        if any(keyword in text_lower for keyword in ['gas', 'gas price', 'gas fee', 'gas cost']):
            chain_name = self.extract_chain_name(text)
            return QueryIntent(
                intent_type='gas_query',
                confidence=0.9 if chain_name else 0.7,
                entities={'chain': chain_name} if chain_name else {},
                chain_name=chain_name,
                metric_type='gas'
            )
        
        # Research queries
        if any(keyword in text_lower for keyword in ['research', 'analyze', 'info', 'information', 'data', 'stats']):
            protocol_name = self.extract_protocol_name(text)
            return QueryIntent(
                intent_type='research_query',
                confidence=0.8 if protocol_name else 0.5,
                entities={'protocol': protocol_name} if protocol_name else {},
                protocol_name=protocol_name,
                metric_type='research'
            )
        
        # Price queries
        if any(keyword in text_lower for keyword in ['price', 'cost', 'value', 'worth', 'trading at']):
            protocol_name = self.extract_protocol_name(text)
            return QueryIntent(
                intent_type='price_query',
                confidence=0.8 if protocol_name else 0.5,
                entities={'protocol': protocol_name} if protocol_name else {},
                protocol_name=protocol_name,
                metric_type='price'
            )
        
        # Summary queries
        if any(keyword in text_lower for keyword in ['summary', 'summarize', 'recap', 'overview']):
            return QueryIntent(
                intent_type='summary_query',
                confidence=0.9,
                entities={},
                metric_type='summary'
            )
        
        # Help queries
        if any(keyword in text_lower for keyword in ['help', 'commands', 'what can you do']):
            return QueryIntent(
                intent_type='help_query',
                confidence=0.9,
                entities={},
                metric_type='help'
            )
        
        # Default: general query
        return QueryIntent(
            intent_type='general_query',
            confidence=0.3,
            entities={},
            metric_type='general'
        )
    
    def clean_protocol_name(self, protocol_name: str) -> str:
        """Clean and normalize protocol name"""
        if not protocol_name:
            return ""
        
        # Remove common prefixes/suffixes
        cleaned = protocol_name.lower().strip()
        cleaned = re.sub(r'^(the|a|an)\s+', '', cleaned)
        cleaned = re.sub(r'\s+(protocol|network|chain|token|coin)$', '', cleaned)
        
        # Handle special cases
        if cleaned in self.protocol_mappings:
            return self.protocol_mappings[cleaned]
        
        return cleaned
    
    def validate_protocol_name(self, protocol_name: str) -> bool:
        """Validate if the extracted protocol name is likely correct"""
        if not protocol_name:
            return False
        
        # Too short or in stop words
        if len(protocol_name) < 2 or protocol_name.lower() in self.stop_words:
            return False
        
        # Known protocol or mapping
        if (protocol_name.lower() in self.protocol_mappings or
            any(protocol_name.lower() in pattern for pattern in self.protocol_patterns)):
            return True
        
        # Has reasonable length and format
        if 2 <= len(protocol_name) <= 20 and re.match(r'^[a-zA-Z][a-zA-Z0-9\s]*$', protocol_name):
            return True
        
        return False

# Global instance
enhanced_nlp = EnhancedNLP()

def process_query(text: str) -> QueryIntent:
    """Process a natural language query and return intent"""
    return enhanced_nlp.detect_intent(text)

def extract_protocol_from_query(text: str) -> Optional[str]:
    """Extract protocol name from query text"""
    protocol = enhanced_nlp.extract_protocol_name(text)
    if protocol and enhanced_nlp.validate_protocol_name(protocol):
        return enhanced_nlp.clean_protocol_name(protocol)
    return None

def extract_chain_from_query(text: str) -> Optional[str]:
    """Extract chain name from query text"""
    return enhanced_nlp.extract_chain_name(text)