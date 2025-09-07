-- ================================
-- Initial Test Data Migration
-- Creates test users and sample data for development
-- ================================

-- ================================
-- TEST COMPANIES
-- ================================

-- Insert test customer companies
INSERT INTO public.companies (id, name, slug, domain, subscription_tier, max_users, max_documents, storage_limit_gb) VALUES
('11111111-1111-1111-1111-111111111111', 'Test Customer GmbH', 'test-customer', 'test-customer.de', 'basic', 5, 50, 5),
('22222222-2222-2222-2222-222222222222', 'Enterprise Client AG', 'enterprise-client', 'enterprise-client.com', 'enterprise', 50, 500, 100),
('33333333-3333-3333-3333-333333333333', 'Startup Innovation UG', 'startup-innovation', 'startup.io', 'pro', 10, 100, 20);

-- ================================
-- TEST USER PROFILES
-- Note: These will be created when users sign up via Supabase Auth
-- This is just for reference - actual users need to be created via auth system
-- ================================

-- Sample system settings for testing
INSERT INTO public.system_settings (category, key, value, description, is_public) VALUES
('testing', 'enable_test_mode', 'true', 'Enable test mode for development', false),
('testing', 'test_data_loaded', 'true', 'Indicates test data has been loaded', false),
('ui', 'default_theme', '"light"', 'Default UI theme', true),
('ui', 'items_per_page', '25', 'Default items per page', true),
('notifications', 'email_enabled', 'true', 'Enable email notifications', true),
('notifications', 'slack_webhook_url', '""', 'Slack webhook for notifications', false);

-- ================================
-- TEST FOLDERS STRUCTURE
-- ================================

-- Create additional test folders
INSERT INTO public.folders (id, name, slug, path, level, visibility, owner_id, company_id, description) VALUES
-- StreamWorks internal structure
('20000000-0000-0000-0000-000000000001', 'Grundlagen', 'grundlagen', '/faq/grundlagen', 1, 'internal', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'Grundlegende StreamWorks Dokumentation'),
('20000000-0000-0000-0000-000000000002', 'API Documentation', 'api-docs', '/faq/api-docs', 1, 'internal', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'API Dokumentation und Guides'),
('20000000-0000-0000-0000-000000000003', 'Security Guidelines', 'security', '/internal/security', 1, 'confidential', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'Interne Sicherheitsrichtlinien'),

-- Customer-specific folders
('30000000-0000-0000-0000-000000000001', 'Test Customer Docs', 'test-customer-docs', '/customer/test-customer', 1, 'company', '11111111-1111-1111-1111-111111111111', '11111111-1111-1111-1111-111111111111', 'Dokumente für Test Customer GmbH'),
('30000000-0000-0000-0000-000000000002', 'Enterprise Client Resources', 'enterprise-resources', '/customer/enterprise', 1, 'company', '22222222-2222-2222-2222-222222222222', '22222222-2222-2222-2222-222222222222', 'Ressourcen für Enterprise Client AG'),

-- Public folders
('40000000-0000-0000-0000-000000000001', 'Public Downloads', 'public-downloads', '/public/downloads', 1, 'public', '00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'Öffentlich zugängliche Downloads');

-- Update parent folder references
UPDATE public.folders SET parent_id = '10000000-0000-0000-0000-000000000001' WHERE id = '20000000-0000-0000-0000-000000000001';
UPDATE public.folders SET parent_id = '10000000-0000-0000-0000-000000000001' WHERE id = '20000000-0000-0000-0000-000000000002';
UPDATE public.folders SET parent_id = '10000000-0000-0000-0000-000000000004' WHERE id = '20000000-0000-0000-0000-000000000003';
UPDATE public.folders SET parent_id = '10000000-0000-0000-0000-000000000003' WHERE id = '30000000-0000-0000-0000-000000000001';
UPDATE public.folders SET parent_id = '10000000-0000-0000-0000-000000000003' WHERE id = '30000000-0000-0000-0000-000000000002';

-- ================================
-- SAMPLE PERMISSIONS
-- Note: These will be created when actual users are added
-- ================================

-- Sample role-based permissions for testing UI
INSERT INTO public.role_permissions (role, resource_type, permission_level, description) VALUES
-- Additional granular permissions for testing
('streamworks_colleague', 'folder', 'read', 'Read access to folders'),
('customer', 'folder', 'read', 'Read access to assigned folders only'),
('streamworks_admin', 'system', 'read', 'Read system settings'),
('owner', 'audit_logs', 'read', 'Full audit log access');

-- ================================
-- SAMPLE AUDIT LOG ENTRIES
-- Note: These are just examples - real audit logs will be created by the system
-- ================================

-- Create some sample audit entries for testing the dashboard
-- (In production, these would be created by the audit service)

-- ================================
-- SAMPLE SYSTEM CONFIGURATION
-- ================================

-- Additional system settings for features
INSERT INTO public.system_settings (category, key, value, description, is_public) VALUES
('features', 'chat_enabled', 'true', 'Enable chat functionality', true),
('features', 'document_upload_enabled', 'true', 'Enable document uploads', true),
('features', 'ai_summarization_enabled', 'true', 'Enable AI document summarization', true),
('features', 'full_text_search_enabled', 'true', 'Enable full-text search', true),
('features', 'audit_logging_enabled', 'true', 'Enable comprehensive audit logging', false),
('features', 'security_monitoring_enabled', 'true', 'Enable security event monitoring', false),

('limits', 'max_chat_messages_per_day', '{"customer": 50, "streamworks_colleague": 200, "streamworks_admin": 500, "owner": 1000}', 'Daily chat message limits by role', false),
('limits', 'max_document_size_mb', '50', 'Maximum document size in MB', true),
('limits', 'max_documents_per_user', '{"customer": 10, "streamworks_colleague": 100, "streamworks_admin": 500, "owner": 1000}', 'Maximum documents per user by role', false),

('ai', 'default_model', '"gpt-3.5-turbo"', 'Default AI model for chat', false),
('ai', 'enable_local_llm', 'true', 'Enable local LLM fallback', false),
('ai', 'summarization_model', '"gpt-3.5-turbo"', 'Model for document summarization', false),
('ai', 'embedding_model', '"text-embedding-ada-002"', 'Model for document embeddings', false),

('storage', 'provider', '"supabase"', 'Storage provider', false),
('storage', 'bucket_name', '"documents"', 'Storage bucket name', false),
('storage', 'max_storage_per_company_gb', '{"basic": 5, "pro": 20, "enterprise": 100}', 'Storage limits by subscription tier', false);

-- ================================
-- SAMPLE DOCUMENT RECORDS
-- Note: These reference the existing documents from your documents.json
-- We'll migrate the existing documents to the new structure
-- ================================

-- Sample document entries that match your existing documents.json structure
-- These would be migrated from your existing storage/documents.json

-- ================================
-- CREATE HELPFUL VIEWS FOR TESTING
-- ================================

-- View for testing role-based access
CREATE VIEW public.test_user_access AS
SELECT 
    up.id as user_id,
    up.email,
    up.role,
    up.company_id,
    c.name as company_name,
    COUNT(DISTINCT d.id) as accessible_documents,
    COUNT(DISTINCT f.id) as accessible_folders
FROM public.user_profiles up
LEFT JOIN public.companies c ON up.company_id = c.id
LEFT JOIN public.documents d ON (
    d.owner_id = up.id OR
    d.visibility = 'public' OR
    (d.visibility = 'internal' AND up.role IN ('owner', 'streamworks_admin', 'streamworks_colleague')) OR
    (d.visibility = 'company' AND d.company_id = up.company_id)
)
LEFT JOIN public.folders f ON (
    f.owner_id = up.id OR
    f.visibility = 'public' OR
    (f.visibility = 'internal' AND up.role IN ('owner', 'streamworks_admin', 'streamworks_colleague')) OR
    (f.visibility = 'company' AND f.company_id = up.company_id)
)
GROUP BY up.id, up.email, up.role, up.company_id, c.name;

-- View for testing permission matrix
CREATE VIEW public.test_permission_matrix AS
SELECT 
    up.email,
    up.role,
    rp.resource_type,
    rp.permission_level,
    rp.description,
    CASE 
        WHEN rp.role = up.role THEN true
        ELSE false
    END as has_default_permission
FROM public.user_profiles up
CROSS JOIN public.role_permissions rp
ORDER BY up.role, rp.resource_type, rp.permission_level;

-- ================================
-- FUNCTIONS FOR TESTING
-- ================================

-- Function to simulate user login for testing
CREATE OR REPLACE FUNCTION public.test_simulate_user_context(user_email TEXT)
RETURNS TABLE (
    user_id UUID,
    user_role user_role,
    company_id UUID,
    company_name TEXT
) 
LANGUAGE sql
SECURITY DEFINER
AS $$
    SELECT 
        up.id,
        up.role,
        up.company_id,
        c.name
    FROM public.user_profiles up
    LEFT JOIN public.companies c ON up.company_id = c.id
    WHERE up.email = user_email;
$$;

-- Function to create test document
CREATE OR REPLACE FUNCTION public.test_create_document(
    p_filename TEXT,
    p_category document_category,
    p_visibility document_visibility,
    p_owner_email TEXT
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_owner_id UUID;
    v_company_id UUID;
    v_document_id UUID;
BEGIN
    -- Get owner info
    SELECT id, company_id INTO v_owner_id, v_company_id
    FROM public.user_profiles 
    WHERE email = p_owner_email;
    
    IF v_owner_id IS NULL THEN
        RAISE EXCEPTION 'User with email % not found', p_owner_email;
    END IF;
    
    -- Create document
    INSERT INTO public.documents (
        filename,
        original_filename,
        file_path,
        file_size_bytes,
        mime_type,
        checksum,
        doctype,
        category,
        visibility,
        owner_id,
        company_id,
        status,
        created_by
    ) VALUES (
        p_filename,
        p_filename,
        '/test/' || p_filename,
        1024, -- 1KB test file
        'application/pdf',
        'test-checksum-' || gen_random_uuid(),
        'manual',
        p_category,
        p_visibility,
        v_owner_id,
        v_company_id,
        'processed',
        v_owner_id
    ) RETURNING id INTO v_document_id;
    
    RETURN v_document_id;
END;
$$;

-- ================================
-- SAMPLE DATA GENERATOR FUNCTION
-- ================================

CREATE OR REPLACE FUNCTION public.generate_test_permissions()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- This function will be used to generate test permissions
    -- when actual users are created via the auth system
    
    -- Example: Grant customer read access to specific documents
    -- This would be called after users are created
    
    RAISE NOTICE 'Test permission generator ready. Call after creating actual users via Supabase Auth.';
END;
$$;

-- ================================
-- COMMENTS FOR TEST DATA
-- ================================

COMMENT ON VIEW public.test_user_access IS 'Shows accessible documents and folders per user for testing';
COMMENT ON VIEW public.test_permission_matrix IS 'Permission matrix for testing role-based access';
COMMENT ON FUNCTION public.test_simulate_user_context IS 'Simulate user context for testing (development only)';
COMMENT ON FUNCTION public.test_create_document IS 'Create test documents for development';
COMMENT ON FUNCTION public.generate_test_permissions IS 'Generate test permissions for development users';

-- ================================
-- DEVELOPMENT NOTICES
-- ================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '======================================';
    RAISE NOTICE 'RBAC Test Data Migration Completed';
    RAISE NOTICE '======================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Create actual users via Supabase Auth UI or signup';
    RAISE NOTICE '2. Assign roles to users via user_profiles table';
    RAISE NOTICE '3. Test permissions with different user roles';
    RAISE NOTICE '4. Use test views to verify access controls';
    RAISE NOTICE '';
    RAISE NOTICE 'Test companies created:';
    RAISE NOTICE '- StreamWorks GmbH (default)';
    RAISE NOTICE '- Test Customer GmbH'; 
    RAISE NOTICE '- Enterprise Client AG';
    RAISE NOTICE '- Startup Innovation UG';
    RAISE NOTICE '';
    RAISE NOTICE 'Test folders created with different visibility levels';
    RAISE NOTICE 'System settings configured for development';
    RAISE NOTICE '';
    RAISE NOTICE '======================================';
END $$;