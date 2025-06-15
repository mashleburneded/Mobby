#!/usr/bin/env python3
"""
Enhance Intent Patterns
Add more comprehensive intent patterns for better recognition
"""

import sys
import sqlite3
import json

sys.path.append('src')

def enhance_intent_patterns():
    """Add comprehensive intent patterns to improve recognition"""
    
    # Additional intent patterns for better recognition
    additional_patterns = [
        # DeFi and TVL queries
        {
            "pattern_id": "defillama_tvl_query",
            "intent": "query_defillama_tvl",
            "pattern": r"(?:get|show|find).*?(?:tvl|total.*?value.*?locked).*?(?:of|for|from)?\s*(\w+).*?(?:defillama|defi)",
            "confidence_threshold": 0.9,
            "context_clues": ["tvl", "defillama", "total value locked", "protocol"],
            "disambiguation_questions": ["Which protocol are you interested in?", "Do you want current TVL or historical data?"]
        },
        {
            "pattern_id": "trading_volume_query",
            "intent": "get_trading_volume",
            "pattern": r"(?:what|show|get).*?(?:trading|daily).*?volume.*?(?:of|for)?\s*(\w+)",
            "confidence_threshold": 0.85,
            "context_clues": ["trading volume", "daily volume", "24h volume", "exchange"],
            "disambiguation_questions": ["Which exchange or timeframe?", "Do you want spot or derivatives volume?"]
        },
        {
            "pattern_id": "defi_explanation",
            "intent": "explain_defi",
            "pattern": r"(?:what|explain|tell.*?me).*?(?:is|about)?\s*defi",
            "confidence_threshold": 0.9,
            "context_clues": ["defi", "decentralized finance", "explain", "what is"],
            "disambiguation_questions": ["Are you new to DeFi?", "What specific aspect interests you?"]
        },
        {
            "pattern_id": "trading_advice_query",
            "intent": "request_trading_advice",
            "pattern": r"(?:should|can|would).*?(?:i|you).*?(?:buy|sell|trade|invest).*?(?:now|today)?",
            "confidence_threshold": 0.8,
            "context_clues": ["should i buy", "trading advice", "investment", "now or wait"],
            "disambiguation_questions": ["What's your risk tolerance?", "What timeframe are you considering?"]
        },
        {
            "pattern_id": "security_wallet_query",
            "intent": "wallet_security_advice",
            "pattern": r"(?:how|what).*?(?:secure|protect|safe).*?(?:wallet|crypto|funds)",
            "confidence_threshold": 0.95,  # Higher confidence to override portfolio analysis
            "context_clues": ["secure wallet", "protect crypto", "wallet security", "safe"],
            "disambiguation_questions": ["What type of wallet do you use?", "Are you concerned about a specific threat?"]
        },
        {
            "pattern_id": "crypto_wallet_security",
            "intent": "wallet_security_advice",
            "pattern": r"(?:secure|protect|safety).*?(?:my|crypto).*?wallet",
            "confidence_threshold": 0.98,  # Very high confidence
            "context_clues": ["secure my wallet", "crypto wallet", "wallet security", "protect wallet"],
            "disambiguation_questions": ["What type of wallet do you use?", "Are you concerned about a specific threat?"]
        },
        {
            "pattern_id": "yield_farming_query",
            "intent": "find_yield_opportunities",
            "pattern": r"(?:find|show|best).*?(?:yield|farming|apy|apr).*?(?:opportunities|pools)?",
            "confidence_threshold": 0.8,
            "context_clues": ["yield farming", "best apy", "farming opportunities", "liquidity pools"],
            "disambiguation_questions": ["What's your risk preference?", "Which blockchain are you interested in?"]
        },
        {
            "pattern_id": "market_trend_analysis",
            "intent": "analyze_market_trends",
            "pattern": r"(?:analyze|what|show).*?(?:market|current).*?(?:trend|trends|analysis)",
            "confidence_threshold": 0.8,
            "context_clues": ["market trends", "current market", "trend analysis", "market analysis"],
            "disambiguation_questions": ["Which market segment?", "What timeframe are you interested in?"]
        },
        {
            "pattern_id": "crypto_comparison",
            "intent": "compare_cryptocurrencies",
            "pattern": r"(?:compare|vs|versus).*?(?:bitcoin|ethereum|btc|eth|\w+).*?(?:and|vs|versus).*?(?:bitcoin|ethereum|btc|eth|\w+)",
            "confidence_threshold": 0.85,
            "context_clues": ["compare", "vs", "versus", "performance", "which is better"],
            "disambiguation_questions": ["What aspects would you like to compare?", "What timeframe interests you?"]
        },
        {
            "pattern_id": "protocol_specific_query",
            "intent": "query_specific_protocol",
            "pattern": r"(?:paradex|hyperliquid|uniswap|aave|compound|makerdao|curve)",
            "confidence_threshold": 0.9,
            "context_clues": ["protocol name", "specific platform", "dapp"],
            "disambiguation_questions": ["What information do you need about this protocol?", "Are you looking for TVL, volume, or other metrics?"]
        }
    ]
    
    # Connect to the database
    db_path = "data/agent_memory.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("🧠 Enhancing intent patterns...")
            
            for pattern in additional_patterns:
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
                print(f"   ✅ Added pattern: {pattern['intent']}")
            
            conn.commit()
            
            # Verify patterns were added
            cursor.execute("SELECT COUNT(*) FROM intent_patterns")
            total_patterns = cursor.fetchone()[0]
            print(f"\n📊 Total intent patterns: {total_patterns}")
            
            # Show some examples
            cursor.execute("SELECT intent, pattern FROM intent_patterns LIMIT 5")
            examples = cursor.fetchall()
            print(f"\n🔍 Example patterns:")
            for intent, pattern in examples:
                print(f"   • {intent}: {pattern[:50]}...")
            
            print(f"\n✅ Intent patterns enhanced successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error enhancing patterns: {e}")
        return False

if __name__ == "__main__":
    success = enhance_intent_patterns()
    sys.exit(0 if success else 1)