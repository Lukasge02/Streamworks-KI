#!/usr/bin/env python3
"""
Script to enrich existing training data with citation metadata
Maps source files to appropriate source types and document types
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import DatabaseManager, TrainingFile
from app.models.schemas import SourceType, DocumentType
from app.services.citation_service import CitationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainingDataEnricher:
    """Enrich training data with citation metadata"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.citation_service = CitationService()
        
        # Mapping rules for existing files
        self.file_mappings = {
            "streamworks_faq.txt": {
                "source_type": SourceType.FAQ.value,
                "source_title": "StreamWorks FAQ - Häufig gestellte Fragen",
                "document_type": DocumentType.FAQ.value,
                "author": "StreamWorks Team",
                "version": "1.0",
                "priority": 1,
                "tags": ["FAQ", "StreamWorks", "Grundlagen"]
            },
            "streamworks_batch_hilfe.txt": {
                "source_type": SourceType.STREAMWORKS.value,
                "source_title": "StreamWorks Batch-Jobs Hilfe",
                "document_type": DocumentType.TROUBLESHOOTING.value,
                "author": "StreamWorks Team",
                "version": "1.0",
                "priority": 1,
                "tags": ["Batch", "Jobs", "Hilfe", "Troubleshooting"]
            },
            "csv_verarbeitung_tipps.txt": {
                "source_type": SourceType.STREAMWORKS.value,
                "source_title": "CSV-Verarbeitung Tipps und Best Practices",
                "document_type": DocumentType.BEST_PRACTICES.value,
                "author": "StreamWorks Team",
                "version": "1.0",
                "priority": 2,
                "tags": ["CSV", "Verarbeitung", "Best Practices"]
            },
            "datenverarbeitung_anleitung.txt": {
                "source_type": SourceType.STREAMWORKS.value,
                "source_title": "Datenverarbeitung Anleitung",
                "document_type": DocumentType.GUIDE.value,
                "author": "StreamWorks Team",
                "version": "1.0",
                "priority": 1,
                "tags": ["Datenverarbeitung", "Anleitung", "Guide"]
            },
            "powershell_streamworks.txt": {
                "source_type": SourceType.STREAMWORKS.value,
                "source_title": "PowerShell Integration für StreamWorks",
                "document_type": DocumentType.TUTORIAL.value,
                "author": "StreamWorks Team",
                "version": "1.0",
                "priority": 2,
                "tags": ["PowerShell", "Integration", "Tutorial"]
            }
        }
        
        # Pattern-based mappings for training_data files
        self.pattern_mappings = {
            "training_data_01.txt": {
                "source_type": SourceType.TUTORIAL.value,
                "source_title": "StreamWorks Batch-Jobs Grundlagen",
                "document_type": DocumentType.TUTORIAL.value,
                "tags": ["Batch-Jobs", "Grundlagen"]
            },
            "training_data_02.txt": {
                "source_type": SourceType.DOCUMENTATION.value,
                "source_title": "StreamWorks Dokumentation Teil 2",
                "document_type": DocumentType.GUIDE.value,
                "tags": ["Dokumentation", "Guide"]
            },
            "training_data_03.txt": {
                "source_type": SourceType.DOCUMENTATION.value,
                "source_title": "StreamWorks Dokumentation Teil 3",
                "document_type": DocumentType.GUIDE.value,
                "tags": ["Dokumentation", "Guide"]
            },
            "training_data_04.txt": {
                "source_type": SourceType.DOCUMENTATION.value,
                "source_title": "StreamWorks Dokumentation Teil 4",
                "document_type": DocumentType.GUIDE.value,
                "tags": ["Dokumentation", "Guide"]
            },
            "training_data_05.txt": {
                "source_type": SourceType.DOCUMENTATION.value,
                "source_title": "StreamWorks Dokumentation Teil 5",
                "document_type": DocumentType.GUIDE.value,
                "tags": ["Dokumentation", "Guide"]
            },
            "training_data_06.txt": {
                "source_type": SourceType.DOCUMENTATION.value,
                "source_title": "StreamWorks Dokumentation Teil 6",
                "document_type": DocumentType.GUIDE.value,
                "tags": ["Dokumentation", "Guide"]
            },
            "training_data_07.txt": {
                "source_type": SourceType.DOCUMENTATION.value,
                "source_title": "StreamWorks Dokumentation Teil 7",
                "document_type": DocumentType.GUIDE.value,
                "tags": ["Dokumentation", "Guide"]
            },
            "training_data_08.txt": {
                "source_type": SourceType.DOCUMENTATION.value,
                "source_title": "StreamWorks Dokumentation Teil 8",
                "document_type": DocumentType.GUIDE.value,
                "tags": ["Dokumentation", "Guide"]
            },
            "training_data_09.txt": {
                "source_type": SourceType.DOCUMENTATION.value,
                "source_title": "StreamWorks Dokumentation Teil 9",
                "document_type": DocumentType.GUIDE.value,
                "tags": ["Dokumentation", "Guide"]
            },
            "training_data_10.txt": {
                "source_type": SourceType.DOCUMENTATION.value,
                "source_title": "StreamWorks Dokumentation Teil 10",
                "document_type": DocumentType.GUIDE.value,
                "tags": ["Dokumentation", "Guide"]
            }
        }
    
    async def enrich_all_files(self):
        """Enrich all training files with citation metadata"""
        logger.info("🔗 Starting citation metadata enrichment...")
        
        async with self.db_manager.get_session() as session:
            # Get all training files
            result = await session.execute(
                "SELECT * FROM training_files WHERE source_type IS NULL"
            )
            
            files_to_update = result.fetchall()
            logger.info(f"📄 Found {len(files_to_update)} files to enrich")
            
            updated_count = 0
            
            for file_row in files_to_update:
                try:
                    filename = file_row[2]  # filename column
                    file_id = file_row[0]   # id column
                    
                    logger.info(f"🔍 Processing: {filename}")
                    
                    # Get metadata for this file
                    metadata = self._get_metadata_for_file(filename)
                    
                    if metadata:
                        # Update the database record
                        update_query = """
                            UPDATE training_files 
                            SET 
                                source_type = ?,
                                source_title = ?,
                                document_type = ?,
                                author = ?,
                                version = ?,
                                last_modified = ?,
                                priority = ?,
                                tags = ?,
                                language = ?
                            WHERE id = ?
                        """
                        
                        await session.execute(update_query, (
                            metadata.get("source_type"),
                            metadata.get("source_title"),
                            metadata.get("document_type"),
                            metadata.get("author", "StreamWorks Team"),
                            metadata.get("version", "1.0"),
                            datetime.now(),
                            metadata.get("priority", 2),
                            str(metadata.get("tags", [])),  # Convert to JSON string
                            "de",
                            file_id
                        ))
                        
                        updated_count += 1
                        logger.info(f"✅ Updated {filename} with citation metadata")
                    else:
                        logger.warning(f"⚠️ No metadata mapping found for {filename}")
                
                except Exception as e:
                    logger.error(f"❌ Failed to update {filename}: {e}")
                    continue
            
            # Commit changes
            await session.commit()
            
        logger.info(f"🎉 Citation enrichment completed! Updated {updated_count} files")
        return updated_count
    
    def _get_metadata_for_file(self, filename: str) -> dict:
        """Get citation metadata for a specific file"""
        
        # Check specific file mappings first
        if filename in self.file_mappings:
            return self.file_mappings[filename]
        
        # Check pattern mappings
        if filename in self.pattern_mappings:
            base_metadata = {
                "author": "StreamWorks Team",
                "version": "1.0",
                "priority": 2
            }
            base_metadata.update(self.pattern_mappings[filename])
            return base_metadata
        
        # Fallback for unknown files
        if filename.startswith("training_data"):
            return {
                "source_type": SourceType.DOCUMENTATION.value,
                "source_title": f"StreamWorks Dokumentation - {filename}",
                "document_type": DocumentType.GUIDE.value,
                "author": "StreamWorks Team",
                "version": "1.0",
                "priority": 3,
                "tags": ["Dokumentation", "StreamWorks"]
            }
        
        return None
    
    async def verify_enrichment(self):
        """Verify that enrichment was successful"""
        logger.info("🔍 Verifying citation enrichment...")
        
        async with self.db_manager.get_session() as session:
            # Count enriched files
            result = await session.execute(
                "SELECT COUNT(*) FROM training_files WHERE source_type IS NOT NULL"
            )
            enriched_count = result.fetchone()[0]
            
            # Count total files
            result = await session.execute(
                "SELECT COUNT(*) FROM training_files"
            )
            total_count = result.fetchone()[0]
            
            # Get breakdown by source type
            result = await session.execute(
                "SELECT source_type, COUNT(*) FROM training_files WHERE source_type IS NOT NULL GROUP BY source_type"
            )
            breakdown = dict(result.fetchall())
            
            logger.info(f"📊 Enrichment Results:")
            logger.info(f"   Total files: {total_count}")
            logger.info(f"   Enriched files: {enriched_count}")
            logger.info(f"   Coverage: {enriched_count/total_count*100:.1f}%")
            logger.info(f"   Source type breakdown: {breakdown}")
            
            return enriched_count, total_count, breakdown


async def main():
    """Main enrichment process"""
    enricher = TrainingDataEnricher()
    
    try:
        # Enrich all files
        updated_count = await enricher.enrich_all_files()
        
        # Verify results
        await enricher.verify_enrichment()
        
        logger.info(f"🎯 Citation metadata enrichment completed successfully!")
        logger.info(f"✅ {updated_count} files updated with citation metadata")
        
    except Exception as e:
        logger.error(f"❌ Enrichment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())