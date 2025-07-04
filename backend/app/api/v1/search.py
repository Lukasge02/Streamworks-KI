"""
Intelligent Search API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchSuggestionRequest(BaseModel):
    partial_query: str

class SearchSuggestionsResponse(BaseModel):
    suggestions: List[str]
    count: int

class QueryExpansionRequest(BaseModel):
    query: str

class QueryExpansionResponse(BaseModel):
    original_query: str
    expanded_query: str
    added_terms: List[str]

class QueryIntentRequest(BaseModel):
    query: str

class QueryIntentResponse(BaseModel):
    primary_intent: str
    confidence: float
    categories: List[str]
    suggested_refinements: List[str]
    detected_entities: List[str]

@router.post("/suggestions", response_model=SearchSuggestionsResponse)
async def get_search_suggestions(request: SearchSuggestionRequest):
    """Get intelligent search suggestions based on partial query"""
    
    try:
        from app.services.intelligent_search import intelligent_search
        
        suggestions = intelligent_search.get_search_suggestions(request.partial_query)
        
        return SearchSuggestionsResponse(
            suggestions=suggestions,
            count=len(suggestions)
        )
        
    except Exception as e:
        logger.error(f"❌ Search suggestions failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/expand", response_model=QueryExpansionResponse)
async def expand_query(request: QueryExpansionRequest):
    """Expand query with synonyms and contextual terms"""
    
    try:
        from app.services.intelligent_search import intelligent_search
        
        original_query = request.query
        expanded_query = intelligent_search.expand_query(original_query)
        
        # Extract added terms
        original_words = set(original_query.lower().split())
        expanded_words = set(expanded_query.lower().split())
        added_terms = list(expanded_words - original_words)
        
        return QueryExpansionResponse(
            original_query=original_query,
            expanded_query=expanded_query,
            added_terms=added_terms
        )
        
    except Exception as e:
        logger.error(f"❌ Query expansion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/intent", response_model=QueryIntentResponse)
async def analyze_query_intent(request: QueryIntentRequest):
    """Analyze intent behind search query"""
    
    try:
        from app.services.intelligent_search import intelligent_search
        
        intent_analysis = intelligent_search.analyze_query_intent(request.query)
        
        return QueryIntentResponse(**intent_analysis)
        
    except Exception as e:
        logger.error(f"❌ Intent analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/related/{term}")
async def get_related_terms(term: str):
    """Get related terms for a search term"""
    
    try:
        from app.services.intelligent_search import intelligent_search
        
        related_terms = intelligent_search.get_related_terms(term)
        
        return {
            "term": term,
            "related_terms": related_terms,
            "count": len(related_terms)
        }
        
    except Exception as e:
        logger.error(f"❌ Related terms lookup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def search_health_check():
    """Health check for intelligent search service"""
    
    try:
        from app.services.intelligent_search import intelligent_search
        
        # Test basic functionality
        test_query = "batch"
        expanded = intelligent_search.expand_query(test_query)
        suggestions = intelligent_search.get_search_suggestions("ba")
        
        return {
            "status": "healthy",
            "service": "intelligent_search",
            "features": {
                "query_expansion": True,
                "search_suggestions": True,
                "intent_analysis": True,
                "related_terms": True
            },
            "test_results": {
                "query_expansion_working": len(expanded) > len(test_query),
                "suggestions_working": len(suggestions) > 0
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Search health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "intelligent_search",
            "error": str(e)
        }