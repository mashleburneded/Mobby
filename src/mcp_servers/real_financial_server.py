#!/usr/bin/env python3
"""
Real MCP Financial Server - Production-grade financial data server
Fully compliant with Model Context Protocol standards
"""

import asyncio
import logging
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# MCP imports
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
app = FastMCP("Mobius Financial Data Server")

class RealFinancialDataProvider:
    """Production-grade financial data provider"""
    
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.defillama_base = "https://api.llama.fi"
        self.session = None
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def rate_limit(self):
        """Implement rate limiting"""
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = datetime.now().timestamp()
    
    async def make_request(self, url: str, params: Dict = None) -> Dict[str, Any]:
        """Make rate-limited HTTP request"""
        await self.rate_limit()
        session = await self.get_session()
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status} - {url}")
                    return {"error": f"API request failed with status {response.status}"}
        except Exception as e:
            logger.error(f"Request error: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global provider instance
provider = RealFinancialDataProvider()

@app.tool()
async def get_crypto_prices(symbols: List[str] = None) -> Dict[str, Any]:
    """
    Get real-time cryptocurrency prices from CoinGecko API
    
    Args:
        symbols: List of cryptocurrency symbols (e.g., ['bitcoin', 'ethereum'])
    
    Returns:
        Dictionary containing price data for requested cryptocurrencies
    """
    try:
        if not symbols:
            symbols = ['bitcoin', 'ethereum', 'cardano', 'polkadot', 'chainlink']
        
        # Convert common symbols to CoinGecko IDs
        symbol_map = {
            'btc': 'bitcoin',
            'eth': 'ethereum', 
            'ada': 'cardano',
            'dot': 'polkadot',
            'link': 'chainlink',
            'matic': 'matic-network',
            'sol': 'solana',
            'avax': 'avalanche-2'
        }
        
        # Map symbols to CoinGecko IDs
        coin_ids = []
        for symbol in symbols:
            symbol_lower = symbol.lower()
            if symbol_lower in symbol_map:
                coin_ids.append(symbol_map[symbol_lower])
            else:
                coin_ids.append(symbol_lower)
        
        # Make API request
        url = f"{provider.coingecko_base}/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_24hr_vol': 'true',
            'include_market_cap': 'true'
        }
        
        data = await provider.make_request(url, params)
        
        if "error" in data:
            return {"success": False, "error": data["error"]}
        
        # Format response
        formatted_data = {}
        for coin_id, price_data in data.items():
            formatted_data[coin_id] = {
                "price_usd": price_data.get("usd", 0),
                "change_24h": price_data.get("usd_24h_change", 0),
                "volume_24h": price_data.get("usd_24h_vol", 0),
                "market_cap": price_data.get("usd_market_cap", 0),
                "timestamp": datetime.now().isoformat()
            }
        
        return {
            "success": True,
            "data": formatted_data,
            "source": "CoinGecko API",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting crypto prices: {e}")
        return {"success": False, "error": str(e)}

@app.tool()
async def get_market_data(symbol: str = "bitcoin") -> Dict[str, Any]:
    """
    Get comprehensive market data for a cryptocurrency
    
    Args:
        symbol: Cryptocurrency symbol or ID
    
    Returns:
        Detailed market data including price history, volume, etc.
    """
    try:
        # Convert symbol to CoinGecko ID if needed
        symbol_map = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'ada': 'cardano',
            'dot': 'polkadot',
            'link': 'chainlink'
        }
        
        coin_id = symbol_map.get(symbol.lower(), symbol.lower())
        
        # Get detailed coin data
        url = f"{provider.coingecko_base}/coins/{coin_id}"
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false'
        }
        
        data = await provider.make_request(url, params)
        
        if "error" in data:
            return {"success": False, "error": data["error"]}
        
        market_data = data.get("market_data", {})
        
        return {
            "success": True,
            "data": {
                "name": data.get("name"),
                "symbol": data.get("symbol", "").upper(),
                "current_price": market_data.get("current_price", {}).get("usd", 0),
                "market_cap": market_data.get("market_cap", {}).get("usd", 0),
                "total_volume": market_data.get("total_volume", {}).get("usd", 0),
                "price_change_24h": market_data.get("price_change_24h", 0),
                "price_change_percentage_24h": market_data.get("price_change_percentage_24h", 0),
                "market_cap_rank": market_data.get("market_cap_rank", 0),
                "circulating_supply": market_data.get("circulating_supply", 0),
                "total_supply": market_data.get("total_supply", 0),
                "ath": market_data.get("ath", {}).get("usd", 0),
                "atl": market_data.get("atl", {}).get("usd", 0),
                "last_updated": market_data.get("last_updated")
            },
            "source": "CoinGecko API",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return {"success": False, "error": str(e)}

@app.tool()
async def get_defi_protocols() -> Dict[str, Any]:
    """
    Get DeFi protocol data from DefiLlama
    
    Returns:
        List of top DeFi protocols with TVL data
    """
    try:
        url = f"{provider.defillama_base}/protocols"
        data = await provider.make_request(url)
        
        if "error" in data:
            return {"success": False, "error": data["error"]}
        
        # Get top 20 protocols by TVL
        protocols = sorted(data, key=lambda x: x.get("tvl", 0), reverse=True)[:20]
        
        formatted_protocols = []
        for protocol in protocols:
            formatted_protocols.append({
                "name": protocol.get("name"),
                "symbol": protocol.get("symbol"),
                "tvl": protocol.get("tvl", 0),
                "change_1d": protocol.get("change_1d", 0),
                "change_7d": protocol.get("change_7d", 0),
                "category": protocol.get("category"),
                "chains": protocol.get("chains", []),
                "url": protocol.get("url")
            })
        
        return {
            "success": True,
            "data": formatted_protocols,
            "source": "DefiLlama API",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting DeFi protocols: {e}")
        return {"success": False, "error": str(e)}

@app.tool()
async def get_trending_coins() -> Dict[str, Any]:
    """
    Get trending cryptocurrencies
    
    Returns:
        List of currently trending cryptocurrencies
    """
    try:
        url = f"{provider.coingecko_base}/search/trending"
        data = await provider.make_request(url)
        
        if "error" in data:
            return {"success": False, "error": data["error"]}
        
        trending_coins = []
        for coin_data in data.get("coins", []):
            coin = coin_data.get("item", {})
            trending_coins.append({
                "name": coin.get("name"),
                "symbol": coin.get("symbol"),
                "market_cap_rank": coin.get("market_cap_rank"),
                "price_btc": coin.get("price_btc"),
                "score": coin.get("score")
            })
        
        return {
            "success": True,
            "data": trending_coins,
            "source": "CoinGecko API",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting trending coins: {e}")
        return {"success": False, "error": str(e)}

@app.tool()
async def get_market_overview() -> Dict[str, Any]:
    """
    Get overall cryptocurrency market overview
    
    Returns:
        Global market statistics and overview
    """
    try:
        url = f"{provider.coingecko_base}/global"
        data = await provider.make_request(url)
        
        if "error" in data:
            return {"success": False, "error": data["error"]}
        
        global_data = data.get("data", {})
        
        return {
            "success": True,
            "data": {
                "total_market_cap": global_data.get("total_market_cap", {}).get("usd", 0),
                "total_volume": global_data.get("total_volume", {}).get("usd", 0),
                "market_cap_percentage": global_data.get("market_cap_percentage", {}),
                "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
                "upcoming_icos": global_data.get("upcoming_icos", 0),
                "ongoing_icos": global_data.get("ongoing_icos", 0),
                "ended_icos": global_data.get("ended_icos", 0),
                "markets": global_data.get("markets", 0),
                "market_cap_change_percentage_24h": global_data.get("market_cap_change_percentage_24h_usd", 0)
            },
            "source": "CoinGecko API",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        return {"success": False, "error": str(e)}

@app.tool()
async def analyze_price_movement(symbol: str = "bitcoin", days: int = 7) -> Dict[str, Any]:
    """
    Analyze price movement and provide basic technical analysis
    
    Args:
        symbol: Cryptocurrency symbol
        days: Number of days to analyze (1, 7, 14, 30, 90, 180, 365)
    
    Returns:
        Price movement analysis with basic indicators
    """
    try:
        # Convert symbol to CoinGecko ID
        symbol_map = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'ada': 'cardano',
            'dot': 'polkadot',
            'link': 'chainlink'
        }
        
        coin_id = symbol_map.get(symbol.lower(), symbol.lower())
        
        # Get historical price data
        url = f"{provider.coingecko_base}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': str(days),
            'interval': 'daily' if days > 1 else 'hourly'
        }
        
        data = await provider.make_request(url, params)
        
        if "error" in data:
            return {"success": False, "error": data["error"]}
        
        prices = data.get("prices", [])
        if not prices:
            return {"success": False, "error": "No price data available"}
        
        # Calculate basic indicators
        price_values = [price[1] for price in prices]
        current_price = price_values[-1]
        start_price = price_values[0]
        
        # Price change
        price_change = current_price - start_price
        price_change_percentage = (price_change / start_price) * 100
        
        # Simple moving averages
        if len(price_values) >= 7:
            sma_7 = sum(price_values[-7:]) / 7
        else:
            sma_7 = current_price
            
        if len(price_values) >= 14:
            sma_14 = sum(price_values[-14:]) / 14
        else:
            sma_14 = current_price
        
        # High and low
        high_price = max(price_values)
        low_price = min(price_values)
        
        # Volatility (standard deviation)
        if len(price_values) > 1:
            mean_price = sum(price_values) / len(price_values)
            variance = sum((price - mean_price) ** 2 for price in price_values) / len(price_values)
            volatility = variance ** 0.5
        else:
            volatility = 0
        
        return {
            "success": True,
            "data": {
                "symbol": symbol.upper(),
                "period_days": days,
                "current_price": current_price,
                "start_price": start_price,
                "price_change": price_change,
                "price_change_percentage": price_change_percentage,
                "high_price": high_price,
                "low_price": low_price,
                "volatility": volatility,
                "sma_7": sma_7,
                "sma_14": sma_14,
                "trend": "bullish" if price_change > 0 else "bearish",
                "data_points": len(price_values)
            },
            "source": "CoinGecko API",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing price movement: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import argparse
    import uvicorn
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Real MCP Financial Server")
    parser.add_argument("--port", type=int, default=8011, help="Port to run the server on")
    args = parser.parse_args()
    
    # Server startup
    logger.info("🚀 Real MCP Financial Server starting up...")
    logger.info("📊 Available tools: get_crypto_prices, get_market_data, get_defi_protocols, get_trending_coins, get_market_overview, analyze_price_movement")
    
    # Run the server using uvicorn
    logger.info(f"🏦 Starting REAL MCP Financial Server on port {args.port}")
    
    try:
        # Create a simple HTTP wrapper around the MCP tools
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        from typing import Any, Dict
        import uvicorn
        
        # Create FastAPI app
        http_app = FastAPI(title="Financial Data Server", version="1.0.0")
        
        class ToolRequest(BaseModel):
            arguments: Dict[str, Any] = {}
        
        class ToolResponse(BaseModel):
            success: bool
            data: Any = None
            error: str = None
            source: str = "Financial Data Server"
        
        @http_app.get("/health")
        async def health():
            return {"status": "healthy", "server": "Financial Data Server", "timestamp": datetime.now().isoformat(), "version": "1.0.0"}
        
        @http_app.get("/tools")
        async def list_tools():
            return {
                "tools": [
                    "get_crypto_prices",
                    "get_market_data", 
                    "get_defi_protocols",
                    "get_trending_coins",
                    "get_market_overview",
                    "analyze_price_movement"
                ]
            }
        
        @http_app.post("/tools/get_crypto_prices")
        async def api_get_crypto_prices(request: ToolRequest):
            try:
                result = await get_crypto_prices(**request.arguments)
                return ToolResponse(success=True, data=result)
            except Exception as e:
                return ToolResponse(success=False, error=str(e))
        
        @http_app.post("/tools/get_market_data")
        async def api_get_market_data(request: ToolRequest):
            try:
                result = await get_market_data(**request.arguments)
                return ToolResponse(success=True, data=result)
            except Exception as e:
                return ToolResponse(success=False, error=str(e))
        
        @http_app.post("/tools/get_defi_protocols")
        async def api_get_defi_protocols(request: ToolRequest):
            try:
                result = await get_defi_protocols(**request.arguments)
                return ToolResponse(success=True, data=result)
            except Exception as e:
                return ToolResponse(success=False, error=str(e))
        
        @http_app.post("/tools/get_trending_coins")
        async def api_get_trending_coins(request: ToolRequest):
            try:
                result = await get_trending_coins(**request.arguments)
                return ToolResponse(success=True, data=result)
            except Exception as e:
                return ToolResponse(success=False, error=str(e))
        
        @http_app.post("/tools/get_market_overview")
        async def api_get_market_overview(request: ToolRequest):
            try:
                result = await get_market_overview(**request.arguments)
                return ToolResponse(success=True, data=result)
            except Exception as e:
                return ToolResponse(success=False, error=str(e))
        
        @http_app.post("/tools/analyze_price_movement")
        async def api_analyze_price_movement(request: ToolRequest):
            try:
                result = await analyze_price_movement(**request.arguments)
                return ToolResponse(success=True, data=result)
            except Exception as e:
                return ToolResponse(success=False, error=str(e))
        
        # Run the HTTP server
        uvicorn.run(http_app, host="0.0.0.0", port=args.port, log_level="info")
    except KeyboardInterrupt:
        logger.info("🛑 Real MCP Financial Server shutting down...")
    finally:
        # Cleanup
        import asyncio
        asyncio.run(provider.close())