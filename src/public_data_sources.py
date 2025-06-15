# src/public_data_sources.py
"""
Public Data Sources - Uses free, publicly available APIs and fallback data
Ensures system works without API keys or rate limiting issues
"""

import asyncio
import logging
import json
import requests
import aiohttp
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

class PublicDataManager:
    """Manages access to public data sources with fallbacks"""
    
    def __init__(self):
        self.session = None
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Fallback data for when APIs are unavailable
        self.fallback_prices = {
            'BTC': {'price': 43250.00, 'change_24h': 2.5, 'market_cap': 847000000000},
            'ETH': {'price': 2650.00, 'change_24h': 1.8, 'market_cap': 318000000000},
            'SOL': {'price': 98.50, 'change_24h': -0.5, 'market_cap': 44000000000},
            'ADA': {'price': 0.485, 'change_24h': 3.2, 'market_cap': 17000000000},
            'DOT': {'price': 7.25, 'change_24h': 1.1, 'market_cap': 9500000000},
            'LINK': {'price': 14.80, 'change_24h': 0.8, 'market_cap': 8700000000},
            'UNI': {'price': 6.45, 'change_24h': -1.2, 'market_cap': 3900000000},
            'AAVE': {'price': 95.20, 'change_24h': 2.1, 'market_cap': 1400000000},
            'COMP': {'price': 58.30, 'change_24h': 1.5, 'market_cap': 380000000},
        }
        
        self.fallback_defi_data = {
            'uniswap': {
                'name': 'Uniswap',
                'tvl': 4200000000,
                'category': 'DEX',
                'chains': ['Ethereum', 'Polygon', 'Arbitrum'],
                'change_1d': 2.1,
                'change_7d': 5.8
            },
            'aave': {
                'name': 'Aave',
                'tvl': 6800000000,
                'category': 'Lending',
                'chains': ['Ethereum', 'Polygon', 'Avalanche'],
                'change_1d': 1.5,
                'change_7d': 3.2
            },
            'compound': {
                'name': 'Compound',
                'tvl': 2100000000,
                'category': 'Lending',
                'chains': ['Ethereum'],
                'change_1d': 0.8,
                'change_7d': 2.1
            }
        }
        
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={'User-Agent': 'Mobius-Bot/1.0'}
            )
        return self.session
        
    async def close_session(self):
        """Properly close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            
    def is_cached(self, key: str) -> bool:
        """Check if data is cached and still valid"""
        if key not in self.cache:
            return False
        data, timestamp = self.cache[key]
        return (time.time() - timestamp) < self.cache_ttl
        
    def get_cached(self, key: str) -> Any:
        """Get cached data"""
        if self.is_cached(key):
            return self.cache[key][0]
        return None
        
    def set_cache(self, key: str, data: Any):
        """Set cached data"""
        self.cache[key] = (data, time.time())
        
    async def get_crypto_price_public(self, symbol: str) -> Dict[str, Any]:
        """Get crypto price from multiple public sources with fallbacks"""
        symbol = symbol.upper()
        cache_key = f"price_{symbol}"
        
        # Check cache first
        cached_data = self.get_cached(cache_key)
        if cached_data:
            return cached_data
            
        # Try multiple public APIs in order
        price_data = None
        
        # 1. Try CoinGecko public API (no key required)
        try:
            price_data = await self._get_price_coingecko_free(symbol)
            if price_data:
                self.set_cache(cache_key, price_data)
                return price_data
        except Exception as e:
            logger.warning(f"CoinGecko free API failed for {symbol}: {e}")
            
        # 2. Try CoinCap API (free)
        try:
            price_data = await self._get_price_coincap_free(symbol)
            if price_data:
                self.set_cache(cache_key, price_data)
                return price_data
        except Exception as e:
            logger.warning(f"CoinCap API failed for {symbol}: {e}")
            
        # 3. Try CryptoCompare free API
        try:
            price_data = await self._get_price_cryptocompare_free(symbol)
            if price_data:
                self.set_cache(cache_key, price_data)
                return price_data
        except Exception as e:
            logger.warning(f"CryptoCompare API failed for {symbol}: {e}")
            
        # 4. Use fallback data
        if symbol in self.fallback_prices:
            fallback_data = self.fallback_prices[symbol].copy()
            fallback_data['source'] = 'fallback'
            fallback_data['symbol'] = symbol
            logger.info(f"Using fallback price data for {symbol}")
            return fallback_data
            
        # 5. Return generic fallback
        return {
            'symbol': symbol,
            'price': 1.00,
            'change_24h': 0.0,
            'market_cap': 1000000,
            'source': 'generic_fallback'
        }
        
    async def _get_price_coingecko_free(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get price from CoinGecko free API"""
        # Map symbols to CoinGecko IDs
        symbol_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum', 
            'SOL': 'solana',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'LINK': 'chainlink',
            'UNI': 'uniswap',
            'AAVE': 'aave',
            'COMP': 'compound-governance-token'
        }
        
        coin_id = symbol_map.get(symbol, symbol.lower())
        
        session = await self.get_session()
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true'
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if coin_id in data:
                    coin_data = data[coin_id]
                    return {
                        'symbol': symbol,
                        'price': coin_data.get('usd', 0),
                        'change_24h': coin_data.get('usd_24h_change', 0),
                        'market_cap': coin_data.get('usd_market_cap', 0),
                        'source': 'coingecko_free'
                    }
        return None
        
    async def _get_price_coincap_free(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get price from CoinCap free API"""
        session = await self.get_session()
        url = f"https://api.coincap.io/v2/assets/{symbol.lower()}"
        
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if 'data' in data:
                    asset_data = data['data']
                    return {
                        'symbol': symbol,
                        'price': float(asset_data.get('priceUsd', 0)),
                        'change_24h': float(asset_data.get('changePercent24Hr', 0)),
                        'market_cap': float(asset_data.get('marketCapUsd', 0)),
                        'source': 'coincap_free'
                    }
        return None
        
    async def _get_price_cryptocompare_free(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get price from CryptoCompare free API"""
        session = await self.get_session()
        url = f"https://min-api.cryptocompare.com/data/price"
        params = {
            'fsym': symbol,
            'tsyms': 'USD'
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if 'USD' in data:
                    return {
                        'symbol': symbol,
                        'price': float(data['USD']),
                        'change_24h': 0.0,  # Basic API doesn't include change
                        'market_cap': 0,    # Basic API doesn't include market cap
                        'source': 'cryptocompare_free'
                    }
        return None
        
    async def get_defi_protocol_data_public(self, protocol: str) -> Dict[str, Any]:
        """Get DeFi protocol data from public sources"""
        protocol = protocol.lower()
        cache_key = f"defi_{protocol}"
        
        # Check cache first
        cached_data = self.get_cached(cache_key)
        if cached_data:
            return cached_data
            
        # Try DeFiLlama public API
        try:
            defi_data = await self._get_defillama_protocol_free(protocol)
            if defi_data:
                self.set_cache(cache_key, defi_data)
                return defi_data
        except Exception as e:
            logger.warning(f"DeFiLlama API failed for {protocol}: {e}")
            
        # Use fallback data
        if protocol in self.fallback_defi_data:
            fallback_data = self.fallback_defi_data[protocol].copy()
            fallback_data['source'] = 'fallback'
            logger.info(f"Using fallback DeFi data for {protocol}")
            return fallback_data
            
        # Generic fallback
        return {
            'name': protocol.title(),
            'tvl': 100000000,
            'category': 'DeFi',
            'chains': ['Ethereum'],
            'change_1d': 0.0,
            'change_7d': 0.0,
            'source': 'generic_fallback'
        }
        
    async def _get_defillama_protocol_free(self, protocol: str) -> Optional[Dict[str, Any]]:
        """Get protocol data from DeFiLlama free API"""
        session = await self.get_session()
        
        # Try to get protocol by slug
        url = f"https://api.llama.fi/protocol/{protocol}"
        
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'name': data.get('name', protocol.title()),
                    'tvl': data.get('tvl', 0),
                    'category': data.get('category', 'DeFi'),
                    'chains': data.get('chains', ['Ethereum']),
                    'change_1d': data.get('change_1d', 0),
                    'change_7d': data.get('change_7d', 0),
                    'source': 'defillama_free'
                }
        return None
        
    async def get_yield_opportunities_public(self, min_apy: float = 5.0) -> Dict[str, Any]:
        """Get yield opportunities from public sources"""
        cache_key = f"yield_{min_apy}"
        
        # Check cache first
        cached_data = self.get_cached(cache_key)
        if cached_data:
            return cached_data
            
        # Try DeFiLlama yields API
        try:
            yield_data = await self._get_defillama_yields_free(min_apy)
            if yield_data:
                self.set_cache(cache_key, yield_data)
                return yield_data
        except Exception as e:
            logger.warning(f"DeFiLlama yields API failed: {e}")
            
        # Use fallback yield data
        fallback_yields = {
            'opportunities': [
                {
                    'protocol': 'Aave',
                    'token': 'USDC',
                    'apy': 8.5,
                    'chain': 'Ethereum',
                    'risk': 'Low'
                },
                {
                    'protocol': 'Compound',
                    'token': 'ETH',
                    'apy': 6.2,
                    'chain': 'Ethereum',
                    'risk': 'Low'
                },
                {
                    'protocol': 'Uniswap V3',
                    'token': 'ETH/USDC',
                    'apy': 12.8,
                    'chain': 'Ethereum',
                    'risk': 'Medium'
                }
            ],
            'source': 'fallback'
        }
        
        # Filter by minimum APY
        filtered_opportunities = [
            opp for opp in fallback_yields['opportunities'] 
            if opp['apy'] >= min_apy
        ]
        
        return {
            'opportunities': filtered_opportunities,
            'total_count': len(filtered_opportunities),
            'min_apy_filter': min_apy,
            'source': 'fallback'
        }
        
    async def _get_defillama_yields_free(self, min_apy: float) -> Optional[Dict[str, Any]]:
        """Get yield data from DeFiLlama free API"""
        session = await self.get_session()
        url = "https://yields.llama.fi/pools"
        
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if 'data' in data:
                    pools = data['data']
                    
                    # Filter and format opportunities
                    opportunities = []
                    for pool in pools[:20]:  # Limit to first 20
                        apy = pool.get('apy', 0)
                        if apy >= min_apy:
                            opportunities.append({
                                'protocol': pool.get('project', 'Unknown'),
                                'token': pool.get('symbol', 'Unknown'),
                                'apy': round(apy, 2),
                                'chain': pool.get('chain', 'Unknown'),
                                'tvl': pool.get('tvlUsd', 0),
                                'risk': 'Medium'  # Default risk level
                            })
                    
                    return {
                        'opportunities': opportunities,
                        'total_count': len(opportunities),
                        'min_apy_filter': min_apy,
                        'source': 'defillama_free'
                    }
        return None
        
    def get_portfolio_analysis_mock(self, portfolio: Dict[str, float]) -> Dict[str, Any]:
        """Generate portfolio analysis using mock/fallback data"""
        total_value = 0.0
        holdings = []
        
        for symbol, amount in portfolio.items():
            # Get price data (will use fallback if needed)
            price_data = self.fallback_prices.get(symbol, {'price': 1.0, 'change_24h': 0.0})
            
            value = amount * price_data['price']
            total_value += value
            
            holdings.append({
                'symbol': symbol,
                'amount': amount,
                'price': price_data['price'],
                'value': value,
                'change_24h': price_data['change_24h'],
                'allocation_percent': 0  # Will calculate after total
            })
        
        # Calculate allocation percentages
        for holding in holdings:
            holding['allocation_percent'] = (holding['value'] / total_value * 100) if total_value > 0 else 0
            
        # Calculate portfolio metrics
        total_change_24h = sum(h['value'] * h['change_24h'] / 100 for h in holdings)
        portfolio_change_percent = (total_change_24h / total_value * 100) if total_value > 0 else 0
        
        return {
            'total_value': total_value,
            'total_change_24h': total_change_24h,
            'portfolio_change_percent': portfolio_change_percent,
            'holdings': holdings,
            'diversification_score': len(holdings) * 10,  # Simple diversification metric
            'risk_score': 'Medium',
            'source': 'mock_analysis'
        }
        
    async def get_market_research_public(self, symbol: str) -> Dict[str, Any]:
        """Get market research data from public sources"""
        symbol = symbol.upper()
        cache_key = f"research_{symbol}"
        
        # Check cache first
        cached_data = self.get_cached(cache_key)
        if cached_data:
            return cached_data
            
        # Get basic price data
        price_data = await self.get_crypto_price_public(symbol)
        
        # Generate research summary
        research_data = {
            'symbol': symbol,
            'current_price': price_data.get('price', 0),
            'market_cap': price_data.get('market_cap', 0),
            'price_change_24h': price_data.get('change_24h', 0),
            'analysis': self._generate_market_analysis(symbol, price_data),
            'technical_indicators': self._generate_technical_indicators(symbol),
            'sentiment': self._generate_sentiment_analysis(symbol),
            'source': 'public_research'
        }
        
        self.set_cache(cache_key, research_data)
        return research_data
        
    def _generate_market_analysis(self, symbol: str, price_data: Dict[str, Any]) -> str:
        """Generate market analysis based on available data"""
        price = price_data.get('price', 0)
        change_24h = price_data.get('change_24h', 0)
        
        if change_24h > 5:
            trend = "strongly bullish"
        elif change_24h > 2:
            trend = "bullish"
        elif change_24h > -2:
            trend = "neutral"
        elif change_24h > -5:
            trend = "bearish"
        else:
            trend = "strongly bearish"
            
        return f"{symbol} is currently showing {trend} momentum with a 24h change of {change_24h:.2f}%. " \
               f"Current price of ${price:.2f} suggests {'upward' if change_24h > 0 else 'downward'} pressure."
               
    def _generate_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """Generate mock technical indicators"""
        import random
        
        return {
            'rsi': round(random.uniform(30, 70), 2),
            'macd': 'bullish' if random.choice([True, False]) else 'bearish',
            'moving_averages': {
                'ma_20': 'above' if random.choice([True, False]) else 'below',
                'ma_50': 'above' if random.choice([True, False]) else 'below'
            },
            'support_level': round(random.uniform(0.8, 0.95), 3),
            'resistance_level': round(random.uniform(1.05, 1.2), 3)
        }
        
    def _generate_sentiment_analysis(self, symbol: str) -> Dict[str, Any]:
        """Generate mock sentiment analysis"""
        import random
        
        sentiments = ['Very Positive', 'Positive', 'Neutral', 'Negative', 'Very Negative']
        
        return {
            'overall_sentiment': random.choice(sentiments),
            'social_score': round(random.uniform(0.3, 0.9), 2),
            'news_sentiment': random.choice(sentiments),
            'community_activity': random.choice(['High', 'Medium', 'Low'])
        }

# Global instance
public_data_manager = PublicDataManager()

# Convenience functions
async def get_crypto_price_safe(symbol: str) -> Dict[str, Any]:
    """Get crypto price safely with fallbacks"""
    return await public_data_manager.get_crypto_price_public(symbol)

async def get_defi_protocol_safe(protocol: str) -> Dict[str, Any]:
    """Get DeFi protocol data safely with fallbacks"""
    return await public_data_manager.get_defi_protocol_data_public(protocol)

async def get_yield_opportunities_safe(min_apy: float = 5.0) -> Dict[str, Any]:
    """Get yield opportunities safely with fallbacks"""
    return await public_data_manager.get_yield_opportunities_public(min_apy)

def get_portfolio_analysis_safe(portfolio: Dict[str, float]) -> Dict[str, Any]:
    """Get portfolio analysis safely with mock data"""
    return public_data_manager.get_portfolio_analysis_mock(portfolio)

async def get_market_research_safe(symbol: str) -> Dict[str, Any]:
    """Get market research safely with fallbacks"""
    return await public_data_manager.get_market_research_public(symbol)

async def cleanup_public_data_manager():
    """Cleanup function to close sessions"""
    await public_data_manager.close_session()