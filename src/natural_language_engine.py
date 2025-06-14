# src/natural_language_engine.py
"""
Natural Language Query Engine for Möbius AI Assistant.
Enables users to ask questions in plain English and get intelligent responses.
"""
import re
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class QueryType(Enum):
    PRICE_QUERY = "price"
    TVL_QUERY = "tvl"
    PROTOCOL_QUERY = "protocol"
    WALLET_QUERY = "wallet"
    COMPARISON_QUERY = "comparison"
    TREND_QUERY = "trend"
    GENERAL_QUERY = "general"

@dataclass
class ParsedQuery:
    query_type: QueryType
    entities: List[str]
    timeframe: Optional[str]
    metric: Optional[str]
    intent: str
    confidence: float
    suggested_command: Optional[str] = None

class NaturalLanguageEngine:
    """
    Advanced natural language processing engine that converts user questions
    into actionable bot commands while maintaining security and performance.
    """
    
    def __init__(self):
        self.query_patterns = self._load_query_patterns()
        self.entity_extractors = self._load_entity_extractors()
        self.command_mappings = self._load_command_mappings()
        self.context_memory = {}  # Store conversation context per user
        
    def _load_query_patterns(self) -> Dict[QueryType, List[Dict[str, Any]]]:
        """Load patterns for different query types"""
        return {
            QueryType.PRICE_QUERY: [
                {
                    "patterns": [
                        r"what.{0,20}price.{0,20}(of\s+)?(?P<token>\w+)",
                        r"how much.{0,20}(?P<token>\w+).{0,20}cost",
                        r"(?P<token>\w+).{0,20}price.{0,20}now",
                        r"current.{0,20}price.{0,20}(?P<token>\w+)"
                    ],
                    "intent": "get_current_price",
                    "confidence_boost": 0.2
                },
                {
                    "patterns": [
                        r"(?P<token>\w+).{0,20}price.{0,20}(?P<timeframe>yesterday|last week|last month)",
                        r"price.{0,20}(?P<token>\w+).{0,20}(?P<timeframe>\d+\s+days?\s+ago)"
                    ],
                    "intent": "get_historical_price",
                    "confidence_boost": 0.3
                }
            ],
            QueryType.TVL_QUERY: [
                {
                    "patterns": [
                        r"(?P<protocol>\w+).{0,20}tvl",
                        r"total.{0,20}value.{0,20}locked.{0,20}(?P<protocol>\w+)",
                        r"how much.{0,20}locked.{0,20}(?P<protocol>\w+)",
                        r"(?P<protocol>\w+).{0,20}total.{0,20}value"
                    ],
                    "intent": "get_protocol_tvl",
                    "confidence_boost": 0.3
                }
            ],
            QueryType.PROTOCOL_QUERY: [
                {
                    "patterns": [
                        r"tell me about (?P<protocol>\w+)",
                        r"what is (?P<protocol>\w+)",
                        r"(?P<protocol>\w+) information",
                        r"research (?P<protocol>\w+)"
                    ],
                    "intent": "get_protocol_info",
                    "confidence_boost": 0.2
                }
            ],
            QueryType.WALLET_QUERY: [
                {
                    "patterns": [
                        r"wallet (?P<address>0x[a-fA-F0-9]{40})",
                        r"address (?P<address>0x[a-fA-F0-9]{40})",
                        r"analyze (?P<address>0x[a-fA-F0-9]{40})",
                        r"(?P<address>0x[a-fA-F0-9]{40}) analysis"
                    ],
                    "intent": "analyze_wallet",
                    "confidence_boost": 0.4
                }
            ],
            QueryType.COMPARISON_QUERY: [
                {
                    "patterns": [
                        r"compare (?P<entity1>\w+) (?:and|vs|with) (?P<entity2>\w+)",
                        r"(?P<entity1>\w+) vs (?P<entity2>\w+)",
                        r"difference between (?P<entity1>\w+) and (?P<entity2>\w+)",
                        r"which is better (?P<entity1>\w+) or (?P<entity2>\w+)"
                    ],
                    "intent": "compare_entities",
                    "confidence_boost": 0.3
                }
            ],
            QueryType.TREND_QUERY: [
                {
                    "patterns": [
                        r"(?P<entity>\w+) trend (?P<timeframe>over.{0,20}(?:week|month|year))",
                        r"trending (?P<metric>protocols|tokens|defi)",
                        r"what.{0,20}trending",
                        r"top (?P<metric>gainers|losers|protocols)"
                    ],
                    "intent": "get_trends",
                    "confidence_boost": 0.2
                }
            ]
        }
    
    def _load_entity_extractors(self) -> Dict[str, List[str]]:
        """Load entity extraction patterns"""
        return {
            "tokens": [
                "btc", "bitcoin", "eth", "ethereum", "usdc", "usdt", "dai", "link", "uni", "aave",
                "comp", "mkr", "snx", "crv", "bal", "yfi", "sushi", "1inch", "matic", "avax"
            ],
            "protocols": [
                "uniswap", "aave", "compound", "makerdao", "curve", "balancer", "yearn",
                "sushiswap", "1inch", "synthetix", "pancakeswap", "quickswap", "trader-joe"
            ],
            "timeframes": [
                "hour", "day", "week", "month", "year", "yesterday", "today",
                "last week", "last month", "last year", "24h", "7d", "30d", "1y"
            ],
            "metrics": [
                "price", "tvl", "volume", "revenue", "fees", "users", "transactions",
                "market cap", "supply", "yield", "apy", "apr"
            ]
        }
    
    def _load_command_mappings(self) -> Dict[str, str]:
        """Map intents to bot commands"""
        return {
            "get_current_price": "/price {token}",
            "get_historical_price": "/price {token} {timeframe}",
            "get_protocol_tvl": "/llama tvl {protocol}",
            "get_protocol_info": "/llama info {protocol}",
            "analyze_wallet": "/arkham {address}",
            "compare_entities": "/compare {entity1} {entity2}",
            "get_trends": "/trends {metric} {timeframe}"
        }
    
    async def process_natural_query(self, user_id: int, query: str) -> Dict[str, Any]:
        """
        Process natural language query and return structured response.
        Maintains conversation context and provides intelligent suggestions.
        """
        try:
            # Clean and normalize the query
            normalized_query = self._normalize_query(query)
            
            # Parse the query
            parsed_query = await self._parse_query(normalized_query)
            
            # Update conversation context
            self._update_context(user_id, query, parsed_query)
            
            # Generate response
            response = await self._generate_response(user_id, parsed_query)
            
            return {
                "success": True,
                "parsed_query": parsed_query,
                "response": response,
                "suggested_commands": self._get_suggested_commands(parsed_query),
                "context_aware": True
            }
            
        except Exception as e:
            logger.error(f"Natural language processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_response": "I didn't understand that. Could you try rephrasing your question?",
                "suggestions": [
                    "Try asking about specific tokens or protocols",
                    "Use commands like '/help' for available options",
                    "Ask about prices, TVL, or wallet analysis"
                ]
            }
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for better processing"""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove common filler words that don't add meaning
        filler_words = ['please', 'can you', 'could you', 'would you', 'i want to', 'i need to']
        for filler in filler_words:
            normalized = normalized.replace(filler, '')
        
        # Clean up extra spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    async def _parse_query(self, query: str) -> ParsedQuery:
        """Parse normalized query into structured format"""
        best_match = None
        best_confidence = 0.0
        
        # Try to match against all query patterns
        for query_type, patterns_list in self.query_patterns.items():
            for pattern_config in patterns_list:
                for pattern in pattern_config["patterns"]:
                    match = re.search(pattern, query, re.IGNORECASE)
                    if match:
                        # Calculate confidence based on match quality
                        confidence = self._calculate_confidence(query, pattern, match)
                        confidence += pattern_config.get("confidence_boost", 0)
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = {
                                "query_type": query_type,
                                "match": match,
                                "intent": pattern_config["intent"],
                                "confidence": confidence
                            }
        
        if best_match:
            # Extract entities from the match
            entities = self._extract_entities(query, best_match["match"])
            timeframe = self._extract_timeframe(query)
            metric = self._extract_metric(query)
            
            return ParsedQuery(
                query_type=best_match["query_type"],
                entities=entities,
                timeframe=timeframe,
                metric=metric,
                intent=best_match["intent"],
                confidence=best_match["confidence"],
                suggested_command=self._generate_command(best_match["intent"], entities, timeframe, metric)
            )
        else:
            # Fallback for unrecognized queries
            return ParsedQuery(
                query_type=QueryType.GENERAL_QUERY,
                entities=self._extract_entities(query),
                timeframe=self._extract_timeframe(query),
                metric=self._extract_metric(query),
                intent="general_help",
                confidence=0.1
            )
    
    def _calculate_confidence(self, query: str, pattern: str, match: re.Match) -> float:
        """Calculate confidence score for pattern match"""
        base_confidence = 0.5
        
        # Boost confidence for exact entity matches
        if match.groupdict():
            base_confidence += 0.2
        
        # Boost confidence for longer matches
        match_length = len(match.group(0))
        query_length = len(query)
        length_ratio = match_length / query_length
        base_confidence += length_ratio * 0.3
        
        # Boost confidence for known entities
        entities = self._extract_entities(query, match)
        known_entities = sum(1 for entity in entities if self._is_known_entity(entity))
        if entities:
            base_confidence += (known_entities / len(entities)) * 0.2
        
        return min(base_confidence, 1.0)
    
    def _extract_entities(self, query: str, match: Optional[re.Match] = None) -> List[str]:
        """Extract entities (tokens, protocols, addresses) from query"""
        entities = []
        
        # Extract from regex match groups first
        if match and match.groupdict():
            for key, value in match.groupdict().items():
                if value and key in ['token', 'protocol', 'address', 'entity1', 'entity2']:
                    entities.append(value.lower())
        
        # Extract known tokens and protocols
        for entity_type, entity_list in self.entity_extractors.items():
            if entity_type in ['tokens', 'protocols']:
                for entity in entity_list:
                    if entity in query.lower():
                        entities.append(entity)
        
        # Extract Ethereum addresses
        eth_addresses = re.findall(r'0x[a-fA-F0-9]{40}', query)
        entities.extend(eth_addresses)
        
        return list(set(entities))  # Remove duplicates
    
    def _extract_timeframe(self, query: str) -> Optional[str]:
        """Extract timeframe from query"""
        timeframe_patterns = [
            r'(?P<timeframe>yesterday|today|last\s+week|last\s+month|last\s+year)',
            r'(?P<timeframe>\d+\s+(?:hours?|days?|weeks?|months?|years?)\s+ago)',
            r'(?P<timeframe>24h|7d|30d|1y|1m)',
            r'over\s+(?:the\s+)?(?P<timeframe>week|month|year)'
        ]
        
        for pattern in timeframe_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group('timeframe').lower()
        
        return None
    
    def _extract_metric(self, query: str) -> Optional[str]:
        """Extract metric from query"""
        for metric in self.entity_extractors['metrics']:
            if metric in query.lower():
                return metric
        return None
    
    def _is_known_entity(self, entity: str) -> bool:
        """Check if entity is in our known entities list"""
        for entity_list in self.entity_extractors.values():
            if entity.lower() in [e.lower() for e in entity_list]:
                return True
        return False
    
    def _generate_command(self, intent: str, entities: List[str], timeframe: Optional[str], metric: Optional[str]) -> Optional[str]:
        """Generate suggested bot command from parsed query"""
        command_template = self.command_mappings.get(intent)
        if not command_template:
            return None
        
        # Replace placeholders with extracted entities
        command = command_template
        
        if entities:
            if '{token}' in command and entities:
                command = command.replace('{token}', entities[0])
            if '{protocol}' in command and entities:
                command = command.replace('{protocol}', entities[0])
            if '{address}' in command and entities:
                # Find Ethereum address in entities
                eth_address = next((e for e in entities if e.startswith('0x')), entities[0])
                command = command.replace('{address}', eth_address)
            if '{entity1}' in command and len(entities) >= 1:
                command = command.replace('{entity1}', entities[0])
            if '{entity2}' in command and len(entities) >= 2:
                command = command.replace('{entity2}', entities[1])
        
        if timeframe and '{timeframe}' in command:
            command = command.replace('{timeframe}', timeframe)
        
        if metric and '{metric}' in command:
            command = command.replace('{metric}', metric)
        
        # Clean up any remaining placeholders
        command = re.sub(r'\{[^}]+\}', '', command).strip()
        
        return command if command != command_template else None
    
    def _update_context(self, user_id: int, query: str, parsed_query: ParsedQuery):
        """Update conversation context for user"""
        if user_id not in self.context_memory:
            self.context_memory[user_id] = {
                "recent_queries": [],
                "entities_mentioned": set(),
                "preferred_timeframes": [],
                "query_count": 0
            }
        
        context = self.context_memory[user_id]
        
        # Add to recent queries (keep last 5)
        context["recent_queries"].append({
            "query": query,
            "parsed": parsed_query,
            "timestamp": time.time()
        })
        if len(context["recent_queries"]) > 5:
            context["recent_queries"].pop(0)
        
        # Track mentioned entities
        context["entities_mentioned"].update(parsed_query.entities)
        
        # Track preferred timeframes
        if parsed_query.timeframe:
            context["preferred_timeframes"].append(parsed_query.timeframe)
            if len(context["preferred_timeframes"]) > 10:
                context["preferred_timeframes"].pop(0)
        
        context["query_count"] += 1
    
    async def _generate_response(self, user_id: int, parsed_query: ParsedQuery) -> str:
        """Generate contextual response based on parsed query"""
        if parsed_query.confidence < 0.3:
            return self._generate_clarification_response(parsed_query)
        
        # Generate response based on query type
        if parsed_query.query_type == QueryType.PRICE_QUERY:
            return self._generate_price_response(parsed_query)
        elif parsed_query.query_type == QueryType.TVL_QUERY:
            return self._generate_tvl_response(parsed_query)
        elif parsed_query.query_type == QueryType.PROTOCOL_QUERY:
            return self._generate_protocol_response(parsed_query)
        elif parsed_query.query_type == QueryType.WALLET_QUERY:
            return self._generate_wallet_response(parsed_query)
        elif parsed_query.query_type == QueryType.COMPARISON_QUERY:
            return self._generate_comparison_response(parsed_query)
        elif parsed_query.query_type == QueryType.TREND_QUERY:
            return self._generate_trend_response(parsed_query)
        else:
            return self._generate_general_response(user_id, parsed_query)
    
    def _generate_price_response(self, parsed_query: ParsedQuery) -> str:
        """Generate response for price queries"""
        if parsed_query.entities:
            entity = parsed_query.entities[0].upper()
            if parsed_query.timeframe:
                return f"🔍 **Looking up historical price for {entity}**\n\nTimeframe: {parsed_query.timeframe}\n\nI'll get that information for you..."
            else:
                return f"💰 **Getting current price for {entity}**\n\nFetching real-time price data..."
        else:
            return "💰 **Price Query**\n\nI can help you get price information. Which token are you interested in?"
    
    def _generate_tvl_response(self, parsed_query: ParsedQuery) -> str:
        """Generate response for TVL queries"""
        if parsed_query.entities:
            entity = parsed_query.entities[0].title()
            return f"📊 **Getting TVL data for {entity}**\n\nFetching total value locked information..."
        else:
            return "📊 **TVL Query**\n\nI can help you get TVL information. Which protocol are you interested in?"
    
    def _generate_protocol_response(self, parsed_query: ParsedQuery) -> str:
        """Generate response for protocol queries"""
        if parsed_query.entities:
            entity = parsed_query.entities[0].title()
            return f"🔍 **Researching {entity}**\n\nGathering comprehensive protocol information..."
        else:
            return "🔍 **Protocol Research**\n\nI can help you research DeFi protocols. Which one would you like to know about?"
    
    def _generate_wallet_response(self, parsed_query: ParsedQuery) -> str:
        """Generate response for wallet queries"""
        if parsed_query.entities:
            address = parsed_query.entities[0]
            return f"🔍 **Analyzing wallet**\n\nAddress: `{address}`\n\nGathering wallet analytics..."
        else:
            return "🔍 **Wallet Analysis**\n\nI can analyze Ethereum wallets. Please provide a wallet address."
    
    def _generate_comparison_response(self, parsed_query: ParsedQuery) -> str:
        """Generate response for comparison queries"""
        if len(parsed_query.entities) >= 2:
            entity1, entity2 = parsed_query.entities[0].title(), parsed_query.entities[1].title()
            return f"⚖️ **Comparing {entity1} vs {entity2}**\n\nAnalyzing differences and similarities..."
        else:
            return "⚖️ **Comparison Analysis**\n\nI can compare tokens or protocols. Please specify what you'd like to compare."
    
    def _generate_trend_response(self, parsed_query: ParsedQuery) -> str:
        """Generate response for trend queries"""
        metric = parsed_query.metric or "market"
        timeframe = parsed_query.timeframe or "recent"
        return f"📈 **Analyzing {metric} trends**\n\nTimeframe: {timeframe}\n\nIdentifying trending patterns..."
    
    def _generate_general_response(self, user_id: int, parsed_query: ParsedQuery) -> str:
        """Generate response for general queries with context"""
        context = self.context_memory.get(user_id, {})
        
        # Use context to provide better responses
        if context.get("entities_mentioned"):
            recent_entities = list(context["entities_mentioned"])[-3:]
            return f"🤔 **I'm here to help!**\n\nBased on our conversation, you've been interested in: {', '.join(recent_entities)}\n\nWhat would you like to know more about?"
        else:
            return "🤔 **I'm here to help!**\n\nI can assist with:\n• Token prices and analysis\n• Protocol TVL and metrics\n• Wallet analysis\n• DeFi research\n\nWhat would you like to explore?"
    
    def _generate_clarification_response(self, parsed_query: ParsedQuery) -> str:
        """Generate clarification request for unclear queries"""
        suggestions = []
        
        if parsed_query.entities:
            entity = parsed_query.entities[0]
            suggestions.extend([
                f"Get price of {entity}",
                f"Research {entity} protocol",
                f"Analyze {entity} metrics"
            ])
        else:
            suggestions.extend([
                "Ask about token prices",
                "Research DeFi protocols",
                "Analyze wallet addresses",
                "Compare different tokens"
            ])
        
        return f"🤔 **I need a bit more clarity**\n\nI understood some parts of your question, but could you be more specific?\n\n💡 **You might want to:**\n" + "\n".join(f"• {s}" for s in suggestions[:3])
    
    def _get_suggested_commands(self, parsed_query: ParsedQuery) -> List[str]:
        """Get suggested commands based on parsed query"""
        suggestions = []
        
        if parsed_query.suggested_command:
            suggestions.append(parsed_query.suggested_command)
        
        # Add related commands based on query type
        if parsed_query.query_type == QueryType.PRICE_QUERY and parsed_query.entities:
            entity = parsed_query.entities[0]
            suggestions.extend([
                f"/llama tvl {entity}",
                f"/arkham {entity}",
                f"/alert price {entity} 10%"
            ])
        elif parsed_query.query_type == QueryType.PROTOCOL_QUERY and parsed_query.entities:
            entity = parsed_query.entities[0]
            suggestions.extend([
                f"/llama revenue {entity}",
                f"/llama raises {entity}"
            ])
        
        return suggestions[:3]  # Limit to 3 suggestions

# Global natural language engine instance
natural_language_engine = NaturalLanguageEngine()