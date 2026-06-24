# Frontend — University Search System

React-приложение для загрузки документов и полнотекстового поиска по базе знаний университета.

## Требования (FE-01 — FE-09)

- Drag-and-Drop загрузка PDF/DOCX с множественным выбором
- Прогресс-бар со статусами: Загрузка..., Индексация..., Готово, Ошибка
- Список загруженных документов с датой и статусом
- Поиск по кнопке «Найти» и клавише Enter
- Карточки результатов с названием файла, страницей, фрагментом и релевантностью
- Подсветка совпадений жёлтым фоном
- Пагинация по 10 результатов
- Сообщение при пустой выдаче
- Адаптивная вёрстка (320px — 1920px)
- История поисковых запросов в localStorage

## Быстрый старт

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Приложение будет доступно на http://localhost:5173

Убедитесь, что бэкенд запущен на http://localhost:8000

## Сборка

```bash
npm run build
npm run preview
```

## Docker

```bash
docker build -t university-search-frontend .
docker run -p 3000:80 university-search-frontend
```

## Структура

```
src/
├── components/   # UI-компоненты
├── pages/        # Страницы
├── services/     # Запросы к API
├── types/        # TypeScript-типы
└── utils/        # Вспомогательные функции
```
