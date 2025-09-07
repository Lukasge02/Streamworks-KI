-- ================================
-- Chat System Migration
-- Creates chat_sessions and chat_messages tables with RBAC
-- ================================

-- ================================
-- CHAT SESSIONS TABLE
-- ================================

CREATE TABLE public.chat_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    
    -- User & Company Context  
    user_id UUID REFERENCES public.user_profiles(id) NOT NULL,
    company_id UUID REFERENCES public.companies(id) DEFAULT '00000000-0000-0000-0000-000000000001',
    
    -- Session Metadata
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP WITH TIME ZONE,
    
    -- Session Configuration
    rag_config JSONB DEFAULT '{}',
    context_filters JSONB DEFAULT '{}',
    
    -- Status & Lifecycle
    is_active BOOLEAN DEFAULT true,
    is_archived BOOLEAN DEFAULT false,
    
    -- Audit Trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for performance
    CONSTRAINT chat_sessions_user_company_idx UNIQUE (user_id, company_id, id)
);

-- ================================
-- CHAT MESSAGES TABLE  
-- ================================

CREATE TABLE public.chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID REFERENCES public.chat_sessions(id) ON DELETE CASCADE NOT NULL,
    
    -- Message Content
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    
    -- RAG Response Metadata
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    processing_time_ms INTEGER,
    sources JSONB DEFAULT '[]',
    model_used VARCHAR(100),
    
    -- Message Context
    sequence_number INTEGER NOT NULL,
    parent_message_id UUID REFERENCES public.chat_messages(id),
    
    -- Performance Metadata
    token_count INTEGER,
    cost_estimate DECIMAL(10,6), -- Cost in USD
    
    -- Audit Trail
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES public.user_profiles(id) NOT NULL,
    
    -- Composite unique constraint for sequence
    CONSTRAINT chat_messages_session_sequence_unique UNIQUE (session_id, sequence_number)
);

-- ================================
-- PERFORMANCE INDEXES
-- ================================

-- Chat Sessions Indexes
CREATE INDEX idx_chat_sessions_user_id ON public.chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_company_id ON public.chat_sessions(company_id);
CREATE INDEX idx_chat_sessions_created_at ON public.chat_sessions(created_at DESC);
CREATE INDEX idx_chat_sessions_active ON public.chat_sessions(is_active) WHERE is_active = true;
CREATE INDEX idx_chat_sessions_last_message ON public.chat_sessions(last_message_at DESC) WHERE is_active = true;

-- Chat Messages Indexes
CREATE INDEX idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON public.chat_messages(created_at DESC);
CREATE INDEX idx_chat_messages_role ON public.chat_messages(role);
CREATE INDEX idx_chat_messages_sequence ON public.chat_messages(session_id, sequence_number);

-- ================================
-- RLS POLICIES
-- ================================

-- Enable RLS
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

-- Chat Sessions Policies
CREATE POLICY "Users can view their own chat sessions"
    ON public.chat_sessions FOR SELECT
    USING (
        user_id = auth.uid()
        OR 
        company_id IN (
            SELECT company_id FROM public.user_profiles 
            WHERE id = auth.uid() AND role IN ('admin', 'manager')
        )
    );

CREATE POLICY "Users can create their own chat sessions"
    ON public.chat_sessions FOR INSERT
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own chat sessions"
    ON public.chat_sessions FOR UPDATE
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can delete their own chat sessions"
    ON public.chat_sessions FOR DELETE
    USING (user_id = auth.uid());

-- Chat Messages Policies
CREATE POLICY "Users can view messages from their accessible sessions"
    ON public.chat_messages FOR SELECT
    USING (
        session_id IN (
            SELECT id FROM public.chat_sessions 
            WHERE user_id = auth.uid()
                OR company_id IN (
                    SELECT company_id FROM public.user_profiles 
                    WHERE id = auth.uid() AND role IN ('admin', 'manager')
                )
        )
    );

CREATE POLICY "Users can create messages in their sessions"
    ON public.chat_messages FOR INSERT
    WITH CHECK (
        user_id = auth.uid()
        AND session_id IN (
            SELECT id FROM public.chat_sessions 
            WHERE user_id = auth.uid()
        )
    );

-- ================================
-- TRIGGERS FOR AUTO-UPDATE
-- ================================

-- Update session's updated_at and message_count when messages are added
CREATE OR REPLACE FUNCTION update_chat_session_on_message()
RETURNS TRIGGER AS $$
BEGIN
    -- Update session metadata
    UPDATE public.chat_sessions 
    SET 
        updated_at = NOW(),
        last_message_at = NOW(),
        message_count = (
            SELECT COUNT(*) FROM public.chat_messages 
            WHERE session_id = NEW.session_id
        )
    WHERE id = NEW.session_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_session_on_message
    AFTER INSERT ON public.chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_chat_session_on_message();

-- Auto-increment sequence_number for messages
CREATE OR REPLACE FUNCTION set_message_sequence_number()
RETURNS TRIGGER AS $$
BEGIN
    -- Set sequence number if not provided
    IF NEW.sequence_number IS NULL THEN
        NEW.sequence_number = COALESCE(
            (SELECT MAX(sequence_number) + 1 FROM public.chat_messages WHERE session_id = NEW.session_id),
            1
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_message_sequence
    BEFORE INSERT ON public.chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION set_message_sequence_number();

-- ================================
-- SAMPLE DATA FOR TESTING
-- ================================

-- Insert a test chat session (will be created by first user)
-- This will be handled by the application when first user logs in

-- ================================
-- CLEANUP FUNCTIONS
-- ================================

-- Function to archive old sessions
CREATE OR REPLACE FUNCTION archive_old_chat_sessions()
RETURNS INTEGER AS $$
DECLARE
    archived_count INTEGER;
BEGIN
    UPDATE public.chat_sessions 
    SET is_archived = true 
    WHERE 
        is_active = true 
        AND last_message_at < NOW() - INTERVAL '30 days'
        AND message_count = 0;
    
    GET DIAGNOSTICS archived_count = ROW_COUNT;
    
    RETURN archived_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get chat statistics
CREATE OR REPLACE FUNCTION get_user_chat_stats(p_user_id UUID)
RETURNS JSONB AS $$
BEGIN
    RETURN jsonb_build_object(
        'total_sessions', (
            SELECT COUNT(*) FROM public.chat_sessions 
            WHERE user_id = p_user_id
        ),
        'active_sessions', (
            SELECT COUNT(*) FROM public.chat_sessions 
            WHERE user_id = p_user_id AND is_active = true
        ),
        'total_messages', (
            SELECT COUNT(*) FROM public.chat_messages 
            WHERE user_id = p_user_id
        ),
        'last_session_date', (
            SELECT MAX(created_at) FROM public.chat_sessions 
            WHERE user_id = p_user_id
        )
    );
END;
$$ LANGUAGE plpgsql;

-- ================================
-- GRANTS
-- ================================

-- Grant access to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON public.chat_sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.chat_messages TO authenticated;

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ================================
-- COMMENTS
-- ================================

COMMENT ON TABLE public.chat_sessions IS 'Chat sessions for RAG-based conversations with RBAC support';
COMMENT ON TABLE public.chat_messages IS 'Individual messages within chat sessions with RAG metadata';

COMMENT ON COLUMN public.chat_sessions.rag_config IS 'RAG configuration overrides for this session (JSON)';
COMMENT ON COLUMN public.chat_sessions.context_filters IS 'Document filters applied to this session (JSON)';

COMMENT ON COLUMN public.chat_messages.confidence_score IS 'RAG response confidence from 0.00 to 1.00';
COMMENT ON COLUMN public.chat_messages.processing_time_ms IS 'Time taken to process the RAG query in milliseconds';
COMMENT ON COLUMN public.chat_messages.sources IS 'Array of source documents used for RAG response (JSON)';
COMMENT ON COLUMN public.chat_messages.sequence_number IS 'Message order within the session';