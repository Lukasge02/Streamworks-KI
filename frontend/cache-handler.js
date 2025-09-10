const { IncrementalCache } = require('next/dist/server/lib/incremental-cache')

module.exports = class CustomCacheHandler extends IncrementalCache {
  constructor(options) {
    super(options)
  }

  async get(key) {
    try {
      return await super.get(key)
    } catch (error) {
      console.warn('Cache get error, returning null:', error.message)
      return null
    }
  }

  async set(key, data, ctx) {
    try {
      return await super.set(key, data, ctx)
    } catch (error) {
      console.warn('Cache set error, skipping:', error.message)
      return
    }
  }
}