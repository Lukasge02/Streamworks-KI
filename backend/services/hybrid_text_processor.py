"""
Hybrid Text Processor für Streamworks-KI
Generiert sparse vectors für BM25-ähnliche Keyword-Suche in Qdrant
"""

import re
import logging
from typing import Dict, List, Set, Optional, Tuple
from collections import Counter
import unicodedata
from math import log

from config import settings

logger = logging.getLogger(__name__)


class HybridTextProcessor:
    """
    Text Processor für Hybrid Search - generiert sparse vectors für BM25-ähnliche Suche

    Features:
    - Multi-language stopword removal (German + English)
    - TF-IDF ähnliche Gewichtung für sparse vectors
    - Qdrant-kompatible sparse vector generation
    - Configurable text normalization
    """

    def __init__(self):
        self.stopwords_de = self._load_german_stopwords()
        self.stopwords_en = self._load_english_stopwords()
        self.stopwords = self.stopwords_de | self.stopwords_en

        # Document frequency storage für TF-IDF
        self.document_frequencies: Dict[str, int] = {}
        self.total_documents = 0

        # Vocabulary mapping für consistent term IDs
        self.term_to_id: Dict[str, int] = {}
        self.next_term_id = 0

        logger.info("🔧 HybridTextProcessor initialized with multi-language support")

    def _load_german_stopwords(self) -> Set[str]:
        """Load German stopwords"""
        german_stopwords = {
            'aber', 'alle', 'allem', 'allen', 'aller', 'alles', 'als', 'also', 'am', 'an', 'ander',
            'andere', 'anderem', 'anderen', 'anderer', 'anderes', 'anderm', 'andern', 'anders',
            'auch', 'auf', 'aus', 'bei', 'bin', 'bis', 'bist', 'da', 'damit', 'dann', 'der',
            'den', 'des', 'dem', 'die', 'das', 'dass', 'daß', 'du', 'er', 'eine', 'ein', 'einem',
            'einen', 'einer', 'eines', 'es', 'für', 'hatte', 'hat', 'hatte', 'haben', 'habe',
            'ich', 'ihn', 'ihm', 'ihr', 'ihre', 'ihrem', 'ihren', 'ihrer', 'ihres', 'im', 'in',
            'ist', 'ja', 'kann', 'machen', 'mein', 'meine', 'meinem', 'meinen', 'meiner', 'meines',
            'mit', 'muss', 'nach', 'nicht', 'noch', 'nur', 'oder', 'ohne', 'sehr', 'sein', 'seine',
            'seinem', 'seinen', 'seiner', 'seines', 'sich', 'sie', 'sind', 'so', 'über', 'um',
            'und', 'uns', 'unse', 'unser', 'unsere', 'unserem', 'unseren', 'unserer', 'unseres',
            'von', 'vor', 'war', 'waren', 'warst', 'was', 'weg', 'weil', 'weiter', 'wenn', 'wer',
            'were', 'wie', 'wieder', 'will', 'wir', 'wird', 'wirst', 'wo', 'wollen', 'wurde',
            'wurden', 'während', 'würde', 'würden', 'zu', 'zum', 'zur', 'zwischen'
        }
        return german_stopwords

    def _load_english_stopwords(self) -> Set[str]:
        """Load English stopwords"""
        english_stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he', 'in',
            'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was', 'will', 'with', 'would',
            'have', 'had', 'has', 'having', 'do', 'does', 'did', 'doing', 'can', 'could', 'should',
            'would', 'may', 'might', 'must', 'shall', 'will', 'am', 'is', 'are', 'was', 'were',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'this', 'that', 'these', 'those',
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
            'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
            'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
            'who', 'whom', 'whose', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
            'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
            'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after', 'above', 'below',
            'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'
        }
        return english_stopwords

    def normalize_text(self, text: str) -> str:
        """
        Normalize text für consistent processing

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        if not text:
            return ""

        # Unicode normalization
        text = unicodedata.normalize('NFKD', text)

        # Convert to lowercase
        text = text.lower()

        # Remove special characters but keep alphanumeric, spaces, and German umlauts
        text = re.sub(r'[^\w\säöüß]', ' ', text)

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into individual terms

        Args:
            text: Normalized text

        Returns:
            List of tokens
        """
        if not text:
            return []

        # Simple whitespace tokenization
        tokens = text.split()
        logger.debug(f"Initial tokens after split: {len(tokens)} - {tokens[:10] if tokens else 'none'}")

        # Filter tokens
        filtered_tokens = []
        removed_reasons = {"short": 0, "stopword": 0, "numeric": 0}

        for token in tokens:
            # Remove very short tokens (< 2 characters)
            if len(token) < 2:
                removed_reasons["short"] += 1
                continue

            # Remove stopwords if configured
            if settings.REMOVE_STOPWORDS and token in self.stopwords:
                removed_reasons["stopword"] += 1
                continue

            # Remove pure numeric tokens
            if token.isdigit():
                removed_reasons["numeric"] += 1
                continue

            filtered_tokens.append(token)

        logger.debug(f"Token filtering: kept {len(filtered_tokens)}, removed: {removed_reasons}")
        return filtered_tokens

    def get_term_id(self, term: str) -> int:
        """Get or create term ID for vocabulary"""
        if term not in self.term_to_id:
            if len(self.term_to_id) >= settings.MAX_SPARSE_VECTOR_SIZE:
                # Vocabulary full - ignore new terms
                return -1
            self.term_to_id[term] = self.next_term_id
            self.next_term_id += 1
        return self.term_to_id[term]

    def compute_tf_idf_weights(self, term_frequencies: Dict[str, int]) -> Dict[str, float]:
        """
        Compute TF-IDF weights for terms

        Args:
            term_frequencies: Term frequency counts

        Returns:
            TF-IDF weighted terms
        """
        tf_idf_weights = {}

        # Total terms in document
        total_terms = sum(term_frequencies.values())

        for term, tf in term_frequencies.items():
            # Term frequency (normalized)
            tf_normalized = tf / total_terms

            # Inverse document frequency (simplified - using global stats)
            doc_freq = self.document_frequencies.get(term, 1)
            idf = log(max(1, self.total_documents) / doc_freq)

            # TF-IDF score
            tf_idf_score = tf_normalized * idf

            # Apply minimum frequency filter
            if tf >= settings.MIN_TERM_FREQUENCY:
                tf_idf_weights[term] = tf_idf_score

        return tf_idf_weights

    def text_to_sparse_vector(self, text: str, update_global_stats: bool = True) -> Dict[int, float]:
        """
        Convert text to sparse vector für Qdrant

        Args:
            text: Input text
            update_global_stats: Whether to update global document frequency stats

        Returns:
            Sparse vector as {term_id: weight} mapping
        """
        if not text or not text.strip():
            logger.debug("Empty text input - returning empty sparse vector")
            return {}

        try:
            # 1. Normalize text
            normalized_text = self.normalize_text(text)
            logger.debug(f"Normalized text: '{normalized_text[:100]}...'")

            # 2. Tokenize
            tokens = self.tokenize(normalized_text)
            logger.debug(f"Tokenized: {len(tokens)} tokens: {tokens[:10] if tokens else 'none'}")

            if not tokens:
                logger.warning("No tokens after tokenization - returning empty sparse vector")
                return {}

            # 3. Count term frequencies
            term_frequencies = Counter(tokens)
            logger.debug(f"Term frequencies: {dict(list(term_frequencies.items())[:5])}...")

            # 4. Update global document frequency stats (for IDF calculation)
            if update_global_stats:
                self.total_documents += 1
                for term in term_frequencies.keys():
                    self.document_frequencies[term] = self.document_frequencies.get(term, 0) + 1

            # 5. Compute TF-IDF weights
            tf_idf_weights = self.compute_tf_idf_weights(term_frequencies)
            logger.debug(f"TF-IDF weights: {len(tf_idf_weights)} terms: {dict(list(tf_idf_weights.items())[:5])}...")

            # 6. Convert to sparse vector format
            sparse_vector = {}
            for term, weight in tf_idf_weights.items():
                term_id = self.get_term_id(term)
                if term_id >= 0:  # Valid term ID
                    sparse_vector[term_id] = weight

            logger.info(f"Generated sparse vector with {len(sparse_vector)} dimensions from {len(tokens)} tokens")
            return sparse_vector

        except Exception as e:
            logger.error(f"Failed to generate sparse vector: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def process_query(self, query: str) -> Dict[int, float]:
        """
        Process query text to sparse vector (no global stats update)

        Args:
            query: Query text

        Returns:
            Query sparse vector
        """
        return self.text_to_sparse_vector(query, update_global_stats=False)

    def process_document(self, text: str) -> Dict[int, float]:
        """
        Process document text to sparse vector (with global stats update)

        Args:
            text: Document text

        Returns:
            Document sparse vector
        """
        return self.text_to_sparse_vector(text, update_global_stats=True)

    def get_vocabulary_info(self) -> Dict[str, any]:
        """Get information about current vocabulary"""
        return {
            "vocabulary_size": len(self.term_to_id),
            "max_vocabulary_size": settings.MAX_SPARSE_VECTOR_SIZE,
            "total_documents_processed": self.total_documents,
            "unique_terms_in_corpus": len(self.document_frequencies),
            "settings": {
                "remove_stopwords": settings.REMOVE_STOPWORDS,
                "min_term_frequency": settings.MIN_TERM_FREQUENCY,
                "language": settings.TEXT_PREPROCESSING_LANGUAGE
            }
        }

    def save_vocabulary(self, file_path: str) -> bool:
        """Save vocabulary to file for persistence"""
        try:
            import json
            vocab_data = {
                "term_to_id": self.term_to_id,
                "document_frequencies": self.document_frequencies,
                "total_documents": self.total_documents,
                "next_term_id": self.next_term_id
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(vocab_data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ Vocabulary saved to {file_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save vocabulary: {str(e)}")
            return False

    def load_vocabulary(self, file_path: str) -> bool:
        """Load vocabulary from file"""
        try:
            import json

            with open(file_path, 'r', encoding='utf-8') as f:
                vocab_data = json.load(f)

            self.term_to_id = vocab_data.get("term_to_id", {})
            self.document_frequencies = vocab_data.get("document_frequencies", {})
            self.total_documents = vocab_data.get("total_documents", 0)
            self.next_term_id = vocab_data.get("next_term_id", 0)

            logger.info(f"✅ Vocabulary loaded from {file_path} - {len(self.term_to_id)} terms")
            return True

        except FileNotFoundError:
            logger.info(f"📁 Vocabulary file not found: {file_path} - starting fresh")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load vocabulary: {str(e)}")
            return False


# Global processor instance
_text_processor = None

def get_hybrid_text_processor() -> HybridTextProcessor:
    """Get global HybridTextProcessor instance"""
    global _text_processor
    if _text_processor is None:
        _text_processor = HybridTextProcessor()

        # Try to load existing vocabulary
        vocab_path = settings.SYSTEM_PATH / "hybrid_vocabulary.json"
        _text_processor.load_vocabulary(str(vocab_path))

    return _text_processor

def save_hybrid_vocabulary():
    """Save current vocabulary state"""
    if _text_processor:
        vocab_path = settings.SYSTEM_PATH / "hybrid_vocabulary.json"
        vocab_path.parent.mkdir(parents=True, exist_ok=True)
        _text_processor.save_vocabulary(str(vocab_path))