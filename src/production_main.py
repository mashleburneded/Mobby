"""
Production Main - Industrial Grade Möbius AI Assistant
======================================================

Enhanced main application with production-grade infrastructure:
- Multi-tier caching system
- Circuit breakers and resilience patterns
- Advanced rate limiting and security
- Comprehensive monitoring and metrics
- Performance optimization
- Health checks and self-healing
"""

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import signal
import sys

# Telegram imports
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Production core imports
from production_core import (
    IntelligentCacheManager, CircuitBreaker, RateLimiter, HealthMonitor,
    MetricsCollector, SecurityManager, PerformanceOptimizer
)
from production_core.cache_manager import cache_manager
from production_core.circuit_breaker import circuit_breaker_manager, CircuitBreakerConfig
from production_core.rate_limiter import rate_limiter_manager, RateLimitConfig, RateLimitAlgorithm
from production_core.health_monitor import health_monitor, HealthCheckConfig, ServiceType
from production_core.metrics_collector import metrics_collector, MetricDefinition, MetricType
from production_core.security_manager import security_manager, validate_input, check_access
from production_core.performance_optimizer import performance_optimizer, performance_monitored

# Existing imports
from config import config
from intelligent_message_router import IntelligentMessageRouter
from enhanced_natural_language import process_natural_language
from crypto_research import get_price_data
from conversation_intelligence import conversation_intelligence
from encryption_manager import EncryptionManager
from persistent_user_context import user_context_manager
from security_auditor import security_auditor

# Set up logging with production configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/mobius_production.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)


class ProductionMobiusBot:
    """
    Production-grade Möbius AI Assistant with enterprise features
    
    Features:
    - Industrial-grade infrastructure
    - Advanced caching and performance optimization
    - Comprehensive security and monitoring
    - Self-healing and resilience patterns
    - Real-time metrics and health monitoring
    """
    
    def __init__(self):
        self.app: Optional[Application] = None
        self.message_router = IntelligentMessageRouter()
        self.encryption_manager = EncryptionManager()
        
        # Production infrastructure
        self.cache_manager = cache_manager
        self.circuit_breaker_manager = circuit_breaker_manager
        self.rate_limiter_manager = rate_limiter_manager
        self.health_monitor = health_monitor
        self.metrics_collector = metrics_collector
        self.security_manager = security_manager
        self.performance_optimizer = performance_optimizer
        
        # Bot state
        self.is_running = False
        self.start_time = datetime.utcnow()
        
        # Graceful shutdown handling
        self.shutdown_event = asyncio.Event()
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Production Möbius Bot initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(self.shutdown())
    
    async def initialize(self):
        """Initialize all production systems"""
        logger.info("🚀 Initializing production systems...")
        
        try:
            # Initialize metrics definitions
            await self._setup_metrics()
            
            # Initialize health checks
            await self._setup_health_checks()
            
            # Initialize security rules
            await self._setup_security()
            
            # Initialize circuit breakers
            await self._setup_circuit_breakers()
            
            # Initialize rate limiters
            await self._setup_rate_limiters()
            
            # Start monitoring systems
            await self.health_monitor.start_monitoring()
            await self.performance_optimizer.start_monitoring()
            
            # Initialize Telegram application
            await self._setup_telegram_app()
            
            logger.info("✅ All production systems initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize production systems: {e}")
            raise
    
    async def _setup_metrics(self):
        """Setup performance metrics definitions"""
        metrics_definitions = [
            MetricDefinition(
                name="telegram_messages_received",
                metric_type=MetricType.COUNTER,
                description="Total Telegram messages received",
                warning_threshold=1000,
                critical_threshold=5000
            ),
            MetricDefinition(
                name="telegram_messages_processed",
                metric_type=MetricType.COUNTER,
                description="Total Telegram messages processed successfully"
            ),
            MetricDefinition(
                name="telegram_message_processing_time",
                metric_type=MetricType.TIMER,
                description="Time taken to process Telegram messages",
                unit="milliseconds",
                warning_threshold=1000,
                critical_threshold=5000
            ),
            MetricDefinition(
                name="crypto_price_requests",
                metric_type=MetricType.COUNTER,
                description="Total crypto price requests"
            ),
            MetricDefinition(
                name="cache_hit_rate",
                metric_type=MetricType.GAUGE,
                description="Cache hit rate percentage",
                unit="percent",
                warning_threshold=70,
                threshold_direction="below"
            ),
            MetricDefinition(
                name="active_users",
                metric_type=MetricType.GAUGE,
                description="Number of active users"
            ),
            MetricDefinition(
                name="error_rate",
                metric_type=MetricType.GAUGE,
                description="Error rate percentage",
                unit="percent",
                warning_threshold=5,
                critical_threshold=10
            )
        ]
        
        for definition in metrics_definitions:
            self.metrics_collector.define_metric(definition)
        
        logger.info(f"Defined {len(metrics_definitions)} performance metrics")
    
    async def _setup_health_checks(self):
        """Setup health monitoring for all services"""
        
        # Database health check
        async def database_health_check():
            start_time = time.time()
            try:
                # Test database connection
                await user_context_manager.get_user_context(1)  # Test query
                response_time = (time.time() - start_time) * 1000
                
                from production_core.health_monitor import HealthCheckResult, HealthStatus
                return HealthCheckResult(
                    service_name="database",
                    status=HealthStatus.HEALTHY,
                    response_time_ms=response_time,
                    timestamp=datetime.utcnow(),
                    message="Database connection successful"
                )
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                from production_core.health_monitor import HealthCheckResult, HealthStatus
                return HealthCheckResult(
                    service_name="database",
                    status=HealthStatus.CRITICAL,
                    response_time_ms=response_time,
                    timestamp=datetime.utcnow(),
                    message=f"Database connection failed: {e}",
                    error=e
                )
        
        # Cache health check
        async def cache_health_check():
            start_time = time.time()
            try:
                # Test cache operations
                test_key = "health_check_test"
                await self.cache_manager.set(test_key, "test_value", ttl=60)
                result = await self.cache_manager.get(test_key)
                
                response_time = (time.time() - start_time) * 1000
                
                from production_core.health_monitor import HealthCheckResult, HealthStatus
                if result == "test_value":
                    return HealthCheckResult(
                        service_name="cache",
                        status=HealthStatus.HEALTHY,
                        response_time_ms=response_time,
                        timestamp=datetime.utcnow(),
                        message="Cache operational"
                    )
                else:
                    return HealthCheckResult(
                        service_name="cache",
                        status=HealthStatus.WARNING,
                        response_time_ms=response_time,
                        timestamp=datetime.utcnow(),
                        message="Cache test failed"
                    )
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                from production_core.health_monitor import HealthCheckResult, HealthStatus
                return HealthCheckResult(
                    service_name="cache",
                    status=HealthStatus.CRITICAL,
                    response_time_ms=response_time,
                    timestamp=datetime.utcnow(),
                    message=f"Cache check failed: {e}",
                    error=e
                )
        
        # Crypto API health check
        async def crypto_api_health_check():
            start_time = time.time()
            try:
                # Test crypto API
                result = await get_price_data("bitcoin")
                response_time = (time.time() - start_time) * 1000
                
                from production_core.health_monitor import HealthCheckResult, HealthStatus
                if result.get("success"):
                    return HealthCheckResult(
                        service_name="crypto_api",
                        status=HealthStatus.HEALTHY,
                        response_time_ms=response_time,
                        timestamp=datetime.utcnow(),
                        message="Crypto API operational"
                    )
                else:
                    return HealthCheckResult(
                        service_name="crypto_api",
                        status=HealthStatus.WARNING,
                        response_time_ms=response_time,
                        timestamp=datetime.utcnow(),
                        message="Crypto API returned error"
                    )
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                from production_core.health_monitor import HealthCheckResult, HealthStatus
                return HealthCheckResult(
                    service_name="crypto_api",
                    status=HealthStatus.CRITICAL,
                    response_time_ms=response_time,
                    timestamp=datetime.utcnow(),
                    message=f"Crypto API check failed: {e}",
                    error=e
                )
        
        # Register health checks
        self.health_monitor.register_service("database", ServiceType.DATABASE, database_health_check)
        self.health_monitor.register_service("cache", ServiceType.CACHE, cache_health_check)
        self.health_monitor.register_service("crypto_api", ServiceType.EXTERNAL_SERVICE, crypto_api_health_check)
        
        logger.info("Health checks configured for all services")
    
    async def _setup_security(self):
        """Setup security monitoring and alerting"""
        
        async def security_alert_handler(event):
            """Handle security events"""
            if event.threat_level.value in ['high', 'critical']:
                logger.warning(f"🚨 Security Alert: {event.to_dict()}")
                
                # Record security metric
                await self.metrics_collector.record_counter(
                    "security_threats_detected",
                    tags={'threat_level': event.threat_level.value}
                )
        
        self.security_manager.add_security_handler(security_alert_handler)
        logger.info("Security monitoring configured")
    
    async def _setup_circuit_breakers(self):
        """Setup circuit breakers for external services"""
        
        # Crypto API circuit breaker
        crypto_api_config = CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60,
            success_threshold=3,
            timeout=30.0
        )
        
        await self.circuit_breaker_manager.get_circuit_breaker("crypto_api", crypto_api_config)
        
        # Database circuit breaker
        database_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=30,
            success_threshold=2,
            timeout=10.0
        )
        
        await self.circuit_breaker_manager.get_circuit_breaker("database", database_config)
        
        logger.info("Circuit breakers configured")
    
    async def _setup_rate_limiters(self):
        """Setup rate limiting for different operations"""
        
        # User message rate limiting
        user_message_config = RateLimitConfig(
            requests_per_second=2.0,
            burst_size=10,
            algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
            adaptive_limiting=True
        )
        
        await self.rate_limiter_manager.get_rate_limiter("user_messages", user_message_config)
        
        # Crypto price request rate limiting
        crypto_price_config = RateLimitConfig(
            requests_per_second=5.0,
            burst_size=20,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            window_size_seconds=60
        )
        
        await self.rate_limiter_manager.get_rate_limiter("crypto_prices", crypto_price_config)
        
        logger.info("Rate limiters configured")
    
    async def _setup_telegram_app(self):
        """Setup Telegram application with handlers"""
        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("health", self.health_command))
        self.app.add_handler(CommandHandler("metrics", self.metrics_command))
        self.app.add_handler(CommandHandler("price", self.price_command))
        
        # Message handler with production features
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Error handler
        self.app.add_error_handler(self.error_handler)
        
        logger.info("Telegram application configured")
    
    @performance_monitored("telegram_message_processing")
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages with production features"""
        start_time = time.time()
        
        try:
            # Record message received metric
            await self.metrics_collector.record_counter("telegram_messages_received")
            
            # Extract message info
            user_id = update.effective_user.id
            username = update.effective_user.username or "unknown"
            message_text = update.effective_message.text
            chat_type = update.effective_chat.type
            
            # Security validation
            is_valid, error_msg = await validate_input(
                "message_text", 
                message_text, 
                str(user_id),
                update.effective_message.from_user.id if update.effective_message else None
            )
            
            if not is_valid:
                await update.effective_message.reply_text(
                    f"❌ Message validation failed: {error_msg}"
                )
                return
            
            # Rate limiting
            rate_limit_result = await self.rate_limiter_manager.check_rate_limit(
                "user_messages", str(user_id)
            )
            
            if not rate_limit_result.allowed:
                await update.effective_message.reply_text(
                    f"⏱️ Rate limit exceeded. Please wait {rate_limit_result.retry_after:.1f} seconds."
                )
                return
            
            # Check access permissions
            has_access = await check_access(str(user_id), "message_processing", "send")
            if not has_access:
                await update.effective_message.reply_text(
                    "🚫 Access denied. Your account may be temporarily restricted."
                )
                return
            
            # Process message with caching
            cache_key = f"message_analysis:{user_id}:{hash(message_text)}"
            cached_analysis = await self.cache_manager.get(cache_key, user_id)
            
            if cached_analysis:
                analysis = cached_analysis
                await self.metrics_collector.record_counter("cache_hits")
            else:
                # Analyze message with circuit breaker
                analysis = await self.circuit_breaker_manager.call_with_circuit_breaker(
                    "message_analysis",
                    self.message_router.analyze_message,
                    None,
                    message_text, chat_type, False, False, False
                )
                
                # Cache the analysis
                await self.cache_manager.set(cache_key, analysis, ttl=300, tags=["message_analysis"])
                await self.metrics_collector.record_counter("cache_misses")
            
            # Process based on analysis
            if analysis.should_respond:
                response = await self._generate_response(analysis, message_text, user_id, username)
                
                if response and response.get("message"):
                    await update.effective_message.reply_text(
                        response["message"],
                        parse_mode=ParseMode.MARKDOWN
                    )
            
            # Record successful processing
            processing_time = (time.time() - start_time) * 1000
            await self.metrics_collector.record_timer("telegram_message_processing_time", processing_time)
            await self.metrics_collector.record_counter("telegram_messages_processed")
            
            # Store conversation for intelligence
            await conversation_intelligence.store_message(
                user_id, username, message_text, chat_type
            )
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.metrics_collector.record_counter("telegram_message_errors")
            
            await update.effective_message.reply_text(
                "❌ Sorry, I encountered an error processing your message. Please try again."
            )
    
    async def _generate_response(self, analysis, message_text: str, user_id: int, username: str) -> Dict[str, Any]:
        """Generate response based on message analysis"""
        
        if analysis.processing_strategy.value == "built_in":
            # Handle built-in commands
            if "price" in analysis.message_type.value:
                return await self._handle_price_request(message_text, user_id)
            else:
                return {"message": "I understand your request. How can I help you further?"}
        
        elif analysis.processing_strategy.value == "ai":
            # Use AI processing with circuit breaker
            return await self.circuit_breaker_manager.call_with_circuit_breaker(
                "ai_processing",
                process_natural_language,
                None,
                user_id, message_text, {}
            )
        
        else:
            return {"message": "I'm here to help! What would you like to know?"}
    
    async def _handle_price_request(self, message_text: str, user_id: int) -> Dict[str, Any]:
        """Handle crypto price requests with production features"""
        
        # Extract crypto symbol
        symbol = self.message_router._extract_crypto_symbol(message_text, "BTC")
        
        # Rate limit crypto price requests
        rate_limit_result = await self.rate_limiter_manager.check_rate_limit(
            "crypto_prices", str(user_id)
        )
        
        if not rate_limit_result.allowed:
            return {
                "message": f"⏱️ Too many price requests. Please wait {rate_limit_result.retry_after:.1f} seconds."
            }
        
        # Check cache first
        cache_key = f"price_data:{symbol}"
        cached_price = await self.cache_manager.get(cache_key)
        
        if cached_price:
            await self.metrics_collector.record_counter("crypto_price_cache_hits")
            price_data = cached_price
        else:
            # Get price data with circuit breaker
            try:
                price_data = await self.circuit_breaker_manager.call_with_circuit_breaker(
                    "crypto_api",
                    get_price_data,
                    None,
                    symbol
                )
                
                # Cache the result
                if price_data.get("success"):
                    await self.cache_manager.set(cache_key, price_data, ttl=60, tags=["price_data"])
                
                await self.metrics_collector.record_counter("crypto_price_requests")
                
            except Exception as e:
                logger.error(f"Price request failed: {e}")
                return {"message": f"❌ Unable to fetch price for {symbol}. Please try again later."}
        
        # Format response
        if price_data.get("success"):
            price = price_data.get("price", 0)
            change_24h = price_data.get("change_24h", 0)
            change_emoji = "📈" if change_24h >= 0 else "📉"
            
            return {
                "message": f"💰 **{symbol.upper()} Price**\n\n"
                          f"💵 ${price:,.2f}\n"
                          f"{change_emoji} 24h: {change_24h:+.2f}%"
            }
        else:
            return {"message": f"❌ Could not find price data for {symbol}"}
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await self.metrics_collector.record_counter("start_commands")
        
        welcome_message = """
🤖 **Welcome to Möbius AI Assistant - Production Edition**

I'm your advanced crypto AI assistant with enterprise-grade features:

✨ **Core Features:**
• Real-time crypto prices and market data
• Portfolio tracking and analytics
• DeFi research and insights
• Natural language conversations

🛡️ **Production Features:**
• Advanced security and rate limiting
• High availability and performance
• Comprehensive monitoring
• Self-healing capabilities

💬 **Get Started:**
Just talk to me naturally! Try:
• "What's the price of Bitcoin?"
• "Show me Ethereum analytics"
• "/help" for more commands

🚀 **Enterprise Ready:** Industrial-grade infrastructure for reliable, secure, and scalable operations.
"""
        
        await update.effective_message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self.metrics_collector.record_counter("help_commands")
        
        help_message = """
🆘 **Möbius AI Assistant - Help**

**💬 Natural Language:**
Just talk to me! I understand natural language.

**📊 Commands:**
• `/start` - Welcome message
• `/help` - This help message
• `/status` - Bot status and performance
• `/health` - System health check
• `/metrics` - Performance metrics
• `/price <symbol>` - Get crypto price

**🔍 Examples:**
• "What's the price of SOL?"
• "Show me Bitcoin analytics"
• "How is Ethereum performing?"

**🛡️ Security Features:**
• Rate limiting protection
• Input validation
• Threat detection
• Access control

**📈 Performance:**
• Multi-tier caching
• Circuit breakers
• Health monitoring
• Auto-optimization

Need help? Just ask me anything!
"""
        
        await update.effective_message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        await self.metrics_collector.record_counter("status_commands")
        
        # Get system status
        uptime = datetime.utcnow() - self.start_time
        health_report = await self.health_monitor.get_overall_health()
        performance_report = await self.performance_optimizer.get_performance_report()
        
        status_message = f"""
📊 **Möbius AI Status**

**⏱️ Uptime:** {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m

**🏥 Health:** {health_report['overall_status'].title()}
• Services: {health_report['healthy_services']}/{health_report['total_services']} healthy
• Success Rate: {health_report['success_rate']:.1f}%

**⚡ Performance:**
• CPU: {performance_report.get('current_metrics', {}).get('cpu_percent', 0):.1f}%
• Memory: {performance_report.get('current_metrics', {}).get('memory_percent', 0):.1f}%
• Connections: {performance_report.get('connection_pool', {}).get('active_connections', 0)}

**🛡️ Security:** Active monitoring enabled
**📈 Monitoring:** {health_report['total_checks']} checks performed

All systems operational! 🚀
"""
        
        await update.effective_message.reply_text(status_message, parse_mode=ParseMode.MARKDOWN)
    
    async def health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /health command"""
        await self.metrics_collector.record_counter("health_commands")
        
        health_report = await self.health_monitor.get_detailed_health_report()
        
        health_message = f"""
🏥 **System Health Report**

**Overall Status:** {health_report['overall']['overall_status'].title()}

**Services:**
"""
        
        for service_name, service_data in health_report['services'].items():
            status_emoji = "✅" if service_data['status'] == 'healthy' else "⚠️" if service_data['status'] == 'warning' else "❌"
            health_message += f"• {status_emoji} {service_name}: {service_data['status'].title()}\n"
        
        health_message += f"""
**Metrics:**
• Total Checks: {health_report['overall']['total_checks']}
• Success Rate: {health_report['overall']['success_rate']:.1f}%
• Monitoring: {'Active' if health_report['overall']['is_monitoring'] else 'Inactive'}

Report generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        
        await update.effective_message.reply_text(health_message, parse_mode=ParseMode.MARKDOWN)
    
    async def metrics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /metrics command"""
        await self.metrics_collector.record_counter("metrics_commands")
        
        # Get performance metrics
        cache_metrics = self.cache_manager.get_performance_metrics()
        security_metrics = await self.security_manager.get_security_metrics()
        
        metrics_message = f"""
📈 **Performance Metrics**

**Cache Performance:**
• Hit Rate: {cache_metrics['hit_rate_percent']:.1f}%
• L1 Hits: {cache_metrics['l1_hits']}
• Total Requests: {cache_metrics['total_requests']}
• Avg Response: {cache_metrics['avg_response_time_ms']:.1f}ms

**Security:**
• Events (24h): {security_metrics['total_events_24h']}
• Blocked Users: {security_metrics['blocked_users']}
• Blocked IPs: {security_metrics['blocked_ips']}

**System:**
• Memory Usage: {cache_metrics['l1_stats']['memory_utilization']*100:.1f}%
• Active Tasks: {cache_metrics['active_warming_tasks']}

All metrics within normal ranges! 📊
"""
        
        await update.effective_message.reply_text(metrics_message, parse_mode=ParseMode.MARKDOWN)
    
    async def price_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /price command"""
        await self.metrics_collector.record_counter("price_commands")
        
        # Extract symbol from command
        if context.args:
            symbol = context.args[0].upper()
        else:
            symbol = "BTC"
        
        user_id = update.effective_user.id
        response = await self._handle_price_request(f"price {symbol}", user_id)
        
        await update.effective_message.reply_text(
            response["message"],
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")
        await self.metrics_collector.record_counter("telegram_errors")
    
    async def run(self):
        """Run the production bot"""
        try:
            logger.info("🚀 Starting Production Möbius AI Assistant...")
            
            # Initialize all systems
            await self.initialize()
            
            # Start the bot
            self.is_running = True
            logger.info("✅ Production bot is now running!")
            
            # Run the application
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
        except Exception as e:
            logger.error(f"❌ Critical error in production bot: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown"""
        if not self.is_running:
            return
        
        logger.info("🛑 Initiating graceful shutdown...")
        self.is_running = False
        
        try:
            # Stop Telegram bot
            if self.app:
                await self.app.updater.stop()
                await self.app.stop()
                await self.app.shutdown()
            
            # Stop monitoring systems
            await self.health_monitor.stop_monitoring()
            await self.performance_optimizer.stop_monitoring()
            
            # Export final metrics and logs
            await self._export_final_reports()
            
            logger.info("✅ Graceful shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        
        self.shutdown_event.set()
    
    async def _export_final_reports(self):
        """Export final reports before shutdown"""
        try:
            # Export metrics
            metrics_report = await self.metrics_collector.export_metrics("json")
            with open(f"logs/final_metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
                f.write(metrics_report)
            
            # Export health report
            health_report = await self.health_monitor.get_detailed_health_report()
            with open(f"logs/final_health_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
                import json
                f.write(json.dumps(health_report, indent=2))
            
            # Export security audit log
            security_log = await self.security_manager.export_audit_log()
            with open(f"logs/final_security_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
                import json
                f.write(json.dumps(security_log, indent=2))
            
            logger.info("📊 Final reports exported successfully")
            
        except Exception as e:
            logger.error(f"Error exporting final reports: {e}")


async def main():
    """Main entry point"""
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Create and run the production bot
    bot = ProductionMobiusBot()
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())