"""
🔬 Evaluation API Endpoints
Wissenschaftliche Metriken und Performance-Analyse für Bachelorarbeit
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from app.services.evaluation_service import evaluation_service
from app.models.database import get_db
from app.models.evaluation import (
    EvaluationMetric,
    QueryEvaluation,
    PerformanceSnapshot,
    ABTestResult,
    EvaluationAlert,
    get_recent_metrics,
    get_performance_trends,
    get_active_alerts
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/metrics")
async def get_current_metrics():
    """
    Aktuelle Evaluation-Metriken abrufen
    
    Returns:
        Aktuelle Performance-Metriken der letzten 10 Queries
    """
    try:
        metrics = await evaluation_service.get_current_metrics()
        return {
            "status": "success",
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Metriken: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report")
async def get_performance_report(
    days: int = Query(default=7, ge=1, le=30, description="Zeitraum in Tagen")
):
    """
    Detaillierten Performance-Bericht generieren
    
    Args:
        days: Anzahl der Tage für den Bericht (1-30)
    
    Returns:
        Umfassender Performance-Bericht mit wissenschaftlichen Metriken
    """
    try:
        report = await evaluation_service.generate_performance_report(days)
        
        return {
            "status": "success",
            "report": {
                "evaluation_period": report.evaluation_period,
                "total_queries": report.total_queries,
                "average_metrics": {
                    "response_time": round(report.avg_response_time, 3),
                    "relevance_score": round(report.avg_relevance_score, 3),
                    "completeness_score": round(report.avg_completeness_score, 3),
                    "confidence_accuracy": round(report.avg_confidence_accuracy, 3),
                    "hallucination_score": round(report.avg_hallucination_score, 3),
                    "user_satisfaction": round(report.avg_user_satisfaction, 3),
                    "overall_score": round(report.avg_overall_score, 3)
                },
                "top_performing_queries": report.top_performing_queries,
                "worst_performing_queries": report.worst_performing_queries,
                "improvement_recommendations": report.improvement_recommendations,
                "statistical_insights": report.statistical_insights
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Fehler beim Generieren des Reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/manual")
async def manual_evaluation(
    query: str,
    response: str,
    sources: List[str] = [],
    confidence: float = 0.9,
    response_time: float = 2.0,
    context: str = ""
):
    """
    Manuelle Evaluierung einer Antwort durchführen
    
    Args:
        query: Die gestellte Frage
        response: Die generierte Antwort
        sources: Verwendete Quellen
        confidence: Confidence Score
        response_time: Antwortzeit in Sekunden
        context: Kontext für die Evaluierung
    
    Returns:
        Evaluation-Metriken für die Antwort
    """
    try:
        metric = await evaluation_service.evaluate_response_quality(
            query=query,
            response=response,
            sources=sources,
            confidence=confidence,
            response_time=response_time,
            context=context
        )
        
        return {
            "status": "success",
            "evaluation": {
                "overall_score": round(metric.overall_score, 3),
                "relevance_score": round(metric.relevance_score, 3),
                "completeness_score": round(metric.completeness_score, 3),
                "confidence_accuracy": round(metric.confidence_accuracy, 3),
                "hallucination_score": round(metric.hallucination_score, 3),
                "source_quality": round(metric.source_quality, 3),
                "user_satisfaction": round(metric.user_satisfaction, 3),
                "metadata": metric.metadata
            },
            "timestamp": metric.timestamp.isoformat()
        }
    except Exception as e:
        logger.error(f"Fehler bei manueller Evaluierung: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_evaluation_history(
    hours: int = Query(default=24, ge=1, le=168, description="Zeitraum in Stunden"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximale Anzahl Einträge")
):
    """
    Evaluierungs-Historie abrufen
    
    Args:
        hours: Zeitraum in Stunden (1-168)
        limit: Maximale Anzahl von Einträgen
    
    Returns:
        Liste der letzten Evaluierungen
    """
    try:
        # Aus In-Memory Historie
        all_metrics = evaluation_service.metrics_history
        
        # Filter nach Zeitraum
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            m for m in all_metrics 
            if m.timestamp >= cutoff_time
        ]
        
        # Sortiere nach Zeit (neueste zuerst) und limitiere
        recent_metrics.sort(key=lambda x: x.timestamp, reverse=True)
        recent_metrics = recent_metrics[:limit]
        
        return {
            "status": "success",
            "count": len(recent_metrics),
            "metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "query": m.query[:100] + "..." if len(m.query) > 100 else m.query,
                    "overall_score": round(m.overall_score, 3),
                    "relevance_score": round(m.relevance_score, 3),
                    "completeness_score": round(m.completeness_score, 3),
                    "hallucination_score": round(m.hallucination_score, 3),
                    "response_time": round(m.response_time, 3),
                    "sources_count": m.sources_count
                }
                for m in recent_metrics
            ]
        }
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Historie: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_performance_trends(
    metric: str = Query(
        default="overall_score",
        description="Metrik für Trend-Analyse",
        regex="^(overall_score|relevance_score|completeness_score|hallucination_score|response_time)$"
    ),
    days: int = Query(default=7, ge=1, le=30, description="Zeitraum in Tagen")
):
    """
    Performance-Trends analysieren
    
    Args:
        metric: Zu analysierende Metrik
        days: Zeitraum für Trend-Analyse
    
    Returns:
        Trend-Daten für die gewählte Metrik
    """
    try:
        # Gruppiere Metriken nach Tag
        cutoff_date = datetime.now() - timedelta(days=days)
        metrics = [m for m in evaluation_service.metrics_history if m.timestamp >= cutoff_date]
        
        if not metrics:
            return {
                "status": "no_data",
                "message": "Keine Daten für den gewählten Zeitraum"
            }
        
        # Gruppiere nach Tag
        daily_data = {}
        for m in metrics:
            date_key = m.timestamp.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = []
            
            # Extrahiere gewünschte Metrik
            if metric == "overall_score":
                value = m.overall_score
            elif metric == "relevance_score":
                value = m.relevance_score
            elif metric == "completeness_score":
                value = m.completeness_score
            elif metric == "hallucination_score":
                value = m.hallucination_score
            elif metric == "response_time":
                value = m.response_time
            
            daily_data[date_key].append(value)
        
        # Berechne Tagesdurchschnitte
        import statistics
        trend_data = []
        for date, values in sorted(daily_data.items()):
            trend_data.append({
                "date": date,
                "value": round(statistics.mean(values), 3),
                "min": round(min(values), 3),
                "max": round(max(values), 3),
                "count": len(values)
            })
        
        return {
            "status": "success",
            "metric": metric,
            "period": f"{days} days",
            "trend_data": trend_data,
            "summary": {
                "current_avg": round(statistics.mean([d["value"] for d in trend_data[-3:]]), 3) if len(trend_data) >= 3 else trend_data[-1]["value"],
                "previous_avg": round(statistics.mean([d["value"] for d in trend_data[:3]]), 3) if len(trend_data) >= 3 else trend_data[0]["value"],
                "trend": "improving" if trend_data[-1]["value"] > trend_data[0]["value"] else "declining"
            }
        }
    except Exception as e:
        logger.error(f"Fehler bei Trend-Analyse: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_evaluation_alerts():
    """
    Aktive Performance-Alerts abrufen
    
    Returns:
        Liste aktiver Alerts für Performance-Probleme
    """
    try:
        # Analysiere aktuelle Metriken für Alerts
        alerts = []
        
        if evaluation_service.metrics_history:
            recent_metrics = evaluation_service.metrics_history[-10:]
            import statistics
            
            # Check für niedrige Overall Scores
            avg_score = statistics.mean([m.overall_score for m in recent_metrics])
            if avg_score < 0.7:
                alerts.append({
                    "type": "low_performance",
                    "severity": "high",
                    "title": "Niedrige Gesamt-Performance",
                    "description": f"Durchschnittlicher Overall Score nur {avg_score:.2f}",
                    "metric_value": avg_score,
                    "threshold": 0.7,
                    "recommendations": [
                        "Prompt-Optimierung durchführen",
                        "Training Data erweitern",
                        "RAG-Parameter anpassen"
                    ]
                })
            
            # Check für Halluzinationen
            hallucination_incidents = sum(1 for m in recent_metrics if m.hallucination_score < 0.7)
            if hallucination_incidents > 2:
                alerts.append({
                    "type": "hallucination",
                    "severity": "critical",
                    "title": "Häufige Halluzinationen erkannt",
                    "description": f"{hallucination_incidents} von 10 Antworten zeigen Halluzinationen",
                    "metric_value": hallucination_incidents,
                    "threshold": 2,
                    "recommendations": [
                        "Fact-Checking verstärken",
                        "Quellen-Validierung verbessern",
                        "Mistral-Parameter anpassen"
                    ]
                })
            
            # Check für langsame Response Times
            slow_responses = sum(1 for m in recent_metrics if m.response_time > 5.0)
            if slow_responses > 3:
                alerts.append({
                    "type": "performance",
                    "severity": "medium",
                    "title": "Langsame Antwortzeiten",
                    "description": f"{slow_responses} Antworten über 5 Sekunden",
                    "metric_value": slow_responses,
                    "threshold": 3,
                    "recommendations": [
                        "RAG-Pipeline optimieren",
                        "Vector-Search beschleunigen",
                        "Cache implementieren"
                    ]
                })
        
        return {
            "status": "success",
            "alert_count": len(alerts),
            "alerts": alerts,
            "checked_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
async def clear_evaluation_history():
    """
    Evaluierungs-Historie löschen (nur für Testing)
    
    Returns:
        Bestätigung der Löschung
    """
    try:
        previous_count = len(evaluation_service.metrics_history)
        evaluation_service.clear_metrics_history()
        
        return {
            "status": "success",
            "message": f"Evaluierungs-Historie gelöscht",
            "deleted_count": previous_count
        }
    except Exception as e:
        logger.error(f"Fehler beim Löschen der Historie: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def evaluation_health_check():
    """
    Health-Check für Evaluation Service
    
    Returns:
        Status des Evaluation Service
    """
    try:
        metrics_count = len(evaluation_service.metrics_history)
        
        return {
            "status": "healthy",
            "service": "evaluation",
            "metrics_in_memory": metrics_count,
            "metric_weights": evaluation_service.metric_weights,
            "hallucination_patterns": len(evaluation_service.hallucination_patterns),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }