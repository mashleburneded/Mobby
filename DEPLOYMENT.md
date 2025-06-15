# Möbius Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from @BotFather)
- Target Telegram Group/Chat ID

### Installation
```bash
git clone <repository-url>
cd curly-octo-fishstick
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`
2. Generate encryption key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
3. Configure required variables in `.env`:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `BOT_MASTER_ENCRYPTION_KEY`

### Launch
```bash
mkdir -p data
python test_bot.py  # Verify setup
python demo.py      # See functionality demo
python src/main.py  # Start the bot
```

## 🔧 Production Deployment

### Environment Variables

**Required:**
```bash
TELEGRAM_BOT_TOKEN="your_bot_token_here"
TELEGRAM_CHAT_ID="-1001234567890"
BOT_MASTER_ENCRYPTION_KEY="your_32_byte_key_here"
```

**Optional API Keys:**
```bash
# AI Providers
GROQ_API_KEY="your_groq_key"
OPENAI_API_KEY="your_openai_key"
GEMINI_API_KEY="your_gemini_key"
ANTHROPIC_API_KEY="your_anthropic_key"

# Crypto APIs
ARKHAM_API_KEY="your_arkham_key"
NANSEN_API_KEY="your_nansen_key"

# Blockchain
ETHEREUM_RPC_URL="https://mainnet.infura.io/v3/your_project_id"

# Subscriptions
WHOP_BEARER_TOKEN="your_whop_token"
WHOP_PREMIUM_RETAIL_PLAN_ID="plan_id"
WHOP_PREMIUM_CORPORATE_PLAN_ID="plan_id"

# Webhooks
ARKHAM_WEBHOOK_URL="https://your-domain.com/webhook/arkham"
```

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p data

CMD ["python", "src/main.py"]
```

Build and run:
```bash
docker build -t mobius-bot .
docker run -d --env-file .env -v $(pwd)/data:/app/data mobius-bot
```

### Systemd Service (Linux)

Create `/etc/systemd/system/mobius.service`:
```ini
[Unit]
Description=Möbius Telegram Bot
After=network.target

[Service]
Type=simple
User=mobius
WorkingDirectory=/opt/mobius
Environment=PATH=/opt/mobius/venv/bin
ExecStart=/opt/mobius/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mobius
sudo systemctl start mobius
sudo systemctl status mobius
```

## 🔒 Security Checklist

- [ ] **Encryption Key**: Generate unique `BOT_MASTER_ENCRYPTION_KEY`
- [ ] **API Keys**: Store securely, never commit to version control
- [ ] **File Permissions**: Restrict access to `.env` and `data/` directory
- [ ] **Network**: Use HTTPS for webhooks, secure RPC endpoints
- [ ] **Backups**: Regular backups of `data/user_data.sqlite`
- [ ] **Monitoring**: Set up logging and error monitoring
- [ ] **Updates**: Keep dependencies updated for security patches

## 📊 Monitoring

### Log Files
- Application logs: stdout/stderr
- Database: `data/user_data.sqlite`
- Summaries: `data/daily_summaries/`
- Config: `data/config.json`

### Health Checks
```bash
# Test bot functionality
python test_bot.py

# Check database
sqlite3 data/user_data.sqlite ".tables"

# Verify encryption
python -c "import sys; sys.path.append('src'); from user_db import init_db; init_db()"
```

### Performance Monitoring
- Memory usage (encryption keys in memory)
- Database size growth
- API rate limits
- Message processing latency

## 🔧 Maintenance

### Regular Tasks
1. **Daily**: Check logs for errors
2. **Weekly**: Review API usage and costs
3. **Monthly**: Update dependencies
4. **Quarterly**: Security audit

### Backup Strategy
```bash
# Backup user data
cp data/user_data.sqlite backups/user_data_$(date +%Y%m%d).sqlite

# Backup configuration
cp data/config.json backups/config_$(date +%Y%m%d).json

# Backup summaries
tar -czf backups/summaries_$(date +%Y%m%d).tar.gz data/daily_summaries/
```

### Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Test after updates
python test_bot.py

# Restart service
sudo systemctl restart mobius
```

## 🚨 Troubleshooting

### Common Issues

**Bot not responding:**
- Check `TELEGRAM_BOT_TOKEN` is valid
- Verify bot is admin in target group
- Check network connectivity

**Database errors:**
- Verify `BOT_MASTER_ENCRYPTION_KEY` is correct
- Check file permissions on `data/` directory
- Ensure SQLite is installed

**API failures:**
- Verify API keys are configured
- Check rate limits
- Confirm service availability

**Memory issues:**
- Monitor encryption manager memory usage
- Check for message store leaks
- Restart service if needed

### Debug Mode
```bash
# Enable debug logging
export PYTHONPATH=src
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from main import main
main()
"
```

### Support
- Check logs: `journalctl -u mobius -f`
- Test components: `python test_bot.py`
- Demo functionality: `python demo.py`
- Review documentation: `README.md`, `features.md`

## 📈 Scaling

### High Availability
- Multiple bot instances with load balancer
- Shared database (PostgreSQL)
- Redis for session management
- Container orchestration (Kubernetes)

### Performance Optimization
- Database indexing
- Message batching
- Async processing
- Caching layer

### Monitoring & Alerting
- Prometheus metrics
- Grafana dashboards
- PagerDuty integration
- Health check endpoints