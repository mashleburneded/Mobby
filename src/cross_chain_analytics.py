# src/cross_chain_analytics.py
import asyncio
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from web3 import Web3

from config import config
from user_db import get_user_property, set_user_property
from security_auditor import security_auditor
from performance_monitor import track_performance

logger = logging.getLogger(__name__)

class ChainType(Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    BSC = "bsc"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    BASE = "base"
    AVALANCHE = "avalanche"
    FANTOM = "fantom"
    SOLANA = "solana"

@dataclass
class ChainInfo:
    """Information about a blockchain"""
    name: str
    chain_id: int
    native_token: str
    rpc_url: str
    explorer_url: str
    gas_token: str
    avg_block_time: float
    current_gas_price: float
    tps: float  # Transactions per second

@dataclass
class CrossChainAsset:
    """Asset across multiple chains"""
    symbol: str
    name: str
    total_supply: float
    chains: Dict[str, Dict[str, Any]]  # chain -> {address, balance, price}
    total_value_usd: float
    dominant_chain: str

@dataclass
class BridgeTransaction:
    """Cross-chain bridge transaction"""
    tx_hash: str
    from_chain: str
    to_chain: str
    asset: str
    amount: float
    status: str  # pending, completed, failed
    bridge_protocol: str
    estimated_time: int  # minutes
    actual_time: Optional[int]
    fees: Dict[str, float]  # chain -> fee amount
    created_at: datetime
    completed_at: Optional[datetime]

@dataclass
class ArbitrageOpportunity:
    """Cross-chain arbitrage opportunity"""
    asset: str
    buy_chain: str
    sell_chain: str
    buy_price: float
    sell_price: float
    price_difference: float
    profit_percentage: float
    required_capital: float
    estimated_profit: float
    bridge_fees: float
    net_profit: float
    execution_time: int  # minutes
    risk_score: float  # 1-10

class CrossChainAnalytics:
    """Cross-chain analytics and operations system"""
    
    def __init__(self):
        self.supported_chains = {
            ChainType.ETHEREUM: ChainInfo(
                name="Ethereum",
                chain_id=1,
                native_token="ETH",
                rpc_url=config.get('ETHEREUM_RPC_URL', 'https://eth.llamarpc.com'),
                explorer_url="https://etherscan.io",
                gas_token="ETH",
                avg_block_time=12.0,
                current_gas_price=0.0,
                tps=15.0
            ),
            ChainType.POLYGON: ChainInfo(
                name="Polygon",
                chain_id=137,
                native_token="MATIC",
                rpc_url=config.get('POLYGON_RPC_URL', 'https://polygon.llamarpc.com'),
                explorer_url="https://polygonscan.com",
                gas_token="MATIC",
                avg_block_time=2.0,
                current_gas_price=0.0,
                tps=7000.0
            ),
            ChainType.BSC: ChainInfo(
                name="BNB Smart Chain",
                chain_id=56,
                native_token="BNB",
                rpc_url=config.get('BSC_RPC_URL', 'https://bsc.llamarpc.com'),
                explorer_url="https://bscscan.com",
                gas_token="BNB",
                avg_block_time=3.0,
                current_gas_price=0.0,
                tps=160.0
            ),
            ChainType.ARBITRUM: ChainInfo(
                name="Arbitrum One",
                chain_id=42161,
                native_token="ETH",
                rpc_url=config.get('ARBITRUM_RPC_URL', 'https://arbitrum.llamarpc.com'),
                explorer_url="https://arbiscan.io",
                gas_token="ETH",
                avg_block_time=0.25,
                current_gas_price=0.0,
                tps=4000.0
            ),
            ChainType.OPTIMISM: ChainInfo(
                name="Optimism",
                chain_id=10,
                native_token="ETH",
                rpc_url=config.get('OPTIMISM_RPC_URL', 'https://optimism.llamarpc.com'),
                explorer_url="https://optimistic.etherscan.io",
                gas_token="ETH",
                avg_block_time=2.0,
                current_gas_price=0.0,
                tps=2000.0
            ),
            ChainType.BASE: ChainInfo(
                name="Base",
                chain_id=8453,
                native_token="ETH",
                rpc_url=config.get('BASE_RPC_URL', 'https://mainnet.base.org'),
                explorer_url="https://base.blockscout.com",
                gas_token="ETH",
                avg_block_time=2.0,
                current_gas_price=0.0,
                tps=1000.0
            )
        }
        
        self.web3_providers = {}
        self.bridge_protocols = [
            "Hop Protocol",
            "Synapse",
            "Multichain",
            "Stargate",
            "Polygon Bridge",
            "Arbitrum Bridge",
            "Optimism Bridge"
        ]
        self._init_web3_providers()

    def _init_web3_providers(self):
        """Initialize Web3 providers for all supported chains"""
        try:
            for chain_type, chain_info in self.supported_chains.items():
                try:
                    self.web3_providers[chain_type] = Web3(Web3.HTTPProvider(chain_info.rpc_url))
                except Exception as e:
                    logger.warning(f"Failed to initialize Web3 for {chain_info.name}: {e}")
        except Exception as e:
            logger.error(f"Error initializing Web3 providers: {e}")

    @track_performance.track_function
    async def get_multichain_portfolio(self, user_id: int, wallet_addresses: List[str]) -> Dict[str, Any]:
        """Get portfolio across all supported chains"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "multichain_portfolio", True, 
                {"wallet_count": len(wallet_addresses)}
            )
            
            portfolio_data = {}
            total_value = 0.0
            
            for chain_type in self.supported_chains:
                chain_name = chain_type.value
                chain_portfolio = await self._get_chain_portfolio(chain_type, wallet_addresses)
                
                if chain_portfolio:
                    portfolio_data[chain_name] = chain_portfolio
                    total_value += chain_portfolio.get('total_value', 0)
            
            # Calculate chain distribution
            chain_distribution = {}
            for chain_name, data in portfolio_data.items():
                chain_value = data.get('total_value', 0)
                chain_distribution[chain_name] = {
                    'value': chain_value,
                    'percentage': (chain_value / total_value * 100) if total_value > 0 else 0
                }
            
            # Find cross-chain assets
            cross_chain_assets = await self._identify_cross_chain_assets(portfolio_data)
            
            return {
                "success": True,
                "total_value": total_value,
                "chain_distribution": chain_distribution,
                "portfolio_by_chain": portfolio_data,
                "cross_chain_assets": cross_chain_assets,
                "supported_chains": list(self.supported_chains.keys()),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting multichain portfolio: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def track_bridge_transaction(self, user_id: int, tx_hash: str, 
                                     from_chain: str, to_chain: str) -> Dict[str, Any]:
        """Track a cross-chain bridge transaction"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "bridge_tracking", True, 
                {"tx_hash": tx_hash[:10] + "...", "from_chain": from_chain, "to_chain": to_chain}
            )
            
            # Get transaction details
            tx_details = await self._get_bridge_transaction_details(tx_hash, from_chain, to_chain)
            
            if not tx_details:
                return {"success": False, "message": "Transaction not found or not a bridge transaction"}
            
            # Create bridge transaction record
            bridge_tx = BridgeTransaction(
                tx_hash=tx_hash,
                from_chain=from_chain,
                to_chain=to_chain,
                asset=tx_details.get('asset', 'Unknown'),
                amount=tx_details.get('amount', 0),
                status=tx_details.get('status', 'pending'),
                bridge_protocol=tx_details.get('bridge_protocol', 'Unknown'),
                estimated_time=tx_details.get('estimated_time', 30),
                actual_time=tx_details.get('actual_time'),
                fees=tx_details.get('fees', {}),
                created_at=tx_details.get('created_at', datetime.now()),
                completed_at=tx_details.get('completed_at')
            )
            
            # Store transaction for tracking
            user_bridge_txs = json.loads(get_user_property(user_id, 'bridge_transactions') or '[]')
            user_bridge_txs.append(asdict(bridge_tx))
            set_user_property(user_id, 'bridge_transactions', json.dumps(user_bridge_txs, default=str))
            
            return {
                "success": True,
                "transaction": asdict(bridge_tx),
                "estimated_completion": (
                    bridge_tx.created_at + timedelta(minutes=bridge_tx.estimated_time)
                ).isoformat() if bridge_tx.status == 'pending' else None
            }
            
        except Exception as e:
            logger.error(f"Error tracking bridge transaction: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def compare_gas_costs(self, user_id: int, chains: List[str], 
                              transaction_type: str = "transfer") -> Dict[str, Any]:
        """Compare gas costs across different chains"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "gas_comparison", True, 
                {"chains": chains, "tx_type": transaction_type}
            )
            
            gas_comparison = {}
            
            for chain_name in chains:
                try:
                    chain_type = ChainType(chain_name.lower())
                    if chain_type not in self.supported_chains:
                        continue
                    
                    gas_data = await self._get_current_gas_costs(chain_type, transaction_type)
                    gas_comparison[chain_name] = gas_data
                    
                except ValueError:
                    logger.warning(f"Unsupported chain: {chain_name}")
                    continue
            
            # Find cheapest option
            cheapest_chain = min(
                gas_comparison.keys(),
                key=lambda x: gas_comparison[x].get('cost_usd', float('inf'))
            ) if gas_comparison else None
            
            # Calculate savings
            savings_analysis = {}
            if cheapest_chain:
                cheapest_cost = gas_comparison[cheapest_chain]['cost_usd']
                for chain, data in gas_comparison.items():
                    if chain != cheapest_chain:
                        savings = data['cost_usd'] - cheapest_cost
                        savings_percentage = (savings / data['cost_usd']) * 100 if data['cost_usd'] > 0 else 0
                        savings_analysis[chain] = {
                            'savings_usd': savings,
                            'savings_percentage': savings_percentage
                        }
            
            return {
                "success": True,
                "gas_comparison": gas_comparison,
                "cheapest_chain": cheapest_chain,
                "savings_analysis": savings_analysis,
                "transaction_type": transaction_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error comparing gas costs: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def scan_arbitrage_opportunities(self, user_id: int, 
                                         min_profit_percentage: float = 1.0) -> Dict[str, Any]:
        """Scan for cross-chain arbitrage opportunities"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "arbitrage_scan", True, 
                {"min_profit": min_profit_percentage}
            )
            
            opportunities = []
            
            # Get price data from multiple chains
            price_data = await self._get_cross_chain_prices()
            
            # Analyze arbitrage opportunities
            for asset, chain_prices in price_data.items():
                if len(chain_prices) < 2:
                    continue
                
                # Find best buy and sell opportunities
                sorted_prices = sorted(chain_prices.items(), key=lambda x: x[1]['price'])
                buy_chain, buy_data = sorted_prices[0]
                sell_chain, sell_data = sorted_prices[-1]
                
                buy_price = buy_data['price']
                sell_price = sell_data['price']
                
                if buy_price <= 0 or sell_price <= 0:
                    continue
                
                price_difference = sell_price - buy_price
                profit_percentage = (price_difference / buy_price) * 100
                
                if profit_percentage >= min_profit_percentage:
                    # Calculate bridge fees and execution costs
                    bridge_fees = await self._estimate_bridge_fees(
                        asset, buy_chain, sell_chain, 1000  # $1000 test amount
                    )
                    
                    # Calculate net profit
                    gross_profit = profit_percentage
                    net_profit = gross_profit - bridge_fees.get('total_fee_percentage', 0)
                    
                    if net_profit > 0:
                        opportunity = ArbitrageOpportunity(
                            asset=asset,
                            buy_chain=buy_chain,
                            sell_chain=sell_chain,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            price_difference=price_difference,
                            profit_percentage=profit_percentage,
                            required_capital=1000,  # Example amount
                            estimated_profit=net_profit * 10,  # For $1000
                            bridge_fees=bridge_fees.get('total_fee_usd', 0),
                            net_profit=net_profit,
                            execution_time=bridge_fees.get('estimated_time', 30),
                            risk_score=await self._calculate_arbitrage_risk(
                                asset, buy_chain, sell_chain, profit_percentage
                            )
                        )
                        
                        opportunities.append(opportunity)
            
            # Sort by net profit
            opportunities.sort(key=lambda x: x.net_profit, reverse=True)
            
            return {
                "success": True,
                "opportunities": [asdict(opp) for opp in opportunities[:10]],  # Top 10
                "total_found": len(opportunities),
                "min_profit_threshold": min_profit_percentage,
                "scan_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scanning arbitrage opportunities: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def get_supported_chains(self, user_id: int) -> Dict[str, Any]:
        """Get list of supported chains with current status"""
        try:
            chains_status = {}
            
            for chain_type, chain_info in self.supported_chains.items():
                # Check chain health
                is_healthy = await self._check_chain_health(chain_type)
                
                # Get current gas price
                current_gas = await self._get_current_gas_price(chain_type)
                
                chains_status[chain_type.value] = {
                    "name": chain_info.name,
                    "chain_id": chain_info.chain_id,
                    "native_token": chain_info.native_token,
                    "explorer_url": chain_info.explorer_url,
                    "avg_block_time": chain_info.avg_block_time,
                    "tps": chain_info.tps,
                    "current_gas_price": current_gas,
                    "is_healthy": is_healthy,
                    "status": "online" if is_healthy else "offline"
                }
            
            return {
                "success": True,
                "supported_chains": chains_status,
                "total_chains": len(chains_status),
                "healthy_chains": sum(1 for status in chains_status.values() if status["is_healthy"])
            }
            
        except Exception as e:
            logger.error(f"Error getting supported chains: {e}")
            return {"success": False, "message": str(e)}

    async def _get_chain_portfolio(self, chain_type: ChainType, 
                                 wallet_addresses: List[str]) -> Optional[Dict[str, Any]]:
        """Get portfolio for a specific chain"""
        try:
            chain_info = self.supported_chains[chain_type]
            web3 = self.web3_providers.get(chain_type)
            
            if not web3:
                return None
            
            total_value = 0.0
            assets = []
            
            for wallet_address in wallet_addresses:
                try:
                    # Get native token balance
                    balance = web3.eth.get_balance(wallet_address)
                    if balance > 0:
                        native_balance = balance / 10**18
                        native_price = await self._get_token_price(chain_info.native_token)
                        native_value = native_balance * native_price
                        
                        assets.append({
                            "symbol": chain_info.native_token,
                            "balance": native_balance,
                            "price_usd": native_price,
                            "value_usd": native_value,
                            "type": "native"
                        })
                        
                        total_value += native_value
                    
                    # Get ERC-20 tokens (would need token list and ABI)
                    # This is simplified - in practice would use APIs like Moralis, Alchemy, etc.
                    
                except Exception as e:
                    logger.warning(f"Error getting balance for {wallet_address} on {chain_info.name}: {e}")
            
            return {
                "chain": chain_type.value,
                "total_value": total_value,
                "assets": assets,
                "wallet_count": len(wallet_addresses)
            }
            
        except Exception as e:
            logger.error(f"Error getting chain portfolio: {e}")
            return None

    async def _identify_cross_chain_assets(self, portfolio_data: Dict) -> List[CrossChainAsset]:
        """Identify assets that exist across multiple chains"""
        try:
            asset_chains = {}
            
            # Group assets by symbol
            for chain_name, chain_data in portfolio_data.items():
                for asset in chain_data.get('assets', []):
                    symbol = asset['symbol']
                    if symbol not in asset_chains:
                        asset_chains[symbol] = {}
                    
                    asset_chains[symbol][chain_name] = {
                        'balance': asset['balance'],
                        'value_usd': asset['value_usd'],
                        'price_usd': asset['price_usd']
                    }
            
            # Find cross-chain assets (present on multiple chains)
            cross_chain_assets = []
            for symbol, chains in asset_chains.items():
                if len(chains) > 1:
                    total_value = sum(data['value_usd'] for data in chains.values())
                    dominant_chain = max(chains.keys(), key=lambda x: chains[x]['value_usd'])
                    
                    cross_chain_asset = CrossChainAsset(
                        symbol=symbol,
                        name=symbol,  # Would get full name from token registry
                        total_supply=0,  # Would get from token contract
                        chains=chains,
                        total_value_usd=total_value,
                        dominant_chain=dominant_chain
                    )
                    
                    cross_chain_assets.append(cross_chain_asset)
            
            return cross_chain_assets
            
        except Exception as e:
            logger.error(f"Error identifying cross-chain assets: {e}")
            return []

    async def _get_bridge_transaction_details(self, tx_hash: str, 
                                            from_chain: str, to_chain: str) -> Optional[Dict[str, Any]]:
        """Get bridge transaction details"""
        try:
            # This would typically query bridge protocol APIs
            # For now, return mock data
            return {
                "asset": "USDC",
                "amount": 1000.0,
                "status": "pending",
                "bridge_protocol": "Hop Protocol",
                "estimated_time": 15,
                "fees": {
                    from_chain: 5.0,
                    to_chain: 2.0
                },
                "created_at": datetime.now() - timedelta(minutes=5)
            }
            
        except Exception as e:
            logger.error(f"Error getting bridge transaction details: {e}")
            return None

    async def _get_current_gas_costs(self, chain_type: ChainType, 
                                   transaction_type: str) -> Dict[str, Any]:
        """Get current gas costs for a chain"""
        try:
            chain_info = self.supported_chains[chain_type]
            web3 = self.web3_providers.get(chain_type)
            
            if not web3:
                return {"error": "Chain not available"}
            
            # Get current gas price
            gas_price = web3.eth.gas_price
            
            # Estimate gas for transaction type
            gas_estimates = {
                "transfer": 21000,
                "erc20_transfer": 65000,
                "swap": 150000,
                "bridge": 200000,
                "nft_mint": 100000
            }
            
            gas_limit = gas_estimates.get(transaction_type, 21000)
            gas_cost_wei = gas_price * gas_limit
            gas_cost_native = gas_cost_wei / 10**18
            
            # Get native token price
            native_price = await self._get_token_price(chain_info.native_token)
            gas_cost_usd = gas_cost_native * native_price
            
            return {
                "chain": chain_type.value,
                "gas_price_gwei": gas_price / 10**9,
                "gas_limit": gas_limit,
                "cost_native": gas_cost_native,
                "cost_usd": gas_cost_usd,
                "native_token": chain_info.native_token,
                "transaction_type": transaction_type
            }
            
        except Exception as e:
            logger.error(f"Error getting gas costs: {e}")
            return {"error": str(e)}

    async def _get_cross_chain_prices(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Get price data across multiple chains"""
        try:
            # This would typically query DEX aggregators on each chain
            # For now, return mock data with slight price differences
            mock_prices = {
                "USDC": {
                    "ethereum": {"price": 1.000, "liquidity": 1000000},
                    "polygon": {"price": 0.998, "liquidity": 500000},
                    "arbitrum": {"price": 1.002, "liquidity": 300000}
                },
                "WETH": {
                    "ethereum": {"price": 2000.00, "liquidity": 50000},
                    "polygon": {"price": 1995.50, "liquidity": 20000},
                    "arbitrum": {"price": 2003.25, "liquidity": 30000}
                }
            }
            
            return mock_prices
            
        except Exception as e:
            logger.error(f"Error getting cross-chain prices: {e}")
            return {}

    async def _estimate_bridge_fees(self, asset: str, from_chain: str, 
                                  to_chain: str, amount: float) -> Dict[str, Any]:
        """Estimate bridge fees for cross-chain transfer"""
        try:
            # Mock bridge fee calculation
            base_fee = 5.0  # $5 base fee
            percentage_fee = 0.1  # 0.1%
            
            percentage_cost = (percentage_fee / 100) * amount
            total_fee_usd = base_fee + percentage_cost
            total_fee_percentage = (total_fee_usd / amount) * 100
            
            return {
                "base_fee_usd": base_fee,
                "percentage_fee": percentage_fee,
                "percentage_cost_usd": percentage_cost,
                "total_fee_usd": total_fee_usd,
                "total_fee_percentage": total_fee_percentage,
                "estimated_time": 15  # minutes
            }
            
        except Exception as e:
            logger.error(f"Error estimating bridge fees: {e}")
            return {"total_fee_usd": 0, "total_fee_percentage": 0, "estimated_time": 30}

    async def _calculate_arbitrage_risk(self, asset: str, buy_chain: str, 
                                      sell_chain: str, profit_percentage: float) -> float:
        """Calculate risk score for arbitrage opportunity"""
        try:
            risk_score = 5.0  # Base risk
            
            # Higher profit = higher risk
            if profit_percentage > 5:
                risk_score += 2
            elif profit_percentage > 2:
                risk_score += 1
            
            # Chain-specific risks
            high_risk_chains = ["bsc", "fantom"]
            if buy_chain in high_risk_chains or sell_chain in high_risk_chains:
                risk_score += 1
            
            # Asset-specific risks
            if asset not in ["USDC", "USDT", "WETH", "WBTC"]:
                risk_score += 1
            
            return min(10.0, max(1.0, risk_score))
            
        except Exception as e:
            logger.error(f"Error calculating arbitrage risk: {e}")
            return 5.0

    async def _check_chain_health(self, chain_type: ChainType) -> bool:
        """Check if a chain is healthy and responsive"""
        try:
            web3 = self.web3_providers.get(chain_type)
            if not web3:
                return False
            
            # Try to get latest block
            latest_block = web3.eth.get_block('latest')
            
            # Check if block is recent (within last 5 minutes)
            block_time = datetime.fromtimestamp(latest_block['timestamp'])
            time_diff = datetime.now() - block_time
            
            return time_diff.total_seconds() < 300  # 5 minutes
            
        except Exception as e:
            logger.warning(f"Chain health check failed for {chain_type.value}: {e}")
            return False

    async def _get_current_gas_price(self, chain_type: ChainType) -> float:
        """Get current gas price for a chain"""
        try:
            web3 = self.web3_providers.get(chain_type)
            if not web3:
                return 0.0
            
            gas_price = web3.eth.gas_price
            return gas_price / 10**9  # Convert to Gwei
            
        except Exception as e:
            logger.warning(f"Failed to get gas price for {chain_type.value}: {e}")
            return 0.0

    async def _get_token_price(self, symbol: str) -> float:
        """Get token price in USD"""
        try:
            # Use CoinGecko API
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get(symbol.lower(), {}).get('usd', 0.0)
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Failed to get price for {symbol}: {e}")
            return 0.0



class CrossChainAnalyzer:
    """Cross-chain analyzer for compatibility"""
    
    def __init__(self):
        self.analytics = CrossChainAnalytics()
        # Expose supported_chains for compatibility
        self.supported_chains = self.analytics.supported_chains
    
    def analyze_cross_chain_activity(self, *args, **kwargs):
        """Analyze cross-chain activity"""
        return self.analytics.get_cross_chain_summary()
    
    def get_bridge_data(self, *args, **kwargs):
        """Get bridge data"""
        return self.analytics.get_bridge_volume()
