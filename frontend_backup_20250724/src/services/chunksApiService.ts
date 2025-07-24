import { 
  ChunksListResponse, 
  ChunkDetailsResponse, 
  ChunksStatisticsResponse,
  ApiResponse 
} from '../types';

// Cache configuration
interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiry: number;
}

interface RequestConfig {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  cacheKey?: string;
  cacheTTL?: number;
}

interface ChunksSearchParams {
  limit?: number;
  offset?: number;
  search?: string;
  sourceFile?: string;
  category?: string;
  sortBy?: string;
  sortOrder?: string;
}

export class ChunksApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
    public retryable: boolean = false
  ) {
    super(message);
    this.name = 'ChunksApiError';
  }
}

export class ChunksApiService {
  private baseUrl = '/api/v1';
  private cache = new Map<string, CacheEntry<any>>();
  private pendingRequests = new Map<string, Promise<any>>();
  private abortControllers = new Map<string, AbortController>();

  // Default configuration
  private defaultConfig: RequestConfig = {
    timeout: 30000,
    retries: 3,
    retryDelay: 1000,
    cacheTTL: 5 * 60 * 1000, // 5 minutes
  };

  /**
   * Generate cache key from URL and params
   */
  private generateCacheKey(url: string, params?: Record<string, any>): string {
    const sortedParams = params ? 
      Object.keys(params)
        .sort()
        .map(key => `${key}=${params[key]}`)
        .join('&') 
      : '';
    return `${url}${sortedParams ? `?${sortedParams}` : ''}`;
  }

  /**
   * Check if cached data is still valid
   */
  private isCacheValid<T>(entry: CacheEntry<T>): boolean {
    return Date.now() < entry.timestamp + entry.expiry;
  }

  /**
   * Get data from cache if available and valid
   */
  private getFromCache<T>(cacheKey: string): T | null {
    const entry = this.cache.get(cacheKey);
    if (entry && this.isCacheValid(entry)) {
      return entry.data;
    }
    if (entry) {
      this.cache.delete(cacheKey);
    }
    return null;
  }

  /**
   * Store data in cache
   */
  private setCache<T>(cacheKey: string, data: T, ttl: number): void {
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now(),
      expiry: ttl,
    });
  }

  /**
   * Sleep utility for retry delays
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Determine if error is retryable
   */
  private isRetryableError(error: any): boolean {
    // Network errors
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return true;
    }
    
    // HTTP status codes that are retryable
    if (error.status) {
      const retryableStatuses = [408, 429, 500, 502, 503, 504];
      return retryableStatuses.includes(error.status);
    }

    return false;
  }

  /**
   * Make HTTP request with retry logic
   */
  private async makeRequest<T>(
    url: string,
    options: RequestInit = {},
    config: RequestConfig = {}
  ): Promise<T> {
    const mergedConfig = { ...this.defaultConfig, ...config };
    const cacheKey = config.cacheKey || this.generateCacheKey(url, options.body ? JSON.parse(options.body as string) : undefined);

    // Check cache first for GET requests
    if (!options.method || options.method === 'GET') {
      const cached = this.getFromCache<T>(cacheKey);
      if (cached) {
        return cached;
      }

      // Check if request is already pending
      const pending = this.pendingRequests.get(cacheKey);
      if (pending) {
        return pending;
      }
    }

    // Create abort controller for this request
    const abortController = new AbortController();
    const requestId = `${Date.now()}-${Math.random()}`;
    this.abortControllers.set(requestId, abortController);

    const requestPromise = this.executeRequest<T>(
      url,
      { 
        ...options, 
        signal: abortController.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        }
      },
      mergedConfig,
      cacheKey
    );

    // Store pending request
    if (!options.method || options.method === 'GET') {
      this.pendingRequests.set(cacheKey, requestPromise);
    }

    try {
      const result = await requestPromise;
      return result;
    } finally {
      // Cleanup
      this.abortControllers.delete(requestId);
      if (!options.method || options.method === 'GET') {
        this.pendingRequests.delete(cacheKey);
      }
    }
  }

  /**
   * Execute HTTP request with timeout and retry logic
   */
  private async executeRequest<T>(
    url: string,
    options: RequestInit,
    config: RequestConfig,
    cacheKey?: string
  ): Promise<T> {
    let lastError: Error;

    for (let attempt = 1; attempt <= (config.retries || 1); attempt++) {
      try {
        // Set up timeout
        const timeoutId = setTimeout(() => {
          if (options.signal && !options.signal.aborted) {
            (options.signal as any).abort();
          }
        }, config.timeout);

        const response = await fetch(url, options);
        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          const error = new ChunksApiError(
            errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
            response.status,
            errorData.code,
            this.isRetryableError({ status: response.status })
          );

          if (!error.retryable || attempt === config.retries) {
            throw error;
          }

          lastError = error;
          await this.sleep((config.retryDelay || 1000) * attempt);
          continue;
        }

        const data = await response.json();

        // Cache successful GET responses
        if ((!options.method || options.method === 'GET') && cacheKey && config.cacheTTL) {
          this.setCache(cacheKey, data, config.cacheTTL);
        }

        return data;

      } catch (error: any) {
        if (error.name === 'AbortError') {
          throw new ChunksApiError('Request was cancelled', 0, 'CANCELLED');
        }

        if (!this.isRetryableError(error) || attempt === config.retries) {
          throw error instanceof ChunksApiError ? error : 
            new ChunksApiError(
              error.message || 'Network request failed',
              error.status,
              error.code,
              this.isRetryableError(error)
            );
        }

        lastError = error;
        await this.sleep((config.retryDelay || 1000) * attempt);
      }
    }

    throw lastError!;
  }

  /**
   * Cancel all pending requests
   */
  public cancelAllRequests(): void {
    this.abortControllers.forEach(controller => {
      controller.abort();
    });
    this.abortControllers.clear();
    this.pendingRequests.clear();
  }

  /**
   * Clear all cached data
   */
  public clearCache(): void {
    this.cache.clear();
  }

  /**
   * Clear cache for specific key pattern
   */
  public clearCachePattern(pattern: string): void {
    const regex = new RegExp(pattern);
    Array.from(this.cache.keys()).forEach(key => {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    });
  }

  /**
   * Get chunks with advanced filtering and pagination
   */
  async getChunks(params: ChunksSearchParams = {}, config?: RequestConfig): Promise<ApiResponse<ChunksListResponse>> {
    try {
      const searchParams = new URLSearchParams();
      
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          searchParams.append(key, value.toString());
        }
      });

      const url = `${this.baseUrl}/chunks${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
      const data = await this.makeRequest<ChunksListResponse>(url, {}, {
        ...config,
        cacheKey: this.generateCacheKey('/chunks', params),
        cacheTTL: 2 * 60 * 1000, // 2 minutes cache for chunk lists
      });

      return { success: true, data };
    } catch (error) {
      console.error('Get chunks error:', error);
      return { 
        success: false, 
        error: error instanceof ChunksApiError ? error.message : `Chunks laden fehlgeschlagen: ${error}` 
      };
    }
  }

  /**
   * Get chunk details by ID
   */
  async getChunkDetails(chunkId: string, config?: RequestConfig): Promise<ApiResponse<ChunkDetailsResponse>> {
    try {
      const url = `${this.baseUrl}/chunks/${encodeURIComponent(chunkId)}`;
      const data = await this.makeRequest<ChunkDetailsResponse>(url, {}, {
        ...config,
        cacheTTL: 10 * 60 * 1000, // 10 minutes cache for chunk details
      });

      return { success: true, data };
    } catch (error) {
      console.error('Get chunk details error:', error);
      return { 
        success: false, 
        error: error instanceof ChunksApiError ? error.message : `Chunk-Details laden fehlgeschlagen: ${error}` 
      };
    }
  }

  /**
   * Search chunks with debouncing support
   */
  async searchChunks(query: string, limit: number = 10, config?: RequestConfig): Promise<ApiResponse<ChunksListResponse>> {
    try {
      if (!query.trim()) {
        return { success: true, data: { chunks: [], total: 0, limit, offset: 0, has_more: false } };
      }

      const params = new URLSearchParams();
      params.append('query', query);
      params.append('limit', limit.toString());

      const url = `${this.baseUrl}/chunks/search?${params.toString()}`;
      const data = await this.makeRequest<ChunksListResponse>(url, {}, {
        ...config,
        cacheTTL: 1 * 60 * 1000, // 1 minute cache for search results
        cacheKey: this.generateCacheKey('/chunks/search', { query, limit }),
      });

      return { success: true, data };
    } catch (error) {
      console.error('Search chunks error:', error);
      return { 
        success: false, 
        error: error instanceof ChunksApiError ? error.message : `Chunks suchen fehlgeschlagen: ${error}` 
      };
    }
  }

  /**
   * Get chunks statistics
   */
  async getChunksStatistics(config?: RequestConfig): Promise<ApiResponse<ChunksStatisticsResponse>> {
    try {
      const url = `${this.baseUrl}/chunks/statistics`;
      const data = await this.makeRequest<ChunksStatisticsResponse>(url, {}, {
        ...config,
        cacheTTL: 5 * 60 * 1000, // 5 minutes cache for statistics
      });

      return { success: true, data };
    } catch (error) {
      console.error('Get chunks statistics error:', error);
      return { 
        success: false, 
        error: error instanceof ChunksApiError ? error.message : `Chunks-Statistiken laden fehlgeschlagen: ${error}` 
      };
    }
  }

  /**
   * Prefetch data for better performance
   */
  async prefetchChunks(params: ChunksSearchParams = {}): Promise<void> {
    try {
      await this.getChunks(params, { cacheTTL: 10 * 60 * 1000 });
    } catch (error) {
      // Prefetch errors are silent
      console.debug('Prefetch chunks failed:', error);
    }
  }

  /**
   * Get cache statistics for debugging
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }
}

// Export singleton instance
export const chunksApiService = new ChunksApiService();