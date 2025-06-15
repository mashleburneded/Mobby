# src/intelligent_ai_provider.py
"""
Intelligent AI Provider Switching System
Automatically selects optimal AI provider based on query complexity, cost, and performance
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Available AI providers"""
    GROQ = "groq"
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"

class QueryComplexity(Enum):
    """Query complexity levels"""
    SIMPLE = "simple"          # Basic questions, greetings
    MODERATE = "moderate"      # Price queries, simple analysis
    COMPLEX = "complex"        # Multi-step analysis, comparisons
    ADVANCED = "advanced"      # Technical analysis, research

class ProviderCapability(Enum):
    """Provider capabilities"""
    FAST_RESPONSE = "fast_response"
    HIGH_QUALITY = "high_quality"
    COST_EFFECTIVE = "cost_effective"
    LARGE_CONTEXT = "large_context"
    TECHNICAL_ANALYSIS = "technical_analysis"
    CREATIVE_WRITING = "creative_writing"
    CODE_GENERATION = "code_generation"

@dataclass
class ProviderMetrics:
    """Performance metrics for an AI provider"""
    provider: AIProvider
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    avg_quality_score: float
    total_cost: float
    avg_cost_per_request: float
    uptime_percentage: float
    last_failure: Optional[datetime]
    consecutive_failures: int
    capabilities: List[ProviderCapability]
    rate_limit_remaining: int
    rate_limit_reset: Optional[datetime]

@dataclass
class QueryAnalysis:
    """Analysis of a query for provider selection"""
    complexity: QueryComplexity
    estimated_tokens: int
    required_capabilities: List[ProviderCapability]
    urgency_level: float  # 0.0 to 1.0
    cost_sensitivity: float  # 0.0 to 1.0
    quality_requirement: float  # 0.0 to 1.0
    context_length_needed: int
    expected_response_length: int

@dataclass
class ProviderSelection:
    """Result of provider selection"""
    primary_provider: AIProvider
    fallback_providers: List[AIProvider]
    selection_reason: str
    estimated_cost: float
    estimated_response_time: float
    confidence_score: float

class IntelligentAIProviderSystem:
    """Intelligent AI provider selection and management system"""
    
    def __init__(self):
        self.provider_metrics = {}
        self.provider_configs = self._initialize_provider_configs()
        self.performance_history = defaultdict(lambda: deque(maxlen=100))
        self.circuit_breakers = {}
        self.cost_tracking = defaultdict(float)
        self.daily_usage = defaultdict(int)
        self.user_preferences = {}
        self._initialize_metrics()
    
    def _initialize_provider_configs(self) -> Dict[AIProvider, Dict]:
        """Initialize provider configurations"""
        return {
            AIProvider.GROQ: {
                "base_cost_per_token": 0.0000001,  # Very low cost
                "max_tokens": 8192,
                "max_context": 32768,
                "avg_response_time": 0.5,  # Very fast
                "capabilities": [
                    ProviderCapability.FAST_RESPONSE,
                    ProviderCapability.COST_EFFECTIVE,
                    ProviderCapability.TECHNICAL_ANALYSIS
                ],
                "rate_limit": 30,  # requests per minute
                "quality_score": 0.8,
                "reliability": 0.95
            },
            
            AIProvider.OPENAI: {
                "base_cost_per_token": 0.000002,  # Moderate cost
                "max_tokens": 4096,
                "max_context": 128000,
                "avg_response_time": 2.0,
                "capabilities": [
                    ProviderCapability.HIGH_QUALITY,
                    ProviderCapability.LARGE_CONTEXT,
                    ProviderCapability.CODE_GENERATION,
                    ProviderCapability.TECHNICAL_ANALYSIS
                ],
                "rate_limit": 60,
                "quality_score": 0.95,
                "reliability": 0.98
            },
            
            AIProvider.GEMINI: {
                "base_cost_per_token": 0.0000005,  # Low cost
                "max_tokens": 8192,
                "max_context": 1000000,  # Very large context
                "avg_response_time": 1.5,
                "capabilities": [
                    ProviderCapability.LARGE_CONTEXT,
                    ProviderCapability.COST_EFFECTIVE,
                    ProviderCapability.HIGH_QUALITY,
                    ProviderCapability.TECHNICAL_ANALYSIS
                ],
                "rate_limit": 60,
                "quality_score": 0.9,
                "reliability": 0.96
            },
            
            AIProvider.ANTHROPIC: {
                "base_cost_per_token": 0.000003,  # Higher cost
                "max_tokens": 4096,
                "max_context": 200000,
                "avg_response_time": 2.5,
                "capabilities": [
                    ProviderCapability.HIGH_QUALITY,
                    ProviderCapability.LARGE_CONTEXT,
                    ProviderCapability.CREATIVE_WRITING,
                    ProviderCapability.TECHNICAL_ANALYSIS
                ],
                "rate_limit": 50,
                "quality_score": 0.97,
                "reliability": 0.97
            },
            
            AIProvider.OPENROUTER: {
                "base_cost_per_token": 0.000001,  # Variable cost
                "max_tokens": 4096,
                "max_context": 32768,
                "avg_response_time": 3.0,
                "capabilities": [
                    ProviderCapability.COST_EFFECTIVE,
                    ProviderCapability.HIGH_QUALITY
                ],
                "rate_limit": 100,
                "quality_score": 0.85,
                "reliability": 0.92
            }
        }
    
    def _initialize_metrics(self):
        """Initialize provider metrics"""
        for provider in AIProvider:
            config = self.provider_configs[provider]
            self.provider_metrics[provider] = ProviderMetrics(
                provider=provider,
                total_requests=0,
                successful_requests=0,
                failed_requests=0,
                avg_response_time=config["avg_response_time"],
                avg_quality_score=config["quality_score"],
                total_cost=0.0,
                avg_cost_per_request=0.0,
                uptime_percentage=config["reliability"],
                last_failure=None,
                consecutive_failures=0,
                capabilities=config["capabilities"],
                rate_limit_remaining=config["rate_limit"],
                rate_limit_reset=None
            )
            
            # Initialize circuit breaker
            self.circuit_breakers[provider] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "last_failure_time": None,
                "timeout": 60  # seconds
            }
    
    async def analyze_query(self, text: str, context: Dict[str, Any]) -> QueryAnalysis:
        """Analyze query to determine optimal provider"""
        # Estimate complexity
        complexity = self._estimate_complexity(text, context)
        
        # Estimate token usage
        estimated_tokens = len(text.split()) * 1.3  # Rough estimation
        
        # Determine required capabilities
        required_capabilities = self._determine_required_capabilities(text, context)
        
        # Assess urgency
        urgency_level = self._assess_urgency(text, context)
        
        # Determine cost sensitivity
        cost_sensitivity = context.get("cost_sensitivity", 0.5)
        
        # Determine quality requirement
        quality_requirement = self._assess_quality_requirement(text, context)
        
        # Estimate context length needed
        context_length_needed = self._estimate_context_length(context)
        
        # Estimate response length
        expected_response_length = self._estimate_response_length(text, complexity)
        
        return QueryAnalysis(
            complexity=complexity,
            estimated_tokens=estimated_tokens,
            required_capabilities=required_capabilities,
            urgency_level=urgency_level,
            cost_sensitivity=cost_sensitivity,
            quality_requirement=quality_requirement,
            context_length_needed=context_length_needed,
            expected_response_length=expected_response_length
        )
    
    async def select_provider(self, query_analysis: QueryAnalysis, user_id: Optional[int] = None) -> ProviderSelection:
        """Select optimal provider based on query analysis"""
        # Get user preferences
        user_prefs = self.user_preferences.get(user_id, {})
        preferred_provider = user_prefs.get("preferred_provider")
        
        # Score all providers
        provider_scores = {}
        
        for provider in AIProvider:
            if not self._is_provider_available(provider):
                continue
            
            score = await self._calculate_provider_score(provider, query_analysis, user_prefs)
            provider_scores[provider] = score
        
        if not provider_scores:
            # All providers unavailable, use fallback
            return self._create_fallback_selection()
        
        # Sort providers by score
        sorted_providers = sorted(provider_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_provider = sorted_providers[0][0]
        fallback_providers = [p[0] for p in sorted_providers[1:3]]  # Top 2 fallbacks
        
        # If user has preferred provider and it's available, consider it
        if (preferred_provider and 
            preferred_provider in provider_scores and 
            provider_scores[preferred_provider] > 0.5):
            
            # Use preferred provider if score is reasonable
            if provider_scores[preferred_provider] >= provider_scores[primary_provider] * 0.8:
                primary_provider = preferred_provider
                fallback_providers = [p for p in fallback_providers if p != preferred_provider]
        
        # Calculate estimates
        config = self.provider_configs[primary_provider]
        metrics = self.provider_metrics[primary_provider]
        
        estimated_cost = (query_analysis.estimated_tokens + query_analysis.expected_response_length) * config["base_cost_per_token"]
        estimated_response_time = metrics.avg_response_time
        confidence_score = provider_scores[primary_provider]
        
        selection_reason = self._generate_selection_reason(primary_provider, query_analysis, provider_scores)
        
        return ProviderSelection(
            primary_provider=primary_provider,
            fallback_providers=fallback_providers,
            selection_reason=selection_reason,
            estimated_cost=estimated_cost,
            estimated_response_time=estimated_response_time,
            confidence_score=confidence_score
        )
    
    async def execute_with_fallback(self, query: str, provider_selection: ProviderSelection, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query with automatic fallback on failure"""
        providers_to_try = [provider_selection.primary_provider] + provider_selection.fallback_providers
        
        for i, provider in enumerate(providers_to_try):
            if not self._is_provider_available(provider):
                continue
            
            start_time = time.time()
            
            try:
                # Execute query with provider
                result = await self._execute_with_provider(provider, query, context)
                
                # Record success
                response_time = time.time() - start_time
                await self._record_success(provider, response_time, result)
                
                result["provider_used"] = provider.value
                result["is_fallback"] = i > 0
                result["attempt_number"] = i + 1
                
                return result
                
            except Exception as e:
                # Record failure
                await self._record_failure(provider, str(e))
                
                logger.warning(f"Provider {provider.value} failed: {e}")
                
                # If this was the last provider, return error
                if i == len(providers_to_try) - 1:
                    return {
                        "type": "error",
                        "message": "All AI providers are currently unavailable. Please try again later.",
                        "error": str(e),
                        "providers_tried": [p.value for p in providers_to_try]
                    }
        
        return {
            "type": "error",
            "message": "No AI providers are currently available.",
            "providers_tried": []
        }
    
    async def _execute_with_provider(self, provider: AIProvider, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query with specific provider"""
        # Import provider-specific modules
        if provider == AIProvider.GROQ:
            from ai_provider_manager import generate_ai_response
            return await generate_ai_response(query, context.get("user_id", "unknown"), "groq")
        
        elif provider == AIProvider.OPENAI:
            from ai_provider_manager import generate_ai_response
            return await generate_ai_response(query, context.get("user_id", "unknown"), "openai")
        
        elif provider == AIProvider.GEMINI:
            from ai_provider_manager import generate_ai_response
            return await generate_ai_response(query, context.get("user_id", "unknown"), "gemini")
        
        elif provider == AIProvider.ANTHROPIC:
            from ai_provider_manager import generate_ai_response
            return await generate_ai_response(query, context.get("user_id", "unknown"), "anthropic")
        
        elif provider == AIProvider.OPENROUTER:
            from ai_provider_manager import generate_ai_response
            return await generate_ai_response(query, context.get("user_id", "unknown"), "openrouter")
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _estimate_complexity(self, text: str, context: Dict[str, Any]) -> QueryComplexity:
        """Estimate query complexity"""
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Simple queries
        if word_count <= 5 and any(word in text_lower for word in ["hi", "hello", "thanks", "yes", "no"]):
            return QueryComplexity.SIMPLE
        
        # Complex indicators
        complex_indicators = [
            "analyze", "compare", "explain", "strategy", "technical analysis",
            "correlation", "risk assessment", "optimization", "recommendation"
        ]
        
        if any(indicator in text_lower for indicator in complex_indicators):
            return QueryComplexity.COMPLEX
        
        # Advanced indicators
        advanced_indicators = [
            "arbitrage", "derivatives", "quantitative", "algorithmic",
            "machine learning", "backtesting", "monte carlo"
        ]
        
        if any(indicator in text_lower for indicator in advanced_indicators):
            return QueryComplexity.ADVANCED
        
        # Moderate by default
        return QueryComplexity.MODERATE
    
    def _determine_required_capabilities(self, text: str, context: Dict[str, Any]) -> List[ProviderCapability]:
        """Determine required capabilities for the query"""
        capabilities = []
        text_lower = text.lower()
        
        # Fast response needed
        if any(word in text_lower for word in ["quick", "fast", "urgent", "now", "immediately"]):
            capabilities.append(ProviderCapability.FAST_RESPONSE)
        
        # High quality needed
        if any(word in text_lower for word in ["detailed", "comprehensive", "thorough", "analysis"]):
            capabilities.append(ProviderCapability.HIGH_QUALITY)
        
        # Technical analysis
        if any(word in text_lower for word in ["technical", "chart", "indicator", "rsi", "macd", "fibonacci"]):
            capabilities.append(ProviderCapability.TECHNICAL_ANALYSIS)
        
        # Large context needed
        conversation_length = len(context.get("conversation_history", []))
        if conversation_length > 10:
            capabilities.append(ProviderCapability.LARGE_CONTEXT)
        
        # Cost effectiveness
        if context.get("cost_sensitive", False):
            capabilities.append(ProviderCapability.COST_EFFECTIVE)
        
        return capabilities
    
    def _assess_urgency(self, text: str, context: Dict[str, Any]) -> float:
        """Assess urgency level of the query"""
        text_lower = text.lower()
        
        # High urgency indicators
        high_urgency = ["urgent", "emergency", "asap", "immediately", "now", "quick"]
        if any(word in text_lower for word in high_urgency):
            return 1.0
        
        # Medium urgency indicators
        medium_urgency = ["soon", "fast", "quickly"]
        if any(word in text_lower for word in medium_urgency):
            return 0.7
        
        # Price queries are often time-sensitive
        if any(word in text_lower for word in ["price", "cost", "value", "worth"]):
            return 0.6
        
        return 0.3  # Default low urgency
    
    def _assess_quality_requirement(self, text: str, context: Dict[str, Any]) -> float:
        """Assess quality requirement for the query"""
        text_lower = text.lower()
        
        # High quality indicators
        high_quality = ["analysis", "detailed", "comprehensive", "thorough", "research", "study"]
        if any(word in text_lower for word in high_quality):
            return 1.0
        
        # Medium quality indicators
        medium_quality = ["explain", "compare", "recommend", "advice"]
        if any(word in text_lower for word in medium_quality):
            return 0.7
        
        # Simple queries don't need high quality
        simple_queries = ["hi", "hello", "thanks", "price", "cost"]
        if any(word in text_lower for word in simple_queries):
            return 0.3
        
        return 0.5  # Default medium quality
    
    def _estimate_context_length(self, context: Dict[str, Any]) -> int:
        """Estimate context length needed"""
        conversation_history = context.get("conversation_history", [])
        context_length = sum(len(msg.get("text", "").split()) for msg in conversation_history)
        
        # Add current context
        context_length += len(str(context).split())
        
        return context_length
    
    def _estimate_response_length(self, text: str, complexity: QueryComplexity) -> int:
        """Estimate expected response length"""
        base_length = {
            QueryComplexity.SIMPLE: 20,
            QueryComplexity.MODERATE: 100,
            QueryComplexity.COMPLEX: 300,
            QueryComplexity.ADVANCED: 500
        }
        
        return base_length.get(complexity, 100)
    
    async def _calculate_provider_score(self, provider: AIProvider, query_analysis: QueryAnalysis, user_prefs: Dict) -> float:
        """Calculate score for a provider based on query requirements"""
        config = self.provider_configs[provider]
        metrics = self.provider_metrics[provider]
        
        score = 0.0
        
        # Base reliability score
        score += metrics.uptime_percentage * 0.3
        
        # Capability matching
        required_caps = set(query_analysis.required_capabilities)
        provider_caps = set(config["capabilities"])
        capability_match = len(required_caps.intersection(provider_caps)) / max(len(required_caps), 1)
        score += capability_match * 0.25
        
        # Response time scoring (inverse - faster is better)
        if query_analysis.urgency_level > 0.7:
            time_score = 1.0 / (metrics.avg_response_time + 0.1)
            score += min(time_score / 5.0, 0.2) * 0.2
        
        # Quality scoring
        if query_analysis.quality_requirement > 0.7:
            score += metrics.avg_quality_score * 0.15
        
        # Cost scoring (inverse - cheaper is better for cost-sensitive queries)
        if query_analysis.cost_sensitivity > 0.5:
            cost_score = 1.0 / (config["base_cost_per_token"] * 1000000 + 1)
            score += cost_score * 0.1
        
        # Context length support
        if query_analysis.context_length_needed > config["max_context"] * 0.8:
            score *= 0.5  # Penalize if context is too large
        
        # Rate limiting consideration
        if metrics.rate_limit_remaining < 5:
            score *= 0.3  # Heavy penalty for rate-limited providers
        
        # Circuit breaker consideration
        if self.circuit_breakers[provider]["state"] == "open":
            score = 0.0  # Don't use providers with open circuit breakers
        elif self.circuit_breakers[provider]["state"] == "half_open":
            score *= 0.5  # Reduced score for half-open circuit breakers
        
        # Recent performance consideration
        recent_performance = self._get_recent_performance(provider)
        score *= recent_performance
        
        return min(score, 1.0)
    
    def _is_provider_available(self, provider: AIProvider) -> bool:
        """Check if provider is available"""
        circuit_breaker = self.circuit_breakers[provider]
        
        # Check circuit breaker state
        if circuit_breaker["state"] == "open":
            # Check if timeout has passed
            if (circuit_breaker["last_failure_time"] and 
                datetime.now() - circuit_breaker["last_failure_time"] > timedelta(seconds=circuit_breaker["timeout"])):
                circuit_breaker["state"] = "half_open"
                return True
            return False
        
        # Check rate limits
        metrics = self.provider_metrics[provider]
        if metrics.rate_limit_remaining <= 0:
            if metrics.rate_limit_reset and datetime.now() < metrics.rate_limit_reset:
                return False
        
        return True
    
    def _get_recent_performance(self, provider: AIProvider) -> float:
        """Get recent performance score for provider"""
        history = self.performance_history[provider]
        if not history:
            return 1.0
        
        # Calculate success rate from recent history
        recent_successes = sum(1 for entry in list(history)[-20:] if entry.get("success", False))
        recent_total = min(len(history), 20)
        
        if recent_total == 0:
            return 1.0
        
        return recent_successes / recent_total
    
    async def _record_success(self, provider: AIProvider, response_time: float, result: Dict[str, Any]):
        """Record successful provider usage"""
        metrics = self.provider_metrics[provider]
        
        # Update metrics
        metrics.total_requests += 1
        metrics.successful_requests += 1
        metrics.consecutive_failures = 0
        
        # Update average response time
        metrics.avg_response_time = (
            (metrics.avg_response_time * (metrics.total_requests - 1) + response_time) / 
            metrics.total_requests
        )
        
        # Update uptime percentage
        metrics.uptime_percentage = metrics.successful_requests / metrics.total_requests
        
        # Record in performance history
        self.performance_history[provider].append({
            "timestamp": datetime.now(),
            "success": True,
            "response_time": response_time,
            "quality_score": result.get("quality_score", 0.8)
        })
        
        # Reset circuit breaker if it was half-open
        if self.circuit_breakers[provider]["state"] == "half_open":
            self.circuit_breakers[provider]["state"] = "closed"
            self.circuit_breakers[provider]["failure_count"] = 0
    
    async def _record_failure(self, provider: AIProvider, error: str):
        """Record provider failure"""
        metrics = self.provider_metrics[provider]
        circuit_breaker = self.circuit_breakers[provider]
        
        # Update metrics
        metrics.total_requests += 1
        metrics.failed_requests += 1
        metrics.consecutive_failures += 1
        metrics.last_failure = datetime.now()
        
        # Update uptime percentage
        if metrics.total_requests > 0:
            metrics.uptime_percentage = metrics.successful_requests / metrics.total_requests
        
        # Record in performance history
        self.performance_history[provider].append({
            "timestamp": datetime.now(),
            "success": False,
            "error": error
        })
        
        # Update circuit breaker
        circuit_breaker["failure_count"] += 1
        circuit_breaker["last_failure_time"] = datetime.now()
        
        # Open circuit breaker if too many failures
        if circuit_breaker["failure_count"] >= 5:
            circuit_breaker["state"] = "open"
            logger.warning(f"Circuit breaker opened for provider {provider.value}")
    
    def _create_fallback_selection(self) -> ProviderSelection:
        """Create fallback selection when no providers are available"""
        return ProviderSelection(
            primary_provider=AIProvider.GROQ,  # Default fallback
            fallback_providers=[],
            selection_reason="Fallback selection - all providers unavailable",
            estimated_cost=0.0,
            estimated_response_time=5.0,
            confidence_score=0.1
        )
    
    def _generate_selection_reason(self, provider: AIProvider, query_analysis: QueryAnalysis, scores: Dict[AIProvider, float]) -> str:
        """Generate human-readable selection reason"""
        config = self.provider_configs[provider]
        score = scores[provider]
        
        reasons = []
        
        if ProviderCapability.FAST_RESPONSE in config["capabilities"] and query_analysis.urgency_level > 0.7:
            reasons.append("fast response time")
        
        if ProviderCapability.HIGH_QUALITY in config["capabilities"] and query_analysis.quality_requirement > 0.7:
            reasons.append("high quality responses")
        
        if ProviderCapability.COST_EFFECTIVE in config["capabilities"] and query_analysis.cost_sensitivity > 0.5:
            reasons.append("cost effectiveness")
        
        if ProviderCapability.LARGE_CONTEXT in config["capabilities"] and query_analysis.context_length_needed > 1000:
            reasons.append("large context support")
        
        if not reasons:
            reasons.append("best overall performance")
        
        return f"Selected {provider.value} for {', '.join(reasons)} (score: {score:.2f})"
    
    async def set_user_preference(self, user_id: int, preferred_provider: str, cost_sensitivity: float = 0.5):
        """Set user preferences for provider selection"""
        try:
            provider_enum = AIProvider(preferred_provider.lower())
            self.user_preferences[user_id] = {
                "preferred_provider": provider_enum,
                "cost_sensitivity": cost_sensitivity
            }
        except ValueError:
            logger.error(f"Invalid provider: {preferred_provider}")
    
    async def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        
        for provider in AIProvider:
            metrics = self.provider_metrics[provider]
            circuit_breaker = self.circuit_breakers[provider]
            
            status[provider.value] = {
                "available": self._is_provider_available(provider),
                "circuit_breaker_state": circuit_breaker["state"],
                "uptime_percentage": metrics.uptime_percentage,
                "avg_response_time": metrics.avg_response_time,
                "avg_quality_score": metrics.avg_quality_score,
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "consecutive_failures": metrics.consecutive_failures,
                "rate_limit_remaining": metrics.rate_limit_remaining
            }
        
        return status
    
    async def optimize_costs(self, daily_budget: float) -> Dict[str, Any]:
        """Optimize provider usage based on daily budget"""
        current_cost = sum(self.cost_tracking.values())
        remaining_budget = daily_budget - current_cost
        
        recommendations = []
        
        if remaining_budget < daily_budget * 0.1:  # Less than 10% budget remaining
            recommendations.append("Switch to cost-effective providers (Groq, Gemini)")
            recommendations.append("Reduce response quality for non-critical queries")
        
        elif remaining_budget > daily_budget * 0.8:  # More than 80% budget remaining
            recommendations.append("Can use premium providers (OpenAI, Anthropic)")
            recommendations.append("Increase response quality for better user experience")
        
        return {
            "current_cost": current_cost,
            "remaining_budget": remaining_budget,
            "budget_utilization": (current_cost / daily_budget) * 100,
            "recommendations": recommendations
        }

# Global instance
intelligent_ai_provider = IntelligentAIProviderSystem()

async def select_optimal_provider(query: str, context: Dict[str, Any], user_id: Optional[int] = None) -> ProviderSelection:
    """Select optimal AI provider for a query"""
    query_analysis = await intelligent_ai_provider.analyze_query(query, context)
    return await intelligent_ai_provider.select_provider(query_analysis, user_id)

async def execute_with_intelligent_fallback(query: str, context: Dict[str, Any], user_id: Optional[int] = None) -> Dict[str, Any]:
    """Execute query with intelligent provider selection and fallback"""
    provider_selection = await select_optimal_provider(query, context, user_id)
    return await intelligent_ai_provider.execute_with_fallback(query, provider_selection, context)

async def set_user_ai_preference(user_id: int, preferred_provider: str, cost_sensitivity: float = 0.5):
    """Set user AI provider preferences"""
    await intelligent_ai_provider.set_user_preference(user_id, preferred_provider, cost_sensitivity)

async def get_ai_provider_status() -> Dict[str, Any]:
    """Get status of all AI providers"""
    return await intelligent_ai_provider.get_provider_status()