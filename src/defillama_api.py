# src/defillama_api.py
"""
DeFiLlama API Integration for Möbius AI Assistant
Provides comprehensive DeFi data and analytics
"""
import logging
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class DeFiLlamaAPI:
    """DeFiLlama API client for DeFi data"""
    
    BASE_URL = "https://api.llama.fi"
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request to DeFiLlama"""
        try:
            session = await self._get_session()
            url = f"{self.BASE_URL}{endpoint}"
            
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"DeFiLlama API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error making DeFiLlama request: {e}")
            return None
    
    async def get_protocols(self) -> Optional[List[Dict]]:
        """Get all DeFi protocols"""
        return await self._make_request("/protocols")
    
    async def get_protocol(self, protocol_slug: str) -> Optional[Dict]:
        """Get specific protocol data"""
        return await self._make_request(f"/protocol/{protocol_slug}")
    
    async def get_tvl_chart(self, protocol_slug: str) -> Optional[List[Dict]]:
        """Get TVL chart data for protocol"""
        return await self._make_request(f"/protocol/{protocol_slug}")
    
    async def get_chains(self) -> Optional[List[Dict]]:
        """Get all blockchain chains"""
        return await self._make_request("/chains")
    
    async def get_chain_tvl(self, chain: str) -> Optional[Dict]:
        """Get TVL for specific chain"""
        return await self._make_request(f"/chains/{chain}")
    
    async def get_yields(self, chain: str = None) -> Optional[List[Dict]]:
        """Get yield farming opportunities"""
        try:
            # Use the correct yields API endpoint
            endpoint = "/yields/pools"
            params = {}
            if chain:
                params["chain"] = chain
            return await self._make_request(endpoint, params)
        except Exception as e:
            logger.error(f"Error getting yields: {e}")
            return []
    
    async def get_pools(self, protocol: str = None) -> Optional[List[Dict]]:
        """Get liquidity pools"""
        try:
            endpoint = "/yields/pools"
            params = {}
            if protocol:
                params["project"] = protocol
            return await self._make_request(endpoint, params)
        except Exception as e:
            logger.error(f"Error getting pools: {e}")
            return []
    
    async def get_stablecoins(self) -> Optional[List[Dict]]:
        """Get stablecoin data"""
        try:
            # Use the correct stablecoins endpoint
            return await self._make_request("/stablecoins?includePrices=true")
        except Exception as e:
            logger.error(f"Error getting stablecoins: {e}")
            return []
    
    async def get_stablecoin_chart(self, stablecoin_id: int) -> Optional[List[Dict]]:
        """Get stablecoin chart data"""
        try:
            return await self._make_request(f"/stablecoincharts/all?stablecoin={stablecoin_id}")
        except Exception as e:
            logger.error(f"Error getting stablecoin chart: {e}")
            return []
    
    async def get_fees(self, protocol: str = None) -> Optional[Dict]:
        """Get protocol fees"""
        try:
            if protocol:
                return await self._make_request(f"/summary/fees/{protocol}")
            return await self._make_request("/overview/fees")
        except Exception as e:
            logger.error(f"Error getting fees: {e}")
            return {}
    
    async def get_volumes(self, protocol: str = None) -> Optional[Dict]:
        """Get protocol volumes"""
        try:
            if protocol:
                return await self._make_request(f"/summary/dexs/{protocol}")
            return await self._make_request("/overview/dexs")
        except Exception as e:
            logger.error(f"Error getting volumes: {e}")
            return {}
    
    async def get_bridges(self) -> Optional[List[Dict]]:
        """Get bridge data"""
        try:
            # Use the correct bridges endpoint
            return await self._make_request("/bridges2")
        except Exception as e:
            logger.error(f"Error getting bridges: {e}")
            return []
    
    async def get_bridge_volume(self, bridge_id: int) -> Optional[Dict]:
        """Get bridge volume data"""
        try:
            return await self._make_request(f"/bridgevolume/{bridge_id}")
        except Exception as e:
            logger.error(f"Error getting bridge volume: {e}")
            return {}
    
    async def search_protocols(self, query: str) -> Optional[List[Dict]]:
        """Search for protocols by name"""
        protocols = await self.get_protocols()
        if not protocols:
            return None
        
        query_lower = query.lower()
        matches = []
        
        for protocol in protocols:
            name = protocol.get('name', '').lower()
            symbol = protocol.get('symbol', '').lower()
            
            if query_lower in name or query_lower in symbol:
                matches.append(protocol)
        
        return matches[:10]  # Return top 10 matches
    
    async def get_top_protocols(self, limit: int = 10) -> Optional[List[Dict]]:
        """Get top protocols by TVL"""
        protocols = await self.get_protocols()
        if not protocols:
            return None
        
        # Sort by TVL and return top N (handle None values)
        sorted_protocols = sorted(
            protocols, 
            key=lambda x: x.get('tvl', 0) or 0, 
            reverse=True
        )
        return sorted_protocols[:limit]
    
    async def get_protocol_summary(self, protocol_slug: str) -> Optional[str]:
        """Get formatted protocol summary"""
        protocol = await self.get_protocol(protocol_slug)
        if not protocol:
            return None
        
        name = protocol.get('name', 'Unknown')
        tvl = protocol.get('tvl', 0)
        change_1d = protocol.get('change_1d', 0)
        change_7d = protocol.get('change_7d', 0)
        category = protocol.get('category', 'Unknown')
        chains = protocol.get('chains', [])
        
        summary = f"📊 **{name}** ({category})\n\n"
        
        # Handle TVL which might be a list or number
        if isinstance(tvl, list):
            tvl_value = tvl[0] if tvl else 0
        else:
            tvl_value = tvl or 0
            
        # Handle change values which might be lists or numbers
        if isinstance(change_1d, list):
            change_1d_value = change_1d[0] if change_1d else 0
        else:
            change_1d_value = change_1d or 0
            
        if isinstance(change_7d, list):
            change_7d_value = change_7d[0] if change_7d else 0
        else:
            change_7d_value = change_7d or 0
        
        summary += f"💰 **TVL:** ${tvl_value:,.2f}\n"
        summary += f"📈 **24h Change:** {change_1d_value:+.2f}%\n"
        summary += f"📊 **7d Change:** {change_7d_value:+.2f}%\n"
        
        if chains and isinstance(chains, list):
            summary += f"🌐 **Chains:** {', '.join(str(chain) for chain in chains[:5])}\n"
        
        if len(chains) > 5:
            summary += f"... and {len(chains) - 5} more\n"
        
        return summary
    
    async def get_yield_opportunities(self, min_apy: float = 5.0, limit: int = 10) -> Optional[str]:
        """Get formatted yield opportunities"""
        yields = await self.get_yields()
        if not yields:
            return None
        
        # Filter by minimum APY and sort by APY
        filtered_yields = [y for y in yields if y.get('apy', 0) >= min_apy]
        sorted_yields = sorted(filtered_yields, key=lambda x: x.get('apy', 0), reverse=True)
        
        if not sorted_yields:
            return f"No yield opportunities found with APY >= {min_apy}%"
        
        summary = f"🌾 **Top Yield Opportunities (APY >= {min_apy}%)**\n\n"
        
        for i, pool in enumerate(sorted_yields[:limit], 1):
            project = pool.get('project', 'Unknown')
            symbol = pool.get('symbol', 'Unknown')
            apy = pool.get('apy', 0)
            tvl = pool.get('tvlUsd', 0)
            chain = pool.get('chain', 'Unknown')
            
            summary += f"{i}. **{project}** - {symbol}\n"
            summary += f"   💰 APY: {apy:.2f}% | TVL: ${tvl:,.0f} | {chain}\n\n"
        
        return summary
    
    async def get_chain_comparison(self, chains: List[str]) -> Optional[str]:
        """Compare multiple chains"""
        if not chains:
            return None
        
        chain_data = {}
        for chain in chains:
            data = await self.get_chain_tvl(chain)
            if data:
                chain_data[chain] = data
        
        if not chain_data:
            return "No data found for the specified chains."
        
        summary = "🌐 **Chain Comparison**\n\n"
        
        for chain, data in chain_data.items():
            tvl = data.get('tvl', 0)
            change_1d = data.get('change_1d', 0)
            change_7d = data.get('change_7d', 0)
            
            summary += f"**{chain.title()}**\n"
            summary += f"💰 TVL: ${tvl:,.2f}\n"
            summary += f"📈 24h: {change_1d:+.2f}% | 7d: {change_7d:+.2f}%\n\n"
        
        return summary
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None

# Global instance
defillama_api = DeFiLlamaAPI()

async def get_protocol_data(protocol_slug: str) -> Optional[str]:
    """Get formatted protocol data"""
    return await defillama_api.get_protocol_summary(protocol_slug)

async def search_defi_protocols(query: str) -> Optional[str]:
    """Search and format DeFi protocols"""
    matches = await defillama_api.search_protocols(query)
    if not matches:
        return f"No protocols found matching '{query}'"
    
    summary = f"🔍 **Search Results for '{query}'**\n\n"
    
    for i, protocol in enumerate(matches[:5], 1):
        name = protocol.get('name', 'Unknown')
        tvl = protocol.get('tvl', 0)
        category = protocol.get('category', 'Unknown')
        slug = protocol.get('slug', '')
        
        summary += f"{i}. **{name}** ({category})\n"
        summary += f"   💰 TVL: ${tvl or 0:,.2f}\n"
        summary += f"   🔗 Use: `/llama protocol {slug}`\n\n"
    
    return summary

async def get_top_defi_protocols(limit: int = 10) -> Optional[str]:
    """Get top DeFi protocols by TVL"""
    protocols = await defillama_api.get_top_protocols(limit)
    if not protocols:
        return "Unable to fetch top protocols"
    
    summary = f"🏆 **Top {limit} DeFi Protocols by TVL**\n\n"
    
    for i, protocol in enumerate(protocols, 1):
        name = protocol.get('name', 'Unknown')
        tvl = protocol.get('tvl', 0)
        change_1d = protocol.get('change_1d', 0)
        category = protocol.get('category', 'Unknown')
        
        summary += f"{i}. **{name}** ({category})\n"
        summary += f"   💰 ${tvl or 0:,.2f} ({change_1d or 0:+.2f}% 24h)\n\n"
    
    return summary

async def get_yield_farming_opportunities(min_apy: float = 5.0) -> Optional[str]:
    """Get yield farming opportunities"""
    return await defillama_api.get_yield_opportunities(min_apy)

async def compare_chains(chain_list: List[str]) -> Optional[str]:
    """Compare blockchain chains"""
    return await defillama_api.get_chain_comparison(chain_list)