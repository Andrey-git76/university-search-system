import pytest
from unittest.mock import AsyncMock, patch

from app.services.searcher import Searcher


@pytest.mark.asyncio
class TestSearcher:
    async def test_search_returns_results_and_total(self, mock_async_es, sample_es_search_response):
        mock_async_es.search = AsyncMock(return_value=sample_es_search_response)

        with patch("app.services.searcher.AsyncElasticsearch", return_value=mock_async_es):
            searcher = Searcher()
            results, total = await searcher.search("Москва", size=10, offset=0)

        assert total == 2
        assert len(results) == 2
        assert results[0]["chunk_id"] == "chunk-1"
        assert results[0]["score"] == 5.42
        assert "<mark>" in results[0]["highlight"]

    async def test_search_empty_on_es_error(self, mock_async_es):
        mock_async_es.search = AsyncMock(side_effect=Exception("connection refused"))

        with patch("app.services.searcher.AsyncElasticsearch", return_value=mock_async_es):
            searcher = Searcher()
            results, total = await searcher.search("запрос")

        assert results == []
        assert total == 0

    async def test_search_passes_pagination_params(self, mock_async_es, sample_es_search_response):
        mock_async_es.search = AsyncMock(return_value=sample_es_search_response)

        with patch("app.services.searcher.AsyncElasticsearch", return_value=mock_async_es):
            searcher = Searcher()
            await searcher.search("МГУ", size=5, offset=10)

        call_body = mock_async_es.search.call_args.kwargs["body"]
        assert call_body["from"] == 10
        assert call_body["size"] == 5
        assert call_body["query"]["multi_match"]["query"] == "МГУ"