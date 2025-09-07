-- Migration: Fix DocumentStatus enum case issue
-- Date: 2025-09-06
-- Description: Fix case mismatch between Python enum and PostgreSQL enum

-- First update all documents to use a temporary status
ALTER TABLE documents ADD COLUMN temp_status text;

-- Update temp column with lowercase values
UPDATE documents SET temp_status = 
  CASE 
    WHEN status::text = 'UPLOADING' THEN 'uploading'
    WHEN status::text = 'PROCESSING' THEN 'processing' 
    WHEN status::text = 'READY' THEN 'ready'
    WHEN status::text = 'ERROR' THEN 'error'
    ELSE 'ready'
  END;

-- Drop the old enum column
ALTER TABLE documents DROP COLUMN status;

-- Recreate the enum type with correct values
DROP TYPE IF EXISTS documentstatus CASCADE;
CREATE TYPE documentstatus AS ENUM ('uploading', 'analyzing', 'processing', 'ready', 'skipped', 'error');

-- Add the column back with new enum
ALTER TABLE documents ADD COLUMN status documentstatus DEFAULT 'uploading';

-- Update with correct values
UPDATE documents SET status = temp_status::documentstatus;

-- Make the column not null
ALTER TABLE documents ALTER COLUMN status SET NOT NULL;

-- Drop the temporary column
ALTER TABLE documents DROP COLUMN temp_status;