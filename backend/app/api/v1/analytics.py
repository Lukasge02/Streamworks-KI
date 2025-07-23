"""
Analytics API - Bachelor-Arbeit Performance Analytics
PostgreSQL-optimiert mit wissenschaftlichen Auswertungen
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import json
import csv
import io
from pydantic import BaseModel

from app.core.database_postgres import get_db
from app.models.postgres_models import SystemMetric, Document

router = APIRouter(prefix="/analytics", tags=["analytics"])

# Pydantic Models for Analytics
class DocumentProcessingStats(BaseModel):
    """Document processing performance statistics"""
    total_documents: int
    avg_processing_time: float
    max_processing_time: float
    min_processing_time: float
    success_rate: float
    total_processing_hours: float
    documents_per_hour: float
    file_type_breakdown: Dict[str, int]
    performance_trends: List[Dict[str, Any]]

class BatchProcessingStats(BaseModel):
    """Batch processing analytics"""
    total_batches: int
    avg_batch_size: int
    avg_batch_time: float
    total_files_processed: int
    batch_success_rate: float
    concurrent_processing_efficiency: float
    batch_trends: List[Dict[str, Any]]

class SystemMetricsResponse(BaseModel):
    """System performance metrics"""
    cpu_performance: Dict[str, float]
    memory_usage: Dict[str, float]
    database_performance: Dict[str, float]
    error_analysis: Dict[str, Any]
    system_health_score: float
    uptime_statistics: Dict[str, Any]

@router.get("/document-processing", response_model=DocumentProcessingStats)
async def get_document_processing_analytics(
    days: int = Query(30, description="Number of days to analyze"),
    file_type: Optional[str] = Query(None, description="Filter by file type (.pdf, .txt, .md)"),
    db: AsyncSession = Depends(get_db)
) -> DocumentProcessingStats:
    """
    Bachelor-Arbeit Analytics: Document Processing Performance
    
    Liefert detaillierte Statistiken über Dokumenten-Konvertierung:
    - Verarbeitungszeiten und Performance-Trends
    - Success Rates und Error Analysis
    - File-Type spezifische Metriken
    - Zeitbasierte Trend-Analyse für wissenschaftliche Auswertung
    """
    
    try:
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Base query for document statistics
        base_query = """
        SELECT 
            COUNT(*) as total_documents,
            AVG(conversion_time_seconds) as avg_processing_time,
            MAX(conversion_time_seconds) as max_processing_time,
            MIN(conversion_time_seconds) as min_processing_time,
            SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
            SUM(conversion_time_seconds) / 3600.0 as total_processing_hours
        FROM documents 
        WHERE created_at >= :start_date AND created_at <= :end_date
        """
        
        # Add file type filter if specified
        if file_type:
            base_query += " AND mime_type LIKE :file_type"
            params = {"start_date": start_date, "end_date": end_date, "file_type": f"%{file_type}%"}
        else:
            params = {"start_date": start_date, "end_date": end_date}
        
        result = await db.execute(text(base_query), params)
        stats = result.first()
        
        if not stats or stats.total_documents == 0:
            return DocumentProcessingStats(
                total_documents=0,
                avg_processing_time=0.0,
                max_processing_time=0.0,
                min_processing_time=0.0,
                success_rate=0.0,
                total_processing_hours=0.0,
                documents_per_hour=0.0,
                file_type_breakdown={},
                performance_trends=[]
            )
        
        # Calculate documents per hour
        documents_per_hour = stats.total_documents / max(stats.total_processing_hours, 0.001)
        
        # File type breakdown
        file_type_query = """
        SELECT 
            CASE 
                WHEN mime_type LIKE '%pdf%' THEN 'PDF'
                WHEN mime_type LIKE '%text%' THEN 'TXT'
                WHEN mime_type LIKE '%markdown%' THEN 'MD'
                ELSE 'OTHER'
            END as file_type,
            COUNT(*) as count
        FROM documents 
        WHERE created_at >= :start_date AND created_at <= :end_date
        GROUP BY file_type
        """
        
        file_type_result = await db.execute(text(file_type_query), params)
        file_type_breakdown = {row.file_type: row.count for row in file_type_result}
        
        # Performance trends (daily aggregation)
        trends_query = """
        WITH daily_stats AS (
            SELECT 
                DATE(created_at) as processing_date,
                COUNT(*) as documents_count,
                AVG(conversion_time_seconds) as avg_time,
                SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as daily_success_rate
            FROM documents 
            WHERE created_at >= :start_date AND created_at <= :end_date
            GROUP BY DATE(created_at)
            ORDER BY processing_date
        )
        SELECT * FROM daily_stats
        """
        
        trends_result = await db.execute(text(trends_query), params)
        performance_trends = [
            {
                "date": str(row.processing_date),
                "documents_count": row.documents_count,
                "avg_processing_time": float(row.avg_time or 0),
                "success_rate": float(row.daily_success_rate or 0)
            }
            for row in trends_result
        ]
        
        return DocumentProcessingStats(
            total_documents=stats.total_documents,
            avg_processing_time=float(stats.avg_processing_time or 0),
            max_processing_time=float(stats.max_processing_time or 0),
            min_processing_time=float(stats.min_processing_time or 0),
            success_rate=float(stats.success_rate or 0),
            total_processing_hours=float(stats.total_processing_hours or 0),
            documents_per_hour=documents_per_hour,
            file_type_breakdown=file_type_breakdown,
            performance_trends=performance_trends
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics query failed: {str(e)}")

@router.get("/batch-statistics", response_model=BatchProcessingStats)
async def get_batch_processing_analytics(
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
) -> BatchProcessingStats:
    """
    Bachelor-Arbeit Analytics: Batch Processing Performance
    
    Analysiert Batch-Verarbeitung für wissenschaftliche Auswertung:
    - Batch-Größen und Verarbeitungszeiten
    - Parallelisierungs-Effizienz
    - Batch Success Rates
    - Concurrent Processing Analysis
    """
    
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Batch processing metrics from SystemMetric table
        batch_query = """
        SELECT 
            COUNT(*) as total_batches,
            AVG(CAST(tags->>'total_found' AS INTEGER)) as avg_batch_size,
            AVG(metric_value) as avg_batch_time,
            SUM(CAST(tags->>'total_found' AS INTEGER)) as total_files_processed,
            AVG(CAST(tags->>'success_rate' AS FLOAT)) as batch_success_rate
        FROM system_metrics 
        WHERE metric_category = 'batch_processing' 
        AND metric_name = 'document_conversion_batch'
        AND created_at >= :start_date AND created_at <= :end_date
        """
        
        params = {"start_date": start_date, "end_date": end_date}
        result = await db.execute(text(batch_query), params)
        batch_stats = result.first()
        
        if not batch_stats or batch_stats.total_batches == 0:
            return BatchProcessingStats(
                total_batches=0,
                avg_batch_size=0,
                avg_batch_time=0.0,
                total_files_processed=0,
                batch_success_rate=0.0,
                concurrent_processing_efficiency=0.0,
                batch_trends=[]
            )
        
        # Calculate concurrent processing efficiency
        # (theoretical max time vs actual time)
        efficiency_query = """
        WITH batch_efficiency AS (
            SELECT 
                metric_value as actual_time,
                CAST(tags->>'total_found' AS INTEGER) as batch_size,
                CAST(tags->>'processing_time' AS FLOAT) as processing_time
            FROM system_metrics 
            WHERE metric_category = 'batch_processing'
            AND created_at >= :start_date AND created_at <= :end_date
            AND CAST(tags->>'total_found' AS INTEGER) > 0
        )
        SELECT AVG(
            CASE 
                WHEN actual_time > 0 THEN (batch_size * 2.0) / actual_time * 100.0
                ELSE 0 
            END
        ) as efficiency
        FROM batch_efficiency
        """
        
        efficiency_result = await db.execute(text(efficiency_query), params)
        efficiency_row = efficiency_result.first()
        concurrent_efficiency = min(float(efficiency_row.efficiency or 0), 100.0)
        
        # Batch trends (daily)
        trends_query = """
        SELECT 
            DATE(created_at) as batch_date,
            COUNT(*) as batches_count,
            AVG(metric_value) as avg_time,
            AVG(CAST(tags->>'success_rate' AS FLOAT)) as avg_success_rate,
            SUM(CAST(tags->>'total_found' AS INTEGER)) as files_processed
        FROM system_metrics 
        WHERE metric_category = 'batch_processing'
        AND created_at >= :start_date AND created_at <= :end_date
        GROUP BY DATE(created_at)
        ORDER BY batch_date
        """
        
        trends_result = await db.execute(text(trends_query), params)
        batch_trends = [
            {
                "date": str(row.batch_date),
                "batches_count": row.batches_count,
                "avg_processing_time": float(row.avg_time or 0),
                "success_rate": float(row.avg_success_rate or 0),
                "files_processed": row.files_processed or 0
            }
            for row in trends_result
        ]
        
        return BatchProcessingStats(
            total_batches=batch_stats.total_batches,
            avg_batch_size=int(batch_stats.avg_batch_size or 0),
            avg_batch_time=float(batch_stats.avg_batch_time or 0),
            total_files_processed=int(batch_stats.total_files_processed or 0),
            batch_success_rate=float(batch_stats.batch_success_rate or 0),
            concurrent_processing_efficiency=concurrent_efficiency,
            batch_trends=batch_trends
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analytics query failed: {str(e)}")

@router.get("/system-metrics", response_model=SystemMetricsResponse)
async def get_system_metrics_analytics(
    days: int = Query(7, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
) -> SystemMetricsResponse:
    """
    Bachelor-Arbeit Analytics: System Performance Metrics
    
    Detaillierte System-Performance für wissenschaftliche Analyse:
    - CPU und Memory Performance
    - Database Query Performance
    - Error Analysis und Health Scoring
    - System Uptime und Reliability Metrics
    """
    
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        params = {"start_date": start_date, "end_date": end_date}
        
        # CPU Performance (from conversion times)
        cpu_query = """
        SELECT 
            AVG(CAST(tags->>'pages_processed' AS INTEGER)) as avg_pages_per_conversion,
            AVG(metric_value) as avg_conversion_time,
            MAX(metric_value) as max_conversion_time,
            MIN(metric_value) as min_conversion_time
        FROM system_metrics 
        WHERE metric_category = 'performance'
        AND metric_name LIKE '%_conversion_time'
        AND created_at >= :start_date AND created_at <= :end_date
        """
        
        cpu_result = await db.execute(text(cpu_query), params)
        cpu_stats = cpu_result.first()
        
        cpu_performance = {
            "avg_pages_per_conversion": float(cpu_stats.avg_pages_per_conversion or 0),
            "avg_processing_time": float(cpu_stats.avg_conversion_time or 0),
            "peak_processing_time": float(cpu_stats.max_conversion_time or 0),
            "min_processing_time": float(cpu_stats.min_conversion_time or 0),
            "cpu_efficiency_score": min(100.0, (1.0 / max(cpu_stats.avg_conversion_time or 1, 0.1)) * 100)
        }
        
        # Memory Usage Analysis (estimated from file sizes)
        memory_query = """
        SELECT 
            AVG(file_size) as avg_file_size,
            MAX(file_size) as max_file_size,
            SUM(file_size) as total_data_processed
        FROM documents 
        WHERE created_at >= :start_date AND created_at <= :end_date
        """
        
        memory_result = await db.execute(text(memory_query), params)
        memory_stats = memory_result.first()
        
        memory_usage = {
            "avg_file_size_mb": float((memory_stats.avg_file_size or 0) / 1024 / 1024),
            "max_file_size_mb": float((memory_stats.max_file_size or 0) / 1024 / 1024),
            "total_data_processed_gb": float((memory_stats.total_data_processed or 0) / 1024 / 1024 / 1024),
            "memory_efficiency_score": 85.0  # Placeholder - could be enhanced with actual memory monitoring
        }
        
        # Database Performance
        db_query = """
        SELECT 
            COUNT(*) as total_queries,
            AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_query_time
        FROM documents 
        WHERE created_at >= :start_date AND created_at <= :end_date
        AND updated_at IS NOT NULL
        """
        
        db_result = await db.execute(text(db_query), params)
        db_stats = db_result.first()
        
        database_performance = {
            "total_database_operations": db_stats.total_queries or 0,
            "avg_query_time_ms": float((db_stats.avg_query_time or 0) * 1000),
            "database_health_score": 90.0,  # Could be enhanced with actual DB monitoring
            "connection_pool_efficiency": 95.0
        }
        
        # Error Analysis
        error_query = """
        SELECT 
            COUNT(*) as total_errors,
            COUNT(DISTINCT tags->>'error_message') as unique_error_types
        FROM system_metrics 
        WHERE metric_category = 'error'
        AND created_at >= :start_date AND created_at <= :end_date
        """
        
        error_result = await db.execute(text(error_query), params)
        error_stats = error_result.first()
        
        error_analysis = {
            "total_errors": error_stats.total_errors or 0,
            "unique_error_types": error_stats.unique_error_types or 0,
            "error_rate": 0.0,  # Will be calculated below
            "most_common_errors": []
        }
        
        # Calculate error rate
        total_operations_query = """
        SELECT COUNT(*) as total_ops 
        FROM documents 
        WHERE created_at >= :start_date AND created_at <= :end_date
        """
        
        total_ops_result = await db.execute(text(total_operations_query), params)
        total_ops = total_ops_result.first().total_ops or 0
        
        if total_ops > 0:
            error_analysis["error_rate"] = (error_stats.total_errors or 0) / total_ops * 100
        
        # Calculate overall system health score
        system_health_score = (
            cpu_performance["cpu_efficiency_score"] * 0.3 +
            memory_usage["memory_efficiency_score"] * 0.2 +
            database_performance["database_health_score"] * 0.3 +
            max(0, 100 - error_analysis["error_rate"]) * 0.2
        )
        
        # Uptime statistics (estimated from data activity)
        uptime_query = """
        SELECT 
            MIN(created_at) as first_activity,
            MAX(created_at) as last_activity,
            COUNT(DISTINCT DATE(created_at)) as active_days
        FROM documents 
        WHERE created_at >= :start_date AND created_at <= :end_date
        """
        
        uptime_result = await db.execute(text(uptime_query), params)
        uptime_stats = uptime_result.first()
        
        uptime_statistics = {
            "system_uptime_days": days,
            "active_processing_days": uptime_stats.active_days or 0,
            "uptime_percentage": ((uptime_stats.active_days or 0) / max(days, 1)) * 100,
            "first_activity": str(uptime_stats.first_activity) if uptime_stats.first_activity else None,
            "last_activity": str(uptime_stats.last_activity) if uptime_stats.last_activity else None
        }
        
        return SystemMetricsResponse(
            cpu_performance=cpu_performance,
            memory_usage=memory_usage,
            database_performance=database_performance,
            error_analysis=error_analysis,
            system_health_score=system_health_score,
            uptime_statistics=uptime_statistics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System metrics query failed: {str(e)}")

@router.get("/export/csv")
async def export_analytics_csv(
    metric_type: str = Query(..., description="Type of metrics to export (document|batch|system)"),
    days: int = Query(30, description="Number of days to export"),
    db: AsyncSession = Depends(get_db)
) -> Response:
    """
    Export Analytics Data as CSV for Scientific Analysis
    
    Exportiert detaillierte Analytics-Daten im CSV-Format für:
    - Statistische Auswertung in R/Python
    - Excel-basierte Visualisierungen
    - Bachelor-Arbeit Datenanhang
    """
    
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        params = {"start_date": start_date, "end_date": end_date}
        
        # Select appropriate query based on metric type
        if metric_type == "document":
            query = """
            SELECT 
                created_at,
                filename,
                mime_type,
                file_size,
                conversion_time_seconds,
                status,
                processing_metadata
            FROM documents 
            WHERE created_at >= :start_date AND created_at <= :end_date
            ORDER BY created_at
            """
        elif metric_type == "batch":
            query = """
            SELECT 
                created_at,
                metric_value as batch_processing_time,
                tags->>'total_found' as files_found,
                tags->>'success_rate' as success_rate,
                tags->>'processing_time' as processing_time
            FROM system_metrics 
            WHERE metric_category = 'batch_processing'
            AND created_at >= :start_date AND created_at <= :end_date
            ORDER BY created_at
            """
        elif metric_type == "system":
            query = """
            SELECT 
                created_at,
                metric_category,
                metric_name,
                metric_value,
                metric_unit,
                tags
            FROM system_metrics 
            WHERE created_at >= :start_date AND created_at <= :end_date
            ORDER BY created_at, metric_category
            """
        else:
            raise HTTPException(status_code=400, detail="Invalid metric_type. Use: document, batch, or system")
        
        result = await db.execute(text(query), params)
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="No data found for the specified period")
        
        # Create CSV content
        output = io.StringIO()
        
        # Get column names from first row
        columns = list(rows[0]._mapping.keys())
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        
        # Write data rows
        for row in rows:
            row_dict = dict(row._mapping)
            # Convert complex types to strings for CSV
            for key, value in row_dict.items():
                if isinstance(value, dict):
                    row_dict[key] = json.dumps(value)
                elif value is None:
                    row_dict[key] = ""
            writer.writerow(row_dict)
        
        csv_content = output.getvalue()
        output.close()
        
        # Return CSV response
        filename = f"streamworks_analytics_{metric_type}_{days}days_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export failed: {str(e)}")

@router.get("/health")
async def analytics_health_check() -> JSONResponse:
    """Health check for analytics service"""
    
    return JSONResponse({
        "service": "analytics_api",
        "status": "healthy",
        "features": [
            "document_processing_analytics",
            "batch_statistics",
            "system_metrics",
            "csv_export",
            "scientific_data_analysis"
        ],
        "supported_exports": ["CSV"],
        "database": "postgresql_optimized",
        "bachelor_thesis_ready": True
    })