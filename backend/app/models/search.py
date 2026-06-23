from pydantic import BaseModel
from typing import Optional, List


class SearchResult(BaseModel):
    chunk_id: str
    file_name: str
    page: int
    text: str
    score: float
    highlight: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    count: int
    message: Optional[str] = None