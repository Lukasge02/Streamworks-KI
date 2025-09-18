-- RBAC Migration Step 1: Create Core Auth Tables Only
-- This creates the basic auth infrastructure without foreign keys to existing tables

-- ====================================================================
-- 1. COMPANIES TABLE - Multi-Tenant Support
-- ====================================================================

CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),

    -- Metadaten
    settings JSONB DEFAULT '{}'::jsonb,
    created_by_owner UUID,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT companies_domain_unique UNIQUE(domain)
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(domain);
CREATE INDEX IF NOT EXISTS idx_companies_created_by ON companies(created_by_owner);

-- ====================================================================
-- 2. USERS TABLE - Core User Management
-- ====================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'kunde',
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,

    -- Status und Metadaten
    is_active BOOLEAN DEFAULT true,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Constraints
    CONSTRAINT check_user_role CHECK (role IN ('owner', 'streamworks_admin', 'kunde')),
    CONSTRAINT check_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_company_id ON users(company_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- ====================================================================
-- 3. USER_SESSIONS TABLE - JWT Session Management
-- ====================================================================

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    jwt_token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Security Metadaten
    ip_address INET,
    user_agent TEXT,
    is_revoked BOOLEAN DEFAULT false
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sessions_token_hash ON user_sessions(jwt_token_hash);

-- ====================================================================
-- 4. FOREIGN KEY für companies.created_by_owner
-- ====================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_companies_created_by_owner'
    ) THEN
        ALTER TABLE companies
        ADD CONSTRAINT fk_companies_created_by_owner
        FOREIGN KEY (created_by_owner) REFERENCES users(id) ON DELETE SET NULL;
    END IF;
END $$;

-- ====================================================================
-- 5. INITIAL SEED DATA - System Setup
-- ====================================================================

-- Default Company für System Owner
INSERT INTO companies (id, name, domain, settings, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'Streamworks System',
    'streamworks.internal',
    '{"type": "system", "description": "Internal system company"}'::jsonb,
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- System Owner Account (password: owner123)
INSERT INTO users (
    id,
    email,
    password_hash,
    first_name,
    last_name,
    role,
    company_id,
    is_active,
    created_at
) VALUES (
    '00000000-0000-0000-0000-000000000001'::uuid,
    'owner@streamworks.dev',
    '$2b$12$LQv3c1yqBwRfx5Dz4x5K1.8N9j1Q2K0l3mJZk4Pz7Y8Xw6Vm5U3Sp', -- password: owner123
    'System',
    'Owner',
    'owner',
    '00000000-0000-0000-0000-000000000001'::uuid,
    true,
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Test Admin Account (password: admin123)
INSERT INTO users (
    email,
    password_hash,
    first_name,
    last_name,
    role,
    company_id,
    is_active,
    created_at
) VALUES (
    'admin@streamworks.dev',
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', -- password: admin123
    'Support',
    'Admin',
    'streamworks_admin',
    '00000000-0000-0000-0000-000000000001'::uuid,
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Test Customer Account (password: kunde123)
INSERT INTO users (
    email,
    password_hash,
    first_name,
    last_name,
    role,
    company_id,
    is_active,
    created_at
) VALUES (
    'kunde@test.dev',
    '$2b$12$CwTycUXWue0Thq9StjUM0uJ4uVlb.HIbPgHYeAv6n1HM8.7HO1lsm', -- password: kunde123
    'Test',
    'Kunde',
    'kunde',
    '00000000-0000-0000-0000-000000000001'::uuid,
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Update companies.created_by_owner
UPDATE companies
SET created_by_owner = '00000000-0000-0000-0000-000000000001'::uuid
WHERE id = '00000000-0000-0000-0000-000000000001'::uuid;

-- ====================================================================
-- 6. FUNCTIONS für Updated_at Timestamps
-- ====================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers für automatic updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ====================================================================
-- STEP 1 COMPLETE - Auth Tables Created
-- ====================================================================

SELECT
    'Step 1: Auth tables created successfully' as status,
    NOW() as completed_at,
    (SELECT COUNT(*) FROM users WHERE role = 'owner') as owner_count,
    (SELECT COUNT(*) FROM users WHERE role = 'streamworks_admin') as admin_count,
    (SELECT COUNT(*) FROM users WHERE role = 'kunde') as kunde_count,
    (SELECT COUNT(*) FROM companies) as company_count;