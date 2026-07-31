# JobScope

Сервис для сбора и анализа вакансий с hh.ru: парсит вакансии по ключевым запросам и городам, считает статистику по зарплатам и навыкам.

## Возможности

- Парсинг вакансий с hh.ru по запросам и городам
- Поиск и фильтрация вакансий (по названию, компании, городу, графику, зарплате)
- Статистика: средняя зарплата, распределение зарплат по диапазонам
- Топ навыков по вакансиям
- Конвертация зарплат в BYN по официальным курсам НБРБ
- Автоматическое обновление данных каждые 6 часов (Celery Beat)

## Стек

- Python, FastAPI
- SQLAlchemy 2.0 (async) + Alembic
- PostgreSQL, Redis
- Celery
- Docker, Docker Compose
- Vanilla JS + Chart.js (фронтенд)

## Запуск

```bash
cp .env.example .env
docker-compose up --build
```

- Web UI: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs

## API

| Метод | Эндпоинт | Описание |
|---|---|---|
| GET | `/vacancies` | Список вакансий с фильтрами и пагинацией |
| GET | `/stats` | Средняя зарплата и количество вакансий |
| GET | `/stats/salary-distribution` | Распределение зарплат по диапазонам |
| GET | `/skills` | Топ навыков |
| POST | `/parse` | Запуск парсинга по запросу и городу |
| POST | `/parse/all` | Запуск полного парсинга |

Пример запроса с фильтрами:

```
GET /vacancies?search=python&city=Минск&salary_min=1000&offset=0
```

## Тесты

```bash
pytest tests/
```

## Структура проекта

```
src/
├── api/routes/       # REST API эндпоинты
├── models/           # SQLAlchemy модели
├── repositories/     # слой доступа к данным
├── schemas/          # схемы фильтров
├── parser/           # парсер hh.ru
├── tasks.py          # Celery задачи
├── celery_app.py     # конфигурация Celery
└── currency.py       # конвертация валют (НБРБ)
```
