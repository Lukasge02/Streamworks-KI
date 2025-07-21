# 🚀 StreamWorks-KI: Enterprise Q&A System

[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-green)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-red)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-Academic-yellow)](LICENSE)

**Enterprise-grade Q&A system with RAG-based document retrieval, built for StreamWorks support automation.**

---

## 🎯 **Project Overview**

StreamWorks-KI is a sophisticated Q&A system that combines modern AI technologies with enterprise-level software engineering practices. Built as a Bachelor Thesis project at FHDW Paderborn in collaboration with Arvato Systems/Bertelsmann.

### **Key Features**
- 🤖 **RAG-based Q&A**: Intelligent document retrieval with Mistral 7B LLM
- 📚 **Enterprise Document Management**: Hierarchical folder structure with batch operations
- 🎨 **Modern UI**: React + TypeScript with Glassmorphism design
- ⚡ **High Performance**: AsyncIO backend with ChromaDB vector storage
- 🔄 **Real-time Features**: Streaming responses and live file upload progress
- 🌐 **German Optimization**: Specifically optimized for German StreamWorks documentation

---

## 🚀 **Quick Start**

### **Prerequisites**
- Node.js 18+
- Python 3.9+
- Ollama with Mistral 7B model

### **Installation**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd StreamWorks-KI
   ```

2. **Setup Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload --port 8000
   ```

3. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Setup Ollama**
   ```bash
   ollama serve
   ollama pull mistral:7b-instruct
   ```

### **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## 📂 **Project Structure**

```
StreamWorks-KI/
├── frontend/                 # React + TypeScript Frontend
│   ├── src/components/      # Enterprise React Components
│   ├── src/store/           # Zustand State Management
│   └── CLAUDE.md            # Frontend Development Guide
├── backend/                  # Python FastAPI Backend
│   ├── app/api/v1/         # REST API Endpoints
│   ├── app/services/       # Business Logic Services
│   └── CLAUDE.md            # Backend Development Guide
├── CLAUDE.md                # Main Project Documentation
└── README.md               # Project Overview
```

---

## 🛠️ **Technology Stack**

### **Frontend**
- **React 18** + **TypeScript** + **Vite**
- **Tailwind CSS** with Glassmorphism design
- **Zustand** state management
- **Lucide React** icons

### **Backend**
- **FastAPI** + **SQLAlchemy 2.0** + **Pydantic v2**
- **ChromaDB** vector database
- **Sentence Transformers** (E5-Multilingual)
- **AsyncIO** throughout

### **AI & ML**
- **Mistral 7B** via Ollama
- **RAG Pipeline** with semantic search
- **German language** optimization

---

## 🎯 **Core Features**

### **Q&A System**
- Semantic document search with ChromaDB
- Context-aware response generation
- German language optimization
- Streaming response delivery

### **Document Management**
- Hierarchical folder structure
- Drag & drop file upload with progress
- Batch operations and search
- Supports: PDF, TXT, MD, JSON, XML, DOCX, XLSX

### **Enterprise UI/UX**
- Glassmorphism design
- Responsive (mobile-first)
- Real-time updates
- Professional error handling

---

## 🎓 **Academic Context**

Bachelor Thesis project at FHDW Paderborn demonstrating:
- **Software Engineering**: Enterprise architecture
- **AI Integration**: RAG systems and LLM integration  
- **Modern Development**: TypeScript + Python best practices
- **User Experience**: Professional UI/UX design

---

## 📞 **Contact**

**Student**: Ravel-Lukas Geck  
**Institution**: FHDW Paderborn  
**Supervisor**: Prof. Dr. Christian Ewering  
**Company**: Arvato Systems / Bertelsmann

---

**🎯 StreamWorks-KI demonstrates the integration of modern AI capabilities with enterprise software development practices.**