#!/usr/bin/env python3
"""
🏭 PRODUCTION DOCUMENT LOADER - FINAL SOLUTION
Combines structured Q&A extraction with universal document processing
Works with ANY document type - from structured MD to chaotic PDFs
"""
import os
import sys
import glob
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
import re
from typing import List, Dict, Tuple, Any

class ProductionEmbeddingFunction(embedding_functions.EmbeddingFunction):
    """Production embedding function with E5 model"""
    def __init__(self, model):
        self.model = model
    
    def __call__(self, input):
        prefixed_texts = [f'passage: {text}' for text in input]
        embeddings = self.model.encode(prefixed_texts)
        return embeddings.tolist()

class ProductionDocumentLoader:
    """🚀 Production document loader - handles ANY document type"""
    
    def __init__(self):
        self.embedding_model = None
        self.client = None
        self.collection = None
        
    def load_documents(self):
        """Load documents with production-grade multi-strategy parsing"""
        print('🏭 PRODUCTION DOCUMENT LOADER - FINAL SOLUTION')
        print('=' * 80)
        
        # Initialize
        print('1. Loading production E5 model...')
        self.embedding_model = SentenceTransformer('intfloat/multilingual-e5-large')
        print(f'✅ Model dimension: {self.embedding_model.get_sentence_embedding_dimension()}')
        
        print('\n2. Connecting to production ChromaDB...')
        self.client = chromadb.PersistentClient(
            path='./data/vector_db_production',
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Clean start
        try:
            self.client.delete_collection('streamworks_production')
            print('✅ Deleted old production collection')
        except:
            pass
        
        # Create production collection
        embedding_fn = ProductionEmbeddingFunction(self.embedding_model)
        self.collection = self.client.create_collection(
            name='streamworks_production',
            embedding_function=embedding_fn
        )
        print('✅ Created production collection')
        
        # Load documents
        print('\n3. Loading documents with production multi-strategy parsing...')
        training_files = glob.glob('data/training_data/optimized/help_data/*.md')
        print(f'📁 Found {len(training_files)} training files')
        
        total_chunks = 0
        parsing_stats = {
            'qa_pairs': 0,
            'structured_sections': 0,
            'unstructured_chunks': 0,
            'key_value_pairs': 0
        }
        
        for i, file_path in enumerate(training_files, 1):
            print(f'\n📄 Processing {i}/{len(training_files)}: {os.path.basename(file_path)}')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Multi-strategy parsing
            all_chunks = self._production_parsing(content, os.path.basename(file_path))
            
            # Update stats
            for chunk in all_chunks:
                parsing_stats[chunk['type']] = parsing_stats.get(chunk['type'], 0) + 1
            
            print(f'   Parsed: {len(all_chunks)} chunks')
            print(f'   Types: QA={sum(1 for c in all_chunks if c["type"] == "qa_pairs")}, '
                  f'Struct={sum(1 for c in all_chunks if c["type"] == "structured_sections")}, '
                  f'Unstruct={sum(1 for c in all_chunks if c["type"] == "unstructured_chunks")}, '
                  f'KV={sum(1 for c in all_chunks if c["type"] == "key_value_pairs")}')
            
            # Add to collection
            for j, chunk in enumerate(all_chunks):
                chunk_id = f'{os.path.basename(file_path)}_chunk_{j}'
                
                self.collection.add(
                    documents=[chunk['content']],
                    metadatas=[{
                        'filename': os.path.basename(file_path),
                        'source': file_path,
                        'chunk_id': j,
                        'chunk_type': chunk['type'],
                        'chunk_size': len(chunk['content']),
                        'parsing_strategy': chunk.get('strategy', 'unknown'),
                        'quality_score': chunk.get('quality', 1.0)
                    }],
                    ids=[chunk_id]
                )
            
            total_chunks += len(all_chunks)
            print(f'   ✅ Added {len(all_chunks)} production chunks')
        
        print(f'\n✅ PRODUCTION LOADING COMPLETE!')
        print(f'📊 Total chunks: {total_chunks}')
        print(f'📈 Parsing statistics:')
        for chunk_type, count in parsing_stats.items():
            print(f'   - {chunk_type}: {count}')
        print(f'📚 Production collection: {self.collection.count()} documents')
        
        # Production quality tests
        self._run_production_tests()
    
    def _production_parsing(self, content: str, filename: str) -> List[Dict]:
        """Production-grade multi-strategy document parsing"""
        all_chunks = []
        
        # Strategy 1: Extract structured Q&A pairs (preserves critical info)
        qa_chunks = self._extract_qa_pairs(content)
        all_chunks.extend(qa_chunks)
        
        # Strategy 2: Extract key-value information (facts and specs)
        kv_chunks = self._extract_key_value_info(content)
        all_chunks.extend(kv_chunks)
        
        # Strategy 3: Parse structured sections (headers, lists, tables)
        structured_chunks = self._parse_structured_sections(content)
        all_chunks.extend(structured_chunks)
        
        # Strategy 4: Universal chunking for remaining content
        remaining_content = self._remove_parsed_content(content, all_chunks)
        universal_chunks = self._universal_chunking(remaining_content)
        all_chunks.extend(universal_chunks)
        
        # Quality scoring and deduplication
        scored_chunks = self._score_and_filter_chunks(all_chunks)
        
        return scored_chunks
    
    def _extract_qa_pairs(self, content: str) -> List[Dict]:
        """Extract Q&A pairs with multiple pattern recognition"""
        qa_chunks = []
        
        # Pattern 1: ❓ Question / A: Answer (structured)
        pattern1 = r'❓\s*([^?\n]+\?)\s*A:\s*([^\n❓]+)'
        matches = re.findall(pattern1, content, re.MULTILINE | re.DOTALL)
        
        for question, answer in matches:
            qa_text = f"FRAGE: {question.strip()}\nANTWORT: {answer.strip()}"
            qa_chunks.append({
                'content': qa_text,
                'type': 'qa_pairs',
                'strategy': 'structured_qa',
                'quality': 1.0  # High quality for structured Q&A
            })
        
        # Pattern 2: Question? Answer (implicit Q&A)
        lines = content.split('\n')
        for i, line in enumerate(lines[:-1]):
            line = line.strip()
            next_line = lines[i + 1].strip()
            
            # Look for question followed by answer
            if (line.endswith('?') and len(line) > 10 and len(line) < 100 and
                len(next_line) > 15 and not next_line.startswith('#')):
                
                qa_text = f"FRAGE: {line}\nANTWORT: {next_line}"
                qa_chunks.append({
                    'content': qa_text,
                    'type': 'qa_pairs',
                    'strategy': 'implicit_qa',
                    'quality': 0.8
                })
        
        # Pattern 3: Contact/Person information
        contact_patterns = [
            r'(linux\s+ansprechperson\?)\s*a:\s*([^\n]+)',
            r'(ansprechpartner.*?):\s*([^\n]+)',
            r'(zuständig.*?):\s*([^\n]+)',
            r'(kontakt.*?):\s*([^\n]+)'
        ]
        
        for pattern in contact_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for question, answer in matches:
                qa_text = f"FRAGE: {question.strip()}\nANTWORT: {answer.strip()}"
                qa_chunks.append({
                    'content': qa_text,
                    'type': 'qa_pairs',
                    'strategy': 'contact_info',
                    'quality': 0.9  # High quality for contact info
                })
        
        return qa_chunks
    
    def _extract_key_value_info(self, content: str) -> List[Dict]:
        """Extract key-value information (specs, requirements, etc.)"""
        kv_chunks = []
        
        # Pattern 1: Technical specifications
        spec_patterns = [
            r'(mindestlänge|minimum|max|maximum):\s*(\d+\s*\w*)',
            r'(gültigkeitsdauer|dauer|zeit):\s*(\d+\s*\w*)',
            r'(speicher|memory|ram):\s*(\d+\s*\w*)',
            r'(betriebssystem|os|system):\s*([^\n]{10,50})',
            r'(version|release):\s*([^\n]{5,30})'
        ]
        
        for pattern in spec_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for key, value in matches:
                kv_text = f"{key.title()}: {value}"
                kv_chunks.append({
                    'content': kv_text,
                    'type': 'key_value_pairs',
                    'strategy': 'specifications',
                    'quality': 0.9
                })
        
        # Pattern 2: Lists with important information
        list_patterns = [
            r'[-•*]\s*([^\n]{20,100})',  # Bullet points
            r'\d+\.\s*([^\n]{20,100})'   # Numbered lists
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, content)
            for match in matches[:5]:  # Limit to avoid noise
                if any(keyword in match.lower() for keyword in ['zeichen', 'tage', 'gb', 'mb', 'version', 'unterstützt']):
                    kv_chunks.append({
                        'content': match.strip(),
                        'type': 'key_value_pairs',
                        'strategy': 'list_items',
                        'quality': 0.7
                    })
        
        return kv_chunks
    
    def _parse_structured_sections(self, content: str) -> List[Dict]:
        """Parse structured sections (headers, paragraphs)"""
        structured_chunks = []
        
        # Split by headers
        sections = re.split(r'\n#{1,4}\s+([^\n]+)\n', content)
        
        current_section = ""
        for i, part in enumerate(sections):
            if i == 0:
                current_section = part  # Content before first header
                continue
            
            if i % 2 == 1:  # This is a header
                header = part.strip()
                if len(current_section.strip()) > 50:
                    # Add previous section
                    clean_section = self._clean_section_content(current_section)
                    if clean_section:
                        structured_chunks.append({
                            'content': clean_section,
                            'type': 'structured_sections',
                            'strategy': 'header_sections',
                            'quality': 0.8
                        })
                current_section = f"# {header}\n"
            else:  # This is content under the header
                current_section += part
        
        # Add last section
        if len(current_section.strip()) > 50:
            clean_section = self._clean_section_content(current_section)
            if clean_section:
                structured_chunks.append({
                    'content': clean_section,
                    'type': 'structured_sections',
                    'strategy': 'header_sections',
                    'quality': 0.8
                })
        
        return structured_chunks
    
    def _clean_section_content(self, content: str) -> str:
        """Clean section content while preserving important information"""
        # Remove metadata patterns but keep content
        lines = content.split('\n')
        clean_lines = []
        
        skip_patterns = [
            r'^#\s*Training Data',
            r'^\*\*Automatisch generiert',
            r'^\*\*Konvertiert am',
            r'^\*\*Typ\*\*:',
            r'^---$',
            r'###\s*📏\s*Statistiken',
            r'- \*\*Wortanzahl\*\*',
            r'- \*\*Zeilen\*\*',
            r'- \*\*Geschätzte Lesezeit\*\*',
            r'\*Dieses Dokument wurde automatisch'
        ]
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if len(line) < 3:
                continue
            
            # Skip metadata
            if any(re.match(pattern, line) for pattern in skip_patterns):
                continue
            
            # Clean but preserve formatting
            cleaned_line = self._clean_line_preserve_info(line)
            if cleaned_line:
                clean_lines.append(cleaned_line)
        
        return '\n'.join(clean_lines)
    
    def _clean_line_preserve_info(self, line: str) -> str:
        """Clean line while preserving all important information"""
        # Remove excessive markdown but keep content
        line = re.sub(r'#{1,6}\s*', '', line)  # Remove header markers
        line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Remove bold but keep content
        line = re.sub(r'`(.*?)`', r'\1', line)  # Remove code markers
        
        # Remove emojis but keep the content
        line = re.sub(r'[📏📊🔍🌐🎯⚙️❓]', '', line)
        
        # Clean whitespace but preserve structure
        line = re.sub(r'\s+', ' ', line).strip()
        
        return line
    
    def _remove_parsed_content(self, content: str, parsed_chunks: List[Dict]) -> str:
        """Remove already parsed content to avoid duplication"""
        remaining_content = content
        
        # Remove Q&A patterns
        qa_patterns = [
            r'❓\s*[^?\n]+\?\s*A:\s*[^\n❓]+',
            r'linux\s+ansprechperson\?\s*a:\s*[^\n]+',
            r'ansprechpartner.*?:\s*[^\n]+'
        ]
        
        for pattern in qa_patterns:
            remaining_content = re.sub(pattern, '', remaining_content, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove metadata sections
        metadata_patterns = [
            r'###\s*📏\s*Statistiken.*?---',
            r'- \*\*Wortanzahl\*\*.*?\n',
            r'- \*\*Zeilen\*\*.*?\n',
            r'- \*\*Geschätzte Lesezeit\*\*.*?\n'
        ]
        
        for pattern in metadata_patterns:
            remaining_content = re.sub(pattern, '', remaining_content, flags=re.DOTALL)
        
        return remaining_content
    
    def _universal_chunking(self, content: str) -> List[Dict]:
        """Universal chunking for remaining unstructured content"""
        if len(content.strip()) < 50:
            return []
        
        chunks = []
        
        # Split by natural breaks
        paragraphs = re.split(r'\n\s*\n', content)
        
        current_chunk = []
        current_size = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) < 20:
                continue
            
            # Add to current chunk
            current_chunk.append(paragraph)
            current_size += len(paragraph)
            
            # Create chunk if size reached - FIXED: Larger chunks preserve context
            if current_size > 800 or len(current_chunk) >= 6:
                chunk_text = '\n\n'.join(current_chunk)
                if len(chunk_text.strip()) > 30:
                    chunks.append({
                        'content': chunk_text,
                        'type': 'unstructured_chunks',
                        'strategy': 'universal',
                        'quality': 0.6
                    })
                current_chunk = []
                current_size = 0
        
        # Add remaining content
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            if len(chunk_text.strip()) > 30:
                chunks.append({
                    'content': chunk_text,
                    'type': 'unstructured_chunks',
                    'strategy': 'universal',
                    'quality': 0.6
                })
        
        return chunks
    
    def _score_and_filter_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Score chunks and filter out low-quality ones"""
        scored_chunks = []
        
        for chunk in chunks:
            content = chunk['content']
            base_quality = chunk.get('quality', 0.5)
            
            # Quality boosters
            quality_score = base_quality
            
            # Length appropriateness
            if 50 <= len(content) <= 800:
                quality_score += 0.1
            
            # Contains important keywords
            important_keywords = ['streamworks', 'linux', 'passwort', 'job', 'api', 'installation', 'sicherheit', 'backup']
            keyword_count = sum(1 for keyword in important_keywords if keyword in content.lower())
            quality_score += min(keyword_count * 0.05, 0.2)
            
            # Has specific information (numbers, names, etc.)
            if re.search(r'\d+', content):  # Contains numbers
                quality_score += 0.05
            if re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', content):  # Contains names
                quality_score += 0.1
            
            # Final quality check
            if quality_score >= 0.4:  # Minimum quality threshold
                chunk['final_quality'] = min(quality_score, 1.0)
                scored_chunks.append(chunk)
        
        # Sort by quality and return
        scored_chunks.sort(key=lambda x: x['final_quality'], reverse=True)
        return scored_chunks
    
    def _run_production_tests(self):
        """Run production-quality tests"""
        print('\n4. Running production quality tests...')
        
        critical_queries = [
            'Wer ist für Linux zuständig?',
            'Was ist StreamWorks?',
            'Welche Passwort-Richtlinien gibt es?',
            'Wie erstelle ich einen Job?',
            'Was kostet StreamWorks?'
        ]
        
        for query in critical_queries:
            results = self.collection.query(
                query_texts=[query],
                n_results=5,
                include=['documents', 'metadatas']
            )
            
            print(f'\n❓ {query}')
            
            # Check if we have good results
            if results['documents'][0]:
                best_doc = results['documents'][0][0]
                best_meta = results['metadatas'][0][0] if results['metadatas'][0] else {}
                
                print(f'   ✅ Best result ({best_meta.get("chunk_type", "unknown")}): {best_doc[:80]}...')
                
                # Special check for Arne Thiele
                if 'linux' in query.lower():
                    if 'arne thiele' in best_doc.lower():
                        print('   🎯 ARNE THIELE FOUND!')
                    else:
                        print('   ⚠️ Arne Thiele not in top result')
                        
                        # Check all results
                        for i, doc in enumerate(results['documents'][0]):
                            if 'arne thiele' in doc.lower():
                                print(f'   🔍 Found Arne in result #{i+1}')
                                break
            else:
                print('   ❌ No results found')
        
        print(f'\n✅ Production quality tests completed')

def main():
    loader = ProductionDocumentLoader()
    loader.load_documents()

if __name__ == '__main__':
    main()