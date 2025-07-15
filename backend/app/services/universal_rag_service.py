"""
🎯 UNIVERSAL RAG SERVICE - PRODUCTION READY
Robustes System für beliebige Dokumenttypen und -strukturen
"""
import logging
import asyncio
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import aiohttp
import json

logger = logging.getLogger(__name__)

@dataclass
class UniversalAnswer:
    """Universal answer structure"""
    question: str
    answer: str
    sources: List[str]
    processing_time: float
    confidence: float
    retrieval_strategies: List[str]
    context_snippets: List[str]
    
class UniversalRAGService:
    """🚀 Universal RAG Service - Works with ANY document structure"""
    
    def __init__(self):
        self.embedding_model = None
        self.chromadb_client = None
        self.collection = None
        self.is_ready = False
        self.executor = ThreadPoolExecutor(max_workers=6, thread_name_prefix="UniversalRAG")
        
        # Production-grade configuration
        self.config = {
            "embedding_model": "intfloat/multilingual-e5-large",
            "chromadb_path": "./data/vector_db_universal",
            "collection_name": "streamworks_universal",
            "mistral_model": "mistral:7b-instruct",
            "ollama_url": "http://localhost:11434",
            "chunk_size": 400,  # Smaller chunks for precision
            "chunk_overlap": 100,  # Overlap for context continuity
            "top_k_semantic": 5,  # More candidates for semantic search
            "top_k_keyword": 3,   # Additional keyword matches
            "max_context_length": 1500,  # Larger context for complex queries
            "temperature": 0.05,  # Ultra-low for factual accuracy
            "timeout": 15,
            "min_confidence_threshold": 0.6
        }
        
        logger.info("🎯 Universal RAG Service initialized for production")
    
    async def initialize(self):
        """Initialize the universal system"""
        try:
            logger.info("🚀 Initializing Universal RAG System...")
            
            # 1. Load embedding model
            logger.info("📊 Loading E5 embedding model...")
            self.embedding_model = SentenceTransformer(self.config["embedding_model"])
            
            # 2. Initialize ChromaDB
            logger.info("📚 Connecting to ChromaDB...")
            self.chromadb_client = chromadb.PersistentClient(
                path=self.config["chromadb_path"],
                settings=Settings(anonymized_telemetry=False)
            )
            
            # 3. Get or create collection
            try:
                self.collection = self.chromadb_client.get_collection(
                    name=self.config["collection_name"]
                )
                doc_count = self.collection.count()
                logger.info(f"📄 Found {doc_count} documents in universal collection")
            except Exception as e:
                logger.error(f"❌ Collection not found: {e}")
                raise ValueError("Universal ChromaDB collection not found - load documents first")
            
            # 4. Test Mistral connection
            await self._test_mistral()
            
            self.is_ready = True
            logger.info("✅ Universal RAG System ready!")
            
        except Exception as e:
            logger.error(f"❌ Universal RAG initialization failed: {e}")
            raise
    
    async def ask(self, question: str) -> UniversalAnswer:
        """Universal Q&A with multiple retrieval strategies"""
        if not self.is_ready:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            logger.info(f"🔍 Processing universal query: '{question}'")
            
            # 1. Multiple parallel retrieval strategies
            retrieval_results = await self._multi_strategy_retrieval(question)
            
            # 2. Merge and rank all results
            merged_docs = self._merge_retrieval_results(retrieval_results)
            
            # 3. Build robust context from merged results
            context = self._build_universal_context(merged_docs, question)
            
            # 4. Generate answer with production-grade prompting
            answer = await self._generate_universal_answer(question, context)
            
            # 5. Calculate confidence and quality metrics
            confidence = self._calculate_universal_confidence(answer, merged_docs, question)
            
            processing_time = time.time() - start_time
            
            result = UniversalAnswer(
                question=question,
                answer=answer,
                sources=self._extract_sources(merged_docs),
                processing_time=round(processing_time, 2),
                confidence=confidence,
                retrieval_strategies=list(retrieval_results.keys()),
                context_snippets=self._extract_context_snippets(merged_docs)
            )
            
            logger.info(f"✅ Universal answer generated in {processing_time:.2f}s | Confidence: {confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Universal RAG failed: {e}")
            raise
    
    async def _multi_strategy_retrieval(self, question: str) -> Dict[str, List[Dict]]:
        """Multiple parallel retrieval strategies for maximum recall"""
        results = {}
        
        # Strategy 1: Semantic search with query expansion
        semantic_queries = self._expand_query(question)
        semantic_docs = []
        for query in semantic_queries:
            docs = await self._semantic_search(query)
            semantic_docs.extend(docs)
        results["semantic"] = self._deduplicate_docs(semantic_docs)
        
        # Strategy 2: Keyword-based search  
        keyword_docs = await self._keyword_search(question)
        results["keyword"] = keyword_docs
        
        # Strategy 3: Fuzzy/partial matching
        fuzzy_docs = await self._fuzzy_search(question)
        results["fuzzy"] = fuzzy_docs
        
        logger.info(f"📊 Retrieval results: semantic={len(results['semantic'])}, keyword={len(results['keyword'])}, fuzzy={len(results['fuzzy'])}")
        
        return results
    
    def _expand_query(self, question: str) -> List[str]:
        """Expand query with synonyms and alternative formulations"""
        expanded = [question]
        
        # German-specific expansions
        expansions = {
            "wer ist": ["wer ist", "ansprechpartner", "zuständig", "verantwortlich"],
            "linux": ["linux", "unix", "server", "system"],
            "passwort": ["passwort", "kennwort", "password", "authentifizierung"],
            "kosten": ["kosten", "preis", "preise", "lizenz", "gebühren"],
            "installation": ["installation", "setup", "einrichtung", "konfiguration"]
        }
        
        question_lower = question.lower()
        for term, synonyms in expansions.items():
            if term in question_lower:
                for synonym in synonyms:
                    if synonym != term:
                        expanded.append(question_lower.replace(term, synonym))
        
        return expanded[:3]  # Limit to avoid too many queries
    
    async def _semantic_search(self, query: str) -> List[Dict]:
        """Enhanced semantic search with E5 embeddings"""
        try:
            # Add E5 query prefix
            query_text = f"query: {query}"
            
            # Get embedding
            loop = asyncio.get_event_loop()
            query_embedding = await loop.run_in_executor(
                self.executor, 
                lambda: self.embedding_model.encode([query_text])[0].tolist()
            )
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=self.config["top_k_semantic"],
                include=['documents', 'metadatas', 'distances']
            )
            
            # Convert to enhanced format
            docs = []
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                distance = results['distances'][0][i] if results['distances'] else 1.0
                
                docs.append({
                    'content': doc,
                    'source': metadata.get('filename', f'doc_{i}'),
                    'relevance': max(0.1, 1.0 - distance),
                    'distance': distance,
                    'strategy': 'semantic',
                    'query': query
                })
            
            return docs
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []
    
    async def _keyword_search(self, question: str) -> List[Dict]:
        """Keyword-based search for exact matches"""
        try:
            # Extract key terms
            keywords = self._extract_keywords(question)
            
            # Search for documents containing keywords
            all_docs = self.collection.get(include=['documents', 'metadatas'])
            
            matching_docs = []
            for i, doc in enumerate(all_docs['documents']):
                doc_lower = doc.lower()
                
                # Score based on keyword matches
                score = 0
                for keyword in keywords:
                    if keyword.lower() in doc_lower:
                        score += 1
                
                if score > 0:
                    metadata = all_docs['metadatas'][i] if all_docs['metadatas'] else {}
                    matching_docs.append({
                        'content': doc,
                        'source': metadata.get('filename', f'doc_{i}'),
                        'relevance': score / len(keywords),
                        'distance': 1.0 - (score / len(keywords)),
                        'strategy': 'keyword',
                        'matches': score
                    })
            
            # Sort by relevance and limit
            matching_docs.sort(key=lambda x: x['relevance'], reverse=True)
            return matching_docs[:self.config["top_k_keyword"]]
            
        except Exception as e:
            logger.error(f"❌ Keyword search failed: {e}")
            return []
    
    async def _fuzzy_search(self, question: str) -> List[Dict]:
        """Fuzzy/partial matching for robustness"""
        try:
            # Extract important terms
            terms = re.findall(r'\b\w{3,}\b', question.lower())
            
            all_docs = self.collection.get(include=['documents', 'metadatas'])
            
            fuzzy_matches = []
            for i, doc in enumerate(all_docs['documents']):
                doc_lower = doc.lower()
                
                # Fuzzy matching score
                matches = 0
                for term in terms:
                    # Exact match
                    if term in doc_lower:
                        matches += 2
                    # Partial match (substring)
                    elif any(term in word for word in doc_lower.split()):
                        matches += 1
                
                if matches > 0:
                    metadata = all_docs['metadatas'][i] if all_docs['metadatas'] else {}
                    fuzzy_matches.append({
                        'content': doc,
                        'source': metadata.get('filename', f'doc_{i}'),
                        'relevance': matches / (len(terms) * 2),  # Normalize
                        'distance': 1.0 - (matches / (len(terms) * 2)),
                        'strategy': 'fuzzy',
                        'matches': matches
                    })
            
            # Sort and limit
            fuzzy_matches.sort(key=lambda x: x['relevance'], reverse=True)
            return fuzzy_matches[:2]  # Fewer fuzzy matches
            
        except Exception as e:
            logger.error(f"❌ Fuzzy search failed: {e}")
            return []
    
    def _extract_keywords(self, question: str) -> List[str]:
        """Extract important keywords from question"""
        # Remove stopwords and extract meaningful terms
        stopwords = {'ist', 'der', 'die', 'das', 'eine', 'ein', 'und', 'oder', 'für', 'von', 'zu', 'in', 'mit', 'auf', 'bei', 'wie', 'was', 'wer', 'wo', 'wann', 'warum'}
        
        words = re.findall(r'\b\w{2,}\b', question.lower())
        keywords = [word for word in words if word not in stopwords and len(word) > 2]
        
        return keywords[:5]  # Limit to most important
    
    def _merge_retrieval_results(self, results: Dict[str, List[Dict]]) -> List[Dict]:
        """Merge and rank results from multiple strategies"""
        all_docs = []
        
        # Add all documents with strategy weights
        strategy_weights = {"semantic": 1.0, "keyword": 0.8, "fuzzy": 0.6}
        
        for strategy, docs in results.items():
            weight = strategy_weights.get(strategy, 0.5)
            for doc in docs:
                doc['weighted_relevance'] = doc['relevance'] * weight
                all_docs.append(doc)
        
        # Deduplicate and sort by weighted relevance
        unique_docs = self._deduplicate_docs(all_docs)
        unique_docs.sort(key=lambda x: x['weighted_relevance'], reverse=True)
        
        return unique_docs[:8]  # Top 8 for context building
    
    def _deduplicate_docs(self, docs: List[Dict]) -> List[Dict]:
        """Remove duplicate documents"""
        seen_content = set()
        unique_docs = []
        
        for doc in docs:
            content_hash = hash(doc['content'][:100])  # Use first 100 chars as hash
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append(doc)
        
        return unique_docs
    
    def _build_universal_context(self, docs: List[Dict], question: str) -> str:
        """Build robust context that works with any document structure"""
        context_parts = []
        total_length = 0
        max_context = self.config["max_context_length"]
        
        # Extract question keywords for relevance filtering
        question_keywords = set(self._extract_keywords(question))
        
        for i, doc in enumerate(docs):
            if total_length >= max_context:
                break
            
            content = doc['content']
            source = doc['source']
            strategy = doc.get('strategy', 'unknown')
            
            # Extract most relevant passages
            relevant_passages = self._extract_relevant_passages(content, question_keywords)
            
            if relevant_passages:
                # Create source block with metadata
                source_block = f"QUELLE ({strategy}): {source}\n{relevant_passages}"
                
                # Check length limit
                if total_length + len(source_block) <= max_context:
                    context_parts.append(source_block)
                    total_length += len(source_block)
                else:
                    # Add partial content if it fits
                    remaining = max_context - total_length
                    if remaining > 100:
                        truncated = source_block[:remaining-20] + "..."
                        context_parts.append(truncated)
                    break
        
        final_context = "\n\n".join(context_parts)
        logger.info(f"📄 Built universal context: {len(final_context)} chars from {len(docs)} docs")
        
        return final_context
    
    def _extract_relevant_passages(self, content: str, keywords: set) -> str:
        """Extract most relevant passages from any document structure"""
        # Split into sentences/lines
        sentences = []
        
        # Try different splitting strategies
        for separator in ['\n', '. ', '! ', '? ']:
            parts = content.split(separator)
            if len(parts) > 1:
                sentences.extend([s.strip() for s in parts if len(s.strip()) > 10])
                break
        
        if not sentences:
            sentences = [content]  # Fallback to full content
        
        # Score sentences by keyword relevance
        scored_sentences = []
        for sentence in sentences:
            if len(sentence) < 20:
                continue
                
            sentence_lower = sentence.lower()
            score = 0
            
            # Keyword matching
            for keyword in keywords:
                if keyword in sentence_lower:
                    score += 2
            
            # Boost sentences with key patterns (flexible)
            boost_patterns = [
                r'\b(ist|sind|werden|wird)\b',  # Definitions
                r'\b(ansprechpartner|zuständig|verantwortlich)\b',  # Contact info
                r'\b(kosten|preis|lizenz)\b',  # Pricing
                r'\b(installation|setup|konfiguration)\b',  # Setup
                r'\b\d+\s*(zeichen|tage|stunden|gb|mb)\b',  # Specific values
            ]
            
            for pattern in boost_patterns:
                if re.search(pattern, sentence_lower):
                    score += 1
            
            if score > 0:
                scored_sentences.append((score, sentence))
        
        # Select best sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        selected = [s[1] for s in scored_sentences[:4]]  # Top 4 sentences
        
        # If no scored sentences, take first few lines
        if not selected:
            lines = content.split('\n')
            selected = [line.strip() for line in lines[:3] if len(line.strip()) > 15]
        
        return '\n'.join(selected)
    
    async def _generate_universal_answer(self, question: str, context: str) -> str:
        """Generate answer with production-grade prompting"""
        try:
            # Ultra-robust prompt for any document type
            prompt = f"""Du bist ein präziser Informations-Assistent. Analysiere die Dokumentation und beantworte die Frage exakt.

KRITISCHE REGEL: Verwende AUSSCHLIESSLICH die bereitgestellte Dokumentation. Erfinde NICHTS!

FRAGE: {question}

VERFÜGBARE DOKUMENTATION:
{context}

ANWEISUNGEN:
- Suche in der Dokumentation nach der exakten Antwort auf die Frage
- Verwende NUR Informationen aus der Dokumentation oben
- Wenn die Information TEILWEISE vorhanden ist, gib die verfügbaren Details an
- Wenn die Information NICHT vorhanden ist, sage: "Diese Information ist in der Dokumentation nicht verfügbar"
- Antworte präzise und direkt ohne Umschweife
- Ignoriere irrelevante Textteile
- Fokussiere auf die kernfrage

ANTWORT (ausschließlich basierend auf obiger Dokumentation):"""

            # Generate with optimized parameters
            payload = {
                "model": self.config["mistral_model"],
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config["temperature"],
                    "top_p": 0.95,
                    "max_tokens": 300,
                    "repeat_penalty": 1.05,
                    "stop": ["FRAGE:", "ANWEISUNGEN:", "DOKUMENTATION:"],
                    "num_ctx": 4096
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config['ollama_url']}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config["timeout"])
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        answer = result.get("response", "")
                        
                        # Clean answer
                        answer = self._clean_universal_answer(answer)
                        
                        if len(answer.strip()) > 15:
                            return answer
                        else:
                            return "Die Anfrage konnte nicht bearbeitet werden."
                    else:
                        error_text = await response.text()
                        logger.error(f"Mistral API error {response.status}: {error_text}")
                        raise ValueError(f"Mistral API error {response.status}")
            
        except Exception as e:
            logger.error(f"❌ Universal answer generation failed: {e}")
            raise
    
    def _clean_universal_answer(self, answer: str) -> str:
        """Clean answer for production quality"""
        # Remove prefixes and artifacts
        answer = re.sub(r'^(passage:|query:)\s*', '', answer, flags=re.MULTILINE)
        
        # Remove verbose introductions
        answer = re.sub(r'^(Basierend auf|Laut|Gemäß|Die Dokumentation zeigt|Es wird erklärt)\s*[^.]*[.,]\s*', '', answer, flags=re.MULTILINE)
        
        # Fix common word-breaking issues from Mistral
        word_fixes = {
            'Ansprechpar ner': 'Ansprechpartner',
            'Dokumen a ion': 'Dokumentation', 
            'Informa ion': 'Information',
            'StreamWor s': 'StreamWorks',
            'S reamWorks': 'StreamWorks',
            'Berech igungen': 'Berechtigungen',
            'Sys em': 'System',
            'Plat form': 'Plattform',
            'Verwal ung': 'Verwaltung',
            'Konfigura ion': 'Konfiguration',
            'Sicher heit': 'Sicherheit',
            'Benut zer': 'Benutzer',
            'Applika ion': 'Applikation',
            'Instal a ion': 'Installation',
            'Authen ifizierung': 'Authentifizierung'
        }
        
        # Apply word-breaking fixes
        for broken, fixed in word_fixes.items():
            answer = answer.replace(broken, fixed)
        
        # Clean up whitespace
        answer = re.sub(r'\n\s*\n', '\n\n', answer)
        answer = re.sub(r'[ \t]+', ' ', answer)
        
        return answer.strip()
    
    def _calculate_universal_confidence(self, answer: str, docs: List[Dict], question: str) -> float:
        """Calculate confidence for universal system"""
        if not answer or len(answer.strip()) < 15:
            return 0.0
        
        # Base confidence from document relevance
        if docs:
            avg_relevance = sum(doc.get('weighted_relevance', 0) for doc in docs) / len(docs)
            base_confidence = min(avg_relevance * 1.3, 1.0)
        else:
            base_confidence = 0.2
        
        # Answer quality factors
        quality_factors = 0.8
        
        # Length appropriateness
        if 30 <= len(answer) <= 400:
            quality_factors += 0.1
        
        # Contains specific information (not generic)
        if not any(phrase in answer.lower() for phrase in ['nicht verfügbar', 'keine information', 'unbekannt']):
            quality_factors += 0.1
        
        # Multiple retrieval strategies agreement
        strategies = set(doc.get('strategy', '') for doc in docs)
        if len(strategies) > 1:
            quality_factors += 0.05
        
        confidence = base_confidence * quality_factors
        return round(min(confidence, 1.0), 2)
    
    def _extract_sources(self, docs: List[Dict]) -> List[str]:
        """Extract unique sources"""
        sources = []
        seen = set()
        
        for doc in docs:
            source = doc['source']
            if source not in seen:
                sources.append(source)
                seen.add(source)
        
        return sources[:3]
    
    def _extract_context_snippets(self, docs: List[Dict]) -> List[str]:
        """Extract context snippets for debugging"""
        snippets = []
        for doc in docs[:3]:
            content = doc['content']
            snippet = content[:100] + "..." if len(content) > 100 else content
            snippets.append(f"{doc.get('strategy', 'unknown')}: {snippet}")
        return snippets
    
    async def _test_mistral(self):
        """Test Mistral connection"""
        try:
            payload = {
                "model": self.config["mistral_model"],
                "prompt": "Test: Antworte mit 'OK'",
                "stream": False,
                "options": {"temperature": 0.1, "max_tokens": 10}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config['ollama_url']}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("response"):
                            logger.info("✅ Mistral connection tested successfully")
                            return
            
            raise ValueError("Mistral test failed")
        except Exception as e:
            logger.error(f"❌ Mistral test failed: {e}")
            raise

# Global instance
universal_rag = UniversalRAGService()