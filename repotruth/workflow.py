import tempfile
from datetime import datetime, timezone
from pathlib import Path

from repotruth.llm import LLMClient
from repotruth.models import AuditReport, ClaimAudit
from repotruth.tools.claim_planner import extract_claims, plan_claim
from repotruth.tools.claim_verifier import verify_claim
from repotruth.tools.clone_repo import clone_repo
from repotruth.tools.evidence_search import search_evidence
from repotruth.tools.github_metadata import get_github_metadata
from repotruth.tools.repo_index import build_repo_index, read_file_contexts, select_context_files
from repotruth.tools.report_writer import write_report


def run_audit(repo_url, claims_path, out_dir, no_llm=False, event=None):
    """Запускает линейный audit workflow."""

    llm = LLMClient.from_env()
    if not no_llm and not llm.available:
        raise RuntimeError("LLM не настроена. Задай OPENAI_BASE_URL, OPENAI_API_KEY и OPENAI_MODEL.")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    log_path = out_path / "run.log"
    log_path.write_text("", encoding="utf-8")

    def emit(message):
        if event:
            event(message)
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"{datetime.now(timezone.utc).isoformat()} {message}\n")

    notes = []
    emit("Читаю GitHub metadata...")
    metadata = get_github_metadata(repo_url)
    emit("Читаю claims...")
    claims_text = Path(claims_path).read_text(encoding="utf-8")
    emit("Extractor выделяет атомарные claims...")
    claims, extractor_used = extract_claims(claims_text, llm if not no_llm else None)

    if not extractor_used:
        notes.append(f"Extractor использовал fallback parsing. Причина: {llm.last_error or 'LLM отключена.'}")

    with tempfile.TemporaryDirectory(prefix="repotruth-") as temp_dir:
        emit("Клонирую репозиторий...")
        repo_path = clone_repo(repo_url, Path(temp_dir) / "repo")
        emit("Строю repo_index...")
        repo_index = build_repo_index(repo_path)
        audits = []

        for index, claim in enumerate(claims, start=1):
            prefix = f"[{index}/{len(claims)}] {claim.text}"
            emit(f"{prefix}: Planner строит план...")
            plan, planner_used = plan_claim(claim, repo_index, llm if not no_llm else None)
            if not planner_used:
                notes.append(f"{claim.id}: Planner использовал registry fallback. Причина: {llm.last_error or 'LLM отключена.'}")

            emit(f"{prefix}: Evidence Search ищет следы...")
            evidence = search_evidence(repo_path, plan)
            emit(f"{prefix}: File Context Reader читает контекст...")
            context_paths = select_context_files(plan, evidence, repo_index)
            file_contexts = read_file_contexts(repo_path, context_paths, evidence)
            emit(f"{prefix}: Verifier выносит verdict...")
            verdict = verify_claim(claim, plan, evidence, file_contexts, llm if not no_llm else None)
            if not verdict.llm_used:
                notes.append(f"{claim.id}: Verifier использовал rule-based fallback.")

            audits.append(ClaimAudit(claim=claim, plan=plan, evidence=evidence, verdict=verdict))

    report = AuditReport(
        repo_url=repo_url,
        generated_at=datetime.now(timezone.utc).isoformat(),
        metadata=metadata,
        audits=audits,
        llm_model=llm.model,
        notes=unique(notes),
    )
    emit("Пишу report.md и report.json...")
    markdown_path, json_path = write_report(report, out_dir)
    emit("Готово.")
    return report, markdown_path, json_path


def unique(values):
    """Убирает дубли, сохраняя порядок."""

    result = []
    seen = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
