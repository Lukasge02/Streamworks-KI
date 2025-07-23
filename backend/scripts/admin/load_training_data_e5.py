#!/usr/bin/env python3
"""
Load all training data into ChromaDB with E5 embeddings
"""
import os
import sys
import glob
import logging
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from chromadb.utils import embedding_functions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class E5EmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model):
        self.model = model
    
    def __call__(self, input):
        # Add E5 prefix for passages
        prefixed_texts = [f'passage: {text}' for text in input]
        embeddings = self.model.encode(prefixed_texts)
        return embeddings.tolist()

def load_training_data():
    """Load training data with comprehensive error handling"""
    try:
        logger.info('🔧 LOADING ALL TRAINING DATA INTO ChromaDB')
        logger.info('=' * 60)
        
        # Initialize embedding model
        logger.info('1. Loading multilingual-e5-large...')
        try:
            embedding_model = SentenceTransformer('intfloat/multilingual-e5-large')
            logger.info(f'✅ Model dimension: {embedding_model.get_sentence_embedding_dimension()}')
        except Exception as e:
            logger.error(f'❌ Failed to load embedding model: {e}')
            raise
    
        # Initialize ChromaDB
        logger.info('\n2. Connecting to ChromaDB...')
        try:
            # Ensure directory exists
            vector_db_path = Path('./data/vector_db_e5')
            vector_db_path.mkdir(parents=True, exist_ok=True)
            
            client = chromadb.PersistentClient(
                path=str(vector_db_path),
                settings=Settings(anonymized_telemetry=False)
            )
        except Exception as e:
            logger.error(f'❌ Failed to connect to ChromaDB: {e}')
            raise
    
        # Get or create collection
        try:
            collection = client.get_collection('streamworks_e5')
            logger.info(f'✅ Found existing collection with {collection.count()} documents')
        except Exception as e:
            logger.info(f'Collection not found, creating new one: {e}')
            try:
                embedding_fn = E5EmbeddingFunction(embedding_model)
                collection = client.create_collection(
                    name='streamworks_e5',
                    embedding_function=embedding_fn
                )
                logger.info('✅ Created new collection')
            except Exception as create_error:
                logger.error(f'❌ Failed to create collection: {create_error}')
                raise
    
        # Load all training files
        logger.info('\n3. Loading training data files...')
        training_pattern = 'data/training_data/optimized/help_data/*.md'
        training_files = glob.glob(training_pattern)
        
        if not training_files:
            logger.warning(f'⚠️ No training files found with pattern: {training_pattern}')
            # Try alternative patterns
            alternative_patterns = [
                'data/training_data/*.md',
                'data/documents/*.md',
                'backend/data/training_data/*.md'
            ]
            for pattern in alternative_patterns:
                training_files = glob.glob(pattern)
                if training_files:
                    logger.info(f'📁 Found {len(training_files)} files with pattern: {pattern}')
                    break
        
        if not training_files:
            logger.error('❌ No training files found in any location')
            raise FileNotFoundError('No training data files found')
        
        logger.info(f'📁 Found {len(training_files)} training files')
    
    total_chunks = 0
    
    for i, file_path in enumerate(training_files, 1):
        logger.info(f'\n📄 Processing {i}/{len(training_files)}: {os.path.basename(file_path)}')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f'❌ Failed to read file {file_path}: {e}')
            continue
        
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
        logger.info(f'   Content cleaned: {len(content)} chars')
        
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
                    logger.info(f"   Q&A extracted: {question}")
                
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
        
        logger.info(f'   Created {len(chunks)} chunks')
        
        # Add chunks to collection
        try:
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
        except Exception as e:
            logger.error(f'❌ Failed to add chunks for {file_path}: {e}')
            continue
        
        total_chunks += len(chunks)
        logger.info(f'   ✅ Added {len(chunks)} chunks')
    
        logger.info(f'\n✅ COMPLETE! Loaded {total_chunks} chunks from {len(training_files)} files')
        logger.info(f'📊 Collection now has {collection.count()} documents total')
    
        # Test queries
        logger.info('\n4. Testing key queries...')
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
        
        logger.info(f'\n❓ Query: {query}')
        if results['documents'][0]:
            doc = results['documents'][0][0]
            logger.info(f'✅ Found: {doc[:150]}...')
        else:
            logger.warning('❌ No results')
            
    except Exception as e:
        logger.error(f'❌ Training data loading failed: {e}')
        raise

if __name__ == '__main__':
    try:
        load_training_data()
    except Exception as e:
        logger.error(f'❌ Script execution failed: {e}')
        sys.exit(1)