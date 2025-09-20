-- Migration: Add new document status values (analyzing, skipped)
-- Date: 2025-09-06
-- Description: Extend DocumentStatus enum with new values for improved status tracking

-- Add new values to the documentstatus enum
ALTER TYPE documentstatus ADD VALUE IF NOT EXISTS 'analyzing';
ALTER TYPE documentstatus ADD VALUE IF NOT EXISTS 'skipped';