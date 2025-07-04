"""
🔬 StreamWorks-KI Evaluation Service
Wissenschaftliche Evaluierung der RAG-System Performance
Ziel: Quantitative Messung der AI-Antwortqualität für Bachelorarbeit
"""
import time
import logging
import statistics
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import re
import difflib
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class EvaluationMetric:
    """Einzelne Evaluierungs-Metrik"""
    timestamp: datetime
    query: str
    response: str
    response_time: float
    relevance_score: float
    completeness_score: float
    confidence_score: float
    confidence_accuracy: float
    hallucination_score: float
    source_quality: float
    user_satisfaction: float
    overall_score: float
    sources_used: List[str]
    metadata: Dict[str, Any]
    
    @property
    def sources_count(self) -> int:
        """Anzahl der verwendeten Quellen"""
        return len(self.sources_used) if self.sources_used else 0

@dataclass
class PerformanceReport:
    """Umfassender Performance-Bericht"""
    evaluation_period: str
    total_queries: int
    avg_response_time: float
    avg_relevance_score: float
    avg_completeness_score: float
    avg_confidence_accuracy: float
    avg_hallucination_score: float
    avg_user_satisfaction: float
    avg_overall_score: float
    top_performing_queries: List[Dict[str, Any]]
    worst_performing_queries: List[Dict[str, Any]]
    improvement_recommendations: List[str]
    statistical_insights: Dict[str, Any]

class EvaluationService:
    """Wissenschaftlicher Evaluation Service für StreamWorks-KI"""
    
    def __init__(self):
        self.metrics_history: List[EvaluationMetric] = []
        self.evaluation_cache = {}
        
        # Wissenschaftliche Gewichtungen für Gesamtscore
        self.metric_weights = {
            'relevance': 0.25,      # 25% - Wie relevant ist die Antwort
            'completeness': 0.20,   # 20% - Wie vollständig ist die Antwort
            'confidence_accuracy': 0.15,  # 15% - Wie genau ist der Confidence Score
            'source_quality': 0.15, # 15% - Qualität der verwendeten Quellen
            'hallucination': 0.15,  # 15% - Penalisierung für Halluzinationen
            'user_satisfaction': 0.10  # 10% - Simulierte Benutzerzufriedenheit
        }
        
        # Halluzinations-Erkennungsmuster
        self.hallucination_patterns = [
            r'PowerShell.*GUI',  # PowerShell wird fälschlicherweise mit GUI verbunden
            r'Administration.*Batch.*Navigation',  # GUI-Navigation die nicht existiert
            r'Streamworks.*Dashboard',  # Nicht existierende Dashboards
            r'Version \d+\.\d+',  # Spezifische Versionsnummern die nicht bestätigt sind
            r'seit \d{4}',  # Zeitangaben die nicht verifiziert sind
        ]
        
        logger.info("🔬 Evaluation Service initialisiert - Wissenschaftliche Metriken aktiv")
    
    async def evaluate_response_quality(self, 
                                      query: str,
                                      response: str,
                                      sources: List[str],
                                      confidence: float,
                                      response_time: float,
                                      context: str = "") -> EvaluationMetric:
        """Hauptevaluierung der Antwortqualität"""
        
        start_time = time.time()
        
        try:
            # 1. Relevanz-Score berechnen
            relevance_score = await self.calculate_relevance_score(query, response, context)
            
            # 2. Vollständigkeits-Score berechnen
            completeness_score = await self.calculate_completeness_score(query, response, sources)
            
            # 3. Confidence-Genauigkeit bewerten
            confidence_accuracy = await self.calculate_confidence_accuracy(
                response, sources, relevance_score, confidence
            )
            
            # 4. Halluzinationen erkennen
            hallucination_score = await self.detect_hallucinations(response, sources, context)
            
            # 5. Quellen-Qualität bewerten
            source_quality = await self.evaluate_source_quality(sources, query)
            
            # 6. Benutzer-Zufriedenheit simulieren
            user_satisfaction = await self.simulate_user_satisfaction(
                query, response, relevance_score, completeness_score
            )
            
            # 7. Gesamtscore berechnen
            overall_score = self.calculate_overall_score({
                'relevance': relevance_score,
                'completeness': completeness_score,
                'confidence_accuracy': confidence_accuracy,
                'source_quality': source_quality,
                'hallucination': hallucination_score,
                'user_satisfaction': user_satisfaction
            })
            
            # Metrik-Objekt erstellen
            metric = EvaluationMetric(
                timestamp=datetime.now(),
                query=query,
                response=response,
                response_time=response_time,
                relevance_score=relevance_score,
                completeness_score=completeness_score,
                confidence_score=confidence,
                confidence_accuracy=confidence_accuracy,
                hallucination_score=hallucination_score,
                source_quality=source_quality,
                user_satisfaction=user_satisfaction,
                overall_score=overall_score,
                sources_used=sources,
                metadata={
                    'evaluation_time': time.time() - start_time,
                    'context_length': len(context),
                    'response_length': len(response),
                    'sources_count': len(sources)
                }
            )
            
            # Zu Historie hinzufügen
            self.metrics_history.append(metric)
            
            logger.info(f"📊 Query evaluiert: Overall Score {overall_score:.2f}")
            return metric
            
        except Exception as e:
            logger.error(f"❌ Evaluation Fehler: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Fallback-Metrik
            return EvaluationMetric(
                timestamp=datetime.now(),
                query=query,
                response=response,
                response_time=response_time,
                relevance_score=0.5,
                completeness_score=0.5,
                confidence_score=confidence,
                confidence_accuracy=0.5,
                hallucination_score=0.5,
                source_quality=0.5,
                user_satisfaction=0.5,
                overall_score=0.5,
                sources_used=sources,
                metadata={'error': str(e)}
            )
    
    async def calculate_relevance_score(self, query: str, response: str, context: str) -> float:
        """Berechne Relevanz der Antwort zur Frage"""
        
        # Normalisiere Query und Response
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Extrahiere Keywords aus Query
        query_keywords = set(re.findall(r'\b\w{3,}\b', query_lower))
        query_keywords = {kw for kw in query_keywords if kw not in ['wie', 'was', 'wann', 'wo', 'warum', 'kann', 'ich', 'der', 'die', 'das']}
        
        if not query_keywords:
            return 0.7  # Neutral bei fehlenden Keywords
        
        # Prüfe Keyword-Übereinstimmung in Response
        matched_keywords = 0
        for keyword in query_keywords:
            if keyword in response_lower:
                matched_keywords += 1
        
        keyword_match_score = matched_keywords / len(query_keywords)
        
        # Themen-spezifische Relevanz-Bewertung
        topic_relevance = 0.0
        
        # XML/Stream-Themen
        if any(term in query_lower for term in ['xml', 'stream', 'erstell', 'generier']):
            if any(term in response_lower for term in ['xml', 'stream', 'tag', 'element', 'attribut']):
                topic_relevance += 0.3
        
        # Batch-Job-Themen
        if any(term in query_lower for term in ['batch', 'job', 'automatisierung']):
            if any(term in response_lower for term in ['batch', 'job', 'schedule', 'cron', 'zeitplan']):
                topic_relevance += 0.3
        
        # API-Themen
        if any(term in query_lower for term in ['api', 'endpoint', 'schnittstelle']):
            if any(term in response_lower for term in ['api', 'endpoint', 'http', 'request', 'response']):
                topic_relevance += 0.3
        
        # Kombiniere Scores
        relevance_score = (keyword_match_score * 0.6) + (topic_relevance * 0.4)
        
        # Normalisiere auf 0-1
        return min(max(relevance_score, 0.0), 1.0)
    
    async def calculate_completeness_score(self, query: str, response: str, sources: List[str]) -> float:
        """Berechne Vollständigkeit der Antwort"""
        
        # Basis-Score basierend auf Response-Länge
        response_length = len(response)
        length_score = min(response_length / 500, 1.0)  # Optimal bei ~500 Zeichen
        
        # Struktur-Score (Markdown, Emojis, Sections)
        structure_score = 0.0
        
        if '##' in response or '###' in response:
            structure_score += 0.2  # Überschriften
        
        if any(emoji in response for emoji in ['🔧', '📋', '🚀', '✅', '💡']):
            structure_score += 0.2  # Emojis
        
        if '•' in response or '-' in response or '1.' in response:
            structure_score += 0.2  # Listen
        
        if '```' in response:
            structure_score += 0.2  # Code-Beispiele
        
        # Quellen-Integration Score
        source_integration_score = 0.0
        if sources:
            if len(sources) >= 2:
                source_integration_score += 0.3  # Multiple Quellen
            if '[Quelle:' in response or 'Training Data' in str(sources):
                source_integration_score += 0.2  # Quellen-Zitation
        
        # Frage-spezifische Vollständigkeit
        query_specific_score = 0.0
        
        if 'wie' in query.lower():
            # "Wie"-Fragen erwarten Schritt-für-Schritt Anweisungen
            if any(indicator in response.lower() for indicator in ['schritt', 'zuerst', 'dann', 'anschließend', '1.', '2.']):
                query_specific_score += 0.3
        
        if 'was' in query.lower():
            # "Was"-Fragen erwarten Definitionen und Erklärungen
            if any(indicator in response.lower() for indicator in ['definition', 'bedeutet', 'ist ein', 'bezeichnet']):
                query_specific_score += 0.3
        
        # Kombiniere alle Scores
        completeness_score = (
            length_score * 0.3 +
            structure_score * 0.3 +
            source_integration_score * 0.2 +
            query_specific_score * 0.2
        )
        
        return min(max(completeness_score, 0.0), 1.0)
    
    async def calculate_confidence_accuracy(self, response: str, sources: List[str], 
                                          relevance_score: float, reported_confidence: float) -> float:
        """Bewerte Genauigkeit des Confidence Scores"""
        
        # Berechne "wahren" Confidence basierend auf objektiven Faktoren
        true_confidence_factors = []
        
        # Faktor 1: Quellen-Verfügbarkeit
        if sources and len(sources) > 0:
            source_confidence = min(len(sources) / 3, 1.0)  # Optimal bei 3+ Quellen
            true_confidence_factors.append(source_confidence)
        else:
            true_confidence_factors.append(0.1)  # Sehr niedrig ohne Quellen
        
        # Faktor 2: Relevanz-Score
        true_confidence_factors.append(relevance_score)
        
        # Faktor 3: Response-Spezifität
        specificity_score = 0.0
        if any(specific in response.lower() for specific in ['beispiel', 'konkret', '```', 'schritte']):
            specificity_score = 0.8
        elif any(vague in response.lower() for vague in ['möglicherweise', 'eventuell', 'unbekannt']):
            specificity_score = 0.3
        else:
            specificity_score = 0.5
        
        true_confidence_factors.append(specificity_score)
        
        # Berechne wahren Confidence
        true_confidence = statistics.mean(true_confidence_factors)
        
        # Berechne Accuracy basierend auf Abweichung
        confidence_difference = abs(reported_confidence - true_confidence)
        accuracy = 1.0 - confidence_difference
        
        return max(accuracy, 0.0)
    
    async def detect_hallucinations(self, response: str, sources: List[str], context: str) -> float:
        """Erkenne Halluzinationen in der Antwort (Höher = weniger Halluzinationen)"""
        
        hallucination_penalty = 0.0
        
        # 1. Pattern-basierte Erkennung
        for pattern in self.hallucination_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                hallucination_penalty += 0.2
                logger.warning(f"🚨 Potentielle Halluzination erkannt: {pattern}")
        
        # 2. Fakten-Überprüfung gegen Quellen
        if sources and context:
            # Extrahiere Aussagen aus Response
            statements = re.split(r'[.!?]', response)
            verified_statements = 0
            total_statements = len([s for s in statements if len(s.strip()) > 10])
            
            for statement in statements:
                if len(statement.strip()) > 10:
                    # Prüfe ob Statement in Context/Quellen unterstützt wird
                    statement_lower = statement.lower()
                    context_lower = context.lower()
                    
                    # Einfache Keyword-Übereinstimmung
                    statement_keywords = set(re.findall(r'\b\w{4,}\b', statement_lower))
                    context_keywords = set(re.findall(r'\b\w{4,}\b', context_lower))
                    
                    if statement_keywords & context_keywords:  # Überschneidung gefunden
                        verified_statements += 1
            
            if total_statements > 0:
                verification_rate = verified_statements / total_statements
                if verification_rate < 0.5:  # Weniger als 50% verifiziert
                    hallucination_penalty += 0.3
        
        # 3. Spezifische StreamWorks-Fakten überprüfen
        streamworks_claims = [
            ('streamworks dashboard', 0.4),  # Nicht existierendes Dashboard
            ('gui interface', 0.3),          # StreamWorks ist nicht GUI-basiert
            ('version 3.0', 0.3),           # Spezifische Versionsangaben
            ('seit 2020', 0.2),             # Nicht verifizierte Zeitangaben
        ]
        
        for claim, penalty in streamworks_claims:
            if claim in response.lower():
                hallucination_penalty += penalty
        
        # Score berechnen (1.0 = keine Halluzinationen, 0.0 = viele Halluzinationen)
        hallucination_score = max(1.0 - hallucination_penalty, 0.0)
        
        return hallucination_score
    
    async def evaluate_source_quality(self, sources: List[str], query: str) -> float:
        """Bewerte die Qualität der verwendeten Quellen"""
        
        if not sources:
            return 0.1  # Sehr niedrig ohne Quellen
        
        quality_factors = []
        
        # 1. Anzahl der Quellen
        source_count_score = min(len(sources) / 3, 1.0)  # Optimal bei 3+ Quellen
        quality_factors.append(source_count_score)
        
        # 2. Quellen-Diversität
        unique_sources = set(sources)
        diversity_score = len(unique_sources) / max(len(sources), 1)
        quality_factors.append(diversity_score)
        
        # 3. Relevanz der Quellen zur Query
        query_lower = query.lower()
        relevant_sources = 0
        
        for source in sources:
            source_lower = str(source).lower()
            
            # Prüfe thematische Relevanz
            if any(term in query_lower for term in ['xml', 'stream']) and any(term in source_lower for term in ['xml', 'stream']):
                relevant_sources += 1
            elif any(term in query_lower for term in ['batch', 'job']) and any(term in source_lower for term in ['batch', 'job']):
                relevant_sources += 1
            elif any(term in query_lower for term in ['api', 'endpoint']) and any(term in source_lower for term in ['api', 'endpoint']):
                relevant_sources += 1
            elif 'training data' in source_lower:  # Training Data ist generell relevant
                relevant_sources += 1
        
        relevance_score = relevant_sources / len(sources) if sources else 0
        quality_factors.append(relevance_score)
        
        # 4. Autoritäts-Score basierend auf Quelle-Typ
        authority_score = 0.0
        for source in sources:
            source_str = str(source).lower()
            if 'training data' in source_str:
                authority_score += 0.3  # Training Data ist autoritativ
            elif any(indicator in source_str for indicator in ['dokumentation', 'manual', 'guide']):
                authority_score += 0.4  # Dokumentation ist sehr autoritativ
            else:
                authority_score += 0.1  # Unbekannte Quellen niedrig bewerten
        
        authority_score = min(authority_score, 1.0)
        quality_factors.append(authority_score)
        
        # Kombiniere alle Faktoren
        source_quality = statistics.mean(quality_factors)
        
        return source_quality
    
    async def simulate_user_satisfaction(self, query: str, response: str, 
                                       relevance_score: float, completeness_score: float) -> float:
        """Simuliere Benutzer-Zufriedenheit basierend auf Response-Qualität"""
        
        satisfaction_factors = []
        
        # 1. Grundzufriedenheit basierend auf Relevanz und Vollständigkeit
        base_satisfaction = (relevance_score * 0.6) + (completeness_score * 0.4)
        satisfaction_factors.append(base_satisfaction)
        
        # 2. Antwort-Geschwindigkeit (simuliert optimale 2-5 Sekunden)
        # Da response_time hier nicht verfügbar ist, nehmen wir Standardwert
        response_time_satisfaction = 0.8
        satisfaction_factors.append(response_time_satisfaction)
        
        # 3. Benutzerfreundlichkeit der Antwort
        usability_score = 0.0
        
        # Emojis und Formatierung
        if any(emoji in response for emoji in ['🔧', '📋', '🚀', '✅', '💡']):
            usability_score += 0.3
        
        # Struktur und Lesbarkeit
        if '##' in response or '###' in response:
            usability_score += 0.2
        
        # Praktische Beispiele
        if '```' in response or 'beispiel' in response.lower():
            usability_score += 0.3
        
        # Deutsche Sprache und Höflichkeit
        if any(polite in response.lower() for polite in ['gerne', 'bitte', 'vielen dank']):
            usability_score += 0.2
        
        usability_score = min(usability_score, 1.0)
        satisfaction_factors.append(usability_score)
        
        # 4. Query-spezifische Zufriedenheit
        query_specific_satisfaction = 0.7  # Standard
        
        # Komplexe Fragen erwarten detaillierte Antworten
        if len(query) > 50:  # Komplexe Frage
            if len(response) > 300:  # Detaillierte Antwort
                query_specific_satisfaction = 0.9
            elif len(response) < 100:  # Zu kurze Antwort
                query_specific_satisfaction = 0.4
        
        satisfaction_factors.append(query_specific_satisfaction)
        
        # Berechne Gesamtzufriedenheit
        user_satisfaction = statistics.mean(satisfaction_factors)
        
        return user_satisfaction
    
    def calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """Berechne gewichteten Gesamtscore"""
        
        overall_score = 0.0
        
        for metric_name, score in metrics.items():
            weight = self.metric_weights.get(metric_name, 0.0)
            overall_score += score * weight
        
        return min(max(overall_score, 0.0), 1.0)
    
    async def generate_performance_report(self, days: int = 7) -> PerformanceReport:
        """Generiere umfassenden Performance-Bericht"""
        
        # Filtere Metriken nach Zeitraum
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_date]
        
        if not recent_metrics:
            logger.warning("📊 Keine Metriken für Bericht verfügbar")
            return PerformanceReport(
                evaluation_period=f"Letzte {days} Tage",
                total_queries=0,
                avg_response_time=0.0,
                avg_relevance_score=0.0,
                avg_completeness_score=0.0,
                avg_confidence_accuracy=0.0,
                avg_hallucination_score=0.0,
                avg_user_satisfaction=0.0,
                avg_overall_score=0.0,
                top_performing_queries=[],
                worst_performing_queries=[],
                improvement_recommendations=[],
                statistical_insights={}
            )
        
        # Berechne Durchschnittswerte
        avg_metrics = {
            'response_time': statistics.mean([m.response_time for m in recent_metrics]),
            'relevance_score': statistics.mean([m.relevance_score for m in recent_metrics]),
            'completeness_score': statistics.mean([m.completeness_score for m in recent_metrics]),
            'confidence_accuracy': statistics.mean([m.confidence_accuracy for m in recent_metrics]),
            'hallucination_score': statistics.mean([m.hallucination_score for m in recent_metrics]),
            'user_satisfaction': statistics.mean([m.user_satisfaction for m in recent_metrics]),
            'overall_score': statistics.mean([m.overall_score for m in recent_metrics])
        }
        
        # Top/Worst performing Queries
        sorted_metrics = sorted(recent_metrics, key=lambda x: x.overall_score, reverse=True)
        
        top_queries = [
            {
                'query': m.query,
                'overall_score': m.overall_score,
                'relevance_score': m.relevance_score,
                'timestamp': m.timestamp.isoformat()
            }
            for m in sorted_metrics[:5]
        ]
        
        worst_queries = [
            {
                'query': m.query,
                'overall_score': m.overall_score,
                'issues': self._identify_issues(m),
                'timestamp': m.timestamp.isoformat()
            }
            for m in sorted_metrics[-5:]
        ]
        
        # Verbesserungs-Empfehlungen
        recommendations = self._generate_improvement_recommendations(recent_metrics, avg_metrics)
        
        # Statistische Insights
        statistical_insights = self._calculate_statistical_insights(recent_metrics)
        
        return PerformanceReport(
            evaluation_period=f"Letzte {days} Tage",
            total_queries=len(recent_metrics),
            avg_response_time=avg_metrics['response_time'],
            avg_relevance_score=avg_metrics['relevance_score'],
            avg_completeness_score=avg_metrics['completeness_score'],
            avg_confidence_accuracy=avg_metrics['confidence_accuracy'],
            avg_hallucination_score=avg_metrics['hallucination_score'],
            avg_user_satisfaction=avg_metrics['user_satisfaction'],
            avg_overall_score=avg_metrics['overall_score'],
            top_performing_queries=top_queries,
            worst_performing_queries=worst_queries,
            improvement_recommendations=recommendations,
            statistical_insights=statistical_insights
        )
    
    def _identify_issues(self, metric: EvaluationMetric) -> List[str]:
        """Identifiziere spezifische Probleme bei einer Metrik"""
        issues = []
        
        if metric.relevance_score < 0.5:
            issues.append("Niedrige Relevanz zur Frage")
        
        if metric.completeness_score < 0.5:
            issues.append("Unvollständige Antwort")
        
        if metric.hallucination_score < 0.7:
            issues.append("Mögliche Halluzinationen")
        
        if metric.confidence_accuracy < 0.5:
            issues.append("Ungenauer Confidence Score")
        
        if metric.source_quality < 0.5:
            issues.append("Schlechte Quellen-Qualität")
        
        if metric.response_time > 10.0:
            issues.append("Lange Antwortzeit")
        
        return issues
    
    def _generate_improvement_recommendations(self, metrics: List[EvaluationMetric], 
                                            avg_metrics: Dict[str, float]) -> List[str]:
        """Generiere Verbesserungs-Empfehlungen"""
        recommendations = []
        
        if avg_metrics['relevance_score'] < 0.7:
            recommendations.append("🎯 Prompt Engineering: Verbessere Keyword-Matching zwischen Query und Response")
        
        if avg_metrics['completeness_score'] < 0.7:
            recommendations.append("📋 Content-Optimierung: Erweitere Response-Templates für strukturiertere Antworten")
        
        if avg_metrics['hallucination_score'] < 0.8:
            recommendations.append("🚨 Fact-Checking: Implementiere strengere Quellen-Validierung")
        
        if avg_metrics['confidence_accuracy'] < 0.7:
            recommendations.append("📊 Confidence-Kalibrierung: Justiere Confidence-Scoring-Algorithmus")
        
        if avg_metrics['response_time'] > 5.0:
            recommendations.append("⚡ Performance: Optimiere RAG-Pipeline für schnellere Antworten")
        
        # Spezifische Empfehlungen basierend auf häufigen Problemen
        hallucination_count = sum(1 for m in metrics if m.hallucination_score < 0.7)
        if hallucination_count > len(metrics) * 0.2:  # Über 20% haben Halluzinationen
            recommendations.append("🔍 Training Data: Erweitere Training-Daten für bessere Fakten-Basis")
        
        return recommendations
    
    def _calculate_statistical_insights(self, metrics: List[EvaluationMetric]) -> Dict[str, Any]:
        """Berechne statistische Insights"""
        
        if not metrics:
            return {}
        
        overall_scores = [m.overall_score for m in metrics]
        response_times = [m.response_time for m in metrics]
        
        return {
            'score_distribution': {
                'min': min(overall_scores),
                'max': max(overall_scores),
                'median': statistics.median(overall_scores),
                'std_dev': statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0.0
            },
            'performance_trend': self._calculate_trend(overall_scores),
            'response_time_analysis': {
                'min': min(response_times),
                'max': max(response_times),
                'median': statistics.median(response_times),
                'avg': statistics.mean(response_times)
            },
            'query_complexity_analysis': self._analyze_query_complexity(metrics),
            'success_rate': len([m for m in metrics if m.overall_score >= 0.7]) / len(metrics)
        }
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Berechne Performance-Trend"""
        if len(scores) < 2:
            return "insufficient_data"
        
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg + 0.05:
            return "improving"
        elif second_avg < first_avg - 0.05:
            return "declining"
        else:
            return "stable"
    
    def _analyze_query_complexity(self, metrics: List[EvaluationMetric]) -> Dict[str, Any]:
        """Analysiere Query-Komplexität vs. Performance"""
        
        simple_queries = [m for m in metrics if len(m.query) < 50]
        complex_queries = [m for m in metrics if len(m.query) >= 50]
        
        return {
            'simple_queries': {
                'count': len(simple_queries),
                'avg_score': statistics.mean([m.overall_score for m in simple_queries]) if simple_queries else 0.0
            },
            'complex_queries': {
                'count': len(complex_queries),
                'avg_score': statistics.mean([m.overall_score for m in complex_queries]) if complex_queries else 0.0
            }
        }
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Aktuelle Metriken für API"""
        
        if not self.metrics_history:
            return {
                'status': 'no_data',
                'message': 'Noch keine Evaluierungen durchgeführt'
            }
        
        # Letzte 10 Metriken
        recent_metrics = self.metrics_history[-10:]
        
        return {
            'status': 'active',
            'total_evaluations': len(self.metrics_history),
            'recent_avg_score': statistics.mean([m.overall_score for m in recent_metrics]),
            'recent_avg_response_time': statistics.mean([m.response_time for m in recent_metrics]),
            'last_evaluation': recent_metrics[-1].timestamp.isoformat(),
            'metrics_summary': {
                'relevance': statistics.mean([m.relevance_score for m in recent_metrics]),
                'completeness': statistics.mean([m.completeness_score for m in recent_metrics]),
                'confidence_accuracy': statistics.mean([m.confidence_accuracy for m in recent_metrics]),
                'hallucination_score': statistics.mean([m.hallucination_score for m in recent_metrics]),
                'user_satisfaction': statistics.mean([m.user_satisfaction for m in recent_metrics])
            }
        }
    
    def clear_metrics_history(self):
        """Lösche Metriken-Historie (für Testing)"""
        self.metrics_history.clear()
        logger.info("🧹 Evaluation Metriken-Historie geleert")

# Global instance
evaluation_service = EvaluationService()