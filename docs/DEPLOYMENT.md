# 🚀 StreamWorks-KI Deployment Guide

## Production Environment Setup

### System Requirements

#### Minimum Hardware
- **CPU**: 4 cores (8 recommended)
- **RAM**: 16GB (32GB recommended)
- **Storage**: 100GB SSD
- **Network**: 100Mbps uplink

#### Software Requirements
- Ubuntu 22.04 LTS or similar
- Docker 24+ & Docker Compose 2.20+
- Nginx 1.24+
- PostgreSQL 15+
- Python 3.9+
- Node.js 18+

### Pre-deployment Checklist

- [ ] Domain name configured with SSL certificate
- [ ] Firewall rules configured (ports 80, 443, 22)
- [ ] Backup strategy in place
- [ ] Monitoring tools configured
- [ ] Environment variables secured
- [ ] Database credentials rotated
- [ ] API keys secured

## Docker Deployment

### 1. Production Docker Compose

Create `docker-compose.production.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.production
    restart: always
    environment:
      - ENV=production
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      - OLLAMA_HOST=${OLLAMA_HOST}
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./data:/app/data
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "127.0.0.1:8000:8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.production
      args:
        - VITE_API_URL=${API_URL}
    restart: always
    ports:
      - "127.0.0.1:3000:80"

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
```

### 2. Backend Dockerfile

Create `backend/Dockerfile.production`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 3. Frontend Dockerfile

Create `frontend/Dockerfile.production`:

```dockerfile
# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4. Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000" always;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            limit_req zone=general burst=20 nodelay;
        }

        # Backend API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Rate limiting for API
            limit_req zone=api burst=20 nodelay;
            
            # Timeouts for long-running requests
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

## Deployment Steps

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create deployment directory
sudo mkdir -p /opt/streamworks-ki
cd /opt/streamworks-ki
```

### 2. Deploy Application

```bash
# Clone repository
git clone https://github.com/Lukasge02/Streamworks-KI.git .

# Create environment file
cp .env.production.example .env.production
# Edit .env.production with secure values

# Create required directories
mkdir -p data nginx/ssl nginx/logs

# Generate SSL certificates (or copy existing)
# For production, use Let's Encrypt:
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check logs
docker-compose -f docker-compose.production.yml logs -f
```

### 3. Database Setup

```bash
# Run migrations
docker-compose -f docker-compose.production.yml exec backend python scripts/migrate_to_postgres.py

# Create admin user (if applicable)
docker-compose -f docker-compose.production.yml exec backend python scripts/create_admin.py

# Verify database
docker-compose -f docker-compose.production.yml exec postgres psql -U streamworks -d streamworks_ki -c "\dt"
```

## Monitoring & Health Checks

### 1. Health Check Endpoints

Configure monitoring to check:
- `https://your-domain.com/health` - Overall system health
- `https://your-domain.com/api/v1/health` - Backend health
- `https://your-domain.com/api/v1/analytics/health` - Analytics service

### 2. Logging

```bash
# View logs
docker-compose -f docker-compose.production.yml logs -f backend
docker-compose -f docker-compose.production.yml logs -f frontend

# Log rotation
cat > /etc/logrotate.d/streamworks-ki << EOF
/opt/streamworks-ki/nginx/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        docker-compose -f /opt/streamworks-ki/docker-compose.production.yml exec nginx nginx -s reload
    endscript
}
EOF
```

### 3. Monitoring Setup

```bash
# Install monitoring stack (optional)
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v /opt/prometheus:/etc/prometheus \
  prom/prometheus

docker run -d \
  --name grafana \
  -p 3001:3000 \
  grafana/grafana
```

## Backup & Recovery

### 1. Automated Backups

Create `/opt/streamworks-ki/scripts/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/streamworks-ki"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose -f /opt/streamworks-ki/docker-compose.production.yml exec -T postgres \
  pg_dump -U streamworks streamworks_ki | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup data files
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /opt/streamworks-ki/data

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/streamworks-ki/.env.production

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### 2. Schedule Backups

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/streamworks-ki/scripts/backup.sh >> /var/log/streamworks-backup.log 2>&1
```

### 3. Recovery Process

```bash
# Stop services
docker-compose -f docker-compose.production.yml down

# Restore database
gunzip < /opt/backups/streamworks-ki/db_20240120_020000.sql.gz | \
  docker-compose -f docker-compose.production.yml exec -T postgres \
  psql -U streamworks streamworks_ki

# Restore data files
tar -xzf /opt/backups/streamworks-ki/data_20240120_020000.tar.gz -C /

# Start services
docker-compose -f docker-compose.production.yml up -d
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Install UFW
sudo apt install ufw

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Fail2ban Setup

```bash
# Install fail2ban
sudo apt install fail2ban

# Configure for nginx
cat > /etc/fail2ban/jail.local << EOF
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /opt/streamworks-ki/nginx/logs/error.log
maxretry = 10
findtime = 60
bantime = 3600
EOF

sudo systemctl restart fail2ban
```

### 3. Security Updates

```bash
# Enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Performance Tuning

### 1. PostgreSQL Optimization

Edit PostgreSQL configuration:

```sql
-- Adjust based on available RAM
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET max_connections = 200;
```

### 2. Application Scaling

```yaml
# Scale backend workers in docker-compose.production.yml
backend:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

## Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```bash
   docker-compose -f docker-compose.production.yml logs [service_name]
   ```

2. **Database Connection Issues**
   ```bash
   docker-compose -f docker-compose.production.yml exec backend python -c "from app.core.database_postgres import test_connection; test_connection()"
   ```

3. **High Memory Usage**
   ```bash
   docker stats
   docker-compose -f docker-compose.production.yml restart [service_name]
   ```

### Emergency Procedures

1. **Rollback Deployment**
   ```bash
   git checkout [previous_version]
   docker-compose -f docker-compose.production.yml build
   docker-compose -f docker-compose.production.yml up -d
   ```

2. **Emergency Maintenance Mode**
   ```nginx
   # Add to nginx.conf
   location / {
       return 503;
       error_page 503 @maintenance;
   }
   
   location @maintenance {
       rewrite ^(.*)$ /maintenance.html break;
   }
   ```