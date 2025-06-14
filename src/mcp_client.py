# src/mcp_client.py - Model Context Protocol Client Infrastructure
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import websockets
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class MCPServer:
    """MCP Server configuration"""
    name: str
    url: str
    tools: List[str]
    auth_token: Optional[str] = None
    timeout: int = 30

class MCPClientManager:
    """Centralized MCP client manager for all server connections"""

    def __init__(self):
        self.clients = {}
        self.sessions = {}
        self.servers = {}
        self.connected = False

    async def initialize_servers(self):
        """Initialize all MCP servers with FastMCP integration - REAL DATA ONLY"""
        try:
            # Real Financial Data Server - Production-grade market data and DeFi analytics
            # Uses CoinGecko, DeFiLlama, and other real APIs
            self.servers['financial'] = MCPServer(
                name="real-financial-server",
                url="http://localhost:8011",
                tools=['get_crypto_prices', 'get_market_data', 'get_defi_protocols', 'get_trending_coins', 'get_market_overview', 'analyze_price_movement']
            )

            # Real Web Research Server - Production-grade browsing and research
            # Uses real web scraping and search APIs
            self.servers['web'] = MCPServer(
                name="real-web-research-server",
                url="http://localhost:8013",
                tools=['web_search', 'extract_webpage_content', 'monitor_news_sources', 'analyze_website_structure', 'research_topic']
            )

            # Real Blockchain Analytics Server - Production-grade Multi-Chain Support
            # Uses real blockchain RPC endpoints and analytics APIs
            self.servers['blockchain'] = MCPServer(
                name="real-blockchain-server",
                url="http://localhost:8012",
                tools=[
                    # Real blockchain tools
                    'get_wallet_balance', 'get_transaction_history', 'get_token_balances', 'get_gas_prices', 'get_block_info', 'track_whale_movements',
                    # New Base and Optimism specific tools
                    'get_base_chain_analytics', 'get_optimism_chain_analytics', 'get_cross_chain_comparison'
                ]
            )

            # Whop Payment Server - Industry-grade payment processing and license validation
            # Uses real Whop API for payment processing, license validation, and webhook handling
            self.servers['payment'] = MCPServer(
                name="whop-payment-server",
                url="http://localhost:8014",
                tools=[
                    'validate_license_key', 'get_membership_info', 'list_recent_payments', 
                    'get_payment_info', 'terminate_user_membership', 'process_payment_webhook', 
                    'check_premium_access'
                ]
            )

            logger.info("✅ MCP servers configured (including Whop payment processing)")

        except Exception as e:
            logger.error(f"❌ Failed to configure MCP servers: {e}")

    async def connect_to_servers(self):
        """Connect to all configured MCP servers - REAL DATA ONLY"""
        connected_count = 0
        real_connections = 0

        for server_name, server in self.servers.items():
            try:
                # STEP 1: Try to connect to actual FastMCP servers with real data
                if await self._test_server_connection(server.url):
                    self.clients[server_name] = FastMCPClient(server)
                    self.sessions[server_name] = await self.clients[server_name].connect()
                    logger.info(f"🌐 Connected to REAL DATA {server_name} at {server.url}")
                    real_connections += 1
                    connected_count += 1
                else:
                    # STEP 2: Try to start the real server if it's not running
                    logger.warning(f"⚠️ Real server {server_name} not responding, attempting to start...")
                    await self._attempt_start_real_server(server_name, server)
                    
                    # Wait a bit for server to start
                    await asyncio.sleep(3)
                    
                    # Test connection again after attempting to start
                    if await self._test_server_connection(server.url):
                        self.clients[server_name] = FastMCPClient(server)
                        self.sessions[server_name] = await self.clients[server_name].connect()
                        logger.info(f"🌐 Connected to REAL DATA {server_name} (auto-started)")
                        real_connections += 1
                        connected_count += 1
                    else:
                        # NO MOCK FALLBACK - Real servers only
                        logger.error(f"❌ Cannot connect to real server {server_name} - SKIPPING (no mock fallback)")

            except Exception as e:
                logger.error(f"❌ Failed to connect to {server_name}: {e} - SKIPPING (no mock fallback)")

        self.connected = connected_count > 0
        logger.info(f"✅ MCP Client Manager initialized ({connected_count} total, {real_connections} real data servers)")
        
        if real_connections == 0:
            logger.error("❌ CRITICAL: No real data servers connected! System will not function properly.")
        elif real_connections < len(self.servers):
            logger.warning(f"⚠️ WARNING: Only {real_connections}/{len(self.servers)} real data servers connected.")
        else:
            logger.info("🎉 SUCCESS: All servers connected to real data sources!")
    
    async def close(self):
        """Close all MCP client connections"""
        for client in self.clients.values():
            if hasattr(client, 'close'):
                try:
                    await client.close()
                except Exception as e:
                    logger.warning(f"Error closing client: {e}")
        self.clients.clear()
        self.sessions.clear()
        self.connected = False
    
    async def _attempt_start_real_server(self, server_name: str, server: MCPServer):
        """Attempt to start a real MCP server"""
        try:
            import subprocess
            import sys
            from pathlib import Path
            
            # Map server names to their real server scripts
            server_scripts = {
                'financial': 'src/mcp_servers/real_financial_server.py',
                'web': 'src/mcp_servers/real_web_research_server.py',
                'blockchain': 'src/mcp_servers/real_blockchain_server.py',
                'payment': 'src/mcp_servers/whop_payment_server.py'
            }
            
            script_path = server_scripts.get(server_name)
            if script_path and Path(script_path).exists():
                # Extract port from URL
                port = server.url.split(':')[-1]
                
                # Start the server in background
                cmd = [sys.executable, script_path, '--port', port]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=Path.cwd()
                )
                
                # Give it a moment to start
                await asyncio.sleep(2)
                logger.info(f"🚀 Attempted to start real server {server_name} on port {port}")
                
            else:
                logger.warning(f"⚠️ Real server script not found for {server_name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to start real server {server_name}: {e}")
    
    async def _test_server_connection(self, url: str) -> bool:
        """Test if MCP server is running"""
        try:
            import aiohttp
            import socket
            
            # First try a simple socket connection to check if port is open
            host = url.split('://')[1].split(':')[0] if '://' in url else url.split(':')[0]
            port = int(url.split(':')[-1])
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                # Port is open, try HTTP request to root
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                        return response.status in [200, 404, 405]  # Any response means server is running
            return False
        except:
            return False

    async def call_tool(self, server: str, tool: str, arguments: dict) -> dict:
        """Call a tool on a specific MCP server with security validation"""
        try:
            # Ensure servers are initialized
            if not self.servers:
                await self.initialize_servers()
                await self.connect_to_servers()
            
            # Security: Validate server name
            if server not in self.servers:
                logger.warning(f"🔒 Security: Invalid server name attempted: {server}")
                return {"error": "Invalid server", "fallback": True}

            # Security: Validate tool name
            allowed_tools = self.servers[server].tools
            if tool not in allowed_tools:
                logger.warning(f"🔒 Security: Invalid tool attempted: {server}.{tool}")
                return {"error": "Invalid tool", "fallback": True}

            # Security: Sanitize arguments
            sanitized_args = self._sanitize_arguments(arguments)

            if server not in self.sessions:
                logger.warning(f"⚠️ Server {server} not connected, using fallback")
                return await self._get_fallback_response(server, tool, sanitized_args)

            session = self.sessions[server]
            result = await session.call_tool(tool, sanitized_args)

            # Security: Validate response
            if not isinstance(result, dict):
                logger.warning("🔒 Security: Invalid response format from MCP server")
                return {"error": "Invalid response format", "fallback": True}

            return result

        except Exception as e:
            logger.error(f"❌ MCP tool call failed: {server}.{tool} - {e}")
            return await self._get_fallback_response(server, tool, arguments)

    def _sanitize_arguments(self, arguments: dict) -> dict:
        """Sanitize MCP arguments for security"""
        if not isinstance(arguments, dict):
            return {}

        sanitized = {}
        for key, value in arguments.items():
            # Security: Only allow safe data types
            if isinstance(value, (str, int, float, bool, list)):
                if isinstance(value, str):
                    # Security: Limit string length and remove dangerous characters
                    value = value[:1000]  # Limit length
                    value = ''.join(c for c in value if c.isprintable())  # Only printable chars
                elif isinstance(value, list):
                    # Security: Limit list size and sanitize elements
                    value = value[:100]  # Limit list size
                    value = [str(item)[:100] for item in value if isinstance(item, (str, int, float))]

                sanitized[key] = value

        return sanitized

    async def _get_fallback_response(self, server: str, tool: str, arguments: dict) -> dict:
        """Get fallback response when MCP server is unavailable"""
        # Return safe fallback data
        return {
            "success": False,
            "fallback": True,
            "message": "Service temporarily unavailable, using cached data",
            "server": server,
            "tool": tool
        }

    async def stream_data(self, server: str, stream_type: str, callback) -> bool:
        """Set up data streaming from MCP server"""
        try:
            if server not in self.sessions:
                return False

            session = self.sessions[server]
            await session.setup_stream(stream_type, callback)
            return True

        except Exception as e:
            logger.error(f"❌ MCP streaming setup failed: {e}")
            return False

class FastMCPClient:
    """FastMCP HTTP client for real MCP servers"""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.session = None
        self.connected = False
    
    async def connect(self):
        """Connect to FastMCP server"""
        import aiohttp
        self.session = aiohttp.ClientSession()
        self.connected = True
        return FastMCPSession(self.server, self.session)
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            self.connected = False

class FastMCPSession:
    """FastMCP HTTP session for tool calls using MCP JSON-RPC protocol"""
    
    def __init__(self, server: MCPServer, session):
        self.server = server
        self.session = session
        self.request_id = 0
        self.initialized = False
    

    
    def _next_id(self):
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def call_tool(self, tool: str, arguments: dict) -> dict:
        """Call tool on server via simple HTTP API"""
        try:
            # Use simple HTTP API instead of MCP protocol
            url = f"{self.server.url}/tools/{tool}"
            headers = {"Content-Type": "application/json"}
            
            # Create request payload - send arguments directly
            payload = arguments
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('success'):
                        return {
                            "success": True,
                            "data": result.get('data'),
                            "source": result.get('source', f"HTTP {self.server.name}")
                        }
                    else:
                        return {
                            "success": False,
                            "error": result.get('error', 'Unknown error')
                        }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {await response.text()}"
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }

mcp_client = MCPClientManager()

# Compatibility layer for new MCP integration
class CompatibilityMCPClient:
    """Compatibility layer for existing MCP client usage"""
    
    def __init__(self):
        self.legacy_client = mcp_client
        # Add servers attribute for compatibility
        self.servers = getattr(self.legacy_client, 'servers', {})
    
    async def initialize_servers(self):
        """Initialize MCP servers"""
        try:
            await self.legacy_client.initialize_servers()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MCP servers: {e}")
            return False
    
    async def connect_to_servers(self):
        """Connect to MCP servers"""
        try:
            await self.legacy_client.connect_to_servers()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP servers: {e}")
            return False
    
    async def call_tool(self, server: str, tool: str, arguments: dict) -> dict:
        """Call tool with compatibility mapping"""
        try:
            # Import here to avoid circular imports
            from mcp_integration import call_mcp_tool
            
            # Map legacy server names to new ones
            server_mapping = {
                'financial': 'financial',
                'web': 'web_research',
                'social': 'web_research',  # Social tools are in web research server
                'blockchain': 'blockchain'
            }
            
            mapped_server = server_mapping.get(server, server)
            result = await call_mcp_tool(mapped_server, tool, arguments)
            
            if result.get('success'):
                return result
            else:
                # Fallback to legacy client
                return await self.legacy_client.call_tool(server, tool, arguments)
                
        except Exception as e:
            # Fallback to legacy client on error
            return await self.legacy_client.call_tool(server, tool, arguments)
    
    async def initialize(self):
        """Initialize compatibility client"""
        return await self.legacy_client.initialize_servers()

# Replace global mcp_client with compatibility version
mcp_client = CompatibilityMCPClient()

async def initialize_mcp():
    """Initialize MCP client infrastructure"""
    try:
        await mcp_client.initialize_servers()
        await mcp_client.connect_to_servers()
        logger.info("🚀 MCP infrastructure ready!")
        return True
    except Exception as e:
        logger.error(f"❌ MCP initialization failed: {e}")
        return False

# Convenience functions for common MCP operations
async def get_market_data(symbols: List[str] = None) -> dict:
    """Get real-time market data via MCP"""
    symbols = symbols or ["BTC", "ETH", "SOL"]
    return await mcp_client.call_tool("financial", "get_crypto_prices", {"symbols": symbols})

async def get_social_sentiment(topic: str = "crypto") -> dict:
    """Get social sentiment analysis via MCP"""
    return await mcp_client.call_tool("social", "twitter_sentiment", {"topic": topic})

async def analyze_wallet(address: str) -> dict:
    """Analyze wallet via MCP blockchain tools"""
    return await mcp_client.call_tool("blockchain", "wallet_tracking", {"address": address})

async def web_research(query: str) -> dict:
    """Perform web research via MCP"""
    return await mcp_client.call_tool("web", "web_search", {"query": query})

async def initialize_mcp_client():
    """Initialize MCP client (alias for compatibility)"""
    return await mcp_client.initialize()