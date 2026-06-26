# 📚 University Search System

**Интеллектуальная поисковая система по внутренней базе знаний университета.**

Этот проект разрабатывается в рамках учебной практики. Система позволяет загружать документы (PDF, DOCX), индексировать их с помощью Elasticsearch и выполнять полнотекстовый поиск с подсветкой совпадений.

---

## 💻 Роли в команде

| Роль | Ответственность |
| :--- | :--- |
| **Backend (BE)** | Разработка API, интеграция с Elasticsearch, бизнес-логика, работа с БД. |
| **Frontend (FE)** | Разработка интерфейса, верстка, клиент-серверное взаимодействие. |
| **DevOps (DO)** | Контейнеризация, CI/CD, мониторинг, управление окружением. |
| **QA** | Автоматизация тестирования, подготовка данных, контроль качества, документация. |

---

## 🛠 Технологический стек

| Компонент | Технология |
| :--- | :--- |
| **Бэкенд** | Python 3.10+, FastAPI, Uvicorn |
| **Поиск** | Elasticsearch 8.x |
| **Кеш** | Redis |
| **БД** | PostgreSQL |
| **Контейнеризация** | Docker, Docker Compose |
| **Документация API** | OpenAPI 3.0 (Swagger UI) |
| **Фронтенд** | React, TypeScript, Vite, Nginx |
| **Мониторинг** | Prometheus, Grafana |
| **CI/CD** | GitHub Actions |

---

## Быстрый старт (для всех членов команды)

Следуй этим шагам, чтобы развернуть проект локально.

### 1. Клонирование репозитория

```bash
git clone https://github.com/Andrey-git76/university-search-system.git
cd university-search-system
```

### 2. Запуск инфраструктуры (Docker)

Запускает все сервисы одной командой:

- **Бэкенд** (FastAPI)
- **Фронтенд** (React + Nginx)
- **Elasticsearch** (поисковый движок)
- **Redis** (кеширование)
- **PostgreSQL** (база данных)
- **Prometheus** (сбор метрик)
- **Grafana** (визуализация метрик)

```bash
docker-compose up -d

**Проверка:** Открой в браузере http://localhost:9200 — должен прийти JSON-ответ от Elasticsearch.

### 3. Настройка и запуск 

# Пересобрать и запустить после изменений
docker-compose up -d --build
# Посмотреть логи всех сервисов
docker-compose logs -f
# Посмотреть логи конкретного сервиса (например, бэкенда)
docker-compose logs -f backend
# Перезапустить все сервисы
docker-compose restart
# Остановить все контейнеры
docker-compose down
# Остановить и удалить данные (VOLUMES)
docker-compose down -v

### 4. Проверка работы

| Сервис | Адрес |
| :--- | :--- |
| **Фронтенд** | http://localhost:3000 |
| **Swagger UI (документация API)** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **Health Check** | http://localhost:8000/health |
| **Elasticsearch** | http://localhost:9200 |
| **Prometheus** | http://localhost:9090 |
| **Grafana** | http://localhost:3001 |

_______________________________________________________________________________________________________________________________________________________________________________________________

## Основные эндпоинты API

| Метод | Эндпоинт | Описание |
| :--- | :--- | :--- |
| `POST` | `/api/v1/documents/upload` | Загрузить PDF/DOCX файл (макс. 20 МБ) |
| `GET` | `/api/v1/documents` | Получить список всех загруженных документов |
| `DELETE` | `/api/v1/documents/{id}` | Удалить документ по ID |
| `GET` | `/api/v1/search` | Полнотекстовый поиск (поддерживает пагинацию) |
| `GET` | `/health` | Проверка статуса сервера |

### Примеры запросов

#### Загрузка документа

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@/path/to/document.pdf"
```

#### Поиск с пагинацией

```bash
# Первая страница (первые 2 результата)
curl "http://localhost:8000/api/v1/search?q=учебная&limit=2&offset=0"

# Вторая страница
curl "http://localhost:8000/api/v1/search?q=учебная&limit=2&offset=2"
```

#### Список документов

```bash
curl "http://localhost:8000/api/v1/documents"
```

#### Удаление документа

```bash
curl -X DELETE "http://localhost:8000/api/v1/documents/{document_id}"
```

---

## Полезные команды для работы с Docker

```bash
# Просмотр запущенных контейнеров
docker ps

# Просмотр логов всех сервисов
docker-compose logs -f

# Перезапуск всех сервисов
docker-compose restart

# Остановка и удаление контейнеров (останавливает всё)
docker-compose down

# Остановка с полной очисткой данных (VOLUMES)
docker-compose down -v
```

---

## Полезные команды для проверки Elasticsearch

```bash
# Проверка, что Elasticsearch запущен
curl http://localhost:9200

# Просмотр всех индексов
curl "http://localhost:9200/_cat/indices?v"

# Просмотр всех документов в индексе documents
curl "http://localhost:9200/documents/_search?pretty"

# Удаление индекса documents (осторожно!)
curl -X DELETE "http://localhost:9200/documents"

# Количество документов в индексе
curl "http://localhost:9200/documents/_count?pretty"
```

---

## Полезные команды для проверки Redis

```bash
# Проверка, что Redis запущен
docker exec -it university-search-redis redis-cli ping

# Очистка кеша Redis
docker exec -it university-search-redis redis-cli flushall
```

---

## Полезные команды для тестирования

```bash
# Запуск всех тестов
cd backend
pytest -v

# Запуск тестов с отчетом о покрытии
pytest --cov=app --cov-report=html

# Запуск конкретного теста
pytest tests/test_api.py -v
```
