# Möbius AI Assistant - Enhanced Edition Deployment Guide

## 🚀 **Quick Start - Enhanced Edition**

This guide covers deploying the Enhanced Edition of Möbius AI Assistant with all the new performance, security, and AI features.

## 📋 **Prerequisites**

### **System Requirements**
- Python 3.9+ (recommended: Python 3.11+)
- 2GB+ RAM (4GB+ recommended for production)
- 1GB+ disk space
- Linux/macOS/Windows with WSL2

### **Required Services**
- Telegram Bot Token (from @BotFather)
- Target Telegram Group/Channel
- At least one AI provider API key (Groq, OpenAI, Gemini, or Anthropic)

### **Optional Services**
- Arkham Intelligence API key
- Nansen API key
- Whop subscription management
- Ethereum RPC endpoint

## 🔧 **Installation Steps**

### **1. Clone and Setup Environment**
```bash
git clone <repository-url>
cd curly-octo-fishstick
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Environment Configuration**
Create your `.env` file:
```bash
cp .env.example .env
```

**Required Environment Variables:**
```env
# Core Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
BOT_MASTER_ENCRYPTION_KEY=your_encryption_key_here

# AI Provider (at least one required)
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional Services
ARKHAM_API_KEY=your_arkham_key_here
NANSEN_API_KEY=your_nansen_key_here
WHOP_BEARER_TOKEN=your_whop_token_here
ETHEREUM_RPC_URL=your_rpc_url_here
```

**Generate Encryption Key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### **3. Database Initialization**
The enhanced database will be automatically initialized on first run:
```bash
mkdir -p data
python src/main.py
```

### **4. Telegram Bot Setup**
1. Add your bot to the target Telegram group
2. Promote it to administrator with message management permissions
3. Send `/start` in a DM to begin onboarding
4. Test with `/help` to see the enhanced interactive menu

## 🎯 **Enhanced Features Configuration**

### **Performance Monitoring**
The performance monitor is enabled by default and tracks:
- Command execution times
- User activity patterns
- System health metrics
- Error rates and types

**Admin Commands:**
- `/metrics` - View real-time performance dashboard
- `/cleanup` - Optimize database and reset metrics

### **Security Auditing**
Security auditing is automatically enabled and provides:
- Complete audit trail for sensitive operations
- Real-time threat detection
- Privacy-protected logging

**Admin Commands:**
- `/security` - View security dashboard
- Access audit logs through interactive menus

### **Contextual AI**
The AI system learns from user interactions:
- Remembers conversation context
- Provides personalized suggestions
- Adapts help content to usage patterns

**Features:**
- Enhanced `/help` with personalized content
- Smart suggestions in command responses
- Predictive next-action recommendations

### **Enhanced UI**
Interactive components are enabled by default:
- Inline keyboards for major functions
- Progress indicators for long operations
- Rich message formatting
- Context-sensitive menus

## 📊 **Monitoring and Maintenance**

### **Health Checks**
Monitor system health with:
```bash
# Check system status
curl -f http://localhost:8000/health || echo "System needs attention"

# View logs
tail -f logs/mobius.log

# Database health
python -c "
import sys; sys.path.append('src')
from enhanced_db import enhanced_db
print('Database status:', 'OK' if enhanced_db.execute_query('SELECT 1').success else 'ERROR')
"
```

### **Performance Optimization**
Regular maintenance tasks:
```bash
# Database optimization (run weekly)
python -c "
import sys; sys.path.append('src')
from enhanced_db import enhanced_db
enhanced_db.cleanup_old_data(30)  # Keep 30 days
enhanced_db.execute_query('VACUUM')
print('Database optimized')
"

# Reset performance metrics (if needed)
python -c "
import sys; sys.path.append('src')
from performance_monitor import performance_monitor
performance_monitor.reset_metrics()
print('Metrics reset')
"
```

### **Security Maintenance**
Security best practices:
```bash
# Export audit logs (monthly)
python -c "
import sys; sys.path.append('src')
from security_auditor import security_auditor
import json
logs = security_auditor.export_audit_log()
with open('audit_export.json', 'w') as f:
    json.dump(logs, f, indent=2)
print(f'Exported {len(logs)} audit events')
"

# Check for suspicious activity
python -c "
import sys; sys.path.append('src')
from security_auditor import security_auditor
summary = security_auditor.get_security_summary()
high_risk = summary['summary']['high_risk_events']
if high_risk > 0:
    print(f'⚠️ {high_risk} high-risk events detected')
else:
    print('✅ No high-risk security events')
"
```

## 🔒 **Security Considerations**

### **Enhanced Security Features**
- All sensitive operations are audited
- User data is hashed for privacy protection
- Rate limiting prevents abuse
- Suspicious activity detection

### **Data Protection**
- Encryption keys are never logged
- User IDs are hashed in audit logs
- IP addresses are anonymized
- Sensitive data is automatically redacted

### **Access Control**
- Admin commands require Telegram admin status
- Sensitive operations require DM context
- Multi-layer authentication for critical functions

## 🚨 **Troubleshooting**

### **Common Issues**

**Import Errors:**
```bash
# Missing dependencies
pip install -r requirements.txt

# Python path issues
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**Database Issues:**
```bash
# Recreate database
rm -f data/user_data.sqlite
python src/main.py  # Will recreate automatically
```

**Performance Issues:**
```bash
# Check system resources
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Disk: {psutil.disk_usage(\"/\").percent}%')
"

# Optimize database
python -c "
import sys; sys.path.append('src')
from enhanced_db import enhanced_db
enhanced_db.cleanup_old_data(7)  # Aggressive cleanup
enhanced_db.execute_query('VACUUM')
"
```

**Security Alerts:**
```bash
# Check recent security events
python -c "
import sys; sys.path.append('src')
from security_auditor import security_auditor
events = security_auditor.export_audit_log()
recent = [e for e in events if e['risk_level'] in ['high', 'critical']]
print(f'Recent high-risk events: {len(recent)}')
for event in recent[-5:]:
    print(f'- {event[\"timestamp\"]}: {event[\"action\"]}')
"
```

## 📈 **Performance Tuning**

### **Database Optimization**
```python
# Custom database tuning (add to config)
DB_POOL_SIZE = 20  # Increase for high load
DB_CACHE_SIZE = 20000  # Increase cache
DB_CLEANUP_DAYS = 30  # Adjust retention
```

### **Memory Management**
```python
# Contextual AI tuning
MAX_CONTEXT_MESSAGES = 100  # Increase for better context
CONTEXT_TIMEOUT = 7200  # 2 hours for longer sessions
MEMORY_CLEANUP_INTERVAL = 600  # 10 minutes
```

### **Performance Monitoring**
```python
# Monitor tuning
MAX_USERS_TRACKED = 50000  # Increase for large deployments
MAX_ERROR_TYPES = 500  # More error tracking
METRIC_RETENTION_HOURS = 168  # 1 week retention
```

## 🎯 **Production Deployment**

### **Systemd Service (Linux)**
Create `/etc/systemd/system/mobius.service`:
```ini
[Unit]
Description=Möbius AI Assistant Enhanced Edition
After=network.target

[Service]
Type=simple
User=mobius
WorkingDirectory=/opt/mobius
Environment=PYTHONPATH=/opt/mobius/src
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

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

ENV PYTHONPATH=/app/src
CMD ["python", "src/main.py"]
```

### **Monitoring Integration**
For production monitoring, integrate with:
- Prometheus for metrics collection
- Grafana for visualization
- ELK stack for log analysis
- Sentry for error tracking

## 🎉 **Verification**

After deployment, verify all enhanced features:

1. **Performance Monitoring**: `/metrics` shows real-time data
2. **Security Auditing**: `/security` displays audit information
3. **Contextual AI**: `/help` provides personalized content
4. **Enhanced UI**: Commands show interactive menus
5. **Analytics**: `/analytics` shows user insights

## 📞 **Support**

For issues with the Enhanced Edition:
1. Check the troubleshooting section above
2. Review logs in `data/` directory
3. Use `/status` command for system health
4. Check GitHub issues for known problems

The Enhanced Edition maintains full backward compatibility while providing significant improvements in performance, security, and user experience.