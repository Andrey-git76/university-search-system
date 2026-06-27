"""QA-05: оценка качества поиска (Precision@3)."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

from tests.helpers.stack import API_URL, is_api_available

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
GROUND_TRUTH_PATH = Path(__file__).resolve().parent / "ground_truth.json"
REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
SEED_DOCUMENTS = ("valid.pdf", "valid.docx", "rare_fonts.pdf")
TOP_K = 3


@dataclass
class QueryEvaluation:
    number: int
    query: str
    expected_file: str
    top_files: list[str]
    hit: bool


def _upload_fixture(client: httpx.Client, file_name: str) -> None:
    file_path = FIXTURES_DIR / file_name
    mime = (
        "application/pdf"
        if file_name.endswith(".pdf")
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    with file_path.open("rb") as handle:
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": (file_name, handle, mime)},
            timeout=120.0,
        )
    response.raise_for_status()


def seed_documents(client: httpx.Client) -> None:
    for file_name in SEED_DOCUMENTS:
        _upload_fixture(client, file_name)
        time.sleep(1)


def load_ground_truth() -> list[dict]:
    return json.loads(GROUND_TRUTH_PATH.read_text(encoding="utf-8"))


def evaluate_query(client: httpx.Client, number: int, item: dict) -> QueryEvaluation:
    response = client.get(
        "/api/v1/search",
        params={"q": item["query"], "limit": TOP_K, "use_cache": False},
        timeout=30.0,
    )
    response.raise_for_status()
    payload = response.json()
    top_files = [result["file_name"] for result in payload.get("results", [])[:TOP_K]]
    expected = item["expected_file"]
    hit = expected in top_files
    return QueryEvaluation(number, item["query"], expected, top_files, hit)


def build_markdown_report(results: list[QueryEvaluation], started_at: datetime) -> str:
    hits = sum(1 for item in results if item.hit)
    precision = hits / len(results) if results else 0.0
    lines = [
        "# Отчёт Precision@3 (QA-05)",
        "",
        f"**Дата:** {started_at.strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Эталонных запросов:** {len(results)}",
        f"**Итоговая Precision@3:** {precision:.0%} ({hits}/{len(results)})",
        "",
        "| № | Запрос | Ожидаемый документ | Топ-3 выдачи | Попадание |",
        "| ---: | :--- | :--- | :--- | :---: |",
    ]

    for item in results:
        top_preview = ", ".join(item.top_files) if item.top_files else "—"
        lines.append(
            f"| {item.number} | {item.query} | {item.expected_file} | {top_preview} | "
            f"{'Да' if item.hit else 'Нет'} |"
        )

    lines.extend(
        [
            "",
            "## Интерпретация",
            "",
            "Precision@3 = доля запросов, для которых ожидаемый документ присутствует "
            f"в первых {TOP_K} результатах поиска.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_precision_evaluation(api_url: str | None = None, seed: bool = True) -> tuple[list[QueryEvaluation], Path]:
    api_url = api_url or API_URL
    if not is_api_available():
        raise RuntimeError(f"API недоступен: {api_url}/health")

    started_at = datetime.now(timezone.utc)
    ground_truth = load_ground_truth()

    with httpx.Client(base_url=api_url, timeout=120.0) as client:
        if seed:
            seed_documents(client)
            time.sleep(2)

        results = [
            evaluate_query(client, index, item)
            for index, item in enumerate(ground_truth, start=1)
        ]

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / "precision_at_3.md"
    report_path.write_text(build_markdown_report(results, started_at), encoding="utf-8")
    return results, report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="QA-05 Precision@3 evaluation")
    parser.add_argument("--api-url", default=API_URL)
    parser.add_argument("--no-seed", action="store_true")
    args = parser.parse_args()

    try:
        results, report_path = run_precision_evaluation(args.api_url, seed=not args.no_seed)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    hits = sum(1 for item in results if item.hit)
    print(f"Precision@3: {hits}/{len(results)}")
    print(f"Отчёт сохранён: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
