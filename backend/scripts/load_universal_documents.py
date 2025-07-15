#!/usr/bin/env python3
"""
🎯 UNIVERSAL DOCUMENT LOADER
Loads ANY document type into ChromaDB with robust chunking
Works with PDFs, Word, text files, markdown, etc.
"""
import os
import sys
import glob
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions
import re
from typing import List, Dict

class UniversalEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model):
        self.model = model
    
    def __call__(self, input):
        # Add E5 prefix for passages
        prefixed_texts = [f'passage: {text}' for text in input]
        embeddings = self.model.encode(prefixed_texts)
        return embeddings.tolist()

class UniversalDocumentLoader:
    """Universal document loader for any content type"""
    
    def __init__(self):
        self.embedding_model = None
        self.client = None
        self.collection = None
        
    def load_documents(self):
        """Load all documents with universal chunking strategy"""
        print('🎯 UNIVERSAL DOCUMENT LOADER - PRODUCTION READY')
        print('=' * 70)
        
        # Initialize embedding model
        print('1. Loading multilingual-e5-large...')
        self.embedding_model = SentenceTransformer('intfloat/multilingual-e5-large')
        print(f'✅ Model dimension: {self.embedding_model.get_sentence_embedding_dimension()}')
        
        # Initialize ChromaDB
        print('\n2. Connecting to ChromaDB...')
        self.client = chromadb.PersistentClient(
            path='./data/vector_db_universal',
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create new collection
        try:
            self.client.delete_collection('streamworks_universal')
            print('✅ Deleted old collection')
        except:
            pass
        
        embedding_fn = UniversalEmbeddingFunction(self.embedding_model)
        self.collection = self.client.create_collection(
            name='streamworks_universal',
            embedding_function=embedding_fn
        )
        print('✅ Created universal collection')
        
        # Load all training files
        print('\n3. Loading training data with universal chunking...')
        training_files = glob.glob('data/training_data/optimized/help_data/*.md')
        print(f'📁 Found {len(training_files)} training files')
        
        total_chunks = 0
        
        for i, file_path in enumerate(training_files, 1):
            print(f'\n📄 Processing {i}/{len(training_files)}: {os.path.basename(file_path)}')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Universal content processing
            processed_content = self._process_universal_content(content)
            print(f'   Content processed: {len(processed_content)} chars')
            
            # Universal chunking
            chunks = self._universal_chunking(processed_content)
            print(f'   Created {len(chunks)} universal chunks')
            
            # Add chunks to collection
            for j, chunk in enumerate(chunks):
                chunk_id = f'{os.path.basename(file_path)}_chunk_{j}'
                
                self.collection.add(
                    documents=[chunk['content']],
                    metadatas=[{
                        'filename': os.path.basename(file_path),
                        'source': file_path,
                        'chunk_id': j,
                        'chunk_type': chunk['type'],
                        'chunk_size': len(chunk['content'])
                    }],
                    ids=[chunk_id]
                )
            
            total_chunks += len(chunks)
            print(f'   ✅ Added {len(chunks)} chunks')
        
        print(f'\n✅ COMPLETE! Loaded {total_chunks} chunks from {len(training_files)} files')
        print(f'📊 Universal collection now has {self.collection.count()} documents total')
        
        # Test universal queries
        self._test_universal_queries()
    
    def _process_universal_content(self, content: str) -> str:
        """Process any document content universally"""
        # Remove common metadata patterns (but keep content)
        lines = content.split('\n')
        processed_lines = []
        
        skip_patterns = [
            r'^#\s*Training Data',
            r'^\*\*Automatisch generiert',
            r'^\*\*Konvertiert am',
            r'^\*\*Typ\*\*:',
            r'^---$',
            r'###\s*📏\s*Statistiken',
            r'###\s*📊\s*Statistiken',
            r'- \*\*Wortanzahl\*\*',
            r'- \*\*Zeilen\*\*',
            r'- \*\*Geschätzte Lesezeit\*\*',
            r'\*Dieses Dokument wurde automatisch'
        ]
        
        for line in lines:
            line = line.strip()
            
            # Skip metadata lines
            if any(re.match(pattern, line) for pattern in skip_patterns):
                continue
            
            # Skip empty lines and very short lines
            if len(line) < 3:
                continue
            
            # Clean line
            cleaned_line = self._clean_line(line)
            if cleaned_line:
                processed_lines.append(cleaned_line)
        
        return '\n'.join(processed_lines)
    
    def _clean_line(self, line: str) -> str:
        """Clean individual line universally"""
        # Remove markdown artifacts that don't add value
        line = re.sub(r'#{1,6}\s*', '', line)  # Remove header markers
        line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)  # Remove bold markers but keep content
        line = re.sub(r'`(.*?)`', r'\1', line)  # Remove code markers but keep content
        line = re.sub(r'📏|📊|🔍|🌐|🎯|⚙️|❓', '', line)  # Remove emojis
        
        # Clean up whitespace
        line = re.sub(r'\s+', ' ', line).strip()
        
        return line
    
    def _universal_chunking(self, content: str) -> List[Dict]:
        """Universal chunking strategy that works with any document structure"""
        chunks = []
        
        # Strategy 1: Semantic chunking by sections
        sections = self._split_by_sections(content)
        
        for section in sections:
            if len(section.strip()) < 30:
                continue
            
            # If section is small enough, use as single chunk
            if len(section) <= 500:
                chunks.append({
                    'content': section.strip(),
                    'type': 'section'
                })
            else:
                # Split large sections into smaller chunks
                sub_chunks = self._split_large_section(section)
                chunks.extend(sub_chunks)
        
        # Strategy 2: Extract Q&A patterns if they exist (flexible)
        qa_chunks = self._extract_qa_patterns(content)
        chunks.extend(qa_chunks)
        
        # Strategy 3: Extract key-value patterns
        kv_chunks = self._extract_key_value_patterns(content)
        chunks.extend(kv_chunks)
        
        return chunks
    
    def _split_by_sections(self, content: str) -> List[str]:
        """Split content by natural sections"""
        # Try different section markers
        section_patterns = [
            r'\n#{1,3}\s+[^\n]+\n',  # Markdown headers
            r'\n[A-Z][A-Z\s]{3,}:\n',  # ALL CAPS sections
            r'\n\d+\.\s+[^\n]+\n',   # Numbered sections
            r'\n[A-Z][^.!?]*[.!?]\s*\n'  # Sentence boundaries
        ]
        
        for pattern in section_patterns:
            sections = re.split(pattern, content)
            if len(sections) > 2:  # Found meaningful splits
                return [s.strip() for s in sections if s.strip()]
        
        # Fallback: split by paragraphs
        paragraphs = content.split('\n\n')
        return [p.strip() for p in paragraphs if len(p.strip()) > 20]
    
    def _split_large_section(self, section: str) -> List[Dict]:
        """Split large sections into manageable chunks"""
        chunks = []
        sentences = re.split(r'[.!?]\s+', section)
        
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_size += len(sentence)
            
            # If chunk is large enough, save it
            if current_size > 300 and len(current_chunk) >= 2:
                chunk_text = '. '.join(current_chunk) + '.'
                chunks.append({
                    'content': chunk_text,
                    'type': 'paragraph'
                })
                current_chunk = []
                current_size = 0
        
        # Add remaining content
        if current_chunk:
            chunk_text = '. '.join(current_chunk)
            if not chunk_text.endswith('.'):
                chunk_text += '.'
            chunks.append({
                'content': chunk_text,
                'type': 'paragraph'
            })
        
        return chunks
    
    def _extract_qa_patterns(self, content: str) -> List[Dict]:
        """Extract Q&A patterns if they exist (flexible)"""
        qa_chunks = []
        
        # Pattern 1: ❓ Question / A: Answer
        qa_pattern1 = r'❓\s*([^?]+\?)\s*A:\s*([^\n❓]+)'
        matches = re.findall(qa_pattern1, content, re.MULTILINE | re.DOTALL)
        
        for question, answer in matches:
            qa_text = f"FRAGE: {question.strip()}\nANTWORT: {answer.strip()}"
            qa_chunks.append({
                'content': qa_text,
                'type': 'qa_pair'
            })
        
        # Pattern 2: Question? Answer (without markers)
        qa_pattern2 = r'([^.!?\n]+\?)\s*([^.!?\n]*[.!])'
        matches = re.findall(qa_pattern2, content)
        
        for question, answer in matches:
            if len(question) > 10 and len(answer) > 10:
                qa_text = f"FRAGE: {question.strip()}\nANTWORT: {answer.strip()}"
                qa_chunks.append({
                    'content': qa_text,
                    'type': 'implicit_qa'
                })
        
        return qa_chunks[:10]  # Limit to avoid duplicates
    
    def _extract_key_value_patterns(self, content: str) -> List[Dict]:
        """Extract key-value information patterns"""
        kv_chunks = []
        
        # Pattern: Key: Value
        kv_pattern = r'([A-Za-zÄÖÜäöüß\s]{3,20}):\s*([^\n:]{10,100})'
        matches = re.findall(kv_pattern, content)
        
        for key, value in matches:
            key = key.strip()
            value = value.strip()
            
            # Filter out junk
            if len(key) > 3 and len(value) > 5:
                kv_text = f"{key}: {value}"
                kv_chunks.append({
                    'content': kv_text,
                    'type': 'key_value'
                })
        
        return kv_chunks[:5]  # Limit to most important
    
    def _test_universal_queries(self):
        """Test the universal system with key queries"""
        print('\n4. Testing universal queries...')
        
        test_queries = [
            'Wer ist für Linux zuständig?',
            'Was ist StreamWorks?',
            'Welche Passwort-Richtlinien gibt es?',
            'Wie erstelle ich einen Job?',
            'Was kostet StreamWorks?'
        ]
        
        for query in test_queries:
            results = self.collection.query(
                query_texts=[query],
                n_results=3
            )
            
            print(f'\n❓ Query: {query}')
            if results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    print(f'   {i+1}. {doc[:80]}...')
            else:
                print('   ❌ No results')

def main():
    loader = UniversalDocumentLoader()
    loader.load_documents()

if __name__ == '__main__':
    main()