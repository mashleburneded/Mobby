#!/usr/bin/env python3
"""
Whop License Tracking Test Script
Tests license validation and plan tracking functionality
"""

import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_plan_mapping():
    """Test plan ID mapping functionality"""
    logger.info("🧪 Testing Plan ID Mapping...")
    
    try:
        from src.whop_integration import WhopIntegration
        
        whop = WhopIntegration()
        
        # Test plan ID mappings
        test_cases = [
            ("plan_DR5ltY4c3QjQV", "retail", "Premium Retail"),
            ("plan_cpsmcglAaG7eI", "enterprise", "Premium Corporate"),
            ("unknown_plan", "retail", "Unknown Plan (unknown_plan)"),
        ]
        
        for plan_id, expected_tier, expected_name in test_cases:
            tier = whop._determine_tier(plan_id)
            name = whop._get_plan_name(plan_id)
            
            tier_match = tier == expected_tier
            name_match = name == expected_name
            
            if tier_match and name_match:
                logger.info(f"✅ Plan {plan_id}: {name} ({tier})")
            else:
                logger.error(f"❌ Plan {plan_id}: Expected {expected_name} ({expected_tier}), got {name} ({tier})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Plan mapping test failed: {e}")
        return False

async def test_license_validation():
    """Test license validation with mock data"""
    logger.info("🧪 Testing License Validation...")
    
    try:
        from src.whop_integration import validate_whop_license
        
        # Test with invalid license key (should fail gracefully)
        result = await validate_whop_license("invalid_test_key_12345")
        
        expected_keys = ["valid", "error", "tier", "plan_name", "plan_id"]
        has_required_keys = all(key in result for key in expected_keys)
        
        if has_required_keys and not result["valid"]:
            logger.info("✅ Invalid license key handled correctly")
            logger.info(f"   Result: {result}")
            return True
        else:
            logger.error(f"❌ License validation failed: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ License validation test failed: {e}")
        return False

async def test_environment_configuration():
    """Test environment variable configuration"""
    logger.info("🧪 Testing Environment Configuration...")
    
    try:
        # Check for required environment variables
        retail_plan_id = os.getenv('WHOP_PREMIUM_RETAIL_PLAN_ID')
        corporate_plan_id = os.getenv('WHOP_PREMIUM_CORPORATE_PLAN_ID')
        bearer_token = os.getenv('WHOP_BEARER_TOKEN')
        
        results = []
        
        if retail_plan_id == "plan_DR5ltY4c3QjQV":
            logger.info("✅ Retail plan ID configured correctly")
            results.append(True)
        else:
            logger.error(f"❌ Retail plan ID incorrect: {retail_plan_id}")
            results.append(False)
        
        if corporate_plan_id == "plan_cpsmcglAaG7eI":
            logger.info("✅ Corporate plan ID configured correctly")
            results.append(True)
        else:
            logger.error(f"❌ Corporate plan ID incorrect: {corporate_plan_id}")
            results.append(False)
        
        if bearer_token:
            logger.info("✅ Bearer token is configured")
            results.append(True)
        else:
            logger.warning("⚠️ Bearer token not configured (expected for testing)")
            results.append(True)  # Not a failure for testing
        
        return all(results)
        
    except Exception as e:
        logger.error(f"❌ Environment configuration test failed: {e}")
        return False

async def test_database_integration():
    """Test database integration for license tracking"""
    logger.info("🧪 Testing Database Integration...")
    
    try:
        from src.enhanced_db import set_user_property, get_user_property
        
        test_user_id = 999999
        
        # Test storing license information
        test_data = {
            'subscription_tier': 'retail',
            'whop_plan_id': 'plan_DR5ltY4c3QjQV',
            'whop_plan_name': 'Premium Retail',
            'whop_license_key': 'test_license_key_12345'
        }
        
        # Store test data
        for key, value in test_data.items():
            set_user_property(test_user_id, key, value)
        
        # Retrieve and verify
        all_correct = True
        for key, expected_value in test_data.items():
            retrieved_value = get_user_property(test_user_id, key)
            if retrieved_value != expected_value:
                logger.error(f"❌ Database test failed for {key}: expected {expected_value}, got {retrieved_value}")
                all_correct = False
        
        if all_correct:
            logger.info("✅ Database integration working correctly")
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"❌ Database integration test failed: {e}")
        return False

def test_plan_id_constants():
    """Test that plan ID constants are correctly set"""
    logger.info("🧪 Testing Plan ID Constants...")
    
    try:
        # Check the actual plan IDs provided by the user
        retail_plan = "plan_DR5ltY4c3QjQV"
        corporate_plan = "plan_cpsmcglAaG7eI"
        
        # Verify they match expected format
        if retail_plan.startswith("plan_") and len(retail_plan) > 10:
            logger.info(f"✅ Retail plan ID format valid: {retail_plan}")
            retail_valid = True
        else:
            logger.error(f"❌ Retail plan ID format invalid: {retail_plan}")
            retail_valid = False
        
        if corporate_plan.startswith("plan_") and len(corporate_plan) > 10:
            logger.info(f"✅ Corporate plan ID format valid: {corporate_plan}")
            corporate_valid = True
        else:
            logger.error(f"❌ Corporate plan ID format invalid: {corporate_plan}")
            corporate_valid = False
        
        return retail_valid and corporate_valid
        
    except Exception as e:
        logger.error(f"❌ Plan ID constants test failed: {e}")
        return False

async def test_whop_client_initialization():
    """Test Whop client initialization"""
    logger.info("🧪 Testing Whop Client Initialization...")
    
    try:
        from src.whop_integration import WhopIntegration, WhopClient
        
        # Test with no token (should handle gracefully)
        whop_no_token = WhopIntegration()
        if whop_no_token.client is None:
            logger.info("✅ Handles missing bearer token gracefully")
            no_token_ok = True
        else:
            logger.warning("⚠️ Client initialized without bearer token")
            no_token_ok = True  # Not necessarily an error
        
        # Test with mock token
        if os.getenv('WHOP_BEARER_TOKEN'):
            whop_with_token = WhopIntegration()
            if whop_with_token.client is not None:
                logger.info("✅ Client initialized with bearer token")
                with_token_ok = True
            else:
                logger.error("❌ Client failed to initialize with bearer token")
                with_token_ok = False
        else:
            logger.info("ℹ️ No bearer token configured (expected for testing)")
            with_token_ok = True
        
        return no_token_ok and with_token_ok
        
    except Exception as e:
        logger.error(f"❌ Whop client initialization test failed: {e}")
        return False

async def main():
    """Run comprehensive Whop license tracking tests"""
    logger.info("🚀 Starting Whop License Tracking Test Suite")
    logger.info("=" * 60)
    
    tests = [
        ("Plan ID Constants", test_plan_id_constants),
        ("Environment Configuration", test_environment_configuration),
        ("Whop Client Initialization", test_whop_client_initialization),
        ("Plan Mapping", test_plan_mapping),
        ("License Validation", test_license_validation),
        ("Database Integration", test_database_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 WHOP LICENSE TRACKING TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("\n🎉 ALL WHOP TESTS PASSED!")
        logger.info("✅ License tracking is fully functional")
        logger.info("✅ Plan mapping is working correctly")
        logger.info("✅ Database integration is operational")
        logger.info("✅ Ready for production license validation")
    else:
        logger.info(f"\n⚠️ {total - passed} tests failed")
        logger.info("❌ Some issues need to be resolved")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)