# 🚀 Möbius AI Assistant - Comprehensive Deployment Guide

## 📋 **Pre-Deployment Checklist**

### **System Requirements**
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Docker
- **Python**: 3.10+ (3.12 recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 20GB minimum, 50GB recommended
- **Network**: Stable internet connection with low latency

### **Required Services**
- **Redis Server**: 6.0+ for caching
- **PostgreSQL/SQLite**: Database storage
- **Telegram Bot**: Bot token from @BotFather
- **AI Provider APIs**: At least one AI provider API key

### **Security Prerequisites**
- **SSL/TLS Certificates**: For HTTPS endpoints
- **Firewall Configuration**: Proper port management
- **API Key Management**: Secure key storage
- **Backup Strategy**: Data backup and recovery plan

## 🔧 **Environment Setup**

### **1. System Preparation**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.12 python3.12-pip python3.12-venv \
    redis-server postgresql postgresql-contrib \
    nginx certbot python3-certbot-nginx \
    git curl wget htop

# Create application user
sudo useradd -m -s /bin/bash mobius
sudo usermod -aG sudo mobius
```

### **2. Redis Configuration**
```bash
# Configure Redis for production
sudo nano /etc/redis/redis.conf

# Key configurations:
# maxmemory 2gb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10
# save 60 10000
# requirepass your_redis_password

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### **3. Database Setup**
```bash
# PostgreSQL setup (optional, SQLite is default)
sudo -u postgres createuser mobius
sudo -u postgres createdb mobius_db -O mobius
sudo -u postgres psql -c "ALTER USER mobius PASSWORD 'secure_password';"
```

### **4. Application Setup**
```bash
# Switch to mobius user
sudo su - mobius

# Clone repository
git clone https://github.com/proy69/mobius.git
cd mobius

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔐 **Security Configuration**

### **1. Environment Variables**
```bash
# Create secure environment file
nano .env

# Required variables
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
REDIS_URL=redis://:your_redis_password@localhost:6379/0
DATABASE_URL=sqlite:///data/mobius.db

# AI Provider Keys (choose one or more)
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# Security settings
ENCRYPTION_KEY=your_32_byte_encryption_key
SECRET_KEY=your_secret_key_for_sessions
ADMIN_USER_IDS=123456789,987654321

# Performance settings
MAX_WORKERS=4
CACHE_TTL=3600
DATABASE_POOL_SIZE=20
REDIS_POOL_SIZE=10

# Monitoring settings
ENABLE_MONITORING=true
METRICS_ENDPOINT=http://localhost:8080/metrics
ALERT_WEBHOOK_URL=your_webhook_url

# Set secure permissions
chmod 600 .env
```

### **2. SSL/TLS Setup**
```bash
# Install SSL certificate (if using domain)
sudo certbot --nginx -d your-domain.com

# Or generate self-signed certificate for testing
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### **3. Firewall Configuration**
```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 6379/tcp  # Redis (only from localhost)
sudo ufw deny 6379/tcp from any to any
```

## 🐳 **Docker Deployment**

### **1. Dockerfile Optimization**
```dockerfile
# Multi-stage build for production
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim

# Create non-root user
RUN useradd -m -u 1000 mobius

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Copy application
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

# Set permissions
RUN chown -R mobius:mobius /app
USER mobius

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Start application
CMD ["python", "src/main_ultimate_fixed.py"]
```

### **2. Docker Compose Production**
```yaml
version: '3.8'

services:
  mobius-bot:
    build: .
    restart: unless-stopped
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://mobius:${DB_PASSWORD}@postgres:5432/mobius_db
      - GROQ_API_KEY=${GROQ_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - redis
      - postgres
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - mobius-network
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    networks:
      - mobius-network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_DB=mobius_db
      - POSTGRES_USER=mobius
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - mobius-network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - mobius-bot
    networks:
      - mobius-network

  monitoring:
    image: prom/prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    networks:
      - mobius-network

volumes:
  redis-data:
  postgres-data:
  prometheus-data:

networks:
  mobius-network:
    driver: bridge
```

### **3. Production Deployment**
```bash
# Create production environment file
cp .env.example .env.production
nano .env.production

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Check deployment status
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f mobius-bot
```

## ☸️ **Kubernetes Deployment**

### **1. Kubernetes Manifests**
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mobius

---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mobius-config
  namespace: mobius
data:
  REDIS_URL: "redis://redis-service:6379/0"
  DATABASE_URL: "postgresql://mobius:password@postgres-service:5432/mobius_db"
  ENABLE_MONITORING: "true"

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: mobius-secrets
  namespace: mobius
type: Opaque
stringData:
  TELEGRAM_BOT_TOKEN: "your_telegram_bot_token"
  GROQ_API_KEY: "your_groq_api_key"
  OPENAI_API_KEY: "your_openai_api_key"
  GEMINI_API_KEY: "your_gemini_api_key"
  REDIS_PASSWORD: "your_redis_password"
  DB_PASSWORD: "your_db_password"

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mobius-bot
  namespace: mobius
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mobius-bot
  template:
    metadata:
      labels:
        app: mobius-bot
    spec:
      containers:
      - name: mobius-bot
        image: ghcr.io/proy69/mobius:latest
        ports:
        - containerPort: 8080
        env:
        - name: TELEGRAM_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: mobius-secrets
              key: TELEGRAM_BOT_TOKEN
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: mobius-secrets
              key: GROQ_API_KEY
        envFrom:
        - configMapRef:
            name: mobius-config
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mobius-service
  namespace: mobius
spec:
  selector:
    app: mobius-bot
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mobius-ingress
  namespace: mobius
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - your-domain.com
    secretName: mobius-tls
  rules:
  - host: your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mobius-service
            port:
              number: 80
```

### **2. Deploy to Kubernetes**
```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n mobius
kubectl get services -n mobius
kubectl logs -f deployment/mobius-bot -n mobius

# Scale deployment
kubectl scale deployment mobius-bot --replicas=3 -n mobius
```

## 📊 **Monitoring Setup**

### **1. Prometheus Configuration**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mobius-bot'
    static_configs:
      - targets: ['mobius-bot:8080']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
```

### **2. Grafana Dashboard**
```json
{
  "dashboard": {
    "title": "Möbius AI Assistant",
    "panels": [
      {
        "title": "System Health",
        "type": "stat",
        "targets": [
          {
            "expr": "mobius_health_score",
            "legendFormat": "Health Score"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(mobius_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "mobius_response_time_seconds",
            "legendFormat": "Response Time"
          }
        ]
      }
    ]
  }
}
```

### **3. Alerting Rules**
```yaml
# alerts.yml
groups:
  - name: mobius-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(mobius_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighMemoryUsage
        expr: mobius_memory_usage_percent > 85
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"

      - alert: DatabaseConnectionFailure
        expr: mobius_database_connections_failed > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failure"
          description: "Database connections are failing"
```

## 🔄 **CI/CD Pipeline**

### **1. GitHub Actions Deployment**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}

      - name: Deploy to Kubernetes
        run: |
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > kubeconfig
          export KUBECONFIG=kubeconfig
          kubectl set image deployment/mobius-bot mobius-bot=ghcr.io/${{ github.repository }}:${{ github.sha }} -n mobius
          kubectl rollout status deployment/mobius-bot -n mobius
```

### **2. Automated Testing**
```bash
# Run comprehensive tests before deployment
python -m pytest tests/ -v --cov=src --cov-report=xml
python tests/test_comprehensive_bug_hunt.py
python tests/test_rate_limiting.py

# Performance testing
python -c "
import asyncio
from src.consolidated_core import init_core_system, get_core_health
async def test():
    await init_core_system()
    health = await get_core_health()
    assert health['overall_status'] in ['HEALTHY', 'WARNING']
    print('✅ Deployment tests passed')
asyncio.run(test())
"
```

## 🔧 **Production Optimization**

### **1. Performance Tuning**
```python
# Production configuration
PRODUCTION_CONFIG = {
    'database': {
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 30,
        'pool_recycle': 3600
    },
    'cache': {
        'max_connections': 50,
        'connection_timeout': 5,
        'socket_timeout': 5,
        'retry_on_timeout': True
    },
    'monitoring': {
        'collection_interval': 10,
        'metrics_retention': 86400,  # 24 hours
        'alert_cooldown': 300  # 5 minutes
    }
}
```

### **2. Resource Limits**
```yaml
# Kubernetes resource limits
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"

# Docker resource limits
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 1G
      cpus: '0.5'
```

### **3. Auto-scaling Configuration**
```yaml
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mobius-hpa
  namespace: mobius
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mobius-bot
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 🛡️ **Security Hardening**

### **1. Network Security**
```bash
# Configure network policies (Kubernetes)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mobius-network-policy
  namespace: mobius
spec:
  podSelector:
    matchLabels:
      app: mobius-bot
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 6379  # Redis
    - protocol: TCP
      port: 5432  # PostgreSQL
```

### **2. Secret Management**
```bash
# Use external secret management
# Example with HashiCorp Vault
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: mobius
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "mobius-role"
```

### **3. Security Scanning**
```bash
# Container security scanning
trivy image ghcr.io/proy69/mobius:latest

# Dependency scanning
safety check -r requirements.txt

# Code security scanning
bandit -r src/ -f json
```

## 📋 **Maintenance Procedures**

### **1. Backup Strategy**
```bash
#!/bin/bash
# backup.sh - Automated backup script

# Database backup
pg_dump -h postgres-service -U mobius mobius_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Redis backup
redis-cli --rdb backup_redis_$(date +%Y%m%d_%H%M%S).rdb

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz .env k8s/ docker-compose.yml

# Upload to cloud storage
aws s3 cp backup_*.sql s3://mobius-backups/database/
aws s3 cp backup_*.rdb s3://mobius-backups/redis/
aws s3 cp config_backup_*.tar.gz s3://mobius-backups/config/
```

### **2. Update Procedures**
```bash
# Rolling update procedure
kubectl set image deployment/mobius-bot mobius-bot=ghcr.io/proy69/mobius:v2.0.0 -n mobius
kubectl rollout status deployment/mobius-bot -n mobius

# Rollback if needed
kubectl rollout undo deployment/mobius-bot -n mobius
```

### **3. Health Monitoring**
```bash
# Health check script
#!/bin/bash
# health_check.sh

# Check application health
curl -f http://localhost:8080/health || exit 1

# Check database connectivity
python -c "
import asyncio
from src.secure_database_manager import secure_db_manager
async def check():
    stats = await secure_db_manager.get_stats()
    assert stats['pool_stats']['total_connections'] > 0
asyncio.run(check())
"

# Check cache connectivity
redis-cli ping || exit 1

echo "✅ All health checks passed"
```

## 🚨 **Troubleshooting Guide**

### **Common Issues**

#### **1. High Memory Usage**
```bash
# Check memory usage
kubectl top pods -n mobius

# Analyze memory leaks
python -m memory_profiler src/main_ultimate_fixed.py

# Restart deployment
kubectl rollout restart deployment/mobius-bot -n mobius
```

#### **2. Database Connection Issues**
```bash
# Check database connectivity
kubectl exec -it deployment/mobius-bot -n mobius -- python -c "
from src.secure_database_manager import secure_db_manager
import asyncio
print(asyncio.run(secure_db_manager.get_stats()))
"

# Check connection pool
kubectl logs deployment/mobius-bot -n mobius | grep "database"
```

#### **3. Cache Performance Issues**
```bash
# Check Redis performance
redis-cli info stats

# Check cache hit ratio
kubectl exec -it deployment/mobius-bot -n mobius -- python -c "
from src.secure_redis_cache import secure_cache
import asyncio
print(asyncio.run(secure_cache.get_cache_stats()))
"
```

### **Emergency Procedures**

#### **1. Complete System Failure**
```bash
# Emergency restart
kubectl delete pods -l app=mobius-bot -n mobius

# Restore from backup
kubectl apply -f k8s/
# Restore database from backup
# Restore Redis from backup
```

#### **2. Security Incident**
```bash
# Immediate response
kubectl scale deployment mobius-bot --replicas=0 -n mobius

# Investigate
kubectl logs deployment/mobius-bot -n mobius --previous
kubectl get events -n mobius

# Rotate secrets
kubectl delete secret mobius-secrets -n mobius
kubectl create secret generic mobius-secrets --from-env-file=.env.new -n mobius
```

---

**This comprehensive deployment guide ensures a secure, scalable, and maintainable production deployment of the Möbius AI Assistant.**