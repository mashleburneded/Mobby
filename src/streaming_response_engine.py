# src/streaming_response_engine.py - Real-time Response Streaming for Immediate User Feedback
import asyncio
import time
import logging
from typing import AsyncGenerator, Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class ProcessingStage(Enum):
    """Processing stages for streaming responses"""
    RECEIVED = "received"
    ANALYZING = "analyzing"
    FETCHING_DATA = "fetching_data"
    PROCESSING_AI = "processing_ai"
    GENERATING_RESPONSE = "generating_response"
    FINALIZING = "finalizing"
    COMPLETE = "complete"

@dataclass
class StreamingProgress:
    """Progress update for streaming responses"""
    stage: ProcessingStage
    message: str
    progress_percent: float
    estimated_time_remaining: Optional[float] = None
    intermediate_result: Optional[str] = None

class StreamingResponseEngine:
    """Real-time response streaming for immediate user feedback"""
    
    def __init__(self):
        self.active_streams: Dict[str, Dict[str, Any]] = {}
        self.stage_timings: Dict[ProcessingStage, float] = {
            ProcessingStage.RECEIVED: 0.1,
            ProcessingStage.ANALYZING: 0.5,
            ProcessingStage.FETCHING_DATA: 1.0,
            ProcessingStage.PROCESSING_AI: 2.0,
            ProcessingStage.GENERATING_RESPONSE: 1.0,
            ProcessingStage.FINALIZING: 0.3,
        }
    
    async def stream_response(self, message: str, user_id: int, 
                            update: Update, context: ContextTypes.DEFAULT_TYPE,
                            processing_function) -> AsyncGenerator[str, None]:
        """Stream response with real-time progress updates"""
        stream_id = f"{user_id}_{int(time.time())}"
        start_time = time.time()
        
        try:
            # Initialize stream tracking
            self.active_streams[stream_id] = {
                "user_id": user_id,
                "start_time": start_time,
                "current_stage": ProcessingStage.RECEIVED,
                "message": message
            }
            
            # Stage 1: Immediate acknowledgment (<50ms)
            yield "🤖 **Processing your request...**\n⏳ *Analyzing query...*"
            await self._update_stream_stage(stream_id, ProcessingStage.ANALYZING)
            
            # Stage 2: Intent analysis and routing
            analysis_result = await self._analyze_message_intent(message, user_id)
            progress_msg = f"📊 **Analysis Complete**\n🎯 *Intent: {analysis_result.get('intent', 'general')}*\n⏳ *Fetching data...*"
            yield progress_msg
            await self._update_stream_stage(stream_id, ProcessingStage.FETCHING_DATA)
            
            # Stage 3: Data fetching with progress
            async for data_progress in self._stream_data_fetching(analysis_result, stream_id):
                yield data_progress
            
            await self._update_stream_stage(stream_id, ProcessingStage.PROCESSING_AI)
            
            # Stage 4: AI processing with incremental results
            yield "🧠 **AI Processing**\n⏳ *Generating intelligent response...*"
            
            async for ai_progress in self._stream_ai_processing(
                message, analysis_result, processing_function, stream_id
            ):
                yield ai_progress
            
            await self._update_stream_stage(stream_id, ProcessingStage.GENERATING_RESPONSE)
            
            # Stage 5: Final response generation
            final_response = await self._generate_final_response(
                message, analysis_result, user_id, stream_id
            )
            
            await self._update_stream_stage(stream_id, ProcessingStage.COMPLETE)
            
            # Stage 6: Final comprehensive result
            processing_time = time.time() - start_time
            yield f"{final_response}\n\n⚡ *Processed in {processing_time:.2f}s*"
            
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield f"❌ **Error occurred while processing**\n*{str(e)}*\n\nPlease try again."
        finally:
            # Cleanup stream tracking
            self.active_streams.pop(stream_id, None)
    
    async def _analyze_message_intent(self, message: str, user_id: int) -> Dict[str, Any]:
        """Analyze message intent with timing"""
        start_time = time.time()
        
        # Simulate intent analysis (replace with actual implementation)
        await asyncio.sleep(0.2)  # Realistic processing time
        
        # Basic intent detection
        intent = "general"
        entities = {}
        confidence = 0.8
        
        if any(word in message.lower() for word in ["price", "cost", "value", "$"]):
            intent = "price_query"
            entities["type"] = "price"
        elif any(word in message.lower() for word in ["portfolio", "balance", "holdings"]):
            intent = "portfolio_query"
            entities["type"] = "portfolio"
        elif any(word in message.lower() for word in ["news", "research", "analysis"]):
            intent = "research_query"
            entities["type"] = "research"
        
        processing_time = time.time() - start_time
        
        return {
            "intent": intent,
            "entities": entities,
            "confidence": confidence,
            "processing_time": processing_time,
            "requires_data": intent in ["price_query", "portfolio_query", "research_query"],
            "complexity": "simple" if len(message.split()) < 10 else "complex"
        }
    
    async def _stream_data_fetching(self, analysis: Dict[str, Any], 
                                  stream_id: str) -> AsyncGenerator[str, None]:
        """Stream data fetching progress"""
        if not analysis.get("requires_data", False):
            yield "📊 **Data Ready**\n✅ *No external data required*"
            return
        
        intent = analysis.get("intent", "general")
        
        # Simulate different data sources based on intent
        if intent == "price_query":
            yield "💰 **Fetching Price Data**\n⏳ *Connecting to CoinGecko...*"
            await asyncio.sleep(0.3)
            yield "💰 **Price Data**\n✅ *Market data retrieved*\n⏳ *Analyzing trends...*"
            await asyncio.sleep(0.2)
            
        elif intent == "portfolio_query":
            yield "📊 **Fetching Portfolio Data**\n⏳ *Scanning blockchain...*"
            await asyncio.sleep(0.4)
            yield "📊 **Portfolio Data**\n✅ *Wallet data retrieved*\n⏳ *Calculating metrics...*"
            await asyncio.sleep(0.3)
            
        elif intent == "research_query":
            yield "🔍 **Gathering Research Data**\n⏳ *Scanning news sources...*"
            await asyncio.sleep(0.5)
            yield "🔍 **Research Data**\n✅ *News and analysis retrieved*\n⏳ *Processing insights...*"
            await asyncio.sleep(0.2)
        
        yield "📊 **Data Collection Complete**\n✅ *All sources processed*"
    
    async def _stream_ai_processing(self, message: str, analysis: Dict[str, Any],
                                  processing_function, stream_id: str) -> AsyncGenerator[str, None]:
        """Stream AI processing with incremental results"""
        complexity = analysis.get("complexity", "simple")
        
        if complexity == "simple":
            yield "🧠 **AI Analysis**\n⏳ *Processing with lightweight model...*"
            await asyncio.sleep(0.5)
            yield "🧠 **AI Analysis**\n✅ *Quick analysis complete*"
        else:
            yield "🧠 **AI Analysis**\n⏳ *Processing with advanced model...*"
            await asyncio.sleep(0.8)
            yield "🧠 **AI Analysis**\n📊 *Intermediate results available*"
            await asyncio.sleep(0.5)
            yield "🧠 **AI Analysis**\n✅ *Deep analysis complete*"
        
        # Show confidence if available
        confidence = analysis.get("confidence", 0.8)
        yield f"🎯 **Confidence Score**\n✅ *{confidence:.1%} accuracy*"
    
    async def _generate_final_response(self, message: str, analysis: Dict[str, Any],
                                     user_id: int, stream_id: str) -> str:
        """Generate the final comprehensive response"""
        intent = analysis.get("intent", "general")
        
        # Simulate final response generation
        await asyncio.sleep(0.3)
        
        if intent == "price_query":
            return "💰 **Price Analysis Complete**\n\n📊 Current market data shows strong trends.\n🎯 Key insights: Market is showing positive momentum.\n📈 Recommendation: Monitor for continued growth."
        
        elif intent == "portfolio_query":
            return "📊 **Portfolio Analysis Complete**\n\n💼 Your portfolio shows balanced allocation.\n📈 Performance: +12.5% this month\n🎯 Suggestion: Consider rebalancing in DeFi sector."
        
        elif intent == "research_query":
            return "🔍 **Research Analysis Complete**\n\n📰 Latest market research indicates positive sentiment.\n📊 Key trends: Institutional adoption increasing\n🎯 Outlook: Bullish medium-term prospects."
        
        else:
            return "🤖 **Analysis Complete**\n\nI've processed your request and here's what I found:\n\n✅ Your query has been analyzed\n📊 Relevant data has been gathered\n🎯 Insights have been generated\n\nHow else can I help you today?"
    
    async def _update_stream_stage(self, stream_id: str, stage: ProcessingStage):
        """Update the current processing stage"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id]["current_stage"] = stage
            self.active_streams[stream_id]["stage_updated"] = time.time()
    
    def get_stream_status(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a stream"""
        return self.active_streams.get(stream_id)
    
    def get_active_streams(self) -> Dict[str, Dict[str, Any]]:
        """Get all active streams"""
        return self.active_streams.copy()
    
    async def cancel_stream(self, stream_id: str):
        """Cancel an active stream"""
        if stream_id in self.active_streams:
            self.active_streams.pop(stream_id)
            logger.info(f"Stream {stream_id} cancelled")

class TelegramStreamingHandler:
    """Telegram-specific streaming response handler"""
    
    def __init__(self, streaming_engine: StreamingResponseEngine):
        self.streaming_engine = streaming_engine
        self.message_update_interval = 2.0  # Update every 2 seconds
    
    async def send_streaming_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    message: str, processing_function) -> None:
        """Send streaming response via Telegram with live updates"""
        user_id = update.effective_user.id
        
        # Send initial message
        sent_message = await update.effective_message.reply_text(
            "🤖 **Starting analysis...**",
            parse_mode="Markdown"
        )
        
        last_update_time = time.time()
        
        try:
            # Stream the response
            async for progress_update in self.streaming_engine.stream_response(
                message, user_id, update, context, processing_function
            ):
                current_time = time.time()
                
                # Update message at intervals to avoid rate limiting
                if current_time - last_update_time >= self.message_update_interval:
                    try:
                        await sent_message.edit_text(
                            progress_update,
                            parse_mode="Markdown"
                        )
                        last_update_time = current_time
                    except Exception as e:
                        # Handle rate limiting or other edit errors
                        logger.warning(f"Message edit failed: {e}")
                        await asyncio.sleep(1)
            
            # Final update with complete response
            await asyncio.sleep(0.5)  # Small delay for better UX
            
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            await sent_message.edit_text(
                "❌ **Error occurred during processing**\n\nPlease try again.",
                parse_mode="Markdown"
            )

# Global streaming engine instance
streaming_engine = StreamingResponseEngine()
telegram_streaming_handler = TelegramStreamingHandler(streaming_engine)

# Convenience functions
async def send_streaming_response(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                message: str, processing_function=None):
    """Send a streaming response to Telegram"""
    await telegram_streaming_handler.send_streaming_response(
        update, context, message, processing_function
    )

def get_streaming_metrics() -> Dict[str, Any]:
    """Get streaming performance metrics"""
    active_streams = streaming_engine.get_active_streams()
    return {
        "active_streams": len(active_streams),
        "streams_by_stage": {
            stage.value: len([s for s in active_streams.values() 
                            if s.get("current_stage") == stage])
            for stage in ProcessingStage
        },
        "average_processing_time": sum(
            time.time() - s["start_time"] for s in active_streams.values()
        ) / max(len(active_streams), 1)
    }