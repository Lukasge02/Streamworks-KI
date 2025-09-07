-- ================================
-- Documents System Migration  
-- Extends existing documents with RBAC support
-- ================================

-- ================================
-- ENHANCED DOCUMENTS TABLE
-- ================================

CREATE TABLE public.documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    filename VARCHAR NOT NULL,
    original_filename VARCHAR NOT NULL,
    title VARCHAR,
    description TEXT,
    file_path VARCHAR NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR NOT NULL,
    checksum VARCHAR NOT NULL,
    
    -- Categorization
    doctype document_type NOT NULL DEFAULT 'general',
    category document_category NOT NULL DEFAULT 'general', 
    folder_id UUID REFERENCES public.folders(id),
    tags TEXT[] DEFAULT '{}',
    
    -- Processing Status
    status document_status NOT NULL DEFAULT 'uploaded',
    processing_progress INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    vector_count INTEGER DEFAULT 0,
    
    -- Metadata
    language VARCHAR DEFAULT 'de',
    auto_generated_summary TEXT,
    keywords TEXT[] DEFAULT '{}',
    custom_metadata JSONB DEFAULT '{}',
    ai_summary JSONB DEFAULT '{}',
    
    -- Access Control
    visibility document_visibility DEFAULT 'private',
    owner_id UUID REFERENCES public.user_profiles(id) NOT NULL,
    company_id UUID REFERENCES public.companies(id) DEFAULT '00000000-0000-0000-0000-000000000001',
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.user_profiles(id),
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    
    -- Versioning
    version_number INTEGER DEFAULT 1,
    parent_document_id UUID REFERENCES public.documents(id),
    is_latest_version BOOLEAN DEFAULT true
);

-- ================================
-- CHAT SYSTEM TABLES
-- ================================

CREATE TABLE public.chat_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR NOT NULL,
    user_id UUID REFERENCES public.user_profiles(id) NOT NULL,
    company_id UUID REFERENCES public.companies(id),
    
    -- Session Config
    model_config JSONB DEFAULT '{}',
    system_prompt TEXT,
    context_documents UUID[] DEFAULT '{}',
    
    -- Status & Metadata
    status chat_status DEFAULT 'active',
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,4) DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE public.chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.user_profiles(id),
    
    -- Message Content
    content TEXT NOT NULL,
    message_type message_type NOT NULL,
    metadata JSONB DEFAULT '{}',
    
    -- AI Response Data
    sources JSONB DEFAULT '[]', -- Referenced documents
    confidence_score REAL,
    processing_time_ms INTEGER,
    tokens_used INTEGER,
    model_used VARCHAR,
    
    -- Audit & Compliance
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- ================================
-- AUDIT & COMPLIANCE SYSTEM
-- ================================

CREATE TABLE public.audit_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Who & When
    user_id UUID REFERENCES public.user_profiles(id),
    session_id VARCHAR, -- Web session ID
    
    -- What & Where
    action audit_action NOT NULL,
    resource_type resource_type NOT NULL,
    resource_id VARCHAR NOT NULL,
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    referer TEXT,
    request_id VARCHAR,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    severity audit_severity DEFAULT 'info',
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE public.security_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id),
    event_type security_event_type NOT NULL,
    severity audit_severity NOT NULL,
    description TEXT NOT NULL,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    resolved BOOLEAN DEFAULT false,
    resolved_by UUID REFERENCES public.user_profiles(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- DOCUMENT PROCESSING JOBS
-- ================================

CREATE TABLE public.document_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    job_type VARCHAR NOT NULL, -- 'chunk', 'vectorize', 'summarize'
    status VARCHAR NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    progress INTEGER DEFAULT 0, -- 0-100
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- DOCUMENT SHARING & COLLABORATION
-- ================================

CREATE TABLE public.document_shares (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    shared_by UUID REFERENCES public.user_profiles(id) NOT NULL,
    shared_with UUID REFERENCES public.user_profiles(id),
    shared_with_email VARCHAR, -- For external sharing
    permission_level permission_level NOT NULL DEFAULT 'read',
    expires_at TIMESTAMP WITH TIME ZONE,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ================================
-- DOCUMENT VERSIONS & HISTORY
-- ================================

CREATE TABLE public.document_versions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    checksum VARCHAR NOT NULL,
    changes_description TEXT,
    created_by UUID REFERENCES public.user_profiles(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_id, version_number)
);

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

-- Documents indexes
CREATE INDEX idx_documents_owner ON public.documents(owner_id);
CREATE INDEX idx_documents_company ON public.documents(company_id);
CREATE INDEX idx_documents_folder ON public.documents(folder_id);
CREATE INDEX idx_documents_category ON public.documents(category);
CREATE INDEX idx_documents_visibility ON public.documents(visibility);
CREATE INDEX idx_documents_status ON public.documents(status);
CREATE INDEX idx_documents_created_at ON public.documents(created_at);
CREATE INDEX idx_documents_filename_search ON public.documents USING gin(to_tsvector('german', original_filename || ' ' || COALESCE(title, '') || ' ' || COALESCE(description, '')));

-- Chat indexes
CREATE INDEX idx_chat_sessions_user ON public.chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_company ON public.chat_sessions(company_id);
CREATE INDEX idx_chat_sessions_created_at ON public.chat_sessions(created_at);
CREATE INDEX idx_chat_messages_session ON public.chat_messages(session_id);
CREATE INDEX idx_chat_messages_user ON public.chat_messages(user_id);
CREATE INDEX idx_chat_messages_created_at ON public.chat_messages(created_at);

-- Audit indexes
CREATE INDEX idx_audit_logs_user ON public.audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON public.audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON public.audit_logs(created_at);
CREATE INDEX idx_audit_logs_severity ON public.audit_logs(severity);

CREATE INDEX idx_security_events_user ON public.security_events(user_id);
CREATE INDEX idx_security_events_type ON public.security_events(event_type);
CREATE INDEX idx_security_events_resolved ON public.security_events(resolved);
CREATE INDEX idx_security_events_created_at ON public.security_events(created_at);

-- Document processing indexes
CREATE INDEX idx_document_jobs_document ON public.document_jobs(document_id);
CREATE INDEX idx_document_jobs_status ON public.document_jobs(status);
CREATE INDEX idx_document_jobs_type ON public.document_jobs(job_type);

-- Document sharing indexes
CREATE INDEX idx_document_shares_document ON public.document_shares(document_id);
CREATE INDEX idx_document_shares_shared_with ON public.document_shares(shared_with);
CREATE INDEX idx_document_shares_email ON public.document_shares(shared_with_email);

-- ================================
-- TRIGGERS
-- ================================

-- Update documents updated_at
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON public.documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update chat sessions updated_at  
CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON public.chat_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update folder stats when documents change
CREATE TRIGGER update_folder_stats_on_document_insert 
    AFTER INSERT ON public.documents 
    FOR EACH ROW EXECUTE FUNCTION update_folder_stats();

CREATE TRIGGER update_folder_stats_on_document_update
    AFTER UPDATE ON public.documents
    FOR EACH ROW EXECUTE FUNCTION update_folder_stats();

CREATE TRIGGER update_folder_stats_on_document_delete
    AFTER DELETE ON public.documents
    FOR EACH ROW EXECUTE FUNCTION update_folder_stats();

-- Update chat session stats
CREATE OR REPLACE FUNCTION update_chat_session_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update message count and last_message_at
    UPDATE public.chat_sessions SET
        message_count = (SELECT COUNT(*) FROM public.chat_messages WHERE session_id = NEW.session_id),
        last_message_at = NEW.created_at,
        updated_at = NOW()
    WHERE id = NEW.session_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_chat_session_stats_trigger
    AFTER INSERT ON public.chat_messages
    FOR EACH ROW EXECUTE FUNCTION update_chat_session_stats();

-- Create document version on file update
CREATE OR REPLACE FUNCTION create_document_version()
RETURNS TRIGGER AS $$
BEGIN
    -- Only create version if file actually changed
    IF OLD.file_path != NEW.file_path OR OLD.checksum != NEW.checksum THEN
        INSERT INTO public.document_versions (
            document_id,
            version_number,
            file_path,
            file_size_bytes,
            checksum,
            created_by
        ) VALUES (
            NEW.id,
            NEW.version_number,
            NEW.file_path,
            NEW.file_size_bytes,
            NEW.checksum,
            NEW.created_by
        );
        
        -- Increment version number
        NEW.version_number = NEW.version_number + 1;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER create_document_version_trigger
    BEFORE UPDATE ON public.documents
    FOR EACH ROW EXECUTE FUNCTION create_document_version();

-- ================================
-- FULL TEXT SEARCH SETUP
-- ================================

-- Create full text search index for documents
CREATE INDEX idx_documents_fulltext_search ON public.documents 
USING gin(to_tsvector('german', 
    original_filename || ' ' || 
    COALESCE(title, '') || ' ' || 
    COALESCE(description, '') || ' ' ||
    COALESCE(auto_generated_summary, '') || ' ' ||
    array_to_string(keywords, ' ')
));

-- Create search function
CREATE OR REPLACE FUNCTION search_documents(
    search_query TEXT,
    user_id UUID,
    category_filter document_category DEFAULT NULL,
    limit_count INTEGER DEFAULT 50
)
RETURNS TABLE (
    id UUID,
    original_filename VARCHAR,
    title VARCHAR,
    description TEXT,
    category document_category,
    visibility document_visibility,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.original_filename,
        d.title,
        d.description,
        d.category,
        d.visibility,
        ts_rank(to_tsvector('german', 
            d.original_filename || ' ' || 
            COALESCE(d.title, '') || ' ' || 
            COALESCE(d.description, '') || ' ' ||
            COALESCE(d.auto_generated_summary, '') || ' ' ||
            array_to_string(d.keywords, ' ')
        ), plainto_tsquery('german', search_query)) as rank
    FROM public.documents d
    WHERE 
        to_tsvector('german', 
            d.original_filename || ' ' || 
            COALESCE(d.title, '') || ' ' || 
            COALESCE(d.description, '') || ' ' ||
            COALESCE(d.auto_generated_summary, '') || ' ' ||
            array_to_string(d.keywords, ' ')
        ) @@ plainto_tsquery('german', search_query)
        AND (category_filter IS NULL OR d.category = category_filter)
        AND d.status = 'processed'
        -- Basic access control (RLS will handle detailed permissions)
        AND (
            d.visibility = 'public' OR
            d.owner_id = user_id OR
            EXISTS (
                SELECT 1 FROM public.permissions p 
                WHERE p.user_id = search_documents.user_id 
                AND p.resource_type = 'document'
                AND p.resource_id = d.id::text
                AND p.permission_level IN ('read', 'write', 'admin', 'owner')
            )
        )
    ORDER BY rank DESC, d.created_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================
-- VIEWS FOR COMMON QUERIES
-- ================================

-- Active documents view
CREATE VIEW public.active_documents AS
SELECT 
    d.*,
    up.full_name as owner_name,
    c.name as company_name,
    f.name as folder_name
FROM public.documents d
LEFT JOIN public.user_profiles up ON d.owner_id = up.id
LEFT JOIN public.companies c ON d.company_id = c.id  
LEFT JOIN public.folders f ON d.folder_id = f.id
WHERE d.status IN ('uploaded', 'processing', 'processed');

-- Recent activity view
CREATE VIEW public.recent_activity AS
SELECT 
    al.id,
    al.action,
    al.resource_type,
    al.resource_id,
    al.created_at,
    al.ip_address,
    up.full_name as user_name,
    up.email as user_email,
    al.metadata
FROM public.audit_logs al
LEFT JOIN public.user_profiles up ON al.user_id = up.id
ORDER BY al.created_at DESC;

-- Document access statistics
CREATE VIEW public.document_stats AS
SELECT 
    d.id,
    d.original_filename,
    d.access_count,
    d.last_accessed_at,
    COUNT(DISTINCT ds.shared_with) as share_count,
    COUNT(DISTINCT al.user_id) as unique_viewers
FROM public.documents d
LEFT JOIN public.document_shares ds ON d.id = ds.document_id
LEFT JOIN public.audit_logs al ON d.id::text = al.resource_id 
    AND al.resource_type = 'document' 
    AND al.action = 'read'
GROUP BY d.id, d.original_filename, d.access_count, d.last_accessed_at;

-- ================================
-- COMMENTS FOR DOCUMENTATION
-- ================================

COMMENT ON TABLE public.documents IS 'Enhanced documents table with RBAC, versioning, and full-text search';
COMMENT ON TABLE public.chat_sessions IS 'Chat sessions with user association and metadata';
COMMENT ON TABLE public.chat_messages IS 'Individual chat messages with AI response data';
COMMENT ON TABLE public.audit_logs IS 'Comprehensive audit trail for all system actions';
COMMENT ON TABLE public.security_events IS 'Security-related events requiring attention';
COMMENT ON TABLE public.document_jobs IS 'Background processing jobs for documents';
COMMENT ON TABLE public.document_shares IS 'Document sharing with users or external emails';
COMMENT ON TABLE public.document_versions IS 'Version history for documents';

COMMENT ON FUNCTION search_documents IS 'Full-text search with RBAC-aware filtering';
COMMENT ON VIEW public.active_documents IS 'Documents that are actively available (not deleted/archived)';
COMMENT ON VIEW public.recent_activity IS 'Recent user activity across the system';
COMMENT ON VIEW public.document_stats IS 'Usage statistics for documents';