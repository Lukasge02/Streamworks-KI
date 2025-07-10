# StreamWorks-KI Security Documentation

## 🔒 Enterprise Security Framework

### Security Architecture Overview

StreamWorks-KI implementiert mehrschichtige Sicherheitsmaßnahmen nach Enterprise-Standards:

```
┌─────────────────────────────────────────────────┐
│                  External Layer                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Nginx     │ │  Firewall   │ │   SSL/TLS   ││
│  │Rate Limiting│ │   Rules     │ │   Certs     ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│                Application Layer                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │Input Valdtn │ │   CORS      │ │   Headers   ││
│  │& Sanitizing │ │Middleware   │ │ Security    ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│                   Data Layer                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │Secret Mgmt  │ │  Database   │ │File Upload  ││
│  │Encryption   │ │ Encryption  │ │  Security   ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
```

---

## 🛡️ Input Validation & Sanitization

### Input Sanitizer Implementation

**Location**: `backend/app/models/validation.py`

#### Features:
- **XSS Protection**: Entfernt gefährliche HTML/JavaScript-Tags
- **SQL Injection Prevention**: Sanitisiert Datenbankabfragen
- **Command Injection Protection**: Filtert Shell-Commands
- **Path Traversal Prevention**: Blockiert gefährliche Pfade

#### Usage Example:
```python
from app.models.validation import InputSanitizer

sanitizer = InputSanitizer()

# Text sanitization
clean_text = sanitizer.sanitize_text(user_input)

# SQL-safe string
safe_query = sanitizer.sanitize_sql(query_param)

# File path validation
safe_path = sanitizer.validate_file_path(file_path)
```

#### Protected Patterns:
```python
DANGEROUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',           # Script tags
    r'javascript:',                         # JavaScript URLs
    r'eval\s*\(',                          # eval() calls
    r'document\.cookie',                    # Cookie access
    r'\.\./',                              # Path traversal
    r'[\x00-\x1f\x7f-\x9f]',              # Control characters
    r'(DROP|DELETE|UPDATE|INSERT)\s+',     # SQL keywords
    r'(\||&|;|\$\()',                      # Command injection
]
```

### File Upload Security

**Location**: `backend/app/models/validation.py:FileUploadValidator`

#### Security Measures:
```python
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/markdown'
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
```

#### Validation Process:
1. **MIME Type Check**: Verifiziert Dateityp
2. **Magic Number Validation**: Prüft echten Dateityp
3. **Size Limit**: Beschränkt Dateigröße
4. **Filename Sanitization**: Entfernt gefährliche Zeichen
5. **Virus Scanning**: (Integration möglich)

---

## 🔐 Secret Management

### SecretManager Implementation

**Location**: `backend/app/core/security.py`

#### Features:
- **Fernet Encryption**: AES 128 Verschlüsselung
- **Environment-based Keys**: Sichere Schlüsselverwaltung
- **Automatic Key Rotation**: Unterstützung für Key-Rotation
- **Audit Logging**: Alle Secret-Zugriffe werden geloggt

#### Usage:
```python
from app.core.security import SecretManager

secret_manager = SecretManager()

# Encrypt sensitive data
encrypted = secret_manager.encrypt_secret("sensitive_data")

# Decrypt when needed
decrypted = secret_manager.decrypt_secret(encrypted)

# Generate secure API keys
api_key = secret_manager.generate_api_key()
```

#### Environment Configuration:
```bash
# Required environment variables
ENCRYPTION_KEY=base64-encoded-fernet-key
SECRET_KEY=random-32-char-secret
```

### Password Security

#### Password Hashing:
```python
from app.core.security import hash_password, verify_password

# Hash password with salt
hashed = hash_password("user_password")

# Verify password
is_valid = verify_password("user_password", hashed)
```

**Implementation**: bcrypt mit Cost Factor 12

---

## 🌐 Web Security Headers

### Security Headers Middleware

**Location**: `backend/app/main.py` (via monitoring middleware)

#### Implemented Headers:
```python
SECURITY_HEADERS = {
    'X-Frame-Options': 'SAMEORIGIN',
    'X-Content-Type-Options': 'nosniff', 
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}
```

### CORS Configuration

```python
# Secure CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Response-Time", "X-Request-ID"]
)
```

---

## 🚦 Rate Limiting & DDoS Protection

### Application-Level Rate Limiting

#### Implementation in Nginx:
```nginx
# Rate limiting configuration
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=uploads:10m rate=2r/s;

server {
    location /api/v1/chat/ {
        limit_req zone=api burst=20 nodelay;
    }
    
    location /api/v1/training/upload {
        limit_req zone=uploads burst=5 nodelay;
    }
}
```

#### Python-Level Protection:
```python
# In middleware/monitoring.py
RATE_LIMITS = {
    '/api/v1/chat/': {'requests': 60, 'window': 60},      # 60 req/min
    '/api/v1/search/': {'requests': 100, 'window': 60},   # 100 req/min
    '/api/v1/training/': {'requests': 10, 'window': 60}   # 10 req/min
}
```

### DDoS Protection Layers:
1. **CloudFlare/CDN**: External DDoS protection
2. **Nginx**: Connection limiting, request throttling
3. **Firewall**: IP-based blocking
4. **Application**: Smart rate limiting per endpoint

---

## 🗄️ Database Security

### Connection Security

```python
# Secure database connection
DATABASE_URL = "postgresql://username:password@host:5432/db?sslmode=require"

# Connection pooling with limits
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 30
SQLALCHEMY_POOL_TIMEOUT = 30
```

### SQL Injection Prevention

#### Parameterized Queries:
```python
# Secure query example
from sqlalchemy import text

stmt = text("SELECT * FROM documents WHERE category = :category AND status = :status")
result = await session.execute(stmt, {"category": category, "status": status})
```

#### ORM Protection:
```python
# SQLAlchemy ORM automatically escapes
documents = await session.execute(
    select(Document).where(
        Document.category == category,
        Document.status == status
    )
)
```

### Data Encryption at Rest

#### Sensitive Fields:
```python
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False)
    # Encrypted sensitive data
    api_key = Column(EncryptedType(String, secret_key, AesEngine, 'pkcs5'))
```

---

## 📁 File System Security

### Secure File Handling

#### Upload Directory Protection:
```python
SECURE_UPLOAD_CONFIG = {
    'UPLOAD_PATH': '/app/data/uploads',
    'PERMISSIONS': 0o750,          # Owner: rwx, Group: r-x, Other: none
    'MAX_SIZE': 50 * 1024 * 1024, # 50 MB
    'QUARANTINE_PATH': '/app/data/quarantine'
}
```

#### File Path Sanitization:
```python
def secure_filename(filename: str) -> str:
    """Generate secure filename"""
    # Remove dangerous characters
    filename = re.sub(r'[^\w\s-.]', '', filename)
    # Prevent path traversal
    filename = filename.replace('..', '')
    # Limit length
    filename = filename[:255]
    return filename
```

### Directory Permissions:
```bash
# Secure directory setup
sudo mkdir -p /app/data/{uploads,training_data,vector_db,logs}
sudo chown -R streamworks:streamworks /app/data
sudo chmod -R 750 /app/data
sudo chmod -R 640 /app/data/logs
```

---

## 🔍 Security Monitoring & Logging

### Security Event Logging

**Location**: `backend/app/middleware/production_monitoring.py`

#### Monitored Events:
```python
SECURITY_EVENTS = {
    'AUTHENTICATION_FAILURE': 'warning',
    'AUTHORIZATION_FAILURE': 'warning', 
    'INPUT_VALIDATION_FAILURE': 'info',
    'RATE_LIMIT_EXCEEDED': 'warning',
    'SUSPICIOUS_FILE_UPLOAD': 'warning',
    'SQL_INJECTION_ATTEMPT': 'critical',
    'XSS_ATTEMPT': 'warning',
    'ADMIN_ACCESS': 'info'
}
```

#### Log Format:
```json
{
  "timestamp": "2025-07-08T10:30:00Z",
  "event_type": "AUTHENTICATION_FAILURE",
  "severity": "warning",
  "source_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "endpoint": "/api/v1/admin",
  "details": {
    "reason": "invalid_api_key",
    "attempt_count": 3
  },
  "request_id": "req_123456"
}
```

### Intrusion Detection

#### Automated Monitoring:
```python
class SecurityMonitor:
    def detect_anomalies(self, request_data):
        """Detect suspicious patterns"""
        alerts = []
        
        # Multiple failed authentication attempts
        if self.check_failed_auth_rate(request_data.ip) > 5:
            alerts.append("BRUTE_FORCE_ATTEMPT")
        
        # Unusual request patterns
        if self.check_request_anomaly(request_data):
            alerts.append("SUSPICIOUS_ACTIVITY")
            
        # Large file uploads from unknown sources
        if self.check_suspicious_upload(request_data):
            alerts.append("SUSPICIOUS_FILE_UPLOAD")
            
        return alerts
```

---

## 🚨 Incident Response

### Security Incident Classification

| Severity | Description | Response Time | Actions |
|----------|-------------|---------------|---------|
| **Critical** | Data breach, system compromise | < 15 minutes | Immediate isolation, emergency team |
| **High** | Successful attack, privilege escalation | < 1 hour | Block source, patch vulnerability |
| **Medium** | Failed attack attempt, suspicious activity | < 4 hours | Investigate, enhance monitoring |
| **Low** | Minor security event, policy violation | < 24 hours | Log, routine review |

### Automated Response Actions

```python
class IncidentResponse:
    def handle_security_event(self, event_type, severity, context):
        """Automated incident response"""
        
        if severity == "critical":
            # Immediate lockdown
            self.enable_maintenance_mode()
            self.block_suspicious_ips(context['source_ips'])
            self.notify_security_team(urgent=True)
            
        elif severity == "high":
            # Enhanced monitoring
            self.increase_logging_level()
            self.block_source_ip(context['source_ip'])
            self.notify_security_team()
            
        elif severity == "medium":
            # Standard monitoring
            self.log_security_event(event_type, context)
            self.update_threat_intelligence()
```

### Emergency Contacts

```yaml
Security Team:
  Primary: security@streamworks-ki.com
  Emergency: +49-XXX-XXXXXXX
  Slack: #security-alerts

System Administrators:
  Primary: admin@streamworks-ki.com
  Emergency: +49-XXX-XXXXXXX
  Slack: #system-alerts

Management:
  CISO: ciso@streamworks-ki.com
  CTO: cto@streamworks-ki.com
```

---

## 🧪 Security Testing & Validation

### Automated Security Testing

#### CI/CD Security Pipeline:
```yaml
# .github/workflows/security-monitoring.yml
security-tests:
  - bandit (SAST)
  - semgrep (SAST)
  - safety (dependency check)
  - trivy (container scan)
  - codeql (code analysis)
```

#### Manual Security Testing:
```bash
# Regular security audits
bandit -r backend/app/ -f json
semgrep --config=auto backend/app/
safety check --json
pip-audit --format json
```

### Penetration Testing

#### Scheduled Tests:
- **Monthly**: Automated vulnerability scans
- **Quarterly**: Professional penetration testing
- **Annually**: Full security audit

#### Test Areas:
1. **Web Application Security**: OWASP Top 10
2. **API Security**: Authentication, authorization, input validation
3. **Infrastructure Security**: Network, system configuration
4. **Social Engineering**: Phishing, pretexting (if applicable)

---

## 📋 Compliance & Standards

### Security Frameworks

#### OWASP Compliance:
- ✅ **A01 - Broken Access Control**: Role-based access control
- ✅ **A02 - Cryptographic Failures**: Strong encryption, secure protocols
- ✅ **A03 - Injection**: Input validation, parameterized queries
- ✅ **A04 - Insecure Design**: Security by design principles
- ✅ **A05 - Security Misconfiguration**: Secure defaults, hardening
- ✅ **A06 - Vulnerable Components**: Dependency scanning, updates
- ✅ **A07 - Authentication Failures**: Strong authentication, rate limiting
- ✅ **A08 - Software Integrity Failures**: Code signing, supply chain security
- ✅ **A09 - Logging Failures**: Comprehensive security logging
- ✅ **A10 - Server-Side Request Forgery**: URL validation, network controls

#### GDPR Considerations:
- **Data Minimization**: Nur notwendige Daten sammeln
- **Purpose Limitation**: Daten nur für angegebene Zwecke nutzen
- **Storage Limitation**: Automatische Datenlöschung nach Aufbewahrungszeit
- **Security**: Angemessene technische und organisatorische Maßnahmen

### Security Certifications

#### Target Certifications:
- **ISO 27001**: Information Security Management
- **SOC 2 Type II**: Security, Availability, Confidentiality
- **BSI Grundschutz**: German IT security standards

---

## 🔧 Security Configuration Checklist

### Production Security Checklist

#### ✅ Application Security
- [ ] Input validation enabled for all endpoints
- [ ] XSS protection implemented
- [ ] SQL injection protection verified
- [ ] File upload security configured
- [ ] Rate limiting enabled
- [ ] Security headers implemented
- [ ] CORS properly configured
- [ ] Error handling doesn't leak information

#### ✅ Infrastructure Security  
- [ ] SSL/TLS certificates installed and configured
- [ ] Firewall rules configured
- [ ] SSH key-based authentication only
- [ ] Regular security updates applied
- [ ] Log monitoring configured
- [ ] Backup encryption enabled
- [ ] Network segmentation implemented
- [ ] Intrusion detection system active

#### ✅ Data Security
- [ ] Database encryption at rest
- [ ] Sensitive data encrypted in application
- [ ] Secure secret management implemented
- [ ] Regular backup verification
- [ ] Data retention policies defined
- [ ] Personal data handling compliant
- [ ] Audit logging configured
- [ ] Access controls properly implemented

#### ✅ Operational Security
- [ ] Security incident response plan documented
- [ ] Regular security training conducted
- [ ] Vulnerability assessment scheduled
- [ ] Penetration testing planned
- [ ] Security metrics monitoring
- [ ] Emergency contacts updated
- [ ] Business continuity plan tested
- [ ] Security documentation current

---

**Security Version**: 1.0  
**Last Updated**: 2025-07-08  
**Next Security Review**: 2025-10-08  
**Security Team**: security@streamworks-ki.com