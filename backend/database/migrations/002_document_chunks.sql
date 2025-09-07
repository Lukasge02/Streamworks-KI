-- Migration: Add document_chunks table for Docling integration
-- Date: 2025-09-05
-- Purpose: Enable structured chunk storage with cascade deletion

-- Create document_chunks table
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    heading TEXT,
    section_name TEXT,
    page_number INTEGER,
    chunk_type VARCHAR(50) DEFAULT 'text' CHECK (chunk_type IN ('text', 'table', 'image', 'code')),
    chunk_metadata JSONB DEFAULT '{}',
    word_count INTEGER,
    char_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_type ON document_chunks(chunk_type);
CREATE INDEX IF NOT EXISTS idx_document_chunks_page ON document_chunks(page_number);
CREATE INDEX IF NOT EXISTS idx_document_chunks_created ON document_chunks(created_at);

-- Add composite index for chunk ordering
CREATE INDEX IF NOT EXISTS idx_document_chunks_order ON document_chunks(document_id, chunk_index);

-- Add trigger for updating updated_at timestamp
CREATE OR REPLACE FUNCTION update_document_chunks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_document_chunks_updated_at
    BEFORE UPDATE ON document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_document_chunks_updated_at();

-- Add new columns to documents table for chunk tracking
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS chunk_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS processing_metadata JSONB DEFAULT '{}';

-- Create index on chunk_count for performance
CREATE INDEX IF NOT EXISTS idx_documents_chunk_count ON documents(chunk_count);

-- Add function to update document chunk count
CREATE OR REPLACE FUNCTION update_document_chunk_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE documents 
        SET chunk_count = (
            SELECT COUNT(*) FROM document_chunks 
            WHERE document_id = NEW.document_id
        )
        WHERE id = NEW.document_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE documents 
        SET chunk_count = (
            SELECT COUNT(*) FROM document_chunks 
            WHERE document_id = OLD.document_id
        )
        WHERE id = OLD.document_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to maintain chunk count
CREATE TRIGGER trigger_update_chunk_count_insert
    AFTER INSERT ON document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_document_chunk_count();

CREATE TRIGGER trigger_update_chunk_count_delete
    AFTER DELETE ON document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_document_chunk_count();

-- Add comments for documentation
COMMENT ON TABLE document_chunks IS 'Structured chunks from documents processed by Docling service';
COMMENT ON COLUMN document_chunks.chunk_type IS 'Type of content: text, table, image, code';
COMMENT ON COLUMN document_chunks.chunk_metadata IS 'Docling-specific metadata and processing information';
COMMENT ON COLUMN document_chunks.word_count IS 'Word count for chunk size analytics';
COMMENT ON COLUMN document_chunks.char_count IS 'Character count for token estimation';

COMMENT ON COLUMN documents.chunk_count IS 'Total number of chunks for this document';
COMMENT ON COLUMN documents.processing_metadata IS 'Docling processing metadata and statistics';

-- Insert migration record (if you want to track migrations)
DO $$
BEGIN
    -- Create migrations table if it doesn't exist
    CREATE TABLE IF NOT EXISTS migration_history (
        id SERIAL PRIMARY KEY,
        filename VARCHAR(255) UNIQUE NOT NULL,
        executed_at TIMESTAMP DEFAULT NOW()
    );
    
    -- Record this migration
    INSERT INTO migration_history (filename) 
    VALUES ('002_document_chunks.sql') 
    ON CONFLICT (filename) DO NOTHING;
END $$;