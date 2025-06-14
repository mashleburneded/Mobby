# src/automated_trading.py
import asyncio
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import ccxt
from web3 import Web3

from config import config
from user_db import get_user_property, set_user_property
from security_auditor import security_auditor
from performance_monitor import track_performance

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    DCA = "dca"  # Dollar Cost Averaging
    GRID = "grid"  # Grid Trading
    MOMENTUM = "momentum"  # Momentum Trading
    MEAN_REVERSION = "mean_reversion"  # Mean Reversion
    ARBITRAGE = "arbitrage"  # Arbitrage
    YIELD_FARMING = "yield_farming"  # Yield Farming
    CUSTOM = "custom"  # Custom Strategy

class StrategyStatus(Enum):
    DRAFT = "draft"
    BACKTESTING = "backtesting"
    PAPER_TRADING = "paper_trading"
    LIVE = "live"
    PAUSED = "paused"
    STOPPED = "stopped"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

@dataclass
class TradingOrder:
    """Represents a trading order"""
    id: str
    strategy_id: str
    symbol: str
    side: str  # buy/sell
    order_type: OrderType
    amount: float
    price: Optional[float]
    status: str
    created_at: datetime
    executed_at: Optional[datetime]
    exchange_order_id: Optional[str]

@dataclass
class StrategyParameters:
    """Strategy configuration parameters"""
    symbol: str
    base_amount: float
    max_position_size: float
    stop_loss_percent: Optional[float]
    take_profit_percent: Optional[float]
    rebalance_frequency: str  # daily, weekly, monthly
    risk_management: Dict[str, Any]
    custom_params: Dict[str, Any]

@dataclass
class TradingStrategy:
    """Represents a trading strategy"""
    id: str
    user_id: int
    name: str
    strategy_type: StrategyType
    status: StrategyStatus
    parameters: StrategyParameters
    performance: Dict[str, float]
    created_at: datetime
    last_executed: Optional[datetime]
    total_trades: int
    successful_trades: int
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float

@dataclass
class BacktestResult:
    """Backtesting results"""
    strategy_id: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    total_trades: int
    avg_trade_duration: float
    trades: List[Dict[str, Any]]

class AutomatedTradingSystem:
    """Automated trading and strategy management system"""
    
    def __init__(self):
        self.strategies: Dict[str, TradingStrategy] = {}
        self.active_orders: Dict[str, TradingOrder] = {}
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.web3_providers: Dict[str, Web3] = {}
        self._init_exchanges()
        self._init_web3()

    def _init_exchanges(self):
        """Initialize exchange connections"""
        try:
            # Initialize supported exchanges
            if config.get('BINANCE_API_KEY'):
                self.exchanges['binance'] = ccxt.binance({
                    'apiKey': config.get('BINANCE_API_KEY'),
                    'secret': config.get('BINANCE_SECRET'),
                    'sandbox': config.get('TRADING_SANDBOX', True),
                    'enableRateLimit': True
                })
            
            if config.get('COINBASE_API_KEY'):
                # Try new coinbase exchange name, fallback to old coinbasepro
                try:
                    self.exchanges['coinbase'] = ccxt.coinbase({
                        'apiKey': config.get('COINBASE_API_KEY'),
                        'secret': config.get('COINBASE_SECRET'),
                        'passphrase': config.get('COINBASE_PASSPHRASE'),
                        'sandbox': config.get('TRADING_SANDBOX', True),
                        'enableRateLimit': True
                    })
                except AttributeError:
                    try:
                        self.exchanges['coinbase'] = ccxt.coinbasepro({
                            'apiKey': config.get('COINBASE_API_KEY'),
                            'secret': config.get('COINBASE_SECRET'),
                            'passphrase': config.get('COINBASE_PASSPHRASE'),
                            'sandbox': config.get('TRADING_SANDBOX', True),
                            'enableRateLimit': True
                        })
                    except AttributeError:
                        logger.warning("Coinbase exchange not available in ccxt")
                
        except Exception as e:
            logger.warning(f"Failed to initialize exchanges: {e}")

    def _init_web3(self):
        """Initialize Web3 providers for DeFi trading"""
        try:
            self.web3_providers = {
                'ethereum': Web3(Web3.HTTPProvider(config.get('ETHEREUM_RPC_URL', 'https://eth.llamarpc.com'))),
                'polygon': Web3(Web3.HTTPProvider(config.get('POLYGON_RPC_URL', 'https://polygon.llamarpc.com'))),
                'bsc': Web3(Web3.HTTPProvider(config.get('BSC_RPC_URL', 'https://bsc.llamarpc.com')))
            }
        except Exception as e:
            logger.warning(f"Failed to initialize Web3 providers: {e}")

    @track_performance.track_function
    async def create_strategy(self, user_id: int, name: str, strategy_type: str, 
                            parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new trading strategy"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "strategy_create", True, 
                {"strategy_type": strategy_type, "name": name}
            )
            
            # Validate strategy type
            try:
                strategy_enum = StrategyType(strategy_type.lower())
            except ValueError:
                return {"success": False, "message": f"Invalid strategy type: {strategy_type}"}
            
            # Validate parameters
            validation_result = await self._validate_strategy_parameters(strategy_enum, parameters)
            if not validation_result["valid"]:
                return {"success": False, "message": validation_result["message"]}
            
            # Create strategy parameters
            strategy_params = StrategyParameters(
                symbol=parameters.get('symbol', 'BTC/USDT'),
                base_amount=float(parameters.get('base_amount', 100)),
                max_position_size=float(parameters.get('max_position_size', 1000)),
                stop_loss_percent=parameters.get('stop_loss_percent'),
                take_profit_percent=parameters.get('take_profit_percent'),
                rebalance_frequency=parameters.get('rebalance_frequency', 'daily'),
                risk_management=parameters.get('risk_management', {}),
                custom_params=parameters.get('custom_params', {})
            )
            
            # Create strategy
            strategy_id = f"strategy_{user_id}_{int(datetime.now().timestamp())}"
            strategy = TradingStrategy(
                id=strategy_id,
                user_id=user_id,
                name=name,
                strategy_type=strategy_enum,
                status=StrategyStatus.DRAFT,
                parameters=strategy_params,
                performance={
                    'total_return': 0.0,
                    'annual_return': 0.0,
                    'win_rate': 0.0,
                    'profit_factor': 0.0
                },
                created_at=datetime.now(),
                last_executed=None,
                total_trades=0,
                successful_trades=0,
                total_pnl=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0
            )
            
            self.strategies[strategy_id] = strategy
            
            # Save to user data
            user_strategies = json.loads(get_user_property(user_id, 'trading_strategies') or '[]')
            user_strategies.append(strategy_id)
            set_user_property(user_id, 'trading_strategies', json.dumps(user_strategies))
            
            return {
                "success": True,
                "message": "Strategy created successfully",
                "strategy_id": strategy_id,
                "strategy": asdict(strategy)
            }
            
        except Exception as e:
            logger.error(f"Error creating strategy: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def backtest_strategy(self, user_id: int, strategy_id: str, 
                              start_date: str, end_date: str, 
                              initial_capital: float = 10000) -> Dict[str, Any]:
        """Backtest a trading strategy"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "strategy_backtest", True, 
                {"strategy_id": strategy_id}
            )
            
            if strategy_id not in self.strategies:
                return {"success": False, "message": "Strategy not found"}
            
            strategy = self.strategies[strategy_id]
            
            if strategy.user_id != user_id:
                return {"success": False, "message": "Access denied"}
            
            # Update strategy status
            strategy.status = StrategyStatus.BACKTESTING
            
            # Parse dates
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            # Get historical data
            historical_data = await self._get_historical_data(
                strategy.parameters.symbol, start_dt, end_dt
            )
            
            if not historical_data:
                return {"success": False, "message": "Could not fetch historical data"}
            
            # Run backtest
            backtest_result = await self._run_backtest(
                strategy, historical_data, initial_capital
            )
            
            # Update strategy status
            strategy.status = StrategyStatus.DRAFT
            
            return {
                "success": True,
                "backtest_result": asdict(backtest_result),
                "message": "Backtest completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error backtesting strategy: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def deploy_strategy(self, user_id: int, strategy_id: str, 
                            mode: str = "paper") -> Dict[str, Any]:
        """Deploy strategy for paper trading or live trading"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "strategy_deploy", True, 
                {"strategy_id": strategy_id, "mode": mode}
            )
            
            if strategy_id not in self.strategies:
                return {"success": False, "message": "Strategy not found"}
            
            strategy = self.strategies[strategy_id]
            
            if strategy.user_id != user_id:
                return {"success": False, "message": "Access denied"}
            
            # Validate deployment mode
            if mode not in ["paper", "live"]:
                return {"success": False, "message": "Invalid mode. Use 'paper' or 'live'"}
            
            # Additional security checks for live trading
            if mode == "live":
                # Check if user has verified trading permissions
                trading_enabled = get_user_property(user_id, 'trading_enabled')
                if not trading_enabled:
                    return {
                        "success": False, 
                        "message": "Live trading not enabled. Contact support to enable live trading."
                    }
                
                # Check if user has sufficient balance
                balance_check = await self._check_user_balance(user_id, strategy)
                if not balance_check["sufficient"]:
                    return {
                        "success": False,
                        "message": f"Insufficient balance. Required: {balance_check['required']}, Available: {balance_check['available']}"
                    }
            
            # Update strategy status
            if mode == "paper":
                strategy.status = StrategyStatus.PAPER_TRADING
            else:
                strategy.status = StrategyStatus.LIVE
            
            strategy.last_executed = datetime.now()
            
            # Initialize strategy execution
            await self._initialize_strategy_execution(strategy, mode)
            
            return {
                "success": True,
                "message": f"Strategy deployed in {mode} mode",
                "strategy_id": strategy_id,
                "status": strategy.status.value
            }
            
        except Exception as e:
            logger.error(f"Error deploying strategy: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def setup_dca_strategy(self, user_id: int, symbol: str, amount: float, 
                               frequency: str = "daily") -> Dict[str, Any]:
        """Setup Dollar Cost Averaging strategy"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "dca_setup", True, 
                {"symbol": symbol, "amount": amount, "frequency": frequency}
            )
            
            # Create DCA strategy parameters
            parameters = {
                'symbol': symbol,
                'base_amount': amount,
                'max_position_size': amount * 365,  # 1 year worth
                'rebalance_frequency': frequency,
                'custom_params': {
                    'dca_amount': amount,
                    'frequency': frequency,
                    'auto_compound': True
                }
            }
            
            # Create strategy
            result = await self.create_strategy(
                user_id, f"DCA {symbol} ({frequency})", "dca", parameters
            )
            
            if result["success"]:
                # Auto-deploy in paper mode for testing
                deploy_result = await self.deploy_strategy(
                    user_id, result["strategy_id"], "paper"
                )
                
                result["deployment"] = deploy_result
            
            return result
            
        except Exception as e:
            logger.error(f"Error setting up DCA strategy: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def optimize_yield_farming(self, user_id: int) -> Dict[str, Any]:
        """Optimize yield farming positions"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "yield_optimization", True, {}
            )
            
            # Get user's current DeFi positions
            positions = await self._get_user_defi_positions(user_id)
            
            if not positions:
                return {
                    "success": True,
                    "message": "No DeFi positions found",
                    "recommendations": []
                }
            
            # Analyze current yields
            current_yields = await self._analyze_current_yields(positions)
            
            # Find better opportunities
            opportunities = await self._find_yield_opportunities()
            
            # Generate optimization recommendations
            recommendations = await self._generate_yield_recommendations(
                current_yields, opportunities
            )
            
            return {
                "success": True,
                "current_positions": positions,
                "current_yields": current_yields,
                "recommendations": recommendations,
                "potential_improvement": await self._calculate_yield_improvement(
                    current_yields, recommendations
                )
            }
            
        except Exception as e:
            logger.error(f"Error optimizing yield farming: {e}")
            return {"success": False, "message": str(e)}

    async def _validate_strategy_parameters(self, strategy_type: StrategyType, 
                                          parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate strategy parameters"""
        try:
            required_params = {
                StrategyType.DCA: ['symbol', 'base_amount'],
                StrategyType.GRID: ['symbol', 'base_amount', 'grid_levels'],
                StrategyType.MOMENTUM: ['symbol', 'base_amount', 'momentum_period'],
                StrategyType.MEAN_REVERSION: ['symbol', 'base_amount', 'reversion_period'],
                StrategyType.ARBITRAGE: ['symbol', 'exchanges'],
                StrategyType.YIELD_FARMING: ['protocols', 'base_amount'],
                StrategyType.CUSTOM: ['symbol', 'base_amount']
            }
            
            required = required_params.get(strategy_type, [])
            
            for param in required:
                if param not in parameters:
                    return {
                        "valid": False,
                        "message": f"Missing required parameter: {param}"
                    }
            
            # Validate amounts
            if 'base_amount' in parameters:
                try:
                    amount = float(parameters['base_amount'])
                    if amount <= 0:
                        return {
                            "valid": False,
                            "message": "Base amount must be positive"
                        }
                except ValueError:
                    return {
                        "valid": False,
                        "message": "Invalid base amount format"
                    }
            
            return {"valid": True, "message": "Parameters valid"}
            
        except Exception as e:
            logger.error(f"Error validating parameters: {e}")
            return {"valid": False, "message": str(e)}

    async def _get_historical_data(self, symbol: str, start_date: datetime, 
                                 end_date: datetime) -> Optional[pd.DataFrame]:
        """Get historical price data for backtesting"""
        try:
            # Use exchange API to get historical data
            if 'binance' in self.exchanges:
                exchange = self.exchanges['binance']
                
                # Convert dates to timestamps
                since = int(start_date.timestamp() * 1000)
                
                # Fetch OHLCV data
                ohlcv = exchange.fetch_ohlcv(symbol, '1d', since)
                
                # Convert to DataFrame
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                # Filter by end date
                df = df[df.index <= end_date]
                
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return None

    async def _run_backtest(self, strategy: TradingStrategy, 
                          historical_data: pd.DataFrame, 
                          initial_capital: float) -> BacktestResult:
        """Run strategy backtest"""
        try:
            trades = []
            capital = initial_capital
            position = 0
            max_drawdown = 0
            peak_capital = initial_capital
            
            # Strategy-specific backtesting logic
            if strategy.strategy_type == StrategyType.DCA:
                trades, capital, position = await self._backtest_dca(
                    strategy, historical_data, initial_capital
                )
            elif strategy.strategy_type == StrategyType.GRID:
                trades, capital, position = await self._backtest_grid(
                    strategy, historical_data, initial_capital
                )
            # Add other strategy types...
            
            # Calculate performance metrics
            total_return = ((capital - initial_capital) / initial_capital) * 100
            
            # Calculate annual return
            days = (historical_data.index[-1] - historical_data.index[0]).days
            annual_return = ((capital / initial_capital) ** (365 / days) - 1) * 100 if days > 0 else 0
            
            # Calculate max drawdown
            equity_curve = [initial_capital]
            running_capital = initial_capital
            
            for trade in trades:
                running_capital += trade['pnl']
                equity_curve.append(running_capital)
                
                if running_capital > peak_capital:
                    peak_capital = running_capital
                
                drawdown = (peak_capital - running_capital) / peak_capital * 100
                max_drawdown = max(max_drawdown, drawdown)
            
            # Calculate Sharpe ratio (simplified)
            if trades:
                returns = [trade['pnl'] / initial_capital for trade in trades]
                avg_return = np.mean(returns)
                std_return = np.std(returns)
                sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return > 0 else 0
            else:
                sharpe_ratio = 0
            
            # Calculate win rate
            winning_trades = len([t for t in trades if t['pnl'] > 0])
            win_rate = (winning_trades / len(trades)) * 100 if trades else 0
            
            # Calculate average trade duration
            avg_duration = np.mean([
                (trade['exit_time'] - trade['entry_time']).total_seconds() / 3600 
                for trade in trades if 'exit_time' in trade and 'entry_time' in trade
            ]) if trades else 0
            
            return BacktestResult(
                strategy_id=strategy.id,
                start_date=historical_data.index[0],
                end_date=historical_data.index[-1],
                initial_capital=initial_capital,
                final_capital=capital,
                total_return=total_return,
                annual_return=annual_return,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                win_rate=win_rate,
                total_trades=len(trades),
                avg_trade_duration=avg_duration,
                trades=trades
            )
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return BacktestResult(
                strategy_id=strategy.id,
                start_date=datetime.now(),
                end_date=datetime.now(),
                initial_capital=initial_capital,
                final_capital=initial_capital,
                total_return=0,
                annual_return=0,
                max_drawdown=0,
                sharpe_ratio=0,
                win_rate=0,
                total_trades=0,
                avg_trade_duration=0,
                trades=[]
            )

    async def _backtest_dca(self, strategy: TradingStrategy, 
                          historical_data: pd.DataFrame, 
                          initial_capital: float) -> Tuple[List[Dict], float, float]:
        """Backtest DCA strategy"""
        try:
            trades = []
            capital = initial_capital
            position = 0
            dca_amount = strategy.parameters.base_amount
            
            # Simulate DCA purchases
            frequency_days = {
                'daily': 1,
                'weekly': 7,
                'monthly': 30
            }
            
            freq_days = frequency_days.get(strategy.parameters.rebalance_frequency, 7)
            
            for i in range(0, len(historical_data), freq_days):
                if i >= len(historical_data):
                    break
                    
                row = historical_data.iloc[i]
                price = row['close']
                
                if capital >= dca_amount:
                    # Buy
                    shares_bought = dca_amount / price
                    position += shares_bought
                    capital -= dca_amount
                    
                    trades.append({
                        'type': 'buy',
                        'price': price,
                        'amount': shares_bought,
                        'cost': dca_amount,
                        'timestamp': row.name,
                        'entry_time': row.name,
                        'pnl': 0  # Will be calculated at the end
                    })
            
            # Calculate final value
            if position > 0:
                final_price = historical_data.iloc[-1]['close']
                position_value = position * final_price
                capital += position_value
                
                # Calculate PnL for each trade
                for trade in trades:
                    trade['pnl'] = (final_price - trade['price']) * trade['amount']
            
            return trades, capital, position
            
        except Exception as e:
            logger.error(f"Error in DCA backtest: {e}")
            return [], initial_capital, 0

    async def _backtest_grid(self, strategy: TradingStrategy, 
                           historical_data: pd.DataFrame, 
                           initial_capital: float) -> Tuple[List[Dict], float, float]:
        """Backtest Grid strategy"""
        # Placeholder for grid strategy backtesting
        return [], initial_capital, 0

    async def _check_user_balance(self, user_id: int, strategy: TradingStrategy) -> Dict[str, Any]:
        """Check if user has sufficient balance for strategy"""
        try:
            # This would check actual exchange balances
            # For now, return mock data
            required_balance = strategy.parameters.base_amount * 10  # 10x buffer
            available_balance = 1000  # Mock balance
            
            return {
                "sufficient": available_balance >= required_balance,
                "required": required_balance,
                "available": available_balance
            }
            
        except Exception as e:
            logger.error(f"Error checking balance: {e}")
            return {"sufficient": False, "required": 0, "available": 0}

    async def _initialize_strategy_execution(self, strategy: TradingStrategy, mode: str):
        """Initialize strategy for execution"""
        try:
            # Set up periodic execution based on strategy frequency
            # This would typically use a task scheduler like Celery
            logger.info(f"Initialized strategy {strategy.id} in {mode} mode")
            
        except Exception as e:
            logger.error(f"Error initializing strategy execution: {e}")

    async def _get_user_defi_positions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's DeFi positions"""
        try:
            # This would query DeFi protocols for user positions
            # For now, return mock data
            return [
                {
                    "protocol": "Uniswap V3",
                    "pool": "ETH/USDC",
                    "amount": 1000,
                    "current_apy": 5.2
                },
                {
                    "protocol": "Aave",
                    "asset": "USDC",
                    "amount": 5000,
                    "current_apy": 3.8
                }
            ]
            
        except Exception as e:
            logger.error(f"Error getting DeFi positions: {e}")
            return []

    async def _analyze_current_yields(self, positions: List[Dict]) -> Dict[str, Any]:
        """Analyze current yield farming positions"""
        try:
            total_value = sum(pos['amount'] for pos in positions)
            weighted_apy = sum(pos['amount'] * pos['current_apy'] for pos in positions) / total_value if total_value > 0 else 0
            
            return {
                "total_value": total_value,
                "weighted_apy": weighted_apy,
                "positions": positions
            }
            
        except Exception as e:
            logger.error(f"Error analyzing yields: {e}")
            return {}

    async def _find_yield_opportunities(self) -> List[Dict[str, Any]]:
        """Find better yield farming opportunities"""
        try:
            # This would query various DeFi protocols for current yields
            # For now, return mock data
            return [
                {
                    "protocol": "Compound",
                    "asset": "USDC",
                    "apy": 4.5,
                    "risk_score": 2,
                    "liquidity": 50000000
                },
                {
                    "protocol": "Curve",
                    "pool": "3pool",
                    "apy": 6.2,
                    "risk_score": 3,
                    "liquidity": 100000000
                }
            ]
            
        except Exception as e:
            logger.error(f"Error finding opportunities: {e}")
            return []

    async def _generate_yield_recommendations(self, current_yields: Dict, 
                                            opportunities: List[Dict]) -> List[Dict[str, Any]]:
        """Generate yield optimization recommendations"""
        try:
            recommendations = []
            
            for opportunity in opportunities:
                if opportunity['apy'] > current_yields.get('weighted_apy', 0):
                    recommendations.append({
                        "action": "migrate",
                        "from": "current_position",
                        "to": opportunity,
                        "potential_improvement": opportunity['apy'] - current_yields.get('weighted_apy', 0),
                        "risk_assessment": opportunity.get('risk_score', 5)
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    async def _calculate_yield_improvement(self, current_yields: Dict, 
                                         recommendations: List[Dict]) -> Dict[str, Any]:
        """Calculate potential yield improvement"""
        try:
            if not recommendations:
                return {"improvement": 0, "additional_annual_income": 0}
            
            best_recommendation = max(recommendations, key=lambda x: x['potential_improvement'])
            improvement = best_recommendation['potential_improvement']
            
            total_value = current_yields.get('total_value', 0)
            additional_income = (improvement / 100) * total_value
            
            return {
                "improvement": improvement,
                "additional_annual_income": additional_income,
                "best_opportunity": best_recommendation
            }
            
        except Exception as e:
            logger.error(f"Error calculating improvement: {e}")
            return {"improvement": 0, "additional_annual_income": 0}

    def get_user_strategies(self, user_id: int) -> List[TradingStrategy]:
        """Get all strategies for a user"""
        return [strategy for strategy in self.strategies.values() if strategy.user_id == user_id]

    def get_strategy(self, strategy_id: str) -> Optional[TradingStrategy]:
        """Get strategy by ID"""
        return self.strategies.get(strategy_id)

    async def pause_strategy(self, user_id: int, strategy_id: str) -> Dict[str, Any]:
        """Pause a running strategy"""
        try:
            if strategy_id not in self.strategies:
                return {"success": False, "message": "Strategy not found"}
            
            strategy = self.strategies[strategy_id]
            
            if strategy.user_id != user_id:
                return {"success": False, "message": "Access denied"}
            
            strategy.status = StrategyStatus.PAUSED
            
            return {"success": True, "message": "Strategy paused"}
            
        except Exception as e:
            logger.error(f"Error pausing strategy: {e}")
            return {"success": False, "message": str(e)}

    async def stop_strategy(self, user_id: int, strategy_id: str) -> Dict[str, Any]:
        """Stop a running strategy"""
        try:
            if strategy_id not in self.strategies:
                return {"success": False, "message": "Strategy not found"}
            
            strategy = self.strategies[strategy_id]
            
            if strategy.user_id != user_id:
                return {"success": False, "message": "Access denied"}
            
            strategy.status = StrategyStatus.STOPPED
            
            return {"success": True, "message": "Strategy stopped"}
            
        except Exception as e:
            logger.error(f"Error stopping strategy: {e}")
            return {"success": False, "message": str(e)}

# Global instance
automated_trading = AutomatedTradingSystem()