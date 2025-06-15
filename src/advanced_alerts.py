# src/advanced_alerts.py
import asyncio
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import requests
import ta
from textblob import TextBlob
import tweepy

from config import config
from user_db import get_user_property, set_user_property, add_alert_to_db
from security_auditor import security_auditor
from performance_monitor import track_performance

logger = logging.getLogger(__name__)

class AlertType(Enum):
    PRICE = "price"
    TECHNICAL = "technical"
    WHALE = "whale"
    PROTOCOL = "protocol"
    SENTIMENT = "sentiment"
    VOLUME = "volume"
    VOLATILITY = "volatility"

class AlertStatus(Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    PAUSED = "paused"
    EXPIRED = "expired"

@dataclass
class Alert:
    """Represents an advanced alert"""
    id: str
    user_id: int
    alert_type: AlertType
    symbol: str
    condition: str
    threshold: float
    current_value: float
    status: AlertStatus
    created_at: datetime
    triggered_at: Optional[datetime]
    metadata: Dict[str, Any]

@dataclass
class TechnicalIndicator:
    """Technical analysis indicator"""
    name: str
    value: float
    signal: str  # BUY, SELL, NEUTRAL
    strength: float  # 0-1

@dataclass
class SentimentData:
    """Social sentiment data"""
    symbol: str
    sentiment_score: float  # -1 to 1
    volume: int
    sources: List[str]
    trending_keywords: List[str]
    last_updated: datetime

class AdvancedAlertsSystem:
    """Advanced alerting system with ML-powered detection"""
    
    def __init__(self):
        self.active_alerts: Dict[str, Alert] = {}
        self.price_cache: Dict[str, Dict] = {}
        self.sentiment_cache: Dict[str, SentimentData] = {}
        self._init_external_apis()
        
    def _init_external_apis(self):
        """Initialize external API connections"""
        try:
            # Twitter API for sentiment analysis
            twitter_bearer = config.get('TWITTER_BEARER_TOKEN')
            if twitter_bearer:
                self.twitter_client = tweepy.Client(bearer_token=twitter_bearer)
            else:
                self.twitter_client = None
                
            # News API
            self.news_api_key = config.get('NEWS_API_KEY')
            
        except Exception as e:
            logger.warning(f"Failed to initialize external APIs: {e}")

    @track_performance.track_function
    async def create_price_alert(self, user_id: int, symbol: str, condition: str, threshold: float) -> Dict[str, Any]:
        """Create a smart price alert with ML-powered detection"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "alert_create", True, 
                {"type": "price", "symbol": symbol, "condition": condition}
            )
            
            # Validate condition
            valid_conditions = ['>', '<', '>=', '<=', 'crosses_above', 'crosses_below', 'volatility_spike']
            if condition not in valid_conditions:
                return {"success": False, "message": f"Invalid condition. Use: {', '.join(valid_conditions)}"}
            
            # Get current price
            current_price = await self._get_current_price(symbol)
            if current_price is None:
                return {"success": False, "message": f"Could not fetch price for {symbol}"}
            
            # Create alert
            alert_id = f"price_{user_id}_{symbol}_{int(datetime.now().timestamp())}"
            alert = Alert(
                id=alert_id,
                user_id=user_id,
                alert_type=AlertType.PRICE,
                symbol=symbol,
                condition=condition,
                threshold=threshold,
                current_value=current_price,
                status=AlertStatus.ACTIVE,
                created_at=datetime.now(),
                triggered_at=None,
                metadata={
                    "ml_confidence": await self._calculate_ml_confidence(symbol, condition, threshold),
                    "historical_accuracy": await self._get_historical_accuracy(symbol, condition),
                    "market_context": await self._get_market_context(symbol)
                }
            )
            
            self.active_alerts[alert_id] = alert
            
            # Store in database
            add_alert_to_db(alert_id, user_id, 0, 'advanced_price', asdict(alert))
            
            return {
                "success": True, 
                "message": f"Smart price alert created for {symbol}",
                "alert_id": alert_id,
                "ml_confidence": alert.metadata["ml_confidence"]
            }
            
        except Exception as e:
            logger.error(f"Error creating price alert: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def create_technical_alert(self, user_id: int, symbol: str, indicator: str, condition: str) -> Dict[str, Any]:
        """Create technical analysis alert"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "alert_create", True, 
                {"type": "technical", "symbol": symbol, "indicator": indicator}
            )
            
            # Validate indicator
            valid_indicators = ['rsi', 'macd', 'bollinger', 'stochastic', 'williams_r', 'cci']
            if indicator not in valid_indicators:
                return {"success": False, "message": f"Invalid indicator. Use: {', '.join(valid_indicators)}"}
            
            # Get current technical data
            technical_data = await self._get_technical_indicators(symbol)
            if not technical_data:
                return {"success": False, "message": f"Could not fetch technical data for {symbol}"}
            
            current_value = technical_data.get(indicator, 0)
            
            # Create alert
            alert_id = f"tech_{user_id}_{symbol}_{indicator}_{int(datetime.now().timestamp())}"
            alert = Alert(
                id=alert_id,
                user_id=user_id,
                alert_type=AlertType.TECHNICAL,
                symbol=symbol,
                condition=f"{indicator}_{condition}",
                threshold=0,  # Technical alerts use condition-based logic
                current_value=current_value,
                status=AlertStatus.ACTIVE,
                created_at=datetime.now(),
                triggered_at=None,
                metadata={
                    "indicator": indicator,
                    "condition": condition,
                    "technical_data": technical_data,
                    "signal_strength": await self._calculate_signal_strength(technical_data)
                }
            )
            
            self.active_alerts[alert_id] = alert
            add_alert_to_db(alert_id, user_id, 0, 'technical', asdict(alert))
            
            return {
                "success": True, 
                "message": f"Technical alert created for {symbol} {indicator}",
                "alert_id": alert_id,
                "current_value": current_value
            }
            
        except Exception as e:
            logger.error(f"Error creating technical alert: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def create_sentiment_alert(self, user_id: int, symbol: str, threshold: float) -> Dict[str, Any]:
        """Create social sentiment alert"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "alert_create", True, 
                {"type": "sentiment", "symbol": symbol}
            )
            
            # Get current sentiment
            sentiment_data = await self._get_sentiment_data(symbol)
            if not sentiment_data:
                return {"success": False, "message": f"Could not fetch sentiment data for {symbol}"}
            
            # Create alert
            alert_id = f"sentiment_{user_id}_{symbol}_{int(datetime.now().timestamp())}"
            alert = Alert(
                id=alert_id,
                user_id=user_id,
                alert_type=AlertType.SENTIMENT,
                symbol=symbol,
                condition="sentiment_change",
                threshold=threshold,
                current_value=sentiment_data.sentiment_score,
                status=AlertStatus.ACTIVE,
                created_at=datetime.now(),
                triggered_at=None,
                metadata={
                    "sentiment_data": asdict(sentiment_data),
                    "baseline_sentiment": sentiment_data.sentiment_score,
                    "volume_threshold": sentiment_data.volume * 1.5  # 50% volume increase
                }
            )
            
            self.active_alerts[alert_id] = alert
            add_alert_to_db(alert_id, user_id, 0, 'sentiment', asdict(alert))
            
            return {
                "success": True, 
                "message": f"Sentiment alert created for {symbol}",
                "alert_id": alert_id,
                "current_sentiment": sentiment_data.sentiment_score
            }
            
        except Exception as e:
            logger.error(f"Error creating sentiment alert: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def create_whale_alert(self, user_id: int, address: str, amount_threshold: float) -> Dict[str, Any]:
        """Create whale movement alert"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "alert_create", True, 
                {"type": "whale", "address": address[:10] + "..."}
            )
            
            # Validate address
            from web3 import Web3
            if not Web3.is_address(address):
                return {"success": False, "message": "Invalid wallet address"}
            
            # Create alert
            alert_id = f"whale_{user_id}_{address}_{int(datetime.now().timestamp())}"
            alert = Alert(
                id=alert_id,
                user_id=user_id,
                alert_type=AlertType.WHALE,
                symbol="",  # Not applicable for whale alerts
                condition="large_transaction",
                threshold=amount_threshold,
                current_value=0,
                status=AlertStatus.ACTIVE,
                created_at=datetime.now(),
                triggered_at=None,
                metadata={
                    "wallet_address": address,
                    "amount_threshold": amount_threshold,
                    "monitor_chains": ["ethereum", "polygon", "bsc", "arbitrum"]
                }
            )
            
            self.active_alerts[alert_id] = alert
            add_alert_to_db(alert_id, user_id, 0, 'whale', asdict(alert))
            
            return {
                "success": True, 
                "message": f"Whale alert created for address {address[:10]}...",
                "alert_id": alert_id
            }
            
        except Exception as e:
            logger.error(f"Error creating whale alert: {e}")
            return {"success": False, "message": str(e)}

    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        try:
            # Check cache first
            if symbol in self.price_cache:
                cache_data = self.price_cache[symbol]
                if datetime.now() - cache_data['timestamp'] < timedelta(minutes=1):
                    return cache_data['price']
            
            # Fetch from CoinGecko
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if symbol.lower() in data:
                    price = data[symbol.lower()]['usd']
                    
                    # Cache the price
                    self.price_cache[symbol] = {
                        'price': price,
                        'timestamp': datetime.now()
                    }
                    
                    return price
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None

    async def _get_technical_indicators(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get technical indicators for symbol"""
        try:
            # Get historical price data
            url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}/market_chart?vs_currency=usd&days=30"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            prices = [point[1] for point in data['prices']]
            
            if len(prices) < 20:
                return None
                
            # Convert to pandas Series for technical analysis
            price_series = pd.Series(prices)
            
            # Calculate indicators
            indicators = {}
            
            # RSI
            indicators['rsi'] = ta.momentum.RSIIndicator(price_series).rsi().iloc[-1]
            
            # MACD
            macd = ta.trend.MACD(price_series)
            indicators['macd'] = macd.macd().iloc[-1]
            indicators['macd_signal'] = macd.macd_signal().iloc[-1]
            indicators['macd_histogram'] = macd.macd_diff().iloc[-1]
            
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(price_series)
            indicators['bb_upper'] = bollinger.bollinger_hband().iloc[-1]
            indicators['bb_middle'] = bollinger.bollinger_mavg().iloc[-1]
            indicators['bb_lower'] = bollinger.bollinger_lband().iloc[-1]
            indicators['bb_width'] = indicators['bb_upper'] - indicators['bb_lower']
            
            # Stochastic
            # Note: Stochastic requires high, low, close data. Using price as approximation.
            indicators['stochastic'] = ta.momentum.StochasticOscillator(
                high=price_series, low=price_series, close=price_series
            ).stoch().iloc[-1]
            
            # Williams %R
            indicators['williams_r'] = ta.momentum.WilliamsRIndicator(
                high=price_series, low=price_series, close=price_series
            ).williams_r().iloc[-1]
            
            # CCI
            indicators['cci'] = ta.trend.CCIIndicator(
                high=price_series, low=price_series, close=price_series
            ).cci().iloc[-1]
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error getting technical indicators for {symbol}: {e}")
            return None

    async def _get_sentiment_data(self, symbol: str) -> Optional[SentimentData]:
        """Get social sentiment data for symbol"""
        try:
            # Check cache first
            if symbol in self.sentiment_cache:
                cache_data = self.sentiment_cache[symbol]
                if datetime.now() - cache_data.last_updated < timedelta(hours=1):
                    return cache_data
            
            sentiment_scores = []
            sources = []
            keywords = []
            total_volume = 0
            
            # Twitter sentiment analysis
            if self.twitter_client:
                try:
                    tweets = self.twitter_client.search_recent_tweets(
                        query=f"${symbol} OR {symbol}",
                        max_results=100,
                        tweet_fields=['public_metrics', 'created_at']
                    )
                    
                    if tweets.data:
                        for tweet in tweets.data:
                            # Analyze sentiment
                            blob = TextBlob(tweet.text)
                            sentiment_scores.append(blob.sentiment.polarity)
                            total_volume += tweet.public_metrics['retweet_count'] + tweet.public_metrics['like_count']
                        
                        sources.append('twitter')
                        
                except Exception as e:
                    logger.warning(f"Error fetching Twitter sentiment: {e}")
            
            # News sentiment analysis
            if self.news_api_key:
                try:
                    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={self.news_api_key}&pageSize=50"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        news_data = response.json()
                        for article in news_data.get('articles', []):
                            title = article.get('title', '')
                            description = article.get('description', '')
                            text = f"{title} {description}"
                            
                            blob = TextBlob(text)
                            sentiment_scores.append(blob.sentiment.polarity)
                            
                            # Extract keywords
                            words = text.lower().split()
                            keywords.extend([word for word in words if len(word) > 4])
                        
                        sources.append('news')
                        
                except Exception as e:
                    logger.warning(f"Error fetching news sentiment: {e}")
            
            # Calculate overall sentiment
            if sentiment_scores:
                overall_sentiment = np.mean(sentiment_scores)
                
                # Get trending keywords
                from collections import Counter
                trending_keywords = [word for word, count in Counter(keywords).most_common(5)]
                
                sentiment_data = SentimentData(
                    symbol=symbol,
                    sentiment_score=overall_sentiment,
                    volume=total_volume,
                    sources=sources,
                    trending_keywords=trending_keywords,
                    last_updated=datetime.now()
                )
                
                # Cache the data
                self.sentiment_cache[symbol] = sentiment_data
                
                return sentiment_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting sentiment data for {symbol}: {e}")
            return None

    async def _calculate_ml_confidence(self, symbol: str, condition: str, threshold: float) -> float:
        """Calculate ML confidence score for price alert"""
        try:
            # This would typically use a trained ML model
            # For now, return a mock confidence based on market conditions
            
            # Get technical indicators
            technical_data = await self._get_technical_indicators(symbol)
            if not technical_data:
                return 0.5
            
            confidence_factors = []
            
            # RSI factor
            rsi = technical_data.get('rsi', 50)
            if condition in ['>', '>=', 'crosses_above'] and rsi < 30:
                confidence_factors.append(0.8)  # Oversold, likely to bounce
            elif condition in ['<', '<=', 'crosses_below'] and rsi > 70:
                confidence_factors.append(0.8)  # Overbought, likely to drop
            else:
                confidence_factors.append(0.5)
            
            # MACD factor
            macd = technical_data.get('macd', 0)
            macd_signal = technical_data.get('macd_signal', 0)
            if macd > macd_signal and condition in ['>', '>=', 'crosses_above']:
                confidence_factors.append(0.7)
            elif macd < macd_signal and condition in ['<', '<=', 'crosses_below']:
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.4)
            
            # Bollinger Bands factor
            bb_width = technical_data.get('bb_width', 0)
            if bb_width > 0:
                # Narrow bands suggest breakout potential
                if bb_width < np.percentile([bb_width], 25):
                    confidence_factors.append(0.6)
                else:
                    confidence_factors.append(0.5)
            
            return np.mean(confidence_factors)
            
        except Exception as e:
            logger.error(f"Error calculating ML confidence: {e}")
            return 0.5

    async def _get_historical_accuracy(self, symbol: str, condition: str) -> float:
        """Get historical accuracy for similar alerts"""
        # This would query historical alert performance
        # For now, return a mock value
        return 0.65

    async def _get_market_context(self, symbol: str) -> Dict[str, Any]:
        """Get market context for the symbol"""
        try:
            context = {}
            
            # Get market cap and volume
            url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                market_data = data.get('market_data', {})
                
                context.update({
                    'market_cap_rank': data.get('market_cap_rank'),
                    'price_change_24h': market_data.get('price_change_percentage_24h'),
                    'volume_24h': market_data.get('total_volume', {}).get('usd'),
                    'market_cap': market_data.get('market_cap', {}).get('usd'),
                    'circulating_supply': market_data.get('circulating_supply')
                })
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting market context: {e}")
            return {}

    async def _calculate_signal_strength(self, technical_data: Dict[str, float]) -> float:
        """Calculate overall signal strength from technical indicators"""
        try:
            signals = []
            
            # RSI signals
            rsi = technical_data.get('rsi', 50)
            if rsi < 30:
                signals.append(0.8)  # Strong oversold
            elif rsi > 70:
                signals.append(-0.8)  # Strong overbought
            else:
                signals.append(0)
            
            # MACD signals
            macd = technical_data.get('macd', 0)
            macd_signal = technical_data.get('macd_signal', 0)
            if macd > macd_signal:
                signals.append(0.6)  # Bullish
            else:
                signals.append(-0.6)  # Bearish
            
            # Bollinger Bands signals
            bb_upper = technical_data.get('bb_upper', 0)
            bb_lower = technical_data.get('bb_lower', 0)
            bb_middle = technical_data.get('bb_middle', 0)
            
            if bb_upper and bb_lower and bb_middle:
                current_price = technical_data.get('current_price', bb_middle)
                if current_price > bb_upper:
                    signals.append(-0.7)  # Overbought
                elif current_price < bb_lower:
                    signals.append(0.7)  # Oversold
                else:
                    signals.append(0)
            
            return abs(np.mean(signals)) if signals else 0.5
            
        except Exception as e:
            logger.error(f"Error calculating signal strength: {e}")
            return 0.5

    @track_performance.track_function
    async def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all active alerts and return triggered ones"""
        triggered_alerts = []
        
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.status != AlertStatus.ACTIVE:
                continue
                
            try:
                is_triggered = False
                trigger_data = {}
                
                if alert.alert_type == AlertType.PRICE:
                    is_triggered, trigger_data = await self._check_price_alert(alert)
                elif alert.alert_type == AlertType.TECHNICAL:
                    is_triggered, trigger_data = await self._check_technical_alert(alert)
                elif alert.alert_type == AlertType.SENTIMENT:
                    is_triggered, trigger_data = await self._check_sentiment_alert(alert)
                elif alert.alert_type == AlertType.WHALE:
                    is_triggered, trigger_data = await self._check_whale_alert(alert)
                
                if is_triggered:
                    alert.status = AlertStatus.TRIGGERED
                    alert.triggered_at = datetime.now()
                    
                    triggered_alerts.append({
                        'alert': alert,
                        'trigger_data': trigger_data
                    })
                    
                    # Remove from active alerts
                    del self.active_alerts[alert_id]
                    
            except Exception as e:
                logger.error(f"Error checking alert {alert_id}: {e}")
        
        return triggered_alerts

    async def _check_price_alert(self, alert: Alert) -> Tuple[bool, Dict[str, Any]]:
        """Check if price alert should trigger"""
        try:
            current_price = await self._get_current_price(alert.symbol)
            if current_price is None:
                return False, {}
            
            condition = alert.condition
            threshold = alert.threshold
            
            is_triggered = False
            
            if condition == '>':
                is_triggered = current_price > threshold
            elif condition == '<':
                is_triggered = current_price < threshold
            elif condition == '>=':
                is_triggered = current_price >= threshold
            elif condition == '<=':
                is_triggered = current_price <= threshold
            elif condition == 'crosses_above':
                # Check if price crossed above threshold
                is_triggered = alert.current_value <= threshold and current_price > threshold
            elif condition == 'crosses_below':
                # Check if price crossed below threshold
                is_triggered = alert.current_value >= threshold and current_price < threshold
            elif condition == 'volatility_spike':
                # Check for volatility spike
                volatility = await self._calculate_volatility(alert.symbol)
                is_triggered = volatility > threshold
            
            # Update current value
            alert.current_value = current_price
            
            trigger_data = {
                'current_price': current_price,
                'threshold': threshold,
                'condition': condition,
                'price_change': ((current_price - alert.current_value) / alert.current_value * 100) if alert.current_value > 0 else 0
            }
            
            return is_triggered, trigger_data
            
        except Exception as e:
            logger.error(f"Error checking price alert: {e}")
            return False, {}

    async def _check_technical_alert(self, alert: Alert) -> Tuple[bool, Dict[str, Any]]:
        """Check if technical alert should trigger"""
        try:
            technical_data = await self._get_technical_indicators(alert.symbol)
            if not technical_data:
                return False, {}
            
            indicator = alert.metadata.get('indicator')
            condition = alert.metadata.get('condition')
            
            is_triggered = False
            trigger_data = {'technical_data': technical_data}
            
            if indicator == 'rsi':
                rsi = technical_data.get('rsi', 50)
                if condition == 'oversold' and rsi < 30:
                    is_triggered = True
                elif condition == 'overbought' and rsi > 70:
                    is_triggered = True
                trigger_data['rsi'] = rsi
                
            elif indicator == 'macd':
                macd = technical_data.get('macd', 0)
                macd_signal = technical_data.get('macd_signal', 0)
                if condition == 'bullish_crossover' and macd > macd_signal:
                    is_triggered = True
                elif condition == 'bearish_crossover' and macd < macd_signal:
                    is_triggered = True
                trigger_data.update({'macd': macd, 'macd_signal': macd_signal})
            
            # Add more technical indicators as needed
            
            return is_triggered, trigger_data
            
        except Exception as e:
            logger.error(f"Error checking technical alert: {e}")
            return False, {}

    async def _check_sentiment_alert(self, alert: Alert) -> Tuple[bool, Dict[str, Any]]:
        """Check if sentiment alert should trigger"""
        try:
            sentiment_data = await self._get_sentiment_data(alert.symbol)
            if not sentiment_data:
                return False, {}
            
            baseline_sentiment = alert.metadata.get('baseline_sentiment', 0)
            threshold = alert.threshold
            
            sentiment_change = abs(sentiment_data.sentiment_score - baseline_sentiment)
            is_triggered = sentiment_change >= threshold
            
            trigger_data = {
                'current_sentiment': sentiment_data.sentiment_score,
                'baseline_sentiment': baseline_sentiment,
                'sentiment_change': sentiment_change,
                'volume': sentiment_data.volume,
                'trending_keywords': sentiment_data.trending_keywords
            }
            
            return is_triggered, trigger_data
            
        except Exception as e:
            logger.error(f"Error checking sentiment alert: {e}")
            return False, {}

    async def _check_whale_alert(self, alert: Alert) -> Tuple[bool, Dict[str, Any]]:
        """Check if whale alert should trigger"""
        try:
            # This would typically monitor blockchain transactions
            # For now, return False as it requires real-time blockchain monitoring
            return False, {}
            
        except Exception as e:
            logger.error(f"Error checking whale alert: {e}")
            return False, {}

    async def _calculate_volatility(self, symbol: str) -> float:
        """Calculate current volatility for symbol"""
        try:
            # Get recent price data
            url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}/market_chart?vs_currency=usd&days=7"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                prices = [point[1] for point in data['prices']]
                
                if len(prices) > 1:
                    price_series = pd.Series(prices)
                    returns = price_series.pct_change().dropna()
                    volatility = returns.std() * np.sqrt(24)  # Annualized hourly volatility
                    return volatility
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 0.0

    def get_user_alerts(self, user_id: int) -> List[Alert]:
        """Get all alerts for a user"""
        return [alert for alert in self.active_alerts.values() if alert.user_id == user_id]

    def pause_alert(self, alert_id: str) -> bool:
        """Pause an alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].status = AlertStatus.PAUSED
            return True
        return False

    def resume_alert(self, alert_id: str) -> bool:
        """Resume a paused alert"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].status = AlertStatus.ACTIVE
            return True
        return False

    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        if alert_id in self.active_alerts:
            del self.active_alerts[alert_id]
            return True
        return False

# Global instance
advanced_alerts = AdvancedAlertsSystem()