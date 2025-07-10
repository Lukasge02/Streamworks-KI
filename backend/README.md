# StreamWorks-KI Backend

## 🚀 Enterprise-Grade RAG + LLM System

StreamWorks-KI ist ein produktionsreifes AI-System, das Retrieval-Augmented Generation (RAG) mit Mistral 7B LLM und LoRA-Finetuning für XML-Generierung kombiniert.

### ✨ Features

- **🤖 Mistral 7B Integration**: Optimiert für deutsche Sprache
- **🔍 Advanced RAG**: Semantische Suche mit Embedding-basierter Retrieval
- **📄 Intelligente XML-Generierung**: LoRA-finetuned für Strukturdatenextraktion
- **🔒 Enterprise Security**: Multi-Layer Security mit Input Validation
- **📊 Production Monitoring**: Umfassendes Monitoring mit Prometheus/Grafana
- **⚡ High Performance**: <3s Response Time, optimierte Async-Verarbeitung
- **🧪 Comprehensive Testing**: Unit/Integration/Performance Tests
- **🚀 CI/CD Ready**: Automatisierte Deployments mit GitHub Actions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Web UI    │ │  Mobile App │ │  API Client │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway Layer                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   Nginx     │ │Rate Limiting│ │   SSL/TLS   │          │
│  │Load Balancer│ │ & Security  │ │   Security  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  FastAPI    │ │  Middleware │ │ Input Valid │          │
│  │   Router    │ │  Monitoring │ │  Sanitizer  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ RAG Service │ │ Mistral LLM │ │XML Generator│          │
│  │   + ChromaDB│ │   Service   │ │ + LoRA Fine │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ PostgreSQL  │ │  ChromaDB   │ │  File Store │          │
│  │  Database   │ │Vector Store │ │  Encrypted  │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Ollama (für Mistral 7B)
- Docker (optional)

### Installation

```bash
# 1. Clone Repository
git clone https://github.com/your-org/streamworks-ki.git
cd streamworks-ki/backend

# 2. Virtual Environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate  # Windows

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Environment Setup
cp .env.template .env
# Edit .env with your configurations

# 5. Database Setup
alembic upgrade head

# 6. Start Services
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Setup

```bash
# Development
docker-compose up -d

# Production
docker build -f Dockerfile.prod -t streamworks-ki:latest .
docker run -d --name streamworks-ki -p 8000:8000 --env-file .env.production streamworks-ki:latest
```

---

## 📖 API Documentation

### Base Endpoints

- **Health Check**: `GET /health`
- **API Docs**: `GET /docs` (Swagger UI)
- **Metrics**: `GET /api/v1/monitoring/metrics`

### Core Features

#### 1. Chat & Q&A
```bash
# Standard Chat with RAG
curl -X POST "http://localhost:8000/api/v1/chat/" \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Wie installiere ich StreamWorks?", "use_rag": true}'

# Dual-Mode Comparison
curl -X POST "http://localhost:8000/api/v1/chat/dual-mode" \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Erkläre die Backup-Strategie", "compare_responses": true}'
```

#### 2. Document Upload & Training
```bash
# Upload Training Document
curl -X POST "http://localhost:8000/api/v1/training/upload" \\
  -F "file=@manual.pdf" \\
  -F "category=documentation"

# Check Processing Status
curl -X GET "http://localhost:8000/api/v1/training/status/file_id"
```

#### 3. XML Generation
```bash
# Generate XML from Text
curl -X POST "http://localhost:8000/api/v1/xml/generate" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "Bestellung für 5 Laptops", "xml_type": "order", "use_lora": true}'
```

#### 4. Semantic Search
```bash
# Search Documents
curl -X POST "http://localhost:8000/api/v1/search/semantic" \\
  -H "Content-Type: application/json" \\
  -d '{"query": "Installation Guide", "top_k": 5}'
```

---

## 🔒 Security Features

### Multi-Layer Security Architecture

1. **Input Validation & Sanitization**
   - XSS Protection
   - SQL Injection Prevention
   - Command Injection Protection
   - Path Traversal Prevention

2. **Secret Management**
   - Encrypted secret storage
   - Environment-based configuration
   - Key rotation support

3. **File Upload Security**
   - MIME type validation
   - File size limits
   - Malware scanning ready
   - Secure filename handling

4. **Web Security Headers**
   - HSTS, CSP, X-Frame-Options
   - CORS configuration
   - Rate limiting

### Security Configuration

```python
# Security Headers
SECURITY_HEADERS = {
    'X-Frame-Options': 'SAMEORIGIN',
    'X-Content-Type-Options': 'nosniff',
    'Strict-Transport-Security': 'max-age=31536000'
}

# Rate Limiting
RATE_LIMITS = {
    '/api/v1/chat/': {'requests': 60, 'window': 60},
    '/api/v1/training/': {'requests': 10, 'window': 60}
}
```

---

## 📊 Monitoring & Observability

### Production Monitoring

- **Prometheus Metrics**: Performance, errors, system resources
- **Health Checks**: Comprehensive service monitoring
- **Alerting**: Automated alerts für kritische Metriken
- **Logging**: Structured logging mit Security Events

### Key Metrics

```bash
# System Status
curl http://localhost:8000/api/v1/monitoring/status

# Performance Metrics
curl http://localhost:8000/api/v1/monitoring/metrics

# Prometheus Metrics
curl http://localhost:8000/api/v1/monitoring/metrics/prometheus
```

---

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── test_security.py
│   ├── test_rag_service.py
│   └── test_xml_generation.py
├── integration/          # Integration tests
│   ├── test_api_endpoints.py
│   └── test_database.py
└── performance/          # Performance tests
    └── test_load.py
```

### Running Tests

```bash
# Unit Tests
pytest tests/unit/ -v --cov=app

# Integration Tests
pytest tests/integration/ -v

# Performance Tests
pytest tests/performance/ -v --benchmark-json=benchmark.json

# All Tests
pytest -v --cov=app --cov-report=html
```

---

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
```bash
# Set Production Environment Variables
export ENV=production
export DATABASE_URL="postgresql://user:pass@host:5432/streamworks_prod"
export SECRET_KEY="your-secret-key"
export ENCRYPTION_KEY="your-encryption-key"
```

2. **Database Migration**
```bash
alembic upgrade head
```

3. **Service Start**
```bash
# With Uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# With Docker
docker run -d --name streamworks-ki-prod \\
  --env-file .env.production \\
  -p 8000:8000 \\
  -v /opt/data:/app/data \\
  streamworks-ki:latest
```

---

## 📚 Documentation

### Available Documentation

- **[API Documentation](API_DOCUMENTATION.md)**: Complete API reference
- **[Security Documentation](SECURITY_DOCUMENTATION.md)**: Security architecture and best practices
- **[Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)**: Production deployment instructions
- **[Production Readiness Plan](../PRODUCTION_READINESS_PLAN.md)**: Enterprise readiness status

### Swagger UI

Interactive API documentation available at:
- Development: `http://localhost:8000/docs`
- Production: `https://api.streamworks-ki.com/docs`

---

## 🛠️ Development

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install

# Run in development mode
uvicorn app.main:app --reload --log-level debug
```

### Code Style

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/

# Security check
bandit -r app/
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Mistral Service Connection Error
```bash
# Check Ollama status
ollama list
ollama pull mistral:7b-instruct

# Restart Ollama
systemctl restart ollama
```

#### 2. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

#### 3. ChromaDB Vector Store Issues
```bash
# Reset vector database
rm -rf data/vector_db/*
curl -X POST http://localhost:8000/api/v1/rebuild-index
```

---

## 📞 Support

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/your-org/streamworks-ki/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/streamworks-ki/discussions)
- **Email**: support@streamworks-ki.com

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Version**: 2.1.0  
**Status**: Production Ready ✅  
**Last Updated**: 2025-07-08  
**Maintainers**: StreamWorks-KI Team