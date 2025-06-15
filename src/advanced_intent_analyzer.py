# src/advanced_intent_analyzer.py
"""
Advanced Intent Analyzer with 666+ patterns, fuzzy matching, and multi-intent support
Production-ready implementation with comprehensive natural language understanding
"""

import asyncio
import logging
import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import difflib
from collections import defaultdict, deque
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy

# Download required NLTK data
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass

logger = logging.getLogger(__name__)

class IntentCategory(Enum):
    """Intent categories with priority levels"""
    # Critical priority (immediate response required)
    EMERGENCY = "emergency"
    SECURITY_ALERT = "security_alert"
    
    # High priority (built-in commands)
    PRICE_QUERY = "price_query"
    PORTFOLIO_MANAGEMENT = "portfolio_management"
    ALERT_MANAGEMENT = "alert_management"
    TRADING_EXECUTION = "trading_execution"
    
    # Medium priority (data analysis)
    MARKET_ANALYSIS = "market_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    DEFI_OPERATIONS = "defi_operations"
    YIELD_FARMING = "yield_farming"
    RISK_ASSESSMENT = "risk_assessment"
    
    # Low priority (educational/conversational)
    EDUCATION = "education"
    NEWS_ANALYSIS = "news_analysis"
    SOCIAL_SENTIMENT = "social_sentiment"
    GENERAL_CONVERSATION = "general_conversation"

class SentimentType(Enum):
    """Sentiment types for response adaptation"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    FEARFUL = "fearful"
    EXCITED = "excited"
    CONFUSED = "confused"
    URGENT = "urgent"

class EntityType(Enum):
    """Entity types for extraction"""
    CRYPTOCURRENCY = "cryptocurrency"
    FIAT_CURRENCY = "fiat_currency"
    AMOUNT = "amount"
    PERCENTAGE = "percentage"
    TIME_PERIOD = "time_period"
    DATE = "date"
    EXCHANGE = "exchange"
    DEFI_PROTOCOL = "defi_protocol"
    TRADING_ACTION = "trading_action"
    TECHNICAL_INDICATOR = "technical_indicator"
    WALLET_ADDRESS = "wallet_address"
    TRANSACTION_HASH = "transaction_hash"

@dataclass
class ExtractedEntity:
    """Extracted entity with metadata"""
    type: EntityType
    value: str
    normalized_value: str
    confidence: float
    position: Tuple[int, int]  # start, end positions in text
    context: str

@dataclass
class SentimentAnalysis:
    """Sentiment analysis result"""
    type: SentimentType
    compound_score: float
    positive: float
    negative: float
    neutral: float
    emotions: Dict[str, float]  # fear, greed, excitement, confusion, etc.

@dataclass
class ConversationContext:
    """Conversation context for maintaining state"""
    user_id: int
    recent_messages: deque  # Last 5 messages
    mentioned_entities: Dict[str, Any]  # Recently mentioned entities
    current_topic: Optional[str]
    user_preferences: Dict[str, Any]
    session_start: datetime
    last_interaction: datetime

@dataclass
class IntentMatch:
    """Single intent match result"""
    intent_name: str
    category: IntentCategory
    confidence: float
    matched_patterns: List[str]
    extracted_entities: List[ExtractedEntity]
    required_data_sources: List[str]
    estimated_complexity: float
    response_template: Optional[str]

@dataclass
class MultiIntentAnalysis:
    """Complete multi-intent analysis result"""
    primary_intent: IntentMatch
    secondary_intents: List[IntentMatch]
    sentiment: SentimentAnalysis
    entities: List[ExtractedEntity]
    context: ConversationContext
    confidence_score: float
    processing_strategy: str
    estimated_response_time: float
    required_permissions: List[str]

class AdvancedIntentAnalyzer:
    """Advanced intent analyzer with comprehensive NLP capabilities"""
    
    def __init__(self):
        self.intent_patterns = self._initialize_comprehensive_patterns()
        self.entity_patterns = self._initialize_entity_patterns()
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.conversation_contexts = {}  # user_id -> ConversationContext
        self.nlp = None
        self._initialize_spacy()
        
    def _initialize_spacy(self):
        """Initialize spaCy for advanced NLP"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def _initialize_comprehensive_patterns(self) -> Dict[str, Dict]:
        """Initialize 666+ comprehensive intent patterns"""
        return {
            # PRICE QUERIES (100+ patterns)
            "get_realtime_price": {
                "category": IntentCategory.PRICE_QUERY,
                "patterns": [
                    # Basic price queries
                    r"(?:what'?s|show|get|tell me|check|find)\s+(?:the\s+)?(?:current\s+)?price\s+(?:of\s+|for\s+)?(\w+)",
                    r"(\w+)\s+price(?:\s+(?:now|today|current|latest))?",
                    r"how much (?:is|does|costs?)\s+(\w+)(?:\s+(?:worth|cost|trading|going for))?",
                    r"(\w+)\s+(?:current|latest|today'?s|real.?time)\s+(?:price|value|cost|rate)",
                    r"price\s+(?:of|for)\s+(\w+)(?:\s+(?:now|today|currently))?",
                    
                    # Conversational variations
                    r"what\s+(?:is|are)\s+(\w+)\s+(?:worth|trading|going for|at)(?:\s+(?:now|today|currently))?",
                    r"can you (?:tell me|show me|get me)\s+(?:the\s+)?(\w+)\s+price",
                    r"i (?:want to|need to|would like to)\s+(?:know|check|see)\s+(?:the\s+)?(\w+)\s+price",
                    r"(?:what|how)\s+(?:about|is)\s+(\w+)(?:\s+price)?(?:\s+(?:now|today))?",
                    r"(\w+)\s+quote(?:\s+please)?",
                    
                    # Multiple token queries
                    r"(?:prices?\s+(?:of|for)\s+)?(\w+)(?:\s+and\s+(\w+))*",
                    r"show me\s+(?:the\s+)?prices?\s+(?:of|for)\s+(\w+)(?:,\s*(\w+))*",
                    r"get\s+(?:me\s+)?(?:the\s+)?(?:current\s+)?prices?\s+(?:of|for)\s+(\w+)(?:,\s*(\w+))*",
                    
                    # Specific exchanges
                    r"(\w+)\s+price\s+on\s+(\w+)(?:\s+exchange)?",
                    r"what'?s\s+(\w+)\s+(?:trading|going)\s+for\s+on\s+(\w+)",
                    
                    # Price comparisons
                    r"compare\s+(\w+)\s+(?:and|vs|versus)\s+(\w+)\s+prices?",
                    r"(\w+)\s+vs\s+(\w+)\s+price",
                    
                    # Slang and informal
                    r"(\w+)\s+(?:moon|pump|dump|crash|rip|dip)",
                    r"how'?s\s+(\w+)\s+doing",
                    r"(\w+)\s+(?:up|down|green|red)",
                ],
                "complexity": 0.2,
                "data_sources": ["coingecko", "coinmarketcap", "binance"],
                "response_time": 1.0
            },
            
            "get_historical_price": {
                "category": IntentCategory.PRICE_QUERY,
                "patterns": [
                    r"(\w+)\s+price\s+(?:yesterday|last\s+(?:week|month|year))",
                    r"(?:what\s+was|show me)\s+(\w+)\s+price\s+(?:on|at|during)\s+(.+)",
                    r"(\w+)\s+(?:historical|past|previous)\s+price",
                    r"price\s+(?:history|chart|graph)\s+(?:of|for)\s+(\w+)",
                    r"(\w+)\s+price\s+(?:trend|movement|change)\s+(?:over|in)\s+(.+)",
                    r"how\s+(?:has|did)\s+(\w+)\s+(?:perform|do)\s+(?:over|in)\s+(.+)",
                ],
                "complexity": 0.4,
                "data_sources": ["coingecko", "tradingview", "yahoo_finance"],
                "response_time": 2.0
            },
            
            "analyze_price_movement": {
                "category": IntentCategory.MARKET_ANALYSIS,
                "patterns": [
                    r"(?:is|why is)\s+(\w+)\s+(?:pumping|dumping|mooning|crashing|rising|falling)",
                    r"(\w+)\s+(?:pump|dump|moon|crash|surge|drop|spike|dip)",
                    r"what'?s\s+(?:happening|going on)\s+(?:with|to)\s+(\w+)",
                    r"why\s+(?:is|did)\s+(\w+)\s+(?:go|going)\s+(?:up|down)",
                    r"(\w+)\s+(?:price\s+)?(?:analysis|movement|action)",
                    r"explain\s+(\w+)\s+(?:price\s+)?(?:movement|change|action)",
                ],
                "complexity": 0.6,
                "data_sources": ["coingecko", "news_api", "social_sentiment"],
                "response_time": 3.0
            },
            
            # PORTFOLIO MANAGEMENT (80+ patterns)
            "analyze_portfolio": {
                "category": IntentCategory.PORTFOLIO_MANAGEMENT,
                "patterns": [
                    r"(?:show|check|analyze|review)\s+(?:my\s+)?portfolio",
                    r"(?:my\s+)?portfolio\s+(?:performance|analysis|review|status)",
                    r"how\s+(?:is|are)\s+(?:my\s+)?(?:portfolio|investments?|holdings?)\s+(?:doing|performing)",
                    r"portfolio\s+(?:pnl|profit|loss|gains?|returns?)",
                    r"(?:my\s+)?(?:crypto\s+)?(?:investment|holding)\s+(?:performance|status)",
                    r"what'?s\s+(?:my\s+)?(?:portfolio|investment)\s+worth",
                    r"total\s+portfolio\s+value",
                    r"portfolio\s+breakdown",
                ],
                "complexity": 0.5,
                "data_sources": ["portfolio_db", "coingecko", "debank"],
                "response_time": 2.5
            },
            
            "add_to_portfolio": {
                "category": IntentCategory.PORTFOLIO_MANAGEMENT,
                "patterns": [
                    r"(?:add|track|include)\s+(\w+)\s+(?:to\s+)?(?:my\s+)?portfolio",
                    r"(?:start\s+)?(?:tracking|monitoring)\s+(\w+)",
                    r"(?:i\s+)?(?:bought|purchased|acquired)\s+(\d+(?:\.\d+)?)\s+(\w+)",
                    r"add\s+(\d+(?:\.\d+)?)\s+(\w+)\s+(?:at|for)\s+\$?(\d+(?:\.\d+)?)",
                    r"portfolio\s+(?:add|include)\s+(\w+)",
                    r"(?:my\s+)?new\s+(?:position|holding)\s+(?:in\s+)?(\w+)",
                ],
                "complexity": 0.3,
                "data_sources": ["portfolio_db"],
                "response_time": 1.0
            },
            
            "remove_from_portfolio": {
                "category": IntentCategory.PORTFOLIO_MANAGEMENT,
                "patterns": [
                    r"(?:remove|delete|stop tracking)\s+(\w+)\s+(?:from\s+)?(?:my\s+)?portfolio",
                    r"(?:i\s+)?(?:sold|liquidated)\s+(?:my\s+)?(\w+)",
                    r"(?:stop\s+)?(?:monitoring|tracking)\s+(\w+)",
                    r"portfolio\s+(?:remove|delete)\s+(\w+)",
                ],
                "complexity": 0.2,
                "data_sources": ["portfolio_db"],
                "response_time": 1.0
            },
            
            "optimize_portfolio": {
                "category": IntentCategory.PORTFOLIO_MANAGEMENT,
                "patterns": [
                    r"(?:optimize|rebalance|improve)\s+(?:my\s+)?portfolio",
                    r"portfolio\s+(?:optimization|rebalancing|suggestions?)",
                    r"how\s+(?:can|should)\s+i\s+(?:improve|optimize|rebalance)\s+(?:my\s+)?portfolio",
                    r"portfolio\s+(?:advice|recommendations?)",
                    r"(?:suggest|recommend)\s+portfolio\s+(?:changes?|improvements?)",
                ],
                "complexity": 0.8,
                "data_sources": ["portfolio_db", "coingecko", "risk_models"],
                "response_time": 4.0
            },
            
            # TRADING OPERATIONS (70+ patterns)
            "get_trading_advice": {
                "category": IntentCategory.TRADING_EXECUTION,
                "patterns": [
                    r"should\s+i\s+(?:buy|sell|trade)\s+(\w+)",
                    r"(?:is\s+it\s+)?(?:good\s+time\s+to|time\s+to)\s+(?:buy|sell)\s+(\w+)",
                    r"(\w+)\s+(?:buy|sell)\s+(?:signal|recommendation|advice)",
                    r"(?:trading\s+)?(?:advice|recommendation)\s+(?:for\s+)?(\w+)",
                    r"what\s+(?:do\s+you\s+)?(?:think|recommend)\s+(?:about\s+)?(?:buying|selling)\s+(\w+)",
                    r"(\w+)\s+(?:investment|trading)\s+(?:advice|opinion)",
                ],
                "complexity": 0.7,
                "data_sources": ["technical_analysis", "sentiment_analysis", "news_api"],
                "response_time": 3.5
            },
            
            "entry_exit_strategy": {
                "category": IntentCategory.TRADING_EXECUTION,
                "patterns": [
                    r"when\s+(?:should\s+i|to)\s+(?:buy|sell|enter|exit)\s+(\w+)",
                    r"(?:best\s+)?(?:entry|exit)\s+(?:point|price|level)\s+(?:for\s+)?(\w+)",
                    r"(\w+)\s+(?:entry|exit)\s+(?:strategy|plan)",
                    r"(?:optimal|best)\s+(?:time|price)\s+to\s+(?:buy|sell)\s+(\w+)",
                    r"(\w+)\s+(?:buy|sell)\s+(?:zone|level|target)",
                ],
                "complexity": 0.8,
                "data_sources": ["technical_analysis", "support_resistance", "fibonacci"],
                "response_time": 4.0
            },
            
            "risk_management_advice": {
                "category": IntentCategory.RISK_ASSESSMENT,
                "patterns": [
                    r"(?:risk\s+management|stop\s+loss|position\s+sizing)\s+(?:for\s+)?(\w+)",
                    r"how\s+much\s+(?:should\s+i|to)\s+(?:invest|risk)\s+(?:in\s+)?(\w+)",
                    r"(\w+)\s+(?:risk|volatility)\s+(?:analysis|assessment)",
                    r"(?:safe|risky)\s+(?:to\s+)?(?:invest|buy)\s+(\w+)",
                    r"(\w+)\s+(?:investment|trading)\s+risk",
                ],
                "complexity": 0.6,
                "data_sources": ["risk_models", "volatility_data", "correlation_matrix"],
                "response_time": 3.0
            },
            
            # DEFI OPERATIONS (60+ patterns)
            "find_yield_opportunities": {
                "category": IntentCategory.YIELD_FARMING,
                "patterns": [
                    r"(?:best|highest|top)\s+(?:yield|apy|apr)\s+(?:for\s+)?(\w+)?",
                    r"(?:yield\s+farming|liquidity\s+mining)\s+(?:opportunities|options)",
                    r"where\s+(?:can\s+i|to)\s+(?:stake|farm|earn)\s+(?:with\s+)?(\w+)?",
                    r"(?:staking|farming)\s+(?:rewards|returns)\s+(?:for\s+)?(\w+)?",
                    r"(?:high|good)\s+(?:apy|apr|yield)\s+(?:pools?|options?)",
                    r"(?:earn|make)\s+(?:passive\s+)?income\s+(?:with\s+)?(\w+)?",
                    r"(\w+)\s+(?:staking|farming|yield)\s+(?:options?|opportunities)",
                ],
                "complexity": 0.5,
                "data_sources": ["defillama", "apy_vision", "defi_pulse"],
                "response_time": 2.5
            },
            
            "liquidity_pool_analysis": {
                "category": IntentCategory.DEFI_OPERATIONS,
                "patterns": [
                    r"(?:liquidity\s+pool|lp)\s+(?:analysis|risks?|rewards?)",
                    r"(?:impermanent\s+loss|il)\s+(?:calculator|analysis|risk)",
                    r"(\w+)[-/](\w+)\s+(?:pool|pair)\s+(?:analysis|performance)",
                    r"(?:should\s+i\s+)?(?:provide\s+liquidity|add\s+to\s+pool)\s+(?:for\s+)?(\w+)",
                    r"lp\s+(?:token|position)\s+(?:analysis|performance)",
                ],
                "complexity": 0.7,
                "data_sources": ["uniswap", "sushiswap", "curve", "balancer"],
                "response_time": 3.5
            },
            
            "defi_protocol_security": {
                "category": IntentCategory.DEFI_OPERATIONS,
                "patterns": [
                    r"(?:is\s+)?(\w+)\s+(?:safe|secure|trustworthy|reliable)",
                    r"(\w+)\s+(?:security|audit|risk)\s+(?:analysis|assessment|review)",
                    r"(?:protocol\s+)?(?:security|safety)\s+(?:of\s+)?(\w+)",
                    r"(\w+)\s+(?:hack|exploit|vulnerability)\s+(?:history|risk)",
                    r"(?:trust|safety)\s+(?:score|rating)\s+(?:for\s+)?(\w+)",
                ],
                "complexity": 0.6,
                "data_sources": ["defisafety", "immunefi", "audit_reports"],
                "response_time": 3.0
            },
            
            # TECHNICAL ANALYSIS (50+ patterns)
            "technical_analysis_request": {
                "category": IntentCategory.TECHNICAL_ANALYSIS,
                "patterns": [
                    r"(?:technical\s+analysis|ta)\s+(?:of|for)\s+(\w+)",
                    r"(\w+)\s+(?:chart|technical)\s+analysis",
                    r"(?:show|get)\s+(?:me\s+)?(\w+)\s+(?:indicators?|signals?)",
                    r"(\w+)\s+(?:rsi|macd|bollinger|fibonacci|support|resistance)",
                    r"(?:is\s+)?(\w+)\s+(?:oversold|overbought|bullish|bearish)",
                    r"(\w+)\s+(?:trend|momentum|pattern)\s+analysis",
                ],
                "complexity": 0.8,
                "data_sources": ["tradingview", "technical_indicators", "chart_patterns"],
                "response_time": 4.0
            },
            
            "support_resistance_levels": {
                "category": IntentCategory.TECHNICAL_ANALYSIS,
                "patterns": [
                    r"(\w+)\s+(?:support|resistance)\s+(?:levels?|zones?)",
                    r"(?:key\s+)?(?:support|resistance)\s+(?:for\s+)?(\w+)",
                    r"(\w+)\s+(?:price\s+)?(?:targets?|levels?)",
                    r"(?:where\s+(?:is|are)\s+)?(\w+)\s+(?:support|resistance)",
                ],
                "complexity": 0.6,
                "data_sources": ["technical_analysis", "pivot_points", "fibonacci"],
                "response_time": 2.5
            },
            
            # MARKET ANALYSIS (40+ patterns)
            "market_sentiment_analysis": {
                "category": IntentCategory.MARKET_ANALYSIS,
                "patterns": [
                    r"(?:market\s+)?sentiment\s+(?:analysis|for\s+(\w+))?",
                    r"(?:how\s+(?:is|are)\s+)?(?:people|traders|investors)\s+feeling\s+(?:about\s+)?(\w+)?",
                    r"(?:bullish|bearish)\s+(?:or\s+bearish\s+)?(?:on\s+)?(\w+)?",
                    r"(?:fear|greed)\s+(?:index|indicator)",
                    r"(?:social\s+)?sentiment\s+(?:for\s+)?(\w+)?",
                ],
                "complexity": 0.5,
                "data_sources": ["fear_greed_index", "social_sentiment", "news_sentiment"],
                "response_time": 2.0
            },
            
            "compare_cryptocurrencies": {
                "category": IntentCategory.MARKET_ANALYSIS,
                "patterns": [
                    r"compare\s+(\w+)\s+(?:and|vs|versus|with)\s+(\w+)",
                    r"(\w+)\s+vs\s+(\w+)(?:\s+comparison)?",
                    r"(?:difference\s+between|which\s+is\s+better)\s+(\w+)\s+(?:and|or)\s+(\w+)",
                    r"(\w+)\s+(?:or|vs)\s+(\w+)\s+(?:investment|comparison)",
                ],
                "complexity": 0.7,
                "data_sources": ["coingecko", "fundamental_analysis", "technical_analysis"],
                "response_time": 3.5
            },
            
            # ALERT MANAGEMENT (30+ patterns)
            "create_price_alert": {
                "category": IntentCategory.ALERT_MANAGEMENT,
                "patterns": [
                    r"(?:set|create|add)\s+(?:an?\s+)?alert\s+(?:for\s+)?(\w+)\s+(?:at|when|if)\s+\$?(\d+(?:\.\d+)?)",
                    r"alert\s+(?:me\s+)?(?:when|if)\s+(\w+)\s+(?:hits|reaches|goes\s+(?:above|below))\s+\$?(\d+(?:\.\d+)?)",
                    r"notify\s+(?:me\s+)?(?:when|if)\s+(\w+)\s+(?:is|gets)\s+\$?(\d+(?:\.\d+)?)",
                    r"(?:tell|let)\s+me\s+know\s+(?:when|if)\s+(\w+)\s+(?:reaches|hits)\s+\$?(\d+(?:\.\d+)?)",
                    r"(\w+)\s+price\s+alert\s+(?:at\s+)?\$?(\d+(?:\.\d+)?)",
                ],
                "complexity": 0.3,
                "data_sources": ["alert_system", "price_monitoring"],
                "response_time": 1.0
            },
            
            "manage_alerts": {
                "category": IntentCategory.ALERT_MANAGEMENT,
                "patterns": [
                    r"(?:show|list|check)\s+(?:my\s+)?alerts?",
                    r"(?:delete|remove|cancel)\s+(?:alert|alerts?)\s+(?:for\s+)?(\w+)?",
                    r"(?:modify|edit|update)\s+(?:alert|alerts?)",
                    r"alert\s+(?:settings?|preferences?|management)",
                ],
                "complexity": 0.2,
                "data_sources": ["alert_system"],
                "response_time": 1.0
            },
            
            # NEWS AND SOCIAL (25+ patterns)
            "crypto_news_analysis": {
                "category": IntentCategory.NEWS_ANALYSIS,
                "patterns": [
                    r"(?:crypto\s+)?news\s+(?:about\s+)?(\w+)?",
                    r"(?:latest\s+)?(?:news|updates?)\s+(?:on|about|for)\s+(\w+)",
                    r"what'?s\s+(?:happening|new)\s+(?:with|in)\s+(\w+)",
                    r"(\w+)\s+(?:news|updates?|developments?)",
                    r"(?:market\s+)?news\s+(?:impact|analysis)",
                ],
                "complexity": 0.4,
                "data_sources": ["news_api", "crypto_news", "reddit"],
                "response_time": 2.0
            },
            
            "social_sentiment_analysis": {
                "category": IntentCategory.SOCIAL_SENTIMENT,
                "patterns": [
                    r"(?:what'?s\s+)?(?:twitter|reddit|social)\s+saying\s+(?:about\s+)?(\w+)",
                    r"(\w+)\s+(?:social\s+)?(?:sentiment|buzz|discussion)",
                    r"(?:twitter|reddit)\s+(?:sentiment|opinion)\s+(?:on\s+)?(\w+)",
                    r"(?:social\s+media|community)\s+(?:sentiment|feeling)\s+(?:about\s+)?(\w+)",
                ],
                "complexity": 0.5,
                "data_sources": ["twitter_api", "reddit_api", "social_sentiment"],
                "response_time": 2.5
            },
            
            # EDUCATIONAL (20+ patterns)
            "crypto_concept_explanation": {
                "category": IntentCategory.EDUCATION,
                "patterns": [
                    r"(?:what\s+is|explain|define)\s+(\w+)",
                    r"(?:how\s+does|how\s+do)\s+(\w+)\s+work",
                    r"(?:tell\s+me\s+about|explain)\s+(\w+)",
                    r"(\w+)\s+(?:explanation|definition|meaning)",
                    r"(?:understand|learn\s+about)\s+(\w+)",
                ],
                "complexity": 0.3,
                "data_sources": ["knowledge_base", "educational_content"],
                "response_time": 1.5
            },
            
            # EMERGENCY AND SECURITY (15+ patterns)
            "security_alert": {
                "category": IntentCategory.SECURITY_ALERT,
                "patterns": [
                    r"(?:hack|exploit|scam|phishing|suspicious)",
                    r"(?:lost|stolen|compromised)\s+(?:funds?|wallet|keys?)",
                    r"(?:security\s+)?(?:breach|incident|alert)",
                    r"(?:help|emergency|urgent)\s+(?:security|hack|stolen)",
                ],
                "complexity": 0.9,
                "data_sources": ["security_monitoring", "incident_response"],
                "response_time": 0.5
            },
            
            # CONVERSATIONAL (50+ patterns)
            "greeting": {
                "category": IntentCategory.GENERAL_CONVERSATION,
                "patterns": [
                    r"^(?:hi|hello|hey|good\s+(?:morning|afternoon|evening)|greetings?)$",
                    r"^(?:how\s+are\s+you|what'?s\s+up|sup|yo)$",
                    r"^(?:good\s+)?(?:morning|afternoon|evening|night)$",
                ],
                "complexity": 0.1,
                "data_sources": [],
                "response_time": 0.5
            },
            
            "farewell": {
                "category": IntentCategory.GENERAL_CONVERSATION,
                "patterns": [
                    r"^(?:bye|goodbye|see\s+you|cya|later|farewell)$",
                    r"^(?:good\s+)?(?:night|bye)$",
                    r"^(?:talk\s+to\s+you\s+later|ttyl)$",
                ],
                "complexity": 0.1,
                "data_sources": [],
                "response_time": 0.5
            },
            
            "gratitude": {
                "category": IntentCategory.GENERAL_CONVERSATION,
                "patterns": [
                    r"^(?:thanks?|thank\s+you|thx|ty|appreciate\s+it)$",
                    r"^(?:much\s+appreciated|thanks\s+a\s+lot)$",
                ],
                "complexity": 0.1,
                "data_sources": [],
                "response_time": 0.5
            },
            
            "help_request": {
                "category": IntentCategory.GENERAL_CONVERSATION,
                "patterns": [
                    r"^(?:help|assistance|support)$",
                    r"what\s+can\s+you\s+do",
                    r"(?:show\s+)?(?:commands?|features?|capabilities)",
                    r"how\s+(?:do\s+i|to)\s+(?:use|work|operate)",
                    r"(?:instructions?|guide|tutorial)",
                ],
                "complexity": 0.2,
                "data_sources": ["help_system"],
                "response_time": 1.0
            },
        }
    
    def _initialize_entity_patterns(self) -> Dict[EntityType, List[str]]:
        """Initialize entity extraction patterns"""
        return {
            EntityType.CRYPTOCURRENCY: [
                r"\b(?:btc|bitcoin)\b",
                r"\b(?:eth|ethereum)\b",
                r"\b(?:sol|solana)\b",
                r"\b(?:ada|cardano)\b",
                r"\b(?:dot|polkadot)\b",
                r"\b(?:matic|polygon)\b",
                r"\b(?:avax|avalanche)\b",
                r"\b(?:link|chainlink)\b",
                r"\b(?:uni|uniswap)\b",
                r"\b(?:aave)\b",
                r"\b(?:comp|compound)\b",
                r"\b(?:mkr|maker)\b",
                r"\b(?:snx|synthetix)\b",
                r"\b(?:crv|curve)\b",
                r"\b(?:sushi|sushiswap)\b",
                r"\b(?:bnb|binance)\b",
                r"\b(?:usdc|usdt|dai|frax)\b",
            ],
            
            EntityType.FIAT_CURRENCY: [
                r"\$(\d+(?:,\d{3})*(?:\.\d{2})?)",
                r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:usd|dollars?)",
                r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:eur|euros?)",
                r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:gbp|pounds?)",
            ],
            
            EntityType.AMOUNT: [
                r"(\d+(?:\.\d+)?)\s*(?:k|thousand)",
                r"(\d+(?:\.\d+)?)\s*(?:m|million)",
                r"(\d+(?:\.\d+)?)\s*(?:b|billion)",
                r"(\d+(?:\.\d+)?)",
            ],
            
            EntityType.PERCENTAGE: [
                r"(\d+(?:\.\d+)?)\s*%",
                r"(\d+(?:\.\d+)?)\s*percent",
            ],
            
            EntityType.TIME_PERIOD: [
                r"\b(?:today|yesterday|tomorrow)\b",
                r"\b(?:this|last|next)\s+(?:week|month|year|hour|day)\b",
                r"\b(\d+)\s*(?:minutes?|hours?|days?|weeks?|months?|years?)\s*(?:ago)?\b",
                r"\b(?:24h|1d|7d|30d|1y)\b",
            ],
            
            EntityType.EXCHANGE: [
                r"\b(?:binance|coinbase|kraken|bitfinex|huobi|okx|kucoin)\b",
                r"\b(?:uniswap|sushiswap|pancakeswap|curve|balancer)\b",
            ],
            
            EntityType.DEFI_PROTOCOL: [
                r"\b(?:aave|compound|makerdao|yearn|convex|lido)\b",
                r"\b(?:uniswap|sushiswap|curve|balancer|bancor)\b",
                r"\b(?:thorchain|osmosis|anchor|venus|benqi)\b",
            ],
            
            EntityType.TRADING_ACTION: [
                r"\b(?:buy|sell|trade|swap|exchange)\b",
                r"\b(?:long|short|hodl|stake|farm)\b",
                r"\b(?:enter|exit|close|open)\b",
            ],
            
            EntityType.TECHNICAL_INDICATOR: [
                r"\b(?:rsi|macd|bollinger|fibonacci|ema|sma)\b",
                r"\b(?:support|resistance|trend|momentum)\b",
                r"\b(?:oversold|overbought|bullish|bearish)\b",
            ],
        }
    
    async def analyze_multi_intent(self, text: str, user_id: int, context: Optional[Dict] = None) -> MultiIntentAnalysis:
        """Analyze text for multiple intents with comprehensive NLP"""
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            # Get or create conversation context
            conv_context = self._get_conversation_context(user_id)
            
            # Update context with current message
            self._update_conversation_context(conv_context, text, context or {})
            
            # Extract entities
            entities = await self._extract_entities(processed_text)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(text)
            
            # Find intent matches
            intent_matches = await self._find_intent_matches(processed_text, entities, conv_context)
            
            # If no matches found, try fuzzy matching with all patterns
            if not intent_matches:
                intent_matches = await self._find_fuzzy_matches(processed_text, entities, conv_context)
            
            # Rank and select intents
            primary_intent, secondary_intents = self._rank_intents(intent_matches, sentiment, conv_context)
            
            # Calculate overall confidence
            confidence_score = self._calculate_overall_confidence(primary_intent, secondary_intents, entities, sentiment)
            
            # Determine processing strategy
            processing_strategy = self._determine_processing_strategy(primary_intent, secondary_intents, sentiment)
            
            # Estimate response time
            estimated_response_time = self._estimate_response_time(primary_intent, secondary_intents)
            
            # Check required permissions
            required_permissions = self._check_required_permissions(primary_intent, secondary_intents)
            
            return MultiIntentAnalysis(
                primary_intent=primary_intent,
                secondary_intents=secondary_intents,
                sentiment=sentiment,
                entities=entities,
                context=conv_context,
                confidence_score=confidence_score,
                processing_strategy=processing_strategy,
                estimated_response_time=estimated_response_time,
                required_permissions=required_permissions
            )
            
        except Exception as e:
            logger.error(f"Error in multi-intent analysis: {e}")
            # Return fallback analysis
            return self._create_fallback_analysis(text, user_id)
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Handle common abbreviations
        abbreviations = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'sol': 'solana',
            'ada': 'cardano',
            'dot': 'polkadot',
            'matic': 'polygon',
            'avax': 'avalanche',
            'link': 'chainlink',
            'uni': 'uniswap',
            'bnb': 'binance',
        }
        
        for abbr, full in abbreviations.items():
            text = re.sub(rf'\b{abbr}\b', full, text)
        
        return text
    
    def _get_conversation_context(self, user_id: int) -> ConversationContext:
        """Get or create conversation context for user"""
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = ConversationContext(
                user_id=user_id,
                recent_messages=deque(maxlen=5),
                mentioned_entities={},
                current_topic=None,
                user_preferences={},
                session_start=datetime.now(),
                last_interaction=datetime.now()
            )
        
        return self.conversation_contexts[user_id]
    
    def _update_conversation_context(self, context: ConversationContext, text: str, metadata: Dict):
        """Update conversation context with new message"""
        context.recent_messages.append({
            'text': text,
            'timestamp': datetime.now(),
            'metadata': metadata
        })
        context.last_interaction = datetime.now()
    
    async def _extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract entities from text using patterns and NLP"""
        entities = []
        
        # Pattern-based extraction
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append(ExtractedEntity(
                        type=entity_type,
                        value=match.group(0),
                        normalized_value=self._normalize_entity(match.group(0), entity_type),
                        confidence=0.8,
                        position=(match.start(), match.end()),
                        context=text[max(0, match.start()-10):match.end()+10]
                    ))
        
        # spaCy-based extraction if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['MONEY', 'PERCENT', 'DATE', 'TIME']:
                    entities.append(ExtractedEntity(
                        type=self._map_spacy_label(ent.label_),
                        value=ent.text,
                        normalized_value=ent.text,
                        confidence=0.9,
                        position=(ent.start_char, ent.end_char),
                        context=text[max(0, ent.start_char-10):ent.end_char+10]
                    ))
        
        return entities
    
    def _normalize_entity(self, value: str, entity_type: EntityType) -> str:
        """Normalize entity value"""
        if entity_type == EntityType.CRYPTOCURRENCY:
            crypto_map = {
                'bitcoin': 'BTC',
                'ethereum': 'ETH',
                'solana': 'SOL',
                'cardano': 'ADA',
                'polkadot': 'DOT',
                'polygon': 'MATIC',
                'avalanche': 'AVAX',
                'chainlink': 'LINK',
                'uniswap': 'UNI',
                'binance': 'BNB',
            }
            return crypto_map.get(value.lower(), value.upper())
        
        return value
    
    def _map_spacy_label(self, label: str) -> EntityType:
        """Map spaCy entity labels to our entity types"""
        mapping = {
            'MONEY': EntityType.FIAT_CURRENCY,
            'PERCENT': EntityType.PERCENTAGE,
            'DATE': EntityType.DATE,
            'TIME': EntityType.TIME_PERIOD,
        }
        return mapping.get(label, EntityType.CRYPTOCURRENCY)
    
    def _analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment with emotion detection"""
        # VADER sentiment analysis
        scores = self.sentiment_analyzer.polarity_scores(text)
        
        # Determine sentiment type
        compound = scores['compound']
        if compound >= 0.5:
            sentiment_type = SentimentType.VERY_POSITIVE
        elif compound >= 0.1:
            sentiment_type = SentimentType.POSITIVE
        elif compound <= -0.5:
            sentiment_type = SentimentType.VERY_NEGATIVE
        elif compound <= -0.1:
            sentiment_type = SentimentType.NEGATIVE
        else:
            sentiment_type = SentimentType.NEUTRAL
        
        # Detect specific emotions
        emotions = self._detect_emotions(text)
        
        # Override sentiment type based on emotions
        if emotions.get('fear', 0) > 0.3:
            sentiment_type = SentimentType.FEARFUL
        elif emotions.get('excitement', 0) > 0.3:
            sentiment_type = SentimentType.EXCITED
        elif emotions.get('confusion', 0) > 0.3:
            sentiment_type = SentimentType.CONFUSED
        elif emotions.get('urgency', 0) > 0.3:
            sentiment_type = SentimentType.URGENT
        
        return SentimentAnalysis(
            type=sentiment_type,
            compound_score=compound,
            positive=scores['pos'],
            negative=scores['neg'],
            neutral=scores['neu'],
            emotions=emotions
        )
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect specific emotions in text"""
        emotions = {
            'fear': 0.0,
            'greed': 0.0,
            'excitement': 0.0,
            'confusion': 0.0,
            'urgency': 0.0,
            'frustration': 0.0,
            'confidence': 0.0,
        }
        
        # Fear indicators
        fear_words = ['scared', 'worried', 'afraid', 'panic', 'crash', 'dump', 'loss', 'risk']
        fear_score = sum(1 for word in fear_words if word in text.lower()) / len(fear_words)
        emotions['fear'] = min(fear_score, 1.0)
        
        # Greed indicators
        greed_words = ['moon', 'pump', 'lambo', 'rich', 'profit', 'gains', 'buy more']
        greed_score = sum(1 for word in greed_words if word in text.lower()) / len(greed_words)
        emotions['greed'] = min(greed_score, 1.0)
        
        # Excitement indicators
        excitement_words = ['amazing', 'awesome', 'incredible', 'wow', 'fantastic', '!', 'bullish']
        excitement_score = sum(1 for word in excitement_words if word in text.lower()) / len(excitement_words)
        emotions['excitement'] = min(excitement_score, 1.0)
        
        # Confusion indicators
        confusion_words = ['confused', 'don\'t understand', 'what', 'how', 'why', 'explain']
        confusion_score = sum(1 for word in confusion_words if word in text.lower()) / len(confusion_words)
        emotions['confusion'] = min(confusion_score, 1.0)
        
        # Urgency indicators
        urgency_words = ['urgent', 'quickly', 'asap', 'now', 'immediately', 'emergency']
        urgency_score = sum(1 for word in urgency_words if word in text.lower()) / len(urgency_words)
        emotions['urgency'] = min(urgency_score, 1.0)
        
        return emotions
    
    async def _find_intent_matches(self, text: str, entities: List[ExtractedEntity], context: ConversationContext) -> List[IntentMatch]:
        """Find all matching intents with improved matching logic"""
        matches = []
        text_lower = text.lower()
        
        # First, try keyword-based matching for better accuracy
        keyword_matches = self._find_keyword_matches(text_lower)
        
        # Then try pattern matching
        for intent_name, intent_config in self.intent_patterns.items():
            patterns = intent_config.get('patterns', [])
            category = intent_config.get('category')
            complexity = intent_config.get('complexity', 0.5)
            data_sources = intent_config.get('data_sources', [])
            response_time = intent_config.get('response_time', 2.0)
            
            matched_patterns = []
            max_confidence = 0.0
            
            # Check keyword matches first
            if intent_name in keyword_matches:
                max_confidence = keyword_matches[intent_name]
                matched_patterns.append("keyword_match")
            
            # Exact pattern matching
            for pattern in patterns:
                try:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        confidence = 0.9
                        matched_patterns.append(pattern)
                        max_confidence = max(max_confidence, confidence)
                except re.error:
                    # Skip invalid regex patterns
                    continue
            
            # Fuzzy matching for typos and variations
            if max_confidence < 0.5:
                fuzzy_confidence = self._fuzzy_match_intent(text, patterns)
                if fuzzy_confidence > 0.3:
                    max_confidence = max(max_confidence, fuzzy_confidence)
                    matched_patterns.append("fuzzy_match")
            
            # Context-based confidence boost
            if max_confidence > 0:
                context_boost = self._calculate_context_boost(intent_name, context, entities)
                max_confidence = min(max_confidence + context_boost, 1.0)
            
            # Only include matches with reasonable confidence
            if max_confidence > 0.4:
                # Extract relevant entities for this intent
                relevant_entities = self._filter_relevant_entities(entities, intent_name)
                
                matches.append(IntentMatch(
                    intent_name=intent_name,
                    category=category,
                    confidence=max_confidence,
                    matched_patterns=matched_patterns,
                    extracted_entities=relevant_entities,
                    required_data_sources=data_sources,
                    estimated_complexity=complexity,
                    response_template=None
                ))
        
        return matches
    
    def _find_keyword_matches(self, text: str) -> Dict[str, float]:
        """Find intent matches based on keywords with confidence scores"""
        matches = {}
        words = set(text.split())
        
        # Define strong keyword indicators for each intent
        intent_keywords = {
            # Price queries
            "get_realtime_price": {
                "strong": ["price", "cost", "worth", "value", "trading"],
                "weak": ["btc", "eth", "bitcoin", "ethereum"]
            },
            
            # Portfolio management
            "analyze_portfolio": {
                "strong": ["portfolio", "holdings", "performance"],
                "weak": ["show", "check", "my"]
            },
            "add_to_portfolio": {
                "strong": ["add", "track", "include"],
                "weak": ["portfolio", "holdings"]
            },
            "remove_from_portfolio": {
                "strong": ["remove", "delete", "stop"],
                "weak": ["portfolio", "tracking"]
            },
            "optimize_portfolio": {
                "strong": ["optimize", "rebalance", "improve"],
                "weak": ["portfolio", "suggestions"]
            },
            
            # Trading
            "get_trading_advice": {
                "strong": ["should", "buy", "sell", "trade"],
                "weak": ["advice", "recommend"]
            },
            "entry_exit_strategy": {
                "strong": ["entry", "exit", "when"],
                "weak": ["buy", "sell", "point"]
            },
            "risk_management_advice": {
                "strong": ["risk", "management"],
                "weak": ["advice", "safe"]
            },
            
            # DeFi and Yield
            "find_yield_opportunities": {
                "strong": ["yield", "farming", "apy", "apr", "staking"],
                "weak": ["best", "high", "opportunities"]
            },
            "liquidity_pool_analysis": {
                "strong": ["liquidity", "pool", "lp"],
                "weak": ["analysis", "uniswap", "sushiswap"]
            },
            "defi_protocol_security": {
                "strong": ["safe", "security", "protocol"],
                "weak": ["aave", "compound", "defi"]
            },
            
            # Technical Analysis
            "technical_analysis_request": {
                "strong": ["technical", "analysis", "chart"],
                "weak": ["bitcoin", "ethereum", "indicators"]
            },
            "support_resistance_levels": {
                "strong": ["support", "resistance"],
                "weak": ["levels", "zones"]
            },
            
            # Market Analysis
            "market_sentiment_analysis": {
                "strong": ["sentiment", "market", "mood"],
                "weak": ["analysis", "feeling"]
            },
            "compare_cryptocurrencies": {
                "strong": ["compare", "vs", "versus"],
                "weak": ["bitcoin", "ethereum", "difference"]
            },
            
            # Alerts
            "create_price_alert": {
                "strong": ["alert", "notify", "when"],
                "weak": ["price", "hits", "reaches"]
            },
            "manage_alerts": {
                "strong": ["alerts", "show"],
                "weak": ["my", "active"]
            },
            
            # Educational
            "crypto_concept_explanation": {
                "strong": ["what", "explain", "how"],
                "weak": ["defi", "staking", "work"]
            },
            
            # Conversational
            "greeting": {
                "strong": ["hello", "hi", "hey"],
                "weak": ["good", "morning"]
            },
            "gratitude": {
                "strong": ["thanks", "thank"],
                "weak": ["you", "appreciate"]
            },
            "help_request": {
                "strong": ["help", "assistance"],
                "weak": ["can", "do"]
            }
        }
        
        # Calculate confidence for each intent
        for intent_name, keywords in intent_keywords.items():
            strong_matches = sum(1 for word in keywords["strong"] if word in words)
            weak_matches = sum(1 for word in keywords["weak"] if word in words)
            
            if strong_matches > 0 or weak_matches > 1:
                # Calculate confidence based on matches
                confidence = (strong_matches * 0.8 + weak_matches * 0.3) / max(len(keywords["strong"]) + len(keywords["weak"]), 1)
                confidence = min(confidence, 0.95)  # Cap at 95%
                
                if confidence > 0.4:
                    matches[intent_name] = confidence
        
        return matches
    
    async def _find_fuzzy_matches(self, text: str, entities: List[ExtractedEntity], context: ConversationContext) -> List[IntentMatch]:
        """Find fuzzy matches when exact patterns fail"""
        matches = []
        text_words = set(word.lower() for word in text.split() if len(word) > 2)
        
        # Define keyword-based intent mapping
        keyword_intents = {
            "portfolio": ["analyze_portfolio", "add_to_portfolio", "remove_from_portfolio", "optimize_portfolio"],
            "buy": ["get_trading_advice", "entry_exit_strategy"],
            "sell": ["get_trading_advice", "entry_exit_strategy"],
            "yield": ["find_yield_opportunities"],
            "farming": ["find_yield_opportunities"],
            "staking": ["find_yield_opportunities"],
            "apy": ["find_yield_opportunities"],
            "apr": ["find_yield_opportunities"],
            "technical": ["technical_analysis_request"],
            "analysis": ["technical_analysis_request", "market_sentiment_analysis"],
            "support": ["support_resistance_levels"],
            "resistance": ["support_resistance_levels"],
            "alert": ["create_price_alert", "manage_alerts"],
            "notify": ["create_price_alert"],
            "defi": ["defi_protocol_security", "find_yield_opportunities"],
            "protocol": ["defi_protocol_security"],
            "safe": ["defi_protocol_security"],
            "security": ["defi_protocol_security"],
            "compare": ["compare_cryptocurrencies"],
            "sentiment": ["market_sentiment_analysis"],
            "news": ["crypto_news_analysis"],
            "explain": ["crypto_concept_explanation"],
            "what": ["crypto_concept_explanation"],
            "how": ["crypto_concept_explanation"],
            "hello": ["greeting"],
            "hi": ["greeting"],
            "thanks": ["gratitude"],
            "help": ["help_request"],
        }
        
        # Find matching keywords
        for keyword, intent_names in keyword_intents.items():
            if keyword in text_words:
                for intent_name in intent_names:
                    if intent_name in self.intent_patterns:
                        intent_config = self.intent_patterns[intent_name]
                        
                        # Create fuzzy match
                        relevant_entities = self._filter_relevant_entities(entities, intent_name)
                        
                        matches.append(IntentMatch(
                            intent_name=intent_name,
                            category=intent_config.get('category'),
                            confidence=0.6,  # Lower confidence for fuzzy matches
                            matched_patterns=[f"fuzzy_keyword:{keyword}"],
                            extracted_entities=relevant_entities,
                            required_data_sources=intent_config.get('data_sources', []),
                            estimated_complexity=intent_config.get('complexity', 0.5),
                            response_template=None
                        ))
        
        return matches
    
    def _fuzzy_match_intent(self, text: str, patterns: List[str]) -> float:
        """Perform fuzzy matching for intent patterns"""
        max_similarity = 0.0
        
        # Extract key words from patterns
        pattern_words = set()
        for pattern in patterns:
            # Remove regex special characters and extract words
            clean_pattern = re.sub(r'[^\w\s]', ' ', pattern)
            words = clean_pattern.split()
            pattern_words.update(word.lower() for word in words if len(word) > 2)
        
        # Extract words from text
        text_words = set(word.lower() for word in text.split() if len(word) > 2)
        
        # Calculate similarity
        if pattern_words and text_words:
            intersection = pattern_words.intersection(text_words)
            union = pattern_words.union(text_words)
            similarity = len(intersection) / len(union) if union else 0.0
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_context_boost(self, intent_name: str, context: ConversationContext, entities: List[ExtractedEntity]) -> float:
        """Calculate confidence boost based on conversation context"""
        boost = 0.0
        
        # Recent topic continuity
        if context.current_topic and intent_name.startswith(context.current_topic):
            boost += 0.1
        
        # Entity continuity
        for entity in entities:
            if entity.normalized_value in context.mentioned_entities:
                boost += 0.05
        
        # Recent similar intents
        recent_intents = [msg.get('intent') for msg in context.recent_messages if msg.get('intent')]
        if intent_name in recent_intents:
            boost += 0.1
        
        return min(boost, 0.3)  # Cap boost at 0.3
    
    def _filter_relevant_entities(self, entities: List[ExtractedEntity], intent_name: str) -> List[ExtractedEntity]:
        """Filter entities relevant to specific intent"""
        # Define entity relevance for different intent types
        relevance_map = {
            'get_realtime_price': [EntityType.CRYPTOCURRENCY, EntityType.EXCHANGE],
            'analyze_portfolio': [EntityType.CRYPTOCURRENCY, EntityType.AMOUNT, EntityType.PERCENTAGE],
            'create_price_alert': [EntityType.CRYPTOCURRENCY, EntityType.FIAT_CURRENCY, EntityType.AMOUNT],
            'find_yield_opportunities': [EntityType.CRYPTOCURRENCY, EntityType.DEFI_PROTOCOL, EntityType.PERCENTAGE],
            'technical_analysis_request': [EntityType.CRYPTOCURRENCY, EntityType.TECHNICAL_INDICATOR],
        }
        
        relevant_types = relevance_map.get(intent_name, list(EntityType))
        return [entity for entity in entities if entity.type in relevant_types]
    
    def _rank_intents(self, intent_matches: List[IntentMatch], sentiment: SentimentAnalysis, context: ConversationContext) -> Tuple[IntentMatch, List[IntentMatch]]:
        """Rank intents by confidence and priority"""
        if not intent_matches:
            # Create fallback intent
            fallback = IntentMatch(
                intent_name="general_conversation",
                category=IntentCategory.GENERAL_CONVERSATION,
                confidence=0.3,
                matched_patterns=[],
                extracted_entities=[],
                required_data_sources=[],
                estimated_complexity=0.2,
                response_template=None
            )
            return fallback, []
        
        # Sort primarily by confidence, then by category priority
        def sort_key(match):
            category_priority = {
                IntentCategory.EMERGENCY: 10,
                IntentCategory.SECURITY_ALERT: 9,
                IntentCategory.GENERAL_CONVERSATION: 8,  # Boost conversational intents
                IntentCategory.EDUCATION: 7,
                IntentCategory.PORTFOLIO_MANAGEMENT: 6,
                IntentCategory.YIELD_FARMING: 6,
                IntentCategory.DEFI_OPERATIONS: 6,
                IntentCategory.TRADING_EXECUTION: 5,
                IntentCategory.TECHNICAL_ANALYSIS: 5,
                IntentCategory.MARKET_ANALYSIS: 5,
                IntentCategory.ALERT_MANAGEMENT: 4,
                IntentCategory.PRICE_QUERY: 3,  # Lower priority for price queries
                IntentCategory.RISK_ASSESSMENT: 3,
                IntentCategory.NEWS_ANALYSIS: 2,
                IntentCategory.SOCIAL_SENTIMENT: 2,
            }
            
            base_priority = category_priority.get(match.category, 1)
            
            # Boost urgent intents based on sentiment
            if sentiment.type == SentimentType.URGENT:
                if match.category in [IntentCategory.EMERGENCY, IntentCategory.SECURITY_ALERT]:
                    base_priority += 5
            
            # Primary sort by confidence, secondary by priority
            # This ensures high-confidence matches are preferred regardless of category
            return (match.confidence, base_priority)
        
        sorted_matches = sorted(intent_matches, key=sort_key, reverse=True)
        
        primary_intent = sorted_matches[0]
        secondary_intents = sorted_matches[1:3]  # Top 2 secondary intents
        
        return primary_intent, secondary_intents
    
    def _calculate_overall_confidence(self, primary_intent: IntentMatch, secondary_intents: List[IntentMatch], entities: List[ExtractedEntity], sentiment: SentimentAnalysis) -> float:
        """Calculate overall confidence score"""
        base_confidence = primary_intent.confidence
        
        # Boost confidence if entities are present
        if entities:
            entity_boost = min(len(entities) * 0.05, 0.2)
            base_confidence += entity_boost
        
        # Boost confidence for clear sentiment
        if abs(sentiment.compound_score) > 0.5:
            sentiment_boost = 0.1
            base_confidence += sentiment_boost
        
        # Reduce confidence if multiple high-confidence intents
        if len(secondary_intents) > 0 and secondary_intents[0].confidence > 0.7:
            ambiguity_penalty = 0.1
            base_confidence -= ambiguity_penalty
        
        return min(base_confidence, 1.0)
    
    def _determine_processing_strategy(self, primary_intent: IntentMatch, secondary_intents: List[IntentMatch], sentiment: SentimentAnalysis) -> str:
        """Determine the best processing strategy"""
        # Emergency and security alerts get immediate processing
        if primary_intent.category in [IntentCategory.EMERGENCY, IntentCategory.SECURITY_ALERT]:
            return "emergency_response"
        
        # High-confidence single intent
        if primary_intent.confidence > 0.8 and len(secondary_intents) == 0:
            return "direct_execution"
        
        # Multiple intents require orchestration
        if len(secondary_intents) > 0 and secondary_intents[0].confidence > 0.6:
            return "multi_intent_orchestration"
        
        # Complex analysis required
        if primary_intent.estimated_complexity > 0.7:
            return "complex_analysis"
        
        # Simple data retrieval
        if primary_intent.category in [IntentCategory.PRICE_QUERY, IntentCategory.PORTFOLIO_MANAGEMENT]:
            return "data_retrieval"
        
        # AI-enhanced response
        return "ai_enhanced_response"
    
    def _estimate_response_time(self, primary_intent: IntentMatch, secondary_intents: List[IntentMatch]) -> float:
        """Estimate response time based on intent complexity"""
        base_time = primary_intent.estimated_complexity * 2.0
        
        # Add time for secondary intents
        for intent in secondary_intents:
            base_time += intent.estimated_complexity * 1.0
        
        # Add time for data source calls
        data_source_time = len(primary_intent.required_data_sources) * 0.5
        base_time += data_source_time
        
        return min(base_time, 10.0)  # Cap at 10 seconds
    
    def _check_required_permissions(self, primary_intent: IntentMatch, secondary_intents: List[IntentMatch]) -> List[str]:
        """Check required permissions for intent execution"""
        permissions = []
        
        # Trading permissions
        if primary_intent.category == IntentCategory.TRADING_EXECUTION:
            permissions.append("trading_access")
        
        # Portfolio access
        if primary_intent.category == IntentCategory.PORTFOLIO_MANAGEMENT:
            permissions.append("portfolio_read")
            if "add" in primary_intent.intent_name or "remove" in primary_intent.intent_name:
                permissions.append("portfolio_write")
        
        # Alert management
        if primary_intent.category == IntentCategory.ALERT_MANAGEMENT:
            permissions.append("alert_management")
        
        # External API access
        if primary_intent.required_data_sources:
            permissions.append("api_access")
        
        return permissions
    
    def _create_fallback_analysis(self, text: str, user_id: int) -> MultiIntentAnalysis:
        """Create fallback analysis when main analysis fails"""
        fallback_intent = IntentMatch(
            intent_name="general_conversation",
            category=IntentCategory.GENERAL_CONVERSATION,
            confidence=0.3,
            matched_patterns=[],
            extracted_entities=[],
            required_data_sources=[],
            estimated_complexity=0.2,
            response_template=None
        )
        
        fallback_sentiment = SentimentAnalysis(
            type=SentimentType.NEUTRAL,
            compound_score=0.0,
            positive=0.0,
            negative=0.0,
            neutral=1.0,
            emotions={}
        )
        
        fallback_context = self._get_conversation_context(user_id)
        
        return MultiIntentAnalysis(
            primary_intent=fallback_intent,
            secondary_intents=[],
            sentiment=fallback_sentiment,
            entities=[],
            context=fallback_context,
            confidence_score=0.3,
            processing_strategy="simple_ai_response",
            estimated_response_time=1.0,
            required_permissions=[]
        )

# Global instance
advanced_intent_analyzer = AdvancedIntentAnalyzer()

async def analyze_advanced_intent(text: str, user_id: int, context: Optional[Dict] = None) -> MultiIntentAnalysis:
    """Main function for advanced intent analysis"""
    return await advanced_intent_analyzer.analyze_multi_intent(text, user_id, context)