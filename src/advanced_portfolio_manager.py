# src/advanced_portfolio_manager.py
import asyncio
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import requests
from web3 import Web3
import ccxt
from pycoingecko import CoinGeckoAPI
import ta

from config import config
from user_db import get_user_property, set_user_property
from security_auditor import security_auditor
from performance_monitor import track_performance

logger = logging.getLogger(__name__)

@dataclass
class Asset:
    """Represents a portfolio asset"""
    symbol: str
    address: Optional[str]
    chain: str
    balance: float
    price_usd: float
    value_usd: float
    allocation_percent: float
    last_updated: datetime

@dataclass
class Portfolio:
    """Represents a user's portfolio"""
    user_id: int
    total_value_usd: float
    assets: List[Asset]
    wallets: List[str]
    last_updated: datetime
    performance_24h: float
    performance_7d: float
    performance_30d: float

@dataclass
class RiskMetrics:
    """Portfolio risk metrics"""
    var_95: float  # Value at Risk 95%
    sharpe_ratio: float
    max_drawdown: float
    volatility: float
    beta: float
    correlation_btc: float

class AdvancedPortfolioManager:
    """Advanced portfolio management with analytics and risk assessment"""
    
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.web3_providers = {
            'ethereum': Web3(Web3.HTTPProvider(config.get('ETHEREUM_RPC_URL', 'https://eth.llamarpc.com'))),
            'polygon': Web3(Web3.HTTPProvider(config.get('POLYGON_RPC_URL', 'https://polygon.llamarpc.com'))),
            'bsc': Web3(Web3.HTTPProvider(config.get('BSC_RPC_URL', 'https://bsc.llamarpc.com'))),
            'arbitrum': Web3(Web3.HTTPProvider(config.get('ARBITRUM_RPC_URL', 'https://arbitrum.llamarpc.com'))),
            'optimism': Web3(Web3.HTTPProvider(config.get('OPTIMISM_RPC_URL', 'https://optimism.llamarpc.com')))
        }
        self.exchanges = {}
        self._init_exchanges()
        
    def _init_exchanges(self):
        """Initialize exchange connections for price data"""
        try:
            self.exchanges['binance'] = ccxt.binance({'enableRateLimit': True})
            # Try new coinbase exchange name, fallback to old coinbasepro
            try:
                self.exchanges['coinbase'] = ccxt.coinbase({'enableRateLimit': True})
            except AttributeError:
                try:
                    self.exchanges['coinbase'] = ccxt.coinbasepro({'enableRateLimit': True})
                except AttributeError:
                    logger.warning("Coinbase exchange not available in ccxt")
        except Exception as e:
            logger.warning(f"Failed to initialize exchanges: {e}")

    @track_performance.track_function
    async def get_portfolio(self, user_id: int) -> Optional[Portfolio]:
        """Get user's complete portfolio"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "portfolio_access", True, 
                {"action": "get_portfolio"}
            )
            
            wallets = self._get_user_wallets(user_id)
            if not wallets:
                return None
                
            assets = []
            total_value = 0.0
            
            for wallet in wallets:
                wallet_assets = await self._get_wallet_assets(wallet)
                assets.extend(wallet_assets)
                
            # Calculate total value and allocations
            total_value = sum(asset.value_usd for asset in assets)
            for asset in assets:
                asset.allocation_percent = (asset.value_usd / total_value * 100) if total_value > 0 else 0
                
            # Calculate performance metrics
            performance_24h = await self._calculate_performance(user_id, '24h')
            performance_7d = await self._calculate_performance(user_id, '7d')
            performance_30d = await self._calculate_performance(user_id, '30d')
            
            portfolio = Portfolio(
                user_id=user_id,
                total_value_usd=total_value,
                assets=assets,
                wallets=wallets,
                last_updated=datetime.now(),
                performance_24h=performance_24h,
                performance_7d=performance_7d,
                performance_30d=performance_30d
            )
            
            # Cache portfolio data
            self._cache_portfolio(user_id, portfolio)
            
            return portfolio
            
        except Exception as e:
            logger.error(f"Error getting portfolio for user {user_id}: {e}")
            return None

    async def _get_wallet_assets(self, wallet_address: str) -> List[Asset]:
        """Get assets for a specific wallet across all chains"""
        assets = []
        
        for chain_name, web3 in self.web3_providers.items():
            try:
                # Get native token balance
                balance = web3.eth.get_balance(wallet_address)
                if balance > 0:
                    native_token = self._get_native_token(chain_name)
                    price = await self._get_token_price(native_token)
                    value = (balance / 10**18) * price
                    
                    asset = Asset(
                        symbol=native_token,
                        address=None,
                        chain=chain_name,
                        balance=balance / 10**18,
                        price_usd=price,
                        value_usd=value,
                        allocation_percent=0,  # Will be calculated later
                        last_updated=datetime.now()
                    )
                    assets.append(asset)
                
                # Get ERC-20 token balances using DeFiLlama or Moralis
                token_assets = await self._get_token_balances(wallet_address, chain_name)
                assets.extend(token_assets)
                
            except Exception as e:
                logger.warning(f"Error getting assets for wallet {wallet_address} on {chain_name}: {e}")
                
        return assets

    async def _get_token_balances(self, wallet_address: str, chain: str) -> List[Asset]:
        """Get ERC-20 token balances using external APIs"""
        assets = []
        
        try:
            # Use DeFiLlama API for token balances
            url = f"https://api.llama.fi/balances/{chain}/{wallet_address}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for token_address, balance_data in data.items():
                    if isinstance(balance_data, dict) and 'amount' in balance_data:
                        symbol = balance_data.get('symbol', 'UNKNOWN')
                        decimals = balance_data.get('decimals', 18)
                        balance = float(balance_data['amount']) / (10 ** decimals)
                        
                        if balance > 0:
                            price = await self._get_token_price(symbol)
                            value = balance * price
                            
                            asset = Asset(
                                symbol=symbol,
                                address=token_address,
                                chain=chain,
                                balance=balance,
                                price_usd=price,
                                value_usd=value,
                                allocation_percent=0,
                                last_updated=datetime.now()
                            )
                            assets.append(asset)
                            
        except Exception as e:
            logger.warning(f"Error getting token balances for {wallet_address}: {e}")
            
        return assets

    async def _get_token_price(self, symbol: str) -> float:
        """Get current token price in USD"""
        try:
            # Try CoinGecko first
            price_data = self.cg.get_price(ids=symbol.lower(), vs_currencies='usd')
            if symbol.lower() in price_data:
                return price_data[symbol.lower()]['usd']
                
            # Fallback to exchange APIs
            for exchange in self.exchanges.values():
                try:
                    ticker = exchange.fetch_ticker(f"{symbol}/USDT")
                    return ticker['last']
                except:
                    continue
                    
            return 0.0
            
        except Exception as e:
            logger.warning(f"Error getting price for {symbol}: {e}")
            return 0.0

    def _get_native_token(self, chain: str) -> str:
        """Get native token symbol for chain"""
        native_tokens = {
            'ethereum': 'ETH',
            'polygon': 'MATIC',
            'bsc': 'BNB',
            'arbitrum': 'ETH',
            'optimism': 'ETH'
        }
        return native_tokens.get(chain, 'ETH')

    async def _calculate_performance(self, user_id: int, timeframe: str) -> float:
        """Calculate portfolio performance for given timeframe"""
        try:
            # Get historical portfolio data
            historical_data = self._get_historical_portfolio_data(user_id, timeframe)
            if not historical_data:
                return 0.0
                
            current_value = historical_data[-1]['value']
            initial_value = historical_data[0]['value']
            
            if initial_value > 0:
                return ((current_value - initial_value) / initial_value) * 100
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating performance: {e}")
            return 0.0

    @track_performance.track_function
    async def calculate_risk_metrics(self, user_id: int) -> Optional[RiskMetrics]:
        """Calculate comprehensive risk metrics for portfolio"""
        try:
            portfolio = await self.get_portfolio(user_id)
            if not portfolio:
                return None
                
            # Get historical price data for portfolio assets
            historical_data = await self._get_portfolio_historical_data(user_id, days=365)
            if len(historical_data) < 30:
                return None
                
            # Convert to pandas DataFrame for analysis
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Calculate daily returns
            df['returns'] = df['value'].pct_change().dropna()
            
            # Calculate risk metrics
            returns = df['returns'].dropna()
            
            # Value at Risk (95% confidence)
            var_95 = np.percentile(returns, 5) * portfolio.total_value_usd
            
            # Sharpe Ratio (assuming 2% risk-free rate)
            risk_free_rate = 0.02 / 365  # Daily risk-free rate
            excess_returns = returns - risk_free_rate
            sharpe_ratio = excess_returns.mean() / returns.std() * np.sqrt(365) if returns.std() > 0 else 0
            
            # Maximum Drawdown
            cumulative_returns = (1 + returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # Volatility (annualized)
            volatility = returns.std() * np.sqrt(365)
            
            # Beta and correlation with BTC
            btc_data = await self._get_btc_historical_data(days=365)
            if btc_data:
                btc_df = pd.DataFrame(btc_data)
                btc_df['date'] = pd.to_datetime(btc_df['date'])
                btc_df.set_index('date', inplace=True)
                btc_df['returns'] = btc_df['price'].pct_change().dropna()
                
                # Align dates
                aligned_data = pd.merge(df[['returns']], btc_df[['returns']], 
                                      left_index=True, right_index=True, 
                                      suffixes=('_portfolio', '_btc'))
                
                if len(aligned_data) > 10:
                    correlation_btc = aligned_data['returns_portfolio'].corr(aligned_data['returns_btc'])
                    
                    # Beta calculation
                    covariance = aligned_data['returns_portfolio'].cov(aligned_data['returns_btc'])
                    btc_variance = aligned_data['returns_btc'].var()
                    beta = covariance / btc_variance if btc_variance > 0 else 0
                else:
                    correlation_btc = 0
                    beta = 0
            else:
                correlation_btc = 0
                beta = 0
            
            risk_metrics = RiskMetrics(
                var_95=var_95,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                volatility=volatility,
                beta=beta,
                correlation_btc=correlation_btc
            )
            
            return risk_metrics
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return None

    async def _get_btc_historical_data(self, days: int) -> List[Dict]:
        """Get Bitcoin historical price data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Use CoinGecko for BTC historical data
            data = self.cg.get_coin_market_chart_range_by_id(
                id='bitcoin',
                vs_currency='usd',
                from_timestamp=int(start_date.timestamp()),
                to_timestamp=int(end_date.timestamp())
            )
            
            historical_data = []
            for price_point in data['prices']:
                historical_data.append({
                    'date': datetime.fromtimestamp(price_point[0] / 1000),
                    'price': price_point[1]
                })
                
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting BTC historical data: {e}")
            return []

    @track_performance.track_function
    async def generate_rebalancing_suggestions(self, user_id: int) -> Dict[str, Any]:
        """Generate AI-powered portfolio rebalancing suggestions"""
        try:
            portfolio = await self.get_portfolio(user_id)
            if not portfolio:
                return {"error": "Portfolio not found"}
                
            # Get user's risk profile
            risk_profile = get_user_property(user_id, 'risk_profile') or 'moderate'
            
            # Define target allocations based on risk profile
            target_allocations = self._get_target_allocations(risk_profile)
            
            # Calculate current allocations by asset type
            current_allocations = self._calculate_current_allocations(portfolio)
            
            # Generate rebalancing suggestions
            suggestions = []
            total_value = portfolio.total_value_usd
            
            for asset_type, target_percent in target_allocations.items():
                current_percent = current_allocations.get(asset_type, 0)
                difference = target_percent - current_percent
                
                if abs(difference) > 5:  # Only suggest if difference > 5%
                    target_value = total_value * (target_percent / 100)
                    current_value = total_value * (current_percent / 100)
                    rebalance_amount = target_value - current_value
                    
                    action = "BUY" if rebalance_amount > 0 else "SELL"
                    
                    suggestions.append({
                        'asset_type': asset_type,
                        'action': action,
                        'current_allocation': current_percent,
                        'target_allocation': target_percent,
                        'rebalance_amount_usd': abs(rebalance_amount),
                        'priority': 'HIGH' if abs(difference) > 15 else 'MEDIUM'
                    })
            
            # Sort by priority and difference
            suggestions.sort(key=lambda x: (x['priority'] == 'HIGH', abs(x['target_allocation'] - x['current_allocation'])), reverse=True)
            
            return {
                'suggestions': suggestions,
                'total_portfolio_value': total_value,
                'risk_profile': risk_profile,
                'rebalancing_needed': len(suggestions) > 0
            }
            
        except Exception as e:
            logger.error(f"Error generating rebalancing suggestions: {e}")
            return {"error": str(e)}

    def _get_target_allocations(self, risk_profile: str) -> Dict[str, float]:
        """Get target asset allocations based on risk profile"""
        allocations = {
            'conservative': {
                'stablecoins': 40,
                'bitcoin': 25,
                'ethereum': 20,
                'defi': 10,
                'altcoins': 5
            },
            'moderate': {
                'stablecoins': 20,
                'bitcoin': 30,
                'ethereum': 25,
                'defi': 15,
                'altcoins': 10
            },
            'aggressive': {
                'stablecoins': 10,
                'bitcoin': 25,
                'ethereum': 20,
                'defi': 25,
                'altcoins': 20
            }
        }
        return allocations.get(risk_profile, allocations['moderate'])

    def _calculate_current_allocations(self, portfolio: Portfolio) -> Dict[str, float]:
        """Calculate current asset type allocations"""
        allocations = {
            'stablecoins': 0,
            'bitcoin': 0,
            'ethereum': 0,
            'defi': 0,
            'altcoins': 0
        }
        
        stablecoins = ['USDT', 'USDC', 'DAI', 'BUSD', 'FRAX', 'LUSD']
        defi_tokens = ['UNI', 'AAVE', 'COMP', 'MKR', 'SNX', 'CRV', 'SUSHI', 'YFI']
        
        for asset in portfolio.assets:
            symbol = asset.symbol.upper()
            allocation = asset.allocation_percent
            
            if symbol in stablecoins:
                allocations['stablecoins'] += allocation
            elif symbol == 'BTC':
                allocations['bitcoin'] += allocation
            elif symbol == 'ETH':
                allocations['ethereum'] += allocation
            elif symbol in defi_tokens:
                allocations['defi'] += allocation
            else:
                allocations['altcoins'] += allocation
                
        return allocations

    def add_wallet(self, user_id: int, wallet_address: str) -> bool:
        """Add wallet to user's portfolio"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "wallet_add", True, 
                {"wallet_address": wallet_address[:10] + "..."}
            )
            
            # Validate wallet address
            if not Web3.is_address(wallet_address):
                return False
                
            wallets = self._get_user_wallets(user_id)
            if wallet_address not in wallets:
                wallets.append(wallet_address)
                set_user_property(user_id, 'portfolio_wallets', json.dumps(wallets))
                
            return True
            
        except Exception as e:
            logger.error(f"Error adding wallet: {e}")
            return False

    def remove_wallet(self, user_id: int, wallet_address: str) -> bool:
        """Remove wallet from user's portfolio"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "wallet_remove", True, 
                {"wallet_address": wallet_address[:10] + "..."}
            )
            
            wallets = self._get_user_wallets(user_id)
            if wallet_address in wallets:
                wallets.remove(wallet_address)
                set_user_property(user_id, 'portfolio_wallets', json.dumps(wallets))
                
            return True
            
        except Exception as e:
            logger.error(f"Error removing wallet: {e}")
            return False

    def _get_user_wallets(self, user_id: int) -> List[str]:
        """Get user's wallet addresses"""
        wallets_json = get_user_property(user_id, 'portfolio_wallets')
        if wallets_json:
            try:
                return json.loads(wallets_json)
            except:
                return []
        return []

    def _cache_portfolio(self, user_id: int, portfolio: Portfolio):
        """Cache portfolio data for performance"""
        try:
            cache_data = {
                'portfolio': asdict(portfolio),
                'timestamp': datetime.now().isoformat()
            }
            set_user_property(user_id, 'portfolio_cache', json.dumps(cache_data, default=str))
        except Exception as e:
            logger.warning(f"Error caching portfolio: {e}")

    def _get_historical_portfolio_data(self, user_id: int, timeframe: str) -> List[Dict]:
        """Get historical portfolio data (placeholder - would need database implementation)"""
        # This would typically query a time-series database
        # For now, return empty list
        return []

    async def _get_portfolio_historical_data(self, user_id: int, days: int) -> List[Dict]:
        """Get portfolio historical data for risk calculations"""
        # This would typically query a time-series database
        # For now, return mock data for demonstration
        historical_data = []
        base_value = 10000  # Mock starting value
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            # Mock some volatility
            daily_change = np.random.normal(0, 0.02)  # 2% daily volatility
            value = base_value * (1 + daily_change)
            base_value = value
            
            historical_data.append({
                'date': date,
                'value': value
            })
            
        return historical_data

# Global instance
advanced_portfolio_manager = AdvancedPortfolioManager()