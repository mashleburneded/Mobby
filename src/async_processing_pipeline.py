# src/async_processing_pipeline.py
"""
Async Processing Pipeline for Parallel Message Processing
Handles multiple analyses concurrently for improved performance
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import concurrent.futures
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class ProcessingStage(Enum):
    """Processing pipeline stages"""
    INTENT_ANALYSIS = "intent_analysis"
    ENTITY_EXTRACTION = "entity_extraction"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    CONTEXT_RETRIEVAL = "context_retrieval"
    RATE_LIMIT_CHECK = "rate_limit_check"
    TOOL_EXECUTION = "tool_execution"
    RESPONSE_GENERATION = "response_generation"

@dataclass
class ProcessingResult:
    """Result from a processing stage"""
    stage: ProcessingStage
    success: bool
    data: Any
    execution_time: float
    error: Optional[str] = None

@dataclass
class PipelineMetrics:
    """Pipeline performance metrics"""
    total_time: float
    stage_times: Dict[ProcessingStage, float]
    parallel_efficiency: float
    bottleneck_stage: Optional[ProcessingStage]
    success_rate: float

class AsyncProcessingPipeline:
    """Async processing pipeline for parallel message processing"""
    
    def __init__(self, max_workers: int = 10, timeout: float = 30.0):
        self.max_workers = max_workers
        self.timeout = timeout
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(max_workers)
        
        # Performance tracking
        self.metrics_history: List[PipelineMetrics] = []
        self.active_pipelines = 0
        
    async def process_message_parallel(
        self, 
        message: str, 
        user_id: int,
        context: Dict[str, Any] = None
    ) -> Tuple[Dict[str, Any], PipelineMetrics]:
        """Process message with parallel analysis stages"""
        
        start_time = time.time()
        self.active_pipelines += 1
        
        try:
            # Stage 1: Parallel analysis (can run concurrently)
            analysis_tasks = [
                self._run_stage(ProcessingStage.INTENT_ANALYSIS, self._analyze_intent, message, user_id),
                self._run_stage(ProcessingStage.ENTITY_EXTRACTION, self._extract_entities, message),
                self._run_stage(ProcessingStage.SENTIMENT_ANALYSIS, self._analyze_sentiment, message),
                self._run_stage(ProcessingStage.CONTEXT_RETRIEVAL, self._get_user_context, user_id),
                self._run_stage(ProcessingStage.RATE_LIMIT_CHECK, self._check_rate_limits, user_id)
            ]
            
            # Wait for all analysis stages to complete
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = self._process_stage_results(analysis_results)
            
            # Stage 2: Tool execution (depends on analysis results)
            if processed_results[ProcessingStage.INTENT_ANALYSIS].success:
                intent_data = processed_results[ProcessingStage.INTENT_ANALYSIS].data
                entities = processed_results[ProcessingStage.ENTITY_EXTRACTION].data if processed_results[ProcessingStage.ENTITY_EXTRACTION].success else []
                
                tool_result = await self._run_stage(
                    ProcessingStage.TOOL_EXECUTION,
                    self._execute_tools,
                    intent_data,
                    entities,
                    context or {}
                )
                processed_results[ProcessingStage.TOOL_EXECUTION] = tool_result
            
            # Stage 3: Response generation (depends on tool execution)
            if ProcessingStage.TOOL_EXECUTION in processed_results and processed_results[ProcessingStage.TOOL_EXECUTION].success:
                response_result = await self._run_stage(
                    ProcessingStage.RESPONSE_GENERATION,
                    self._generate_response,
                    processed_results
                )
                processed_results[ProcessingStage.RESPONSE_GENERATION] = response_result
            
            # Calculate metrics
            total_time = time.time() - start_time
            metrics = self._calculate_metrics(processed_results, total_time)
            
            # Combine results
            final_result = self._combine_results(processed_results)
            
            return final_result, metrics
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            raise
        finally:
            self.active_pipelines -= 1
    
    async def _run_stage(
        self, 
        stage: ProcessingStage, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> ProcessingResult:
        """Run a single processing stage with timing and error handling"""
        
        start_time = time.time()
        
        try:
            async with self.semaphore:  # Limit concurrent operations
                if asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout)
                else:
                    # Run CPU-bound tasks in thread pool
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(self.executor, func, *args, **kwargs)
                
                execution_time = time.time() - start_time
                
                return ProcessingResult(
                    stage=stage,
                    success=True,
                    data=result,
                    execution_time=execution_time
                )
                
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            logger.warning(f"Stage {stage.value} timed out after {self.timeout}s")
            
            return ProcessingResult(
                stage=stage,
                success=False,
                data=None,
                execution_time=execution_time,
                error=f"Timeout after {self.timeout}s"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Stage {stage.value} failed: {e}")
            
            return ProcessingResult(
                stage=stage,
                success=False,
                data=None,
                execution_time=execution_time,
                error=str(e)
            )
    
    def _process_stage_results(self, results: List[Any]) -> Dict[ProcessingStage, ProcessingResult]:
        """Process stage results and handle exceptions"""
        processed = {}
        
        stages = [
            ProcessingStage.INTENT_ANALYSIS,
            ProcessingStage.ENTITY_EXTRACTION,
            ProcessingStage.SENTIMENT_ANALYSIS,
            ProcessingStage.CONTEXT_RETRIEVAL,
            ProcessingStage.RATE_LIMIT_CHECK
        ]
        
        for i, result in enumerate(results):
            stage = stages[i]
            
            if isinstance(result, Exception):
                processed[stage] = ProcessingResult(
                    stage=stage,
                    success=False,
                    data=None,
                    execution_time=0.0,
                    error=str(result)
                )
            else:
                processed[stage] = result
        
        return processed
    
    def _calculate_metrics(
        self, 
        results: Dict[ProcessingStage, ProcessingResult], 
        total_time: float
    ) -> PipelineMetrics:
        """Calculate pipeline performance metrics"""
        
        stage_times = {stage: result.execution_time for stage, result in results.items()}
        
        # Calculate parallel efficiency
        sequential_time = sum(stage_times.values())
        parallel_efficiency = (sequential_time / total_time) if total_time > 0 else 0
        
        # Find bottleneck stage
        bottleneck_stage = max(stage_times.items(), key=lambda x: x[1])[0] if stage_times else None
        
        # Calculate success rate
        successful_stages = sum(1 for result in results.values() if result.success)
        success_rate = (successful_stages / len(results)) if results else 0
        
        metrics = PipelineMetrics(
            total_time=total_time,
            stage_times=stage_times,
            parallel_efficiency=parallel_efficiency,
            bottleneck_stage=bottleneck_stage,
            success_rate=success_rate
        )
        
        # Store metrics for analysis
        self.metrics_history.append(metrics)
        
        # Keep only last 100 metrics
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return metrics
    
    def _combine_results(self, results: Dict[ProcessingStage, ProcessingResult]) -> Dict[str, Any]:
        """Combine processing results into final response"""
        
        combined = {
            'success': True,
            'timestamp': time.time(),
            'processing_stages': {}
        }
        
        for stage, result in results.items():
            combined['processing_stages'][stage.value] = {
                'success': result.success,
                'execution_time': result.execution_time,
                'error': result.error
            }
            
            # Add stage data to combined result
            if result.success and result.data:
                if stage == ProcessingStage.INTENT_ANALYSIS:
                    combined['intent'] = result.data
                elif stage == ProcessingStage.ENTITY_EXTRACTION:
                    combined['entities'] = result.data
                elif stage == ProcessingStage.SENTIMENT_ANALYSIS:
                    combined['sentiment'] = result.data
                elif stage == ProcessingStage.CONTEXT_RETRIEVAL:
                    combined['context'] = result.data
                elif stage == ProcessingStage.TOOL_EXECUTION:
                    combined['tool_results'] = result.data
                elif stage == ProcessingStage.RESPONSE_GENERATION:
                    combined['response'] = result.data
        
        # Overall success depends on critical stages
        critical_stages = [ProcessingStage.INTENT_ANALYSIS, ProcessingStage.TOOL_EXECUTION]
        combined['success'] = all(
            results.get(stage, ProcessingResult(stage, False, None, 0)).success 
            for stage in critical_stages
        )
        
        return combined
    
    # Processing stage implementations
    async def _analyze_intent(self, message: str, user_id: int) -> Dict[str, Any]:
        """Analyze message intent"""
        # Import here to avoid circular imports
        from enhanced_nlp_patterns import analyze_enhanced_intent
        
        intent, confidence, entities = analyze_enhanced_intent(message)
        
        return {
            'intent': intent,
            'confidence': confidence,
            'entities': entities
        }
    
    async def _extract_entities(self, message: str) -> List[Dict[str, Any]]:
        """Extract entities from message"""
        # Simple entity extraction (can be enhanced with NER models)
        entities = []
        
        # Extract cryptocurrency symbols
        crypto_patterns = [
            r'\b(BTC|bitcoin)\b',
            r'\b(ETH|ethereum)\b',
            r'\b(SOL|solana)\b',
            r'\b(ADA|cardano)\b',
            r'\b(DOT|polkadot)\b'
        ]
        
        import re
        for pattern in crypto_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'type': 'cryptocurrency',
                    'value': match.upper(),
                    'confidence': 0.9
                })
        
        # Extract price values
        price_pattern = r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        price_matches = re.findall(price_pattern, message)
        for match in price_matches:
            entities.append({
                'type': 'price',
                'value': float(match.replace(',', '')),
                'confidence': 0.8
            })
        
        return entities
    
    async def _analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """Analyze message sentiment"""
        # Simple sentiment analysis (can be enhanced with ML models)
        positive_words = ['good', 'great', 'excellent', 'bullish', 'up', 'rise', 'gain']
        negative_words = ['bad', 'terrible', 'bearish', 'down', 'fall', 'loss', 'crash']
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = max(0.1, 0.5 - (negative_count - positive_count) * 0.1)
        else:
            sentiment = 'neutral'
            score = 0.5
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count
        }
    
    async def _get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Get user context and preferences"""
        # Mock user context (would come from database in production)
        return {
            'user_id': user_id,
            'preferences': {
                'risk_tolerance': 'medium',
                'preferred_assets': ['BTC', 'ETH'],
                'notification_settings': {'price_alerts': True}
            },
            'portfolio': {
                'BTC': 0.5,
                'ETH': 2.0,
                'SOL': 10.0,
                'ADA': 100.0
            },
            'recent_activity': []
        }
    
    async def _check_rate_limits(self, user_id: int) -> Dict[str, Any]:
        """Check user rate limits"""
        # Mock rate limit check (would use Redis in production)
        return {
            'rate_limit_ok': True,
            'requests_remaining': 95,
            'reset_time': time.time() + 3600
        }
    
    async def _execute_tools(
        self, 
        intent_data: Dict[str, Any], 
        entities: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute tools based on intent and entities"""
        # Import here to avoid circular imports
        from universal_intent_executor import execute_intent_with_tools
        
        intent = intent_data.get('intent', 'unknown')
        
        # Convert entities to expected format
        formatted_entities = []
        for entity in entities:
            if entity.get('type') == 'cryptocurrency':
                formatted_entities.append({
                    'type': 'cryptocurrency',
                    'value': entity['value']
                })
        
        # Execute tools
        result = await execute_intent_with_tools(intent, formatted_entities, context)
        
        return {
            'success': result.success,
            'data': result.data,
            'execution_time': result.execution_time,
            'tools_used': result.tool_calls_made
        }
    
    async def _generate_response(self, results: Dict[ProcessingStage, ProcessingResult]) -> Dict[str, Any]:
        """Generate final response based on all processing results"""
        
        response = {
            'type': 'success',
            'message': 'Request processed successfully',
            'data': {}
        }
        
        # Extract tool execution results
        if ProcessingStage.TOOL_EXECUTION in results:
            tool_result = results[ProcessingStage.TOOL_EXECUTION]
            if tool_result.success and tool_result.data:
                response['data'] = tool_result.data.get('data', {})
        
        # Add sentiment context
        if ProcessingStage.SENTIMENT_ANALYSIS in results:
            sentiment_result = results[ProcessingStage.SENTIMENT_ANALYSIS]
            if sentiment_result.success:
                response['sentiment'] = sentiment_result.data
        
        return response
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get pipeline performance statistics"""
        if not self.metrics_history:
            return {'message': 'No metrics available'}
        
        recent_metrics = self.metrics_history[-10:]  # Last 10 executions
        
        avg_total_time = sum(m.total_time for m in recent_metrics) / len(recent_metrics)
        avg_efficiency = sum(m.parallel_efficiency for m in recent_metrics) / len(recent_metrics)
        avg_success_rate = sum(m.success_rate for m in recent_metrics) / len(recent_metrics)
        
        # Find most common bottleneck
        bottlenecks = [m.bottleneck_stage for m in recent_metrics if m.bottleneck_stage]
        most_common_bottleneck = max(set(bottlenecks), key=bottlenecks.count) if bottlenecks else None
        
        return {
            'active_pipelines': self.active_pipelines,
            'total_executions': len(self.metrics_history),
            'avg_execution_time': f"{avg_total_time:.3f}s",
            'avg_parallel_efficiency': f"{avg_efficiency:.1%}",
            'avg_success_rate': f"{avg_success_rate:.1%}",
            'most_common_bottleneck': most_common_bottleneck.value if most_common_bottleneck else None,
            'max_workers': self.max_workers
        }
    
    async def shutdown(self):
        """Shutdown pipeline and cleanup resources"""
        self.executor.shutdown(wait=True)
        logger.info("Async processing pipeline shutdown complete")

# Global pipeline instance
async_pipeline = AsyncProcessingPipeline()

async def process_message_async(message: str, user_id: int, context: Dict[str, Any] = None) -> Tuple[Dict[str, Any], PipelineMetrics]:
    """Process message using async pipeline"""
    return await async_pipeline.process_message_parallel(message, user_id, context)

async def get_pipeline_stats() -> Dict[str, Any]:
    """Get pipeline performance statistics"""
    return async_pipeline.get_performance_stats()

async def cleanup_pipeline():
    """Cleanup pipeline resources"""
    await async_pipeline.shutdown()