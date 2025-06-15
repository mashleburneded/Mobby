# src/mcp_background_processor.py - Background MCP Processing to Prevent Chat Flooding
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque
import json

from mcp_client import mcp_client
from mcp_ai_orchestrator import ai_orchestrator

logger = logging.getLogger(__name__)

@dataclass
class ProcessingJob:
    """Background processing job"""
    job_id: str
    user_id: int
    job_type: str
    parameters: dict
    callback: Optional[Callable] = None
    priority: int = 1  # 1=low, 2=medium, 3=high
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, processing, completed, failed
    result: Optional[dict] = None
    error: Optional[str] = None

@dataclass
class UserRateLimit:
    """User rate limiting"""
    user_id: int
    requests_count: int = 0
    last_request: datetime = field(default_factory=datetime.now)
    window_start: datetime = field(default_factory=datetime.now)

class MCPBackgroundProcessor:
    """Background processor for MCP operations to prevent chat flooding"""

    def __init__(self):
        self.job_queue: deque = deque()
        self.processing_jobs: Dict[str, ProcessingJob] = {}
        self.completed_jobs: Dict[str, ProcessingJob] = {}
        self.user_rate_limits: Dict[int, UserRateLimit] = {}
        self.worker_tasks: List[asyncio.Task] = []
        self.running = False
        self.max_concurrent_jobs = 5
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max_requests = 10  # per window

    async def initialize(self):
        """Initialize background processor"""
        try:
            # Start worker tasks
            for i in range(self.max_concurrent_jobs):
                task = asyncio.create_task(self._worker(f"worker-{i}"))
                self.worker_tasks.append(task)

            # Start cleanup task
            cleanup_task = asyncio.create_task(self._cleanup_worker())
            self.worker_tasks.append(cleanup_task)

            self.running = True
            logger.info(f"🔄 Background processor initialized with {self.max_concurrent_jobs} workers")

        except Exception as e:
            logger.error(f"❌ Background processor initialization failed: {e}")

    async def submit_job(self, user_id: int, job_type: str, parameters: dict,
                        callback: Optional[Callable] = None, priority: int = 1) -> Optional[str]:
        """Submit job for background processing with rate limiting"""
        try:
            # Security: Check rate limits
            if not await self._check_rate_limit(user_id):
                logger.warning(f"🔒 Rate limit exceeded for user {user_id}")
                return None

            # Security: Validate job type
            if not self._validate_job_type(job_type):
                logger.warning(f"🔒 Invalid job type: {job_type}")
                return None

            # Security: Sanitize parameters
            sanitized_params = self._sanitize_parameters(parameters)

            # Create job
            job_id = f"{user_id}_{job_type}_{datetime.now().timestamp()}"
            job = ProcessingJob(
                job_id=job_id,
                user_id=user_id,
                job_type=job_type,
                parameters=sanitized_params,
                callback=callback,
                priority=priority
            )

            # Add to queue (higher priority first)
            if priority >= 3:
                self.job_queue.appendleft(job)
            else:
                self.job_queue.append(job)

            logger.info(f"✅ Job submitted: {job_id} (priority: {priority})")
            return job_id

        except Exception as e:
            logger.error(f"❌ Job submission failed: {e}")
            return None

    async def _check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        current_time = datetime.now()

        if user_id not in self.user_rate_limits:
            self.user_rate_limits[user_id] = UserRateLimit(user_id=user_id)
            return True

        rate_limit = self.user_rate_limits[user_id]

        # Reset window if needed
        if (current_time - rate_limit.window_start).total_seconds() >= self.rate_limit_window:
            rate_limit.requests_count = 0
            rate_limit.window_start = current_time

        # Check limit
        if rate_limit.requests_count >= self.rate_limit_max_requests:
            return False

        # Update counters
        rate_limit.requests_count += 1
        rate_limit.last_request = current_time

        return True

    def _validate_job_type(self, job_type: str) -> bool:
        """Validate job type for security"""
        allowed_job_types = [
            "market_analysis", "social_sentiment", "wallet_analysis",
            "price_alert_check", "news_summary", "research_query",
            "portfolio_update", "cross_chain_analysis", "defi_analysis"
        ]
        return job_type in allowed_job_types

    def _sanitize_parameters(self, parameters: dict) -> dict:
        """Sanitize job parameters for security"""
        if not isinstance(parameters, dict):
            return {}

        sanitized = {}
        for key, value in parameters.items():
            if isinstance(value, (str, int, float, bool)):
                if isinstance(value, str):
                    # Limit string length and sanitize
                    value = value[:500]
                    value = ''.join(c for c in value if c.isprintable())
                sanitized[key] = value
            elif isinstance(value, list):
                # Limit list size and sanitize elements
                value = value[:50]
                sanitized[key] = [str(item)[:100] for item in value if isinstance(item, (str, int, float))]

        return sanitized

    async def _worker(self, worker_name: str):
        """Background worker to process jobs"""
        logger.info(f"🔄 Worker {worker_name} started")

        while self.running:
            try:
                # Get next job
                if not self.job_queue:
                    await asyncio.sleep(1)
                    continue

                job = self.job_queue.popleft()

                # Start processing
                job.status = "processing"
                job.started_at = datetime.now()
                self.processing_jobs[job.job_id] = job

                logger.info(f"🔄 {worker_name} processing job {job.job_id}")

                # Process the job
                result = await self._process_job(job)

                # Complete job
                job.status = "completed" if result.get("success") else "failed"
                job.completed_at = datetime.now()
                job.result = result

                # Move to completed jobs
                self.completed_jobs[job.job_id] = job
                if job.job_id in self.processing_jobs:
                    del self.processing_jobs[job.job_id]

                # Call callback if provided (non-blocking)
                if job.callback:
                    try:
                        asyncio.create_task(job.callback(job))
                    except Exception as e:
                        logger.error(f"❌ Callback failed for job {job.job_id}: {e}")

                logger.info(f"✅ {worker_name} completed job {job.job_id}")

            except Exception as e:
                logger.error(f"❌ Worker {worker_name} error: {e}")
                if 'job' in locals():
                    job.status = "failed"
                    job.error = str(e)
                    job.completed_at = datetime.now()

                await asyncio.sleep(5)  # Wait before retrying

    async def _process_job(self, job: ProcessingJob) -> dict:
        """Process individual job based on type"""
        try:
            if job.job_type == "market_analysis":
                return await self._process_market_analysis(job)
            elif job.job_type == "social_sentiment":
                return await self._process_social_sentiment(job)
            elif job.job_type == "wallet_analysis":
                return await self._process_wallet_analysis(job)
            elif job.job_type == "research_query":
                return await self._process_research_query(job)
            elif job.job_type == "cross_chain_analysis":
                return await self._process_cross_chain_analysis(job)
            elif job.job_type == "defi_analysis":
                return await self._process_defi_analysis(job)
            else:
                return {"success": False, "error": "Unknown job type"}

        except Exception as e:
            logger.error(f"❌ Job processing failed: {e}")
            return {"success": False, "error": str(e)}

    async def _process_market_analysis(self, job: ProcessingJob) -> dict:
        """Process market analysis job"""
        symbols = job.parameters.get("symbols", ["BTC", "ETH"])

        # Get market data from MCP
        market_data = await mcp_client.call_tool("financial", "get_crypto_prices", {"symbols": symbols})
        defi_data = await mcp_client.call_tool("financial", "get_defi_protocols", {})

        # Generate AI analysis
        ai_response = await ai_orchestrator.generate_enhanced_response(
            f"Analyze market conditions for {', '.join(symbols)}",
            {"market_data": market_data, "defi_data": defi_data}
        )

        return {
            "success": True,
            "type": "market_analysis",
            "data": {
                "market_data": market_data,
                "defi_data": defi_data,
                "ai_analysis": ai_response
            }
        }

    async def _process_social_sentiment(self, job: ProcessingJob) -> dict:
        """Process social sentiment analysis job"""
        topic = job.parameters.get("topic", "crypto")

        # Get sentiment data from MCP
        sentiment_data = await mcp_client.call_tool("social", "twitter_sentiment", {"topic": topic})

        return {
            "success": True,
            "type": "social_sentiment",
            "data": sentiment_data
        }

    async def _process_wallet_analysis(self, job: ProcessingJob) -> dict:
        """Process wallet analysis job"""
        address = job.parameters.get("address", "")
        chains = job.parameters.get("chains", ["ethereum"])

        results = {}
        for chain in chains:
            tool_name = f"{chain}_analysis"
            chain_data = await mcp_client.call_tool("blockchain", tool_name, {"address": address})
            results[chain] = chain_data

        return {
            "success": True,
            "type": "wallet_analysis",
            "data": results
        }

    async def _process_research_query(self, job: ProcessingJob) -> dict:
        """Process research query job"""
        query = job.parameters.get("query", "")

        # Get web research data
        web_data = await mcp_client.call_tool("web", "web_search", {"query": query})

        # Generate AI response
        ai_response = await ai_orchestrator.generate_enhanced_response(query, {"web_data": web_data})

        return {
            "success": True,
            "type": "research_query",
            "data": {
                "web_data": web_data,
                "ai_response": ai_response
            }
        }

    async def _process_cross_chain_analysis(self, job: ProcessingJob) -> dict:
        """Process cross-chain analysis job"""
        # Get cross-chain data
        cross_chain_data = await mcp_client.call_tool("blockchain", "cross_chain_tracking", {})

        return {
            "success": True,
            "type": "cross_chain_analysis",
            "data": cross_chain_data
        }

    async def _process_defi_analysis(self, job: ProcessingJob) -> dict:
        """Process DeFi analysis job"""
        protocols = job.parameters.get("protocols", [])

        # Get DeFi data
        defi_data = await mcp_client.call_tool("financial", "defi_protocols", {"protocols": protocols})

        return {
            "success": True,
            "type": "defi_analysis",
            "data": defi_data
        }

    async def _cleanup_worker(self):
        """Cleanup completed jobs periodically"""
        while self.running:
            try:
                current_time = datetime.now()
                cutoff_time = current_time - timedelta(hours=1)  # Keep jobs for 1 hour

                # Clean up old completed jobs
                jobs_to_remove = [
                    job_id for job_id, job in self.completed_jobs.items()
                    if job.completed_at and job.completed_at < cutoff_time
                ]

                for job_id in jobs_to_remove:
                    del self.completed_jobs[job_id]

                if jobs_to_remove:
                    logger.info(f"🧹 Cleaned up {len(jobs_to_remove)} old jobs")

                # Clean up old rate limit data
                rate_limit_cutoff = current_time - timedelta(minutes=5)
                users_to_clean = [
                    user_id for user_id, rate_limit in self.user_rate_limits.items()
                    if rate_limit.last_request < rate_limit_cutoff
                ]

                for user_id in users_to_clean:
                    del self.user_rate_limits[user_id]

                await asyncio.sleep(300)  # Run cleanup every 5 minutes

            except Exception as e:
                logger.error(f"❌ Cleanup worker error: {e}")
                await asyncio.sleep(60)

    async def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get job status"""
        # Check processing jobs
        if job_id in self.processing_jobs:
            job = self.processing_jobs[job_id]
            return {
                "job_id": job_id,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None
            }

        # Check completed jobs
        if job_id in self.completed_jobs:
            job = self.completed_jobs[job_id]
            return {
                "job_id": job_id,
                "status": job.status,
                "created_at": job.created_at.isoformat(),
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "result": job.result,
                "error": job.error
            }

        return None

    async def get_user_jobs(self, user_id: int) -> dict:
        """Get user's job statistics"""
        processing_count = len([job for job in self.processing_jobs.values() if job.user_id == user_id])
        completed_count = len([job for job in self.completed_jobs.values() if job.user_id == user_id])

        rate_limit = self.user_rate_limits.get(user_id)

        return {
            "user_id": user_id,
            "processing_jobs": processing_count,
            "completed_jobs": completed_count,
            "rate_limit": {
                "requests_used": rate_limit.requests_count if rate_limit else 0,
                "requests_limit": self.rate_limit_max_requests,
                "window_seconds": self.rate_limit_window
            }
        }

    async def stop(self):
        """Stop background processor"""
        self.running = False

        for task in self.worker_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("🔄 Background processor stopped")

# Global background processor instance
background_processor = MCPBackgroundProcessor()

async def initialize_background_processor():
    """Initialize background processor"""
    await background_processor.initialize()
    logger.info("🔄 Background processor ready!")

# Convenience functions
async def submit_background_job(user_id: int, job_type: str, parameters: dict,
                               callback: Optional[Callable] = None, priority: int = 1) -> Optional[str]:
    """Submit job for background processing"""
    return await background_processor.submit_job(user_id, job_type, parameters, callback, priority)

async def get_job_result(job_id: str) -> Optional[dict]:
    """Get job result"""
    return await background_processor.get_job_status(job_id)