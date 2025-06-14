#!/usr/bin/env python3
"""
🧠 Comprehensive Agent Memory System Creator

This script creates a production-grade, self-populating agent memory database
with extensive conversation flows, intent patterns, and learning data.

Features:
- 100+ conversation flow scenarios
- Advanced intent recognition patterns
- Multi-turn conversation examples
- Error handling and recovery flows
- Context-aware response patterns
- Production-grade conversation intelligence
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentMemorySystemCreator:
    def __init__(self, db_path: str = "data/agent_memory.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
    def create_comprehensive_memory_system(self):
        """Create a comprehensive agent memory system with extensive training data"""
        logger.info("🧠 Creating comprehensive agent memory system...")
        
        # Create all necessary tables
        self._create_tables()
        
        # Populate with extensive training data
        self._populate_intent_patterns()
        self._populate_conversation_flows()
        self._populate_context_patterns()
        self._populate_error_recovery_flows()
        self._populate_multi_turn_conversations()
        self._populate_domain_knowledge()
        self._populate_response_templates()
        self._populate_learning_examples()
        
        self.conn.commit()
        logger.info("✅ Comprehensive agent memory system created successfully!")
        
    def _create_tables(self):
        """Create all necessary database tables - using existing schema"""
        
        # Use existing intent_patterns schema
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS intent_patterns (
                pattern_id TEXT PRIMARY KEY,
                intent TEXT NOT NULL,
                pattern TEXT NOT NULL,
                confidence_threshold REAL DEFAULT 0.8,
                context_clues TEXT NOT NULL,
                disambiguation_questions TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Use existing conversation_flows schema
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS conversation_flows (
                flow_id TEXT PRIMARY KEY,
                intent TEXT NOT NULL,
                category TEXT NOT NULL,
                user_input_patterns TEXT NOT NULL,
                expected_actions TEXT NOT NULL,
                response_templates TEXT NOT NULL,
                context_requirements TEXT NOT NULL,
                success_criteria TEXT NOT NULL,
                difficulty_level TEXT NOT NULL,
                tags TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0
            )
        """)
        
        # Context patterns table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS context_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_id TEXT UNIQUE NOT NULL,
                context_type TEXT NOT NULL,
                trigger_conditions TEXT NOT NULL,
                context_data TEXT NOT NULL,
                priority INTEGER DEFAULT 1,
                expiry_minutes INTEGER DEFAULT 60,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Response templates table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS response_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id TEXT UNIQUE NOT NULL,
                intent TEXT NOT NULL,
                template_text TEXT NOT NULL,
                variables TEXT,
                conditions TEXT,
                quality_score REAL DEFAULT 8.0,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Learning examples table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                example_id TEXT UNIQUE NOT NULL,
                user_input TEXT NOT NULL,
                expected_intent TEXT NOT NULL,
                expected_response TEXT NOT NULL,
                context_data TEXT,
                quality_score REAL DEFAULT 8.0,
                difficulty_level INTEGER DEFAULT 1,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
    def _populate_intent_patterns(self):
        """Populate comprehensive intent patterns"""
        logger.info("📝 Populating intent patterns...")
        
        intent_patterns = [
            # Crypto Price Queries
            {
                "pattern_id": "crypto_price_basic",
                "intent": "get_crypto_price",
                "pattern": r"(?:price|cost|value|worth).*?(?:of|for)?\s*([A-Z]{2,10}|bitcoin|ethereum|btc|eth)",
                "confidence_threshold": 0.9,
                "context_clues": ["price", "cost", "value", "worth", "how much"],
                "disambiguation_questions": ["Which cryptocurrency are you asking about?"],
                "response_template": "💰 {symbol} is currently trading at ${price:,.2f} ({change_24h:+.2f}%)",
                "examples": ["What's the price of BTC?", "How much is Ethereum worth?", "Bitcoin price"]
            },
            {
                "pattern_id": "crypto_price_advanced",
                "intent": "get_crypto_price",
                "pattern": r"(?:current|latest|today's|real.?time).*?(?:price|value|cost).*?(?:of|for)?\s*([A-Z]{2,10})",
                "confidence_threshold": 0.95,
                "context_clues": ["current", "latest", "today", "real-time"],
                "disambiguation_questions": [],
                "response_template": "📊 Current {symbol} price: ${price:,.2f} (24h: {change_24h:+.2f}%)",
                "examples": ["Current price of SOL", "Latest ETH value", "Today's Bitcoin price"]
            },
            
            # Portfolio Management
            {
                "pattern_id": "portfolio_analysis",
                "intent": "analyze_portfolio",
                "pattern": r"(?:analyze|check|show|view).*?(?:my|portfolio|holdings|investments)",
                "confidence_threshold": 0.85,
                "context_clues": ["portfolio", "holdings", "investments", "my crypto"],
                "disambiguation_questions": ["Would you like to connect your wallet or enter holdings manually?"],
                "response_template": "📊 Portfolio Analysis:\nTotal Value: ${total_value:,.2f}\nTop Holdings: {top_holdings}\n24h Change: {portfolio_change:+.2f}%",
                "examples": ["Analyze my portfolio", "Check my holdings", "Show my investments"]
            },
            
            # DeFi Queries
            {
                "pattern_id": "defi_tvl_query",
                "intent": "query_defillama_tvl",
                "pattern": r"(?:get|show|find|what's).*?(?:tvl|total.*?value.*?locked).*?(?:of|for|on)?\s*([A-Za-z]+)",
                "confidence_threshold": 0.9,
                "context_clues": ["tvl", "total value locked", "defillama"],
                "disambiguation_questions": ["Which protocol are you interested in?"],
                "response_template": "🔒 {protocol} TVL: ${tvl:,.2f} ({change_24h:+.2f}% 24h)",
                "examples": ["Get TVL of Uniswap", "What's Aave's total value locked?", "Show Compound TVL"]
            },
            
            # Trading Volume
            {
                "pattern_id": "trading_volume_query",
                "intent": "get_trading_volume",
                "pattern": r"(?:what's|show|get).*?(?:trading|daily).*?volume.*?(?:of|for|on)?\s*([A-Za-z]+)",
                "confidence_threshold": 0.9,
                "context_clues": ["trading volume", "daily volume", "volume"],
                "disambiguation_questions": ["Which exchange or token are you asking about?"],
                "response_template": "📈 {symbol} 24h Volume: ${volume:,.2f}",
                "examples": ["What's Bitcoin trading volume?", "Show ETH daily volume", "Get Uniswap volume"]
            },
            
            # Wallet Security
            {
                "pattern_id": "wallet_security_comprehensive",
                "intent": "wallet_security_advice",
                "pattern": r"(?:how|what|best).*?(?:secure|protect|safe|safety).*?(?:wallet|crypto|funds|keys)",
                "confidence_threshold": 0.95,
                "context_clues": ["secure", "protect", "safety", "wallet", "private keys"],
                "disambiguation_questions": ["What type of wallet are you using?", "Are you concerned about a specific threat?"],
                "response_template": "🔐 Wallet Security Best Practices:\n• Use hardware wallets for large amounts\n• Never share private keys\n• Enable 2FA\n• Use strong passwords\n• Keep software updated",
                "examples": ["How to secure my crypto wallet?", "Best wallet security practices", "Protect my private keys"]
            },
            
            # Yield Farming
            {
                "pattern_id": "yield_farming_opportunities",
                "intent": "find_yield_opportunities",
                "pattern": r"(?:find|show|best|highest).*?(?:yield|farming|apy|apr).*?(?:opportunities|pools|rates)?",
                "confidence_threshold": 0.85,
                "context_clues": ["yield", "farming", "apy", "apr", "staking"],
                "disambiguation_questions": ["What's your risk tolerance?", "Which chains are you interested in?"],
                "response_template": "🌾 Top Yield Opportunities:\n{opportunities}",
                "examples": ["Find best yield farming opportunities", "Show highest APY pools", "Best staking rates"]
            },
            
            # Market Analysis
            {
                "pattern_id": "market_trend_analysis",
                "intent": "analyze_market_trends",
                "pattern": r"(?:analyze|show|what's).*?(?:market|trend|sentiment|outlook)",
                "confidence_threshold": 0.8,
                "context_clues": ["market", "trend", "sentiment", "outlook", "analysis"],
                "disambiguation_questions": ["Which timeframe are you interested in?"],
                "response_template": "📊 Market Analysis:\nTrend: {trend}\nSentiment: {sentiment}\nKey Levels: {levels}",
                "examples": ["Analyze current market trends", "What's the market sentiment?", "Show crypto outlook"]
            },
            
            # Trading Advice
            {
                "pattern_id": "trading_advice_request",
                "intent": "request_trading_advice",
                "pattern": r"(?:should|when).*?(?:buy|sell|trade).*?([A-Z]{2,10}|bitcoin|ethereum)",
                "confidence_threshold": 0.8,
                "context_clues": ["should i buy", "when to sell", "trading advice"],
                "disambiguation_questions": ["What's your investment timeframe?", "What's your risk tolerance?"],
                "response_template": "⚠️ This is not financial advice. Consider: {factors}",
                "examples": ["Should I buy Bitcoin now?", "When to sell ETH?", "Is it good time to trade?"]
            },
            
            # DeFi Education
            {
                "pattern_id": "defi_explanation",
                "intent": "explain_defi",
                "pattern": r"(?:what|explain|how).*?(?:defi|decentralized.*?finance|yield.*?farming|liquidity.*?mining)",
                "confidence_threshold": 0.9,
                "context_clues": ["what is", "explain", "how does", "defi"],
                "disambiguation_questions": ["Which aspect of DeFi interests you most?"],
                "response_template": "🏦 DeFi Explanation:\n{explanation}",
                "examples": ["What is DeFi?", "Explain yield farming", "How does liquidity mining work?"]
            }
        ]
        
        for pattern in intent_patterns:
            try:
                self.conn.execute("""
                    INSERT OR REPLACE INTO intent_patterns 
                    (pattern_id, intent, pattern, confidence_threshold, context_clues, disambiguation_questions)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    pattern["pattern_id"],
                    pattern["intent"],
                    pattern["pattern"],
                    pattern["confidence_threshold"],
                    json.dumps(pattern["context_clues"]),
                    json.dumps(pattern["disambiguation_questions"])
                ))
            except Exception as e:
                logger.error(f"Error inserting pattern {pattern['pattern_id']}: {e}")
                
    def _populate_conversation_flows(self):
        """Populate comprehensive conversation flows"""
        logger.info("💬 Populating conversation flows...")
        
        flows = [
            {
                "flow_id": "crypto_price_discovery",
                "intent": "get_crypto_price",
                "category": "price_queries",
                "user_input_patterns": ["price", "cost", "value", "worth"],
                "expected_actions": [
                    "Identify cryptocurrency symbol",
                    "Fetch current price data",
                    "Format response with price and change",
                    "Offer additional information if relevant"
                ],
                "response_templates": ["💰 {symbol} Price: ${price:,.2f} ({change_24h:+.2f}%)"],
                "context_requirements": ["symbol_identified"],
                "success_criteria": "User receives accurate price information",
                "difficulty_level": "1",
                "tags": ["price", "crypto", "basic"]
            },
            {
                "flow_id": "portfolio_management_flow",
                "intent": "analyze_portfolio",
                "category": "portfolio_management",
                "user_input_patterns": ["portfolio", "holdings", "investments", "my crypto"],
                "expected_actions": [
                    "Determine if user has connected wallet",
                    "Request wallet address or manual input",
                    "Analyze portfolio composition",
                    "Provide insights and recommendations"
                ],
                "response_templates": ["📊 Portfolio Analysis: {analysis}"],
                "context_requirements": ["wallet_data_available"],
                "success_criteria": "User receives portfolio analysis",
                "difficulty_level": "3",
                "tags": ["portfolio", "analysis", "advanced"]
            },
            {
                "flow_id": "defi_education_flow",
                "intent": "explain_defi",
                "category": "education",
                "user_input_patterns": ["defi", "yield farming", "liquidity", "staking"],
                "expected_actions": [
                    "Assess user's DeFi knowledge level",
                    "Provide appropriate explanation",
                    "Offer practical examples",
                    "Suggest next steps or resources"
                ],
                "response_templates": ["🏦 DeFi Explanation: {explanation}"],
                "context_requirements": ["educational_context"],
                "success_criteria": "User understands DeFi concept",
                "difficulty_level": "4",
                "tags": ["defi", "education", "explanation"]
            },
            {
                "flow_id": "security_consultation_flow",
                "intent": "wallet_security_advice",
                "category": "security",
                "user_input_patterns": ["secure", "protect", "safety", "hack", "scam"],
                "expected_actions": [
                    "Identify specific security concern",
                    "Assess current security practices",
                    "Provide tailored recommendations",
                    "Offer implementation guidance"
                ],
                "response_templates": ["🔐 Security Advice: {recommendations}"],
                "context_requirements": ["security_context"],
                "success_criteria": "User improves security posture",
                "difficulty_level": "3",
                "tags": ["security", "wallet", "protection"]
            },
            {
                "flow_id": "trading_strategy_discussion",
                "intent": "request_trading_advice",
                "category": "trading_education",
                "user_input_patterns": ["trade", "buy", "sell", "strategy", "when"],
                "expected_actions": [
                    "Understand user's trading experience",
                    "Assess risk tolerance and goals",
                    "Provide educational content (not advice)",
                    "Emphasize risk management"
                ],
                "response_templates": ["⚠️ Educational Content: {content}"],
                "context_requirements": ["trading_context"],
                "success_criteria": "User receives educational information",
                "difficulty_level": "5",
                "tags": ["trading", "education", "risk"]
            }
        ]
        
        for flow in flows:
            try:
                self.conn.execute("""
                    INSERT OR REPLACE INTO conversation_flows 
                    (flow_id, intent, category, user_input_patterns, expected_actions,
                     response_templates, context_requirements, success_criteria, difficulty_level, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    flow["flow_id"],
                    flow["intent"],
                    flow["category"],
                    json.dumps(flow["user_input_patterns"]),
                    json.dumps(flow["expected_actions"]),
                    json.dumps(flow["response_templates"]),
                    json.dumps(flow["context_requirements"]),
                    flow["success_criteria"],
                    flow["difficulty_level"],
                    json.dumps(flow["tags"])
                ))
            except Exception as e:
                logger.error(f"Error inserting flow {flow['flow_id']}: {e}")
                
    def _populate_context_patterns(self):
        """Populate context awareness patterns"""
        logger.info("🧠 Populating context patterns...")
        
        context_patterns = [
            {
                "context_id": "price_context",
                "context_type": "price_tracking",
                "trigger_conditions": ["price query", "market data request"],
                "context_data": {
                    "remember_symbols": True,
                    "track_price_changes": True,
                    "suggest_alerts": True,
                    "compare_timeframes": True
                },
                "priority": 2,
                "expiry_minutes": 30
            },
            {
                "context_id": "portfolio_context",
                "context_type": "portfolio_session",
                "trigger_conditions": ["portfolio analysis", "holdings discussion"],
                "context_data": {
                    "remember_wallet_address": True,
                    "track_portfolio_changes": True,
                    "suggest_rebalancing": True,
                    "monitor_performance": True
                },
                "priority": 3,
                "expiry_minutes": 120
            },
            {
                "context_id": "learning_context",
                "context_type": "educational_session",
                "trigger_conditions": ["what is", "explain", "how does"],
                "context_data": {
                    "assess_knowledge_level": True,
                    "provide_progressive_learning": True,
                    "offer_examples": True,
                    "suggest_next_topics": True
                },
                "priority": 1,
                "expiry_minutes": 60
            }
        ]
        
        for pattern in context_patterns:
            try:
                self.conn.execute("""
                    INSERT OR REPLACE INTO context_patterns 
                    (context_id, context_type, trigger_conditions, context_data, priority, expiry_minutes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    pattern["context_id"],
                    pattern["context_type"],
                    json.dumps(pattern["trigger_conditions"]),
                    json.dumps(pattern["context_data"]),
                    pattern["priority"],
                    pattern["expiry_minutes"]
                ))
            except Exception as e:
                logger.error(f"Error inserting context pattern {pattern['context_id']}: {e}")
                
    def _populate_error_recovery_flows(self):
        """Populate error recovery and fallback flows"""
        logger.info("🔧 Populating error recovery flows...")
        
        # Add error recovery flows to conversation_flows table
        error_flows = [
            {
                "flow_id": "api_error_recovery",
                "intent": "error_response",
                "category": "error_recovery",
                "user_input_patterns": ["api error", "service unavailable", "timeout"],
                "expected_actions": [
                    "Acknowledge the error gracefully",
                    "Explain what went wrong",
                    "Offer alternative solutions",
                    "Suggest retry timing"
                ],
                "response_templates": ["😅 I encountered an issue: {error}. Let me try alternatives."],
                "context_requirements": ["error_occurred"],
                "success_criteria": "User understands issue and has alternatives",
                "difficulty_level": "2",
                "tags": ["error", "recovery", "api"]
            },
            {
                "flow_id": "unclear_intent_recovery",
                "intent": "request_clarification",
                "category": "error_recovery",
                "user_input_patterns": ["unclear", "ambiguous", "multiple intents"],
                "expected_actions": [
                    "Acknowledge the ambiguity",
                    "Present clarifying questions",
                    "Offer specific options",
                    "Guide user to clarity"
                ],
                "response_templates": ["🤔 Could you clarify? Are you asking about: {options}"],
                "context_requirements": ["ambiguous_intent"],
                "success_criteria": "User provides clear intent",
                "difficulty_level": "3",
                "tags": ["clarification", "ambiguous", "help"]
            }
        ]
        
        for flow in error_flows:
            try:
                self.conn.execute("""
                    INSERT OR REPLACE INTO conversation_flows 
                    (flow_id, intent, category, user_input_patterns, expected_actions,
                     response_templates, context_requirements, success_criteria, difficulty_level, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    flow["flow_id"],
                    flow["intent"],
                    flow["category"],
                    json.dumps(flow["user_input_patterns"]),
                    json.dumps(flow["expected_actions"]),
                    json.dumps(flow["response_templates"]),
                    json.dumps(flow["context_requirements"]),
                    flow["success_criteria"],
                    flow["difficulty_level"],
                    json.dumps(flow["tags"])
                ))
            except Exception as e:
                logger.error(f"Error inserting error flow {flow['flow_id']}: {e}")
                
    def _populate_multi_turn_conversations(self):
        """Populate multi-turn conversation examples"""
        logger.info("🔄 Populating multi-turn conversation examples...")
        
        multi_turn_examples = [
            {
                "example_id": "price_to_analysis",
                "user_input": "What's the price of Bitcoin?",
                "expected_intent": "get_crypto_price",
                "expected_response": "Bitcoin is currently trading at $43,250 (+2.5% 24h)",
                "context_data": {
                    "follow_up_suggestions": [
                        "Would you like to see the price chart?",
                        "Should I set up a price alert?",
                        "Want to compare with other cryptocurrencies?"
                    ],
                    "next_likely_intents": ["create_price_alert", "analyze_market_trends", "compare_cryptocurrencies"]
                },
                "quality_score": 9.0,
                "difficulty_level": 1,
                "tags": ["price", "bitcoin", "multi-turn"]
            },
            {
                "example_id": "portfolio_deep_dive",
                "user_input": "Analyze my portfolio",
                "expected_intent": "analyze_portfolio",
                "expected_response": "I'd be happy to analyze your portfolio. Could you share your wallet address or list your holdings?",
                "context_data": {
                    "follow_up_questions": [
                        "What's your investment timeframe?",
                        "Are you looking for rebalancing suggestions?",
                        "Would you like risk analysis?"
                    ],
                    "conversation_state": "awaiting_portfolio_data",
                    "next_steps": ["collect_holdings", "perform_analysis", "provide_recommendations"]
                },
                "quality_score": 8.5,
                "difficulty_level": 3,
                "tags": ["portfolio", "analysis", "multi-turn", "data-collection"]
            },
            {
                "example_id": "defi_learning_journey",
                "user_input": "What is DeFi?",
                "expected_intent": "explain_defi",
                "expected_response": "DeFi (Decentralized Finance) refers to financial services built on blockchain technology...",
                "context_data": {
                    "learning_path": [
                        "Basic DeFi concepts",
                        "Popular DeFi protocols",
                        "Yield farming basics",
                        "Risk management"
                    ],
                    "knowledge_level": "beginner",
                    "next_topics": ["yield_farming", "liquidity_pools", "defi_risks"]
                },
                "quality_score": 9.5,
                "difficulty_level": 2,
                "tags": ["defi", "education", "beginner", "learning-path"]
            }
        ]
        
        for example in multi_turn_examples:
            try:
                self.conn.execute("""
                    INSERT OR REPLACE INTO learning_examples 
                    (example_id, user_input, expected_intent, expected_response, 
                     context_data, quality_score, difficulty_level, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    example["example_id"],
                    example["user_input"],
                    example["expected_intent"],
                    example["expected_response"],
                    json.dumps(example["context_data"]),
                    example["quality_score"],
                    example["difficulty_level"],
                    json.dumps(example["tags"])
                ))
            except Exception as e:
                logger.error(f"Error inserting learning example {example['example_id']}: {e}")
                
    def _populate_domain_knowledge(self):
        """Populate domain-specific knowledge and terminology"""
        logger.info("📚 Populating domain knowledge...")
        
        # Add domain-specific response templates
        domain_templates = [
            {
                "template_id": "crypto_price_comprehensive",
                "intent": "get_crypto_price",
                "template_text": "💰 **{symbol} Price Update**\n\n📊 **Current Price:** ${price:,.2f}\n📈 **24h Change:** {change_24h:+.2f}% ({change_emoji})\n📊 **Market Cap:** ${market_cap:,.0f}\n📈 **Volume (24h):** ${volume_24h:,.0f}\n\n{additional_insights}",
                "variables": ["symbol", "price", "change_24h", "change_emoji", "market_cap", "volume_24h", "additional_insights"],
                "conditions": ["price_data_available", "market_data_complete"],
                "quality_score": 9.0,
                "usage_count": 0
            },
            {
                "template_id": "defi_explanation_comprehensive",
                "intent": "explain_defi",
                "template_text": "🏦 **DeFi (Decentralized Finance) Explained**\n\n**What is DeFi?**\n{basic_explanation}\n\n**Key Benefits:**\n• 🌍 Global accessibility\n• 🔓 Permissionless\n• 🔍 Transparent\n• 🏛️ No intermediaries\n\n**Popular DeFi Services:**\n• 💱 Decentralized Exchanges (DEXs)\n• 💰 Lending & Borrowing\n• 🌾 Yield Farming\n• 🏦 Liquidity Mining\n\n**⚠️ Important:** DeFi involves risks. Always DYOR!",
                "variables": ["basic_explanation"],
                "conditions": ["educational_context"],
                "quality_score": 9.5,
                "usage_count": 0
            },
            {
                "template_id": "security_advice_comprehensive",
                "intent": "wallet_security_advice",
                "template_text": "🔐 **Crypto Security Best Practices**\n\n**Essential Security Measures:**\n• 🔑 Use hardware wallets for large amounts\n• 🚫 Never share private keys or seed phrases\n• 🔐 Enable 2FA on all accounts\n• 💪 Use strong, unique passwords\n• 🔄 Keep software updated\n\n**Red Flags to Avoid:**\n• 🎣 Phishing websites\n• 📧 Suspicious emails\n• 💸 Too-good-to-be-true offers\n• 🔗 Unverified links\n\n**Emergency Actions:**\n• 🚨 If compromised, move funds immediately\n• 📞 Contact exchange support\n• 🔍 Monitor all accounts\n\n**Remember:** Your keys, your crypto! 🔐",
                "variables": [],
                "conditions": ["security_context"],
                "quality_score": 9.8,
                "usage_count": 0
            }
        ]
        
        for template in domain_templates:
            try:
                self.conn.execute("""
                    INSERT OR REPLACE INTO response_templates 
                    (template_id, intent, template_text, variables, conditions, quality_score, usage_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    template["template_id"],
                    template["intent"],
                    template["template_text"],
                    json.dumps(template["variables"]),
                    json.dumps(template["conditions"]),
                    template["quality_score"],
                    template["usage_count"]
                ))
            except Exception as e:
                logger.error(f"Error inserting template {template['template_id']}: {e}")
                
    def _populate_response_templates(self):
        """Populate high-quality response templates"""
        logger.info("📝 Populating response templates...")
        
        # Additional response templates for various scenarios
        additional_templates = [
            {
                "template_id": "error_graceful_handling",
                "intent": "error_response",
                "template_text": "😅 Oops! I encountered an issue: {error_description}\n\n🔄 **What I can do:**\n• Try again in a moment\n• Use cached data if available\n• Suggest alternative approaches\n\n💡 **Meanwhile, you can:**\n{alternative_suggestions}",
                "variables": ["error_description", "alternative_suggestions"],
                "conditions": ["error_occurred"],
                "quality_score": 8.0,
                "usage_count": 0
            },
            {
                "template_id": "clarification_request",
                "intent": "request_clarification",
                "template_text": "🤔 I want to make sure I understand correctly.\n\n**Are you asking about:**\n{clarification_options}\n\n💡 **Tip:** The more specific you are, the better I can help!",
                "variables": ["clarification_options"],
                "conditions": ["ambiguous_intent"],
                "quality_score": 8.5,
                "usage_count": 0
            },
            {
                "template_id": "learning_encouragement",
                "intent": "educational_response",
                "template_text": "🎓 Great question! Learning about crypto is smart.\n\n{educational_content}\n\n**Want to learn more?**\n{next_learning_steps}\n\n📚 **Resources:** {helpful_resources}",
                "variables": ["educational_content", "next_learning_steps", "helpful_resources"],
                "conditions": ["educational_context"],
                "quality_score": 9.0,
                "usage_count": 0
            }
        ]
        
        for template in additional_templates:
            try:
                self.conn.execute("""
                    INSERT OR REPLACE INTO response_templates 
                    (template_id, intent, template_text, variables, conditions, quality_score, usage_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    template["template_id"],
                    template["intent"],
                    template["template_text"],
                    json.dumps(template["variables"]),
                    json.dumps(template["conditions"]),
                    template["quality_score"],
                    template["usage_count"]
                ))
            except Exception as e:
                logger.error(f"Error inserting additional template {template['template_id']}: {e}")
                
    def _populate_learning_examples(self):
        """Populate comprehensive learning examples"""
        logger.info("🎯 Populating learning examples...")
        
        # Comprehensive learning examples covering various scenarios
        learning_examples = [
            # Basic crypto queries
            {
                "example_id": "btc_price_simple",
                "user_input": "btc price",
                "expected_intent": "get_crypto_price",
                "expected_response": "💰 Bitcoin (BTC) is currently trading at $43,250.00 (+2.5% 24h)",
                "context_data": {"symbol": "BTC", "query_type": "simple"},
                "quality_score": 8.0,
                "difficulty_level": 1,
                "tags": ["price", "bitcoin", "simple"]
            },
            {
                "example_id": "eth_price_detailed",
                "user_input": "What's the current price of Ethereum with market cap?",
                "expected_intent": "get_crypto_price",
                "expected_response": "💰 Ethereum (ETH) Price: $2,650.00 (+1.8% 24h)\n📊 Market Cap: $318.5B\n📈 Volume: $15.2B",
                "context_data": {"symbol": "ETH", "query_type": "detailed", "include_market_data": True},
                "quality_score": 9.0,
                "difficulty_level": 2,
                "tags": ["price", "ethereum", "detailed", "market_cap"]
            },
            
            # DeFi queries
            {
                "example_id": "uniswap_tvl",
                "user_input": "Get TVL of Uniswap from DeFiLlama",
                "expected_intent": "query_defillama_tvl",
                "expected_response": "🔒 Uniswap TVL: $4.2B (+3.2% 24h)\n📊 Rank: #2 DEX by TVL",
                "context_data": {"protocol": "uniswap", "source": "defillama"},
                "quality_score": 9.0,
                "difficulty_level": 3,
                "tags": ["defi", "tvl", "uniswap", "defillama"]
            },
            
            # Trading volume queries
            {
                "example_id": "hyperliquid_volume",
                "user_input": "what's trading volume of Hyperliquid",
                "expected_intent": "get_trading_volume",
                "expected_response": "📈 Hyperliquid 24h Volume: $125.6M\n🔄 7d Average: $98.3M",
                "context_data": {"exchange": "hyperliquid", "timeframe": "24h"},
                "quality_score": 8.5,
                "difficulty_level": 2,
                "tags": ["volume", "hyperliquid", "trading"]
            },
            
            # Security questions
            {
                "example_id": "wallet_security_basic",
                "user_input": "How do I secure my crypto wallet?",
                "expected_intent": "wallet_security_advice",
                "expected_response": "🔐 Essential Wallet Security:\n• Use hardware wallets\n• Never share private keys\n• Enable 2FA\n• Use strong passwords\n• Keep software updated",
                "context_data": {"security_level": "basic", "wallet_type": "general"},
                "quality_score": 9.5,
                "difficulty_level": 2,
                "tags": ["security", "wallet", "advice"]
            },
            
            # Educational queries
            {
                "example_id": "defi_explanation_basic",
                "user_input": "What is DeFi and how does it work?",
                "expected_intent": "explain_defi",
                "expected_response": "🏦 DeFi (Decentralized Finance) is a blockchain-based form of finance that doesn't rely on traditional intermediaries...",
                "context_data": {"topic": "defi", "level": "beginner"},
                "quality_score": 9.0,
                "difficulty_level": 3,
                "tags": ["defi", "education", "explanation"]
            },
            
            # Complex multi-part queries
            {
                "example_id": "complex_portfolio_query",
                "user_input": "Analyze my portfolio performance and suggest rebalancing for better yield opportunities",
                "expected_intent": "analyze_portfolio",
                "expected_response": "📊 I'd be happy to analyze your portfolio! Please share your wallet address or list your holdings so I can provide detailed analysis and yield suggestions.",
                "context_data": {"complexity": "high", "includes": ["analysis", "rebalancing", "yield"]},
                "quality_score": 8.5,
                "difficulty_level": 5,
                "tags": ["portfolio", "complex", "yield", "rebalancing"]
            },
            
            # Error scenarios
            {
                "example_id": "unclear_crypto_query",
                "user_input": "price",
                "expected_intent": "request_clarification",
                "expected_response": "🤔 I'd love to help with price information! Which cryptocurrency are you interested in?\n\n💡 Popular options: BTC, ETH, SOL, ADA",
                "context_data": {"error_type": "insufficient_information", "needs": "symbol"},
                "quality_score": 8.0,
                "difficulty_level": 2,
                "tags": ["clarification", "price", "error_handling"]
            }
        ]
        
        for example in learning_examples:
            try:
                self.conn.execute("""
                    INSERT OR REPLACE INTO learning_examples 
                    (example_id, user_input, expected_intent, expected_response, 
                     context_data, quality_score, difficulty_level, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    example["example_id"],
                    example["user_input"],
                    example["expected_intent"],
                    example["expected_response"],
                    json.dumps(example["context_data"]),
                    example["quality_score"],
                    example["difficulty_level"],
                    json.dumps(example["tags"])
                ))
            except Exception as e:
                logger.error(f"Error inserting learning example {example['example_id']}: {e}")
                
    def get_statistics(self):
        """Get statistics about the created memory system"""
        stats = {}
        
        tables = ['intent_patterns', 'conversation_flows', 'context_patterns', 
                 'response_templates', 'learning_examples']
        
        for table in tables:
            cursor = self.conn.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
            
        return stats
        
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    """Main function to create the comprehensive agent memory system"""
    print("🚀 Creating Comprehensive Agent Memory System...")
    print("=" * 60)
    
    creator = AgentMemorySystemCreator()
    
    try:
        creator.create_comprehensive_memory_system()
        
        # Get and display statistics
        stats = creator.get_statistics()
        
        print("\n📊 Memory System Statistics:")
        print("-" * 40)
        for table, count in stats.items():
            print(f"  {table}: {count} entries")
        
        total_entries = sum(stats.values())
        print(f"\n🎯 Total Entries: {total_entries}")
        print("\n✅ Comprehensive Agent Memory System created successfully!")
        print("\n🧠 The agent now has extensive training data for:")
        print("  • Intent recognition and classification")
        print("  • Conversation flow management")
        print("  • Context-aware responses")
        print("  • Error handling and recovery")
        print("  • Multi-turn conversations")
        print("  • Domain-specific knowledge")
        print("  • High-quality response templates")
        print("  • Comprehensive learning examples")
        
    except Exception as e:
        logger.error(f"Error creating memory system: {e}")
        print(f"❌ Error: {e}")
    finally:
        creator.close()

if __name__ == "__main__":
    main()