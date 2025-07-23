"""
Analytics Service für Bachelor-Arbeit Performance Evaluation
"""
import asyncio
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import text

from app.core.database_postgres import get_db_session
from app.models.postgres_models import ChatSession, Document, DocumentChunk, SystemMetric

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Analytics Service für wissenschaftliche Evaluation"""
    
    async def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Performance Summary für Bachelor-Arbeit Dashboard"""
        
        async with get_db_session() as session:
            # Query from analytics view
            result = await session.execute(text("""
            SELECT 
                COUNT(*) as total_queries,
                AVG(total_processing_time) as avg_processing_time,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_processing_time) as p95_processing_time,
                AVG(confidence_score) as avg_confidence,
                COUNT(*) FILTER (WHERE confidence_score > 0.8) as high_confidence_queries,
                AVG(chunks_retrieved) as avg_chunks_retrieved
            FROM chat_sessions
            WHERE created_at > NOW() - INTERVAL '%s days'
            """ % days))
            
            row = result.first()
            
            return {
                "period_days": days,
                "total_queries": row[0] or 0,
                "avg_processing_time": float(row[1] or 0),
                "p95_processing_time": float(row[2] or 0),
                "avg_confidence": float(row[3] or 0),
                "high_confidence_queries": row[4] or 0,
                "avg_chunks_retrieved": float(row[5] or 0),
                "high_confidence_rate": (row[4] or 0) / max(row[0] or 1, 1) * 100
            }
    
    async def get_document_processing_stats(self) -> Dict[str, Any]:
        """Document Processing Performance Statistics"""
        
        async with get_db_session() as session:
            result = await session.execute(text("""
            SELECT 
                status,
                COUNT(*) as count,
                AVG(file_size / 1024.0) as avg_file_size_kb,
                AVG(conversion_time_seconds) as avg_conversion_time,
                AVG(chunk_count) as avg_chunks_per_doc
            FROM documents
            GROUP BY status
            ORDER BY count DESC
            """))
            
            stats_by_status = {}
            for row in result:
                stats_by_status[row[0]] = {
                    "count": row[1],
                    "avg_file_size_kb": float(row[2] or 0),
                    "avg_conversion_time": float(row[3] or 0),
                    "avg_chunks_per_doc": float(row[4] or 0)
                }
            
            return {
                "by_status": stats_by_status,
                "total_documents": sum(stats["count"] for stats in stats_by_status.values()),
                "processing_success_rate": (
                    stats_by_status.get("indexed", {}).get("count", 0) + 
                    stats_by_status.get("converted", {}).get("count", 0)
                ) / max(sum(stats["count"] for stats in stats_by_status.values()), 1) * 100
            }
    
    async def get_rag_effectiveness_metrics(self) -> Dict[str, Any]:
        """RAG System Effectiveness Metrics"""
        
        async with get_db_session() as session:
            # Chunk retrieval effectiveness
            result = await session.execute(text("""
            SELECT 
                content_type,
                COUNT(*) as total_chunks,
                AVG(quality_score) as avg_quality_score,
                AVG(retrieval_count) as avg_retrieval_count,
                AVG(avg_relevance_score) as avg_relevance_score,
                COUNT(*) FILTER (WHERE retrieval_count > 0) as chunks_ever_retrieved
            FROM document_chunks
            WHERE quality_score IS NOT NULL
            GROUP BY content_type
            ORDER BY avg_relevance_score DESC NULLS LAST
            """))
            
            chunk_effectiveness = []
            for row in result:
                chunk_effectiveness.append({
                    "content_type": row[0],
                    "total_chunks": row[1],
                    "avg_quality_score": float(row[2] or 0),
                    "avg_retrieval_count": float(row[3] or 0),
                    "avg_relevance_score": float(row[4] or 0),
                    "chunks_ever_retrieved": row[5],
                    "retrieval_rate": row[5] / max(row[1], 1) * 100
                })
            
            return {
                "chunk_effectiveness": chunk_effectiveness,
                "total_chunks": sum(item["total_chunks"] for item in chunk_effectiveness),
                "overall_retrieval_rate": sum(item["chunks_ever_retrieved"] for item in chunk_effectiveness) / 
                                        max(sum(item["total_chunks"] for item in chunk_effectiveness), 1) * 100
            }
    
    async def export_thesis_data(self, output_path: str = "./thesis_data.json") -> str:
        """Export all analytics data for Bachelor thesis"""
        
        logger.info("📊 Exporting thesis analytics data...")
        
        # Collect all analytics
        data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "performance_summary_7d": await self.get_performance_summary(7),
            "performance_summary_30d": await self.get_performance_summary(30),
            "document_processing": await self.get_document_processing_stats(),
            "rag_effectiveness": await self.get_rag_effectiveness_metrics(),
        }
        
        # Add detailed time series data
        async with get_db_session() as session:
            # Hourly performance over last 7 days
            result = await session.execute(text("""
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                COUNT(*) as queries,
                AVG(total_processing_time) as avg_time,
                AVG(confidence_score) as avg_confidence
            FROM chat_sessions
            WHERE created_at > NOW() - INTERVAL '7 days'
            GROUP BY hour
            ORDER BY hour
            """))
            
            hourly_performance = []
            for row in result:
                hourly_performance.append({
                    "hour": row[0].isoformat(),
                    "queries": row[1],
                    "avg_processing_time": float(row[2] or 0),
                    "avg_confidence": float(row[3] or 0)
                })
            
            data["hourly_performance_7d"] = hourly_performance
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Thesis data exported to: {output_path}")
        return output_path

# Global analytics service
analytics_service = AnalyticsService()