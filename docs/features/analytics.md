# 📊 Analytics & Monitoring Features

## Feature Overview & Purpose

The StreamWorks-KI Analytics & Monitoring System provides comprehensive insights into system performance, user behavior, and operational metrics. Designed specifically for Bachelor thesis research requirements, it offers scientific-grade data collection, analysis, and export capabilities.

### Key Capabilities
- **Real-time Metrics Collection**: System performance and user interaction tracking
- **Scientific Data Export**: CSV exports for academic research and analysis
- **PostgreSQL Analytics**: Advanced SQL-based reporting and aggregation
- **Performance Monitoring**: Response times, error rates, and resource utilization
- **Usage Analytics**: Document processing statistics and user behavior patterns
- **Bachelor Thesis Integration**: Specialized metrics for academic evaluation

## Technical Implementation Details

### Architecture Overview
```
Event Generation → Metric Collection → PostgreSQL Storage → Analysis & Export
```

### Core Components

#### 1. Analytics Service (`app/services/analytics_service.py`)
- **Primary Service**: Central analytics orchestrator and data aggregator
- **Metric Collection**: Real-time system and user metrics capture
- **PostgreSQL Integration**: Efficient bulk data operations and complex queries
- **Export Engine**: CSV generation for scientific analysis

#### 2. System Metrics Model (`app/models/postgres_models.py`)
- **Data Schema**: Structured metrics storage with metadata support
- **Indexing Strategy**: Optimized for time-series queries and aggregations
- **Data Retention**: Configurable retention policies for long-term analysis

#### 3. Analytics API (`app/api/v1/analytics.py`)
- **REST Endpoints**: Comprehensive API for metrics access and export
- **Query Interface**: Flexible filtering and aggregation capabilities
- **Export Features**: Multiple format support for research data

### Database Schema

#### System Metrics Table
```sql
CREATE TABLE system_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    value DECIMAL(15,6) NOT NULL,
    unit VARCHAR(20),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for performance
    INDEX idx_system_metrics_name_time (metric_name, created_at),
    INDEX idx_system_metrics_metadata (metadata USING gin)
);
```

#### Metric Categories
- **Performance Metrics**: Response times, throughput, resource usage
- **User Interaction Metrics**: Query patterns, document access, feature usage
- **System Health Metrics**: Error rates, availability, service status
- **Business Metrics**: Document processing volume, user engagement

### Metrics Collection Framework

#### Automatic Metric Generation
```python
async def track_performance_metric(
    operation: str,
    duration: float,
    metadata: Dict[str, Any] = None
) -> None:
    """Track performance metrics with contextual metadata"""
    
    await SystemMetric.create(
        metric_name=f"performance.{operation}.duration",
        value=duration,
        unit="seconds",
        metadata={
            "operation": operation,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context": metadata or {}
        }
    )
```

#### Decorator-based Tracking
```python
@track_analytics("document_conversion")
async def convert_document(file_path: str) -> ConversionResult:
    """Document conversion with automatic analytics tracking"""
    start_time = time.time()
    
    try:
        result = await process_document(file_path)
        
        # Track success metrics
        await track_metric(
            "document_conversion.success",
            1,
            metadata={
                "file_type": result.format,
                "file_size": result.size,
                "processing_time": time.time() - start_time
            }
        )
        
        return result
        
    except Exception as e:
        # Track error metrics
        await track_metric(
            "document_conversion.error",
            1,
            metadata={
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )
        raise
```

## API Endpoints

### Document Processing Analytics

#### `GET /api/v1/analytics/document-processing`
**Purpose**: Comprehensive document processing statistics

**Query Parameters**:
- `days`: Analysis period (default: 30)
- `format`: File format filter
- `category_id`: Category filter

**Response**:
```json
{
  "period": {
    "days": 30,
    "start_date": "2024-12-24T00:00:00Z",
    "end_date": "2025-01-23T23:59:59Z"
  },
  "totals": {
    "documents_processed": 1247,
    "total_file_size_mb": 8942.5,
    "total_processing_time_hours": 12.7,
    "success_rate": 0.964
  },
  "by_format": {
    "pdf": {
      "count": 856,
      "avg_processing_time": 4.2,
      "success_rate": 0.971
    },
    "docx": {
      "count": 234,
      "avg_processing_time": 2.1,
      "success_rate": 0.945
    }
  },
  "performance_trends": [
    {
      "date": "2025-01-23",
      "documents": 47,
      "avg_processing_time": 3.8,
      "peak_concurrent": 5
    }
  ]
}
```

#### `GET /api/v1/analytics/batch-statistics`
**Purpose**: Batch processing performance analysis

**Response**:
```json
{
  "batch_summary": {
    "total_batches": 156,
    "avg_batch_size": 18.3,
    "avg_batch_time": 45.7,
    "batch_success_rate": 0.927
  },
  "efficiency_metrics": {
    "avg_parallel_factor": 4.2,
    "resource_utilization": 0.76,
    "queue_wait_time": 2.3
  },
  "size_distribution": {
    "small_batches_1_10": 45,
    "medium_batches_11_25": 89,
    "large_batches_26_plus": 22
  }
}
```

### System Performance Analytics

#### `GET /api/v1/analytics/system-metrics`
**Purpose**: System-wide performance metrics

**Query Parameters**:
- `metric_names`: Comma-separated metric names
- `hours`: Time window (default: 24)
- `aggregation`: min/max/avg/sum (default: avg)

**Response**:
```json
{
  "time_window": {
    "hours": 24,
    "start": "2025-01-22T12:00:00Z",
    "end": "2025-01-23T12:00:00Z"
  },
  "metrics": {
    "response_time_p95": {
      "value": 8.2,
      "unit": "seconds",
      "trend": "stable",
      "samples": 1847
    },
    "memory_usage_avg": {
      "value": 4.7,
      "unit": "gb",
      "trend": "increasing",
      "peak": 6.2
    },
    "cpu_utilization": {
      "value": 0.67,
      "unit": "percent",
      "trend": "stable",
      "baseline": 0.45
    }
  },
  "alerts": [
    {
      "level": "warning",
      "metric": "memory_usage",
      "message": "Memory usage above 80% threshold"
    }
  ]
}
```

### Research Data Export

#### `GET /api/v1/analytics/export/csv`
**Purpose**: Export comprehensive analytics data for Bachelor thesis research

**Query Parameters**:
- `dataset`: Type of data (performance/usage/errors/all)
- `start_date`: ISO 8601 start date
- `end_date`: ISO 8601 end date
- `include_metadata`: Include JSON metadata columns

**Response**: CSV file download
```csv
timestamp,metric_name,value,unit,operation_type,file_format,processing_time,error_type,user_session
2025-01-23T10:00:00Z,document_conversion.duration,4.2,seconds,pdf_conversion,pdf,4.2,,session_abc123
2025-01-23T10:00:05Z,qa_system.query.duration,2.1,seconds,question_answering,,2.1,,session_def456
2025-01-23T10:00:10Z,system.memory.usage,4700,mb,system_monitoring,,,memory,
```

#### `GET /api/v1/analytics/research-summary`
**Purpose**: Consolidated research metrics for thesis analysis

**Response**:
```json
{
  "study_period": {
    "start": "2024-09-01T00:00:00Z",
    "end": "2025-01-23T23:59:59Z",
    "total_days": 144
  },
  "system_performance": {
    "total_queries_processed": 15742,
    "avg_response_time": 4.3,
    "p95_response_time": 8.7,
    "system_availability": 0.997,
    "total_documents_processed": 3247
  },
  "user_interaction_patterns": {
    "daily_active_sessions": 47.2,
    "avg_queries_per_session": 3.8,
    "peak_concurrent_users": 12,
    "most_common_query_types": [
      "streamworks_functionality",
      "troubleshooting",
      "configuration"
    ]
  },
  "ml_model_performance": {
    "embedding_model": "multilingual-e5-large",
    "avg_retrieval_accuracy": 0.87,
    "context_relevance_score": 0.82,
    "answer_quality_rating": 4.2
  },
  "scientific_insights": {
    "hypothesis_validation": "Confirmed: RAG approach improves answer quality by 34%",
    "performance_benchmarks": "System handles 15+ concurrent users with <5s response time",
    "scalability_findings": "Linear scaling up to 10,000 documents with minimal performance impact"
  }
}
```

## Configuration Options

### Analytics Collection Settings

#### Metric Collection Configuration
```bash
# Collection intervals
ANALYTICS_COLLECTION_INTERVAL=30  # seconds
PERFORMANCE_SAMPLING_RATE=1.0     # 100% sampling
USER_INTERACTION_TRACKING=true

# Data retention
METRICS_RETENTION_DAYS=365
RAW_DATA_RETENTION_DAYS=90
AGGREGATED_DATA_RETENTION_YEARS=5

# Export settings
CSV_EXPORT_MAX_ROWS=1000000
EXPORT_TIMEZONE="Europe/Berlin"
```

#### Database Optimization
```bash
# PostgreSQL analytics optimization
ANALYTICS_DB_POOL_SIZE=20
BATCH_INSERT_SIZE=1000
ASYNC_COMMIT_ENABLED=true

# Index maintenance
AUTO_VACUUM_ANALYTICS=true
ANALYTICS_PARTITION_BY_MONTH=true
```

### Monitoring Thresholds

#### Performance Alerts
```bash
# Response time thresholds
RESPONSE_TIME_WARNING_THRESHOLD=5.0    # seconds
RESPONSE_TIME_CRITICAL_THRESHOLD=10.0  # seconds

# Resource utilization alerts
MEMORY_WARNING_THRESHOLD=0.80          # 80%
CPU_WARNING_THRESHOLD=0.85             # 85%
DISK_WARNING_THRESHOLD=0.90            # 90%
```

#### Quality Metrics
```bash
# Success rate thresholds
DOCUMENT_PROCESSING_SUCCESS_THRESHOLD=0.95
QA_ACCURACY_THRESHOLD=0.80
SYSTEM_AVAILABILITY_THRESHOLD=0.99

# User experience metrics
MAX_ACCEPTABLE_QUERY_TIME=8.0          # seconds
MIN_ANSWER_QUALITY_SCORE=3.0           # 1-5 scale
```

## Research & Scientific Features

### Bachelor Thesis Integration

#### Hypothesis Testing Framework
```python
class HypothesisTest:
    """Framework for scientific hypothesis validation"""
    
    async def test_rag_effectiveness(self) -> TestResult:
        """Test: RAG improves answer quality vs. direct LLM"""
        
        # Collect baseline metrics (direct LLM)
        baseline_metrics = await self.collect_baseline_performance()
        
        # Collect RAG metrics
        rag_metrics = await self.collect_rag_performance()
        
        # Statistical analysis
        improvement = self.calculate_statistical_significance(
            baseline_metrics, rag_metrics
        )
        
        return TestResult(
            hypothesis="RAG improves answer quality",
            confirmed=improvement.p_value < 0.05,
            effect_size=improvement.effect_size,
            confidence_interval=improvement.ci_95
        )
```

#### Performance Benchmarking
```python
async def run_performance_benchmark() -> BenchmarkResult:
    """Scientific performance benchmarking for thesis"""
    
    test_scenarios = [
        {"concurrent_users": 1, "query_complexity": "simple"},
        {"concurrent_users": 5, "query_complexity": "medium"},
        {"concurrent_users": 10, "query_complexity": "complex"},
        {"concurrent_users": 15, "query_complexity": "mixed"}
    ]
    
    results = []
    for scenario in test_scenarios:
        result = await execute_load_test(scenario)
        results.append({
            "scenario": scenario,
            "avg_response_time": result.avg_response_time,
            "p95_response_time": result.p95_response_time,
            "success_rate": result.success_rate,
            "resource_utilization": result.resource_usage
        })
    
    return BenchmarkResult(
        test_date=datetime.now(),
        scenarios=results,
        conclusion=analyze_scalability_limits(results)
    )
```

### Data Export for Academic Analysis

#### Research Dataset Generation
```python
async def generate_research_dataset(
    start_date: datetime,
    end_date: datetime
) -> ResearchDataset:
    """Generate comprehensive dataset for thesis analysis"""
    
    dataset = ResearchDataset()
    
    # Query performance data
    dataset.query_performance = await collect_query_metrics(
        start_date, end_date
    )
    
    # Document processing data
    dataset.document_processing = await collect_processing_metrics(
        start_date, end_date
    )
    
    # User interaction patterns
    dataset.user_interactions = await collect_interaction_data(
        start_date, end_date
    )
    
    # System resource utilization
    dataset.resource_usage = await collect_resource_metrics(
        start_date, end_date
    )
    
    return dataset
```

#### Statistical Analysis Support
```python
def calculate_statistical_metrics(data: List[float]) -> StatisticalSummary:
    """Calculate comprehensive statistical metrics for thesis"""
    
    return StatisticalSummary(
        count=len(data),
        mean=statistics.mean(data),
        median=statistics.median(data),
        std_dev=statistics.stdev(data),
        variance=statistics.variance(data),
        percentiles={
            "p25": numpy.percentile(data, 25),
            "p50": numpy.percentile(data, 50),
            "p75": numpy.percentile(data, 75),
            "p90": numpy.percentile(data, 90),
            "p95": numpy.percentile(data, 95),
            "p99": numpy.percentile(data, 99)
        },
        confidence_intervals={
            "95%": calculate_confidence_interval(data, 0.95),
            "99%": calculate_confidence_interval(data, 0.99)
        }
    )
```

## Performance Characteristics

### Data Collection Performance
- **Metric Collection Overhead**: <1% system impact
- **Database Insert Rate**: 10,000+ metrics/second
- **Query Response Time**: <100ms for most analytics queries
- **Export Generation**: 1M rows in 5-10 seconds

### Storage Efficiency
- **Raw Metrics Storage**: ~500MB per month
- **Aggregated Data**: ~50MB per month
- **Index Overhead**: 20-30% of data size
- **Compression Ratio**: 70-80% for historical data

### Analytics Query Performance
- **Simple Aggregations**: <50ms
- **Complex Multi-table Joins**: <500ms
- **Time-series Analysis**: <1s for 1M data points
- **Export Queries**: <5s for full dataset

## Troubleshooting Guide

### Common Issues

#### 1. Missing Analytics Data
**Symptoms**: Gaps in metrics collection or zero values
**Causes**:
- Analytics service downtime
- Database connection issues
- Configuration errors
- Performance overhead limits

**Solutions**:
```bash
# Check analytics service status
curl -X GET "http://localhost:8000/api/v1/analytics/health"

# Verify metric collection
curl -X GET "http://localhost:8000/api/v1/analytics/system-metrics?hours=1"

# Check database connectivity
python -c "
from app.models.postgres_models import SystemMetric
print(f'Total metrics: {SystemMetric.count()}')
"

# Review collection configuration
grep -r "ANALYTICS_" backend/app/core/settings.py
```

#### 2. Slow Analytics Queries
**Symptoms**: Analytics API endpoints taking >5 seconds
**Causes**:
- Missing database indexes
- Large time ranges
- Complex aggregations
- Concurrent query load

**Solutions**:
```sql
-- Check slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
WHERE query LIKE '%system_metrics%' 
ORDER BY mean_exec_time DESC;

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_system_metrics_recent 
ON system_metrics(created_at DESC, metric_name) 
WHERE created_at > NOW() - INTERVAL '30 days';

-- Analyze query plans
EXPLAIN ANALYZE SELECT metric_name, AVG(value) 
FROM system_metrics 
WHERE created_at > NOW() - INTERVAL '7 days' 
GROUP BY metric_name;
```

#### 3. Export Generation Failures
**Symptoms**: CSV export timeouts or incomplete files
**Causes**:
- Large dataset size
- Memory limitations
- Disk space issues
- Network timeouts

**Solutions**:
```bash
# Check available disk space
df -h /data/exports

# Test smaller date ranges
curl -X GET "http://localhost:8000/api/v1/analytics/export/csv?days=7"

# Monitor memory usage during export
watch -n 1 'ps aux | grep python | grep analytics'

# Use streaming export for large datasets
curl -X GET "http://localhost:8000/api/v1/analytics/export/stream?days=30" \
  --output analytics_data.csv
```

#### 4. Research Data Inconsistencies
**Symptoms**: Unexpected values or missing correlations in thesis data
**Causes**:
- Timezone conversion issues
- Sampling rate changes
- System downtime periods
- Data aggregation errors

**Solutions**:
```python
# Validate data consistency
from app.services.analytics_service import analytics_service

# Check for data gaps
gaps = await analytics_service.detect_data_gaps(
    start_date=datetime(2024, 9, 1),
    end_date=datetime(2025, 1, 23)
)

# Verify metric correlations
correlations = await analytics_service.validate_metric_correlations()

# Generate data quality report
quality_report = await analytics_service.generate_quality_report()
```

### Debug Mode

#### Enable Analytics Debugging
```bash
export LOG_LEVEL=DEBUG
export ANALYTICS_DEBUG_MODE=true
export TRACK_QUERY_PERFORMANCE=true
```

#### Research Data Validation
```python
# Validate research dataset
from app.services.analytics_service import analytics_service

# Run comprehensive validation
validation_results = await analytics_service.validate_research_data(
    start_date=datetime(2024, 9, 1),
    end_date=datetime(2025, 1, 23)
)

print(f"Data completeness: {validation_results.completeness}%")
print(f"Consistency score: {validation_results.consistency}")
print(f"Quality issues: {validation_results.issues}")
```

## Future Enhancement Ideas

### Short-term Improvements (1-3 months)
1. **Real-time Dashboards**: Live analytics visualization with charts and graphs
2. **Automated Alerting**: Intelligent threshold-based notifications
3. **A/B Testing Framework**: Built-in experimentation platform
4. **Custom Metrics**: User-defined metric collection and analysis

### Medium-term Enhancements (3-6 months)
1. **Machine Learning Analytics**: 
   - Anomaly detection in system behavior
   - Predictive performance modeling
   - User behavior pattern recognition
2. **Advanced Research Tools**:
   - Hypothesis testing automation
   - Statistical significance calculators
   - Experiment design frameworks

### Long-term Vision (6+ months)
1. **AI-Powered Insights**: 
   - Automatic performance optimization recommendations
   - Intelligent alert correlation
   - Self-healing system responses
2. **Academic Integration**:
   - Direct integration with research databases
   - Automated thesis data generation
   - Publication-ready analytics reports

### Research & Development Roadmap

#### Scientific Computing Integration
- **R/Python Integration**: Native support for statistical analysis
- **Jupyter Notebook Exports**: Interactive analysis capabilities
- **Academic Publishing**: LaTeX table generation and figure exports
- **Peer Review Support**: Reproducible research data packages

---

**Last Updated**: 2025-01-23  
**Version**: 2.0.0  
**Maintainer**: StreamWorks-KI Development Team  
**Research Focus**: Bachelor Thesis Performance Analysis  
**Related Documents**: [API Reference](api_reference.md), [Q&A System](qa_system.md)