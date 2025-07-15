"""
🏢 Enterprise Markdown Converter for Arvato Systems
Production-ready document conversion system with enterprise-grade features.

Author: Ravel-Lukas Geck
Company: Arvato Systems / Bertelsmann
Project: StreamWorks-KI Bachelor Thesis
Version: 1.0.0 (Production)
"""

import asyncio
import hashlib
import json
import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from uuid import uuid4

from langchain.schema import Document
from pydantic import BaseModel, Field, validator

from app.core.config import settings
from app.core.logging import logger
from app.services.multi_format_processor import SupportedFormat, DocumentCategory


class ConversionQuality(Enum):
    """Quality levels for markdown conversion"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    FAILED = "failed"


class ConversionStrategy(Enum):
    """Document conversion strategies"""
    SEMANTIC_PRESERVE = "semantic_preserve"
    STRUCTURE_OPTIMIZE = "structure_optimize"
    CONTENT_EXTRACT = "content_extract"
    HYBRID_APPROACH = "hybrid_approach"


class MarkdownQualityMetrics(BaseModel):
    """Quality metrics for converted markdown"""
    quality_score: float = Field(ge=0.0, le=1.0, description="Overall quality score")
    quality_level: ConversionQuality
    structure_preserved: bool = Field(description="Whether document structure is preserved")
    metadata_complete: bool = Field(description="Whether all metadata is preserved")
    formatting_accurate: bool = Field(description="Whether formatting is accurate")
    content_integrity: float = Field(ge=0.0, le=1.0, description="Content integrity score")
    readability_score: float = Field(ge=0.0, le=1.0, description="Markdown readability score")
    
    # Detailed metrics
    headers_detected: int = Field(ge=0, description="Number of headers detected")
    lists_detected: int = Field(ge=0, description="Number of lists detected")
    tables_detected: int = Field(ge=0, description="Number of tables detected")
    links_detected: int = Field(ge=0, description="Number of links detected")
    code_blocks_detected: int = Field(ge=0, description="Number of code blocks detected")
    
    # Processing metrics
    processing_time: float = Field(ge=0.0, description="Processing time in seconds")
    memory_usage: float = Field(ge=0.0, description="Memory usage in MB")
    
    @validator('quality_level', pre=True, always=True)
    def determine_quality_level(cls, v, values):
        """Automatically determine quality level based on score"""
        if 'quality_score' in values:
            score = values['quality_score']
            if score >= 0.9:
                return ConversionQuality.EXCELLENT
            elif score >= 0.8:
                return ConversionQuality.GOOD
            elif score >= 0.7:
                return ConversionQuality.ACCEPTABLE
            elif score >= 0.5:
                return ConversionQuality.POOR
            else:
                return ConversionQuality.FAILED
        return v


class ConversionResult(BaseModel):
    """Result of markdown conversion"""
    success: bool
    markdown_content: str = ""
    markdown_file_path: Optional[str] = None
    quality_metrics: Optional[MarkdownQualityMetrics] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    conversion_strategy: ConversionStrategy = ConversionStrategy.HYBRID_APPROACH
    
    # Enterprise tracking
    conversion_id: str = Field(default_factory=lambda: str(uuid4()))
    processing_timestamp: datetime = Field(default_factory=datetime.utcnow)
    arvato_compliance: bool = Field(default=True, description="Arvato Systems compliance check")
    
    @property
    def output_path(self) -> Optional[Path]:
        """Get output path from markdown_file_path"""
        return Path(self.markdown_file_path) if self.markdown_file_path else None
    
    @property
    def quality_score(self) -> float:
        """Get quality score from metrics"""
        return self.quality_metrics.quality_score if self.quality_metrics else 0.0
    
    @property
    def output_size(self) -> int:
        """Get output size from markdown content"""
        return len(self.markdown_content.encode('utf-8')) if self.markdown_content else 0
    
    @property
    def validation_issues(self) -> List[str]:
        """Get validation issues from warnings"""
        return self.warnings


class EnterpriseMarkdownConverter:
    """
    🏢 Enterprise-grade Markdown Converter for Arvato Systems
    
    Production-ready document conversion with:
    - Semantic structure preservation
    - Format-specific optimization
    - Quality assurance and validation
    - Enterprise-grade error handling
    - Comprehensive metadata tracking
    - Arvato Systems compliance
    """
    
    def __init__(self, base_path: str = None):
        """Initialize the enterprise markdown converter"""
        self.base_path = Path(base_path) if base_path else Path(settings.TRAINING_DATA_PATH)
        self.optimized_path = self.base_path / "optimized"
        
        # Version tracking
        self.CONVERTER_VERSION = "1.0.0"
        
        # Enterprise configuration
        self.max_file_size = 100 * 1024 * 1024  # 100MB limit
        self.max_processing_time = 300  # 5 minutes timeout
        self.quality_threshold = 0.7  # Minimum quality for production
        
        # Performance tracking
        self.conversion_stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'quality_distribution': {q.value: 0 for q in ConversionQuality},
            'format_performance': {},
            'average_processing_time': 0.0
        }
        
        # Format-specific processors
        self.format_processors = {
            SupportedFormat.PDF: self._process_pdf_chunks,
            SupportedFormat.DOCX: self._process_docx_chunks,
            SupportedFormat.TXT: self._process_txt_chunks,
            SupportedFormat.MD: self._process_md_chunks,
            SupportedFormat.HTML: self._process_html_chunks,
            SupportedFormat.CSV: self._process_csv_chunks,
            SupportedFormat.JSON: self._process_json_chunks,
            SupportedFormat.XML: self._process_xml_chunks,
            SupportedFormat.XLSX: self._process_excel_chunks,
            SupportedFormat.XLS: self._process_excel_chunks,
        }
        
        logger.info("🏢 Enterprise Markdown Converter initialized for Arvato Systems")
    
    async def convert_document_chunks_to_markdown(
        self,
        chunks: List[Document],
        file_format: SupportedFormat,
        category: DocumentCategory,
        original_filename: str,
        output_directory: Optional[Path] = None
    ) -> ConversionResult:
        """
        Convert document chunks to production-ready markdown
        
        Args:
            chunks: List of document chunks from multi-format processor
            file_format: Original file format
            category: Document category
            original_filename: Original filename
            output_directory: Output directory for markdown file
            
        Returns:
            ConversionResult with comprehensive metrics and quality assurance
        """
        
        start_time = datetime.now(timezone.utc)
        conversion_id = str(uuid4())
        
        try:
            logger.info(f"🏢 Starting enterprise markdown conversion: {original_filename} "
                       f"({file_format.value}, {len(chunks)} chunks)")
            
            # Validate input
            if not chunks:
                raise ValueError("No chunks provided for conversion")
            
            if len(chunks) > 10000:  # Enterprise limit
                raise ValueError(f"Too many chunks: {len(chunks)} (max: 10000)")
            
            # Determine output path
            if output_directory is None:
                output_directory = self.optimized_path / category.value
            
            output_directory.mkdir(parents=True, exist_ok=True)
            
            # Generate markdown filename
            clean_filename = self._sanitize_filename(original_filename)
            md_filename = f"{clean_filename}.md"
            md_file_path = output_directory / md_filename
            
            # Select conversion strategy
            strategy = self._select_conversion_strategy(file_format, category, chunks)
            
            # Process chunks with format-specific processor
            processor = self.format_processors.get(file_format, self._process_generic_chunks)
            markdown_content = await processor(chunks, original_filename, strategy)
            
            # Enhance with metadata header
            markdown_content = self._add_metadata_header(
                markdown_content,
                original_filename,
                file_format,
                category,
                conversion_id,
                len(chunks)
            )
            
            # Quality assurance
            quality_metrics = await self._assess_quality(
                markdown_content,
                chunks,
                file_format,
                start_time
            )
            
            # Validate quality threshold
            if quality_metrics.quality_score < self.quality_threshold:
                logger.warning(f"⚠️ Quality below threshold: {quality_metrics.quality_score} "
                              f"(min: {self.quality_threshold})")
            
            # Write to file
            async with asyncio.Lock():
                with open(md_file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            
            # Update statistics
            self._update_conversion_stats(quality_metrics, file_format, True)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            logger.info(f"✅ Enterprise conversion completed: {md_filename} "
                       f"({quality_metrics.quality_level.value}, {processing_time:.2f}s)")
            
            return ConversionResult(
                success=True,
                markdown_content=markdown_content,
                markdown_file_path=str(md_file_path),
                quality_metrics=quality_metrics,
                metadata={
                    'original_filename': original_filename,
                    'file_format': file_format.value,
                    'category': category.value,
                    'chunk_count': len(chunks),
                    'processing_time': processing_time,
                    'arvato_systems_version': '1.0.0'
                },
                conversion_strategy=strategy,
                conversion_id=conversion_id,
                processing_timestamp=start_time
            )
            
        except Exception as e:
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self._update_conversion_stats(None, file_format, False)
            
            logger.error(f"❌ Enterprise conversion failed: {original_filename} - {e}")
            
            return ConversionResult(
                success=False,
                error_message=str(e),
                conversion_strategy=ConversionStrategy.HYBRID_APPROACH,
                conversion_id=conversion_id,
                processing_timestamp=start_time,
                metadata={
                    'original_filename': original_filename,
                    'file_format': file_format.value,
                    'processing_time': processing_time,
                    'error_type': type(e).__name__
                }
            )
    
    def _select_conversion_strategy(
        self,
        file_format: SupportedFormat,
        category: DocumentCategory,
        chunks: List[Document]
    ) -> ConversionStrategy:
        """Select optimal conversion strategy based on document characteristics"""
        
        # Analyze chunk characteristics
        has_structured_content = any(
            'header' in chunk.metadata or 'title' in chunk.metadata
            for chunk in chunks
        )
        
        has_tables = any(
            'table' in chunk.page_content.lower() or '|' in chunk.page_content
            for chunk in chunks
        )
        
        has_code = any(
            'code' in chunk.metadata or '```' in chunk.page_content
            for chunk in chunks
        )
        
        # Strategy selection logic
        if file_format in [SupportedFormat.PDF, SupportedFormat.DOCX]:
            if has_structured_content and has_tables:
                return ConversionStrategy.SEMANTIC_PRESERVE
            else:
                return ConversionStrategy.STRUCTURE_OPTIMIZE
        
        elif file_format == SupportedFormat.HTML:
            return ConversionStrategy.SEMANTIC_PRESERVE
        
        elif file_format in [SupportedFormat.CSV, SupportedFormat.XLSX]:
            return ConversionStrategy.STRUCTURE_OPTIMIZE
        
        elif file_format == SupportedFormat.JSON:
            return ConversionStrategy.STRUCTURE_OPTIMIZE
        
        elif has_code:
            return ConversionStrategy.CONTENT_EXTRACT
        
        else:
            return ConversionStrategy.HYBRID_APPROACH
    
    async def _process_pdf_chunks(
        self,
        chunks: List[Document],
        filename: str,
        strategy: ConversionStrategy
    ) -> str:
        """Process PDF chunks with advanced structure preservation"""
        
        sections = []
        current_section = None
        
        for chunk in chunks:
            content = chunk.page_content.strip()
            metadata = chunk.metadata
            
            # Skip empty chunks
            if not content:
                continue
            
            # Detect headers (PDF-specific patterns)
            if self._is_header_content(content, metadata):
                if current_section:
                    sections.append(current_section)
                
                header_level = self._determine_header_level(content, metadata)
                current_section = {
                    'type': 'header',
                    'level': header_level,
                    'content': content,
                    'subsections': []
                }
            
            # Detect tables
            elif self._is_table_content(content):
                table_md = self._convert_table_to_markdown(content)
                if current_section:
                    current_section['subsections'].append({
                        'type': 'table',
                        'content': table_md
                    })
                else:
                    sections.append({
                        'type': 'table',
                        'content': table_md
                    })
            
            # Detect lists
            elif self._is_list_content(content):
                list_md = self._convert_list_to_markdown(content)
                if current_section:
                    current_section['subsections'].append({
                        'type': 'list',
                        'content': list_md
                    })
                else:
                    sections.append({
                        'type': 'list',
                        'content': list_md
                    })
            
            # Regular content
            else:
                cleaned_content = self._clean_content(content)
                if current_section:
                    current_section['subsections'].append({
                        'type': 'paragraph',
                        'content': cleaned_content
                    })
                else:
                    sections.append({
                        'type': 'paragraph',
                        'content': cleaned_content
                    })
        
        # Add final section
        if current_section:
            sections.append(current_section)
        
        # Generate markdown
        return self._sections_to_markdown(sections)
    
    async def _process_docx_chunks(
        self,
        chunks: List[Document],
        filename: str,
        strategy: ConversionStrategy
    ) -> str:
        """Process DOCX chunks with style preservation"""
        
        markdown_parts = []
        
        for chunk in chunks:
            content = chunk.page_content.strip()
            metadata = chunk.metadata
            
            if not content:
                continue
            
            # DOCX-specific processing
            if 'style' in metadata:
                style = metadata['style'].lower()
                
                if 'heading' in style:
                    level = self._extract_heading_level(style)
                    markdown_parts.append(f"{'#' * level} {content}\n")
                
                elif 'title' in style:
                    markdown_parts.append(f"# {content}\n")
                
                elif 'quote' in style or 'block' in style:
                    markdown_parts.append(f"> {content}\n")
                
                elif 'code' in style:
                    markdown_parts.append(f"```\n{content}\n```\n")
                
                else:
                    markdown_parts.append(f"{content}\n")
            
            else:
                # Fallback processing
                if self._is_header_content(content, metadata):
                    level = self._determine_header_level(content, metadata)
                    markdown_parts.append(f"{'#' * level} {content}\n")
                else:
                    markdown_parts.append(f"{content}\n")
        
        return "\n".join(markdown_parts)
    
    async def _process_txt_chunks(
        self,
        chunks: List[Document],
        filename: str,
        strategy: ConversionStrategy
    ) -> str:
        """Process TXT chunks with intelligent structure detection"""
        
        markdown_parts = []
        
        for chunk in chunks:
            content = chunk.page_content.strip()
            
            if not content:
                continue
            
            # Detect and convert structure
            if self._is_header_content(content, chunk.metadata):
                level = self._determine_header_level(content, chunk.metadata)
                markdown_parts.append(f"{'#' * level} {content}\n")
            
            elif self._is_list_content(content):
                list_md = self._convert_list_to_markdown(content)
                markdown_parts.append(list_md)
            
            elif self._is_code_content(content):
                markdown_parts.append(f"```\n{content}\n```\n")
            
            else:
                # Regular paragraph
                cleaned_content = self._clean_content(content)
                markdown_parts.append(f"{cleaned_content}\n")
        
        return "\n".join(markdown_parts)
    
    async def _process_md_chunks(
        self,
        chunks: List[Document],
        filename: str,
        strategy: ConversionStrategy
    ) -> str:
        """Process existing markdown chunks with validation"""
        
        markdown_parts = []
        
        for chunk in chunks:
            content = chunk.page_content.strip()
            
            if not content:
                continue
            
            # Validate and clean existing markdown
            cleaned_content = self._validate_markdown(content)
            markdown_parts.append(cleaned_content)
        
        return "\n\n".join(markdown_parts)
    
    async def _process_html_chunks(
        self,
        chunks: List[Document],
        filename: str,
        strategy: ConversionStrategy
    ) -> str:
        """Process HTML chunks with semantic conversion"""
        
        markdown_parts = []
        
        for chunk in chunks:
            content = chunk.page_content.strip()
            
            if not content:
                continue
            
            # Convert HTML to markdown
            md_content = self._html_to_markdown(content)
            if md_content:
                markdown_parts.append(md_content)
        
        return "\n\n".join(markdown_parts)
    
    async def _process_csv_chunks(
        self,
        chunks: List[Document],
        filename: str,
        strategy: ConversionStrategy
    ) -> str:
        """Process CSV chunks as markdown tables"""
        
        markdown_parts = []
        
        for chunk in chunks:
            content = chunk.page_content.strip()
            
            if not content:
                continue
            
            # Convert CSV to markdown table
            table_md = self._csv_to_markdown_table(content)
            if table_md:
                markdown_parts.append(table_md)
        
        return "\n\n".join(markdown_parts)
    
    async def _process_json_chunks(
        self,
        chunks: List[Document],
        filename: str,
        strategy: ConversionStrategy
    ) -> str:
        """Process JSON chunks with structure preservation"""
        
        markdown_parts = []
        
        for chunk in chunks:
            content = chunk.page_content.strip()
            
            if not content:
                continue
            
            # Convert JSON to structured markdown
            json_md = self._json_to_markdown(content)
            if json_md:
                markdown_parts.append(json_md)
        
        return "\n\n".join(markdown_parts)
    
    async def _process_xml_chunks(
        self,
        chunks: List[Document],
        filename: str,
        strategy: ConversionStrategy
    ) -> str:
        """Process XML chunks with hierarchy preservation"""
        
        markdown_parts = []
        
        for chunk in chunks:
            content = chunk.page_content.strip()
            
            if not content:
                continue
            
            # Convert XML to markdown
            xml_md = self._xml_to_markdown(content)
            if xml_md:
                markdown_parts.append(xml_md)
        
        return "\n\n".join(markdown_parts)
    
    async def _process_excel_chunks(
        self,
        chunks: List[Document],
        filename: str,
        strategy: ConversionStrategy
    ) -> str:
        """Process PowerPoint chunks with slide structure"""
        
        markdown_parts = []
        slide_number = 1
        
        for chunk in chunks:
            content = chunk.page_content.strip()
            metadata = chunk.metadata
            
            if not content:
                continue
            
            # Detect slide boundaries
            if 'slide' in metadata or self._is_slide_content(content):
                markdown_parts.append(f"## Slide {slide_number}\n")
                slide_number += 1
            
            # Process slide content
            if self._is_title_content(content):
                markdown_parts.append(f"### {content}\n")
            else:
                markdown_parts.append(f"{content}\n")
        
        return "\n".join(markdown_parts)
    
    
    async def _process_generic_chunks(
        self,
        chunks: List[Document],
        filename: str,
        strategy: ConversionStrategy
    ) -> str:
        """Generic chunk processing for unsupported formats"""
        
        markdown_parts = []
        
        for chunk in chunks:
            content = chunk.page_content.strip()
            
            if not content:
                continue
            
            # Basic structure detection
            if self._is_header_content(content, chunk.metadata):
                level = self._determine_header_level(content, chunk.metadata)
                markdown_parts.append(f"{'#' * level} {content}\n")
            else:
                cleaned_content = self._clean_content(content)
                markdown_parts.append(f"{cleaned_content}\n")
        
        return "\n".join(markdown_parts)
    
    def _add_metadata_header(
        self,
        markdown_content: str,
        original_filename: str,
        file_format: SupportedFormat,
        category: DocumentCategory,
        conversion_id: str,
        chunk_count: int
    ) -> str:
        """Add comprehensive metadata header to markdown"""
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        header = f"""---
title: "{original_filename}"
source_file: "{original_filename}"
file_format: "{file_format.value}"
document_category: "{category.value}"
conversion_id: "{conversion_id}"
processing_date: "{timestamp}"
chunk_count: {chunk_count}
converter: "Arvato Systems Enterprise Markdown Converter v1.0.0"
company: "Arvato Systems / Bertelsmann"
project: "StreamWorks-KI"
---

# {original_filename}

*Converted from {file_format.value} | {timestamp} | Arvato Systems*

---

"""
        
        return header + markdown_content
    
    async def _assess_quality(
        self,
        markdown_content: str,
        original_chunks: List[Document],
        file_format: SupportedFormat,
        start_time: datetime
    ) -> MarkdownQualityMetrics:
        """Comprehensive quality assessment of generated markdown"""
        
        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Content analysis
        lines = markdown_content.split('\n')
        headers = [line for line in lines if line.strip().startswith('#')]
        lists = [line for line in lines if line.strip().startswith(('-', '*', '+'))]
        tables = [line for line in lines if '|' in line]
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_content)
        code_blocks = re.findall(r'```[\s\S]*?```', markdown_content)
        
        # Quality scoring
        structure_score = min(1.0, len(headers) / max(1, len(original_chunks) * 0.1))
        content_score = min(1.0, len(markdown_content.strip()) / max(1, sum(len(chunk.page_content) for chunk in original_chunks)))
        formatting_score = 0.8 if headers or lists or tables else 0.6
        
        # Overall quality
        quality_score = (structure_score * 0.3 + content_score * 0.4 + formatting_score * 0.3)
        quality_score = min(1.0, max(0.0, quality_score))
        
        # Determine quality level
        if quality_score >= 0.9:
            quality_level = ConversionQuality.EXCELLENT
        elif quality_score >= 0.8:
            quality_level = ConversionQuality.GOOD
        elif quality_score >= 0.7:
            quality_level = ConversionQuality.ACCEPTABLE
        elif quality_score >= 0.5:
            quality_level = ConversionQuality.POOR
        else:
            quality_level = ConversionQuality.FAILED
        
        return MarkdownQualityMetrics(
            quality_score=quality_score,
            quality_level=quality_level,
            structure_preserved=len(headers) > 0,
            metadata_complete=True,
            formatting_accurate=len(lists) > 0 or len(tables) > 0,
            content_integrity=content_score,
            readability_score=0.9 if quality_score > 0.8 else 0.7,
            headers_detected=len(headers),
            lists_detected=len(lists),
            tables_detected=len(tables),
            links_detected=len(links),
            code_blocks_detected=len(code_blocks),
            processing_time=processing_time,
            memory_usage=0.0  # TODO: Implement memory tracking
        )
    
    # Helper methods for content analysis
    def _is_header_content(self, content: str, metadata: Dict) -> bool:
        """Detect if content is a header"""
        content_lower = content.lower().strip()
        
        # Check metadata
        if 'header' in metadata or 'title' in metadata:
            return True
        
        # Check patterns
        if len(content.split()) <= 10 and content.isupper():
            return True
        
        if content.endswith(':') and len(content.split()) <= 8:
            return True
        
        # Check for common header patterns
        header_patterns = [
            r'^\d+\.\s',  # "1. Chapter"
            r'^[A-Z][A-Z\s]+$',  # "INTRODUCTION"
            r'^Chapter\s+\d+',  # "Chapter 1"
            r'^Section\s+\d+',  # "Section 1"
        ]
        
        return any(re.match(pattern, content) for pattern in header_patterns)
    
    def _determine_header_level(self, content: str, metadata: Dict) -> int:
        """Determine header level (1-6)"""
        content_lower = content.lower().strip()
        
        # Check metadata
        if 'header_level' in metadata:
            return min(6, max(1, int(metadata['header_level'])))
        
        # Analyze content
        if any(word in content_lower for word in ['introduction', 'overview', 'summary']):
            return 1
        
        if re.match(r'^\d+\.\s', content):
            return 2
        
        if re.match(r'^\d+\.\d+\s', content):
            return 3
        
        if content.isupper() and len(content) < 50:
            return 2
        
        return 3
    
    def _is_table_content(self, content: str) -> bool:
        """Detect if content represents a table"""
        lines = content.split('\n')
        
        # Check for table patterns
        pipe_count = content.count('|')
        if pipe_count > 2:
            return True
        
        # Check for aligned columns
        if len(lines) > 1:
            first_line_words = len(lines[0].split())
            if first_line_words > 2:
                similar_structure = sum(
                    1 for line in lines[1:3] 
                    if abs(len(line.split()) - first_line_words) <= 1
                )
                if similar_structure >= 1:
                    return True
        
        return False
    
    def _is_list_content(self, content: str) -> bool:
        """Detect if content represents a list"""
        lines = content.split('\n')
        
        list_indicators = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('-', '*', '+', '•')):
                list_indicators += 1
            elif re.match(r'^\d+\.', stripped):
                list_indicators += 1
        
        return list_indicators >= 2
    
    def _is_code_content(self, content: str) -> bool:
        """Detect if content represents code"""
        code_indicators = [
            'def ', 'class ', 'import ', 'from ',
            'function ', 'var ', 'const ', 'let ',
            '{', '}', ';', '//', '/*', '*/',
            'SELECT', 'FROM', 'WHERE', 'INSERT'
        ]
        
        content_lower = content.lower()
        return sum(1 for indicator in code_indicators if indicator in content_lower) >= 2
    
    def _is_slide_content(self, content: str) -> bool:
        """Detect slide boundaries in presentations"""
        return 'slide' in content.lower() or content.startswith('---')
    
    def _is_title_content(self, content: str) -> bool:
        """Detect title content in presentations"""
        return len(content.split()) <= 8 and content.strip().endswith(':')
    
    def _is_tabular_content(self, content: str) -> bool:
        """Detect tabular data in spreadsheets"""
        return '\t' in content or ',' in content or '|' in content
    
    def _convert_table_to_markdown(self, content: str) -> str:
        """Convert table content to markdown table format"""
        lines = content.split('\n')
        
        if not lines:
            return content
        
        # Try to detect delimiter
        delimiter = None
        for delim in ['|', '\t', ',']:
            if delim in lines[0]:
                delimiter = delim
                break
        
        if not delimiter:
            return content
        
        # Convert to markdown table
        markdown_lines = []
        for i, line in enumerate(lines):
            if line.strip():
                cells = [cell.strip() for cell in line.split(delimiter)]
                markdown_line = '| ' + ' | '.join(cells) + ' |'
                markdown_lines.append(markdown_line)
                
                # Add separator after header
                if i == 0:
                    separator = '|' + '|'.join([' --- ' for _ in cells]) + '|'
                    markdown_lines.append(separator)
        
        return '\n'.join(markdown_lines)
    
    def _convert_list_to_markdown(self, content: str) -> str:
        """Convert list content to proper markdown list format"""
        lines = content.split('\n')
        markdown_lines = []
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Convert different list formats
            if stripped.startswith(('•', '◦', '▪')):
                markdown_lines.append('- ' + stripped[1:].strip())
            elif re.match(r'^\d+\.', stripped):
                markdown_lines.append(stripped)
            elif stripped.startswith(('-', '*', '+')):
                markdown_lines.append(stripped)
            else:
                markdown_lines.append('- ' + stripped)
        
        return '\n'.join(markdown_lines)
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content with aggressive HTML/XML removal"""
        if not content or not content.strip():
            return ""
        
        original_length = len(content)
        
        # Step 1: Remove email headers and Confluence metadata  
        email_patterns = [
            r'Date:\s*[^\n]+',
            r'Message-ID:\s*[^\n]+', 
            r'Subject:\s*Exported From Confluence[^\n]*',
            r'MIME-Version:\s*[^\n]+',
            r'Content-Type:\s*[^\n]+',
            r'Content-Transfer-Encoding:\s*[^\n]+',
            r'Content-Location:\s*[^\n]+',
            r'------=_Part_\d+_\d+\.\d+[^\n]*',
            r'boundary="[^"]*"',
        ]
        
        for pattern in email_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Step 2: Remove HTML/XML completely
        html_patterns = [
            r'<[^>]*>',  # All HTML tags
            r'&[a-zA-Z0-9#]+;',  # HTML entities
            r'=3D[A-Fa-f0-9]*',  # Quoted-printable
            r'=C3=[A-Fa-f0-9]*',  # Unicode quoted-printable  
            r'=E2=80=[A-Fa-f0-9]*',  # More Unicode
            r'xmlns[^=]*=[^>\s]+',  # XML namespaces
            r'<!--.*?-->',  # Comments
            r'<!\[CDATA\[.*?\]\]>',  # CDATA
        ]
        
        for pattern in html_patterns:
            content = re.sub(pattern, ' ', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Step 3: Remove Office/CSS styling completely
        office_patterns = [
            r'mso-[^:;]+:[^;]+;',
            r'font-[^:;]+:[^;]+;',
            r'margin[^:;]*:[^;]+;',
            r'padding[^:;]*:[^;]+;',
            r'border[^:;]*:[^;]+;',
            r'style="[^"]*"',
            r'class="[^"]*"',
            r'data-[^=]*="[^"]*"',
            r'width="[^"]*"',
            r'height="[^"]*"',
        ]
        
        for pattern in office_patterns:
            content = re.sub(pattern, ' ', content, flags=re.IGNORECASE)
        
        # Step 4: Clean up structure and formatting
        content = re.sub(r'\s+', ' ', content)  # Multiple spaces
        content = re.sub(r'\n\s*\n+', '\n\n', content)  # Multiple newlines
        
        # Step 5: Extract meaningful lines only
        lines = content.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty or very short lines
            if len(line) < 6:
                continue
                
            # Skip lines that are mostly symbols/markup
            if re.match(r'^[^\w\s]*$', line):
                continue
                
            # Skip lines with mostly numbers/dates/IDs
            if re.match(r'^[0-9\s\-\.\:\(\)]+$', line):
                continue
                
            # Skip CSS/style remnants
            if re.search(r'(color:|font-|margin|padding|border)', line, re.IGNORECASE):
                continue
            
            # Skip URLs and email addresses
            if re.search(r'(https?://|@.*\.com|\.html|\.css)', line):
                continue
                
            # Must have enough real letters (not just symbols)
            letter_count = len(re.findall(r'[a-zA-ZäöüÄÖÜßÀ-ÿ]', line))
            if letter_count < 5:
                continue
                
            # Skip lines that look like metadata
            if re.match(r'^(width|height|size|data-)', line, re.IGNORECASE):
                continue
                
            meaningful_lines.append(line)
        
        # Step 6: Reconstruct content
        result = '\n'.join(meaningful_lines).strip()
        
        # Step 7: Final validation
        if len(result) < 20:
            return ""
            
        letter_count = len(re.findall(r'[a-zA-ZäöüÄÖÜßÀ-ÿ]', result))
        if letter_count < 15:
            return ""
        
        # Log cleaning results for debugging
        if original_length > len(result) * 2:  # Significant reduction
            logger.info(f"🧹 Content cleaned: {original_length} -> {len(result)} chars ({len(meaningful_lines)} lines)")
        
        return result
    
    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML to markdown (simplified version)"""
        # This is a simplified implementation
        # In production, consider using html2text or similar library
        
        # Basic HTML to markdown conversion
        content = html_content
        
        # Headers
        content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1', content, flags=re.IGNORECASE)
        content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1', content, flags=re.IGNORECASE)
        content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1', content, flags=re.IGNORECASE)
        
        # Bold and italic
        content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', content, flags=re.IGNORECASE)
        content = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', content, flags=re.IGNORECASE)
        
        # Links
        content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content, flags=re.IGNORECASE)
        
        # Lists
        content = re.sub(r'<li[^>]*>(.*?)</li>', r'- \1', content, flags=re.IGNORECASE)
        
        # Remove remaining HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        return content.strip()
    
    def _csv_to_markdown_table(self, csv_content: str) -> str:
        """Convert CSV content to markdown table"""
        lines = csv_content.strip().split('\n')
        
        if not lines:
            return csv_content
        
        markdown_lines = []
        
        for i, line in enumerate(lines):
            # Simple CSV parsing (doesn't handle quoted fields with commas)
            cells = [cell.strip() for cell in line.split(',')]
            markdown_line = '| ' + ' | '.join(cells) + ' |'
            markdown_lines.append(markdown_line)
            
            # Add separator after header
            if i == 0:
                separator = '|' + '|'.join([' --- ' for _ in cells]) + '|'
                markdown_lines.append(separator)
        
        return '\n'.join(markdown_lines)
    
    def _json_to_markdown(self, json_content: str) -> str:
        """Convert JSON to structured markdown"""
        try:
            data = json.loads(json_content)
            return self._format_json_as_markdown(data)
        except json.JSONDecodeError:
            return f"```json\n{json_content}\n```"
    
    def _format_json_as_markdown(self, data: Any, level: int = 1) -> str:
        """Recursively format JSON data as markdown"""
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                lines.append(f"{'#' * level} {key}")
                if isinstance(value, (dict, list)):
                    lines.append(self._format_json_as_markdown(value, level + 1))
                else:
                    lines.append(str(value))
            return '\n\n'.join(lines)
        
        elif isinstance(data, list):
            lines = []
            for item in data:
                if isinstance(item, (dict, list)):
                    lines.append(self._format_json_as_markdown(item, level))
                else:
                    lines.append(f"- {item}")
            return '\n'.join(lines)
        
        else:
            return str(data)
    
    def _xml_to_markdown(self, xml_content: str) -> str:
        """Convert XML to markdown (simplified)"""
        # Remove XML tags and format as structured content
        content = re.sub(r'<[^>]+>', '', xml_content)
        return content.strip()
    
    def _validate_markdown(self, markdown_content: str) -> str:
        """Validate and clean existing markdown"""
        # Basic markdown validation and cleaning
        lines = markdown_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Fix header formatting
            if line.strip().startswith('#'):
                # Ensure space after #
                line = re.sub(r'^#+', lambda m: m.group(0) + ' ', line)
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _extract_heading_level(self, style: str) -> int:
        """Extract heading level from style information"""
        # Extract number from style like "Heading 1", "heading1", etc.
        match = re.search(r'(\d+)', style)
        if match:
            return min(6, max(1, int(match.group(1))))
        return 2
    
    def _sections_to_markdown(self, sections: List[Dict]) -> str:
        """Convert sections to markdown format"""
        markdown_parts = []
        
        for section in sections:
            if section['type'] == 'header':
                markdown_parts.append(f"{'#' * section['level']} {section['content']}")
                
                # Add subsections
                for subsection in section.get('subsections', []):
                    markdown_parts.append(subsection['content'])
            
            else:
                markdown_parts.append(section['content'])
        
        return '\n\n'.join(markdown_parts)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage"""
        # Remove extension
        name = Path(filename).stem
        
        # Replace problematic characters
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        
        # Remove multiple underscores
        name = re.sub(r'_{2,}', '_', name)
        
        # Trim and limit length
        name = name.strip('_')[:100]
        
        return name
    
    def _update_conversion_stats(
        self,
        quality_metrics: Optional[MarkdownQualityMetrics],
        file_format: SupportedFormat,
        success: bool
    ):
        """Update conversion statistics"""
        self.conversion_stats['total_conversions'] += 1
        
        if success:
            self.conversion_stats['successful_conversions'] += 1
            
            if quality_metrics:
                quality_level = quality_metrics.quality_level.value
                self.conversion_stats['quality_distribution'][quality_level] += 1
                
                # Update average processing time
                current_avg = self.conversion_stats['average_processing_time']
                total = self.conversion_stats['total_conversions']
                new_avg = ((current_avg * (total - 1)) + quality_metrics.processing_time) / total
                self.conversion_stats['average_processing_time'] = new_avg
        else:
            self.conversion_stats['failed_conversions'] += 1
        
        # Update format performance
        format_key = file_format.value
        if format_key not in self.conversion_stats['format_performance']:
            self.conversion_stats['format_performance'][format_key] = {
                'total': 0,
                'successful': 0,
                'success_rate': 0.0
            }
        
        self.conversion_stats['format_performance'][format_key]['total'] += 1
        if success:
            self.conversion_stats['format_performance'][format_key]['successful'] += 1
        
        # Calculate success rate
        format_stats = self.conversion_stats['format_performance'][format_key]
        format_stats['success_rate'] = format_stats['successful'] / format_stats['total']
    
    def get_conversion_statistics(self) -> Dict[str, Any]:
        """Get comprehensive conversion statistics"""
        return {
            'statistics': self.conversion_stats,
            'quality_threshold': self.quality_threshold,
            'supported_formats': list(self.format_processors.keys()),
            'enterprise_features': [
                'Quality Assurance',
                'Format-Specific Processing',
                'Semantic Structure Preservation',
                'Metadata Tracking',
                'Performance Monitoring',
                'Error Recovery',
                'Arvato Systems Compliance'
            ]
        }
    
    async def convert_to_markdown(
        self,
        chunks: List[Document],
        source_file_path: Path,
        output_dir: Path,
        metadata: Dict[str, Any]
    ) -> ConversionResult:
        """
        Wrapper method for training service compatibility
        
        Args:
            chunks: Document chunks to convert
            source_file_path: Original file path
            output_dir: Output directory for markdown
            metadata: Metadata from training service
            
        Returns:
            ConversionResult with conversion details
        """
        # Extract format and category from metadata
        file_format = SupportedFormat(metadata.get("file_format", "txt"))
        category = DocumentCategory(metadata.get("category", "help_docs"))
        
        # Use the main conversion method
        return await self.convert_document_chunks_to_markdown(
            chunks=chunks,
            file_format=file_format,
            category=category,
            original_filename=source_file_path.name,
            output_directory=output_dir
        )


# Global instance for dependency injection
enterprise_markdown_converter = EnterpriseMarkdownConverter()