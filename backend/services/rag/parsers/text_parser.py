"""
Text Parser
Simple parser for plain text files (TXT, MD, JSON, XML)
"""

import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from .base_parser import BaseParser, ParsedDocument, DocumentType


class TextParser(BaseParser):
    """
    Parser for text-based file formats
    
    Supports:
    - Plain text (.txt)
    - Markdown (.md)
    - JSON (.json)
    - XML (.xml)
    
    Lightweight and fast for simple documents
    """
    
    @property
    def supported_types(self) -> List[DocumentType]:
        return [
            DocumentType.TXT,
            DocumentType.MD,
            DocumentType.JSON,
            DocumentType.XML
        ]
    
    @property
    def name(self) -> str:
        return "TextParser"
    
    def parse(
        self,
        content: bytes,
        filename: str,
        **kwargs
    ) -> ParsedDocument:
        """
        Parse text-based documents
        """
        doc_type = self._detect_type(filename)
        
        # Decode bytes to string
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            text_content = content.decode('latin-1')
        
        metadata = {
            "source": filename,
            "parsing_engine": "text_parser"
        }
        
        # Type-specific processing
        if doc_type == DocumentType.XML:
            metadata.update(self._extract_xml_metadata(text_content))
        elif doc_type == DocumentType.JSON:
            metadata.update(self._extract_json_metadata(text_content))
        
        return ParsedDocument(
            content=text_content,
            filename=filename,
            doc_type=doc_type,
            metadata=metadata,
            parsing_method="text_parser"
        )
    
    def _extract_xml_metadata(self, content: str) -> Dict[str, Any]:
        """Extract Streamworks-specific metadata from XML"""
        metadata = {"xml_valid": False}
        
        try:
            root = ET.fromstring(content)
            metadata["xml_valid"] = True
            metadata["root_tag"] = root.tag
            
            # Streamworks-specific elements
            extractors = {
                "stream_name": [".//StreamName", ".//Name"],
                "job_type": [".//Type", ".//JobType"],
                "source_agent": [".//SourceAgent", ".//Source//Agent"],
                "target_agent": [".//TargetAgent", ".//Target//Agent"],
                "schedule": [".//Schedule", ".//StartTime"],
                "description": [".//Description"]
            }
            
            for key, xpaths in extractors.items():
                for xpath in xpaths:
                    elem = root.find(xpath)
                    if elem is not None and elem.text:
                        metadata[key] = elem.text[:500]
                        break
            
        except ET.ParseError:
            pass
        
        return metadata
    
    def _extract_json_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from JSON documents"""
        metadata = {"json_valid": False}
        
        try:
            data = json.loads(content)
            metadata["json_valid"] = True
            
            if isinstance(data, dict):
                metadata["keys"] = list(data.keys())[:10]
                metadata["key_count"] = len(data)
            elif isinstance(data, list):
                metadata["item_count"] = len(data)
                
        except json.JSONDecodeError:
            pass
        
        return metadata
    
    def parse_with_chunks(
        self,
        content: bytes,
        filename: str,
        chunk_size: int = 2000,
        overlap: int = 200
    ) -> ParsedDocument:
        """
        Parse and chunk document
        """
        doc = self.parse(content, filename)
        
        if len(doc.content) <= chunk_size:
            doc.chunks = [doc.content]
            return doc
        
        chunks = []
        start = 0
        text = doc.content
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Find good break point
            break_point = self._find_break_point(text, start, end)
            chunks.append(text[start:break_point])
            start = break_point - overlap
        
        doc.chunks = chunks
        return doc
    
    def _find_break_point(self, text: str, start: int, end: int) -> int:
        """Find natural break point for chunking"""
        search_start = start + (end - start) // 2
        
        # Priority: paragraph > line > sentence > space
        for delimiter in ['\n\n', '\n', '. ', ' ']:
            pos = text.rfind(delimiter, search_start, end)
            if pos != -1:
                return pos + len(delimiter)
        
        return end
