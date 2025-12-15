# StreamWorks Installations- und Konfigurationsanleitung

## Systemanforderungen

### Hardware

**Minimal (bis 50 Streams):**
- 4 CPU Cores
- 8 GB RAM
- 50 GB SSD

**Empfohlen (50-500 Streams):**
- 8 CPU Cores
- 16 GB RAM
- 200 GB SSD

**Enterprise (500+ Streams):**
- 16+ CPU Cores
- 32+ GB RAM
- 500 GB+ SSD (NVMe)
- Cluster-Setup empfohlen

### Software

- **Betriebssystem**: Ubuntu 22.04 LTS, RHEL 8+, Windows Server 2019+
- **Datenbank**: PostgreSQL 14+ (15 empfohlen)
- **Runtime**: .NET 8.0 Runtime
- **Optional**: Redis 7.0+ für Caching

## Installation

### 1. Repository hinzufügen

```bash
# Ubuntu/Debian
curl -fsSL https://packages.streamworks.example.com/gpg.key | sudo apt-key add -
echo "deb https://packages.streamworks.example.com/apt stable main" | sudo tee /etc/apt/sources.list.d/streamworks.list
sudo apt update
```

### 2. Pakete installieren

```bash
sudo apt install streamworks-server streamworks-agent streamworks-cli
```

### 3. Datenbank einrichten

```bash
sudo -u postgres psql
CREATE DATABASE streamworks;
CREATE USER streamworks WITH ENCRYPTED PASSWORD 'SecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE streamworks TO streamworks;
```

### 4. Konfiguration erstellen

Datei: `/etc/streamworks/config.yaml`

```yaml
server:
  host: 0.0.0.0
  port: 8080
  tls:
    enabled: true
    certFile: /etc/streamworks/cert.pem
    keyFile: /etc/streamworks/key.pem

database:
  host: localhost
  port: 5432
  name: streamworks
  user: streamworks
  password: ${DB_PASSWORD}  # Aus Umgebungsvariable

logging:
  level: INFO
  format: json
  output: /var/log/streamworks/server.log

security:
  jwtSecret: ${JWT_SECRET}
  sessionTimeout: 3600
  maxLoginAttempts: 5
  lockoutDuration: 900

workers:
  maxConcurrent: 10
  queueSize: 100
  timeout: 7200

features:
  webhooks: true
  apiRateLimit: 100
  metricsEnabled: true
```

### 5. Service starten

```bash
sudo systemctl enable streamworks-server
sudo systemctl start streamworks-server
sudo systemctl status streamworks-server
```

## Agent-Installation

Agents führen Jobs auf Remote-Systemen aus.

### 1. Agent installieren

```bash
sudo apt install streamworks-agent
```

### 2. Agent konfigurieren

Datei: `/etc/streamworks/agent.yaml`

```yaml
agent:
  name: agent-01
  serverUrl: https://streamworks.example.com:8080
  token: ${AGENT_TOKEN}
  
capabilities:
  - sql
  - command
  - file_transfer
  
resources:
  maxJobs: 5
  cpuLimit: 80
  memoryLimit: 4096
```

### 3. Agent starten

```bash
sudo systemctl enable streamworks-agent
sudo systemctl start streamworks-agent
```

## Cluster-Setup

Für Hochverfügbarkeit empfehlen wir:

1. **Load Balancer**: HAProxy oder nginx
2. **3+ Server-Instanzen**: Für Failover
3. **PostgreSQL mit Streaming Replication**
4. **Redis Cluster**: Für verteiltes Caching

## Backup und Wiederherstellung

### Automatisches Backup

```bash
# Konfiguration in /etc/streamworks/backup.yaml
backup:
  schedule: "0 2 * * *"  # Täglich um 02:00
  retention: 30  # 30 Tage aufbewahren
  location: /backup/streamworks
  compression: gzip
```

### Manuelles Backup

```bash
streamworks-cli backup create --output /backup/streamworks-$(date +%Y%m%d).tar.gz
```

### Wiederherstellung

```bash
streamworks-cli backup restore --input /backup/streamworks-20240115.tar.gz
```

## Monitoring

### Health Check

```bash
curl https://streamworks.example.com:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.5.1",
  "uptime": 86400,
  "database": "connected",
  "agents": 5,
  "activeRuns": 12
}
```

### Prometheus Metriken

Metriken unter `/metrics`:
- `streamworks_streams_total`
- `streamworks_runs_active`
- `streamworks_runs_completed_total`
- `streamworks_runs_failed_total`
- `streamworks_job_duration_seconds`

## Upgrade

```bash
sudo apt update
sudo apt upgrade streamworks-server
sudo systemctl restart streamworks-server
```

**Hinweis**: Vor Major-Upgrades immer Backup erstellen!
