from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
MAX_FILE_SIZE_MB = 20


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


def make_oversized_pdf_bytes(size_mb: int = MAX_FILE_SIZE_MB + 1) -> bytes:
    """Сгенерировать PDF-подобный файл больше лимита загрузки (без файла в репозитории)."""
    payload_size = size_mb * 1024 * 1024 - len(b"%PDF-1.4\n")
    return b"%PDF-1.4\n" + b"0" * payload_size


def read_fixture(name: str) -> bytes:
    path = FIXTURES_DIR / name
    if not path.exists():
        pytest.skip(f"Фикстура не найдена: {path}")
    return path.read_bytes()


@pytest.fixture
def valid_pdf_bytes() -> bytes:
    return read_fixture("valid.pdf")


@pytest.fixture
def valid_docx_bytes() -> bytes:
    return read_fixture("valid.docx")


@pytest.fixture
def empty_docx_bytes(fixtures_dir) -> bytes:
    path = fixtures_dir / "empty.docx"
    if not path.exists():
        pytest.skip("Фикстура empty.docx не найдена")
    return path.read_bytes()


@pytest.fixture
def rare_fonts_pdf_bytes() -> bytes:
    """QA-03: PDF с нестандартными шрифтами и спецсимволами."""
    return read_fixture("rare_fonts.pdf")


@pytest.fixture
def rare_fonts_docx_bytes() -> bytes:
    """QA-03: DOCX с нестандартными шрифтами и спецсимволами."""
    return read_fixture("rare_fonts.docx")


@pytest.fixture
def oversized_pdf_bytes() -> bytes:
    """Файл > 20 МБ для проверки лимита размера (валидация до парсинга)."""
    return make_oversized_pdf_bytes()


@pytest.fixture
def mock_redis():
    redis = MagicMock()
    redis.ping.return_value = True
    redis.get.return_value = None
    redis.setex.return_value = True
    redis.scan_iter.return_value = iter([])
    redis.flushdb.return_value = True
    redis.delete.return_value = 1
    return redis


@pytest.fixture
def mock_async_es():
    es = AsyncMock()
    es.indices.exists = AsyncMock(return_value=False)
    es.indices.create = AsyncMock()
    es.indices.delete = AsyncMock()
    es.indices.refresh = AsyncMock()
    es.index = AsyncMock()
    es.search = AsyncMock()
    es.delete_by_query = AsyncMock(return_value={"deleted": 1})
    return es


@pytest.fixture
def sample_es_search_response():
    return {
        "hits": {
            "total": {"value": 2},
            "hits": [
                {
                    "_score": 5.42,
                    "_source": {
                        "chunk_id": "chunk-1",
                        "file_name": "valid.pdf",
                        "page": 1,
                        "text": "Москва — столица Российской Федерации",
                    },
                    "highlight": {
                        "text": ["<mark>Москва</mark> — столица Российской Федерации"]
                    },
                },
                {
                    "_score": 3.1,
                    "_source": {
                        "chunk_id": "chunk-2",
                        "file_name": "valid.docx",
                        "page": 1,
                        "text": "МГУ имени М.В. Ломоносова",
                    },
                    "highlight": {},
                },
            ],
        }
    }


@pytest.fixture
def sample_es_list_response():
    return {
        "aggregations": {
            "unique_documents": {
                "buckets": [
                    {
                        "key": "doc-uuid-1",
                        "doc_count": 5,
                        "latest_hit": {
                            "hits": {
                                "hits": [
                                    {
                                        "_source": {
                                            "file_name": "valid.pdf",
                                            "created_at": "2025-01-15T10:00:00",
                                        }
                                    }
                                ]
                            }
                        },
                    }
                ]
            }
        }
    }


@pytest.fixture
def api_client(mock_async_es, mock_redis):
    """
    TestClient без реального Elasticsearch и Redis.
    Lifespan патчится, чтобы не создавать индекс при старте.
    """
    with patch("app.services.indexer.AsyncElasticsearch", return_value=mock_async_es), \
         patch("app.services.searcher.AsyncElasticsearch", return_value=mock_async_es), \
         patch("app.services.cache.redis.Redis.from_url", return_value=mock_redis), \
         patch("app.main.IndexManager") as MockIndexManager:

        mock_manager = AsyncMock()
        mock_manager.create_index = AsyncMock()
        MockIndexManager.return_value = mock_manager

        from fastapi.testclient import TestClient
        from app.main import app

        with TestClient(app) as client:
            yield client