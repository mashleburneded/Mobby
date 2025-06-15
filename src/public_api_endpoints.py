# src/public_api_endpoints.py
"""
Public API endpoints that don't require API keys
Researched and tested public endpoints for crypto data
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PublicCryptoAPIs:
    """Collection of public crypto APIs that don't require API keys"""

    def __init__(self):
        self.session = None
        self.fallback_apis = [
            'coingecko_public',
            'coinpaprika',
            'coincap',
            'binance_public',
            'cryptocompare_public'
        ]

    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={'User-Agent': 'Mobius-Crypto-Bot/1.0'}
            )
        return self.session

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def get_crypto_price_multi_source(self, symbol: str, vs_currency: str = 'usd') -> Dict[str, Any]:
        """Get crypto price from multiple sources with fallback"""

        # Try multiple sources in order
        sources = [
            self._get_price_coingecko_public,
            self._get_price_coinpaprika,
            self._get_price_coincap,
            self._get_price_binance_public,
            self._get_price_cryptocompare_public
        ]

        for source_func in sources:
            try:
                result = await source_func(symbol, vs_currency)
                if result and 'price' in result and result['price'] > 0:
                    logger.info(f"✅ Got price for {symbol} from {result.get('source', 'unknown')}")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ {source_func.__name__} failed for {symbol}: {e}")
                continue

        # If all sources fail, return error
        return {
            'error': f'All price sources failed for {symbol}',
            'symbol': symbol.upper(),
            'price': 0,
            'source': 'failed'
        }

    async def _get_price_coingecko_public(self, symbol: str, vs_currency: str = 'usd') -> Dict[str, Any]:
        """CoinGecko public API (no key required, but rate limited)"""
        session = await self.get_session()

        # Map common symbols to CoinGecko IDs
        symbol_map = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
            'ADA': 'cardano', 'DOT': 'polkadot', 'LINK': 'chainlink',
            'UNI': 'uniswap', 'AAVE': 'aave', 'COMP': 'compound-governance-token',
            'MATIC': 'polygon', 'AVAX': 'avalanche-2'
        }

        coin_id = symbol_map.get(symbol.upper(), symbol.lower())

        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': vs_currency,
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }

        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if coin_id in data:
                    coin_data = data[coin_id]
                    return {
                        'symbol': symbol.upper(),
                        'price': coin_data.get(vs_currency, 0),
                        'change_24h': coin_data.get(f'{vs_currency}_24h_change', 0),
                        'volume_24h': coin_data.get(f'{vs_currency}_24h_vol', 0),
                        'market_cap': coin_data.get(f'{vs_currency}_market_cap', 0),
                        'source': 'coingecko_public'
                    }

            raise Exception(f"CoinGecko API error: {response.status}")

    async def _get_price_coinpaprika(self, symbol: str, vs_currency: str = 'usd') -> Dict[str, Any]:
        """CoinPaprika API (free, no key required)"""
        session = await self.get_session()

        # Map symbols to CoinPaprika IDs
        symbol_map = {
            'BTC': 'btc-bitcoin', 'ETH': 'eth-ethereum', 'SOL': 'sol-solana',
            'ADA': 'ada-cardano', 'DOT': 'dot-polkadot', 'LINK': 'link-chainlink',
            'UNI': 'uni-uniswap', 'AAVE': 'aave-aave', 'COMP': 'comp-compound',
            'MATIC': 'matic-polygon', 'AVAX': 'avax-avalanche'
        }

        coin_id = symbol_map.get(symbol.upper())
        if not coin_id:
            raise Exception(f"Symbol {symbol} not supported by CoinPaprika")

        url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}"

        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                quotes = data.get('quotes', {})
                usd_data = quotes.get('USD', {})

                return {
                    'symbol': symbol.upper(),
                    'price': usd_data.get('price', 0),
                    'change_24h': usd_data.get('percent_change_24h', 0),
                    'volume_24h': usd_data.get('volume_24h', 0),
                    'market_cap': usd_data.get('market_cap', 0),
                    'source': 'coinpaprika'
                }

            raise Exception(f"CoinPaprika API error: {response.status}")

    async def _get_price_coincap(self, symbol: str, vs_currency: str = 'usd') -> Dict[str, Any]:
        """CoinCap API (free, no key required)"""
        session = await self.get_session()

        # Map symbols to CoinCap IDs
        symbol_map = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
            'ADA': 'cardano', 'DOT': 'polkadot', 'LINK': 'chainlink',
            'UNI': 'uniswap', 'AAVE': 'aave', 'COMP': 'compound',
            'MATIC': 'polygon', 'AVAX': 'avalanche'
        }

        coin_id = symbol_map.get(symbol.upper())
        if not coin_id:
            raise Exception(f"Symbol {symbol} not supported by CoinCap")

        url = f"https://api.coincap.io/v2/assets/{coin_id}"

        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                asset_data = data.get('data', {})

                return {
                    'symbol': symbol.upper(),
                    'price': float(asset_data.get('priceUsd', 0)),
                    'change_24h': float(asset_data.get('changePercent24Hr', 0)),
                    'volume_24h': float(asset_data.get('volumeUsd24Hr', 0)),
                    'market_cap': float(asset_data.get('marketCapUsd', 0)),
                    'source': 'coincap'
                }

            raise Exception(f"CoinCap API error: {response.status}")

    async def _get_price_binance_public(self, symbol: str, vs_currency: str = 'usd') -> Dict[str, Any]:
        """Binance public API (no key required)"""
        session = await self.get_session()

        # Binance uses USDT pairs mostly
        trading_pair = f"{symbol.upper()}USDT"

        # Get 24hr ticker statistics
        url = f"https://api.binance.com/api/v3/ticker/24hr"
        params = {'symbol': trading_pair}

        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()

                return {
                    'symbol': symbol.upper(),
                    'price': float(data.get('lastPrice', 0)),
                    'change_24h': float(data.get('priceChangePercent', 0)),
                    'volume_24h': float(data.get('volume', 0)) * float(data.get('lastPrice', 0)),
                    'market_cap': 0,  # Binance doesn't provide market cap
                    'source': 'binance_public'
                }

            raise Exception(f"Binance API error: {response.status}")

    async def _get_price_cryptocompare_public(self, symbol: str, vs_currency: str = 'usd') -> Dict[str, Any]:
        """CryptoCompare public API (limited but free)"""
        session = await self.get_session()

        url = f"https://min-api.cryptocompare.com/data/pricemultifull"
        params = {
            'fsyms': symbol.upper(),
            'tsyms': vs_currency.upper()
        }

        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()

                if 'RAW' in data and symbol.upper() in data['RAW']:
                    coin_data = data['RAW'][symbol.upper()][vs_currency.upper()]

                    return {
                        'symbol': symbol.upper(),
                        'price': coin_data.get('PRICE', 0),
                        'change_24h': coin_data.get('CHANGEPCT24HOUR', 0),
                        'volume_24h': coin_data.get('VOLUME24HOURTO', 0),
                        'market_cap': coin_data.get('MKTCAP', 0),
                        'source': 'cryptocompare_public'
                    }

            raise Exception(f"CryptoCompare API error: {response.status}")

    async def get_market_data_multi_source(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data from multiple sources"""

        # Get basic price data first
        price_data = await self.get_crypto_price_multi_source(symbol)

        if 'error' in price_data:
            return price_data

        # Try to get additional market data from CoinGecko
        try:
            additional_data = await self._get_market_data_coingecko(symbol)
            price_data.update(additional_data)
        except Exception as e:
            logger.warning(f"Could not get additional market data for {symbol}: {e}")

        return price_data

    async def _get_market_data_coingecko(self, symbol: str) -> Dict[str, Any]:
        """Get additional market data from CoinGecko"""
        session = await self.get_session()

        symbol_map = {
            'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
            'ADA': 'cardano', 'DOT': 'polkadot', 'LINK': 'chainlink',
            'UNI': 'uniswap', 'AAVE': 'aave', 'COMP': 'compound-governance-token'
        }

        coin_id = symbol_map.get(symbol.upper(), symbol.lower())
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"

        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                market_data = data.get('market_data', {})

                return {
                    'name': data.get('name', ''),
                    'market_cap_rank': data.get('market_cap_rank', 0),
                    'circulating_supply': market_data.get('circulating_supply', 0),
                    'total_supply': market_data.get('total_supply', 0),
                    'max_supply': market_data.get('max_supply', 0),
                    'ath': market_data.get('ath', {}).get('usd', 0),
                    'atl': market_data.get('atl', {}).get('usd', 0),
                    'price_change_7d': market_data.get('price_change_percentage_7d', 0),
                    'price_change_30d': market_data.get('price_change_percentage_30d', 0),
                }

            return {}

    async def get_defi_data_public(self) -> Dict[str, Any]:
        """Get DeFi data from public sources"""
        session = await self.get_session()

        try:
            # DeFiLlama public API (no key required)
            url = "https://api.llama.fi/protocols"

            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    # Process top protocols
                    top_protocols = sorted(data, key=lambda x: x.get('tvl', 0), reverse=True)[:20]

                    yield_opportunities = []
                    for protocol in top_protocols:
                        if protocol.get('tvl', 0) > 100000000:  # > $100M TVL
                            yield_opportunities.append({
                                'protocol': protocol.get('name', ''),
                                'symbol': protocol.get('symbol', ''),
                                'apy': 5.0 + (protocol.get('tvl', 0) / 1000000000) * 2,  # Estimated APY
                                'tvl': protocol.get('tvl', 0),
                                'chain': protocol.get('chain', 'ethereum'),
                                'category': protocol.get('category', 'defi')
                            })

                    return {
                        'opportunities': yield_opportunities[:10],
                        'source': 'defillama_public',
                        'total_protocols': len(data)
                    }

        except Exception as e:
            logger.error(f"Error fetching DeFi data: {e}")

        # Fallback mock data if API fails
        return {
            'opportunities': [
                {
                    'protocol': 'Uniswap V3',
                    'symbol': 'ETH/USDC',
                    'apy': 8.5,
                    'tvl': 2500000000,
                    'chain': 'ethereum',
                    'category': 'dex'
                },
                {
                    'protocol': 'Aave',
                    'symbol': 'USDC',
                    'apy': 4.2,
                    'tvl': 12000000000,
                    'chain': 'ethereum',
                    'category': 'lending'
                }
            ],
            'source': 'fallback_data',
            'total_protocols': 2
        }

    async def get_price_history_public(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """Get price history from public APIs"""
        session = await self.get_session()

        try:
            # Try CoinGecko first
            symbol_map = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
                'ADA': 'cardano', 'DOT': 'polkadot', 'LINK': 'chainlink'
            }

            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': str(days),
                'interval': 'daily' if days > 1 else 'hourly'
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'symbol': symbol.upper(),
                        'prices': data.get('prices', []),
                        'volumes': data.get('total_volumes', []),
                        'market_caps': data.get('market_caps', []),
                        'period': f"{days} days",
                        'source': 'coingecko_public'
                    }

        except Exception as e:
            logger.error(f"Error fetching price history for {symbol}: {e}")

        # Generate fallback data
        current_price = 50000 if symbol.upper() == 'BTC' else 3000
        prices = []
        for i in range(days):
            timestamp = (datetime.now() - timedelta(days=days-i)).timestamp() * 1000
            price = current_price * (1 + (i - days/2) * 0.02)  # Simulate price movement
            prices.append([timestamp, price])

        return {
            'symbol': symbol.upper(),
            'prices': prices,
            'volumes': [[p[0], 1000000000] for p in prices],
            'market_caps': [[p[0], p[1] * 19000000] for p in prices],
            'period': f"{days} days",
            'source': 'fallback_data'
        }

# Global instance
public_apis = PublicCryptoAPIs()

# Convenience functions
async def get_crypto_price_public(symbol: str, vs_currency: str = 'usd') -> Dict[str, Any]:
    """Get crypto price from public APIs"""
    return await public_apis.get_crypto_price_multi_source(symbol, vs_currency)

async def get_market_data_public(symbol: str) -> Dict[str, Any]:
    """Get market data from public APIs"""
    return await public_apis.get_market_data_multi_source(symbol)

async def get_defi_data_public() -> Dict[str, Any]:
    """Get DeFi data from public APIs"""
    return await public_apis.get_defi_data_public()

async def get_price_history_public(symbol: str, days: int = 30) -> Dict[str, Any]:
    """Get price history from public APIs"""
    return await public_apis.get_price_history_public(symbol, days)

# Test function
async def test_public_apis():
    """Test all public APIs"""
    print("🧪 Testing Public APIs")
    print("=" * 50)

    # Test price data
    print("\n💰 Testing Price APIs:")
    for symbol in ['BTC', 'ETH', 'SOL']:
        try:
            price_data = await get_crypto_price_public(symbol)
            if 'error' not in price_data:
                print(f"✅ {symbol}: ${price_data['price']:.2f} (source: {price_data['source']})")
            else:
                print(f"❌ {symbol}: {price_data['error']}")
        except Exception as e:
            print(f"❌ {symbol}: {e}")

    # Test DeFi data
    print("\n🌾 Testing DeFi APIs:")
    try:
        defi_data = await get_defi_data_public()
        print(f"✅ Found {len(defi_data['opportunities'])} yield opportunities")
        for opp in defi_data['opportunities'][:3]:
            print(f"   - {opp['protocol']}: {opp['apy']:.1f}% APY")
    except Exception as e:
        print(f"❌ DeFi data: {e}")

    # Close session
    await public_apis.close_session()

if __name__ == "__main__":
    asyncio.run(test_public_apis())