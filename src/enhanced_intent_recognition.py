# src/enhanced_intent_recognition.py
"""
Enhanced Intent Recognition System for Möbius AI Assistant
Advanced natural language processing for better intent detection and conversation flow assignment.
"""

import re
import logging
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import sqlite3

logger = logging.getLogger(__name__)

@dataclass
class IntentMatch:
    """Represents a matched intent with confidence and context"""
    intent: str
    confidence: float
    matched_patterns: List[str]
    context_clues: List[str]
    extracted_entities: Dict[str, Any]
    suggested_flow: Optional[str] = None
    disambiguation_needed: bool = False

class EnhancedIntentRecognizer:
    """Advanced intent recognition with natural language understanding"""
    
    def __init__(self, db_path: str = "data/agent_memory.db"):
        self.db_path = db_path
        self.intent_patterns = {}
        self.entity_extractors = {}
        self.context_analyzers = {}
        self.load_intent_patterns()
        self.setup_entity_extractors()
        self.setup_context_analyzers()
        
    def load_intent_patterns(self):
        """Load intent patterns from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM intent_patterns')
                
                for row in cursor.fetchall():
                    pattern_id, intent, pattern, threshold, context_clues, disambiguation = row
                    
                    if intent not in self.intent_patterns:
                        self.intent_patterns[intent] = []
                    
                    try:
                        self.intent_patterns[intent].append({
                            'pattern_id': pattern_id,
                            'regex': re.compile(pattern, re.IGNORECASE),
                            'threshold': threshold,
                            'context_clues': json.loads(context_clues) if context_clues else [],
                            'disambiguation': json.loads(disambiguation) if disambiguation else []
                        })
                    except (json.JSONDecodeError, re.error) as e:
                        logger.warning(f"Error loading pattern {pattern_id}: {e}")
                        
        except Exception as e:
            logger.error(f"Error loading intent patterns: {e}")
    
    def setup_entity_extractors(self):
        """Setup entity extraction patterns"""
        self.entity_extractors = {
            'crypto_token': {
                'patterns': [
                    r'\b([A-Z]{2,10})\b',  # Token symbols
                    r'\b(bitcoin|btc|ethereum|eth|cardano|ada|solana|sol|polygon|matic|chainlink|link|uniswap|uni|aave|compound|maker|mkr|yearn|yfi|curve|crv|sushi|sushiswap|pancakeswap|cake|binance coin|bnb|dogecoin|doge|shiba inu|shib|avalanche|avax|terra|luna|cosmos|atom|polkadot|dot|kusama|ksm|near|algorand|algo|tezos|xtz|fantom|ftm|harmony|one|elrond|egld|theta|tfuel|vechain|vet|enjin|enj|chiliz|chz|basic attention token|bat|decentraland|mana|the sandbox|sand|axie infinity|axs|gala|flow|icp|internet computer|filecoin|fil|helium|hnt|arweave|ar)\b',
                ],
                'normalize': lambda x: x.upper() if len(x) <= 5 else x.title()
            },
            'price_amount': {
                'patterns': [
                    r'\$([0-9,]+\.?[0-9]*)',  # Dollar amounts
                    r'([0-9,]+\.?[0-9]*)\s*(?:dollars?|usd|bucks?)',
                ],
                'normalize': lambda x: float(x.replace(',', ''))
            },
            'time_period': {
                'patterns': [
                    r'\b(today|yesterday|last\s+(?:week|month|year|day)|past\s+(?:\d+\s+)?(?:days?|weeks?|months?|years?))\b',
                    r'\b(\d+)\s*(days?|weeks?|months?|years?)\s*ago\b',
                    r'\bsince\s+(\d{4}|\d{1,2}\/\d{1,2}\/\d{4})\b'
                ],
                'normalize': lambda x: x.lower().strip()
            },
            'action_type': {
                'patterns': [
                    r'\b(buy|sell|trade|invest|stake|farm|yield|lend|borrow|swap|exchange|hold|hodl)\b',
                ],
                'normalize': lambda x: x.lower()
            },
            'risk_level': {
                'patterns': [
                    r'\b(low|medium|high|conservative|aggressive|safe|risky|dangerous)\s*risk\b',
                    r'\b(safe|risky|dangerous|conservative|aggressive)\b'
                ],
                'normalize': lambda x: x.lower()
            }
        }
    
    def setup_context_analyzers(self):
        """Setup context analysis patterns"""
        self.context_analyzers = {
            'urgency': {
                'high': ['urgent', 'asap', 'immediately', 'right now', 'quickly', 'fast'],
                'medium': ['soon', 'today', 'this week'],
                'low': ['eventually', 'when possible', 'no rush']
            },
            'sentiment': {
                'positive': ['good', 'great', 'excellent', 'amazing', 'bullish', 'optimistic'],
                'negative': ['bad', 'terrible', 'awful', 'bearish', 'pessimistic', 'worried'],
                'neutral': ['okay', 'fine', 'normal', 'standard']
            },
            'experience_level': {
                'beginner': ['new', 'beginner', 'novice', 'first time', 'just started', 'learning'],
                'intermediate': ['some experience', 'intermediate', 'familiar with'],
                'advanced': ['experienced', 'advanced', 'expert', 'professional', 'veteran']
            },
            'question_type': {
                'what': ['what is', 'what are', 'what does', 'define', 'explain'],
                'how': ['how to', 'how do', 'how does', 'how can', 'process', 'steps'],
                'when': ['when to', 'when should', 'timing', 'best time'],
                'where': ['where to', 'where can', 'which platform', 'which exchange'],
                'why': ['why should', 'why is', 'reason', 'benefit', 'advantage']
            }
        }
    
    def analyze_intent(self, user_input: str, context: Dict[str, Any] = None) -> IntentMatch:
        """Analyze user input and determine intent with high accuracy"""
        if not user_input or not user_input.strip():
            return IntentMatch(
                intent="unknown",
                confidence=0.0,
                matched_patterns=[],
                context_clues=[],
                extracted_entities={}
            )
        
        # Extract entities first
        entities = self.extract_entities(user_input)
        
        # Analyze context
        context_analysis = self.analyze_context(user_input, context or {})
        
        # Find matching intents
        intent_matches = []
        
        for intent, patterns in self.intent_patterns.items():
            for pattern_info in patterns:
                match = pattern_info['regex'].search(user_input)
                if match:
                    # Calculate confidence based on pattern match and context
                    confidence = self.calculate_confidence(
                        user_input, pattern_info, entities, context_analysis
                    )
                    
                    if confidence >= pattern_info['threshold']:
                        intent_matches.append({
                            'intent': intent,
                            'confidence': confidence,
                            'pattern_id': pattern_info['pattern_id'],
                            'matched_text': match.group(0),
                            'context_clues': pattern_info['context_clues'],
                            'disambiguation': pattern_info['disambiguation']
                        })
        
        # If no pattern matches, use fallback analysis
        if not intent_matches:
            return self.fallback_intent_analysis(user_input, entities, context_analysis)
        
        # Sort by confidence and return best match
        intent_matches.sort(key=lambda x: x['confidence'], reverse=True)
        best_match = intent_matches[0]
        
        # Check if disambiguation is needed
        disambiguation_needed = (
            len(intent_matches) > 1 and 
            intent_matches[1]['confidence'] > 0.7 and
            abs(best_match['confidence'] - intent_matches[1]['confidence']) < 0.2
        )
        
        return IntentMatch(
            intent=best_match['intent'],
            confidence=best_match['confidence'],
            matched_patterns=[best_match['matched_text']],
            context_clues=best_match['context_clues'],
            extracted_entities=entities,
            suggested_flow=self.suggest_conversation_flow(best_match['intent'], entities),
            disambiguation_needed=disambiguation_needed
        )
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text using pattern matching"""
        entities = {}
        
        for entity_type, config in self.entity_extractors.items():
            matches = []
            for pattern in config['patterns']:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    value = match.group(1) if match.groups() else match.group(0)
                    normalized = config['normalize'](value)
                    matches.append(normalized)
            
            if matches:
                entities[entity_type] = matches[0] if len(matches) == 1 else matches
        
        return entities
    
    def analyze_context(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze contextual information from text and conversation context"""
        analysis = {}
        
        for context_type, categories in self.context_analyzers.items():
            scores = {}
            for category, keywords in categories.items():
                score = sum(1 for keyword in keywords if keyword.lower() in text.lower())
                if score > 0:
                    scores[category] = score
            
            if scores:
                analysis[context_type] = max(scores, key=scores.get)
        
        # Add conversation context
        if context:
            analysis['conversation_context'] = context
        
        return analysis
    
    def calculate_confidence(self, text: str, pattern_info: Dict, entities: Dict, context: Dict) -> float:
        """Calculate confidence score for intent match"""
        base_confidence = 0.6  # Base confidence for pattern match
        
        # Boost confidence based on context clues
        context_boost = 0.0
        for clue in pattern_info['context_clues']:
            if clue.lower() in text.lower():
                context_boost += 0.1
        
        # Boost confidence based on extracted entities
        entity_boost = 0.0
        if entities:
            entity_boost = min(0.2, len(entities) * 0.05)
        
        # Boost confidence based on context analysis
        context_analysis_boost = 0.0
        if context:
            context_analysis_boost = min(0.1, len(context) * 0.02)
        
        # Calculate final confidence
        confidence = min(1.0, base_confidence + context_boost + entity_boost + context_analysis_boost)
        
        return confidence
    
    def fallback_intent_analysis(self, text: str, entities: Dict, context: Dict) -> IntentMatch:
        """Fallback analysis when no patterns match"""
        
        # Simple keyword-based fallback
        fallback_intents = {
            'get_realtime_price': ['price', 'cost', 'value', 'worth', 'trading at'],
            'get_historical_price': ['history', 'chart', 'performance', 'trend', 'over time'],
            'get_trading_advice': ['buy', 'sell', 'trade', 'invest', 'should i'],
            'learn_crypto_basics': ['what is', 'explain', 'how does', 'learn', 'understand'],
            'find_yield_farming': ['yield', 'farming', 'staking', 'apy', 'rewards'],
            'get_market_overview': ['market', 'overview', 'sentiment', 'happening'],
            'get_crypto_news': ['news', 'updates', 'latest', 'breaking', 'headlines']
        }
        
        best_intent = "unknown"
        best_score = 0
        
        for intent, keywords in fallback_intents.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text.lower())
            if score > best_score:
                best_score = score
                best_intent = intent
        
        confidence = min(0.6, best_score * 0.15) if best_score > 0 else 0.0
        
        return IntentMatch(
            intent=best_intent,
            confidence=confidence,
            matched_patterns=[],
            context_clues=[],
            extracted_entities=entities
        )
    
    def suggest_conversation_flow(self, intent: str, entities: Dict) -> Optional[str]:
        """Suggest the best conversation flow for the given intent and entities"""
        
        # Map intents to conversation flows
        intent_to_flow = {
            'get_realtime_price': 'crypto_price_realtime',
            'get_historical_price': 'crypto_price_historical',
            'get_trading_advice': 'trading_strategy_basic',
            'learn_crypto_basics': 'crypto_education_basics',
            'find_yield_farming': 'defi_yield_opportunities',
            'get_market_overview': 'market_overview',
            'get_crypto_news': 'crypto_news_analysis',
            'analyze_portfolio': 'portfolio_optimization',
            'audit_wallet_security': 'wallet_security_audit',
            'perform_technical_analysis': 'technical_analysis_comprehensive'
        }
        
        base_flow = intent_to_flow.get(intent)
        
        # Modify flow based on entities and context
        if base_flow and entities:
            # If user seems like a beginner, use simpler flows
            if 'experience_level' in entities and entities['experience_level'] == 'beginner':
                if base_flow == 'trading_strategy_basic':
                    return 'crypto_education_basics'
                elif base_flow == 'technical_analysis_comprehensive':
                    return 'crypto_price_realtime'
            
            # If high-value amounts mentioned, suggest security flows
            if 'price_amount' in entities:
                amount = entities['price_amount']
                if isinstance(amount, (int, float)) and amount > 10000:
                    if base_flow in ['crypto_price_realtime', 'trading_strategy_basic']:
                        return 'wallet_security_audit'
        
        return base_flow
    
    def get_disambiguation_questions(self, intent_matches: List[Dict]) -> List[str]:
        """Generate disambiguation questions when multiple intents are possible"""
        
        if len(intent_matches) < 2:
            return []
        
        questions = []
        intents = [match['intent'] for match in intent_matches[:3]]
        
        # Generate contextual questions based on the ambiguous intents
        if 'get_realtime_price' in intents and 'get_historical_price' in intents:
            questions.append("Are you looking for the current price or historical price data?")
        
        if 'get_trading_advice' in intents and 'learn_crypto_basics' in intents:
            questions.append("Are you looking to learn about trading or get specific trading advice?")
        
        if 'find_yield_farming' in intents and 'learn_crypto_basics' in intents:
            questions.append("Do you want to learn about DeFi concepts or find specific yield opportunities?")
        
        # Generic fallback questions
        if not questions:
            questions.append("Could you be more specific about what you're looking for?")
            questions.append("Are you looking for information, advice, or help with a specific action?")
        
        return questions[:2]  # Return max 2 questions
    
    def update_intent_confidence(self, intent: str, user_feedback: bool, context: Dict = None):
        """Update intent recognition based on user feedback"""
        
        # This would be used to improve the system over time
        # For now, just log the feedback
        logger.info(f"Intent feedback: {intent} - {'positive' if user_feedback else 'negative'}")
        
        # In a production system, this would update pattern weights and thresholds
        # based on user feedback to improve accuracy over time

# Global instance for easy access
enhanced_intent_recognizer = EnhancedIntentRecognizer()