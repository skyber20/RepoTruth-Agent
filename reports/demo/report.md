# RepoTruth Report

Repo: examples/mock_repo
Generated: 2026-04-25 10:49:35 MSK
Model: qwen3.5-122b
Score: 3/5 confirmed

## Есть FastAPI backend

- verdict: `confirmed`
- confidence: `0.95`
- tools: `repo_evidence_search_tool`
- reason: Evidencesa подтверждают наличие FastAPI: import в app/main.py, создание app = FastAPI(), и зависимоть в requirements.txt
- evidence used: requirements.txt, app/main.py, requirements.txt:1, app/main.py:1, app/main.py:4

Evidence:
- `requirements.txt` [code] file: `fastapi==0.115.0`
- `app/main.py` [code] file: `from fastapi import FastAPI`
- `requirements.txt:1` [dependency] dependency:fastapi: `fastapi==0.115.0`
- `app/main.py:1` [code] pattern:from fastapi import FastAPI: `from fastapi import FastAPI`
- `app/main.py:4` [code] pattern:app = FastAPI(: `app = FastAPI()`

## Проект запускается в Docker

- verdict: `confirmed`
- confidence: `0.95`
- tools: `repo_evidence_search_tool`
- reason: Наличие файла Dockerfile с инструкциями FROM python, COPY Requirements и CMD для запуска uvicorn напрямую подтверждает возможность запуска проекта в Docker
- evidence used: Dockerfile:1, Dockerfile:4, Dockerfile:7

Evidence:
- `requirements.txt` [code] file: `fastapi==0.115.0`
- `Dockerfile` [config] file: `FROM python:3.12-slim`
- `Dockerfile:1` [config] pattern:FROM python: `FROM python:3.12-slim`
- `Dockerfile:4` [config] pattern:COPY requirements: `COPY requirements.txt .`
- `Dockerfile:7` [config] pattern:CMD: `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`
- `app/main.py:1` [code] pattern:FROM: `from fastapi import FastAPI`

## Есть telegram интеграция

- verdict: `missing`
- confidence: `0.90`
- tools: `repo_evidence_search_tool`
- reason: В Evidence отсутствуют подтверждения telegram интеграции: нет импортов библиотек (aiogram, telebot), нет BOT_TOKEN в коде
- missing: импорт telegram/aiogram/telebot, наличие BOT_TOKEN в коде

Evidence:
- `requirements.txt` [code] file: `fastapi==0.115.0`
- `app/main.py` [code] file: `from fastapi import FastAPI`

## Есть тесты

- verdict: `confirmed`
- confidence: `0.95`
- tools: `repo_evidence_search_tool`
- reason: Файл tests/test_health.py содержит функцию def test_health_contract(), что прямо подтверждает наличие специализированных тестов.
- evidence used: tests/test_health.py:1, tests/test_health.py

Evidence:
- `requirements.txt` [code] file: `fastapi==0.115.0`
- `tests/test_health.py` [code] file: `def test_health_contract():`
- `requirements.txt:3` [dependency] dependency:pytest: `pytest==8.3.0`
- `tests/test_health.py:1` [code] pattern:def test_: `def test_health_contract():`

## Реализован RAG

- verdict: `missing`
- confidence: `0.95`
- tools: `repo_evidence_search_tool`
- reason: Доказательства ограничиваются базовой настройкой FastAPI. Отсутствуют импорты RAG-библиотек, код работы с векторами или контекстом.
- missing: импорты langchain/chromadb, определение vector_store, логика retrival

Evidence:
- `requirements.txt` [code] file: `fastapi==0.115.0`
- `app/main.py` [code] file: `from fastapi import FastAPI`
