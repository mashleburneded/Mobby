# src/social_trading.py
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
from textblob import TextBlob

from config import config
from user_db import get_user_property, set_user_property
from security_auditor import security_auditor
from performance_monitor import track_performance

logger = logging.getLogger(__name__)

class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    LONG = "long"
    SHORT = "short"

class SignalStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    EXPIRED = "expired"

@dataclass
class TradingSignal:
    """Represents a trading signal from a trader"""
    id: str
    trader_id: int
    trader_username: str
    signal_type: SignalType
    symbol: str
    entry_price: float
    target_price: Optional[float]
    stop_loss: Optional[float]
    confidence: float  # 0-1
    reasoning: str
    created_at: datetime
    status: SignalStatus
    performance: Optional[float]  # Actual performance when closed
    followers_count: int
    likes: int
    comments: List[Dict[str, Any]]

@dataclass
class TraderProfile:
    """Represents a trader's profile and statistics"""
    user_id: int
    username: str
    display_name: str
    bio: str
    avatar_url: Optional[str]
    verified: bool
    reputation_score: float  # 0-100
    total_signals: int
    successful_signals: int
    win_rate: float
    avg_return: float
    total_return: float
    followers_count: int
    following_count: int
    risk_score: float  # 0-10, higher = riskier
    specialties: List[str]  # e.g., ["DeFi", "NFTs", "Layer1"]
    joined_date: datetime
    last_active: datetime

@dataclass
class CommunityStats:
    """Community-wide statistics"""
    total_traders: int
    total_signals: int
    total_followers: int
    avg_win_rate: float
    top_performers: List[TraderProfile]
    trending_tokens: List[str]
    sentiment_overview: Dict[str, float]
    active_signals: int

class SocialTradingSystem:
    """Social trading and community features"""
    
    def __init__(self):
        self.traders: Dict[int, TraderProfile] = {}
        self.signals: Dict[str, TradingSignal] = {}
        self.followers: Dict[int, List[int]] = {}  # follower_id -> [trader_ids]
        self.community_stats = None
        self._load_data()

    def _load_data(self):
        """Load existing data from storage"""
        try:
            # In a real implementation, this would load from database
            # For now, initialize with empty data
            pass
        except Exception as e:
            logger.error(f"Error loading social trading data: {e}")

    @track_performance.track_function
    async def create_trader_profile(self, user_id: int, username: str, display_name: str, bio: str = "") -> Dict[str, Any]:
        """Create or update trader profile"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "trader_profile_create", True, 
                {"username": username}
            )
            
            # Check if username is already taken
            for trader in self.traders.values():
                if trader.username == username and trader.user_id != user_id:
                    return {"success": False, "message": "Username already taken"}
            
            # Create or update profile
            if user_id in self.traders:
                trader = self.traders[user_id]
                trader.username = username
                trader.display_name = display_name
                trader.bio = bio
                trader.last_active = datetime.now()
            else:
                trader = TraderProfile(
                    user_id=user_id,
                    username=username,
                    display_name=display_name,
                    bio=bio,
                    avatar_url=None,
                    verified=False,
                    reputation_score=50.0,  # Start with neutral reputation
                    total_signals=0,
                    successful_signals=0,
                    win_rate=0.0,
                    avg_return=0.0,
                    total_return=0.0,
                    followers_count=0,
                    following_count=0,
                    risk_score=5.0,  # Neutral risk
                    specialties=[],
                    joined_date=datetime.now(),
                    last_active=datetime.now()
                )
                self.traders[user_id] = trader
            
            # Save to user properties
            set_user_property(user_id, 'trader_profile', json.dumps(asdict(trader), default=str))
            
            return {
                "success": True, 
                "message": "Trader profile created successfully",
                "profile": asdict(trader)
            }
            
        except Exception as e:
            logger.error(f"Error creating trader profile: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def publish_signal(self, user_id: int, signal_type: str, symbol: str, entry_price: float, 
                           target_price: Optional[float] = None, stop_loss: Optional[float] = None,
                           confidence: float = 0.5, reasoning: str = "") -> Dict[str, Any]:
        """Publish a trading signal"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "signal_publish", True, 
                {"symbol": symbol, "signal_type": signal_type}
            )
            
            # Check if user has trader profile
            if user_id not in self.traders:
                return {"success": False, "message": "Please create a trader profile first"}
            
            trader = self.traders[user_id]
            
            # Validate signal type
            try:
                signal_enum = SignalType(signal_type.lower())
            except ValueError:
                return {"success": False, "message": f"Invalid signal type: {signal_type}"}
            
            # Create signal
            signal_id = f"signal_{user_id}_{int(datetime.now().timestamp())}"
            signal = TradingSignal(
                id=signal_id,
                trader_id=user_id,
                trader_username=trader.username,
                signal_type=signal_enum,
                symbol=symbol.upper(),
                entry_price=entry_price,
                target_price=target_price,
                stop_loss=stop_loss,
                confidence=max(0.0, min(1.0, confidence)),
                reasoning=reasoning,
                created_at=datetime.now(),
                status=SignalStatus.ACTIVE,
                performance=None,
                followers_count=trader.followers_count,
                likes=0,
                comments=[]
            )
            
            self.signals[signal_id] = signal
            
            # Update trader stats
            trader.total_signals += 1
            trader.last_active = datetime.now()
            
            # Notify followers
            await self._notify_followers(user_id, signal)
            
            return {
                "success": True,
                "message": "Signal published successfully",
                "signal_id": signal_id,
                "signal": asdict(signal)
            }
            
        except Exception as e:
            logger.error(f"Error publishing signal: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def follow_trader(self, follower_id: int, trader_id: int) -> Dict[str, Any]:
        """Follow a trader"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                follower_id, "trader_follow", True, 
                {"trader_id": trader_id}
            )
            
            if trader_id not in self.traders:
                return {"success": False, "message": "Trader not found"}
            
            if follower_id == trader_id:
                return {"success": False, "message": "Cannot follow yourself"}
            
            # Add to followers list
            if follower_id not in self.followers:
                self.followers[follower_id] = []
            
            if trader_id not in self.followers[follower_id]:
                self.followers[follower_id].append(trader_id)
                
                # Update trader's follower count
                self.traders[trader_id].followers_count += 1
                
                # Update follower's following count
                if follower_id in self.traders:
                    self.traders[follower_id].following_count += 1
                
                return {
                    "success": True,
                    "message": f"Now following {self.traders[trader_id].username}"
                }
            else:
                return {"success": False, "message": "Already following this trader"}
                
        except Exception as e:
            logger.error(f"Error following trader: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def unfollow_trader(self, follower_id: int, trader_id: int) -> Dict[str, Any]:
        """Unfollow a trader"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                follower_id, "trader_unfollow", True, 
                {"trader_id": trader_id}
            )
            
            if follower_id in self.followers and trader_id in self.followers[follower_id]:
                self.followers[follower_id].remove(trader_id)
                
                # Update counts
                if trader_id in self.traders:
                    self.traders[trader_id].followers_count -= 1
                
                if follower_id in self.traders:
                    self.traders[follower_id].following_count -= 1
                
                return {
                    "success": True,
                    "message": f"Unfollowed {self.traders[trader_id].username}"
                }
            else:
                return {"success": False, "message": "Not following this trader"}
                
        except Exception as e:
            logger.error(f"Error unfollowing trader: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def get_leaderboard(self, metric: str = "win_rate", limit: int = 10) -> Dict[str, Any]:
        """Get trader leaderboard"""
        try:
            valid_metrics = ["win_rate", "total_return", "reputation_score", "followers_count"]
            if metric not in valid_metrics:
                return {"success": False, "message": f"Invalid metric. Use: {', '.join(valid_metrics)}"}
            
            # Filter traders with minimum activity
            active_traders = [
                trader for trader in self.traders.values() 
                if trader.total_signals >= 5  # Minimum 5 signals to be on leaderboard
            ]
            
            # Sort by metric
            sorted_traders = sorted(
                active_traders, 
                key=lambda t: getattr(t, metric), 
                reverse=True
            )[:limit]
            
            leaderboard = []
            for i, trader in enumerate(sorted_traders, 1):
                leaderboard.append({
                    "rank": i,
                    "username": trader.username,
                    "display_name": trader.display_name,
                    "metric_value": getattr(trader, metric),
                    "win_rate": trader.win_rate,
                    "total_signals": trader.total_signals,
                    "followers": trader.followers_count,
                    "reputation": trader.reputation_score,
                    "verified": trader.verified
                })
            
            return {
                "success": True,
                "leaderboard": leaderboard,
                "metric": metric,
                "total_traders": len(active_traders)
            }
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def get_signals_feed(self, user_id: int, limit: int = 20) -> Dict[str, Any]:
        """Get personalized signals feed"""
        try:
            # Get signals from followed traders
            followed_traders = self.followers.get(user_id, [])
            
            # Get recent signals
            recent_signals = []
            for signal in self.signals.values():
                if signal.status == SignalStatus.ACTIVE:
                    # Include signals from followed traders or top performers
                    if (signal.trader_id in followed_traders or 
                        signal.trader_id in self.traders and 
                        self.traders[signal.trader_id].reputation_score > 70):
                        recent_signals.append(signal)
            
            # Sort by creation time and confidence
            recent_signals.sort(
                key=lambda s: (s.created_at, s.confidence), 
                reverse=True
            )
            
            # Format signals for response
            signals_data = []
            for signal in recent_signals[:limit]:
                trader = self.traders.get(signal.trader_id)
                signals_data.append({
                    "signal": asdict(signal),
                    "trader": {
                        "username": trader.username if trader else "Unknown",
                        "reputation": trader.reputation_score if trader else 0,
                        "verified": trader.verified if trader else False,
                        "win_rate": trader.win_rate if trader else 0
                    }
                })
            
            return {
                "success": True,
                "signals": signals_data,
                "total_signals": len(recent_signals)
            }
            
        except Exception as e:
            logger.error(f"Error getting signals feed: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def analyze_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Analyze community sentiment for a symbol"""
        try:
            # Get recent signals for the symbol
            symbol_signals = [
                signal for signal in self.signals.values()
                if signal.symbol.upper() == symbol.upper() and
                signal.created_at > datetime.now() - timedelta(days=7)
            ]
            
            if not symbol_signals:
                return {
                    "success": True,
                    "symbol": symbol,
                    "sentiment": "neutral",
                    "score": 0.0,
                    "signal_count": 0,
                    "message": "No recent signals found for this symbol"
                }
            
            # Calculate sentiment scores
            buy_signals = len([s for s in symbol_signals if s.signal_type in [SignalType.BUY, SignalType.LONG]])
            sell_signals = len([s for s in symbol_signals if s.signal_type in [SignalType.SELL, SignalType.SHORT]])
            hold_signals = len([s for s in symbol_signals if s.signal_type == SignalType.HOLD])
            
            total_signals = len(symbol_signals)
            
            # Weight by trader reputation and confidence
            weighted_score = 0.0
            total_weight = 0.0
            
            for signal in symbol_signals:
                trader = self.traders.get(signal.trader_id)
                trader_weight = (trader.reputation_score / 100) if trader else 0.5
                confidence_weight = signal.confidence
                
                signal_score = 0
                if signal.signal_type in [SignalType.BUY, SignalType.LONG]:
                    signal_score = 1
                elif signal.signal_type in [SignalType.SELL, SignalType.SHORT]:
                    signal_score = -1
                # HOLD signals contribute 0
                
                weight = trader_weight * confidence_weight
                weighted_score += signal_score * weight
                total_weight += weight
            
            # Calculate final sentiment score (-1 to 1)
            sentiment_score = weighted_score / total_weight if total_weight > 0 else 0
            
            # Determine sentiment label
            if sentiment_score > 0.3:
                sentiment = "bullish"
            elif sentiment_score < -0.3:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
            
            return {
                "success": True,
                "symbol": symbol,
                "sentiment": sentiment,
                "score": sentiment_score,
                "signal_count": total_signals,
                "breakdown": {
                    "buy_signals": buy_signals,
                    "sell_signals": sell_signals,
                    "hold_signals": hold_signals
                },
                "confidence": min(total_weight / total_signals, 1.0) if total_signals > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def get_community_stats(self) -> Dict[str, Any]:
        """Get overall community statistics"""
        try:
            # Calculate stats
            total_traders = len(self.traders)
            total_signals = len(self.signals)
            active_signals = len([s for s in self.signals.values() if s.status == SignalStatus.ACTIVE])
            
            # Calculate average win rate
            traders_with_signals = [t for t in self.traders.values() if t.total_signals > 0]
            avg_win_rate = np.mean([t.win_rate for t in traders_with_signals]) if traders_with_signals else 0
            
            # Get top performers
            top_performers = sorted(
                [t for t in self.traders.values() if t.total_signals >= 5],
                key=lambda t: t.reputation_score,
                reverse=True
            )[:5]
            
            # Get trending tokens (most signaled in last 24h)
            recent_signals = [
                s for s in self.signals.values()
                if s.created_at > datetime.now() - timedelta(days=1)
            ]
            
            from collections import Counter
            symbol_counts = Counter([s.symbol for s in recent_signals])
            trending_tokens = [symbol for symbol, count in symbol_counts.most_common(10)]
            
            # Calculate overall sentiment
            sentiment_overview = {}
            for symbol in trending_tokens[:5]:  # Top 5 trending
                sentiment_data = await self.analyze_sentiment(symbol)
                if sentiment_data["success"]:
                    sentiment_overview[symbol] = {
                        "sentiment": sentiment_data["sentiment"],
                        "score": sentiment_data["score"]
                    }
            
            stats = CommunityStats(
                total_traders=total_traders,
                total_signals=total_signals,
                total_followers=sum(len(followers) for followers in self.followers.values()),
                avg_win_rate=avg_win_rate,
                top_performers=top_performers,
                trending_tokens=trending_tokens,
                sentiment_overview=sentiment_overview,
                active_signals=active_signals
            )
            
            self.community_stats = stats
            
            return {
                "success": True,
                "stats": asdict(stats)
            }
            
        except Exception as e:
            logger.error(f"Error getting community stats: {e}")
            return {"success": False, "message": str(e)}

    async def _notify_followers(self, trader_id: int, signal: TradingSignal):
        """Notify followers of new signal (placeholder)"""
        try:
            # In a real implementation, this would send notifications
            # to all followers via Telegram, email, etc.
            follower_ids = [
                follower_id for follower_id, following_list in self.followers.items()
                if trader_id in following_list
            ]
            
            logger.info(f"Would notify {len(follower_ids)} followers of new signal from trader {trader_id}")
            
        except Exception as e:
            logger.error(f"Error notifying followers: {e}")

    @track_performance.track_function
    async def update_signal_performance(self, signal_id: str, current_price: float) -> Dict[str, Any]:
        """Update signal performance based on current price"""
        try:
            if signal_id not in self.signals:
                return {"success": False, "message": "Signal not found"}
            
            signal = self.signals[signal_id]
            
            if signal.status != SignalStatus.ACTIVE:
                return {"success": False, "message": "Signal is not active"}
            
            # Calculate performance
            entry_price = signal.entry_price
            performance = 0.0
            
            if signal.signal_type in [SignalType.BUY, SignalType.LONG]:
                performance = ((current_price - entry_price) / entry_price) * 100
            elif signal.signal_type in [SignalType.SELL, SignalType.SHORT]:
                performance = ((entry_price - current_price) / entry_price) * 100
            
            signal.performance = performance
            
            # Check if signal should be closed
            should_close = False
            close_reason = ""
            
            if signal.target_price and signal.signal_type in [SignalType.BUY, SignalType.LONG]:
                if current_price >= signal.target_price:
                    should_close = True
                    close_reason = "Target reached"
            elif signal.target_price and signal.signal_type in [SignalType.SELL, SignalType.SHORT]:
                if current_price <= signal.target_price:
                    should_close = True
                    close_reason = "Target reached"
            
            if signal.stop_loss:
                if signal.signal_type in [SignalType.BUY, SignalType.LONG] and current_price <= signal.stop_loss:
                    should_close = True
                    close_reason = "Stop loss hit"
                elif signal.signal_type in [SignalType.SELL, SignalType.SHORT] and current_price >= signal.stop_loss:
                    should_close = True
                    close_reason = "Stop loss hit"
            
            # Close signal if needed
            if should_close:
                signal.status = SignalStatus.CLOSED
                
                # Update trader statistics
                trader = self.traders.get(signal.trader_id)
                if trader:
                    if performance > 0:
                        trader.successful_signals += 1
                    
                    # Recalculate win rate
                    closed_signals = [
                        s for s in self.signals.values()
                        if s.trader_id == signal.trader_id and s.status == SignalStatus.CLOSED
                    ]
                    
                    if closed_signals:
                        successful = len([s for s in closed_signals if s.performance and s.performance > 0])
                        trader.win_rate = (successful / len(closed_signals)) * 100
                        
                        # Update average return
                        returns = [s.performance for s in closed_signals if s.performance is not None]
                        trader.avg_return = np.mean(returns) if returns else 0
                        trader.total_return = sum(returns) if returns else 0
                        
                        # Update reputation score based on performance
                        trader.reputation_score = min(100, max(0, 
                            50 + (trader.win_rate - 50) * 0.5 + trader.avg_return * 0.1
                        ))
            
            return {
                "success": True,
                "signal_id": signal_id,
                "performance": performance,
                "status": signal.status.value,
                "closed": should_close,
                "close_reason": close_reason if should_close else None
            }
            
        except Exception as e:
            logger.error(f"Error updating signal performance: {e}")
            return {"success": False, "message": str(e)}

    def get_trader_profile(self, user_id: int) -> Optional[TraderProfile]:
        """Get trader profile by user ID"""
        return self.traders.get(user_id)

    def search_traders(self, query: str, limit: int = 10) -> List[TraderProfile]:
        """Search traders by username or display name"""
        query_lower = query.lower()
        matching_traders = []
        
        for trader in self.traders.values():
            if (query_lower in trader.username.lower() or 
                query_lower in trader.display_name.lower() or
                any(query_lower in specialty.lower() for specialty in trader.specialties)):
                matching_traders.append(trader)
        
        # Sort by reputation score
        matching_traders.sort(key=lambda t: t.reputation_score, reverse=True)
        
        return matching_traders[:limit]

class SocialTradingHub:
    """
    Main interface for social trading features.
    Provides a unified API for all social trading functionality.
    """
    
    def __init__(self):
        self.system = SocialTradingSystem()
    
    async def process_command(self, user_id: int, command: str, args: list) -> Dict[str, Any]:
        """Process social trading commands"""
        try:
            if command == "profile":
                if len(args) >= 3:
                    return await self.system.create_trader_profile(
                        user_id, args[0], args[1], " ".join(args[2:])
                    )
                else:
                    return {"success": False, "message": "Usage: /social profile <username> <display_name> <bio>"}
            
            elif command == "signal":
                if len(args) >= 3:
                    signal_type = args[0]
                    symbol = args[1]
                    entry_price = float(args[2])
                    target_price = float(args[3]) if len(args) > 3 else None
                    stop_loss = float(args[4]) if len(args) > 4 else None
                    confidence = float(args[5]) if len(args) > 5 else 0.5
                    reasoning = " ".join(args[6:]) if len(args) > 6 else ""
                    
                    return await self.system.publish_signal(
                        user_id, signal_type, symbol, entry_price,
                        target_price, stop_loss, confidence, reasoning
                    )
                else:
                    return {"success": False, "message": "Usage: /social signal <buy/sell/hold> <symbol> <price> [target] [stop_loss] [confidence] [reasoning]"}
            
            elif command == "follow":
                if len(args) >= 1:
                    trader_username = args[0].replace("@", "")
                    # Find trader by username
                    trader_id = None
                    for tid, trader in self.system.traders.items():
                        if trader.username == trader_username:
                            trader_id = tid
                            break
                    
                    if trader_id:
                        return await self.system.follow_trader(user_id, trader_id)
                    else:
                        return {"success": False, "message": f"Trader @{trader_username} not found"}
                else:
                    return {"success": False, "message": "Usage: /social follow @username"}
            
            elif command == "unfollow":
                if len(args) >= 1:
                    trader_username = args[0].replace("@", "")
                    # Find trader by username
                    trader_id = None
                    for tid, trader in self.system.traders.items():
                        if trader.username == trader_username:
                            trader_id = tid
                            break
                    
                    if trader_id:
                        return await self.system.unfollow_trader(user_id, trader_id)
                    else:
                        return {"success": False, "message": f"Trader @{trader_username} not found"}
                else:
                    return {"success": False, "message": "Usage: /social unfollow @username"}
            
            elif command == "leaderboard":
                metric = args[0] if args else "win_rate"
                try:
                    limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
                except (ValueError, IndexError):
                    limit = 10
                return await self.system.get_leaderboard(metric, limit)
            
            elif command == "feed":
                try:
                    limit = int(args[0]) if args and args[0].isdigit() else 20
                except (ValueError, IndexError):
                    limit = 20
                return await self.system.get_signals_feed(user_id, limit)
            
            elif command == "sentiment":
                if len(args) >= 1:
                    symbol = args[0]
                    return await self.system.analyze_sentiment(symbol)
                else:
                    return {"success": False, "message": "Usage: /social sentiment <symbol>"}
            
            elif command == "search":
                if len(args) >= 1:
                    query = " ".join(args)
                    traders = self.system.search_traders(query)
                    return {
                        "success": True,
                        "traders": [
                            {
                                "username": t.username,
                                "display_name": t.display_name,
                                "reputation": t.reputation_score,
                                "win_rate": t.win_rate,
                                "followers": t.followers_count,
                                "verified": t.verified
                            } for t in traders
                        ]
                    }
                else:
                    return {"success": False, "message": "Usage: /social search <query>"}
            
            else:
                return {
                    "success": False,
                    "message": "Available commands: profile, signal, follow, unfollow, leaderboard, feed, sentiment, search"
                }
                
        except Exception as e:
            logger.error(f"Error processing social trading command: {e}")
            return {"success": False, "message": str(e)}
    
    async def get_overview(self, user_id: int) -> Dict[str, Any]:
        """Get social trading overview for user"""
        try:
            trader = self.system.get_trader_profile(user_id)
            following = self.system.followers.get(user_id, [])
            
            return {
                "success": True,
                "has_profile": trader is not None,
                "trader_info": {
                    "username": trader.username if trader else None,
                    "reputation": trader.reputation_score if trader else 0,
                    "win_rate": trader.win_rate if trader else 0,
                    "total_signals": trader.total_signals if trader else 0,
                    "followers": trader.followers_count if trader else 0,
                    "following": len(following)
                } if trader else None,
                "following_count": len(following),
                "recent_signals": len([
                    s for s in self.system.signals.values()
                    if s.trader_id == user_id and s.status.value == "active"
                ]) if trader else 0
            }
        except Exception as e:
            logger.error(f"Error getting social trading overview: {e}")
            return {"success": False, "message": str(e)}

# Global instances
social_trading = SocialTradingSystem()
social_trading_hub = SocialTradingHub()
