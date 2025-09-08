# Manual Migration Guide für Supabase Chat-Tabellen

Da die automatische Migration fehlgeschlagen ist (Invalid API Key), müssen die Tabellen manuell über das Supabase Dashboard erstellt werden.

## Vorgehensweise:

### 1. Supabase Dashboard öffnen
1. Gehe zu https://supabase.com/dashboard
2. Öffne dein Projekt
3. Gehe zu "SQL Editor"

### 2. SQL-Script ausführen
Kopiere den gesamten Inhalt aus `migrations/001_create_chat_tables.sql` und führe ihn im SQL Editor aus.

### 3. Alternative: Tabellen einzeln erstellen

**Tabelle: chat_sessions**
```sql
CREATE TABLE chat_sessions (
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
```

**Tabelle: chat_messages**
```sql
CREATE TABLE chat_messages (
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
```

**Wichtige Indices:**
```sql
CREATE INDEX idx_chat_sessions_user_active ON chat_sessions(user_id, is_active);
CREATE INDEX idx_chat_messages_session_sequence ON chat_messages(session_id, sequence_number);
```

### 4. RLS deaktivieren (für Testzwecke)
```sql
ALTER TABLE chat_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages DISABLE ROW LEVEL SECURITY;
```

### 5. Backend testen
Nach der manuellen Erstellung können wir das Backend starten und testen.