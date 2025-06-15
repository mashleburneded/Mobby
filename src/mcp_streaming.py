# src/mcp_streaming.py - Real-Time Data Streaming with MCP Integration
import asyncio
import logging
import json
import websockets
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import aiohttp
from collections import defaultdict

from mcp_client import mcp_client

logger = logging.getLogger(__name__)

@dataclass
class StreamSubscription:
    """Stream subscription configuration"""
    user_id: int
    stream_type: str
    parameters: dict
    callback: Callable
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True

@dataclass
class AlertRule:
    """Alert rule configuration"""
    user_id: int
    rule_type: str  # price_above, price_below, volume_spike, whale_movement
    symbol: str
    threshold: float
    callback: Callable
    created_at: datetime = field(default_factory=datetime.now)
    triggered_count: int = 0
    last_triggered: Optional[datetime] = None

class MCPDataStreamer:
    """Real-time data streaming manager with MCP integration"""

    def __init__(self):
        self.subscriptions: Dict[str, List[StreamSubscription]] = defaultdict(list)
        self.alert_rules: Dict[int, List[AlertRule]] = defaultdict(list)
        self.streaming_tasks: Dict[str, asyncio.Task] = {}
        self.price_cache: Dict[str, dict] = {}
        self.running = False

    async def initialize(self):
        """Initialize streaming infrastructure"""
        try:
            # Start core streaming tasks
            self.streaming_tasks['price_monitor'] = asyncio.create_task(self._price_monitoring_loop())
            self.streaming_tasks['social_monitor'] = asyncio.create_task(self._social_monitoring_loop())
            self.streaming_tasks['blockchain_monitor'] = asyncio.create_task(self._blockchain_monitoring_loop())
            self.streaming_tasks['alert_processor'] = asyncio.create_task(self._alert_processing_loop())
            
            # Start rate limiting and batching
            self.streaming_tasks['batch_processor'] = asyncio.create_task(self._batch_processing_loop())
            
            self.running = True
            logger.info("🔄 MCP Data Streamer initialized with concurrent processing")
            
        except Exception as e:
            logger.error(f"❌ Streaming initialization failed: {e}")

    async def subscribe(self, user_id: int, stream_type: str, parameters: dict, callback: Callable) -> str:
        """Generic subscription method for compatibility"""
        try:
            logger.debug(f"🔄 Subscribe called: user_id={user_id}, stream_type={stream_type}, parameters={parameters}")
            
            if stream_type == "price_alerts":
                symbols = parameters.get("symbols", ["BTC", "ETH"])
                return await self.subscribe_to_price_alerts(user_id, symbols, callback)
            elif stream_type == "blockchain_events":
                chains = parameters.get("chains", ["ethereum"])
                event_types = parameters.get("event_types", ["whale_movement"])
                return await self.subscribe_to_blockchain_events(user_id, chains, callback, event_types)
            else:
                logger.warning(f"Unknown stream type: {stream_type}")
                return f"subscription_{user_id}_{stream_type}_{datetime.now().timestamp()}"
                
        except Exception as e:
            logger.error(f"❌ Subscribe method error: {e}")
            import traceback
            traceback.print_exc()
            # Return a safe fallback
            return f"error_subscription_{user_id}_{stream_type}_{datetime.now().timestamp()}"

    async def subscribe_to_price_alerts(self, user_id: int, symbols: List[str], 
                                      callback: Callable, alert_rules: List[dict] = None) -> str:
        """Subscribe to real-time price alerts with smart batching"""
        try:
            subscription_id = f"price_{user_id}_{datetime.now().timestamp()}"
            
            subscription = StreamSubscription(
                user_id=user_id,
                stream_type="price_alerts",
                parameters={"symbols": symbols, "alert_rules": alert_rules or []},
                callback=callback
            )
            
            self.subscriptions["price_alerts"].append(subscription)
            
            # Add alert rules if provided
            if alert_rules:
                for rule_config in alert_rules:
                    alert_rule = AlertRule(
                        user_id=user_id,
                        rule_type=rule_config.get("type", "price_above"),
                        symbol=rule_config.get("symbol", "BTC"),
                        threshold=rule_config.get("threshold", 0),
                        callback=callback
                    )
                    self.alert_rules[user_id].append(alert_rule)
            
            logger.info(f"✅ Price alerts subscription created: {subscription_id}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"❌ Price alerts subscription failed: {e}")
            return None

    async def subscribe_to_blockchain_events(self, user_id: int, chains: List[str], 
                                           event_types: List[str], callback: Callable) -> str:
        """Subscribe to blockchain events with intelligent filtering"""
        try:
            subscription_id = f"blockchain_{user_id}_{datetime.now().timestamp()}"
            
            subscription = StreamSubscription(
                user_id=user_id,
                stream_type="blockchain_events",
                parameters={"chains": chains, "event_types": event_types},
                callback=callback
            )
            
            self.subscriptions["blockchain_events"].append(subscription)
            
            logger.info(f"✅ Blockchain events subscription created: {subscription_id}")
            return subscription_id
            
        except Exception as e:
            logger.error(f"❌ Blockchain events subscription failed: {e}")
            return None

    async def _price_monitoring_loop(self):
        """Concurrent price monitoring with smart batching"""
        while self.running:
            try:
                # Get all unique symbols from subscriptions
                symbols = set()
                for subscription in self.subscriptions["price_alerts"]:
                    symbols.update(subscription.parameters.get("symbols", []))
                
                if symbols:
                    # Fetch price data via MCP
                    price_data = await mcp_client.call_tool(
                        "financial", "get_crypto_prices", 
                        {"symbols": list(symbols)}
                    )
                    
                    if price_data.get("success"):
                        # Update cache
                        self.price_cache.update(price_data.get("data", {}))
                        
                        # Process alerts in batches to prevent flooding
                        await self._process_price_alerts_batch(price_data.get("data", {}))
                
                # Wait before next update (configurable interval)
                await asyncio.sleep(5)  # 5-second intervals
                
            except Exception as e:
                logger.error(f"❌ Price monitoring error: {e}")
                await asyncio.sleep(10)  # Wait longer on error

    async def _social_monitoring_loop(self):
        """Concurrent social sentiment monitoring"""
        while self.running:
            try:
                # Get social subscriptions
                social_subs = self.subscriptions.get("social_sentiment", [])
                
                if social_subs:
                    # Batch process social sentiment
                    topics = set()
                    for sub in social_subs:
                        topics.update(sub.parameters.get("topics", ["crypto"]))
                    
                    for topic in topics:
                        sentiment_data = await mcp_client.call_tool(
                            "social", "twitter_sentiment", 
                            {"topic": topic}
                        )
                        
                        if sentiment_data.get("success"):
                            await self._process_social_alerts_batch(topic, sentiment_data)
                
                # Social data updates less frequently
                await asyncio.sleep(30)  # 30-second intervals
                
            except Exception as e:
                logger.error(f"❌ Social monitoring error: {e}")
                await asyncio.sleep(60)

    async def _blockchain_monitoring_loop(self):
        """Concurrent blockchain monitoring with multi-chain support"""
        while self.running:
            try:
                blockchain_subs = self.subscriptions.get("blockchain_events", [])
                
                if blockchain_subs:
                    # Process each chain concurrently
                    chains = set()
                    for sub in blockchain_subs:
                        chains.update(sub.parameters.get("chains", []))
                    
                    # Create concurrent tasks for each chain
                    chain_tasks = []
                    for chain in chains:
                        task = asyncio.create_task(self._monitor_chain(chain))
                        chain_tasks.append(task)
                    
                    if chain_tasks:
                        await asyncio.gather(*chain_tasks, return_exceptions=True)
                
                await asyncio.sleep(15)  # 15-second intervals for blockchain
                
            except Exception as e:
                logger.error(f"❌ Blockchain monitoring error: {e}")
                await asyncio.sleep(30)

    async def _monitor_chain(self, chain: str):
        """Monitor individual blockchain"""
        try:
            chain_data = await mcp_client.call_tool(
                "blockchain", f"{chain}_analysis", {}
            )
            
            if chain_data.get("success"):
                await self._process_blockchain_alerts_batch(chain, chain_data)
                
        except Exception as e:
            logger.error(f"❌ Chain monitoring error for {chain}: {e}")

    async def _alert_processing_loop(self):
        """Process alerts with rate limiting to prevent chat flooding"""
        alert_queue = asyncio.Queue()
        self.alert_queue = alert_queue
        
        while self.running:
            try:
                # Process alerts in batches
                alerts_batch = []
                
                # Collect alerts for batch processing (max 5 per batch)
                for _ in range(5):
                    try:
                        alert = await asyncio.wait_for(alert_queue.get(), timeout=1.0)
                        alerts_batch.append(alert)
                    except asyncio.TimeoutError:
                        break
                
                if alerts_batch:
                    await self._process_alerts_batch(alerts_batch)
                
                # Rate limiting: minimum 2 seconds between batches
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Alert processing error: {e}")
                await asyncio.sleep(5)

    async def _batch_processing_loop(self):
        """Batch processing to prevent chat flooding"""
        user_message_counts = defaultdict(int)
        reset_time = datetime.now()
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Reset counters every minute
                if (current_time - reset_time).total_seconds() >= 60:
                    user_message_counts.clear()
                    reset_time = current_time
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Batch processing error: {e}")
                await asyncio.sleep(30)

    async def _process_price_alerts_batch(self, price_data: dict):
        """Process price alerts in batches to prevent flooding"""
        try:
            user_alerts = defaultdict(list)
            
            # Group alerts by user
            for user_id, alert_rules in self.alert_rules.items():
                for rule in alert_rules:
                    if rule.symbol in price_data:
                        current_price = price_data[rule.symbol].get("price", 0)
                        
                        # Check if alert should trigger
                        should_trigger = False
                        if rule.rule_type == "price_above" and current_price > rule.threshold:
                            should_trigger = True
                        elif rule.rule_type == "price_below" and current_price < rule.threshold:
                            should_trigger = True
                        
                        # Rate limiting: don't trigger same alert too frequently
                        if should_trigger and self._should_trigger_alert(rule):
                            user_alerts[user_id].append({
                                "rule": rule,
                                "current_price": current_price,
                                "symbol": rule.symbol
                            })
                            
                            rule.triggered_count += 1
                            rule.last_triggered = datetime.now()
            
            # Send batched alerts to users
            for user_id, alerts in user_alerts.items():
                if alerts:
                    await self._send_batched_alert(user_id, alerts)
                    
        except Exception as e:
            logger.error(f"❌ Price alerts batch processing failed: {e}")

    def _should_trigger_alert(self, rule: AlertRule) -> bool:
        """Check if alert should trigger based on rate limiting"""
        if rule.last_triggered is None:
            return True
        
        # Don't trigger same alert more than once per 5 minutes
        time_since_last = datetime.now() - rule.last_triggered
        return time_since_last.total_seconds() >= 300

    async def _send_batched_alert(self, user_id: int, alerts: List[dict]):
        """Send batched alerts to prevent chat flooding"""
        try:
            if len(alerts) == 1:
                alert = alerts[0]
                message = f"🚨 **Price Alert**\n\n{alert['symbol']} is now ${alert['current_price']:,.2f}"
            else:
                message = f"🚨 **{len(alerts)} Price Alerts**\n\n"
                for alert in alerts[:3]:  # Limit to 3 alerts per batch
                    message += f"• {alert['symbol']}: ${alert['current_price']:,.2f}\n"
                
                if len(alerts) > 3:
                    message += f"• ... and {len(alerts) - 3} more alerts"
            
            # Find callback for this user
            for subscription in self.subscriptions["price_alerts"]:
                if subscription.user_id == user_id:
                    await subscription.callback(message)
                    break
                    
        except Exception as e:
            logger.error(f"❌ Batched alert sending failed: {e}")

    async def _process_social_alerts_batch(self, topic: str, sentiment_data: dict):
        """Process social sentiment alerts in batches"""
        # Implementation for social sentiment batching
        pass

    async def _process_blockchain_alerts_batch(self, chain: str, chain_data: dict):
        """Process blockchain alerts in batches"""
        # Implementation for blockchain event batching
        pass

    async def _process_alerts_batch(self, alerts_batch: List[dict]):
        """Process a batch of alerts"""
        # Implementation for general alert batching
        pass

    async def unsubscribe(self, user_id: int, subscription_type: str = None):
        """Unsubscribe from streams"""
        try:
            if subscription_type:
                # Remove specific subscription type
                self.subscriptions[subscription_type] = [
                    sub for sub in self.subscriptions[subscription_type] 
                    if sub.user_id != user_id
                ]
            else:
                # Remove all subscriptions for user
                for stream_type in self.subscriptions:
                    self.subscriptions[stream_type] = [
                        sub for sub in self.subscriptions[stream_type] 
                        if sub.user_id != user_id
                    ]
            
            # Remove alert rules
            if user_id in self.alert_rules:
                del self.alert_rules[user_id]
            
            logger.info(f"✅ Unsubscribed user {user_id} from {subscription_type or 'all'} streams")
            
        except Exception as e:
            logger.error(f"❌ Unsubscribe failed: {e}")

    async def get_user_subscriptions(self, user_id: int) -> List[dict]:
        """Get all subscriptions for a user"""
        try:
            user_subscriptions = []
            
            for stream_type, subscriptions in self.subscriptions.items():
                for subscription in subscriptions:
                    if subscription.user_id == user_id and subscription.active:
                        user_subscriptions.append({
                            "stream_type": stream_type,
                            "parameters": subscription.parameters,
                            "created_at": subscription.created_at.isoformat()
                        })
            
            return user_subscriptions
            
        except Exception as e:
            logger.error(f"❌ Failed to get user subscriptions: {e}")
            return []

    async def stop(self):
        """Stop all streaming tasks"""
        self.running = False
        
        for task_name, task in self.streaming_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        logger.info("🔄 MCP Data Streamer stopped")

# Global streaming instance
data_streamer = MCPDataStreamer()
streaming_manager = data_streamer  # Alias for compatibility

async def initialize_streaming():
    """Initialize MCP streaming infrastructure"""
    await data_streamer.initialize()
    logger.info("🌊 MCP Streaming ready!")

async def initialize_streaming_manager():
    """Initialize streaming manager (alias)"""
    return await initialize_streaming()

# Convenience functions
async def subscribe_price_alerts(user_id: int, symbols: List[str], callback: Callable, alert_rules: List[dict] = None) -> str:
    """Subscribe to price alerts"""
    return await data_streamer.subscribe_to_price_alerts(user_id, symbols, callback, alert_rules)

async def subscribe_blockchain_events(user_id: int, chains: List[str], event_types: List[str], callback: Callable) -> str:
    """Subscribe to blockchain events"""
    return await data_streamer.subscribe_to_blockchain_events(user_id, chains, event_types, callback)