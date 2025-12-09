# Appendix Listings B – Ergänzende Codebeispiele

## Listing B-8 – Initialisierung des API-Gateways mit Dependency Injection (FastAPI)
**Einfügen:** Anhang B.8, Bezug zu Kapitel 5.2.3 „API-Gateway und Dependency Injection“.

```python
app = FastAPI(title="Streamworks-KI API", version="0.14.0")

container = DIContainer()
container.register_singleton(DatabaseService, DatabaseService)
container.register_singleton(LangExtractService, LangExtractService)

app.include_router(langextract_router, prefix="/api/langextract")
app.include_router(xml_router, prefix="/api/xml")


@app.on_event("startup")
async def startup() -> None:
    await container.get(DatabaseService).connect()


def get_langextract_service() -> LangExtractService:
    return container.get_sync(LangExtractService)
```

## Listing B-9 – React-Komponente zur Stream-Erstellung mit Typisierung (TypeScript)
**Einfügen:** Anhang B.9, Bezug zu Kapitel 5.3.2 „Architekturprinzipien und Struktur“.

```typescript
type StreamFormProps = {
  initialName?: string
  onSubmit: (payload: { name: string; schedule: string }) => void
}

export function StreamForm({ initialName = '', onSubmit }: StreamFormProps) {
  const [name, setName] = useState(initialName)
  const [schedule, setSchedule] = useState('00:00')

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    onSubmit({ name, schedule })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Stream-Name" />
      <input value={schedule} onChange={(event) => setSchedule(event.target.value)} placeholder="Zeitplan" />
      <button type="submit">Stream speichern</button>
    </form>
  )
}
```

## Listing B-10 – Iterative Validierung und Fehler-Feedback im LangExtractService
**Einfügen:** Anhang B.10, Bezug zu Kapitel 5.4.1.4 „Iterative Vervollständigung“.

```python
async def complete_parameters(service: LangExtractService, session_id: str) -> None:
    state = await service.store.load(session_id)
    missing = service.mandatory_parameters(state.job_type)

    while missing:
        prompt = service.build_clarification_prompt(missing)
        answer = await service.llm.ask(prompt)
        updates = await service.extractor.collect(answer, state.job_type, state.parameters)
        state.parameters.update(updates.parameters)
        missing = [key for key in missing if not state.parameters.get(key)]

    await service.store.save(state)
```

## Listing B-11 – Validierungs-Orchestrierung mit Pydantic und XSD (lxml)
**Einfügen:** Anhang B.11, Bezug zu Kapitel 5.5.1.3 „Validierungsstufen“.

```python
class TemplateInput(BaseModel):
    job_type: Literal["STANDARD", "FILE_TRANSFER", "SAP"]
    parameters: dict[str, str]


def run_validation(payload: TemplateInput, xsd: XMLSchema) -> ValidationResult:
    xml = render_template(payload.job_type, payload.parameters)
    document = etree.fromstring(xml.encode("utf-8"))
    xsd.assertValid(document)
    security_check(document)
    business_rules(document)
    return ValidationResult(xml=xml, status="valid")
```

## Listing B-12 – Automatisierte Test-Suite zur XML-Evaluierung (Pytest-Runner)
**Einfügen:** Anhang B.12, Bezug zu Kapitel 6.2 „Evaluierung der XML-Generierung“.

```python
@pytest.mark.parametrize("fixture_name", sorted(Path("tests/xml_cases").glob("*.json")))
def test_xml_case(fixture_name: Path) -> None:
    data = json.loads(fixture_name.read_text())
    payload = TemplateInput(**data["input"])
    result = run_validation(payload, XML_SCHEMA)
    assert result.status == data["expected_status"], fixture_name.name
```

## Listing B-13 – Hybrid-Retrieval mit Reciprocal Rank Fusion (RRF)
**Einfügen:** Anhang B.13, Bezug zu Kapitel 6.3 „Evaluierung des RAG-Systems“.

```python
async def hybrid_retrieve(query: str, vector: VectorRetriever, keyword: KeywordRetriever) -> list[DocumentChunk]:
    dense = await vector.retrieve(query, limit=10)
    sparse = await keyword.retrieve(query, limit=10)
    combined = defaultdict(float)

    for rank, chunk in enumerate(dense, start=1):
        combined[chunk] += 1 / (60 + rank)

    for rank, chunk in enumerate(sparse, start=1):
        combined[chunk] += 1 / (60 + rank)

    return [chunk for chunk, _ in sorted(combined.items(), key=lambda item: item[1], reverse=True)[:5]]
```
