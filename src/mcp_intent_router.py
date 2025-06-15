# src/mcp_intent_router.py - Smart Intent Routing for MCP Operations
import asyncio
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from mcp_client import mcp_client
from mcp_ai_orchestrator import ai_orchestrator
from mcp_background_processor import submit_background_job
from mcp_streaming import streaming_manager

logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Types of user intents"""
    IMMEDIATE_QUERY = "immediate"      # Needs instant response
    BACKGROUND_ANALYSIS = "background" # Can be processed in background
    STREAMING_REQUEST = "streaming"    # Needs real-time updates
    COMPLEX_RESEARCH = "complex"       # Requires multiple MCP calls
    SIMPLE_INFO = "simple"            # Basic information request

class RoutingStrategy(Enum):
    """Routing strategies for different intents"""
    DIRECT_RESPONSE = "direct"         # Respond immediately
    BACKGROUND_NOTIFY = "background"   # Process in background, notify when done
    STREAM_SETUP = "stream"           # Set up streaming subscription
    HYBRID_APPROACH = "hybrid"        # Immediate + background processing

@dataclass
class IntentAnalysis:
    """Analysis of user intent"""
    intent_type: IntentType
    routing_strategy: RoutingStrategy
    confidence: float
    keywords: List[str]
    entities: List[str]
    urgency_score: float
    complexity_score: float
    estimated_processing_time: float
    use_mcp: bool = False

class MCPIntentRouter:
    """Smart intent router for optimal MCP operation routing"""

    def __init__(self):
        self.intent_patterns = {}
        self.routing_rules = {}
        self.user_preferences = {}
        self.performance_metrics = {}
        self._initialize_patterns()
        self._initialize_routing_rules()

    def _initialize_patterns(self):
        """Initialize comprehensive intent recognition patterns"""
        self.intent_patterns = {
            # Immediate queries - need instant response (use built-in capabilities first)
            "immediate": [
                # Price queries
                r"(?:what'?s|show|get|tell me|check).*?(?:price|cost|value).*?(?:of|for)?\s*(?:btc|bitcoin|eth|ethereum|sol|solana|ada|cardano|dot|polkadot)",
                r"(?:current|latest|now|today'?s).*?(?:price|value|cost|rate)",
                r"how much (?:is|does|costs?)\s*(?:btc|bitcoin|eth|ethereum|crypto|coin)",
                r"(?:btc|bitcoin|eth|ethereum)\s+(?:price|value|cost|rate)",
                r"price\s+(?:of|for)\s+(?:btc|bitcoin|eth|ethereum)",
                
                # Quick balance/portfolio checks
                r"(?:show|check|get|what'?s).*?(?:my|wallet|portfolio).*?(?:balance|holdings)",
                r"(?:balance|holdings)\s+(?:check|update|status)",
                r"how much.*?(?:do i have|in my wallet|in portfolio)",
                
                # Simple commands
                r"^(?:/start|/help|/portfolio|/balance|/price|/wallet)",
                r"(?:help|assistance)\s+(?:me|with|please)",
                r"(?:quick|fast|urgent)\s+(?:check|look|info|help)",
            ],
            
            # Background analysis - can wait for thorough processing
            "background": [
                r"(?:analyze|analysis|research|study|investigate).*?(?:portfolio|market|trend|performance)",
                r"(?:deep|detailed|comprehensive|thorough|extensive).*?(?:analysis|research|study|review)",
                r"(?:generate|create|build|prepare).*?(?:report|analysis|summary|breakdown)",
                r"(?:compare|comparison|contrast).*?(?:across|between|multiple|different)",
                r"(?:historical|past|previous|trend|pattern).*?(?:analysis|data|performance|behavior)",
                r"(?:risk|volatility|correlation).*?(?:analysis|assessment|evaluation)",
                r"(?:performance|returns|gains|losses).*?(?:analysis|review|breakdown)",
            ],
            
            # Streaming requests - need real-time updates
            "streaming": [
                r"(?:monitor|watch|track|follow|observe).*?(?:price|portfolio|wallet|market|movements)",
                r"(?:alert|notify|tell me|let me know).*?(?:when|if).*?(?:price|value|change|reaches|drops|rises)",
                r"(?:real.?time|live|continuous|ongoing).*?(?:updates|monitoring|tracking|feed)",
                r"(?:subscribe|follow|watch).*?(?:updates|changes|movements|notifications)",
                r"(?:keep me|let me know|inform me).*?(?:updated|informed|posted|notified)",
                r"set.*?(?:alert|notification|reminder).*?(?:for|when|if)",
                r"(?:stream|feed).*?(?:data|prices|updates)",
            ],
            
            # Complex research - needs multiple MCP calls (use MCP when necessary)
            "complex": [
                r"(?:cross.?chain|multi.?chain|inter.?chain).*?(?:analysis|comparison|tracking|arbitrage)",
                r"(?:defi|yield|farming|liquidity|staking).*?(?:opportunities|analysis|comparison|optimization)",
                r"(?:arbitrage|profit|opportunity|edge).*?(?:analysis|finding|detection|hunting)",
                r"(?:whale|large|institutional).*?(?:movements|transactions|analysis|tracking)",
                r"(?:social|sentiment|community|market).*?(?:analysis|research|monitoring|intelligence)",
                r"(?:on.?chain|blockchain).*?(?:analysis|investigation|forensics|tracking)",
                r"(?:smart contract|protocol|dapp).*?(?:analysis|audit|research|investigation)",
                r"(?:market making|liquidity|orderbook).*?(?:analysis|strategy|optimization)",
                r"(?:correlation|regression|statistical).*?(?:analysis|modeling|prediction)",
                r"(?:machine learning|ai|predictive).*?(?:analysis|modeling|forecasting)",
            ],
            
            # Simple info - basic information requests (use built-in knowledge first)
            "simple": [
                # Greetings and basic interactions
                r"^(?:hello|hi|hey|greetings|good morning|good afternoon|good evening)(?:\s|$|!|\?|,)",
                r"(?:how are you|what'?s up|how'?s it going)",
                r"(?:thank you|thanks|thx|appreciate)",
                
                # Basic questions
                r"(?:what|who|where|when|how)\s+(?:is|are|does|do|can|will)\s+\w+",
                r"(?:explain|define|meaning|definition)\s+(?:of|what\s+is|for)",
                r"(?:help|assistance|support|guide)\s+(?:with|for|about|me)",
                r"(?:basic|simple|quick|general)\s+(?:info|information|explanation|overview)",
                
                # Crypto basics
                r"what\s+(?:is|are)\s+(?:bitcoin|ethereum|crypto|blockchain|defi|nft)",
                r"how\s+(?:does|do)\s+(?:bitcoin|ethereum|crypto|blockchain|defi)\s+work",
                r"(?:difference|compare)\s+between\s+(?:bitcoin|ethereum|crypto)",
                
                # Simple price queries (single token, no complex analysis)
                r"(?:price|value|cost)\s+(?:of|for)\s+\w+(?:\s+(?:today|now|current))?$",
                r"(?:how\s+much|what\s+is\s+the\s+price)",
                
                # Basic wallet operations
                r"(?:create|make|generate)\s+(?:wallet|address)",
                r"(?:send|transfer)\s+(?:crypto|tokens|coins)",
                r"(?:receive|get)\s+(?:crypto|tokens|coins)",
            ],
            
            # Command detection - explicit commands
            "command": [
                r"^/\w+",  # Slash commands
                r"(?:run|execute|perform)\s+(?:command|function|operation)",
                r"(?:start|begin|initiate)\s+(?:process|operation|function)",
                r"(?:stop|end|terminate|cancel)\s+(?:process|operation|function)",
            ]
        }

    def _initialize_routing_rules(self):
        """Initialize intelligent routing rules - MCP as fallback only"""
        self.routing_rules = {
            IntentType.IMMEDIATE_QUERY: {
                "strategy": RoutingStrategy.DIRECT_RESPONSE,
                "max_processing_time": 3.0,
                "use_cache": True,
                "use_mcp": False,  # Always try built-in first
                "fallback_to_mcp": True,  # Only if built-in fails
                "built_in_capabilities": ["price_lookup", "balance_check", "basic_portfolio", "simple_commands"],
                "mcp_threshold": 0.8  # Only use MCP if confidence > 80%
            },
            
            IntentType.BACKGROUND_ANALYSIS: {
                "strategy": RoutingStrategy.BACKGROUND_NOTIFY,
                "max_processing_time": 60.0,
                "use_cache": False,
                "use_mcp": False,  # Try built-in analysis first
                "fallback_to_mcp": True,  # Use MCP for complex analysis
                "built_in_capabilities": ["portfolio_analysis", "performance_metrics", "basic_research"],
                "priority": 2,
                "mcp_threshold": 0.7
            },
            
            IntentType.STREAMING_REQUEST: {
                "strategy": RoutingStrategy.STREAM_SETUP,
                "max_subscriptions_per_user": 5,
                "rate_limit_window": 3600,
                "auto_unsubscribe_after": 86400,
                "use_mcp": False,  # Built-in streaming preferred
                "fallback_to_mcp": False,  # Streaming should be handled internally
                "built_in_capabilities": ["price_alerts", "portfolio_monitoring", "balance_tracking"]
            },
            
            IntentType.COMPLEX_RESEARCH: {
                "strategy": RoutingStrategy.HYBRID_APPROACH,
                "immediate_response_timeout": 5.0,
                "background_processing": True,
                "use_mcp": False,  # Try built-in first, even for complex queries
                "fallback_to_mcp": True,  # Use MCP only when built-in is insufficient
                "built_in_capabilities": ["basic_analysis", "simple_research"],
                "priority": 3,
                "mcp_threshold": 0.6  # Lower threshold for complex queries
            },
            
            IntentType.SIMPLE_INFO: {
                "strategy": RoutingStrategy.DIRECT_RESPONSE,
                "max_processing_time": 2.0,
                "use_cache": True,
                "use_mcp": False,  # Never use MCP for simple info
                "fallback_to_mcp": False,  # Built-in should handle all simple queries
                "built_in_capabilities": ["basic_info", "help", "greetings", "explanations"]
            }
        }
        
        # Built-in capability handlers
        self.built_in_handlers = {
            "price_lookup": self._handle_price_query,
            "balance_check": self._handle_balance_query,
            "basic_portfolio": self._handle_portfolio_query,
            "simple_commands": self._handle_simple_command,
            "portfolio_analysis": self._handle_portfolio_analysis,
            "performance_metrics": self._handle_performance_metrics,
            "basic_research": self._handle_basic_research,
            "price_alerts": self._handle_price_alerts,
            "portfolio_monitoring": self._handle_portfolio_monitoring,
            "balance_tracking": self._handle_balance_tracking,
            "basic_analysis": self._handle_basic_analysis,
            "simple_research": self._handle_simple_research,
            "basic_info": self._handle_basic_info,
            "help": self._handle_help,
            "greetings": self._handle_greetings,
            "explanations": self._handle_explanations
        }

    async def analyze_intent(self, user_id: int, message: str, context: dict = None) -> IntentAnalysis:
        """Analyze user intent and determine optimal routing strategy"""
        try:
            # Ensure message is a string
            if not isinstance(message, str):
                if hasattr(message, 'text'):
                    message = message.text
                else:
                    message = str(message)
            
            message_lower = message.lower()
            
            # Extract keywords and entities
            keywords = self._extract_keywords(message_lower)
            entities = self._extract_entities(message)
            
            # Determine intent type
            intent_type, confidence = self._classify_intent(message_lower)
            
            # Calculate urgency and complexity scores
            urgency_score = self._calculate_urgency_score(message_lower, keywords)
            complexity_score = self._calculate_complexity_score(message_lower, keywords, entities)
            
            # Estimate processing time
            estimated_time = self._estimate_processing_time(intent_type, complexity_score)
            
            # Determine routing strategy
            routing_strategy = self._determine_routing_strategy(
                intent_type, urgency_score, complexity_score, user_id
            )
            
            # Try built-in capabilities first before determining MCP usage
            should_use_mcp = self._should_use_mcp(intent_type, confidence, complexity_score)
            
            return IntentAnalysis(
                intent_type=intent_type,
                routing_strategy=routing_strategy,
                confidence=confidence,
                keywords=keywords,
                entities=entities,
                urgency_score=urgency_score,
                complexity_score=complexity_score,
                estimated_processing_time=estimated_time,
                use_mcp=should_use_mcp
            )
            
        except Exception as e:
            logger.error(f"❌ Intent analysis failed: {e}")
            # Return safe default
            return IntentAnalysis(
                intent_type=IntentType.SIMPLE_INFO,
                routing_strategy=RoutingStrategy.DIRECT_RESPONSE,
                confidence=0.5,
                keywords=[],
                entities=[],
                urgency_score=0.5,
                complexity_score=0.3,
                estimated_processing_time=2.0
            )

    def _classify_intent(self, message: str) -> Tuple[IntentType, float]:
        """Advanced intent classification with natural language understanding"""
        message_lower = message.lower().strip()
        
        # Multi-layered intent classification
        intent_scores = {}
        
        # Layer 1: Pattern matching with weighted scoring
        for intent_name, patterns in self.intent_patterns.items():
            score = 0
            pattern_matches = 0
            
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    pattern_matches += 1
                    # Weight patterns differently based on specificity
                    if len(pattern) > 50:  # Complex patterns get higher weight
                        score += 2.0
                    elif len(pattern) > 30:  # Medium patterns
                        score += 1.5
                    else:  # Simple patterns
                        score += 1.0
            
            if pattern_matches > 0:
                # Calculate confidence based on pattern matches and complexity
                base_confidence = min(score / len(patterns), 1.0)
                # Boost for multiple pattern matches
                if pattern_matches > 1:
                    base_confidence = min(base_confidence * 1.3, 1.0)
                intent_scores[intent_name] = base_confidence
        
        # Layer 2: Semantic analysis using keywords and context
        semantic_scores = self._analyze_semantic_intent(message_lower)
        
        # Layer 3: Combine pattern and semantic scores
        combined_scores = {}
        all_intents = set(intent_scores.keys()) | set(semantic_scores.keys())
        
        for intent in all_intents:
            pattern_score = intent_scores.get(intent, 0.0)
            semantic_score = semantic_scores.get(intent, 0.0)
            
            # Weighted combination: 60% pattern, 40% semantic
            combined_score = (pattern_score * 0.6) + (semantic_score * 0.4)
            
            if combined_score > 0.1:  # Only consider meaningful scores
                combined_scores[intent] = combined_score
        
        # Layer 4: Apply business logic and context rules
        final_intent, final_confidence = self._apply_business_rules(message_lower, combined_scores)
        
        # Layer 5: Confidence calibration
        final_confidence = self._calibrate_confidence(message_lower, final_intent, final_confidence)
        
        # Map to IntentType enum
        intent_mapping = {
            "immediate": IntentType.IMMEDIATE_QUERY,
            "background": IntentType.BACKGROUND_ANALYSIS,
            "streaming": IntentType.STREAMING_REQUEST,
            "complex": IntentType.COMPLEX_RESEARCH,
            "simple": IntentType.SIMPLE_INFO,
            "command": IntentType.IMMEDIATE_QUERY  # Commands are immediate
        }
        
        return intent_mapping.get(final_intent, IntentType.SIMPLE_INFO), final_confidence
    
    def _analyze_semantic_intent(self, message: str) -> Dict[str, float]:
        """Analyze semantic intent using keyword analysis and context"""
        semantic_scores = {}
        
        # Define semantic keyword groups with weights
        keyword_groups = {
            "immediate": {
                "high": ["price", "current", "now", "quick", "fast", "urgent", "asap", "immediately"],
                "medium": ["show", "get", "tell", "check", "what", "how much", "value", "cost"],
                "low": ["btc", "bitcoin", "eth", "ethereum", "crypto", "coin"]
            },
            "simple": {
                "high": ["hello", "hi", "hey", "thanks", "thank you", "help", "what is", "explain"],
                "medium": ["basic", "simple", "general", "info", "information"],
                "low": ["define", "meaning", "how", "why", "when", "where"]
            },
            "complex": {
                "high": ["analysis", "analyze", "research", "investigate", "deep", "comprehensive"],
                "medium": ["defi", "yield", "arbitrage", "correlation", "statistical", "machine learning"],
                "low": ["advanced", "detailed", "thorough", "complex", "sophisticated"]
            },
            "streaming": {
                "high": ["monitor", "watch", "track", "alert", "notify", "real-time", "live"],
                "medium": ["subscribe", "follow", "continuous", "ongoing", "stream"],
                "low": ["updates", "changes", "movements", "feed"]
            },
            "background": {
                "high": ["report", "summary", "breakdown", "comparison", "historical"],
                "medium": ["performance", "trends", "patterns", "metrics"],
                "low": ["analyze", "study", "review", "evaluate"]
            }
        }
        
        # Calculate semantic scores
        for intent, groups in keyword_groups.items():
            score = 0.0
            
            for weight_level, keywords in groups.items():
                weight = {"high": 3.0, "medium": 2.0, "low": 1.0}[weight_level]
                matches = sum(1 for keyword in keywords if keyword in message)
                score += matches * weight
            
            if score > 0:
                # Normalize score (max possible score per intent varies)
                max_possible = sum(len(keywords) * {"high": 3.0, "medium": 2.0, "low": 1.0}[level] 
                                 for level, keywords in groups.items())
                normalized_score = min(score / max_possible, 1.0)
                semantic_scores[intent] = normalized_score
        
        return semantic_scores
    
    def _apply_business_rules(self, message: str, scores: Dict[str, float]) -> Tuple[str, float]:
        """Apply business logic and context rules to refine intent classification"""
        
        # Rule 1: Slash commands are always immediate
        if message.startswith('/'):
            return "immediate", 0.95
        
        # Rule 2: Greetings are always simple
        greeting_words = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if any(greeting in message for greeting in greeting_words):
            return "simple", 0.9
        
        # Rule 3: Price queries with specific tokens are immediate
        price_patterns = [
            r"(?:price|cost|value).*?(?:btc|bitcoin|eth|ethereum|sol|ada|dot)",
            r"(?:btc|bitcoin|eth|ethereum).*?(?:price|cost|value)",
            r"how much.*?(?:btc|bitcoin|eth|ethereum|crypto)"
        ]
        if any(re.search(pattern, message, re.IGNORECASE) for pattern in price_patterns):
            return "immediate", 0.9
        
        # Rule 4: Complex analysis keywords override simple patterns
        complex_indicators = ["cross-chain", "multi-chain", "defi opportunities", "arbitrage", 
                            "whale movements", "on-chain analysis", "smart contract audit"]
        if any(indicator in message for indicator in complex_indicators):
            return "complex", 0.85
        
        # Rule 5: Streaming keywords with time indicators
        streaming_indicators = ["monitor", "watch", "track", "alert", "notify", "real-time", "live"]
        time_indicators = ["continuously", "ongoing", "24/7", "always", "constantly"]
        if (any(s_ind in message for s_ind in streaming_indicators) and 
            any(t_ind in message for t_ind in time_indicators)):
            return "streaming", 0.85
        
        # Rule 6: If no clear winner, use highest score
        if not scores:
            return "simple", 0.5
        
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]
        
        # Rule 7: Confidence threshold - if too low, default to simple
        if best_score < 0.3:
            return "simple", 0.6
        
        return best_intent, best_score
    
    def _calibrate_confidence(self, message: str, intent: str, confidence: float) -> float:
        """Calibrate confidence based on message characteristics"""
        
        # Boost confidence for clear, unambiguous messages
        if len(message.split()) <= 3:  # Very short messages
            if intent == "simple":
                confidence = min(confidence + 0.1, 1.0)
        
        # Boost confidence for messages with clear intent indicators
        clear_indicators = {
            "immediate": ["now", "current", "quick", "fast", "urgent"],
            "simple": ["hello", "help", "what is", "explain"],
            "complex": ["analysis", "research", "comprehensive", "detailed"],
            "streaming": ["monitor", "track", "alert", "real-time"],
            "background": ["report", "summary", "historical", "trends"]
        }
        
        if intent in clear_indicators:
            indicator_matches = sum(1 for indicator in clear_indicators[intent] if indicator in message)
            if indicator_matches >= 2:
                confidence = min(confidence + 0.15, 1.0)
            elif indicator_matches >= 1:
                confidence = min(confidence + 0.1, 1.0)
        
        # Reduce confidence for ambiguous messages
        ambiguous_words = ["maybe", "perhaps", "might", "could", "possibly", "not sure"]
        if any(word in message for word in ambiguous_words):
            confidence = max(confidence - 0.2, 0.3)
        
        # Ensure minimum confidence for recognized patterns
        if confidence > 0.1:
            confidence = max(confidence, 0.5)
        
        return confidence

    # Built-in capability handlers (use these before MCP)
    async def _handle_price_query(self, message: str, context: dict) -> Optional[str]:
        """Handle price queries using built-in capabilities"""
        # Extract token from message
        tokens = ["btc", "bitcoin", "eth", "ethereum", "sol", "solana", "ada", "cardano"]
        found_token = None
        for token in tokens:
            if token in message.lower():
                found_token = token
                break
        
        if found_token:
            return f"🔍 Checking {found_token.upper()} price using built-in price feed..."
        return None
    
    async def _handle_balance_query(self, message: str, context: dict) -> Optional[str]:
        """Handle balance queries using built-in wallet functionality"""
        return "💰 Checking your wallet balance using built-in wallet manager..."
    
    async def _handle_portfolio_query(self, message: str, context: dict) -> Optional[str]:
        """Handle portfolio queries using built-in portfolio manager"""
        return "📊 Generating portfolio overview using built-in analytics..."
    
    async def _handle_simple_command(self, message: str, context: dict) -> Optional[str]:
        """Handle simple commands using built-in command processor"""
        if message.startswith('/'):
            return f"⚡ Processing command {message} using built-in handler..."
        return None
    
    async def _handle_portfolio_analysis(self, message: str, context: dict) -> Optional[str]:
        """Handle portfolio analysis using built-in analytics"""
        return "📈 Running portfolio analysis using built-in analytics engine..."
    
    async def _handle_performance_metrics(self, message: str, context: dict) -> Optional[str]:
        """Handle performance metrics using built-in calculations"""
        return "📊 Calculating performance metrics using built-in algorithms..."
    
    async def _handle_basic_research(self, message: str, context: dict) -> Optional[str]:
        """Handle basic research using built-in knowledge base"""
        return "🔍 Conducting research using built-in knowledge base..."
    
    async def _handle_price_alerts(self, message: str, context: dict) -> Optional[str]:
        """Handle price alerts using built-in alert system"""
        return "🚨 Setting up price alert using built-in monitoring system..."
    
    async def _handle_portfolio_monitoring(self, message: str, context: dict) -> Optional[str]:
        """Handle portfolio monitoring using built-in tracking"""
        return "👁️ Setting up portfolio monitoring using built-in tracker..."
    
    async def _handle_balance_tracking(self, message: str, context: dict) -> Optional[str]:
        """Handle balance tracking using built-in wallet monitor"""
        return "💰 Setting up balance tracking using built-in wallet monitor..."
    
    async def _handle_basic_analysis(self, message: str, context: dict) -> Optional[str]:
        """Handle basic analysis using built-in tools"""
        return "🔬 Running basic analysis using built-in analytical tools..."
    
    async def _handle_simple_research(self, message: str, context: dict) -> Optional[str]:
        """Handle simple research using built-in resources"""
        return "📚 Conducting research using built-in resources..."
    
    async def _handle_basic_info(self, message: str, context: dict) -> Optional[str]:
        """Handle basic info requests using built-in knowledge"""
        return "ℹ️ Providing information using built-in knowledge base..."
    
    async def _handle_help(self, message: str, context: dict) -> Optional[str]:
        """Handle help requests using built-in help system"""
        return "❓ Providing help using built-in assistance system..."
    
    async def _handle_greetings(self, message: str, context: dict) -> Optional[str]:
        """Handle greetings using built-in responses"""
        greetings = ["Hello! 👋", "Hi there! 😊", "Hey! How can I help?", "Greetings! 🤖"]
        import random
        return random.choice(greetings)
    
    async def _handle_explanations(self, message: str, context: dict) -> Optional[str]:
        """Handle explanations using built-in knowledge"""
        return "📖 Providing explanation using built-in knowledge base..."
    
    async def _try_built_in_capabilities(self, intent_type: IntentType, message: str, context: dict) -> Optional[str]:
        """Try to handle request using built-in capabilities before falling back to MCP"""
        rules = self.routing_rules.get(intent_type, {})
        capabilities = rules.get("built_in_capabilities", [])
        
        # Try each capability in order
        for capability in capabilities:
            handler = self.built_in_handlers.get(capability)
            if handler:
                try:
                    result = await handler(message, context)
                    if result:
                        logger.info(f"✅ Handled using built-in capability: {capability}")
                        return result
                except Exception as e:
                    logger.warning(f"Built-in handler {capability} failed: {e}")
                    continue
        
        return None
    
    def _should_use_mcp(self, intent_type: IntentType, confidence: float, complexity_score: float) -> bool:
        """Intelligent decision on whether to use MCP based on intent analysis"""
        rules = self.routing_rules.get(intent_type, {})
        
        # Never use MCP for simple info
        if intent_type == IntentType.SIMPLE_INFO:
            return False
        
        # Never use MCP for streaming (should be handled internally)
        if intent_type == IntentType.STREAMING_REQUEST:
            return False
        
        # Check if MCP is explicitly disabled for this intent type
        if not rules.get("fallback_to_mcp", False):
            return False
        
        # Check confidence and complexity thresholds
        mcp_threshold = rules.get("mcp_threshold", 0.7)
        
        # Use MCP only if:
        # 1. Confidence is high enough AND complexity is high
        # 2. OR it's a complex research query with medium confidence
        if intent_type == IntentType.COMPLEX_RESEARCH:
            return confidence >= 0.6 and complexity_score >= 0.7
        elif intent_type == IntentType.BACKGROUND_ANALYSIS:
            return confidence >= mcp_threshold and complexity_score >= 0.6
        elif intent_type == IntentType.IMMEDIATE_QUERY:
            # Only use MCP for immediate queries if they're very complex
            return confidence >= mcp_threshold and complexity_score >= 0.8
        
        return False
    
    async def process_with_intelligent_routing(self, user_id: int, message: str, context: dict = None) -> dict:
        """Process message with intelligent routing - built-in first, MCP as fallback"""
        if context is None:
            context = {}
        
        # Analyze intent
        analysis = await self.analyze_intent(user_id, message, context)
        
        logger.info(f"🎯 Intent: {analysis.intent_type.value}, Strategy: {analysis.routing_strategy.value}, "
                   f"Confidence: {analysis.confidence:.2f}, Use MCP: {getattr(analysis, 'use_mcp', False)}")
        
        # Try built-in capabilities first
        built_in_result = await self._try_built_in_capabilities(analysis.intent_type, message, context)
        
        if built_in_result:
            return {
                "success": True,
                "response": built_in_result,
                "method": "built_in",
                "intent": analysis.intent_type.value,
                "confidence": analysis.confidence
            }
        
        # Fall back to MCP only if necessary and allowed
        if getattr(analysis, 'use_mcp', False):
            logger.info(f"🔄 Falling back to MCP for {analysis.intent_type.value}")
            return {
                "success": False,
                "response": "Falling back to MCP for advanced processing...",
                "method": "mcp_fallback",
                "intent": analysis.intent_type.value,
                "confidence": analysis.confidence,
                "requires_mcp": True
            }
        
        # If no MCP fallback allowed, provide a helpful response
        return {
            "success": True,
            "response": f"I understand you're asking about {analysis.intent_type.value.replace('_', ' ')}, "
                      f"but I can handle this using my built-in capabilities. Let me help you with that!",
            "method": "built_in_fallback",
            "intent": analysis.intent_type.value,
            "confidence": analysis.confidence
        }

    def _extract_keywords(self, message: str) -> List[str]:
        """Extract relevant keywords from message"""
        crypto_keywords = [
            "bitcoin", "btc", "ethereum", "eth", "polygon", "matic", "arbitrum", "arb",
            "optimism", "op", "base", "avalanche", "avax", "solana", "sol",
            "price", "value", "cost", "market", "trading", "volume", "liquidity",
            "defi", "yield", "farming", "staking", "lending", "borrowing",
            "wallet", "address", "transaction", "transfer", "swap", "bridge",
            "analysis", "research", "monitor", "track", "alert", "notify"
        ]
        
        found_keywords = []
        for keyword in crypto_keywords:
            if keyword in message:
                found_keywords.append(keyword)
        
        return found_keywords

    def _extract_entities(self, message: str) -> List[str]:
        """Extract entities like addresses, symbols, numbers"""
        entities = []
        
        # Extract wallet addresses
        address_pattern = r'0x[a-fA-F0-9]{40}'
        addresses = re.findall(address_pattern, message)
        entities.extend(addresses)
        
        # Extract crypto symbols (3-5 uppercase letters)
        symbol_pattern = r'\b[A-Z]{3,5}\b'
        symbols = re.findall(symbol_pattern, message)
        entities.extend(symbols)
        
        # Extract numbers (prices, amounts)
        number_pattern = r'\$?[\d,]+\.?\d*'
        numbers = re.findall(number_pattern, message)
        entities.extend(numbers)
        
        return entities

    def _calculate_urgency_score(self, message: str, keywords: List[str]) -> float:
        """Calculate urgency score (0-1)"""
        urgency_indicators = [
            "urgent", "asap", "quickly", "fast", "now", "immediately", "current",
            "latest", "today", "right now", "quick", "hurry", "emergency"
        ]
        
        score = 0.0
        for indicator in urgency_indicators:
            if indicator in message:
                score += 0.2
        
        # Time-sensitive keywords
        if any(word in keywords for word in ["price", "value", "current", "latest"]):
            score += 0.3
        
        return min(score, 1.0)

    def _calculate_complexity_score(self, message: str, keywords: List[str], entities: List[str]) -> float:
        """Calculate complexity score (0-1)"""
        complexity_indicators = [
            "analyze", "analysis", "research", "compare", "comparison", "cross-chain",
            "multi-chain", "comprehensive", "detailed", "deep", "thorough",
            "arbitrage", "yield", "farming", "defi", "liquidity", "whale"
        ]
        
        score = 0.0
        
        # Base complexity from indicators
        for indicator in complexity_indicators:
            if indicator in message:
                score += 0.15
        
        # Multiple entities increase complexity
        if len(entities) > 3:
            score += 0.2
        elif len(entities) > 1:
            score += 0.1
        
        # Multiple keywords increase complexity
        if len(keywords) > 5:
            score += 0.2
        elif len(keywords) > 2:
            score += 0.1
        
        # Long messages tend to be more complex
        if len(message.split()) > 20:
            score += 0.1
        
        return min(score, 1.0)

    def _estimate_processing_time(self, intent_type: IntentType, complexity_score: float) -> float:
        """Estimate processing time in seconds"""
        base_times = {
            IntentType.IMMEDIATE_QUERY: 2.0,
            IntentType.BACKGROUND_ANALYSIS: 30.0,
            IntentType.STREAMING_REQUEST: 5.0,
            IntentType.COMPLEX_RESEARCH: 45.0,
            IntentType.SIMPLE_INFO: 1.0
        }
        
        base_time = base_times.get(intent_type, 5.0)
        complexity_multiplier = 1 + complexity_score
        
        return base_time * complexity_multiplier

    def _determine_routing_strategy(self, intent_type: IntentType, urgency_score: float, 
                                  complexity_score: float, user_id: int) -> RoutingStrategy:
        """Determine the best routing strategy"""
        rules = self.routing_rules.get(intent_type, {})
        base_strategy = rules.get("strategy", RoutingStrategy.DIRECT_RESPONSE)
        
        # Override based on urgency and complexity
        if urgency_score > 0.7 and complexity_score < 0.5:
            return RoutingStrategy.DIRECT_RESPONSE
        
        if complexity_score > 0.7 and urgency_score < 0.5:
            return RoutingStrategy.BACKGROUND_NOTIFY
        
        if urgency_score > 0.5 and complexity_score > 0.5:
            return RoutingStrategy.HYBRID_APPROACH
        
        return base_strategy

    async def route_request(self, user_id: int, message: str, context: dict = None) -> dict:
        """Route request based on intent analysis"""
        try:
            # Analyze intent
            analysis = await self.analyze_intent(user_id, message, context)
            
            logger.info(f"🎯 Intent: {analysis.intent_type.value}, Strategy: {analysis.routing_strategy.value}, Confidence: {analysis.confidence:.2f}")
            
            # Route based on strategy
            if analysis.routing_strategy == RoutingStrategy.DIRECT_RESPONSE:
                return await self._handle_direct_response(user_id, message, analysis, context)
            
            elif analysis.routing_strategy == RoutingStrategy.BACKGROUND_NOTIFY:
                return await self._handle_background_processing(user_id, message, analysis, context)
            
            elif analysis.routing_strategy == RoutingStrategy.STREAM_SETUP:
                return await self._handle_streaming_setup(user_id, message, analysis, context)
            
            elif analysis.routing_strategy == RoutingStrategy.HYBRID_APPROACH:
                return await self._handle_hybrid_approach(user_id, message, analysis, context)
            
            else:
                return await self._handle_direct_response(user_id, message, analysis, context)
                
        except Exception as e:
            logger.error(f"❌ Request routing failed: {e}")
            return {
                "success": False,
                "error": "Failed to route request",
                "fallback_response": "I'm experiencing technical difficulties. Please try rephrasing your request."
            }

    async def _handle_direct_response(self, user_id: int, message: str, 
                                    analysis: IntentAnalysis, context: dict) -> dict:
        """Handle direct response routing"""
        try:
            # Use AI orchestrator for immediate response
            response = await ai_orchestrator.generate_enhanced_response(
                message, context, analysis.intent_type.value
            )
            
            return {
                "success": True,
                "response": response.get("response", "I understand your request."),
                "routing_strategy": "direct",
                "processing_time": analysis.estimated_processing_time,
                "intent_confidence": analysis.confidence
            }
            
        except Exception as e:
            logger.error(f"❌ Direct response failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_response": "I'm processing your request, but it's taking longer than expected."
            }

    async def _handle_background_processing(self, user_id: int, message: str, 
                                          analysis: IntentAnalysis, context: dict) -> dict:
        """Handle background processing routing"""
        try:
            # Submit to background processor
            job_id = await submit_background_job(
                user_id=user_id,
                job_type=analysis.intent_type.value,
                parameters={
                    "message": message,
                    "context": context,
                    "analysis": analysis.__dict__
                },
                priority=2
            )
            
            return {
                "success": True,
                "response": f"🔄 I'm analyzing your request in the background. This may take {analysis.estimated_processing_time:.0f} seconds. I'll notify you when complete.",
                "routing_strategy": "background",
                "job_id": job_id,
                "estimated_completion": analysis.estimated_processing_time
            }
            
        except Exception as e:
            logger.error(f"❌ Background processing failed: {e}")
            return await self._handle_direct_response(user_id, message, analysis, context)

    async def _handle_streaming_setup(self, user_id: int, message: str, 
                                    analysis: IntentAnalysis, context: dict) -> dict:
        """Handle streaming setup routing"""
        try:
            # Extract streaming parameters from message
            stream_params = self._extract_streaming_parameters(message, analysis)
            
            # Set up streaming subscription
            subscription_id = await streaming_manager.subscribe(
                user_id=user_id,
                stream_type=stream_params["type"],
                parameters=stream_params["params"],
                callback=lambda data: self._handle_stream_callback(user_id, data)
            )
            
            return {
                "success": True,
                "response": f"📡 Real-time monitoring activated! I'll keep you updated on {stream_params['description']}.",
                "routing_strategy": "streaming",
                "subscription_id": subscription_id,
                "stream_type": stream_params["type"]
            }
            
        except Exception as e:
            logger.error(f"❌ Streaming setup failed: {e}")
            return await self._handle_direct_response(user_id, message, analysis, context)

    async def _handle_hybrid_approach(self, user_id: int, message: str, 
                                    analysis: IntentAnalysis, context: dict) -> dict:
        """Handle hybrid approach routing"""
        try:
            # Provide immediate response
            immediate_response = await ai_orchestrator.generate_enhanced_response(
                message, context, analysis.intent_type.value
            )
            
            # Also submit for background processing
            job_id = await submit_background_job(
                user_id=user_id,
                job_type=f"detailed_{analysis.intent_type.value}",
                parameters={
                    "message": message,
                    "context": context,
                    "analysis": analysis.__dict__
                },
                priority=3
            )
            
            return {
                "success": True,
                "response": immediate_response.get("response", "") + f"\n\n🔄 I'm also preparing a detailed analysis in the background.",
                "routing_strategy": "hybrid",
                "job_id": job_id,
                "immediate_response": True
            }
            
        except Exception as e:
            logger.error(f"❌ Hybrid approach failed: {e}")
            return await self._handle_direct_response(user_id, message, analysis, context)

    def _extract_streaming_parameters(self, message: str, analysis: IntentAnalysis) -> dict:
        """Extract streaming parameters from message"""
        # Default streaming setup
        stream_params = {
            "type": "price_feed",
            "params": {"symbols": ["BTC", "ETH"]},
            "description": "price movements"
        }
        
        # Extract symbols from entities
        symbols = [entity for entity in analysis.entities if len(entity) <= 5 and entity.isupper()]
        if symbols:
            stream_params["params"]["symbols"] = symbols
            stream_params["description"] = f"{', '.join(symbols)} price movements"
        
        # Determine stream type from keywords
        if any(word in analysis.keywords for word in ["whale", "large", "transaction"]):
            stream_params["type"] = "whale_alerts"
            stream_params["description"] = "whale movements"
        elif any(word in analysis.keywords for word in ["news", "social", "sentiment"]):
            stream_params["type"] = "social_sentiment"
            stream_params["description"] = "social sentiment changes"
        elif any(word in analysis.keywords for word in ["defi", "protocol", "yield"]):
            stream_params["type"] = "defi_events"
            stream_params["description"] = "DeFi protocol events"
        
        return stream_params

    async def _handle_stream_callback(self, user_id: int, data: dict):
        """Handle streaming data callback"""
        try:
            # This would typically send a message to the user
            # Implementation depends on the messaging system
            logger.info(f"📡 Stream data for user {user_id}: {data}")
            
        except Exception as e:
            logger.error(f"❌ Stream callback failed: {e}")

# Global intent router instance
intent_router = MCPIntentRouter()

async def route_user_request(user_id: int, message: str, context: dict = None) -> dict:
    """Route user request through smart intent analysis"""
    return await intent_router.route_request(user_id, message, context)

async def analyze_user_intent(user_id: int, message: str, context: dict = None) -> dict:
    """Analyze user intent without routing"""
    analysis = await intent_router.analyze_intent(user_id, message, context)
    return {
        "intent_type": analysis.intent_type.value,
        "routing_strategy": analysis.routing_strategy.value,
        "confidence": analysis.confidence,
        "urgency_score": analysis.urgency_score,
        "complexity_score": analysis.complexity_score,
        "estimated_processing_time": analysis.estimated_processing_time,
        "keywords": analysis.keywords,
        "entities": analysis.entities
    }