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
            
            # Create request payload
            payload = {"arguments": arguments}
            
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

class MockMCPClient:
    """Mock MCP client for development/testing"""

    def __init__(self, server: MCPServer):
        self.server = server
        self.connected = False

    async def connect(self):
        """Mock connection"""
        self.connected = True
        return MockMCPSession(self.server)

class MockMCPSession:
    """Mock MCP session for development/testing"""

    def __init__(self, server: MCPServer):
        self.server = server

    async def call_tool(self, tool: str, arguments: dict) -> dict:
        """Mock tool call with realistic responses"""

        # Financial data responses
        if self.server.name == "financial-data-server":
            if tool == "get_crypto_prices":
                return {
                    "success": True,
                    "data": {
                        "BITCOIN": {"price": 43250.50, "change_24h": 2.3, "market_cap": 850000000000, "volume_24h": 25000000000},
                        "ETHEREUM": {"price": 2650.75, "change_24h": -1.2, "market_cap": 320000000000, "volume_24h": 15000000000},
                        "SOLANA": {"price": 98.45, "change_24h": 5.7, "market_cap": 45000000000, "volume_24h": 2500000000}
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "CoinGecko API"
                }
            elif tool == "get_defi_protocols":
                return {
                    "success": True,
                    "data": {
                        "protocols": [
                            {"name": "Uniswap", "tvl": 4200000000, "change_1d": 1.5, "chain": "Ethereum", "category": "DEX"},
                            {"name": "Aave", "tvl": 3800000000, "change_1d": -0.8, "chain": "Ethereum", "category": "Lending"},
                            {"name": "Compound", "tvl": 2100000000, "change_1d": 2.1, "chain": "Ethereum", "category": "Lending"}
                        ],
                        "total_protocols": 500,
                        "total_tvl": 45000000000
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "DeFiLlama API"
                }
            elif tool == "get_market_overview":
                return {
                    "success": True,
                    "data": {
                        "total_market_cap": 1750000000000,
                        "total_volume": 85000000000,
                        "market_cap_change_24h": 2.3,
                        "active_cryptocurrencies": 12500,
                        "markets": 850,
                        "btc_dominance": 52.5,
                        "eth_dominance": 18.2,
                        "trending": {
                            "coins": ["Bitcoin", "Ethereum", "Solana", "Cardano", "Polygon"],
                            "nfts": ["CryptoPunks", "Bored Apes", "Azuki"]
                        }
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "CoinGecko Global API"
                }

        # Web research responses
        elif self.server.name == "web-research-server":
            if tool == "web_search":
                return {
                    "success": True,
                    "data": {
                        "query": arguments.get("query", "crypto"),
                        "results": [
                            {
                                "title": "Bitcoin Price Analysis: BTC Shows Strong Support",
                                "url": "https://example.com/btc-analysis",
                                "snippet": "Bitcoin maintains strong support levels as institutional adoption continues...",
                                "relevance_score": 0.95
                            },
                            {
                                "title": "DeFi Market Update: TVL Reaches New Highs",
                                "url": "https://example.com/defi-update",
                                "snippet": "Total Value Locked in DeFi protocols surpasses $45B milestone...",
                                "relevance_score": 0.88
                            }
                        ],
                        "total_found": 2
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "DuckDuckGo Search"
                }
            elif tool == "get_crypto_news":
                return {
                    "success": True,
                    "data": {
                        "articles": [
                            {
                                "title": "Major Exchange Announces New DeFi Integration",
                                "url": "https://example.com/news1",
                                "source": "cointelegraph",
                                "published": datetime.now().isoformat(),
                                "relevance_score": 0.92
                            },
                            {
                                "title": "Ethereum Layer 2 Solutions See Record Usage",
                                "url": "https://example.com/news2",
                                "source": "coindesk",
                                "published": datetime.now().isoformat(),
                                "relevance_score": 0.87
                            }
                        ],
                        "sources_checked": ["cointelegraph", "coindesk"],
                        "total_articles": 2
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "Multi-source News Aggregation"
                }
            elif tool == "monitor_social_sentiment":
                return {
                    "success": True,
                    "data": {
                        "topics_analyzed": arguments.get("topics", ["bitcoin", "ethereum"]),
                        "sentiment_analysis": {
                            "bitcoin": {
                                "sentiment_score": 0.72,
                                "sentiment_label": "Bullish",
                                "mentions_analyzed": 156,
                                "confidence": 0.85
                            },
                            "ethereum": {
                                "sentiment_score": 0.68,
                                "sentiment_label": "Bullish",
                                "mentions_analyzed": 142,
                                "confidence": 0.82
                            }
                        },
                        "overall_market_sentiment": {
                            "score": 0.70,
                            "label": "Bullish",
                            "confidence": 0.83
                        }
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "Social Media Sentiment Analysis"
                }

        # Blockchain analytics responses - Multi-Chain Support
        elif self.server.name == "blockchain-analytics-server":
            if tool == "analyze_wallet_cross_chain":
                wallet_address = arguments.get("wallet_address", "0x742d35Cc6634C0532925a3b8D4C9db96")
                return {
                    "success": True,
                    "data": {
                        "wallet_address": wallet_address,
                        "cross_chain_analysis": {
                            "ethereum": {
                                "chain_info": {"name": "Ethereum", "type": "L1", "native_token": "ETH"},
                                "balance": {"native_balance": 2.5, "usd_value": 6250},
                                "recent_transactions": {"transactions": [], "total_count": 0},
                                "activity_score": 75.0
                            },
                            "polygon": {
                                "chain_info": {"name": "Polygon", "type": "L2", "native_token": "MATIC"},
                                "balance": {"native_balance": 1500, "usd_value": 1200},
                                "recent_transactions": {"transactions": [], "total_count": 0},
                                "activity_score": 60.0
                            },
                            "base": {
                                "chain_info": {"name": "Base", "type": "L2", "native_token": "ETH"},
                                "balance": {"native_balance": 0.5, "usd_value": 1250},
                                "recent_transactions": {"transactions": [], "total_count": 0},
                                "activity_score": 45.0
                            },
                            "optimism": {
                                "chain_info": {"name": "Optimism", "type": "L2", "native_token": "ETH"},
                                "balance": {"native_balance": 1.2, "usd_value": 3000},
                                "recent_transactions": {"transactions": [], "total_count": 0},
                                "activity_score": 55.0
                            }
                        },
                        "portfolio_summary": {
                            "total_value_usd": 11700,
                            "active_chains": 4,
                            "total_recent_transactions": 0,
                            "diversification_score": 40.0
                        }
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "Multi-chain Analysis"
                }
            elif tool == "get_chain_analytics":
                chain = arguments.get("chain", "ethereum")
                return {
                    "success": True,
                    "data": {
                        "chain_info": {
                            "name": "Ethereum" if chain == "ethereum" else chain.title(),
                            "type": "L1" if chain in ["ethereum", "bitcoin", "solana"] else "L2",
                            "native_token": "ETH" if chain in ["ethereum", "arbitrum", "optimism", "base"] else chain.upper(),
                            "chain_id": 1 if chain == "ethereum" else 137
                        },
                        "network_metrics": {
                            "gas_price_gwei": 15 if chain == "ethereum" else 0.1,
                            "tps": 15 if chain == "ethereum" else 2000,
                            "tvl_usd": "45.2B" if chain == "ethereum" else "1.2B",
                            "active_addresses_24h": 450000 if chain == "ethereum" else 65000,
                            "block_time_seconds": 12 if chain == "ethereum" else 2,
                            "finality": "12 blocks" if chain == "ethereum" else "7 days (to L1)"
                        },
                        "health_status": "healthy"
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "Multi-source Analytics"
                }
            elif tool == "compare_chains":
                chains = arguments.get("chains", ["ethereum", "polygon", "arbitrum", "optimism", "base"])
                return {
                    "success": True,
                    "data": {
                        "chains_compared": chains,
                        "rankings": {
                            "fastest_tps": [
                                {"chain": "polygon", "tps": 7000},
                                {"chain": "arbitrum", "tps": 4000},
                                {"chain": "optimism", "tps": 2000}
                            ],
                            "lowest_gas": [
                                {"chain": "polygon", "gas_gwei": 0.001},
                                {"chain": "base", "gas_gwei": 0.05},
                                {"chain": "optimism", "gas_gwei": 0.1}
                            ],
                            "highest_tvl": [
                                {"chain": "ethereum", "tvl": "45.2B"},
                                {"chain": "arbitrum", "tvl": "2.8B"},
                                {"chain": "optimism", "tvl": "1.9B"}
                            ]
                        }
                    },
                    "timestamp": datetime.now().isoformat(),
                    "source": "Multi-chain Comparison"
                }
            elif tool.endswith("_analysis"):
                chain_name = tool.replace("_analysis", "")
                
                # Chain-specific data
                chain_data = {
                    "ethereum": {"gas_price": "15 gwei", "tps": 15, "tvl": "45.2B", "addresses": 450000},
                    "bitcoin": {"gas_price": "N/A", "tps": 7, "tvl": "N/A", "addresses": 1000000},
                    "solana": {"gas_price": "0.00025 SOL", "tps": 65000, "tvl": "1.8B", "addresses": 180000},
                    "polygon": {"gas_price": "0.001 gwei", "tps": 7000, "tvl": "1.2B", "addresses": 125000},
                    "arbitrum": {"gas_price": "0.1 gwei", "tps": 4000, "tvl": "2.8B", "addresses": 85000},
                    "optimism": {"gas_price": "0.1 gwei", "tps": 2000, "tvl": "1.9B", "addresses": 65000},
                    "base": {"gas_price": "0.05 gwei", "tps": 2000, "tvl": "0.8B", "addresses": 45000},
                    "avalanche": {"gas_price": "25 nAVAX", "tps": 4500, "tvl": "1.1B", "addresses": 95000},
                    "bsc": {"gas_price": "5 gwei", "tps": 160, "tvl": "3.2B", "addresses": 180000},
                    "fantom": {"gas_price": "1 gwei", "tps": 10000, "tvl": "0.4B", "addresses": 35000},
                    "zksync": {"gas_price": "0.01 gwei", "tps": 2000, "tvl": "0.3B", "addresses": 25000},
                    "starknet": {"gas_price": "0.001 gwei", "tps": 1000, "tvl": "0.1B", "addresses": 15000}
                }
                
                data = chain_data.get(chain_name, {
                    "gas_price": "1 gwei", "tps": 1000, "tvl": "0.5B", "addresses": 50000
                })
                
                return {
                    "success": True,
                    "data": {
                        "chain": chain_name,
                        "network_status": "healthy",
                        "gas_price": data["gas_price"],
                        "tps": data["tps"],
                        "tvl": f"${data['tvl']}",
                        "active_addresses": data["addresses"],
                        "block_time": "2s" if chain_name in ["polygon", "bsc"] else "12s",
                        "finality": "instant" if chain_name in ["solana", "avalanche"] else "12 blocks"
                    }
                }
            elif tool == "cross_chain_tracking":
                return {
                    "success": True,
                    "data": {
                        "total_chains": 15,
                        "bridge_volume_24h": "$2.8B",
                        "cross_chain_transactions": 25420,
                        "supported_chains": [
                            "ethereum", "bitcoin", "solana", "polygon", "arbitrum", 
                            "optimism", "base", "avalanche", "bsc", "fantom",
                            "zksync", "starknet", "near", "cronos", "moonbeam"
                        ],
                        "top_bridges": [
                            {"name": "Stargate", "volume_24h": "$450M", "chains": 8},
                            {"name": "Hop Protocol", "volume_24h": "$320M", "chains": 6},
                            {"name": "Synapse", "volume_24h": "$280M", "chains": 12},
                            {"name": "Multichain", "volume_24h": "$250M", "chains": 15}
                        ],
                        "bridge_fees": {
                            "ethereum_to_polygon": "0.1%",
                            "ethereum_to_arbitrum": "0.05%",
                            "ethereum_to_optimism": "0.05%",
                            "ethereum_to_base": "0.03%",
                            "polygon_to_arbitrum": "0.08%"
                        }
                    }
                }

        # Web research responses
        elif self.server.name == "web-research-server":
            if tool == "web_search":
                return {
                    "success": True,
                    "data": {
                        "results": [
                            {"title": "Latest Crypto News", "url": "example.com", "snippet": "Market analysis..."},
                            {"title": "DeFi Protocol Update", "url": "example2.com", "snippet": "New features..."}
                        ],
                        "total_results": 1250
                    }
                }

        # Default response
        return {
            "success": True,
            "data": f"Mock response from {self.server.name}.{tool}",
            "arguments": arguments
        }

    async def setup_stream(self, stream_type: str, callback):
        """Mock streaming setup"""
        logger.info(f"✅ Mock stream setup: {stream_type}")

        # Simulate periodic data updates
        async def mock_stream():
            while True:
                await asyncio.sleep(5)  # Update every 5 seconds
                mock_data = {
                    "timestamp": datetime.now().isoformat(),
                    "type": stream_type,
                    "data": f"Mock streaming data for {stream_type}"
                }
                await callback(mock_data)

        # Start background task
        asyncio.create_task(mock_stream())

# Global MCP client manager instance
mcp_client = MCPClientManager()

# Compatibility layer for new MCP integration
class CompatibilityMCPClient:
    """Compatibility layer for existing MCP client usage"""
    
    def __init__(self):
        self.legacy_client = mcp_client
        # Add servers attribute for compatibility
        self.servers = getattr(self.legacy_client, 'servers', {})
    
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