# src/natural_language_processor.py
"""
Natural Language Processing Engine for Mobius AI Assistant
Handles intent recognition, conversation flow, and Groq API integration with rate limiting
"""

import asyncio
import logging
import re
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import aiohttp
from config import config
from persistent_user_context import user_context_manager
from intelligent_error_handler import error_handler

logger = logging.getLogger(__name__)

@dataclass
class Intent:
    name: str
    confidence: float
    entities: Dict[str, str]
    suggested_action: str

@dataclass
class ConversationContext:
    user_id: int
    last_intent: Optional[str] = None
    conversation_history: List[Dict] = None
    current_topic: Optional[str] = None
    waiting_for_input: bool = False
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

class GroqRateLimiter:
    """Rate limiter for Groq API with 6000 TPM limit"""
    
    def __init__(self, max_tokens_per_minute: int = 5500):  # Leave buffer
        self.max_tokens_per_minute = max_tokens_per_minute
        self.token_usage = []
        self.lock = asyncio.Lock()
    
    async def can_make_request(self, estimated_tokens: int) -> bool:
        """Check if we can make a request without hitting rate limits"""
        async with self.lock:
            now = datetime.now()
            # Remove entries older than 1 minute
            self.token_usage = [
                (timestamp, tokens) for timestamp, tokens in self.token_usage
                if now - timestamp < timedelta(minutes=1)
            ]
            
            # Calculate current usage
            current_usage = sum(tokens for _, tokens in self.token_usage)
            
            # Check if we can make the request
            if current_usage + estimated_tokens <= self.max_tokens_per_minute:
                self.token_usage.append((now, estimated_tokens))
                return True
            
            return False
    
    async def wait_for_capacity(self, estimated_tokens: int):
        """Wait until we have capacity for the request"""
        while not await self.can_make_request(estimated_tokens):
            await asyncio.sleep(1)  # Wait 1 second and try again

class NaturalLanguageProcessor:
    """Main NLP engine for intent recognition and conversation handling"""
    
    def __init__(self):
        self.groq_api_key = config.get('GROQ_API_KEY')
        self.rate_limiter = GroqRateLimiter()
        self.conversation_contexts: Dict[int, ConversationContext] = {}
        
        # Learning and adaptation features
        self.user_patterns: Dict[int, Dict[str, int]] = {}  # Track user intent patterns
        self.successful_responses: Dict[str, int] = {}  # Track successful response patterns
        self.failed_patterns: Dict[str, int] = {}  # Track failed patterns for improvement
        self.learned_entities: Dict[str, str] = {}  # Learn new entities from context
        
        # MASSIVELY ENHANCED Intent patterns for comprehensive natural language understanding
        self.intent_patterns = {
            'portfolio_check': [
                r'(?i).*(portfolio|balance|holdings|my\s+coins|my\s+tokens|my\s+assets|my\s+investments|my\s+crypto|my\s+defi|my\s+positions|my\s+funds|my\s+money).*',
                r'(?i).*(show|check|view|display|see|look\s+at).*(portfolio|balance|holdings|assets|investments).*',
                r'(?i).*(what|how\s+much).*(do\s+i\s+have|i\s+own|my\s+balance|i\s+hold|is\s+my\s+balance).*',
                r'(?i).*(account\s+balance|wallet\s+balance|total\s+value|net\s+worth).*'
            ],
            'price_check': [
                # Direct token price queries
                r'(?i)^(btc|bitcoin|eth|ethereum|sol|solana|ada|cardano|dot|polkadot|matic|polygon|avax|avalanche|link|chainlink|uni|uniswap|aave|comp|compound|mkr|maker|crv|curve|yfi|yearn|sushi|sushiswap|1inch|snx|synthetix|bal|balancer)\s+(price|cost|value|worth|rate)$',
                r'(?i).*(price|cost|value|worth|rate|quote).*(of|for|is|btc|bitcoin|eth|ethereum|sol|solana|ada|dot|matic|avax|link|uni|aave|comp|mkr|crv|yfi|sushi|1inch|snx|bal).*',
                r'(?i).*(what|how\s+much).*(is|costs?|worth|trading\s+at).*(btc|bitcoin|eth|ethereum|sol|solana|ada|dot|matic|avax|link|uni|aave|comp|mkr|crv|yfi|sushi|1inch|snx|bal).*',
                r'(?i).*(btc|bitcoin|eth|ethereum|sol|solana|ada|dot|matic|avax|link|uni|aave|comp|mkr|crv|yfi|sushi|1inch|snx|bal).*(price|cost|value|worth|rate|trading|current|today|now).*',
                r'(?i).*(current|latest|today|now|real\s+time).*(price|value|cost|rate).*',
                r'(?i).*(trading\s+at|priced\s+at|valued\s+at|going\s+for).*',
                r'(?i).*(market\s+price|spot\s+price|live\s+price|current\s+rate).*',
                # Simple patterns like "BTC price", "ETH value", etc.
                r'(?i)^(btc|bitcoin|eth|ethereum|sol|solana|ada|cardano|dot|polkadot|matic|polygon|avax|avalanche|link|chainlink|uni|uniswap|aave|comp|compound|mkr|maker|crv|curve|yfi|yearn|sushi|sushiswap|1inch|snx|synthetix|bal|balancer)$',
                r'(?i)^(price|cost|value|worth)\s+(btc|bitcoin|eth|ethereum|sol|solana|ada|cardano|dot|polkadot|matic|polygon|avax|avalanche|link|chainlink|uni|uniswap|aave|comp|compound|mkr|maker|crv|curve|yfi|yearn|sushi|sushiswap|1inch|snx|synthetix|bal|balancer)$'
            ],
            'research_request': [
                r'(?i).*(research|analyze|investigate|study|examine|look\s+into|tell\s+me\s+about|info\s+on|information\s+about|details\s+about|data\s+on).*',
                r'(?i).*(what\s+is|what\s+about|details\s+on|data\s+on|stats\s+on|metrics\s+for|analytics\s+for).*',
                r'(?i).*(tvl|volume|market\s+cap|liquidity|apy|apr|yield|revenue|fees|users|transactions).*(of|for|on).*',
                r'(?i).*(protocol\s+info|token\s+info|project\s+info|defi\s+data|chain\s+data).*',
                r'(?i).*(performance|statistics|metrics|analytics|breakdown|overview|summary).*(of|for).*',
                r'(?i).*(how\s+is|how\s+does|what\s+about).*(performing|doing|looking|trending).*'
            ],
            'summary_request': [
                r'(?i).*(summary|summarize|recap|overview|digest|roundup|wrap\s+up).*',
                r'(?i).*(what\s+happened|what\s+did\s+we\s+discuss|conversation\s+summary|chat\s+summary).*',
                r'(?i).*(today|yesterday|this\s+week|recent|latest).*(summary|recap|digest|overview).*',
                r'(?i).*(key\s+points|main\s+topics|important\s+stuff|highlights).*',
                r'(?i).*(catch\s+me\s+up|bring\s+me\s+up\s+to\s+speed|what\s+did\s+i\s+miss).*'
            ],
            'alert_management': [
                r'(?i).*(alert|notification|notify|remind|watch|monitor|track|alarm).*',
                r'(?i).*(set\s+up|create|add|remove|delete|manage|configure).*(alert|notification|reminder).*',
                r'(?i).*(price\s+alert|movement\s+alert|change\s+alert|threshold\s+alert).*',
                r'(?i).*(notify\s+me|tell\s+me|alert\s+me|let\s+me\s+know).*(when|if).*',
                r'(?i).*(watch\s+for|monitor\s+for|track\s+for|keep\s+an\s+eye\s+on).*'
            ],
            'help_request': [
                r'(?i).*(help|assist|support|guide|how\s+to|what\s+can\s+you\s+do|instructions).*',
                r'(?i).*(commands|features|functions|capabilities|options|what\s+do\s+you\s+do).*',
                r'(?i).*(confused|lost|don\'t\s+know|not\s+sure|need\s+help|stuck).*',
                r'(?i).*(how\s+do\s+i|how\s+can\s+i|what\s+should\s+i|where\s+do\s+i).*',
                r'(?i).*(tutorial|walkthrough|getting\s+started|first\s+time).*'
            ],
            'menu_request': [
                r'(?i).*(menu|options|choices|main\s+menu|show\s+menu|navigation).*',
                r'(?i).*(what\s+can\s+i\s+do|available\s+options|list\s+commands|show\s+commands).*',
                r'(?i).*(dashboard|control\s+panel|interface|home\s+screen).*'
            ],
            'greeting': [
                r'(?i)^(hi|hello|hey|good\s+morning|good\s+afternoon|good\s+evening|sup|what\'s\s+up|yo|greetings|salutations|howdy).*',
                r'(?i).*(how\s+are\s+you|how\s+is\s+it\s+going|how\s+you\s+doing|how\s+are\s+things).*',
                r'(?i).*(good\s+morning|good\s+afternoon|good\s+evening|good\s+day).*',
                r'(?i).*(hey\s+there|hi\s+there|hello\s+there).*',
                r'(?i).*(what.*up|wassup|whats\s+up).*',
                r'(?i).*(nice\s+to\s+meet|pleasure\s+to\s+meet|glad\s+to\s+meet).*'
            ],
            'status_check': [
                r'(?i).*(status|health|uptime|online|working|functioning|operational).*',
                r'(?i).*(how.*is.*bot|how.*are.*you.*doing|are.*you.*ok|are.*you.*working).*',
                r'(?i).*(system\s+status|bot\s+status|service\s+status|connection\s+status).*',
                r'(?i).*(alive|responsive|active|running|available).*'
            ],
            'mentions_request': [
                r'(?i).*(my.*mentions|where.*mentioned|show.*mentions|find.*mentions).*',
                r'(?i).*(mentioned\s+me|talked\s+about\s+me|referenced\s+me|tagged\s+me).*',
                r'(?i).*(search\s+mentions|look\s+for\s+mentions|find\s+my\s+name).*'
            ],
            'yield_farming': [
                r'(?i).*(yield|farming|staking|liquidity\s+mining|apy|apr|rewards|passive\s+income).*',
                r'(?i).*(best\s+yields|highest\s+apy|top\s+farms|farming\s+opportunities).*',
                r'(?i).*(stake|provide\s+liquidity|earn\s+rewards|compound\s+rewards).*'
            ],
            'defi_protocols': [
                r'(?i).*(defi|protocol|dapp|decentralized\s+finance|smart\s+contracts).*',
                r'(?i).*(lending|borrowing|swapping|trading|dex|exchange|amm).*',
                r'(?i).*(compound|aave|uniswap|sushiswap|curve|balancer|yearn).*'
            ],
            'market_analysis': [
                r'(?i).*(market|trend|analysis|sentiment|outlook|forecast|prediction).*',
                r'(?i).*(bullish|bearish|pump|dump|moon|crash|rally|correction).*',
                r'(?i).*(technical\s+analysis|chart\s+analysis|price\s+prediction|ta).*',
                r'(?i).*(support|resistance|fibonacci|rsi|macd|moving\s+average).*'
            ],
            'news_request': [
                r'(?i).*(news|updates|announcements|latest|recent\s+developments).*',
                r'(?i).*(what\'s\s+new|what\'s\s+happening|any\s+news|breaking\s+news).*',
                r'(?i).*(headlines|current\s+events|market\s+news|crypto\s+news).*'
            ],
            'comparison_request': [
                r'(?i).*(compare|versus|vs|difference|better|which\s+is|which\s+one).*',
                r'(?i).*(pros\s+and\s+cons|advantages|disadvantages|trade\s+offs).*',
                r'(?i).*(similar|alternative|competitor|rival|substitute).*'
            ],
            'transaction_help': [
                r'(?i).*(transaction|tx|send|transfer|swap|trade|buy|sell|exchange).*',
                r'(?i).*(gas\s+fees|transaction\s+fees|slippage|deadline|mev).*',
                r'(?i).*(metamask|wallet|connect|approve|confirm|sign).*',
                r'(?i).*(bridge|cross\s+chain|layer\s+2|l2|arbitrum|polygon).*'
            ],
            'learning_request': [
                r'(?i).*(learn|teach|explain|understand|how\s+does|what\s+is).*',
                r'(?i).*(beginner|new\s+to|getting\s+started|basics|fundamentals).*',
                r'(?i).*(tutorial|guide|walkthrough|step\s+by\s+step).*'
            ],
            'security_concern': [
                r'(?i).*(security|safe|secure|risk|danger|scam|hack|exploit).*',
                r'(?i).*(private\s+key|seed\s+phrase|wallet\s+security|phishing).*',
                r'(?i).*(audit|verified|trusted|legitimate|official).*'
            ]
        }
        
        # MASSIVELY ENHANCED Entity extraction patterns for comprehensive understanding
        self.entity_patterns = {
            'token_symbol': r'\b([A-Z]{2,10})\b',
            'protocol_name': r'\b(paradex|lido|uniswap|aave|compound|makerdao|curve|balancer|sushiswap|pancakeswap|1inch|yearn|convex|frax|rocket\s*pool|eigenlayer|pendle|morpho|euler|radiant|venus|benqi|trader\s*joe|platypus|stargate|synapse|hop|across|celer|multichain|anyswap|thorchain|osmosis|juno|terra|anchor|mirror|astroport|prism|mars|kujira|comdex|crescent|sommelier|umee|stride|quicksilver|persistence|regen|akash|sentinel|iris|starname|bitcanna|likecoin|desmos|chihuahua|stargaze|omniflix|cerberus|cheqd|lumnetwork|provenance|dig|fetchai|assetmantle|konstellation|pylons|medibloc|sifchain|crypto\.org|cronos|evmos|kava|secret|injective|band|odin|terra\s*classic|luna\s*classic|ust|ustc|lunc|atom|osmo|scrt|inj|akt|dvpn|xprt|regen|like|chihuahua|stars|cerberus|cheqd|lum|hash|fetch|mntl|darc|pylon|bcna|med|sif|cro|evmos|hard|swp|usdx|bnb|cake|bake|burger|auto|alpaca|belt|xvs|vai|cream|ice|bunny|egg|watch|bifi|acryptos|ellipsis|eps|dodo|mdx|heco|ht|husd|usdt|usdc|busd|dai|frax|fei|lusd|mim|tusd|gusd|paxg|wbtc|renbtc|hbtc|btcb|eth|weth|matic|avax|wavax|ftm|wftm|one|wone|wcro|wbnb|ada|dot|ksm|sol|wsol|near|wnear|algo|xlm|xtz|egld|elgd|icp|ar|fil|theta|tfuel|vet|vtho|hbar|miota|neo|gas|ont|ong|qtum|waves|zil|icx|lsk|nano|xno|dcr|zec|xmr|dash|etc|bch|bsv|ltc|doge|shib|floki|safemoon|pepe|bitcoin|ethereum|binance|cardano|solana|polkadot|avalanche|fantom|harmony|cosmos|chainlink|polygon|arbitrum|optimism|base|zksync|starknet)\b',
            'amount': r'\$?(\d+(?:,\d{3})*(?:\.\d+)?)\s*([kmbtKMBT]|million|billion|trillion|thousand)?',
            'percentage': r'(\d+(?:\.\d+)?)\s*%',
            'time_period': r'\b(today|yesterday|week|month|year|24h|7d|30d|1y|daily|weekly|monthly|yearly|now|current|latest|recent|this\s+week|last\s+week|this\s+month|last\s+month)\b',
            'wallet_address': r'0x[a-fA-F0-9]{40}',
            'metric_type': r'\b(tvl|volume|market\s*cap|liquidity|apy|apr|yield|revenue|fees|price|cost|value|worth|users|transactions|holders|supply|circulation|dominance)\b',
            'action_verb': r'\b(buy|sell|trade|swap|stake|farm|provide|withdraw|deposit|bridge|send|transfer|approve|connect|analyze|research|check|show|display|view|compare|monitor|track|watch|alert|notify)\b',
            'comparison_word': r'\b(vs|versus|compared\s+to|against|better|worse|higher|lower|more|less|similar|different)\b',
            'time_frame': r'\b(real\s*time|live|current|latest|now|today|yesterday|this\s+week|last\s+week|24h|7d|30d|1y)\b',
            'blockchain': r'\b(ethereum|bitcoin|binance\s*smart\s*chain|bsc|polygon|arbitrum|optimism|avalanche|fantom|solana|cardano|polkadot|cosmos|near|harmony|cronos|evmos|kava|secret|injective|terra|juno|osmosis|base|zksync|starknet|scroll|mode|blast|mantle)\b',
            'defi_action': r'\b(lending|borrowing|staking|farming|providing\s+liquidity|yield\s+farming|liquidity\s+mining|swapping|trading|bridging)\b',
            'sentiment': r'\b(bullish|bearish|positive|negative|optimistic|pessimistic|confident|uncertain|excited|worried|hopeful|concerned)\b',
            'urgency': r'\b(urgent|asap|quickly|immediately|now|soon|later|eventually|when\s+possible)\b',
            'question_word': r'\b(what|how|when|where|why|which|who|whose)\b',
            'negation': r'\b(not|no|never|none|nothing|nowhere|nobody|neither|nor|don\'t|doesn\'t|didn\'t|won\'t|wouldn\'t|can\'t|couldn\'t|shouldn\'t|isn\'t|aren\'t|wasn\'t|weren\'t)\b'
        }
    
    def get_conversation_context(self, user_id: int) -> ConversationContext:
        """Get or create conversation context for user"""
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = ConversationContext(user_id)
        return self.conversation_contexts[user_id]
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from text using regex patterns"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches[0] if isinstance(matches[0], str) else matches[0][0]
        
        return entities
    
    def analyze_intent(self, text: str) -> Intent:
        """Analyze intent from text - main entry point for intent analysis"""
        # Try quick pattern-based recognition first
        intent = self.quick_intent_recognition(text)
        
        if intent:
            return intent
        
        # If no pattern match, return a default intent
        entities = self.extract_entities(text)
        return Intent(
            name='general_query',
            confidence=0.5,
            entities=entities,
            suggested_action='help'
        )
    
    def quick_intent_recognition(self, text: str) -> Optional[Intent]:
        """Quick intent recognition using regex patterns"""
        entities = self.extract_entities(text)
        
        for intent_name, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return Intent(
                        name=intent_name,
                        confidence=0.8,  # High confidence for pattern matches
                        entities=entities,
                        suggested_action=self.get_suggested_action(intent_name, entities)
                    )
        
        return None
    
    def get_suggested_action(self, intent: str, entities: Dict[str, str]) -> str:
        """Get suggested action based on intent and entities"""
        # Enhanced action mapping with comprehensive intent handling
        protocol_or_token = entities.get('protocol_name', entities.get('token_symbol', ''))
        
        action_map = {
            'portfolio_check': '/portfolio',
            'price_check': f"/research {protocol_or_token}" if protocol_or_token else '/research',
            'summary_request': '/summarynow',
            'research_request': f"/research {protocol_or_token}" if protocol_or_token else '/research',
            'alert_management': '/alerts',
            'help_request': '/help',
            'menu_request': '/menu',
            'mentions_request': '/mymentions',
            'greeting': 'greeting_response',
            'status_check': '/status',
            'yield_farming': '/research yields',
            'defi_protocols': f"/research {protocol_or_token}" if protocol_or_token else '/research protocols',
            'market_analysis': f"/research {protocol_or_token}" if protocol_or_token else 'ai_response',
            'news_request': 'ai_response',
            'comparison_request': f"/research {protocol_or_token}" if protocol_or_token else 'ai_response',
            'transaction_help': 'ai_response',
            'learning_request': '/help',
            'security_concern': 'ai_response'
        }
        
        return action_map.get(intent, '/help')
    
    async def groq_intent_recognition(self, text: str, context: ConversationContext) -> Optional[Intent]:
        """Use Groq API for advanced intent recognition"""
        if not self.groq_api_key:
            logger.warning("Groq API key not available")
            return None
        
        # Estimate tokens (rough estimation: 1 token ≈ 4 characters)
        estimated_tokens = len(text) // 4 + 200  # Add buffer for prompt and response
        
        # Check rate limits
        if not await self.rate_limiter.can_make_request(estimated_tokens):
            logger.warning("Rate limit reached, falling back to pattern matching")
            return None
        
        try:
            prompt = self.create_intent_prompt(text, context)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.groq_api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'model': 'llama3-8b-8192',  # Fast model for intent recognition
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are an intent recognition system for a crypto trading assistant. Respond only with valid JSON.'
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'max_tokens': 150,
                    'temperature': 0.1
                }
                
                async with session.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        
                        # Parse JSON response
                        try:
                            intent_data = json.loads(content)
                            return Intent(
                                name=intent_data.get('intent', 'unknown'),
                                confidence=intent_data.get('confidence', 0.5),
                                entities=intent_data.get('entities', {}),
                                suggested_action=intent_data.get('action', '/help')
                            )
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse Groq response: {content}")
                            return None
                    else:
                        logger.error(f"Groq API error: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return None
    
    def create_intent_prompt(self, text: str, context: ConversationContext) -> str:
        """Create prompt for Groq intent recognition"""
        context_info = ""
        if context.conversation_history:
            recent_messages = context.conversation_history[-3:]  # Last 3 messages
            context_info = f"Recent conversation: {recent_messages}"
        
        return f"""
Analyze this message from a crypto trading bot user and return intent information as JSON.

User message: "{text}"
{context_info}

Available intents:
- portfolio_check: User wants to see their portfolio
- price_check: User wants to check token prices
- summary_request: User wants a conversation summary
- research_request: User wants research on a token/topic
- alert_management: User wants to manage alerts
- help_request: User needs help or instructions
- greeting: User is greeting or making small talk
- status_check: User wants to check bot status
- general_question: General crypto/trading question

Return JSON format:
{{
    "intent": "intent_name",
    "confidence": 0.0-1.0,
    "entities": {{
        "token_symbol": "BTC",
        "amount": "100",
        "time_period": "24h"
    }},
    "action": "/command or response_type"
}}
"""
    
    async def process_natural_language(self, user_id: int, text: str) -> Tuple[Intent, str]:
        """Process natural language input with persistent context and error handling"""
        
        # Get persistent user context
        persistent_context = user_context_manager.get_user_context(user_id)
        
        # Update conversation flow in real-time
        user_context_manager.update_conversation_flow(user_id, "user_message", text)
        
        # Check for input errors and suggest corrections
        correction = error_handler.detect_and_correct_input(text, {
            'last_intent': persistent_context.last_intent,
            'current_topic': persistent_context.current_topic
        })
        
        if correction and correction.confidence > 0.8:
            # Auto-correct high-confidence corrections
            text = correction.suggested
            logger.info(f"Auto-corrected input for user {user_id}: {correction.original} -> {correction.suggested}")
        elif correction and correction.confidence > 0.6:
            # Suggest correction for medium confidence
            suggestion_response = f"🤔 {correction.explanation}\n\nI'll proceed with what I think you meant: \"{correction.suggested}\""
            text = correction.suggested
        
        # Get legacy conversation context for backward compatibility
        context = self.get_conversation_context(user_id)
        
        # Merge with persistent context
        if persistent_context.current_topic:
            context.current_topic = persistent_context.current_topic
        if persistent_context.last_intent:
            context.last_intent = persistent_context.last_intent
        
        # Try quick pattern matching first
        intent = self.quick_intent_recognition(text)
        
        # If no clear pattern match, use Groq for advanced recognition
        if not intent or intent.confidence < 0.7:
            groq_intent = await self.groq_intent_recognition(text, context)
            if groq_intent and groq_intent.confidence > (intent.confidence if intent else 0):
                intent = groq_intent
        
        # Fallback to general question if no intent found
        if not intent:
            intent = Intent(
                name='general_question',
                confidence=0.5,
                entities=self.extract_entities(text),
                suggested_action='ai_response'
            )
        
        # Update persistent context
        persistent_context.last_intent = intent.name
        if intent.entities.get('token_symbol'):
            persistent_context.current_topic = intent.entities['token_symbol']
        
        # Learn user preferences from conversation
        await self.learn_user_preferences(user_id, text, intent, persistent_context)
        
        # Generate personalized response
        response = await self.generate_response(intent, text, persistent_context)
        
        # Update conversation flow with bot response
        user_context_manager.update_conversation_flow(user_id, "bot_response", response, intent.name)
        
        # Save persistent context
        user_context_manager.save_user_context(persistent_context)
        
        return intent, response
    
    async def learn_user_preferences(self, user_id: int, text: str, intent: Intent, context):
        """Learn user preferences from conversation patterns"""
        try:
            # Learn communication style
            if any(word in text.lower() for word in ["please", "thank you", "could you"]):
                user_context_manager.learn_preference(user_id, "communication_style", "polite", "conversation", 0.7)
            elif any(word in text.lower() for word in ["hey", "yo", "sup", "what's up"]):
                user_context_manager.learn_preference(user_id, "communication_style", "casual", "conversation", 0.7)
            
            # Learn preferred tokens
            if intent.entities.get('token_symbol'):
                token = intent.entities['token_symbol']
                user_context_manager.learn_preference(user_id, f"interested_in_{token.lower()}", True, "conversation", 0.6)
            
            # Learn preferred features
            if intent.name == 'portfolio_check':
                user_context_manager.learn_preference(user_id, "uses_portfolio", True, "conversation", 0.8)
            elif intent.name == 'summary_request':
                user_context_manager.learn_preference(user_id, "likes_summaries", True, "conversation", 0.8)
            elif intent.name == 'research_request':
                user_context_manager.learn_preference(user_id, "uses_research", True, "conversation", 0.8)
            
            # Learn time preferences
            current_hour = datetime.now().hour
            if 6 <= current_hour <= 12:
                time_period = "morning"
            elif 12 <= current_hour <= 18:
                time_period = "afternoon"
            elif 18 <= current_hour <= 22:
                time_period = "evening"
            else:
                time_period = "night"
            
            user_context_manager.learn_preference(user_id, f"active_{time_period}", True, "conversation", 0.5)
            
        except Exception as e:
            logger.error(f"Error learning preferences for user {user_id}: {e}")
    
    async def generate_response(self, intent: Intent, original_text: str, context) -> str:
        """Generate appropriate response based on intent"""
        
        if intent.name == 'greeting':
            return self.generate_greeting_response(context)
        
        elif intent.name == 'portfolio_check':
            return "📊 Let me check your portfolio for you. Use /portfolio to see detailed information."
        
        elif intent.name == 'price_check':
            token = intent.entities.get('token_symbol', 'BTC')
            return f"💰 Checking price for {token}. Use /research {token} for detailed analysis."
        
        elif intent.name == 'summary_request':
            return "📋 Generating conversation summary for you. Use /summarynow for immediate results."
        
        elif intent.name == 'research_request':
            token = intent.entities.get('token_symbol', '')
            if token:
                return f"🔍 Researching {token} for you. Use /research {token} for comprehensive analysis."
            else:
                return "🔍 What would you like me to research? Please specify a token symbol."
        
        elif intent.name == 'alert_management':
            return "🔔 Managing your alerts. Use /alerts to see all options or /alert <address> <amount> to set new ones."
        
        elif intent.name == 'help_request':
            return "❓ I'm here to help! Use /help to see all available commands, or just tell me what you need in natural language."
        
        elif intent.name == 'menu_request':
            return "📋 Opening the main menu for you! Use /menu to see all available options."
        
        elif intent.name == 'status_check':
            return "✅ I'm online and ready to help! Use /status for detailed system information."
        
        elif intent.name == 'mentions_request':
            return "📬 Searching for your mentions! Use /mymentions to see where you've been mentioned."
        
        elif intent.name == 'yield_farming':
            return "🌾 Looking for yield farming opportunities! Use /research yields to see the best APY rates."
        
        elif intent.name == 'defi_protocols':
            protocol = intent.entities.get('protocol_name', '')
            if protocol:
                return f"🔍 Researching {protocol} protocol for you! Use /research {protocol} for detailed information."
            else:
                return "🔍 Researching DeFi protocols! Use /research protocols to see top protocols."
        
        elif intent.name == 'market_analysis':
            return "📊 Analyzing market trends for you! Let me gather the latest data..."
        
        elif intent.name == 'news_request':
            return "📰 I'd love to share the latest crypto news! For now, try specific research commands like /research or check reliable crypto news sources."
        
        elif intent.name == 'comparison_request':
            return "⚖️ Comparing options for you! Use specific research commands to get detailed comparisons."
        
        elif intent.name == 'transaction_help':
            return "💸 I can help with transaction questions! What specific transaction issue are you facing?"
        
        elif intent.name == 'learning_request':
            return "🎓 Happy to help you learn! Use /help to see all available commands and features."
        
        elif intent.name == 'security_concern':
            return "🔒 Security is crucial in crypto! Always verify contracts, use hardware wallets, and never share private keys. What specific security question do you have?"
        
        elif intent.name == 'general_question':
            return await self.generate_ai_response(original_text, context)
        
        else:
            return "🤔 I understand you're asking about something, but I'm not sure exactly what. Could you be more specific?"
    
    def learn_from_interaction(self, user_id: int, text: str, intent: Intent, success: bool):
        """Learn from user interactions to improve future responses"""
        try:
            # Track user patterns
            if user_id not in self.user_patterns:
                self.user_patterns[user_id] = {}
            
            intent_name = intent.name
            if intent_name not in self.user_patterns[user_id]:
                self.user_patterns[user_id][intent_name] = 0
            self.user_patterns[user_id][intent_name] += 1
            
            # Track successful/failed patterns
            pattern_key = f"{intent_name}:{len(text.split())}"  # Intent + word count
            
            if success:
                if pattern_key not in self.successful_responses:
                    self.successful_responses[pattern_key] = 0
                self.successful_responses[pattern_key] += 1
            else:
                if pattern_key not in self.failed_patterns:
                    self.failed_patterns[pattern_key] = 0
                self.failed_patterns[pattern_key] += 1
            
            # Learn new entities from successful interactions
            if success and intent.entities:
                for entity_type, entity_value in intent.entities.items():
                    if entity_type == 'protocol_name' and entity_value.lower() not in self.entity_patterns['protocol_name']:
                        # Learn new protocol names
                        self.learned_entities[entity_value.lower()] = entity_type
                        logger.info(f"Learned new entity: {entity_value} ({entity_type})")
            
        except Exception as e:
            logger.error(f"Error in learning from interaction: {e}")
    
    def get_user_preferences(self, user_id: int) -> Dict[str, str]:
        """Get user preferences based on interaction history"""
        if user_id not in self.user_patterns:
            return {}
        
        patterns = self.user_patterns[user_id]
        
        # Determine user's most common intents
        most_common_intent = max(patterns.items(), key=lambda x: x[1])[0] if patterns else None
        
        preferences = {
            'primary_interest': most_common_intent,
            'interaction_count': sum(patterns.values()),
            'preferred_style': 'detailed' if sum(patterns.values()) > 10 else 'simple'
        }
        
        return preferences
    
    def adapt_response_style(self, user_id: int, base_response: str) -> str:
        """Adapt response style based on user preferences"""
        try:
            preferences = self.get_user_preferences(user_id)
            
            if preferences.get('preferred_style') == 'detailed':
                # Add more detail for experienced users
                if "Use /" in base_response:
                    base_response += "\n\n💡 *Tip: You can also try natural language like 'research Bitcoin' or 'show my portfolio'*"
            
            # Personalize based on primary interest
            primary_interest = preferences.get('primary_interest')
            if primary_interest == 'research_request':
                base_response += "\n\n🔍 *I notice you like research - try asking about specific protocols or metrics!*"
            elif primary_interest == 'portfolio_check':
                base_response += "\n\n💰 *For portfolio tracking, you can ask 'show my balance' or 'what do I own'*"
            
            return base_response
            
        except Exception as e:
            logger.error(f"Error adapting response style: {e}")
            return base_response
    
    def clean_thinking_process(self, response: str) -> str:
        """CRITICAL: Remove any thinking process tags or meta-commentary from AI responses"""
        try:
            # Remove <think> tags and their content
            import re
            
            # Remove <think>...</think> blocks
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove thinking indicators at the start of responses
            thinking_patterns = [
                r'^(thinking about|analyzing|processing|let me think|i need to|i should|first i|let me analyze).*?\n',
                r'^(hmm|well|so|now|okay|alright),?\s*',
                r'^\*?(thinking|analyzing|processing|considering).*?\*?\n',
                r'^\[.*?(thinking|analysis|processing).*?\]\n',
                r'(thinking about|analyzing|processing).*?\.\.\.',
                r'(thinking about|analyzing|processing).*?\.',
                r'(let me think|i need to|i should).*?\.',
                r'(analyzing your|processing this).*?\.'
            ]
            
            for pattern in thinking_patterns:
                response = re.sub(pattern, '', response, flags=re.IGNORECASE | re.MULTILINE)
            
            # Remove meta-commentary phrases
            meta_phrases = [
                r'(let me think about this|i\'m thinking|analyzing this|processing this)',
                r'(based on my analysis|after analyzing|upon reflection)',
                r'(i need to consider|i should analyze|let me examine)',
                r'(thinking through this|working through this)'
            ]
            
            for phrase in meta_phrases:
                response = re.sub(phrase, '', response, flags=re.IGNORECASE)
            
            # Clean up extra whitespace and newlines
            response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)  # Multiple newlines to double
            response = re.sub(r'^\s+', '', response)  # Leading whitespace
            response = response.strip()
            
            # If response is empty after cleaning, provide fallback
            if not response or len(response.strip()) < 10:
                return "🤖 I understand your question. Could you please be more specific so I can help you better?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error cleaning thinking process: {e}")
            return response  # Return original if cleaning fails
    
    def generate_greeting_response(self, context) -> str:
        """Generate personalized greeting response based on user preferences"""
        user_id = context.user_id if hasattr(context, 'user_id') else None
        
        # Get user's communication style preference
        comm_style = "professional"
        if user_id:
            comm_style = user_context_manager.get_preference(user_id, "communication_style", "professional")
        
        # Generate greeting based on style and context
        if comm_style == "casual":
            greetings = [
                "👋 Hey! What's up? Ready to check some crypto stuff?",
                "🤖 Yo! What can I help you with today?",
                "✨ Hey there! What's on your crypto mind?",
                "🚀 What's good? Let's dive into some crypto!"
            ]
        elif comm_style == "polite":
            greetings = [
                "👋 Good day! I'd be delighted to assist you with your crypto needs.",
                "🤖 Hello! How may I help you with your cryptocurrency inquiries today?",
                "✨ Greetings! What crypto assistance can I provide for you?",
                "🚀 Hello! I'm here to help with any crypto questions you might have."
            ]
        else:  # professional
            greetings = [
                "👋 Hello! I'm Möbius, your AI crypto assistant. How can I help you today?",
                "🤖 Hi there! Ready to dive into some crypto analysis?",
                "✨ Hello! What can I help you with in the crypto world today?",
                "🚀 Hello! I'm here to help with all your crypto needs."
            ]
        
        # Personalize based on user history
        if user_id and hasattr(context, 'conversation_flow') and context.conversation_flow:
            if comm_style == "casual":
                return "👋 Hey, welcome back! What do you want to check out today?"
            elif comm_style == "polite":
                return "👋 Welcome back! I hope you're having a wonderful day. How may I assist you?"
            else:
                return "👋 Welcome back! What would you like to explore today?"
        
        import random
        return random.choice(greetings)
    
    async def generate_ai_response(self, text: str, context) -> str:
        """Generate AI response using Groq for general questions"""
        if not self.groq_api_key:
            return "🤖 I'd love to help with that question! For now, try using specific commands like /help, /research, or /portfolio."
        
        # Estimate tokens
        estimated_tokens = len(text) // 4 + 300
        
        # Check rate limits
        if not await self.rate_limiter.can_make_request(estimated_tokens):
            return "🤖 I'm processing a lot of requests right now. Please try again in a moment, or use specific commands like /help."
        
        try:
            prompt = self.create_ai_response_prompt(text, context)
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.groq_api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'model': 'llama3-8b-8192',
                    'messages': [
                        {
                            'role': 'system',
                            'content': '''You are Möbius, a helpful crypto trading AI assistant.

CRITICAL RESPONSE RULES:
- Provide ONLY the final response to the user
- Do NOT include any thinking process, analysis steps, or meta-commentary
- Do NOT use <think> tags or show your reasoning process
- Do NOT include phrases like "thinking about", "analyzing", "processing", "let me think"
- Do NOT show any internal deliberation or thought process
- Respond directly and naturally as if speaking to the user
- Be concise, friendly, and informative
- Always suggest relevant commands when appropriate

Respond with ONLY the final answer the user should see - no thinking process visible.'''
                        },
                        {
                            'role': 'user',
                            'content': prompt
                        }
                    ],
                    'max_tokens': 200,
                    'temperature': 0.7
                }
                
                async with session.post(
                    'https://api.groq.com/openai/v1/chat/completions',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        ai_response = data['choices'][0]['message']['content']
                        
                        # CRITICAL: Clean any thinking process that might leak through
                        ai_response = self.clean_thinking_process(ai_response)
                        
                        # Add helpful command suggestions
                        if 'portfolio' in text.lower():
                            ai_response += "\n\n💡 Try: /portfolio"
                        elif any(word in text.lower() for word in ['price', 'cost', 'value']):
                            ai_response += "\n\n💡 Try: /research <token>"
                        elif 'summary' in text.lower():
                            ai_response += "\n\n💡 Try: /summarynow"
                        
                        return ai_response
                    else:
                        logger.error(f"Groq API error: {response.status}")
                        return "🤖 I'm having trouble processing that right now. Try using specific commands like /help or /research."
        
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "🤖 I'm having trouble processing that right now. Try using specific commands like /help or /research."
    
    def create_ai_response_prompt(self, text: str, context) -> str:
        """Create prompt for AI response generation"""
        context_info = ""
        if context.current_topic:
            context_info = f"Current topic: {context.current_topic}\n"
        
        if context.conversation_history:
            recent = context.conversation_history[-2:]  # Last 2 exchanges
            context_info += f"Recent conversation: {recent}\n"
        
        return f"""
{context_info}
User question: "{text}"

Provide a helpful, concise response about crypto/trading. If you suggest actions, mention relevant commands like /portfolio, /research, /alerts, etc.
"""

    def process_query(self, query: str, user_id: int = None) -> Dict[str, any]:
        """Process a natural language query and return intent analysis"""
        try:
            # Analyze intent
            intent = self.analyze_intent(query)
            
            # Extract entities
            entities = self.extract_entities(query)
            
            # Get or create conversation context
            if user_id:
                context = self.get_conversation_context(user_id)
            else:
                context = ConversationContext(user_id=0)
            
            return {
                'intent': intent.name,
                'confidence': intent.confidence,
                'entities': entities,
                'suggested_action': intent.suggested_action,
                'context': context
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'entities': {},
                'suggested_action': 'help',
                'context': None,
                'error': str(e)
            }

# Global instance
nlp_processor = NaturalLanguageProcessor()