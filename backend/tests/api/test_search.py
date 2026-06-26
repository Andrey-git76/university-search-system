from unittest.mock import AsyncMock, patch


class TestSearchEndpoint:
    def test_search_requires_query(self, api_client):
        response = api_client.get("/api/v1/search")
        assert response.status_code == 422

    @patch("app.api.v1.endpoints.search.Searcher")
    def test_search_returns_results(self, MockSearcher, api_client):
        mock_instance = AsyncMock()
        mock_instance.search = AsyncMock(
            return_value=(
                [
                    {
                        "chunk_id": "c1",
                        "file_name": "valid.pdf",
                        "page": 1,
                        "text": "Москва — столица",
                        "score": 5.0,
                        "highlight": "<mark>Москва</mark> — столица",
                    }
                ],
                1,
            )
        )
        MockSearcher.return_value = mock_instance

        response = api_client.get(
            "/api/v1/search",
            params={"q": "Москва", "use_cache": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Москва"
        assert data["total"] == 1
        assert data["from_cache"] is False
        assert data["results"][0]["file_name"] == "valid.pdf"

    @patch("app.api.v1.endpoints.search.cache")
    def test_search_cache_hit(self, mock_cache, api_client):
        cached_payload = {
            "query": "Кремль",
            "results": [],
            "count": 0,
            "total": 0,
            "page": 1,
            "total_pages": 0,
        }
        mock_cache.get.return_value = cached_payload.copy()

        response = api_client.get("/api/v1/search", params={"q": "Кремль"})

        assert response.status_code == 200
        assert response.json()["from_cache"] is True

    @patch("app.api.v1.endpoints.search.Searcher")
    def test_search_empty_results_message(self, MockSearcher, api_client):
        mock_instance = AsyncMock()
        mock_instance.search = AsyncMock(return_value=([], 0))
        MockSearcher.return_value = mock_instance

        response = api_client.get(
            "/api/v1/search",
            params={"q": "xyz123nonexistent", "use_cache": False},
        )

        data = response.json()
        assert data["total"] == 0
        assert data["message"] == (
            "По вашему запросу ничего не найдено. Попробуйте изменить формулировку"
        )

    @patch("app.api.v1.endpoints.search.Searcher")
    def test_search_pagination_fields(self, MockSearcher, api_client):
        mock_instance = AsyncMock()
        mock_instance.search = AsyncMock(return_value=([], 25))
        MockSearcher.return_value = mock_instance

        response = api_client.get(
            "/api/v1/search",
            params={"q": "университет", "limit": 10, "offset": 10, "use_cache": False},
        )

        data = response.json()
        assert data["page"] == 2
        assert data["total_pages"] == 3