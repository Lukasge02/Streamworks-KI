"""
Dependency Validator
Validates all required services at startup - FAIL FAST approach
"""

import asyncio
import logging
from typing import Dict, Any
import httpx
import chromadb
from ollama import AsyncClient

logger = logging.getLogger(__name__)


class DependencyValidationError(Exception):
    """Raised when critical dependencies are not available"""
    pass


class DependencyValidator:
    """
    Validates all critical system dependencies at startup
    NO FALLBACKS - system must have all dependencies or fail
    """

    def __init__(self, settings):
        self.settings = settings

    async def validate_all_dependencies(self) -> Dict[str, Any]:
        """
        Validate critical dependencies (Supabase is now optional)
        Raises DependencyValidationError only for critical failures
        """
        logger.info("🔍 Validating system dependencies...")

        results = {}

        try:
            # 1. Validate Ollama + Model (CRITICAL)
            ollama_result = await self._validate_ollama()
            results["ollama"] = ollama_result

            # 2. Validate ChromaDB (CRITICAL)
            chroma_result = await self._validate_chromadb()
            results["chromadb"] = chroma_result

            # 3. Validate Supabase (OPTIONAL - for mirror only)
            try:
                supabase_result = await self._validate_supabase()
                results["supabase"] = supabase_result
            except Exception as e:
                logger.warning(f"⚠️ Supabase validation failed (non-critical for mirror): {str(e)}")
                results["supabase"] = {
                    "status": "unavailable",
                    "error": str(e),
                    "note": "Mirror disabled - ChromaDB-only mode"
                }

            # 4. Validate BGE Model availability (CRITICAL)
            embedding_result = await self._validate_embedding_model()
            results["embeddings"] = embedding_result

            logger.info("✅ All critical dependencies validated successfully!")
            return results

        except Exception as e:
            logger.error(f"❌ Critical dependency validation failed: {str(e)}")
            raise DependencyValidationError(f"Critical dependency missing: {str(e)}") from e

    async def _validate_ollama(self) -> Dict[str, Any]:
        """Validate Ollama service and required model"""
        logger.info(f"🦙 Validating Ollama service and model: {self.settings.OLLAMA_MODEL}")

        try:
            client = AsyncClient(host=self.settings.OLLAMA_BASE_URL)

            # Test connection
            models = await client.list()
            available_models = [model.model for model in models.models]

            if self.settings.OLLAMA_MODEL not in available_models:
                raise DependencyValidationError(
                    f"Required Ollama model '{self.settings.OLLAMA_MODEL}' not found. "
                    f"Available models: {available_models}"
                )

            # Test model functionality
            response = await client.chat(
                model=self.settings.OLLAMA_MODEL,
                messages=[{"role": "user", "content": "Test"}],
                stream=False
            )

            if not response or not response.message:
                raise DependencyValidationError("Ollama model not responding correctly")

            logger.info(f"✅ Ollama model {self.settings.OLLAMA_MODEL} validated")
            return {
                "status": "ok",
                "model": self.settings.OLLAMA_MODEL,
                "available_models": available_models,
                "base_url": self.settings.OLLAMA_BASE_URL
            }

        except httpx.ConnectError:
            raise DependencyValidationError(
                f"Cannot connect to Ollama at {self.settings.OLLAMA_BASE_URL}. "
                "Is Ollama running?"
            )
        except Exception as e:
            raise DependencyValidationError(f"Ollama validation failed: {str(e)}")

    async def _validate_chromadb(self) -> Dict[str, Any]:
        """Validate ChromaDB functionality"""
        logger.info("🗄️ Validating ChromaDB...")

        try:
            # Test ChromaDB connection
            client = chromadb.PersistentClient(
                path=str(self.settings.CHROMA_PATH)
            )

            # Test basic operations
            test_collection_name = "dependency_test"

            # Clean up any existing test collection
            try:
                client.delete_collection(test_collection_name)
            except:
                pass

            # Create test collection
            collection = client.create_collection(test_collection_name)

            # Test add/query
            collection.add(
                embeddings=[[1.0, 2.0, 3.0]],
                documents=["test document"],
                ids=["test_id"]
            )

            results = collection.query(
                query_embeddings=[[1.0, 2.0, 3.0]],
                n_results=1
            )

            if not results or not results['documents']:
                raise DependencyValidationError("ChromaDB query test failed")

            # Clean up test collection
            client.delete_collection(test_collection_name)

            logger.info("✅ ChromaDB validated")
            return {
                "status": "ok",
                "path": str(self.settings.CHROMA_PATH),
                "collections": len(client.list_collections())
            }

        except Exception as e:
            raise DependencyValidationError(f"ChromaDB validation failed: {str(e)}")

    async def _validate_supabase(self) -> Dict[str, Any]:
        """Validate Supabase connection and required tables"""
        logger.info("🛸 Validating Supabase connection...")

        try:
            # Import Supabase client
            from supabase import create_client

            if not self.settings.SUPABASE_URL or not self.settings.SUPABASE_SERVICE_KEY:
                raise DependencyValidationError("Supabase credentials not configured")

            # Test connection
            client = create_client(
                self.settings.SUPABASE_URL,
                self.settings.SUPABASE_SERVICE_KEY
            )

            # Test basic query (try to list tables or do a simple select)
            # This will fail if connection is bad
            response = client.table('documents').select('id').limit(1).execute()

            logger.info("✅ Supabase validated")
            return {
                "status": "ok",
                "url": self.settings.SUPABASE_URL,
                "connection": "verified"
            }

        except Exception as e:
            raise DependencyValidationError(
                f"Supabase validation failed: {str(e)}. "
                "Check SUPABASE_URL and SUPABASE_SERVICE_KEY"
            )

    async def _validate_embedding_model(self) -> Dict[str, Any]:
        """Validate BGE embedding model availability"""
        logger.info("🧠 Validating BGE embedding model...")

        try:
            from sentence_transformers import SentenceTransformer
            import torch

            # Check device availability
            if torch.cuda.is_available():
                device = "cuda"
            elif torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"

            # Test model loading
            model = SentenceTransformer("BAAI/bge-base-en-v1.5", device=device)

            # Test embedding generation
            test_embeddings = model.encode(["test sentence"], normalize_embeddings=True)

            if test_embeddings is None or len(test_embeddings) == 0:
                raise DependencyValidationError("BGE model embedding test failed")

            logger.info(f"✅ BGE model validated on device: {device}")
            return {
                "status": "ok",
                "model": "BAAI/bge-base-en-v1.5",
                "device": device,
                "embedding_dim": test_embeddings.shape[1] if len(test_embeddings.shape) > 1 else len(test_embeddings[0])
            }

        except Exception as e:
            raise DependencyValidationError(f"BGE model validation failed: {str(e)}")

    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status (for monitoring)"""
        try:
            results = await self.validate_all_dependencies()
            return {
                "status": "healthy",
                "dependencies": results,
                "timestamp": asyncio.get_event_loop().time()
            }
        except DependencyValidationError as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }


# Global validator instance
_validator = None

def get_dependency_validator(settings=None):
    """Get global dependency validator instance"""
    global _validator
    if _validator is None:
        from config import settings as app_settings
        _validator = DependencyValidator(settings or app_settings)
    return _validator