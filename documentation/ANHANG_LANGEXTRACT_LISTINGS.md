# Appendix Listings – Streamworks-KI Prototype

## Listing A1 – Asynchroner LangExtract-Nachrichtenfluss
**Einfügen:** Anhang A.1, Bezug zu Kapitel 5.2 „Backend-Implementierung mit FastAPI“.

Der Ausschnitt zeigt, wie eine eingehende Nachricht durch Erkennung, Extraktion und Antwortformulierung fließt und verdeutlicht den in Kapitel 5.2 beschriebenen orchestrierten Service-Layer.

```python
@dataclass
class LangExtractState:
    session_id: str
    job_type: str | None
    confidence: float
    parameters: dict[str, Any]


async def handle_message(store: SessionStore, detector: JobDetector,
                         extractor: ParameterExtractor, responder: Responder,
                         session_id: str, message: str) -> LangExtractResponse:
    state = await store.load(session_id)
    if state.job_type is None or state.confidence < 0.7:
        result = await detector.analyse(message)
        if result.confidence >= 0.7:
            state.job_type = result.job_type
            state.confidence = result.confidence

    if state.job_type:
        extraction = await extractor.collect(message, state.job_type, state.parameters)
        state.parameters.update(extraction.parameters)
        completion = extraction.completion
    else:
        completion = 0.0

    reply = responder.compose(state.job_type, completion, state.parameters)
    await store.append_messages(session_id, message, reply)
    await store.save(state)

    return LangExtractResponse(session_id=session_id,
                               job_type=state.job_type,
                               confidence=state.confidence,
                               parameters=state.parameters,
                               completion=completion,
                               message=reply)
```

## Listing A2 – Mehrstufige Job-Typ-Erkennung
**Einfügen:** Anhang A.2, Bezug zu Kapitel 5.2.1 „Architekturprinzipien und Services“.

Das Beispiel illustriert die Kombination aus Pattern-Abgleich, unscharfer Suche und Kontextsignalen, die den in der Arbeit beschriebenen Detection-Stack vereinfacht nachbildet.

```python
class LayeredJobDetector:
    patterns: dict[str, list[re.Pattern]]
    synonyms: dict[str, list[str]]
    context_terms: dict[str, set[str]]

    def evaluate(self, text: str) -> DetectionResult:
        text = text.lower()
        scores = {key: 0.0 for key in self.patterns}

        for job, compiled in self.patterns.items():
            if any(p.search(text) for p in compiled):
                scores[job] = max(scores[job], 0.85)

        for job, terms in self.synonyms.items():
            if any(term in text for term in terms):
                scores[job] = max(scores[job], 0.75)

        for job, keywords in self.context_terms.items():
            hit_ratio = len(keywords.intersection(text.split())) / max(len(keywords), 1)
            scores[job] = max(scores[job], min(0.65 + hit_ratio, 0.9))

        job, confidence = max(scores.items(), key=lambda item: item[1])
        return DetectionResult(job_type=job if confidence >= 0.7 else None,
                               confidence=confidence)
```

## Listing A3 – Fortschrittsbewertung für Parameter
**Einfügen:** Anhang A.3, Bezug zu Kapitel 5.3 „LangExtract Service Implementation“.

Die Funktion misst den Parameterfüllstand pro Job-Typ und spiegelt das in Kapitel 5.3 erläuterte Fortschrittsfeedback wider.

```python
REQUIRED_PARAMS = {
    "FILE_TRANSFER": {"source_server", "target_server", "source_path", "target_path"},
    "SAP": {"sap_system", "transaction_code", "table_name", "export_path"},
    "STANDARD": {"script_path", "server", "arguments"},
}


def completion_report(job_type: str, provided: dict[str, Any]) -> ParameterProgress:
    required = REQUIRED_PARAMS.get(job_type, set())
    present = {key for key in required if provided.get(key)}
    ratio = len(present) / len(required) if required else 0.0
    missing = sorted(required - present)
    return ParameterProgress(job_type=job_type,
                              completion=ratio,
                              missing=missing,
                              parameters={key: provided.get(key) for key in present})
```

## Listing A4 – XML-Template-Befüllung mit Sicherheitschecks
**Einfügen:** Anhang A.4, Bezug zu Kapitel 5.4 „XML-Generierung und Template Engine“.

Der Ausschnitt zeigt eine minimierte Variante der Template-Befüllung inklusive Pflichtfeldprüfung, wie sie im Kapitel zur XML-Automatisierung beschrieben wird.

```python
def render_xml(template: Template, mappings: dict[str, str], values: dict[str, Any]) -> str:
    missing = [key for key in mappings if not values.get(key)]
    if missing:
        raise ValueError(f"missing fields: {', '.join(missing)}")

    context = {alias: values[key] for alias, key in mappings.items()}
    return template.render(**context)
```

## Listing A5 – Vereinfachter RAG-Abfragezyklus
**Einfügen:** Anhang A.5, Bezug zu Kapitel 6.3 „Evaluierung des RAG-Systems“.

Der Code veranschaulicht den Retrieval-Flow aus Einbettung, Vektor-Suche und Antwortaggregation und stützt die Evaluationsbeschreibung in Kapitel 6.3.

```python
async def answer_question(embeddings: EmbeddingClient, store: VectorStore,
                          llm: ChatModel, question: str) -> str:
    query_vector = await embeddings.embed(question)
    top_chunks = await store.search(query_vector, limit=4)
    context = "\n".join(chunk.text for chunk in top_chunks)
    prompt = f"Kontext:\n{context}\n\nFrage: {question}"
    return await llm.complete(prompt)
```

## Listing A6 – Frontend-Mutation für LangExtract
**Einfügen:** Anhang A.6, Bezug zu Kapitel 5.5 „Frontend-Implementierung mit Next.js“.

Die Mutation spiegelt den in Kapitel 5.5 beschriebenen UX-Flow mit Status-Feedback wider und zeigt, wie Nachrichten an das Backend gesendet werden.

```typescript
const processMessage = useMutation({
  mutationFn: async (message: string) => {
    const { data } = await api.post<LangExtractResponse>(`/langextract/sessions/${sessionId}/messages`, { message })
    return data
  },
  onMutate: () => setTyping(true),
  onSuccess: (response) => {
    setTyping(false)
    queryClient.invalidateQueries({ queryKey: ['langextract-session', sessionId] })
    if (response.job_type && response.confidence >= 0.9) toast.success(`Job erkannt: ${response.job_type}`)
  },
  onError: () => {
    setTyping(false)
    toast.error('Verarbeitung fehlgeschlagen')
  }
})

const submitMessage = async (event: FormEvent<HTMLFormElement>) => {
  event.preventDefault()
  if (!text.trim()) return
  const payload = text.trim()
  setText('')
  await processMessage.mutateAsync(payload)
}
```

## Listing A7 – Persistente Sitzungsverwaltung
**Einfügen:** Anhang A.7, Bezug zu Kapitel 5.3 „LangExtract Service Implementation“.

Der Ausschnitt verdeutlicht das asynchrone Lesen und Speichern von Sitzungen, wie es für die in Kapitel 5.3 beschriebene Zustandsverwaltung erforderlich ist.

```python
class SessionStore:
    def __init__(self, backend: SessionBackend):
        self._backend = backend

    async def load(self, session_id: str) -> LangExtractState:
        raw = await self._backend.read(session_id)
        return LangExtractState(**raw) if raw else LangExtractState(session_id, None, 0.0, {})

    async def save(self, state: LangExtractState) -> None:
        payload = asdict(state)
        payload["updated_at"] = datetime.utcnow().isoformat()
        await self._backend.write(state.session_id, payload)

    async def append_messages(self, session_id: str, user: str, assistant: str) -> None:
        await self._backend.append_history(session_id, {"user": user, "assistant": assistant})
```

## Listing A8 – Parameter-Normalisierung und Vorbelegung
**Einfügen:** Anhang A.8, Bezug zu Kapitel 5.3 „LangExtract Service Implementation“.

Das Beispiel zeigt, wie Rohwerte vereinheitlicht und fehlende Parameter mit sinnvollen Standardwerten aus Kapitel 5.3 ergänzt werden.

```python
DEFAULTS = {
    "FILE_TRANSFER": {"retry_count": 3, "audit_log": True},
    "SAP": {"client": "100", "language": "DE"},
}


def normalize_parameters(job_type: str, values: dict[str, Any]) -> dict[str, Any]:
    normalized = {key: str(value).strip() for key, value in values.items() if value is not None}
    for key, default in DEFAULTS.get(job_type, {}).items():
        normalized.setdefault(key, default)
    if "source_path" in normalized:
        normalized["source_path"] = normalized["source_path"].rstrip('/') + '/'
    return normalized
```

## Listing A9 – Mehrstufige XML-Validierung
**Einfügen:** Anhang A.9, Bezug zu Kapitel 6.1 „Evaluierung der XML-Ergebnisse“.

Die Funktion kombiniert Schema-, Geschäfts- und Sicherheitsprüfung und illustriert die in Kapitel 6.1 dargestellten Qualitätsmetriken.

```python
def validate_xml(xml: str, schema: XMLSchema, rules: list[Callable[[ElementTree], None]]) -> ValidationSummary:
    tree = ElementTree.fromstring(xml)
    schema.assertValid(tree)
    for rule in rules:
        rule(tree)
    if "<!ENTITY" in xml:
        raise ValueError("entity declarations are not permitted")
    return ValidationSummary(is_valid=True, checked_rules=len(rules) + 1)
```

## Listing A10 – RAG-Dokumenten-Chunking
**Einfügen:** Anhang A.10, Bezug zu Kapitel 4.3 „Konzeption des Wissensspeichers“.

Die Routine illustriert den in Kapitel 4.3 beschriebenen Prozess, Dokumente in semantisch handhabbare Chunks zu zerlegen, bevor sie eingebettet werden.

```python
def chunk_document(text: str, max_tokens: int = 200) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    buffer: list[str] = []
    for word in words:
      buffer.append(word)
      if len(buffer) >= max_tokens:
          chunks.append(" ".join(buffer))
          buffer.clear()
    if buffer:
        chunks.append(" ".join(buffer))
    return chunks
```

## Listing A11 – Zustandsspeicher für LangExtract-Frontend
**Einfügen:** Anhang A.11, Bezug zu Kapitel 5.5 „Frontend-Implementierung mit Next.js“.

Das Snippet demonstriert den in Kapitel 5.5 erwähnten Einsatz eines globalen Stores zur Verwaltung von Session- und Fortschrittsdaten.

```typescript
interface LangExtractStore {
  sessionId: string | null
  completion: number
  setSession: (id: string) => void
  setCompletion: (value: number) => void
}

export const useLangExtractStore = create<LangExtractStore>((set) => ({
  sessionId: null,
  completion: 0,
  setSession: (id) => set({ sessionId: id }),
  setCompletion: (value) => set({ completion: value })
}))
```

## Listing A12 – Stream-Orchestrierung für Standard-Jobs
**Einfügen:** Anhang A.12, Bezug zu Kapitel 4.2 „Konzeption der Prozessarchitektur“.

Die Routine zeigt, wie StartPoint, Jobs und EndPoint zu einem Stream kombiniert werden und greift das in Kapitel 4.2 erläuterte Orchestrierungsmodell auf.

```python
def build_standard_stream(name: str, start: dict[str, Any], jobs: list[dict[str, Any]], end: dict[str, Any]) -> dict[str, Any]:
    stream = {"name": name, "components": [start, *jobs, end]}
    stream["metadata"] = {"created_at": datetime.utcnow().isoformat(), "job_count": len(jobs)}
    return stream


def validate_stream(stream: dict[str, Any]) -> None:
    if not stream["components"] or stream["components"][0]["type"] != "START":
        raise ValueError("stream requires START component")
    if stream["components"][-1]["type"] != "END":
        raise ValueError("stream requires END component")
```

## Listing A13 – Dokument-Ingestion für das RAG-System
**Einfügen:** Anhang A.13, Bezug zu Kapitel 5.2.3 „Dokumentenpipeline und Vektorspeicher“.

Das Beispiel verdeutlicht, wie Dokumente in den hybridisierten Vektorspeicher eingespeist werden und unterstützt die RAG-Beschreibung in Kapitel 5.2.3.

```python
async def ingest_document(parser: DocumentParser, embeddings: EmbeddingClient,
                          store: HybridVectorStore, doc_id: str, raw: bytes) -> None:
    content = parser.extract_text(raw)
    chunks = chunk_document(content)
    vectors = await embeddings.embed_batch(chunks)
    await store.upsert_many(doc_id, list(zip(chunks, vectors)))
```

## Listing A14 – JWT-Ausstellung für das Auth-System
**Einfügen:** Anhang A.14, Bezug zu Kapitel 5.4 „Authentifizierung und Sicherheit“.

Der Code demonstriert, wie im Backend signierte Tokens erzeugt und mit Ablaufdaten versehen werden, wie in Kapitel 5.4 beschrieben.

```python
def issue_access_token(secret: str, user_id: str, roles: list[str], ttl_minutes: int = 30) -> str:
    payload = {
        "sub": user_id,
        "roles": roles,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=ttl_minutes),
    }
    return jwt.encode(payload, secret, algorithm="HS256")
```

## Listing A15 – Pipeline-Metriken für die Evaluation
**Einfügen:** Anhang A.15, Bezug zu Kapitel 6.2 „Evaluierung der Pipeline-Effizienz“.

Die Aggregation fasst Verarbeitungszeiten und Erfolgsquoten zusammen und stützt die in Kapitel 6.2 vorgestellten Kennzahlen.

```python
def aggregate_metrics(results: Iterable[RunResult]) -> dict[str, float]:
    total = list(results)
    durations = [run.duration for run in total]
    success_rate = sum(run.success for run in total) / max(len(total), 1)
    return {
        "avg_duration_ms": statistics.fmean(durations) * 1000 if durations else 0.0,
        "p95_duration_ms": statistics.quantiles(durations, n=20)[18] * 1000 if len(durations) >= 20 else 0.0,
        "success_rate": success_rate,
    }
```

## Listing A16 – Frontend-Workflow zur Dokumentenvorschau
**Einfügen:** Anhang A.16, Bezug zu Kapitel 5.5.2 „Dokumenten- und XML-Visualisierung“.

Das Snippet illustriert die Vorschau-Logik für generierte XML-Dateien und ergänzt den in Kapitel 5.5.2 beschriebenen UI-Workflow.

```typescript
const usePreview = () => {
  const [content, setContent] = useState<string | null>(null)
  const openPreview = async (sessionId: string) => {
    const { data } = await api.get(`/xml-generator/template/preview`, { params: { sessionId } })
    setContent(data.xml_content)
  }
  return { content, openPreview }
}

export function XMLPreviewButton({ sessionId }: { sessionId: string }) {
  const { content, openPreview } = usePreview()
  return (
    <>
      <button onClick={() => openPreview(sessionId)}>Vorschau anzeigen</button>
      {content && <CodeViewer language="xml" value={content} />}
    </>
  )
}
```

## Listing A17 – Docling-Dokumentenaufbereitung
**Einfügen:** Anhang A.17, Bezug zu Kapitel 5.2.3 „Dokumentenpipeline und Vektorspeicher“.

Der Ausschnitt demonstriert, wie Docling-Dateien in ein einheitliches Textformat überführt und mit Metadaten angereichert werden, bevor sie in die RAG-Pipeline eingespeist werden.

```python
async def convert_docling_file(docling_client: DoclingClient, file_path: Path) -> ConvertedDocument:
    raw = file_path.read_bytes()
    result = await docling_client.extract(raw)
    text = "\n".join(section.content for section in result.sections)
    metadata = {
        "source": str(file_path),
        "title": result.meta.get("title"),
        "pages": result.meta.get("page_count"),
    }
    return ConvertedDocument(text=text, metadata=metadata)
```
