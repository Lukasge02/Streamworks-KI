# Streamworks-KI: Claude Code Projektanweisungen

> **Spezialisierte Claude-Anweisungen für das Streamworks-KI RAG System**  
> Enterprise RAG System mit modularer Backend-Architektur und XML-Generierung

---

## 📋 **Projekt-Übersicht**

**Streamworks-KI** ist ein hochmodernes RAG-System für Enterprise-Umgebungen mit:
- **Backend**: FastAPI mit 108+ Python-Dateien in modularer Service-Architektur
- **Frontend**: Next.js 15 mit 600+ TypeScript-Dateien
- **Features**: Dokumentenverarbeitung, RAG-basierte Fragebeantwortung, XML-Wizard

---

## 🏗️ **Backend-Architektur (Wichtig für Code-Änderungen)**

### Service-Module (Modular aufgebaut)
```
backend/services/
├── document/              # → Document Service Module
│   ├── crud_operations.py    # CRUD-Operationen für Dokumente
│   ├── document_service.py   # Hauptservice für Dokumentenverwaltung
│   └── processing_pipeline.py # Verarbeitungs-Pipeline
├── embeddings/            # → Embedding Service Module  
│   ├── embedding_service.py  # Haupt-Embedding Service
│   ├── local_embeddings.py   # Lokale Embeddings (Gamma)
│   └── openai_embeddings.py  # OpenAI Embeddings
├── rag/                   # → RAG Pipeline Module
│   ├── adaptive_retrieval.py # Intelligente Kontext-Auswahl
│   ├── qa_pipeline.py        # Question-Answering Pipeline
│   └── unified_rag_service.py # Vereinheitlichte RAG-Logik
└── [andere services...]
```

### Router-Module (API Endpoints)
```
backend/routers/
├── documents/             # → Modular Document API
│   ├── upload.py             # Upload-Endpoints
│   ├── crud.py              # CRUD-Endpoints  
│   └── search.py            # Search-Endpoints
├── chat.py               # Chat-API
├── folders.py            # Ordner-Management
└── xml_generator.py      # XML-Wizard API
```

---

## 🎯 **Frontend-Architektur**

### Komponenten-Struktur
```
frontend/src/components/
├── xml-wizard/            # → XML Wizard Feature
│   ├── XmlGenerator.tsx      # Hauptkomponente
│   ├── components/          # Sub-Komponenten
│   │   ├── ChapterNavigation.tsx
│   │   ├── WizardForm.tsx
│   │   └── XmlDisplay.tsx
│   └── hooks/              # Custom Hooks
│       ├── useWizardState.ts
│       └── useXMLPreview.ts
├── chat/                 # → Chat Interface
├── documents/            # → Document Management  
├── dashboard/            # → System Monitoring
└── ui/                   # → Reusable Components
```

### App Router Structure
```
frontend/src/app/
├── xml/                  # → XML Wizard Pages
├── chat/                 # → Chat Interface
└── documents/            # → Document Management
```

---

## ⚙️ **Entwicklungsrichtlinien**

### Code-Konventionen
- **Python**: PEP 8, async/await patterns, SQLAlchemy 2.0 ORM
- **TypeScript**: Strict types, React Query für Server State, Zustand für Client State  
- **Modularität**: Services sind in Module aufgeteilt - respektiere diese Struktur
- **Tests**: Pytest für Backend, Jest für Frontend

### Wichtige Patterns
```python
# Backend Service Pattern
class DocumentService:
    def __init__(self, db_service, embedding_service, vectorstore_service):
        self.db = db_service
        self.embeddings = embedding_service
        self.vectorstore = vectorstore_service
    
    async def process_document(self, file_path: str) -> ProcessedDocument:
        # Docling processing, embedding, vectorstore storage
```

```typescript
// Frontend Hook Pattern
export const useDocumentUpload = () => {
  const mutation = useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => queryClient.invalidateQueries(['documents'])
  })
}
```

---

## 📁 **Wichtige Dateipfade**

### Backend Key Files
- `backend/main.py` - FastAPI-Anwendung  
- `backend/config.py` - Konfiguration mit Pydantic Settings
- `backend/database.py` - SQLAlchemy Database Setup
- `backend/services/di_container.py` - Dependency Injection Container
- `backend/services/xml_template_engine.py` - XML-Generierung Engine

### Frontend Key Files  
- `frontend/src/app/layout.tsx` - Root Layout
- `frontend/src/components/DocumentManager.tsx` - Haupt-Dokumentenverwaltung
- `frontend/src/services/api.ts` - API Client
- `frontend/tailwind.config.js` - TailwindCSS Konfiguration

---

## 🔧 **Development Commands**

### Backend
```bash
cd backend
python main.py                    # Start server
pip install -r requirements.txt  # Install dependencies  
pytest                           # Run tests
```

### Frontend  
```bash
cd frontend
npm run dev                      # Start dev server
npm run dev:clean               # Start with cache clear
npm run build                   # Production build
npm run type-check              # TypeScript check
```

---

## 🚨 **Wichtige Coding-Regeln**

### 1. **Respektiere Modulare Struktur**
- Wenn du Document-Features änderst → verwende `services/document/`
- Wenn du Embedding-Features änderst → verwende `services/embeddings/`  
- Wenn du RAG-Features änderst → verwende `services/rag/`

### 2. **Database Patterns**
```python
# Immer async/await verwenden
async def get_documents(db: AsyncSession, folder_id: Optional[int] = None):
    query = select(Document)
    if folder_id:
        query = query.filter(Document.folder_id == folder_id)
    result = await db.execute(query)
    return result.scalars().all()
```

### 3. **Frontend State Management**
```typescript
// Server State → React Query
const { data: documents, isLoading } = useQuery({
  queryKey: ['documents', folderId],
  queryFn: () => fetchDocuments(folderId)
})

// Client State → Zustand
const useDocumentStore = create<DocumentStore>((set) => ({
  selectedDocuments: [],
  setSelectedDocuments: (docs) => set({ selectedDocuments: docs })
}))
```

### 4. **Error Handling**
```python
# Backend: HTTPException mit detail
raise HTTPException(
    status_code=404,
    detail={"error": "Document not found", "document_id": doc_id}
)
```

```typescript
// Frontend: React Query error handling
const mutation = useMutation({
  mutationFn: uploadDocument,
  onError: (error) => {
    toast.error(`Upload failed: ${error.message}`)
  }
})
```

---

## 🔄 **XML-Wizard Spezifika**

### Backend (xml_generator.py)
- Ollama Integration für lokale LLM-Generierung
- Template Engine in `xml_template_engine.py`
- Streamworks-spezifische XML-Struktur

### Frontend (xml-wizard/)
- Monaco Editor für XML-Bearbeitung
- Real-time Preview mit Syntax-Highlighting
- Chapter-basierte Navigation

---

## 📊 **Testing Guidelines**

### Backend Tests
```python
# Verwende pytest mit async support
@pytest.mark.asyncio
async def test_document_upload(test_db, test_file):
    service = DocumentService(test_db)
    result = await service.upload_document(test_file)
    assert result.status == "processed"
```

### Frontend Tests
```typescript
// Jest + React Testing Library
test('document upload shows progress', async () => {
  render(<DocumentUpload />)
  // ... test logic
})
```

---

## 🎯 **Häufige Aufgaben & Patterns**

### Neues Document Feature hinzufügen
1. Backend: Erweitere `services/document/` Module
2. Router: Füge Endpoint in `routers/documents/` hinzu
3. Frontend: Verwende React Query für API-Calls
4. UI: Füge zu `components/documents/` hinzu

### Neue RAG-Funktionalität
1. Backend: Erweitere `services/rag/` Module  
2. Teste mit `services/unified_rag_service.py`
3. Frontend: Chat-Interface in `components/chat/`

### XML-Wizard Feature
1. Backend: `routers/xml_generator.py` und `services/xml_template_engine.py`
2. Frontend: `components/xml-wizard/` Module
3. Verwende Monaco Editor für Code-Editing

---

## 💡 **Performance Considerations**

- **Async/await**: Immer für I/O-Operationen verwenden
- **Caching**: Multi-Level Caching implementiert
- **Chunking**: Large files werden chunked verarbeitet
- **WebSockets**: Für real-time features verwenden

---

**🔧 Diese Anweisungen helfen dir, effizient mit der modularen Streamworks-KI Architektur zu arbeiten!**