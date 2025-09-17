"""
Knowledge Graph Monitoring and Quality Metrics Service
Real-time monitoring, quality assessment, and performance optimization
Enterprise-grade observability for knowledge graph operations
"""
import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import statistics
from collections import defaultdict, deque

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from .models import (
    KnowledgeEntity, KnowledgeRelation, KnowledgeFact, KnowledgeEpisode,
    KnowledgeGraphMetrics, EntityType, RelationType, FactType
)

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types of metrics we track"""
    PERFORMANCE = "performance"
    QUALITY = "quality"
    USAGE = "usage"
    HEALTH = "health"
    TREND = "trend"

@dataclass
class QualityAlert:
    """Alert for quality issues"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    level: AlertLevel = AlertLevel.INFO
    metric_type: MetricType = MetricType.QUALITY
    title: str = ""
    description: str = ""
    value: float = 0.0
    threshold: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class SystemHealthReport:
    """Comprehensive system health report"""
    overall_score: float = 0.0
    component_scores: Dict[str, float] = field(default_factory=dict)
    active_alerts: List[QualityAlert] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)

class KnowledgeGraphMonitoringService:
    """
    Enterprise monitoring service for knowledge graph operations
    Provides real-time quality metrics, alerts, and optimization recommendations
    """

    def __init__(self,
                 db_session: AsyncSession,
                 alert_thresholds: Optional[Dict[str, float]] = None,
                 metric_retention_days: int = 30):

        self.db = db_session
        self.metric_retention_days = metric_retention_days

        # Default quality thresholds
        self.thresholds = alert_thresholds or {
            'entity_confidence_min': 0.3,
            'fact_confidence_min': 0.4,
            'extraction_accuracy_min': 0.8,
            'response_time_max_ms': 2000,
            'memory_usage_max_mb': 1000,
            'graph_density_min': 0.1,
            'duplicate_entity_rate_max': 0.1,
            'stale_knowledge_rate_max': 0.2
        }

        # Real-time metric tracking
        self.live_metrics = {
            'extraction_times': deque(maxlen=100),
            'query_times': deque(maxlen=100),
            'entity_confidences': deque(maxlen=1000),
            'fact_confidences': deque(maxlen=1000),
            'active_sessions': set(),
            'error_counts': defaultdict(int),
            'cache_hits': 0,
            'cache_misses': 0
        }

        # Active alerts
        self.active_alerts: List[QualityAlert] = []
        self.alert_history: List[QualityAlert] = []

        # Performance baselines
        self.performance_baselines = {
            'avg_extraction_time': 500.0,  # ms
            'avg_query_time': 200.0,       # ms
            'avg_entity_confidence': 0.7,
            'avg_fact_confidence': 0.6
        }

        logger.info("📊 KnowledgeGraphMonitoringService initialized")

    async def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect comprehensive system metrics
        Main method for periodic metric collection
        """
        start_time = datetime.utcnow()

        try:
            metrics = {}

            # Database metrics
            metrics['database'] = await self._collect_database_metrics()

            # Performance metrics
            metrics['performance'] = await self._collect_performance_metrics()

            # Quality metrics
            metrics['quality'] = await self._collect_quality_metrics()

            # Usage metrics
            metrics['usage'] = await self._collect_usage_metrics()

            # Graph structure metrics
            metrics['graph_structure'] = await self._collect_graph_metrics()

            # System health
            metrics['system_health'] = await self._assess_system_health()

            # Collection performance
            collection_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            metrics['collection_time_ms'] = collection_time

            # Store metrics in database
            await self._store_metrics_snapshot(metrics)

            logger.info(f"📈 Metrics collected in {collection_time:.1f}ms")
            return metrics

        except Exception as e:
            logger.error(f"❌ Metric collection failed: {str(e)}")
            return {}

    async def check_quality_alerts(self) -> List[QualityAlert]:
        """
        Check for quality issues and generate alerts
        Returns new alerts that need attention
        """
        try:
            new_alerts = []

            # Check entity confidence distribution
            entity_alert = await self._check_entity_confidence_alert()
            if entity_alert:
                new_alerts.append(entity_alert)

            # Check fact confidence distribution
            fact_alert = await self._check_fact_confidence_alert()
            if fact_alert:
                new_alerts.append(fact_alert)

            # Check extraction performance
            perf_alert = await self._check_performance_alert()
            if perf_alert:
                new_alerts.append(perf_alert)

            # Check for duplicate entities
            dup_alert = await self._check_duplicate_entities_alert()
            if dup_alert:
                new_alerts.append(dup_alert)

            # Check for stale knowledge
            stale_alert = await self._check_stale_knowledge_alert()
            if stale_alert:
                new_alerts.append(stale_alert)

            # Add new alerts to active list
            for alert in new_alerts:
                self.active_alerts.append(alert)
                self.alert_history.append(alert)

            if new_alerts:
                logger.warning(f"⚠️ Generated {len(new_alerts)} new quality alerts")

            return new_alerts

        except Exception as e:
            logger.error(f"❌ Quality alert check failed: {str(e)}")
            return []

    async def generate_health_report(self) -> SystemHealthReport:
        """
        Generate comprehensive system health report
        Used for dashboards and operational monitoring
        """
        try:
            report = SystemHealthReport()

            # Collect current metrics
            current_metrics = await self.collect_metrics()

            # Calculate component scores
            report.component_scores = {
                'database': await self._score_database_health(),
                'performance': await self._score_performance_health(),
                'quality': await self._score_quality_health(),
                'memory': await self._score_memory_health(),
                'graph_integrity': await self._score_graph_integrity()
            }

            # Overall score (weighted average)
            weights = {'database': 0.25, 'performance': 0.25, 'quality': 0.3, 'memory': 0.1, 'graph_integrity': 0.1}
            report.overall_score = sum(
                score * weights.get(component, 0.2)
                for component, score in report.component_scores.items()
            )

            # Active alerts
            report.active_alerts = [alert for alert in self.active_alerts if not alert.resolved]

            # Performance and quality metrics
            report.performance_metrics = current_metrics.get('performance', {})
            report.quality_metrics = current_metrics.get('quality', {})

            # Generate recommendations
            report.recommendations = await self._generate_recommendations(report)

            logger.info(f"🏥 Health report generated: Overall score {report.overall_score:.2f}")
            return report

        except Exception as e:
            logger.error(f"❌ Health report generation failed: {str(e)}")
            return SystemHealthReport()

    async def optimize_graph_performance(self) -> Dict[str, Any]:
        """
        Analyze and optimize graph performance
        Returns optimization actions taken
        """
        try:
            optimizations = {}

            # Clean up old metrics
            cleaned_metrics = await self._cleanup_old_metrics()
            optimizations['cleaned_old_metrics'] = cleaned_metrics

            # Merge duplicate entities
            merged_entities = await self._merge_duplicate_entities()
            optimizations['merged_duplicate_entities'] = merged_entities

            # Update entity confidence scores
            updated_confidences = await self._recalculate_confidence_scores()
            optimizations['updated_confidence_scores'] = updated_confidences

            # Optimize graph indexes
            index_optimizations = await self._optimize_database_indexes()
            optimizations['index_optimizations'] = index_optimizations

            # Update performance baselines
            await self._update_performance_baselines()
            optimizations['updated_baselines'] = True

            total_optimizations = sum(
                v for v in optimizations.values() if isinstance(v, int)
            )

            logger.info(f"⚡ Graph optimization completed: {total_optimizations} actions taken")
            return optimizations

        except Exception as e:
            logger.error(f"❌ Graph optimization failed: {str(e)}")
            return {}

    # Real-time metric tracking methods

    def track_extraction_time(self, time_ms: float):
        """Track entity extraction time"""
        self.live_metrics['extraction_times'].append(time_ms)

    def track_query_time(self, time_ms: float):
        """Track graph query time"""
        self.live_metrics['query_times'].append(time_ms)

    def track_entity_confidence(self, confidence: float):
        """Track entity confidence score"""
        self.live_metrics['entity_confidences'].append(confidence)

    def track_fact_confidence(self, confidence: float):
        """Track fact confidence score"""
        self.live_metrics['fact_confidences'].append(confidence)

    def track_session_start(self, session_id: str):
        """Track session start"""
        self.live_metrics['active_sessions'].add(session_id)

    def track_session_end(self, session_id: str):
        """Track session end"""
        self.live_metrics['active_sessions'].discard(session_id)

    def track_error(self, error_type: str):
        """Track error occurrence"""
        self.live_metrics['error_counts'][error_type] += 1

    def track_cache_hit(self):
        """Track cache hit"""
        self.live_metrics['cache_hits'] += 1

    def track_cache_miss(self):
        """Track cache miss"""
        self.live_metrics['cache_misses'] += 1

    # Private methods for metric collection

    async def _collect_database_metrics(self) -> Dict[str, Any]:
        """Collect database-related metrics"""
        try:
            # Count entities by type
            entity_counts = {}
            for entity_type in EntityType:
                result = await self.db.execute(
                    select(func.count(KnowledgeEntity.id)).where(
                        and_(
                            KnowledgeEntity.entity_type == entity_type.value,
                            KnowledgeEntity.valid_to.is_(None)
                        )
                    )
                )
                entity_counts[entity_type.value] = result.scalar() or 0

            # Count facts by type
            fact_counts = {}
            for fact_type in FactType:
                result = await self.db.execute(
                    select(func.count(KnowledgeFact.id)).where(
                        and_(
                            KnowledgeFact.fact_type == fact_type.value,
                            KnowledgeFact.valid_to.is_(None)
                        )
                    )
                )
                fact_counts[fact_type.value] = result.scalar() or 0

            # Count relations by type
            relation_counts = {}
            for relation_type in RelationType:
                result = await self.db.execute(
                    select(func.count(KnowledgeRelation.id)).where(
                        and_(
                            KnowledgeRelation.relation_type == relation_type.value,
                            KnowledgeRelation.valid_to.is_(None)
                        )
                    )
                )
                relation_counts[relation_type.value] = result.scalar() or 0

            # Total counts
            total_entities = sum(entity_counts.values())
            total_facts = sum(fact_counts.values())
            total_relations = sum(relation_counts.values())

            # Active episodes
            result = await self.db.execute(
                select(func.count(KnowledgeEpisode.id)).where(
                    KnowledgeEpisode.valid_to.is_(None)
                )
            )
            total_episodes = result.scalar() or 0

            return {
                'total_entities': total_entities,
                'total_facts': total_facts,
                'total_relations': total_relations,
                'total_episodes': total_episodes,
                'entity_counts_by_type': entity_counts,
                'fact_counts_by_type': fact_counts,
                'relation_counts_by_type': relation_counts,
                'graph_size': total_entities + total_relations
            }

        except Exception as e:
            logger.error(f"❌ Database metrics collection failed: {str(e)}")
            return {}

    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance-related metrics"""
        try:
            metrics = {}

            # Extraction times
            if self.live_metrics['extraction_times']:
                extraction_times = list(self.live_metrics['extraction_times'])
                metrics['avg_extraction_time_ms'] = statistics.mean(extraction_times)
                metrics['p95_extraction_time_ms'] = statistics.quantiles(extraction_times, n=20)[18]  # 95th percentile
                metrics['max_extraction_time_ms'] = max(extraction_times)

            # Query times
            if self.live_metrics['query_times']:
                query_times = list(self.live_metrics['query_times'])
                metrics['avg_query_time_ms'] = statistics.mean(query_times)
                metrics['p95_query_time_ms'] = statistics.quantiles(query_times, n=20)[18]
                metrics['max_query_time_ms'] = max(query_times)

            # Cache performance
            total_cache_operations = self.live_metrics['cache_hits'] + self.live_metrics['cache_misses']
            if total_cache_operations > 0:
                metrics['cache_hit_rate'] = self.live_metrics['cache_hits'] / total_cache_operations

            # Active sessions
            metrics['active_sessions_count'] = len(self.live_metrics['active_sessions'])

            # Error rates
            total_errors = sum(self.live_metrics['error_counts'].values())
            metrics['total_errors'] = total_errors
            metrics['error_breakdown'] = dict(self.live_metrics['error_counts'])

            return metrics

        except Exception as e:
            logger.error(f"❌ Performance metrics collection failed: {str(e)}")
            return {}

    async def _collect_quality_metrics(self) -> Dict[str, Any]:
        """Collect quality-related metrics"""
        try:
            metrics = {}

            # Entity confidence distribution
            if self.live_metrics['entity_confidences']:
                confidences = list(self.live_metrics['entity_confidences'])
                metrics['avg_entity_confidence'] = statistics.mean(confidences)
                metrics['min_entity_confidence'] = min(confidences)
                metrics['p25_entity_confidence'] = statistics.quantiles(confidences, n=4)[0]
                metrics['median_entity_confidence'] = statistics.median(confidences)

            # Fact confidence distribution
            if self.live_metrics['fact_confidences']:
                confidences = list(self.live_metrics['fact_confidences'])
                metrics['avg_fact_confidence'] = statistics.mean(confidences)
                metrics['min_fact_confidence'] = min(confidences)
                metrics['p25_fact_confidence'] = statistics.quantiles(confidences, n=4)[0]
                metrics['median_fact_confidence'] = statistics.median(confidences)

            # Quality distribution
            entity_quality_dist = await self._calculate_entity_quality_distribution()
            metrics['entity_quality_distribution'] = entity_quality_dist

            # Validation levels
            validation_dist = await self._calculate_validation_distribution()
            metrics['validation_level_distribution'] = validation_dist

            return metrics

        except Exception as e:
            logger.error(f"❌ Quality metrics collection failed: {str(e)}")
            return {}

    async def _collect_usage_metrics(self) -> Dict[str, Any]:
        """Collect usage-related metrics"""
        try:
            # Get recent activity (last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)

            # Recent entities created
            result = await self.db.execute(
                select(func.count(KnowledgeEntity.id)).where(
                    KnowledgeEntity.created_at >= cutoff_time
                )
            )
            recent_entities = result.scalar() or 0

            # Recent facts created
            result = await self.db.execute(
                select(func.count(KnowledgeFact.id)).where(
                    KnowledgeFact.created_at >= cutoff_time
                )
            )
            recent_facts = result.scalar() or 0

            # Active episodes in last 24h
            result = await self.db.execute(
                select(func.count(KnowledgeEpisode.id)).where(
                    KnowledgeEpisode.updated_at >= cutoff_time
                )
            )
            active_episodes_24h = result.scalar() or 0

            return {
                'recent_entities_24h': recent_entities,
                'recent_facts_24h': recent_facts,
                'active_episodes_24h': active_episodes_24h,
                'entity_creation_rate': recent_entities / 24,  # per hour
                'fact_creation_rate': recent_facts / 24
            }

        except Exception as e:
            logger.error(f"❌ Usage metrics collection failed: {str(e)}")
            return {}

    async def _collect_graph_metrics(self) -> Dict[str, Any]:
        """Collect graph structure metrics"""
        try:
            # Get total entities and relations for density calculation
            result = await self.db.execute(
                select(func.count(KnowledgeEntity.id)).where(
                    KnowledgeEntity.valid_to.is_(None)
                )
            )
            total_entities = result.scalar() or 0

            result = await self.db.execute(
                select(func.count(KnowledgeRelation.id)).where(
                    KnowledgeRelation.valid_to.is_(None)
                )
            )
            total_relations = result.scalar() or 0

            # Calculate graph density
            max_possible_relations = total_entities * (total_entities - 1) / 2 if total_entities > 1 else 1
            graph_density = total_relations / max_possible_relations if max_possible_relations > 0 else 0

            # Entity connectivity
            result = await self.db.execute(
                select(
                    func.avg(
                        select(func.count(KnowledgeRelation.id)).where(
                            or_(
                                KnowledgeRelation.source_entity_id == KnowledgeEntity.id,
                                KnowledgeRelation.target_entity_id == KnowledgeEntity.id
                            )
                        ).scalar_subquery()
                    )
                ).select_from(KnowledgeEntity)
            )
            avg_entity_connections = result.scalar() or 0

            return {
                'graph_density': graph_density,
                'avg_entity_connections': float(avg_entity_connections),
                'total_graph_nodes': total_entities,
                'total_graph_edges': total_relations
            }

        except Exception as e:
            logger.error(f"❌ Graph metrics collection failed: {str(e)}")
            return {}

    async def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health"""
        try:
            health_score = 1.0
            issues = []

            # Check recent error rate
            total_errors = sum(self.live_metrics['error_counts'].values())
            if total_errors > 10:  # More than 10 errors
                health_score -= 0.2
                issues.append("High error rate detected")

            # Check average response times
            if self.live_metrics['extraction_times']:
                avg_extraction = statistics.mean(self.live_metrics['extraction_times'])
                if avg_extraction > self.thresholds['response_time_max_ms']:
                    health_score -= 0.2
                    issues.append("High extraction times")

            # Check entity confidence levels
            if self.live_metrics['entity_confidences']:
                avg_confidence = statistics.mean(self.live_metrics['entity_confidences'])
                if avg_confidence < self.thresholds['entity_confidence_min']:
                    health_score -= 0.2
                    issues.append("Low entity confidence")

            # Determine health status
            if health_score >= 0.8:
                status = "healthy"
            elif health_score >= 0.6:
                status = "warning"
            else:
                status = "unhealthy"

            return {
                'status': status,
                'score': max(0.0, health_score),
                'issues': issues,
                'components_checked': 3
            }

        except Exception as e:
            logger.error(f"❌ System health assessment failed: {str(e)}")
            return {'status': 'unknown', 'score': 0.0, 'issues': ['Health check failed']}

    # Alert checking methods

    async def _check_entity_confidence_alert(self) -> Optional[QualityAlert]:
        """Check for entity confidence issues"""
        if not self.live_metrics['entity_confidences']:
            return None

        avg_confidence = statistics.mean(self.live_metrics['entity_confidences'])
        threshold = self.thresholds['entity_confidence_min']

        if avg_confidence < threshold:
            return QualityAlert(
                level=AlertLevel.WARNING,
                metric_type=MetricType.QUALITY,
                title="Low Entity Confidence",
                description=f"Average entity confidence ({avg_confidence:.3f}) below threshold ({threshold})",
                value=avg_confidence,
                threshold=threshold
            )

        return None

    async def _check_fact_confidence_alert(self) -> Optional[QualityAlert]:
        """Check for fact confidence issues"""
        if not self.live_metrics['fact_confidences']:
            return None

        avg_confidence = statistics.mean(self.live_metrics['fact_confidences'])
        threshold = self.thresholds['fact_confidence_min']

        if avg_confidence < threshold:
            return QualityAlert(
                level=AlertLevel.WARNING,
                metric_type=MetricType.QUALITY,
                title="Low Fact Confidence",
                description=f"Average fact confidence ({avg_confidence:.3f}) below threshold ({threshold})",
                value=avg_confidence,
                threshold=threshold
            )

        return None

    async def _check_performance_alert(self) -> Optional[QualityAlert]:
        """Check for performance issues"""
        if not self.live_metrics['extraction_times']:
            return None

        avg_time = statistics.mean(self.live_metrics['extraction_times'])
        threshold = self.thresholds['response_time_max_ms']

        if avg_time > threshold:
            return QualityAlert(
                level=AlertLevel.WARNING,
                metric_type=MetricType.PERFORMANCE,
                title="High Extraction Time",
                description=f"Average extraction time ({avg_time:.1f}ms) above threshold ({threshold}ms)",
                value=avg_time,
                threshold=threshold
            )

        return None

    async def _check_duplicate_entities_alert(self) -> Optional[QualityAlert]:
        """Check for duplicate entities"""
        # Placeholder - would implement duplicate detection logic
        return None

    async def _check_stale_knowledge_alert(self) -> Optional[QualityAlert]:
        """Check for stale knowledge"""
        # Placeholder - would check for old, unused knowledge
        return None

    # Health scoring methods

    async def _score_database_health(self) -> float:
        """Score database component health (0.0 to 1.0)"""
        try:
            # Check if we can query the database
            result = await self.db.execute(select(func.count(KnowledgeEntity.id)).limit(1))
            if result.scalar() is not None:
                return 1.0
            else:
                return 0.5
        except Exception:
            return 0.0

    async def _score_performance_health(self) -> float:
        """Score performance health"""
        score = 1.0

        # Check extraction times
        if self.live_metrics['extraction_times']:
            avg_time = statistics.mean(self.live_metrics['extraction_times'])
            baseline = self.performance_baselines['avg_extraction_time']
            if avg_time > baseline * 2:
                score -= 0.5
            elif avg_time > baseline * 1.5:
                score -= 0.2

        return max(0.0, score)

    async def _score_quality_health(self) -> float:
        """Score quality health"""
        score = 1.0

        # Check entity confidence
        if self.live_metrics['entity_confidences']:
            avg_confidence = statistics.mean(self.live_metrics['entity_confidences'])
            baseline = self.performance_baselines['avg_entity_confidence']
            if avg_confidence < baseline * 0.8:
                score -= 0.3
            elif avg_confidence < baseline * 0.9:
                score -= 0.1

        return max(0.0, score)

    async def _score_memory_health(self) -> float:
        """Score memory/resource health"""
        # Placeholder - would check actual memory usage
        return 0.9

    async def _score_graph_integrity(self) -> float:
        """Score graph integrity"""
        # Placeholder - would check for orphaned relations, etc.
        return 0.95

    # Optimization methods

    async def _cleanup_old_metrics(self) -> int:
        """Clean up old metric records"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.metric_retention_days)

        result = await self.db.execute(
            delete(KnowledgeGraphMetrics).where(
                KnowledgeGraphMetrics.recorded_at < cutoff_date
            )
        )

        cleaned_count = result.rowcount
        await self.db.commit()

        return cleaned_count

    async def _merge_duplicate_entities(self) -> int:
        """Merge duplicate entities"""
        # Placeholder - would implement entity deduplication
        return 0

    async def _recalculate_confidence_scores(self) -> int:
        """Recalculate entity confidence scores"""
        # Placeholder - would update confidence based on usage patterns
        return 0

    async def _optimize_database_indexes(self) -> Dict[str, Any]:
        """Optimize database indexes"""
        # Placeholder - would analyze and optimize DB indexes
        return {'indexes_analyzed': 0, 'optimizations_applied': 0}

    async def _update_performance_baselines(self):
        """Update performance baselines based on recent data"""
        if self.live_metrics['extraction_times']:
            self.performance_baselines['avg_extraction_time'] = statistics.mean(
                list(self.live_metrics['extraction_times'])
            )

        if self.live_metrics['entity_confidences']:
            self.performance_baselines['avg_entity_confidence'] = statistics.mean(
                list(self.live_metrics['entity_confidences'])
            )

    # Helper methods

    async def _store_metrics_snapshot(self, metrics: Dict[str, Any]):
        """Store metrics snapshot in database"""
        try:
            db_metrics = metrics.get('database', {})
            perf_metrics = metrics.get('performance', {})
            quality_metrics = metrics.get('quality', {})

            metric_record = KnowledgeGraphMetrics(
                total_entities=db_metrics.get('total_entities', 0),
                total_relations=db_metrics.get('total_relations', 0),
                total_facts=db_metrics.get('total_facts', 0),
                total_episodes=db_metrics.get('total_episodes', 0),
                avg_entity_confidence=quality_metrics.get('avg_entity_confidence'),
                avg_fact_confidence=quality_metrics.get('avg_fact_confidence'),
                query_response_time_ms=perf_metrics.get('avg_query_time_ms'),
                extraction_time_ms=perf_metrics.get('avg_extraction_time_ms'),
                properties=metrics
            )

            self.db.add(metric_record)
            await self.db.commit()

        except Exception as e:
            logger.error(f"❌ Failed to store metrics snapshot: {str(e)}")

    async def _calculate_entity_quality_distribution(self) -> Dict[str, int]:
        """Calculate distribution of entity quality levels"""
        # Placeholder - would analyze entity quality scores
        return {'high': 0, 'medium': 0, 'low': 0}

    async def _calculate_validation_distribution(self) -> Dict[str, int]:
        """Calculate distribution of validation levels"""
        # Placeholder - would analyze validation level distribution
        return {'cross_validated': 0, 'llm_confirmed': 0, 'template_confirmed': 0}

    async def _generate_recommendations(self, health_report: SystemHealthReport) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        if health_report.overall_score < 0.8:
            recommendations.append("System health below optimal - consider optimization")

        if health_report.component_scores.get('performance', 1.0) < 0.7:
            recommendations.append("Performance issues detected - review query optimization")

        if health_report.component_scores.get('quality', 1.0) < 0.7:
            recommendations.append("Quality issues detected - review extraction pipeline")

        if len(health_report.active_alerts) > 5:
            recommendations.append("Multiple active alerts - prioritize resolution")

        return recommendations

    def get_live_metrics(self) -> Dict[str, Any]:
        """Get current live metrics"""
        return {
            'extraction_times_count': len(self.live_metrics['extraction_times']),
            'query_times_count': len(self.live_metrics['query_times']),
            'active_sessions': len(self.live_metrics['active_sessions']),
            'total_errors': sum(self.live_metrics['error_counts'].values()),
            'cache_hit_rate': self.live_metrics['cache_hits'] / max(
                self.live_metrics['cache_hits'] + self.live_metrics['cache_misses'], 1
            ),
            'alert_count': len([a for a in self.active_alerts if not a.resolved])
        }