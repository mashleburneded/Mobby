#!/usr/bin/env python3
"""
IMPROVED NATURAL LANGUAGE PROCESSOR
===================================
Enhanced NLP with better protocol name extraction and TVL query handling.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    intent: str
    protocol_name: Optional[str] = None
    query_type: Optional[str] = None  # tvl, price, volume, etc.
    confidence: float = 0.0

class ImprovedNLPProcessor:
    """Enhanced NLP processor with better protocol extraction"""
    
    def __init__(self):
        # Known protocols for better matching
        self.known_protocols = {
            'paradex', 'hyperliquid', 'lido', 'uniswap', 'aave', 'compound', 'makerdao', 
            'curve', 'balancer', 'sushiswap', 'pancakeswap', '1inch', 'yearn', 'convex',
            'frax', 'rocket pool', 'eigenlayer', 'pendle', 'morpho', 'euler', 'radiant',
            'venus', 'benqi', 'trader joe', 'platypus', 'stargate', 'synapse', 'hop',
            'across', 'celer', 'multichain', 'anyswap', 'thorchain', 'osmosis', 'juno',
            'terra', 'anchor', 'mirror', 'astroport', 'prism', 'mars', 'kujira',
            'comdex', 'crescent', 'sommelier', 'umee', 'stride', 'quicksilver'
        }
        
        # Query type patterns
        self.query_patterns = {
            'tvl': [
                r'(?i).*tvl.*(?:of|for)\s+(\w+)',
                r'(?i).*total\s+value\s+locked.*(?:of|for)\s+(\w+)',
                r'(?i).*(\w+).*tvl',
                r'(?i).*what.*tvl.*(\w+)',
                r'(?i).*(\w+).*total\s+value'
            ],
            'price': [
                r'(?i).*price.*(?:of|for)\s+(\w+)',
                r'(?i).*(\w+).*price',
                r'(?i).*what.*price.*(\w+)',
                r'(?i).*(\w+).*cost'
            ],
            'volume': [
                r'(?i).*volume.*(?:of|for)\s+(\w+)',
                r'(?i).*(\w+).*volume',
                r'(?i).*trading.*volume.*(\w+)'
            ],
            'research': [
                r'(?i).*research.*(\w+)',
                r'(?i).*tell.*me.*about.*(\w+)',
                r'(?i).*info.*(?:on|about).*(\w+)',
                r'(?i).*(\w+).*information'
            ]
        }
    
    def extract_protocol_name(self, text: str) -> Optional[str]:
        """Extract protocol name from text using multiple strategies"""
        text_lower = text.lower()
        
        # Strategy 1: Direct protocol name matching
        for protocol in self.known_protocols:
            if protocol in text_lower:
                return protocol
        
        # Strategy 2: Pattern-based extraction
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    potential_protocol = match.group(1).lower()
                    # Filter out common words that aren't protocols
                    if potential_protocol not in ['what', 'the', 'is', 'of', 'for', 'on', 'about', 'me', 'you', 'it', 'this', 'that']:
                        return potential_protocol
        
        # Strategy 3: Extract last meaningful word after common question words
        question_words = ['what', 'whats', 'how', 'tell', 'show', 'get', 'find']
        words = text_lower.split()
        
        # Remove question words and common words
        filtered_words = []
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word and clean_word not in question_words and clean_word not in ['is', 'the', 'of', 'for', 'on', 'about', 'tvl', 'price', 'volume']:
                filtered_words.append(clean_word)
        
        # Return the last meaningful word (likely the protocol)
        if filtered_words:
            return filtered_words[-1]
        
        return None
    
    def determine_query_type(self, text: str) -> str:
        """Determine what type of query this is"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['tvl', 'total value locked', 'total value']):
            return 'tvl'
        elif any(word in text_lower for word in ['price', 'cost', 'worth', 'value']):
            return 'price'
        elif any(word in text_lower for word in ['volume', 'trading volume']):
            return 'volume'
        elif any(word in text_lower for word in ['research', 'info', 'information', 'about', 'tell me']):
            return 'research'
        else:
            return 'research'  # Default to research
    
    def process_query(self, text: str) -> QueryResult:
        """Process a natural language query and extract intent and entities"""
        protocol_name = self.extract_protocol_name(text)
        query_type = self.determine_query_type(text)
        
        # Determine intent based on query type
        if query_type == 'tvl':
            intent = 'tvl_request'
        elif query_type == 'price':
            intent = 'price_request'
        elif query_type == 'volume':
            intent = 'volume_request'
        else:
            intent = 'research_request'
        
        # Calculate confidence based on protocol recognition
        confidence = 0.8 if protocol_name and protocol_name in self.known_protocols else 0.6
        
        return QueryResult(
            intent=intent,
            protocol_name=protocol_name,
            query_type=query_type,
            confidence=confidence
        )

# Global instance
improved_nlp = ImprovedNLPProcessor()

def process_natural_language_query(text: str) -> QueryResult:
    """Main function to process natural language queries"""
    return improved_nlp.process_query(text)