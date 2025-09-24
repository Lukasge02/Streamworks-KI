# 5. Implementierung

Die technische Realisierung des in Kapitel 4 konzipierten Prototypen für effiziente Workload-Automatisierung durch Self-Service und Künstliche Intelligenz erfolgte durch die systematische Umsetzung der dort entwickelten Architektur- und Designprinzipien. Dieses Kapitel dokumentiert die praktische Überführung der theoretischen Konzepte in eine funktionsfähige Anwendung und erläutert die getroffenen Technologieentscheidungen vor dem Hintergrund der spezifischen Anforderungen des StreamWorks-Umfelds.

Die Implementierung folgt dabei einer Service-Oriented Architecture, die eine klare Trennung der Geschäftsdomänen XML-Generierung, RAG-Hilfssystem und Benutzerinteraktion ermöglicht. Besonderer Wert wurde auf die Entwicklung eines leistungsfähigen LangExtract-Systems gelegt, das natürlichsprachliche Eingaben in strukturierte XML-Parameter transformiert und dabei eine Erkennungsgenauigkeit von 88,9% für deutsche StreamWorks-Terminologie erreicht. Das System wurde als hochmodulares Backend mit Python und FastAPI sowie ein responsives Frontend mit Next.js und TypeScript realisiert.

## 5.1 Auswahl des Technologiestacks

Die Technologieauswahl orientierte sich an den funktionalen und nicht-funktionalen Anforderungen des StreamWorks-KI Systems, insbesondere der Notwendigkeit zur Verarbeitung asynchroner KI-Operationen, der Skalierbarkeit bei gleichzeitigen Benutzersessions und der Integrationsfähigkeit in das bestehende StreamWorks-Ökosystem.

### Backend-Technologiestack: Python und FastAPI

Für die Backend-Implementierung wurde Python in Kombination mit dem FastAPI-Framework gewählt. Diese Entscheidung basiert primär auf der nativen Unterstützung asynchroner Verarbeitung, die für die I/O-intensiven Operationen der Large Language Model-Anbindung von entscheidender Bedeutung ist. Während einer typischen Parameter-Extraktion werden mehrere sequenzielle API-Calls an OpenAI oder lokale Ollama-Instanzen durchgeführt, wobei Wartezeiten von 1-3 Sekunden pro Request auftreten. Die `async`/`await`-Syntax von FastAPI ermöglicht es, diese Wartezeiten effizient zu überbrücken und die Anwendung für parallele Benutzeranfragen skalierbar zu gestalten.

Ein weiterer entscheidender Faktor war die automatische Generierung von OpenAPI-konformer Dokumentation, die während der Entwicklungsphase für die Frontend-Integration essentiell war. Die interaktive Swagger-UI unter `/docs` ermöglichte rapid prototyping und vereinfachte das Testing der entwickelten API-Endpoints erheblich. Darüber hinaus bietet die native Pydantic-Integration von FastAPI umfassende Datenvalidierung und Serialisierung, was bei der Transformation unstrukturierter Benutzereingaben in strukturierte XML-Parameter von großer Bedeutung ist.

### Frontend-Technologiestack: Next.js und React-Ökosystem

Für die Frontend-Implementierung wurde Next.js 15 mit TypeScript als Entwicklungsplattform gewählt. Diese Entscheidung wurde durch mehrere Faktoren motiviert: Erstens bietet der App Router von Next.js 15 eine moderne Routing-Architektur, die sowohl Client-Side Navigation als auch serverseitige Optimierungen ermöglicht. Dies erwies sich als besonders relevant für die verschiedenen Anwendungsbereiche des Systems – das Chat-Interface unter `/chat`, das LangExtract-System unter `/langextract` und die XML-Generierung unter `/xml` erfordern jeweils spezifische Performance-Optimierungen.

Die komponentenbasierte Architektur von React ermöglichte die Entwicklung wiederverwendbarer UI-Module, die unabhängig entwickelt und getestet werden konnten. Das LangExtract-System beispielsweise besteht aus spezialisierten Komponenten wie `ParameterOverview`, `SmartSuggestions` und `XMLGenerationPanel`, die sich zu einem kohärenten Benutzerinterface zusammenfügen. Die strikte TypeScript-Integration mit aktivierten Compiler-Flags reduziert Laufzeitfehler erheblich und verbessert die Entwicklererfahrung durch IntelliSense und automatische Refactoring-Unterstützung.

### Datenbank-Strategie: Hybride Architektur

Die Implementierung nutzt eine duale Datenbankstrategie, die den unterschiedlichen Datentypen und Zugriffsmustern des Systems Rechnung trägt. Strukturierte relationale Daten wie Benutzersessions, Authentifizierungsinformationen und Chat-Verläufe werden in PostgreSQL mit SQLAlchemy 2.0 verwaltet. Die Entscheidung für PostgreSQL basiert auf der ausgezeichneten Python-Integration, der ACID-Konformität für kritische Geschäftsdaten und der bewährten Skalierbarkeit in Enterprise-Umgebungen.

Parallel dazu wird Qdrant als spezialisierte Vektordatenbank für die Speicherung und Abfrage von Dokumenten-Embeddings eingesetzt. Diese architektonische Trennung ermöglicht es, die Vorteile beider Datenbanktypen optimal zu nutzen: PostgreSQL für transaktionale Konsistenz und komplexe relationale Abfragen, Qdrant für effiziente Ähnlichkeitssuchen in hochdimensionalen Vektorräumen. Die Embeddings werden mit dem `sentence-transformers/all-MiniLM-L6-v2` Modell in 384-dimensionalen Vektorräumen generiert und ermöglichen semantische Dokumentensuche mit Sub-Sekunden-Antwortzeiten.

### Containerisierung und Deployment-Strategie

Docker wurde als Containerisierungsplattform gewählt, um die komplexe Service-Landschaft zu kapseln und Portabilität zwischen verschiedenen Deployment-Umgebungen zu gewährleisten. Die Docker-basierte Architektur ermöglicht es, Backend-Services, Frontend-Anwendung, Datenbanken und externe Dependencies in isolierten Containern zu betreiben, was sowohl die Entwicklung als auch das Deployment erheblich vereinfacht.

## 5.2 Backend-Implementierung: Die Service-Architektur

Das Backend folgt einer strikten Service-Oriented Architecture, die die in Kapitel 4 definierten Bounded Contexts in konkrete Python-Module überführt. Die Architektur basiert auf Domain-Driven Design Prinzipien, wobei jeder Service eine klar definierte Geschäftsverantwortlichkeit besitzt und über wohldefinierte Interfaces mit anderen Services kommuniziert.

### Modulare Projektstruktur

Die Backend-Architektur gliedert sich in logische Module, die den identifizierten Geschäftsdomänen entsprechen. Das `services/ai/`-Verzeichnis enthält 21 spezialisierte Module für KI-Operationen, wobei das `langextract/`-Unterverzeichnis das Kernsystem der Parameter-Extraktion beherbergt. Die XML-Generierung ist im `services/xml_generation/`-Modul mit dem Template-Engine und Parameter-Mapper gekapselt. Das RAG-Hilfssystem residiert in `services/rag/` und umfasst die gesamte Dokumenten-Verarbeitungspipeline.

Diese Struktur spiegelt bewusst die fachlichen Abgrenzungen wider, die in Kapitel 4 entwickelt wurden. Jedes Modul kann unabhängig entwickelt, getestet und deployed werden, was sowohl die Wartbarkeit als auch die Skalierbarkeit des Systems erhöht. Die strikte Kapselung ermöglicht es beispielsweise, das LangExtract-System zu erweitern, ohne die RAG-Funktionalität zu beeinträchtigen.

### FastAPI als API-Gateway

Die zentrale `main.py` implementiert FastAPI als API-Gateway, das die verschiedenen Service-Router koordiniert und Cross-Cutting Concerns wie CORS, Performance-Monitoring und Authentifizierung zentral verwaltet:

```python
# backend/main.py - Zentrale Service-Koordination
app = FastAPI(
    title="StreamWorks Document Management",
    description="Enterprise-grade document management system",
    version="2.0.0"
)

# Include routers für verschiedene Domänen
app.include_router(auth)                    # Authentifizierung
app.include_router(langextract_chat)        # LangExtract-System
app.include_router(xml_generator)           # XML-Generierung
app.include_router(chat_rag_test)          # RAG-Hilfssystem
```

Das API-Gateway implementiert einen strukturierten Middleware-Stack, der essenzielle Querschnittsfunktionalitäten bereitstellt. Das Performance-Monitoring erfasst Response-Zeiten für alle Endpoints und ermöglicht die Identifikation von Engpässen in Produktionsumgebungen. Die CORS-Konfiguration ermöglicht sichere Cross-Origin-Requests vom Frontend, während das RAG-Metrics-Middleware die Qualität der generierten Antworten kontinuierlich überwacht.

### Dependency Injection Container

Das Herzstück der Service-Architektur bildet ein benutzerdefinierter Dependency Injection Container in `backend/services/di_container.py`, der die Entkopplung von Services gewährleistet und Testbarkeit ermöglicht. Der Container implementiert das Singleton-Pattern für ressourcenintensive Services wie den Qdrant-Client oder die LLM-Anbindung, während zustandsabhängige Services wie Session-Handler als Instanzen erstellt werden.

Die Container-Implementierung ermöglicht es, komplexe Service-Abhängigkeiten deklarativ zu definieren. Der `UnifiedLangExtractService` beispielsweise benötigt den `EnhancedJobTypeDetector`, den `EnhancedUnifiedParameterExtractor` und den `SessionPersistenceService`. Diese Abhängigkeiten werden automatisch aufgelöst und in der korrekten Reihenfolge instanziiert, was sowohl die Entwicklung als auch das Testing erheblich vereinfacht.

## 5.3 Implementierung der Kernfunktion: Der XML-Generierungsprozess

Die Kernfunktionalität des Systems – die automatisierte XML-Generierung aus natürlichsprachlichen Eingaben – wurde als dreistufiger Prozess implementiert, der die in Kapitel 4.3 konzipierten Algorithmen in produktive Python-Klassen überführt.

### 5.3.1 Umsetzung des Enhanced Job Type Detectors

Der Job Type Detector bildet die erste Stufe der Verarbeitungskette und implementiert einen Multi-Layer-Ansatz zur Erkennung von StreamWorks-Job-Typen. Die Klasse `EnhancedJobTypeDetector` in `backend/services/ai/enhanced_job_type_detector.py` erreicht eine gemessene Accuracy von 88,9% durch die Kombination von Pattern-Matching, semantischer Kontextanalyse und gewichtetem Confidence-Scoring.

Die erste Erkennungsschicht basiert auf erweiterten regulären Ausdrücken, die speziell für deutsche StreamWorks-Terminologie optimiert wurden. Für FILE_TRANSFER-Jobs werden Patterns wie `(?:daten[trs]*transfer|file\s*transfer|datei[en]*\s*transfer)` mit 95%iger Confidence verwendet, während strukturelle Patterns wie `zwischen\s+([a-zA-Z0-9_\-]+)\s+(?:und|zu|nach)\s+([a-zA-Z0-9_\-]+)` System-zu-System-Transfers mit 92%iger Confidence erkennen.

Die zweite Schicht implementiert eine semantische Kontextanalyse, die benachbarte Keywords und Phrasen evaluiert, um die Pattern-basierte Erkennung zu verstärken. Begriffe wie "Agent", "Server" oder "Synchronisation" in der Nähe von Transfer-Patterns erhöhen die Confidence um bis zu 30%. Die finale Entscheidung erfolgt durch einen gewichteten Scoring-Algorithmus, der alle Layer-Ergebnisse zu einem finalen Confidence-Score kombiniert.

### 5.3.2 Realisierung der Parameter-Extraktion

Die Parameter-Extraktion implementiert eine Zustandsmaschine in der Klasse `EnhancedUnifiedParameterExtractor`, die den Dialogverlauf steuert und iterativ alle benötigten Parameter sammelt. Die Zustandsübergänge werden durch regelbasierte Logik gesteuert, die den aktuellen Extraktionsfortschritt evaluiert.

Der Extraktionsprozess beginnt im `INITIAL`-Zustand und wechselt nach der ersten Benutzereingabe zu `COLLECTING_REQUIRED`. In diesem Zustand werden die für den erkannten Job-Typ obligatorischen Parameter gesammelt. Sind alle Pflichtparameter vorhanden, erfolgt der Übergang zu `COLLECTING_OPTIONAL`, wo weitere Parameter zur Vervollständigung des XML-Templates gesammelt werden. Bei einer Vollständigkeit von über 80% wechselt das System in den `VALIDATION`-Zustand.

Die Session-Persistierung erfolgt über SQLAlchemy in PostgreSQL, um eine zustandserhaltende Kommunikation über mehrere HTTP-Requests zu ermöglichen. Das `LangExtractSessionDB`-Model in `backend/models/parameter_models.py` speichert den aktuellen Zustand, extrahierte Parameter und Metadata wie Confidence-Scores und Completion-Percentage. Diese Architektur ermöglicht es Benutzern, Sessions zu unterbrechen und später fortzusetzen, ohne den Extraktionsfortschritt zu verlieren.

### 5.3.3 Implementierung der Template-basierten XML-Generierung

Die XML-Generierung erfolgt ausschließlich über Jinja2-Templates in `backend/services/xml_generation/template_engine.py` und verzichtet bewusst auf LLM-basierte Generierung, um Konsistenz und Validierbarkeit zu gewährleisten. Diese Entscheidung basiert auf der Erkenntnis, dass XML-Strukturen deterministisch und schema-konform sein müssen, was durch template-basierte Generierung besser gewährleistet werden kann als durch generative KI-Modelle.

Die `TemplateEngine`-Klasse initialisiert eine Jinja2-Umgebung mit speziellen Security-Konfigurationen und registriert benutzerdefinierte Filter für StreamWorks-spezifische Formatierungen. Der `stream_prefix`-Filter beispielsweise stellt sicher, dass alle Stream-Namen den erforderlichen `zsw_`-Prefix erhalten, während der `format_datetime`-Filter Zeitstempel in das von StreamWorks erwartete Format konvertiert.

Der Parameter-Mapper in `backend/services/xml_generation/parameter_mapper.py` implementiert intelligente Feldmappings, die extrahierte Parameter an Template-Variablen binden. Dabei werden sowohl exakte String-Matches als auch Fuzzy-Matching-Algorithmen eingesetzt, um auch bei Schreibfehlern oder Synonymen korrekte Zuordnungen zu gewährleisten. Fehlende Parameter werden durch job-type-spezifische Defaults ergänzt, um vollständige XML-Templates zu generieren.

## 5.4 Implementierung des RAG-Hilfesystems

Das RAG-Hilfssystem implementiert eine moderne Retrieval-Augmented Generation Pipeline, die Benutzern kontextuell relevante Informationen zu StreamWorks-Konzepten bereitstellt. Die Implementierung folgt dabei dem in Kapitel 4.4 entwickelten Architekturentwurf für den "StreamWorks Assistant".

### 5.4.1 Realisierung der Dokumenten-Verarbeitungspipeline

Die Dokumenten-Pipeline in `backend/services/document/enhanced_document_processor.py` implementiert Layout-Aware Chunking für optimale Retrieval-Performance. Anders als naive Text-Splitting-Verfahren berücksichtigt dieser Ansatz die dokumenteninhärente Struktur wie Überschriften, Absätze und Listenpunkte, um semantisch kohärente Chunks zu erstellen.

Der Chunking-Algorithmus analysiert zunächst das PDF-Layout mit der `pdfplumber`-Bibliothek und identifiziert strukturelle Elemente. Anschließend werden Chunks gebildet, die maximal 512 Tokens umfassen, aber niemals strukturelle Grenzen durchbrechen. Dies gewährleistet, dass zusammengehörige Informationen in einem Chunk verbleiben und bei der späteren Retrieval-Phase vollständig verfügbar sind.

Die generierten Chunks werden mit dem `sentence-transformers/all-MiniLM-L6-v2` Modell in 384-dimensionale Vektoren transformiert und in der Qdrant-Vektordatenbank gespeichert. Dabei werden zusätzliche Metadaten wie Dokumententyp, Seitenzahl und Chunk-Index persistiert, die später für die Quellenangaben in den generierten Antworten verwendet werden.

### 5.4.2 Umsetzung des Hybrid-Retrieval-Mechanismus

Das Hybrid-Retrieval in `backend/services/rag/unified_rag_service.py` kombiniert Vektor- und lexikalische Suche für optimale Recall- und Precision-Werte. Die beiden Suchverfahren werden parallel ausgeführt, um die Gesamtlatenz zu minimieren. Die Vektorsuche nutzt cosine similarity auf den 384-dimensionalen Embeddings, während die lexikalische Suche auf BM25-Scoring basiert.

Die Ergebnisse beider Suchverfahren werden durch Reciprocal Rank Fusion (RRF) kombiniert, einem etablierten Algorithmus zur Fusion von Ranking-Listen. RRF gewichtet die Rangpositionen in beiden Listen und erstellt ein kombiniertes Ranking, das sowohl semantische Ähnlichkeit als auch exakte Term-Matches berücksichtigt. Der Fusion-Parameter k=60 wurde empirisch optimiert, um die beste Balance zwischen den beiden Suchverfahren zu erreichen.

### 5.4.3 Anbindung des Sprachmodells und Source Grounding

Die finale Antwortgenerierung erfolgt durch strukturiertes Prompt-Engineering mit automatischer Quellenangabe. Der Prompt wird dynamisch aus den relevantesten Dokumenten-Chunks zusammengesetzt, wobei jeder Chunk mit einer eindeutigen Quellenreferenz versehen wird. Das System-Prompt instruiert das LLM explizit, Quellenangaben in der Form `[Quelle X]` zu verwenden, um die Nachvollziehbarkeit der generierten Antworten zu gewährleisten.

Die LLM-Anbindung unterstützt sowohl OpenAI-Models über API als auch lokale Ollama-Instanzen für datenschutzkritische Deployments. Die Prompt-Temperatur wird auf 0.1 gesetzt, um deterministische und faktentreue Antworten zu fördern. Die maximale Token-Anzahl ist auf 512 begrenzt, um prägnante und fokussierte Antworten zu gewährleisten.

## 5.5 Frontend-Implementierung: Die Benutzeroberfläche

Das Frontend implementiert eine moderne, responsive Benutzeroberfläche, die sowohl die komplexen LangExtract-Workflows als auch die intuitive Bedienung des RAG-Hilfssystems ermöglicht. Die Implementierung basiert auf React-Komponenten mit TypeScript und folgt modernen UI/UX-Prinzipien.

### 5.5.1 React-Komponenten und State Management

Die Hauptkomponente `LangExtractInterface` in `frontend/src/components/langextract-chat/LangExtractInterface.tsx` orchestriert das gesamte LangExtract-Benutzererlebnis. Die Komponente implementiert lokales State Management mit React Hooks für UI-Zustand und React Query für Server-State-Synchronisation.

```typescript
// State Management in LangExtractInterface
const [sessionId, setSessionId] = useState<string>(uuidv4())
const [messages, setMessages] = useState<LangExtractMessage[]>([])

const { data: session, isLoading } = useQuery({
  queryKey: ['langextract-session', sessionId],
  queryFn: () => fetchLangExtractSession(sessionId),
  refetchInterval: 30000, // Auto-refresh alle 30s
})
```

Die React Query-Integration ermöglicht optimistische Updates und automatische Wiederholung fehlgeschlagener Requests. Sessions werden alle 30 Sekunden aktualisiert, um sicherzustellen, dass der UI-Zustand mit dem Backend synchron bleibt. Die Mutation für Message Processing implementiert umfassendes Error Handling und bietet Benutzern visuelles Feedback über Toast-Notifications.

Die `ParameterOverview`-Komponente visualisiert den aktuellen Extraktionsfortschritt mit einem Progress-Indikator und einer strukturierten Darstellung der gesammelten Parameter. Pflichtfelder werden von optionalen Feldern unterschieden, und bereits extrahierte Werte werden hervorgehoben. Diese Darstellung hilft Benutzern zu verstehen, welche Informationen noch benötigt werden, um die XML-Generierung zu vervollständigen.

### 5.5.2 API-Integration und Error Handling

Der API-Service in `frontend/src/services/api.service.ts` kapselt die Backend-Kommunikation und implementiert umfassendes Error Handling. Die Axios-Instanz wird mit Interceptors konfiguriert, die automatisch Authentifizierungs-Token hinzufügen und HTTP-Fehler in strukturierte Error-Objects transformieren.

```typescript
// API Service mit strukturiertem Error Handling
async processLangExtractMessage(sessionId: string, message: string): Promise<LangExtractResponse> {
  const response = await this.axiosInstance.post(`/api/langextract/sessions/${sessionId}/messages`, {
    message,
    timestamp: new Date().toISOString()
  })
  return response.data
}
```

Die TypeScript-Integration gewährleistet Type-Safety für alle API-Responses. Interface-Definitionen in `frontend/src/types/api.types.ts` spezifizieren die erwarteten Datenstrukturen und ermöglichen Compile-Time-Validierung. Dies reduziert Runtime-Fehler erheblich und verbessert die Entwicklererfahrung durch präzise Code-Completion und automatische Refactoring-Unterstützung.

## 5.6 Integration und Deployment des Prototypen

Die Integration aller Systemkomponenten erfolgte durch Docker-basierte Containerisierung und eine koordinierte Deployment-Strategie, die sowohl lokale Entwicklung als auch Produktionsumgebungen unterstützt.

### Docker-basierte Service-Orchestrierung

Die vollständige Service-Landschaft wird durch `docker-compose.yml` orchestriert, die alle notwendigen Komponenten und deren Abhängigkeiten definiert. Das Backend wird als Python 3.10-Container mit allen Dependencies aus `requirements.txt` bereitgestellt. Qdrant läuft als separater Container mit persistentem Storage, um Vektordaten zwischen Restarts zu erhalten.

```yaml
# docker-compose.yml - Service-Orchestrierung
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [qdrant]
    environment:
      - QDRANT_URL=http://qdrant:6333

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
    volumes: [qdrant_storage:/qdrant/storage]
```

Health Checks sind für alle kritischen Services konfiguriert und prüfen sowohl die Erreichbarkeit als auch die funktionale Verfügbarkeit. Das Backend Health Check unter `/health/detailed` validiert die Konnektivität zu PostgreSQL, Qdrant und den konfigurierten LLM-Services. Diese umfassenden Checks ermöglichen es, Infrastruktur-Probleme schnell zu identifizieren und zu beheben.

### CI/CD Pipeline Konzept

Das Konzept für eine automatisierte CI/CD-Pipeline basiert auf GitHub Actions und implementiert einen mehrstufigen Deployment-Prozess. Die Pipeline umfasst separate Jobs für Backend-Tests (pytest mit Coverage), Frontend-Tests (TypeScript-Validation, Linting, Build), Security-Scans (Safety, Bandit, npm audit) und Integration-Tests.

Der Docker-Build-Job erstellt produktionsreife Container-Images nur nach erfolgreichem Abschluss aller Tests. Deployment erfolgt stufenweise: Feature-Branches werden in eine Staging-Umgebung deployed, während der main-Branch automatisch in die Produktionsumgebung überführt wird. Diese Strategie gewährleistet, dass nur getestete und validierte Änderungen in die Produktion gelangen.

Die Monitoring-Strategie umfasst Application Performance Monitoring mit automatischer Erfassung von Request-Latenz und Error-Rates. Slow Queries werden automatisch geloggt, und Performance-Metriken werden als HTTP-Header exponiert. Diese Observability ermöglicht es, Performance-Regressions schnell zu identifizieren und die Systemleistung kontinuierlich zu optimieren.

Die Implementierung des StreamWorks-KI Prototypen demonstriert die erfolgreiche Umsetzung einer komplexen, KI-gestützten Workload-Automatisierungslösung. Durch den systematischen Einsatz moderner Architekturprinzipien und bewährter Technologien konnte ein produktionsreifes System entwickelt werden, das sowohl die funktionalen Anforderungen der automatisierten XML-Generierung als auch die nicht-funktionalen Anforderungen bezüglich Performance und Wartbarkeit erfüllt. Die modulare Service-Architektur und die containerisierte Deployment-Strategie bilden das technologische Fundament für die in Kapitel 6 evaluierten Leistungsmetriken.