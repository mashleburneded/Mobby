#!/usr/bin/env python3
"""
Whop Payment MCP Server - Industry-grade payment processing and license validation
Fully compliant with Model Context Protocol standards
"""

import asyncio
import logging
import json
import sys
import os
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# MCP imports
from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent
import aiohttp
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
app = FastMCP("Mobius Whop Payment Server")

class WhopPaymentProvider:
    """Industry-grade Whop payment processing provider"""
    
    def __init__(self):
        self.session = None
        self.base_url = "https://api.whop.com/api/v2"
        self.bearer_token = os.getenv('WHOP_BEARER_TOKEN', '')
        self.premium_retail_plan_id = os.getenv('WHOP_PREMIUM_RETAIL_PLAN_ID', 'plan_DR5ltY4c3QjQV')
        self.premium_corporate_plan_id = os.getenv('WHOP_PREMIUM_CORPORATE_PLAN_ID', 'plan_cpsmcglAaG7eI')
        
        # Payment status tracking
        self.payment_cache = {}
        self.license_cache = {}
        
        # Webhook verification
        self.webhook_secret = os.getenv('WHOP_WEBHOOK_SECRET', '')
        
    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'Authorization': f'Bearer {self.bearer_token}',
                    'Content-Type': 'application/json'
                }
            )
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers"""
        return {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }
    
    async def validate_license(self, membership_id: str, metadata: Dict = None) -> Dict[str, Any]:
        """Validate a Whop license key"""
        try:
            await self.initialize()
            
            # Check cache first
            cache_key = f"license_{membership_id}"
            if cache_key in self.license_cache:
                cached_data = self.license_cache[cache_key]
                if datetime.now() - cached_data['timestamp'] < timedelta(minutes=5):
                    logger.info(f"✅ License validation (cached): {membership_id}")
                    return cached_data['data']
            
            url = f"{self.base_url}/memberships/{membership_id}/validate_license"
            payload = {"metadata": metadata or {}}
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Cache the result
                    self.license_cache[cache_key] = {
                        'data': data,
                        'timestamp': datetime.now()
                    }
                    
                    logger.info(f"✅ License validated: {membership_id} - Status: {data.get('status', 'unknown')}")
                    
                    return {
                        "success": True,
                        "data": data,
                        "source": "Whop API",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ License validation failed: {response.status} - {error_text}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status}",
                        "details": error_text
                    }
                    
        except Exception as e:
            logger.error(f"❌ License validation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_membership_details(self, membership_id: str) -> Dict[str, Any]:
        """Get detailed membership information"""
        try:
            await self.initialize()
            
            url = f"{self.base_url}/memberships/{membership_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Membership details retrieved: {membership_id}")
                    
                    return {
                        "success": True,
                        "data": data,
                        "source": "Whop API",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Membership retrieval failed: {response.status}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status}",
                        "details": error_text
                    }
                    
        except Exception as e:
            logger.error(f"❌ Membership retrieval error: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_payments(self, limit: int = 10, page: int = 1) -> Dict[str, Any]:
        """List recent payments"""
        try:
            await self.initialize()
            
            url = f"{self.base_url}/payments"
            params = {
                'limit': min(limit, 100),
                'page': page
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Payments listed: {len(data.get('data', []))} payments")
                    
                    return {
                        "success": True,
                        "data": data,
                        "source": "Whop API",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Payment listing failed: {response.status}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status}",
                        "details": error_text
                    }
                    
        except Exception as e:
            logger.error(f"❌ Payment listing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get detailed payment information"""
        try:
            await self.initialize()
            
            url = f"{self.base_url}/payments/{payment_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Payment details retrieved: {payment_id}")
                    
                    return {
                        "success": True,
                        "data": data,
                        "source": "Whop API",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Payment retrieval failed: {response.status}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status}",
                        "details": error_text
                    }
                    
        except Exception as e:
            logger.error(f"❌ Payment retrieval error: {e}")
            return {"success": False, "error": str(e)}
    
    async def terminate_membership(self, membership_id: str) -> Dict[str, Any]:
        """Terminate a membership"""
        try:
            await self.initialize()
            
            url = f"{self.base_url}/memberships/{membership_id}/terminate"
            
            async with self.session.post(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Membership terminated: {membership_id}")
                    
                    # Clear from cache
                    cache_key = f"license_{membership_id}"
                    if cache_key in self.license_cache:
                        del self.license_cache[cache_key]
                    
                    return {
                        "success": True,
                        "data": data,
                        "source": "Whop API",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Membership termination failed: {response.status}")
                    return {
                        "success": False,
                        "error": f"API error: {response.status}",
                        "details": error_text
                    }
                    
        except Exception as e:
            logger.error(f"❌ Membership termination error: {e}")
            return {"success": False, "error": str(e)}
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Whop webhook signature"""
        try:
            if not self.webhook_secret:
                logger.warning("⚠️ No webhook secret configured")
                return False
            
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(f"sha256={expected_signature}", signature)
            
        except Exception as e:
            logger.error(f"❌ Webhook verification error: {e}")
            return False
    
    async def process_webhook(self, payload: Dict[str, Any], signature: str = None) -> Dict[str, Any]:
        """Process incoming Whop webhook"""
        try:
            # Verify signature if provided
            if signature:
                payload_str = json.dumps(payload, sort_keys=True)
                if not self.verify_webhook_signature(payload_str, signature):
                    return {
                        "success": False,
                        "error": "Invalid webhook signature"
                    }
            
            event_type = payload.get('type', 'unknown')
            data = payload.get('data', {})
            
            logger.info(f"🔔 Processing webhook: {event_type}")
            
            # Handle different webhook events
            if event_type == 'payment.completed':
                await self._handle_payment_completed(data)
            elif event_type == 'payment.failed':
                await self._handle_payment_failed(data)
            elif event_type == 'membership.created':
                await self._handle_membership_created(data)
            elif event_type == 'membership.terminated':
                await self._handle_membership_terminated(data)
            
            return {
                "success": True,
                "event_type": event_type,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Webhook processing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _handle_payment_completed(self, data: Dict[str, Any]):
        """Handle completed payment webhook"""
        payment_id = data.get('id')
        membership_id = data.get('membership')
        amount = data.get('final_amount', 0)
        
        logger.info(f"💰 Payment completed: {payment_id} - ${amount/100:.2f}")
        
        # Clear license cache to force refresh
        if membership_id:
            cache_key = f"license_{membership_id}"
            if cache_key in self.license_cache:
                del self.license_cache[cache_key]
    
    async def _handle_payment_failed(self, data: Dict[str, Any]):
        """Handle failed payment webhook"""
        payment_id = data.get('id')
        failure_message = data.get('failure_message', 'Unknown error')
        
        logger.warning(f"❌ Payment failed: {payment_id} - {failure_message}")
    
    async def _handle_membership_created(self, data: Dict[str, Any]):
        """Handle new membership webhook"""
        membership_id = data.get('id')
        plan_id = data.get('plan')
        
        logger.info(f"🎉 New membership created: {membership_id} - Plan: {plan_id}")
    
    async def _handle_membership_terminated(self, data: Dict[str, Any]):
        """Handle terminated membership webhook"""
        membership_id = data.get('id')
        
        logger.info(f"🛑 Membership terminated: {membership_id}")
        
        # Clear from cache
        cache_key = f"license_{membership_id}"
        if cache_key in self.license_cache:
            del self.license_cache[cache_key]

# Initialize provider
provider = WhopPaymentProvider()

# MCP Tool Definitions
@app.tool()
async def validate_license_key(membership_id: str, metadata: dict = None) -> dict:
    """
    Validate a Whop license key/membership
    
    Args:
        membership_id: The membership ID to validate
        metadata: Optional metadata to include in validation
    
    Returns:
        Validation result with license status and details
    """
    return await provider.validate_license(membership_id, metadata)

@app.tool()
async def get_membership_info(membership_id: str) -> dict:
    """
    Get detailed membership information
    
    Args:
        membership_id: The membership ID to retrieve
    
    Returns:
        Detailed membership information
    """
    return await provider.get_membership_details(membership_id)

@app.tool()
async def list_recent_payments(limit: int = 10, page: int = 1) -> dict:
    """
    List recent payments
    
    Args:
        limit: Number of payments to retrieve (max 100)
        page: Page number for pagination
    
    Returns:
        List of recent payments with pagination info
    """
    return await provider.list_payments(limit, page)

@app.tool()
async def get_payment_info(payment_id: str) -> dict:
    """
    Get detailed payment information
    
    Args:
        payment_id: The payment ID to retrieve
    
    Returns:
        Detailed payment information
    """
    return await provider.get_payment_details(payment_id)

@app.tool()
async def terminate_user_membership(membership_id: str) -> dict:
    """
    Terminate a user's membership
    
    Args:
        membership_id: The membership ID to terminate
    
    Returns:
        Termination result
    """
    return await provider.terminate_membership(membership_id)

@app.tool()
async def process_payment_webhook(payload: dict, signature: str = None) -> dict:
    """
    Process incoming Whop webhook
    
    Args:
        payload: The webhook payload
        signature: Optional webhook signature for verification
    
    Returns:
        Processing result
    """
    return await provider.process_webhook(payload, signature)

@app.tool()
async def check_premium_access(membership_id: str) -> dict:
    """
    Check if user has premium access (retail or corporate)
    
    Args:
        membership_id: The membership ID to check
    
    Returns:
        Premium access status and plan type
    """
    try:
        validation_result = await provider.validate_license(membership_id)
        
        if not validation_result.get("success"):
            return {
                "success": False,
                "has_premium": False,
                "error": validation_result.get("error", "Validation failed")
            }
        
        license_data = validation_result.get("data", {})
        plan_id = license_data.get("plan", "")
        status = license_data.get("status", "")
        valid = license_data.get("valid", False)
        
        # Check if user has premium access
        has_premium = (
            valid and 
            status in ["active", "trialing"] and
            plan_id in [provider.premium_retail_plan_id, provider.premium_corporate_plan_id]
        )
        
        plan_type = None
        if has_premium:
            if plan_id == provider.premium_retail_plan_id:
                plan_type = "retail"
            elif plan_id == provider.premium_corporate_plan_id:
                plan_type = "corporate"
        
        return {
            "success": True,
            "has_premium": has_premium,
            "plan_type": plan_type,
            "plan_id": plan_id,
            "status": status,
            "valid": valid,
            "license_data": license_data
        }
        
    except Exception as e:
        logger.error(f"❌ Premium access check error: {e}")
        return {
            "success": False,
            "has_premium": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Whop Payment MCP Server")
    parser.add_argument("--port", type=int, default=8014, help="Port to run the server on")
    args = parser.parse_args()
    
    # Server startup
    logger.info("🚀 Whop Payment MCP Server starting up...")
    logger.info("💳 Available tools: validate_license_key, get_membership_info, list_recent_payments, get_payment_info, terminate_user_membership, process_payment_webhook, check_premium_access")
    
    # Run the server using FastMCP's built-in runner
    logger.info(f"💰 Starting REAL Whop Payment MCP Server on port {args.port}")
    
    try:
        # Use uvicorn with FastMCP's streamable HTTP app
        import uvicorn
        http_app = app.streamable_http_app()
        uvicorn.run(http_app, host="0.0.0.0", port=args.port, log_level="info")
    except KeyboardInterrupt:
        logger.info("🛑 Whop Payment MCP Server shutting down...")
    finally:
        # Cleanup
        import asyncio
        asyncio.run(provider.close())