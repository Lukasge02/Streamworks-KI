# 🚀 LangExtract Integration Plan - Streamworks-KI Revolution

## **🎯 Vision: Source-Grounded Parameter Extraction**

**Ziel:** Kompletter Ersatz des aktuellen Parameter-Extraktors durch LangExtract mit **Source Grounding** für maximale Transparenz und User-Vertrauen.

---

## **📋 Stream-Typen Analyse**

### **1. FILE_TRANSFER**
- **Keywords:** datentransfer, übertragung, transfer, dateien, agent, server
- **Core Parameter:** SourceServer, TargetServer, FilePattern, TransferMode
- **Komplexität:** Medium (5-15 Min)

### **2. SAP**
- **Keywords:** sap, export, import, kalender, personal
- **Core Parameter:** SAPSystem, TableName, ExportFormat, FilterCriteria
- **Komplexität:** High (10-20 Min)

### **3. STANDARD**
- **Keywords:** standard, prozess, job, verarbeitung
- **Core Parameter:** ProcessType, InputFormat, OutputFormat, Schedule
- **Komplexität:** Low (3-10 Min)

---

## **🏗️ Technische Implementierung**

### **Phase 1: LangExtract Service (Tag 1-2)**

```python
# services/ai/langextract_parameter_service.py
class LangExtractParameterService:
    """
    Ersetzt UnifiedParameterExtractor komplett
    Nutzt LangExtract für Source-Grounded Parameter Extraction
    """

    def __init__(self, openai_api_key: str):
        self.llm_model = "gpt-4o"  # Euer bestehender Stack
        self.schema_loader = StreamSchemaLoader()
        self.examples_manager = FewShotExamplesManager()

    async def extract_parameters_with_grounding(
        self,
        user_message: str,
        job_type: Optional[str] = None
    ) -> SourceGroundedExtractionResult:

        # 1. Job-Type Detection (falls nicht bekannt)
        if not job_type:
            job_type = await self._detect_job_type_langextract(user_message)

        # 2. Schema für Job-Type laden
        schema = self._get_job_schema(job_type)
        examples = self._get_few_shot_examples(job_type)

        # 3. LangExtract Magic ✨
        result = await lx.extract(
            text=user_message,
            prompt_description=self._build_extraction_prompt(job_type),
            examples=examples,
            model_id=self.llm_model,
            fence_output=True,
            use_schema_constraints=False,
            enable_source_grounding=True  # 🎯 Das ist der Game Changer!
        )

        # 4. In euer Format konvertieren
        return self._convert_to_streamworks_format(result, job_type)

    def _build_extraction_prompt(self, job_type: str) -> str:
        """Job-Type spezifische Prompts"""
        prompts = {
            "FILE_TRANSFER": "Extract file transfer parameters including source/target servers, file patterns, and transfer settings from the user message.",
            "SAP": "Extract SAP-related parameters including system names, table names, export formats, and filter criteria from the user message.",
            "STANDARD": "Extract standard process parameters including process type, input/output formats, and scheduling information from the user message."
        }
        return prompts.get(job_type, "Extract stream configuration parameters from the user message.")
```

### **Phase 2: Enhanced Models (Tag 2-3)**

```python
# models/source_grounded_models.py
class SourceGroundedParameter(BaseModel):
    """Enhanced Parameter mit Source Grounding"""
    name: str
    value: Any
    confidence: float

    # 🆕 Source Grounding Features
    source_text: str                    # Original text chunk
    character_offsets: Tuple[int, int]  # [start, end] positions
    extraction_confidence: float        # LangExtract confidence

    # UI Enhancement Data
    highlight_color: str = "blue"       # CSS color for highlighting
    tooltip_info: str = ""              # Additional context

class SourceGroundedExtractionResult(BaseModel):
    """LangExtract Result mit allen Features"""
    detected_job_type: str
    job_type_confidence: float

    # Grounded Parameters
    stream_parameters: List[SourceGroundedParameter]
    job_parameters: List[SourceGroundedParameter]

    # Source Mapping
    full_text: str                      # Original user message
    highlighted_ranges: List[Tuple[int, int, str]]  # All highlights

    # Status
    completion_percentage: float
    next_required_parameter: Optional[str]
    suggested_questions: List[str]
```

### **Phase 3: Frontend Source Highlighting (Tag 3-5)**

```tsx
// components/xml-chat-v2/source-grounding/SourceHighlightedMessage.tsx
interface SourceHighlightedMessageProps {
  message: string
  parameters: SourceGroundedParameter[]
  onParameterClick: (param: SourceGroundedParameter) => void
}

const SourceHighlightedMessage: React.FC<SourceHighlightedMessageProps> = ({
  message,
  parameters,
  onParameterClick
}) => {
  const renderHighlightedText = () => {
    let highlightedText = message
    let offset = 0

    // Sort by character position
    const sortedParams = [...parameters].sort((a, b) => a.character_offsets[0] - b.character_offsets[0])

    return sortedParams.map((param, index) => {
      const [start, end] = param.character_offsets
      const beforeText = message.slice(offset, start)
      const highlightedText = message.slice(start, end)
      offset = end

      return (
        <span key={index}>
          {beforeText}
          <HighlightedSpan
            text={highlightedText}
            parameter={param}
            onClick={() => onParameterClick(param)}
          />
        </span>
      )
    })
  }

  return (
    <div className="relative">
      <div className="text-gray-800 leading-relaxed">
        {renderHighlightedText()}
        {/* Rest of message after last highlight */}
        {message.slice(parameters[parameters.length - 1]?.character_offsets[1] || 0)}
      </div>
    </div>
  )
}

// Einzelner Highlight-Span
const HighlightedSpan: React.FC<{
  text: string
  parameter: SourceGroundedParameter
  onClick: () => void
}> = ({ text, parameter, onClick }) => {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'bg-green-100 border-green-400 text-green-800'
    if (confidence >= 0.7) return 'bg-blue-100 border-blue-400 text-blue-800'
    if (confidence >= 0.5) return 'bg-yellow-100 border-yellow-400 text-yellow-800'
    return 'bg-red-100 border-red-400 text-red-800'
  }

  return (
    <Tooltip content={
      <div className="p-2">
        <div className="font-semibold">{parameter.name}</div>
        <div className="text-sm text-gray-600">{parameter.value}</div>
        <div className="text-xs mt-1">
          Confidence: {(parameter.confidence * 100).toFixed(1)}%
        </div>
      </div>
    }>
      <span
        onClick={onClick}
        className={`
          px-1 py-0.5 rounded cursor-pointer border-2
          transition-all duration-200 hover:scale-105 hover:shadow-md
          ${getConfidenceColor(parameter.confidence)}
        `}
      >
        {text}
      </span>
    </Tooltip>
  )
}
```

### **Phase 4: Chat Integration (Tag 4-5)**

```tsx
// components/xml-chat-v2/enhanced/EnhancedChatMessage.tsx
const EnhancedChatMessage: React.FC<{
  message: XMLChatMessage
  sourceGroundedData?: SourceGroundedExtractionResult
}> = ({ message, sourceGroundedData }) => {

  const handleParameterClick = (param: SourceGroundedParameter) => {
    // Show parameter details modal
    setSelectedParameter(param)
    setShowParameterModal(true)
  }

  const handleParameterCorrection = (param: SourceGroundedParameter, newValue: any) => {
    // User correction workflow
    updateParameterValue(param.name, newValue)
    toast.success(`Parameter ${param.name} wurde korrigiert`)
  }

  return (
    <div className="space-y-4">
      {/* Original Message mit Source Highlighting */}
      {message.role === 'user' && sourceGroundedData && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="text-sm text-blue-600 mb-2 font-medium">
            📍 Erkannte Parameter:
          </div>
          <SourceHighlightedMessage
            message={message.content}
            parameters={[
              ...sourceGroundedData.stream_parameters,
              ...sourceGroundedData.job_parameters
            ]}
            onParameterClick={handleParameterClick}
          />
        </div>
      )}

      {/* Standard Message Rendering */}
      <div className={`flex items-start gap-4 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
        <ChatMessageContent message={message} />
      </div>

      {/* Parameter Summary Card */}
      {sourceGroundedData && (
        <ParameterSummaryCard
          extractionResult={sourceGroundedData}
          onParameterEdit={handleParameterCorrection}
        />
      )}
    </div>
  )
}
```

### **Phase 5: Backend Router Integration (Tag 5-6)**

```python
# routers/chat_xml.py - Enhanced für LangExtract
@router.post("/smart-chat")
async def enhanced_smart_chat(
    request: SmartChatRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        # 🆕 LangExtract Service nutzen
        langextract_service = get_langextract_parameter_service()

        # Parameter mit Source Grounding extrahieren
        extraction_result = await langextract_service.extract_parameters_with_grounding(
            user_message=request.message,
            job_type=request.job_type
        )

        # Dialog Manager mit Source-Grounded Data
        dialog_manager = get_intelligent_dialog_manager()
        response = await dialog_manager.process_message_with_grounding(
            session_id=request.session_id,
            user_message=request.message,
            extraction_result=extraction_result
        )

        return SmartChatResponse(
            session_id=response.session_id,
            response_message=response.message,
            extracted_parameters=response.parameters,

            # 🆕 Source Grounding Data für Frontend
            source_grounding_data={
                "highlighted_ranges": extraction_result.highlighted_ranges,
                "parameter_sources": [
                    {
                        "name": p.name,
                        "source_text": p.source_text,
                        "character_offsets": p.character_offsets,
                        "confidence": p.confidence
                    }
                    for p in extraction_result.stream_parameters + extraction_result.job_parameters
                ]
            },

            metadata=ChatResponseMetadata(
                job_type=extraction_result.detected_job_type,
                confidence=extraction_result.job_type_confidence,
                extraction_method="langextract"  # 🏷️ Tracking
            )
        )

    except Exception as e:
        logger.error(f"Enhanced smart chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## **🎨 UX/UI Innovations**

### **1. Real-Time Parameter Discovery**
- **Während User tippt:** Live highlighting von erkannten Parametern
- **Confidence Colors:** Grün=Hoch, Blau=Mittel, Gelb=Niedrig, Rot=Sehr niedrig
- **Interactive Tooltips:** Click auf Highlight zeigt Parameter-Details

### **2. Source Traceability Dashboard**
```tsx
// Neues Feature: Parameter Provenance View
const ParameterProvenanceView = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">📍 Parameter-Herkunft</h3>

      {parameters.map(param => (
        <div key={param.name} className="border-l-4 border-blue-400 pl-4 mb-4">
          <div className="font-medium">{param.name}: {param.value}</div>
          <div className="text-sm text-gray-600 italic">
            "'{param.source_text}"
            <span className="text-gray-400">
              (Zeichen {param.character_offsets[0]}-{param.character_offsets[1]})
            </span>
          </div>
          <div className="text-xs text-blue-600">
            Confidence: {(param.confidence * 100).toFixed(1)}%
          </div>
        </div>
      ))}
    </div>
  )
}
```

### **3. Parameter Correction Flow**
- **One-Click Editing:** Click auf Parameter → Inline-Editor
- **Suggestion Engine:** AI schlägt alternative Werte vor
- **Undo/Redo:** Parameter-Änderungen rückgängig machen

---

## **📊 Qualitätssicherung & Testing**

### **Testing Strategy (Tag 6-7)**

```python
# tests/test_langextract_integration.py
class TestLangExtractIntegration:

    @pytest.mark.asyncio
    async def test_file_transfer_extraction(self):
        """Test FILE_TRANSFER parameter extraction"""
        user_input = "Ich brauche einen Datentransfer von Server001 nach Server002 für alle *.csv Dateien"

        result = await langextract_service.extract_parameters_with_grounding(
            user_message=user_input,
            job_type="FILE_TRANSFER"
        )

        # Verify extracted parameters
        assert result.detected_job_type == "FILE_TRANSFER"
        assert any(p.name == "SourceServer" and p.value == "Server001" for p in result.stream_parameters)
        assert any(p.name == "TargetServer" and p.value == "Server002" for p in result.stream_parameters)
        assert any(p.name == "FilePattern" and p.value == "*.csv" for p in result.job_parameters)

        # Verify source grounding
        source_server_param = next(p for p in result.stream_parameters if p.name == "SourceServer")
        assert source_server_param.source_text == "Server001"
        assert source_server_param.character_offsets[0] > 0  # Has valid position

    @pytest.mark.asyncio
    async def test_sap_extraction(self):
        """Test SAP parameter extraction"""
        user_input = "SAP Kalender Export von System ZTV Tabelle PA1 als Excel Format"

        result = await langextract_service.extract_parameters_with_grounding(
            user_message=user_input,
            job_type="SAP"
        )

        assert result.detected_job_type == "SAP"
        assert any(p.name == "SAPSystem" and p.value == "ZTV" for p in result.stream_parameters)
        assert any(p.name == "TableName" and p.value == "PA1" for p in result.job_parameters)
        assert any(p.name == "ExportFormat" and p.value == "Excel" for p in result.job_parameters)
```

### **Performance Benchmarks**
- **Target Latency:** <3 Sekunden für Parameter-Extraktion
- **Target Accuracy:** >90% Parameter-Erkennungsrate
- **Target Confidence:** >85% durchschnittliche Confidence

---

## **🚀 Rollout-Strategie**

### **Week 1: Core Implementation**
- **Tag 1-2:** LangExtract Service + Enhanced Models
- **Tag 3-4:** Frontend Source Highlighting Components
- **Tag 5:** Backend Router Integration
- **Tag 6-7:** Testing & Bugfixes

### **Week 2: UI Polish & Launch**
- **Tag 8-9:** Parameter Correction Flow
- **Tag 10:** Real-time highlighting während typing
- **Tag 11-12:** UX Testing & Refinements
- **Tag 13-14:** Documentation & Launch Prep

### **Success Metrics**
- **Parameter Accuracy:** +20% vs. current system
- **User Confidence:** >95% "verstehe warum Parameter extrahiert wurden"
- **Time to XML:** -40% through better parameter collection
- **User Satisfaction:** >4.5/5 stars for new experience

---

## **💰 Cost-Benefit Analysis**

### **Costs:**
- **Development:** 14 Tage (2 Wochen intensiv)
- **OpenAI API:** Keine zusätzlichen Kosten (gleiche Models)
- **Testing:** 3 Tage
- **Total:** ~17 Tage

### **Benefits:**
- **Revolutionary UX:** Source Grounding = Game Changer für Enterprise AI
- **Trust & Transparency:** User sehen exakt woher Parameter kommen
- **Accuracy Boost:** LangExtract ist optimiert für structured extraction
- **Competitive Advantage:** Einzigartiges Feature im RAG/AI Bereich
- **User Adoption:** Erwartung +50% durch bessere UX

**ROI:** 400-600% binnen 6 Monaten durch höhere Accuracy + User-Trust

---

## **🎯 Nächste Schritte**

1. **LangExtract Installation:** `pip install langextract[openai]`
2. **Core Service Implementation:** Start mit `LangExtractParameterService`
3. **Few-Shot Examples:** Konvertierung der `unified_stream_schemas.json`
4. **Frontend Components:** Source Highlighting System
5. **Integration Testing:** Mit echten Stream-Konfigurationen

**Let's revolutionize parameter extraction! 🚀✨**