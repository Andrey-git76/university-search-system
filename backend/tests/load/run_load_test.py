"""Запуск нагрузочного теста и формирование отчёта QA-04."""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from tests.helpers.stack import API_URL, is_api_available

LOAD_DIR = Path(__file__).resolve().parent
REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"


def _read_locust_stats(stats_csv: Path) -> dict | None:
    if not stats_csv.exists():
        return None

    with stats_csv.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        if row.get("Name") == "Aggregated":
            return row
    return rows[-1] if rows else None


def _build_markdown_report(
    stats: dict,
    host: str,
    users: int,
    duration: str,
    started_at: datetime,
) -> str:
    avg_ms = float(stats.get("Average Response Time", 0))
    p95_ms = float(stats.get("95%", 0))
    p99_ms = float(stats.get("99%", 0))
    max_ms = float(stats.get("Max Response Time", 0))
    requests = int(float(stats.get("Request Count", 0)))
    failures = int(float(stats.get("Failure Count", 0)))
    rps = float(stats.get("Requests/s", 0))

    return f"""# Отчёт нагрузочного тестирования (QA-04)

**Дата:** {started_at.strftime("%Y-%m-%d %H:%M UTC")}  
**Стенд:** {host}  
**Профиль:** {users} одновременных пользователей, длительность {duration}

## Параметры сценария

- Эндпоинт: `GET /api/v1/search`
- Количество пользователей: **{users}**
- Сценарий: случайные поисковые запросы по индексированным документам

## Результаты

| Метрика | Значение |
| :--- | ---: |
| Всего запросов | {requests} |
| Ошибки | {failures} |
| Запросов/сек (RPS) | {rps:.2f} |
| Среднее время отклика, мс | {avg_ms:.2f} |
| p95, мс | {p95_ms:.2f} |
| p99, мс | {p99_ms:.2f} |
| Максимум, мс | {max_ms:.2f} |

## Вывод

{"Нагрузочный тест завершён без ошибок." if failures == 0 else f"Зафиксировано {failures} ошибок — проверьте логи backend и Elasticsearch."}
"""


def run_load_test(
    host: str | None = None,
    users: int = 50,
    spawn_rate: int = 50,
    duration: str = "30s",
) -> int:
    host = host or API_URL
    if not is_api_available():
        print(f"API недоступен: {host}/health", file=sys.stderr)
        return 1

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc)
    csv_prefix = REPORTS_DIR / "load"

    command = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        str(LOAD_DIR / "locustfile.py"),
        "--headless",
        "-u",
        str(users),
        "-r",
        str(spawn_rate),
        "-t",
        duration,
        "--host",
        host,
        "--csv",
        str(csv_prefix),
        "--html",
        str(REPORTS_DIR / "load_test.html"),
    ]

    print("Запуск Locust:", " ".join(command))
    result = subprocess.run(command, check=False)
    stats = _read_locust_stats(Path(f"{csv_prefix}_stats.csv"))
    if stats is None:
        print("Не удалось прочитать статистику Locust.", file=sys.stderr)
        return result.returncode or 1

    report = _build_markdown_report(stats, host, users, duration, started_at)
    report_path = REPORTS_DIR / "load_test_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Отчёт сохранён: {report_path}")
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="QA-04 load test runner")
    parser.add_argument("--host", default=os.getenv("QA_API_URL", API_URL))
    parser.add_argument("--users", type=int, default=50)
    parser.add_argument("--spawn-rate", type=int, default=50)
    parser.add_argument("--duration", default="30s")
    args = parser.parse_args()
    return run_load_test(args.host, args.users, args.spawn_rate, args.duration)


if __name__ == "__main__":
    raise SystemExit(main())
