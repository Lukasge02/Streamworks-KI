-- StreamWorks-KI PostgreSQL Initialization
-- Performance and RAG-optimized extensions

-- Enable required extensions for better performance
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For similarity searches
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For JSON indexing

-- Create custom functions for RAG optimization
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Comment for documentation
COMMENT ON FUNCTION update_modified_column() IS 'Automatically updates updated_at timestamp on row modification';

-- Set timezone
SET timezone = 'Europe/Berlin';

-- Optimize for RAG workloads
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET random_page_cost = 1.1;  -- SSD optimization
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Enable query logging for performance analysis
ALTER SYSTEM SET log_statement = 'mod';
ALTER SYSTEM SET log_min_duration_statement = 1000;

SELECT pg_reload_conf();