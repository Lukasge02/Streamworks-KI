# 🚀 StreamWorks-KI

**Enterprise Q&A System with RAG-based document retrieval for StreamWorks support automation.**

StreamWorks-KI combines modern AI technologies (Mistral 7B, ChromaDB) with enterprise software practices to deliver intelligent document-based question answering in German.

## 🎯 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker (for PostgreSQL)
- Ollama with Mistral 7B

### Installation

1. **Clone and Setup**
   ```bash
   git clone https://github.com/Lukasge02/Streamworks-KI.git
   cd Streamworks-KI
   ```

2. **Start PostgreSQL**
   ```bash
   docker run --name streamworks-postgres \
     -e POSTGRES_USER=streamworks \
     -e POSTGRES_PASSWORD=streamworks_secure_2025 \
     -e POSTGRES_DB=streamworks_ki \
     -p 5432:5432 -d postgres:15
   ```

3. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python3 -m uvicorn app.main:app --reload
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access Application**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## 📚 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - System design and technology stack
- [Features Guide](docs/FEATURES.md) - Detailed feature documentation  
- [Development Guide](docs/DEVELOPMENT.md) - Setup and coding standards
- [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment instructions

## 🎓 Academic Project

Bachelor Thesis at FHDW Paderborn with Arvato Systems/Bertelsmann  
**Author**: Ravel-Lukas Geck  
**Supervisor**: Prof. Dr. Christian Ewering  
**License**: Academic Use