"""
Seed Documents
Uploads sample documents to the system for testing purposes.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.rag.document_service import document_service

DOCUMENTS = [
    {
        "filename": "StreamWorks_Overview.txt",
        "content": """
StreamWorks ist eine Plattform für die KI-gestützte Erstellung von XML-Streams.
Sie ermöglicht es Benutzern, natürliche Sprache zu verwenden, um komplexe Stream-Definitionen zu generieren.
Die Architektur basiert auf einem Python-Backend (FastAPI) und einem Next.js Frontend.
Die RAG-Komponente nutzt Qdrant für die Vektorsuche und OpenAI für die Generierung.
Benutzer können Dokumente hochladen, die dann verarbeitet und indexiert werden.
""",
    },
    {
        "filename": "RAG_Architecture.txt",
        "content": """
Die RAG-Architektur von StreamWorks umfasst folgende Komponenten:
1. DocumentService: Verarbeitet Uploads (PDF, DOCX) und extrahiert Text.
2. VectorStore: Speichert Embeddings in Qdrant.
3. HybridSearch: Kombiniert semantische Suche mit BM25 Keyword-Suche.
4. Reranker: Nutzt FlashRank, um die Relevanz der Suchergebnisse zu verbessern.
5. QueryService: Orchestriert den Abfrageprozess und kommuniziert mit dem LLM.
""",
    },
    {
        "filename": "Deployment_Guide.txt",
        "content": """
Deployment von StreamWorks:
Das System wird containerisiert mit Docker bereitgestellt.
Es gibt Container für Backend, Frontend, Qdrant, MinIO und Postgres.
Die Konfiguration erfolgt über Umgebungsvariablen (.env).
Für das Backend wird Uvicorn als Server verwendet.
Das Frontend wird als statischer Export oder Node-Server betrieben.
""",
    },
]


def seed():
    print("🌱 Seeding Vector Store with sample documents...")
    for doc in DOCUMENTS:
        print(f"   Processing {doc['filename']}...")
        document_service.process_text(
            text_content=doc["content"], filename=doc["filename"]
        )
    print("✅ Seeding complete.")


if __name__ == "__main__":
    seed()
