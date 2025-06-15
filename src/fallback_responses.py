# src/fallback_responses.py - Fallback Response System
import random
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class FallbackResponseGenerator:
    """Generate intelligent fallback responses when APIs are unavailable"""
    
    def __init__(self):
        self.response_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, List[str]]:
        """Initialize response templates by category"""
        return {
            'price_query': [
                "I'm currently unable to fetch real-time price data. Please check a reliable crypto exchange or price tracking website for the most current {symbol} price.",
                "Price data is temporarily unavailable. You can check {symbol} prices on CoinGecko, CoinMarketCap, or your preferred exchange.",
                "I'm experiencing technical difficulties accessing price feeds. For {symbol} pricing, I recommend checking multiple sources for accuracy."
            ],
            'market_analysis': [
                "I'm currently unable to provide real-time market analysis. For the latest market insights, please check reputable crypto news sources and analysis platforms.",
                "Market analysis features are temporarily unavailable. Consider checking crypto news sites, trading platforms, or market analysis tools for current insights.",
                "Technical difficulties are preventing me from accessing market data. Please refer to professional trading platforms for current market analysis."
            ],
            'portfolio_query': [
                "Portfolio tracking is temporarily unavailable. Please check your exchange accounts or portfolio tracking apps for current holdings.",
                "I'm unable to access portfolio data right now. Your exchange accounts or dedicated portfolio apps will have the most up-to-date information.",
                "Portfolio features are experiencing technical issues. Please use your preferred portfolio tracking method for current data."
            ],
            'wallet_analysis': [
                "Wallet analysis is currently unavailable. You can check wallet addresses directly on blockchain explorers like Etherscan, Polygonscan, or similar tools.",
                "I'm unable to analyze wallet data at the moment. Blockchain explorers provide detailed wallet and transaction information.",
                "Wallet tracking features are temporarily down. Please use blockchain explorers for detailed wallet analysis."
            ],
            'general': [
                "I'm experiencing technical difficulties with my advanced features. Please try again later or rephrase your question.",
                "Some of my services are temporarily unavailable. I apologize for the inconvenience and appreciate your patience.",
                "I'm currently operating with limited functionality. Please try again in a few moments or contact support if the issue persists."
            ]
        }
    
    def get_fallback_response(self, query_type: str, context: Dict = None) -> str:
        """Get appropriate fallback response"""
        templates = self.response_templates.get(query_type, self.response_templates['general'])
        response = random.choice(templates)
        
        # Replace placeholders if context provided
        if context:
            for key, value in context.items():
                response = response.replace(f'{{{key}}}', str(value))
        
        return response
    
    def get_service_status_message(self) -> str:
        """Get service status message"""
        return """🔧 **Service Status Update**

Some advanced features are currently experiencing technical difficulties:
• Real-time price data may be delayed
• AI analysis features may be limited
• Some blockchain data may be unavailable

**What's still working:**
• Basic bot commands
• Database operations
• Security features
• Core functionality

We're working to restore full functionality. Thank you for your patience!"""

# Global instance
fallback_generator = FallbackResponseGenerator()
