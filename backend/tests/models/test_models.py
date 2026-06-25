import pytest
from pydantic import ValidationError

from app.models.document import DocumentUploadResponse, DocumentChunk
from app.models.search import SearchResult, SearchResponse


class TestDocumentModels:
    def test_upload_response_valid(self):
        resp = DocumentUploadResponse(
            document_id="uuid-1",
            file_name="valid.pdf",
            chunks_count=10,
            status="indexed",
        )
        assert resp.status == "indexed"

    def test_document_chunk_requires_all_fields(self):
        with pytest.raises(ValidationError):
            DocumentChunk(chunk_id="c1", document_id="d1")


class TestSearchModels:
    def test_search_result_with_optional_highlight(self):
        result = SearchResult(
            chunk_id="c1",
            file_name="valid.pdf",
            page=1,
            text="Москва",
            score=4.5,
        )
        assert result.highlight is None

    def test_search_response_structure(self):
        resp = SearchResponse(query="МГУ", results=[], count=0)
        assert resp.message is None