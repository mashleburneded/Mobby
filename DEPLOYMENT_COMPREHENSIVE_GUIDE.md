# 🚀 Möbius AI Assistant - Comprehensive Deployment Guide

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [AI Provider Setup](#ai-provider-setup)
6. [Database Initialization](#database-initialization)
7. [Production Deployment](#production-deployment)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Features](#advanced-features)

## 🔧 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **Python**: 3.12 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space minimum
- **Network**: Stable internet connection for API access

### Required API Keys
- **Telegram Bot Token** (Required) - Get from [@BotFather](https://t.me/botfather)
- **AI Provider API Key** (Required) - Choose one:
  - Groq API Key (Recommended for speed)
  - Google Gemini API Key (Recommended for quality)
  - OpenAI API Key
  - Anthropic API Key
- **Encryption Key** (Required) - 32-byte key for data encryption
- **Optional APIs**:
  - CoinGecko API Key (for enhanced crypto data)
  - Whop API Key (for premium features)
  - Ethereum RPC URL (for blockchain data)

## 🌍 Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/johhnysins63/mobby.git
cd mobby
```

### 2. Python Environment Setup

#### Option A: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### Option B: Using Conda
```bash
conda create -n mobius python=3.12
conda activate mobius
```

### 3. Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install optional AI providers (choose based on your preference)
pip install groq                    # For Groq (fast inference)
pip install google-generativeai     # For Gemini (high quality)
pip install openai                  # For OpenAI GPT models
pip install anthropic               # For Claude models
```

## ⚙️ Configuration

### 1. Environment Variables Setup

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Required Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
BOT_MASTER_ENCRYPTION_KEY=your_32_byte_encryption_key_here

# AI Provider Configuration (Choose one as primary)
AI_PROVIDER=groq                    # Options: groq, gemini, openai, anthropic
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional Configuration
WHOP_API_KEY=your_whop_api_key_here
COINGECKO_API_KEY=your_coingecko_api_key_here
ETHEREUM_RPC_URL=your_ethereum_rpc_url_here

# Advanced Configuration
AI_MODEL=llama3-70b-8192           # Model to use (provider-specific)
RATE_LIMIT_REQUESTS=100            # Requests per minute
CACHE_TTL=300                      # Cache time-to-live in seconds
```

### 2. Generate Encryption Key

```python
# Run this Python script to generate a secure encryption key
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(f"BOT_MASTER_ENCRYPTION_KEY={key.decode()}")
```

### 3. Get Telegram Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot`
3. Follow the prompts to create your bot
4. Copy the token to your `.env` file

### 4. Get Chat ID

```bash
# Start your bot and send it a message, then run:
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
# Look for "chat":{"id": in the response
```

## 🤖 AI Provider Setup

### Groq (Recommended for Speed)
1. Visit [Groq Console](https://console.groq.com/)
2. Create account and generate API key
3. Add to `.env`: `GROQ_API_KEY=your_key_here`
4. Set: `AI_PROVIDER=groq`

### Google Gemini (Recommended for Quality)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create API key
3. Add to `.env`: `GEMINI_API_KEY=your_key_here`
4. Set: `AI_PROVIDER=gemini`

### OpenAI
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create API key
3. Add to `.env`: `OPENAI_API_KEY=your_key_here`
4. Set: `AI_PROVIDER=openai`

### Anthropic Claude
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create API key
3. Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`
4. Set: `AI_PROVIDER=anthropic`

## 🗄️ Database Initialization

The system automatically initializes databases on first run:

```bash
# Test database initialization
python -c "
from src.user_db import init_db
from src.agent_memory_database import agent_memory
print('✅ Databases initialized successfully')
"
```

### Manual Database Setup (if needed)
```bash
# Create data directory
mkdir -p data

# Initialize databases
python src/user_db.py
python src/agent_memory_database.py
```

## 🚀 Installation Methods

### Method 1: Quick Start (Development)
```bash
# After completing environment setup and configuration
python src/main.py
```

### Method 2: Production with Process Manager
```bash
# Install PM2 (Node.js process manager)
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'mobius-ai',
    script: 'python',
    args: 'src/main.py',
    cwd: '/path/to/mobby',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Method 3: Docker Deployment
```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "src/main.py"]
EOF

# Build and run
docker build -t mobius-ai .
docker run -d --name mobius-ai --env-file .env mobius-ai
```

### Method 4: Systemd Service (Linux)
```bash
# Create service file
sudo tee /etc/systemd/system/mobius-ai.service << EOF
[Unit]
Description=Mobius AI Assistant
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/mobby
Environment=PATH=/path/to/mobby/venv/bin
ExecStart=/path/to/mobby/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable mobius-ai
sudo systemctl start mobius-ai
sudo systemctl status mobius-ai
```

## 🔧 Production Deployment

### 1. Security Hardening
```bash
# Set proper file permissions
chmod 600 .env
chmod 755 src/
chmod 644 src/*.py

# Create dedicated user (Linux)
sudo useradd -r -s /bin/false mobius
sudo chown -R mobius:mobius /path/to/mobby
```

### 2. Reverse Proxy Setup (Nginx)
```nginx
# /etc/nginx/sites-available/mobius-ai
server {
    listen 80;
    server_name your-domain.com;
    
    location /webhook {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. SSL Certificate (Let's Encrypt)
```bash
sudo certbot --nginx -d your-domain.com
```

### 4. Monitoring Setup
```bash
# Install monitoring tools
pip install prometheus-client grafana-api

# Create monitoring endpoint
# Add to main.py:
from prometheus_client import start_http_server, Counter, Histogram
start_http_server(8001)  # Metrics endpoint
```

### 5. Log Management
```bash
# Configure log rotation
sudo tee /etc/logrotate.d/mobius-ai << EOF
/path/to/mobby/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 mobius mobius
}
EOF
```

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check bot status
curl http://localhost:8001/metrics

# Check database
python -c "
from src.user_db import init_db
from src.agent_memory_database import agent_memory
print('✅ All systems operational')
"

# Check AI providers
python -c "
import asyncio
from src.ai_provider_manager import ai_provider_manager
results = asyncio.run(ai_provider_manager.test_all_providers())
for provider, result in results.items():
    status = '✅' if result['success'] else '❌'
    print(f'{status} {provider}: {result.get(\"response_time\", 0):.2f}s')
"
```

### Performance Monitoring
```bash
# Monitor memory usage
ps aux | grep python | grep main.py

# Monitor disk usage
du -sh data/

# Monitor network connections
netstat -tulpn | grep python
```

### Backup Strategy
```bash
# Create backup script
cat > backup.sh << EOF
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mobius_\$DATE"
mkdir -p \$BACKUP_DIR

# Backup databases
cp data/*.db \$BACKUP_DIR/
cp data/*.sqlite \$BACKUP_DIR/

# Backup configuration
cp .env \$BACKUP_DIR/
cp -r src/ \$BACKUP_DIR/

# Compress backup
tar -czf "\$BACKUP_DIR.tar.gz" \$BACKUP_DIR
rm -rf \$BACKUP_DIR

echo "Backup completed: \$BACKUP_DIR.tar.gz"
EOF

chmod +x backup.sh

# Schedule daily backups
echo "0 2 * * * /path/to/mobby/backup.sh" | crontab -
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -r requirements.txt

# Check specific imports
python -c "from src.main import *"
```

#### 2. Database Issues
```bash
# Reset databases
rm data/*.db data/*.sqlite
python src/user_db.py
python src/agent_memory_database.py
```

#### 3. API Connection Issues
```bash
# Test API connectivity
python -c "
import asyncio
from src.ai_provider_manager import test_ai_provider
result = asyncio.run(test_ai_provider('groq'))
print(result)
"
```

#### 4. Permission Issues
```bash
# Fix file permissions
chmod -R 755 src/
chmod 600 .env
chown -R $USER:$USER .
```

### Debug Mode
```bash
# Run with debug logging
export PYTHONPATH=/path/to/mobby
export LOG_LEVEL=DEBUG
python src/main.py
```

### Log Analysis
```bash
# View recent logs
tail -f logs/mobius.log

# Search for errors
grep -i error logs/mobius.log

# Monitor real-time activity
tail -f logs/mobius.log | grep -E "(INFO|ERROR|WARNING)"
```

## 🚀 Advanced Features

### 1. AI Provider Switching
```bash
# Switch providers via command
/switch_ai gemini

# Or via environment
export AI_PROVIDER=gemini
```

### 2. Memory System Training
```bash
# View memory status
/memory_status

# Run training scenarios
/memory_train beginner

# View learning insights
/memory_insights performance
```

### 3. Custom MCP Servers
```python
# Add custom MCP server
# Create src/mcp_servers/custom_server.py
# Register in src/mcp_integration.py
```

### 4. Webhook Mode (Production)
```python
# Add to main.py for webhook mode
from telegram.ext import Updater

def setup_webhook():
    updater = Updater(token=TOKEN)
    updater.start_webhook(
        listen="0.0.0.0",
        port=8000,
        url_path=TOKEN,
        webhook_url=f"https://your-domain.com/{TOKEN}"
    )
```

### 5. Multi-Instance Deployment
```bash
# Load balancer configuration
# Use multiple instances with shared database
# Configure Redis for session management
```

## 📈 Performance Optimization

### 1. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_user_properties_user_id ON user_properties(user_id);
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp);
```

### 2. Caching Strategy
```python
# Configure Redis caching
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300  # 5 minutes
```

### 3. Rate Limiting
```python
# Configure rate limits per user
RATE_LIMIT_REQUESTS=100  # per minute
RATE_LIMIT_BURST=10      # burst allowance
```

## 🔐 Security Best Practices

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables or secure vaults
   - Rotate keys regularly

2. **Database Security**
   - Enable encryption at rest
   - Use strong encryption keys
   - Regular security audits

3. **Network Security**
   - Use HTTPS for all communications
   - Implement proper firewall rules
   - Monitor for suspicious activity

4. **Access Control**
   - Implement user authentication
   - Use role-based permissions
   - Log all administrative actions

## 📞 Support & Resources

- **Documentation**: [GitHub Wiki](https://github.com/johhnysins63/mobby/wiki)
- **Issues**: [GitHub Issues](https://github.com/johhnysins63/mobby/issues)
- **Community**: [Telegram Group](https://t.me/mobius_ai_community)
- **Updates**: [Release Notes](https://github.com/johhnysins63/mobby/releases)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**🚀 Ready for Production • 🔴 100% Real Data • 🛡️ Enterprise Security**

*Built with ❤️ for the crypto community*