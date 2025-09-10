-- Migration: Add AI Summary Caching Fields to Documents Table
-- This migration adds fields to cache AI-generated summaries for better performance

-- Add AI summary caching fields
ALTER TABLE documents 
ADD COLUMN ai_summary TEXT,
ADD COLUMN summary_key_points JSONB,
ADD COLUMN summary_generated_at TIMESTAMP;

-- Add index on summary_generated_at for performance
CREATE INDEX idx_documents_summary_generated_at ON documents(summary_generated_at);

-- Add comment for documentation
COMMENT ON COLUMN documents.ai_summary IS 'Cached AI-generated summary text';
COMMENT ON COLUMN documents.summary_key_points IS 'JSON array of key points extracted by AI';
COMMENT ON COLUMN documents.summary_generated_at IS 'Timestamp when the summary was generated';