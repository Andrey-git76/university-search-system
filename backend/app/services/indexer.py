from elasticsearch import AsyncElasticsearch
from datetime import datetime
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class IndexManager:
    
    def __init__(self):
        self.es = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
        self.index = settings.ELASTICSEARCH_INDEX
    
    async def create_index(self):
        """Create Elasticsearch index with Russian analyzer."""
        
        # Check if index exists
        exists = await self.es.indices.exists(index=self.index)
        
        if exists:
            logger.info(f"Deleting existing index: {self.index}")
            await self.es.indices.delete(index=self.index)
        
        # Create index with Russian analyzer
        mapping = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "russian_analyzer": {
                            "type": "russian",
                            "stopwords": "_russian_"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "document_id": {"type": "keyword"},
                    "chunk_id": {"type": "keyword"},
                    "file_name": {"type": "text"},
                    "page": {"type": "integer"},
                    "text": {
                        "type": "text",
                        "analyzer": "russian_analyzer",
                        "search_analyzer": "russian_analyzer"
                    },
                    "created_at": {"type": "date"}
                }
            }
        }
        
        try:
            await self.es.indices.create(index=self.index, body=mapping)
            logger.info(f"Index {self.index} created successfully")
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            raise
    
    async def index_chunks(self, document_id: str, file_name: str, chunks: list):
        """Index document chunks in Elasticsearch."""
        for chunk in chunks:
            doc = {
                "document_id": document_id,
                "chunk_id": chunk["chunk_id"],
                "file_name": file_name,
                "page": chunk["page"],
                "text": chunk["text"],
                "created_at": datetime.utcnow().isoformat()
            }
            
            await self.es.index(
                index=self.index,
                id=chunk["chunk_id"],
                document=doc
            )
        
        await self.es.indices.refresh(index=self.index)
        logger.info(f"Indexed {len(chunks)} chunks for {file_name}")
    
    async def list_documents(self, limit: int = 50, offset: int = 0):
        """Get list of unique documents from Elasticsearch."""
        body = {
            "size": 0,
            "from": offset,
            "aggs": {
                "unique_documents": {
                    "terms": {
                        "field": "document_id",
                        "size": limit,
                        "order": {"latest_created": "desc"}
                    },
                    "aggs": {
                        "latest_created": {
                            "max": {
                                "field": "created_at"
                            }
                        },
                        "latest_hit": {
                            "top_hits": {
                                "size": 1,
                                "sort": [{"created_at": {"order": "desc"}}]
                            }
                        }
                    }
                }
            }
        }
        
        try:
            response = await self.es.search(index=self.index, body=body)
        except Exception as e:
            logger.error(f"List documents error: {str(e)}")
            return []
        
        documents = []
        for bucket in response["aggregations"]["unique_documents"]["buckets"]:
            hit = bucket["latest_hit"]["hits"]["hits"][0]["_source"]
            documents.append({
                "document_id": bucket["key"],
                "file_name": hit.get("file_name"),
                "chunks_count": bucket["doc_count"],
                "created_at": hit.get("created_at")
            })
        
        return documents
    
    async def get_total_documents(self):
        """Get total number of unique documents."""
        body = {
            "size": 0,
            "aggs": {
                "unique_documents": {
                    "cardinality": {
                        "field": "document_id"
                    }
                }
            }
        }
        
        try:
            response = await self.es.search(index=self.index, body=body)
            return response["aggregations"]["unique_documents"]["value"]
        except Exception as e:
            logger.error(f"Get total documents error: {str(e)}")
            return 0
    
    async def delete_document(self, document_id: str):
        """Delete all chunks of a document."""
        try:
            response = await self.es.delete_by_query(
                index=self.index,
                body={
                    "query": {
                        "term": {"document_id": document_id}
                    }
                }
            )
            deleted_count = response.get("deleted", 0)
            await self.es.indices.refresh(index=self.index)
            logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"Delete document error: {str(e)}")
            return False