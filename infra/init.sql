-- StreamWorks RAG Database Initialization
-- This script runs when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set search path
ALTER DATABASE ragdb SET search_path TO rag, public;

-- Create initial user permissions
GRANT ALL PRIVILEGES ON SCHEMA rag TO rag;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO rag;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'StreamWorks RAG Database initialized successfully';
    RAISE NOTICE 'Database: ragdb | User: rag | Schemas: rag, analytics';
END $$;