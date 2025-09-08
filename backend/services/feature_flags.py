"""
Feature Flags Service

Dynamic feature flag management for the Streamworks RAG system.
Enables gradual rollout, A/B testing, and performance monitoring of advanced RAG features.

Author: AI Assistant
Date: 2025-01-XX
"""

import json
import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
import asyncio

logger = logging.getLogger(__name__)


class FeatureState(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


class RolloutStrategy(Enum):
    ALL_USERS = "all_users"
    PERCENTAGE = "percentage"
    USER_LIST = "user_list"
    GRADUAL = "gradual"


@dataclass
class FeatureFlag:
    """Feature flag configuration"""
    name: str
    state: FeatureState
    rollout_strategy: RolloutStrategy
    rollout_percentage: float = 0.0
    enabled_users: List[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: str = ""
    dependencies: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.enabled_users is None:
            self.enabled_users = []
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FeatureUsageMetrics:
    """Metrics for feature usage tracking"""
    feature_name: str
    total_uses: int = 0
    successful_uses: int = 0
    failed_uses: int = 0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None
    user_count: int = 0
    error_rate: float = 0.0
    
    @property
    def success_rate(self) -> float:
        if self.total_uses == 0:
            return 0.0
        return self.successful_uses / self.total_uses


class FeatureFlagsService:
    """Service for managing feature flags and rollouts"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("./config/feature_flags.json")
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Feature flags storage
        self._flags: Dict[str, FeatureFlag] = {}
        self._metrics: Dict[str, FeatureUsageMetrics] = {}
        
        # Load configuration
        self._load_config()
        
        # Initialize default flags
        self._initialize_default_flags()
        
        logger.info(f"FeatureFlagsService initialized with {len(self._flags)} flags")
    
    def _load_config(self):
        """Load feature flags from configuration file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Load flags
                for flag_data in config_data.get('flags', []):
                    flag = FeatureFlag(
                        name=flag_data['name'],
                        state=FeatureState(flag_data['state']),
                        rollout_strategy=RolloutStrategy(flag_data['rollout_strategy']),
                        rollout_percentage=flag_data.get('rollout_percentage', 0.0),
                        enabled_users=flag_data.get('enabled_users', []),
                        start_date=datetime.fromisoformat(flag_data['start_date']) if flag_data.get('start_date') else None,
                        end_date=datetime.fromisoformat(flag_data['end_date']) if flag_data.get('end_date') else None,
                        description=flag_data.get('description', ''),
                        dependencies=flag_data.get('dependencies', []),
                        metadata=flag_data.get('metadata', {})
                    )
                    self._flags[flag.name] = flag
                
                # Load metrics
                for metrics_data in config_data.get('metrics', []):
                    metrics = FeatureUsageMetrics(
                        feature_name=metrics_data['feature_name'],
                        total_uses=metrics_data.get('total_uses', 0),
                        successful_uses=metrics_data.get('successful_uses', 0),
                        failed_uses=metrics_data.get('failed_uses', 0),
                        avg_response_time=metrics_data.get('avg_response_time', 0.0),
                        last_used=datetime.fromisoformat(metrics_data['last_used']) if metrics_data.get('last_used') else None,
                        user_count=metrics_data.get('user_count', 0),
                        error_rate=metrics_data.get('error_rate', 0.0)
                    )
                    self._metrics[metrics.feature_name] = metrics
                    
                logger.info(f"Loaded {len(self._flags)} feature flags from config")
                
            except Exception as e:
                logger.error(f"Error loading feature flags config: {e}")
    
    def _initialize_default_flags(self):
        """Initialize default feature flags for advanced RAG features"""
        default_flags = {
            # Advanced RAG Features
            "advanced_rag_orchestrator": FeatureFlag(
                name="advanced_rag_orchestrator",
                state=FeatureState.EXPERIMENTAL,
                rollout_strategy=RolloutStrategy.PERCENTAGE,
                rollout_percentage=10.0,
                description="Enable advanced RAG orchestrator with hybrid retrieval",
                dependencies=["bm25_service", "query_expansion"]
            ),
            
            "bm25_service": FeatureFlag(
                name="bm25_service",
                state=FeatureState.ENABLED,
                rollout_strategy=RolloutStrategy.ALL_USERS,
                description="Enable BM25 sparse retrieval service"
            ),
            
            "query_expansion": FeatureFlag(
                name="query_expansion",
                state=FeatureState.EXPERIMENTAL,
                rollout_strategy=RolloutStrategy.PERCENTAGE,
                rollout_percentage=25.0,
                description="Enable LLM-powered query expansion"
            ),
            
            "result_fusion": FeatureFlag(
                name="result_fusion",
                state=FeatureState.EXPERIMENTAL,
                rollout_strategy=RolloutStrategy.PERCENTAGE,
                rollout_percentage=15.0,
                description="Enable intelligent result fusion and deduplication"
            ),
            
            "adaptive_chunking": FeatureFlag(
                name="adaptive_chunking",
                state=FeatureState.EXPERIMENTAL,
                rollout_strategy=RolloutStrategy.PERCENTAGE,
                rollout_percentage=20.0,
                description="Enable adaptive document chunking strategies"
            ),
            
            "contextual_embeddings": FeatureFlag(
                name="contextual_embeddings",
                state=FeatureState.EXPERIMENTAL,
                rollout_strategy=RolloutStrategy.PERCENTAGE,
                rollout_percentage=5.0,
                description="Enable context-aware document embeddings",
                dependencies=["adaptive_chunking"]
            ),
            
            # Performance Features
            "embedding_cache": FeatureFlag(
                name="embedding_cache",
                state=FeatureState.ENABLED,
                rollout_strategy=RolloutStrategy.ALL_USERS,
                description="Enable embedding result caching"
            ),
            
            "query_cache": FeatureFlag(
                name="query_cache",
                state=FeatureState.ENABLED,
                rollout_strategy=RolloutStrategy.ALL_USERS,
                description="Enable query result caching"
            ),
            
            "performance_monitoring": FeatureFlag(
                name="performance_monitoring",
                state=FeatureState.ENABLED,
                rollout_strategy=RolloutStrategy.ALL_USERS,
                description="Enable comprehensive performance monitoring"
            ),
            
            # Experimental Features
            "auto_optimization": FeatureFlag(
                name="auto_optimization",
                state=FeatureState.EXPERIMENTAL,
                rollout_strategy=RolloutStrategy.PERCENTAGE,
                rollout_percentage=1.0,
                description="Enable automatic system optimization based on performance metrics"
            ),
            
            "multi_language_support": FeatureFlag(
                name="multi_language_support",
                state=FeatureState.DISABLED,
                rollout_strategy=RolloutStrategy.USER_LIST,
                description="Enable multi-language document processing"
            )
        }
        
        # Add default flags that don't exist
        for name, flag in default_flags.items():
            if name not in self._flags:
                self._flags[name] = flag
                self._metrics[name] = FeatureUsageMetrics(feature_name=name)
    
    def is_enabled(self, feature_name: str, user_id: Optional[str] = None) -> bool:
        """Check if a feature is enabled for a user"""
        flag = self._flags.get(feature_name)
        if not flag:
            return False
        
        # Check if feature is globally disabled or deprecated
        if flag.state in [FeatureState.DISABLED, FeatureState.DEPRECATED]:
            return False
        
        # Check date-based availability
        now = datetime.now()
        if flag.start_date and now < flag.start_date:
            return False
        if flag.end_date and now > flag.end_date:
            return False
        
        # Check dependencies
        for dependency in flag.dependencies:
            if not self.is_enabled(dependency, user_id):
                return False
        
        # Apply rollout strategy
        if flag.rollout_strategy == RolloutStrategy.ALL_USERS:
            return True
        elif flag.rollout_strategy == RolloutStrategy.USER_LIST:
            return user_id in flag.enabled_users if user_id else False
        elif flag.rollout_strategy == RolloutStrategy.PERCENTAGE:
            if not user_id:
                return False
            # Use hash of user_id + feature_name for consistent rollout
            import hashlib
            hash_input = f"{user_id}:{feature_name}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            percentage = (hash_value % 100) / 100.0
            return percentage < (flag.rollout_percentage / 100.0)
        elif flag.rollout_strategy == RolloutStrategy.GRADUAL:
            # Gradual rollout based on time since start_date
            if not flag.start_date:
                return False
            days_since_start = (now - flag.start_date).days
            target_percentage = min(days_since_start * 5, flag.rollout_percentage)  # 5% per day
            if not user_id:
                return False
            import hashlib
            hash_input = f"{user_id}:{feature_name}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            percentage = (hash_value % 100) / 100.0
            return percentage < (target_percentage / 100.0)
        
        return False
    
    def track_usage(self, feature_name: str, success: bool = True, response_time: float = 0.0, user_id: Optional[str] = None):
        """Track feature usage for metrics"""
        if feature_name not in self._metrics:
            self._metrics[feature_name] = FeatureUsageMetrics(feature_name=feature_name)
        
        metrics = self._metrics[feature_name]
        metrics.total_uses += 1
        metrics.last_used = datetime.now()
        
        if success:
            metrics.successful_uses += 1
        else:
            metrics.failed_uses += 1
        
        # Update average response time
        if response_time > 0:
            total_time = metrics.avg_response_time * (metrics.total_uses - 1) + response_time
            metrics.avg_response_time = total_time / metrics.total_uses
        
        # Update error rate
        metrics.error_rate = metrics.failed_uses / metrics.total_uses
        
        # Track unique users (simplified - in production you'd use a more sophisticated approach)
        if user_id:
            # This is a simplified user counting - in production you'd track unique users properly
            metrics.user_count = max(metrics.user_count, 1)
    
    def get_feature_metrics(self, feature_name: str) -> Optional[FeatureUsageMetrics]:
        """Get usage metrics for a feature"""
        return self._metrics.get(feature_name)
    
    def get_all_metrics(self) -> Dict[str, FeatureUsageMetrics]:
        """Get metrics for all features"""
        return self._metrics.copy()
    
    def update_flag(self, feature_name: str, **updates) -> bool:
        """Update a feature flag configuration"""
        if feature_name not in self._flags:
            return False
        
        flag = self._flags[feature_name]
        
        for key, value in updates.items():
            if hasattr(flag, key):
                if key == 'state' and isinstance(value, str):
                    value = FeatureState(value)
                elif key == 'rollout_strategy' and isinstance(value, str):
                    value = RolloutStrategy(value)
                elif key in ['start_date', 'end_date'] and isinstance(value, str):
                    value = datetime.fromisoformat(value)
                
                setattr(flag, key, value)
        
        # Save configuration
        self._save_config()
        
        logger.info(f"Updated feature flag '{feature_name}'")
        return True
    
    def create_flag(self, flag: FeatureFlag) -> bool:
        """Create a new feature flag"""
        if flag.name in self._flags:
            logger.warning(f"Feature flag '{flag.name}' already exists")
            return False
        
        self._flags[flag.name] = flag
        self._metrics[flag.name] = FeatureUsageMetrics(feature_name=flag.name)
        
        # Save configuration
        self._save_config()
        
        logger.info(f"Created feature flag '{flag.name}'")
        return True
    
    def delete_flag(self, feature_name: str) -> bool:
        """Delete a feature flag"""
        if feature_name not in self._flags:
            return False
        
        del self._flags[feature_name]
        if feature_name in self._metrics:
            del self._metrics[feature_name]
        
        # Save configuration
        self._save_config()
        
        logger.info(f"Deleted feature flag '{feature_name}'")
        return True
    
    def get_flag(self, feature_name: str) -> Optional[FeatureFlag]:
        """Get a feature flag configuration"""
        return self._flags.get(feature_name)
    
    def list_flags(self, state_filter: Optional[FeatureState] = None) -> Dict[str, FeatureFlag]:
        """List all feature flags, optionally filtered by state"""
        flags = self._flags.copy()
        
        if state_filter:
            flags = {name: flag for name, flag in flags.items() if flag.state == state_filter}
        
        return flags
    
    def _save_config(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'flags': [],
                'metrics': [],
                'last_updated': datetime.now().isoformat()
            }
            
            # Serialize flags
            for flag in self._flags.values():
                flag_data = asdict(flag)
                # Convert datetime objects to ISO strings
                if flag_data.get('start_date'):
                    flag_data['start_date'] = flag.start_date.isoformat()
                if flag_data.get('end_date'):
                    flag_data['end_date'] = flag.end_date.isoformat()
                # Convert enums to values
                flag_data['state'] = flag.state.value
                flag_data['rollout_strategy'] = flag.rollout_strategy.value
                
                config_data['flags'].append(flag_data)
            
            # Serialize metrics
            for metrics in self._metrics.values():
                metrics_data = asdict(metrics)
                if metrics_data.get('last_used'):
                    metrics_data['last_used'] = metrics.last_used.isoformat()
                
                config_data['metrics'].append(metrics_data)
            
            # Write to file
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving feature flags config: {e}")
    
    def get_rollout_status(self) -> Dict[str, Any]:
        """Get comprehensive rollout status report"""
        status = {
            'total_flags': len(self._flags),
            'enabled_flags': 0,
            'experimental_flags': 0,
            'disabled_flags': 0,
            'flags_by_state': {},
            'top_used_features': [],
            'performance_summary': {},
            'rollout_health': 'healthy'
        }
        
        # Count by state
        state_counts = {}
        for flag in self._flags.values():
            state_counts[flag.state.value] = state_counts.get(flag.state.value, 0) + 1
            
            if flag.state == FeatureState.ENABLED:
                status['enabled_flags'] += 1
            elif flag.state == FeatureState.EXPERIMENTAL:
                status['experimental_flags'] += 1
            elif flag.state == FeatureState.DISABLED:
                status['disabled_flags'] += 1
        
        status['flags_by_state'] = state_counts
        
        # Top used features
        sorted_metrics = sorted(
            self._metrics.values(),
            key=lambda m: m.total_uses,
            reverse=True
        )
        
        status['top_used_features'] = [
            {
                'name': m.feature_name,
                'uses': m.total_uses,
                'success_rate': m.success_rate,
                'avg_response_time': m.avg_response_time
            }
            for m in sorted_metrics[:5]
        ]
        
        # Performance summary
        if sorted_metrics:
            total_uses = sum(m.total_uses for m in sorted_metrics)
            avg_success_rate = sum(m.success_rate for m in sorted_metrics) / len(sorted_metrics)
            avg_response_time = sum(m.avg_response_time for m in sorted_metrics if m.avg_response_time > 0)
            avg_response_time = avg_response_time / len([m for m in sorted_metrics if m.avg_response_time > 0]) if avg_response_time else 0
            
            status['performance_summary'] = {
                'total_feature_uses': total_uses,
                'average_success_rate': avg_success_rate,
                'average_response_time': avg_response_time
            }
        
        # Health check
        unhealthy_features = [
            m.feature_name for m in sorted_metrics
            if m.total_uses > 10 and (m.success_rate < 0.8 or m.error_rate > 0.2)
        ]
        
        if unhealthy_features:
            status['rollout_health'] = 'degraded'
            status['unhealthy_features'] = unhealthy_features
        
        return status
    
    async def cleanup_expired_flags(self):
        """Clean up expired feature flags"""
        now = datetime.now()
        expired_flags = []
        
        for name, flag in self._flags.items():
            if flag.end_date and now > flag.end_date:
                expired_flags.append(name)
        
        for name in expired_flags:
            logger.info(f"Cleaning up expired feature flag: {name}")
            self.delete_flag(name)
        
        return len(expired_flags)
    
    def feature_enabled(self, feature_name: str):
        """Decorator to check if feature is enabled before execution"""
        def decorator(func):
            async def async_wrapper(*args, **kwargs):
                # Extract user_id from common patterns
                user_id = kwargs.get('user_id')
                if not user_id and hasattr(args[0], 'user_id'):
                    user_id = args[0].user_id
                
                if not self.is_enabled(feature_name, user_id):
                    raise ValueError(f"Feature '{feature_name}' is not enabled for this user")
                
                import time
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    self.track_usage(feature_name, True, time.time() - start_time, user_id)
                    return result
                except Exception as e:
                    self.track_usage(feature_name, False, time.time() - start_time, user_id)
                    raise
            
            def sync_wrapper(*args, **kwargs):
                user_id = kwargs.get('user_id')
                if not user_id and hasattr(args[0], 'user_id'):
                    user_id = args[0].user_id
                
                if not self.is_enabled(feature_name, user_id):
                    raise ValueError(f"Feature '{feature_name}' is not enabled for this user")
                
                import time
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    self.track_usage(feature_name, True, time.time() - start_time, user_id)
                    return result
                except Exception as e:
                    self.track_usage(feature_name, False, time.time() - start_time, user_id)
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator


# Global feature flags service instance
feature_flags = FeatureFlagsService()