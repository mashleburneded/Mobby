#!/usr/bin/env python3
"""
MCP Integration - Proper integration with FastMCP servers
Handles concurrent startup and intelligent routing
"""

import asyncio
import logging
import subprocess
import sys
import os
import signal
from pathlib import Path
from typing import Dict, Any, Optional, List
import aiohttp
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_mcp_servers():
    """Start all MCP servers"""
    manager = MCPServerManager()
    await manager.start_all_servers()
    return manager

class MCPServerManager:
    """Manages MCP server lifecycle and integration"""
    
    def __init__(self):
        self.server_processes = {}
        self.server_configs = {
            'financial': {
                'script': 'mcp_servers/real_financial_server.py',
                'port': 8001,
                'name': 'Financial Data Server',
                'tools': ['get_price_feeds', 'get_defi_protocols', 'get_yield_farming_opportunities', 'get_market_overview']
            },
            'web_research': {
                'script': 'mcp_servers/web_research_server.py',
                'port': 8002,
                'name': 'Web Research Server',
                'tools': ['web_search', 'fetch_page_content', 'get_crypto_news', 'research_defi_protocol', 'monitor_social_sentiment']
            },
            'blockchain': {
                'script': 'mcp_servers/blockchain_server.py',
                'port': 8003,
                'name': 'Blockchain Analytics Server',
                'tools': ['analyze_wallet_cross_chain', 'get_wallet_balance', 'get_wallet_transactions', 'get_chain_analytics', 'compare_chains']
            }
        }
        self.session = None
        self.running = False
    
    async def start_all_servers(self):
        """Start all MCP servers concurrently"""
        try:
            logger.info("🚀 Starting MCP servers concurrently...")
            
            # Start all servers in parallel
            start_tasks = []
            for server_name, config in self.server_configs.items():
                task = asyncio.create_task(self._start_server(server_name, config))
                start_tasks.append(task)
            
            # Wait for all servers to start
            results = await asyncio.gather(*start_tasks, return_exceptions=True)
            
            # Check results
            successful_starts = 0
            for i, result in enumerate(results):
                server_name = list(self.server_configs.keys())[i]
                if isinstance(result, Exception):
                    logger.error(f"❌ Failed to start {server_name}: {result}")
                else:
                    successful_starts += 1
                    logger.info(f"✅ {server_name} started successfully")
            
            if successful_starts > 0:
                self.running = True
                logger.info(f"🎉 {successful_starts}/{len(self.server_configs)} MCP servers started")
                
                # Initialize HTTP session for health checks
                self.session = aiohttp.ClientSession()
                
                # Wait for servers to be ready
                await self._wait_for_servers_ready()
                
                return True
            else:
                logger.error("❌ No MCP servers started successfully")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start MCP servers: {e}")
            return False
    
    async def _start_server(self, server_name: str, config: Dict[str, Any]):
        """Start individual MCP server"""
        try:
            script_path = Path("src") / config['script']
            if not script_path.exists():
                raise FileNotFoundError(f"Server script not found: {script_path}")
            
            # Set up environment
            env = os.environ.copy()
            env['PYTHONPATH'] = str(Path.cwd() / "src")
            
            # Start server process
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            self.server_processes[server_name] = process
            logger.info(f"🔄 Started {config['name']} (PID: {process.pid})")
            
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start {server_name}: {e}")
            raise
    
    async def _wait_for_servers_ready(self, timeout: int = 30):
        """Wait for all servers to be ready"""
        logger.info("⏳ Waiting for servers to be ready...")
        
        start_time = asyncio.get_event_loop().time()
        ready_servers = set()
        
        while len(ready_servers) < len(self.server_configs) and \
              (asyncio.get_event_loop().time() - start_time) < timeout:
            
            for server_name, config in self.server_configs.items():
                if server_name not in ready_servers:
                    if await self._check_server_health(server_name, config):
                        ready_servers.add(server_name)
                        logger.info(f"✅ {config['name']} is ready")
            
            if len(ready_servers) < len(self.server_configs):
                await asyncio.sleep(1)
        
        if len(ready_servers) == len(self.server_configs):
            logger.info("🎉 All MCP servers are ready!")
        else:
            logger.warning(f"⚠️ Only {len(ready_servers)}/{len(self.server_configs)} servers ready")
    
    async def _check_server_health(self, server_name: str, config: Dict[str, Any]) -> bool:
        """Check if server is healthy"""
        try:
            url = f"http://localhost:{config['port']}/health"
            async with self.session.get(url, timeout=2) as response:
                return response.status == 200
        except:
            return False
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool on a specific MCP server"""
        if not self.running:
            return {"success": False, "error": "MCP servers not running"}
        
        if server_name not in self.server_configs:
            return {"success": False, "error": f"Unknown server: {server_name}"}
        
        config = self.server_configs[server_name]
        
        if tool_name not in config['tools']:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        try:
            # For now, call the info endpoint to simulate tool calls
            # In a real implementation, this would use the MCP protocol
            url = f"http://localhost:{config['port']}/info"
            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    server_info = await response.json()
                    return {
                        "success": True,
                        "data": {
                            "server": server_info,
                            "tool": tool_name,
                            "arguments": arguments or {},
                            "timestamp": datetime.now().isoformat()
                        }
                    }
                else:
                    return {"success": False, "error": f"Server error: {response.status}"}
        
        except Exception as e:
            logger.error(f"❌ Tool call failed {server_name}.{tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers"""
        status = {}
        
        for server_name, config in self.server_configs.items():
            process = self.server_processes.get(server_name)
            is_healthy = await self._check_server_health(server_name, config) if self.session else False
            
            status[server_name] = {
                "name": config['name'],
                "port": config['port'],
                "tools": config['tools'],
                "process_running": process is not None and process.returncode is None,
                "health_check": is_healthy,
                "status": "running" if is_healthy else "error"
            }
        
        return status
    
    async def stop_all_servers(self):
        """Stop all MCP servers"""
        logger.info("🛑 Stopping MCP servers...")
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        # Stop all server processes
        for server_name, process in self.server_processes.items():
            try:
                if process.returncode is None:
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=5)
                        logger.info(f"✅ Stopped {server_name}")
                    except asyncio.TimeoutError:
                        process.kill()
                        await process.wait()
                        logger.warning(f"⚠️ Force killed {server_name}")
            except Exception as e:
                logger.error(f"❌ Error stopping {server_name}: {e}")
        
        self.server_processes.clear()
        self.running = False
        logger.info("🛑 All MCP servers stopped")

# Global MCP server manager
mcp_server_manager = MCPServerManager()

# Enhanced MCP Client with proper FastMCP integration
class EnhancedMCPClient:
    """Enhanced MCP client with intelligent routing and background processing"""
    
    def __init__(self):
        self.intent_patterns = {
            'price': ['price', 'cost', 'value', 'worth', 'usd', 'dollar'],
            'wallet': ['wallet', 'address', 'balance', 'holdings', 'portfolio'],
            'defi': ['defi', 'protocol', 'yield', 'farming', 'liquidity', 'tvl'],
            'news': ['news', 'latest', 'update', 'announcement', 'article'],
            'research': ['research', 'analyze', 'study', 'investigate', 'explore'],
            'market': ['market', 'overview', 'summary', 'trend', 'analysis'],
            'blockchain': ['chain', 'transaction', 'block', 'gas', 'network']
        }
    
    def detect_intent(self, query: str) -> List[str]:
        """Detect user intent from query"""
        query_lower = query.lower()
        detected_intents = []
        
        for intent, keywords in self.intent_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents.append(intent)
        
        return detected_intents
    
    def route_request(self, intents: List[str]) -> Dict[str, List[str]]:
        """Route request to appropriate MCP servers based on intents"""
        routing = {}
        
        for intent in intents:
            if intent in ['price', 'market']:
                if 'financial' not in routing:
                    routing['financial'] = []
                if intent == 'price':
                    routing['financial'].append('get_price_feeds')
                elif intent == 'market':
                    routing['financial'].append('get_market_overview')
            
            elif intent in ['defi']:
                if 'financial' not in routing:
                    routing['financial'] = []
                routing['financial'].extend(['get_defi_protocols', 'get_yield_farming_opportunities'])
            
            elif intent in ['wallet', 'blockchain']:
                if 'blockchain' not in routing:
                    routing['blockchain'] = []
                if intent == 'wallet':
                    routing['blockchain'].extend(['get_wallet_balance', 'analyze_wallet_cross_chain'])
                elif intent == 'blockchain':
                    routing['blockchain'].append('get_chain_analytics')
            
            elif intent in ['news', 'research']:
                if 'web_research' not in routing:
                    routing['web_research'] = []
                if intent == 'news':
                    routing['web_research'].append('get_crypto_news')
                elif intent == 'research':
                    routing['web_research'].extend(['web_search', 'research_defi_protocol'])
        
        return routing
    
    async def enhanced_query_processing(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process query with MCP enhancement in background"""
        try:
            # Detect user intent
            intents = self.detect_intent(query)
            if not intents:
                return {'enhanced': False, 'reason': 'No relevant intents detected'}
            
            # Route to appropriate servers
            routing = self.route_request(intents)
            if not routing:
                return {'enhanced': False, 'reason': 'No servers available for detected intents'}
            
            # Execute calls concurrently in background
            tasks = []
            for server, tools in routing.items():
                for tool in tools:
                    task = asyncio.create_task(
                        mcp_server_manager.call_tool(server, tool, context)
                    )
                    tasks.append((server, tool, task))
            
            # Gather results with timeout
            results = {}
            for server, tool, task in tasks:
                try:
                    result = await asyncio.wait_for(task, timeout=5.0)
                    if result and result.get('success'):
                        if server not in results:
                            results[server] = {}
                        results[server][tool] = result
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout calling {server}.{tool}")
                except Exception as e:
                    logger.error(f"Error in task {server}.{tool}: {e}")
            
            return {
                'enhanced': True,
                'intents': intents,
                'routing': routing,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced query processing: {e}")
            return {'enhanced': False, 'error': str(e)}

# Global enhanced MCP client
enhanced_mcp_client = EnhancedMCPClient()

# Convenience functions
async def start_mcp_integration():
    """Start MCP integration"""
    return await mcp_server_manager.start_all_servers()

async def stop_mcp_integration():
    """Stop MCP integration"""
    await mcp_server_manager.stop_all_servers()

async def enhance_query(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Enhance query with MCP capabilities"""
    return await enhanced_mcp_client.enhanced_query_processing(query, context)

async def get_mcp_status() -> Dict[str, Any]:
    """Get MCP server status"""
    return await mcp_server_manager.get_server_status()

async def call_mcp_tool(server: str, tool: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
    """Call MCP tool"""
    return await mcp_server_manager.call_tool(server, tool, arguments)