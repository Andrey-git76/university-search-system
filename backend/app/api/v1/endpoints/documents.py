from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pathlib import Path
import uuid
import logging
from app.core.config import settings
from app.services.parser import DocumentParser
from app.services.indexer import IndexManager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and index a document.
    
    - Supports PDF and DOCX formats
    - Maximum file size: 20 MB
    - Returns document ID and indexing status
    """
    # Validate file extension
    allowed_extensions = {'.pdf', '.docx'}
    ext = Path(file.filename).suffix.lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB} MB"
        )
    
    # Generate unique document ID
    document_id = str(uuid.uuid4())
    logger.info(f"Processing: {file.filename} (ID: {document_id})")
    
    try:
        # Parse document
        if ext == '.pdf':
            pages = await DocumentParser.parse_pdf(content)
        else:  # .docx
            pages = await DocumentParser.parse_docx(content)
        
        if not pages:
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document"
            )
        
        # Split into chunks
        chunks = DocumentParser.chunk_pages(
            pages,
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP
        )
        
        # Index in Elasticsearch
        indexer = IndexManager()
        await indexer.index_chunks(
            document_id=document_id,
            file_name=file.filename,
            chunks=chunks
        )
        
        # Clear cache for this document
        from app.services.cache import CacheService
        cache = CacheService()
        cache.clear()
        
        return {
            "document_id": document_id,
            "file_name": file.filename,
            "chunks_count": len(chunks),
            "status": "indexed",
            "message": "Document uploaded and indexed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("")
async def list_documents(
    limit: int = Query(50, ge=1, le=100, description="Max documents to return"),
    offset: int = Query(0, ge=0, description="Number to skip")
):
    """
    Get list of all uploaded documents with their metadata.
    """
    indexer = IndexManager()
    documents = await indexer.list_documents(limit, offset)
    return {
        "documents": documents,
        "count": len(documents),
        "total": await indexer.get_total_documents()
    }


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks from Elasticsearch.
    """
    indexer = IndexManager()
    deleted = await indexer.delete_document(document_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )
    
    # Clear cache
    from app.services.cache import CacheService
    cache = CacheService()
    cache.clear()
    
    return {
        "document_id": document_id,
        "status": "deleted",
        "message": f"Document {document_id} deleted successfully"
    }