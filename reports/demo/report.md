# RepoTruth Report

Repo: examples/mock_repo
Generated: 2026-04-25 11:24:28 MSK
Model: qwen3.5-122b
Score: 2/3 confirmed

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

## Есть telegram интеграция

- verdict: `missing`
- confidence: `0.95`
- tools: `repo_evidence_search_tool`
- reason: Evidence содержат только конфигурацию FastAPI, отсутствуют имена зависимостей Telegram или импорты соответствующих библиотек.
- missing: Зависимость aiogram или pyTelegramBotApi в requirements.txt, Импорт модулей telegram в коде

Evidence:
- `requirements.txt` [code] file: `fastapi==0.115.0`
- `app/main.py` [code] file: `from fastapi import FastAPI`

## Проект запускается в Docker

- verdict: `confirmed`
- confidence: `0.95`
- tools: `repo_evidence_search_tool`
- reason: Файл Dockerfile присутствует с инструкциями FROM python:3.12-slim и CMD для сборки и запуска образа контейнера
- evidence used: Dockerfile:1, Dockerfile:7

Evidence:
- `Dockerfile` [config] file: `FROM python:3.12-slim`
- `Dockerfile:1` [config] pattern:FROM python: `FROM python:3.12-slim`
- `Dockerfile:7` [config] pattern:CMD: `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`
- `app/main.py:1` [code] pattern:FROM: `from fastapi import FastAPI`
