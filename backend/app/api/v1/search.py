"""
Intelligent & Smart Search API Endpoints for StreamWorks-KI
Provides both legacy intelligent search and new smart search capabilities
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging

from app.services.smart_search import smart_search_service, SearchFilter, SearchStrategy

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


# 🚀 NEW SMART SEARCH API ENDPOINTS (Phase 2)

class SmartSearchRequest(BaseModel):
    """Smart search request model"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    include_analysis: bool = Field(default=True, description="Include query analysis in response")

class SearchFilterRequest(BaseModel):
    """Search filter request model"""
    document_types: Optional[List[str]] = Field(default=None, description="Filter by document types")
    file_formats: Optional[List[str]] = Field(default=None, description="Filter by file formats")
    chunk_types: Optional[List[str]] = Field(default=None, description="Filter by chunk types")
    source_categories: Optional[List[str]] = Field(default=None, description="Filter by source categories")
    processing_methods: Optional[List[str]] = Field(default=None, description="Filter by processing methods")
    complexity_min: Optional[int] = Field(default=None, ge=1, le=10, description="Minimum complexity")
    complexity_max: Optional[int] = Field(default=None, ge=1, le=10, description="Maximum complexity")

class AdvancedSearchRequest(BaseModel):
    """Advanced search with custom filters"""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20)
    filters: Optional[SearchFilterRequest] = Field(default=None)
    include_analysis: bool = Field(default=True)

class QueryAnalysisRequest(BaseModel):
    """Query analysis only request"""
    query: str = Field(..., min_length=1, max_length=1000)


@router.post("/smart")
async def smart_search(request: SmartSearchRequest):
    """
    🧠 Intelligent search with automatic query classification and strategy selection
    """
    logger.info(f"🔍 Smart search request: '{request.query[:50]}{'...' if len(request.query) > 50 else ''}'")
    
    try:
        # Perform smart search
        result = await smart_search_service.smart_search(
            query=request.query,
            top_k=request.top_k,
            include_analysis=request.include_analysis
        )
        
        logger.info(f"✅ Smart search completed: {result['total_results']} results in {result['response_time_ms']}ms")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Smart search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Smart search failed: {str(e)}")


@router.post("/advanced")
async def advanced_search(request: AdvancedSearchRequest):
    """
    🎯 Advanced search with custom filters and explicit control
    """
    logger.info(f"🎯 Advanced search request: '{request.query[:50]}{'...' if len(request.query) > 50 else ''}'")
    
    try:
        # Convert request filters to SearchFilter
        custom_filter = None
        if request.filters:
            complexity_range = None
            if request.filters.complexity_min is not None or request.filters.complexity_max is not None:
                min_val = request.filters.complexity_min or 1
                max_val = request.filters.complexity_max or 10
                complexity_range = (min_val, max_val)
            
            custom_filter = SearchFilter(
                document_types=request.filters.document_types,
                file_formats=request.filters.file_formats,
                chunk_types=request.filters.chunk_types,
                source_categories=request.filters.source_categories,
                processing_methods=request.filters.processing_methods,
                complexity_range=complexity_range
            )
        
        # Perform advanced search
        result = await smart_search_service.smart_search(
            query=request.query,
            top_k=request.top_k,
            custom_filter=custom_filter,
            include_analysis=request.include_analysis
        )
        
        logger.info(f"✅ Advanced search completed: {result['total_results']} results")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Advanced search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Advanced search failed: {str(e)}")


@router.post("/analyze-query")
async def analyze_query(request: QueryAnalysisRequest):
    """
    🧠 Analyze a query to understand intent, complexity, and suggested search strategy
    """
    logger.info(f"🧠 Query analysis request: '{request.query[:50]}{'...' if len(request.query) > 50 else ''}'")
    
    try:
        # Perform query classification
        analysis = smart_search_service.query_classifier.classify_query(request.query)
        
        # Add timestamp
        analysis['analysis_timestamp'] = datetime.utcnow().isoformat()
        
        logger.info(f"✅ Query analysis completed: intent={analysis['primary_intent']}, "
                   f"complexity={analysis['complexity_level']}")
        
        return {
            "query": request.query,
            "analysis": analysis,
            "recommendations": {
                "optimal_strategy": analysis['search_strategy'].value,
                "suggested_document_types": analysis['preferred_doc_types'],
                "enhancement_tips": analysis['enhancement_suggestions']
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Query analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query analysis failed: {str(e)}")


@router.get("/strategies")
async def get_search_strategies():
    """
    📋 Get available search strategies and their descriptions
    """
    strategies = {
        "semantic_only": {
            "name": "Semantic Only",
            "description": "Pure vector similarity search using embeddings",
            "best_for": ["Simple queries", "General information requests"],
            "performance": "Fast"
        },
        "filtered": {
            "name": "Filtered Search",
            "description": "Metadata-based filtering with semantic search",
            "best_for": ["Specific document types", "Technical queries"],
            "performance": "Medium"
        },
        "hybrid": {
            "name": "Hybrid Search",
            "description": "Combination of semantic, keyword, and filtered search",
            "best_for": ["Complex queries", "Multi-faceted information needs"],
            "performance": "Comprehensive"
        },
        "contextual": {
            "name": "Contextual Search",
            "description": "Query expansion with domain-specific context",
            "best_for": ["Troubleshooting", "Ambiguous queries"],
            "performance": "Intelligent"
        },
        "concept_based": {
            "name": "Concept-Based Search",
            "description": "Focus on domain-specific concepts and terminology",
            "best_for": ["API usage", "Technical documentation"],
            "performance": "Specialized"
        }
    }
    
    return {
        "available_strategies": strategies,
        "default_strategy": "semantic_only",
        "auto_selection": "Smart search automatically selects optimal strategy based on query analysis"
    }


@router.get("/filters/options")
async def get_filter_options():
    """
    🔧 Get available filter options for advanced search
    """
    try:
        # Get options from the multi-format processor and existing data
        from app.services.multi_format_processor import multi_format_processor
        
        # Get current options from the system
        supported_formats = multi_format_processor.get_supported_formats()
        supported_categories = multi_format_processor.get_supported_categories()
        
        # Chunk types (from our chunking strategies)
        chunk_types = [
            "default_recursive", "function_based", "header_based", "element_based",
            "structure_based", "row_based", "section_based", "xml_element",
            "json_object_key", "csv_rows", "html_section", "markdown_section"
        ]
        
        # Processing methods
        processing_methods = [
            "multi_format_processor", "default_recursive", "function_based",
            "structure_based", "element_based", "row_based", "header_based"
        ]
        
        # Source categories
        source_categories = ["Testdaten", "StreamWorks Hilfe", "SharePoint"]
        
        return {
            "document_types": supported_categories,
            "file_formats": supported_formats,
            "chunk_types": chunk_types,
            "processing_methods": processing_methods,
            "source_categories": source_categories,
            "complexity_range": {
                "min": 1,
                "max": 10,
                "levels": {
                    "basic": "1-3",
                    "intermediate": "3-7", 
                    "advanced": "6-10"
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get filter options: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get filter options: {str(e)}")


@router.get("/smart/statistics")
async def get_smart_search_statistics():
    """
    📊 Get comprehensive smart search performance statistics
    """
    try:
        # Get smart search statistics
        smart_stats = smart_search_service.get_search_statistics()
        
        return {
            "smart_search": smart_stats,
            "system_info": {
                "total_search_endpoints": 8,
                "available_strategies": len(SearchStrategy),
                "smart_search_enabled": True,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get smart search statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/smart/health")
async def smart_search_health_check():
    """
    🏥 Health check for smart search system
    """
    try:
        # Test basic functionality
        test_query = "StreamWorks XML configuration"
        
        # Quick classification test
        analysis = smart_search_service.query_classifier.classify_query(test_query)
        
        return {
            "status": "healthy",
            "smart_search_available": True,
            "query_classifier_working": bool(analysis),
            "total_searches_performed": smart_search_service.search_stats['total_searches'],
            "average_response_time_ms": round(smart_search_service.search_stats['average_response_time'] * 1000, 2),
            "available_strategies": len(SearchStrategy),
            "features": {
                "query_classification": True,
                "intent_detection": True,
                "complexity_assessment": True,
                "automatic_strategy_selection": True,
                "advanced_filtering": True,
                "performance_tracking": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Smart search health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }