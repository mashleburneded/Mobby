# src/tier_access_control.py
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class SubscriptionTier(Enum):
    FREE = "free"
    RETAIL = "retail"
    CORPORATE = "corporate"

@dataclass
class FeatureLimit:
    """Represents limits for a specific feature"""
    enabled: bool
    daily_limit: Optional[int] = None
    monthly_limit: Optional[int] = None
    max_concurrent: Optional[int] = None
    advanced_features: bool = False

@dataclass
class TierLimits:
    """Complete tier limitations"""
    # Portfolio Management
    portfolio_tracking: FeatureLimit
    portfolio_analytics: FeatureLimit
    portfolio_rebalancing: FeatureLimit
    
    # Alerts
    price_alerts: FeatureLimit
    technical_alerts: FeatureLimit
    whale_alerts: FeatureLimit
    sentiment_alerts: FeatureLimit
    
    # Research & Analysis
    token_research: FeatureLimit
    technical_analysis: FeatureLimit
    fundamental_analysis: FeatureLimit
    ai_insights: FeatureLimit
    
    # Trading
    paper_trading: FeatureLimit
    live_trading: FeatureLimit
    strategy_backtesting: FeatureLimit
    automated_strategies: FeatureLimit
    
    # Social Trading
    signal_publishing: FeatureLimit
    signal_following: FeatureLimit
    leaderboard_access: FeatureLimit
    
    # Cross-Chain
    multichain_portfolio: FeatureLimit
    bridge_tracking: FeatureLimit
    arbitrage_scanning: FeatureLimit
    gas_optimization: FeatureLimit
    
    # Natural Language
    nlp_queries: FeatureLimit
    ai_conversations: FeatureLimit
    
    # Enterprise
    api_access: FeatureLimit
    team_management: FeatureLimit
    compliance_reports: FeatureLimit
    priority_support: FeatureLimit

class TierAccessControl:
    """Manages tier-based access control for all features"""
    
    def __init__(self):
        self.tier_limits = self._initialize_tier_limits()
        
    def _initialize_tier_limits(self) -> Dict[SubscriptionTier, TierLimits]:
        """Initialize tier limits for all subscription levels"""
        
        # FREE TIER - Limited functionality
        free_limits = TierLimits(
            # Portfolio Management - Basic only
            portfolio_tracking=FeatureLimit(enabled=True, daily_limit=5),
            portfolio_analytics=FeatureLimit(enabled=False),
            portfolio_rebalancing=FeatureLimit(enabled=False),
            
            # Alerts - Very limited
            price_alerts=FeatureLimit(enabled=True, daily_limit=3, max_concurrent=3),
            technical_alerts=FeatureLimit(enabled=False),
            whale_alerts=FeatureLimit(enabled=False),
            sentiment_alerts=FeatureLimit(enabled=False),
            
            # Research & Analysis - Basic only
            token_research=FeatureLimit(enabled=True, daily_limit=5),
            technical_analysis=FeatureLimit(enabled=True, daily_limit=3),
            fundamental_analysis=FeatureLimit(enabled=False),
            ai_insights=FeatureLimit(enabled=True, daily_limit=3),
            
            # Trading - Paper only
            paper_trading=FeatureLimit(enabled=True, daily_limit=5),
            live_trading=FeatureLimit(enabled=False),
            strategy_backtesting=FeatureLimit(enabled=True, daily_limit=2),
            automated_strategies=FeatureLimit(enabled=False),
            
            # Social Trading - View only
            signal_publishing=FeatureLimit(enabled=False),
            signal_following=FeatureLimit(enabled=True, max_concurrent=3),
            leaderboard_access=FeatureLimit(enabled=True),
            
            # Cross-Chain - Limited
            multichain_portfolio=FeatureLimit(enabled=True, daily_limit=3),
            bridge_tracking=FeatureLimit(enabled=True, daily_limit=2),
            arbitrage_scanning=FeatureLimit(enabled=False),
            gas_optimization=FeatureLimit(enabled=True, daily_limit=5),
            
            # Natural Language - Limited
            nlp_queries=FeatureLimit(enabled=True, daily_limit=10),
            ai_conversations=FeatureLimit(enabled=True, daily_limit=5),
            
            # Enterprise - None
            api_access=FeatureLimit(enabled=False),
            team_management=FeatureLimit(enabled=False),
            compliance_reports=FeatureLimit(enabled=False),
            priority_support=FeatureLimit(enabled=False)
        )
        
        # RETAIL TIER - Enhanced functionality
        retail_limits = TierLimits(
            # Portfolio Management - Full access
            portfolio_tracking=FeatureLimit(enabled=True, daily_limit=50),
            portfolio_analytics=FeatureLimit(enabled=True, daily_limit=20),
            portfolio_rebalancing=FeatureLimit(enabled=True, daily_limit=5),
            
            # Alerts - Enhanced
            price_alerts=FeatureLimit(enabled=True, daily_limit=50, max_concurrent=50),
            technical_alerts=FeatureLimit(enabled=True, daily_limit=20, max_concurrent=20),
            whale_alerts=FeatureLimit(enabled=True, daily_limit=10, max_concurrent=10),
            sentiment_alerts=FeatureLimit(enabled=True, daily_limit=10, max_concurrent=10),
            
            # Research & Analysis - Advanced
            token_research=FeatureLimit(enabled=True, daily_limit=50, advanced_features=True),
            technical_analysis=FeatureLimit(enabled=True, daily_limit=30, advanced_features=True),
            fundamental_analysis=FeatureLimit(enabled=True, daily_limit=20),
            ai_insights=FeatureLimit(enabled=True, daily_limit=30, advanced_features=True),
            
            # Trading - Full paper, limited live
            paper_trading=FeatureLimit(enabled=True, daily_limit=100),
            live_trading=FeatureLimit(enabled=True, daily_limit=20),
            strategy_backtesting=FeatureLimit(enabled=True, daily_limit=20),
            automated_strategies=FeatureLimit(enabled=True, max_concurrent=3),
            
            # Social Trading - Full access
            signal_publishing=FeatureLimit(enabled=True, daily_limit=10),
            signal_following=FeatureLimit(enabled=True, max_concurrent=20),
            leaderboard_access=FeatureLimit(enabled=True, advanced_features=True),
            
            # Cross-Chain - Enhanced
            multichain_portfolio=FeatureLimit(enabled=True, daily_limit=50),
            bridge_tracking=FeatureLimit(enabled=True, daily_limit=20),
            arbitrage_scanning=FeatureLimit(enabled=True, daily_limit=10),
            gas_optimization=FeatureLimit(enabled=True, daily_limit=50),
            
            # Natural Language - Enhanced
            nlp_queries=FeatureLimit(enabled=True, daily_limit=100),
            ai_conversations=FeatureLimit(enabled=True, daily_limit=50),
            
            # Enterprise - Limited
            api_access=FeatureLimit(enabled=True, daily_limit=1000),
            team_management=FeatureLimit(enabled=False),
            compliance_reports=FeatureLimit(enabled=False),
            priority_support=FeatureLimit(enabled=True)
        )
        
        # CORPORATE TIER - Unlimited functionality
        corporate_limits = TierLimits(
            # Portfolio Management - Unlimited
            portfolio_tracking=FeatureLimit(enabled=True),
            portfolio_analytics=FeatureLimit(enabled=True, advanced_features=True),
            portfolio_rebalancing=FeatureLimit(enabled=True, advanced_features=True),
            
            # Alerts - Unlimited
            price_alerts=FeatureLimit(enabled=True, advanced_features=True),
            technical_alerts=FeatureLimit(enabled=True, advanced_features=True),
            whale_alerts=FeatureLimit(enabled=True, advanced_features=True),
            sentiment_alerts=FeatureLimit(enabled=True, advanced_features=True),
            
            # Research & Analysis - Full advanced
            token_research=FeatureLimit(enabled=True, advanced_features=True),
            technical_analysis=FeatureLimit(enabled=True, advanced_features=True),
            fundamental_analysis=FeatureLimit(enabled=True, advanced_features=True),
            ai_insights=FeatureLimit(enabled=True, advanced_features=True),
            
            # Trading - Unlimited
            paper_trading=FeatureLimit(enabled=True),
            live_trading=FeatureLimit(enabled=True, advanced_features=True),
            strategy_backtesting=FeatureLimit(enabled=True, advanced_features=True),
            automated_strategies=FeatureLimit(enabled=True, advanced_features=True),
            
            # Social Trading - Full advanced
            signal_publishing=FeatureLimit(enabled=True, advanced_features=True),
            signal_following=FeatureLimit(enabled=True, advanced_features=True),
            leaderboard_access=FeatureLimit(enabled=True, advanced_features=True),
            
            # Cross-Chain - Unlimited
            multichain_portfolio=FeatureLimit(enabled=True, advanced_features=True),
            bridge_tracking=FeatureLimit(enabled=True, advanced_features=True),
            arbitrage_scanning=FeatureLimit(enabled=True, advanced_features=True),
            gas_optimization=FeatureLimit(enabled=True, advanced_features=True),
            
            # Natural Language - Unlimited
            nlp_queries=FeatureLimit(enabled=True, advanced_features=True),
            ai_conversations=FeatureLimit(enabled=True, advanced_features=True),
            
            # Enterprise - Full access
            api_access=FeatureLimit(enabled=True, advanced_features=True),
            team_management=FeatureLimit(enabled=True, advanced_features=True),
            compliance_reports=FeatureLimit(enabled=True, advanced_features=True),
            priority_support=FeatureLimit(enabled=True, advanced_features=True)
        )
        
        return {
            SubscriptionTier.FREE: free_limits,
            SubscriptionTier.RETAIL: retail_limits,
            SubscriptionTier.CORPORATE: corporate_limits
        }
    
    def check_feature_access(self, tier: str, feature: str) -> Dict[str, Any]:
        """Check if user has access to a specific feature"""
        try:
            subscription_tier = SubscriptionTier(tier.lower())
            tier_limits = self.tier_limits[subscription_tier]
            
            # Get feature limit
            feature_limit = getattr(tier_limits, feature, None)
            
            if not feature_limit:
                return {
                    "allowed": False,
                    "reason": "Feature not found",
                    "upgrade_required": True
                }
            
            if not feature_limit.enabled:
                return {
                    "allowed": False,
                    "reason": f"Feature not available in {tier} tier",
                    "upgrade_required": True,
                    "available_in": self._get_feature_availability(feature)
                }
            
            return {
                "allowed": True,
                "limits": {
                    "daily_limit": feature_limit.daily_limit,
                    "monthly_limit": feature_limit.monthly_limit,
                    "max_concurrent": feature_limit.max_concurrent,
                    "advanced_features": feature_limit.advanced_features
                }
            }
            
        except ValueError:
            return {
                "allowed": False,
                "reason": "Invalid tier",
                "upgrade_required": False
            }
        except Exception as e:
            logger.error(f"Error checking feature access: {e}")
            return {
                "allowed": False,
                "reason": "Access check failed",
                "upgrade_required": False
            }
    
    def get_tier_comparison(self) -> Dict[str, Any]:
        """Get comparison of all tiers"""
        comparison = {}
        
        for tier, limits in self.tier_limits.items():
            tier_features = {}
            
            # Get all features and their limits
            for feature_name in dir(limits):
                if not feature_name.startswith('_'):
                    feature_limit = getattr(limits, feature_name)
                    if isinstance(feature_limit, FeatureLimit):
                        tier_features[feature_name] = {
                            "enabled": feature_limit.enabled,
                            "daily_limit": feature_limit.daily_limit,
                            "monthly_limit": feature_limit.monthly_limit,
                            "max_concurrent": feature_limit.max_concurrent,
                            "advanced_features": feature_limit.advanced_features
                        }
            
            comparison[tier.value] = tier_features
        
        return comparison
    
    def _get_feature_availability(self, feature: str) -> List[str]:
        """Get which tiers have access to a feature"""
        available_tiers = []
        
        for tier, limits in self.tier_limits.items():
            feature_limit = getattr(limits, feature, None)
            if feature_limit and feature_limit.enabled:
                available_tiers.append(tier.value)
        
        return available_tiers
    
    def get_upgrade_benefits(self, current_tier: str, target_tier: str) -> Dict[str, Any]:
        """Get benefits of upgrading from current to target tier"""
        try:
            current = SubscriptionTier(current_tier.lower())
            target = SubscriptionTier(target_tier.lower())
            
            current_limits = self.tier_limits[current]
            target_limits = self.tier_limits[target]
            
            benefits = []
            
            # Compare all features
            for feature_name in dir(target_limits):
                if not feature_name.startswith('_'):
                    current_feature = getattr(current_limits, feature_name)
                    target_feature = getattr(target_limits, feature_name)
                    
                    if isinstance(target_feature, FeatureLimit):
                        # Check if feature becomes available
                        if not current_feature.enabled and target_feature.enabled:
                            benefits.append(f"Access to {feature_name.replace('_', ' ').title()}")
                        
                        # Check if limits increase
                        elif (current_feature.enabled and target_feature.enabled and
                              current_feature.daily_limit and target_feature.daily_limit and
                              target_feature.daily_limit > current_feature.daily_limit):
                            benefits.append(f"Increased {feature_name.replace('_', ' ')} limit: {current_feature.daily_limit} → {target_feature.daily_limit}")
                        
                        # Check if advanced features become available
                        elif (current_feature.enabled and target_feature.enabled and
                              not current_feature.advanced_features and target_feature.advanced_features):
                            benefits.append(f"Advanced {feature_name.replace('_', ' ')} features")
            
            return {
                "benefits": benefits,
                "total_new_features": len([b for b in benefits if "Access to" in b]),
                "enhanced_features": len([b for b in benefits if "Advanced" in b or "Increased" in b])
            }
            
        except Exception as e:
            logger.error(f"Error getting upgrade benefits: {e}")
            return {"benefits": [], "total_new_features": 0, "enhanced_features": 0}

# Global instance
tier_access_control = TierAccessControl()