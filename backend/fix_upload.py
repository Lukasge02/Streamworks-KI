#!/usr/bin/env python3
"""
Fix upload functionality for the new enterprise system
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text
import uuid
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from app.core.config import settings

def fix_upload_route():
    """Create a simple upload route that works with the new system"""
    
    # Create the simplified upload route
    upload_route = '''
@router.post("/upload", response_model=dict)
async def upload_training_file(
    file: UploadFile = File(...),
    category: str = Form("qa"),
    folder: str = Form("streamworks-f1"),
    db: AsyncSession = Depends(get_db)
):
    """Upload a single training file to the new enterprise system"""
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension. Allowed: {ALLOWED_EXTENSIONS}"
            )
        
        # Read file content
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Get category and folder IDs
        category_result = await db.execute(
            text("SELECT id FROM document_categories WHERE slug = :slug"),
            {"slug": category}
        )
        category_id = category_result.scalar()
        
        if not category_id:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        folder_id = None
        if folder:
            folder_result = await db.execute(
                text("SELECT id FROM document_folders WHERE slug = :slug AND category_id = :category_id"),
                {"slug": folder, "category_id": category_id}
            )
            folder_id = folder_result.scalar()
        
        # Create storage path
        storage_path = f"data/documents/{category}"
        if folder:
            storage_path += f"/{folder}"
        storage_path += f"/{file.filename}"
        
        # Save file to disk
        file_path = Path(storage_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Save to database
        file_id = str(uuid.uuid4())
        await db.execute(
            text("""
                INSERT INTO training_files_v2 (
                    id, category_id, folder_id, original_filename, 
                    storage_path, file_hash, file_size, file_type,
                    processing_status, created_at
                ) VALUES (
                    :id, :category_id, :folder_id, :filename,
                    :storage_path, :file_hash, :file_size, :file_type,
                    'pending', :created_at
                )
            """),
            {
                "id": file_id,
                "category_id": category_id,
                "folder_id": folder_id,
                "filename": file.filename,
                "storage_path": str(file_path),
                "file_hash": hashlib.sha256(file_content).hexdigest(),
                "file_size": len(file_content),
                "file_type": file_extension,
                "created_at": datetime.now()
            }
        )
        
        await db.commit()
        
        return {
            "message": "File uploaded successfully",
            "id": file_id,
            "filename": file.filename,
            "category": category,
            "folder": folder,
            "size": len(file_content),
            "status": "pending"
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"❌ Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
'''
    
    print("✅ Upload route code generated. Manual integration needed.")
    print(upload_route)

if __name__ == "__main__":
    fix_upload_route()