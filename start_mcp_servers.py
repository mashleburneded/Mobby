#!/usr/bin/env python3
"""
Start MCP Servers - Launch all FastMCP servers for Möbius AI Assistant
"""

import asyncio
import subprocess
import sys
import time
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServerManager:
    """Manage multiple MCP servers"""
    
    def __init__(self):
        self.servers = {
            "financial": {
                "script": "src/mcp_servers/financial_server.py",
                "port": 8001,
                "name": "Financial Data Server"
            },
            "web": {
                "script": "src/mcp_servers/web_research_server.py", 
                "port": 8002,
                "name": "Web Research Server"
            },
            "blockchain": {
                "script": "src/mcp_servers/blockchain_server.py",
                "port": 8003,
                "name": "Blockchain Analytics Server"
            }
        }
        self.processes = {}
    
    def start_server(self, server_name: str, config: dict):
        """Start a single MCP server"""
        try:
            script_path = Path(config["script"])
            if not script_path.exists():
                logger.error(f"❌ Server script not found: {script_path}")
                return None
            
            # Start the server process with proper environment
            cmd = [sys.executable, str(script_path)]
            env = {
                **os.environ,
                "PORT": str(config["port"]),
                "HOST": "0.0.0.0",
                "PYTHONPATH": str(Path.cwd() / "src")
            }
            
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            logger.info(f"✅ Started {config['name']} on port {config['port']} (PID: {process.pid})")
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start {server_name}: {e}")
            return None
    
    def start_all_servers(self):
        """Start all MCP servers"""
        logger.info("🚀 Starting MCP servers...")
        
        for server_name, config in self.servers.items():
            process = self.start_server(server_name, config)
            if process:
                self.processes[server_name] = process
                time.sleep(1)  # Give server time to start
        
        logger.info(f"✅ Started {len(self.processes)} MCP servers")
        return len(self.processes) > 0
    
    def stop_all_servers(self):
        """Stop all MCP servers"""
        logger.info("🛑 Stopping MCP servers...")
        
        for server_name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ Stopped {server_name}")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"⚠️ Force killed {server_name}")
            except Exception as e:
                logger.error(f"❌ Error stopping {server_name}: {e}")
        
        self.processes.clear()
    
    def check_server_health(self):
        """Check if all servers are running"""
        healthy_count = 0
        
        for server_name, process in self.processes.items():
            if process.poll() is None:  # Process is still running
                healthy_count += 1
            else:
                logger.warning(f"⚠️ Server {server_name} has stopped")
        
        return healthy_count == len(self.processes)

async def test_mcp_integration():
    """Test MCP integration with the AI orchestrator"""
    try:
        # Import after servers are started
        sys.path.insert(0, 'src')
        from mcp_ai_orchestrator import ai_orchestrator
        
        logger.info("🧪 Testing MCP integration...")
        
        # Test different query types
        test_queries = [
            ("What's the current Bitcoin price?", "market_research"),
            ("Analyze wallet 0x742d35Cc6634C0532925a3b8D4C9db96", "blockchain_analysis"),
            ("What's the sentiment around Ethereum?", "social_sentiment"),
            ("Search for latest DeFi news", "general_chat")
        ]
        
        for query, expected_type in test_queries:
            logger.info(f"Testing: {query}")
            result = await ai_orchestrator.generate_enhanced_response(query)
            
            if result["success"]:
                logger.info(f"✅ Query successful - Type: {result.get('query_type', 'unknown')}")
                logger.info(f"   Sources: {result.get('context_sources', [])}")
            else:
                logger.error(f"❌ Query failed: {result.get('error', 'Unknown error')}")
        
        logger.info("✅ MCP integration test completed")
        
    except Exception as e:
        logger.error(f"❌ MCP integration test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to start servers and test integration"""
    import os
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    manager = MCPServerManager()
    
    try:
        # Start all servers
        if manager.start_all_servers():
            logger.info("🎉 All MCP servers started successfully!")
            
            # Wait a moment for servers to fully initialize
            time.sleep(3)
            
            # Test integration
            asyncio.run(test_mcp_integration())
            
            # Keep servers running
            logger.info("🔄 MCP servers running. Press Ctrl+C to stop...")
            try:
                while True:
                    time.sleep(10)
                    if not manager.check_server_health():
                        logger.warning("⚠️ Some servers are not healthy")
                        break
            except KeyboardInterrupt:
                logger.info("🛑 Received stop signal")
        else:
            logger.error("❌ Failed to start MCP servers")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        return 1
    finally:
        manager.stop_all_servers()
        logger.info("✅ MCP servers stopped")
    
    return 0

if __name__ == "__main__":
    exit(main())