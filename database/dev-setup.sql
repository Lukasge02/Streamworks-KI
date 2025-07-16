-- StreamWorks-KI Development Database Setup
-- Zusätzliche Entwicklungstools und Test-Daten

-- Aktiviere alle PostgreSQL Extensions für Development
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Erstelle Development-spezifische Schemas
CREATE SCHEMA IF NOT EXISTS dev_tools;
CREATE SCHEMA IF NOT EXISTS test_data;

-- Logging-Funktion für Development
CREATE OR REPLACE FUNCTION dev_tools.log_query(query_text TEXT, execution_time INTERVAL DEFAULT NULL)
RETURNS void AS $$
BEGIN
    INSERT INTO dev_tools.query_log (query_text, execution_time, logged_at)
    VALUES (query_text, execution_time, NOW());
END;
$$ LANGUAGE plpgsql;

-- Query Log Tabelle
CREATE TABLE IF NOT EXISTS dev_tools.query_log (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    execution_time INTERVAL,
    logged_at TIMESTAMP DEFAULT NOW()
);

-- Performance Monitoring View
CREATE OR REPLACE VIEW dev_tools.slow_queries AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time,
    stddev_time
FROM pg_stat_statements
WHERE mean_time > 100  -- Queries slower than 100ms
ORDER BY mean_time DESC;

-- Test-Daten für Development
INSERT INTO test_data.sample_documents (title, content, category) VALUES
('Test Document 1', 'Dies ist ein Test-Dokument für die Entwicklung', 'help_data'),
('Test Document 2', 'Weitere Test-Inhalte für StreamWorks-KI', 'stream_templates')
ON CONFLICT DO NOTHING;

-- Erstelle Test-Daten Tabelle falls nicht existiert
CREATE TABLE IF NOT EXISTS test_data.sample_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Development-spezifische Indexes für bessere Performance
CREATE INDEX IF NOT EXISTS idx_dev_query_log_logged_at ON dev_tools.query_log(logged_at);
CREATE INDEX IF NOT EXISTS idx_dev_sample_docs_category ON test_data.sample_documents(category);

-- Setze Development-optimierte Konfiguration
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;
ALTER SYSTEM SET log_min_duration_statement = 0;

-- Erstelle Development-User mit erweiterten Rechten
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'streamworks_dev') THEN
        CREATE ROLE streamworks_dev LOGIN PASSWORD 'dev_password_2025';
        GRANT CONNECT ON DATABASE streamworks_ki_dev TO streamworks_dev;
        GRANT USAGE ON SCHEMA public, dev_tools, test_data TO streamworks_dev;
        GRANT CREATE ON SCHEMA public TO streamworks_dev;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public, dev_tools, test_data TO streamworks_dev;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public, dev_tools, test_data TO streamworks_dev;
    END IF;
END
$$;

-- Kommentare für bessere Dokumentation
COMMENT ON SCHEMA dev_tools IS 'Development-Tools und Debugging-Funktionen';
COMMENT ON SCHEMA test_data IS 'Test-Daten für Development und Testing';
COMMENT ON TABLE dev_tools.query_log IS 'Log aller Queries für Performance-Analyse';
COMMENT ON VIEW dev_tools.slow_queries IS 'Übersicht über langsame Queries (>100ms)';

-- Bestätige Setup
SELECT 'Development database setup completed successfully!' AS status;