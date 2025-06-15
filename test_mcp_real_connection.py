#!/usr/bin/env python3
"""
Test MCP Real Server Connection
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_real_connection():
    """Test MCP client connection to real servers"""
    try:
        from mcp_client import MCPClientManager
        
        logger.info("🧪 Testing MCP Real Server Connection...")
        
        # Initialize MCP client
        mcp_client = MCPClientManager()
        await mcp_client.initialize_servers()
        
        logger.info("✅ MCP servers initialized")
        
        # Connect to servers
        await mcp_client.connect_to_servers()
        
        if mcp_client.connected:
            logger.info("✅ MCP client connected successfully!")
            
            # Test a simple tool call
            try:
                result = await mcp_client.call_tool(
                    'financial', 
                    'get_crypto_prices', 
                    {'symbols': ['BTC']}
                )
                
                if result and result.get("success"):
                    logger.info("✅ Financial tool call successful!")
                    logger.info(f"Result: {result}")
                else:
                    logger.warning("⚠️ Financial tool call returned no data (may be using mock)")
                    
            except Exception as e:
                logger.error(f"❌ Financial tool call failed: {e}")
            
            # Test web research tool
            try:
                web_result = await mcp_client.call_tool(
                    'web',
                    'web_search',
                    {'query': 'Bitcoin price', 'limit': 2}
                )
                
                if web_result and web_result.get("success"):
                    logger.info("✅ Web research tool call successful!")
                    logger.info(f"Result: {web_result}")
                else:
                    logger.warning("⚠️ Web research tool call returned no data (may be using mock)")
                    
            except Exception as e:
                logger.error(f"❌ Web research tool call failed: {e}")
        
        else:
            logger.error("❌ MCP client failed to connect")
        
        await mcp_client.close()
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_real_connection())