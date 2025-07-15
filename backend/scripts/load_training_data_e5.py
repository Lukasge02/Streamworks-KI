#!/usr/bin/env python3
"""
Load all training data into ChromaDB with E5 embeddings
"""
import os
import sys
import glob
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions

class E5EmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model):
        self.model = model
    
    def __call__(self, input):
        # Add E5 prefix for passages
        prefixed_texts = [f'passage: {text}' for text in input]
        embeddings = self.model.encode(prefixed_texts)
        return embeddings.tolist()

def load_training_data():
    print('🔧 LOADING ALL TRAINING DATA INTO ChromaDB')
    print('=' * 60)
    
    # Initialize embedding model
    print('1. Loading multilingual-e5-large...')
    embedding_model = SentenceTransformer('intfloat/multilingual-e5-large')
    print(f'✅ Model dimension: {embedding_model.get_sentence_embedding_dimension()}')
    
    # Initialize ChromaDB
    print('\n2. Connecting to ChromaDB...')
    client = chromadb.PersistentClient(
        path='./data/vector_db_e5',
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    try:
        collection = client.get_collection('streamworks_e5')
        print(f'✅ Found existing collection with {collection.count()} documents')
    except:
        embedding_fn = E5EmbeddingFunction(embedding_model)
        collection = client.create_collection(
            name='streamworks_e5',
            embedding_function=embedding_fn
        )
        print('✅ Created new collection')
    
    # Load all training files
    print('\n3. Loading training data files...')
    training_files = glob.glob('data/training_data/optimized/help_data/*.md')
    print(f'📁 Found {len(training_files)} training files')
    
    total_chunks = 0
    
    for i, file_path in enumerate(training_files, 1):
        print(f'\n📄 Processing {i}/{len(training_files)}: {os.path.basename(file_path)}')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Clean content: Remove metadata header and statistics
        lines = content.split('\n')
        clean_lines = []
        skip_metadata = True
        
        for line in lines:
            # Skip until we find content after metadata
            if skip_metadata:
                if line.startswith('##') or (line.strip() and not line.startswith('#') and not line.startswith('**') and not line.startswith('---')):
                    skip_metadata = False
                    clean_lines.append(line)
            else:
                # Skip statistics sections
                if not any(skip_word in line for skip_word in ['📏 Statistiken', '📊 Statistiken', 'Wortanzahl', 'Zeilen', 'Geschätzte Lesezeit', '*Dieses Dokument wurde automatisch']):
                    clean_lines.append(line)
        
        content = '\n'.join(clean_lines)
        print(f'   Content cleaned: {len(content)} chars')
        
        # PRODUCTION-GRADE chunking: Separate Q&A pairs + general content
        chunks = []
        lines = content.split('\n')
        
        # First pass: Extract Q&A pairs separately
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for Q&A patterns
            if line.startswith('### ❓') and i + 1 < len(lines):
                # Extract question
                question = line.replace('### ❓', '').strip()
                
                # Look for answer on next line(s)
                answer_lines = []
                j = i + 1
                while j < len(lines) and not lines[j].startswith('###') and not lines[j].startswith('##'):
                    if lines[j].strip():
                        answer_lines.append(lines[j].strip())
                    j += 1
                
                if answer_lines:
                    # Create dedicated Q&A chunk
                    qa_chunk = f"FRAGE: {question}\nANTWORT: {' '.join(answer_lines)}"
                    chunks.append(qa_chunk)
                    print(f"   Q&A extracted: {question}")
                
                i = j
            else:
                i += 1
        
        # Second pass: Regular chunking for remaining content
        current_chunk = []
        current_size = 0
        
        for line in lines:
            # Skip Q&A sections (already processed)
            if line.startswith('### ❓'):
                # Skip this Q&A block
                continue
            
            # Start new chunk on headers
            if line.startswith('#') and current_size > 200:
                if current_chunk:
                    chunk_text = '\n'.join(current_chunk)
                    if len(chunk_text.strip()) > 50 and not any(qa in chunk_text for qa in ['FRAGE:', 'ANTWORT:']):
                        chunks.append(chunk_text)
                    current_chunk = [line]
                    current_size = len(line)
            else:
                current_chunk.append(line)
                current_size += len(line)
                
                # Create chunk if size limit reached
                if current_size > 600:  # Smaller chunks for better precision
                    chunk_text = '\n'.join(current_chunk)
                    if len(chunk_text.strip()) > 50 and not any(qa in chunk_text for qa in ['FRAGE:', 'ANTWORT:']):
                        chunks.append(chunk_text)
                    current_chunk = []
                    current_size = 0
        
        # Add last chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            if len(chunk_text.strip()) > 50 and not any(qa in chunk_text for qa in ['FRAGE:', 'ANTWORT:']):
                chunks.append(chunk_text)
        
        print(f'   Created {len(chunks)} chunks')
        
        # Add chunks to collection
        for j, chunk in enumerate(chunks):
            collection.add(
                documents=[chunk],
                metadatas=[{
                    'filename': os.path.basename(file_path),
                    'source': file_path,
                    'chunk_id': j,
                    'type': 'help_data'
                }],
                ids=[f'{os.path.basename(file_path)}_chunk_{j}']
            )
        
        total_chunks += len(chunks)
        print(f'   ✅ Added {len(chunks)} chunks')
    
    print(f'\n✅ COMPLETE! Loaded {total_chunks} chunks from {len(training_files)} files')
    print(f'📊 Collection now has {collection.count()} documents total')
    
    # Test queries
    print('\n4. Testing key queries...')
    test_queries = [
        'Wer ist Arne Thiele?',
        'Was ist StreamWorks?',
        'Welche Passwort-Richtlinien gibt es?'
    ]
    
    for query in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=1
        )
        
        print(f'\n❓ Query: {query}')
        if results['documents'][0]:
            doc = results['documents'][0][0]
            print(f'✅ Found: {doc[:150]}...')
        else:
            print('❌ No results')

if __name__ == '__main__':
    load_training_data()