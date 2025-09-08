"""
XML RAG Service for StreamWorks XML Generation
Provides RAG-based XML template search and generation using ChromaDB and Ollama
"""
import logging
import json
import time
import os
import xml.etree.ElementTree as ET
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path
import glob
import asyncio
import aiofiles
from datetime import datetime

# ChromaDB and embeddings
import chromadb
from chromadb.config import Settings
import numpy as np

# Ollama for LLM generation
import ollama

from schemas.xml_generation import (
    XMLTemplate, TemplateMatch, TemplateSearchQuery,
    WizardFormData, XMLGenerationResult, JobType,
    ValidationResult, ValidationSeverity, ValidationError
)
from services.xml_validator import get_validator

logger = logging.getLogger(__name__)


class XMLTemplateRAG:
    """RAG service for XML template management and generation"""
    
    def __init__(self, 
                 chroma_path: str = "storage/chroma_xml_templates",
                 embedding_model: str = "embeddinggemma",
                 ollama_model: str = "llama3:8b"):
        self.chroma_path = chroma_path
        self.embedding_model_name = embedding_model
        self.ollama_model = ollama_model
        self.collection_name = "streamworks_xml_templates"
        
        # Initialize components
        self.chroma_client = None
        self.collection = None
        self.validator = get_validator()
        
        # Template cache
        self.template_cache: Dict[str, XMLTemplate] = {}
        
        self._initialize()
    
    def _initialize(self):
        """Initialize RAG components"""
        try:
            # Check if Ollama embedding model is available
            logger.info(f"Checking Ollama embedding model: {self.embedding_model_name}")
            self._check_ollama_model(self.embedding_model_name)
            
            # Initialize ChromaDB
            os.makedirs(self.chroma_path, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(
                path=self.chroma_path,
                settings=Settings(allow_reset=True)
            )
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name=self.collection_name,
                    embedding_function=self._get_embedding_function()
                )
                logger.info(f"Loaded existing collection: {self.collection_name}")
            except ValueError:
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    embedding_function=self._get_embedding_function()
                )
                logger.info(f"Created new collection: {self.collection_name}")
            
            logger.info("XML RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize XML RAG service: {str(e)}")
            raise
    
    def _get_embedding_function(self):
        """Create ChromaDB embedding function using Ollama"""
        class OllamaEmbeddingFunction:
            def __init__(self, model_name):
                self.model_name = model_name
            
            def __call__(self, input_texts):
                embeddings = []
                for text in input_texts:
                    try:
                        response = ollama.embeddings(
                            model=self.model_name,
                            prompt=text
                        )
                        embeddings.append(response['embedding'])
                    except Exception as e:
                        logger.error(f"Failed to get embedding for text: {str(e)}")
                        # Return zero vector as fallback
                        embeddings.append([0.0] * 1536)  # Default embedding dimension
                return embeddings
        
        return OllamaEmbeddingFunction(self.embedding_model_name)
    
    def _check_ollama_model(self, model_name: str):
        """Check if Ollama model is available and pull if needed"""
        try:
            models = ollama.list()
            model_names = [model['name'] for model in models['models']]
            
            if not any(name.startswith(model_name) for name in model_names):
                logger.info(f"Pulling Ollama model: {model_name}")
                ollama.pull(model_name)
                logger.info(f"Successfully pulled model: {model_name}")
            else:
                logger.info(f"Ollama model {model_name} is available")
                
        except Exception as e:
            logger.error(f"Failed to check/pull Ollama model {model_name}: {str(e)}")
            raise RuntimeError(f"Ollama model {model_name} not available: {str(e)}")
    
    async def index_xml_templates(self, xml_directory: str = "Export-Streams") -> int:
        """
        Index all XML templates from the specified directory
        
        Args:
            xml_directory: Directory containing XML template files
            
        Returns:
            Number of templates indexed
        """
        logger.info(f"Starting XML template indexing from: {xml_directory}")
        indexed_count = 0
        
        try:
            # Find all XML files
            xml_pattern = os.path.join(xml_directory, "**", "*.xml")
            xml_files = glob.glob(xml_pattern, recursive=True)
            
            logger.info(f"Found {len(xml_files)} XML files to index")
            
            # Process each XML file
            for xml_file in xml_files:
                try:
                    template = await self._create_template_from_file(xml_file)
                    if template:
                        await self._add_template_to_collection(template)
                        self.template_cache[template.id] = template
                        indexed_count += 1
                        
                        if indexed_count % 10 == 0:
                            logger.info(f"Indexed {indexed_count} templates...")
                
                except Exception as e:
                    logger.warning(f"Failed to index {xml_file}: {str(e)}")
                    continue
            
            logger.info(f"Successfully indexed {indexed_count} XML templates")
            return indexed_count
            
        except Exception as e:
            logger.error(f"Template indexing failed: {str(e)}")
            return indexed_count
    
    async def _create_template_from_file(self, xml_file_path: str) -> Optional[XMLTemplate]:
        """Create XMLTemplate from XML file"""
        try:
            async with aiofiles.open(xml_file_path, 'r', encoding='utf-8') as file:
                xml_content = await file.read()
            
            # Parse XML to extract metadata
            metadata = self._extract_xml_metadata(xml_content)
            if not metadata:
                return None
            
            # Create searchable description
            description = self._create_template_description(metadata)
            
            # Determine job type
            job_type = self._determine_job_type(metadata)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(metadata)
            
            template = XMLTemplate(
                id=f"template_{Path(xml_file_path).stem}",
                filename=Path(xml_file_path).name,
                file_path=xml_file_path,
                job_type=job_type,
                description=description,
                complexity_score=complexity_score,
                job_count=len(metadata.get('jobs', [])),
                patterns=metadata.get('patterns', []),
                xml_content=xml_content,
                metadata=metadata
            )
            
            return template
            
        except Exception as e:
            logger.error(f"Failed to create template from {xml_file_path}: {str(e)}")
            return None
    
    def _extract_xml_metadata(self, xml_content: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from XML content"""
        try:
            root = ET.fromstring(xml_content)
            
            # Find Stream element
            stream = root.find(".//Stream")
            if stream is None:
                return None
            
            metadata = {
                'stream_name': self._get_element_text(stream, 'StreamName'),
                'description': self._get_element_text(stream, 'StreamDocumentation'),
                'short_description': self._get_element_text(stream, 'ShortDescription'),
                'agent_detail': self._get_element_text(stream, 'AgentDetail'),
                'max_runs': self._get_element_text(stream, 'MaxStreamRuns'),
                'stream_type': self._get_element_text(stream, 'StreamType'),
                'jobs': [],
                'patterns': [],
                'has_scheduling': False,
                'has_file_transfer': False,
                'has_sap': False
            }
            
            # Extract job information
            jobs_elem = stream.find('Jobs')
            if jobs_elem is not None:
                for job in jobs_elem.findall('Job'):
                    job_info = {
                        'name': self._get_element_text(job, 'JobName'),
                        'category': self._get_element_text(job, 'JobCategory'),
                        'type': self._get_element_text(job, 'JobType'),
                        'template_type': self._get_element_text(job, 'TemplateType'),
                        'description': self._get_element_text(job, 'ShortDescription'),
                        'script': self._get_element_text(job, 'MainScript')
                    }
                    metadata['jobs'].append(job_info)
                    
                    # Detect patterns
                    if job_info['template_type'] == 'FileTransfer':
                        metadata['has_file_transfer'] = True
                        metadata['patterns'].append('file-transfer')
                    
                    if job_info['type'] in ['Windows', 'Unix']:
                        metadata['patterns'].append(f"script-{job_info['type'].lower()}")
                    
                    if 'SAP' in str(job_info.get('description', '')).upper() or 'REPORT' in str(job_info.get('script', '')).upper():
                        metadata['has_sap'] = True
                        metadata['patterns'].append('sap-integration')
            
            # Check for scheduling
            schedule_rule = stream.find('ScheduleRule')
            if schedule_rule is not None and schedule_rule.find('ScheduleRuleXml') is not None:
                metadata['has_scheduling'] = True
                metadata['patterns'].append('scheduling')
            
            # Add general patterns
            if len(metadata['jobs']) == 1:
                metadata['patterns'].append('single-job')
            elif len(metadata['jobs']) > 1:
                metadata['patterns'].append('multi-job')
            
            if metadata.get('stream_type') == 'Normal':
                metadata['patterns'].append('normal-stream')
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract XML metadata: {str(e)}")
            return None
    
    def _get_element_text(self, parent, element_name: str) -> str:
        """Safely get element text content"""
        elem = parent.find(element_name)
        if elem is not None:
            return elem.text or ""
        return ""
    
    def _create_template_description(self, metadata: Dict[str, Any]) -> str:
        """Create searchable description from metadata"""
        parts = []
        
        # Stream info
        if metadata.get('stream_name'):
            parts.append(f"Stream: {metadata['stream_name']}")
        
        if metadata.get('description'):
            parts.append(f"Description: {metadata['description']}")
        
        if metadata.get('short_description'):
            parts.append(f"Summary: {metadata['short_description']}")
        
        # Job info
        jobs = metadata.get('jobs', [])
        if jobs:
            parts.append(f"Jobs: {len(jobs)} job(s)")
            for job in jobs[:3]:  # First 3 jobs
                if job.get('name'):
                    parts.append(f"- {job['name']}")
                if job.get('description'):
                    parts.append(f"  {job['description']}")
        
        # Patterns
        patterns = metadata.get('patterns', [])
        if patterns:
            parts.append(f"Patterns: {', '.join(patterns)}")
        
        # Technical details
        if metadata.get('has_file_transfer'):
            parts.append("Includes file transfer operations")
        
        if metadata.get('has_sap'):
            parts.append("Includes SAP integration")
        
        if metadata.get('has_scheduling'):
            parts.append("Includes scheduling configuration")
        
        return " | ".join(parts)
    
    def _determine_job_type(self, metadata: Dict[str, Any]) -> JobType:
        """Determine primary job type from metadata"""
        if metadata.get('has_file_transfer'):
            return JobType.FILE_TRANSFER
        elif metadata.get('has_sap'):
            return JobType.SAP
        else:
            return JobType.STANDARD
    
    def _calculate_complexity_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate complexity score (0-10)"""
        score = 1.0  # Base score
        
        # Job count contribution
        job_count = len(metadata.get('jobs', []))
        score += min(job_count * 0.5, 3.0)
        
        # Pattern complexity
        patterns = metadata.get('patterns', [])
        if 'file-transfer' in patterns:
            score += 1.5
        if 'sap-integration' in patterns:
            score += 2.0
        if 'scheduling' in patterns:
            score += 1.0
        if 'multi-job' in patterns:
            score += 1.0
        
        # Script complexity (basic heuristic)
        for job in metadata.get('jobs', []):
            script = job.get('script', '')
            if script:
                if len(script) > 200:
                    score += 0.5
                if any(keyword in script.lower() for keyword in ['loop', 'function', 'procedure']):
                    score += 0.5
        
        return min(score, 10.0)
    
    async def _add_template_to_collection(self, template: XMLTemplate):
        """Add template to ChromaDB collection"""
        try:
            self.collection.add(
                documents=[template.description],
                metadatas=[{
                    'id': template.id,
                    'filename': template.filename,
                    'job_type': template.job_type.value,
                    'complexity_score': template.complexity_score,
                    'job_count': template.job_count,
                    'patterns': json.dumps(template.patterns)
                }],
                ids=[template.id]
            )
        except Exception as e:
            logger.error(f"Failed to add template to collection: {str(e)}")
            raise
    
    async def search_similar_templates(self, query: TemplateSearchQuery) -> List[TemplateMatch]:
        """
        Search for similar templates using RAG
        
        Args:
            query: Search query with filters
            
        Returns:
            List of matching templates with similarity scores
        """
        try:
            start_time = time.time()
            
            # Prepare where clause for filtering
            where_clause = {}
            if query.job_type:
                where_clause['job_type'] = query.job_type.value
            
            # Search in ChromaDB
            results = self.collection.query(
                query_texts=[query.query],
                n_results=query.max_results,
                where=where_clause if where_clause else None
            )
            
            matches = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    template_id = results['ids'][0][i]
                    similarity_score = 1.0 - results['distances'][0][i]  # Convert distance to similarity
                    
                    # Get template from cache or create
                    template = self.template_cache.get(template_id)
                    if not template:
                        # Recreate template from metadata
                        metadata = results['metadatas'][0][i]
                        template = await self._recreate_template_from_metadata(metadata)
                        if template:
                            self.template_cache[template_id] = template
                    
                    if template:
                        match_reasons = self._generate_match_reasons(template, query.query, similarity_score)
                        matches.append(TemplateMatch(
                            template=template,
                            similarity_score=similarity_score,
                            reasons=match_reasons
                        ))
            
            search_time = int((time.time() - start_time) * 1000)
            logger.info(f"Template search completed in {search_time}ms - Found {len(matches)} matches")
            
            # Sort by similarity score
            matches.sort(key=lambda x: x.similarity_score, reverse=True)
            
            return matches
            
        except Exception as e:
            logger.error(f"Template search failed: {str(e)}")
            return []
    
    def _generate_match_reasons(self, template: XMLTemplate, query: str, similarity_score: float) -> List[str]:
        """Generate reasons why template matches query"""
        reasons = []
        
        query_lower = query.lower()
        
        # Check for keyword matches
        if any(word in template.description.lower() for word in query_lower.split()):
            reasons.append("Keyword match in description")
        
        if template.job_type.value in query_lower:
            reasons.append(f"Job type match: {template.job_type.value}")
        
        for pattern in template.patterns:
            if pattern.replace('-', ' ') in query_lower:
                reasons.append(f"Pattern match: {pattern}")
        
        if similarity_score > 0.8:
            reasons.append("High semantic similarity")
        elif similarity_score > 0.6:
            reasons.append("Good semantic similarity")
        
        if template.complexity_score < 5 and "simple" in query_lower:
            reasons.append("Low complexity match")
        elif template.complexity_score >= 7 and any(word in query_lower for word in ["complex", "advanced"]):
            reasons.append("High complexity match")
        
        return reasons or ["General similarity match"]
    
    async def _recreate_template_from_metadata(self, metadata: Dict[str, Any]) -> Optional[XMLTemplate]:
        """Recreate template from ChromaDB metadata"""
        try:
            template_id = metadata['id']
            filename = metadata['filename']
            
            # Try to find original file
            xml_files = glob.glob(f"Export-Streams/**/{filename}", recursive=True)
            if xml_files:
                return await self._create_template_from_file(xml_files[0])
            
            # Create minimal template if file not found
            return XMLTemplate(
                id=template_id,
                filename=filename,
                file_path="",
                job_type=JobType(metadata['job_type']),
                description="Template not found",
                complexity_score=float(metadata.get('complexity_score', 5)),
                job_count=int(metadata.get('job_count', 1)),
                patterns=json.loads(metadata.get('patterns', '[]')),
                xml_content="",
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to recreate template from metadata: {str(e)}")
            return None
    
    async def generate_xml(self, wizard_data: WizardFormData) -> XMLGenerationResult:
        """
        Generate XML using RAG pipeline
        
        Args:
            wizard_data: Complete wizard form data
            
        Returns:
            XML generation result with validation
        """
        start_time = time.time()
        
        try:
            # Step 1: Find best matching template
            search_query = self._create_search_query_from_wizard_data(wizard_data)
            template_matches = await self.search_similar_templates(search_query)
            
            if not template_matches:
                return XMLGenerationResult(
                    success=False,
                    error_message="No suitable templates found for XML generation"
                )
            
            best_match = template_matches[0]
            
            # Step 2: Generate prompt
            prompt = self._create_generation_prompt(wizard_data, best_match)
            
            # Step 3: Generate XML with LLM
            generated_xml = await self._generate_xml_with_llm(prompt)
            
            if not generated_xml:
                return XMLGenerationResult(
                    success=False,
                    error_message="Failed to generate XML content"
                )
            
            # Step 4: Validate generated XML
            validation_result = self.validator.validate_xml_string(generated_xml)
            
            # Step 5: Determine if human review is needed
            requires_review = self._requires_human_review(wizard_data, validation_result, best_match)
            review_reasons = self._get_review_reasons(wizard_data, validation_result, best_match)
            
            generation_time = int((time.time() - start_time) * 1000)
            
            return XMLGenerationResult(
                success=True,
                xml_content=generated_xml,
                template_used=best_match,
                validation_results=validation_result,
                requires_human_review=requires_review,
                review_reasons=review_reasons,
                generation_time_ms=generation_time
            )
            
        except Exception as e:
            logger.error(f"XML generation failed: {str(e)}")
            return XMLGenerationResult(
                success=False,
                error_message=str(e),
                generation_time_ms=int((time.time() - start_time) * 1000)
            )
    
    def _create_search_query_from_wizard_data(self, wizard_data: WizardFormData) -> TemplateSearchQuery:
        """Create search query from wizard form data"""
        query_parts = []
        
        # Add job type
        query_parts.append(wizard_data.job_type.value)
        
        # Add specific job details
        if hasattr(wizard_data.job_form, 'job_name') and wizard_data.job_form.job_name:
            query_parts.append(wizard_data.job_form.job_name)
        
        # Add stream description
        if wizard_data.stream_properties.description:
            query_parts.append(wizard_data.stream_properties.description)
        
        # Add specific patterns based on job type
        if wizard_data.job_type == JobType.FILE_TRANSFER:
            query_parts.append("file transfer")
        elif wizard_data.job_type == JobType.SAP:
            query_parts.append("SAP report")
        elif wizard_data.job_type == JobType.STANDARD:
            if hasattr(wizard_data.job_form, 'os'):
                query_parts.append(f"{wizard_data.job_form.os} script")
        
        query = " ".join(query_parts)
        
        return TemplateSearchQuery(
            query=query,
            job_type=wizard_data.job_type,
            max_results=3
        )
    
    def _create_generation_prompt(self, wizard_data: WizardFormData, template_match: TemplateMatch) -> str:
        """Create structured prompt for XML generation"""
        
        prompt = f"""Du bist ein Experte für StreamWorks XML-Generierung. 

TEMPLATE (Ähnlichkeit: {template_match.similarity_score:.2f}):
{template_match.template.xml_content}

BENUTZER-ANFRAGE:
Job-Typ: {wizard_data.job_type.value}

Stream-Eigenschaften:
- Name: {wizard_data.stream_properties.stream_name}
- Beschreibung: {wizard_data.stream_properties.description}
- Agent: {getattr(wizard_data.job_form, 'agent', 'gtasswvk05445')}
- Max Runs: {wizard_data.stream_properties.max_runs}
- Kontakt: {wizard_data.stream_properties.contact_person.first_name} {wizard_data.stream_properties.contact_person.last_name}

Job-Details:
{self._format_job_details(wizard_data)}

Scheduling:
{self._format_scheduling_details(wizard_data.scheduling)}

AUFGABE: 
Generiere eine vollständige StreamWorks XML-Konfiguration basierend auf dem Template und den Benutzer-Daten.
- Behalte die XML-Struktur und alle erforderlichen Elemente bei
- Ersetze nur die relevanten Werte mit den Benutzerdaten
- Stelle sicher, dass die XML syntaktisch korrekt ist
- Verwende CDATA-Sections für Text-Inhalte mit Sonderzeichen

XML:"""
        
        return prompt
    
    def _format_job_details(self, wizard_data: WizardFormData) -> str:
        """Format job details for prompt"""
        job_form = wizard_data.job_form
        
        if wizard_data.job_type == JobType.STANDARD:
            return f"""- Job Name: {getattr(job_form, 'job_name', '')}
- Betriebssystem: {getattr(job_form, 'os', '')}
- Script: {getattr(job_form, 'script', '')}"""
        
        elif wizard_data.job_type == JobType.SAP:
            params = getattr(job_form, 'selection_parameters', [])
            param_text = "\n".join([f"  {p.parameter}: {p.value}" for p in params])
            return f"""- Job Name: {getattr(job_form, 'job_name', '')}
- System: {getattr(job_form, 'system', '')}
- Report: {getattr(job_form, 'report', '')}
- Variante: {getattr(job_form, 'variant', '')}
- Batch User: {getattr(job_form, 'batch_user', '')}
- Parameter:
{param_text}"""
        
        elif wizard_data.job_type == JobType.FILE_TRANSFER:
            return f"""- Job Name: {getattr(job_form, 'job_name', '')}
- Source Agent: {getattr(job_form, 'source_agent', '')}
- Source Path: {getattr(job_form, 'source_path', '')}
- Target Agent: {getattr(job_form, 'target_agent', '')}
- Target Path: {getattr(job_form, 'target_path', '')}
- Verhalten bei existierenden Dateien: {getattr(job_form, 'on_exists_behavior', 'Overwrite')}"""
        
        return "- Standard Job Configuration"
    
    def _format_scheduling_details(self, scheduling) -> str:
        """Format scheduling details for prompt"""
        if scheduling.mode == "simple" and scheduling.simple:
            return f"- Einfache Planung: {scheduling.simple.preset} um {scheduling.simple.time or 'unbestimmt'}"
        elif scheduling.mode == "natural" and scheduling.natural:
            return f"- Natürliche Beschreibung: {scheduling.natural.description}"
        elif scheduling.mode == "advanced" and scheduling.advanced:
            if scheduling.advanced.cron_expression:
                return f"- Cron: {scheduling.advanced.cron_expression}"
            elif scheduling.advanced.schedule_rule_xml:
                return f"- Schedule Rule XML: {scheduling.advanced.schedule_rule_xml}"
        
        return "- Manuelle Ausführung"
    
    async def _generate_xml_with_llm(self, prompt: str) -> Optional[str]:
        """Generate XML using Ollama LLM"""
        try:
            # Check if Ollama is available
            models = ollama.list()
            if not any(model['name'].startswith(self.ollama_model) for model in models['models']):
                logger.error(f"Ollama model {self.ollama_model} not available")
                return None
            
            # Generate with Ollama
            response = ollama.generate(
                model=self.ollama_model,
                prompt=prompt,
                options={
                    'temperature': 0.1,  # Low temperature for consistent XML generation
                    'top_k': 10,
                    'top_p': 0.9
                }
            )
            
            generated_text = response['response']
            
            # Extract XML from response
            xml_content = self._extract_xml_from_response(generated_text)
            
            return xml_content
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return None
    
    def _extract_xml_from_response(self, response: str) -> Optional[str]:
        """Extract XML content from LLM response"""
        # Look for XML content between <?xml and </ExportableStream>
        start_marker = "<?xml"
        end_marker = "</ExportableStream>"
        
        start_idx = response.find(start_marker)
        if start_idx == -1:
            # Try without XML declaration
            start_marker = "<ExportableStream"
            start_idx = response.find(start_marker)
        
        if start_idx == -1:
            logger.error("No XML content found in LLM response")
            return None
        
        end_idx = response.find(end_marker, start_idx)
        if end_idx == -1:
            logger.error("Incomplete XML in LLM response")
            return None
        
        xml_content = response[start_idx:end_idx + len(end_marker)].strip()
        
        # Add XML declaration if missing
        if not xml_content.startswith("<?xml"):
            xml_content = '<?xml version="1.0" encoding="utf-8"?>\n' + xml_content
        
        return xml_content
    
    def _requires_human_review(self, wizard_data: WizardFormData, 
                              validation_result: ValidationResult, 
                              template_match: TemplateMatch) -> bool:
        """Determine if human review is required"""
        
        # Always review if validation failed
        if not validation_result.valid:
            return True
        
        # Review if template similarity is low
        if template_match.similarity_score < 0.7:
            return True
        
        # Review complex jobs
        if wizard_data.job_type == JobType.SAP:
            sap_params = getattr(wizard_data.job_form, 'selection_parameters', [])
            if len(sap_params) > 5:
                return True
        
        # Review if template complexity is high
        if template_match.template.complexity_score > 7:
            return True
        
        return False
    
    def _get_review_reasons(self, wizard_data: WizardFormData, 
                           validation_result: ValidationResult,
                           template_match: TemplateMatch) -> List[str]:
        """Get reasons why human review is needed"""
        reasons = []
        
        if not validation_result.valid:
            reasons.append("XML validation errors detected")
        
        if template_match.similarity_score < 0.7:
            reasons.append(f"Low template similarity ({template_match.similarity_score:.2f})")
        
        if wizard_data.job_type == JobType.SAP:
            sap_params = getattr(wizard_data.job_form, 'selection_parameters', [])
            if len(sap_params) > 5:
                reasons.append("Complex SAP parameter configuration")
        
        if template_match.template.complexity_score > 7:
            reasons.append("High template complexity")
        
        return reasons


# Global RAG service instance
rag_service_instance = None

def get_rag_service() -> XMLTemplateRAG:
    """Get global RAG service instance (singleton pattern)"""
    global rag_service_instance
    if rag_service_instance is None:
        rag_service_instance = XMLTemplateRAG()
    return rag_service_instance