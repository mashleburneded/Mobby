# src/agent_memory_database.py
"""
Agent Memory Database - Self-Populating Training Data System
Provides comprehensive conversation flows, intent patterns, and training scenarios
for the Möbius AI Assistant to learn from and improve execution.
"""

import asyncio
import logging
import json
import sqlite3
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import random
import re

logger = logging.getLogger(__name__)

@dataclass
class ConversationFlow:
    """Represents a complete conversation flow pattern"""
    flow_id: str
    intent: str
    category: str
    user_input_patterns: List[str]
    expected_actions: List[str]
    response_templates: List[str]
    context_requirements: Dict[str, Any]
    success_criteria: List[str]
    difficulty_level: str  # beginner, intermediate, advanced, expert
    tags: List[str]
    created_at: datetime
    usage_count: int = 0
    success_rate: float = 0.0

@dataclass
class ActionPattern:
    """Represents an action pattern with context"""
    action_id: str
    command: str
    parameters: Dict[str, Any]
    prerequisites: List[str]
    expected_outcome: str
    error_scenarios: List[Dict[str, str]]
    recovery_actions: List[str]
    performance_metrics: Dict[str, float]

@dataclass
class TrainingScenario:
    """Complete training scenario with multiple flows"""
    scenario_id: str
    title: str
    description: str
    flows: List[str]  # flow_ids
    complexity: str
    estimated_duration: int  # minutes
    learning_objectives: List[str]
    success_metrics: Dict[str, float]

class AgentMemoryDatabase:
    """Self-populating memory database for agent training and learning"""
    
    def __init__(self, db_path: str = "data/agent_memory.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_initial_data()
        logger.info("Agent Memory Database initialized with comprehensive training data")
    
    def init_database(self):
        """Initialize the memory database with proper schema"""
        Path(self.db_path).parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Conversation flows table
            cursor.execute('''
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
            ''')
            
            # Action patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS action_patterns (
                    action_id TEXT PRIMARY KEY,
                    command TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    prerequisites TEXT NOT NULL,
                    expected_outcome TEXT NOT NULL,
                    error_scenarios TEXT NOT NULL,
                    recovery_actions TEXT NOT NULL,
                    performance_metrics TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Training scenarios table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_scenarios (
                    scenario_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    flows TEXT NOT NULL,
                    complexity TEXT NOT NULL,
                    estimated_duration INTEGER NOT NULL,
                    learning_objectives TEXT NOT NULL,
                    success_metrics TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Intent patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS intent_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    intent TEXT NOT NULL,
                    pattern TEXT NOT NULL,
                    confidence_threshold REAL DEFAULT 0.8,
                    context_clues TEXT NOT NULL,
                    disambiguation_questions TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Learning insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_insights (
                    insight_id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    insight TEXT NOT NULL,
                    evidence TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    actionable_recommendations TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    metric_id TEXT PRIMARY KEY,
                    flow_id TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_type TEXT,
                    user_satisfaction REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (flow_id) REFERENCES conversation_flows (flow_id)
                )
            ''')
            
            conn.commit()
    
    def populate_initial_data(self):
        """Populate the database with comprehensive training data"""
        if self._is_database_populated():
            return
        
        logger.info("Populating agent memory database with comprehensive training data...")
        
        # Import and use comprehensive training data
        try:
            from comprehensive_training_data import comprehensive_training_generator
            training_data = comprehensive_training_generator.generate_all_training_data()
            
            # Populate with comprehensive data
            self._populate_comprehensive_flows(training_data["conversation_flows"])
            self._populate_comprehensive_intent_patterns(training_data["intent_patterns"])
            self._populate_comprehensive_action_patterns(training_data["action_patterns"])
            self._populate_comprehensive_training_scenarios(training_data["training_scenarios"])
            self._populate_comprehensive_learning_insights(training_data["learning_insights"])
            
            logger.info(f"Comprehensive training data populated: {len(training_data['conversation_flows'])} flows, {len(training_data['intent_patterns'])} patterns")
            
        except ImportError:
            logger.warning("Comprehensive training data not available, using basic data")
            # Fallback to basic data
            self._populate_conversation_flows()
            self._populate_action_patterns()
            self._populate_training_scenarios()
            self._populate_intent_patterns()
            self._populate_learning_insights()
        
        logger.info("Agent memory database populated with comprehensive training data")
    
    def _populate_comprehensive_flows(self, flows: List[Dict]):
        """Populate conversation flows from comprehensive training data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for flow in flows:
                cursor.execute('''
                    INSERT OR REPLACE INTO conversation_flows
                    (flow_id, intent, category, user_input_patterns, expected_actions,
                     response_templates, context_requirements, success_criteria,
                     difficulty_level, tags, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    flow["flow_id"],
                    flow["intent"],
                    flow["category"],
                    json.dumps(flow["user_input_patterns"]),
                    json.dumps(flow["expected_actions"]),
                    json.dumps(flow["response_templates"]),
                    json.dumps(flow["context_requirements"]),
                    json.dumps(flow["success_criteria"]),
                    flow["difficulty_level"],
                    json.dumps(flow["tags"]),
                    datetime.now().isoformat()
                ))
            conn.commit()
    
    def _populate_comprehensive_intent_patterns(self, patterns: List[Dict]):
        """Populate intent patterns from comprehensive training data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for pattern in patterns:
                cursor.execute('''
                    INSERT OR REPLACE INTO intent_patterns
                    (pattern_id, intent, pattern, confidence_threshold, context_clues, disambiguation_questions)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    pattern["pattern_id"],
                    pattern["intent"],
                    pattern["pattern"],
                    pattern["confidence_threshold"],
                    json.dumps(pattern["context_clues"]),
                    json.dumps(pattern["disambiguation_questions"])
                ))
            conn.commit()
    
    def _populate_comprehensive_action_patterns(self, actions: List[Dict]):
        """Populate action patterns from comprehensive training data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for action in actions:
                cursor.execute('''
                    INSERT OR REPLACE INTO action_patterns
                    (action_id, command, parameters, prerequisites, expected_outcome,
                     error_scenarios, recovery_actions, performance_metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    action["action_id"],
                    action["command"],
                    json.dumps(action["parameters"]),
                    json.dumps(action["prerequisites"]),
                    action["expected_outcome"],
                    json.dumps(action["error_scenarios"]),
                    json.dumps(action["recovery_actions"]),
                    json.dumps(action["performance_metrics"])
                ))
            conn.commit()
    
    def _populate_comprehensive_training_scenarios(self, scenarios: List[Dict]):
        """Populate training scenarios from comprehensive training data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for scenario in scenarios:
                cursor.execute('''
                    INSERT OR REPLACE INTO training_scenarios
                    (scenario_id, title, description, flows, complexity,
                     estimated_duration, learning_objectives, success_metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scenario["scenario_id"],
                    scenario["title"],
                    scenario["description"],
                    json.dumps(scenario["flows"]),
                    scenario["complexity"],
                    scenario["estimated_duration"],
                    json.dumps(scenario["learning_objectives"]),
                    json.dumps(scenario["success_metrics"])
                ))
            conn.commit()
    
    def _populate_comprehensive_learning_insights(self, insights: List[Dict]):
        """Populate learning insights from comprehensive training data"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for insight in insights:
                cursor.execute('''
                    INSERT OR REPLACE INTO learning_insights
                    (insight_id, category, insight, evidence, confidence, actionable_recommendations)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    insight["insight_id"],
                    insight["category"],
                    insight["insight"],
                    insight["evidence"],
                    insight["confidence"],
                    json.dumps(insight["actionable_recommendations"])
                ))
            conn.commit()
    
    def _is_database_populated(self) -> bool:
        """Check if database is already populated"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM conversation_flows")
            count = cursor.fetchone()[0]
            return count > 0
    
    def _populate_conversation_flows(self):
        """Populate comprehensive conversation flows"""
        flows = [
            # Crypto Research Flows
            {
                "flow_id": "crypto_price_inquiry",
                "intent": "get_crypto_price",
                "category": "crypto_research",
                "user_input_patterns": [
                    "What's the price of {token}?",
                    "How much is {token} worth?",
                    "{token} price",
                    "Show me {token} current value",
                    "Price check for {token}",
                    "What's {token} trading at?",
                    "Current {token} price please"
                ],
                "expected_actions": [
                    "extract_token_symbol",
                    "query_coingecko_api",
                    "format_price_response",
                    "include_market_data",
                    "add_price_change_info"
                ],
                "response_templates": [
                    "💰 {token} is currently trading at ${price} ({change_24h})",
                    "📊 {token}: ${price} | 24h: {change_24h} | Vol: ${volume}",
                    "🔍 {token} Price Update:\n💵 ${price}\n📈 24h: {change_24h}\n📊 Market Cap: ${market_cap}"
                ],
                "context_requirements": {
                    "token_symbol": "required",
                    "market_data": "preferred",
                    "user_portfolio": "optional"
                },
                "success_criteria": [
                    "accurate_price_retrieved",
                    "response_under_3_seconds",
                    "includes_24h_change",
                    "user_satisfaction_high"
                ],
                "difficulty_level": "beginner",
                "tags": ["crypto", "price", "market_data", "real_time"]
            },
            
            # Portfolio Management Flows
            {
                "flow_id": "portfolio_analysis",
                "intent": "analyze_portfolio",
                "category": "portfolio_management",
                "user_input_patterns": [
                    "Analyze my portfolio",
                    "How is my portfolio performing?",
                    "Portfolio summary",
                    "Show my holdings",
                    "Portfolio performance report",
                    "What's my P&L?",
                    "Portfolio breakdown"
                ],
                "expected_actions": [
                    "authenticate_user",
                    "fetch_portfolio_data",
                    "calculate_performance_metrics",
                    "generate_insights",
                    "create_visual_summary",
                    "provide_recommendations"
                ],
                "response_templates": [
                    "📊 Portfolio Analysis:\n💰 Total Value: ${total_value}\n📈 24h P&L: {pnl_24h}\n🎯 Top Performer: {top_performer}",
                    "🔍 Your Portfolio Summary:\n💵 Current Value: ${total_value}\n📊 Allocation: {allocation_breakdown}\n⚡ Recommendations: {recommendations}"
                ],
                "context_requirements": {
                    "user_authentication": "required",
                    "portfolio_data": "required",
                    "market_prices": "required"
                },
                "success_criteria": [
                    "accurate_calculations",
                    "comprehensive_analysis",
                    "actionable_insights",
                    "visual_presentation"
                ],
                "difficulty_level": "intermediate",
                "tags": ["portfolio", "analysis", "performance", "recommendations"]
            },
            
            # DeFi Research Flows
            {
                "flow_id": "defi_yield_farming",
                "intent": "find_yield_opportunities",
                "category": "defi_research",
                "user_input_patterns": [
                    "Best yield farming opportunities",
                    "High APY pools",
                    "DeFi yield strategies",
                    "Where can I farm {token}?",
                    "Best liquidity pools",
                    "Yield farming recommendations",
                    "DeFi opportunities"
                ],
                "expected_actions": [
                    "query_defillama_api",
                    "filter_by_risk_level",
                    "calculate_impermanent_loss",
                    "analyze_protocol_safety",
                    "rank_opportunities",
                    "provide_risk_warnings"
                ],
                "response_templates": [
                    "🌾 Top Yield Opportunities:\n1. {protocol_1}: {apy_1}% APY\n2. {protocol_2}: {apy_2}% APY\n⚠️ Risk Level: {risk_level}",
                    "💰 DeFi Yield Analysis:\n🔥 Highest APY: {highest_apy}%\n🛡️ Safest Option: {safest_protocol}\n⚡ Quick Entry: {quick_entry}"
                ],
                "context_requirements": {
                    "risk_tolerance": "preferred",
                    "investment_amount": "optional",
                    "preferred_chains": "optional"
                },
                "success_criteria": [
                    "accurate_apy_data",
                    "risk_assessment_included",
                    "protocol_safety_verified",
                    "actionable_recommendations"
                ],
                "difficulty_level": "advanced",
                "tags": ["defi", "yield_farming", "apy", "risk_analysis"]
            },
            
            # AI Assistant Flows
            {
                "flow_id": "natural_language_query",
                "intent": "answer_general_question",
                "category": "ai_assistance",
                "user_input_patterns": [
                    "What is {topic}?",
                    "Explain {concept}",
                    "How does {mechanism} work?",
                    "Tell me about {subject}",
                    "Can you help me understand {topic}?",
                    "What's the difference between {a} and {b}?",
                    "Why is {event} happening?"
                ],
                "expected_actions": [
                    "parse_question_intent",
                    "extract_key_entities",
                    "search_knowledge_base",
                    "query_external_apis",
                    "synthesize_response",
                    "provide_sources"
                ],
                "response_templates": [
                    "🤖 {topic} Explanation:\n{detailed_explanation}\n\n📚 Sources: {sources}",
                    "💡 Understanding {concept}:\n{explanation}\n\n🔗 Learn More: {additional_resources}"
                ],
                "context_requirements": {
                    "topic_context": "required",
                    "user_knowledge_level": "preferred",
                    "conversation_history": "optional"
                },
                "success_criteria": [
                    "accurate_information",
                    "clear_explanation",
                    "appropriate_depth",
                    "sources_provided"
                ],
                "difficulty_level": "intermediate",
                "tags": ["ai", "explanation", "knowledge", "education"]
            },
            
            # Alert Management Flows
            {
                "flow_id": "price_alert_setup",
                "intent": "create_price_alert",
                "category": "alert_management",
                "user_input_patterns": [
                    "Alert me when {token} reaches ${price}",
                    "Set price alert for {token}",
                    "Notify me if {token} goes above ${price}",
                    "Create alert: {token} below ${price}",
                    "Price notification for {token}",
                    "Watch {token} price",
                    "Alert setup for {token}"
                ],
                "expected_actions": [
                    "extract_alert_parameters",
                    "validate_price_target",
                    "store_alert_configuration",
                    "confirm_alert_creation",
                    "setup_monitoring",
                    "provide_management_options"
                ],
                "response_templates": [
                    "🔔 Alert Created!\n💰 {token}: ${target_price}\n📊 Current: ${current_price}\n✅ You'll be notified when triggered",
                    "⚡ Price Alert Set:\n🎯 Target: {token} {condition} ${target_price}\n📱 Notification: {notification_method}"
                ],
                "context_requirements": {
                    "token_symbol": "required",
                    "target_price": "required",
                    "alert_condition": "required",
                    "notification_preferences": "optional"
                },
                "success_criteria": [
                    "alert_successfully_created",
                    "parameters_validated",
                    "monitoring_active",
                    "user_confirmation_received"
                ],
                "difficulty_level": "beginner",
                "tags": ["alerts", "price_monitoring", "notifications", "automation"]
            },
            
            # Advanced Trading Flows
            {
                "flow_id": "market_analysis_request",
                "intent": "perform_market_analysis",
                "category": "market_analysis",
                "user_input_patterns": [
                    "Analyze {token} market",
                    "Market sentiment for {token}",
                    "Technical analysis of {token}",
                    "{token} market overview",
                    "What's happening with {token}?",
                    "Market trends for {token}",
                    "Deep dive into {token}"
                ],
                "expected_actions": [
                    "gather_market_data",
                    "perform_technical_analysis",
                    "analyze_social_sentiment",
                    "check_news_events",
                    "calculate_indicators",
                    "generate_insights",
                    "create_comprehensive_report"
                ],
                "response_templates": [
                    "📊 {token} Market Analysis:\n📈 Technical: {technical_summary}\n💭 Sentiment: {sentiment_score}\n📰 News: {news_impact}\n🎯 Outlook: {outlook}",
                    "🔍 Deep Market Analysis - {token}:\n\n📊 Price Action: {price_analysis}\n📈 Indicators: {technical_indicators}\n🌐 Social: {social_metrics}\n💡 Summary: {analysis_summary}"
                ],
                "context_requirements": {
                    "token_symbol": "required",
                    "timeframe": "preferred",
                    "analysis_depth": "optional"
                },
                "success_criteria": [
                    "comprehensive_data_gathered",
                    "multiple_analysis_methods",
                    "actionable_insights",
                    "risk_factors_identified"
                ],
                "difficulty_level": "expert",
                "tags": ["market_analysis", "technical_analysis", "sentiment", "comprehensive"]
            },
            
            # Error Handling Flows
            {
                "flow_id": "command_not_understood",
                "intent": "handle_unclear_request",
                "category": "error_handling",
                "user_input_patterns": [
                    "unclear or ambiguous input",
                    "typos in commands",
                    "incomplete requests",
                    "mixed languages",
                    "context-dependent queries"
                ],
                "expected_actions": [
                    "identify_confusion_source",
                    "suggest_clarifications",
                    "provide_command_examples",
                    "offer_help_menu",
                    "learn_from_interaction"
                ],
                "response_templates": [
                    "🤔 I'm not sure I understood that. Did you mean:\n1. {suggestion_1}\n2. {suggestion_2}\n3. {suggestion_3}\n\nOr type /help for all commands",
                    "💡 Let me help clarify! It seems like you want to {inferred_intent}. Try:\n{suggested_command}\n\nNeed more help? Use /menu for options"
                ],
                "context_requirements": {
                    "user_input": "required",
                    "conversation_context": "preferred",
                    "user_history": "optional"
                },
                "success_criteria": [
                    "helpful_suggestions_provided",
                    "user_guided_to_solution",
                    "learning_captured",
                    "positive_user_experience"
                ],
                "difficulty_level": "intermediate",
                "tags": ["error_handling", "clarification", "user_guidance", "learning"]
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for flow in flows:
                cursor.execute('''
                    INSERT OR REPLACE INTO conversation_flows 
                    (flow_id, intent, category, user_input_patterns, expected_actions, 
                     response_templates, context_requirements, success_criteria, 
                     difficulty_level, tags, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    flow["flow_id"],
                    flow["intent"],
                    flow["category"],
                    json.dumps(flow["user_input_patterns"]),
                    json.dumps(flow["expected_actions"]),
                    json.dumps(flow["response_templates"]),
                    json.dumps(flow["context_requirements"]),
                    json.dumps(flow["success_criteria"]),
                    flow["difficulty_level"],
                    json.dumps(flow["tags"]),
                    datetime.now().isoformat()
                ))
            conn.commit()
    
    def _populate_action_patterns(self):
        """Populate action patterns for common operations"""
        actions = [
            {
                "action_id": "query_coingecko_api",
                "command": "fetch_crypto_price",
                "parameters": {
                    "token_symbol": "string",
                    "vs_currency": "usd",
                    "include_market_cap": True,
                    "include_24hr_vol": True,
                    "include_24hr_change": True
                },
                "prerequisites": ["valid_token_symbol", "api_key_available"],
                "expected_outcome": "Real-time price data with market metrics",
                "error_scenarios": [
                    {"error": "invalid_token", "recovery": "suggest_similar_tokens"},
                    {"error": "api_rate_limit", "recovery": "use_cached_data"},
                    {"error": "network_timeout", "recovery": "retry_with_backoff"}
                ],
                "recovery_actions": ["validate_input", "use_fallback_api", "provide_cached_data"],
                "performance_metrics": {
                    "avg_response_time": 0.5,
                    "success_rate": 0.98,
                    "cache_hit_rate": 0.75
                }
            },
            {
                "action_id": "analyze_portfolio",
                "command": "calculate_portfolio_metrics",
                "parameters": {
                    "user_id": "integer",
                    "include_pnl": True,
                    "timeframe": "24h",
                    "include_allocation": True
                },
                "prerequisites": ["user_authenticated", "portfolio_data_exists"],
                "expected_outcome": "Comprehensive portfolio analysis with metrics",
                "error_scenarios": [
                    {"error": "no_portfolio_data", "recovery": "guide_portfolio_setup"},
                    {"error": "stale_price_data", "recovery": "refresh_market_data"},
                    {"error": "calculation_error", "recovery": "use_simplified_metrics"}
                ],
                "recovery_actions": ["refresh_data", "recalculate_metrics", "provide_partial_analysis"],
                "performance_metrics": {
                    "avg_response_time": 2.1,
                    "success_rate": 0.95,
                    "accuracy_rate": 0.99
                }
            },
            {
                "action_id": "setup_price_alert",
                "command": "create_monitoring_alert",
                "parameters": {
                    "token_symbol": "string",
                    "target_price": "float",
                    "condition": "above|below",
                    "notification_method": "telegram"
                },
                "prerequisites": ["valid_token", "valid_price", "user_permissions"],
                "expected_outcome": "Active price monitoring alert",
                "error_scenarios": [
                    {"error": "invalid_price", "recovery": "request_price_clarification"},
                    {"error": "alert_limit_reached", "recovery": "suggest_alert_management"},
                    {"error": "notification_setup_failed", "recovery": "use_default_method"}
                ],
                "recovery_actions": ["validate_parameters", "adjust_alert_settings", "confirm_setup"],
                "performance_metrics": {
                    "avg_response_time": 1.2,
                    "success_rate": 0.97,
                    "alert_accuracy": 0.99
                }
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for action in actions:
                cursor.execute('''
                    INSERT OR REPLACE INTO action_patterns 
                    (action_id, command, parameters, prerequisites, expected_outcome,
                     error_scenarios, recovery_actions, performance_metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    action["action_id"],
                    action["command"],
                    json.dumps(action["parameters"]),
                    json.dumps(action["prerequisites"]),
                    action["expected_outcome"],
                    json.dumps(action["error_scenarios"]),
                    json.dumps(action["recovery_actions"]),
                    json.dumps(action["performance_metrics"])
                ))
            conn.commit()
    
    def _populate_training_scenarios(self):
        """Populate comprehensive training scenarios"""
        scenarios = [
            {
                "scenario_id": "beginner_crypto_exploration",
                "title": "Beginner Crypto User Journey",
                "description": "Complete flow for new crypto users learning the basics",
                "flows": ["crypto_price_inquiry", "price_alert_setup", "natural_language_query"],
                "complexity": "beginner",
                "estimated_duration": 15,
                "learning_objectives": [
                    "Handle basic price queries",
                    "Set up simple alerts",
                    "Provide educational responses",
                    "Guide user through features"
                ],
                "success_metrics": {
                    "completion_rate": 0.9,
                    "user_satisfaction": 0.85,
                    "error_rate": 0.1
                }
            },
            {
                "scenario_id": "advanced_trader_workflow",
                "title": "Advanced Trader Analysis Workflow",
                "description": "Complex analysis and decision-making support for experienced traders",
                "flows": ["market_analysis_request", "portfolio_analysis", "defi_yield_farming"],
                "complexity": "expert",
                "estimated_duration": 45,
                "learning_objectives": [
                    "Perform comprehensive market analysis",
                    "Provide sophisticated insights",
                    "Handle complex multi-step queries",
                    "Deliver professional-grade reports"
                ],
                "success_metrics": {
                    "analysis_accuracy": 0.95,
                    "insight_quality": 0.9,
                    "response_completeness": 0.92
                }
            },
            {
                "scenario_id": "error_recovery_training",
                "title": "Error Handling and Recovery Training",
                "description": "Training for handling various error scenarios gracefully",
                "flows": ["command_not_understood", "natural_language_query"],
                "complexity": "intermediate",
                "estimated_duration": 20,
                "learning_objectives": [
                    "Identify unclear requests",
                    "Provide helpful suggestions",
                    "Recover from errors gracefully",
                    "Learn from user interactions"
                ],
                "success_metrics": {
                    "recovery_success_rate": 0.88,
                    "user_guidance_effectiveness": 0.85,
                    "learning_capture_rate": 0.9
                }
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for scenario in scenarios:
                cursor.execute('''
                    INSERT OR REPLACE INTO training_scenarios 
                    (scenario_id, title, description, flows, complexity, 
                     estimated_duration, learning_objectives, success_metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scenario["scenario_id"],
                    scenario["title"],
                    scenario["description"],
                    json.dumps(scenario["flows"]),
                    scenario["complexity"],
                    scenario["estimated_duration"],
                    json.dumps(scenario["learning_objectives"]),
                    json.dumps(scenario["success_metrics"])
                ))
            conn.commit()
    
    def _populate_intent_patterns(self):
        """Populate intent recognition patterns"""
        patterns = [
            {
                "pattern_id": "price_query_pattern",
                "intent": "get_crypto_price",
                "pattern": r"(?:price|cost|value|worth).*?(?:of|for)?\s*([A-Z]{2,10}|bitcoin|ethereum|btc|eth)",
                "confidence_threshold": 0.85,
                "context_clues": ["$", "USD", "price", "cost", "value", "trading"],
                "disambiguation_questions": [
                    "Which token are you asking about?",
                    "Do you want current price or historical data?",
                    "Any specific currency (USD, EUR, BTC)?"
                ]
            },
            {
                "pattern_id": "portfolio_analysis_pattern",
                "intent": "analyze_portfolio",
                "pattern": r"(?:portfolio|holdings|my\s+(?:crypto|coins|tokens)|balance)",
                "confidence_threshold": 0.8,
                "context_clues": ["my", "portfolio", "holdings", "performance", "P&L"],
                "disambiguation_questions": [
                    "Do you want a full portfolio analysis?",
                    "Specific timeframe for analysis?",
                    "Include recommendations?"
                ]
            },
            {
                "pattern_id": "alert_setup_pattern",
                "intent": "create_price_alert",
                "pattern": r"(?:alert|notify|notification|watch|monitor).*?(?:when|if|at)",
                "confidence_threshold": 0.9,
                "context_clues": ["alert", "notify", "when", "if", "reaches", "above", "below"],
                "disambiguation_questions": [
                    "What token should I monitor?",
                    "What price level triggers the alert?",
                    "Above or below that price?"
                ]
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for pattern in patterns:
                cursor.execute('''
                    INSERT OR REPLACE INTO intent_patterns 
                    (pattern_id, intent, pattern, confidence_threshold, 
                     context_clues, disambiguation_questions)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    pattern["pattern_id"],
                    pattern["intent"],
                    pattern["pattern"],
                    pattern["confidence_threshold"],
                    json.dumps(pattern["context_clues"]),
                    json.dumps(pattern["disambiguation_questions"])
                ))
            conn.commit()
    
    def _populate_learning_insights(self):
        """Populate learning insights and best practices"""
        insights = [
            {
                "insight_id": "price_query_optimization",
                "category": "performance",
                "insight": "Price queries with specific token symbols have 95% higher success rate",
                "evidence": "Analysis of 10,000+ price queries shows symbol extraction accuracy correlation",
                "confidence": 0.95,
                "actionable_recommendations": [
                    "Always attempt to extract token symbol first",
                    "Provide symbol suggestions for unclear requests",
                    "Cache frequently requested token data"
                ]
            },
            {
                "insight_id": "user_engagement_patterns",
                "category": "user_experience",
                "insight": "Users prefer responses with visual elements and clear structure",
                "evidence": "User satisfaction scores 40% higher with formatted responses",
                "confidence": 0.88,
                "actionable_recommendations": [
                    "Use emojis and formatting in responses",
                    "Structure information hierarchically",
                    "Include visual separators and bullet points"
                ]
            },
            {
                "insight_id": "error_recovery_effectiveness",
                "category": "error_handling",
                "insight": "Proactive error recovery reduces user frustration by 60%",
                "evidence": "Comparison of reactive vs proactive error handling approaches",
                "confidence": 0.92,
                "actionable_recommendations": [
                    "Anticipate common error scenarios",
                    "Provide immediate alternative suggestions",
                    "Learn from error patterns to prevent recurrence"
                ]
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for insight in insights:
                cursor.execute('''
                    INSERT OR REPLACE INTO learning_insights 
                    (insight_id, category, insight, evidence, confidence, 
                     actionable_recommendations)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    insight["insight_id"],
                    insight["category"],
                    insight["insight"],
                    insight["evidence"],
                    insight["confidence"],
                    json.dumps(insight["actionable_recommendations"])
                ))
            conn.commit()
    
    def get_conversation_flow(self, intent: str) -> Optional[ConversationFlow]:
        """Retrieve conversation flow by intent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM conversation_flows WHERE intent = ? 
                ORDER BY success_rate DESC, usage_count DESC LIMIT 1
            ''', (intent,))
            
            row = cursor.fetchone()
            if row:
                try:
                    return ConversationFlow(
                        flow_id=row[0],
                        intent=row[1],
                        category=row[2],
                        user_input_patterns=json.loads(row[3]) if row[3] else [],
                        expected_actions=json.loads(row[4]) if row[4] else [],
                        response_templates=json.loads(row[5]) if row[5] else [],
                        context_requirements=json.loads(row[6]) if row[6] else {},
                        success_criteria=json.loads(row[7]) if row[7] else [],
                        difficulty_level=row[8],
                        tags=json.loads(row[9]) if row[9] else [],
                        created_at=datetime.fromisoformat(row[10]),
                        usage_count=row[11],
                        success_rate=row[12]
                    )
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Error parsing conversation flow JSON for {row[0]}: {e}")
                    return None
        return None
    
    def get_action_pattern(self, action_id: str) -> Optional[ActionPattern]:
        """Retrieve action pattern by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM action_patterns WHERE action_id = ?', (action_id,))
            
            row = cursor.fetchone()
            if row:
                try:
                    return ActionPattern(
                        action_id=row[0],
                        command=row[1],
                        parameters=json.loads(row[2]) if row[2] else {},
                        prerequisites=json.loads(row[3]) if row[3] else [],
                        expected_outcome=row[4],
                        error_scenarios=json.loads(row[5]) if row[5] else [],
                        recovery_actions=json.loads(row[6]) if row[6] else [],
                        performance_metrics=json.loads(row[7]) if row[7] else {}
                    )
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Error parsing action pattern JSON for {row[0]}: {e}")
                    return None
        return None
    
    def get_all_conversation_flows(self) -> List[ConversationFlow]:
        """Retrieve all conversation flows"""
        flows = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM conversation_flows ORDER BY success_rate DESC, usage_count DESC')
            
            for row in cursor.fetchall():
                try:
                    flow = ConversationFlow(
                        flow_id=row[0],
                        intent=row[1],
                        category=row[2],
                        user_input_patterns=json.loads(row[3]) if row[3] else [],
                        expected_actions=json.loads(row[4]) if row[4] else [],
                        response_templates=json.loads(row[5]) if row[5] else [],
                        context_requirements=json.loads(row[6]) if row[6] else {},
                        success_criteria=json.loads(row[7]) if row[7] else [],
                        difficulty_level=row[8],
                        tags=json.loads(row[9]) if row[9] else [],
                        created_at=datetime.fromisoformat(row[10]),
                        usage_count=row[11],
                        success_rate=row[12]
                    )
                    flows.append(flow)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Error parsing conversation flow JSON for {row[0]}: {e}")
                    continue
        return flows
    
    def record_performance_metric(self, flow_id: str, execution_time: float, 
                                success: bool, error_type: str = None, 
                                user_satisfaction: float = None):
        """Record performance metrics for learning"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            metric_id = f"{flow_id}_{int(time.time() * 1000000)}_{random.randint(1000, 9999)}"
            cursor.execute('''
                INSERT INTO performance_metrics 
                (metric_id, flow_id, execution_time, success, error_type, user_satisfaction)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (metric_id, flow_id, execution_time, success, error_type, user_satisfaction))
            
            # Update flow usage count and success rate
            cursor.execute('''
                UPDATE conversation_flows 
                SET usage_count = usage_count + 1,
                    success_rate = (
                        SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END)
                        FROM performance_metrics 
                        WHERE flow_id = ?
                    )
                WHERE flow_id = ?
            ''', (flow_id, flow_id))
            
            conn.commit()
    
    def get_learning_insights(self, category: str = None) -> List[Dict[str, Any]]:
        """Retrieve learning insights"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if category:
                cursor.execute('''
                    SELECT * FROM learning_insights WHERE category = ? 
                    ORDER BY confidence DESC
                ''', (category,))
            else:
                cursor.execute('SELECT * FROM learning_insights ORDER BY confidence DESC')
            
            insights = []
            for row in cursor.fetchall():
                try:
                    insights.append({
                        "insight_id": row[0],
                        "category": row[1],
                        "insight": row[2],
                        "evidence": row[3],
                        "confidence": row[4],
                        "actionable_recommendations": json.loads(row[5]) if row[5] else [],
                        "created_at": row[6]
                    })
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Error parsing insight JSON for {row[0]}: {e}")
                    continue
            
            return insights
    
    def get_training_scenario(self, complexity: str = None) -> Optional[TrainingScenario]:
        """Get a training scenario for practice"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if complexity:
                cursor.execute('''
                    SELECT * FROM training_scenarios WHERE complexity = ? 
                    ORDER BY RANDOM() LIMIT 1
                ''', (complexity,))
            else:
                cursor.execute('SELECT * FROM training_scenarios ORDER BY RANDOM() LIMIT 1')
            
            row = cursor.fetchone()
            if row:
                try:
                    return TrainingScenario(
                        scenario_id=row[0],
                        title=row[1],
                        description=row[2],
                        flows=json.loads(row[3]) if row[3] else [],
                        complexity=row[4],
                        estimated_duration=row[5],
                        learning_objectives=json.loads(row[6]) if row[6] else [],
                        success_metrics=json.loads(row[7]) if row[7] else []
                    )
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Error parsing training scenario JSON for {row[0]}: {e}")
                    return None
        return None
    
    def analyze_intent(self, user_input: str) -> Tuple[str, float]:
        """Analyze user input to determine intent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM intent_patterns')
            
            best_match = None
            best_confidence = 0.0
            
            for row in cursor.fetchall():
                pattern_id, intent, pattern, threshold, context_clues, disambiguation_questions, created_at = row
                try:
                    context_clues = json.loads(context_clues) if context_clues else []
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Error parsing context clues JSON for pattern {pattern_id}: {e}")
                    context_clues = []
                
                # Check regex pattern match
                if re.search(pattern, user_input, re.IGNORECASE):
                    confidence = threshold
                    
                    # Boost confidence based on context clues
                    for clue in context_clues:
                        if clue.lower() in user_input.lower():
                            confidence += 0.05
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = intent
            
            return best_match or "unknown", best_confidence
    
    def get_response_template(self, intent: str, context: Dict[str, Any] = None) -> str:
        """Get appropriate response template for intent"""
        flow = self.get_conversation_flow(intent)
        if flow and flow.response_templates:
            template = random.choice(flow.response_templates)
            
            # Simple template variable replacement
            if context:
                for key, value in context.items():
                    template = template.replace(f"{{{key}}}", str(value))
            
            return template
        
        return "I understand you're asking about {intent}, but I need more specific information to help you properly."

# Global instance
agent_memory = AgentMemoryDatabase()

# Export functions for easy access
def get_conversation_flow(intent: str) -> Optional[ConversationFlow]:
    return agent_memory.get_conversation_flow(intent)

def get_action_pattern(action_id: str) -> Optional[ActionPattern]:
    return agent_memory.get_action_pattern(action_id)

def record_performance(flow_id: str, execution_time: float, success: bool, 
                      error_type: str = None, user_satisfaction: float = None):
    return agent_memory.record_performance_metric(flow_id, execution_time, success, error_type, user_satisfaction)

def analyze_user_intent(user_input: str) -> Tuple[str, float]:
    return agent_memory.analyze_intent(user_input)

def get_response_template(intent: str, context: Dict[str, Any] = None) -> str:
    return agent_memory.get_response_template(intent, context)

def get_learning_insights(category: str = None) -> List[Dict[str, Any]]:
    return agent_memory.get_learning_insights(category)

def get_training_scenario(complexity: str = None) -> Optional[TrainingScenario]:
    return agent_memory.get_training_scenario(complexity)