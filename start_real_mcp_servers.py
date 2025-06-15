#!/usr/bin/env python3
"""
Start all Real MCP servers for Möbius AI Assistant
Production-grade MCP server infrastructure
"""

import asyncio
import subprocess
import sys
import time
import logging
import signal
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPServerManager:
    """Manages multiple MCP servers"""
    
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_server(self, script_path: str, port: int, name: str):
        """Start an MCP server"""
        try:
            logger.info(f"🚀 Starting {name} on port {port}")
            
            # Ensure the script is executable
            script_path = Path(script_path)
            if not script_path.exists():
                logger.error(f"❌ Server script not found: {script_path}")
                return None
            
            # Start the server process
            env = os.environ.copy()
            env['PYTHONPATH'] = str(Path.cwd() / 'src')
            
            process = subprocess.Popen([
                sys.executable, str(script_path)
            ], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            env=env,
            cwd=Path.cwd()
            )
            
            logger.info(f"✅ {name} started with PID {process.pid}")
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")
            return None
    
    def start_all_servers(self):
        """Start all MCP servers"""
        logger.info("🏭 Starting Möbius Real MCP Server Infrastructure")
        logger.info("=" * 70)
        
        # Real server configurations
        servers = [
            {
                "script": "src/mcp_servers/real_financial_server.py",
                "port": 8001,
                "name": "Real Financial Data Server"
            },
            {
                "script": "src/mcp_servers/real_blockchain_server.py", 
                "port": 8002,
                "name": "Real Blockchain Analytics Server"
            },
            {
                "script": "src/mcp_servers/real_web_research_server.py",
                "port": 8003,
                "name": "Real Web Research Server"
            }
        ]
        
        for server in servers:
            process = self.start_server(server["script"], server["port"], server["name"])
            if process:
                self.processes.append((process, server["name"], server["port"]))
        
        if self.processes:
            logger.info(f"\n✅ Started {len(self.processes)} Real MCP servers")
            logger.info("🔗 Server URLs:")
            for process, name, port in self.processes:
                logger.info(f"   • {name}: http://localhost:{port}")
            
            logger.info("\n🛠️  Server Tools Available:")
            logger.info("   💰 Financial: get_crypto_prices, get_market_data, get_defi_protocols, analyze_price_movement")
            logger.info("   ⛓️  Blockchain: get_wallet_balance, get_transaction_history, track_whale_movements")
            logger.info("   🌐 Web Research: web_search, extract_webpage_content, research_topic")
            
            logger.info("\n📋 To stop servers, press Ctrl+C")
            return True
        else:
            logger.error("❌ No Real MCP servers could be started")
            return False
    
    def monitor_servers(self):
        """Monitor server health"""
        try:
            while self.running:
                time.sleep(5)  # Check every 5 seconds
                
                # Check if any process has died
                for i, (process, name, port) in enumerate(self.processes):
                    if process.poll() is not None:
                        logger.error(f"❌ {name} has stopped unexpectedly (exit code: {process.returncode})")
                        
                        # Try to restart the server
                        logger.info(f"🔄 Attempting to restart {name}...")
                        if name == "Real Financial Data Server":
                            new_process = self.start_server("src/mcp_servers/real_financial_server.py", port, name)
                        elif name == "Real Blockchain Analytics Server":
                            new_process = self.start_server("src/mcp_servers/real_blockchain_server.py", port, name)
                        elif name == "Real Web Research Server":
                            new_process = self.start_server("src/mcp_servers/real_web_research_server.py", port, name)
                        else:
                            new_process = None
                        
                        if new_process:
                            self.processes[i] = (new_process, name, port)
                            logger.info(f"✅ Successfully restarted {name}")
                        else:
                            logger.error(f"❌ Failed to restart {name}")
                            
        except KeyboardInterrupt:
            self.stop_all_servers()
    
    def stop_all_servers(self):
        """Stop all MCP servers"""
        logger.info("\n🛑 Stopping all Real MCP servers...")
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
        
        logger.info("🏁 All Real MCP servers stopped")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"\n📡 Received signal {signum}, shutting down...")
    global server_manager
    if server_manager:
        server_manager.stop_all_servers()
    sys.exit(0)

# Global server manager
server_manager = None

def main():
    """Main server management function"""
    global server_manager
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    server_manager = MCPServerManager()
    
    # Start all servers
    if server_manager.start_all_servers():
        logger.info("\n🎯 Real MCP Server Infrastructure is ready!")
        logger.info("🔄 Monitoring server health...")
        
        # Monitor servers
        server_manager.monitor_servers()
    else:
        logger.error("❌ Failed to start MCP server infrastructure")
        sys.exit(1)

if __name__ == "__main__":
    main()