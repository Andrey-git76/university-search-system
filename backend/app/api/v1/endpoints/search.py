from fastapi import APIRouter, Query
from app.services.searcher import Searcher
from app.services.cache import CacheService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
cache = CacheService()


@router.get("")
async def search_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip (for pagination)"),
    use_cache: bool = Query(True, description="Use Redis cache")
):
    """
    Search documents with pagination and caching.
    
    - Supports fuzzy search (auto-corrects typos)
    - Results are highlighted
    - Cached in Redis for 5 minutes
    """
    logger.info(f"Search: '{q}' (limit={limit}, offset={offset}, cache={use_cache})")
    
    # Check cache
    if use_cache:
        cached = cache.get(q, limit, offset)
        if cached:
            logger.info(f"Cache hit for '{q}'")
            cached["from_cache"] = True
            return cached
    
    # Execute search
    searcher = Searcher()
    results, total = await searcher.search(q, size=limit, offset=offset)
    
    response = {
        "query": q,
        "results": results,
        "count": len(results),
        "total": total,
        "page": offset // limit + 1 if limit > 0 else 1,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
        "from_cache": False
    }
    
    if not results:
        response["message"] = "По вашему запросу ничего не найдено. Попробуйте изменить формулировку"
    
    # Save to cache
    if use_cache and results:
        cache.set(q, limit, offset, response)
        logger.info(f"Cached results for '{q}'")
    
    return response