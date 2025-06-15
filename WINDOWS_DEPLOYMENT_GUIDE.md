# Möbius AI Assistant - Windows PowerShell Deployment Guide

## Prerequisites

### 1. Install Python 3.12+
```powershell
# Download and install Python from python.org
# Or use winget
winget install Python.Python.3.12

# Verify installation
python --version
pip --version
```

### 2. Install Git
```powershell
# Install Git
winget install Git.Git

# Verify installation
git --version
```

### 3. Install Visual Studio Build Tools (for some dependencies)
```powershell
# Download and install Visual Studio Build Tools
# Or use winget
winget install Microsoft.VisualStudio.2022.BuildTools
```

## Installation Steps

### 1. Clone Repository
```powershell
# Clone the repository
git clone https://github.com/jeyn69/mobius.git
cd mobius

# Verify you're in the right directory
Get-Location
```

### 2. Create Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If execution policy prevents activation, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activation again
.\venv\Scripts\Activate.ps1

# Verify activation (you should see (venv) in prompt)
```

### 3. Install Dependencies
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install compatible dependencies
pip install -r requirements_clean.txt

# If you encounter conflicts, force reinstall
pip install -r requirements_clean.txt --force-reinstall --no-deps

# Verify critical packages
pip list | Select-String "telegram|fastmcp|aiohttp"
```

### 4. Environment Configuration
```powershell
# Create .env file
New-Item -Path ".env" -ItemType File

# Edit .env file with your configuration
notepad .env
```

Add the following to your `.env` file:
```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# AI Provider Keys (at least one required)
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Database Configuration
DATABASE_URL=sqlite:///data/user_context.db

# Security
ENCRYPTION_KEY=your_32_character_encryption_key_here

# MCP Server Configuration
MCP_FINANCIAL_PORT=8011
MCP_WEB_RESEARCH_PORT=8013
MCP_BLOCKCHAIN_PORT=8012

# Optional: External API Keys for real data
COINGECKO_API_KEY=your_coingecko_key
DEFILLAMA_API_KEY=your_defillama_key
```

### 5. Initialize Database
```powershell
# Create data directory
New-Item -Path "data" -ItemType Directory -Force

# Initialize database
python -c "from src.user_db import init_db; init_db()"
```

### 6. Start MCP Servers (Real Data)
```powershell
# Start financial data server
Start-Process python -ArgumentList "src/mcp_servers/real_financial_server.py --port 8011" -WindowStyle Hidden

# Start web research server  
Start-Process python -ArgumentList "src/mcp_servers/real_web_research_server.py --port 8013" -WindowStyle Hidden

# Start blockchain analytics server
Start-Process python -ArgumentList "src/mcp_servers/real_blockchain_server.py --port 8012" -WindowStyle Hidden

# Wait for servers to start
Start-Sleep -Seconds 5

# Verify servers are running
Test-NetConnection -ComputerName localhost -Port 8011
Test-NetConnection -ComputerName localhost -Port 8013
Test-NetConnection -ComputerName localhost -Port 8012
```

### 7. Run Comprehensive Tests
```powershell
# Run the comprehensive test suite
python test_comprehensive_agent.py

# Check test results
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All tests passed! Ready to deploy." -ForegroundColor Green
} else {
    Write-Host "❌ Some tests failed. Check logs." -ForegroundColor Red
}
```

### 8. Start the Bot
```powershell
# Start the main bot
python src/main.py

# Or run in background
Start-Process python -ArgumentList "src/main.py" -WindowStyle Hidden
```

## AI Interactive Shell Setup

### 1. Install Additional Dependencies
```powershell
# Install interactive shell dependencies
pip install ipython rich prompt-toolkit
```

### 2. Create Interactive Shell Script
```powershell
# Create interactive shell script
New-Item -Path "interactive_shell.py" -ItemType File
```

Add this content to `interactive_shell.py`:
```python
#!/usr/bin/env python3
"""
Möbius AI Interactive Shell for Windows PowerShell
"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

console = Console()

async def interactive_shell():
    """Interactive AI shell"""
    console.print(Panel.fit("🤖 Möbius AI Interactive Shell", style="bold blue"))
    
    try:
        from mcp_natural_language import process_natural_language
        from mcp_client import mcp_client
        
        # Initialize MCP
        await mcp_client.initialize_servers()
        await mcp_client.connect_to_servers()
        
        console.print("✅ MCP servers connected", style="green")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                
                # Process with AI
                console.print("🤔 Processing...", style="yellow")
                
                result = await process_natural_language(
                    12345,  # Test user ID
                    user_input,
                    {"chat_type": "private"}
                )
                
                if result and result.get("success"):
                    response = result["response"]["message"]
                    console.print(f"\n[bold green]Möbius[/bold green]: {response}")
                else:
                    console.print("\n[bold red]Error[/bold red]: Could not process request")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"\n[bold red]Error[/bold red]: {e}")
        
        console.print("\n👋 Goodbye!", style="blue")
        
    except Exception as e:
        console.print(f"❌ Failed to start interactive shell: {e}", style="red")

if __name__ == "__main__":
    asyncio.run(interactive_shell())
```

### 3. Run Interactive Shell
```powershell
# Start interactive shell
python interactive_shell.py
```

## Troubleshooting

### Common Issues and Solutions

#### 1. PowerShell Execution Policy
```powershell
# If you get execution policy errors
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Port Already in Use
```powershell
# Find processes using ports
Get-NetTCPConnection -LocalPort 8011,8012,8013

# Kill processes if needed
Stop-Process -Id <ProcessId> -Force
```

#### 3. Dependency Conflicts
```powershell
# Clean install
pip uninstall -y -r requirements.txt
pip install -r requirements_clean.txt --no-cache-dir
```

#### 4. Missing Visual C++ Build Tools
```powershell
# Install build tools
winget install Microsoft.VisualStudio.2022.BuildTools

# Or download from Microsoft website
```

#### 5. SSL Certificate Issues
```powershell
# Update certificates
pip install --upgrade certifi

# Or set environment variable
$env:REQUESTS_CA_BUNDLE = "path\to\cacert.pem"
```

## Production Deployment

### 1. Windows Service Setup
```powershell
# Install NSSM (Non-Sucking Service Manager)
winget install NSSM.NSSM

# Create service
nssm install MobiusBot "C:\path\to\python.exe" "C:\path\to\mobius\src\main.py"
nssm set MobiusBot AppDirectory "C:\path\to\mobius"
nssm set MobiusBot DisplayName "Möbius AI Assistant"
nssm set MobiusBot Description "Telegram AI Assistant with MCP Integration"

# Start service
nssm start MobiusBot
```

### 2. Firewall Configuration
```powershell
# Allow MCP server ports
New-NetFirewallRule -DisplayName "Mobius MCP Financial" -Direction Inbound -Port 8011 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Mobius MCP Web Research" -Direction Inbound -Port 8013 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Mobius MCP Blockchain" -Direction Inbound -Port 8012 -Protocol TCP -Action Allow
```

### 3. Monitoring Setup
```powershell
# Create monitoring script
New-Item -Path "monitor.ps1" -ItemType File
```

Add monitoring content:
```powershell
# Monitor Möbius services
while ($true) {
    $processes = Get-Process python -ErrorAction SilentlyContinue
    if ($processes.Count -lt 4) {
        Write-Host "⚠️ Some services may be down" -ForegroundColor Yellow
        # Restart services
        nssm restart MobiusBot
    }
    
    # Check MCP server health
    $ports = @(8011, 8012, 8013)
    foreach ($port in $ports) {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
        if (-not $connection.TcpTestSucceeded) {
            Write-Host "❌ Port $port not responding" -ForegroundColor Red
        }
    }
    
    Start-Sleep -Seconds 60
}
```

## Performance Optimization

### 1. Memory Management
```powershell
# Set Python memory limits
$env:PYTHONMALLOC = "malloc"
$env:PYTHONHASHSEED = "0"
```

### 2. Process Priority
```powershell
# Set high priority for main bot process
Get-Process python | Where-Object {$_.MainWindowTitle -like "*main.py*"} | ForEach-Object {$_.PriorityClass = "High"}
```

### 3. Disk I/O Optimization
```powershell
# Move database to SSD if available
# Update DATABASE_URL in .env file
```

## Security Considerations

### 1. Environment Variables
```powershell
# Set system environment variables instead of .env file for production
[Environment]::SetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "your_token", "Machine")
```

### 2. File Permissions
```powershell
# Restrict access to sensitive files
icacls ".env" /grant:r "$env:USERNAME:(R)"
icacls "data" /grant:r "$env:USERNAME:(F)"
```

### 3. Network Security
```powershell
# Bind MCP servers to localhost only
# Configure Windows Defender firewall rules
```

## Maintenance

### 1. Log Rotation
```powershell
# Create log rotation script
# Use Windows Task Scheduler for automated cleanup
```

### 2. Backup Strategy
```powershell
# Backup database and configuration
Copy-Item "data\*" "backup\$(Get-Date -Format 'yyyy-MM-dd')" -Recurse
```

### 3. Updates
```powershell
# Update dependencies
pip install --upgrade -r requirements_clean.txt

# Restart services
nssm restart MobiusBot
```

## Support

For issues specific to Windows deployment:
1. Check Windows Event Viewer for service errors
2. Review PowerShell execution policies
3. Verify all dependencies are installed correctly
4. Test network connectivity to external APIs

## Quick Start Script

Save this as `quick_start.ps1`:
```powershell
# Möbius Quick Start Script for Windows
Write-Host "🚀 Starting Möbius AI Assistant..." -ForegroundColor Cyan

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start MCP servers
Start-Process python -ArgumentList "src/mcp_servers/real_financial_server.py --port 8011" -WindowStyle Hidden
Start-Process python -ArgumentList "src/mcp_servers/real_web_research_server.py --port 8013" -WindowStyle Hidden
Start-Process python -ArgumentList "src/mcp_servers/real_blockchain_server.py --port 8012" -WindowStyle Hidden

# Wait for servers
Start-Sleep -Seconds 5

# Start main bot
python src/main.py
```

Run with:
```powershell
.\quick_start.ps1
```