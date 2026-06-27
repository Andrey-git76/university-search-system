# QA-тестирование — University Search System

Документация по требованиям QA из задания на учебную практику.

## Статус требований

| ID | Требование | Статус | Где реализовано |
| :--- | :--- | :--- | :--- |
| **QA-01** | Юнит-тесты backend (pytest), покрытие ≥ 50% | ✅ | `tests/unit/`, `tests/api/`, `pytest.ini` (`--cov-fail-under=50`) |
| **QA-02** | E2E-тесты (Playwright): загрузка → индексация → поиск | ✅ | `tests/e2e/` |
| **QA-03** | Набор тестовых документов | ✅ | `tests/fixtures/` (см. `fixtures/README.md`) |
| **QA-04** | Нагрузочные тесты, 50 пользователей, отчёт по времени отклика | ✅ | `tests/load/` |
| **QA-05** | Precision@3 для 10 эталонных запросов, таблица результатов | ✅ | `tests/evaluation/` |
| QA-06 | Руководство пользователя | — | Не входит в текущую задачу |

## Быстрый старт

```bash
cd backend
pip install -r requirements.txt
playwright install chromium   # только для QA-02
```

### QA-01 — юнит- и API-тесты (по умолчанию)

```bash
pytest
```

Запускаются тесты из `tests/unit/` и `tests/api/` с проверкой покрытия `app/` ≥ 50%.

### QA-02 — E2E (Playwright)

1. Поднимите стек: Elasticsearch, Redis, backend, frontend.
2. Frontend в режиме разработки (прокси `/api` → backend):

```bash
# Терминал 1 — инфраструктура и backend
docker-compose up -d elasticsearch redis
cd backend && uvicorn app.main:app --reload

# Терминал 2 — frontend
cd frontend && npm install && npm run dev
```

3. Запуск E2E:

```bash
cd backend
pytest tests/e2e -m e2e --no-cov
```

Переменные окружения (опционально):

- `E2E_FRONTEND_URL` — URL фронтенда (по умолчанию `http://localhost:5173`)
- `E2E_API_URL` / `QA_API_URL` — URL backend (по умолчанию `http://localhost:8000`)

### QA-04 — нагрузочное тестирование

Перед запуском убедитесь, что backend доступен и в Elasticsearch есть проиндексированные документы.

```bash
cd backend
python -m tests.load.run_load_test --users 50 --spawn-rate 50 --duration 30s
```

Или через pytest:

```bash
pytest tests/load -m load --no-cov
```

Отчёты сохраняются в `tests/reports/`:

- `load_test_report.md` — сводка (среднее время, p95, p99, RPS)
- `load_test.html` — HTML-отчёт Locust

### QA-05 — Precision@3

```bash
cd backend
python -m tests.evaluation.evaluate_precision
```

Скрипт загружает эталонные документы (`valid.pdf`, `valid.docx`, `rare_fonts.pdf`), выполняет 10 запросов из `ground_truth.json` и формирует таблицу в `tests/reports/precision_at_3.md`.

Через pytest:

```bash
pytest tests/evaluation -m evaluation --no-cov
```

## Структура

```
tests/
├── api/              # API-тесты (моки ES/Redis)
├── unit/             # Юнит-тесты сервисов
├── fixtures/         # Тестовые документы (QA-03)
├── e2e/              # Playwright E2E (QA-02)
├── load/             # Locust (QA-04)
├── evaluation/       # Precision@3 (QA-05)
├── helpers/          # Проверка доступности стенда
└── reports/          # Генерируемые отчёты (gitignore)
```

## QA-03 — состав фикстур

| Категория | Файлы |
| :--- | :--- |
| Корректные PDF/DOCX | `valid.pdf`, `valid.docx` |
| Пустые | `empty.pdf`, `empty.docx` |
| Битое форматирование | `corrupted.pdf` |
| Нестандартные шрифты | `rare_fonts.pdf`, `rare_fonts.docx` |
| Неверный формат | `wrong_format.txt` |
| Превышение 20 МБ | генерируется в `conftest.py` |

## Все маркеры pytest

```bash
pytest -m e2e          # только E2E
pytest -m load         # только нагрузочные
pytest -m evaluation   # только Precision@3
pytest -m "not e2e and not load and not evaluation"  # только QA-01 (по умолчанию)
```
