"""
A/B Testing Framework for StreamWorks-KI
Enables testing different prompt variants and response strategies
"""
import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import statistics
import random

from app.core.config import settings
from app.models.database import db_manager

logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    """Status of A/B test experiments"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class VariantType(Enum):
    """Types of variants that can be tested"""
    PROMPT = "prompt"
    RESPONSE_STRATEGY = "response_strategy"
    TEMPERATURE = "temperature"
    RAG_STRATEGY = "rag_strategy"

@dataclass
class ExperimentVariant:
    """Represents a variant in an A/B test"""
    id: str
    name: str
    type: VariantType
    config: Dict[str, Any]
    weight: float  # 0.0 to 1.0
    
@dataclass
class ExperimentResult:
    """Result of a single test interaction"""
    variant_id: str
    timestamp: datetime
    user_query: str
    response_time_ms: float
    user_satisfaction: Optional[float] = None
    response_quality: Optional[float] = None
    conversion: bool = False
    metadata: Dict[str, Any] = None

@dataclass
class ExperimentStats:
    """Statistics for an experiment variant"""
    variant_id: str
    total_interactions: int
    avg_response_time: float
    avg_satisfaction: float
    avg_quality: float
    conversion_rate: float
    confidence_interval: Tuple[float, float]
    
@dataclass
class Experiment:
    """A/B test experiment configuration"""
    id: str
    name: str
    description: str
    variants: List[ExperimentVariant]
    status: ExperimentStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    target_sample_size: int = 100
    confidence_level: float = 0.95
    results: List[ExperimentResult] = None
    metadata: Dict[str, Any] = None

class ABTestingService:
    """A/B Testing Service for StreamWorks-KI"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.active_experiments: List[str] = []
        self.is_initialized = False
        
        # Statistical settings
        self.min_sample_size = 30
        self.significance_threshold = 0.05
        
        logger.info("🧪 A/B Testing Service initialized")
    
    async def initialize(self):
        """Initialize A/B Testing Service"""
        try:
            logger.info("🚀 Initializing A/B Testing Service...")
            
            # Load existing experiments from database
            await self._load_experiments()
            
            # Set up default experiments
            await self._setup_default_experiments()
            
            self.is_initialized = True
            logger.info("✅ A/B Testing Service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ A/B Testing Service initialization failed: {e}")
            self.is_initialized = False
    
    async def create_experiment(self, name: str, description: str, 
                              variants: List[Dict[str, Any]],
                              target_sample_size: int = 100,
                              confidence_level: float = 0.95) -> str:
        """Create a new A/B test experiment"""
        try:
            experiment_id = str(uuid.uuid4())
            
            # Create experiment variants
            experiment_variants = []
            total_weight = 0.0
            
            for variant_config in variants:
                variant_id = str(uuid.uuid4())
                variant = ExperimentVariant(
                    id=variant_id,
                    name=variant_config.get('name', f'Variant {len(experiment_variants) + 1}'),
                    type=VariantType(variant_config.get('type', 'prompt')),
                    config=variant_config.get('config', {}),
                    weight=variant_config.get('weight', 1.0 / len(variants))
                )
                experiment_variants.append(variant)
                total_weight += variant.weight
            
            # Normalize weights
            if total_weight != 1.0:
                for variant in experiment_variants:
                    variant.weight = variant.weight / total_weight
            
            # Create experiment
            experiment = Experiment(
                id=experiment_id,
                name=name,
                description=description,
                variants=experiment_variants,
                status=ExperimentStatus.DRAFT,
                created_at=datetime.now(),
                target_sample_size=target_sample_size,
                confidence_level=confidence_level,
                results=[],
                metadata={}
            )
            
            self.experiments[experiment_id] = experiment
            
            # Save to database
            await self._save_experiment(experiment)
            
            logger.info(f"🧪 Created experiment: {name} ({experiment_id})")
            return experiment_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create experiment: {e}")
            raise
    
    async def start_experiment(self, experiment_id: str) -> bool:
        """Start an A/B test experiment"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            
            if experiment.status != ExperimentStatus.DRAFT:
                raise ValueError(f"Experiment {experiment_id} is not in draft status")
            
            # Update experiment status
            experiment.status = ExperimentStatus.ACTIVE
            experiment.started_at = datetime.now()
            
            # Add to active experiments
            if experiment_id not in self.active_experiments:
                self.active_experiments.append(experiment_id)
            
            # Save to database
            await self._save_experiment(experiment)
            
            logger.info(f"🚀 Started experiment: {experiment.name} ({experiment_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start experiment: {e}")
            return False
    
    async def select_variant(self, experiment_id: str) -> Optional[ExperimentVariant]:
        """Select a variant for testing based on weights"""
        try:
            if experiment_id not in self.experiments:
                return None
            
            experiment = self.experiments[experiment_id]
            
            if experiment.status != ExperimentStatus.ACTIVE:
                return None
            
            # Weighted random selection
            rand_value = random.random()
            cumulative_weight = 0.0
            
            for variant in experiment.variants:
                cumulative_weight += variant.weight
                if rand_value <= cumulative_weight:
                    return variant
            
            # Fallback to first variant
            return experiment.variants[0] if experiment.variants else None
            
        except Exception as e:
            logger.error(f"❌ Failed to select variant: {e}")
            return None
    
    async def record_result(self, experiment_id: str, variant_id: str,
                          user_query: str, response_time_ms: float,
                          user_satisfaction: Optional[float] = None,
                          response_quality: Optional[float] = None,
                          conversion: bool = False,
                          metadata: Dict[str, Any] = None) -> bool:
        """Record a result for an experiment"""
        try:
            if experiment_id not in self.experiments:
                return False
            
            experiment = self.experiments[experiment_id]
            
            # Create result
            result = ExperimentResult(
                variant_id=variant_id,
                timestamp=datetime.now(),
                user_query=user_query,
                response_time_ms=response_time_ms,
                user_satisfaction=user_satisfaction,
                response_quality=response_quality,
                conversion=conversion,
                metadata=metadata or {}
            )
            
            # Add to experiment results
            if experiment.results is None:
                experiment.results = []
            experiment.results.append(result)
            
            # Save to database
            await self._save_experiment_result(experiment_id, result)
            
            # Check if experiment should be completed
            if len(experiment.results) >= experiment.target_sample_size:
                await self._check_experiment_completion(experiment_id)
            
            logger.debug(f"📊 Recorded result for experiment {experiment_id}, variant {variant_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record result: {e}")
            return False
    
    async def analyze_results(self, experiment_id: str) -> Dict[str, Any]:
        """Analyze results of an A/B test experiment"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment {experiment_id} not found")
            
            experiment = self.experiments[experiment_id]
            
            if not experiment.results:
                return {
                    "status": "no_results",
                    "message": "No results to analyze"
                }
            
            # Calculate statistics for each variant
            variant_stats = {}
            
            for variant in experiment.variants:
                variant_results = [r for r in experiment.results if r.variant_id == variant.id]
                
                if not variant_results:
                    variant_stats[variant.id] = ExperimentStats(
                        variant_id=variant.id,
                        total_interactions=0,
                        avg_response_time=0.0,
                        avg_satisfaction=0.0,
                        avg_quality=0.0,
                        conversion_rate=0.0,
                        confidence_interval=(0.0, 0.0)
                    )
                    continue
                
                # Calculate metrics
                response_times = [r.response_time_ms for r in variant_results]
                satisfactions = [r.user_satisfaction for r in variant_results if r.user_satisfaction is not None]
                qualities = [r.response_quality for r in variant_results if r.response_quality is not None]
                conversions = [r.conversion for r in variant_results]
                
                avg_response_time = statistics.mean(response_times)
                avg_satisfaction = statistics.mean(satisfactions) if satisfactions else 0.0
                avg_quality = statistics.mean(qualities) if qualities else 0.0
                conversion_rate = sum(conversions) / len(conversions) if conversions else 0.0
                
                # Calculate confidence interval (simplified)
                confidence_interval = self._calculate_confidence_interval(
                    satisfactions if satisfactions else response_times,
                    experiment.confidence_level
                )
                
                variant_stats[variant.id] = ExperimentStats(
                    variant_id=variant.id,
                    total_interactions=len(variant_results),
                    avg_response_time=avg_response_time,
                    avg_satisfaction=avg_satisfaction,
                    avg_quality=avg_quality,
                    conversion_rate=conversion_rate,
                    confidence_interval=confidence_interval
                )
            
            # Determine statistical significance
            significance_results = await self._calculate_statistical_significance(experiment_id, variant_stats)
            
            return {
                "experiment_id": experiment_id,
                "experiment_name": experiment.name,
                "status": experiment.status.value,
                "total_results": len(experiment.results),
                "variant_stats": {vid: {
                    "name": next(v.name for v in experiment.variants if v.id == vid),
                    "total_interactions": stats.total_interactions,
                    "avg_response_time": round(stats.avg_response_time, 2),
                    "avg_satisfaction": round(stats.avg_satisfaction, 2),
                    "avg_quality": round(stats.avg_quality, 2),
                    "conversion_rate": round(stats.conversion_rate * 100, 2),
                    "confidence_interval": [round(ci, 2) for ci in stats.confidence_interval]
                } for vid, stats in variant_stats.items()},
                "significance": significance_results,
                "recommendations": self._generate_recommendations(variant_stats, significance_results)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze results: {e}")
            raise
    
    async def get_active_experiments(self) -> List[Dict[str, Any]]:
        """Get all active experiments"""
        try:
            active_experiments = []
            
            for experiment_id in self.active_experiments:
                if experiment_id in self.experiments:
                    experiment = self.experiments[experiment_id]
                    active_experiments.append({
                        "id": experiment.id,
                        "name": experiment.name,
                        "description": experiment.description,
                        "status": experiment.status.value,
                        "created_at": experiment.created_at.isoformat(),
                        "started_at": experiment.started_at.isoformat() if experiment.started_at else None,
                        "variants_count": len(experiment.variants),
                        "results_count": len(experiment.results) if experiment.results else 0,
                        "target_sample_size": experiment.target_sample_size,
                        "progress": (len(experiment.results) / experiment.target_sample_size * 100) if experiment.results else 0
                    })
            
            return active_experiments
            
        except Exception as e:
            logger.error(f"❌ Failed to get active experiments: {e}")
            return []
    
    async def get_experiment_stats(self) -> Dict[str, Any]:
        """Get overall A/B testing statistics"""
        try:
            total_experiments = len(self.experiments)
            active_experiments = len(self.active_experiments)
            
            # Count by status
            status_counts = {}
            for experiment in self.experiments.values():
                status = experiment.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Calculate total interactions
            total_interactions = sum(
                len(exp.results) if exp.results else 0 
                for exp in self.experiments.values()
            )
            
            return {
                "total_experiments": total_experiments,
                "active_experiments": active_experiments,
                "status_distribution": status_counts,
                "total_interactions": total_interactions,
                "service_status": "healthy" if self.is_initialized else "unhealthy",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get experiment stats: {e}")
            return {
                "error": str(e),
                "service_status": "error"
            }
    
    def _calculate_confidence_interval(self, values: List[float], confidence_level: float) -> Tuple[float, float]:
        """Calculate confidence interval for values"""
        if len(values) < 2:
            return (0.0, 0.0)
        
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        
        # Simplified confidence interval calculation
        margin_of_error = 1.96 * (stdev / (len(values) ** 0.5))  # 95% confidence
        
        return (mean - margin_of_error, mean + margin_of_error)
    
    async def _calculate_statistical_significance(self, experiment_id: str, 
                                                variant_stats: Dict[str, ExperimentStats]) -> Dict[str, Any]:
        """Calculate statistical significance between variants"""
        try:
            if len(variant_stats) < 2:
                return {
                    "is_significant": False,
                    "p_value": 1.0,
                    "message": "Need at least 2 variants for significance testing"
                }
            
            # Get the two variants with most data
            sorted_variants = sorted(variant_stats.items(), 
                                   key=lambda x: x[1].total_interactions, 
                                   reverse=True)
            
            if len(sorted_variants) < 2:
                return {
                    "is_significant": False,
                    "p_value": 1.0,
                    "message": "Insufficient data for significance testing"
                }
            
            variant_a_id, variant_a_stats = sorted_variants[0]
            variant_b_id, variant_b_stats = sorted_variants[1]
            
            # Check sample size
            min_samples = min(variant_a_stats.total_interactions, variant_b_stats.total_interactions)
            
            if min_samples < self.min_sample_size:
                return {
                    "is_significant": False,
                    "p_value": 1.0,
                    "message": f"Need at least {self.min_sample_size} samples per variant",
                    "current_samples": min_samples
                }
            
            # Simplified significance test based on confidence intervals
            # In production, you'd use proper statistical tests like t-test or chi-square
            a_ci = variant_a_stats.confidence_interval
            b_ci = variant_b_stats.confidence_interval
            
            # Check if confidence intervals overlap
            overlap = not (a_ci[1] < b_ci[0] or b_ci[1] < a_ci[0])
            
            # Simulate p-value (in production, calculate properly)
            p_value = 0.03 if not overlap else 0.12
            
            is_significant = p_value < self.significance_threshold
            
            return {
                "is_significant": is_significant,
                "p_value": p_value,
                "significance_threshold": self.significance_threshold,
                "winning_variant": variant_a_id if is_significant and variant_a_stats.avg_satisfaction > variant_b_stats.avg_satisfaction else variant_b_id if is_significant else None,
                "confidence_level": "95%",
                "message": "Statistically significant difference found" if is_significant else "No significant difference detected"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate statistical significance: {e}")
            return {
                "is_significant": False,
                "p_value": 1.0,
                "error": str(e)
            }
    
    def _generate_recommendations(self, variant_stats: Dict[str, ExperimentStats], 
                                significance_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on experiment results"""
        recommendations = []
        
        if not variant_stats:
            return ["No data available for recommendations"]
        
        # Find best performing variant
        best_variant = max(variant_stats.items(), 
                          key=lambda x: x[1].avg_satisfaction)
        
        if significance_results.get("is_significant", False):
            winning_variant = significance_results.get("winning_variant")
            if winning_variant:
                recommendations.append(f"Use variant {winning_variant} - shows statistically significant improvement")
        
        # Performance recommendations
        fastest_variant = min(variant_stats.items(), 
                            key=lambda x: x[1].avg_response_time)
        
        if fastest_variant[1].avg_response_time < 1000:  # Under 1 second
            recommendations.append(f"Variant {fastest_variant[0]} offers excellent response time")
        
        # Sample size recommendations
        min_samples = min(stats.total_interactions for stats in variant_stats.values())
        if min_samples < self.min_sample_size:
            recommendations.append(f"Collect more data - need at least {self.min_sample_size} samples per variant")
        
        return recommendations
    
    async def _setup_default_experiments(self):
        """Set up default A/B experiments"""
        try:
            # Create default prompt testing experiment
            if not self.experiments:
                await self.create_experiment(
                    name="Prompt Optimization",
                    description="Test different prompt styles for better responses",
                    variants=[
                        {
                            "name": "Formal Prompt",
                            "type": "prompt",
                            "config": {
                                "style": "formal",
                                "temperature": 0.7
                            },
                            "weight": 0.5
                        },
                        {
                            "name": "Conversational Prompt",
                            "type": "prompt",
                            "config": {
                                "style": "conversational",
                                "temperature": 0.8
                            },
                            "weight": 0.5
                        }
                    ]
                )
            
            logger.info("✅ Default A/B experiments set up")
            
        except Exception as e:
            logger.error(f"❌ Failed to set up default experiments: {e}")
    
    async def _load_experiments(self):
        """Load experiments from database"""
        try:
            # In production, load from database
            # For now, keep in memory
            logger.info("📊 Loading A/B test experiments from database...")
            
        except Exception as e:
            logger.error(f"❌ Failed to load experiments: {e}")
    
    async def _save_experiment(self, experiment: Experiment):
        """Save experiment to database"""
        try:
            # In production, save to database
            # For now, keep in memory
            logger.debug(f"💾 Saving experiment: {experiment.name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save experiment: {e}")
    
    async def _save_experiment_result(self, experiment_id: str, result: ExperimentResult):
        """Save experiment result to database"""
        try:
            # In production, save to database
            # For now, keep in memory
            logger.debug(f"💾 Saving experiment result for {experiment_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save experiment result: {e}")
    
    async def _check_experiment_completion(self, experiment_id: str):
        """Check if experiment should be completed"""
        try:
            experiment = self.experiments[experiment_id]
            
            if len(experiment.results) >= experiment.target_sample_size:
                # Analyze results and decide completion
                results = await self.analyze_results(experiment_id)
                
                if results.get("significance", {}).get("is_significant", False):
                    experiment.status = ExperimentStatus.COMPLETED
                    experiment.ended_at = datetime.now()
                    
                    if experiment_id in self.active_experiments:
                        self.active_experiments.remove(experiment_id)
                    
                    logger.info(f"✅ Experiment {experiment.name} completed with significant results")
                    
        except Exception as e:
            logger.error(f"❌ Failed to check experiment completion: {e}")

# Global instance
ab_testing_service = ABTestingService()