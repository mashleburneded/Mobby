"""
Enhanced Whop Integration for Möbius AI Assistant
Handles license key validation, subscription management, and tier access control
"""

import os
import logging
import aiohttp
import asyncio
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from config import config
from user_db import get_user_property, set_user_property

logger = logging.getLogger(__name__)

@dataclass
class WhopSubscription:
    """Whop subscription data"""
    id: str
    status: str
    plan_id: str
    plan_name: str
    user_id: str
    expires_at: Optional[datetime]
    created_at: datetime
    metadata: Dict[str, Any]
    tier: str  # free, retail, corporate

@dataclass
class LicenseValidationResult:
    """Result of license validation"""
    is_valid: bool
    subscription: Optional[WhopSubscription]
    error_message: Optional[str]
    tier: str
    features: List[str]

class EnhancedWhopClient:
    """Enhanced Whop API client with comprehensive license management"""
    
    def __init__(self):
        self.bearer_token = config.get("WHOP_BEARER_TOKEN")
        self.base_url = "https://api.whop.com"
        self.webhook_secret = config.get("WHOP_WEBHOOK_SECRET")
        
        # Plan ID mappings
        self.plan_mappings = {
            "plan_retail": "retail",
            "plan_corporate": "corporate",
            # Add your actual Whop plan IDs here
        }
        
        # Tier features
        self.tier_features = {
            "free": [
                "portfolio_basic",
                "basic_portfolio",
                "price_alerts_3",
                "basic_research",
                "wallet_creation",
                "balance_check"
            ],
            "retail": [
                "portfolio_basic",
                "portfolio_advanced",
                "advanced_portfolio",
                "price_alerts_50",
                "advanced_research",
                "wallet_management",
                "basic_trading",
                "defi_analytics",
                "social_trading"
            ],
            "corporate": [
                "portfolio_basic",
                "portfolio_advanced",
                "api_access",
                "enterprise_portfolio",
                "unlimited_alerts",
                "institutional_research",
                "advanced_trading",
                "cross_chain_analytics",
                "api_access",
                "priority_support",
                "custom_integrations"
            ]
        }
        
        # Cache for validated licenses
        self.license_cache: Dict[str, LicenseValidationResult] = {}
        self.cache_ttl = timedelta(hours=1)  # Cache for 1 hour
        
        if not self.bearer_token:
            logger.warning("WHOP_BEARER_TOKEN not configured - license validation will be disabled")
    
    async def validate_license_key(self, license_key: str, user_id: int) -> LicenseValidationResult:
        """
        Validate a license key and return comprehensive validation result
        
        Args:
            license_key: The license key to validate
            user_id: Telegram user ID
            
        Returns:
            LicenseValidationResult with validation details
        """
        
        # Check cache first
        cache_key = f"{license_key}_{user_id}"
        if cache_key in self.license_cache:
            cached_result = self.license_cache[cache_key]
            # Check if cache is still valid
            if hasattr(cached_result, 'cached_at'):
                if datetime.now() - cached_result.cached_at < self.cache_ttl:
                    return cached_result
        
        if not self.bearer_token:
            return LicenseValidationResult(
                is_valid=False,
                subscription=None,
                error_message="License validation not configured",
                tier="free",
                features=self.tier_features["free"]
            )
        
        try:
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                # Try multiple validation methods
                subscription = await self._validate_via_rest_api(session, license_key, headers)
                
                if not subscription:
                    subscription = await self._validate_via_graphql(session, license_key, headers)
                
                if not subscription:
                    subscription = await self._validate_via_webhook_verification(license_key, user_id)
                
                if subscription:
                    # Determine tier from plan
                    tier = self._determine_tier_from_plan(subscription.plan_id, subscription.plan_name)
                    subscription.tier = tier
                    
                    # Store validated license for user
                    await self._store_user_license(user_id, license_key, subscription)
                    
                    result = LicenseValidationResult(
                        is_valid=True,
                        subscription=subscription,
                        error_message=None,
                        tier=tier,
                        features=self.tier_features.get(tier, self.tier_features["free"])
                    )
                else:
                    result = LicenseValidationResult(
                        is_valid=False,
                        subscription=None,
                        error_message="Invalid or expired license key",
                        tier="free",
                        features=self.tier_features["free"]
                    )
                
                # Cache result
                result.cached_at = datetime.now()
                self.license_cache[cache_key] = result
                
                return result
                
        except Exception as e:
            logger.error(f"Error validating license key: {e}")
            return LicenseValidationResult(
                is_valid=False,
                subscription=None,
                error_message=f"Validation error: {str(e)}",
                tier="free",
                features=self.tier_features["free"]
            )
    
    async def _validate_via_rest_api(
        self, 
        session: aiohttp.ClientSession, 
        license_key: str, 
        headers: Dict[str, str]
    ) -> Optional[WhopSubscription]:
        """Validate license using REST API"""
        try:
            url = f"{self.base_url}/api/v2/licenses/{license_key}"
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"License validation successful via REST API: {license_key[:8]}...")
                    return self._parse_subscription(data)
                elif response.status == 404:
                    logger.debug(f"License not found via REST API: {license_key[:8]}...")
                else:
                    error_text = await response.text()
                    logger.warning(f"REST API error: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.warning(f"REST API validation failed: {e}")
        
        return None
    
    async def _validate_via_graphql(
        self, 
        session: aiohttp.ClientSession, 
        license_key: str, 
        headers: Dict[str, str]
    ) -> Optional[WhopSubscription]:
        """Validate license using GraphQL"""
        try:
            query = """
            query GetLicense($licenseKey: String!) {
                license(key: $licenseKey) {
                    id
                    status
                    plan {
                        id
                        name
                    }
                    user {
                        id
                        email
                    }
                    expiresAt
                    createdAt
                    metadata
                }
            }
            """
            
            variables = {"licenseKey": license_key}
            
            url = f"{self.base_url}/graphql"
            payload = {
                "query": query,
                "variables": variables
            }
            
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "data" in data and data["data"]["license"]:
                        logger.info(f"License validation successful via GraphQL: {license_key[:8]}...")
                        return self._parse_graphql_subscription(data["data"]["license"])
                    else:
                        logger.debug(f"License not found via GraphQL: {license_key[:8]}...")
                else:
                    error_text = await response.text()
                    logger.warning(f"GraphQL error: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.warning(f"GraphQL validation failed: {e}")
        
        return None
    
    async def _validate_via_webhook_verification(self, license_key: str, user_id: int) -> Optional[WhopSubscription]:
        """Validate license using stored webhook data"""
        try:
            # Check if we have stored license data from webhooks
            stored_licenses = get_user_property(user_id, "whop_licenses") or {}
            
            if license_key in stored_licenses:
                license_data = stored_licenses[license_key]
                
                # Check if license is still valid
                if license_data.get("status") == "active":
                    expires_at = license_data.get("expires_at")
                    if not expires_at or datetime.fromisoformat(expires_at) > datetime.now():
                        logger.info(f"License validation successful via webhook data: {license_key[:8]}...")
                        return WhopSubscription(
                            id=license_data["id"],
                            status=license_data["status"],
                            plan_id=license_data["plan_id"],
                            plan_name=license_data.get("plan_name", "Unknown"),
                            user_id=license_data["user_id"],
                            expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
                            created_at=datetime.fromisoformat(license_data["created_at"]),
                            metadata=license_data.get("metadata", {}),
                            tier="free"  # Will be determined later
                        )
                        
        except Exception as e:
            logger.warning(f"Webhook validation failed: {e}")
        
        return None
    
    def _parse_subscription(self, data: Dict[str, Any]) -> WhopSubscription:
        """Parse subscription data from REST API response"""
        return WhopSubscription(
            id=data["id"],
            status=data["status"],
            plan_id=data["plan"]["id"],
            plan_name=data["plan"].get("name", "Unknown"),
            user_id=data["user"]["id"],
            expires_at=datetime.fromisoformat(data["expiresAt"]) if data.get("expiresAt") else None,
            created_at=datetime.fromisoformat(data["createdAt"]),
            metadata=data.get("metadata", {}),
            tier="free"  # Will be determined later
        )
    
    def _parse_graphql_subscription(self, data: Dict[str, Any]) -> WhopSubscription:
        """Parse subscription data from GraphQL response"""
        return WhopSubscription(
            id=data["id"],
            status=data["status"],
            plan_id=data["plan"]["id"],
            plan_name=data["plan"].get("name", "Unknown"),
            user_id=data["user"]["id"],
            expires_at=datetime.fromisoformat(data["expiresAt"]) if data.get("expiresAt") else None,
            created_at=datetime.fromisoformat(data["createdAt"]),
            metadata=data.get("metadata", {}),
            tier="free"  # Will be determined later
        )
    
    def _determine_tier_from_plan(self, plan_id: str, plan_name: str) -> str:
        """Determine user tier from plan information"""
        
        # Check plan ID mapping
        if plan_id in self.plan_mappings:
            return self.plan_mappings[plan_id]
        
        # Check plan name for keywords
        plan_name_lower = plan_name.lower()
        
        if any(keyword in plan_name_lower for keyword in ["corporate", "enterprise", "business"]):
            return "corporate"
        elif any(keyword in plan_name_lower for keyword in ["retail", "premium", "pro"]):
            return "retail"
        else:
            return "free"
    
    async def _store_user_license(self, user_id: int, license_key: str, subscription: WhopSubscription):
        """Store validated license for user"""
        try:
            # Get existing licenses
            stored_licenses = get_user_property(user_id, "whop_licenses") or {}
            
            # Store license data
            stored_licenses[license_key] = {
                "id": subscription.id,
                "status": subscription.status,
                "plan_id": subscription.plan_id,
                "plan_name": subscription.plan_name,
                "user_id": subscription.user_id,
                "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
                "created_at": subscription.created_at.isoformat(),
                "metadata": subscription.metadata,
                "tier": subscription.tier,
                "validated_at": datetime.now().isoformat()
            }
            
            # Store updated licenses
            set_user_property(user_id, "whop_licenses", stored_licenses)
            
            # Store current tier
            set_user_property(user_id, "subscription_tier", subscription.tier)
            
            logger.info(f"Stored license for user {user_id}: {license_key[:8]}... (tier: {subscription.tier})")
            
        except Exception as e:
            logger.error(f"Error storing user license: {e}")
    
    async def get_user_tier(self, user_id: int) -> str:
        """Get user's current subscription tier"""
        try:
            # Check stored tier
            tier = get_user_property(user_id, "subscription_tier")
            if tier and tier in self.tier_features:
                return tier
            
            # Check if user has any valid licenses
            stored_licenses = get_user_property(user_id, "whop_licenses") or {}
            
            highest_tier = "free"
            for license_key, license_data in stored_licenses.items():
                if license_data.get("status") == "active":
                    expires_at = license_data.get("expires_at")
                    if not expires_at or datetime.fromisoformat(expires_at) > datetime.now():
                        license_tier = license_data.get("tier", "free")
                        
                        # Determine highest tier
                        if license_tier == "corporate":
                            highest_tier = "corporate"
                        elif license_tier == "retail" and highest_tier != "corporate":
                            highest_tier = "retail"
            
            # Update stored tier
            set_user_property(user_id, "subscription_tier", highest_tier)
            return highest_tier
            
        except Exception as e:
            logger.error(f"Error getting user tier: {e}")
            return "free"
    
    async def get_user_features(self, user_id: int) -> List[str]:
        """Get list of features available to user"""
        tier = await self.get_user_tier(user_id)
        return self.tier_features.get(tier, self.tier_features["free"])
    
    async def has_feature(self, user_id: int, feature: str) -> bool:
        """Check if user has access to a specific feature"""
        features = await self.get_user_features(user_id)
        return feature in features
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """Process Whop webhook for license updates"""
        try:
            event_type = webhook_data.get("type")
            
            if event_type in ["license.created", "license.updated", "license.cancelled"]:
                license_data = webhook_data.get("data", {})
                
                # Extract user information (you may need to map Whop user ID to Telegram user ID)
                whop_user_id = license_data.get("user", {}).get("id")
                
                # For now, we'll store the webhook data for later validation
                # In production, you'd want to map Whop user IDs to Telegram user IDs
                
                logger.info(f"Processed webhook: {event_type} for user {whop_user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
        
        return False
    
    def clear_cache(self):
        """Clear license validation cache"""
        self.license_cache.clear()
        logger.info("License validation cache cleared")
    
    async def has_feature_for_tier(self, feature: str, tier: str) -> bool:
        """Check if a specific tier has access to a feature"""
        tier_features = self.tier_features.get(tier, [])
        return feature in tier_features

# Global instance
whop_client = EnhancedWhopClient()

# Export functions for backward compatibility
async def validate_license_key(license_key: str, user_id: int) -> LicenseValidationResult:
    """Validate a license key"""
    return await whop_client.validate_license_key(license_key, user_id)

async def get_user_tier(user_id: int) -> str:
    """Get user's subscription tier"""
    return await whop_client.get_user_tier(user_id)

async def get_user_features(user_id: int) -> List[str]:
    """Get user's available features"""
    return await whop_client.get_user_features(user_id)

async def has_feature(user_id: int, feature: str) -> bool:
    """Check if user has access to feature"""
    return await whop_client.has_feature(user_id, feature)

async def process_webhook(webhook_data: Dict[str, Any]) -> bool:
    """Process Whop webhook"""
    return await whop_client.process_webhook(webhook_data)
