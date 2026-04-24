# RepoTruth Report

Repo: https://github.com/skyber20/TODO-matrix
Generated: 2026-04-24T14:54:30.027074+00:00
Model: qwen3.5-122b

Score: 3/5 confirmed, 3/5 supported

## Confirmed

- Есть FastAPI backend
  - verdict confidence: 0.95
  - reason: fastapi подтвержден: найдены сильные сигналы (dependency, fastapi_code, route, test_file, test_function).
  - tools: repo_evidence_search_tool, file_context_reader_tool, claim_verifier_tool
  - evidence: run.py:1, requirements.txt:1, app/main.py:1, tests/test_main.py:1, requirements.txt:2, requirements.txt:3, run.py:2, run.py:3
- Проект запускается в Docker
  - verdict confidence: 0.95
  - reason: docker подтвержден: найдены сильные сигналы (dependency, docker_file, fastapi_code).
  - tools: repo_evidence_search_tool, file_context_reader_tool, claim_verifier_tool
  - evidence: requirements.txt:1, Dockerfile:1, .dockerignore:1, docker-compose.yml:1, requirements.txt:3, requirements.txt:5, Dockerfile:10, Dockerfile:27
- Есть тесты
  - verdict confidence: 0.95
  - reason: tests подтвержден: найдены сильные сигналы (dependency, test_file, test_function).
  - tools: repo_evidence_search_tool, file_context_reader_tool, claim_verifier_tool
  - evidence: tests/conftest.py:1, tests/test_database.py:1, tests/test_main.py:1, requirements.txt:9, requirements.txt:17, .gitlab-ci.yml:9, .gitlab-ci.yml:17, .gitlab-ci.yml:21

## Partial

None

## Missing

- Есть Telegram-интеграция
  - verdict confidence: 0.90
  - reason: Не найдено evidence в коде, зависимостях или конфигах.
  - tools: repo_evidence_search_tool, claim_verifier_tool
- Реализован RAG
  - verdict confidence: 0.90
  - reason: Не найдено evidence в коде, зависимостях или конфигах.
  - tools: repo_evidence_search_tool, claim_verifier_tool

## Evidence

### C1. Есть FastAPI backend
- `run.py:1` [file] file:run.py: `if __name__ == '__main__':`
- `requirements.txt:1` [file] file:requirements.txt: `fastapi==0.121.2`
- `app/main.py:1` [file] file:app/main.py: `import logging`
- `tests/test_main.py:1` [file] file:tests/test_main.py: `def test_health(client):`
- `requirements.txt:1` [dependency] dependency:fastapi: `fastapi==0.121.2`
- `requirements.txt:2` [dependency] dependency:pydantic: `pydantic==2.12.4`
- `requirements.txt:3` [dependency] dependency:uvicorn: `uvicorn==0.38.0`
- `run.py:2` [code] pattern:uvicorn: `import uvicorn`
- `run.py:3` [code] pattern:uvicorn.run: `uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)`
- `requirements.txt:1` [code] pattern:fastapi: `fastapi==0.121.2`
- `requirements.txt:3` [code] pattern:uvicorn: `uvicorn==0.38.0`
- `Dockerfile:29` [code] pattern:uvicorn: `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`

### C2. Проект запускается в Docker
- `requirements.txt:1` [file] file:requirements.txt: `fastapi==0.121.2`
- `Dockerfile:1` [config] file:Dockerfile: `FROM python:3.12-alpine AS builder`
- `.dockerignore:1` [file] file:.dockerignore: `.venv/`
- `docker-compose.yml:1` [config] file:docker-compose.yml: `services:`
- `requirements.txt:1` [dependency] dependency:fastapi: `fastapi==0.121.2`
- `requirements.txt:3` [dependency] dependency:uvicorn: `uvicorn==0.38.0`
- `requirements.txt:5` [dependency] dependency:SQLAlchemy: `SQLAlchemy==2.0.45`
- `Dockerfile:1` [code] pattern:FROM python: `FROM python:3.12-alpine AS builder`
- `Dockerfile:10` [code] pattern:FROM python: `FROM python:3.12-alpine`
- `Dockerfile:27` [code] pattern:EXPOSE: `EXPOSE 8000`
- `Dockerfile:29` [code] pattern:CMD: `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`
- `README.md:8` [readme] pattern:docker: `- **Контейнеризация:** Docker, Docker Compose`

### C3. Есть тесты
- `tests/conftest.py:1` [file] file:tests/conftest.py: `import os`
- `tests/test_database.py:1` [file] file:tests/test_database.py: `import pytest`
- `tests/__init__.py` [file] file:tests/__init__.py: `file exists: tests/__init__.py`
- `tests/test_main.py:1` [file] file:tests/test_main.py: `def test_health(client):`
- `requirements.txt:9` [dependency] dependency:pytest: `pytest==9.0.2`
- `requirements.txt:9` [code] pattern:pytest: `pytest==9.0.2`
- `requirements.txt:17` [code] pattern:pytest: `pytest-cov==7.0.0`
- `README.md:10` [readme] pattern:pytest: `- **Тестирование:** pytest, pytest-cov`
- `README.md:49` [readme] pattern:pytest: `- **pytest** — фреймворк для написания и запуска тестов`
- `README.md:50` [readme] pattern:pytest: `- **pytest-cov** — измерение покрытия кода`
- `.gitlab-ci.yml:9` [config] pattern:test_: `LATEST_TAG: $CI_REGISTRY_IMAGE:latest`
- `.gitlab-ci.yml:17` [config] pattern:pytest: `- pip install pytest pytest-cov httpx`

### C4. Есть Telegram-интеграция
No evidence found.

### C5. Реализован RAG
No evidence found.

## Notes

- C1: Verifier использовал rule-based fallback.
- C2: Verifier использовал rule-based fallback.
- C3: Planner использовал registry fallback. Причина: The read operation timed out
- C3: Verifier использовал rule-based fallback.
- C4: Planner использовал registry fallback. Причина: LLM недоступна: <urlopen error _ssl.c:1063: The handshake operation timed out>
- C4: Verifier использовал rule-based fallback.
- C5: Verifier использовал rule-based fallback.
