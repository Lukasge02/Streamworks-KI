"""
Batch Parameter Extractor for Enterprise Document Processing

Extracts parameters from multiple sources:
- Excel/CSV: Structured table extraction with header mapping
- PDF/DOCX: NLP-based extraction using AI
- Hybrid: Combines both approaches

Features:
- Per-parameter confidence scoring
- Source grounding (where each value came from)
- Multi-stream extraction
- Intelligent job type detection
"""

from typing import Dict, Any, Optional, List, Literal
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import traceback

from openai import OpenAI
import instructor

from config import config
from .schemas import StreamworksParams


@dataclass
class SourceLocation:
    """Describes where a parameter value was extracted from"""
    source_type: Literal["cell", "text", "inferred"]  # cell for Excel, text for NLP
    location: str  # e.g., "Row 3, Column B" or "Paragraph 2, Character 45-67"
    original_text: Optional[str] = None  # The original text snippet
    confidence: float = 0.8


@dataclass
class ParameterWithConfidence:
    """A parameter value with its confidence and source"""
    value: Any
    confidence: float
    source: Optional[SourceLocation] = None
    is_explicit: bool = True  # True if explicitly stated, False if inferred


@dataclass 
class ExtractedStream:
    """A complete stream extracted from document"""
    stream_name: Optional[str]
    job_type: Literal["STANDARD", "FILE_TRANSFER", "SAP"]
    parameters: Dict[str, ParameterWithConfidence]
    missing_required: List[str] = field(default_factory=list)
    row_number: Optional[int] = None  # For Excel extraction
    overall_confidence: float = 0.8
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "stream_name": self.stream_name,
            "job_type": self.job_type,
            "parameters": {
                k: {
                    "value": v.value,
                    "confidence": v.confidence,
                    "source": {
                        "type": v.source.source_type,
                        "location": v.source.location,
                        "original_text": v.source.original_text,
                    } if v.source else None,
                    "is_explicit": v.is_explicit,
                }
                for k, v in self.parameters.items()
            },
            "missing_required": self.missing_required,
            "row_number": self.row_number,
            "overall_confidence": self.overall_confidence,
            "warnings": self.warnings,
        }


@dataclass
class DocumentExtractionResult:
    """Complete result of extracting parameters from a document"""
    streams: List[ExtractedStream]
    document_summary: str
    extraction_method: Literal["tabular", "nlp", "hybrid"]
    total_streams: int
    successful_extractions: int
    file_type: str
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "streams": [s.to_dict() for s in self.streams],
            "document_summary": self.document_summary,
            "extraction_method": self.extraction_method,
            "total_streams": self.total_streams,
            "successful_extractions": self.successful_extractions,
            "file_type": self.file_type,
            "warnings": self.warnings,
        }


# Pydantic model for structured NLP extraction
class DocumentStreamExtraction(BaseModel):
    """AI-extracted streams from document text"""
    
    streams: List[StreamworksParams] = Field(
        description="Liste aller erkannten Stream-Konfigurationen im Dokument"
    )
    
    document_summary: str = Field(
        description="Kurze Zusammenfassung des Dokuments (1-2 Sätze)"
    )
    
    extraction_notes: Optional[str] = Field(
        default=None,
        description="Hinweise zur Extraktion, z.B. unsichere Werte oder fehlende Informationen"
    )


DOCUMENT_EXTRACTION_PROMPT = """Du bist ein Experte für Streamworks Job-Automatisierung.
Extrahiere ALLE Stream-Konfigurationen aus dem folgenden Dokument.

## REGELN

1. Jeder beschriebene Stream/Job/Transfer wird als separates Element in 'streams' zurückgegeben
2. Erkenne den Job-Typ automatisch:
   - FILE_TRANSFER: Wenn Dateien kopiert/übertragen werden
   - SAP: Wenn SAP-Systeme, Reports, Transaktionen erwähnt werden  
   - STANDARD: Für Scripts, Befehle, allgemeine Jobs

3. Extrahiere so viele Parameter wie möglich:
   - stream_name: Name des Streams (generiere einen passenden wenn nicht genannt)
   - source_agent, target_agent: Server für Dateitransfers
   - source_file_pattern, target_file_path: Dateipfade
   - agent_detail: Ausführungsserver für Standard-Jobs
   - main_script: Auszuführendes Script/Befehl
   - schedule, start_time: Zeitplanung
   - sap_system, sap_report, sap_client: SAP-Parameter

4. Setze confidence basierend auf Explizitheit:
   - 0.9-1.0: Explizit im Text genannt
   - 0.7-0.9: Aus Kontext ableitbar
   - 0.5-0.7: Annahme/Interpretation

5. Generiere eine kurze document_summary

## FEW-SHOT BEISPIELE

Dokument: "Wir brauchen einen täglichen Backup-Job um 23:00 auf Server BACKUP01. Das Script backup_all.sh soll /data sichern."
→ 1 Stream: STANDARD, stream_name: "BACKUP_DAILY", agent_detail: "BACKUP01", main_script: "backup_all.sh", schedule: "täglich", start_time: "23:00"

Dokument: "Dateitransfer von PROD_SERVER nach ARCHIVE_SERVER: Alle CSV-Dateien aus /export/ nach /archive/daily/"  
→ 1 Stream: FILE_TRANSFER, stream_name: "FT_PROD_ARCHIVE", source_agent: "PROD_SERVER", target_agent: "ARCHIVE_SERVER", source_file_pattern: "/export/*.csv", target_file_path: "/archive/daily/"

Dokument: "SAP Report ZEXPORT_MONTHLY auf System PA1, Mandant 100, jeden 1. des Monats"
→ 1 Stream: SAP, stream_name: "SAP_ZEXPORT_MONTHLY", sap_system: "PA1", sap_report: "ZEXPORT_MONTHLY", sap_client: "100", schedule: "monatlich"
"""


class BatchParameterExtractor:
    """
    Enterprise-Grade Parameter Extraction from Documents
    
    Supports:
    - Excel/CSV: Direct table extraction with header mapping
    - PDF/DOCX: AI-powered NLP extraction
    - Hybrid: Best of both approaches
    """
    
    def __init__(self):
        self._excel_parser = None
        self._pdf_parser = None
        self._client = None
    
    @property
    def excel_parser(self):
        """Lazy load Excel parser"""
        if self._excel_parser is None:
            from services.rag.parsers.excel_parser import ExcelParser
            self._excel_parser = ExcelParser()
        return self._excel_parser
    
    @property
    def pdf_parser(self):
        """Lazy load PDF parser"""
        if self._pdf_parser is None:
            from services.rag.parsers.pymupdf_parser import PyMuPdfParser
            self._pdf_parser = PyMuPdfParser()
        return self._pdf_parser
    
    @property
    def ai_client(self):
        """Lazy load AI client with instructor"""
        if self._client is None:
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY nicht konfiguriert!")
            self._client = instructor.from_openai(OpenAI(api_key=config.OPENAI_API_KEY))
        return self._client
    
    def extract_from_document(
        self,
        file_content: bytes,
        filename: str,
    ) -> DocumentExtractionResult:
        """
        Main extraction method - automatically selects best approach
        
        Args:
            file_content: Raw file bytes
            filename: Original filename with extension
            
        Returns:
            DocumentExtractionResult with all extracted streams
        """
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        
        try:
            if ext in ("xlsx", "xls", "csv"):
                return self._extract_from_spreadsheet(file_content, filename)
            elif ext == "pdf":
                return self._extract_from_pdf(file_content, filename)
            elif ext in ("docx", "doc", "txt", "md"):
                return self._extract_from_text(file_content, filename)
            else:
                return DocumentExtractionResult(
                    streams=[],
                    document_summary=f"Unsupported file type: {ext}",
                    extraction_method="tabular",
                    total_streams=0,
                    successful_extractions=0,
                    file_type=ext,
                    warnings=[f"Dateityp '.{ext}' wird nicht unterstützt"],
                )
        except Exception as e:
            traceback.print_exc()
            return DocumentExtractionResult(
                streams=[],
                document_summary=f"Extraction error: {str(e)}",
                extraction_method="tabular",
                total_streams=0,
                successful_extractions=0,
                file_type=ext,
                warnings=[f"Fehler bei der Extraktion: {str(e)}"],
            )
    
    def _extract_from_spreadsheet(
        self,
        content: bytes,
        filename: str,
    ) -> DocumentExtractionResult:
        """Extract parameters from Excel/CSV"""
        result = self.excel_parser.parse_for_parameters(content, filename)
        
        streams = []
        for row in result.rows:
            # Determine job type from parameters
            job_type = self._detect_job_type(row.mapped_params)
            
            # Convert to ParameterWithConfidence
            params_with_conf = {}
            for key, value in row.mapped_params.items():
                params_with_conf[key] = ParameterWithConfidence(
                    value=value,
                    confidence=0.95,  # High confidence for explicit table data
                    source=SourceLocation(
                        source_type="cell",
                        location=f"Zeile {row.row_number}",
                        original_text=value,
                        confidence=0.95,
                    ),
                    is_explicit=True,
                )
            
            # Check missing required params
            missing = self._get_missing_required(job_type, row.mapped_params)
            
            streams.append(ExtractedStream(
                stream_name=row.mapped_params.get("stream_name"),
                job_type=job_type,
                parameters=params_with_conf,
                missing_required=missing,
                row_number=row.row_number,
                overall_confidence=row.confidence,
                warnings=[f"Fehlend: {m}" for m in missing] if missing else [],
            ))
        
        ext = filename.split(".")[-1].lower()
        summary = f"{len(streams)} Stream(s) aus {ext.upper()}-Datei extrahiert"
        if result.unmapped_columns:
            summary += f". Nicht erkannte Spalten: {', '.join(result.unmapped_columns[:3])}"
        
        return DocumentExtractionResult(
            streams=streams,
            document_summary=summary,
            extraction_method="tabular",
            total_streams=len(streams),
            successful_extractions=len([s for s in streams if not s.missing_required]),
            file_type=ext,
            warnings=[f"Spalte '{c}' nicht erkannt" for c in result.unmapped_columns],
        )
    
    def _extract_from_pdf(
        self,
        content: bytes,
        filename: str,
    ) -> DocumentExtractionResult:
        """Extract parameters from PDF using NLP"""
        # Parse PDF to text
        parsed = self.pdf_parser.parse(content, filename)
        
        # Use AI to extract streams
        return self._extract_with_ai(parsed.content, filename, "pdf")
    
    def _extract_from_text(
        self,
        content: bytes,
        filename: str,
    ) -> DocumentExtractionResult:
        """Extract parameters from text documents using NLP"""
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            text = content.decode("latin-1")
        
        ext = filename.split(".")[-1].lower()
        return self._extract_with_ai(text, filename, ext)
    
    def _extract_with_ai(
        self,
        text: str,
        filename: str,
        file_type: str,
    ) -> DocumentExtractionResult:
        """Use AI to extract stream parameters from text"""
        # Truncate very long documents
        max_chars = 12000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[... Text gekürzt ...]"
        
        try:
            result = self.ai_client.chat.completions.create(
                model=config.LLM_MODEL,
                response_model=DocumentStreamExtraction,
                messages=[
                    {"role": "system", "content": DOCUMENT_EXTRACTION_PROMPT},
                    {"role": "user", "content": f"Dokument: {filename}\n\n{text}"},
                ],
                temperature=0.1,
            )
            
            # Convert to ExtractedStream objects
            streams = []
            for idx, params in enumerate(result.streams):
                params_with_conf = {}
                
                # Convert each parameter
                for field_name, value in params.model_dump().items():
                    if value is not None and field_name not in ["missing_required", "follow_up_question", "confidence", "job_type"]:
                        params_with_conf[field_name] = ParameterWithConfidence(
                            value=value,
                            confidence=params.confidence * 0.9,  # Slightly lower for NLP
                            source=SourceLocation(
                                source_type="text",
                                location=f"Dokument {filename}",
                                confidence=params.confidence,
                            ),
                            is_explicit=params.confidence > 0.8,
                        )
                
                missing = self._get_missing_required(params.job_type, params.model_dump())
                
                streams.append(ExtractedStream(
                    stream_name=params.stream_name,
                    job_type=params.job_type,
                    parameters=params_with_conf,
                    missing_required=missing,
                    overall_confidence=params.confidence,
                    warnings=[f"Fehlend: {m}" for m in missing] if missing else [],
                ))
            
            return DocumentExtractionResult(
                streams=streams,
                document_summary=result.document_summary,
                extraction_method="nlp",
                total_streams=len(streams),
                successful_extractions=len([s for s in streams if not s.missing_required]),
                file_type=file_type,
                warnings=[result.extraction_notes] if result.extraction_notes else [],
            )
            
        except Exception as e:
            traceback.print_exc()
            return DocumentExtractionResult(
                streams=[],
                document_summary=f"AI extraction failed: {str(e)}",
                extraction_method="nlp",
                total_streams=0,
                successful_extractions=0,
                file_type=file_type,
                warnings=[f"KI-Extraktion fehlgeschlagen: {str(e)}"],
            )
    
    def _detect_job_type(self, params: Dict[str, str]) -> Literal["STANDARD", "FILE_TRANSFER", "SAP"]:
        """Detect job type from extracted parameters"""
        # Check for FILE_TRANSFER indicators
        if params.get("source_agent") or params.get("target_agent"):
            return "FILE_TRANSFER"
        if params.get("source_file_pattern") or params.get("target_file_path"):
            return "FILE_TRANSFER"
        
        # Check for SAP indicators
        if params.get("sap_system") or params.get("sap_report"):
            return "SAP"
        
        # Check job_type field if present
        job_type = params.get("job_type", "").upper()
        if "FILE" in job_type or "TRANSFER" in job_type:
            return "FILE_TRANSFER"
        if "SAP" in job_type:
            return "SAP"
        
        return "STANDARD"
    
    def _get_missing_required(
        self,
        job_type: str,
        params: Dict[str, Any],
    ) -> List[str]:
        """Determine missing required parameters"""
        missing = []
        
        # Stream name always required
        if not params.get("stream_name"):
            missing.append("stream_name")
        
        if job_type == "FILE_TRANSFER":
            if not params.get("source_agent"):
                missing.append("source_agent")
            if not params.get("target_agent"):
                missing.append("target_agent")
        
        elif job_type == "STANDARD":
            if not params.get("agent_detail"):
                missing.append("agent_detail")
            if not params.get("main_script") and not params.get("short_description"):
                missing.append("main_script")
        
        elif job_type == "SAP":
            if not params.get("sap_system"):
                missing.append("sap_system")
        
        return missing


# Singleton instance
_batch_extractor: Optional[BatchParameterExtractor] = None


def get_batch_extractor() -> BatchParameterExtractor:
    """Get or create batch extractor instance"""
    global _batch_extractor
    if _batch_extractor is None:
        _batch_extractor = BatchParameterExtractor()
    return _batch_extractor
