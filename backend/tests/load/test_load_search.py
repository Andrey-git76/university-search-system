"""Pytest-обёртка для QA-04 (требует запущенный backend с проиндексированными документами)."""

import pytest

from tests.helpers.stack import is_api_available
from tests.load.run_load_test import run_load_test

pytestmark = pytest.mark.load


@pytest.fixture(scope="module")
def require_load_stack():
    if not is_api_available():
        pytest.skip("Load: запустите backend, Elasticsearch и Redis")


def test_search_load_50_users(require_load_stack):
    exit_code = run_load_test(users=50, spawn_rate=50, duration="15s")
    assert exit_code == 0
