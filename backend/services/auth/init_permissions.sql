-- Create a table for public profiles
CREATE TABLE IF NOT EXISTS public.profiles (
  id uuid REFERENCES auth.users ON DELETE CASCADE NOT NULL PRIMARY KEY,
  updated_at timestamp with time zone,
  username text UNIQUE,
  full_name text,
  avatar_url text,
  website text,
  role text DEFAULT 'customer' CHECK (role IN ('owner', 'admin', 'internal', 'customer')),
  organization_id uuid,
  
  CONSTRAINT username_length CHECK (char_length(username) >= 3)
);

-- Set up Row Level Security (RLS)
-- See https://supabase.com/docs/guides/auth/row-level-security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public profiles are viewable by everyone." ON public.profiles
  FOR SELECT USING (true);

CREATE POLICY "Users can insert their own profile." ON public.profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile." ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- Handle User Creation Trigger
-- This ensures a profile is created whenever a user signs up via Auth
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, full_name, role)
  VALUES (new.id, new.raw_user_meta_data->>'full_name', COALESCE(new.raw_user_meta_data->>'role', 'customer'));
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- Create document_permissions table for granular access
CREATE TABLE IF NOT EXISTS public.document_permissions (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    doc_id text NOT NULL, -- Corresponds to Qdrant ID or Document Store ID
    role text CHECK (role IN ('owner', 'admin', 'internal', 'customer')),
    user_id uuid REFERENCES auth.users(id),
    can_view boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    UNIQUE(doc_id, role),
    UNIQUE(doc_id, user_id)
);

ALTER TABLE public.document_permissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Docs permissions viewable by internal+" ON public.document_permissions
  FOR SELECT USING (
    (SELECT role FROM public.profiles WHERE id = auth.uid()) IN ('owner', 'admin', 'internal')
  );

-- Function to check access (Helper for RLS or Supabase functions)
CREATE OR REPLACE FUNCTION public.has_role(required_role text)
RETURNS boolean AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM public.profiles 
    WHERE id = auth.uid() 
    AND role = required_role
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
