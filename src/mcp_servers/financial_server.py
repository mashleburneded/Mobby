#!/usr/bin/env python3
"""
MCP Financial Data Server - Real-time crypto market data and DeFi analytics
Provides comprehensive financial data through MCP protocol
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server with proper configuration
mcp = FastMCP(
    name="Financial Data Server",
    instructions="Real-time cryptocurrency market data and DeFi analytics"
)

class FinancialDataProvider:
    """Enhanced financial data provider with multiple sources"""
    
    def __init__(self):
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.defillama_api = "https://api.llama.fi"
        self.session = None
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

# Global provider instance
financial_provider = FinancialDataProvider()

@mcp.tool()
async def get_price_feeds(symbols: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get real-time price feeds for cryptocurrencies
    
    Args:
        symbols: List of crypto symbols (default: BTC, ETH, SOL)
    
    Returns:
        Dict with price data for each symbol
    """
    if not symbols:
        symbols = ["bitcoin", "ethereum", "solana"]
    
    try:
        session = await financial_provider.get_session()
        
        # Convert symbols to CoinGecko IDs
        symbol_map = {
            "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
            "ADA": "cardano", "DOT": "polkadot", "AVAX": "avalanche-2",
            "MATIC": "matic-network", "LINK": "chainlink", "UNI": "uniswap"
        }
        
        # Map input symbols to CoinGecko IDs
        coin_ids = []
        for symbol in symbols:
            if symbol.upper() in symbol_map:
                coin_ids.append(symbol_map[symbol.upper()])
            else:
                coin_ids.append(symbol.lower())
        
        # Fetch price data
        url = f"{financial_provider.coingecko_api}/simple/price"
        params = {
            "ids": ",".join(coin_ids),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_market_cap": "true",
            "include_24hr_vol": "true"
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                
                # Format response
                formatted_data = {}
                for coin_id, price_data in data.items():
                    symbol = coin_id.upper()
                    formatted_data[symbol] = {
                        "price": price_data.get("usd", 0),
                        "change_24h": price_data.get("usd_24h_change", 0),
                        "market_cap": price_data.get("usd_market_cap", 0),
                        "volume_24h": price_data.get("usd_24h_vol", 0)
                    }
                
                return {
                    "success": True,
                    "data": formatted_data,
                    "timestamp": datetime.now().isoformat(),
                    "source": "CoinGecko API"
                }
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status}",
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Error fetching price feeds: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
async def get_defi_protocols(limit: int = 10) -> Dict[str, Any]:
    """
    Get top DeFi protocols by TVL
    
    Args:
        limit: Number of protocols to return (default: 10)
    
    Returns:
        Dict with DeFi protocol data
    """
    try:
        session = await financial_provider.get_session()
        
        url = f"{financial_provider.defillama_api}/protocols"
        
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                
                # Sort by TVL and take top protocols
                sorted_protocols = sorted(data, key=lambda x: x.get("tvl", 0), reverse=True)[:limit]
                
                formatted_protocols = []
                for protocol in sorted_protocols:
                    formatted_protocols.append({
                        "name": protocol.get("name", "Unknown"),
                        "symbol": protocol.get("symbol", ""),
                        "tvl": protocol.get("tvl", 0),
                        "change_1d": protocol.get("change_1d", 0),
                        "change_7d": protocol.get("change_7d", 0),
                        "chain": protocol.get("chain", "Unknown"),
                        "category": protocol.get("category", "Unknown")
                    })
                
                return {
                    "success": True,
                    "data": {
                        "protocols": formatted_protocols,
                        "total_protocols": len(data),
                        "total_tvl": sum(p.get("tvl", 0) for p in data)
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "DeFiLlama API"
                }
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status}",
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Error fetching DeFi protocols: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
async def get_yield_farming_opportunities(min_apy: float = 5.0) -> Dict[str, Any]:
    """
    Get yield farming opportunities with APY above threshold
    
    Args:
        min_apy: Minimum APY percentage (default: 5.0)
    
    Returns:
        Dict with yield farming opportunities
    """
    try:
        session = await financial_provider.get_session()
        
        url = f"{financial_provider.defillama_api}/yields"
        
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                
                # Filter by minimum APY
                opportunities = []
                for pool in data.get("data", []):
                    apy = pool.get("apy", 0)
                    if apy >= min_apy:
                        opportunities.append({
                            "pool": pool.get("pool", "Unknown"),
                            "project": pool.get("project", "Unknown"),
                            "symbol": pool.get("symbol", ""),
                            "apy": apy,
                            "tvl": pool.get("tvlUsd", 0),
                            "chain": pool.get("chain", "Unknown"),
                            "risk_level": "High" if apy > 50 else "Medium" if apy > 20 else "Low"
                        })
                
                # Sort by APY
                opportunities.sort(key=lambda x: x["apy"], reverse=True)
                
                return {
                    "success": True,
                    "data": {
                        "opportunities": opportunities[:20],  # Top 20
                        "total_pools": len(opportunities),
                        "avg_apy": sum(o["apy"] for o in opportunities) / len(opportunities) if opportunities else 0
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "DeFiLlama Yields API"
                }
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status}",
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Error fetching yield farming opportunities: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
async def get_market_overview() -> Dict[str, Any]:
    """
    Get comprehensive market overview
    
    Returns:
        Dict with market overview data
    """
    try:
        session = await financial_provider.get_session()
        
        # Get global market data
        url = f"{financial_provider.coingecko_api}/global"
        
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                global_data = data.get("data", {})
                
                # Get trending coins
                trending_url = f"{financial_provider.coingecko_api}/search/trending"
                async with session.get(trending_url) as trending_response:
                    trending_data = {}
                    if trending_response.status == 200:
                        trending_json = await trending_response.json()
                        trending_data = {
                            "coins": [coin["item"]["name"] for coin in trending_json.get("coins", [])[:5]],
                            "nfts": [nft["name"] for nft in trending_json.get("nfts", [])[:3]]
                        }
                
                return {
                    "success": True,
                    "data": {
                        "total_market_cap": global_data.get("total_market_cap", {}).get("usd", 0),
                        "total_volume": global_data.get("total_volume", {}).get("usd", 0),
                        "market_cap_change_24h": global_data.get("market_cap_change_percentage_24h_usd", 0),
                        "active_cryptocurrencies": global_data.get("active_cryptocurrencies", 0),
                        "markets": global_data.get("markets", 0),
                        "btc_dominance": global_data.get("market_cap_percentage", {}).get("btc", 0),
                        "eth_dominance": global_data.get("market_cap_percentage", {}).get("eth", 0),
                        "trending": trending_data
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "CoinGecko Global API"
                }
            else:
                return {
                    "success": False,
                    "error": f"API request failed with status {response.status}",
                    "timestamp": datetime.now().isoformat()
                }
                
    except Exception as e:
        logger.error(f"Error fetching market overview: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for server monitoring"""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "status": "healthy",
        "server": "Financial Data Server",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

# Server info endpoint  
@mcp.custom_route("/info", methods=["GET"])
async def server_info(request):
    """Server information endpoint"""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "name": "Financial Data Server",
        "description": "Real-time cryptocurrency market data and DeFi analytics",
        "version": "1.0.0",
        "tools": [
            "get_price_feeds",
            "get_defi_protocols", 
            "get_yield_farming_opportunities",
            "get_market_overview"
        ],
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })

# Cleanup function (called manually if needed)
async def cleanup():
    """Cleanup resources on server shutdown"""
    await financial_provider.close()
    logger.info("Financial Data Server shutdown complete")

async def main():
    """Main function to start the server"""
    try:
        port = int(os.getenv("PORT", 8001))
        host = os.getenv("HOST", "0.0.0.0")
        
        logger.info(f"🚀 Starting Financial Data Server on {host}:{port}")
        logger.info("📊 Available tools: get_price_feeds, get_defi_protocols, get_yield_farming_opportunities, get_market_overview")
        
        # Run the server with HTTP transport
        await mcp.run_http_async(transport="streamable-http", host=host, port=port)
        
    except Exception as e:
        logger.error(f"❌ Failed to start Financial Data Server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())