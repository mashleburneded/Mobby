# src/enhanced_response_handler.py
"""
Enhanced Response Handler for Möbius AI Assistant
Prioritizes real-time data and built-in commands over templates and MCP
"""

import asyncio
import logging
import json
import requests
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta

# Import data sources and handlers
from enhanced_intent_system import EnhancedIntentAnalysis, IntentType, ResponseStrategy
from defillama_api import defillama_api, get_protocol_data, search_defi_protocols, get_top_defi_protocols
from crypto_research import query_defillama, get_arkham_data, get_nansen_data
from ai_provider_manager import generate_ai_response
from config import config

logger = logging.getLogger(__name__)

class EnhancedResponseHandler:
    """Enhanced response handler with smart routing and real data integration"""
    
    def __init__(self):
        self.coingecko_api_key = config.get('COINGECKO_API_KEY')
        self.response_cache = {}
        self.cache_ttl = 300  # 5 minutes cache for price data
        
    async def handle_intent(self, analysis: EnhancedIntentAnalysis, text: str, user_id: int, context: Dict = None) -> Dict[str, Any]:
        """Route intent to appropriate handler based on analysis"""
        try:
            # Route based on response strategy
            if analysis.response_strategy == ResponseStrategy.BUILT_IN_COMMAND:
                return await self._handle_built_in_command(analysis, text, user_id, context)
            
            elif analysis.response_strategy == ResponseStrategy.LIVE_DATA_API:
                return await self._handle_live_data_query(analysis, text, user_id, context)
            
            elif analysis.response_strategy == ResponseStrategy.AI_WITH_DATA:
                return await self._handle_ai_with_data(analysis, text, user_id, context)
            
            elif analysis.response_strategy == ResponseStrategy.TEMPLATE_RESPONSE:
                return await self._handle_template_response(analysis, text, user_id, context)
            
            elif analysis.response_strategy == ResponseStrategy.SIMPLE_AI:
                return await self._handle_simple_ai(analysis, text, user_id, context)
            
            else:
                # Fallback to MCP if configured
                if analysis.fallback_strategy:
                    logger.info(f"Using fallback strategy: {analysis.fallback_strategy}")
                    return await self._handle_fallback(analysis, text, user_id, context)
                else:
                    return await self._handle_simple_ai(analysis, text, user_id, context)
                    
        except Exception as e:
            logger.error(f"Error handling intent {analysis.intent_type}: {e}")
            return {
                "type": "error",
                "message": "I encountered an error processing your request. Please try again.",
                "error": str(e)
            }
    
    async def _handle_built_in_command(self, analysis: EnhancedIntentAnalysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle built-in commands"""
        intent_type = analysis.intent_type
        entities = analysis.extracted_entities
        
        if intent_type == IntentType.CRYPTO_PRICE:
            return await self._handle_price_query(entities, text)
        
        elif intent_type == IntentType.PORTFOLIO_CHECK:
            return await self._handle_portfolio_query(user_id, context)
        
        elif intent_type == IntentType.ALERT_MANAGEMENT:
            return await self._handle_alert_query(entities, user_id, context)
        
        elif intent_type == IntentType.HELP_REQUEST:
            return await self._handle_help_query()
        
        else:
            return {
                "type": "error",
                "message": "Built-in command handler not implemented for this intent."
            }
    
    async def _handle_live_data_query(self, analysis: EnhancedIntentAnalysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle queries that need live data from APIs"""
        intent_type = analysis.intent_type
        entities = analysis.extracted_entities
        
        if intent_type == IntentType.CRYPTO_PRICE:
            return await self._fetch_crypto_price(entities)
        
        elif intent_type == IntentType.DEFI_PROTOCOL:
            return await self._fetch_defi_protocol_data(entities)
        
        elif intent_type == IntentType.YIELD_FARMING:
            return await self._fetch_yield_opportunities(text)
        
        elif intent_type == IntentType.CHAIN_ANALYSIS:
            return await self._fetch_chain_analysis(text)
        
        else:
            return {
                "type": "error",
                "message": "Live data handler not implemented for this intent."
            }
    
    async def _handle_ai_with_data(self, analysis: EnhancedIntentAnalysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle AI responses enhanced with real data"""
        # Fetch relevant data first
        data_context = await self._gather_relevant_data(analysis, text)
        
        # Generate AI response with data context
        enhanced_prompt = f"""
        User query: {text}
        
        Relevant data context:
        {json.dumps(data_context, indent=2)}
        
        Please provide a comprehensive response using the provided data context.
        Focus on being accurate and helpful, using the real data provided.
        """
        
        messages = [{"role": "user", "content": enhanced_prompt}]
        ai_response = await generate_ai_response(messages)
        
        return {
            "type": "ai_with_data",
            "message": ai_response if ai_response else "I couldn't generate a response with the available data.",
            "data_context": data_context,
            "confidence": analysis.confidence
        }
    
    async def _handle_template_response(self, analysis: EnhancedIntentAnalysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle template responses for simple interactions"""
        intent_type = analysis.intent_type
        
        if intent_type == IntentType.GREETING:
            return {
                "type": "template",
                "message": "👋 Hello! I'm Möbius, your DeFi and crypto assistant. How can I help you today?\n\nTry asking me about:\n• Crypto prices: 'BTC price'\n• DeFi protocols: 'Tell me about Uniswap'\n• Yield opportunities: 'Best yields'\n• Portfolio help: 'My portfolio'"
            }
        
        else:
            return {
                "type": "template",
                "message": "I'm here to help with crypto and DeFi questions!"
            }
    
    async def _handle_simple_ai(self, analysis: EnhancedIntentAnalysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle simple AI responses"""
        try:
            messages = [{"role": "user", "content": text}]
            ai_response = await generate_ai_response(messages)
            
            return {
                "type": "ai_simple",
                "message": ai_response if ai_response else "I'm not sure how to help with that. Could you rephrase your question?",
                "confidence": analysis.confidence
            }
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                "type": "ai_simple",
                "message": "I'm not sure how to help with that. Could you rephrase your question?",
                "confidence": analysis.confidence
            }
    
    async def _handle_fallback(self, analysis: EnhancedIntentAnalysis, text: str, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle fallback strategies"""
        if analysis.fallback_strategy == ResponseStrategy.SIMPLE_AI:
            return await self._handle_simple_ai(analysis, text, user_id, context)
        elif analysis.fallback_strategy == ResponseStrategy.MCP_FALLBACK:
            # Try MCP as last resort
            try:
                from mcp_integration import enhance_query
                mcp_response = await enhance_query(text, user_id)
                return {
                    "type": "mcp_fallback",
                    "message": mcp_response.get("message", "I couldn't process that request."),
                    "confidence": 0.5
                }
            except Exception as e:
                logger.error(f"MCP fallback failed: {e}")
                return await self._handle_simple_ai(analysis, text, user_id, context)
        else:
            return await self._handle_simple_ai(analysis, text, user_id, context)
    
    async def _fetch_crypto_price(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch real-time crypto price data"""
        symbol = entities.get('normalized_symbol', entities.get('symbol', ''))
        
        if not symbol:
            return {
                "type": "error",
                "message": "Please specify which cryptocurrency you'd like the price for."
            }
        
        # Check cache first
        cache_key = f"price_{symbol}"
        if cache_key in self.response_cache:
            cached_data, timestamp = self.response_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                return cached_data
        
        try:
            # Fetch from CoinGecko API
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': symbol,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if symbol in data:
                    price_data = data[symbol]
                    price = price_data.get('usd', 0)
                    change_24h = price_data.get('usd_24h_change', 0)
                    market_cap = price_data.get('usd_market_cap', 0)
                    volume_24h = price_data.get('usd_24h_vol', 0)
                    
                    # Format response
                    change_emoji = "📈" if change_24h > 0 else "📉" if change_24h < 0 else "➡️"
                    
                    message = f"💰 **{symbol.upper()} Price**\n\n"
                    message += f"💵 **Price:** ${price:,.4f}\n"
                    message += f"{change_emoji} **24h Change:** {change_24h:+.2f}%\n"
                    
                    if market_cap:
                        message += f"📊 **Market Cap:** ${market_cap:,.0f}\n"
                    if volume_24h:
                        message += f"📈 **24h Volume:** ${volume_24h:,.0f}\n"
                    
                    message += f"\n🕐 *Updated: {datetime.now().strftime('%H:%M UTC')}*"
                    
                    result = {
                        "type": "price_data",
                        "message": message,
                        "data": {
                            "symbol": symbol,
                            "price": price,
                            "change_24h": change_24h,
                            "market_cap": market_cap,
                            "volume_24h": volume_24h
                        }
                    }
                    
                    # Cache the result
                    self.response_cache[cache_key] = (result, datetime.now())
                    return result
                
                else:
                    return {
                        "type": "error",
                        "message": f"Cryptocurrency '{symbol}' not found. Please check the symbol and try again."
                    }
            
            else:
                logger.error(f"CoinGecko API error: {response.status_code}")
                return {
                    "type": "error",
                    "message": "Unable to fetch price data at the moment. Please try again later."
                }
                
        except Exception as e:
            logger.error(f"Error fetching crypto price: {e}")
            return {
                "type": "error",
                "message": "Error fetching price data. Please try again."
            }
    
    async def _fetch_defi_protocol_data(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch DeFi protocol data from DeFiLlama"""
        protocol = entities.get('protocol', '')
        
        if not protocol:
            return {
                "type": "error",
                "message": "Please specify which DeFi protocol you'd like information about."
            }
        
        try:
            # Try to get protocol data from DeFiLlama
            protocol_data = await get_protocol_data(protocol)
            
            if protocol_data:
                return {
                    "type": "defi_protocol",
                    "message": protocol_data,
                    "protocol": protocol
                }
            else:
                # Try searching for the protocol
                search_results = await search_defi_protocols(protocol)
                
                if search_results and "No protocols found" not in search_results:
                    return {
                        "type": "defi_search",
                        "message": search_results,
                        "query": protocol
                    }
                else:
                    return {
                        "type": "error",
                        "message": f"DeFi protocol '{protocol}' not found. Try searching for similar protocols or check the spelling."
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching DeFi protocol data: {e}")
            return {
                "type": "error",
                "message": "Error fetching protocol data. Please try again."
            }
    
    async def _fetch_yield_opportunities(self, text: str) -> Dict[str, Any]:
        """Fetch yield farming opportunities"""
        try:
            # Extract minimum APY if specified
            import re
            apy_match = re.search(r'(\d+(?:\.\d+)?)%?\s*(?:apy|apr)', text.lower())
            min_apy = float(apy_match.group(1)) if apy_match else 5.0
            
            yield_data = await defillama_api.get_yield_opportunities(min_apy)
            
            if yield_data:
                return {
                    "type": "yield_opportunities",
                    "message": yield_data,
                    "min_apy": min_apy
                }
            else:
                return {
                    "type": "error",
                    "message": "Unable to fetch yield opportunities at the moment."
                }
                
        except Exception as e:
            logger.error(f"Error fetching yield opportunities: {e}")
            return {
                "type": "error",
                "message": "Error fetching yield data. Please try again."
            }
    
    async def _fetch_chain_analysis(self, text: str) -> Dict[str, Any]:
        """Fetch blockchain analysis data"""
        try:
            # Extract chain names from text
            import re
            chain_patterns = {
                'ethereum': ['ethereum', 'eth'],
                'solana': ['solana', 'sol'],
                'polygon': ['polygon', 'matic'],
                'avalanche': ['avalanche', 'avax'],
                'bsc': ['bsc', 'binance', 'bnb'],
            }
            
            detected_chains = []
            text_lower = text.lower()
            
            for chain, keywords in chain_patterns.items():
                if any(keyword in text_lower for keyword in keywords):
                    detected_chains.append(chain)
            
            if not detected_chains:
                detected_chains = ['ethereum', 'solana', 'polygon']  # Default comparison
            
            chain_data = await defillama_api.get_chain_comparison(detected_chains)
            
            if chain_data:
                return {
                    "type": "chain_analysis",
                    "message": chain_data,
                    "chains": detected_chains
                }
            else:
                return {
                    "type": "error",
                    "message": "Unable to fetch chain analysis data at the moment."
                }
                
        except Exception as e:
            logger.error(f"Error fetching chain analysis: {e}")
            return {
                "type": "error",
                "message": "Error fetching chain data. Please try again."
            }
    
    async def _gather_relevant_data(self, analysis: EnhancedIntentAnalysis, text: str) -> Dict[str, Any]:
        """Gather relevant data for AI enhancement"""
        data_context = {}
        
        try:
            # Gather data based on intent type
            if analysis.intent_type == IntentType.MARKET_DATA:
                # Get top protocols for market overview
                top_protocols = await get_top_defi_protocols(5)
                if top_protocols:
                    data_context['top_defi_protocols'] = top_protocols
            
            # Add more data gathering logic as needed
            
        except Exception as e:
            logger.error(f"Error gathering data context: {e}")
        
        return data_context
    
    async def _handle_price_query(self, entities: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Handle price queries using built-in logic"""
        return await self._fetch_crypto_price(entities)
    
    async def _handle_portfolio_query(self, user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle portfolio queries"""
        # This would integrate with user's portfolio data
        return {
            "type": "portfolio",
            "message": "📊 **Portfolio Feature**\n\nPortfolio tracking is coming soon! You'll be able to:\n• Track your holdings\n• Monitor performance\n• Get alerts on changes\n\nFor now, you can ask me about specific crypto prices or DeFi protocols."
        }
    
    async def _handle_alert_query(self, entities: Dict[str, Any], user_id: int, context: Dict) -> Dict[str, Any]:
        """Handle alert queries"""
        target = entities.get('target', '')
        
        return {
            "type": "alert",
            "message": f"🔔 **Alert System**\n\nAlert functionality is being enhanced! You'll soon be able to set alerts for:\n• Price changes\n• Portfolio movements\n• DeFi protocol updates\n\nFor now, you can ask me about current prices and protocol data."
        }
    
    async def _handle_help_query(self) -> Dict[str, Any]:
        """Handle help queries"""
        help_message = """
🤖 **Möbius AI Assistant - Help**

**What I can do:**

💰 **Crypto Prices**
• `BTC price` - Get Bitcoin price
• `ETH price` - Get Ethereum price
• `price of [symbol]` - Get any crypto price

📊 **DeFi Protocols**
• `Tell me about Uniswap` - Protocol information
• `Aave protocol` - Get protocol stats
• `Search [protocol name]` - Find protocols

🌾 **Yield Farming**
• `Best yields` - Top yield opportunities
• `High APY` - Find high-yield pools
• `Yield farming opportunities` - Current opportunities

🔗 **Chain Analysis**
• `Ethereum analysis` - Chain statistics
• `Compare chains` - Multi-chain comparison
• `Solana vs Ethereum` - Chain comparison

📈 **Market Data**
• `Market overview` - General market info
• `Top DeFi protocols` - Leading protocols
• `Market trends` - Current trends

**Examples:**
• "What's the price of Bitcoin?"
• "Tell me about the Uniswap protocol"
• "Show me the best yield farming opportunities"
• "Compare Ethereum and Solana"

Need help with something specific? Just ask!
        """
        
        return {
            "type": "help",
            "message": help_message.strip()
        }

# Global instance
enhanced_response_handler = EnhancedResponseHandler()

async def handle_enhanced_response(analysis: EnhancedIntentAnalysis, text: str, user_id: int, context: Dict = None) -> Dict[str, Any]:
    """Handle enhanced response routing"""
    return await enhanced_response_handler.handle_intent(analysis, text, user_id, context or {})