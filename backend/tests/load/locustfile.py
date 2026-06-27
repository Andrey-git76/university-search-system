"""QA-04: нагрузочное тестирование поиска (50 одновременных пользователей)."""

from __future__ import annotations

import random

from locust import HttpUser, between, task

SEARCH_QUERIES = [
    "Москва",
    "Кремль",
    "МГУ",
    "Ломоносова",
    "ЮНЕСКО",
    "университет",
    "столица",
    "географическое",
    "образовательный",
    "достопримечательности",
]


class SearchUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def search_documents(self):
        query = random.choice(SEARCH_QUERIES)
        self.client.get(
            "/api/v1/search",
            params={"q": query, "limit": 10, "use_cache": False},
            name="/api/v1/search",
        )
