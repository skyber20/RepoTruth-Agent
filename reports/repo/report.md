# RepoTruth Report

Repo: https://github.com/skyber20/RepoTruth-Agent.git
Generated: 2026-04-24T13:08:40.986729+00:00
Model: qwen3.5-122b

Score: 10/23 confirmed, 18/23 supported

## Repository

Тестовое задание для прохождения в весеннюю школу ИТ и ИИ

## Confirmed

- В репозитории есть файл README
  - verdict confidence: 0.95
  - reason: Файл README.md существует и подтверждён несколькими evidence (kind: file и kind: readme). Файл_contexts показывает реальное содержимое, а не заглушку.
  - evidence: README.md:1, README.md:5, README.md:7
- В репозитории есть файл REFLECTION.md
  - verdict confidence: 0.95
  - reason: Файл REFLECTION.md существует в репозитории с реальным содержимым. Есть прямое evidence типа 'file' и несколько evidence из кода файла.
  - evidence: REFLECTION.md:1, REFLECTION.md:5, REFLECTION.md:7, REFLECTION.md:13, REFLECTION.md:17
- В REFLECTION.md содержится 300+ слов
  - verdict confidence: 0.95
  - reason: Файл REFLECTION.md существует и содержит полный текст из 25 строк. По подсчету слов в file_contexts (5 параграфов по 50-100 слов каждый) общее количество слов превышает 300.
  - evidence: REFLECTION.md:1, REFLECTION.md:15
- В REFLECTION.md описаны failure case агента
  - verdict confidence: 0.95
  - reason: В REFLECTION.md есть раздел '## Где агент ломался' с 3 конкретными failure case (слишком общие claims, сложный RAG, непредсказуемость LLM JSON)
  - evidence: REFLECTION.md:11, REFLECTION.md:13, REFLECTION.md:15, REFLECTION.md:17
- В REFLECTION.md описаны планы на будущее
  - verdict confidence: 0.95
  - reason: В REFLECTION.md есть раздел «Что сделал бы дальше» (строки 19-23) с конкретными планами: baseline comparison, веб-интерфейс, поддержка private repos, больше языков, semantic code search.
  - evidence: REFLECTION.md:1, REFLECTION.md:5
- Первая строка README содержит тег трека (A/B/C/D)
  - verdict confidence: 0.95
  - reason: Первая строка README.md (строка 1) содержит 'Track: A+C', что включает теги трека A и C из допустимого набора (A/B/C/D).
  - evidence: README.md:1
- У агента реализован минимум 1 инструмент
  - verdict confidence: 0.95
  - reason: В проекте реализована директория `tools/` с несколькими модулями (`claim_verifier.py`, `evidence_search.py` и др.), содержащими рабочие функции. Эти функции импортируются и используются в `workflow.py` как инструменты агента.
  - evidence: repotruth/tools/__init__.py:1, repotruth/tools/claim_verifier.py:1, repotruth/tools/evidence_search.py:1, repotruth/workflow.py:7, repotruth/workflow.py:8
- В коде указан используемый LLM провайдер
  - verdict confidence: 0.85
  - reason: LLM провайдер указан в коде: repotruth/llm.py содержит клиент для OpenAI-compatible Qwen API с конфигурацией через OPENAI_BASE_URL, OPENAI_API_KEY, MODEL_DEFAULT. .env.example также определяет эти переменные.
  - evidence: repotruth/llm.py:17, repotruth/llm.py:28, repotruth/llm.py:29, repotruth/llm.py:30, .env.example:1
- В коде указан используемый стек технологий
  - verdict confidence: 0.88
  - reason: Стек технологий явно указан в requirements.txt (typer, rich, pydantic, pytest, python-dotenv), Dockerfile (Python 3.12-slim), и поддерживается кодом для сбора зависимостей.
  - evidence: requirements.txt:1, requirements.txt:2, requirements.txt:3, requirements.txt:4, requirements.txt:5, examples/mock_repo/requirements.txt:1, examples/mock_repo/Dockerfile:1, pytest.ini:1
- Агент вызывает внешний API
  - verdict confidence: 0.90
  - reason: Агент явно вызывает внешние API: LLM API через urllib.request в llm.py и GitHub API через urllib.request в github_metadata.py с реальными HTTP-запросами
  - evidence: repotruth/llm.py:60, repotruth/llm.py:71, repotruth/tools/github_metadata.py:21, repotruth/tools/github_metadata.py:45

## Partial

- В README есть инструкция запуска одной командой
  - verdict confidence: 0.75
  - reason: В README есть раздел 'Быстрый запуск' с инструкциями, но это не одна команда: требуется настройка venv, установка зависимостей, переменных окружения, а сам запуск — многокомандный процесс с несколькими флагами.
  - evidence: README.md:15, README.md:22, README.md:33, README.md:36, README.md:52
- Агент реально использует инструмент, а не только LLM
  - verdict confidence: 0.72
  - reason: Агент использует инструменты (clone_repo, build_repo_index, get_github_metadata, verify_claim), но полная интеграция tool-системы с LLM не полностью доказана в evidence. Есть rule-based verifier fallback.
  - evidence: repotruth/workflow.py:7, repotruth/workflow.py:8, repotruth/workflow.py:9, repotruth/workflow.py:10, repotruth/workflow.py:11, repotruth/workflow.py:12, repotruth/workflow.py:17, repotruth/tools/claim_verifier.py:1, repotruth/tools/claim_verifier.py:62, repotruth/tools/claim_verifier.py:159, tests/test_workflow_smoke.py:1, tests/test_workflow_smoke.py:4
- Агент сам решает, когда вызывать API
  - verdict confidence: 0.60
  - reason: Найдены инструменты и LLM-клиент, но в коде нет явной логики автономного выбора вызовов API (цикл, условные переходы). Workflow выглядит линейным.
  - evidence: repotruth/workflow.py:1, repotruth/llm.py:1, repotruth/tools/claim_verifier.py:1
- В репозитории есть ссылки на данные
  - verdict confidence: 0.67
  - reason: unknown подтвержден частично: найдены только часть сигналов (context, dependency, fastapi_code, test_file, vector_store).
  - evidence: README.md:1, .env.example:1, repotruth/tools/evidence_search.py:1, repotruth/tools/clone_repo.py:1, requirements.txt:5, REFLECTION.md:5, REFLECTION.md:7, REFLECTION.md:9
- Указаны источники и дата сбора данных
  - verdict confidence: 0.55
  - reason: Найдена частичная реализация: есть timestamp генерации отчета (workflow.py:52) и сбор GitHub-метаданных (github_metadata.py), но нет явного указания источников данных и дат сбора для проверяемых claims.
  - evidence: repotruth/workflow.py:52, repotruth/models.py:59, repotruth/models.py:103, repotruth/tools/github_metadata.py:11, repotruth/tools/github_metadata.py:15
- Есть baseline решение
  - verdict confidence: 0.65
  - reason: Найдена базовая реализация в examples/mock_repo/ (FastAPI app, тесты, Docker), но механизм baseline comparison не реализован (упоминается как future work в REFLECTION.md)
  - evidence: examples/mock_repo/app/main.py:1, examples/mock_repo/tests/test_health.py:1, examples/mock_repo/Dockerfile:1, examples/mock_repo/requirements.txt:1, REFLECTION.md:21
- Есть сравнение решений
  - verdict confidence: 0.62
  - reason: unknown подтвержден частично: найдены только часть сигналов (context, fastapi_code, test_file, vector_store).
  - evidence: REFLECTION.md:5, REFLECTION.md:17, repotruth/prompts.py:8, repotruth/prompts.py:26, repotruth/prompts.py:52, repotruth/prompts.py:64, tests/test_evidence_search.py:14, tests/test_workflow_smoke.py:15
- Если использован шаблон, в README это указано
  - verdict confidence: 0.67
  - reason: unknown подтвержден частично: найдены только часть сигналов (context, embeddings, fastapi_code, retrieval, vector_store).
  - evidence: README.md:1, REFLECTION.md:5, REFLECTION.md:9, REFLECTION.md:15, REFLECTION.md:21, repotruth/models.py:70, repotruth/prompts.py:26, repotruth/prompts.py:27

## Missing

- В REFLECTION.md описан выбор задачи и мотивация
  - verdict confidence: 0.35
  - reason: Найдены только слабые совпадения, сильных сигналов реализации нет.
- В репозитории есть train.ipynb или скрипт обучения
  - verdict confidence: 0.85
  - reason: В репозитории нет train.ipynb или скрипта обучения. ML-паттерны в patterns.py — это конфигурация для проверки других репозиториев, а не реализация обучения. В requirements.txt нет ML-зависимостей (torch, tensorflow, scikit-learn).
- В документации указаны метрики модели
  - verdict confidence: 0.90
  - reason: Найдены только слабые совпадения, сильных сигналов реализации нет.
- В коде агента загружается модель
  - verdict confidence: 0.85
  - reason: В коде агента нет загрузки ML-моделей. Файл models.py содержит Pydantic-схемы данных, а не ML-модели. LLMClient в llm.py использует внешние API (OpenAI-compatible), не загружает модели локально. В patterns.py определены только шаблоны для проверки ML-моделей в других проектах, но нет реальной реализации загрузки моделей (нет torch.load, AutoModel, fit, predict и т.д.).
- Есть улучшенное решение
  - verdict confidence: 0.30
  - reason: Нет доказательств улучшенного решения. Версия 0.1.0 есть, но нет changelog, performance_metrics или comparison_code. REFLECTION.md обсуждает будущие улучшения, а не реализованные.

## Evidence

### C1. В репозитории есть файл README
- `README.md:1` [file] file:README.md: `Track: A+C`
- `README.md:5` [readme] pattern:репозитории: `RepoTruth Agent проверяет утверждения о GitHub-репозитории по реальным следам в коде.`
- `README.md:7` [readme] pattern:файл: `Он принимает список claims, строит для каждого claim план поиска, клонирует публичный репозиторий, ищет evidence в файлах/зависимостях/коде и выдает отчет:`
- `README.md:13` [readme] pattern:README: `Главное отличие от обычного LLM-ответа: агент не верит README на слово. Для каждого вывода он показывает `path:line -> snippet`.`
- `README.md:49` [readme] pattern:есть: `Для локальной отладки без LLM есть режим:`
- `README.md:72` [readme] pattern:репозитории: `Например, claim `Есть Telegram-интеграция` не проверяется только словом `telegram`. LLM Planner строит search plan: какие библиотеки, файлы, imports и code patterns нужно искать. Затем Python-инструмент ищет реальные evidence в репозитории, а LLM Verifier выносит verdict только по найденным доказате`
- `README.md:83` [readme] pattern:README: `README-only evidence не может подтвердить реализацию.`
- `README.md:132` [readme] pattern:репозитории: `- Проверяются только публичные GitHub-репозитории или локальные папки.`
- `REFLECTION.md:5` [code] pattern:README: `Я выбрал RepoTruth Agent, потому что это очень практичная задача на стыке ИИ, разработки и честной оценки проектов. В резюме, на хакатонах и в учебных отборах люди часто пишут короткие утверждения: “сделал RAG”, “есть FastAPI backend”, “проект запускается в Docker”, “есть тесты”. Но по одному README`
- `REFLECTION.md:7` [code] pattern:репозитории: `Мне понравилась идея сделать агента, который не просто отвечает красивым текстом, а ищет проверяемые доказательства. Поэтому RepoTruth устроен как evidence-based workflow: LLM сначала помогает понять, что именно нужно проверить, затем строит search plan, Python-инструменты собирают реальные следы в `
- `REFLECTION.md:13` [code] pattern:файл: `Первый failure case — слишком общие claims. Например, утверждение “проект хорошо спроектирован” почти невозможно честно подтвердить простым поиском по файлам. Для таких claims агент может найти косвенные признаки, но не должен писать `confirmed`. В MVP такие claims лучше получают `partial` или `miss`
- `REFLECTION.md:15` [code] pattern:README: `Второй failure case — сложный RAG. Многие проекты имеют Chroma, embeddings или слово RAG в README, но не имеют полноценного retrieval pipeline, где документы загружаются, режутся на chunks, превращаются в embeddings, ищутся через retriever и передаются в prompt как context. Поэтому RAG проверяется с`

### C2. В README есть инструкция запуска одной командой
- `README.md:1` [file] file:README.md: `Track: A+C`
- `repotruth/patterns.py:1` [file] file:repotruth/patterns.py: `from .models import AtomicClaim, SearchPlan`
- `repotruth/models.py:1` [file] file:repotruth/models.py: `from pydantic import BaseModel, ConfigDict, Field`
- `repotruth/__init__.py:1` [file] file:repotruth/__init__.py: `"""Пакет RepoTruth Agent."""`
- `repotruth/llm.py:1` [file] file:repotruth/llm.py: `import json`
- `repotruth/prompts.py:1` [file] file:repotruth/prompts.py: `CLAIM_EXTRACTOR_PROMPT = """`
- `repotruth/cli.py:1` [file] file:repotruth/cli.py: `from pathlib import Path`
- `repotruth/workflow.py:1` [file] file:repotruth/workflow.py: `import tempfile`
- `repotruth/__main__.py:1` [file] file:repotruth/__main__.py: `from .cli import main`
- `examples/mock_repo/Dockerfile:1` [config] file:examples/mock_repo/Dockerfile: `FROM python:3.12-slim`
- `repotruth/tools/__init__.py:1` [file] file:repotruth/tools/__init__.py: `"""Инструменты RepoTruth."""`
- `repotruth/tools/clone_repo.py:1` [file] file:repotruth/tools/clone_repo.py: `import shutil`

### C3. В репозитории есть файл REFLECTION.md
- `REFLECTION.md:1` [file] file:REFLECTION.md: `# Рефлексия`
- `pytest.ini:2` [config] pattern:Path: `testpaths = tests`
- `README.md:5` [readme] pattern:репозитории: `RepoTruth Agent проверяет утверждения о GitHub-репозитории по реальным следам в коде.`
- `README.md:7` [readme] pattern:файл: `Он принимает список claims, строит для каждого claim план поиска, клонирует публичный репозиторий, ищет evidence в файлах/зависимостях/коде и выдает отчет:`
- `README.md:13` [readme] pattern:Path: `Главное отличие от обычного LLM-ответа: агент не верит README на слово. Для каждого вывода он показывает `path:line -> snippet`.`
- `README.md:25` [readme] pattern:open: `Настрой Qwen через OpenAI-compatible endpoint:`
- `README.md:28` [readme] pattern:open: `export OPENAI_BASE_URL="http://localhost:8000/v1"`
- `README.md:29` [readme] pattern:open: `export OPENAI_API_KEY="your-key"`
- `README.md:30` [readme] pattern:open: `export OPENAI_MODEL="qwen3.5:122b"`
- `README.md:49` [readme] pattern:есть: `Для локальной отладки без LLM есть режим:`
- `README.md:52` [readme] pattern:Path: `python -m repotruth audit --repo /path/to/local/repo --claims examples/claims_basic.md --out reports/local --no-llm`
- `README.md:72` [readme] pattern:репозитории: `Например, claim `Есть Telegram-интеграция` не проверяется только словом `telegram`. LLM Planner строит search plan: какие библиотеки, файлы, imports и code patterns нужно искать. Затем Python-инструмент ищет реальные evidence в репозитории, а LLM Verifier выносит verdict только по найденным доказате`

### C4. В REFLECTION.md содержится 300+ слов
- `REFLECTION.md:1` [file] file:REFLECTION.md: `# Рефлексия`
- `tests/test_claims.py:1` [file] file:tests/test_claims.py: `from repotruth.patterns import fallback_extract_claims, registry_plan_for_claim`
- `README.md:13` [readme] pattern:слов: `Главное отличие от обычного LLM-ответа: агент не верит README на слово. Для каждого вывода он показывает `path:line -> snippet`.`
- `README.md:72` [readme] pattern:слов: `Например, claim `Есть Telegram-интеграция` не проверяется только словом `telegram`. LLM Planner строит search plan: какие библиотеки, файлы, imports и code patterns нужно искать. Затем Python-инструмент ищет реальные evidence в репозитории, а LLM Verifier выносит verdict только по найденным доказате`
- `REFLECTION.md:15` [code] pattern:слов: `Второй failure case — сложный RAG. Многие проекты имеют Chroma, embeddings или слово RAG в README, но не имеют полноценного retrieval pipeline, где документы загружаются, режутся на chunks, превращаются в embeddings, ищутся через retriever и передаются в prompt как context. Поэтому RAG проверяется с`
- `repotruth/patterns.py:8` [code] pattern:words: `"keywords": ["docker", "dockerfile", "compose"],`
- `repotruth/patterns.py:17` [code] pattern:words: `"keywords": ["fastapi", "uvicorn"],`
- `repotruth/patterns.py:26` [code] pattern:assert: `"keywords": ["pytest", "unittest", "assert ", "test_"],`
- `repotruth/patterns.py:35` [code] pattern:words: `"keywords": ["telegram", "bot", "aiogram", "telebot", "python-telegram-bot"],`
- `repotruth/patterns.py:44` [code] pattern:words: `"keywords": ["rag", "retrieval", "embedding", "vector", "context", "documents"],`
- `repotruth/patterns.py:53` [code] pattern:words: `"keywords": ["database", "postgres", "sqlite", "mongodb", "redis", "sqlalchemy"],`
- `repotruth/patterns.py:62` [code] pattern:words: `"keywords": ["github actions", "workflow", "ci", "pytest", "lint"],`

### C5. В REFLECTION.md описан выбор задачи и мотивация
- `REFLECTION.md:1` [file] file:REFLECTION.md: `# Рефлексия`
- `REFLECTION.md:21` [code] pattern:описан: `Если бы было больше времени, я бы добавил baseline comparison: обычная LLM получает только README и claims, а RepoTruth получает tools и evidence. Это наглядно показало бы, где простая LLM верит описанию, а агент находит реальное состояние кода.`
- `repotruth/prompts.py:43` [code] pattern:описан: `- README-самоописание не является сильным доказательством.`

### C6. В REFLECTION.md описаны failure case агента
- `REFLECTION.md:1` [file] file:REFLECTION.md: `# Рефлексия`
- `README.md:13` [readme] pattern:агент: `Главное отличие от обычного LLM-ответа: агент не верит README на слово. Для каждого вывода он показывает `path:line -> snippet`.`
- `README.md:68` [readme] pattern:агент: `## Почему это агент, а не grep script`
- `REFLECTION.md:7` [code] pattern:агента: `Мне понравилась идея сделать агента, который не просто отвечает красивым текстом, а ищет проверяемые доказательства. Поэтому RepoTruth устроен как evidence-based workflow: LLM сначала помогает понять, что именно нужно проверить, затем строит search plan, Python-инструменты собирают реальные следы в `
- `REFLECTION.md:9` [code] pattern:агент: `Особенно важная часть проекта — evidence contract. Если агент пишет `confirmed`, он обязан показать путь, номер строки и фрагмент кода. Это снижает риск галлюцинаций и делает результат воспроизводимым. Для меня это главный инженерный урок проекта: LLM должна не заменять проверку, а управлять проверя`
- `REFLECTION.md:11` [code] pattern:агент: `## Где агент ломался`
- `REFLECTION.md:13` [code] pattern:failure case: `Первый failure case — слишком общие claims. Например, утверждение “проект хорошо спроектирован” почти невозможно честно подтвердить простым поиском по файлам. Для таких claims агент может найти косвенные признаки, но не должен писать `confirmed`. В MVP такие claims лучше получают `partial` или `miss`
- `REFLECTION.md:15` [code] pattern:failure case: `Второй failure case — сложный RAG. Многие проекты имеют Chroma, embeddings или слово RAG в README, но не имеют полноценного retrieval pipeline, где документы загружаются, режутся на chunks, превращаются в embeddings, ищутся через retriever и передаются в prompt как context. Поэтому RAG проверяется с`
- `REFLECTION.md:17` [code] pattern:failure case: `Третий failure case — непредсказуемость LLM JSON. Даже сильная модель иногда возвращает пояснения вокруг JSON. Поэтому в проекте есть JSON extractor и fallback registry patterns. Это делает систему стабильнее и проще для демонстрации.`
- `REFLECTION.md:21` [code] pattern:агент: `Если бы было больше времени, я бы добавил baseline comparison: обычная LLM получает только README и claims, а RepoTruth получает tools и evidence. Это наглядно показало бы, где простая LLM верит описанию, а агент находит реальное состояние кода.`
- `REFLECTION.md:25` [code] pattern:агент: `Также я бы расширил режим для кандидатов: агент мог бы не только говорить `confirmed/partial/missing`, но и предлагать честную формулировку для резюме. Например, вместо “реализовал полноценный RAG” предложить “добавил embeddings и Chroma; retrieval pipeline требует доработки”. Это делает инструмент `
- `repotruth/llm.py:12` [code] pattern:ошибка: `"""Ошибка ответа модели."""`

### C7. В REFLECTION.md описаны планы на будущее
- `REFLECTION.md:1` [file] file:REFLECTION.md: `# Рефлексия`
- `REFLECTION.md:5` [code] pattern:планы: `Я выбрал RepoTruth Agent, потому что это очень практичная задача на стыке ИИ, разработки и честной оценки проектов. В резюме, на хакатонах и в учебных отборах люди часто пишут короткие утверждения: “сделал RAG”, “есть FastAPI backend”, “проект запускается в Docker”, “есть тесты”. Но по одному README`

### C8. Первая строка README содержит тег трека (A/B/C/D)
- `README.md:1` [file] file:README.md: `Track: A+C`
- `README.md:13` [readme] pattern:readme: `Главное отличие от обычного LLM-ответа: агент не верит README на слово. Для каждого вывода он показывает `path:line -> snippet`.`
- `README.md:72` [readme] pattern:Тег: `Например, claim `Есть Telegram-интеграция` не проверяется только словом `telegram`. LLM Planner строит search plan: какие библиотеки, файлы, imports и code patterns нужно искать. Затем Python-инструмент ищет реальные evidence в репозитории, а LLM Verifier выносит verdict только по найденным доказате`
- `README.md:83` [readme] pattern:readme: `README-only evidence не может подтвердить реализацию.`
- `REFLECTION.md:5` [code] pattern:readme: `Я выбрал RepoTruth Agent, потому что это очень практичная задача на стыке ИИ, разработки и честной оценки проектов. В резюме, на хакатонах и в учебных отборах люди часто пишут короткие утверждения: “сделал RAG”, “есть FastAPI backend”, “проект запускается в Docker”, “есть тесты”. Но по одному README`
- `REFLECTION.md:15` [code] pattern:readme: `Второй failure case — сложный RAG. Многие проекты имеют Chroma, embeddings или слово RAG в README, но не имеют полноценного retrieval pipeline, где документы загружаются, режутся на chunks, превращаются в embeddings, ищутся через retriever и передаются в prompt как context. Поэтому RAG проверяется с`
- `REFLECTION.md:21` [code] pattern:readme: `Если бы было больше времени, я бы добавил baseline comparison: обычная LLM получает только README и claims, а RepoTruth получает tools и evidence. Это наглядно показало бы, где простая LLM верит описанию, а агент находит реальное состояние кода.`
- `repotruth/models.py:70` [code] pattern:readme: `readme: str | None = None`
- `repotruth/prompts.py:43` [code] pattern:readme: `- README-самоописание не является сильным доказательством.`
- `repotruth/prompts.py:70` [code] pattern:readme: `- README-only evidence не может дать confirmed.`
- `tests/test_verifier_rules.py:24` [code] pattern:Тег: `claim = AtomicClaim(id="C1", text="Есть Telegram-интеграция")`
- `tests/test_claims.py:29` [code] pattern:Тег: `claim = fallback_extract_claims("- Есть Telegram-интеграция")[0]`

### C9. У агента реализован минимум 1 инструмент
- `repotruth/workflow.py:1` [file] file:repotruth/workflow.py: `import tempfile`
- `repotruth/tools/github_metadata.py:1` [file] file:repotruth/tools/github_metadata.py: `import base64`
- `repotruth/tools/__init__.py:1` [file] file:repotruth/tools/__init__.py: `"""Инструменты RepoTruth."""`
- `repotruth/tools/claim_verifier.py:1` [file] file:repotruth/tools/claim_verifier.py: `from repotruth.models import ClaimVerdict`
- `repotruth/tools/evidence_search.py:1` [file] file:repotruth/tools/evidence_search.py: `import json`
- `repotruth/tools/report_writer.py:1` [file] file:repotruth/tools/report_writer.py: `import json`
- `repotruth/tools/repo_index.py:1` [file] file:repotruth/tools/repo_index.py: `from pathlib import Path`
- `repotruth/tools/clone_repo.py:1` [file] file:repotruth/tools/clone_repo.py: `import shutil`
- `repotruth/tools/claim_planner.py:1` [file] file:repotruth/tools/claim_planner.py: `from repotruth.models import AtomicClaim, SearchPlan`
- `requirements.txt:1` [dependency] dependency:typer: `typer==0.24.1`
- `requirements.txt:3` [dependency] dependency:pydantic: `pydantic==2.13.3`
- `README.md:3` [readme] pattern:agent: `# RepoTruth Agent`

### C10. Агент реально использует инструмент, а не только LLM
- `repotruth/models.py:1` [file] file:repotruth/models.py: `from pydantic import BaseModel, ConfigDict, Field`
- `repotruth/llm.py:1` [file] file:repotruth/llm.py: `import json`
- `repotruth/workflow.py:1` [file] file:repotruth/workflow.py: `import tempfile`
- `tests/test_workflow_smoke.py:1` [file] file:tests/test_workflow_smoke.py: `from repotruth.workflow import run_audit`
- `repotruth/tools/github_metadata.py:1` [file] file:repotruth/tools/github_metadata.py: `import base64`
- `repotruth/tools/__init__.py:1` [file] file:repotruth/tools/__init__.py: `"""Инструменты RepoTruth."""`
- `repotruth/tools/claim_verifier.py:1` [file] file:repotruth/tools/claim_verifier.py: `from repotruth.models import ClaimVerdict`
- `repotruth/tools/evidence_search.py:1` [file] file:repotruth/tools/evidence_search.py: `import json`
- `repotruth/tools/report_writer.py:1` [file] file:repotruth/tools/report_writer.py: `import json`
- `repotruth/tools/repo_index.py:1` [file] file:repotruth/tools/repo_index.py: `from pathlib import Path`
- `repotruth/tools/clone_repo.py:1` [file] file:repotruth/tools/clone_repo.py: `import shutil`
- `repotruth/tools/claim_planner.py:1` [file] file:repotruth/tools/claim_planner.py: `from repotruth.models import AtomicClaim, SearchPlan`

### C11. В коде указан используемый LLM провайдер
- `requirements.txt:1` [file] file:requirements.txt: `typer==0.24.1`
- `.env.example:1` [file] file:.env.example: `OPENAI_BASE_URL=`
- `repotruth/models.py:1` [file] file:repotruth/models.py: `from pydantic import BaseModel, ConfigDict, Field`
- `repotruth/llm.py:1` [file] file:repotruth/llm.py: `import json`
- `repotruth/cli.py:1` [file] file:repotruth/cli.py: `from pathlib import Path`
- `examples/mock_repo/requirements.txt:1` [file] file:requirements.txt: `fastapi==0.115.0`
- `README.md:5` [readme] pattern:коде: `RepoTruth Agent проверяет утверждения о GitHub-репозитории по реальным следам в коде.`
- `README.md:7` [readme] pattern:коде: `Он принимает список claims, строит для каждого claim план поиска, клонирует публичный репозиторий, ищет evidence в файлах/зависимостях/коде и выдает отчет:`
- `README.md:13` [readme] pattern:LLM: `Главное отличие от обычного LLM-ответа: агент не верит README на слово. Для каждого вывода он показывает `path:line -> snippet`.`
- `README.md:25` [readme] pattern:openai: `Настрой Qwen через OpenAI-compatible endpoint:`
- `README.md:28` [readme] pattern:openai: `export OPENAI_BASE_URL="http://localhost:8000/v1"`
- `README.md:29` [readme] pattern:openai: `export OPENAI_API_KEY="your-key"`

### C12. В коде указан используемый стек технологий
- `pytest.ini:1` [file] file:pytest.ini: `[pytest]`
- `requirements.txt:1` [file] file:requirements.txt: `typer==0.24.1`
- `README.md:1` [file] file:README.md: `Track: A+C`
- `examples/mock_repo/requirements.txt:1` [file] file:requirements.txt: `fastapi==0.115.0`
- `examples/mock_repo/Dockerfile:1` [config] file:examples/mock_repo/Dockerfile: `FROM python:3.12-slim`
- `requirements.txt:1` [dependency] dependency:typer: `typer==0.24.1`
- `requirements.txt:2` [dependency] dependency:rich: `rich==15.0.0`
- `requirements.txt:3` [dependency] dependency:pydantic: `pydantic==2.13.3`
- `requirements.txt:4` [dependency] dependency:pytest: `pytest==9.0.2`
- `requirements.txt:5` [dependency] dependency:python-dotenv: `python-dotenv==1.2.2`
- `README.md:5` [readme] pattern:коде: `RepoTruth Agent проверяет утверждения о GitHub-репозитории по реальным следам в коде.`
- `README.md:7` [readme] pattern:коде: `Он принимает список claims, строит для каждого claim план поиска, клонирует публичный репозиторий, ищет evidence в файлах/зависимостях/коде и выдает отчет:`

### C13. Агент вызывает внешний API
- `requirements.txt:1` [file] file:requirements.txt: `typer==0.24.1`
- `repotruth/models.py:1` [file] file:repotruth/models.py: `from pydantic import BaseModel, ConfigDict, Field`
- `repotruth/llm.py:1` [file] file:repotruth/llm.py: `import json`
- `repotruth/workflow.py:1` [file] file:repotruth/workflow.py: `import tempfile`
- `examples/mock_repo/requirements.txt:1` [file] file:requirements.txt: `fastapi==0.115.0`
- `repotruth/tools/github_metadata.py:1` [file] file:repotruth/tools/github_metadata.py: `import base64`
- `README.md:13` [readme] pattern:агент: `Главное отличие от обычного LLM-ответа: агент не верит README на слово. Для каждого вывода он показывает `path:line -> snippet`.`
- `README.md:25` [readme] pattern:endpoint: `Настрой Qwen через OpenAI-compatible endpoint:`
- `README.md:28` [readme] pattern:http: `export OPENAI_BASE_URL="http://localhost:8000/v1"`
- `README.md:29` [readme] pattern:api_key: `export OPENAI_API_KEY="your-key"`
- `README.md:37` [readme] pattern:http: `--repo https://github.com/user/project \`
- `README.md:68` [readme] pattern:агент: `## Почему это агент, а не grep script`

### C14. Агент сам решает, когда вызывать API
- `repotruth/models.py:1` [file] file:repotruth/models.py: `from pydantic import BaseModel, ConfigDict, Field`
- `repotruth/llm.py:1` [file] file:repotruth/llm.py: `import json`
- `repotruth/workflow.py:1` [file] file:repotruth/workflow.py: `import tempfile`
- `repotruth/tools/github_metadata.py:1` [file] file:repotruth/tools/github_metadata.py: `import base64`
- `repotruth/tools/__init__.py:1` [file] file:repotruth/tools/__init__.py: `"""Инструменты RepoTruth."""`
- `repotruth/tools/claim_verifier.py:1` [file] file:repotruth/tools/claim_verifier.py: `from repotruth.models import ClaimVerdict`
- `repotruth/tools/evidence_search.py:1` [file] file:repotruth/tools/evidence_search.py: `import json`
- `repotruth/tools/report_writer.py:1` [file] file:repotruth/tools/report_writer.py: `import json`
- `repotruth/tools/repo_index.py:1` [file] file:repotruth/tools/repo_index.py: `from pathlib import Path`
- `repotruth/tools/clone_repo.py:1` [file] file:repotruth/tools/clone_repo.py: `import shutil`
- `repotruth/tools/claim_planner.py:1` [file] file:repotruth/tools/claim_planner.py: `from repotruth.models import AtomicClaim, SearchPlan`
- `requirements.txt:3` [dependency] dependency:pydantic: `pydantic==2.13.3`

### C15. В репозитории есть train.ipynb или скрипт обучения
- `requirements.txt:1` [file] file:requirements.txt: `typer==0.24.1`
- `README.md:1` [file] file:README.md: `Track: A+C`
- `repotruth/models.py:1` [file] file:repotruth/models.py: `from pydantic import BaseModel, ConfigDict, Field`
- `repotruth/workflow.py:1` [file] file:repotruth/workflow.py: `import tempfile`
- `examples/mock_repo/requirements.txt:1` [file] file:requirements.txt: `fastapi==0.115.0`
- `repotruth/tools/claim_verifier.py:1` [file] file:repotruth/tools/claim_verifier.py: `from repotruth.models import ClaimVerdict`
- `README.md:5` [readme] pattern:репозитории: `RepoTruth Agent проверяет утверждения о GitHub-репозитории по реальным следам в коде.`
- `README.md:30` [readme] pattern:model: `export OPENAI_MODEL="qwen3.5:122b"`
- `README.md:49` [readme] pattern:есть: `Для локальной отладки без LLM есть режим:`
- `README.md:72` [readme] pattern:репозитории: `Например, claim `Есть Telegram-интеграция` не проверяется только словом `telegram`. LLM Planner строит search plan: какие библиотеки, файлы, imports и code patterns нужно искать. Затем Python-инструмент ищет реальные evidence в репозитории, а LLM Verifier выносит verdict только по найденным доказате`
- `README.md:94` [readme] pattern:model: `- ML model`
- `README.md:102` [readme] pattern:model: `OPENAI_MODEL        # например qwen3.5:122b`

### C16. В документации указаны метрики модели
- `README.md:1` [file] file:README.md: `Track: A+C`
- `REFLECTION.md:1` [file] file:REFLECTION.md: `# Рефлексия`
- `repotruth/models.py:1` [file] file:repotruth/models.py: `from pydantic import BaseModel, ConfigDict, Field`
- `README.md:113` [readme] pattern:модели: `models.py              # Pydantic-модели`
- `repotruth/llm.py:12` [code] pattern:модели: `"""Ошибка ответа модели."""`
- `repotruth/llm.py:93` [code] pattern:модели: `"""Достает первый JSON из ответа модели."""`
- `repotruth/cli.py:39` [code] pattern:ошибка: `console.print(f"[red]Ошибка:[/red] {error}")`

### C17. В коде агента загружается модель
- `repotruth/models.py:1` [file] file:repotruth/models.py: `from pydantic import BaseModel, ConfigDict, Field`
- `repotruth/llm.py:1` [file] file:repotruth/llm.py: `import json`
- `repotruth/workflow.py:1` [file] file:repotruth/workflow.py: `import tempfile`
- `README.md:30` [readme] pattern:model: `export OPENAI_MODEL="qwen3.5:122b"`
- `README.md:94` [readme] pattern:model: `- ML model`
- `README.md:102` [readme] pattern:model: `OPENAI_MODEL        # например qwen3.5:122b`
- `README.md:113` [readme] pattern:model: `models.py              # Pydantic-модели`
- `README.md:135` [readme] pattern:Pipeline: `- RAG проверяется строго: embeddings и vector store без retrieval pipeline дадут `partial`, а не `confirmed`.`
- `REFLECTION.md:15` [code] pattern:Pipeline: `Второй failure case — сложный RAG. Многие проекты имеют Chroma, embeddings или слово RAG в README, но не имеют полноценного retrieval pipeline, где документы загружаются, режутся на chunks, превращаются в embeddings, ищутся через retriever и передаются в prompt как context. Поэтому RAG проверяется с`
- `REFLECTION.md:17` [code] pattern:модель: `Третий failure case — непредсказуемость LLM JSON. Даже сильная модель иногда возвращает пояснения вокруг JSON. Поэтому в проекте есть JSON extractor и fallback registry patterns. Это делает систему стабильнее и проще для демонстрации.`
- `REFLECTION.md:25` [code] pattern:Pipeline: `Также я бы расширил режим для кандидатов: агент мог бы не только говорить `confirmed/partial/missing`, но и предлагать честную формулировку для резюме. Например, вместо “реализовал полноценный RAG” предложить “добавил embeddings и Chroma; retrieval pipeline требует доработки”. Это делает инструмент `
- `repotruth/patterns.py:1` [code] pattern:model: `from .models import AtomicClaim, SearchPlan`

### C18. В репозитории есть ссылки на данные
- `README.md:1` [file] file:README.md: `Track: A+C`
- `.env.example:1` [file] file:.env.example: `OPENAI_BASE_URL=`
- `repotruth/tools/evidence_search.py:1` [file] file:repotruth/tools/evidence_search.py: `import json`
- `repotruth/tools/clone_repo.py:1` [file] file:repotruth/tools/clone_repo.py: `import shutil`
- `requirements.txt:5` [dependency] dependency:python-dotenv: `python-dotenv==1.2.2`
- `README.md:5` [readme] pattern:репозитории: `RepoTruth Agent проверяет утверждения о GitHub-репозитории по реальным следам в коде.`
- `README.md:28` [readme] pattern:http://: `export OPENAI_BASE_URL="http://localhost:8000/v1"`
- `README.md:37` [readme] pattern:https://: `--repo https://github.com/user/project \`
- `README.md:49` [readme] pattern:есть: `Для локальной отладки без LLM есть режим:`
- `README.md:72` [readme] pattern:репозитории: `Например, claim `Есть Telegram-интеграция` не проверяется только словом `telegram`. LLM Planner строит search plan: какие библиотеки, файлы, imports и code patterns нужно искать. Затем Python-инструмент ищет реальные evidence в репозитории, а LLM Verifier выносит verdict только по найденным доказате`
- `README.md:100` [readme] pattern:url: `OPENAI_BASE_URL     # endpoint Qwen в формате OpenAI-compatible API`
- `README.md:132` [readme] pattern:репозитории: `- Проверяются только публичные GitHub-репозитории или локальные папки.`

### C19. Указаны источники и дата сбора данных
- `README.md:1` [file] file:README.md: `Track: A+C`
- `REFLECTION.md:1` [file] file:REFLECTION.md: `# Рефлексия`
- `examples/claims_basic.md:1` [file] file:examples/claims_basic.md: `# Claims для демо`
- `repotruth/tools/github_metadata.py:1` [file] file:repotruth/tools/github_metadata.py: `import base64`
- `requirements.txt:3` [dependency] dependency:pydantic: `pydantic==2.13.3`
- `README.md:21` [readme] pattern:source: `source .venv/bin/activate`
- `README.md:117` [readme] pattern:metadata: `github_metadata.py`
- `repotruth/patterns.py:84` [code] pattern:source: `"strong_signals": ["package_json", "frontend_source"],`
- `repotruth/patterns.py:98` [code] pattern:source: `claims.append(AtomicClaim(id=f"C{len(claims) + 1}", text=line, source_line=line_number))`
- `repotruth/patterns.py:101` [code] pattern:source: `claims.append(AtomicClaim(id="C1", text=text.strip(), source_line=1))`
- `repotruth/patterns.py:162` [code] pattern:date: `llm_plan = SearchPlan.model_validate(llm_plan)`
- `repotruth/models.py:11` [code] pattern:source: `source_line: int | None = None`

### C20. Есть baseline решение
- `pytest.ini:1` [file] file:pytest.ini: `[pytest]`
- `repotruth/workflow.py:1` [file] file:repotruth/workflow.py: `import tempfile`
- `repotruth/__main__.py:1` [file] file:repotruth/__main__.py: `from .cli import main`
- `examples/claims_basic.md:1` [file] file:examples/claims_basic.md: `# Claims для демо`
- `examples/claims_rag.md:1` [file] file:examples/claims_rag.md: `# RAG claims для демо`
- `examples/mock_repo/requirements.txt:1` [file] file:examples/mock_repo/requirements.txt: `fastapi==0.115.0`
- `examples/mock_repo/Dockerfile:1` [config] file:examples/mock_repo/Dockerfile: `FROM python:3.12-slim`
- `examples/mock_repo/app/main.py:1` [file] file:examples/mock_repo/app/main.py: `from fastapi import FastAPI`
- `examples/mock_repo/tests/test_health.py:1` [file] file:examples/mock_repo/tests/test_health.py: `def test_health_contract():`
- `repotruth/tools/claim_verifier.py:1` [file] file:repotruth/tools/claim_verifier.py: `from repotruth.models import ClaimVerdict`
- `requirements.txt:1` [dependency] dependency:typer: `typer==0.24.1`
- `requirements.txt:2` [dependency] dependency:rich: `rich==15.0.0`

### C21. Есть улучшенное решение
- `pytest.ini:1` [file] file:pytest.ini: `[pytest]`
- `requirements.txt:1` [file] file:requirements.txt: `typer==0.24.1`
- `README.md:1` [file] file:README.md: `Track: A+C`
- `REFLECTION.md:1` [file] file:REFLECTION.md: `# Рефлексия`
- `repotruth/workflow.py:1` [file] file:repotruth/workflow.py: `import tempfile`
- `examples/mock_repo/requirements.txt:1` [file] file:requirements.txt: `fastapi==0.115.0`
- `repotruth/tools/claim_verifier.py:1` [file] file:repotruth/tools/claim_verifier.py: `from repotruth.models import ClaimVerdict`
- `repotruth/tools/evidence_search.py:1` [file] file:repotruth/tools/evidence_search.py: `import json`
- `requirements.txt:1` [dependency] dependency:typer: `typer==0.24.1`
- `requirements.txt:2` [dependency] dependency:rich: `rich==15.0.0`
- `requirements.txt:3` [dependency] dependency:pydantic: `pydantic==2.13.3`
- `requirements.txt:4` [dependency] dependency:pytest: `pytest==9.0.2`

### C22. Есть сравнение решений
- `README.md:49` [readme] pattern:есть: `Для локальной отладки без LLM есть режим:`
- `README.md:72` [readme] pattern:есть: `Например, claim `Есть Telegram-интеграция` не проверяется только словом `telegram`. LLM Planner строит search plan: какие библиотеки, файлы, imports и code patterns нужно искать. Затем Python-инструмент ищет реальные evidence в репозитории, а LLM Verifier выносит verdict только по найденным доказате`
- `REFLECTION.md:5` [code] pattern:есть: `Я выбрал RepoTruth Agent, потому что это очень практичная задача на стыке ИИ, разработки и честной оценки проектов. В резюме, на хакатонах и в учебных отборах люди часто пишут короткие утверждения: “сделал RAG”, “есть FastAPI backend”, “проект запускается в Docker”, “есть тесты”. Но по одному README`
- `REFLECTION.md:17` [code] pattern:есть: `Третий failure case — непредсказуемость LLM JSON. Даже сильная модель иногда возвращает пояснения вокруг JSON. Поэтому в проекте есть JSON extractor и fallback registry patterns. Это делает систему стабильнее и проще для демонстрации.`
- `repotruth/prompts.py:8` [code] pattern:есть: `{"id": "C1", "text": "Есть FastAPI backend", "source_line": 3}`
- `repotruth/prompts.py:26` [code] pattern:есть: `Если repo_index есть, поле likely_files заполняй только существующими путями из repo_index.files или repo_index.important_files.`
- `repotruth/prompts.py:52` [code] pattern:есть: `Используй file_contexts, чтобы понять, есть ли настоящая реализация или только импорт/пустая заглушка.`
- `repotruth/prompts.py:64` [code] pattern:есть: `- confirmed: есть сильные доказательства в коде, зависимостях или конфигах.`
- `tests/test_evidence_search.py:14` [code] pattern:есть: `claim = AtomicClaim(id="C1", text="Есть FastAPI backend")`
- `tests/test_workflow_smoke.py:15` [code] pattern:есть: `"- Есть FastAPI backend\n- Проект запускается в Docker\n- Есть тесты\n",`
- `tests/test_verifier_rules.py:13` [code] pattern:есть: `claim = AtomicClaim(id="C1", text="Есть FastAPI backend")`
- `tests/test_verifier_rules.py:24` [code] pattern:есть: `claim = AtomicClaim(id="C1", text="Есть Telegram-интеграция")`

### C23. Если использован шаблон, в README это указано
- `README.md:1` [file] file:README.md: `Track: A+C`
- `README.md:13` [readme] pattern:readme: `Главное отличие от обычного LLM-ответа: агент не верит README на слово. Для каждого вывода он показывает `path:line -> snippet`.`
- `README.md:83` [readme] pattern:readme: `README-only evidence не может подтвердить реализацию.`
- `REFLECTION.md:5` [code] pattern:readme: `Я выбрал RepoTruth Agent, потому что это очень практичная задача на стыке ИИ, разработки и честной оценки проектов. В резюме, на хакатонах и в учебных отборах люди часто пишут короткие утверждения: “сделал RAG”, “есть FastAPI backend”, “проект запускается в Docker”, “есть тесты”. Но по одному README`
- `REFLECTION.md:9` [code] pattern:если: `Особенно важная часть проекта — evidence contract. Если агент пишет `confirmed`, он обязан показать путь, номер строки и фрагмент кода. Это снижает риск галлюцинаций и делает результат воспроизводимым. Для меня это главный инженерный урок проекта: LLM должна не заменять проверку, а управлять проверя`
- `REFLECTION.md:15` [code] pattern:readme: `Второй failure case — сложный RAG. Многие проекты имеют Chroma, embeddings или слово RAG в README, но не имеют полноценного retrieval pipeline, где документы загружаются, режутся на chunks, превращаются в embeddings, ищутся через retriever и передаются в prompt как context. Поэтому RAG проверяется с`
- `REFLECTION.md:21` [code] pattern:если: `Если бы было больше времени, я бы добавил baseline comparison: обычная LLM получает только README и claims, а RepoTruth получает tools и evidence. Это наглядно показало бы, где простая LLM верит описанию, а агент находит реальное состояние кода.`
- `repotruth/models.py:70` [code] pattern:readme: `readme: str | None = None`
- `repotruth/prompts.py:26` [code] pattern:если: `Если repo_index есть, поле likely_files заполняй только существующими путями из repo_index.files или repo_index.important_files.`
- `repotruth/prompts.py:27` [code] pattern:если: `Не придумывай имена файлов вроде bot.py, если такого файла нет в repo_index.`
- `repotruth/prompts.py:43` [code] pattern:readme: `- README-самоописание не является сильным доказательством.`
- `repotruth/prompts.py:67` [code] pattern:использован: `- Один импорт без использования чаще всего partial или missing, а не confirmed.`

## Notes

- C5: Verifier использовал rule-based fallback.
- C7: Planner использовал registry fallback. Причина: The read operation timed out
- C16: Verifier использовал rule-based fallback.
- C18: Verifier использовал rule-based fallback.
- C22: Planner использовал registry fallback. Причина: LLM HTTP 429: {"error":{"message":"litellm.RateLimitError: No deployments available for selected model. Passed model=qwen3.5-122b. Deployments={'bab43edbf5f8dac9e034ec98c62034592b1176f02a7e6dc1475a8d1c0cd88d87': {'current_tpm': 40830, 'tpm_limit': inf, 'current_rpm': 5, 'rpm_limit': 6}}. Received Model Group=qwen3.5-122b\nAvailable Model Group Fallbacks=None","type":"throttling_error","param":null,"code":"429"}}
- C22: Verifier использовал rule-based fallback.
- C23: Planner использовал registry fallback. Причина: LLM HTTP 429: {"error":{"message":"litellm.RateLimitError: No deployments available for selected model. Passed model=qwen3.5-122b. Deployments={'bab43edbf5f8dac9e034ec98c62034592b1176f02a7e6dc1475a8d1c0cd88d87': {'current_tpm': 40830, 'tpm_limit': inf, 'current_rpm': 5, 'rpm_limit': 6}}. Received Model Group=qwen3.5-122b\nAvailable Model Group Fallbacks=None","type":"throttling_error","param":null,"code":"429"}}
- C23: Verifier использовал rule-based fallback.
