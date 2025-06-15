#!/usr/bin/env python3
"""
GAS PRICE MONITORING SYSTEM
===========================
Monitor gas prices across multiple blockchain networks.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GasPriceMonitor:
    """Monitor gas prices across multiple chains"""
    
    def __init__(self):
        self.chains = {
            'ethereum': {
                'name': 'Ethereum',
                'symbol': 'ETH',
                'api_url': 'https://api.etherscan.io/api?module=gastracker&action=gasoracle',
                'unit': 'gwei',
                'decimals': 9
            },
            'polygon': {
                'name': 'Polygon',
                'symbol': 'MATIC',
                'api_url': 'https://api.polygonscan.com/api?module=gastracker&action=gasoracle',
                'unit': 'gwei',
                'decimals': 9
            },
            'bsc': {
                'name': 'BNB Smart Chain',
                'symbol': 'BNB',
                'api_url': 'https://api.bscscan.com/api?module=gastracker&action=gasoracle',
                'unit': 'gwei',
                'decimals': 9
            },
            'arbitrum': {
                'name': 'Arbitrum One',
                'symbol': 'ETH',
                'api_url': 'https://api.arbiscan.io/api?module=gastracker&action=gasoracle',
                'unit': 'gwei',
                'decimals': 9
            },
            'optimism': {
                'name': 'Optimism',
                'symbol': 'ETH',
                'api_url': 'https://api-optimistic.etherscan.io/api?module=gastracker&action=gasoracle',
                'unit': 'gwei',
                'decimals': 9
            },
            'avalanche': {
                'name': 'Avalanche C-Chain',
                'symbol': 'AVAX',
                'api_url': 'https://api.snowtrace.io/api?module=gastracker&action=gasoracle',
                'unit': 'gwei',
                'decimals': 9
            },
            'fantom': {
                'name': 'Fantom',
                'symbol': 'FTM',
                'api_url': 'https://api.ftmscan.com/api?module=gastracker&action=gasoracle',
                'unit': 'gwei',
                'decimals': 9
            }
        }
        
        self.cache = {}
        self.cache_duration = 30  # 30 seconds cache
    
    async def get_gas_price(self, chain: str) -> Optional[Dict]:
        """Get gas price for a specific chain"""
        if chain not in self.chains:
            return None
        
        # Check cache
        cache_key = f"gas_{chain}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_duration):
                return cached_data
        
        try:
            chain_info = self.chains[chain]
            
            async with aiohttp.ClientSession() as session:
                async with session.get(chain_info['api_url'], timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == '1' and 'result' in data:
                            result = data['result']
                            gas_data = {
                                'chain': chain,
                                'name': chain_info['name'],
                                'symbol': chain_info['symbol'],
                                'slow': float(result.get('SafeGasPrice', 0)),
                                'standard': float(result.get('ProposeGasPrice', 0)),
                                'fast': float(result.get('FastGasPrice', 0)),
                                'unit': chain_info['unit'],
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            # Cache the result
                            self.cache[cache_key] = (gas_data, datetime.now())
                            return gas_data
        
        except Exception as e:
            logger.error(f"Error fetching gas price for {chain}: {e}")
        
        return None
    
    async def get_all_gas_prices(self) -> Dict[str, Dict]:
        """Get gas prices for all supported chains"""
        tasks = []
        for chain in self.chains.keys():
            tasks.append(self.get_gas_price(chain))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        gas_prices = {}
        for i, result in enumerate(results):
            chain = list(self.chains.keys())[i]
            if isinstance(result, dict) and result:
                gas_prices[chain] = result
            else:
                gas_prices[chain] = {
                    'chain': chain,
                    'name': self.chains[chain]['name'],
                    'error': 'Failed to fetch data'
                }
        
        return gas_prices
    
    def format_gas_prices(self, gas_prices: Dict[str, Dict]) -> str:
        """Format gas prices for display"""
        if not gas_prices:
            return "❌ No gas price data available"
        
        message = "⛽ **Gas Prices Across Chains**\n\n"
        
        for chain, data in gas_prices.items():
            if 'error' in data:
                message += f"❌ **{data['name']}**: {data['error']}\n\n"
                continue
            
            message += f"🔗 **{data['name']} ({data['symbol']})**\n"
            message += f"🐌 Slow: {data['slow']:.1f} {data['unit']}\n"
            message += f"⚡ Standard: {data['standard']:.1f} {data['unit']}\n"
            message += f"🚀 Fast: {data['fast']:.1f} {data['unit']}\n\n"
        
        message += f"🕐 Last updated: {datetime.now().strftime('%H:%M:%S UTC')}\n"
        message += "💡 Use `/gas <chain>` for specific chain data"
        
        return message
    
    def format_single_gas_price(self, gas_data: Dict) -> str:
        """Format single chain gas price for display"""
        if not gas_data or 'error' in gas_data:
            return f"❌ Failed to get gas price data"
        
        message = f"⛽ **{gas_data['name']} Gas Prices**\n\n"
        message += f"🐌 **Slow**: {gas_data['slow']:.1f} {gas_data['unit']}\n"
        message += f"⚡ **Standard**: {gas_data['standard']:.1f} {gas_data['unit']}\n"
        message += f"🚀 **Fast**: {gas_data['fast']:.1f} {gas_data['unit']}\n\n"
        
        # Add cost estimates for common operations
        if gas_data['chain'] == 'ethereum':
            eth_price = 3000  # Rough estimate, could be fetched from API
            message += "💰 **Estimated Costs (USD)**:\n"
            message += f"• Simple Transfer: ${(gas_data['standard'] * 21000 * eth_price / 1e9):.2f}\n"
            message += f"• Uniswap Swap: ${(gas_data['standard'] * 150000 * eth_price / 1e9):.2f}\n"
            message += f"• NFT Mint: ${(gas_data['standard'] * 100000 * eth_price / 1e9):.2f}\n\n"
        
        message += f"🕐 Last updated: {datetime.now().strftime('%H:%M:%S UTC')}"
        
        return message
    
    def get_supported_chains(self) -> List[str]:
        """Get list of supported chains"""
        return list(self.chains.keys())
    
    def get_chain_info(self, chain: str) -> Optional[Dict]:
        """Get information about a specific chain"""
        return self.chains.get(chain)

# Global instance
gas_monitor = GasPriceMonitor()

async def get_gas_prices(chain: Optional[str] = None) -> str:
    """Get gas prices for all chains or a specific chain"""
    if chain:
        if chain.lower() not in gas_monitor.get_supported_chains():
            supported = ", ".join(gas_monitor.get_supported_chains())
            return f"❌ Unsupported chain '{chain}'. Supported chains: {supported}"
        
        gas_data = await gas_monitor.get_gas_price(chain.lower())
        return gas_monitor.format_single_gas_price(gas_data)
    else:
        gas_prices = await gas_monitor.get_all_gas_prices()
        return gas_monitor.format_gas_prices(gas_prices)