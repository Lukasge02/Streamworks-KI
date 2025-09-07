-- ================================
-- Row Level Security Policies
-- Comprehensive RBAC security implementation
-- ================================

-- ================================
-- ENABLE RLS ON ALL TABLES
-- ================================

ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.folders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.security_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_shares ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_versions ENABLE ROW LEVEL SECURITY;

-- ================================
-- HELPER FUNCTIONS
-- ================================

-- Function to get current user's role
CREATE OR REPLACE FUNCTION auth.current_user_role()
RETURNS user_role
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT role FROM public.user_profiles WHERE id = auth.uid();
$$;

-- Function to get current user's company
CREATE OR REPLACE FUNCTION auth.current_user_company()
RETURNS UUID
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT company_id FROM public.user_profiles WHERE id = auth.uid();
$$;

-- Function to check if user has permission for resource
CREATE OR REPLACE FUNCTION auth.has_permission(resource_type text, resource_id text, permission_level text)
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1 FROM public.permissions p
        WHERE p.user_id = auth.uid()
        AND p.resource_type = resource_type::resource_type
        AND p.resource_id = resource_id
        AND p.permission_level = permission_level::permission_level
        AND (p.expires_at IS NULL OR p.expires_at > NOW())
    );
$$;

-- Function to check if user is admin (owner or streamworks_admin)
CREATE OR REPLACE FUNCTION auth.is_admin()
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT auth.current_user_role() IN ('owner', 'streamworks_admin');
$$;

-- Function to check if user is StreamWorks employee
CREATE OR REPLACE FUNCTION auth.is_streamworks_employee()
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT auth.current_user_role() IN ('owner', 'streamworks_admin', 'streamworks_colleague');
$$;

-- ================================
-- USER PROFILES POLICIES
-- ================================

-- Users can read their own profile and profiles in their company (if admin)
CREATE POLICY "user_profiles_select" ON public.user_profiles
FOR SELECT USING (
    auth.uid() = id OR
    auth.is_admin() OR
    (
        auth.is_streamworks_employee() AND
        company_id = auth.current_user_company()
    )
);

-- Users can update their own profile, admins can update others
CREATE POLICY "user_profiles_update" ON public.user_profiles  
FOR UPDATE USING (
    auth.uid() = id OR
    auth.is_admin()
);

-- Only admins can insert new users
CREATE POLICY "user_profiles_insert" ON public.user_profiles
FOR INSERT WITH CHECK (
    auth.is_admin()
);

-- Only owners can delete users
CREATE POLICY "user_profiles_delete" ON public.user_profiles
FOR DELETE USING (
    auth.current_user_role() = 'owner'
);

-- ================================
-- COMPANIES POLICIES  
-- ================================

-- Users can read their own company, admins can read all
CREATE POLICY "companies_select" ON public.companies
FOR SELECT USING (
    auth.is_admin() OR
    id = auth.current_user_company()
);

-- Only admins can modify companies
CREATE POLICY "companies_update" ON public.companies
FOR UPDATE USING (auth.is_admin());

CREATE POLICY "companies_insert" ON public.companies
FOR INSERT WITH CHECK (auth.is_admin());

CREATE POLICY "companies_delete" ON public.companies
FOR DELETE USING (auth.current_user_role() = 'owner');

-- ================================
-- PERMISSIONS POLICIES
-- ================================

-- Users can see permissions granted to them, admins can see all
CREATE POLICY "permissions_select" ON public.permissions
FOR SELECT USING (
    user_id = auth.uid() OR
    auth.is_admin() OR
    granted_by = auth.uid()
);

-- Only users with admin permission on resource can grant permissions
CREATE POLICY "permissions_insert" ON public.permissions
FOR INSERT WITH CHECK (
    auth.is_admin() OR
    auth.has_permission(resource_type::text, resource_id, 'admin')
);

-- Only granters or admins can modify permissions
CREATE POLICY "permissions_update" ON public.permissions
FOR UPDATE USING (
    granted_by = auth.uid() OR
    auth.is_admin()
);

-- Only granters or admins can delete permissions
CREATE POLICY "permissions_delete" ON public.permissions
FOR DELETE USING (
    granted_by = auth.uid() OR
    auth.is_admin()
);

-- ================================
-- ROLE PERMISSIONS POLICIES
-- ================================

-- Everyone can read role permissions (for UI)
CREATE POLICY "role_permissions_select" ON public.role_permissions
FOR SELECT USING (true);

-- Only owners can modify role permissions
CREATE POLICY "role_permissions_modify" ON public.role_permissions
FOR ALL USING (auth.current_user_role() = 'owner');

-- ================================
-- FOLDERS POLICIES
-- ================================

-- Users can see folders they own, have access to, or are public/internal
CREATE POLICY "folders_select" ON public.folders
FOR SELECT USING (
    -- Owner can access
    owner_id = auth.uid() OR
    
    -- Admins can access all
    auth.is_admin() OR
    
    -- Public folders
    visibility = 'public' OR
    
    -- Internal folders for StreamWorks employees
    (visibility = 'internal' AND auth.is_streamworks_employee()) OR
    
    -- Company folders for same company members
    (visibility = 'company' AND company_id = auth.current_user_company()) OR
    
    -- Explicit permissions
    auth.has_permission('folder', id::text, 'read')
);

-- Users can create folders in their company or if they have permission
CREATE POLICY "folders_insert" ON public.folders
FOR INSERT WITH CHECK (
    -- Admins can create anywhere
    auth.is_admin() OR
    
    -- Users can create in their company with private visibility
    (
        visibility = 'private' AND
        owner_id = auth.uid() AND
        company_id = auth.current_user_company()
    ) OR
    
    -- StreamWorks employees can create internal folders
    (
        auth.is_streamworks_employee() AND
        visibility IN ('internal', 'private') AND
        company_id = '00000000-0000-0000-0000-000000000001'
    )
);

-- Users can update folders they own or have admin permission on
CREATE POLICY "folders_update" ON public.folders
FOR UPDATE USING (
    owner_id = auth.uid() OR
    auth.is_admin() OR
    auth.has_permission('folder', id::text, 'admin')
);

-- Users can delete folders they own or have admin permission on
CREATE POLICY "folders_delete" ON public.folders
FOR DELETE USING (
    owner_id = auth.uid() OR
    auth.is_admin() OR
    auth.has_permission('folder', id::text, 'admin')
);

-- ================================
-- DOCUMENTS POLICIES  
-- ================================

-- Complex document access based on role, visibility, and permissions
CREATE POLICY "documents_select" ON public.documents
FOR SELECT USING (
    -- Admins can access everything
    auth.is_admin() OR
    
    -- Document owner
    owner_id = auth.uid() OR
    
    -- Public documents
    visibility = 'public' OR
    
    -- Internal documents for StreamWorks employees
    (visibility = 'internal' AND auth.is_streamworks_employee()) OR
    
    -- Company documents for same company members
    (visibility = 'company' AND company_id = auth.current_user_company()) OR
    
    -- Explicit permissions granted
    auth.has_permission('document', id::text, 'read')
);

-- Document insertion based on role and category
CREATE POLICY "documents_insert" ON public.documents
FOR INSERT WITH CHECK (
    -- Admins can insert anywhere
    auth.is_admin() OR
    
    -- StreamWorks colleagues can insert internal documents
    (
        auth.current_user_role() = 'streamworks_colleague' AND
        category IN ('internal', 'general', 'faq') AND
        visibility IN ('internal', 'private')
    ) OR
    
    -- Users can insert private documents to their own company
    (
        visibility = 'private' AND
        owner_id = auth.uid() AND
        company_id = auth.current_user_company() AND
        category IN ('general', 'customer')
    )
);

-- Document updates
CREATE POLICY "documents_update" ON public.documents
FOR UPDATE USING (
    -- Document owner
    owner_id = auth.uid() OR
    
    -- Explicit write permissions
    auth.has_permission('document', id::text, 'write') OR
    
    -- Admins
    auth.is_admin()
);

-- Document deletion
CREATE POLICY "documents_delete" ON public.documents
FOR DELETE USING (
    -- Document owner
    owner_id = auth.uid() OR
    
    -- Explicit delete permissions
    auth.has_permission('document', id::text, 'delete') OR
    
    -- Admins
    auth.is_admin()
);

-- ================================
-- CHAT POLICIES
-- ================================

-- Users can only access their own chat sessions
CREATE POLICY "chat_sessions_select" ON public.chat_sessions
FOR SELECT USING (
    user_id = auth.uid() OR
    auth.is_admin()
);

-- Users can create their own chat sessions
CREATE POLICY "chat_sessions_insert" ON public.chat_sessions
FOR INSERT WITH CHECK (
    user_id = auth.uid()
);

-- Users can update their own chat sessions
CREATE POLICY "chat_sessions_update" ON public.chat_sessions
FOR UPDATE USING (
    user_id = auth.uid() OR
    auth.is_admin()
);

-- Users can delete their own chat sessions
CREATE POLICY "chat_sessions_delete" ON public.chat_sessions
FOR DELETE USING (
    user_id = auth.uid() OR
    auth.is_admin()
);

-- Chat messages follow session permissions
CREATE POLICY "chat_messages_select" ON public.chat_messages  
FOR SELECT USING (
    user_id = auth.uid() OR
    EXISTS (
        SELECT 1 FROM public.chat_sessions cs
        WHERE cs.id = chat_messages.session_id
        AND cs.user_id = auth.uid()
    ) OR
    auth.is_admin()
);

CREATE POLICY "chat_messages_insert" ON public.chat_messages
FOR INSERT WITH CHECK (
    user_id = auth.uid() OR
    EXISTS (
        SELECT 1 FROM public.chat_sessions cs
        WHERE cs.id = chat_messages.session_id
        AND cs.user_id = auth.uid()
    )
);

-- ================================
-- AUDIT & SECURITY POLICIES
-- ================================

-- Users can see their own audit logs, admins can see all
CREATE POLICY "audit_logs_select" ON public.audit_logs
FOR SELECT USING (
    user_id = auth.uid() OR
    auth.is_admin()
);

-- Only system/service can insert audit logs
CREATE POLICY "audit_logs_insert" ON public.audit_logs
FOR INSERT WITH CHECK (
    auth.role() = 'service_role' OR
    auth.is_admin()
);

-- Security events - admins only
CREATE POLICY "security_events_select" ON public.security_events
FOR SELECT USING (auth.is_admin());

CREATE POLICY "security_events_insert" ON public.security_events
FOR INSERT WITH CHECK (
    auth.role() = 'service_role' OR
    auth.is_admin()
);

CREATE POLICY "security_events_update" ON public.security_events
FOR UPDATE USING (auth.is_admin());

-- ================================
-- SYSTEM SETTINGS POLICIES
-- ================================

-- Public settings can be read by all, private by admins only
CREATE POLICY "system_settings_select" ON public.system_settings
FOR SELECT USING (
    is_public = true OR
    auth.is_admin()
);

-- Only admins can modify system settings
CREATE POLICY "system_settings_modify" ON public.system_settings
FOR ALL USING (auth.is_admin());

-- ================================
-- API KEYS POLICIES
-- ================================

-- Users can see their own API keys, admins can see all
CREATE POLICY "api_keys_select" ON public.api_keys
FOR SELECT USING (
    user_id = auth.uid() OR
    auth.is_admin()
);

-- Users can create their own API keys (if allowed by role)
CREATE POLICY "api_keys_insert" ON public.api_keys
FOR INSERT WITH CHECK (
    user_id = auth.uid() AND
    auth.is_streamworks_employee()
);

-- Users can update their own API keys
CREATE POLICY "api_keys_update" ON public.api_keys
FOR UPDATE USING (
    user_id = auth.uid() OR
    auth.is_admin()
);

-- Users can delete their own API keys
CREATE POLICY "api_keys_delete" ON public.api_keys
FOR DELETE USING (
    user_id = auth.uid() OR
    auth.is_admin()
);

-- ================================
-- DOCUMENT PROCESSING POLICIES
-- ================================

-- Users can see jobs for their documents, admins can see all
CREATE POLICY "document_jobs_select" ON public.document_jobs
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = document_jobs.document_id
        AND d.owner_id = auth.uid()
    ) OR
    auth.is_admin()
);

-- Only system can insert/update job records
CREATE POLICY "document_jobs_modify" ON public.document_jobs
FOR ALL USING (
    auth.role() = 'service_role' OR
    auth.is_admin()
);

-- ================================
-- DOCUMENT SHARING POLICIES
-- ================================

-- Users can see shares they created or received, admins can see all
CREATE POLICY "document_shares_select" ON public.document_shares
FOR SELECT USING (
    shared_by = auth.uid() OR
    shared_with = auth.uid() OR
    auth.is_admin()
);

-- Users can create shares for documents they own or have admin access to
CREATE POLICY "document_shares_insert" ON public.document_shares
FOR INSERT WITH CHECK (
    shared_by = auth.uid() AND (
        EXISTS (
            SELECT 1 FROM public.documents d
            WHERE d.id = document_shares.document_id
            AND d.owner_id = auth.uid()
        ) OR
        auth.has_permission('document', document_id::text, 'admin')
    )
);

-- Users can update shares they created
CREATE POLICY "document_shares_update" ON public.document_shares
FOR UPDATE USING (
    shared_by = auth.uid() OR
    auth.is_admin()
);

-- Users can delete shares they created
CREATE POLICY "document_shares_delete" ON public.document_shares
FOR DELETE USING (
    shared_by = auth.uid() OR
    auth.is_admin()
);

-- ================================
-- DOCUMENT VERSIONS POLICIES
-- ================================

-- Users can see versions of documents they have access to
CREATE POLICY "document_versions_select" ON public.document_versions
FOR SELECT USING (
    EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = document_versions.document_id
        AND (
            d.owner_id = auth.uid() OR
            auth.has_permission('document', d.id::text, 'read') OR
            auth.is_admin()
        )
    )
);

-- Only system can insert version records (via trigger)
CREATE POLICY "document_versions_insert" ON public.document_versions
FOR INSERT WITH CHECK (
    auth.role() = 'service_role' OR
    auth.is_admin() OR
    EXISTS (
        SELECT 1 FROM public.documents d
        WHERE d.id = document_versions.document_id
        AND d.owner_id = auth.uid()
    )
);

-- ================================
-- GRANT PERMISSIONS TO AUTHENTICATED USERS
-- ================================

-- Grant usage on sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Grant select/insert/update permissions to authenticated users
-- (RLS will handle the actual access control)
GRANT SELECT ON public.user_profiles TO authenticated;
GRANT INSERT, UPDATE ON public.user_profiles TO authenticated;

GRANT SELECT ON public.companies TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.companies TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE ON public.permissions TO authenticated;
GRANT SELECT ON public.role_permissions TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE ON public.folders TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.documents TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE ON public.chat_sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.chat_messages TO authenticated;

GRANT SELECT, INSERT ON public.audit_logs TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.security_events TO authenticated;

GRANT SELECT ON public.system_settings TO authenticated;
GRANT INSERT, UPDATE, DELETE ON public.system_settings TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE ON public.api_keys TO authenticated;
GRANT SELECT ON public.document_jobs TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.document_shares TO authenticated;
GRANT SELECT, INSERT ON public.document_versions TO authenticated;

-- Grant execute on functions
GRANT EXECUTE ON FUNCTION auth.current_user_role() TO authenticated;
GRANT EXECUTE ON FUNCTION auth.current_user_company() TO authenticated;
GRANT EXECUTE ON FUNCTION auth.has_permission(text, text, text) TO authenticated;
GRANT EXECUTE ON FUNCTION auth.is_admin() TO authenticated;
GRANT EXECUTE ON FUNCTION auth.is_streamworks_employee() TO authenticated;
GRANT EXECUTE ON FUNCTION search_documents(text, uuid, document_category, integer) TO authenticated;

-- Grant access to views
GRANT SELECT ON public.active_documents TO authenticated;
GRANT SELECT ON public.recent_activity TO authenticated;
GRANT SELECT ON public.document_stats TO authenticated;

-- ================================
-- SPECIAL PERMISSIONS FOR SERVICE ROLE
-- ================================

-- Service role needs full access for system operations
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- ================================
-- COMMENTS FOR DOCUMENTATION
-- ================================

COMMENT ON POLICY "user_profiles_select" ON public.user_profiles IS 'Users can read their own profile and admins can read all profiles';
COMMENT ON POLICY "documents_select" ON public.documents IS 'Complex document access based on visibility, ownership, and explicit permissions';
COMMENT ON POLICY "chat_sessions_select" ON public.chat_sessions IS 'Users can only access their own chat sessions unless admin';
COMMENT ON POLICY "audit_logs_select" ON public.audit_logs IS 'Users see their own actions, admins see all audit logs';

COMMENT ON FUNCTION auth.current_user_role() IS 'Helper function to get current authenticated user role';
COMMENT ON FUNCTION auth.has_permission(text, text, text) IS 'Check if current user has specific permission for resource';
COMMENT ON FUNCTION auth.is_admin() IS 'Check if current user is admin (owner or streamworks_admin)';
COMMENT ON FUNCTION auth.is_streamworks_employee() IS 'Check if current user is StreamWorks employee';