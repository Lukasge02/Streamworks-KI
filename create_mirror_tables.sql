-- Supabase Mirror Tables
-- Non-critical mirroring of ChromaDB metadata for visibility/monitoring
-- ChromaDB remains the single master for RAG operations

-- Table: chunk_metadata_mirror
-- Purpose: Mirror ChromaDB chunk metadata for UI viewing
CREATE TABLE IF NOT EXISTS chunk_metadata_mirror (
    chunk_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    content_preview TEXT,
    word_count INTEGER DEFAULT 0,
    chunk_index INTEGER DEFAULT 0,
    processing_status TEXT DEFAULT 'indexed',
    sync_status TEXT DEFAULT 'synced',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast document-based queries
CREATE INDEX IF NOT EXISTS idx_chunk_metadata_document_id
ON chunk_metadata_mirror(document_id);

-- Index for chunk ordering
CREATE INDEX IF NOT EXISTS idx_chunk_metadata_chunk_index
ON chunk_metadata_mirror(chunk_index);

-- Index for status filtering
CREATE INDEX IF NOT EXISTS idx_chunk_metadata_status
ON chunk_metadata_mirror(processing_status);

-- Table: document_processing_stats
-- Purpose: Mirror document processing statistics
CREATE TABLE IF NOT EXISTS document_processing_stats (
    document_id TEXT PRIMARY KEY,
    chunk_count INTEGER DEFAULT 0,
    processing_engine TEXT DEFAULT 'llamaindex',
    embedding_model TEXT DEFAULT 'BAAI/bge-base-en-v1.5',
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for status queries
CREATE INDEX IF NOT EXISTS idx_document_processing_status
ON document_processing_stats(status);

-- Index for processing engine analysis
CREATE INDEX IF NOT EXISTS idx_document_processing_engine
ON document_processing_stats(processing_engine);

-- Table: chromadb_health_log
-- Purpose: Log ChromaDB health checks and stats
CREATE TABLE IF NOT EXISTS chromadb_health_log (
    id SERIAL PRIMARY KEY,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    collection_name TEXT DEFAULT 'streamworks_rag',
    total_chunks INTEGER DEFAULT 0,
    health_status TEXT DEFAULT 'healthy',
    storage_path TEXT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Index for health monitoring
CREATE INDEX IF NOT EXISTS idx_chromadb_health_recorded_at
ON chromadb_health_log(recorded_at);

-- Index for status analysis
CREATE INDEX IF NOT EXISTS idx_chromadb_health_status
ON chromadb_health_log(health_status);

-- Enable Row Level Security (RLS) for security
ALTER TABLE chunk_metadata_mirror ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_processing_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE chromadb_health_log ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
CREATE POLICY IF NOT EXISTS "Allow read access to chunk_metadata_mirror"
ON chunk_metadata_mirror FOR SELECT
USING (TRUE);

CREATE POLICY IF NOT EXISTS "Allow insert/update access to chunk_metadata_mirror"
ON chunk_metadata_mirror FOR ALL
USING (TRUE);

CREATE POLICY IF NOT EXISTS "Allow read access to document_processing_stats"
ON document_processing_stats FOR SELECT
USING (TRUE);

CREATE POLICY IF NOT EXISTS "Allow insert/update access to document_processing_stats"
ON document_processing_stats FOR ALL
USING (TRUE);

CREATE POLICY IF NOT EXISTS "Allow read access to chromadb_health_log"
ON chromadb_health_log FOR SELECT
USING (TRUE);

CREATE POLICY IF NOT EXISTS "Allow insert access to chromadb_health_log"
ON chromadb_health_log FOR INSERT
WITH CHECK (TRUE);

-- Comments for documentation
COMMENT ON TABLE chunk_metadata_mirror IS 'Non-critical mirror of ChromaDB chunk metadata for UI visibility';
COMMENT ON TABLE document_processing_stats IS 'Document processing statistics mirrored from ChromaDB operations';
COMMENT ON TABLE chromadb_health_log IS 'ChromaDB health monitoring and statistics log';

COMMENT ON COLUMN chunk_metadata_mirror.chunk_id IS 'Unique chunk identifier from ChromaDB';
COMMENT ON COLUMN chunk_metadata_mirror.document_id IS 'Parent document identifier';
COMMENT ON COLUMN chunk_metadata_mirror.content_preview IS 'First 200 characters of chunk content for UI preview';
COMMENT ON COLUMN chunk_metadata_mirror.sync_status IS 'Mirror synchronization status';

-- Create a view for easy monitoring
CREATE OR REPLACE VIEW mirror_status_summary AS
SELECT
    COUNT(DISTINCT document_id) as total_documents,
    COUNT(*) as total_chunks,
    COUNT(CASE WHEN processing_status = 'indexed' THEN 1 END) as indexed_chunks,
    COUNT(CASE WHEN sync_status = 'synced' THEN 1 END) as synced_chunks,
    AVG(word_count) as avg_word_count,
    MAX(created_at) as last_mirror_update
FROM chunk_metadata_mirror;

COMMENT ON VIEW mirror_status_summary IS 'Summary statistics for ChromaDB mirror status monitoring';

-- Success message
SELECT 'ChromaDB Mirror Tables Created Successfully!' as status;