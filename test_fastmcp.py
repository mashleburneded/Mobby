#!/usr/bin/env python3
"""
Test FastMCP server to debug the issue
"""

import asyncio
import logging
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a simple FastMCP server
mcp = FastMCP(name="Test Server")

@mcp.tool()
def test_tool(message: str) -> str:
    """A simple test tool"""
    return f"Echo: {message}"

async def main():
    """Test the server startup"""
    try:
        logger.info("🚀 Starting Test FastMCP Server on 0.0.0.0:8000")
        await mcp.run_sse_async(host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())