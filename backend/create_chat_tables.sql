-- Minimal Chat Tables für Supabase (via PostgreSQL)
-- Dieses Script kann direkt über das Supabase Dashboard ausgeführt werden

-- 1. Chat Sessions Tabelle
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

-- 2. Chat Messages Tabelle  
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

-- 3. Performance Indices
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_active 
    ON chat_sessions(user_id, is_active);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at 
    ON chat_sessions(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_sequence 
    ON chat_messages(session_id, sequence_number);

CREATE INDEX IF NOT EXISTS idx_chat_messages_user_created 
    ON chat_messages(user_id, created_at DESC);

-- 4. Auto-Sequence Function für Messages
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

-- 5. Trigger für Auto-Sequence
DROP TRIGGER IF EXISTS trigger_set_message_sequence ON chat_messages;
CREATE TRIGGER trigger_set_message_sequence
    BEFORE INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION set_message_sequence_number();

-- 6. Session Update Function
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

-- 7. Triggers für Session Updates
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

-- 8. User Stats Function
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

-- 9. Disable RLS für jetzt (für einfacheres Testing)
ALTER TABLE chat_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages DISABLE ROW LEVEL SECURITY;

-- 10. Test-Insert (optional)
-- INSERT INTO chat_sessions (title, user_id) VALUES ('Test Session', 'test-user');

-- Verification Query
SELECT 
    'chat_sessions' as table_name, 
    COUNT(*) as row_count 
FROM chat_sessions
UNION ALL
SELECT 
    'chat_messages' as table_name, 
    COUNT(*) as row_count 
FROM chat_messages;