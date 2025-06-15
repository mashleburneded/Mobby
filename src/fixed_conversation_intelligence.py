# src/fixed_conversation_intelligence.py - Fixed version with safe regex patterns
import asyncio
import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class IntentCategory(Enum):
    """Categories of user intents"""
    PRICE_QUERY = "price_query"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    TRADING_SIGNALS = "trading_signals"
    DEFI_RESEARCH = "defi_research"
    WALLET_OPERATIONS = "wallet_operations"
    MARKET_ANALYSIS = "market_analysis"
    NEWS_RESEARCH = "news_research"
    TECHNICAL_ANALYSIS = "technical_analysis"
    GENERAL_CRYPTO = "general_crypto"
    CASUAL_CHAT = "casual_chat"
    HELP_SUPPORT = "help_support"

@dataclass
class SimpleIntentAnalysis:
    """Simplified intent analysis result"""
    primary_intent: IntentCategory
    confidence: float
    entities: Dict[str, Any]
    processing_time: float

class SimpleIntentClassifier:
    """Simplified intent classifier with safe patterns"""
    
    def __init__(self):
        self.intent_keywords = {
            IntentCategory.PRICE_QUERY: ["price", "cost", "value", "worth", "quote", "current"],
            IntentCategory.PORTFOLIO_MANAGEMENT: ["portfolio", "holdings", "balance", "assets", "investments"],
            IntentCategory.TRADING_SIGNALS: ["trading", "signals", "buy", "sell", "trade", "recommendations"],
            IntentCategory.DEFI_RESEARCH: ["defi", "yield", "farming", "liquidity", "staking", "apy", "protocol"],
            IntentCategory.WALLET_OPERATIONS: ["wallet", "address", "transaction", "transfer", "send", "receive"],
            IntentCategory.MARKET_ANALYSIS: ["market", "analysis", "overview", "sentiment", "trends", "bullish", "bearish"],
            IntentCategory.NEWS_RESEARCH: ["news", "updates", "announcement", "events", "sentiment", "social"],
            IntentCategory.TECHNICAL_ANALYSIS: ["technical", "chart", "indicators", "rsi", "macd", "support", "resistance"],
            IntentCategory.GENERAL_CRYPTO: ["crypto", "bitcoin", "ethereum", "blockchain", "altcoin", "cryptocurrency"],
            IntentCategory.CASUAL_CHAT: ["hello", "hi", "hey", "thanks", "thank", "good", "great", "awesome", "ok", "bye"],
            IntentCategory.HELP_SUPPORT: ["help", "how", "what", "explain", "tutorial", "guide", "support"]
        }
        
        # Safe regex patterns for entity extraction
        self.entity_patterns = {
            "cryptocurrency": r"\b(?:BTC|ETH|SOL|ADA|DOT|AVAX|MATIC|LINK|UNI|AAVE|COMP|MKR|SNX|CRV|YFI|SUSHI)\b",
            "price": r"\$?\d+(?:,\d{3})*(?:\.\d{2})?",
            "percentage": r"\d+(?:\.\d+)?\s*%",
            "wallet_address": r"0x[a-fA-F0-9]{40}",
            "amount": r"\d+(?:\.\d+)?\s*\w+"
        }
    
    async def classify_message(self, message: str, user_id: int) -> SimpleIntentAnalysis:
        """Classify message intent using keyword matching"""
        start_time = time.time()
        
        message_lower = message.lower()
        intent_scores = {}
        
        # Score each intent based on keyword matches
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in message_lower:
                    score += 1
            
            # Normalize by number of keywords
            intent_scores[intent] = score / len(keywords) if keywords else 0
        
        # Find best intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            primary_intent = best_intent[0]
            confidence = min(best_intent[1] * 2, 1.0)  # Scale confidence
        else:
            primary_intent = IntentCategory.GENERAL_CRYPTO
            confidence = 0.5
        
        # Extract entities
        entities = await self._extract_entities(message)
        
        processing_time = time.time() - start_time
        
        return SimpleIntentAnalysis(
            primary_intent=primary_intent,
            confidence=confidence,
            entities=entities,
            processing_time=processing_time
        )
    
    async def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities using safe regex patterns"""
        entities = {}
        
        try:
            for entity_type, pattern in self.entity_patterns.items():
                matches = re.findall(pattern, message, re.IGNORECASE)
                if matches:
                    entities[entity_type] = matches
        except Exception as e:
            logger.warning(f"Entity extraction error: {e}")
        
        return entities

# Global instance
simple_classifier = SimpleIntentClassifier()

# Convenience function
async def analyze_message_safely(message: str, user_id: int) -> SimpleIntentAnalysis:
    """Safely analyze message with simplified classifier"""
    return await simple_classifier.classify_message(message, user_id)