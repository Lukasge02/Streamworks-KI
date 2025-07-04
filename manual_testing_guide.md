# 🧪 StreamWorks-KI Manual Testing Guide

## Server Setup
```bash
cd /Applications/Programmieren/Visual\ Studio/Bachelorarbeit/Streamworks-KI/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Server URL: `http://localhost:8000`

---

## 🏥 1. HEALTH SYSTEM TESTING

### Basic Health Checks
```bash
# 1. Quick health check (load balancer style)
curl http://localhost:8000/api/v1/health/quick

# 2. Comprehensive system health
curl http://localhost:8000/api/v1/health/

# 3. Component-specific health checks
curl http://localhost:8000/api/v1/health/component/database
curl http://localhost:8000/api/v1/health/component/rag_service
curl http://localhost:8000/api/v1/health/component/xml_generator
curl http://localhost:8000/api/v1/health/component/llm_service

# 4. Health metrics for monitoring
curl http://localhost:8000/api/v1/health/metrics
```

### Expected Results:
- ✅ Status: "healthy", "degraded", or "unhealthy"
- ✅ Response times in milliseconds
- ✅ Component-specific details
- ✅ System resource information

---

## 🔬 2. EVALUATION SERVICE TESTING

### Current Metrics
```bash
# Get current evaluation metrics
curl http://localhost:8000/api/v1/evaluation/metrics
```

### Manual Evaluation
```bash
# Trigger manual evaluation
curl -X POST "http://localhost:8000/api/v1/evaluation/manual" \
-H "Content-Type: application/json" \
-d '{
  "query": "Wie erstelle ich einen StreamWorks Batch Job?",
  "response": "Um einen StreamWorks Batch Job zu erstellen, verwenden Sie die Administration Console...",
  "sources": ["streamworks_manual.txt", "batch_guide.pdf"],
  "confidence": 0.85,
  "response_time": 750
}'
```

### Performance Reports
```bash
# Get performance report (last 7 days)
curl http://localhost:8000/api/v1/evaluation/report

# Get evaluation trends
curl http://localhost:8000/api/v1/evaluation/trends

# Get evaluation history
curl http://localhost:8000/api/v1/evaluation/history

# Check for alerts
curl http://localhost:8000/api/v1/evaluation/alerts
```

### Expected Results:
- ✅ Relevance scores (0-1)
- ✅ Completeness scores (0-1)
- ✅ Hallucination detection (0-1)
- ✅ Response time metrics
- ✅ Statistical trends and insights

---

## 🧪 3. A/B TESTING FRAMEWORK

### Create Experiment
```bash
# Create new A/B test experiment
curl -X POST "http://localhost:8000/api/v1/ab-testing/experiment" \
-H "Content-Type: application/json" \
-d '{
  "name": "Prompt Style Test",
  "description": "Testing formal vs casual prompt styles",
  "variants": [
    {
      "name": "Formal Style",
      "type": "prompt",
      "config": {"style": "formal", "temperature": 0.7},
      "weight": 0.5
    },
    {
      "name": "Casual Style", 
      "type": "prompt",
      "config": {"style": "casual", "temperature": 0.8},
      "weight": 0.5
    }
  ],
  "target_sample_size": 100
}'
```

### Start Experiment
```bash
# Get experiment ID from previous response, then start it
curl -X POST "http://localhost:8000/api/v1/ab-testing/experiment/{EXPERIMENT_ID}/start"
```

### Get Variant for Testing
```bash
# Get a variant for current user
curl http://localhost:8000/api/v1/ab-testing/experiment/{EXPERIMENT_ID}/variant
```

### Record Results
```bash
# Record experiment result
curl -X POST "http://localhost:8000/api/v1/ab-testing/experiment/result" \
-H "Content-Type: application/json" \
-d '{
  "experiment_id": "{EXPERIMENT_ID}",
  "variant_id": "{VARIANT_ID}",
  "user_query": "How do I configure StreamWorks?",
  "response_time_ms": 850,
  "user_satisfaction": 4.2,
  "response_quality": 4.0,
  "conversion": true
}'
```

### View Results
```bash
# Get active experiments
curl http://localhost:8000/api/v1/ab-testing/active

# Get experiment results and analysis
curl http://localhost:8000/api/v1/ab-testing/results/{EXPERIMENT_ID}

# Get A/B testing statistics
curl http://localhost:8000/api/v1/ab-testing/stats
```

### Simulate Data (Development Only)
```bash
# Generate test data for experiment
curl -X POST "http://localhost:8000/api/v1/ab-testing/experiment/{EXPERIMENT_ID}/simulate?num_results=50"
```

### Expected Results:
- ✅ Statistical significance calculations
- ✅ Confidence intervals
- ✅ Performance comparisons
- ✅ Recommendation engine results

---

## 🤖 4. RAG SYSTEM TESTING

### Basic Chat
```bash
# Test RAG-based Q&A
curl -X POST "http://localhost:8000/api/v1/chat/" \
-H "Content-Type: application/json" \
-d '{
  "message": "Wie erstelle ich einen StreamWorks Batch Job?",
  "session_id": "test-session-123"
}'
```

### Document Search
```bash
# Search documents directly
curl "http://localhost:8000/api/v1/chat/search?query=batch job&limit=5"

# Get document list
curl http://localhost:8000/api/v1/chat/documents
```

### RAG Health
```bash
# RAG service health
curl http://localhost:8000/api/v1/chat/health

# RAG service status
curl http://localhost:8000/api/v1/chat/mistral-status
```

---

## 🔧 5. XML GENERATION TESTING

### Generate XML Stream
```bash
# Test XML generation
curl -X POST "http://localhost:8000/api/v1/xml/generate" \
-H "Content-Type: application/json" \
-d '{
  "name": "Daily Data Processing",
  "description": "Process daily customer data",
  "schedule": "daily",
  "source": "CSV",
  "destination": "Database",
  "data_source": "/data/customers.csv",
  "output_path": "/data/processed/"
}'
```

### XML Service Health
```bash
# XML generator health
curl http://localhost:8000/api/v1/xml/health

# Available templates
curl http://localhost:8000/api/v1/xml/templates
```

---

## 📊 6. PERFORMANCE MONITORING

### System Metrics
```bash
# Performance metrics
curl http://localhost:8000/api/v1/metrics

# Mistral-specific metrics
curl http://localhost:8000/api/v1/mistral-metrics
```

---

## 🖥️ 7. WEB INTERFACE TESTING

### Swagger Documentation
Open in browser: `http://localhost:8000/docs`

This provides:
- ✅ Interactive API documentation
- ✅ Try-it-out functionality for all endpoints
- ✅ Request/response schemas
- ✅ Authentication testing

### API Endpoints Overview
Open in browser: `http://localhost:8000/redoc`

---

## 🔧 8. INTEGRATION TESTING SCENARIOS

### Complete Workflow Test
```bash
# 1. Check system health
curl http://localhost:8000/api/v1/health/

# 2. Create A/B experiment
EXPERIMENT_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/ab-testing/experiment" \
-H "Content-Type: application/json" \
-d '{"name": "Integration Test", "description": "Full system test", "variants": [{"name": "V1", "type": "prompt", "config": {}, "weight": 1.0}]}')

# 3. Extract experiment ID and start experiment
# 4. Test RAG with evaluation
# 5. Generate XML with performance tracking
# 6. Analyze results
```

### Load Testing
```bash
# Simple load test (install httpie first: pip install httpie)
for i in {1..10}; do
  http POST localhost:8000/api/v1/chat/ message="Test query $i" session_id="load-test-$i" &
done
wait
```

---

## ✅ SUCCESS CRITERIA CHECKLIST

### Health System
- [ ] All components report health status
- [ ] Response times under 1000ms
- [ ] System resources monitored
- [ ] Error handling graceful

### Evaluation Service  
- [ ] Automatic quality assessment
- [ ] 5+ different metrics calculated
- [ ] Statistical trends available
- [ ] Performance reports generated

### A/B Testing
- [ ] Experiments created and started
- [ ] Statistical significance calculated
- [ ] Variants properly rotated
- [ ] Results analysis comprehensive

### RAG System
- [ ] Document search functional
- [ ] Chat responses relevant
- [ ] Sources properly cited
- [ ] Performance within targets

### XML Generation
- [ ] Valid XML generated
- [ ] Templates properly loaded
- [ ] Validation successful
- [ ] Error handling robust

---

## 🐛 TROUBLESHOOTING

### Common Issues

1. **Server won't start**
   ```bash
   # Check Python version
   python3 --version
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Database errors**
   - Development mode continues despite DB errors
   - Check logs for specific issues

3. **Model loading issues**
   - Ensure sufficient RAM (8GB+)
   - Check model cache directory

4. **Port conflicts**
   ```bash
   # Use different port
   uvicorn app.main:app --port 8001
   ```

### Logs and Debugging
- Server logs show in terminal
- Check individual service health endpoints
- Use `/docs` for API exploration
- Monitor response times and error rates

---

## 📈 PERFORMANCE BENCHMARKS

Expected performance targets:
- Health checks: < 100ms
- RAG queries: < 2000ms  
- XML generation: < 1000ms
- A/B variant selection: < 50ms
- Evaluation metrics: < 500ms

Monitor these via the metrics endpoints and health system!