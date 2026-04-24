from .models import AtomicClaim, SearchPlan


DEFAULT_TOOLS = ["repo_evidence_search_tool", "file_context_reader_tool", "claim_verifier_tool"]
ALLOWED_TOOLS = set(DEFAULT_TOOLS)


PATTERNS = [
    {
        "claim_type": "docker",
        "triggers": ["docker", "контейнер", "compose"],
        "keywords": ["docker", "dockerfile", "compose"],
        "likely_files": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"],
        "dependency_names": [],
        "code_patterns": ["services:"],
        "strong_signals": ["dockerfile", "compose_file"],
    },
    {
        "claim_type": "fastapi",
        "triggers": ["fastapi", "fast api"],
        "keywords": ["fastapi", "uvicorn"],
        "likely_files": ["main.py", "app/main.py", "api.py", "server.py", "routers.py"],
        "dependency_names": ["fastapi", "uvicorn"],
        "code_patterns": ["from fastapi import FastAPI", "import fastapi", "FastAPI(", "@app.get", "@app.post", "APIRouter"],
        "strong_signals": ["dependency", "import", "route"],
    },
    {
        "claim_type": "tests",
        "triggers": ["test", "тест", "pytest", "unittest"],
        "keywords": ["pytest", "unittest", "assert ", "test_"],
        "likely_files": ["tests", "test_", "_test.py", "pytest.ini", "conftest.py"],
        "dependency_names": ["pytest", "unittest"],
        "code_patterns": ["def test_", "class Test", "pytest", "unittest"],
        "strong_signals": ["test_file", "test_function"],
    },
    {
        "claim_type": "telegram_bot",
        "triggers": ["telegram", "телеграм", "тг", "bot", "бот"],
        "keywords": ["telegram", "bot", "aiogram", "telebot", "python-telegram-bot"],
        "likely_files": ["bot.py", "telegram.py", "handlers.py", "main.py"],
        "dependency_names": ["aiogram", "pyTelegramBotAPI", "python-telegram-bot", "telebot"],
        "code_patterns": ["Bot(", "Dispatcher", "message_handler", "callback_query", "polling", "webhook", "TELEGRAM_TOKEN", "BOT_TOKEN"],
        "strong_signals": ["dependency", "bot_initialization", "handler"],
    },
    {
        "claim_type": "rag",
        "triggers": ["rag", "retrieval", "ретрив", "vector", "вектор", "embedding", "эмбед"],
        "keywords": ["rag", "retrieval", "embedding", "vector", "context", "documents"],
        "likely_files": ["rag.py", "retriever.py", "vectorstore.py", "embeddings.py", "chains.py"],
        "dependency_names": ["langchain", "llama-index", "chromadb", "faiss-cpu", "qdrant-client", "pinecone-client", "sentence-transformers"],
        "code_patterns": ["OpenAIEmbeddings", "HuggingFaceEmbeddings", "SentenceTransformer", "Chroma", "FAISS", "Qdrant", "Pinecone", "similarity_search", "as_retriever", "retriever", "chunk_size", "RecursiveCharacterTextSplitter", "context", "retrieved_docs"],
        "strong_signals": ["embeddings", "vector_store", "retrieval", "context_in_prompt"],
    },
    {
        "claim_type": "database",
        "triggers": ["database", "postgres", "sqlite", "база", "бд", "sqlalchemy"],
        "keywords": ["database", "postgres", "sqlite", "mongodb", "redis", "sqlalchemy"],
        "likely_files": ["models.py", "database.py", "db.py", "migrations"],
        "dependency_names": ["sqlalchemy", "asyncpg", "psycopg", "pymongo", "redis"],
        "code_patterns": ["create_engine", "sessionmaker", "DATABASE_URL", "MongoClient", "Redis("],
        "strong_signals": ["dependency", "connection_code"],
    },
    {
        "claim_type": "ci",
        "triggers": ["ci", "github actions", "pipeline", "workflow", "cicd"],
        "keywords": ["github actions", "workflow", "ci", "pytest", "lint"],
        "likely_files": [".github/workflows", ".gitlab-ci.yml"],
        "dependency_names": [],
        "code_patterns": ["on:", "jobs:", "runs-on:"],
        "strong_signals": ["workflow_file"],
    },
    {
        "claim_type": "ml_model",
        "triggers": ["ml", "machine learning", "model", "модель", "sklearn", "torch"],
        "keywords": ["model", "train", "predict", "sklearn", "torch", "tensorflow", "transformers"],
        "likely_files": ["train.py", "model.py", "predict.py", "inference.py"],
        "dependency_names": ["scikit-learn", "sklearn", "torch", "tensorflow", "transformers"],
        "code_patterns": ["fit(", "predict(", "torch.nn", "joblib.dump", "pickle.dump"],
        "strong_signals": ["ml_dependency", "training_or_inference_code"],
    },
    {
        "claim_type": "frontend",
        "triggers": ["frontend", "react", "vite", "next", "фронт"],
        "keywords": ["react", "vite", "next", "frontend", "package.json"],
        "likely_files": ["package.json", "src/App.jsx", "src/App.tsx", "pages", "app"],
        "dependency_names": ["react", "vite", "next"],
        "code_patterns": ["React", "useState", "export default", "createRoot"],
        "strong_signals": ["package_json", "frontend_source"],
    },
]


def fallback_extract_claims(text):
    """Разбирает bullet-list без LLM."""

    claims = []
    lines = text.splitlines()
    for line_number, raw_line in enumerate(lines, start=1):
        line = clean_claim_line(raw_line)
        if not line:
            continue
        claims.append(AtomicClaim(id=f"C{len(claims) + 1}", text=line, source_line=line_number))

    if not claims and text.strip():
        claims.append(AtomicClaim(id="C1", text=text.strip(), source_line=1))

    return claims


def clean_claim_line(raw_line):
    """Чистит строку claim."""

    line = raw_line.strip()
    if not line or line.startswith(("#", "```")):
        return ""

    if line.startswith(("- ", "* ")):
        return line[2:].strip()

    if len(line) > 2 and line[0].isdigit() and line[1] in [".", ")"]:
        return line[2:].strip()

    if len(line) > 15 and not raw_line.startswith((" ", "\t")):
        return line

    return ""


def registry_plan_for_claim(claim):
    """Дает базовый план без LLM."""

    text = claim.text.lower()
    for pattern in PATTERNS:
        if any(trigger in text for trigger in pattern["triggers"]):
            return SearchPlan(
                claim_id=claim.id,
                claim_type=pattern["claim_type"],
                keywords=pattern["keywords"],
                likely_files=pattern["likely_files"],
                dependency_names=pattern["dependency_names"],
                code_patterns=pattern["code_patterns"],
                strong_signals=pattern["strong_signals"],
                tools=DEFAULT_TOOLS,
            )

    words = []
    for word in claim.text.split():
        clean = word.strip(".,:;!?()[]{}\"'").lower()
        if len(clean) >= 4:
            words.append(clean)

    return SearchPlan(
        claim_id=claim.id,
        claim_type="unknown",
        keywords=unique(words)[:8],
        strong_signals=["code_or_config_match"],
        tools=DEFAULT_TOOLS,
    )


def merge_plans(base, llm_plan):
    """Объединяет локальный и LLM-план."""

    if not llm_plan:
        return clamp_plan(base)

    if isinstance(llm_plan, dict):
        llm_plan = SearchPlan.model_validate(llm_plan)

    claim_type = base.claim_type
    if llm_plan.claim_type and llm_plan.claim_type != "unknown":
        claim_type = llm_plan.claim_type

    return clamp_plan(
        SearchPlan(
            claim_id=base.claim_id,
            claim_type=claim_type,
            keywords=unique(base.keywords + llm_plan.keywords),
            likely_files=unique(base.likely_files + llm_plan.likely_files),
            dependency_names=unique(base.dependency_names + llm_plan.dependency_names),
            code_patterns=unique(base.code_patterns + llm_plan.code_patterns),
            strong_signals=unique(base.strong_signals + llm_plan.strong_signals),
            tools=normalize_tools(llm_plan.tools or base.tools),
        )
    )


def clamp_plan(plan):
    """Ограничивает слишком длинный план."""

    plan.keywords = unique(plan.keywords)[:20]
    plan.likely_files = unique(plan.likely_files)[:20]
    plan.dependency_names = unique(plan.dependency_names)[:20]
    plan.code_patterns = unique(plan.code_patterns)[:24]
    plan.strong_signals = unique(plan.strong_signals)[:12]
    plan.tools = normalize_tools(plan.tools)
    return plan


def normalize_tools(tools):
    """Чистит список tools."""

    result = [tool for tool in unique(tools) if tool in ALLOWED_TOOLS]
    if "repo_evidence_search_tool" not in result:
        result.insert(0, "repo_evidence_search_tool")
    if "claim_verifier_tool" not in result:
        result.append("claim_verifier_tool")
    return result


def unique(values):
    """Оставляет уникальные строки."""

    result = []
    seen = set()
    for value in values:
        item = str(value).strip()
        key = item.lower()
        if item and key not in seen:
            seen.add(key)
            result.append(item)
    return result
