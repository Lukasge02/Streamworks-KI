"""
Qdrant Collections Setup Script
Erstellt automatisch die erforderlichen Collections für Streamworks-KI
"""

import asyncio
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, CollectionStatus
from config import settings

logger = logging.getLogger(__name__)

async def setup_qdrant_collections():
    """Setup alle erforderlichen Qdrant Collections"""

    try:
        # Qdrant Client initialisieren
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
            timeout=30
        )

        logger.info(f"🔗 Connecting to Qdrant at {settings.QDRANT_URL}")

        # Health Check
        health_info = client.get_collections()
        logger.info(f"✅ Qdrant connection successful")

        # Collection Konfigurationen
        collections_config = [
            {
                "name": settings.QDRANT_COLLECTION_NAME,  # streamworks_documents
                "vector_params": VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,  # 768 für Gamma Embeddings
                    distance=Distance.COSINE
                ),
                "description": "Main document collection for Streamworks RAG pipeline"
            },
            {
                "name": settings.XML_COLLECTION_NAME,  # streamworks_xml_streams
                "vector_params": VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE,
                    distance=Distance.COSINE
                ),
                "description": "XML streams collection for XML Wizard functionality"
            }
        ]

        # Collections erstellen
        for config in collections_config:
            collection_name = config["name"]

            try:
                # Prüfen ob Collection bereits existiert
                collection_info = client.get_collection(collection_name)

                if collection_info.status == CollectionStatus.GREEN:
                    logger.info(f"✅ Collection '{collection_name}' bereits vorhanden und gesund")
                    logger.info(f"   Points: {collection_info.points_count}")
                    logger.info(f"   Segments: {collection_info.segments_count}")
                    continue

            except Exception:
                # Collection existiert nicht, erstellen
                logger.info(f"🏗️  Erstelle Collection '{collection_name}'...")

                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=config["vector_params"]
                )

                logger.info(f"✅ Collection '{collection_name}' erfolgreich erstellt")
                logger.info(f"   Description: {config.get('description', 'N/A')}")
                logger.info(f"   Vector Size: {config['vector_params'].size}")
                logger.info(f"   Distance Metric: {config['vector_params'].distance}")

        # Final Health Check
        logger.info("\n🔍 Final Collections Status:")
        collections = client.get_collections()

        for collection in collections.collections:
            info = client.get_collection(collection.name)
            logger.info(f"📊 {collection.name}:")
            logger.info(f"   Status: {info.status}")
            logger.info(f"   Points: {info.points_count}")
            logger.info(f"   Vector Size: {info.config.params.vectors.size}")
            logger.info(f"   Distance: {info.config.params.vectors.distance}")

        logger.info("🎉 Qdrant Collections Setup erfolgreich abgeschlossen!")
        return True

    except Exception as e:
        logger.error(f"❌ Fehler beim Setup der Qdrant Collections: {str(e)}")
        return False

async def main():
    """Main Setup Routine"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("🚀 Starte Qdrant Collections Setup...")

    success = await setup_qdrant_collections()

    if success:
        logger.info("✅ Setup erfolgreich!")
        print("\n🎯 Nächste Schritte:")
        print(f"1. Starte Qdrant: docker-compose -f docker-compose.qdrant.yml up -d")
        print(f"2. Web UI: http://localhost:6333/dashboard")
        print(f"3. Collections: {settings.QDRANT_COLLECTION_NAME}, {settings.XML_COLLECTION_NAME}")
    else:
        logger.error("❌ Setup fehlgeschlagen!")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())