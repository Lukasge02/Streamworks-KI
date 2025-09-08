-- Migration: Create Chat System Tables for Streamworks
-- Description: Creates chat_sessions and chat_messages tables with proper relationships

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL,
    user_id text NOT NULL,
    company_id uuid DEFAULT '00000000-0000-0000-0000-000000000001'::uuid,
    message_count integer DEFAULT 0,
    rag_config jsonb DEFAULT '{}'::jsonb,
    context_filters jsonb DEFAULT '{}'::jsonb,
    is_active boolean DEFAULT true,
    is_archived boolean DEFAULT false,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    last_message_at timestamptz
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id uuid NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id text NOT NULL,
    role text NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content text NOT NULL,
    confidence_score numeric CHECK (confidence_score >= 0 AND confidence_score <= 1),
    processing_time_ms integer CHECK (processing_time_ms >= 0),
    sources jsonb DEFAULT '[]'::jsonb,
    model_used text,
    created_at timestamptz DEFAULT now(),
    sequence_number integer
);

-- Create sequence for message numbering per session
CREATE SEQUENCE IF NOT EXISTS chat_message_seq;

-- Function to auto-increment sequence_number per session
CREATE OR REPLACE FUNCTION set_message_sequence_number()
RETURNS TRIGGER AS $$
BEGIN
    -- Get next sequence number for this session
    SELECT COALESCE(MAX(sequence_number), 0) + 1
    INTO NEW.sequence_number
    FROM chat_messages
    WHERE session_id = NEW.session_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-set sequence numbers
DROP TRIGGER IF EXISTS trigger_set_message_sequence ON chat_messages;
CREATE TRIGGER trigger_set_message_sequence
    BEFORE INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION set_message_sequence_number();

-- Function to update chat_sessions.updated_at and message_count
CREATE OR REPLACE FUNCTION update_session_on_message()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Update session stats when new message is added
        UPDATE chat_sessions 
        SET 
            updated_at = now(),
            last_message_at = now(),
            message_count = message_count + 1
        WHERE id = NEW.session_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- Update session stats when message is deleted
        UPDATE chat_sessions 
        SET 
            updated_at = now(),
            message_count = GREATEST(message_count - 1, 0)
        WHERE id = OLD.session_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Triggers to maintain session statistics
DROP TRIGGER IF EXISTS trigger_update_session_on_message_insert ON chat_messages;
CREATE TRIGGER trigger_update_session_on_message_insert
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_session_on_message();

DROP TRIGGER IF EXISTS trigger_update_session_on_message_delete ON chat_messages;
CREATE TRIGGER trigger_update_session_on_message_delete
    AFTER DELETE ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_session_on_message();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for auto-updating updated_at on sessions
DROP TRIGGER IF EXISTS trigger_update_session_timestamp ON chat_sessions;
CREATE TRIGGER trigger_update_session_timestamp
    BEFORE UPDATE ON chat_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Performance Indices
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_active 
    ON chat_sessions(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at 
    ON chat_sessions(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_sequence 
    ON chat_messages(session_id, sequence_number);

CREATE INDEX IF NOT EXISTS idx_chat_messages_user_created 
    ON chat_messages(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_role 
    ON chat_messages(role);

-- Search index for message content (for full-text search)
CREATE INDEX IF NOT EXISTS idx_chat_messages_content_search 
    ON chat_messages USING gin(to_tsvector('english', content));

-- Stored function for user statistics
CREATE OR REPLACE FUNCTION get_user_chat_stats(p_user_id text)
RETURNS TABLE(
    total_sessions bigint,
    active_sessions bigint,
    total_messages bigint,
    last_session_date timestamptz
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_sessions,
        COUNT(*) FILTER (WHERE is_active = true) as active_sessions,
        COALESCE(SUM(message_count), 0) as total_messages,
        MAX(created_at) as last_session_date
    FROM chat_sessions 
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- RLS (Row Level Security) Setup
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own sessions
DROP POLICY IF EXISTS "Users can view own chat sessions" ON chat_sessions;
CREATE POLICY "Users can view own chat sessions" 
    ON chat_sessions FOR ALL 
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- RLS Policy: Users can only access their own messages  
DROP POLICY IF EXISTS "Users can view own chat messages" ON chat_messages;
CREATE POLICY "Users can view own chat messages" 
    ON chat_messages FOR ALL 
    USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- Service role bypass (for backend service key)
DROP POLICY IF EXISTS "Service role has full access to sessions" ON chat_sessions;
CREATE POLICY "Service role has full access to sessions" 
    ON chat_sessions FOR ALL 
    TO service_role 
    USING (true);

DROP POLICY IF EXISTS "Service role has full access to messages" ON chat_messages;  
CREATE POLICY "Service role has full access to messages" 
    ON chat_messages FOR ALL 
    TO service_role 
    USING (true);

-- Grant permissions to authenticated users
GRANT ALL ON chat_sessions TO authenticated;
GRANT ALL ON chat_messages TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Grant permissions to service role (for backend)
GRANT ALL ON chat_sessions TO service_role;
GRANT ALL ON chat_messages TO service_role;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- Comments for documentation
COMMENT ON TABLE chat_sessions IS 'Chat sessions for RAG-powered conversations';
COMMENT ON TABLE chat_messages IS 'Individual messages within chat sessions';
COMMENT ON FUNCTION get_user_chat_stats(text) IS 'Get comprehensive chat statistics for a user';

-- Verification queries (optional - for testing)
-- SELECT 'chat_sessions table created' as status WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chat_sessions');
-- SELECT 'chat_messages table created' as status WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'chat_messages');