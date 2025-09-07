#!/bin/bash

# Supabase Migration Runner
# Führt die document_chunks Migration direkt in Supabase aus

echo "🚀 Running Supabase Migration..."

# Supabase connection details
DB_HOST="db.snzxgfmewxbeevoywula.supabase.co"
DB_PORT="5432"
DB_NAME="postgres"
DB_USER="postgres"

# You'll need to enter the password when prompted
# Password: Specki2002!

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo "❌ psql is not installed. Install it with: brew install postgresql"
    exit 1
fi

# Run migration
echo "📋 Executing migration 002_document_chunks.sql..."
psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER -f backend/database/migrations/002_document_chunks.sql

if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully!"
    
    # Verify tables
    echo ""
    echo "📊 Verifying tables..."
    psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER -c "
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('documents', 'document_chunks', 'folders')
        ORDER BY table_name;"
    
    # Check chunk table structure
    echo ""
    echo "🔍 Document chunks table structure:"
    psql -h $DB_HOST -p $DB_PORT -d $DB_NAME -U $DB_USER -c "
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'document_chunks'
        ORDER BY ordinal_position
        LIMIT 10;"
else
    echo "❌ Migration failed!"
    exit 1
fi

echo ""
echo "🎉 Supabase is ready for Docling chunks!"