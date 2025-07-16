-- Enterprise Document Management System Migration
-- Version: 1.0.0
-- Date: 2025-01-15

-- 1. Document Categories (Top-Level)
CREATE TABLE IF NOT EXISTS document_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Document Folders (For Q&A Category)
CREATE TABLE IF NOT EXISTS document_folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES document_categories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    parent_folder_id UUID REFERENCES document_folders(id) ON DELETE CASCADE,
    color VARCHAR(7) DEFAULT '#6B7280',
    icon VARCHAR(50),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, parent_folder_id, slug)
);

-- 3. Enhanced Training Files Table
CREATE TABLE IF NOT EXISTS training_files_v2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES document_categories(id),
    folder_id UUID REFERENCES document_folders(id) ON DELETE SET NULL,
    original_filename VARCHAR(500) NOT NULL,
    display_name VARCHAR(500),
    storage_path VARCHAR(1000) NOT NULL UNIQUE,
    file_hash VARCHAR(64) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    mime_type VARCHAR(100),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    language VARCHAR(10) DEFAULT 'de',
    
    -- Processing Status
    processing_status VARCHAR(50) DEFAULT 'pending',
    processed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    
    -- Vector DB Integration
    chunk_count INTEGER DEFAULT 0,
    embedding_model VARCHAR(100),
    last_indexed_at TIMESTAMP WITH TIME ZONE,
    
    -- Enterprise Features
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    is_archived BOOLEAN DEFAULT false,
    access_level VARCHAR(50) DEFAULT 'public',
    
    -- Audit
    uploaded_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 4. Document Chunks Enhanced
CREATE TABLE IF NOT EXISTS document_chunks_v2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID NOT NULL REFERENCES training_files_v2(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    
    -- Vector DB Reference
    vector_id VARCHAR(100) UNIQUE,
    embedding_model VARCHAR(100),
    
    -- Metadata for Better Retrieval
    start_page INTEGER,
    end_page INTEGER,
    section_title VARCHAR(500),
    chunk_type VARCHAR(50) DEFAULT 'text',
    
    -- Search Optimization
    search_text TEXT,
    relevance_score FLOAT DEFAULT 1.0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_id, chunk_index)
);

-- 5. User Folder Permissions (Enterprise)
CREATE TABLE IF NOT EXISTS folder_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    folder_id UUID NOT NULL REFERENCES document_folders(id) ON DELETE CASCADE,
    user_id UUID,
    role VARCHAR(50) NOT NULL,
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(folder_id, user_id)
);

-- 6. Document Access Logs (Audit)
CREATE TABLE IF NOT EXISTS document_access_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_id UUID REFERENCES training_files_v2(id) ON DELETE SET NULL,
    user_id UUID,
    action VARCHAR(50) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Performance
CREATE INDEX idx_training_files_category ON training_files_v2(category_id);
CREATE INDEX idx_training_files_folder ON training_files_v2(folder_id);
CREATE INDEX idx_training_files_hash ON training_files_v2(file_hash);
CREATE INDEX idx_training_files_status ON training_files_v2(processing_status);
CREATE INDEX idx_training_files_created ON training_files_v2(created_at DESC);

CREATE INDEX idx_document_folders_category ON document_folders(category_id);
CREATE INDEX idx_document_folders_parent ON document_folders(parent_folder_id);

CREATE INDEX idx_chunks_file ON document_chunks_v2(file_id);
CREATE INDEX idx_chunks_vector ON document_chunks_v2(vector_id);

-- Full Text Search
CREATE INDEX idx_chunks_search ON document_chunks_v2 USING gin(to_tsvector('german', search_text));

-- Default Categories
INSERT INTO document_categories (name, slug, description, icon, sort_order) VALUES
('Q&A', 'qa', 'Knowledge Base Dokumente für Frage-Antwort System', 'MessageSquare', 1),
('Stream XML', 'stream-xml', 'XML Templates und Beispiele für Streamworks', 'Code', 2),
('Streamworks API', 'streamworks-api', 'API Dokumentation und Spezifikationen', 'Plug', 3)
ON CONFLICT (slug) DO NOTHING;

-- Default Q&A Folders
INSERT INTO document_folders (category_id, name, slug, description, color, icon, sort_order)
SELECT 
    id,
    folder.name,
    folder.slug,
    folder.description,
    folder.color,
    folder.icon,
    folder.sort_order
FROM document_categories
CROSS JOIN (VALUES
    ('Streamworks F1 Hilfe', 'streamworks-f1', 'Hilfe und Anleitungen für Streamworks F1', '#3B82F6', 'HelpCircle', 1),
    ('SharePoint', 'sharepoint', 'SharePoint Dokumentation und Guides', '#10B981', 'Database', 2),
    ('Confluence', 'confluence', 'Confluence Knowledge Base', '#8B5CF6', 'BookOpen', 3)
) AS folder(name, slug, description, color, icon, sort_order)
WHERE document_categories.slug = 'qa'
ON CONFLICT (category_id, parent_folder_id, slug) DO NOTHING;

-- Migration View for Backward Compatibility
CREATE OR REPLACE VIEW training_files AS
SELECT 
    id,
    original_filename as filename,
    file_hash,
    file_type,
    file_size,
    uploaded_by as user_id,
    created_at as upload_date,
    processing_status as status,
    chunk_count
FROM training_files_v2
WHERE is_active = true AND deleted_at IS NULL;