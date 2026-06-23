from elasticsearch import AsyncElasticsearch
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Searcher:
    
    def __init__(self):
        self.es = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
        self.index = settings.ELASTICSEARCH_INDEX
    
    async def search(self, query: str, size: int = 10, offset: int = 0):
        """
        Search for documents matching the query with pagination.
        
        Args:
            query: Search query string
            size: Number of results per page
            offset: Number of results to skip (for pagination)
        
        Returns:
            Tuple of (results list, total count)
        """
        
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["text^3", "file_name^2"],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                    "operator": "or"
                }
            },
            "from": offset,
            "size": size,
            "highlight": {
                "fields": {
                    "text": {
                        "fragment_size": 200,
                        "number_of_fragments": 3,
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"]
                    }
                }
            }
        }
        
        try:
            response = await self.es.search(index=self.index, body=body)
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return [], 0
        
        total = response["hits"]["total"]["value"]
        
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            highlight = hit.get("highlight", {})
            
            highlights = highlight.get("text", [])
            
            results.append({
                "chunk_id": source.get("chunk_id"),
                "file_name": source.get("file_name"),
                "page": source.get("page"),
                "text": source.get("text"),
                "score": round(hit["_score"], 2),
                "highlight": " ... ".join(highlights) if highlights else None
            })
        
        logger.info(f"Found {total} results for: '{query}' (showing {len(results)})")
        return results, total