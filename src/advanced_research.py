# src/advanced_research.py
import asyncio
import logging
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import requests
import ta
from io import BytesIO
import base64

from config import config
from ai_providers import get_ai_response
from security_auditor import security_auditor
from performance_monitor import track_performance

logger = logging.getLogger(__name__)

@dataclass
class TokenMetrics:
    """Comprehensive token metrics"""
    symbol: str
    name: str
    current_price: float
    market_cap: float
    volume_24h: float
    circulating_supply: float
    total_supply: float
    max_supply: Optional[float]
    price_change_24h: float
    price_change_7d: float
    price_change_30d: float
    market_cap_rank: int
    volume_rank: int
    all_time_high: float
    all_time_low: float
    ath_change_percentage: float
    atl_change_percentage: float
    last_updated: datetime

@dataclass
class TechnicalAnalysis:
    """Technical analysis results"""
    symbol: str
    timeframe: str
    trend: str  # bullish, bearish, neutral
    support_levels: List[float]
    resistance_levels: List[float]
    indicators: Dict[str, Any]
    signals: List[Dict[str, Any]]
    confidence: float
    analysis_date: datetime

@dataclass
class FundamentalAnalysis:
    """Fundamental analysis results"""
    symbol: str
    project_name: str
    category: str
    description: str
    team_score: float
    technology_score: float
    adoption_score: float
    tokenomics_score: float
    overall_score: float
    strengths: List[str]
    weaknesses: List[str]
    risks: List[str]
    opportunities: List[str]
    analysis_date: datetime

@dataclass
class OnChainMetrics:
    """On-chain analysis metrics"""
    symbol: str
    active_addresses: int
    transaction_count: int
    transaction_volume: float
    network_value: float
    velocity: float
    concentration: float  # Gini coefficient
    whale_activity: Dict[str, Any]
    developer_activity: Dict[str, Any]
    social_metrics: Dict[str, Any]
    analysis_date: datetime

class AdvancedResearchEngine:
    """Advanced research and analysis tools"""
    
    def __init__(self):
        self.cache = {}
        self.analysis_cache = {}
        
    @track_performance.track_function
    async def comprehensive_token_research(self, user_id: int, symbol: str) -> Dict[str, Any]:
        """Generate comprehensive token research report"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "token_research", True, 
                {"symbol": symbol}
            )
            
            symbol = symbol.upper()
            
            # Gather all data
            token_metrics = await self._get_token_metrics(symbol)
            technical_analysis = await self._perform_technical_analysis(symbol, "1d")
            fundamental_analysis = await self._perform_fundamental_analysis(symbol)
            onchain_metrics = await self._get_onchain_metrics(symbol)
            
            if not token_metrics:
                return {"success": False, "message": f"Could not find data for {symbol}"}
            
            # Generate AI-powered insights
            ai_insights = await self._generate_ai_insights(
                symbol, token_metrics, technical_analysis, fundamental_analysis, onchain_metrics
            )
            
            # Create comprehensive report
            report = {
                "symbol": symbol,
                "generated_at": datetime.now().isoformat(),
                "token_metrics": asdict(token_metrics) if token_metrics else None,
                "technical_analysis": asdict(technical_analysis) if technical_analysis else None,
                "fundamental_analysis": asdict(fundamental_analysis) if fundamental_analysis else None,
                "onchain_metrics": asdict(onchain_metrics) if onchain_metrics else None,
                "ai_insights": ai_insights,
                "risk_assessment": await self._assess_risk(symbol, token_metrics, technical_analysis),
                "price_targets": await self._calculate_price_targets(symbol, technical_analysis, fundamental_analysis),
                "investment_thesis": await self._generate_investment_thesis(symbol, fundamental_analysis, ai_insights)
            }
            
            return {
                "success": True,
                "report": report,
                "summary": await self._generate_report_summary(report)
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive research: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def compare_tokens(self, user_id: int, symbols: List[str]) -> Dict[str, Any]:
        """Compare multiple tokens across various metrics"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "token_comparison", True, 
                {"symbols": symbols, "count": len(symbols)}
            )
            
            if len(symbols) < 2:
                return {"success": False, "message": "Please provide at least 2 tokens to compare"}
            
            if len(symbols) > 5:
                return {"success": False, "message": "Maximum 5 tokens can be compared at once"}
            
            # Gather data for all tokens
            comparison_data = {}
            
            for symbol in symbols:
                symbol = symbol.upper()
                token_metrics = await self._get_token_metrics(symbol)
                technical_analysis = await self._perform_technical_analysis(symbol, "1d")
                
                if token_metrics:
                    comparison_data[symbol] = {
                        "metrics": asdict(token_metrics),
                        "technical": asdict(technical_analysis) if technical_analysis else None
                    }
            
            if not comparison_data:
                return {"success": False, "message": "Could not find data for any of the provided tokens"}
            
            # Generate comparison analysis
            comparison_analysis = await self._generate_comparison_analysis(comparison_data)
            
            # Create comparison charts
            charts = await self._create_comparison_charts(comparison_data)
            
            return {
                "success": True,
                "comparison": {
                    "tokens": list(comparison_data.keys()),
                    "data": comparison_data,
                    "analysis": comparison_analysis,
                    "charts": charts,
                    "winner": await self._determine_comparison_winner(comparison_data),
                    "generated_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error comparing tokens: {e}")
            return {"success": False, "message": str(e)}

    @track_performance.track_function
    async def generate_technical_chart(self, user_id: int, symbol: str, timeframe: str = "1d") -> Dict[str, Any]:
        """Generate advanced technical analysis chart"""
        try:
            # Security audit
            security_auditor.log_sensitive_action(
                user_id, "chart_generation", True, 
                {"symbol": symbol, "timeframe": timeframe}
            )
            
            # Get historical price data
            price_data = await self._get_historical_data(symbol, timeframe)
            if not price_data:
                return {"success": False, "message": f"Could not get price data for {symbol}"}
            
            # Create DataFrame
            df = pd.DataFrame(price_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Calculate technical indicators
            df = await self._add_technical_indicators(df)
            
            # Create interactive chart
            chart = await self._create_interactive_chart(df, symbol, timeframe)
            
            # Generate chart analysis
            chart_analysis = await self._analyze_chart_patterns(df, symbol)
            
            return {
                "success": True,
                "chart": chart,
                "analysis": chart_analysis,
                "data_points": len(df),
                "timeframe": timeframe,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return {"success": False, "message": str(e)}

    async def _get_token_metrics(self, symbol: str) -> Optional[TokenMetrics]:
        """Get comprehensive token metrics"""
        try:
            # Check cache first
            cache_key = f"metrics_{symbol}"
            if cache_key in self.cache:
                cache_data = self.cache[cache_key]
                if datetime.now() - cache_data['timestamp'] < timedelta(minutes=5):
                    return cache_data['data']
            
            # Fetch from CoinGecko
            url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            market_data = data.get('market_data', {})
            
            metrics = TokenMetrics(
                symbol=symbol,
                name=data.get('name', ''),
                current_price=market_data.get('current_price', {}).get('usd', 0),
                market_cap=market_data.get('market_cap', {}).get('usd', 0),
                volume_24h=market_data.get('total_volume', {}).get('usd', 0),
                circulating_supply=market_data.get('circulating_supply', 0),
                total_supply=market_data.get('total_supply', 0),
                max_supply=market_data.get('max_supply'),
                price_change_24h=market_data.get('price_change_percentage_24h', 0),
                price_change_7d=market_data.get('price_change_percentage_7d', 0),
                price_change_30d=market_data.get('price_change_percentage_30d', 0),
                market_cap_rank=data.get('market_cap_rank', 0),
                volume_rank=0,  # Would need separate API call
                all_time_high=market_data.get('ath', {}).get('usd', 0),
                all_time_low=market_data.get('atl', {}).get('usd', 0),
                ath_change_percentage=market_data.get('ath_change_percentage', {}).get('usd', 0),
                atl_change_percentage=market_data.get('atl_change_percentage', {}).get('usd', 0),
                last_updated=datetime.now()
            )
            
            # Cache the result
            self.cache[cache_key] = {
                'data': metrics,
                'timestamp': datetime.now()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting token metrics: {e}")
            return None

    async def _perform_technical_analysis(self, symbol: str, timeframe: str) -> Optional[TechnicalAnalysis]:
        """Perform comprehensive technical analysis"""
        try:
            # Get historical data
            price_data = await self._get_historical_data(symbol, timeframe)
            if not price_data:
                return None
            
            df = pd.DataFrame(price_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Calculate indicators
            df = await self._add_technical_indicators(df)
            
            # Determine trend
            trend = await self._determine_trend(df)
            
            # Find support and resistance levels
            support_levels, resistance_levels = await self._find_support_resistance(df)
            
            # Generate signals
            signals = await self._generate_technical_signals(df)
            
            # Calculate confidence
            confidence = await self._calculate_technical_confidence(df, signals)
            
            analysis = TechnicalAnalysis(
                symbol=symbol,
                timeframe=timeframe,
                trend=trend,
                support_levels=support_levels,
                resistance_levels=resistance_levels,
                indicators={
                    'rsi': df['rsi'].iloc[-1] if 'rsi' in df.columns else None,
                    'macd': df['macd'].iloc[-1] if 'macd' in df.columns else None,
                    'macd_signal': df['macd_signal'].iloc[-1] if 'macd_signal' in df.columns else None,
                    'bb_upper': df['bb_upper'].iloc[-1] if 'bb_upper' in df.columns else None,
                    'bb_lower': df['bb_lower'].iloc[-1] if 'bb_lower' in df.columns else None,
                    'sma_20': df['sma_20'].iloc[-1] if 'sma_20' in df.columns else None,
                    'sma_50': df['sma_50'].iloc[-1] if 'sma_50' in df.columns else None,
                    'ema_12': df['ema_12'].iloc[-1] if 'ema_12' in df.columns else None,
                    'ema_26': df['ema_26'].iloc[-1] if 'ema_26' in df.columns else None
                },
                signals=signals,
                confidence=confidence,
                analysis_date=datetime.now()
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            return None

    async def _perform_fundamental_analysis(self, symbol: str) -> Optional[FundamentalAnalysis]:
        """Perform fundamental analysis"""
        try:
            # This would typically involve:
            # - Team analysis
            # - Technology assessment
            # - Tokenomics evaluation
            # - Adoption metrics
            # - Competitive analysis
            
            # For now, return a mock analysis
            analysis = FundamentalAnalysis(
                symbol=symbol,
                project_name=f"{symbol} Project",
                category="DeFi",  # Would be determined from data
                description=f"Analysis for {symbol}",
                team_score=7.5,
                technology_score=8.0,
                adoption_score=6.5,
                tokenomics_score=7.0,
                overall_score=7.25,
                strengths=[
                    "Strong technical foundation",
                    "Active development team",
                    "Growing adoption"
                ],
                weaknesses=[
                    "High competition",
                    "Regulatory uncertainty"
                ],
                risks=[
                    "Market volatility",
                    "Technical risks",
                    "Regulatory changes"
                ],
                opportunities=[
                    "Market expansion",
                    "New partnerships",
                    "Technology improvements"
                ],
                analysis_date=datetime.now()
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in fundamental analysis: {e}")
            return None

    async def _get_onchain_metrics(self, symbol: str) -> Optional[OnChainMetrics]:
        """Get on-chain metrics"""
        try:
            # This would typically use APIs like:
            # - Glassnode
            # - IntoTheBlock
            # - Messari
            # - Dune Analytics
            
            # For now, return mock data
            metrics = OnChainMetrics(
                symbol=symbol,
                active_addresses=50000,
                transaction_count=10000,
                transaction_volume=1000000,
                network_value=500000000,
                velocity=2.5,
                concentration=0.65,
                whale_activity={
                    "large_transactions": 150,
                    "whale_balance_change": 2.5
                },
                developer_activity={
                    "commits": 45,
                    "contributors": 12
                },
                social_metrics={
                    "twitter_followers": 100000,
                    "reddit_subscribers": 25000
                },
                analysis_date=datetime.now()
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting on-chain metrics: {e}")
            return None

    async def _get_historical_data(self, symbol: str, timeframe: str) -> Optional[List[Dict]]:
        """Get historical price data"""
        try:
            # Map timeframe to days
            timeframe_map = {
                "1h": 1,
                "4h": 7,
                "1d": 30,
                "1w": 90,
                "1M": 365
            }
            
            days = timeframe_map.get(timeframe, 30)
            
            url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}/market_chart?vs_currency=usd&days={days}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Convert to our format
            price_data = []
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            
            for i, price_point in enumerate(prices):
                timestamp = datetime.fromtimestamp(price_point[0] / 1000)
                price = price_point[1]
                volume = volumes[i][1] if i < len(volumes) else 0
                
                price_data.append({
                    'timestamp': timestamp,
                    'price': price,
                    'volume': volume,
                    'open': price,  # Simplified - would need OHLC data
                    'high': price,
                    'low': price,
                    'close': price
                })
            
            return price_data
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return None

    async def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to DataFrame"""
        try:
            # Use price as close for calculations
            close = df['price']
            
            # Moving averages
            df['sma_20'] = ta.trend.SMAIndicator(close, window=20).sma_indicator()
            df['sma_50'] = ta.trend.SMAIndicator(close, window=50).sma_indicator()
            df['ema_12'] = ta.trend.EMAIndicator(close, window=12).ema_indicator()
            df['ema_26'] = ta.trend.EMAIndicator(close, window=26).ema_indicator()
            
            # RSI
            df['rsi'] = ta.momentum.RSIIndicator(close).rsi()
            
            # MACD
            macd = ta.trend.MACD(close)
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            # Bollinger Bands
            bollinger = ta.volatility.BollingerBands(close)
            df['bb_upper'] = bollinger.bollinger_hband()
            df['bb_middle'] = bollinger.bollinger_mavg()
            df['bb_lower'] = bollinger.bollinger_lband()
            
            # Stochastic (using price as approximation for high/low)
            stoch = ta.momentum.StochasticOscillator(high=close, low=close, close=close)
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # Williams %R
            df['williams_r'] = ta.momentum.WilliamsRIndicator(high=close, low=close, close=close).williams_r()
            
            return df
            
        except Exception as e:
            logger.error(f"Error adding technical indicators: {e}")
            return df

    async def _determine_trend(self, df: pd.DataFrame) -> str:
        """Determine overall trend"""
        try:
            if 'sma_20' not in df.columns or 'sma_50' not in df.columns:
                return "neutral"
            
            current_price = df['price'].iloc[-1]
            sma_20 = df['sma_20'].iloc[-1]
            sma_50 = df['sma_50'].iloc[-1]
            
            if current_price > sma_20 > sma_50:
                return "bullish"
            elif current_price < sma_20 < sma_50:
                return "bearish"
            else:
                return "neutral"
                
        except Exception as e:
            logger.error(f"Error determining trend: {e}")
            return "neutral"

    async def _find_support_resistance(self, df: pd.DataFrame) -> Tuple[List[float], List[float]]:
        """Find support and resistance levels"""
        try:
            prices = df['price'].values
            
            # Simple approach: find local minima and maxima
            from scipy.signal import argrelextrema
            
            # Find local minima (support)
            support_indices = argrelextrema(prices, np.less, order=5)[0]
            support_levels = [prices[i] for i in support_indices]
            
            # Find local maxima (resistance)
            resistance_indices = argrelextrema(prices, np.greater, order=5)[0]
            resistance_levels = [prices[i] for i in resistance_indices]
            
            # Sort and take most recent/relevant levels
            support_levels = sorted(support_levels)[-3:]  # Last 3 support levels
            resistance_levels = sorted(resistance_levels, reverse=True)[:3]  # Top 3 resistance levels
            
            return support_levels, resistance_levels
            
        except Exception as e:
            logger.error(f"Error finding support/resistance: {e}")
            return [], []

    async def _generate_technical_signals(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate technical trading signals"""
        try:
            signals = []
            
            if len(df) < 2:
                return signals
            
            current = df.iloc[-1]
            previous = df.iloc[-2]
            
            # RSI signals
            if 'rsi' in df.columns:
                rsi = current['rsi']
                if rsi < 30:
                    signals.append({
                        "type": "BUY",
                        "indicator": "RSI",
                        "reason": f"RSI oversold at {rsi:.1f}",
                        "strength": "STRONG" if rsi < 25 else "MEDIUM"
                    })
                elif rsi > 70:
                    signals.append({
                        "type": "SELL",
                        "indicator": "RSI",
                        "reason": f"RSI overbought at {rsi:.1f}",
                        "strength": "STRONG" if rsi > 75 else "MEDIUM"
                    })
            
            # MACD signals
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                macd_current = current['macd']
                macd_signal_current = current['macd_signal']
                macd_previous = previous['macd']
                macd_signal_previous = previous['macd_signal']
                
                # Bullish crossover
                if (macd_previous <= macd_signal_previous and 
                    macd_current > macd_signal_current):
                    signals.append({
                        "type": "BUY",
                        "indicator": "MACD",
                        "reason": "MACD bullish crossover",
                        "strength": "MEDIUM"
                    })
                
                # Bearish crossover
                elif (macd_previous >= macd_signal_previous and 
                      macd_current < macd_signal_current):
                    signals.append({
                        "type": "SELL",
                        "indicator": "MACD",
                        "reason": "MACD bearish crossover",
                        "strength": "MEDIUM"
                    })
            
            # Moving average signals
            if 'sma_20' in df.columns and 'sma_50' in df.columns:
                price = current['price']
                sma_20 = current['sma_20']
                sma_50 = current['sma_50']
                
                if price > sma_20 > sma_50:
                    signals.append({
                        "type": "BUY",
                        "indicator": "MA",
                        "reason": "Price above both moving averages",
                        "strength": "MEDIUM"
                    })
                elif price < sma_20 < sma_50:
                    signals.append({
                        "type": "SELL",
                        "indicator": "MA",
                        "reason": "Price below both moving averages",
                        "strength": "MEDIUM"
                    })
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return []

    async def _calculate_technical_confidence(self, df: pd.DataFrame, signals: List[Dict]) -> float:
        """Calculate confidence in technical analysis"""
        try:
            if not signals:
                return 0.5
            
            # Count signal types
            buy_signals = len([s for s in signals if s['type'] == 'BUY'])
            sell_signals = len([s for s in signals if s['type'] == 'SELL'])
            
            # Calculate signal strength
            strong_signals = len([s for s in signals if s.get('strength') == 'STRONG'])
            total_signals = len(signals)
            
            # Base confidence on signal consensus and strength
            if buy_signals > sell_signals:
                consensus = buy_signals / total_signals
            elif sell_signals > buy_signals:
                consensus = sell_signals / total_signals
            else:
                consensus = 0.5
            
            strength_factor = (strong_signals / total_signals) if total_signals > 0 else 0
            
            confidence = (consensus * 0.7) + (strength_factor * 0.3)
            
            return min(0.95, max(0.05, confidence))
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5

    async def _generate_ai_insights(self, symbol: str, token_metrics: TokenMetrics, 
                                  technical_analysis: TechnicalAnalysis, 
                                  fundamental_analysis: FundamentalAnalysis,
                                  onchain_metrics: OnChainMetrics) -> str:
        """Generate AI-powered insights"""
        try:
            prompt = f"""
            Analyze {symbol} based on the following data:
            
            Token Metrics:
            - Price: ${token_metrics.current_price:,.2f}
            - Market Cap: ${token_metrics.market_cap:,.0f}
            - 24h Change: {token_metrics.price_change_24h:.2f}%
            - Market Cap Rank: #{token_metrics.market_cap_rank}
            
            Technical Analysis:
            - Trend: {technical_analysis.trend if technical_analysis else 'N/A'}
            - RSI: {technical_analysis.indicators.get('rsi', 'N/A') if technical_analysis else 'N/A'}
            - Signals: {len(technical_analysis.signals) if technical_analysis else 0} active signals
            
            Fundamental Score: {fundamental_analysis.overall_score if fundamental_analysis else 'N/A'}/10
            
            Provide 3-4 key insights about this token's current state and potential. Be concise and actionable.
            """
            
            insights = await get_ai_response(prompt, 0)  # Use system user ID
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return "AI insights temporarily unavailable."

    async def _assess_risk(self, symbol: str, token_metrics: TokenMetrics, 
                          technical_analysis: TechnicalAnalysis) -> Dict[str, Any]:
        """Assess investment risk"""
        try:
            risk_factors = []
            risk_score = 5.0  # Start with neutral risk (1-10 scale)
            
            if token_metrics:
                # Market cap risk
                if token_metrics.market_cap < 100_000_000:  # < $100M
                    risk_factors.append("Small market cap - high volatility risk")
                    risk_score += 1.5
                elif token_metrics.market_cap > 10_000_000_000:  # > $10B
                    risk_score -= 0.5
                
                # Volume risk
                volume_to_mcap = token_metrics.volume_24h / token_metrics.market_cap if token_metrics.market_cap > 0 else 0
                if volume_to_mcap < 0.01:  # Low volume
                    risk_factors.append("Low trading volume - liquidity risk")
                    risk_score += 1.0
                
                # Price volatility
                if abs(token_metrics.price_change_24h) > 20:
                    risk_factors.append("High price volatility")
                    risk_score += 1.0
                
                # Rank risk
                if token_metrics.market_cap_rank > 100:
                    risk_factors.append("Lower market cap ranking")
                    risk_score += 0.5
            
            if technical_analysis:
                # Technical risk
                sell_signals = len([s for s in technical_analysis.signals if s['type'] == 'SELL'])
                if sell_signals > 2:
                    risk_factors.append("Multiple bearish technical signals")
                    risk_score += 1.0
                
                if technical_analysis.trend == "bearish":
                    risk_factors.append("Bearish technical trend")
                    risk_score += 0.5
            
            # Cap risk score
            risk_score = min(10.0, max(1.0, risk_score))
            
            # Determine risk level
            if risk_score <= 3:
                risk_level = "LOW"
            elif risk_score <= 6:
                risk_level = "MEDIUM"
            elif risk_score <= 8:
                risk_level = "HIGH"
            else:
                risk_level = "VERY HIGH"
            
            return {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "recommendation": await self._get_risk_recommendation(risk_level)
            }
            
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            return {"risk_score": 5.0, "risk_level": "MEDIUM", "risk_factors": [], "recommendation": ""}

    async def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get risk-based recommendation"""
        recommendations = {
            "LOW": "Suitable for conservative investors. Consider for long-term holding.",
            "MEDIUM": "Moderate risk. Suitable for balanced portfolios with proper position sizing.",
            "HIGH": "High risk investment. Only suitable for risk-tolerant investors with small position sizes.",
            "VERY HIGH": "Extremely high risk. Consider avoiding or use only for speculation with minimal allocation."
        }
        return recommendations.get(risk_level, "")

    async def _calculate_price_targets(self, symbol: str, technical_analysis: TechnicalAnalysis,
                                     fundamental_analysis: FundamentalAnalysis) -> Dict[str, float]:
        """Calculate price targets"""
        try:
            targets = {}
            
            if technical_analysis and technical_analysis.resistance_levels:
                # Technical targets based on resistance levels
                targets["technical_upside"] = max(technical_analysis.resistance_levels)
                targets["technical_downside"] = min(technical_analysis.support_levels) if technical_analysis.support_levels else None
            
            # Fundamental targets would require more complex valuation models
            # For now, provide placeholder
            if fundamental_analysis and fundamental_analysis.overall_score > 7:
                targets["fundamental_upside"] = "Strong fundamentals suggest upside potential"
            
            return targets
            
        except Exception as e:
            logger.error(f"Error calculating price targets: {e}")
            return {}

    async def _generate_investment_thesis(self, symbol: str, fundamental_analysis: FundamentalAnalysis,
                                        ai_insights: str) -> str:
        """Generate investment thesis"""
        try:
            if not fundamental_analysis:
                return "Insufficient data for investment thesis."
            
            thesis = f"Investment Thesis for {symbol}:\n\n"
            
            if fundamental_analysis.overall_score >= 7:
                thesis += "BULLISH: Strong fundamentals support long-term growth potential.\n"
            elif fundamental_analysis.overall_score >= 5:
                thesis += "NEUTRAL: Mixed fundamentals suggest cautious approach.\n"
            else:
                thesis += "BEARISH: Weak fundamentals present significant risks.\n"
            
            thesis += f"\nKey Strengths: {', '.join(fundamental_analysis.strengths[:3])}\n"
            thesis += f"Main Risks: {', '.join(fundamental_analysis.risks[:2])}\n"
            
            return thesis
            
        except Exception as e:
            logger.error(f"Error generating investment thesis: {e}")
            return "Investment thesis unavailable."

    # Placeholder methods for comparison and charting
    async def _generate_comparison_analysis(self, comparison_data: Dict) -> Dict[str, Any]:
        """Generate comparison analysis"""
        return {"analysis": "Comparison analysis coming soon"}

    async def _create_comparison_charts(self, comparison_data: Dict) -> List[Dict]:
        """Create comparison charts"""
        return [{"type": "comparison", "data": "Chart data coming soon"}]

    async def _determine_comparison_winner(self, comparison_data: Dict) -> Dict[str, Any]:
        """Determine comparison winner"""
        return {"winner": "Analysis pending", "reason": "Comprehensive comparison coming soon"}

    async def _create_interactive_chart(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Create interactive chart"""
        return {"chart": "Interactive chart coming soon", "symbol": symbol, "timeframe": timeframe}

    async def _analyze_chart_patterns(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Analyze chart patterns"""
        return {"patterns": "Pattern analysis coming soon"}

    async def _generate_report_summary(self, report: Dict) -> str:
        """Generate executive summary of research report"""
        try:
            symbol = report["symbol"]
            summary = f"📊 **{symbol} Research Summary**\n\n"
            
            if report.get("token_metrics"):
                metrics = report["token_metrics"]
                summary += f"💰 Price: ${metrics['current_price']:,.2f} "
                summary += f"({metrics['price_change_24h']:+.2f}% 24h)\n"
                summary += f"📈 Market Cap: ${metrics['market_cap']:,.0f} "
                summary += f"(Rank #{metrics['market_cap_rank']})\n\n"
            
            if report.get("technical_analysis"):
                tech = report["technical_analysis"]
                summary += f"🔍 Technical Trend: {tech['trend'].title()}\n"
                summary += f"📊 Active Signals: {len(tech['signals'])}\n\n"
            
            if report.get("risk_assessment"):
                risk = report["risk_assessment"]
                summary += f"⚠️ Risk Level: {risk['risk_level']}\n"
                summary += f"🎯 Risk Score: {risk['risk_score']:.1f}/10\n\n"
            
            if report.get("ai_insights"):
                summary += f"🤖 **AI Insights:**\n{report['ai_insights']}\n\n"
            
            summary += f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Summary generation failed."

# Alias for compatibility
ResearchEngine = AdvancedResearchEngine

