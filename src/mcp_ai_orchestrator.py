# src/mcp_ai_orchestrator.py - Multi-Model AI Orchestrator with MCP Integration
import asyncio
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
import json
from datetime import datetime

# AI Provider imports
import openai
import anthropic
from groq import Groq
import google.generativeai as genai

from mcp_client import mcp_client

logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Query classification types"""
    TECHNICAL_ANALYSIS = "technical_analysis"
    MARKET_RESEARCH = "market_research"
    CODE_GENERATION = "code_generation"
    CREATIVE_WRITING = "creative_writing"
    DATA_ANALYSIS = "data_analysis"
    SOCIAL_SENTIMENT = "social_sentiment"
    BLOCKCHAIN_ANALYSIS = "blockchain_analysis"
    GENERAL_CHAT = "general_chat"

class MCPAIOrchestrator:
    """Multi-model AI orchestrator with MCP integration"""

    def __init__(self):
        self.models = {}
        self.query_classifier = None
        self.context_manager = {}

    async def initialize(self):
        """Initialize AI models and MCP connections"""
        try:
            # Initialize AI models with specializations
            self.models = {
                QueryType.TECHNICAL_ANALYSIS: {
                    'primary': 'llama3-70b-8192',
                    'fallback': 'llama3-8b-8192',
                    'client': None
                },
                QueryType.MARKET_RESEARCH: {
                    'primary': 'llama3-8b-8192',
                    'fallback': 'claude-3-sonnet',
                    'client': None
                },
                QueryType.CODE_GENERATION: {
                    'primary': 'claude-3-sonnet',
                    'fallback': 'gpt-4',
                    'client': None
                },
                QueryType.CREATIVE_WRITING: {
                    'primary': 'gemini-2.0-flash',
                    'fallback': 'claude-3-haiku',
                    'client': None
                },
                QueryType.DATA_ANALYSIS: {
                    'primary': 'llama3-8b-8192',
                    'fallback': 'llama3-70b-8192',
                    'client': None
                },
                QueryType.SOCIAL_SENTIMENT: {
                    'primary': 'claude-3-haiku',
                    'fallback': 'llama3-8b-8192',
                    'client': None
                },
                QueryType.BLOCKCHAIN_ANALYSIS: {
                    'primary': 'llama3-70b-8192',
                    'fallback': 'llama3-8b-8192',
                    'client': None
                },
                QueryType.GENERAL_CHAT: {
                    'primary': 'llama3-8b-8192',
                    'fallback': 'claude-3-haiku',
                    'client': None
                }
            }

            logger.info("✅ MCP AI Orchestrator initialized")

        except Exception as e:
            logger.error(f"❌ AI Orchestrator initialization failed: {e}")

    async def classify_query(self, query: str, context: dict = None) -> QueryType:
        """Classify query to determine best AI model"""
        query_lower = query.lower()

        # Technical analysis keywords
        if any(word in query_lower for word in ['chart', 'technical', 'resistance', 'support', 'rsi', 'macd', 'bollinger']):
            return QueryType.TECHNICAL_ANALYSIS

        # Market research keywords
        elif any(word in query_lower for word in ['research', 'analysis', 'market', 'protocol', 'defi', 'tvl']):
            return QueryType.MARKET_RESEARCH

        # Code generation keywords
        elif any(word in query_lower for word in ['code', 'function', 'smart contract', 'solidity', 'python', 'javascript']):
            return QueryType.CODE_GENERATION

        # Social sentiment keywords
        elif any(word in query_lower for word in ['sentiment', 'social', 'twitter', 'reddit', 'community', 'buzz']):
            return QueryType.SOCIAL_SENTIMENT

        # Blockchain analysis keywords
        elif any(word in query_lower for word in ['wallet', 'transaction', 'address', 'blockchain', 'onchain', 'whale']):
            return QueryType.BLOCKCHAIN_ANALYSIS

        # Data analysis keywords
        elif any(word in query_lower for word in ['data', 'statistics', 'metrics', 'calculate', 'analyze']):
            return QueryType.DATA_ANALYSIS

        # Creative writing keywords
        elif any(word in query_lower for word in ['write', 'create', 'story', 'poem', 'creative', 'imagine']):
            return QueryType.CREATIVE_WRITING

        else:
            return QueryType.GENERAL_CHAT

    async def gather_mcp_context(self, query_type: QueryType, query: str) -> dict:
        """Gather relevant context from MCP servers based on query type"""
        context = {}

        try:
            if query_type == QueryType.MARKET_RESEARCH:
                # Get comprehensive market data
                market_data = await mcp_client.call_tool("financial", "get_crypto_prices", {"symbols": ["bitcoin", "ethereum", "solana"]})
                defi_data = await mcp_client.call_tool("financial", "get_defi_protocols", {"limit": 10})
                market_overview = await mcp_client.call_tool("financial", "get_market_overview", {})
                context.update({"market_data": market_data, "defi_data": defi_data, "market_overview": market_overview})

            elif query_type == QueryType.SOCIAL_SENTIMENT:
                # Get social sentiment and news data
                sentiment_data = await mcp_client.call_tool("web", "monitor_social_sentiment", {"topics": ["bitcoin", "ethereum", "defi"]})
                news_data = await mcp_client.call_tool("web", "get_crypto_news", {"limit": 5})
                context.update({"sentiment_data": sentiment_data, "news_data": news_data})

            elif query_type == QueryType.BLOCKCHAIN_ANALYSIS:
                # Get blockchain analytics if wallet address is mentioned
                if "0x" in query:
                    address = self.extract_wallet_address(query)
                    if address:
                        wallet_data = await mcp_client.call_tool("blockchain", "analyze_wallet_cross_chain", {"wallet_address": address})
                        context.update({"wallet_data": wallet_data})
                else:
                    # Get general chain analytics
                    chain_comparison = await mcp_client.call_tool("blockchain", "compare_chains", {"chains": ["ethereum", "polygon", "arbitrum", "optimism", "base"]})
                    context.update({"chain_data": chain_comparison})

            elif query_type in [QueryType.TECHNICAL_ANALYSIS, QueryType.DATA_ANALYSIS]:
                # Get comprehensive market data
                market_data = await mcp_client.call_tool("financial", "get_crypto_prices", {})
                market_overview = await mcp_client.call_tool("financial", "get_market_overview", {})
                context.update({"market_data": market_data, "market_overview": market_overview})

            # Always try to get recent web research for current context
            web_data = await mcp_client.call_tool("web", "web_search", {"query": query[:100], "max_results": 3})
            context.update({"web_data": web_data})

        except Exception as e:
            logger.warning(f"⚠️ Failed to gather MCP context: {e}")

        return context

    def extract_wallet_address(self, text: str) -> Optional[str]:
        """Extract wallet address from text"""
        import re
        # Ethereum address pattern
        pattern = r'0x[a-fA-F0-9]{40}'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def _map_intent_to_query_type(self, intent: str) -> QueryType:
        """Map NLP intent to AI orchestrator QueryType"""
        intent_mapping = {
            "price_query": QueryType.MARKET_RESEARCH,
            "market_analysis": QueryType.MARKET_RESEARCH,
            "portfolio_query": QueryType.DATA_ANALYSIS,
            "wallet_analysis": QueryType.BLOCKCHAIN_ANALYSIS,
            "blockchain_analysis": QueryType.BLOCKCHAIN_ANALYSIS,
            "defi_query": QueryType.MARKET_RESEARCH,
            "social_sentiment": QueryType.SOCIAL_SENTIMENT,
            "technical_analysis": QueryType.TECHNICAL_ANALYSIS,
            "research_query": QueryType.MARKET_RESEARCH,
            "comparison_query": QueryType.DATA_ANALYSIS,
            "alert_management": QueryType.DATA_ANALYSIS,
            "news_query": QueryType.MARKET_RESEARCH,
            "help_request": QueryType.GENERAL_CHAT,
            "greeting": QueryType.GENERAL_CHAT,
            "general_query": QueryType.GENERAL_CHAT
        }
        
        return intent_mapping.get(intent, QueryType.GENERAL_CHAT)

    async def generate_enhanced_response(self, query: str, user_context: dict = None, intent: str = None) -> dict:
        """Generate enhanced AI response using MCP data and best-suited model"""
        try:
            # Auto-initialize if not already done
            if not self.models:
                await self.initialize()
            
            # Use provided intent or classify the query
            if intent:
                query_type = self._map_intent_to_query_type(intent)
            else:
                query_type = await self.classify_query(query, user_context)

            # Gather MCP context
            mcp_context = await self.gather_mcp_context(query_type, query)

            # Combine contexts
            full_context = {
                "user_context": user_context or {},
                "mcp_context": mcp_context,
                "query_type": query_type.value,
                "timestamp": datetime.now().isoformat()
            }

            # Generate response using specialized model
            response = await self.call_specialized_model(query_type, query, full_context)

            return {
                "success": True,
                "response": response,
                "query_type": query_type.value,
                "model_used": self.models[query_type]['primary'],
                "context_sources": list(mcp_context.keys()) if isinstance(mcp_context, dict) else [],
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Enhanced response generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_response": "I apologize, but I'm experiencing technical difficulties. Please try again."
            }

    async def call_specialized_model(self, query_type: QueryType, query: str, context: dict) -> str:
        """Call the specialized AI model for the query type"""

        # Create enhanced prompt with MCP context
        enhanced_prompt = self.create_enhanced_prompt(query, context)

        # For now, use a mock response since we don't have actual API keys configured
        return await self.generate_mock_response(query_type, query, context)

    def create_enhanced_prompt(self, query: str, context: dict) -> str:
        """Create enhanced prompt with MCP context"""
        prompt = f"""You are Möbius, an advanced AI crypto assistant with access to real-time data.

User Query: {query}

Real-time Context:
"""

        # Add MCP context data
        mcp_context = context.get("mcp_context", {})

        if "market_data" in mcp_context:
            prompt += f"\nMarket Data: {json.dumps(mcp_context['market_data'], indent=2)}"

        if "sentiment_data" in mcp_context:
            prompt += f"\nSocial Sentiment: {json.dumps(mcp_context['sentiment_data'], indent=2)}"

        if "wallet_data" in mcp_context:
            prompt += f"\nWallet Analysis: {json.dumps(mcp_context['wallet_data'], indent=2)}"

        if "web_data" in mcp_context:
            prompt += f"\nWeb Research: {json.dumps(mcp_context['web_data'], indent=2)}"

        prompt += f"""

Query Type: {context.get('query_type', 'general')}

Please provide a comprehensive, accurate response using the real-time data above. Be specific, actionable, and include relevant metrics when available."""

        return prompt

    async def generate_mock_response(self, query_type: QueryType, query: str, context: dict) -> str:
        """Generate mock response based on query type and context"""

        mcp_context = context.get("mcp_context", {})

        if query_type == QueryType.MARKET_RESEARCH:
            market_data = mcp_context.get("market_data", {})
            if isinstance(market_data, dict) and market_data.get("success"):
                data = market_data.get("data", {})
                if isinstance(data, dict) and data:
                    response = "📊 **Real-Time Market Analysis**\n\n"
                    for symbol, info in data.items():
                        if isinstance(info, dict):
                            change_emoji = "📈" if info.get("change_24h", 0) > 0 else "📉"
                            price = info.get("price", 0)
                            change = info.get("change_24h", 0)
                            response += f"• **{symbol}**: ${price:,.2f} {change_emoji} {change:+.1f}%\n"
                    response += f"\n🔍 **Analysis**: Based on current market data, "
                    if any(info.get("change_24h", 0) > 0 for info in data.values() if isinstance(info, dict)):
                        response += "we're seeing positive momentum across major cryptocurrencies."
                    else:
                        response += "the market is experiencing some volatility."
                    return response

        elif query_type == QueryType.SOCIAL_SENTIMENT:
            sentiment_data = mcp_context.get("sentiment_data", {})
            if sentiment_data.get("success"):
                data = sentiment_data.get("data", {})
                sentiment = data.get("overall_sentiment", "neutral")
                score = data.get("sentiment_score", 0.5)
                trending = data.get("trending_topics", [])

                response = f"🌐 **Social Sentiment Analysis**\n\n"
                response += f"📊 **Overall Sentiment**: {sentiment.title()} ({score:.2f}/1.0)\n"
                response += f"🔥 **Trending Topics**: {', '.join(trending)}\n"
                response += f"👥 **Influencer Mentions**: {data.get('influencer_mentions', 0)}\n\n"
                response += "💡 **Insight**: "
                if score > 0.6:
                    response += "Strong bullish sentiment in the community!"
                elif score < 0.4:
                    response += "Bearish sentiment detected, exercise caution."
                else:
                    response += "Neutral sentiment, market waiting for direction."
                return response

        elif query_type == QueryType.BLOCKCHAIN_ANALYSIS:
            wallet_data = mcp_context.get("wallet_data", {})
            if wallet_data.get("success"):
                data = wallet_data.get("data", {})
                response = "🔍 **Blockchain Wallet Analysis**\n\n"
                response += f"⚡ **Activity Level**: {data.get('wallet_activity', 'unknown').title()}\n"
                response += f"📊 **Transaction Count**: {data.get('transaction_count', 0)}\n"
                response += f"💰 **Total Value**: {data.get('total_value', 'unknown')}\n"
                response += f"🛡️ **Risk Score**: {data.get('risk_score', 'unknown').title()}\n\n"
                response += "💡 **Assessment**: This wallet shows "
                if data.get('wallet_activity') == 'high':
                    response += "high activity levels, indicating an active trader or DeFi user."
                else:
                    response += "moderate activity levels, typical of a long-term holder."
                return response

        # Default enhanced response
        return f"""thinking..."""

    def generate_contextual_insight(self, query: str, query_type: QueryType, mcp_context: dict) -> str:
        """Generate contextual insight based on available data"""
        if not mcp_context:
            return "While I don't have real-time data at the moment, I can provide general guidance based on my knowledge."

        insights = []

        if "market_data" in mcp_context:
            insights.append("Current market data shows mixed signals across major cryptocurrencies.")

        if "sentiment_data" in mcp_context:
            insights.append("Social sentiment analysis indicates community interest remains strong.")

        if "web_data" in mcp_context:
            insights.append("Recent news and developments suggest continued innovation in the space.")

        return " ".join(insights) if insights else "Analysis complete based on available data sources."

    def generate_recommendation(self, query_type: QueryType) -> str:
        """Generate recommendation based on query type"""
        recommendations = {
            QueryType.MARKET_RESEARCH: "Consider diversifying across multiple assets and timeframes.",
            QueryType.TECHNICAL_ANALYSIS: "Use multiple indicators and confirm signals before trading.",
            QueryType.SOCIAL_SENTIMENT: "Balance social sentiment with fundamental analysis.",
            QueryType.BLOCKCHAIN_ANALYSIS: "Always verify on-chain data with multiple sources.",
            QueryType.DATA_ANALYSIS: "Cross-reference data points for comprehensive insights.",
            QueryType.GENERAL_CHAT: "Stay informed and make decisions based on thorough research."
        }

        return recommendations.get(query_type, "Always do your own research and consider multiple perspectives.")

# Global AI orchestrator instance
ai_orchestrator = MCPAIOrchestrator()

async def initialize_ai_orchestrator():
    """Initialize the AI orchestrator"""
    await ai_orchestrator.initialize()
    logger.info("🧠 MCP AI Orchestrator ready!")

# Convenience function for enhanced AI responses
async def get_enhanced_ai_response(query: str, user_context: dict = None) -> dict:
    """Get enhanced AI response using MCP data and specialized models"""
    return await ai_orchestrator.generate_enhanced_response(query, user_context)