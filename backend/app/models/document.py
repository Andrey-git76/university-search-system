from pydantic import BaseModel
from typing import Optional


class DocumentUploadResponse(BaseModel):
    document_id: str
    file_name: str
    chunks_count: int
    status: str
    message: Optional[str] = None


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    file_name: str
    page: int
    text: str
    created_at: str