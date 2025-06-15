#!/usr/bin/env python3
"""
MCP Server Manager - Automatic startup and management of MCP servers
Integrates with the main bot to ensure MCP servers are always available
"""

import asyncio
import logging
import subprocess
import sys
import os
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class MCPServerManager:
    """Manages MCP servers lifecycle alongside the main bot"""
    
    def __init__(self):
        self.processes: List[Tuple[subprocess.Popen, str, int]] = []
        self.running = False
        self.startup_timeout = 30  # seconds
        self.health_check_interval = 30  # seconds
        self.restart_attempts = 3
        
        # Server configurations
        self.servers = [
            {
                "script": "mcp_servers/real_financial_server.py",
                "port": 8011,
                "name": "Real Financial Data Server",
                "health_endpoint": "/health"
            },
            {
                "script": "mcp_servers/real_blockchain_server.py", 
                "port": 8012,
                "name": "Real Blockchain Analytics Server",
                "health_endpoint": "/health"
            },
            {
                "script": "mcp_servers/real_web_research_server.py",
                "port": 8013,
                "name": "Real Web Research Server",
                "health_endpoint": "/health"
            }
        ]
    
    async def start_all_servers(self) -> bool:
        """Start all MCP servers"""
        logger.info("🏭 Starting MCP Server Infrastructure...")
        
        self.running = True
        success_count = 0
        
        for server in self.servers:
            if await self._start_server(server):
                success_count += 1
            else:
                logger.error(f"❌ Failed to start {server['name']}")
        
        if success_count > 0:
            logger.info(f"✅ Started {success_count}/{len(self.servers)} MCP servers")
            
            # Start health monitoring in background
            asyncio.create_task(self._monitor_servers())
            
            return True
        else:
            logger.error("❌ No MCP servers could be started")
            return False
    
    async def _start_server(self, server_config: Dict) -> bool:
        """Start a single MCP server"""
        try:
            script_path = Path(__file__).parent / server_config["script"]
            
            if not script_path.exists():
                logger.error(f"❌ Server script not found: {script_path}")
                return False
            
            logger.info(f"🚀 Starting {server_config['name']} on port {server_config['port']}")
            
            # Set up environment
            env = os.environ.copy()
            env['PYTHONPATH'] = str(Path(__file__).parent)
            
            # Start the server process
            process = subprocess.Popen([
                sys.executable, str(script_path)
            ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            env=env,
            cwd=Path(__file__).parent
            )
            
            # Wait for server to start
            if await self._wait_for_server_startup(server_config['port'], self.startup_timeout):
                self.processes.append((process, server_config['name'], server_config['port']))
                logger.info(f"✅ {server_config['name']} started successfully (PID: {process.pid})")
                return True
            else:
                logger.error(f"❌ {server_config['name']} failed to start within {self.startup_timeout}s")
                process.terminate()
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting {server_config['name']}: {e}")
            return False
    
    async def _wait_for_server_startup(self, port: int, timeout: int) -> bool:
        """Wait for server to become available"""
        import aiohttp
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://localhost:{port}/health", 
                                         timeout=aiohttp.ClientTimeout(total=2)) as response:
                        if response.status == 200:
                            return True
            except:
                pass
            
            await asyncio.sleep(1)
        
        return False
    
    async def _monitor_servers(self):
        """Monitor server health and restart if needed"""
        while self.running:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for i, (process, name, port) in enumerate(self.processes):
                    # Check if process is still running
                    if process.poll() is not None:
                        logger.warning(f"⚠️ {name} has stopped (exit code: {process.returncode})")
                        
                        # Find server config for restart
                        server_config = next((s for s in self.servers if s['port'] == port), None)
                        if server_config:
                            logger.info(f"🔄 Attempting to restart {name}...")
                            
                            if await self._start_server(server_config):
                                # Update process list
                                new_process = self.processes[-1][0]  # Last added process
                                self.processes[i] = (new_process, name, port)
                                logger.info(f"✅ Successfully restarted {name}")
                            else:
                                logger.error(f"❌ Failed to restart {name}")
                    
                    # Health check for running processes
                    else:
                        try:
                            import aiohttp
                            async with aiohttp.ClientSession() as session:
                                async with session.get(f"http://localhost:{port}/health", 
                                                     timeout=aiohttp.ClientTimeout(total=5)) as response:
                                    if response.status != 200:
                                        logger.warning(f"⚠️ {name} health check failed (HTTP {response.status})")
                        except Exception as e:
                            logger.warning(f"⚠️ {name} health check failed: {e}")
                            
            except Exception as e:
                logger.error(f"❌ Error in server monitoring: {e}")
    
    async def stop_all_servers(self):
        """Stop all MCP servers gracefully"""
        logger.info("🛑 Stopping all MCP servers...")
        self.running = False
        
        for process, name, port in self.processes:
            try:
                logger.info(f"🛑 Stopping {name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    logger.info(f"✅ Gracefully stopped {name}")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Force killing {name}...")
                    process.kill()
                    process.wait()
                    logger.info(f"🔪 Force killed {name}")
                    
            except Exception as e:
                logger.error(f"❌ Error stopping {name}: {e}")
        
        self.processes.clear()
        logger.info("🏁 All MCP servers stopped")
    
    def get_server_status(self) -> Dict[str, Dict]:
        """Get status of all servers"""
        status = {}
        
        for process, name, port in self.processes:
            is_running = process.poll() is None
            status[name] = {
                "running": is_running,
                "port": port,
                "pid": process.pid if is_running else None,
                "url": f"http://localhost:{port}"
            }
        
        return status
    
    async def restart_server(self, server_name: str) -> bool:
        """Restart a specific server"""
        # Find the server
        for i, (process, name, port) in enumerate(self.processes):
            if name == server_name:
                logger.info(f"🔄 Restarting {server_name}...")
                
                # Stop the current process
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                # Find server config
                server_config = next((s for s in self.servers if s['port'] == port), None)
                if server_config and await self._start_server(server_config):
                    # Update process list
                    new_process = self.processes[-1][0]  # Last added process
                    self.processes[i] = (new_process, name, port)
                    logger.info(f"✅ Successfully restarted {server_name}")
                    return True
                else:
                    logger.error(f"❌ Failed to restart {server_name}")
                    return False
        
        logger.error(f"❌ Server {server_name} not found")
        return False

# Global server manager instance
mcp_server_manager = MCPServerManager()

async def initialize_mcp_servers() -> bool:
    """Initialize MCP servers - called from main bot startup"""
    try:
        logger.info("🔧 Initializing MCP Server Infrastructure...")
        success = await mcp_server_manager.start_all_servers()
        
        if success:
            logger.info("✅ MCP Server Infrastructure ready")
            
            # Log server status
            status = mcp_server_manager.get_server_status()
            for server_name, info in status.items():
                if info['running']:
                    logger.info(f"   🟢 {server_name}: {info['url']} (PID: {info['pid']})")
                else:
                    logger.warning(f"   🔴 {server_name}: Not running")
        else:
            logger.warning("⚠️ MCP Server Infrastructure partially failed")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize MCP servers: {e}")
        return False

async def shutdown_mcp_servers():
    """Shutdown MCP servers - called from main bot shutdown"""
    try:
        await mcp_server_manager.stop_all_servers()
    except Exception as e:
        logger.error(f"❌ Error shutting down MCP servers: {e}")

def get_mcp_server_status() -> Dict[str, Dict]:
    """Get current status of all MCP servers"""
    return mcp_server_manager.get_server_status()

async def restart_mcp_server(server_name: str) -> bool:
    """Restart a specific MCP server"""
    return await mcp_server_manager.restart_server(server_name)

# Signal handlers for graceful shutdown
def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info(f"📡 Received signal {signum}, shutting down MCP servers...")
        asyncio.create_task(shutdown_mcp_servers())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    # For testing the server manager standalone
    async def test_manager():
        setup_signal_handlers()
        
        if await initialize_mcp_servers():
            logger.info("🎯 MCP servers running. Press Ctrl+C to stop.")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                pass
        
        await shutdown_mcp_servers()
    
    asyncio.run(test_manager())