from fastapi import APIRouter, HTTPException, Query
from typing import List
from pydantic import BaseModel
from services.db import db

router = APIRouter(prefix="/api/options", tags=["Options"])

class Option(BaseModel):
    label: str
    value: str

@router.get("/{category}", response_model=List[Option])
async def get_options(category: str):
    """Get active options for a specific category"""
    if not db.client:
        raise HTTPException(status_code=503, detail="Database not available")
        
    options = db.get_dropdown_options(category)
    return [Option(label=o["label"], value=o["value"]) for o in options]
