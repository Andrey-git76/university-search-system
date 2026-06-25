import pytest
from unittest.mock import AsyncMock, patch

from app.services.indexer import IndexManager


@pytest.mark.asyncio
class TestIndexManager:
    async def test_create_index_when_not_exists(self, mock_async_es):
        mock_async_es.indices.exists = AsyncMock(return_value=False)

        with patch("app.services.indexer.AsyncElasticsearch", return_value=mock_async_es):
            manager = IndexManager()
            await manager.create_index()

        mock_async_es.indices.create.assert_called_once()
        mock_async_es.indices.delete.assert_not_called()

    async def test_create_index_deletes_existing(self, mock_async_es):
        mock_async_es.indices.exists = AsyncMock(return_value=True)

        with patch("app.services.indexer.AsyncElasticsearch", return_value=mock_async_es):
            manager = IndexManager()
            await manager.create_index()

        mock_async_es.indices.delete.assert_called_once()
        mock_async_es.indices.create.assert_called_once()

    async def test_index_chunks_indexes_all(self, mock_async_es):
        chunks = [
            {"chunk_id": "c1", "page": 1, "text": "Москва"},
            {"chunk_id": "c2", "page": 2, "text": "Кремль"},
        ]

        with patch("app.services.indexer.AsyncElasticsearch", return_value=mock_async_es):
            manager = IndexManager()
            await manager.index_chunks("doc-1", "valid.pdf", chunks)

        assert mock_async_es.index.call_count == 2
        mock_async_es.indices.refresh.assert_called_once()

    async def test_list_documents_parses_aggregation(self, mock_async_es, sample_es_list_response):
        mock_async_es.search = AsyncMock(return_value=sample_es_list_response)

        with patch("app.services.indexer.AsyncElasticsearch", return_value=mock_async_es):
            manager = IndexManager()
            docs = await manager.list_documents()

        assert len(docs) == 1
        assert docs[0]["document_id"] == "doc-uuid-1"
        assert docs[0]["file_name"] == "valid.pdf"
        assert docs[0]["chunks_count"] == 5

    async def test_get_total_documents(self, mock_async_es):
        mock_async_es.search = AsyncMock(
            return_value={"aggregations": {"unique_documents": {"value": 3}}}
        )

        with patch("app.services.indexer.AsyncElasticsearch", return_value=mock_async_es):
            manager = IndexManager()
            total = await manager.get_total_documents()

        assert total == 3

    async def test_delete_document_returns_true_on_success(self, mock_async_es):
        with patch("app.services.indexer.AsyncElasticsearch", return_value=mock_async_es):
            manager = IndexManager()
            result = await manager.delete_document("doc-1")

        assert result is True

    async def test_delete_document_returns_false_on_error(self, mock_async_es):
        mock_async_es.delete_by_query = AsyncMock(side_effect=Exception("ES error"))

        with patch("app.services.indexer.AsyncElasticsearch", return_value=mock_async_es):
            manager = IndexManager()
            result = await manager.delete_document("doc-1")

        assert result is False