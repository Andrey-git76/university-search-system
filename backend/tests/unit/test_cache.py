from unittest.mock import patch

from app.services.cache import CacheService


class TestCacheService:
    def test_get_returns_none_when_redis_unavailable(self):
        with patch("app.services.cache.redis.Redis.from_url", side_effect=ConnectionError):
            cache = CacheService()
            assert cache.get("Москва", 10, 0) is None

    def test_set_and_get_roundtrip(self, mock_redis):
        stored = {}

        def fake_setex(key, ttl, value):
            stored[key] = value

        def fake_get(key):
            return stored.get(key)

        mock_redis.setex.side_effect = fake_setex
        mock_redis.get.side_effect = fake_get

        with patch("app.services.cache.redis.Redis.from_url", return_value=mock_redis):
            cache = CacheService()
            payload = {"query": "Кремль", "results": [], "total": 0}
            cache.set("Кремль", 10, 0, payload)

            assert cache.get("Кремль", 10, 0) == payload

    def test_cache_key_is_deterministic(self, mock_redis):
        with patch("app.services.cache.redis.Redis.from_url", return_value=mock_redis):
            cache = CacheService()
            key1 = cache._get_cache_key("Москва", 10, 0)
            key2 = cache._get_cache_key("Москва", 10, 0)
            key3 = cache._get_cache_key("Москва", 10, 5)

            assert key1 == key2
            assert key1 != key3
            assert key1.startswith("search:")

    def test_clear_all_calls_flushdb(self, mock_redis):
        with patch("app.services.cache.redis.Redis.from_url", return_value=mock_redis):
            cache = CacheService()
            cache.clear()
            mock_redis.flushdb.assert_called_once()