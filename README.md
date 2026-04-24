Track: A+C

# RepoTruth Agent

RepoTruth Agent проверяет утверждения о GitHub-репозитории по реальным следам в коде.

Он принимает список claims, строит для каждого claim план поиска, клонирует публичный репозиторий, ищет evidence в файлах/зависимостях/коде и выдает отчет:

- `confirmed`
- `partial`
- `missing`

Главное отличие от обычного LLM-ответа: агент не верит README на слово. Для каждого вывода он показывает `path:line -> snippet`.

## Быстрый запуск

Нужен Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Настрой Qwen через OpenAI-compatible endpoint:

```bash
export OPENAI_BASE_URL="http://localhost:8000/v1"
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="qwen3.5:122b"
```

Запуск:

```bash
python -m repotruth audit \
  --repo https://github.com/user/project \
  --claims examples/claims_basic.md \
  --out reports/demo
```

Результат:

```text
reports/demo/report.md
reports/demo/report.json
```

Для локальной отладки без LLM есть режим:

```bash
python -m repotruth audit --repo /path/to/local/repo --claims examples/claims_basic.md --out reports/local --no-llm
```

Для сдачи используется обычный режим с Qwen, без `--no-llm`.

## Как это работает

```text
claims.md
  -> LLM Extractor
  -> LLM Planner + Tool Router
  -> выбранные tools
  -> Claim Verifier
  -> Markdown/JSON Report
```

## Почему это агент, а не grep script

RepoTruth использует LLM для динамического планирования проверки.

Например, claim `Есть Telegram-интеграция` не проверяется только словом `telegram`. LLM Planner строит search plan: какие библиотеки, файлы, imports и code patterns нужно искать. Затем Python-инструмент ищет реальные evidence в репозитории, а LLM Verifier выносит verdict только по найденным доказательствам.

Planner также возвращает список tools, которые нужны для claim. Workflow не просто всегда вызывает один и тот же код, а выполняет выбранные инструменты и записывает `tools_used` в отчет. Если rule-based verifier уже нашел сильные доказательства или понятное отсутствие evidence, LLM verifier не вызывается.

## Evidence Contract

Каждый `confirmed` или `partial` verdict обязан иметь evidence:

```text
app/main.py:1 -> from fastapi import FastAPI
requirements.txt:3 -> fastapi==0.115.0
```

README-only evidence не может подтвердить реализацию.

## Поддерживаемые claim types

- Docker
- FastAPI
- Tests
- Telegram bot
- RAG
- Database
- CI
- ML model
- Frontend

## Переменные окружения

```bash
OPENAI_BASE_URL     # endpoint Qwen в формате OpenAI-compatible API
OPENAI_API_KEY      # ключ endpoint
OPENAI_MODEL        # например qwen3.5:122b
GITHUB_TOKEN        # необязательно, помогает при GitHub rate limit
```

## Структура

```text
repotruth/
  cli.py                 # CLI
  workflow.py            # линейный agentic workflow
  llm.py                 # Qwen OpenAI-compatible client
  models.py              # Pydantic-модели
  patterns.py            # локальные claim patterns
  tools/
    clone_repo.py
    github_metadata.py
    claim_planner.py
    evidence_search.py
    claim_verifier.py
    report_writer.py
```

## Тесты

```bash
pytest
```

## Ограничения MVP

- Проверяются только публичные GitHub-репозитории или локальные папки.
- Evidence search не делает полный AST-анализ.
- Архитектурные claims вроде `clean architecture` могут требовать ручной проверки.
- RAG проверяется строго: embeddings и vector store без retrieval pipeline дадут `partial`, а не `confirmed`.
