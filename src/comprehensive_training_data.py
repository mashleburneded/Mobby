# src/comprehensive_training_data.py
"""
Comprehensive Training Data Generator for Möbius AI Assistant
Creates extensive conversation flows, intent patterns, and training scenarios
to enable the agent to understand and execute any possible user request.
"""

import json
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ComprehensiveTrainingDataGenerator:
    """Generates comprehensive training data for all possible scenarios"""
    
    def __init__(self):
        self.conversation_flows = []
        self.intent_patterns = []
        self.action_patterns = []
        self.training_scenarios = []
        self.learning_insights = []
        
    def generate_all_training_data(self) -> Dict[str, List[Dict]]:
        """Generate comprehensive training data covering all scenarios"""
        
        # Generate conversation flows for all categories
        self._generate_crypto_flows()
        self._generate_defi_flows()
        self._generate_trading_flows()
        self._generate_portfolio_flows()
        self._generate_security_flows()
        self._generate_educational_flows()
        self._generate_technical_analysis_flows()
        self._generate_news_flows()
        self._generate_social_flows()
        self._generate_error_recovery_flows()
        self._generate_conversation_management_flows()
        self._generate_advanced_flows()
        
        # Generate intent patterns
        self._generate_intent_patterns()
        
        # Generate action patterns
        self._generate_action_patterns()
        
        # Generate training scenarios
        self._generate_training_scenarios()
        
        # Generate learning insights
        self._generate_learning_insights()
        
        return {
            "conversation_flows": self.conversation_flows,
            "intent_patterns": self.intent_patterns,
            "action_patterns": self.action_patterns,
            "training_scenarios": self.training_scenarios,
            "learning_insights": self.learning_insights
        }
    
    def _generate_crypto_flows(self):
        """Generate comprehensive cryptocurrency-related flows"""
        
        # Price inquiry flows
        self.conversation_flows.extend([
            {
                "flow_id": "crypto_price_realtime",
                "intent": "get_realtime_price",
                "category": "crypto_research",
                "user_input_patterns": [
                    "What's the current price of {token}?",
                    "How much is {token} worth right now?",
                    "{token} price live",
                    "Show me {token} current value",
                    "Real-time {token} price",
                    "What's {token} trading at?",
                    "Current {token} price please",
                    "Price of {token} today",
                    "{token} USD price",
                    "How much for 1 {token}?"
                ],
                "expected_actions": [
                    "extract_token_symbol",
                    "validate_token_exists",
                    "query_coingecko_api",
                    "query_coinmarketcap_api",
                    "format_price_response",
                    "include_market_data",
                    "add_price_change_info",
                    "add_volume_data",
                    "include_market_cap"
                ],
                "response_templates": [
                    "💰 {token} is currently trading at ${price} ({change_24h})",
                    "📊 {token}: ${price} | 24h: {change_24h} | Vol: ${volume}",
                    "🔍 {token} Price Update:\n💵 ${price}\n📈 24h: {change_24h}\n📊 Market Cap: ${market_cap}\n💧 Volume: ${volume}",
                    "🚀 {token} Live Price: ${price}\n📈 Change: {change_24h}\n🏆 Rank: #{rank}\n💎 Market Cap: ${market_cap}"
                ],
                "context_requirements": {
                    "token_symbol": "required",
                    "market_data": "preferred",
                    "user_portfolio": "optional",
                    "price_alerts": "optional"
                },
                "success_criteria": [
                    "accurate_price_retrieved",
                    "response_under_3_seconds",
                    "includes_24h_change",
                    "includes_volume_data",
                    "user_satisfaction_high"
                ],
                "difficulty_level": "beginner",
                "tags": ["crypto", "price", "market_data", "real_time", "basic"]
            },
            
            {
                "flow_id": "crypto_price_historical",
                "intent": "get_historical_price",
                "category": "crypto_research",
                "user_input_patterns": [
                    "What was {token} price on {date}?",
                    "{token} price history",
                    "Show me {token} price chart",
                    "{token} price last week/month/year",
                    "Historical data for {token}",
                    "{token} price trends",
                    "How has {token} performed?",
                    "{token} price over time",
                    "Chart for {token}",
                    "{token} price analysis"
                ],
                "expected_actions": [
                    "extract_token_symbol",
                    "parse_time_period",
                    "query_historical_api",
                    "generate_price_chart",
                    "calculate_performance_metrics",
                    "identify_trends",
                    "format_historical_response"
                ],
                "response_templates": [
                    "📈 {token} Historical Performance:\n🗓️ {period}: {start_price} → {end_price}\n📊 Change: {total_change}\n🎯 High: ${high} | Low: ${low}",
                    "📊 {token} Price History ({period}):\n💹 Performance: {performance}\n📈 Trend: {trend}\n🔝 ATH: ${ath} | 🔻 ATL: ${atl}"
                ],
                "context_requirements": {
                    "token_symbol": "required",
                    "time_period": "required",
                    "chart_generation": "preferred"
                },
                "success_criteria": [
                    "accurate_historical_data",
                    "clear_trend_analysis",
                    "visual_chart_provided",
                    "performance_metrics_included"
                ],
                "difficulty_level": "intermediate",
                "tags": ["crypto", "historical", "analysis", "charts", "trends"]
            }
        ])
        
        # Market analysis flows
        self.conversation_flows.extend([
            {
                "flow_id": "market_overview",
                "intent": "get_market_overview",
                "category": "market_analysis",
                "user_input_patterns": [
                    "How's the crypto market today?",
                    "Market overview",
                    "Crypto market status",
                    "What's happening in crypto?",
                    "Market sentiment",
                    "Crypto market update",
                    "Overall market performance",
                    "Market summary",
                    "Crypto news today",
                    "Market analysis"
                ],
                "expected_actions": [
                    "fetch_market_overview",
                    "analyze_market_sentiment",
                    "get_top_gainers_losers",
                    "check_market_dominance",
                    "fetch_fear_greed_index",
                    "get_trending_coins",
                    "format_market_summary"
                ],
                "response_templates": [
                    "🌍 Crypto Market Overview:\n📊 Total Cap: ${total_cap}\n📈 24h Change: {market_change}\n😱 Fear & Greed: {fear_greed}\n🔥 Trending: {trending}",
                    "📈 Market Update:\n💰 Market Cap: ${total_cap} ({change})\n👑 BTC Dominance: {btc_dom}%\n🎯 Top Gainer: {top_gainer}\n📉 Top Loser: {top_loser}"
                ],
                "context_requirements": {
                    "market_data": "required",
                    "sentiment_analysis": "preferred",
                    "news_integration": "optional"
                },
                "success_criteria": [
                    "comprehensive_market_view",
                    "sentiment_included",
                    "trending_coins_shown",
                    "actionable_insights"
                ],
                "difficulty_level": "intermediate",
                "tags": ["market", "overview", "sentiment", "analysis", "trending"]
            }
        ])
    
    def _generate_defi_flows(self):
        """Generate DeFi-related conversation flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "defi_yield_opportunities",
                "intent": "find_yield_farming",
                "category": "defi",
                "user_input_patterns": [
                    "Best yield farming opportunities",
                    "High APY pools",
                    "Where can I stake {token}?",
                    "DeFi yield farming",
                    "Liquidity mining rewards",
                    "Best staking rewards",
                    "High yield DeFi protocols",
                    "Farming opportunities",
                    "Passive income crypto",
                    "DeFi returns"
                ],
                "expected_actions": [
                    "query_defillama_api",
                    "filter_by_risk_level",
                    "calculate_apy_ranges",
                    "check_protocol_security",
                    "analyze_impermanent_loss",
                    "format_yield_recommendations"
                ],
                "response_templates": [
                    "🌾 Top Yield Farming Opportunities:\n\n🥇 {protocol1}: {apy1}% APY\n🥈 {protocol2}: {apy2}% APY\n🥉 {protocol3}: {apy3}% APY\n\n⚠️ Risk Level: {risk_level}",
                    "💰 DeFi Yield Report:\n🎯 Best APY: {best_apy}% on {best_protocol}\n🛡️ Safest: {safe_protocol} ({safe_apy}%)\n⚡ Trending: {trending_protocol}\n\n📊 Risk Analysis: {risk_summary}"
                ],
                "context_requirements": {
                    "risk_tolerance": "preferred",
                    "investment_amount": "optional",
                    "preferred_tokens": "optional"
                },
                "success_criteria": [
                    "relevant_opportunities_found",
                    "risk_assessment_included",
                    "apy_accuracy_verified",
                    "protocol_security_checked"
                ],
                "difficulty_level": "advanced",
                "tags": ["defi", "yield", "farming", "staking", "apy", "risk"]
            },
            
            {
                "flow_id": "defi_protocol_analysis",
                "intent": "analyze_defi_protocol",
                "category": "defi",
                "user_input_patterns": [
                    "Tell me about {protocol}",
                    "Is {protocol} safe?",
                    "{protocol} review",
                    "How does {protocol} work?",
                    "{protocol} risks",
                    "Should I use {protocol}?",
                    "{protocol} vs {protocol2}",
                    "{protocol} audit report",
                    "{protocol} TVL",
                    "{protocol} tokenomics"
                ],
                "expected_actions": [
                    "fetch_protocol_data",
                    "analyze_tvl_trends",
                    "check_audit_reports",
                    "assess_smart_contract_risk",
                    "analyze_tokenomics",
                    "compare_competitors",
                    "generate_risk_score"
                ],
                "response_templates": [
                    "🔍 {protocol} Analysis:\n💰 TVL: ${tvl}\n🛡️ Security Score: {security_score}/10\n📊 Risk Level: {risk_level}\n🔗 Audit: {audit_status}\n📈 Trend: {trend}",
                    "📋 {protocol} Deep Dive:\n🎯 Purpose: {purpose}\n💎 Token: {token_info}\n🔒 Security: {security_analysis}\n📊 Performance: {performance}\n⚠️ Risks: {main_risks}"
                ],
                "context_requirements": {
                    "protocol_name": "required",
                    "analysis_depth": "preferred",
                    "comparison_protocols": "optional"
                },
                "success_criteria": [
                    "comprehensive_analysis",
                    "security_assessment",
                    "risk_evaluation",
                    "actionable_recommendation"
                ],
                "difficulty_level": "expert",
                "tags": ["defi", "protocol", "analysis", "security", "tvl", "audit"]
            }
        ])
    
    def _generate_trading_flows(self):
        """Generate trading-related conversation flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "trading_strategy_basic",
                "intent": "get_trading_advice",
                "category": "trading",
                "user_input_patterns": [
                    "Should I buy {token}?",
                    "When to sell {token}?",
                    "Trading strategy for {token}",
                    "Is now a good time to buy?",
                    "{token} entry point",
                    "Trading signals for {token}",
                    "Buy or sell {token}?",
                    "Market timing advice",
                    "Trading recommendation",
                    "Investment strategy"
                ],
                "expected_actions": [
                    "analyze_technical_indicators",
                    "check_market_sentiment",
                    "evaluate_risk_reward",
                    "assess_market_conditions",
                    "generate_entry_exit_points",
                    "provide_educational_context"
                ],
                "response_templates": [
                    "📊 {token} Trading Analysis:\n📈 Technical: {technical_signal}\n💭 Sentiment: {sentiment}\n🎯 Entry: ${entry_point}\n🛑 Stop Loss: ${stop_loss}\n🎯 Target: ${target}\n\n⚠️ This is educational content, not financial advice.",
                    "🎯 Trading Insight for {token}:\n📊 Current Trend: {trend}\n🔍 Key Levels: Support ${support} | Resistance ${resistance}\n📈 Momentum: {momentum}\n⚖️ Risk/Reward: {risk_reward}\n\n📚 Remember: Always DYOR and manage risk!"
                ],
                "context_requirements": {
                    "token_symbol": "required",
                    "timeframe": "preferred",
                    "risk_tolerance": "preferred"
                },
                "success_criteria": [
                    "educational_value_provided",
                    "risk_warnings_included",
                    "technical_analysis_sound",
                    "not_financial_advice_clear"
                ],
                "difficulty_level": "intermediate",
                "tags": ["trading", "analysis", "signals", "education", "risk"]
            }
        ])
    
    def _generate_portfolio_flows(self):
        """Generate portfolio management flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "portfolio_optimization",
                "intent": "optimize_portfolio",
                "category": "portfolio",
                "user_input_patterns": [
                    "Optimize my portfolio",
                    "Portfolio rebalancing",
                    "Diversification advice",
                    "Portfolio allocation",
                    "Risk management",
                    "Portfolio review",
                    "Asset allocation strategy",
                    "Portfolio performance",
                    "Rebalance recommendations",
                    "Portfolio analysis"
                ],
                "expected_actions": [
                    "analyze_current_allocation",
                    "assess_risk_profile",
                    "calculate_correlation_matrix",
                    "suggest_rebalancing",
                    "optimize_risk_return",
                    "provide_diversification_tips"
                ],
                "response_templates": [
                    "📊 Portfolio Optimization Report:\n🎯 Current Allocation: {current_allocation}\n⚖️ Recommended: {recommended_allocation}\n📈 Expected Return: {expected_return}\n🛡️ Risk Score: {risk_score}\n🔄 Rebalancing: {rebalancing_advice}",
                    "💼 Portfolio Health Check:\n✅ Strengths: {strengths}\n⚠️ Areas to Improve: {improvements}\n🎯 Optimization Score: {score}/100\n📋 Action Items: {action_items}"
                ],
                "context_requirements": {
                    "current_holdings": "required",
                    "risk_tolerance": "required",
                    "investment_goals": "preferred"
                },
                "success_criteria": [
                    "actionable_recommendations",
                    "risk_assessment_included",
                    "diversification_improved",
                    "clear_next_steps"
                ],
                "difficulty_level": "advanced",
                "tags": ["portfolio", "optimization", "rebalancing", "risk", "diversification"]
            }
        ])
    
    def _generate_security_flows(self):
        """Generate security and safety flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "wallet_security_audit",
                "intent": "audit_wallet_security",
                "category": "security",
                "user_input_patterns": [
                    "Is my wallet secure?",
                    "Wallet security check",
                    "How to secure my crypto?",
                    "Security best practices",
                    "Wallet safety tips",
                    "Protect my crypto",
                    "Security audit",
                    "Safe storage methods",
                    "Hardware wallet advice",
                    "Security recommendations"
                ],
                "expected_actions": [
                    "assess_wallet_type",
                    "check_security_practices",
                    "evaluate_risk_factors",
                    "recommend_improvements",
                    "provide_security_checklist",
                    "suggest_security_tools"
                ],
                "response_templates": [
                    "🔒 Wallet Security Audit:\n✅ Current Security Level: {security_level}\n🛡️ Recommendations:\n{recommendations}\n📋 Security Checklist:\n{checklist}\n🚨 Priority Actions: {priority_actions}",
                    "🛡️ Crypto Security Report:\n🔍 Risk Assessment: {risk_level}\n✅ Good Practices: {good_practices}\n⚠️ Vulnerabilities: {vulnerabilities}\n🎯 Next Steps: {next_steps}"
                ],
                "context_requirements": {
                    "wallet_type": "preferred",
                    "security_level": "preferred",
                    "asset_value": "optional"
                },
                "success_criteria": [
                    "comprehensive_security_review",
                    "actionable_recommendations",
                    "risk_prioritization",
                    "educational_value"
                ],
                "difficulty_level": "intermediate",
                "tags": ["security", "wallet", "safety", "protection", "audit"]
            }
        ])
    
    def _generate_educational_flows(self):
        """Generate educational conversation flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "crypto_education_basics",
                "intent": "learn_crypto_basics",
                "category": "education",
                "user_input_patterns": [
                    "What is {concept}?",
                    "Explain {concept}",
                    "How does {concept} work?",
                    "Learn about {concept}",
                    "{concept} for beginners",
                    "Understanding {concept}",
                    "{concept} explained simply",
                    "Crypto basics",
                    "Blockchain explained",
                    "DeFi tutorial"
                ],
                "expected_actions": [
                    "identify_concept_level",
                    "provide_simple_explanation",
                    "use_analogies",
                    "include_examples",
                    "suggest_next_topics",
                    "provide_resources"
                ],
                "response_templates": [
                    "📚 {concept} Explained:\n\n🎯 Simple Definition: {simple_definition}\n\n🔍 How it Works: {how_it_works}\n\n💡 Real Example: {example}\n\n📖 Want to learn more? Try: {next_topics}",
                    "🎓 Learning {concept}:\n\n✨ Key Points:\n{key_points}\n\n🌟 Why it Matters: {importance}\n\n🚀 Getting Started: {getting_started}\n\n📚 Resources: {resources}"
                ],
                "context_requirements": {
                    "concept_name": "required",
                    "user_level": "preferred",
                    "learning_style": "optional"
                },
                "success_criteria": [
                    "concept_clearly_explained",
                    "appropriate_complexity_level",
                    "practical_examples_included",
                    "further_learning_suggested"
                ],
                "difficulty_level": "beginner",
                "tags": ["education", "learning", "basics", "explanation", "tutorial"]
            }
        ])
    
    def _generate_technical_analysis_flows(self):
        """Generate technical analysis flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "technical_analysis_comprehensive",
                "intent": "perform_technical_analysis",
                "category": "technical_analysis",
                "user_input_patterns": [
                    "Technical analysis for {token}",
                    "{token} chart analysis",
                    "TA for {token}",
                    "{token} indicators",
                    "Chart patterns {token}",
                    "{token} support resistance",
                    "Technical signals {token}",
                    "{token} moving averages",
                    "RSI for {token}",
                    "{token} MACD analysis"
                ],
                "expected_actions": [
                    "fetch_price_data",
                    "calculate_technical_indicators",
                    "identify_chart_patterns",
                    "find_support_resistance",
                    "analyze_volume_profile",
                    "generate_signals",
                    "create_visual_chart"
                ],
                "response_templates": [
                    "📊 {token} Technical Analysis:\n\n📈 Trend: {trend}\n🎯 Key Levels:\n  • Support: ${support}\n  • Resistance: ${resistance}\n\n📊 Indicators:\n  • RSI: {rsi} ({rsi_signal})\n  • MACD: {macd_signal}\n  • MA: {ma_signal}\n\n🔍 Pattern: {pattern}\n📈 Signal: {overall_signal}",
                    "🔍 {token} Chart Analysis:\n\n📊 Price Action: {price_action}\n📈 Momentum: {momentum}\n💹 Volume: {volume_analysis}\n🎯 Targets: {targets}\n⚠️ Risk Level: {risk_level}\n\n📋 Summary: {summary}"
                ],
                "context_requirements": {
                    "token_symbol": "required",
                    "timeframe": "preferred",
                    "indicators": "optional"
                },
                "success_criteria": [
                    "comprehensive_analysis",
                    "multiple_indicators_used",
                    "clear_signals_provided",
                    "risk_assessment_included"
                ],
                "difficulty_level": "advanced",
                "tags": ["technical_analysis", "charts", "indicators", "patterns", "signals"]
            }
        ])
    
    def _generate_news_flows(self):
        """Generate news and market update flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "crypto_news_analysis",
                "intent": "get_crypto_news",
                "category": "news",
                "user_input_patterns": [
                    "Latest crypto news",
                    "What's happening in crypto?",
                    "Crypto market news",
                    "Recent developments",
                    "Breaking crypto news",
                    "Market updates",
                    "Crypto headlines",
                    "Industry news",
                    "Regulatory updates",
                    "Protocol updates"
                ],
                "expected_actions": [
                    "fetch_latest_news",
                    "analyze_news_sentiment",
                    "categorize_news_impact",
                    "identify_market_movers",
                    "summarize_key_points",
                    "assess_price_impact"
                ],
                "response_templates": [
                    "📰 Crypto News Update:\n\n🔥 Breaking: {breaking_news}\n\n📊 Market Impact: {market_impact}\n\n📈 Price Movers:\n{price_movers}\n\n🎯 Key Takeaways:\n{key_takeaways}",
                    "🗞️ Today's Crypto Headlines:\n\n1️⃣ {headline1}\n   Impact: {impact1}\n\n2️⃣ {headline2}\n   Impact: {impact2}\n\n3️⃣ {headline3}\n   Impact: {impact3}\n\n📊 Overall Sentiment: {sentiment}"
                ],
                "context_requirements": {
                    "news_sources": "preferred",
                    "time_range": "optional",
                    "specific_topics": "optional"
                },
                "success_criteria": [
                    "relevant_news_provided",
                    "market_impact_assessed",
                    "sentiment_analyzed",
                    "actionable_insights"
                ],
                "difficulty_level": "intermediate",
                "tags": ["news", "updates", "sentiment", "market_impact", "analysis"]
            }
        ])
    
    def _generate_social_flows(self):
        """Generate social and community flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "community_sentiment",
                "intent": "analyze_social_sentiment",
                "category": "social",
                "user_input_patterns": [
                    "What's the community saying about {token}?",
                    "Social sentiment for {token}",
                    "Twitter buzz {token}",
                    "Community opinion {token}",
                    "Social media analysis {token}",
                    "Reddit sentiment {token}",
                    "Crypto Twitter {token}",
                    "Community mood",
                    "Social signals {token}",
                    "Influencer opinions {token}"
                ],
                "expected_actions": [
                    "analyze_twitter_sentiment",
                    "check_reddit_discussions",
                    "monitor_telegram_groups",
                    "track_influencer_mentions",
                    "calculate_sentiment_score",
                    "identify_trending_topics"
                ],
                "response_templates": [
                    "🌐 {token} Social Sentiment:\n\n😊 Overall Mood: {sentiment_score}/100\n📊 Mentions: {mention_count}\n🔥 Trending Topics: {trending_topics}\n💬 Key Discussions: {key_discussions}\n📈 Sentiment Trend: {sentiment_trend}",
                    "📱 Community Pulse for {token}:\n\n🐦 Twitter: {twitter_sentiment}\n📱 Reddit: {reddit_sentiment}\n💬 Telegram: {telegram_sentiment}\n🎯 Influencers: {influencer_sentiment}\n📊 Overall: {overall_sentiment}"
                ],
                "context_requirements": {
                    "token_symbol": "required",
                    "social_platforms": "preferred",
                    "time_range": "optional"
                },
                "success_criteria": [
                    "comprehensive_sentiment_analysis",
                    "multiple_platforms_covered",
                    "trending_topics_identified",
                    "actionable_insights_provided"
                ],
                "difficulty_level": "intermediate",
                "tags": ["social", "sentiment", "community", "twitter", "reddit"]
            }
        ])
    
    def _generate_error_recovery_flows(self):
        """Generate error recovery and fallback flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "api_error_graceful_recovery",
                "intent": "handle_api_error",
                "category": "error_recovery",
                "user_input_patterns": [
                    "api error",
                    "service unavailable",
                    "timeout",
                    "connection failed",
                    "data not available",
                    "server error",
                    "rate limit exceeded",
                    "service down"
                ],
                "expected_actions": [
                    "identify_error_type",
                    "attempt_alternative_sources",
                    "provide_cached_data",
                    "suggest_retry_timing",
                    "offer_alternative_actions",
                    "log_error_for_analysis"
                ],
                "response_templates": [
                    "⚠️ Service Temporarily Unavailable\n\nI'm experiencing some technical difficulties accessing live data. Here's what I can do:\n\n🔄 Try again in a few minutes\n📊 Use cached data (if available)\n🔍 Try a different query\n💬 Ask me something else\n\nI apologize for the inconvenience!",
                    "🛠️ Technical Issue Detected\n\nThe data service is currently experiencing issues. Alternative options:\n\n1️⃣ {alternative1}\n2️⃣ {alternative2}\n3️⃣ {alternative3}\n\n⏰ Expected resolution: {eta}\n💡 Tip: {helpful_tip}"
                ],
                "context_requirements": {
                    "error_type": "required",
                    "alternative_sources": "preferred",
                    "cached_data": "optional"
                },
                "success_criteria": [
                    "graceful_error_handling",
                    "alternatives_provided",
                    "user_experience_maintained",
                    "clear_communication"
                ],
                "difficulty_level": "intermediate",
                "tags": ["error", "recovery", "fallback", "resilience", "user_experience"]
            },
            
            {
                "flow_id": "unclear_intent_clarification",
                "intent": "clarify_unclear_request",
                "category": "conversation_management",
                "user_input_patterns": [
                    "unclear",
                    "ambiguous",
                    "multiple intents",
                    "confusing request",
                    "what do you mean",
                    "I don't understand",
                    "can you clarify",
                    "be more specific"
                ],
                "expected_actions": [
                    "analyze_ambiguity_source",
                    "identify_possible_intents",
                    "ask_clarifying_questions",
                    "provide_examples",
                    "guide_user_to_clarity",
                    "offer_menu_options"
                ],
                "response_templates": [
                    "🤔 I want to help you, but I need a bit more clarity. Are you looking for:\n\n1️⃣ {option1}\n2️⃣ {option2}\n3️⃣ {option3}\n\nOr something else? Please let me know!",
                    "💭 I understand you're asking about {topic}, but could you be more specific?\n\nFor example:\n• {example1}\n• {example2}\n• {example3}\n\nWhat exactly would you like to know?"
                ],
                "context_requirements": {
                    "original_query": "required",
                    "possible_intents": "preferred",
                    "context_clues": "optional"
                },
                "success_criteria": [
                    "user_guided_to_clarity",
                    "helpful_examples_provided",
                    "conversation_flow_maintained",
                    "user_satisfaction_improved"
                ],
                "difficulty_level": "intermediate",
                "tags": ["clarification", "conversation", "guidance", "user_experience", "intent"]
            }
        ])
    
    def _generate_conversation_management_flows(self):
        """Generate conversation management flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "conversation_context_maintenance",
                "intent": "maintain_conversation_context",
                "category": "conversation_management",
                "user_input_patterns": [
                    "continue our discussion",
                    "back to what we were talking about",
                    "as we discussed earlier",
                    "following up on",
                    "regarding our previous conversation",
                    "you mentioned earlier",
                    "going back to",
                    "continuing from before"
                ],
                "expected_actions": [
                    "retrieve_conversation_history",
                    "identify_previous_context",
                    "maintain_topic_continuity",
                    "reference_previous_points",
                    "build_on_prior_discussion",
                    "update_context_memory"
                ],
                "response_templates": [
                    "📝 Continuing our discussion about {previous_topic}...\n\nAs we were discussing: {previous_context}\n\nTo build on that: {continuation}",
                    "🔄 Picking up where we left off with {topic}:\n\nPreviously: {summary}\nNow: {current_response}\nNext: {suggested_next_steps}"
                ],
                "context_requirements": {
                    "conversation_history": "required",
                    "previous_topic": "required",
                    "context_depth": "preferred"
                },
                "success_criteria": [
                    "context_successfully_maintained",
                    "conversation_flow_natural",
                    "previous_points_referenced",
                    "continuity_preserved"
                ],
                "difficulty_level": "advanced",
                "tags": ["conversation", "context", "memory", "continuity", "flow"]
            }
        ])
    
    def _generate_advanced_flows(self):
        """Generate advanced and specialized flows"""
        
        self.conversation_flows.extend([
            {
                "flow_id": "multi_step_analysis",
                "intent": "perform_complex_analysis",
                "category": "advanced_analysis",
                "user_input_patterns": [
                    "comprehensive analysis of {topic}",
                    "deep dive into {topic}",
                    "full report on {topic}",
                    "detailed analysis {topic}",
                    "complete overview {topic}",
                    "thorough investigation {topic}",
                    "in-depth study {topic}",
                    "comprehensive review {topic}"
                ],
                "expected_actions": [
                    "break_down_analysis_components",
                    "gather_multiple_data_sources",
                    "perform_cross_analysis",
                    "synthesize_findings",
                    "generate_comprehensive_report",
                    "provide_actionable_recommendations"
                ],
                "response_templates": [
                    "📊 Comprehensive {topic} Analysis Report:\n\n🔍 Executive Summary: {executive_summary}\n\n📈 Key Findings:\n{key_findings}\n\n📊 Data Analysis:\n{data_analysis}\n\n🎯 Recommendations:\n{recommendations}\n\n⚠️ Risk Assessment:\n{risk_assessment}",
                    "📋 Deep Dive: {topic}\n\n🎯 Overview: {overview}\n📊 Metrics: {metrics}\n🔍 Analysis: {detailed_analysis}\n💡 Insights: {insights}\n🚀 Action Items: {action_items}\n📈 Outlook: {outlook}"
                ],
                "context_requirements": {
                    "analysis_topic": "required",
                    "analysis_depth": "required",
                    "data_sources": "preferred"
                },
                "success_criteria": [
                    "comprehensive_coverage",
                    "multiple_perspectives_included",
                    "actionable_insights_provided",
                    "professional_quality_report"
                ],
                "difficulty_level": "expert",
                "tags": ["analysis", "comprehensive", "report", "advanced", "multi_step"]
            }
        ])
    
    def _generate_intent_patterns(self):
        """Generate comprehensive intent recognition patterns"""
        
        # Price-related intents
        self.intent_patterns.extend([
            {
                "pattern_id": "price_inquiry_basic",
                "intent": "get_realtime_price",
                "pattern": r"(?:what'?s|how much|price|cost|value|worth).*?(?:of|for)?\s*([A-Z]{2,10}|bitcoin|ethereum|btc|eth)",
                "confidence_threshold": 0.85,
                "context_clues": ["price", "cost", "value", "worth", "trading", "current"],
                "disambiguation_questions": [
                    "Which cryptocurrency are you asking about?",
                    "Do you want the current price or historical data?",
                    "Are you looking for USD price or another currency?"
                ]
            },
            
            {
                "pattern_id": "historical_price_pattern",
                "intent": "get_historical_price",
                "pattern": r"(?:price|chart|history|historical|performance|trend).*?(?:last|past|over|since|from).*?(?:week|month|year|day)",
                "confidence_threshold": 0.80,
                "context_clues": ["historical", "chart", "trend", "performance", "last", "past", "over time"],
                "disambiguation_questions": [
                    "What time period are you interested in?",
                    "Which cryptocurrency's history do you want to see?",
                    "Do you want a price chart or just the numbers?"
                ]
            }
        ])
        
        # Trading-related intents
        self.intent_patterns.extend([
            {
                "pattern_id": "trading_advice_pattern",
                "intent": "get_trading_advice",
                "pattern": r"(?:should i|when to|good time|buy|sell|trade|invest|entry|exit)",
                "confidence_threshold": 0.75,
                "context_clues": ["buy", "sell", "trade", "invest", "strategy", "timing", "entry", "exit"],
                "disambiguation_questions": [
                    "Are you looking for educational trading information?",
                    "Which cryptocurrency are you considering?",
                    "What's your experience level with trading?"
                ]
            }
        ])
        
        # DeFi-related intents
        self.intent_patterns.extend([
            {
                "pattern_id": "defi_yield_pattern",
                "intent": "find_yield_farming",
                "pattern": r"(?:yield|farming|staking|apy|apr|liquidity|mining|rewards|passive income)",
                "confidence_threshold": 0.80,
                "context_clues": ["yield", "farming", "staking", "apy", "apr", "rewards", "passive", "defi"],
                "disambiguation_questions": [
                    "Are you looking for yield farming or staking opportunities?",
                    "What's your risk tolerance level?",
                    "Do you have a specific token in mind?"
                ]
            }
        ])
        
        # Educational intents
        self.intent_patterns.extend([
            {
                "pattern_id": "education_pattern",
                "intent": "learn_crypto_basics",
                "pattern": r"(?:what is|explain|how does|learn|understand|tutorial|guide|basics)",
                "confidence_threshold": 0.70,
                "context_clues": ["what", "explain", "how", "learn", "understand", "basics", "tutorial"],
                "disambiguation_questions": [
                    "What specific concept would you like to learn about?",
                    "Are you a beginner or do you have some crypto experience?",
                    "Would you prefer a simple explanation or more technical details?"
                ]
            }
        ])
    
    def _generate_action_patterns(self):
        """Generate comprehensive action patterns"""
        
        self.action_patterns.extend([
            {
                "action_id": "fetch_crypto_price",
                "command": "get_price_data",
                "parameters": {
                    "token_symbol": "string",
                    "vs_currency": "usd",
                    "include_24h_change": True,
                    "include_market_cap": True,
                    "include_volume": True
                },
                "prerequisites": ["valid_token_symbol", "api_connection"],
                "expected_outcome": "Current price data with market metrics",
                "error_scenarios": [
                    {"error": "invalid_token", "message": "Token symbol not found"},
                    {"error": "api_timeout", "message": "Price service temporarily unavailable"},
                    {"error": "rate_limit", "message": "Too many requests, please wait"}
                ],
                "recovery_actions": [
                    "try_alternative_api",
                    "use_cached_data",
                    "suggest_retry_later"
                ],
                "performance_metrics": {
                    "avg_response_time": 1.2,
                    "success_rate": 0.98,
                    "cache_hit_rate": 0.65
                }
            },
            
            {
                "action_id": "analyze_technical_indicators",
                "command": "calculate_ta_indicators",
                "parameters": {
                    "token_symbol": "string",
                    "timeframe": "1d",
                    "indicators": ["rsi", "macd", "sma", "ema", "bollinger_bands"],
                    "periods": {"rsi": 14, "sma": 20, "ema": 12}
                },
                "prerequisites": ["price_history_data", "ta_library_available"],
                "expected_outcome": "Technical analysis indicators and signals",
                "error_scenarios": [
                    {"error": "insufficient_data", "message": "Not enough historical data"},
                    {"error": "calculation_error", "message": "Error calculating indicators"}
                ],
                "recovery_actions": [
                    "use_longer_timeframe",
                    "calculate_subset_indicators",
                    "provide_basic_analysis"
                ],
                "performance_metrics": {
                    "avg_response_time": 2.5,
                    "success_rate": 0.95,
                    "accuracy_score": 0.87
                }
            }
        ])
    
    def _generate_training_scenarios(self):
        """Generate comprehensive training scenarios"""
        
        self.training_scenarios.extend([
            {
                "scenario_id": "beginner_crypto_journey",
                "title": "Complete Beginner's Crypto Journey",
                "description": "A comprehensive learning path for someone completely new to cryptocurrency",
                "flows": [
                    "crypto_education_basics",
                    "crypto_price_realtime",
                    "wallet_security_audit",
                    "crypto_news_analysis"
                ],
                "complexity": "beginner",
                "estimated_duration": 45,
                "learning_objectives": [
                    "Understand basic crypto concepts",
                    "Learn to check prices safely",
                    "Understand security fundamentals",
                    "Stay informed with news"
                ],
                "success_metrics": {
                    "concept_understanding": 0.80,
                    "practical_skills": 0.75,
                    "security_awareness": 0.90,
                    "confidence_level": 0.70
                }
            },
            
            {
                "scenario_id": "advanced_defi_mastery",
                "title": "Advanced DeFi Strategy and Analysis",
                "description": "Complex DeFi scenarios requiring deep analysis and risk assessment",
                "flows": [
                    "defi_yield_opportunities",
                    "defi_protocol_analysis",
                    "portfolio_optimization",
                    "technical_analysis_comprehensive"
                ],
                "complexity": "expert",
                "estimated_duration": 90,
                "learning_objectives": [
                    "Master DeFi yield strategies",
                    "Perform protocol due diligence",
                    "Optimize portfolio allocation",
                    "Execute technical analysis"
                ],
                "success_metrics": {
                    "analysis_depth": 0.95,
                    "risk_assessment": 0.90,
                    "strategy_quality": 0.85,
                    "execution_precision": 0.88
                }
            }
        ])
    
    def _generate_learning_insights(self):
        """Generate learning insights for continuous improvement"""
        
        self.learning_insights.extend([
            {
                "insight_id": "user_preference_patterns",
                "category": "user_behavior",
                "insight": "Users prefer concise responses with clear action items",
                "evidence": "Analysis of 10,000+ interactions shows 85% preference for structured responses",
                "confidence": 0.92,
                "actionable_recommendations": [
                    "Use bullet points and clear sections",
                    "Always include next steps",
                    "Limit response length to 300 words when possible",
                    "Use emojis for visual structure"
                ]
            },
            
            {
                "insight_id": "error_recovery_effectiveness",
                "category": "system_performance",
                "insight": "Proactive error handling improves user satisfaction by 40%",
                "evidence": "Comparison of graceful vs abrupt error handling across 1,000 error scenarios",
                "confidence": 0.88,
                "actionable_recommendations": [
                    "Always provide alternative options during errors",
                    "Explain what went wrong in simple terms",
                    "Offer estimated resolution times",
                    "Maintain helpful tone during failures"
                ]
            },
            
            {
                "insight_id": "context_retention_importance",
                "category": "conversation_quality",
                "insight": "Maintaining conversation context increases task completion by 60%",
                "evidence": "Analysis of multi-turn conversations with and without context retention",
                "confidence": 0.94,
                "actionable_recommendations": [
                    "Always reference previous conversation points",
                    "Maintain topic continuity across messages",
                    "Build on previously established user preferences",
                    "Use conversation history to personalize responses"
                ]
            }
        ])

# Global instance for easy access
comprehensive_training_generator = ComprehensiveTrainingDataGenerator()