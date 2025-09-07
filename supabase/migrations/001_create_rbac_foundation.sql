-- ================================
-- RBAC Foundation Migration
-- Creates core RBAC system with users, companies, permissions
-- ================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================
-- ENUMS
-- ================================

-- User Roles
CREATE TYPE user_role AS ENUM (
    'owner',
    'streamworks_admin', 
    'streamworks_colleague',
    'customer'
);

-- User Status
CREATE TYPE user_status AS ENUM (
    'active',
    'inactive',
    'suspended',
    'pending_activation'
);

-- Resource Types for permissions
CREATE TYPE resource_type AS ENUM (
    'document',
    'folder', 
    'chat_session',
    'company',
    'system'
);

-- Permission Levels
CREATE TYPE permission_level AS ENUM (
    'read',
    'write', 
    'delete',
    'admin',
    'owner'
);

-- Document Types
CREATE TYPE document_type AS ENUM (
    'manual',
    'faq',
    'policy',
    'contract',
    'report',
    'presentation',
    'spreadsheet',
    'general'
);

-- Document Categories  
CREATE TYPE document_category AS ENUM (
    'faq',
    'xml',
    'internal',
    'customer',
    'public',
    'confidential',
    'general'
);

-- Document Status
CREATE TYPE document_status AS ENUM (
    'uploaded',
    'processing', 
    'processed',
    'failed',
    'archived',
    'deleted'
);

-- Document Visibility
CREATE TYPE document_visibility AS ENUM (
    'public',      -- Für alle sichtbar
    'internal',    -- Nur für StreamWorks Mitarbeiter  
    'company',     -- Nur für Firma des Owners
    'private',     -- Nur für Owner + explizite Permissions
    'confidential' -- Restricted access, extra logging
);

-- Chat Status
CREATE TYPE chat_status AS ENUM (
    'active',
    'archived', 
    'deleted'
);

-- Message Types
CREATE TYPE message_type AS ENUM (
    'user',
    'assistant',
    'system'
);

-- Audit Actions
CREATE TYPE audit_action AS ENUM (
    'login',
    'logout', 
    'create',
    'read',
    'update',
    'delete',
    'download',
    'upload',
    'share',
    'permission_grant',
    'permission_revoke',
    'export',
    'import',
    'system_config'
);

-- Audit Severity
CREATE TYPE audit_severity AS ENUM (
    'info',
    'warning',
    'error',
    'critical'
);

-- Security Event Types
CREATE TYPE security_event_type AS ENUM (
    'failed_login',
    'suspicious_activity',
    'unauthorized_access',
    'permission_escalation',
    'data_breach',
    'unusual_download',
    'rate_limit_exceeded'
);

-- ================================
-- COMPANIES & ORGANIZATIONS
-- ================================

CREATE TABLE public.companies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR NOT NULL,
    slug VARCHAR NOT NULL UNIQUE,
    domain VARCHAR,
    logo_url TEXT,
    address JSONB,
    contact_info JSONB,
    subscription_tier VARCHAR DEFAULT 'basic',
    max_users INTEGER DEFAULT 10,
    max_documents INTEGER DEFAULT 100,
    storage_limit_gb INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create StreamWorks company as default
INSERT INTO public.companies (id, name, slug, domain, subscription_tier, max_users, max_documents, storage_limit_gb) 
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'StreamWorks GmbH',
    'streamworks',
    'streamworks.de',
    'enterprise',
    1000,
    10000,
    1000
);

-- ================================
-- USER PROFILES & AUTHENTICATION
-- ================================

CREATE TABLE public.user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email VARCHAR NOT NULL UNIQUE,
    full_name VARCHAR NOT NULL,
    role user_role NOT NULL DEFAULT 'customer',
    company_id UUID REFERENCES public.companies(id) DEFAULT '00000000-0000-0000-0000-000000000001',
    department VARCHAR,
    position VARCHAR,
    avatar_url TEXT,
    phone VARCHAR,
    timezone VARCHAR DEFAULT 'Europe/Berlin',
    language VARCHAR DEFAULT 'de',
    preferences JSONB DEFAULT '{}',
    status user_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE
);

-- ================================
-- PERMISSIONS SYSTEM
-- ================================

-- Granular Permissions Table
CREATE TABLE public.permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.user_profiles(id) ON DELETE CASCADE,
    resource_type resource_type NOT NULL,
    resource_id VARCHAR NOT NULL,
    permission_level permission_level NOT NULL,
    granted_by UUID REFERENCES public.user_profiles(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    UNIQUE(user_id, resource_type, resource_id, permission_level)
);

-- Role-based Default Permissions
CREATE TABLE public.role_permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    role user_role NOT NULL,
    resource_type resource_type NOT NULL,
    permission_level permission_level NOT NULL,
    is_default BOOLEAN DEFAULT true,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(role, resource_type, permission_level)
);

-- Insert default role permissions
INSERT INTO public.role_permissions (role, resource_type, permission_level, description) VALUES
-- Owner permissions (everything)
('owner', 'system', 'owner', 'Full system access'),
('owner', 'document', 'owner', 'All document access'),
('owner', 'folder', 'owner', 'All folder access'),
('owner', 'chat_session', 'owner', 'All chat access'),
('owner', 'company', 'owner', 'Company management'),

-- StreamWorks Admin permissions
('streamworks_admin', 'system', 'admin', 'System administration'),
('streamworks_admin', 'document', 'admin', 'Document administration'),
('streamworks_admin', 'folder', 'admin', 'Folder administration'), 
('streamworks_admin', 'chat_session', 'read', 'View chat sessions'),
('streamworks_admin', 'company', 'admin', 'Company administration'),

-- StreamWorks Colleague permissions
('streamworks_colleague', 'document', 'write', 'Create/edit internal documents'),
('streamworks_colleague', 'folder', 'write', 'Manage own folders'),
('streamworks_colleague', 'chat_session', 'write', 'Full chat access'),

-- Customer permissions (very limited)
('customer', 'document', 'read', 'Read assigned documents only'),
('customer', 'chat_session', 'write', 'Limited chat access');

-- ================================
-- FOLDERS/COLLECTIONS
-- ================================

CREATE TABLE public.folders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR NOT NULL,
    slug VARCHAR NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES public.folders(id),
    path VARCHAR NOT NULL, -- Materialized path for fast queries
    level INTEGER NOT NULL DEFAULT 0,
    
    -- Access Control
    visibility document_visibility DEFAULT 'private',
    owner_id UUID REFERENCES public.user_profiles(id) NOT NULL,
    company_id UUID REFERENCES public.companies(id) DEFAULT '00000000-0000-0000-0000-000000000001',
    
    -- Metadata
    color VARCHAR DEFAULT '#6B7280',
    icon VARCHAR DEFAULT 'folder',
    sort_order INTEGER DEFAULT 0,
    custom_metadata JSONB DEFAULT '{}',
    
    -- Stats
    document_count INTEGER DEFAULT 0,
    total_size_bytes BIGINT DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.user_profiles(id)
);

-- Create default folders
INSERT INTO public.folders (id, name, slug, path, level, visibility, owner_id, company_id) VALUES
('10000000-0000-0000-0000-000000000001', 'FAQ & Documentation', 'faq', '/faq', 0, 'internal', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000002', 'XML Configuration', 'xml', '/xml', 0, 'internal', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000003', 'Customer Documents', 'customer', '/customer', 0, 'company', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001'),
('10000000-0000-0000-0000-000000000004', 'Internal StreamWorks', 'internal', '/internal', 0, 'internal', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001');

-- ================================
-- SYSTEM CONFIGURATION
-- ================================

CREATE TABLE public.system_settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    category VARCHAR NOT NULL,
    key VARCHAR NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    updated_by UUID REFERENCES public.user_profiles(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(category, key)
);

-- Insert default system settings
INSERT INTO public.system_settings (category, key, value, description, is_public) VALUES
('chat', 'rate_limits', '{"customer": 50, "streamworks_colleague": 200, "streamworks_admin": 500, "owner": 1000}', 'Chat rate limits per hour by role', false),
('documents', 'max_file_size_mb', '50', 'Maximum file size in MB', true),
('documents', 'allowed_types', '["pdf", "docx", "txt", "md"]', 'Allowed document types', true),
('security', 'session_timeout_minutes', '480', 'Session timeout in minutes', false),
('security', 'require_2fa_roles', '["owner", "streamworks_admin"]', 'Roles that require 2FA', false);

-- ================================
-- API KEYS & INTEGRATIONS
-- ================================

CREATE TABLE public.api_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR NOT NULL,
    key_hash VARCHAR NOT NULL UNIQUE, -- bcrypt hash
    key_prefix VARCHAR NOT NULL, -- First 8 chars for identification
    user_id UUID REFERENCES public.user_profiles(id) NOT NULL,
    company_id UUID REFERENCES public.companies(id),
    
    -- Permissions
    scopes TEXT[] NOT NULL DEFAULT '{}',
    rate_limit_per_hour INTEGER DEFAULT 1000,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES public.user_profiles(id)
);

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

-- User profiles indexes
CREATE INDEX idx_user_profiles_role ON public.user_profiles(role);
CREATE INDEX idx_user_profiles_company ON public.user_profiles(company_id);
CREATE INDEX idx_user_profiles_status ON public.user_profiles(status);
CREATE INDEX idx_user_profiles_email ON public.user_profiles(email);

-- Permissions indexes
CREATE INDEX idx_permissions_user ON public.permissions(user_id);
CREATE INDEX idx_permissions_resource ON public.permissions(resource_type, resource_id);
CREATE INDEX idx_permissions_level ON public.permissions(permission_level);
CREATE INDEX idx_permissions_expires ON public.permissions(expires_at) WHERE expires_at IS NOT NULL;

-- Folders indexes
CREATE INDEX idx_folders_path ON public.folders(path);
CREATE INDEX idx_folders_parent ON public.folders(parent_id);
CREATE INDEX idx_folders_owner ON public.folders(owner_id);
CREATE INDEX idx_folders_company ON public.folders(company_id);

-- Companies indexes
CREATE INDEX idx_companies_slug ON public.companies(slug);
CREATE INDEX idx_companies_domain ON public.companies(domain);

-- ================================
-- FUNCTIONS & TRIGGERS
-- ================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON public.user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON public.companies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_folders_updated_at BEFORE UPDATE ON public.folders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically update folder document count
CREATE OR REPLACE FUNCTION update_folder_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update document count and total size for folder
    UPDATE public.folders SET
        document_count = (
            SELECT COUNT(*) FROM public.documents WHERE folder_id = NEW.folder_id
        ),
        total_size_bytes = (
            SELECT COALESCE(SUM(file_size_bytes), 0) FROM public.documents WHERE folder_id = NEW.folder_id
        )
    WHERE id = NEW.folder_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to generate materialized path for folders
CREATE OR REPLACE FUNCTION generate_folder_path()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.parent_id IS NULL THEN
        NEW.path = '/' || NEW.slug;
        NEW.level = 0;
    ELSE
        SELECT path || '/' || NEW.slug, level + 1
        INTO NEW.path, NEW.level
        FROM public.folders
        WHERE id = NEW.parent_id;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER generate_folder_path_trigger
    BEFORE INSERT OR UPDATE ON public.folders
    FOR EACH ROW EXECUTE FUNCTION generate_folder_path();

-- ================================
-- COMMENTS FOR DOCUMENTATION
-- ================================

COMMENT ON TABLE public.user_profiles IS 'Extended user profiles with RBAC roles and company associations';
COMMENT ON TABLE public.companies IS 'Organizations/companies for multi-tenant support';
COMMENT ON TABLE public.permissions IS 'Granular permissions for resources';
COMMENT ON TABLE public.role_permissions IS 'Default permissions by role';
COMMENT ON TABLE public.folders IS 'Folder hierarchy with access control';
COMMENT ON TABLE public.system_settings IS 'System-wide configuration settings';
COMMENT ON TABLE public.api_keys IS 'API keys for external integrations';

COMMENT ON COLUMN public.user_profiles.role IS 'User role determining base permissions';
COMMENT ON COLUMN public.permissions.expires_at IS 'Optional expiration for temporary permissions';
COMMENT ON COLUMN public.folders.path IS 'Materialized path for efficient hierarchy queries';
COMMENT ON COLUMN public.folders.visibility IS 'Access control level for folder contents';