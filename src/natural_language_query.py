# src/natural_language_query.py
import asyncio
import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import requests
import pandas as pd
import numpy as np
from textblob import TextBlob
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from config import config
from ai_providers import get_ai_response
from crypto_research import query_defillama
from advanced_portfolio_manager import advanced_portfolio_manager
from advanced_alerts import advanced_alerts
from security_auditor import security_auditor
from performance_monitor import track_performance

logger = logging.getLogger(__name__)

@dataclass
class QueryIntent:
    """Represents the intent of a natural language query"""
    intent_type: str  # price, portfolio, analysis, comparison, etc.
    entities: List[str]  # tokens, protocols, addresses
    timeframe: Optional[str]  # 1h, 24h, 7d, 30d, etc.
    action: str  # get, compare, analyze, predict, etc.
    confidence: float  # 0-1
    parameters: Dict[str, Any]

@dataclass
class QueryResponse:
    """Response to a natural language query"""
    answer: str
    data: Dict[str, Any]
    visualizations: List[Dict[str, Any]]
    suggestions: List[str]
    confidence: float
    sources: List[str]

class NaturalLanguageQueryEngine:
    """Advanced natural language processing for crypto queries"""
    
    def __init__(self):
        self._init_nltk()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Intent patterns
        self.intent_patterns = {
            'price': [
                r'price of (\w+)',
                r'(\w+) price',
                r'how much is (\w+)',
                r'(\w+) cost',
                r'value of (\w+)'
            ],
            'portfolio': [
                r'my portfolio',
                r'portfolio value',
                r'portfolio performance',
                r'my holdings',
                r'my assets'
            ],
            'comparison': [
                r'compare (\w+) and (\w+)',
                r'(\w+) vs (\w+)',
                r'difference between (\w+) and (\w+)',
                r'which is better (\w+) or (\w+)'
            ],
            'analysis': [
                r'analyze (\w+)',
                r'analysis of (\w+)',
                r'(\w+) analysis',
                r'research (\w+)',
                r'study (\w+)'
            ],
            'prediction': [
                r'predict (\w+)',
                r'(\w+) prediction',
                r'forecast (\w+)',
                r'(\w+) forecast',
                r'will (\w+) go up',
                r'will (\w+) go down'
            ],
            'trend': [
                r'trend of (\w+)',
                r'(\w+) trend',
                r'trending',
                r'what\'s hot',
                r'popular tokens'
            ],
            'yield': [
                r'yield farming',
                r'best yields',
                r'highest apy',
                r'defi yields',
                r'staking rewards'
            ],
            'news': [
                r'news about (\w+)',
                r'(\w+) news',
                r'latest news',
                r'what happened to (\w+)'
            ]
        }
        
        # Entity recognition patterns
        self.entity_patterns = {
            'token': r'\b[A-Z]{2,10}\b',  # Token symbols
            'address': r'0x[a-fA-F0-9]{40}',  # Ethereum addresses
            'amount': r'\$?[\d,]+\.?\d*[kmb]?',  # Amounts with k/m/b suffixes
            'percentage': r'\d+\.?\d*%',  # Percentages
            'timeframe': r'\b(?:1h|24h|7d|30d|1m|3m|6m|1y)\b'  # Timeframes
        }
        
    def _init_nltk(self):
        """Initialize NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            logger.warning(f"Failed to download NLTK data: {e}")

    @track_performance.track_function
    async def process_query(self, user_id: int, query: str) -> QueryResponse:
        """Process a natural language query and return structured response"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "nlp_query", True, 
                {"query_length": len(query), "query_type": "natural_language"}
            )
            
            # Parse the query to understand intent
            intent = await self._parse_intent(query)
            
            # Route to appropriate handler based on intent
            if intent.intent_type == 'price':
                response = await self._handle_price_query(user_id, intent, query)
            elif intent.intent_type == 'portfolio':
                response = await self._handle_portfolio_query(user_id, intent, query)
            elif intent.intent_type == 'comparison':
                response = await self._handle_comparison_query(user_id, intent, query)
            elif intent.intent_type == 'analysis':
                response = await self._handle_analysis_query(user_id, intent, query)
            elif intent.intent_type == 'prediction':
                response = await self._handle_prediction_query(user_id, intent, query)
            elif intent.intent_type == 'trend':
                response = await self._handle_trend_query(user_id, intent, query)
            elif intent.intent_type == 'yield':
                response = await self._handle_yield_query(user_id, intent, query)
            elif intent.intent_type == 'news':
                response = await self._handle_news_query(user_id, intent, query)
            else:
                response = await self._handle_general_query(user_id, intent, query)
            
            # Enhance response with AI if needed
            if response.confidence < 0.7:
                response = await self._enhance_with_ai(user_id, query, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryResponse(
                answer="I encountered an error processing your query. Please try rephrasing it.",
                data={},
                visualizations=[],
                suggestions=["Try asking about specific token prices", "Ask about your portfolio"],
                confidence=0.0,
                sources=[]
            )

    async def _parse_intent(self, query: str) -> QueryIntent:
        """Parse query to extract intent and entities"""
        query_lower = query.lower()
        
        # Find intent type
        intent_type = 'general'
        confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    intent_type = intent
                    confidence = 0.8
                    break
            if confidence > 0:
                break
        
        # Extract entities
        entities = []
        
        # Extract tokens
        token_matches = re.findall(self.entity_patterns['token'], query.upper())
        entities.extend(token_matches)
        
        # Extract addresses
        address_matches = re.findall(self.entity_patterns['address'], query)
        entities.extend(address_matches)
        
        # Extract timeframe
        timeframe = None
        timeframe_matches = re.findall(self.entity_patterns['timeframe'], query_lower)
        if timeframe_matches:
            timeframe = timeframe_matches[0]
        
        # Extract action verbs
        action = 'get'
        action_words = ['get', 'show', 'find', 'compare', 'analyze', 'predict', 'calculate']
        for word in action_words:
            if word in query_lower:
                action = word
                break
        
        # Extract additional parameters
        parameters = {}
        
        # Extract amounts
        amount_matches = re.findall(self.entity_patterns['amount'], query)
        if amount_matches:
            parameters['amounts'] = amount_matches
        
        # Extract percentages
        percentage_matches = re.findall(self.entity_patterns['percentage'], query)
        if percentage_matches:
            parameters['percentages'] = percentage_matches
        
        return QueryIntent(
            intent_type=intent_type,
            entities=entities,
            timeframe=timeframe,
            action=action,
            confidence=confidence,
            parameters=parameters
        )

    async def _handle_price_query(self, user_id: int, intent: QueryIntent, query: str) -> QueryResponse:
        """Handle price-related queries"""
        try:
            if not intent.entities:
                return QueryResponse(
                    answer="Please specify which token's price you'd like to know.",
                    data={},
                    visualizations=[],
                    suggestions=["Try: 'What's the price of BTC?'", "Try: 'ETH price'"],
                    confidence=0.3,
                    sources=[]
                )
            
            token = intent.entities[0]
            
            # Get current price
            price_data = await self._get_token_price_data(token)
            if not price_data:
                return QueryResponse(
                    answer=f"I couldn't find price data for {token}. Please check the token symbol.",
                    data={},
                    visualizations=[],
                    suggestions=[f"Try searching for {token} on CoinGecko", "Check if the symbol is correct"],
                    confidence=0.2,
                    sources=[]
                )
            
            # Format response
            price = price_data['current_price']
            change_24h = price_data.get('price_change_percentage_24h', 0)
            
            answer = f"💰 **{token.upper()} Price**\n\n"
            answer += f"Current Price: **${price:,.2f}**\n"
            
            if change_24h > 0:
                answer += f"24h Change: **+{change_24h:.2f}%** 📈\n"
            else:
                answer += f"24h Change: **{change_24h:.2f}%** 📉\n"
            
            if 'market_cap' in price_data:
                answer += f"Market Cap: **${price_data['market_cap']:,.0f}**\n"
            
            if 'volume_24h' in price_data:
                answer += f"24h Volume: **${price_data['volume_24h']:,.0f}**\n"
            
            # Add context
            if abs(change_24h) > 10:
                answer += f"\n⚠️ **High volatility detected!** {token} has moved {abs(change_24h):.1f}% in 24h."
            
            suggestions = [
                f"Set a price alert for {token}",
                f"Get technical analysis for {token}",
                f"Compare {token} with other tokens"
            ]
            
            return QueryResponse(
                answer=answer,
                data=price_data,
                visualizations=[{
                    'type': 'price_chart',
                    'token': token,
                    'timeframe': intent.timeframe or '24h'
                }],
                suggestions=suggestions,
                confidence=0.9,
                sources=['CoinGecko']
            )
            
        except Exception as e:
            logger.error(f"Error handling price query: {e}")
            return QueryResponse(
                answer="I encountered an error getting price data.",
                data={},
                visualizations=[],
                suggestions=[],
                confidence=0.0,
                sources=[]
            )

    async def _handle_portfolio_query(self, user_id: int, intent: QueryIntent, query: str) -> QueryResponse:
        """Handle portfolio-related queries"""
        try:
            portfolio = await advanced_portfolio_manager.get_portfolio(user_id)
            
            if not portfolio:
                return QueryResponse(
                    answer="You don't have any wallets added to your portfolio yet. Use `/portfolio add <address>` to get started.",
                    data={},
                    visualizations=[],
                    suggestions=[
                        "Add a wallet to your portfolio",
                        "Learn about portfolio tracking",
                        "See portfolio management features"
                    ],
                    confidence=0.8,
                    sources=[]
                )
            
            # Format portfolio response
            answer = f"📊 **Your Portfolio Overview**\n\n"
            answer += f"Total Value: **${portfolio.total_value_usd:,.2f}**\n"
            answer += f"24h Performance: **{portfolio.performance_24h:+.2f}%**\n"
            answer += f"7d Performance: **{portfolio.performance_7d:+.2f}%**\n"
            answer += f"30d Performance: **{portfolio.performance_30d:+.2f}%**\n\n"
            
            # Top holdings
            top_assets = sorted(portfolio.assets, key=lambda x: x.value_usd, reverse=True)[:5]
            answer += "**Top Holdings:**\n"
            for asset in top_assets:
                answer += f"• {asset.symbol}: ${asset.value_usd:,.2f} ({asset.allocation_percent:.1f}%)\n"
            
            # Portfolio insights
            if portfolio.total_value_usd > 10000:
                answer += "\n💡 **Insight:** You have a substantial portfolio. Consider diversification analysis."
            
            suggestions = [
                "Get portfolio risk analysis",
                "See rebalancing suggestions",
                "View detailed asset breakdown",
                "Set portfolio alerts"
            ]
            
            return QueryResponse(
                answer=answer,
                data={'portfolio': portfolio},
                visualizations=[{
                    'type': 'portfolio_pie_chart',
                    'data': [{'symbol': a.symbol, 'value': a.value_usd} for a in portfolio.assets]
                }],
                suggestions=suggestions,
                confidence=0.9,
                sources=['Portfolio Manager']
            )
            
        except Exception as e:
            logger.error(f"Error handling portfolio query: {e}")
            return QueryResponse(
                answer="I encountered an error accessing your portfolio.",
                data={},
                visualizations=[],
                suggestions=[],
                confidence=0.0,
                sources=[]
            )

    async def _handle_comparison_query(self, user_id: int, intent: QueryIntent, query: str) -> QueryResponse:
        """Handle comparison queries"""
        try:
            if len(intent.entities) < 2:
                return QueryResponse(
                    answer="Please specify two tokens to compare.",
                    data={},
                    visualizations=[],
                    suggestions=["Try: 'Compare BTC and ETH'", "Try: 'BTC vs ETH'"],
                    confidence=0.3,
                    sources=[]
                )
            
            token1, token2 = intent.entities[0], intent.entities[1]
            
            # Get data for both tokens
            data1 = await self._get_token_price_data(token1)
            data2 = await self._get_token_price_data(token2)
            
            if not data1 or not data2:
                return QueryResponse(
                    answer=f"I couldn't find data for one or both tokens: {token1}, {token2}",
                    data={},
                    visualizations=[],
                    suggestions=["Check token symbols", "Try different tokens"],
                    confidence=0.2,
                    sources=[]
                )
            
            # Compare the tokens
            answer = f"⚖️ **{token1.upper()} vs {token2.upper()} Comparison**\n\n"
            
            # Price comparison
            answer += "**Current Prices:**\n"
            answer += f"• {token1.upper()}: ${data1['current_price']:,.2f}\n"
            answer += f"• {token2.upper()}: ${data2['current_price']:,.2f}\n\n"
            
            # Performance comparison
            change1 = data1.get('price_change_percentage_24h', 0)
            change2 = data2.get('price_change_percentage_24h', 0)
            
            answer += "**24h Performance:**\n"
            answer += f"• {token1.upper()}: {change1:+.2f}%\n"
            answer += f"• {token2.upper()}: {change2:+.2f}%\n\n"
            
            # Market cap comparison
            if 'market_cap' in data1 and 'market_cap' in data2:
                answer += "**Market Cap:**\n"
                answer += f"• {token1.upper()}: ${data1['market_cap']:,.0f}\n"
                answer += f"• {token2.upper()}: ${data2['market_cap']:,.0f}\n\n"
            
            # Winner analysis
            if change1 > change2:
                answer += f"🏆 **24h Winner:** {token1.upper()} (+{change1:.2f}%)"
            elif change2 > change1:
                answer += f"🏆 **24h Winner:** {token2.upper()} (+{change2:.2f}%)"
            else:
                answer += "🤝 **24h Performance:** Tied"
            
            suggestions = [
                f"Get detailed analysis of {token1}",
                f"Get detailed analysis of {token2}",
                f"Set alerts for {token1} and {token2}",
                "Compare with other tokens"
            ]
            
            return QueryResponse(
                answer=answer,
                data={'token1': data1, 'token2': data2},
                visualizations=[{
                    'type': 'comparison_chart',
                    'tokens': [token1, token2],
                    'timeframe': intent.timeframe or '24h'
                }],
                suggestions=suggestions,
                confidence=0.9,
                sources=['CoinGecko']
            )
            
        except Exception as e:
            logger.error(f"Error handling comparison query: {e}")
            return QueryResponse(
                answer="I encountered an error comparing the tokens.",
                data={},
                visualizations=[],
                suggestions=[],
                confidence=0.0,
                sources=[]
            )

    async def _handle_analysis_query(self, user_id: int, intent: QueryIntent, query: str) -> QueryResponse:
        """Handle analysis queries"""
        try:
            if not intent.entities:
                return QueryResponse(
                    answer="Please specify what you'd like me to analyze.",
                    data={},
                    visualizations=[],
                    suggestions=["Try: 'Analyze BTC'", "Try: 'ETH analysis'"],
                    confidence=0.3,
                    sources=[]
                )
            
            token = intent.entities[0]
            
            # Get comprehensive data
            price_data = await self._get_token_price_data(token)
            technical_data = await self._get_technical_analysis(token)
            
            if not price_data:
                return QueryResponse(
                    answer=f"I couldn't find data for {token}.",
                    data={},
                    visualizations=[],
                    suggestions=["Check token symbol", "Try a different token"],
                    confidence=0.2,
                    sources=[]
                )
            
            # Generate analysis
            answer = f"🔍 **{token.upper()} Analysis**\n\n"
            
            # Price analysis
            price = price_data['current_price']
            change_24h = price_data.get('price_change_percentage_24h', 0)
            change_7d = price_data.get('price_change_percentage_7d', 0)
            
            answer += "**Price Analysis:**\n"
            answer += f"• Current: ${price:,.2f}\n"
            answer += f"• 24h: {change_24h:+.2f}%\n"
            answer += f"• 7d: {change_7d:+.2f}%\n\n"
            
            # Technical analysis
            if technical_data:
                answer += "**Technical Indicators:**\n"
                rsi = technical_data.get('rsi', 50)
                if rsi < 30:
                    answer += f"• RSI: {rsi:.1f} (Oversold 📉)\n"
                elif rsi > 70:
                    answer += f"• RSI: {rsi:.1f} (Overbought 📈)\n"
                else:
                    answer += f"• RSI: {rsi:.1f} (Neutral ➡️)\n"
                
                macd = technical_data.get('macd', 0)
                macd_signal = technical_data.get('macd_signal', 0)
                if macd > macd_signal:
                    answer += "• MACD: Bullish 🟢\n"
                else:
                    answer += "• MACD: Bearish 🔴\n"
                
                answer += "\n"
            
            # Market context
            if 'market_cap_rank' in price_data:
                rank = price_data['market_cap_rank']
                answer += f"**Market Position:**\n"
                answer += f"• Rank: #{rank}\n"
                
                if rank <= 10:
                    answer += "• Category: Blue Chip 💎\n"
                elif rank <= 50:
                    answer += "• Category: Large Cap 🏢\n"
                elif rank <= 200:
                    answer += "• Category: Mid Cap 📊\n"
                else:
                    answer += "• Category: Small Cap 🚀\n"
                
                answer += "\n"
            
            # AI-powered insights
            insights = await self._generate_ai_insights(token, price_data, technical_data)
            if insights:
                answer += f"**AI Insights:**\n{insights}\n\n"
            
            suggestions = [
                f"Set price alerts for {token}",
                f"Compare {token} with similar tokens",
                f"Get {token} news and updates",
                f"Add {token} to portfolio tracking"
            ]
            
            return QueryResponse(
                answer=answer,
                data={'price_data': price_data, 'technical_data': technical_data},
                visualizations=[{
                    'type': 'analysis_dashboard',
                    'token': token,
                    'timeframe': intent.timeframe or '7d'
                }],
                suggestions=suggestions,
                confidence=0.9,
                sources=['CoinGecko', 'Technical Analysis']
            )
            
        except Exception as e:
            logger.error(f"Error handling analysis query: {e}")
            return QueryResponse(
                answer="I encountered an error performing the analysis.",
                data={},
                visualizations=[],
                suggestions=[],
                confidence=0.0,
                sources=[]
            )

    async def _handle_general_query(self, user_id: int, intent: QueryIntent, query: str) -> QueryResponse:
        """Handle general queries using AI"""
        try:
            # Use AI to generate response
            ai_prompt = f"""
            User query: "{query}"
            
            This is a cryptocurrency-related question. Please provide a helpful, accurate response.
            Focus on:
            - Factual information about cryptocurrencies, DeFi, or blockchain
            - Educational content
            - Practical advice
            
            Keep the response concise and actionable.
            """
            
            ai_response = await get_ai_response(ai_prompt, user_id)
            
            suggestions = [
                "Ask about specific token prices",
                "Check your portfolio",
                "Get market analysis",
                "Set up price alerts"
            ]
            
            return QueryResponse(
                answer=ai_response,
                data={},
                visualizations=[],
                suggestions=suggestions,
                confidence=0.7,
                sources=['AI Assistant']
            )
            
        except Exception as e:
            logger.error(f"Error handling general query: {e}")
            return QueryResponse(
                answer="I'm not sure how to help with that. Try asking about token prices, portfolio analysis, or market data.",
                data={},
                visualizations=[],
                suggestions=[
                    "Ask about token prices",
                    "Check portfolio performance",
                    "Get market analysis"
                ],
                confidence=0.3,
                sources=[]
            )

    async def _get_token_price_data(self, token: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive price data for a token"""
        try:
            # Use CoinGecko API
            url = f"https://api.coingecko.com/api/v3/coins/{token.lower()}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                market_data = data.get('market_data', {})
                
                return {
                    'current_price': market_data.get('current_price', {}).get('usd', 0),
                    'price_change_percentage_24h': market_data.get('price_change_percentage_24h', 0),
                    'price_change_percentage_7d': market_data.get('price_change_percentage_7d', 0),
                    'market_cap': market_data.get('market_cap', {}).get('usd', 0),
                    'market_cap_rank': data.get('market_cap_rank', 0),
                    'volume_24h': market_data.get('total_volume', {}).get('usd', 0),
                    'circulating_supply': market_data.get('circulating_supply', 0),
                    'total_supply': market_data.get('total_supply', 0)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting token price data: {e}")
            return None

    async def _get_technical_analysis(self, token: str) -> Optional[Dict[str, float]]:
        """Get technical analysis data for a token"""
        try:
            # This would typically use the advanced_alerts technical analysis
            from advanced_alerts import advanced_alerts
            return await advanced_alerts._get_technical_indicators(token)
            
        except Exception as e:
            logger.error(f"Error getting technical analysis: {e}")
            return None

    async def _generate_ai_insights(self, token: str, price_data: Dict, technical_data: Dict) -> str:
        """Generate AI-powered insights"""
        try:
            prompt = f"""
            Analyze {token.upper()} based on this data:
            
            Price Data:
            - Current Price: ${price_data.get('current_price', 0):,.2f}
            - 24h Change: {price_data.get('price_change_percentage_24h', 0):.2f}%
            - Market Cap Rank: #{price_data.get('market_cap_rank', 'N/A')}
            
            Technical Data:
            {json.dumps(technical_data, indent=2) if technical_data else 'No technical data available'}
            
            Provide 2-3 key insights in bullet points. Be concise and actionable.
            """
            
            insights = await get_ai_response(prompt, 0)  # Use system user ID
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return ""

    async def _enhance_with_ai(self, user_id: int, query: str, response: QueryResponse) -> QueryResponse:
        """Enhance response with AI if confidence is low"""
        try:
            prompt = f"""
            User asked: "{query}"
            
            Current response: "{response.answer}"
            
            The response confidence is low ({response.confidence:.2f}). 
            Please provide a better, more helpful response to the user's question.
            Focus on cryptocurrency, DeFi, and blockchain topics.
            """
            
            enhanced_answer = await get_ai_response(prompt, user_id)
            
            response.answer = enhanced_answer
            response.confidence = 0.7
            response.sources.append('AI Enhancement')
            
            return response
            
        except Exception as e:
            logger.error(f"Error enhancing response with AI: {e}")
            return response

    # Placeholder methods for other query types
    async def _handle_prediction_query(self, user_id: int, intent: QueryIntent, query: str) -> QueryResponse:
        """Handle prediction queries"""
        return QueryResponse(
            answer="Price predictions are not available yet. This feature is coming soon!",
            data={},
            visualizations=[],
            suggestions=["Try technical analysis instead", "Set price alerts", "Check current market trends"],
            confidence=0.5,
            sources=[]
        )

    async def _handle_trend_query(self, user_id: int, intent: QueryIntent, query: str) -> QueryResponse:
        """Handle trend queries"""
        return QueryResponse(
            answer="Trend analysis is not available yet. This feature is coming soon!",
            data={},
            visualizations=[],
            suggestions=["Check individual token analysis", "Compare tokens", "Set up alerts"],
            confidence=0.5,
            sources=[]
        )

    async def _handle_yield_query(self, user_id: int, intent: QueryIntent, query: str) -> QueryResponse:
        """Handle yield farming queries"""
        return QueryResponse(
            answer="Yield farming data is not available yet. This feature is coming soon!",
            data={},
            visualizations=[],
            suggestions=["Check DeFi protocols", "Analyze token performance", "Set portfolio alerts"],
            confidence=0.5,
            sources=[]
        )

    async def _handle_news_query(self, user_id: int, intent: QueryIntent, query: str) -> QueryResponse:
        """Handle news queries"""
        return QueryResponse(
            answer="News aggregation is not available yet. This feature is coming soon!",
            data={},
            visualizations=[],
            suggestions=["Check token analysis", "Set price alerts", "Monitor social sentiment"],
            confidence=0.5,
            sources=[]
        )

# Global instance
natural_language_query = NaturalLanguageQueryEngine()