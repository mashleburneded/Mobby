# 🚀 Möbius AI Assistant - Production Deployment Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Linux/macOS Deployment](#linuxmacos-deployment)
3. [Windows PowerShell Deployment](#windows-powershell-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Production Deployment](#production-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Troubleshooting](#troubleshooting)
8. [Monitoring & Maintenance](#monitoring--maintenance)

## 🔧 Prerequisites

### System Requirements
- **Python**: 3.12 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Stable internet connection

### Required API Keys
- **Telegram Bot Token** (Required) - Get from [@BotFather](https://t.me/botfather)
- **Groq API Key** (Required) - Get from [Groq Console](https://console.groq.com)
- **CoinGecko API Key** (Optional) - For enhanced rate limits
- **Whop API Key** (Optional) - For premium features

## 🐧 Linux/macOS Deployment

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/jeyn69/mobius.git
cd mobius

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with your API keys

# 5. Initialize database
mkdir -p data
python -c "import sys; sys.path.append('src'); from user_db import init_db; init_db()"

# 6. Test installation
python test_comprehensive_corporate_standard.py

# 7. Start the bot
python src/main.py
```

### Detailed Linux Setup

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12
sudo apt install python3.12 python3.12-venv python3.12-dev -y

# Install system dependencies
sudo apt install git curl build-essential -y

# Clone and setup
git clone https://github.com/jeyn69/mobius.git
cd mobius
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### CentOS/RHEL/Fedora
```bash
# Install Python 3.12
sudo dnf install python3.12 python3.12-venv python3.12-devel -y

# Install dependencies
sudo dnf install git curl gcc gcc-c++ make -y

# Setup project
git clone https://github.com/jeyn69/mobius.git
cd mobius
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.12
brew install python@3.12

# Setup project
git clone https://github.com/jeyn69/mobius.git
cd mobius
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 🪟 Windows PowerShell Deployment

### Prerequisites for Windows
```powershell
# Check PowerShell version (should be 5.1+)
$PSVersionTable.PSVersion

# Install Python 3.12 from Microsoft Store or python.org
# Verify installation
python --version
```

### Windows Quick Start
```powershell
# 1. Clone repository
git clone https://github.com/jeyn69/mobius.git
cd mobius

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
notepad .env  # Edit with your API keys

# 5. Initialize database
mkdir data -Force
python -c "import sys; sys.path.append('src'); from user_db import init_db; init_db()"

# 6. Test installation
python test_comprehensive_corporate_standard.py

# 7. Start the bot
python src/main.py
```

### Windows Detailed Setup

#### Install Python 3.12
```powershell
# Option 1: Microsoft Store
winget install Python.Python.3.12

# Option 2: Direct download
# Download from https://www.python.org/downloads/windows/
# Make sure to check "Add Python to PATH"

# Verify installation
python --version
pip --version
```

#### Install Git
```powershell
# Install Git for Windows
winget install Git.Git

# Or download from https://git-scm.com/download/win
```

#### Setup Project
```powershell
# Create project directory
mkdir C:\Projects
cd C:\Projects

# Clone repository
git clone https://github.com/jeyn69/mobius.git
cd mobius

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
python -m pip install -r requirements.txt
```

#### Windows-Specific Configuration
```powershell
# Set execution policy (if needed)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Create data directory
New-Item -ItemType Directory -Force -Path "data"

# Copy environment template
Copy-Item ".env.example" ".env"

# Edit environment file
notepad .env
```

### Windows Service Installation
```powershell
# Install as Windows Service using NSSM
# Download NSSM from https://nssm.cc/download

# Install service
nssm install MobiusBot "C:\Projects\mobius\venv\Scripts\python.exe"
nssm set MobiusBot Arguments "C:\Projects\mobius\src\main.py"
nssm set MobiusBot AppDirectory "C:\Projects\mobius"
nssm set MobiusBot DisplayName "Möbius AI Assistant"
nssm set MobiusBot Description "AI-powered Telegram bot for crypto research"

# Start service
nssm start MobiusBot

# Check service status
nssm status MobiusBot
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Create data directory
RUN mkdir -p data

# Expose port (if needed for health checks)
EXPOSE 8080

# Run the application
CMD ["python", "src/main.py"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  mobius:
    build: .
    container_name: mobius-ai
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - mobius-network

  redis:
    image: redis:7-alpine
    container_name: mobius-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - mobius-network

networks:
  mobius-network:
    driver: bridge

volumes:
  redis_data:
```

### Docker Commands
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f mobius

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build
```

## 🏭 Production Deployment

### VPS/Cloud Deployment

#### DigitalOcean Droplet
```bash
# Create Ubuntu 22.04 droplet (minimum 2GB RAM)
# SSH into droplet

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.12 python3.12-venv git nginx certbot -y

# Setup application
git clone https://github.com/jeyn69/mobius.git
cd mobius
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env

# Create systemd service
sudo nano /etc/systemd/system/mobius.service
```

#### Systemd Service File
```ini
[Unit]
Description=Möbius AI Assistant
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/mobius
Environment=PATH=/home/ubuntu/mobius/venv/bin
ExecStart=/home/ubuntu/mobius/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Start Service
```bash
# Reload systemd and start service
sudo systemctl daemon-reload
sudo systemctl enable mobius
sudo systemctl start mobius

# Check status
sudo systemctl status mobius

# View logs
sudo journalctl -u mobius -f
```

### AWS EC2 Deployment
```bash
# Launch EC2 instance (t3.medium recommended)
# Security group: Allow SSH (22) and HTTPS (443)

# Connect via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install python3.12 python3.12-venv git -y

# Setup application (same as above)
# Configure Auto Scaling Group for high availability
```

### Google Cloud Platform
```bash
# Create Compute Engine instance
gcloud compute instances create mobius-bot \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --zone=us-central1-a

# SSH and setup (same as above)
```

## ⚙️ Environment Configuration

### Required Environment Variables
```env
# REQUIRED - Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_group_chat_id

# REQUIRED - AI Provider
GROQ_API_KEY=your_groq_api_key

# REQUIRED - Security
ENCRYPTION_KEY=your_32_byte_fernet_encryption_key
BOT_MASTER_ENCRYPTION_KEY=your_master_encryption_key

# OPTIONAL - Enhanced Features
COINGECKO_API_KEY=your_coingecko_api_key
WHOP_API_KEY=your_whop_api_key
ETHEREUM_RPC_URL=your_ethereum_rpc_endpoint

# OPTIONAL - Additional AI Providers
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_google_gemini_api_key

# OPTIONAL - External Services
ARKHAM_API_KEY=your_arkham_intelligence_key
NANSEN_API_KEY=your_nansen_api_key
```

### Generate Encryption Keys
```python
# Generate Fernet encryption key
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

```bash
# Or use command line
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Get Telegram Chat ID
```bash
# Method 1: Use @userinfobot in your group
# Method 2: Use Telegram API
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

## 🔧 Troubleshooting

### Common Issues

#### Import Errors
```bash
# Fix: Install missing dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Permission Errors (Linux)
```bash
# Fix file permissions
chmod +x src/main.py
chown -R $USER:$USER .
```

#### Port Already in Use
```bash
# Find process using port
lsof -i :8011
netstat -tulpn | grep 8011

# Kill process
kill -9 <PID>
```

#### Database Errors
```bash
# Reinitialize database
rm -f data/user_data.sqlite
python -c "import sys; sys.path.append('src'); from user_db import init_db; init_db()"
```

#### MCP Server Issues
```bash
# Check server status
curl http://localhost:8011/health
curl http://localhost:8012/health
curl http://localhost:8013/health
curl http://localhost:8014/health

# Restart servers
pkill -f "mcp_servers"
python src/main.py
```

### Windows-Specific Issues

#### PowerShell Execution Policy
```powershell
# Fix execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Virtual Environment Activation
```powershell
# If activation fails
.\venv\Scripts\Activate.ps1

# Alternative
.\venv\Scripts\activate.bat
```

#### Path Issues
```powershell
# Add Python to PATH
$env:PATH += ";C:\Python312;C:\Python312\Scripts"

# Permanent fix
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Python312;C:\Python312\Scripts", "User")
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check bot status
curl http://localhost:8080/health

# Check MCP servers
python -c "
import sys
sys.path.append('src')
from mcp_client import mcp_client
print('MCP Status:', mcp_client.get_status())
"
```

### Log Monitoring
```bash
# View real-time logs
tail -f logs/mobius.log

# Search for errors
grep -i error logs/mobius.log

# Monitor system resources
htop
df -h
free -h
```

### Backup Strategy
```bash
# Backup database
cp data/user_data.sqlite backups/user_data_$(date +%Y%m%d).sqlite

# Backup configuration
cp .env backups/env_$(date +%Y%m%d).backup

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups
cp data/user_data.sqlite backups/user_data_$DATE.sqlite
cp .env backups/env_$DATE.backup
echo "Backup completed: $DATE"
```

### Performance Monitoring
```python
# Monitor memory usage
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Memory usage: {memory_mb:.1f} MB")
```

### Update Procedure
```bash
# 1. Backup current installation
cp -r mobius mobius_backup_$(date +%Y%m%d)

# 2. Pull latest changes
cd mobius
git pull origin master

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Run tests
python test_comprehensive_corporate_standard.py

# 5. Restart service
sudo systemctl restart mobius
```

## 🚀 Performance Optimization

### System Optimization
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize Python
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1
```

### Database Optimization
```sql
-- SQLite optimization
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = memory;
```

### Memory Management
```python
# Add to main.py
import gc
gc.set_threshold(700, 10, 10)  # Optimize garbage collection
```

## 🔒 Security Hardening

### Firewall Configuration
```bash
# Ubuntu UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 443
sudo ufw deny 8011:8014/tcp  # Block MCP ports from external access
```

### SSL/TLS Setup
```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Environment Security
```bash
# Secure .env file
chmod 600 .env
chown root:root .env

# Use secrets management
# Consider using HashiCorp Vault or AWS Secrets Manager for production
```

---

## 📞 Support

### Getting Help
- **Documentation**: This guide and README.md
- **Issues**: GitHub Issues for bug reports
- **Community**: Telegram support group
- **Enterprise**: Contact for dedicated support

### Useful Commands
```bash
# Quick status check
python -c "
import sys; sys.path.append('src')
from main import *
print('✅ All imports successful')
"

# Test MCP servers
curl -s http://localhost:8011/tools/get_crypto_prices -X POST -H "Content-Type: application/json" -d '{"symbols": ["BTC"]}'

# Check database
python -c "
import sys; sys.path.append('src')
from user_db import *
print('✅ Database accessible')
"
```

---

**🚀 Production Ready • 🔴 Real Data • 🛡️ Enterprise Security**

*For additional support, please refer to the GitHub repository or contact the development team.*