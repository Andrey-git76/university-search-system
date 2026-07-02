"""QA-05: Модуль автоматической оценки точности полнотекстового поиска (Precision@3)."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

from tests.helpers.stack import API_URL, is_api_available


FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
EVAL_FIXTURES_DIR = FIXTURES_DIR / "for_evaluation"

GROUND_TRUTH_PATH = Path(__file__).resolve().parent / "ground_truth.json"
REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"

SEED_DOCUMENTS = (
    "valid.pdf", 
    "rare_fonts.pdf", 
    "technology.pdf", 
    "history.pdf", 
    "universities.pdf", 
    "nature.pdf"
)
TOP_K = 3


@dataclass
class QueryEvaluation:
    """Класс для фиксации результатов обработки одного тестового запроса."""
    number: int
    query: str
    expected_file: str
    top_files: list[str]
    hit: bool


def _upload_fixture(client: httpx.Client, file_name: str) -> None:
    """Отправляет тестовый PDF-документ на бэкенд."""
    if file_name in ("valid.pdf", "rare_fonts.pdf"):
        file_path = FIXTURES_DIR / file_name
    else:
        file_path = EVAL_FIXTURES_DIR / file_name

    with file_path.open("rb") as handle:
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": (file_name, handle, "application/pdf")},
            timeout=60.0,
        )
    response.raise_for_status()


def seed_documents(client: httpx.Client) -> None:
    """Загружает все файлы из пула в систему для построения индекса поиска."""
    for file_name in SEED_DOCUMENTS:
        _upload_fixture(client, file_name)
        time.sleep(1)  # Пауза для стабильной индексации документов внутри Elasticsearch


def load_ground_truth() -> list[dict]:
    """Считывает эталонные запросы и имена целевых файлов из JSON-конфигурации."""
    return json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))


def evaluate_query(client: httpx.Client, number: int, item: dict) -> QueryEvaluation:
    """Выполняет запрос к API поиска и выбирает Топ-3 уникальных документа."""
    response = client.get(
        "/api/v1/search",
        params={"q": item["query"], "limit": 15, "use_cache": False},
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()

    results_list = payload if isinstance(payload, list) else payload.get("results", [])
    
    # Алгоритм дедупликации чанков: формируем Топ-3 исключительно из уникальных файлов
    top_files = []
    for result in results_list:
        file_name = result["file_name"]
        if file_name not in top_files:
            top_files.append(file_name)
        if len(top_files) == TOP_K:
            break

    expected = item["expected_file"]
    hit = expected in top_files

    return QueryEvaluation(number, item["query"], expected, top_files, hit)


def build_markdown_report(results: list[QueryEvaluation], started_at: datetime) -> str:
    """Генерирует отчет в формате Markdown по результатам тестов."""
    hits = sum(1 for item in results if item.hit)
    precision = hits / len(results) if results else 0.0
    
    lines = [
        "# Отчёт по метрике Precision@3 (Контроль качества поиска QA-05)",
        "",
        f"**Время запуска:** {started_at.strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Количество тестов:** {len(results)}",
        f"**Итоговая точность Precision@3:** {precision:.0%} ({hits}/{len(results)})",
        "",
        "| № | Поисковый запрос | Ожидаемый документ | Топ-3 (Уникальные файлы) | Попадание |",
        "| ---: | :--- | :--- | :--- | :---: |",
    ]

    for item in results:
        top_preview = ", ".join(item.top_files) if item.top_files else "—"
        lines.append(
            f"| {item.number} | {item.query} | {item.expected_file} | {top_preview} | "
            f"{'Да' if item.hit else 'Нет'} |"
        )

    return "\n".join(lines) + "\n"


def run_precision_evaluation(api_url: str | None = None, seed: bool = True) -> tuple[list[QueryEvaluation], Path]:
    """Запускает полный цикл тестирования точности поиска."""
    api_url = api_url or API_URL
    if not is_api_available():
        raise RuntimeError(f"Сбой: Сервер API недоступен по адресу {api_url}/health")

    started_at = datetime.now(timezone.utc)
    ground_truth = load_ground_truth()

    with httpx.Client(base_url=api_url, timeout=60.0) as client:
        if seed:
            seed_documents(client)
            time.sleep(2)

        print("[ЛОГ] Выполнение эталонных поисковых запросов...")
        results = [
            evaluate_query(client, index, item)
            for index, item in enumerate(ground_truth, start=1)
        ]

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "precision_at_3.md"
    report_path.write_text(build_markdown_report(results, started_at), encoding="utf-8")
    return results, report_path