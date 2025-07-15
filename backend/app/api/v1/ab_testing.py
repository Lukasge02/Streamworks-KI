"""
A/B Testing API for StreamWorks-KI
Provides endpoints for managing A/B test experiments
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from app.services.ab_testing_service import ab_testing_service, VariantType, ExperimentStatus
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class CreateExperimentRequest(BaseModel):
    """Request model for creating a new experiment"""
    name: str = Field(..., description="Name of the experiment")
    description: str = Field(..., description="Description of the experiment")
    variants: List[Dict[str, Any]] = Field(..., description="List of variants to test")
    target_sample_size: int = Field(100, description="Target sample size for the experiment")
    confidence_level: float = Field(0.95, description="Confidence level for statistical significance")

class RecordResultRequest(BaseModel):
    """Request model for recording an experiment result"""
    experiment_id: str = Field(..., description="ID of the experiment")
    variant_id: str = Field(..., description="ID of the variant used")
    user_query: str = Field(..., description="User query that was processed")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    user_satisfaction: Optional[float] = Field(None, description="User satisfaction score (0-5)")
    response_quality: Optional[float] = Field(None, description="Response quality score (0-5)")
    conversion: bool = Field(False, description="Whether the interaction resulted in a conversion")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ExperimentResponse(BaseModel):
    """Response model for experiment information"""
    id: str
    name: str
    description: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    variants_count: int
    results_count: int
    target_sample_size: int
    progress: float

@router.post("/experiment", response_model=Dict[str, str])
async def create_experiment(request: CreateExperimentRequest):
    """Create a new A/B test experiment"""
    try:
        # Ensure A/B testing service is initialized
        if not ab_testing_service.is_initialized:
            await ab_testing_service.initialize()
        
        # Validate variants
        if len(request.variants) < 2:
            raise HTTPException(
                status_code=400,
                detail="Experiment must have at least 2 variants"
            )
        
        # Create experiment
        experiment_id = await ab_testing_service.create_experiment(
            name=request.name,
            description=request.description,
            variants=request.variants,
            target_sample_size=request.target_sample_size,
            confidence_level=request.confidence_level
        )
        
        logger.info(f"✅ Created A/B test experiment: {request.name}")
        
        return {
            "experiment_id": experiment_id,
            "status": "created",
            "message": f"Experiment '{request.name}' created successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to create experiment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create experiment: {str(e)}"
        )

@router.post("/experiment/{experiment_id}/start")
async def start_experiment(experiment_id: str):
    """Start an A/B test experiment"""
    try:
        # Ensure A/B testing service is initialized
        if not ab_testing_service.is_initialized:
            await ab_testing_service.initialize()
        
        success = await ab_testing_service.start_experiment(experiment_id)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to start experiment"
            )
        
        logger.info(f"✅ Started A/B test experiment: {experiment_id}")
        
        return {
            "experiment_id": experiment_id,
            "status": "started",
            "message": "Experiment started successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to start experiment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start experiment: {str(e)}"
        )

@router.get("/experiment/{experiment_id}/variant")
async def get_variant_for_user(experiment_id: str):
    """Get a variant for a user (for A/B testing)"""
    try:
        # Ensure A/B testing service is initialized
        if not ab_testing_service.is_initialized:
            await ab_testing_service.initialize()
        
        variant = await ab_testing_service.select_variant(experiment_id)
        
        if not variant:
            raise HTTPException(
                status_code=404,
                detail="No active variant found for this experiment"
            )
        
        return {
            "experiment_id": experiment_id,
            "variant_id": variant.id,
            "variant_name": variant.name,
            "variant_type": variant.type.value,
            "config": variant.config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get variant: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get variant: {str(e)}"
        )

@router.post("/experiment/result")
async def record_experiment_result(request: RecordResultRequest):
    """Record a result for an A/B test experiment"""
    try:
        # Ensure A/B testing service is initialized
        if not ab_testing_service.is_initialized:
            await ab_testing_service.initialize()
        
        success = await ab_testing_service.record_result(
            experiment_id=request.experiment_id,
            variant_id=request.variant_id,
            user_query=request.user_query,
            response_time_ms=request.response_time_ms,
            user_satisfaction=request.user_satisfaction,
            response_quality=request.response_quality,
            conversion=request.conversion,
            metadata=request.metadata or {}
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to record experiment result"
            )
        
        logger.debug(f"📊 Recorded result for experiment {request.experiment_id}")
        
        return {
            "status": "recorded",
            "message": "Experiment result recorded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to record result: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record result: {str(e)}"
        )

@router.get("/results/{experiment_id}")
async def get_experiment_results(experiment_id: str):
    """Get results and analysis for an A/B test experiment"""
    try:
        # Ensure A/B testing service is initialized
        if not ab_testing_service.is_initialized:
            await ab_testing_service.initialize()
        
        results = await ab_testing_service.analyze_results(experiment_id)
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Failed to get experiment results: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get experiment results: {str(e)}"
        )

@router.get("/active", response_model=List[ExperimentResponse])
async def get_active_experiments():
    """Get all active A/B test experiments"""
    try:
        # Ensure A/B testing service is initialized
        if not ab_testing_service.is_initialized:
            await ab_testing_service.initialize()
        
        experiments = await ab_testing_service.get_active_experiments()
        
        return [
            ExperimentResponse(
                id=exp["id"],
                name=exp["name"],
                description=exp["description"],
                status=exp["status"],
                created_at=exp["created_at"],
                started_at=exp.get("started_at"),
                ended_at=exp.get("ended_at"),
                variants_count=exp["variants_count"],
                results_count=exp["results_count"],
                target_sample_size=exp["target_sample_size"],
                progress=exp["progress"]
            ) for exp in experiments
        ]
        
    except Exception as e:
        logger.error(f"❌ Failed to get active experiments: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get active experiments: {str(e)}"
        )

@router.get("/stats")
async def get_ab_testing_stats():
    """Get overall A/B testing statistics"""
    try:
        # Ensure A/B testing service is initialized
        if not ab_testing_service.is_initialized:
            await ab_testing_service.initialize()
        
        stats = await ab_testing_service.get_experiment_stats()
        
        return stats
        
    except Exception as e:
        logger.error(f"❌ Failed to get A/B testing stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get A/B testing stats: {str(e)}"
        )

@router.get("/health")
async def ab_testing_health():
    """Health check for A/B testing service"""
    try:
        # Ensure A/B testing service is initialized
        if not ab_testing_service.is_initialized:
            await ab_testing_service.initialize()
        
        stats = await ab_testing_service.get_experiment_stats()
        
        return {
            "status": "healthy" if ab_testing_service.is_initialized else "unhealthy",
            "service": "ab_testing",
            "initialized": ab_testing_service.is_initialized,
            "total_experiments": stats.get("total_experiments", 0),
            "active_experiments": stats.get("active_experiments", 0),
            "total_interactions": stats.get("total_interactions", 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ A/B testing health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "ab_testing",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/experiment/{experiment_id}/simulate")
async def simulate_experiment_data(experiment_id: str, num_results: int = 50):
    """Simulate data for an experiment (for testing purposes)"""
    try:
        if not settings.ENV == "development":
            raise HTTPException(
                status_code=403,
                detail="Simulation is only available in development environment"
            )
        
        # Ensure A/B testing service is initialized
        if not ab_testing_service.is_initialized:
            await ab_testing_service.initialize()
        
        # Get experiment variants
        if experiment_id not in ab_testing_service.experiments:
            raise HTTPException(
                status_code=404,
                detail="Experiment not found"
            )
        
        experiment = ab_testing_service.experiments[experiment_id]
        
        # Simulate results for each variant
        import random
        
        for i in range(num_results):
            variant = random.choice(experiment.variants)
            
            # Simulate different performance for different variants
            base_response_time = 800 if variant.name == "Formal Prompt" else 750
            base_satisfaction = 4.0 if variant.name == "Formal Prompt" else 4.2
            base_quality = 3.8 if variant.name == "Formal Prompt" else 4.0
            
            await ab_testing_service.record_result(
                experiment_id=experiment_id,
                variant_id=variant.id,
                user_query=f"Simulated query {i+1}",
                response_time_ms=base_response_time + random.uniform(-100, 200),
                user_satisfaction=min(5.0, max(1.0, base_satisfaction + random.uniform(-0.5, 0.5))),
                response_quality=min(5.0, max(1.0, base_quality + random.uniform(-0.5, 0.5))),
                conversion=random.random() < 0.15,  # 15% conversion rate
                metadata={"simulated": True}
            )
        
        logger.info(f"🎭 Simulated {num_results} results for experiment {experiment_id}")
        
        return {
            "status": "simulated",
            "experiment_id": experiment_id,
            "results_added": num_results,
            "message": f"Added {num_results} simulated results"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to simulate experiment data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to simulate data: {str(e)}"
        )