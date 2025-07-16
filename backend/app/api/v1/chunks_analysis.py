"""
📊 CHUNKS ANALYSIS API - ENTERPRISE VISUALIZATION
Advanced chunk analysis and visualization endpoints for training data
Provides detailed insights into how documents are chunked and indexed

Author: Senior AI Engineer
Version: 1.0.0 (Enterprise Production)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional
import json
import chromadb
from chromadb.config import Settings

from ...models.database import get_db
from ...services.enterprise_chromadb_indexer import enterprise_indexer

router = APIRouter()

@router.get("/files/{file_id}/chunks", response_model=Dict[str, Any])
async def get_file_chunks(
    file_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    📊 GET FILE CHUNKS WITH DETAILED ANALYSIS
    Returns comprehensive chunk analysis for a specific file
    """
    try:
        # Get file information
        file_query = """
        SELECT 
            tf.id, tf.filename, tf.file_path, tf.chunk_count,
            tf.processing_status, tf.created_at, tf.last_indexed_at,
            tf.category as category_name, tf.category as category_slug,
            NULL as folder_name, NULL as folder_slug
        FROM training_files tf
        JOIN document_categories dc ON tf.category_id = dc.id
        LEFT JOIN document_folders df ON tf.folder_id = df.id
        WHERE tf.id = :file_id AND tf.deleted_at IS NULL
        """
        
        result = await db.execute(text(file_query), {"file_id": file_id})
        file_record = result.first()
        
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get chunks from ChromaDB
        chunks_data = await _get_chunks_from_chromadb(file_id)
        
        # Calculate statistics
        stats = _calculate_chunk_statistics(chunks_data)
        
        return {
            "file_info": {
                "id": str(file_record.id),
                "filename": file_record.filename,
                "category": file_record.category_name,
                "folder": file_record.folder_name,
                "chunk_count": file_record.chunk_count,
                "processing_status": file_record.status,
                "created_at": file_record.upload_date if isinstance(file_record.upload_date, str) else (file_record.upload_date.isoformat() if file_record.upload_date else None),
                "last_indexed_at": file_record.indexed_at if isinstance(file_record.indexed_at, str) else (file_record.indexed_at.isoformat() if file_record.indexed_at else None)
            },
            "chunks": chunks_data,
            "statistics": stats,
            "visualization_data": _prepare_visualization_data(chunks_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chunks: {str(e)}")

@router.get("/overview", response_model=Dict[str, Any])
async def get_chunks_overview(
    category_slug: Optional[str] = Query(None, description="Filter by category"),
    folder_slug: Optional[str] = Query(None, description="Filter by folder"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    📈 GET CHUNKS OVERVIEW
    Provides system-wide chunk statistics and quality metrics
    """
    try:
        # Build query with filters
        query = """
        SELECT 
            tf.id, tf.filename, tf.chunk_count, tf.status,
            tf.upload_date, tf.indexed_at,
            tf.category as category_name, tf.category as category_slug,
            NULL as folder_name, NULL as folder_slug
        FROM training_files tf
        WHERE tf.status != 'deleted'
        """
        
        params = {}
        if category_slug:
            query += " AND tf.category = :category_slug"
            params["category_slug"] = category_slug
        if folder_slug:
            # Folder filtering not supported in current schema
            pass
            
        query += " ORDER BY tf.upload_date DESC"
        
        result = await db.execute(text(query), params)
        files = result.fetchall()
        
        # Calculate overview statistics
        overview_stats = {
            "total_files": len(files),
            "total_chunks": sum(f.chunk_count or 0 for f in files),
            "indexed_files": len([f for f in files if f.status == 'indexed']),
            "pending_files": len([f for f in files if f.status in ['uploaded', 'processing']]),
            "failed_files": len([f for f in files if f.status == 'error']),
            "categories": {},
            "folders": {}
        }
        
        # Group by categories and folders
        for file in files:
            # Categories
            cat_name = file.category_name
            if cat_name not in overview_stats["categories"]:
                overview_stats["categories"][cat_name] = {
                    "files": 0,
                    "chunks": 0,
                    "slug": file.category_slug
                }
            overview_stats["categories"][cat_name]["files"] += 1
            overview_stats["categories"][cat_name]["chunks"] += file.chunk_count or 0
            
            # Folders
            folder_name = file.folder_name or "root"
            if folder_name not in overview_stats["folders"]:
                overview_stats["folders"][folder_name] = {
                    "files": 0,
                    "chunks": 0,
                    "slug": file.folder_slug
                }
            overview_stats["folders"][folder_name]["files"] += 1
            overview_stats["folders"][folder_name]["chunks"] += file.chunk_count or 0
        
        # Get recent activity
        recent_files = [
            {
                "id": str(f.id),
                "filename": f.filename,
                "category": f.category_name,
                "folder": f.folder_name,
                "chunks": f.chunk_count or 0,
                "status": f.status,
                "indexed_at": f.indexed_at if isinstance(f.indexed_at, str) else (f.indexed_at.isoformat() if f.indexed_at else None)
            }
            for f in files[:10]  # Last 10 files
        ]
        
        return {
            "overview": overview_stats,
            "recent_files": recent_files,
            "system_health": _assess_system_health(files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve overview: {str(e)}")

@router.get("/enterprise-analysis", response_model=Dict[str, Any])
async def get_enterprise_analysis(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    🏢 ENTERPRISE CHUNKS ANALYSIS
    Comprehensive analysis for enterprise-level insights
    """
    try:
        # Get all files with detailed metadata
        files_query = """
        SELECT 
            tf.id, tf.filename, tf.chunk_count, tf.status, tf.file_size,
            tf.upload_date, tf.indexed_at, tf.category, tf.processing_method,
            tf.processing_quality, tf.extraction_confidence
        FROM training_files tf
        WHERE tf.status != 'deleted'
        ORDER BY tf.upload_date DESC
        """
        
        result = await db.execute(text(files_query))
        files = result.fetchall()
        
        # Get chunks from ChromaDB for detailed analysis
        all_chunks = await _get_all_chunks_from_chromadb()
        
        # Calculate comprehensive metrics
        file_analytics = []
        for file_record in files:
            # Try to match chunks by filename since file_id might be inconsistent
            file_chunks = [c for c in all_chunks if 
                          c.get('metadata', {}).get('file_id') == str(file_record.id) or
                          (c.get('metadata', {}).get('filename', '').startswith(file_record.filename.split('.')[0]))]
            
            if file_chunks:
                chunk_lengths = [len(c['content']) for c in file_chunks]
                quality_scores = [c.get('quality_score', 0.0) for c in file_chunks]
                
                file_analytics.append({
                    "file_id": str(file_record.id),
                    "filename": file_record.filename,
                    "total_chunks": len(file_chunks),
                    "total_characters": sum(chunk_lengths),
                    "avg_chunk_size": sum(chunk_lengths) / len(chunk_lengths) if chunk_lengths else 0,
                    "min_chunk_size": min(chunk_lengths) if chunk_lengths else 0,
                    "max_chunk_size": max(chunk_lengths) if chunk_lengths else 0,
                    "avg_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                    "quality_distribution": _analyze_quality_distribution(quality_scores),
                    "chunk_types": _analyze_chunk_types(file_chunks),
                    "file_size_bytes": file_record.file_size,
                    "compression_ratio": (file_record.file_size / sum(chunk_lengths)) if chunk_lengths and file_record.file_size else 0,
                    "indexed_at": file_record.indexed_at,
                    "processing_method": file_record.processing_method,
                    "processing_quality": file_record.processing_quality,
                    "extraction_confidence": file_record.extraction_confidence
                })
        
        # System-wide analytics
        system_analytics = _calculate_system_analytics(all_chunks, files)
        
        # Performance metrics
        performance_metrics = _calculate_performance_metrics(all_chunks)
        
        return {
            "timestamp": "2025-07-16T14:00:00Z",
            "system_overview": {
                "total_files": len(files),
                "total_chunks": len(all_chunks),
                "total_characters": sum(len(c['content']) for c in all_chunks),
                "avg_chunks_per_file": len(all_chunks) / len(files) if files else 0,
                "indexing_efficiency": sum(1 for f in files if f.status == 'ready') / len(files) if files else 0
            },
            "file_analytics": file_analytics,
            "system_analytics": system_analytics,
            "performance_metrics": performance_metrics,
            "quality_insights": _generate_quality_insights(all_chunks),
            "recommendations": _generate_enterprise_recommendations(all_chunks, files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve enterprise analysis: {str(e)}")

@router.get("/quality-analysis", response_model=Dict[str, Any])
async def get_quality_analysis(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    🔍 GET CHUNK QUALITY ANALYSIS
    Analyzes chunk quality across the entire system
    """
    try:
        # Get all chunks from ChromaDB
        all_chunks = await _get_all_chunks_from_chromadb()
        
        # Analyze quality metrics
        quality_analysis = _analyze_chunk_quality(all_chunks)
        
        return {
            "quality_metrics": quality_analysis,
            "recommendations": _generate_quality_recommendations(quality_analysis),
            "chunk_distribution": _analyze_chunk_distribution(all_chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze quality: {str(e)}")

@router.post("/reindex/{file_id}")
async def reindex_file_chunks(
    file_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    🔄 REINDEX FILE CHUNKS
    Triggers re-indexing of a specific file with latest chunking strategy
    """
    try:
        # Remove existing chunks
        await enterprise_indexer.remove_file_from_index(file_id, db)
        
        # Re-index with latest strategy
        result = await enterprise_indexer.index_file(file_id, db)
        
        return {
            "file_id": file_id,
            "reindex_result": result,
            "message": "File re-indexed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reindex file: {str(e)}")

# Helper functions

async def _get_chunks_from_chromadb(file_id: str) -> List[Dict[str, Any]]:
    """Get chunks for a specific file from ChromaDB"""
    try:
        # Connect to ChromaDB
        client = chromadb.PersistentClient(
            path="./data/vector_db_production",
            settings=Settings(anonymized_telemetry=False)
        )
        
        collection = client.get_collection("streamworks_production")
        
        # Get chunks for this file
        all_chunks = collection.get(
            include=['documents', 'metadatas'],
            where={"file_id": file_id}
        )
        
        chunks_data = []
        for i, (doc, metadata) in enumerate(zip(all_chunks['documents'], all_chunks['metadatas'])):
            chunk_data = {
                "index": i,
                "content": doc,
                "content_length": len(doc),
                "metadata": metadata,
                # Enterprise metrics (if available)
                "quality_score": metadata.get("quality_score", 0.0),
                "semantic_density": metadata.get("semantic_density", 0.0),
                "readability_score": metadata.get("readability_score", 0.0),
                "chunk_type": metadata.get("chunk_type", "unknown"),
                "strategy_used": metadata.get("strategy_used", "unknown"),
                "quality_assessment": metadata.get("quality_assessment", "unknown"),
                "key_concepts": metadata.get("key_concepts", "").split(",") if metadata.get("key_concepts") else [],
                "entities": metadata.get("entities", "").split(",") if metadata.get("entities") else []
            }
            chunks_data.append(chunk_data)
        
        return chunks_data
        
    except Exception as e:
        print(f"Error getting chunks from ChromaDB: {e}")
        return []

async def _get_all_chunks_from_chromadb() -> List[Dict[str, Any]]:
    """Get all chunks from ChromaDB for system-wide analysis"""
    try:
        client = chromadb.PersistentClient(
            path="./data/vector_db_production",
            settings=Settings(anonymized_telemetry=False)
        )
        
        try:
            collection = client.get_collection("streamworks_production")
        except Exception:
            # Collection doesn't exist, return empty
            return []
        
        all_chunks = collection.get(include=['documents', 'metadatas'])
        
        # Handle empty collection
        if not all_chunks.get('documents') or not all_chunks.get('metadatas'):
            return []
        
        chunks_data = []
        for doc, metadata in zip(all_chunks['documents'] or [], all_chunks['metadatas'] or []):
            chunk_data = {
                "content": doc,
                "content_length": len(doc),
                "metadata": metadata,
                "quality_score": metadata.get("quality_score", 0.0),
                "semantic_density": metadata.get("semantic_density", 0.0),
                "readability_score": metadata.get("readability_score", 0.0),
                "chunk_type": metadata.get("chunk_type", "unknown"),
                "strategy_used": metadata.get("strategy_used", "unknown"),
                "quality_assessment": metadata.get("quality_assessment", "unknown")
            }
            chunks_data.append(chunk_data)
        
        return chunks_data
        
    except Exception as e:
        print(f"Error getting all chunks from ChromaDB: {e}")
        return []

def _calculate_chunk_statistics(chunks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics for chunks"""
    if not chunks_data:
        return {"total_chunks": 0}
    
    total_chunks = len(chunks_data)
    avg_length = sum(chunk["content_length"] for chunk in chunks_data) / total_chunks
    
    # Quality metrics
    quality_scores = [chunk["quality_score"] for chunk in chunks_data if isinstance(chunk["quality_score"], (int, float))]
    avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
    # Chunk types distribution
    chunk_types = {}
    for chunk in chunks_data:
        chunk_type = chunk["chunk_type"]
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
    
    # Strategy usage
    strategies = {}
    for chunk in chunks_data:
        strategy = chunk["strategy_used"]
        strategies[strategy] = strategies.get(strategy, 0) + 1
    
    return {
        "total_chunks": total_chunks,
        "average_length": round(avg_length, 2),
        "average_quality": round(avg_quality, 3),
        "chunk_types": chunk_types,
        "strategies_used": strategies,
        "quality_distribution": _get_quality_distribution(chunks_data)
    }

def _prepare_visualization_data(chunks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Prepare data for frontend visualization"""
    return {
        "chunk_timeline": [
            {
                "index": i,
                "start_char": chunk["metadata"].get("start_char", 0),
                "end_char": chunk["metadata"].get("end_char", 0),
                "length": chunk["content_length"],
                "quality": chunk["quality_score"],
                "type": chunk["chunk_type"]
            }
            for i, chunk in enumerate(chunks_data)
        ],
        "quality_heatmap": [
            {
                "index": i,
                "quality_score": chunk["quality_score"],
                "semantic_density": chunk["semantic_density"],
                "readability_score": chunk["readability_score"]
            }
            for i, chunk in enumerate(chunks_data)
        ]
    }

def _get_quality_distribution(chunks_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get quality assessment distribution"""
    distribution = {}
    for chunk in chunks_data:
        quality = chunk["quality_assessment"]
        distribution[quality] = distribution.get(quality, 0) + 1
    return distribution

def _analyze_chunk_quality(chunks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze overall chunk quality"""
    if not chunks_data:
        return {"message": "No chunks available for analysis"}
    
    quality_scores = [chunk["quality_score"] for chunk in chunks_data if isinstance(chunk["quality_score"], (int, float))]
    
    return {
        "total_chunks": len(chunks_data),
        "average_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
        "quality_range": {
            "min": min(quality_scores) if quality_scores else 0.0,
            "max": max(quality_scores) if quality_scores else 0.0
        },
        "quality_buckets": {
            "excellent": len([q for q in quality_scores if q >= 0.85]),
            "good": len([q for q in quality_scores if 0.75 <= q < 0.85]),
            "acceptable": len([q for q in quality_scores if 0.6 <= q < 0.75]),
            "poor": len([q for q in quality_scores if q < 0.6])
        }
    }

def _generate_quality_recommendations(quality_analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on quality analysis"""
    recommendations = []
    
    if quality_analysis.get("average_quality", 0) < 0.7:
        recommendations.append("Consider adjusting chunk size parameters for better quality")
    
    quality_buckets = quality_analysis.get("quality_buckets", {})
    poor_chunks = quality_buckets.get("poor", 0)
    total_chunks = quality_analysis.get("total_chunks", 1)
    
    if poor_chunks / total_chunks > 0.2:
        recommendations.append("High percentage of poor quality chunks - review chunking strategy")
    
    if not recommendations:
        recommendations.append("Chunk quality is good - no immediate actions needed")
    
    return recommendations

def _analyze_chunk_distribution(chunks_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze chunk size and type distribution"""
    if not chunks_data:
        return {}
    
    lengths = [chunk["content_length"] for chunk in chunks_data]
    
    return {
        "size_distribution": {
            "small": len([l for l in lengths if l < 300]),
            "medium": len([l for l in lengths if 300 <= l < 800]),
            "large": len([l for l in lengths if l >= 800])
        },
        "average_size": sum(lengths) / len(lengths),
        "size_range": {
            "min": min(lengths),
            "max": max(lengths)
        }
    }

def _analyze_quality_distribution(quality_scores: List[float]) -> Dict[str, int]:
    """Analyze quality score distribution"""
    if not quality_scores:
        return {"excellent": 0, "good": 0, "acceptable": 0, "poor": 0}
    
    return {
        "excellent": len([q for q in quality_scores if q >= 0.85]),
        "good": len([q for q in quality_scores if 0.75 <= q < 0.85]),
        "acceptable": len([q for q in quality_scores if 0.6 <= q < 0.75]),
        "poor": len([q for q in quality_scores if q < 0.6])
    }

def _analyze_chunk_types(chunks: List[Dict[str, Any]]) -> Dict[str, int]:
    """Analyze chunk types distribution"""
    types = {}
    for chunk in chunks:
        chunk_type = chunk.get('chunk_type', 'unknown')
        types[chunk_type] = types.get(chunk_type, 0) + 1
    return types

def _calculate_system_analytics(all_chunks: List[Dict[str, Any]], files: List[Any]) -> Dict[str, Any]:
    """Calculate system-wide analytics"""
    if not all_chunks:
        return {"message": "No chunks available"}
    
    chunk_lengths = [len(c['content']) for c in all_chunks]
    quality_scores = [c.get('quality_score', 0.0) for c in all_chunks]
    
    return {
        "chunk_size_stats": {
            "avg_size": sum(chunk_lengths) / len(chunk_lengths),
            "min_size": min(chunk_lengths),
            "max_size": max(chunk_lengths),
            "std_deviation": _calculate_std_dev(chunk_lengths),
            "size_distribution": {
                "small": len([l for l in chunk_lengths if l < 300]),
                "medium": len([l for l in chunk_lengths if 300 <= l < 800]),
                "large": len([l for l in chunk_lengths if l >= 800])
            }
        },
        "quality_stats": {
            "avg_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "quality_std_dev": _calculate_std_dev(quality_scores),
            "quality_range": {"min": min(quality_scores), "max": max(quality_scores)} if quality_scores else {"min": 0, "max": 0}
        },
        "indexing_timeline": _analyze_indexing_timeline(files),
        "content_density": sum(len(c['content']) for c in all_chunks) / len(files) if files else 0
    }

def _calculate_performance_metrics(all_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate performance metrics"""
    if not all_chunks:
        return {"message": "No performance data available"}
    
    semantic_densities = [c.get('semantic_density', 0.0) for c in all_chunks]
    readability_scores = [c.get('readability_score', 0.0) for c in all_chunks]
    
    return {
        "embedding_efficiency": {
            "avg_semantic_density": sum(semantic_densities) / len(semantic_densities) if semantic_densities else 0,
            "high_density_chunks": len([d for d in semantic_densities if d > 0.8]),
            "low_density_chunks": len([d for d in semantic_densities if d < 0.3])
        },
        "readability_metrics": {
            "avg_readability": sum(readability_scores) / len(readability_scores) if readability_scores else 0,
            "highly_readable": len([r for r in readability_scores if r > 0.7]),
            "poorly_readable": len([r for r in readability_scores if r < 0.3])
        },
        "retrieval_potential": {
            "optimal_chunks": len([c for c in all_chunks if c.get('quality_score', 0) > 0.8 and len(c['content']) > 200]),
            "suboptimal_chunks": len([c for c in all_chunks if c.get('quality_score', 0) < 0.6 or len(c['content']) < 100])
        }
    }

def _generate_quality_insights(all_chunks: List[Dict[str, Any]]) -> List[str]:
    """Generate quality insights"""
    insights = []
    
    if not all_chunks:
        return ["No chunks available for analysis"]
    
    quality_scores = [c.get('quality_score', 0.0) for c in all_chunks]
    avg_quality = sum(quality_scores) / len(quality_scores)
    
    if avg_quality > 0.8:
        insights.append("🟢 Excellent overall chunk quality detected")
    elif avg_quality > 0.6:
        insights.append("🟡 Good chunk quality with room for improvement")
    else:
        insights.append("🔴 Chunk quality needs attention")
    
    chunk_lengths = [len(c['content']) for c in all_chunks]
    avg_length = sum(chunk_lengths) / len(chunk_lengths)
    
    if avg_length > 1000:
        insights.append("📏 Chunks are relatively long - consider more granular chunking")
    elif avg_length < 200:
        insights.append("📏 Chunks are quite short - may lose context")
    
    return insights

def _generate_enterprise_recommendations(all_chunks: List[Dict[str, Any]], files: List[Any]) -> List[str]:
    """Generate enterprise-level recommendations"""
    recommendations = []
    
    if not all_chunks:
        return ["No data available for recommendations"]
    
    # Quality-based recommendations
    quality_scores = [c.get('quality_score', 0.0) for c in all_chunks]
    poor_quality_count = len([q for q in quality_scores if q < 0.6])
    
    if poor_quality_count > len(all_chunks) * 0.2:
        recommendations.append("🔧 Consider reprocessing files with poor chunk quality")
    
    # Size-based recommendations
    chunk_lengths = [len(c['content']) for c in all_chunks]
    large_chunks = len([l for l in chunk_lengths if l > 1500])
    
    if large_chunks > len(all_chunks) * 0.3:
        recommendations.append("✂️ Consider reducing chunk size for better retrieval performance")
    
    # Indexing recommendations
    ready_files = len([f for f in files if f.status == 'ready'])
    if ready_files < len(files):
        recommendations.append("📁 Some files are not fully indexed - check processing status")
    
    return recommendations

def _calculate_std_dev(values: List[float]) -> float:
    """Calculate standard deviation"""
    if len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5

def _analyze_indexing_timeline(files: List[Any]) -> Dict[str, Any]:
    """Analyze indexing timeline"""
    if not files:
        return {"message": "No files to analyze"}
    
    indexed_files = [f for f in files if f.indexed_at]
    
    if not indexed_files:
        return {"message": "No indexed files found"}
    
    # Convert string dates to datetime for analysis
    from datetime import datetime
    
    timeline = []
    for file in indexed_files:
        try:
            if isinstance(file.indexed_at, str):
                indexed_time = datetime.fromisoformat(file.indexed_at.replace('Z', '+00:00'))
            else:
                indexed_time = file.indexed_at
            timeline.append({
                "filename": file.filename,
                "indexed_at": indexed_time.isoformat(),
                "chunks": file.chunk_count or 0
            })
        except Exception:
            continue
    
    return {
        "total_indexed": len(timeline),
        "indexing_history": sorted(timeline, key=lambda x: x["indexed_at"], reverse=True)[:10]
    }

def _assess_system_health(files: List[Any]) -> Dict[str, Any]:
    """Assess overall system health"""
    total_files = len(files)
    if total_files == 0:
        return {"status": "no_data", "message": "No files in system"}
    
    indexed_files = len([f for f in files if f.status == 'indexed'])
    failed_files = len([f for f in files if f.status == 'error'])
    
    success_rate = indexed_files / total_files
    
    if success_rate >= 0.95:
        status = "excellent"
    elif success_rate >= 0.8:
        status = "good"
    elif success_rate >= 0.6:
        status = "fair"
    else:
        status = "poor"
    
    return {
        "status": status,
        "success_rate": round(success_rate * 100, 1),
        "indexed_files": indexed_files,
        "total_files": total_files,
        "failed_files": failed_files
    }