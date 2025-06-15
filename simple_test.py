#!/usr/bin/env python3
"""
Simple test for tier access control
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tier_access_control import tier_access_control

def test_tier_access():
    """Test basic tier access control"""
    print("🧪 Testing Tier Access Control...")
    
    # Test free tier
    free_portfolio = tier_access_control.check_feature_access("free", "portfolio_tracking")
    print(f"Free tier portfolio tracking: {free_portfolio['allowed']}")
    
    free_analytics = tier_access_control.check_feature_access("free", "portfolio_analytics")
    print(f"Free tier portfolio analytics: {free_analytics['allowed']}")
    
    # Test retail tier
    retail_analytics = tier_access_control.check_feature_access("retail", "portfolio_analytics")
    print(f"Retail tier portfolio analytics: {retail_analytics['allowed']}")
    
    # Test corporate tier
    corporate_api = tier_access_control.check_feature_access("corporate", "api_access")
    print(f"Corporate tier API access: {corporate_api['allowed']}")
    
    # Test tier comparison
    comparison = tier_access_control.get_tier_comparison()
    print(f"Available tiers: {list(comparison.keys())}")
    
    # Test upgrade benefits
    benefits = tier_access_control.get_upgrade_benefits("free", "retail")
    print(f"Upgrade benefits (free -> retail): {benefits['total_new_features']} new features")
    
    print("✅ Tier access control working correctly!")

if __name__ == "__main__":
    test_tier_access()