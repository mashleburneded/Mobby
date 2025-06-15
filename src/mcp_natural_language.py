# src/mcp_natural_language.py - Enhanced Natural Language Processing with MCP
import asyncio
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json

from mcp_client import mcp_client
from mcp_ai_orchestrator import ai_orchestrator
from mcp_background_processor import submit_background_job

logger = logging.getLogger(__name__)

class MCPNaturalLanguageProcessor:
    """Enhanced natural language processor with MCP integration"""

    def __init__(self):
        self.intent_patterns = {}
        self.context_memory = {}  # User context memory
        self.conversation_history = {}  # Conversation tracking
        self.entity_extractors = {}

    async def initialize(self):
        """Initialize NLP processor"""
        try:
            # Define comprehensive intent patterns for better natural language understanding
            self.intent_patterns = {
                "price_query": [
                    r"(?:what'?s|show|get|tell me).*?(?:price|cost|value).*?(?:of|for)?\s*(\w+)",
                    r"(\w+)\s*(?:price|cost|value)",
                    r"how much (?:is|does|costs?)\s*(\w+)",
                    r"price (?:of|for)\s*(\w+)",
                    r"(\w+)\s*(?:trading at|costs?|priced at)",
                ],
                "market_analysis": [
                    r"(?:analyze|analysis|research|study).*?(?:market|crypto|token|coin)",
                    r"(?:market|crypto|token)\s*(?:analysis|research|study)",
                    r"what'?s happening (?:in|with|to) (?:the )?(?:market|crypto)",
                    r"market (?:overview|summary|update|status)",
                    r"crypto (?:news|updates|trends)",
                ],
                "portfolio_query": [
                    r"(?:show|display|get|check).*?(?:portfolio|holdings|balance)",
                    r"(?:my|our)\s*(?:portfolio|holdings|balance|assets)",
                    r"what do i (?:own|have|hold)",
                    r"portfolio (?:overview|summary|status)",
                    r"(?:check|show) (?:my )?(?:holdings|assets)",
                ],
                "wallet_analysis": [
                    r"(?:analyze|check|track|monitor).*?(?:wallet|address)",
                    r"wallet\s*(?:analysis|tracking|monitoring)",
                    r"(?:0x[a-fA-F0-9]{40})",  # Ethereum address pattern
                    r"(?:track|monitor|analyze)\s*(?:this|that)?\s*(?:wallet|address)",
                    r"wallet (?:activity|transactions|history)",
                ],
                "blockchain_analysis": [
                    r"(?:ethereum|polygon|arbitrum|optimism|base|avalanche|bsc|fantom)\s*(?:analysis|data|info)",
                    r"(?:analyze|check|show)\s*(?:ethereum|polygon|arbitrum|optimism|base|avalanche|bsc|fantom)",
                    r"(?:gas|fees?)\s*(?:on|for)\s*(\w+)",
                    r"(?:network|chain)\s*(?:status|health|performance)",
                    r"cross[- ]?chain\s*(?:analysis|tracking|bridge)",
                ],
                "social_sentiment": [
                    r"(?:sentiment|mood|feeling|opinion).*?(?:about|on|for)\s*(\w+)",
                    r"what (?:are people|is everyone) saying about\s*(\w+)",
                    r"(?:social|community|twitter|reddit)\s*(?:sentiment|buzz|talk)",
                ],
                "defi_query": [
                    r"(?:defi|decentralized finance|yield|farming|liquidity)",
                    r"(?:protocol|dapp|smart contract).*?(?:tvl|volume|apy)",
                    r"(?:uniswap|aave|compound|curve|sushiswap)",
                ],
                "cross_chain": [
                    r"(?:cross.?chain|multi.?chain|bridge|layer.?2)",
                    r"(?:polygon|arbitrum|optimism|base|avalanche|bsc)",
                    r"(?:ethereum|eth)\s*(?:vs|versus|compared to)",
                ],
                "news_query": [
                    r"(?:news|updates|latest|recent).*?(?:about|on|for)\s*(\w+)",
                    r"what'?s (?:new|happening|going on) (?:with|in)\s*(\w+)",
                    r"(?:latest|recent|new)\s*(?:news|updates|developments)",
                ],
                "help_request": [
                    r"(?:help|assist|support|guide|how to)",
                    r"(?:what can you|how do i|can you help)",
                    r"(?:commands|features|capabilities)",
                ],
                "greeting": [
                    r"(?:hi|hello|hey|greetings|good morning|good afternoon|good evening)",
                    r"(?:what'?s up|how are you|how'?s it going)",
                ],
            }

            # Initialize entity extractors
            self.entity_extractors = {
                "crypto_symbols": self._extract_crypto_symbols,
                "wallet_addresses": self._extract_wallet_addresses,
                "numbers": self._extract_numbers,
                "time_expressions": self._extract_time_expressions,
            }

            logger.info("✅ Enhanced NLP processor initialized")

        except Exception as e:
            logger.error(f"❌ NLP processor initialization failed: {e}")

    async def process_message(self, user_id: int, message: str, context: dict = None) -> dict:
        """Process natural language message with MCP enhancement"""
        try:
            # Security: Sanitize input
            message = self._sanitize_message(message)

            # Update conversation history
            self._update_conversation_history(user_id, message)

            # Extract intent and entities
            intent, confidence = await self._extract_intent(message)
            entities = await self._extract_entities(message)

            # Get user context
            user_context = self._get_user_context(user_id, context)

            # Determine processing strategy
            processing_strategy = self._determine_processing_strategy(intent, entities, user_context)

            # Process based on strategy
            if processing_strategy == "immediate":
                response = await self._process_immediate(user_id, message, intent, entities, user_context)
            elif processing_strategy == "background":
                response = await self._process_background(user_id, message, intent, entities, user_context)
            else:
                response = await self._process_standard(user_id, message, intent, entities, user_context)

            # Update user context
            self._update_user_context(user_id, intent, entities, response)

            return {
                "success": True,
                "response": response,
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "processing_strategy": processing_strategy,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Message processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_response": "I apologize, but I'm having trouble understanding your request. Could you please rephrase it?"
            }

    def _sanitize_message(self, message: str) -> str:
        """Sanitize user message for security"""
        if not isinstance(message, str):
            return ""

        # Limit length
        message = message[:2000]

        # Remove potentially dangerous characters but keep crypto-relevant ones
        allowed_chars = re.compile(r'[a-zA-Z0-9\s\.\,\!\?\-\_\@\#\$\%\(\)\[\]\{\}\:\;\"\'\/\\x]')
        message = ''.join(allowed_chars.findall(message))

        return message.strip()

    async def _extract_intent(self, message: str) -> Tuple[str, float]:
        """Extract intent from message using pattern matching"""
        message_lower = message.lower()
        best_intent = "general_query"
        best_confidence = 0.0

        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    # Calculate confidence based on match quality
                    confidence = len(match.group(0)) / len(message_lower)
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence

        return best_intent, min(best_confidence, 1.0)

    async def _extract_entities(self, message: str) -> dict:
        """Extract entities from message"""
        entities = {}

        for entity_type, extractor in self.entity_extractors.items():
            try:
                extracted = extractor(message)
                if extracted:
                    entities[entity_type] = extracted
            except Exception as e:
                logger.warning(f"Entity extraction failed for {entity_type}: {e}")

        return entities

    def _extract_crypto_symbols(self, message: str) -> List[str]:
        """Extract cryptocurrency symbols"""
        # Common crypto symbols
        crypto_patterns = [
            r'\b(?:BTC|BITCOIN)\b',
            r'\b(?:ETH|ETHEREUM)\b',
            r'\b(?:SOL|SOLANA)\b',
            r'\b(?:ADA|CARDANO)\b',
            r'\b(?:DOT|POLKADOT)\b',
            r'\b(?:LINK|CHAINLINK)\b',
            r'\b(?:UNI|UNISWAP)\b',
            r'\b(?:AAVE)\b',
            r'\b(?:COMP|COMPOUND)\b',
            r'\b(?:MKR|MAKER)\b',
        ]

        symbols = []
        message_upper = message.upper()

        for pattern in crypto_patterns:
            matches = re.findall(pattern, message_upper)
            symbols.extend(matches)

        return list(set(symbols))  # Remove duplicates

    def _extract_wallet_addresses(self, message: str) -> List[str]:
        """Extract wallet addresses"""
        # Ethereum address pattern
        eth_pattern = r'0x[a-fA-F0-9]{40}'
        addresses = re.findall(eth_pattern, message)
        return addresses

    def _extract_numbers(self, message: str) -> List[dict]:
        """Extract numbers with context"""
        number_patterns = [
            (r'\$?([\d,]+\.?\d*)\s*(?:k|thousand)', lambda x: float(x.replace(',', '')) * 1000),
            (r'\$?([\d,]+\.?\d*)\s*(?:m|million)', lambda x: float(x.replace(',', '')) * 1000000),
            (r'\$?([\d,]+\.?\d*)\s*(?:b|billion)', lambda x: float(x.replace(',', '')) * 1000000000),
            (r'\$?([\d,]+\.?\d*)', lambda x: float(x.replace(',', ''))),
        ]

        numbers = []
        for pattern, converter in number_patterns:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                try:
                    value = converter(match.group(1))
                    numbers.append({
                        "value": value,
                        "original": match.group(0),
                        "position": match.span()
                    })
                except ValueError:
                    continue

        return numbers

    def _extract_time_expressions(self, message: str) -> List[str]:
        """Extract time expressions"""
        time_patterns = [
            r'\b(?:today|yesterday|tomorrow)\b',
            r'\b(?:this|last|next)\s+(?:week|month|year)\b',
            r'\b(?:24h|24 hours?|daily)\b',
            r'\b(?:weekly|monthly|yearly)\b',
        ]

        expressions = []
        message_lower = message.lower()

        for pattern in time_patterns:
            matches = re.findall(pattern, message_lower)
            expressions.extend(matches)

        return expressions

    def _get_user_context(self, user_id: int, additional_context: dict = None) -> dict:
        """Get user context including conversation history"""
        context = self.context_memory.get(user_id, {})

        # Add conversation history
        history = self.conversation_history.get(user_id, [])
        context["conversation_history"] = history[-5:]  # Last 5 messages

        # Add additional context
        if additional_context:
            context.update(additional_context)

        return context

    def _update_conversation_history(self, user_id: int, message: str):
        """Update conversation history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        self.conversation_history[user_id].append({
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only last 20 messages
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]

    def _update_user_context(self, user_id: int, intent: str, entities: dict, response: dict):
        """Update user context based on interaction"""
        if user_id not in self.context_memory:
            self.context_memory[user_id] = {}

        context = self.context_memory[user_id]

        # Update last intent and entities
        context["last_intent"] = intent
        context["last_entities"] = entities
        context["last_interaction"] = datetime.now().isoformat()

        # Track user preferences
        if "preferences" not in context:
            context["preferences"] = {}

        # Update preferences based on entities
        if "crypto_symbols" in entities:
            if "favorite_symbols" not in context["preferences"]:
                context["preferences"]["favorite_symbols"] = []
            for symbol in entities["crypto_symbols"]:
                if symbol not in context["preferences"]["favorite_symbols"]:
                    context["preferences"]["favorite_symbols"].append(symbol)

        # Keep preferences list manageable
        if "favorite_symbols" in context["preferences"]:
            context["preferences"]["favorite_symbols"] = context["preferences"]["favorite_symbols"][-10:]

    def _determine_processing_strategy(self, intent: str, entities: dict, context: dict) -> str:
        """Determine how to process the request"""
        # Immediate processing for simple queries
        immediate_intents = ["greeting", "help_request", "price_query"]
        if intent in immediate_intents:
            return "immediate"

        # Background processing for complex analysis
        background_intents = ["market_analysis", "wallet_analysis", "social_sentiment"]
        if intent in background_intents:
            return "background"

        # Standard processing for everything else
        return "standard"

    async def _process_immediate(self, user_id: int, message: str, intent: str, entities: dict, context: dict) -> dict:
        """Process immediate responses"""
        if intent == "greeting":
            return {
                "type": "immediate",
                "message": "👋 Hello! I'm Möbius, your AI crypto assistant. I can help you with market analysis, portfolio tracking, blockchain data, and much more. What would you like to know?",
                "suggestions": [
                    "Check BTC price",
                    "Analyze my portfolio", 
                    "Market overview",
                    "Gas fees comparison"
                ]
            }
        
        elif intent == "help_request":
            return {
                "type": "immediate",
                "message": """🤖 **Möbius AI Assistant - Help Guide**

**🔍 Market Analysis:**
• `price BTC` - Get current prices
• `market analysis` - Comprehensive market overview
• `sentiment Bitcoin` - Social sentiment analysis

**💼 Portfolio & Wallets:**
• `portfolio overview` - Your holdings summary
• `analyze wallet 0x...` - Wallet analysis
• `track my assets` - Multi-chain tracking

**⛓️ Blockchain Data:**
• `ethereum analysis` - Network status & metrics
• `gas fees comparison` - Cross-chain fee analysis
• `bridge tracking` - Cross-chain bridge data

**📊 Advanced Features:**
• `defi protocols` - DeFi ecosystem overview
• `yield farming` - Best yield opportunities
• `arbitrage scan` - Cross-chain arbitrage

Just ask me naturally - I understand conversational language! 🚀""",
                "suggestions": [
                    "Show me BTC price",
                    "What's happening in crypto?",
                    "Analyze Ethereum network",
                    "Check DeFi protocols"
                ]
            }
        
        elif intent == "price_query":
            symbols = entities.get("crypto_symbols", ["BTC"])
            return await self._get_price_data(symbols)
        
        else:
            return {
                "type": "immediate",
                "message": "I understand you're looking for information. Let me process that for you...",
                "processing": True
            }

    async def _get_price_data(self, symbols: List[str]) -> dict:
        """Get price data via MCP"""
        try:
            price_data = await mcp_client.call_tool("financial", "get_crypto_prices", {"symbols": symbols})
            
            if price_data.get("success"):
                data = price_data.get("data", {})
                message = "💰 **Current Prices:**\n\n"
                
                for symbol, info in data.items():
                    change_emoji = "📈" if info["change_24h"] > 0 else "📉"
                    message += f"• **{symbol}**: ${info['price']:,.2f} {change_emoji} {info['change_24h']:+.1f}%\n"
                
                return {
                    "type": "price_data",
                    "message": message,
                    "data": data
                }
            else:
                return {
                    "type": "error",
                    "message": "❌ Unable to fetch price data at the moment. Please try again."
                }
                
        except Exception as e:
            logger.error(f"Price data fetch failed: {e}")
            return {
                "type": "error",
                "message": "❌ Price service temporarily unavailable."
            }

    async def _process_background(self, user_id: int, message: str, intent: str, entities: dict, context: dict) -> dict:
        """Process complex requests in background to avoid chat flooding"""
        try:
            # Submit background job based on intent
            job_id = None
            
            if intent == "market_analysis":
                job_id = await submit_background_job(
                    user_id, "market_analysis", 
                    {"symbols": entities.get("crypto_symbols", ["BTC", "ETH"])},
                    priority=2
                )
            
            elif intent == "wallet_analysis":
                addresses = entities.get("wallet_addresses", [])
                if addresses:
                    job_id = await submit_background_job(
                        user_id, "wallet_analysis",
                        {"address": addresses[0], "chains": ["ethereum", "polygon", "arbitrum"]},
                        priority=2
                    )
            
            elif intent == "social_sentiment":
                symbols = entities.get("crypto_symbols", ["crypto"])
                job_id = await submit_background_job(
                    user_id, "social_sentiment",
                    {"topic": symbols[0] if symbols else "crypto"},
                    priority=1
                )
            
            elif intent == "blockchain_analysis":
                # Extract chain from message
                chains = self._extract_blockchain_names(message)
                if chains:
                    job_id = await submit_background_job(
                        user_id, "cross_chain_analysis",
                        {"chains": chains},
                        priority=2
                    )
            
            if job_id:
                return {
                    "type": "background_processing",
                    "message": f"🔄 **Processing your request in the background...**\n\nI'm analyzing the data you requested. This may take a moment for the most accurate results.\n\n*Job ID: {job_id[:8]}...*",
                    "job_id": job_id,
                    "estimated_time": "30-60 seconds"
                }
            else:
                # Fallback to standard processing
                return await self._process_standard(user_id, message, intent, entities, context)
                
        except Exception as e:
            logger.error(f"Background processing failed: {e}")
            return await self._process_standard(user_id, message, intent, entities, context)

    def _extract_blockchain_names(self, message: str) -> List[str]:
        """Extract blockchain names from message"""
        blockchain_patterns = {
            "ethereum": r"\b(?:ethereum|eth)\b",
            "bitcoin": r"\b(?:bitcoin|btc)\b", 
            "solana": r"\b(?:solana|sol)\b",
            "polygon": r"\b(?:polygon|matic)\b",
            "arbitrum": r"\b(?:arbitrum|arb)\b",
            "optimism": r"\b(?:optimism|op)\b",
            "base": r"\b(?:base)\b",
            "avalanche": r"\b(?:avalanche|avax)\b",
            "bsc": r"\b(?:bsc|binance smart chain|bnb)\b",
            "fantom": r"\b(?:fantom|ftm)\b"
        }
        
        chains = []
        message_lower = message.lower()
        
        for chain, pattern in blockchain_patterns.items():
            if re.search(pattern, message_lower):
                chains.append(chain)
        
        return chains

    async def _process_standard(self, user_id: int, message: str, intent: str, entities: dict, context: dict) -> dict:
        """Standard processing with MCP enhancement"""
        try:
            # Use AI orchestrator for enhanced response with intent
            ai_response = await ai_orchestrator.generate_enhanced_response(message, context, intent)
            
            if ai_response.get("success"):
                return {
                    "type": "ai_enhanced",
                    "message": ai_response["response"],
                    "model_used": ai_response.get("model_used"),
                    "context_sources": ai_response.get("context_sources", [])
                }
            else:
                return {
                    "type": "fallback",
                    "message": "I understand your request, but I'm having some technical difficulties. Let me try to help you with the information I have available."
                }
                
        except Exception as e:
            logger.error(f"Standard processing failed: {e}")
            return {
                "type": "error",
                "message": "I apologize, but I'm experiencing technical difficulties. Please try rephrasing your question."
            }

# Global NLP processor instance
nlp_processor = MCPNaturalLanguageProcessor()

async def initialize_nlp_processor():
    """Initialize the enhanced NLP processor"""
    await nlp_processor.initialize()
    logger.info("🧠 Enhanced NLP processor ready!")

async def process_natural_language(user_id: int, message: str, context: dict = None) -> dict:
    """Process natural language message with MCP enhancement"""
    return await nlp_processor.process_message(user_id, message, context)

# Convenience function for background job submission
async def submit_background_job(user_id: int, job_type: str, parameters: dict, priority: int = 1) -> Optional[str]:
    """Submit background job (imported from background processor)"""
    try:
        from mcp_background_processor import background_processor
        return await background_processor.submit_job(user_id, job_type, parameters, priority=priority)
    except Exception as e:
        logger.error(f"Background job submission failed: {e}")
        return None