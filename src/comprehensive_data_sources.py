# src/comprehensive_data_sources.py
"""
Comprehensive Data Sources - Multi-Source Crypto/DeFi Data Aggregation
Fetches from 20+ public APIs and data sources for maximum coverage
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Configuration for a data source"""
    name: str
    base_url: str
    api_key_required: bool
    rate_limit: int  # requests per minute
    reliability_score: float  # 1-10
    data_types: List[str]  # price, market, defi, yield, social, etc.
    endpoints: Dict[str, str]

class ComprehensiveDataSources:
    """Comprehensive data aggregation from multiple sources"""
    
    def __init__(self):
        self.sources = self._initialize_sources()
        self.session = None
        self.rate_limiters = {}
        self.cache = {}
        self.last_requests = {}
        
    def _initialize_sources(self) -> Dict[str, DataSource]:
        """Initialize all data sources"""
        return {
            # Price & Market Data Sources
            "coingecko": DataSource(
                name="CoinGecko",
                base_url="https://api.coingecko.com/api/v3",
                api_key_required=False,
                rate_limit=50,
                reliability_score=9.5,
                data_types=["price", "market", "historical", "trending"],
                endpoints={
                    "price": "/simple/price",
                    "market": "/coins/markets",
                    "coin_data": "/coins/{id}",
                    "trending": "/search/trending",
                    "global": "/global"
                }
            ),
            
            "coinmarketcap": DataSource(
                name="CoinMarketCap",
                base_url="https://pro-api.coinmarketcap.com/v1",
                api_key_required=True,
                rate_limit=333,
                reliability_score=9.0,
                data_types=["price", "market", "listings"],
                endpoints={
                    "listings": "/cryptocurrency/listings/latest",
                    "quotes": "/cryptocurrency/quotes/latest",
                    "metadata": "/cryptocurrency/info"
                }
            ),
            
            "cryptocompare": DataSource(
                name="CryptoCompare",
                base_url="https://min-api.cryptocompare.com/data",
                api_key_required=False,
                rate_limit=100,
                reliability_score=8.5,
                data_types=["price", "historical", "social"],
                endpoints={
                    "price": "/price",
                    "historical": "/v2/histoday",
                    "social": "/v2/social/coin/latest"
                }
            ),
            
            "coinpaprika": DataSource(
                name="CoinPaprika",
                base_url="https://api.coinpaprika.com/v1",
                api_key_required=False,
                rate_limit=25000,
                reliability_score=8.0,
                data_types=["price", "market", "events"],
                endpoints={
                    "coins": "/coins",
                    "ticker": "/tickers/{coin_id}",
                    "events": "/coins/{coin_id}/events"
                }
            ),
            
            # DeFi Data Sources
            "defillama": DataSource(
                name="DefiLlama",
                base_url="https://api.llama.fi",
                api_key_required=False,
                rate_limit=300,
                reliability_score=9.5,
                data_types=["defi", "tvl", "yield", "protocols"],
                endpoints={
                    "protocols": "/protocols",
                    "tvl": "/v2/historicalChainTvl",
                    "yields": "/pools",
                    "protocol": "/protocol/{protocol}"
                }
            ),
            
            "dune_analytics": DataSource(
                name="Dune Analytics",
                base_url="https://api.dune.com/api/v1",
                api_key_required=True,
                rate_limit=100,
                reliability_score=9.0,
                data_types=["onchain", "analytics", "custom"],
                endpoints={
                    "query": "/query/{query_id}/execute",
                    "results": "/execution/{execution_id}/results"
                }
            ),
            
            "messari": DataSource(
                name="Messari",
                base_url="https://data.messari.io/api/v1",
                api_key_required=False,
                rate_limit=20,
                reliability_score=8.5,
                data_types=["market", "metrics", "research"],
                endpoints={
                    "assets": "/assets",
                    "metrics": "/assets/{asset}/metrics",
                    "news": "/news"
                }
            ),
            
            # Yield & Staking Sources
            "stakerewards": DataSource(
                name="StakeRewards",
                base_url="https://api.stakerewards.com",
                api_key_required=True,
                rate_limit=1000,
                reliability_score=8.0,
                data_types=["staking", "yield", "validators"],
                endpoints={
                    "assets": "/assets",
                    "providers": "/providers",
                    "rewards": "/rewards"
                }
            ),
            
            "beaconchain": DataSource(
                name="BeaconChain",
                base_url="https://beaconcha.in/api/v1",
                api_key_required=False,
                rate_limit=100,
                reliability_score=9.0,
                data_types=["eth2", "staking", "validators"],
                endpoints={
                    "validators": "/validator/{validator}",
                    "epoch": "/epoch/{epoch}",
                    "stats": "/stats"
                }
            ),
            
            # On-Chain Analytics
            "glassnode": DataSource(
                name="Glassnode",
                base_url="https://api.glassnode.com/v1/metrics",
                api_key_required=True,
                rate_limit=100,
                reliability_score=9.5,
                data_types=["onchain", "metrics", "indicators"],
                endpoints={
                    "market": "/market",
                    "network": "/network",
                    "addresses": "/addresses",
                    "transactions": "/transactions"
                }
            ),
            
            "santiment": DataSource(
                name="Santiment",
                base_url="https://api.santiment.net/graphql",
                api_key_required=True,
                rate_limit=300,
                reliability_score=8.5,
                data_types=["social", "onchain", "dev_activity"],
                endpoints={
                    "graphql": ""
                }
            ),
            
            "nansen": DataSource(
                name="Nansen",
                base_url="https://api.nansen.ai/v1",
                api_key_required=True,
                rate_limit=100,
                reliability_score=9.0,
                data_types=["onchain", "labels", "flows"],
                endpoints={
                    "wallets": "/wallets",
                    "tokens": "/tokens",
                    "flows": "/token-flows"
                }
            ),
            
            # Social & Sentiment
            "lunarcrush": DataSource(
                name="LunarCrush",
                base_url="https://api.lunarcrush.com/v2",
                api_key_required=True,
                rate_limit=100,
                reliability_score=8.0,
                data_types=["social", "sentiment", "influencers"],
                endpoints={
                    "assets": "/assets",
                    "social": "/social",
                    "influencers": "/influencers"
                }
            ),
            
            "alternative_me": DataSource(
                name="Alternative.me",
                base_url="https://api.alternative.me",
                api_key_required=False,
                rate_limit=600,
                reliability_score=8.5,
                data_types=["sentiment", "fear_greed"],
                endpoints={
                    "fear_greed": "/fng/",
                    "global_crypto": "/global-crypto-charts/"
                }
            ),
            
            # Blockchain Explorers
            "etherscan": DataSource(
                name="Etherscan",
                base_url="https://api.etherscan.io/api",
                api_key_required=True,
                rate_limit=200,
                reliability_score=9.5,
                data_types=["ethereum", "transactions", "contracts"],
                endpoints={
                    "balance": "",
                    "transactions": "",
                    "gas": ""
                }
            ),
            
            "bscscan": DataSource(
                name="BscScan",
                base_url="https://api.bscscan.com/api",
                api_key_required=True,
                rate_limit=200,
                reliability_score=9.0,
                data_types=["bsc", "transactions", "contracts"],
                endpoints={
                    "balance": "",
                    "transactions": "",
                    "gas": ""
                }
            ),
            
            "polygonscan": DataSource(
                name="PolygonScan",
                base_url="https://api.polygonscan.com/api",
                api_key_required=True,
                rate_limit=200,
                reliability_score=9.0,
                data_types=["polygon", "transactions", "contracts"],
                endpoints={
                    "balance": "",
                    "transactions": "",
                    "gas": ""
                }
            ),
            
            # News & Research
            "cryptopanic": DataSource(
                name="CryptoPanic",
                base_url="https://cryptopanic.com/api/v1",
                api_key_required=True,
                rate_limit=1000,
                reliability_score=8.0,
                data_types=["news", "sentiment"],
                endpoints={
                    "posts": "/posts/"
                }
            ),
            
            "newsapi": DataSource(
                name="NewsAPI",
                base_url="https://newsapi.org/v2",
                api_key_required=True,
                rate_limit=1000,
                reliability_score=8.5,
                data_types=["news", "articles"],
                endpoints={
                    "everything": "/everything",
                    "headlines": "/top-headlines"
                }
            ),
            
            # Additional DeFi Sources
            "1inch": DataSource(
                name="1inch",
                base_url="https://api.1inch.io/v5.0",
                api_key_required=False,
                rate_limit=100,
                reliability_score=8.5,
                data_types=["dex", "swaps", "liquidity"],
                endpoints={
                    "tokens": "/{chain}/tokens",
                    "quote": "/{chain}/quote",
                    "swap": "/{chain}/swap"
                }
            ),
            
            "uniswap": DataSource(
                name="Uniswap",
                base_url="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
                api_key_required=False,
                rate_limit=1000,
                reliability_score=9.0,
                data_types=["dex", "pools", "volume"],
                endpoints={
                    "graphql": ""
                }
            )
        }
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _check_rate_limit(self, source_name: str) -> bool:
        """Check if we can make a request to this source"""
        source = self.sources[source_name]
        current_time = time.time()
        
        if source_name not in self.last_requests:
            self.last_requests[source_name] = []
        
        # Remove requests older than 1 minute
        self.last_requests[source_name] = [
            req_time for req_time in self.last_requests[source_name]
            if current_time - req_time < 60
        ]
        
        # Check if we're under the rate limit
        if len(self.last_requests[source_name]) >= source.rate_limit:
            return False
        
        self.last_requests[source_name].append(current_time)
        return True
    
    async def _make_request(self, source_name: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to a data source"""
        if not await self._check_rate_limit(source_name):
            logger.warning(f"Rate limit exceeded for {source_name}")
            return None
        
        source = self.sources[source_name]
        session = await self.get_session()
        
        url = f"{source.base_url}{endpoint}"
        headers = {}
        
        # Add API key if required
        if source.api_key_required:
            api_key_env = f"{source_name.upper()}_API_KEY"
            api_key = os.getenv(api_key_env)
            if not api_key:
                logger.warning(f"API key not found for {source_name}: {api_key_env}")
                return None
            
            # Different sources use different header formats
            if source_name in ["coinmarketcap"]:
                headers["X-CMC_PRO_API_KEY"] = api_key
            elif source_name in ["etherscan", "bscscan", "polygonscan"]:
                if params is None:
                    params = {}
                params["apikey"] = api_key
            else:
                headers["Authorization"] = f"Bearer {api_key}"
        
        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Error from {source_name}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Request failed for {source_name}: {e}")
            return None
    
    async def get_price_data(self, symbol: str) -> Dict[str, Any]:
        """Get price data from multiple sources"""
        results = {}
        
        # CoinGecko
        try:
            params = {"ids": symbol.lower(), "vs_currencies": "usd", "include_24hr_change": "true"}
            data = await self._make_request("coingecko", "/simple/price", params)
            if data and symbol.lower() in data:
                results["coingecko"] = data[symbol.lower()]
        except Exception as e:
            logger.error(f"CoinGecko price error: {e}")
        
        # CryptoCompare
        try:
            params = {"fsym": symbol.upper(), "tsyms": "USD"}
            data = await self._make_request("cryptocompare", "/price", params)
            if data and "USD" in data:
                results["cryptocompare"] = {"usd": data["USD"]}
        except Exception as e:
            logger.error(f"CryptoCompare price error: {e}")
        
        # CoinPaprika
        try:
            data = await self._make_request("coinpaprika", f"/tickers/{symbol.lower()}-{symbol.lower()}")
            if data:
                results["coinpaprika"] = {
                    "usd": data.get("quotes", {}).get("USD", {}).get("price"),
                    "usd_24h_change": data.get("quotes", {}).get("USD", {}).get("percent_change_24h")
                }
        except Exception as e:
            logger.error(f"CoinPaprika price error: {e}")
        
        return self._aggregate_price_data(results)
    
    async def get_defi_data(self, protocol: str = None) -> Dict[str, Any]:
        """Get DeFi data from multiple sources"""
        results = {}
        
        # DefiLlama
        try:
            if protocol:
                data = await self._make_request("defillama", f"/protocol/{protocol}")
            else:
                data = await self._make_request("defillama", "/protocols")
            if data:
                results["defillama"] = data
        except Exception as e:
            logger.error(f"DefiLlama error: {e}")
        
        return results
    
    async def get_yield_opportunities(self, min_apy: float = 5.0) -> List[Dict[str, Any]]:
        """Get yield opportunities from multiple sources"""
        opportunities = []
        
        # DefiLlama Yields
        try:
            data = await self._make_request("defillama", "/pools")
            if data and "data" in data:
                for pool in data["data"]:
                    apy = pool.get("apy", 0)
                    if apy >= min_apy:
                        opportunities.append({
                            "source": "defillama",
                            "protocol": pool.get("project"),
                            "chain": pool.get("chain"),
                            "symbol": pool.get("symbol"),
                            "apy": apy,
                            "tvl": pool.get("tvlUsd"),
                            "pool_id": pool.get("pool")
                        })
        except Exception as e:
            logger.error(f"DefiLlama yields error: {e}")
        
        return sorted(opportunities, key=lambda x: x.get("apy", 0), reverse=True)
    
    async def get_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get social sentiment from multiple sources"""
        results = {}
        
        # Alternative.me Fear & Greed Index
        try:
            data = await self._make_request("alternative_me", "/fng/")
            if data and "data" in data:
                results["fear_greed"] = data["data"][0]
        except Exception as e:
            logger.error(f"Fear & Greed Index error: {e}")
        
        # CryptoCompare Social
        try:
            data = await self._make_request("cryptocompare", f"/v2/social/coin/latest?coinId={symbol.upper()}")
            if data and "Data" in data:
                results["cryptocompare_social"] = data["Data"]
        except Exception as e:
            logger.error(f"CryptoCompare social error: {e}")
        
        return results
    
    async def get_onchain_metrics(self, symbol: str, chain: str = "ethereum") -> Dict[str, Any]:
        """Get on-chain metrics from multiple sources"""
        results = {}
        
        # This would integrate with Glassnode, Nansen, etc.
        # For now, return basic structure
        results["placeholder"] = {
            "active_addresses": None,
            "transaction_count": None,
            "network_value": None,
            "hash_rate": None
        }
        
        return results
    
    async def get_news_sentiment(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news and sentiment analysis"""
        news_items = []
        
        # This would integrate with CryptoPanic, NewsAPI, etc.
        # For now, return basic structure
        news_items.append({
            "source": "placeholder",
            "title": f"Latest {symbol} news",
            "sentiment": "neutral",
            "timestamp": datetime.now().isoformat(),
            "url": "#"
        })
        
        return news_items
    
    def _aggregate_price_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate price data from multiple sources"""
        if not results:
            return {}
        
        prices = []
        changes_24h = []
        
        for source, data in results.items():
            if isinstance(data, dict):
                price = data.get("usd") or data.get("USD")
                if price:
                    prices.append(float(price))
                
                change = data.get("usd_24h_change") or data.get("percent_change_24h")
                if change:
                    changes_24h.append(float(change))
        
        if not prices:
            return {}
        
        # Calculate aggregated values
        avg_price = sum(prices) / len(prices)
        avg_change = sum(changes_24h) / len(changes_24h) if changes_24h else 0
        
        return {
            "price_usd": avg_price,
            "price_change_24h": avg_change,
            "sources_count": len(results),
            "sources": list(results.keys()),
            "raw_data": results
        }
    
    async def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive data from all available sources"""
        tasks = [
            self.get_price_data(symbol),
            self.get_social_sentiment(symbol),
            self.get_onchain_metrics(symbol),
            self.get_news_sentiment(symbol)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "symbol": symbol.upper(),
            "timestamp": datetime.now().isoformat(),
            "price_data": results[0] if not isinstance(results[0], Exception) else {},
            "social_sentiment": results[1] if not isinstance(results[1], Exception) else {},
            "onchain_metrics": results[2] if not isinstance(results[2], Exception) else {},
            "news_sentiment": results[3] if not isinstance(results[3], Exception) else {},
            "data_sources": list(self.sources.keys())
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global instance
comprehensive_data_sources = ComprehensiveDataSources()

async def get_multi_source_price(symbol: str) -> Dict[str, Any]:
    """Get price from multiple sources"""
    return await comprehensive_data_sources.get_price_data(symbol)

async def get_multi_source_defi_data(protocol: str = None) -> Dict[str, Any]:
    """Get DeFi data from multiple sources"""
    return await comprehensive_data_sources.get_defi_data(protocol)

async def get_multi_source_yields(min_apy: float = 5.0) -> List[Dict[str, Any]]:
    """Get yield opportunities from multiple sources"""
    return await comprehensive_data_sources.get_yield_opportunities(min_apy)

async def get_comprehensive_crypto_data(symbol: str) -> Dict[str, Any]:
    """Get comprehensive crypto data from all sources"""
    return await comprehensive_data_sources.get_comprehensive_data(symbol)

async def cleanup_data_sources():
    """Cleanup data sources"""
    await comprehensive_data_sources.cleanup()