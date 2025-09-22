# Streamworks Implementierung Guide

## Übersicht

Dieser Guide erklärt die technische Implementierung des Streamworks-KI Systems und wie neue Features entwickelt werden.

## Architektur-Übersicht

### Backend-Struktur
```
backend/
├── services/               # Service Layer (Business Logic)
├── routers/               # API Endpoints (FastAPI Router)
├── models/                # SQLAlchemy Models
├── schemas/               # Pydantic Schemas
├── templates/             # XML Templates
└── main.py               # FastAPI Application
```

### Service Layer Pattern

Das System verwendet eine modulare Service-Architektur:

```python
# Dependency Injection Container
class ServiceContainer:
    def __init__(self):
        self.xml_stream_service = XMLStreamService()
        self.template_engine = XMLTemplateEngine()
        self.parameter_service = ParameterExtractionService()
```

---

## Stream-Funktionalität

### 1. XMLStream Model

**Datenbankmodell** (`models/core.py`):

```python
class XMLStream(Base):
    __tablename__ = "xml_streams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stream_name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    xml_content = Column(Text)  # Generiertes XML
    wizard_data = Column(JSON)  # Eingabeparameter als JSON
    job_type = Column(String(50), default="standard")
    status = Column(Enum(XMLStreamStatus), default=XMLStreamStatus.DRAFT)

    # Metadaten
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), default="system")

    # Features
    tags = Column(ARRAY(String), default=[])
    is_favorite = Column(Boolean, default=False)
    template_id = Column(String(100))
    version = Column(Integer, default=1)
```

### 2. Stream Service Pattern

**CRUD Operations** (`services/xml_stream_service.py`):

```python
class XMLStreamService:
    @staticmethod
    async def create_stream(db: AsyncSession, stream_data: XMLStreamCreate) -> XMLStream:
        """Stream erstellen mit Validierung"""
        db_stream = XMLStream(
            stream_name=stream_data.stream_name,
            description=stream_data.description,
            wizard_data=stream_data.wizard_data or {},
            xml_content=stream_data.xml_content
        )

        db.add(db_stream)
        await db.commit()
        await db.refresh(db_stream)
        return db_stream

    @staticmethod
    async def list_streams(db: AsyncSession, filters: StreamFilters) -> Tuple[List[XMLStream], int]:
        """Streams mit Filterung und Paginierung"""
        query = select(XMLStream)

        # Filter anwenden
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(or_(
                XMLStream.stream_name.ilike(search_term),
                XMLStream.description.ilike(search_term)
            ))

        # Sortierung und Paginierung
        result = await db.execute(query)
        return result.scalars().all(), total_count
```

### 3. Parameter Schema System

**Stream Type Detection** (`schemas/streamworks_schemas.py`):

```python
class StreamType(Enum):
    STANDARD = "STANDARD"
    SAP = "SAP"
    FILE_TRANSFER = "FILE_TRANSFER"
    CUSTOM = "CUSTOM"

def get_schema_for_type(stream_type: StreamType) -> Dict[str, Any]:
    """Schema für Stream-Typ zurückgeben"""
    schemas = {
        StreamType.SAP: SAP_STREAM_SCHEMA,
        StreamType.FILE_TRANSFER: FILE_TRANSFER_SCHEMA,
        StreamType.STANDARD: STANDARD_STREAM_SCHEMA
    }
    return schemas.get(stream_type, STANDARD_STREAM_SCHEMA)
```

**Parameter Validation**:

```python
def get_missing_parameters(collected: Dict[str, Any], stream_type: StreamType) -> List[str]:
    """Fehlende erforderliche Parameter identifizieren"""
    required = get_required_parameters(stream_type)
    return [param for param in required if param not in collected or not collected[param]]

def generate_prompt_for_parameter(param_name: str, stream_type: StreamType) -> str:
    """Intelligente Prompts für fehlende Parameter"""
    schema = get_schema_for_type(stream_type)
    # Schema durchsuchen und passenden Prompt zurückgeben
    return param_def.get("prompt", f"Bitte geben Sie {param_name} an:")
```

---

## XML Template Engine

### 1. Template System

**Jinja2-basierte Templates** (`templates/xml_templates/`):

```xml
<!-- SAP Job Template -->
<Stream>
    <StreamName>{{ stream_name | default('SAP_STREAM_' + timestamp) }}</StreamName>
    <AgentDetail>{{ agent_detail | default('') }}</AgentDetail>
    <CalendarId>{{ calendar_id | default('UATDefaultCalendar') }}</CalendarId>

    {% if sap_properties %}
    <JobSapProperty>
        <SapSystem>{{ sap_system | default('PA1_100') }}</SapSystem>
        <SapClient>{{ sap_client | default('100') }}</SapClient>
        <SapUser>{{ sap_user | default('SAP_USER') }}</SapUser>
        {% if sap_parameters %}
        <SapParameters>
            {% for param_name, param_value in sap_parameters.items() %}
            <SapParameter>
                <ParameterName>{{ param_name }}</ParameterName>
                <ParameterValue>{{ param_value }}</ParameterValue>
            </SapParameter>
            {% endfor %}
        </SapParameters>
        {% endif %}
    </JobSapProperty>
    {% endif %}
</Stream>
```

### 2. Template Engine Implementation

**Template Processing** (`services/xml_template_engine.py`):

```python
class XMLTemplateEngine:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates/xml_templates'))

    async def generate_xml(self, stream_type: str, parameters: Dict[str, Any]) -> str:
        """XML aus Template und Parametern generieren"""
        template_map = {
            'sap': 'sap_job_template.xml',
            'file_transfer': 'file_transfer_template.xml',
            'standard': 'standard_job_template.xml'
        }

        template_file = template_map.get(stream_type, 'standard_job_template.xml')
        template = self.env.get_template(template_file)

        # Zusätzliche Template-Variablen
        template_vars = {
            **parameters,
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'generated_at': datetime.now().isoformat()
        }

        return template.render(**template_vars)
```

---

## API Implementation

### 1. Router Pattern

**FastAPI Router** (`routers/xml_streams.py`):

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/xml-streams", tags=["XML Streams"])

@router.post("/", response_model=XMLStreamResponse)
async def create_stream(
    stream_data: XMLStreamCreate,
    db: AsyncSession = Depends(get_db)
):
    """Neuen Stream erstellen"""
    try:
        stream = await XMLStreamService.create_stream(db, stream_data)
        return XMLStreamResponse.from_orm(stream)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=XMLStreamListResponse)
async def list_streams(
    search: Optional[str] = None,
    job_types: Optional[List[str]] = Query(None),
    statuses: Optional[List[str]] = Query(None),
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Streams mit Filterung auflisten"""
    filters = StreamFilters(
        search=search,
        job_types=job_types,
        statuses=statuses
    )

    streams, total = await XMLStreamService.list_streams(db, filters, limit=limit, offset=offset)

    return XMLStreamListResponse(
        items=[XMLStreamResponse.from_orm(s) for s in streams],
        total=total,
        limit=limit,
        offset=offset
    )
```

### 2. Pydantic Schemas

**Request/Response Models** (`schemas/xml_streams.py`):

```python
class XMLStreamCreate(BaseModel):
    stream_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    wizard_data: Optional[Dict[str, Any]] = None
    xml_content: Optional[str] = None
    job_type: Optional[str] = "standard"
    status: Optional[str] = "draft"
    created_by: Optional[str] = "system"
    tags: Optional[List[str]] = []
    is_favorite: Optional[bool] = False

class XMLStreamResponse(BaseModel):
    id: UUID
    stream_name: str
    description: Optional[str]
    job_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    is_favorite: bool

    class Config:
        from_attributes = True
```

---

## Frontend Integration

### 1. API Service Layer

**TypeScript API Client** (`frontend/src/services/api.service.ts`):

```typescript
export interface XMLStream {
  id: string;
  stream_name: string;
  description?: string;
  job_type: string;
  status: string;
  wizard_data?: Record<string, any>;
  xml_content?: string;
  created_at: string;
  updated_at: string;
  tags: string[];
  is_favorite: boolean;
}

export class XMLStreamAPI {
  private baseURL = 'http://localhost:8000/xml-streams';

  async createStream(data: Partial<XMLStream>): Promise<XMLStream> {
    const response = await fetch(this.baseURL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }

  async listStreams(filters?: StreamFilters): Promise<{items: XMLStream[], total: number}> {
    const params = new URLSearchParams();
    if (filters?.search) params.append('search', filters.search);
    if (filters?.job_types) filters.job_types.forEach(type => params.append('job_types', type));

    const response = await fetch(`${this.baseURL}?${params}`);
    return response.json();
  }

  async updateStream(id: string, data: Partial<XMLStream>): Promise<XMLStream> {
    const response = await fetch(`${this.baseURL}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }
}
```

### 2. React Query Integration

**Data Fetching Hooks**:

```typescript
export const useXMLStreams = (filters?: StreamFilters) => {
  return useQuery({
    queryKey: ['xml-streams', filters],
    queryFn: () => xmlStreamAPI.listStreams(filters),
    staleTime: 5 * 60 * 1000, // 5 Minuten
  });
};

export const useCreateXMLStream = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: xmlStreamAPI.createStream,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['xml-streams'] });
      toast.success('Stream erfolgreich erstellt!');
    },
    onError: (error) => {
      toast.error(`Fehler: ${error.message}`);
    }
  });
};
```

---

## Testing Strategy

### 1. Backend Tests

**Service Tests** (`tests/test_xml_stream_service.py`):

```python
@pytest.mark.asyncio
async def test_create_stream(test_db, sample_stream_data):
    """Stream-Erstellung testen"""
    stream = await XMLStreamService.create_stream(test_db, sample_stream_data)

    assert stream.stream_name == sample_stream_data.stream_name
    assert stream.status == XMLStreamStatus.DRAFT
    assert stream.id is not None

@pytest.mark.asyncio
async def test_list_streams_with_filters(test_db):
    """Stream-Filterung testen"""
    # Test-Daten erstellen
    await create_test_streams(test_db)

    # Suche testen
    filters = StreamFilters(search="SAP")
    streams, total = await XMLStreamService.list_streams(test_db, filters)

    assert total > 0
    assert all("SAP" in stream.stream_name for stream in streams)
```

### 2. API Tests

**Router Tests**:

```python
def test_create_stream_endpoint(test_client, sample_stream_data):
    """Stream-Erstellung API-Endpoint testen"""
    response = test_client.post("/xml-streams/", json=sample_stream_data.dict())

    assert response.status_code == 200
    data = response.json()
    assert data["stream_name"] == sample_stream_data.stream_name

def test_list_streams_endpoint(test_client):
    """Stream-Auflistung API-Endpoint testen"""
    response = test_client.get("/xml-streams/?search=test&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
```

---

## Deployment & Monitoring

### 1. Database Migrations

**Alembic Migration**:

```python
def upgrade():
    """Add XML streams table"""
    op.create_table(
        'xml_streams',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('stream_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('xml_content', sa.Text()),
        sa.Column('wizard_data', sa.JSON()),
        sa.Column('job_type', sa.String(50)),
        sa.Column('status', sa.Enum(XMLStreamStatus)),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.Column('tags', sa.ARRAY(sa.String())),
        sa.Column('is_favorite', sa.Boolean()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stream_name')
    )
```

### 2. Performance Monitoring

**Logging & Metrics**:

```python
import logging
from services.performance_monitor import track_performance

logger = logging.getLogger(__name__)

@track_performance("xml_stream_creation")
async def create_stream(db: AsyncSession, stream_data: XMLStreamCreate):
    """Performance-überwachte Stream-Erstellung"""
    logger.info(f"Creating stream: {stream_data.stream_name}")

    try:
        result = await XMLStreamService.create_stream(db, stream_data)
        logger.info(f"✅ Created stream: {result.id}")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to create stream: {str(e)}")
        raise
```

---

## Best Practices

### 1. Code Organization

- **Service Layer**: Business Logic von API-Endpoints trennen
- **Dependency Injection**: Services über Container verwalten
- **Schema Validation**: Pydantic für Input/Output Validation
- **Error Handling**: Strukturierte Exceptions und Logging

### 2. Performance

- **Async/Await**: Für alle I/O-Operationen verwenden
- **Database Indexes**: Auf häufig abgefragte Felder
- **Caching**: Für Template-Rendering und Parameter-Schemas
- **Pagination**: Für große Datenmengen

### 3. Security

- **Input Validation**: Alle Benutzereingaben validieren
- **SQL Injection**: SQLAlchemy ORM verwenden
- **Authentication**: JWT-basierte Authentifizierung
- **Authorization**: Role-based Access Control