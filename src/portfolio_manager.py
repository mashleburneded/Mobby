# src/portfolio_manager.py
"""
Portfolio Management System for Möbius AI Assistant.
Provides comprehensive portfolio tracking, analysis, and optimization features.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import math

logger = logging.getLogger(__name__)

@dataclass
class Asset:
    symbol: str
    name: str
    amount: float
    price_usd: float
    value_usd: float
    chain: str
    protocol: Optional[str] = None
    asset_type: str = "token"  # token, lp, staked, etc.

@dataclass
class Portfolio:
    user_id: int
    wallets: List[str]
    total_value_usd: float
    assets: List[Asset]
    last_updated: datetime
    performance_24h: float = 0.0
    performance_7d: float = 0.0
    performance_30d: float = 0.0

@dataclass
class PortfolioAnalysis:
    diversification_score: float
    risk_score: float
    yield_opportunities: List[Dict[str, Any]]
    rebalancing_suggestions: List[Dict[str, Any]]
    top_performers: List[Asset]
    underperformers: List[Asset]

class PortfolioManager:
    """
    Advanced portfolio management with real-time tracking, analysis, and optimization.
    Maintains security and performance while providing comprehensive insights.
    """
    
    def __init__(self):
        self.portfolios = {}  # user_id -> Portfolio
        self.price_cache = {}  # symbol -> price data
        self.cache_ttl = 300  # 5 minutes
        self.supported_chains = ["ethereum", "polygon", "arbitrum", "optimism", "bsc"]
        
    async def add_wallet_to_portfolio(self, user_id: int, wallet_address: str) -> Dict[str, Any]:
        """Add wallet to user's portfolio with validation"""
        try:
            # Validate wallet address
            if not self._is_valid_address(wallet_address):
                return {
                    "success": False,
                    "error": "Invalid wallet address format",
                    "suggestions": ["Ensure address starts with 0x and is 42 characters long"]
                }
            
            # Get or create portfolio
            if user_id not in self.portfolios:
                self.portfolios[user_id] = Portfolio(
                    user_id=user_id,
                    wallets=[],
                    total_value_usd=0.0,
                    assets=[],
                    last_updated=datetime.now()
                )
            
            portfolio = self.portfolios[user_id]
            
            # Check if wallet already added
            if wallet_address.lower() in [w.lower() for w in portfolio.wallets]:
                return {
                    "success": False,
                    "error": "Wallet already in portfolio",
                    "current_wallets": len(portfolio.wallets)
                }
            
            # Add wallet and refresh portfolio
            portfolio.wallets.append(wallet_address)
            await self._refresh_portfolio(user_id)
            
            return {
                "success": True,
                "message": f"✅ **Wallet Added Successfully**\n\nAddress: `{wallet_address[:10]}...{wallet_address[-8:]}`\nTotal wallets: {len(portfolio.wallets)}",
                "portfolio_value": portfolio.total_value_usd,
                "asset_count": len(portfolio.assets)
            }
            
        except Exception as e:
            logger.error(f"Failed to add wallet to portfolio: {e}")
            return {
                "success": False,
                "error": "Failed to add wallet",
                "details": str(e)
            }
    
    async def get_portfolio_overview(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive portfolio overview"""
        try:
            if user_id not in self.portfolios:
                return {
                    "success": False,
                    "error": "No portfolio found",
                    "suggestion": "Use `/portfolio add <wallet_address>` to start tracking"
                }
            
            portfolio = self.portfolios[user_id]
            
            # Refresh if data is stale
            if self._is_portfolio_stale(portfolio):
                await self._refresh_portfolio(user_id)
                portfolio = self.portfolios[user_id]
            
            # Calculate portfolio metrics
            metrics = self._calculate_portfolio_metrics(portfolio)
            
            # Generate overview message
            overview_message = self._format_portfolio_overview(portfolio, metrics)
            
            return {
                "success": True,
                "message": overview_message,
                "portfolio": asdict(portfolio),
                "metrics": metrics,
                "last_updated": portfolio.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get portfolio overview: {e}")
            return {
                "success": False,
                "error": "Failed to retrieve portfolio",
                "details": str(e)
            }
    
    async def analyze_portfolio(self, user_id: int) -> Dict[str, Any]:
        """Perform deep portfolio analysis with recommendations"""
        try:
            if user_id not in self.portfolios:
                return {
                    "success": False,
                    "error": "No portfolio found"
                }
            
            portfolio = self.portfolios[user_id]
            
            # Ensure fresh data
            await self._refresh_portfolio(user_id)
            portfolio = self.portfolios[user_id]
            
            # Perform analysis
            analysis = await self._perform_portfolio_analysis(portfolio)
            
            # Generate analysis message
            analysis_message = self._format_portfolio_analysis(analysis)
            
            return {
                "success": True,
                "message": analysis_message,
                "analysis": asdict(analysis),
                "recommendations": self._generate_recommendations(analysis)
            }
            
        except Exception as e:
            logger.error(f"Portfolio analysis failed: {e}")
            return {
                "success": False,
                "error": "Analysis failed",
                "details": str(e)
            }
    
    async def get_rebalancing_suggestions(self, user_id: int, target_allocation: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Generate portfolio rebalancing suggestions"""
        try:
            if user_id not in self.portfolios:
                return {
                    "success": False,
                    "error": "No portfolio found"
                }
            
            portfolio = self.portfolios[user_id]
            
            # Use default allocation if none provided
            if not target_allocation:
                target_allocation = {
                    "BTC": 0.30,
                    "ETH": 0.25,
                    "Stablecoins": 0.20,
                    "DeFi": 0.15,
                    "Other": 0.10
                }
            
            # Calculate current allocation
            current_allocation = self._calculate_current_allocation(portfolio)
            
            # Generate rebalancing suggestions
            suggestions = self._generate_rebalancing_suggestions(
                portfolio, current_allocation, target_allocation
            )
            
            # Format suggestions message
            suggestions_message = self._format_rebalancing_suggestions(
                current_allocation, target_allocation, suggestions
            )
            
            return {
                "success": True,
                "message": suggestions_message,
                "current_allocation": current_allocation,
                "target_allocation": target_allocation,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Rebalancing suggestions failed: {e}")
            return {
                "success": False,
                "error": "Failed to generate suggestions",
                "details": str(e)
            }
    
    async def _refresh_portfolio(self, user_id: int):
        """Refresh portfolio data from blockchain and price feeds"""
        portfolio = self.portfolios[user_id]
        all_assets = []
        total_value = 0.0
        
        for wallet_address in portfolio.wallets:
            # Get assets for each wallet across all supported chains
            for chain in self.supported_chains:
                try:
                    assets = await self._get_wallet_assets(wallet_address, chain)
                    all_assets.extend(assets)
                except Exception as e:
                    logger.warning(f"Failed to get assets for {wallet_address} on {chain}: {e}")
        
        # Consolidate duplicate assets
        consolidated_assets = self._consolidate_assets(all_assets)
        
        # Update prices and calculate values
        for asset in consolidated_assets:
            price = await self._get_asset_price(asset.symbol)
            asset.price_usd = price
            asset.value_usd = asset.amount * price
            total_value += asset.value_usd
        
        # Calculate performance
        performance_24h, performance_7d, performance_30d = await self._calculate_performance(
            user_id, consolidated_assets
        )
        
        # Update portfolio
        portfolio.assets = consolidated_assets
        portfolio.total_value_usd = total_value
        portfolio.last_updated = datetime.now()
        portfolio.performance_24h = performance_24h
        portfolio.performance_7d = performance_7d
        portfolio.performance_30d = performance_30d
    
    async def _get_wallet_assets(self, wallet_address: str, chain: str) -> List[Asset]:
        """Get assets for a specific wallet on a specific chain"""
        # This would integrate with actual blockchain APIs
        # For now, return mock data for demonstration
        
        mock_assets = [
            Asset(
                symbol="ETH",
                name="Ethereum",
                amount=2.5,
                price_usd=2000.0,
                value_usd=5000.0,
                chain=chain,
                asset_type="token"
            ),
            Asset(
                symbol="USDC",
                name="USD Coin",
                amount=1000.0,
                price_usd=1.0,
                value_usd=1000.0,
                chain=chain,
                asset_type="token"
            )
        ]
        
        return mock_assets
    
    async def _get_asset_price(self, symbol: str) -> float:
        """Get current asset price with caching"""
        cache_key = f"price_{symbol}"
        current_time = datetime.now()
        
        # Check cache
        if cache_key in self.price_cache:
            cached_data = self.price_cache[cache_key]
            if (current_time - cached_data["timestamp"]).seconds < self.cache_ttl:
                return cached_data["price"]
        
        # Fetch new price (mock implementation)
        price_map = {
            "ETH": 2000.0,
            "BTC": 45000.0,
            "USDC": 1.0,
            "USDT": 1.0,
            "DAI": 1.0,
            "UNI": 25.0,
            "AAVE": 150.0,
            "LINK": 15.0
        }
        
        price = price_map.get(symbol.upper(), 1.0)
        
        # Cache the price
        self.price_cache[cache_key] = {
            "price": price,
            "timestamp": current_time
        }
        
        return price
    
    def _consolidate_assets(self, assets: List[Asset]) -> List[Asset]:
        """Consolidate duplicate assets across chains"""
        consolidated = {}
        
        for asset in assets:
            key = f"{asset.symbol}_{asset.asset_type}"
            
            if key in consolidated:
                # Combine amounts
                consolidated[key].amount += asset.amount
            else:
                consolidated[key] = asset
        
        return list(consolidated.values())
    
    async def _calculate_performance(self, user_id: int, assets: List[Asset]) -> Tuple[float, float, float]:
        """Calculate portfolio performance over different timeframes"""
        # This would use historical price data
        # For now, return mock performance data
        return 5.2, 12.8, -3.1  # 24h, 7d, 30d performance percentages
    
    def _calculate_portfolio_metrics(self, portfolio: Portfolio) -> Dict[str, Any]:
        """Calculate various portfolio metrics"""
        if not portfolio.assets:
            return {}
        
        # Asset allocation
        allocation = {}
        for asset in portfolio.assets:
            allocation[asset.symbol] = (asset.value_usd / portfolio.total_value_usd) * 100
        
        # Top holdings
        top_holdings = sorted(portfolio.assets, key=lambda x: x.value_usd, reverse=True)[:5]
        
        # Chain distribution
        chain_distribution = {}
        for asset in portfolio.assets:
            chain = asset.chain
            if chain in chain_distribution:
                chain_distribution[chain] += asset.value_usd
            else:
                chain_distribution[chain] = asset.value_usd
        
        # Convert to percentages
        for chain in chain_distribution:
            chain_distribution[chain] = (chain_distribution[chain] / portfolio.total_value_usd) * 100
        
        return {
            "asset_count": len(portfolio.assets),
            "allocation": allocation,
            "top_holdings": [asdict(asset) for asset in top_holdings],
            "chain_distribution": chain_distribution,
            "performance": {
                "24h": portfolio.performance_24h,
                "7d": portfolio.performance_7d,
                "30d": portfolio.performance_30d
            }
        }
    
    async def _perform_portfolio_analysis(self, portfolio: Portfolio) -> PortfolioAnalysis:
        """Perform comprehensive portfolio analysis"""
        # Calculate diversification score
        diversification_score = self._calculate_diversification_score(portfolio)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(portfolio)
        
        # Find yield opportunities
        yield_opportunities = await self._find_yield_opportunities(portfolio)
        
        # Generate rebalancing suggestions
        rebalancing_suggestions = self._generate_basic_rebalancing_suggestions(portfolio)
        
        # Identify top performers and underperformers
        sorted_assets = sorted(portfolio.assets, key=lambda x: x.value_usd, reverse=True)
        top_performers = sorted_assets[:3]
        underperformers = sorted_assets[-3:] if len(sorted_assets) > 3 else []
        
        return PortfolioAnalysis(
            diversification_score=diversification_score,
            risk_score=risk_score,
            yield_opportunities=yield_opportunities,
            rebalancing_suggestions=rebalancing_suggestions,
            top_performers=top_performers,
            underperformers=underperformers
        )
    
    def _calculate_diversification_score(self, portfolio: Portfolio) -> float:
        """Calculate portfolio diversification score (0-100)"""
        if not portfolio.assets:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index
        total_value = portfolio.total_value_usd
        hhi = sum((asset.value_usd / total_value) ** 2 for asset in portfolio.assets)
        
        # Convert to diversification score (higher is better)
        max_hhi = 1.0  # Completely concentrated
        min_hhi = 1.0 / len(portfolio.assets)  # Perfectly diversified
        
        if max_hhi == min_hhi:
            return 100.0
        
        diversification_score = ((max_hhi - hhi) / (max_hhi - min_hhi)) * 100
        return round(diversification_score, 1)
    
    def _calculate_risk_score(self, portfolio: Portfolio) -> float:
        """Calculate portfolio risk score (0-100, higher is riskier)"""
        if not portfolio.assets:
            return 0.0
        
        # Simple risk scoring based on asset types and allocation
        risk_weights = {
            "BTC": 0.3,
            "ETH": 0.4,
            "USDC": 0.1,
            "USDT": 0.1,
            "DAI": 0.1,
            "UNI": 0.7,
            "AAVE": 0.6,
            "LINK": 0.6
        }
        
        total_value = portfolio.total_value_usd
        weighted_risk = 0.0
        
        for asset in portfolio.assets:
            weight = asset.value_usd / total_value
            asset_risk = risk_weights.get(asset.symbol, 0.8)  # Default high risk for unknown assets
            weighted_risk += weight * asset_risk
        
        return round(weighted_risk * 100, 1)
    
    async def _find_yield_opportunities(self, portfolio: Portfolio) -> List[Dict[str, Any]]:
        """Find yield farming and staking opportunities"""
        opportunities = []
        
        for asset in portfolio.assets:
            if asset.symbol in ["ETH", "USDC", "DAI", "USDT"]:
                # Mock yield opportunities
                if asset.symbol == "ETH":
                    opportunities.append({
                        "asset": asset.symbol,
                        "protocol": "Lido",
                        "apy": 4.2,
                        "type": "staking",
                        "risk": "low"
                    })
                elif asset.symbol in ["USDC", "DAI", "USDT"]:
                    opportunities.append({
                        "asset": asset.symbol,
                        "protocol": "Aave",
                        "apy": 3.8,
                        "type": "lending",
                        "risk": "low"
                    })
        
        return opportunities
    
    def _generate_basic_rebalancing_suggestions(self, portfolio: Portfolio) -> List[Dict[str, Any]]:
        """Generate basic rebalancing suggestions"""
        suggestions = []
        
        # Check for over-concentration
        total_value = portfolio.total_value_usd
        for asset in portfolio.assets:
            allocation_pct = (asset.value_usd / total_value) * 100
            
            if allocation_pct > 50:
                suggestions.append({
                    "type": "reduce_concentration",
                    "asset": asset.symbol,
                    "current_allocation": allocation_pct,
                    "suggested_allocation": 30.0,
                    "reason": "Over-concentrated position"
                })
        
        return suggestions
    
    def _format_portfolio_overview(self, portfolio: Portfolio, metrics: Dict[str, Any]) -> str:
        """Format portfolio overview message"""
        performance_24h = portfolio.performance_24h
        performance_emoji = "📈" if performance_24h >= 0 else "📉"
        
        message = f"""💼 **Portfolio Overview**

💰 **Total Value:** ${portfolio.total_value_usd:,.2f}
{performance_emoji} **24h Change:** {performance_24h:+.2f}%
📊 **7d Change:** {portfolio.performance_7d:+.2f}%
📈 **30d Change:** {portfolio.performance_30d:+.2f}%

🏦 **Wallets Tracked:** {len(portfolio.wallets)}
🪙 **Assets:** {len(portfolio.assets)}

**🔝 Top Holdings:**"""
        
        for i, asset in enumerate(metrics.get("top_holdings", [])[:3], 1):
            allocation = (asset["value_usd"] / portfolio.total_value_usd) * 100
            message += f"\n{i}. {asset['symbol']}: ${asset['value_usd']:,.2f} ({allocation:.1f}%)"
        
        message += f"\n\n📅 **Last Updated:** {portfolio.last_updated.strftime('%Y-%m-%d %H:%M UTC')}"
        
        return message
    
    def _format_portfolio_analysis(self, analysis: PortfolioAnalysis) -> str:
        """Format portfolio analysis message"""
        message = f"""🔍 **Portfolio Analysis**

📊 **Diversification Score:** {analysis.diversification_score}/100
⚠️ **Risk Score:** {analysis.risk_score}/100

**🎯 Top Performers:**"""
        
        for asset in analysis.top_performers[:3]:
            message += f"\n• {asset.symbol}: ${asset.value_usd:,.2f}"
        
        if analysis.yield_opportunities:
            message += "\n\n**💰 Yield Opportunities:**"
            for opp in analysis.yield_opportunities[:3]:
                message += f"\n• {opp['asset']} on {opp['protocol']}: {opp['apy']:.1f}% APY"
        
        if analysis.rebalancing_suggestions:
            message += "\n\n**⚖️ Rebalancing Suggestions:**"
            for suggestion in analysis.rebalancing_suggestions[:2]:
                message += f"\n• Reduce {suggestion['asset']} from {suggestion['current_allocation']:.1f}% to {suggestion['suggested_allocation']:.1f}%"
        
        return message
    
    def _is_valid_address(self, address: str) -> bool:
        """Validate Ethereum address format"""
        return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))
    
    def _is_portfolio_stale(self, portfolio: Portfolio) -> bool:
        """Check if portfolio data is stale"""
        return (datetime.now() - portfolio.last_updated).seconds > self.cache_ttl
    
    def _calculate_current_allocation(self, portfolio: Portfolio) -> Dict[str, float]:
        """Calculate current asset allocation"""
        allocation = {}
        total_value = portfolio.total_value_usd
        
        for asset in portfolio.assets:
            category = self._categorize_asset(asset.symbol)
            if category in allocation:
                allocation[category] += (asset.value_usd / total_value) * 100
            else:
                allocation[category] = (asset.value_usd / total_value) * 100
        
        return allocation
    
    def _categorize_asset(self, symbol: str) -> str:
        """Categorize asset into major categories"""
        categories = {
            "BTC": "BTC",
            "ETH": "ETH",
            "USDC": "Stablecoins",
            "USDT": "Stablecoins",
            "DAI": "Stablecoins",
            "UNI": "DeFi",
            "AAVE": "DeFi",
            "COMP": "DeFi",
            "LINK": "DeFi"
        }
        return categories.get(symbol.upper(), "Other")
    
    def _generate_rebalancing_suggestions(self, portfolio: Portfolio, current: Dict[str, float], target: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate specific rebalancing suggestions"""
        suggestions = []
        
        for category, target_pct in target.items():
            current_pct = current.get(category, 0.0)
            difference = target_pct - current_pct
            
            if abs(difference) > 5.0:  # Only suggest if difference > 5%
                action = "increase" if difference > 0 else "decrease"
                suggestions.append({
                    "category": category,
                    "action": action,
                    "current_allocation": current_pct,
                    "target_allocation": target_pct,
                    "difference": abs(difference),
                    "amount_usd": abs(difference / 100) * portfolio.total_value_usd
                })
        
        return sorted(suggestions, key=lambda x: x["difference"], reverse=True)
    
    def _format_rebalancing_suggestions(self, current: Dict[str, float], target: Dict[str, float], suggestions: List[Dict[str, Any]]) -> str:
        """Format rebalancing suggestions message"""
        message = "⚖️ **Portfolio Rebalancing Suggestions**\n\n"
        
        message += "**Current vs Target Allocation:**\n"
        for category, target_pct in target.items():
            current_pct = current.get(category, 0.0)
            message += f"• {category}: {current_pct:.1f}% → {target_pct:.1f}%\n"
        
        if suggestions:
            message += "\n**🎯 Recommended Actions:**\n"
            for suggestion in suggestions[:3]:
                action_emoji = "📈" if suggestion["action"] == "increase" else "📉"
                message += f"{action_emoji} {suggestion['action'].title()} {suggestion['category']} by {suggestion['difference']:.1f}% (${suggestion['amount_usd']:,.0f})\n"
        else:
            message += "\n✅ **Portfolio is well-balanced!**"
        
        return message
    
    def _generate_recommendations(self, analysis: PortfolioAnalysis) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if analysis.diversification_score < 50:
            recommendations.append("Consider diversifying across more assets to reduce risk")
        
        if analysis.risk_score > 70:
            recommendations.append("Portfolio has high risk - consider adding stablecoins")
        
        if analysis.yield_opportunities:
            recommendations.append("Explore yield farming opportunities to increase returns")
        
        if analysis.rebalancing_suggestions:
            recommendations.append("Rebalance portfolio to optimize allocation")
        
        return recommendations

# Global portfolio manager instance
portfolio_manager = PortfolioManager()