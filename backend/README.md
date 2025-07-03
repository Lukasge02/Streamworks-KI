# StreamWorks-KI Backend

## 🚀 Quick Start

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Development Server
```bash
# Start server
uvicorn app.main:app --reload --port 8000

# Server läuft auf: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hallo SKI, erstelle einen XML-Stream"}'
```

#### Stream Generation
```bash
curl -X POST http://localhost:8000/api/v1/streams/generate-stream \
  -H "Content-Type: application/json" \
  -d '{
    "streamName": "DailyProcessing",
    "jobName": "ProcessData",
    "dataSource": "/data/input",
    "outputPath": "/data/output",
    "schedule": "daily"
  }'
```

## 🏗️ Architecture

```
app/
├── main.py              # FastAPI application
├── core/               # Configuration & logging
├── api/v1/             # API endpoints
├── services/           # Business logic
├── models/             # Data models
├── utils/              # Utilities
└── repositories/       # Data access (future)
```

## 🔧 Features

- ✅ FastAPI with async support
- ✅ CORS configured for frontend
- ✅ Structured logging with Loguru
- ✅ Mock LLM service (SKI responses)
- ✅ XML stream generation
- ✅ Pydantic data validation
- ✅ Health checks
- ✅ API documentation

## 🎯 Next Steps

1. Connect to real LLM (DialoGPT)
2. Add database integration
3. Implement file upload
4. Add authentication
5. LoRA fine-tuning