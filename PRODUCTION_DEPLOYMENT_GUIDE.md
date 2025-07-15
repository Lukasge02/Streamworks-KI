# StreamWorks-KI Production Deployment Guide

## Overview

This guide covers the complete production deployment of StreamWorks-KI, including security considerations, monitoring, and maintenance procedures.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Security Configuration](#security-configuration)
4. [Deployment Process](#deployment-process)
5. [Monitoring & Observability](#monitoring--observability)
6. [Maintenance & Operations](#maintenance--operations)
7. [Troubleshooting](#troubleshooting)
8. [Backup & Recovery](#backup--recovery)

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 4+ cores (8+ recommended)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 100GB+ SSD
- **Network**: Public IP with ports 80, 443 accessible

### Software Dependencies

```bash
# Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Additional utilities
sudo apt update
sudo apt install -y curl wget git htop nginx-utils logrotate
```

### Hardware Recommendations

| Component | Minimum | Recommended | Enterprise |
|-----------|---------|-------------|------------|
| CPU | 4 cores | 8 cores | 16+ cores |
| RAM | 8GB | 16GB | 32GB+ |
| Storage | 100GB SSD | 500GB SSD | 1TB+ NVMe |
| Network | 100Mbps | 1Gbps | 10Gbps |

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/streamworks-ki.git
cd streamworks-ki
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.production.template .env.production

# Edit production environment
nano .env.production
```

### Critical Environment Variables

```bash
# Security
SECRET_KEY="your-super-secret-key-minimum-32-characters-long"
POSTGRES_PASSWORD="your-secure-database-password"
GRAFANA_ADMIN_PASSWORD="your-grafana-admin-password"

# Database
DATABASE_URL="postgresql://streamworks:${POSTGRES_PASSWORD}@postgres:5432/streamworks_ki_prod"

# Domain Configuration
ALLOWED_HOSTS="yourdomain.com,api.yourdomain.com"
CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"

# Monitoring
SENTRY_DSN="https://your-sentry-dsn@sentry.io/project-id"

# Email (for alerts)
SMTP_HOST="smtp.gmail.com"
SMTP_USERNAME="alerts@yourdomain.com"
SMTP_PASSWORD="your-app-password"
ALERT_EMAIL_TO="admin@yourdomain.com,ops@yourdomain.com"
```

### 3. SSL Certificate Setup

```bash
# Create SSL directory
mkdir -p ssl

# Option 1: Let's Encrypt (recommended)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
sudo chown $USER:$USER ssl/*.pem

# Option 2: Self-signed (development only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/privkey.pem \
    -out ssl/fullchain.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"
```

## Security Configuration

### 1. Firewall Setup

```bash
# UFW Configuration
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow monitoring (restrict to specific IPs in production)
sudo ufw allow from YOUR_MONITORING_IP to any port 9090
sudo ufw allow from YOUR_MONITORING_IP to any port 3000

# Check status
sudo ufw status verbose
```

### 2. System Security

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install security updates automatically
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Configure fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Docker Security

```bash
# Create docker daemon configuration
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true
}
EOF

sudo systemctl restart docker
```

## Deployment Process

### 1. Automated Deployment

```bash
# Make deployment script executable
chmod +x scripts/deploy.sh

# Run full deployment
./scripts/deploy.sh deploy
```

### 2. Manual Deployment Steps

```bash
# 1. Build images
docker build -f backend/Dockerfile.production -t streamworks-ki/backend:latest backend/
docker build -f frontend/Dockerfile.production -t streamworks-ki/frontend:latest frontend/

# 2. Start infrastructure
docker-compose -f docker-compose.production.yml up -d postgres redis

# 3. Wait for database
sleep 30

# 4. Start application services
docker-compose -f docker-compose.production.yml up -d ollama backend frontend

# 5. Start monitoring
docker-compose -f docker-compose.production.yml up -d prometheus grafana elasticsearch kibana
```

### 3. Verification

```bash
# Check service status
./scripts/deploy.sh status

# Run verification
./scripts/deploy.sh verify

# Check logs
./scripts/deploy.sh logs backend
```

## Monitoring & Observability

### 1. Health Checks

| Service | Health Check URL | Expected Response |
|---------|------------------|-------------------|
| Frontend | http://localhost/health | {"status":"healthy"} |
| Backend | http://localhost:8000/health | {"status":"healthy"} |
| Prometheus | http://localhost:9090/-/healthy | Prometheus is Healthy |
| Grafana | http://localhost:3000/api/health | {"database": "ok"} |

### 2. Key Metrics to Monitor

#### Application Metrics
- Request rate and latency
- Error rates (4xx, 5xx)
- LLM response times
- ChromaDB query performance
- Upload success rates

#### System Metrics
- CPU utilization (< 80%)
- Memory usage (< 90%)
- Disk usage (< 85%)
- Network I/O
- Container health

#### Business Metrics
- Active users
- Search queries per hour
- Document uploads per day
- Storage usage growth

### 3. Alerting Setup

```bash
# Configure alerting rules in Prometheus
# File: config/prometheus/rules/alerts.yml

groups:
  - name: critical-alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
          
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

### 4. Log Management

```bash
# View real-time logs
docker-compose -f docker-compose.production.yml logs -f backend

# Search logs with ElasticSearch/Kibana
# Access Kibana at http://localhost:5601

# Log retention policy
# Logs are automatically rotated and compressed
# Backend logs: 30 days retention
# Nginx logs: 30 days retention
# Application logs: JSON format for structured logging
```

## Maintenance & Operations

### 1. Regular Maintenance Tasks

#### Daily
- Check service health status
- Monitor disk usage
- Review error logs
- Verify backup completion

#### Weekly
- Update system packages
- Review security logs
- Analyze performance metrics
- Check SSL certificate expiry

#### Monthly
- Full system backup
- Security vulnerability scan
- Performance optimization review
- Capacity planning assessment

### 2. Backup Procedures

```bash
# Automated backup (included in deployment script)
./scripts/deploy.sh backup

# Manual database backup
docker-compose -f docker-compose.production.yml exec postgres pg_dump \
    -U $POSTGRES_USER -d $POSTGRES_DB \
    --clean --if-exists --create > backup_$(date +%Y%m%d).sql

# Manual ChromaDB backup
tar -czf chromadb_backup_$(date +%Y%m%d).tar.gz data/chromadb/

# Upload to cloud storage (recommended)
aws s3 cp backup_$(date +%Y%m%d).sql s3://your-backup-bucket/
```

### 3. Update Procedures

```bash
# Update application code
git pull origin main

# Rebuild and redeploy
./scripts/deploy.sh deploy

# Rolling update (zero downtime)
docker-compose -f docker-compose.production.yml up -d --scale backend=2 backend
sleep 30
docker-compose -f docker-compose.production.yml up -d --scale backend=1 backend
```

### 4. Scaling

#### Horizontal Scaling
```bash
# Scale backend services
docker-compose -f docker-compose.production.yml up -d --scale backend=3

# Load balancer configuration (nginx)
upstream backend {
    server backend_1:8000;
    server backend_2:8000;
    server backend_3:8000;
}
```

#### Vertical Scaling
```yaml
# Update docker-compose.production.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs backend

# Check resource usage
docker stats

# Restart service
docker-compose -f docker-compose.production.yml restart backend
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose -f docker-compose.production.yml exec postgres pg_isready

# Check connection from backend
docker-compose -f docker-compose.production.yml exec backend \
    python -c "from app.models.database import test_connection; test_connection()"
```

#### 3. High Memory Usage
```bash
# Check memory usage by container
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Restart memory-intensive services
docker-compose -f docker-compose.production.yml restart ollama
```

#### 4. Disk Space Issues
```bash
# Clean up old Docker images
docker system prune -a

# Clean up logs
find logs/ -name "*.log" -mtime +30 -delete

# Check largest directories
du -h data/ | sort -rh | head -10
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Run in PostgreSQL
ANALYZE;
REINDEX DATABASE streamworks_ki_prod;

-- Check slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### 2. ChromaDB Optimization
```bash
# Check ChromaDB statistics
curl http://localhost:8000/api/v1/chunks/statistics

# Optimize vector index
# (This would be implemented in the application)
```

#### 3. Application Optimization
```bash
# Monitor application metrics
curl http://localhost:8000/metrics | grep http_requests

# Check memory usage
curl http://localhost:8000/health/detailed
```

## Backup & Recovery

### Backup Strategy

#### 1. Automated Backups
```bash
# Daily backup cron job
0 2 * * * /path/to/streamworks-ki/scripts/deploy.sh backup

# Weekly full system backup
0 1 * * 0 /path/to/scripts/full_backup.sh
```

#### 2. Backup Verification
```bash
# Test database restore
docker-compose -f docker-compose.production.yml exec postgres \
    psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT COUNT(*) FROM training_files;"
```

### Recovery Procedures

#### 1. Database Recovery
```bash
# Stop application
docker-compose -f docker-compose.production.yml stop backend

# Restore database
docker-compose -f docker-compose.production.yml exec postgres \
    psql -U $POSTGRES_USER -d $POSTGRES_DB < backup_file.sql

# Start application
docker-compose -f docker-compose.production.yml start backend
```

#### 2. Full System Recovery
```bash
# Restore from backup
tar -xzf full_backup.tar.gz

# Restore environment
cp backup/.env.production .env.production

# Restore data
cp -r backup/data/* data/

# Redeploy
./scripts/deploy.sh deploy
```

## Security Best Practices

1. **Regular Updates**: Keep all components updated
2. **Access Control**: Limit access to production systems
3. **Monitoring**: Monitor for suspicious activities
4. **Encryption**: Use HTTPS for all communications
5. **Secrets Management**: Never commit secrets to version control
6. **Network Security**: Use firewalls and VPNs
7. **Audit Logs**: Maintain comprehensive audit trails
8. **Backup Security**: Encrypt and secure backups

## Support & Documentation

- **Internal Documentation**: See `/docs` directory
- **API Documentation**: Available at `/api/v1/docs`
- **Monitoring Dashboards**: Grafana at `http://localhost:3000`
- **Log Analysis**: Kibana at `http://localhost:5601`
- **Metrics**: Prometheus at `http://localhost:9090`

For additional support, contact the DevOps team or refer to the troubleshooting section above.