/**
 * Enterprise-grade resilience utilities for Streamworks RAG System
 * Implements retry, circuit breaker, and exponential backoff patterns
 */

interface RetryOptions {
  maxRetries: number
  baseDelay: number
  maxDelay: number
  exponentialBase: number
  jitterMax: number
  retryCondition?: (error: any) => boolean
}

interface CircuitBreakerOptions {
  failureThreshold: number
  resetTimeout: number
  monitoringPeriod: number
}

class CircuitBreaker {
  private failures = 0
  private nextAttempt = Date.now()
  private state: 'closed' | 'open' | 'half-open' = 'closed'

  constructor(private options: CircuitBreakerOptions) {}

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN - operation not attempted')
      }
      this.state = 'half-open'
    }

    try {
      const result = await operation()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }

  private onSuccess() {
    this.failures = 0
    this.state = 'closed'
  }

  private onFailure() {
    this.failures++
    if (this.failures >= this.options.failureThreshold) {
      this.state = 'open'
      this.nextAttempt = Date.now() + this.options.resetTimeout
    }
  }

  getState() {
    return {
      state: this.state,
      failures: this.failures,
      nextAttempt: this.nextAttempt
    }
  }
}

export class ResilienceManager {
  private static instance: ResilienceManager
  private circuitBreakers = new Map<string, CircuitBreaker>()

  static getInstance(): ResilienceManager {
    if (!ResilienceManager.instance) {
      ResilienceManager.instance = new ResilienceManager()
    }
    return ResilienceManager.instance
  }

  /**
   * Execute operation with retry logic and exponential backoff
   */
  async withRetry<T>(
    operation: () => Promise<T>,
    options: Partial<RetryOptions> = {}
  ): Promise<T> {
    const config: RetryOptions = {
      maxRetries: 3,
      baseDelay: 1000,
      maxDelay: 10000,
      exponentialBase: 2,
      jitterMax: 100,
      retryCondition: (error) => this.isRetryableError(error),
      ...options
    }

    let lastError: any
    
    for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
      try {
        return await operation()
      } catch (error) {
        lastError = error
        
        // Don't retry if this is the last attempt or error is not retryable
        if (attempt === config.maxRetries || !config.retryCondition!(error)) {
          break
        }

        const delay = this.calculateDelay(attempt, config)
        console.warn(`Operation failed (attempt ${attempt + 1}/${config.maxRetries + 1}), retrying in ${delay}ms:`, error)
        
        await this.sleep(delay)
      }
    }

    throw lastError
  }

  /**
   * Execute operation with circuit breaker protection
   */
  async withCircuitBreaker<T>(
    operation: () => Promise<T>,
    circuitName: string,
    options: Partial<CircuitBreakerOptions> = {}
  ): Promise<T> {
    const config: CircuitBreakerOptions = {
      failureThreshold: 5,
      resetTimeout: 60000, // 1 minute
      monitoringPeriod: 10000, // 10 seconds
      ...options
    }

    if (!this.circuitBreakers.has(circuitName)) {
      this.circuitBreakers.set(circuitName, new CircuitBreaker(config))
    }

    const breaker = this.circuitBreakers.get(circuitName)!
    return breaker.execute(operation)
  }

  /**
   * Combine retry and circuit breaker patterns
   */
  async withFullResilience<T>(
    operation: () => Promise<T>,
    circuitName: string,
    retryOptions: Partial<RetryOptions> = {},
    circuitOptions: Partial<CircuitBreakerOptions> = {}
  ): Promise<T> {
    return this.withCircuitBreaker(
      () => this.withRetry(operation, retryOptions),
      circuitName,
      circuitOptions
    )
  }

  /**
   * Calculate delay with exponential backoff and jitter
   */
  private calculateDelay(attempt: number, options: RetryOptions): number {
    const exponentialDelay = options.baseDelay * Math.pow(options.exponentialBase, attempt)
    const jitter = Math.random() * options.jitterMax
    return Math.min(exponentialDelay + jitter, options.maxDelay)
  }

  /**
   * Determine if error should trigger a retry
   */
  private isRetryableError(error: any): boolean {
    // Network errors
    if (error.name === 'NetworkError' || error.code === 'NETWORK_ERROR') return true
    
    // HTTP status codes that are retryable
    if (error.status) {
      const retryableStatuses = [408, 429, 500, 502, 503, 504]
      return retryableStatuses.includes(error.status)
    }

    // Supabase specific errors
    if (error.message) {
      const retryableMessages = [
        'connection timed out',
        'connection refused',
        'temporary failure',
        'rate limit exceeded'
      ]
      const message = error.message.toLowerCase()
      return retryableMessages.some(msg => message.includes(msg))
    }

    return false
  }

  /**
   * Sleep utility
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  /**
   * Get circuit breaker status for monitoring
   */
  getCircuitBreakerStatus(): Record<string, any> {
    const status: Record<string, any> = {}
    this.circuitBreakers.forEach((breaker, name) => {
      status[name] = breaker.getState()
    })
    return status
  }
}

// Export singleton instance
export const resilience = ResilienceManager.getInstance()

// Convenience functions
export const withRetry = <T>(op: () => Promise<T>, options?: Partial<RetryOptions>) => 
  resilience.withRetry(op, options)

export const withCircuitBreaker = <T>(op: () => Promise<T>, name: string, options?: Partial<CircuitBreakerOptions>) => 
  resilience.withCircuitBreaker(op, name, options)

export const withFullResilience = <T>(
  op: () => Promise<T>, 
  name: string, 
  retryOpts?: Partial<RetryOptions>, 
  circuitOpts?: Partial<CircuitBreakerOptions>
) => resilience.withFullResilience(op, name, retryOpts, circuitOpts)