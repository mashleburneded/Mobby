# 🔐 Whop Integration Setup Guide for Möbius AI Assistant

## 📋 Overview

This guide will walk you through setting up Whop integration for license key validation and subscription management in your Möbius AI Assistant bot.

## 🎯 What You'll Need

1. **Whop Account** - Developer access to Whop platform
2. **Whop App** - Created in your Whop dashboard
3. **Bearer Token** - API authentication token
4. **Product/Plans** - Set up in Whop for your bot subscriptions

## 🚀 Step-by-Step Setup

### Step 1: Create Whop Developer Account

1. **Visit Whop Developer Portal**
   - Go to [https://dev.whop.com](https://dev.whop.com)
   - Sign up or log in to your Whop account

2. **Access Developer Dashboard**
   - Navigate to the developer section
   - Create a new developer account if needed

### Step 2: Create Your App

1. **Create New App**
   ```
   - Go to Whop Dashboard → Apps → Create App
   - App Name: "Möbius AI Assistant"
   - Description: "Enterprise-grade AI assistant for Telegram"
   - Category: "Productivity" or "Tools"
   ```

2. **Configure App Settings**
   ```
   - Webhook URL: https://your-domain.com/whop-webhook (optional)
   - Redirect URLs: Add your bot's domain if needed
   - Permissions: Select required permissions
   ```

### Step 3: Generate Bearer Token

1. **Navigate to API Settings**
   ```
   Dashboard → Your App → API → Authentication
   ```

2. **Create Bearer Token**
   ```bash
   # In your Whop app dashboard:
   1. Go to "API Keys" section
   2. Click "Generate New Token"
   3. Name: "Mobius-Bot-Production"
   4. Permissions: 
      - Read licenses
      - Read subscriptions
      - Read users
   5. Copy the generated token (save it securely!)
   ```

3. **Token Format**
   ```
   Your token will look like: whop_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Step 4: Set Up Products and Plans

1. **Create Product**
   ```
   Dashboard → Products → Create Product
   - Name: "Möbius AI Assistant"
   - Type: "Software/SaaS"
   - Description: "AI-powered Telegram assistant"
   ```

2. **Create Plans**
   ```
   Create these plans in your product:
   
   Plan 1: "Retail Plan"
   - ID: plan_retail
   - Price: $X/month
   - Features: Premium AI features, advanced research
   
   Plan 2: "Enterprise Plan" 
   - ID: plan_enterprise
   - Price: $Y/month
   - Features: All features + priority support
   ```

### Step 5: Configure Environment Variables

1. **Add to .env file**
   ```bash
   # Add this to your .env file
   WHOP_BEARER_TOKEN=whop_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   WHOP_PREMIUM_RETAIL_PLAN_ID=plan_DR5ltY4c3QjQV
   WHOP_PREMIUM_CORPORATE_PLAN_ID=plan_cpsmcglAaG7eI
   ```

2. **Verify Environment Setup**
   ```bash
   # Test that the token is loaded
   python -c "import os; print('Token loaded:', bool(os.getenv('WHOP_BEARER_TOKEN')))"
   ```

### Step 6: Test Integration

1. **Run Integration Test**
   ```bash
   cd Mobius
   python -c "
   import asyncio
   from src.whop_integration import test_whop_integration
   asyncio.run(test_whop_integration())
   "
   ```

2. **Test License Validation**
   ```bash
   # Test with a real license key from your Whop dashboard
   python -c "
   import asyncio
   from src.whop_integration import validate_whop_license
   result = asyncio.run(validate_whop_license('your_test_license_key'))
   print('Validation result:', result)
   "
   ```

## 🔧 API Configuration Details

### Required Whop API Permissions

Your bearer token needs these permissions:

```json
{
  "permissions": [
    "licenses:read",
    "subscriptions:read", 
    "users:read",
    "products:read"
  ]
}
```

### API Endpoints Used

The integration uses these Whop API endpoints:

1. **License Validation**
   ```
   GET https://api.whop.com/api/v2/licenses/{license_key}
   ```

2. **Subscription Details**
   ```
   GET https://api.whop.com/api/v2/subscriptions/{subscription_id}
   ```

3. **GraphQL Queries**
   ```
   POST https://api.whop.com/api/graphql
   ```

## 🎛️ Plan Mapping Configuration

### Customize Plan Tiers

The plan mapping is automatically configured using your environment variables:

```python
# Current plan mapping (automatically configured):
WHOP_PREMIUM_RETAIL_PLAN_ID = "plan_DR5ltY4c3QjQV"     → "retail" tier
WHOP_PREMIUM_CORPORATE_PLAN_ID = "plan_cpsmcglAaG7eI"  → "enterprise" tier

# Plan names:
plan_DR5ltY4c3QjQV → "Premium Retail"
plan_cpsmcglAaG7eI → "Premium Corporate"
```

The integration automatically detects which plan a user purchased based on their license key and assigns the correct tier and features.

## 📊 License Tracking & Validation

### How License Tracking Works

1. **License Key Validation**: When a user enters a license key, the bot:
   - Validates the key with Whop API
   - Determines which plan was purchased (Retail or Corporate)
   - Assigns the appropriate tier and features
   - Stores the license information in the database

2. **Plan Detection**: The system automatically detects:
   ```
   License Key → Whop API → Plan ID → Bot Tier → Features
   
   Example:
   abc123... → plan_DR5ltY4c3QjQV → "retail" → Premium Retail features
   xyz789... → plan_cpsmcglAaG7eI → "enterprise" → Premium Corporate features
   ```

3. **Status Tracking**: Users can check their subscription status with `/status`:
   - Current plan name and tier
   - License key validation status
   - Expiration date (if applicable)
   - Available features

### Supported License Validation Methods

1. **Direct API Lookup**: `/api/v2/licenses/{license_key}`
2. **GraphQL Fallback**: Advanced query for detailed license information
3. **Plan Mapping**: Automatic tier assignment based on plan ID

## 🧪 Testing Your Setup

### Test License Tracking

1. **Run License Tracking Tests**
   ```bash
   # Test all license tracking functionality
   python test_whop_license_tracking.py
   
   # Should show:
   # 🎉 ALL WHOP TESTS PASSED!
   # ✅ License tracking is fully functional
   # ✅ Plan mapping is working correctly
   ```

2. **Get Test License Key**
   ```
   - Go to Whop Dashboard → Your Product → Licenses
   - Create a test license or use an existing one
   - Copy the license key
   ```

2. **Test in Bot**
   ```
   - Start your bot: python src/main.py
   - Send /start to your bot
   - Choose "Activate Premium Plan"
   - Paste your test license key
   - Verify it validates correctly
   ```

### Test Subscription Status

```python
# Test subscription checking
import asyncio
from src.whop_integration import check_whop_subscription

async def test():
    status = await check_whop_subscription("user@example.com")
    print(f"Subscription status: {status}")

asyncio.run(test())
```

## 🔒 Security Best Practices

### Token Security

1. **Never commit tokens to git**
   ```bash
   # Make sure .env is in .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables**
   ```bash
   # For production deployment
   export WHOP_BEARER_TOKEN=whop_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Rotate tokens regularly**
   ```
   - Generate new tokens every 90 days
   - Update environment variables
   - Test thoroughly after rotation
   ```

### Error Handling

The integration includes comprehensive error handling:

- **Invalid tokens** → Falls back to free tier
- **Network errors** → Graceful degradation
- **API rate limits** → Automatic retry logic
- **Invalid license keys** → Clear error messages

## 🚨 Troubleshooting

### Common Issues

1. **"Whop integration not configured"**
   ```bash
   # Check if token is set
   echo $WHOP_BEARER_TOKEN
   
   # If empty, add to .env:
   echo "WHOP_BEARER_TOKEN=your_token_here" >> .env
   ```

2. **"License key not found"**
   ```
   - Verify the license key is correct
   - Check if the license is active in Whop dashboard
   - Ensure the license belongs to your product
   ```

3. **"API authentication failed"**
   ```
   - Verify bearer token is correct
   - Check token permissions in Whop dashboard
   - Ensure token hasn't expired
   ```

4. **"Plan ID not recognized"**
   ```
   - Check plan IDs in Whop dashboard
   - Update plan_tier_mapping in whop_integration.py
   - Restart the bot after changes
   ```

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
# Add to your main.py
import logging
logging.getLogger('whop_integration').setLevel(logging.DEBUG)
```

## 📊 Monitoring and Analytics

### Track License Usage

```python
# Add to your bot to track license validations
from src.whop_integration import validate_whop_license

async def track_license_validation(license_key: str, user_id: int):
    result = await validate_whop_license(license_key)
    
    # Log for analytics
    logger.info(f"License validation: user={user_id}, valid={result['valid']}, tier={result['tier']}")
    
    return result
```

### Monitor Subscription Health

```python
# Periodic subscription health check
async def check_subscription_health():
    # Check active subscriptions
    # Send alerts for expiring licenses
    # Update user tiers based on current status
    pass
```

## 🎉 Success Verification

Your Whop integration is working correctly when:

✅ **License keys validate properly**
✅ **Invalid keys are rejected with clear messages**  
✅ **Subscription tiers are correctly assigned**
✅ **Expiration dates are tracked**
✅ **Error handling works gracefully**
✅ **Bot falls back to free tier when needed**

## 📞 Support

If you encounter issues:

1. **Check Whop Documentation**: [https://dev.whop.com](https://dev.whop.com)
2. **Verify API Status**: [https://status.whop.com](https://status.whop.com)
3. **Test with Postman**: Use the provided API endpoints
4. **Contact Whop Support**: For API-specific issues

## 🔄 Maintenance

### Regular Tasks

1. **Monthly**: Review token permissions and usage
2. **Quarterly**: Rotate bearer tokens
3. **As needed**: Update plan mappings for new products
4. **Monitor**: API rate limits and error rates

Your Möbius AI Assistant now has enterprise-grade license validation! 🚀