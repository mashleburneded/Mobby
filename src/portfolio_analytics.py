"""
Advanced Portfolio Analytics for Möbius AI Assistant
Provides comprehensive portfolio analysis, risk metrics, and rebalancing suggestions
"""
import logging
import numpy as np
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from config import config

logger = logging.getLogger(__name__)

@dataclass
class AssetHolding:
    symbol: str
    amount: float
    current_price: float
    value_usd: float
    allocation_percent: float
    
@dataclass
class PortfolioMetrics:
    total_value: float
    daily_pnl: float
    daily_pnl_percent: float
    sharpe_ratio: float
    volatility: float
    max_drawdown: float
    var_95: float  # Value at Risk 95%
    
@dataclass
class RebalanceRecommendation:
    asset: str
    current_allocation: float
    target_allocation: float
    action: str  # "buy", "sell", "hold"
    amount_change: float
    reason: str

class PortfolioAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.price_cache = {}
        
    async def get_asset_price(self, symbol: str) -> float:
        """Get current price for an asset"""
        if symbol in self.price_cache:
            cache_time, price = self.price_cache[symbol]
            if datetime.now() - cache_time < timedelta(minutes=5):
                return price
        
        try:
            # Use CoinGecko API for price data
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": symbol.lower(), "vs_currencies": "usd"}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            price = data.get(symbol.lower(), {}).get('usd', 0)
            self.price_cache[symbol] = (datetime.now(), price)
            return price
        except Exception as e:
            self.logger.error(f"Failed to get price for {symbol}: {e}")
            return 0.0
    
    async def get_historical_prices(self, symbol: str, days: int = 30) -> List[float]:
        """Get historical prices for volatility calculation"""
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}/market_chart"
            params = {"vs_currency": "usd", "days": days}
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            prices = [price[1] for price in data.get('prices', [])]
            return prices
        except Exception as e:
            self.logger.error(f"Failed to get historical prices for {symbol}: {e}")
            return []
    
    def calculate_portfolio_metrics(self, holdings: List[AssetHolding], historical_data: Dict[str, List[float]]) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics"""
        total_value = sum(holding.value_usd for holding in holdings)
        
        # Calculate portfolio returns from historical data
        portfolio_returns = []
        if historical_data:
            min_length = min(len(prices) for prices in historical_data.values() if prices)
            if min_length > 1:
                for i in range(1, min_length):
                    portfolio_value_prev = 0
                    portfolio_value_curr = 0
                    
                    for holding in holdings:
                        if holding.symbol.lower() in historical_data:
                            prices = historical_data[holding.symbol.lower()]
                            if len(prices) > i:
                                portfolio_value_prev += holding.amount * prices[i-1]
                                portfolio_value_curr += holding.amount * prices[i]
                    
                    if portfolio_value_prev > 0:
                        daily_return = (portfolio_value_curr - portfolio_value_prev) / portfolio_value_prev
                        portfolio_returns.append(daily_return)
        
        # Calculate metrics
        if portfolio_returns:
            returns_array = np.array(portfolio_returns)
            daily_pnl_percent = returns_array[-1] if len(returns_array) > 0 else 0
            volatility = np.std(returns_array) * np.sqrt(365)  # Annualized
            sharpe_ratio = np.mean(returns_array) / np.std(returns_array) * np.sqrt(365) if np.std(returns_array) > 0 else 0
            
            # Calculate max drawdown
            cumulative_returns = np.cumprod(1 + returns_array)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdown)
            
            # Calculate VaR (95% confidence)
            var_95 = np.percentile(returns_array, 5) * total_value
        else:
            daily_pnl_percent = 0
            volatility = 0
            sharpe_ratio = 0
            max_drawdown = 0
            var_95 = 0
        
        daily_pnl = daily_pnl_percent * total_value
        
        return PortfolioMetrics(
            total_value=total_value,
            daily_pnl=daily_pnl,
            daily_pnl_percent=daily_pnl_percent,
            sharpe_ratio=sharpe_ratio,
            volatility=volatility,
            max_drawdown=max_drawdown,
            var_95=var_95
        )
    
    def generate_rebalancing_suggestions(self, holdings: List[AssetHolding], target_allocations: Dict[str, float]) -> List[RebalanceRecommendation]:
        """Generate portfolio rebalancing recommendations"""
        recommendations = []
        total_value = sum(holding.value_usd for holding in holdings)
        
        # Current allocations
        current_allocations = {holding.symbol: holding.allocation_percent for holding in holdings}
        
        for symbol, target_percent in target_allocations.items():
            current_percent = current_allocations.get(symbol, 0)
            difference = target_percent - current_percent
            
            if abs(difference) > 1:  # Only suggest if difference > 1%
                action = "buy" if difference > 0 else "sell"
                amount_change = abs(difference) * total_value / 100
                
                reason = f"Rebalance to target allocation of {target_percent:.1f}%"
                if difference > 5:
                    reason += " (significantly underweight)"
                elif difference < -5:
                    reason += " (significantly overweight)"
                
                recommendations.append(RebalanceRecommendation(
                    asset=symbol,
                    current_allocation=current_percent,
                    target_allocation=target_percent,
                    action=action,
                    amount_change=amount_change,
                    reason=reason
                ))
        
        # Sort by magnitude of change needed
        recommendations.sort(key=lambda x: abs(x.target_allocation - x.current_allocation), reverse=True)
        return recommendations
    
    def analyze_asset_correlation(self, historical_data: Dict[str, List[float]]) -> Dict[Tuple[str, str], float]:
        """Calculate correlation matrix between assets"""
        correlations = {}
        symbols = list(historical_data.keys())
        
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols[i+1:], i+1):
                prices1 = historical_data[symbol1]
                prices2 = historical_data[symbol2]
                
                if len(prices1) > 1 and len(prices2) > 1:
                    min_length = min(len(prices1), len(prices2))
                    returns1 = np.diff(prices1[:min_length]) / prices1[:min_length-1]
                    returns2 = np.diff(prices2[:min_length]) / prices2[:min_length-1]
                    
                    if len(returns1) > 0 and len(returns2) > 0:
                        correlation = np.corrcoef(returns1, returns2)[0, 1]
                        correlations[(symbol1, symbol2)] = correlation
        
        return correlations
    
    def detect_risk_factors(self, holdings: List[AssetHolding], metrics: PortfolioMetrics) -> List[str]:
        """Detect potential risk factors in the portfolio"""
        risks = []
        
        # Concentration risk
        for holding in holdings:
            if holding.allocation_percent > 50:
                risks.append(f"High concentration risk: {holding.symbol} represents {holding.allocation_percent:.1f}% of portfolio")
        
        # Volatility risk
        if metrics.volatility > 1.0:  # 100% annualized volatility
            risks.append(f"High volatility: {metrics.volatility:.1%} annualized")
        
        # Drawdown risk
        if metrics.max_drawdown < -0.3:  # 30% drawdown
            risks.append(f"Significant drawdown risk: {metrics.max_drawdown:.1%} max drawdown")
        
        # VaR risk
        if abs(metrics.var_95) > metrics.total_value * 0.1:  # 10% daily VaR
            risks.append(f"High daily risk: ${abs(metrics.var_95):,.0f} potential daily loss (95% confidence)")
        
        return risks

# Global instance
portfolio_analyzer = PortfolioAnalyzer()