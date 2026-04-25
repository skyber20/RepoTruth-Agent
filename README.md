Track: A+C

# RepoTruth Agent

RepoTruth проверяет ТЗ, резюме или список claims по реальному коду репозитория.

LLM здесь не “угадывает” ответ. Она делает две агентные вещи:

1. Разбивает текст на проверяемые claims.
2. Для каждого claim выбирает tools.

Дальше обычный Python собирает evidence, а LLM-verifier ставит `confirmed`, `partial` или `missing` только по найденным evidence.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export OPENAI_BASE_URL="http://localhost:8000/v1"
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="qwen3.5:122b"

python -m repotruth --repo https://github.com/user/project --claims examples/claims_basic.md --out reports/demo
```

Можно положить `OPENAI_BASE_URL`, `OPENAI_API_KEY` и `OPENAI_MODEL` в `.env`.

Результат:

```text
reports/demo/report.md
reports/demo/report.json
reports/demo/run.log
```

## Tools

У агента два выбираемых инструмента. Именно эти имена LLM-router кладет в `plan.tools`:

- `github_metadata_tool` — внешний GitHub API: описание, языки, звезды, форки, лицензия.
- `repo_evidence_search_tool` — поиск по файлам, зависимостям, конфигам и строкам кода.

Важно для Track A: GitHub API вызывается не всегда, а только если LLM-router выбрал `github_metadata_tool` для claim.

Файлы вроде `claim_planner.py`, `claim_verifier.py` и `report_writer.py` — это не agent tools, а обычные внутренние модули каркаса.

## Workflow

```text
claims/resume/tz
  -> LLM Extractor
  -> clone/copy repo
  -> repo index
  -> LLM Tool Router
  -> selected tools
  -> LLM Verifier
  -> Markdown + JSON report
```

## Почему Track A+C

Track A: есть внешний API tool — GitHub REST API (`/repos`, `/languages`).

Track C: агент собирает данные из репозитория и сохраняет структурированный `report.json`: claim, plan, выбранные tools, evidence и verdict.

## Evidence Contract

Для `confirmed` и `partial` нужны ссылки на реальные источники:

```text
requirements.txt:1 -> fastapi==0.115.0
app/main.py:1 -> from fastapi import FastAPI
GitHub API /repos/owner/name -> stars=42; license=MIT
```

README считается слабым evidence и не подтверждает реализацию сам по себе.

## Структура

```text
repotruth/
  cli.py                    # красивый CLI на typer + rich
  workflow.py               # основной сценарий агента
  llm.py                    # OpenAI-compatible запрос к модели
  models.py                 # Pydantic-схемы данных
  prompts.py                # prompts для extractor/router
  tools/
    claim_planner.py        # LLM Extractor + LLM Tool Router
    github_metadata.py      # GitHub API tool
    evidence_search.py      # поиск evidence в коде
    claim_verifier.py       # LLM verifier по найденным evidence
    report_writer.py        # Markdown/JSON отчет
```

## Ограничения

- Для локальной папки `github_metadata_tool` не сможет получить API metadata.
- Архитектурные claims вроде “clean architecture” лучше проверять вручную.
- Если evidence нерелевантны claim, LLM-verifier должен вернуть `missing`.
