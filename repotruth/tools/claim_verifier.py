from repotruth.models import ClaimVerdict
from repotruth.prompts import CLAIM_VERIFIER_PROMPT


def verify_claim(claim, plan, evidence, file_contexts=None, llm=None):
    """Выносит verdict по evidence."""

    file_contexts = file_contexts or []
    rule_verdict = verify_by_rules(plan, evidence)
    if skip_llm_verifier(rule_verdict, evidence):
        return rule_verdict

    if not llm or not llm.available:
        return rule_verdict

    payload = {
        "claim": claim.model_dump(),
        "plan": plan.model_dump(),
        "evidence": [item.model_dump() | {"ref": item.ref} for item in evidence[:40]],
        "file_contexts": file_contexts,
        "allowed_refs": [item.ref for item in evidence],
        "rule_suggestion": rule_verdict.model_dump(),
    }
    data = llm.try_complete_json(CLAIM_VERIFIER_PROMPT, payload)
    if not data:
        return rule_verdict

    try:
        verdict = ClaimVerdict.model_validate(data)
    except Exception:
        return rule_verdict

    if verdict.verdict not in ["confirmed", "partial", "missing"]:
        return rule_verdict

    verdict.evidence_used = valid_refs(verdict.evidence_used, evidence)
    verdict.confidence = max(0.0, min(1.0, verdict.confidence))
    verdict.llm_used = True

    if verdict.verdict == "missing":
        verdict.evidence_used = []

    if verdict.verdict == "confirmed" and not has_real_evidence(verdict.evidence_used, evidence):
        verdict.verdict = "partial" if evidence else "missing"
        verdict.confidence = min(verdict.confidence, 0.55)
        verdict.reason = "LLM не сослалась на реальные code/config evidence, verdict понижен."

    return verdict


def skip_llm_verifier(rule_verdict, evidence):
    """Пропускает LLM, если claim явно не найден."""

    if rule_verdict.verdict != "missing":
        return False
    real = [item for item in evidence if item.kind != "readme"]
    return not signal_groups(real)


def verify_by_rules(plan, evidence):
    """Простой verifier без LLM."""

    real = [item for item in evidence if item.kind != "readme"]
    if not real:
        return ClaimVerdict(
            verdict="missing",
            confidence=0.2,
            reason="Не найдено evidence в коде, зависимостях или конфигах.",
            missing_signals=plan.strong_signals,
        )

    groups = signal_groups(real)
    if not groups:
        return ClaimVerdict(
            verdict="missing",
            confidence=0.25,
            reason="Найдены только слабые совпадения, сильных сигналов реализации нет.",
            evidence_used=[],
            missing_signals=plan.strong_signals,
        )

    claim_type = plan.claim_type

    if claim_type == "docker":
        verdict = "confirmed" if "docker_file" in groups else "partial"
    elif claim_type == "fastapi":
        verdict = "confirmed" if {"dependency", "fastapi_code"} <= groups or {"fastapi_code", "route"} <= groups else "partial"
    elif claim_type == "tests":
        verdict = "confirmed" if "test_file" in groups or "test_function" in groups else "partial"
    elif claim_type == "telegram_bot":
        verdict = "confirmed" if len(groups & {"dependency", "bot_code", "handler"}) >= 2 else "partial"
    elif claim_type == "rag":
        verdict = rag_verdict(groups)
    else:
        verdict = "partial"

    confidence = confidence_for(verdict, groups)
    return ClaimVerdict(
        verdict=verdict,
        confidence=confidence,
        reason=reason_for(claim_type, verdict, groups),
        evidence_used=best_refs(real),
        missing_signals=missing_signals(plan, groups),
    )


def signal_groups(evidence):
    """Группирует evidence по смыслу."""

    groups = set()
    for item in evidence:
        text = f"{item.path} {item.snippet} {item.matched_signal}".lower()
        if item.kind == "dependency":
            groups.add("dependency")
        if "file:dockerfile" in text or "file:docker-compose" in text or "compose.yaml" in text or "services:" in text:
            groups.add("docker_file")
        if "fastapi" in text or "apirouter" in text:
            groups.add("fastapi_code")
        if "@app.get" in text or "@app.post" in text or "@router." in text:
            groups.add("route")
        if "/tests/" in f"/{item.path.lower()}" or file_name(item.path).startswith("test_"):
            groups.add("test_file")
        if "def test_" in text or "class test" in text:
            groups.add("test_function")
        if any(token in text for token in ["aiogram", "telebot", "python-telegram-bot", "bot("]):
            groups.add("bot_code")
        if any(token in text for token in ["message_handler", "callback_query", "polling", "webhook", "dispatcher"]):
            groups.add("handler")
        if any(token in text for token in ["embedding", "embeddings", "sentencetransformer"]):
            groups.add("embeddings")
        if any(token in text for token in ["chroma", "faiss", "qdrant", "pinecone", "vector"]):
            groups.add("vector_store")
        if any(token in text for token in ["similarity_search", "as_retriever", "retriever", "top_k"]):
            groups.add("retrieval")
        if any(token in text for token in ["context", "documents", "retrieved_docs"]):
            groups.add("context")
    return groups


def file_name(path):
    """Возвращает имя файла без импорта pathlib."""

    return path.replace("\\", "/").split("/")[-1].lower()


def rag_verdict(groups):
    """Оценивает RAG строже остальных claims."""

    required = {"embeddings", "vector_store", "retrieval"}
    if required <= groups and "context" in groups:
        return "confirmed"
    if len(required & groups) >= 2:
        return "partial"
    return "missing"


def confidence_for(verdict, groups):
    """Считает confidence по числу сигналов."""

    if verdict == "confirmed":
        return min(0.95, 0.75 + len(groups) * 0.04)
    if verdict == "partial":
        return min(0.72, 0.42 + len(groups) * 0.05)
    return 0.25


def reason_for(claim_type, verdict, groups):
    """Объясняет rule-based verdict."""

    found = ", ".join(sorted(groups)) or "нет сильных сигналов"
    if verdict == "confirmed":
        return f"{claim_type} подтвержден: найдены сильные сигналы ({found})."
    if verdict == "partial":
        return f"{claim_type} подтвержден частично: найдены только часть сигналов ({found})."
    return f"{claim_type} не подтвержден: сильные сигналы не найдены."


def missing_signals(plan, groups):
    """Показывает недостающие сигналы."""

    missing = []
    for signal in plan.strong_signals:
        if signal not in groups:
            missing.append(signal)
    return missing


def valid_refs(refs, evidence):
    """Оставляет только настоящие refs."""

    allowed = {item.ref for item in evidence}
    return [ref for ref in refs if ref in allowed]


def unique_refs(refs):
    """Убирает дубли refs."""

    result = []
    seen = set()
    for ref in refs:
        if ref not in seen:
            seen.add(ref)
            result.append(ref)
    return result


def best_refs(evidence):
    """Сначала refs со строками, потом file-only."""

    with_lines = [item.ref for item in evidence if item.line]
    without_lines = [item.ref for item in evidence if not item.line]
    return unique_refs(with_lines + without_lines)[:8]


def has_real_evidence(refs, evidence):
    """Проверяет, что refs ведут не только на README."""

    by_ref = {item.ref: item for item in evidence}
    return any(ref in by_ref and by_ref[ref].kind != "readme" for ref in refs)
