export interface RagLiveMetricsResponse {
  status: 'initializing' | 'ok' | 'degraded' | 'error'
  window_minutes: number
  updated_at: string
  totals: {
    queries: number
    successful: number
    failed: number
    cache_hit_rate: number
  }
  latency: {
    average_ms: number
    p95_ms: number
    p99_ms: number
  }
  quality: {
    avg_relevance: number
    avg_sources_per_query: number
    unique_sources: number
  }
}

export interface RagSourceInsightsResponse {
  status: 'initializing' | 'ok'
  updated_at: string
  totals: {
    documents: number
    usages: number
  }
  top_documents: Array<{
    document_id: string
    filename: string
    usage_count: number
    avg_relevance: number
    avg_confidence: number
    last_used: string | null
  }>
}

export interface RagActivityResponse {
  status: 'initializing' | 'ok'
  updated_at: string
  window_minutes: number
  bucket_size_minutes: number
  buckets: Array<{
    start: string
    end: string
    total_queries: number
    avg_response_time_ms: number
    cache_hit_rate: number
    error_count: number
  }>
}
