"""
Feature Flags API Router

REST API for managing feature flags, rollouts, and monitoring usage metrics.
Enables dynamic feature control and A/B testing capabilities.

Author: AI Assistant
Date: 2025-01-XX
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

from services.feature_flags import feature_flags, FeatureFlag, FeatureState, RolloutStrategy, FeatureUsageMetrics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/feature-flags", tags=["feature-flags"])


# ================================
# PYDANTIC MODELS
# ================================

class FeatureFlagRequest(BaseModel):
    name: str
    state: str  # FeatureState enum value
    rollout_strategy: str  # RolloutStrategy enum value
    rollout_percentage: float = 0.0
    enabled_users: List[str] = []
    start_date: Optional[str] = None  # ISO format
    end_date: Optional[str] = None    # ISO format
    description: str = ""
    dependencies: List[str] = []
    metadata: Dict[str, Any] = {}


class FeatureFlagUpdateRequest(BaseModel):
    state: Optional[str] = None
    rollout_strategy: Optional[str] = None
    rollout_percentage: Optional[float] = None
    enabled_users: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class FeatureFlagResponse(BaseModel):
    name: str
    state: str
    rollout_strategy: str
    rollout_percentage: float
    enabled_users: List[str]
    start_date: Optional[str]
    end_date: Optional[str]
    description: str
    dependencies: List[str]
    metadata: Dict[str, Any]


class FeatureCheckRequest(BaseModel):
    feature_name: str
    user_id: Optional[str] = None


class FeatureCheckResponse(BaseModel):
    feature_name: str
    enabled: bool
    user_id: Optional[str]
    reason: str


class UsageMetricsResponse(BaseModel):
    feature_name: str
    total_uses: int
    successful_uses: int
    failed_uses: int
    success_rate: float
    error_rate: float
    avg_response_time: float
    last_used: Optional[str]
    user_count: int


# ================================
# AUTHENTICATION DEPENDENCY (simplified)
# ================================

async def verify_admin_access() -> bool:
    """Verify admin access - simplified for demo"""
    # In production, implement proper authentication/authorization
    return True


# ================================
# FEATURE FLAGS MANAGEMENT
# ================================

@router.get("/", response_model=Dict[str, FeatureFlagResponse])
async def list_feature_flags(
    state: Optional[str] = Query(None, description="Filter by state: enabled, disabled, experimental, deprecated"),
    admin_verified: bool = Depends(verify_admin_access)
):
    """List all feature flags, optionally filtered by state"""
    try:
        state_filter = None
        if state:
            try:
                state_filter = FeatureState(state)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid state. Must be one of: {[s.value for s in FeatureState]}"
                )
        
        flags = feature_flags.list_flags(state_filter)
        
        response = {}
        for name, flag in flags.items():
            response[name] = FeatureFlagResponse(
                name=flag.name,
                state=flag.state.value,
                rollout_strategy=flag.rollout_strategy.value,
                rollout_percentage=flag.rollout_percentage,
                enabled_users=flag.enabled_users,
                start_date=flag.start_date.isoformat() if flag.start_date else None,
                end_date=flag.end_date.isoformat() if flag.end_date else None,
                description=flag.description,
                dependencies=flag.dependencies,
                metadata=flag.metadata
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error listing feature flags: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list feature flags: {str(e)}")


@router.get("/{feature_name}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    feature_name: str,
    admin_verified: bool = Depends(verify_admin_access)
):
    """Get specific feature flag configuration"""
    try:
        flag = feature_flags.get_flag(feature_name)
        if not flag:
            raise HTTPException(status_code=404, detail="Feature flag not found")
        
        return FeatureFlagResponse(
            name=flag.name,
            state=flag.state.value,
            rollout_strategy=flag.rollout_strategy.value,
            rollout_percentage=flag.rollout_percentage,
            enabled_users=flag.enabled_users,
            start_date=flag.start_date.isoformat() if flag.start_date else None,
            end_date=flag.end_date.isoformat() if flag.end_date else None,
            description=flag.description,
            dependencies=flag.dependencies,
            metadata=flag.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature flag {feature_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get feature flag: {str(e)}")


@router.post("/", response_model=Dict[str, str])
async def create_feature_flag(
    request: FeatureFlagRequest,
    admin_verified: bool = Depends(verify_admin_access)
):
    """Create a new feature flag"""
    try:
        # Validate enum values
        try:
            state = FeatureState(request.state)
            rollout_strategy = RolloutStrategy(request.rollout_strategy)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {str(e)}")
        
        # Parse dates
        start_date = None
        end_date = None
        if request.start_date:
            try:
                start_date = datetime.fromisoformat(request.start_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use ISO format.")
        
        if request.end_date:
            try:
                end_date = datetime.fromisoformat(request.end_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use ISO format.")
        
        # Create feature flag
        flag = FeatureFlag(
            name=request.name,
            state=state,
            rollout_strategy=rollout_strategy,
            rollout_percentage=request.rollout_percentage,
            enabled_users=request.enabled_users,
            start_date=start_date,
            end_date=end_date,
            description=request.description,
            dependencies=request.dependencies,
            metadata=request.metadata
        )
        
        success = feature_flags.create_flag(flag)
        if not success:
            raise HTTPException(status_code=409, detail="Feature flag already exists")
        
        return {"message": f"Feature flag '{request.name}' created successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating feature flag: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create feature flag: {str(e)}")


@router.put("/{feature_name}", response_model=Dict[str, str])
async def update_feature_flag(
    feature_name: str,
    request: FeatureFlagUpdateRequest,
    admin_verified: bool = Depends(verify_admin_access)
):
    """Update an existing feature flag"""
    try:
        # Check if flag exists
        if not feature_flags.get_flag(feature_name):
            raise HTTPException(status_code=404, detail="Feature flag not found")
        
        # Prepare updates
        updates = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                updates[field] = value
        
        success = feature_flags.update_flag(feature_name, **updates)
        if not success:
            raise HTTPException(status_code=404, detail="Feature flag not found")
        
        return {"message": f"Feature flag '{feature_name}' updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating feature flag {feature_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update feature flag: {str(e)}")


@router.delete("/{feature_name}", response_model=Dict[str, str])
async def delete_feature_flag(
    feature_name: str,
    admin_verified: bool = Depends(verify_admin_access)
):
    """Delete a feature flag"""
    try:
        success = feature_flags.delete_flag(feature_name)
        if not success:
            raise HTTPException(status_code=404, detail="Feature flag not found")
        
        return {"message": f"Feature flag '{feature_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting feature flag {feature_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete feature flag: {str(e)}")


# ================================
# FEATURE CHECKING AND TESTING
# ================================

@router.post("/check", response_model=FeatureCheckResponse)
async def check_feature_enabled(request: FeatureCheckRequest):
    """Check if a feature is enabled for a specific user"""
    try:
        enabled = feature_flags.is_enabled(request.feature_name, request.user_id)
        
        # Determine reason
        flag = feature_flags.get_flag(request.feature_name)
        if not flag:
            reason = "Feature flag not found"
        elif flag.state == FeatureState.DISABLED:
            reason = "Feature is disabled"
        elif flag.state == FeatureState.DEPRECATED:
            reason = "Feature is deprecated"
        elif enabled:
            if flag.rollout_strategy == RolloutStrategy.ALL_USERS:
                reason = "Enabled for all users"
            elif flag.rollout_strategy == RolloutStrategy.USER_LIST:
                reason = "User in enabled list"
            elif flag.rollout_strategy == RolloutStrategy.PERCENTAGE:
                reason = f"User in {flag.rollout_percentage}% rollout"
            else:
                reason = "Enabled by rollout strategy"
        else:
            if flag.rollout_strategy == RolloutStrategy.USER_LIST:
                reason = "User not in enabled list"
            elif flag.rollout_strategy == RolloutStrategy.PERCENTAGE:
                reason = f"User not in {flag.rollout_percentage}% rollout"
            else:
                reason = "Not enabled by rollout strategy"
        
        return FeatureCheckResponse(
            feature_name=request.feature_name,
            enabled=enabled,
            user_id=request.user_id,
            reason=reason
        )
        
    except Exception as e:
        logger.error(f"Error checking feature {request.feature_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check feature: {str(e)}")


@router.get("/{feature_name}/users", response_model=Dict[str, Any])
async def get_feature_rollout_info(
    feature_name: str,
    admin_verified: bool = Depends(verify_admin_access)
):
    """Get detailed rollout information for a feature"""
    try:
        flag = feature_flags.get_flag(feature_name)
        if not flag:
            raise HTTPException(status_code=404, detail="Feature flag not found")
        
        metrics = feature_flags.get_feature_metrics(feature_name)
        
        return {
            "feature_name": feature_name,
            "rollout_strategy": flag.rollout_strategy.value,
            "rollout_percentage": flag.rollout_percentage,
            "enabled_users_count": len(flag.enabled_users),
            "enabled_users": flag.enabled_users if flag.rollout_strategy == RolloutStrategy.USER_LIST else [],
            "usage_metrics": {
                "total_uses": metrics.total_uses if metrics else 0,
                "user_count": metrics.user_count if metrics else 0,
                "success_rate": metrics.success_rate if metrics else 0.0,
                "last_used": metrics.last_used.isoformat() if metrics and metrics.last_used else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rollout info for {feature_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get rollout info: {str(e)}")


# ================================
# METRICS AND ANALYTICS
# ================================

@router.get("/metrics/overview", response_model=Dict[str, Any])
async def get_feature_flags_overview(
    admin_verified: bool = Depends(verify_admin_access)
):
    """Get comprehensive feature flags overview and metrics"""
    try:
        status = feature_flags.get_rollout_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting feature flags overview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get overview: {str(e)}")


@router.get("/metrics/{feature_name}", response_model=UsageMetricsResponse)
async def get_feature_metrics(
    feature_name: str,
    admin_verified: bool = Depends(verify_admin_access)
):
    """Get detailed usage metrics for a specific feature"""
    try:
        metrics = feature_flags.get_feature_metrics(feature_name)
        if not metrics:
            # Return empty metrics if feature exists but has no usage
            flag = feature_flags.get_flag(feature_name)
            if not flag:
                raise HTTPException(status_code=404, detail="Feature flag not found")
            
            return UsageMetricsResponse(
                feature_name=feature_name,
                total_uses=0,
                successful_uses=0,
                failed_uses=0,
                success_rate=0.0,
                error_rate=0.0,
                avg_response_time=0.0,
                last_used=None,
                user_count=0
            )
        
        return UsageMetricsResponse(
            feature_name=metrics.feature_name,
            total_uses=metrics.total_uses,
            successful_uses=metrics.successful_uses,
            failed_uses=metrics.failed_uses,
            success_rate=metrics.success_rate,
            error_rate=metrics.error_rate,
            avg_response_time=metrics.avg_response_time,
            last_used=metrics.last_used.isoformat() if metrics.last_used else None,
            user_count=metrics.user_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics for {feature_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/metrics", response_model=Dict[str, UsageMetricsResponse])
async def get_all_feature_metrics(
    admin_verified: bool = Depends(verify_admin_access)
):
    """Get usage metrics for all features"""
    try:
        all_metrics = feature_flags.get_all_metrics()
        
        response = {}
        for name, metrics in all_metrics.items():
            response[name] = UsageMetricsResponse(
                feature_name=metrics.feature_name,
                total_uses=metrics.total_uses,
                successful_uses=metrics.successful_uses,
                failed_uses=metrics.failed_uses,
                success_rate=metrics.success_rate,
                error_rate=metrics.error_rate,
                avg_response_time=metrics.avg_response_time,
                last_used=metrics.last_used.isoformat() if metrics.last_used else None,
                user_count=metrics.user_count
            )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting all metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get all metrics: {str(e)}")


# ================================
# MAINTENANCE OPERATIONS
# ================================

@router.post("/cleanup", response_model=Dict[str, Any])
async def cleanup_expired_flags(
    admin_verified: bool = Depends(verify_admin_access)
):
    """Clean up expired feature flags"""
    try:
        cleaned_count = await feature_flags.cleanup_expired_flags()
        
        return {
            "message": "Cleanup completed",
            "expired_flags_removed": cleaned_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup: {str(e)}")


@router.get("/health", response_model=Dict[str, Any])
async def feature_flags_health_check():
    """Health check for feature flags system"""
    try:
        # Basic health checks
        flags_count = len(feature_flags.list_flags())
        status = feature_flags.get_rollout_status()
        
        # Check for any critical issues
        health_status = "healthy"
        issues = []
        
        if status.get('unhealthy_features'):
            health_status = "degraded"
            issues.append(f"Unhealthy features: {', '.join(status['unhealthy_features'])}")
        
        if flags_count == 0:
            health_status = "warning"
            issues.append("No feature flags configured")
        
        return {
            "status": health_status,
            "total_flags": flags_count,
            "enabled_flags": status.get('enabled_flags', 0),
            "experimental_flags": status.get('experimental_flags', 0),
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Feature flags health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }