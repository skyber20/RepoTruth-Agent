import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from repotruth.llm import LLMClient
from repotruth.models import AuditReport, ClaimAudit, RepoMetadata
from repotruth.tools.claim_planner import extract_claims, plan_claim
from repotruth.tools.claim_verifier import verify_claim
from repotruth.tools.clone_repo import clone_repo, parse_github_url
from repotruth.tools.evidence_search import build_repo_index, search_evidence
from repotruth.tools.github_metadata import get_github_metadata, metadata_to_evidence
from repotruth.tools.report_writer import write_report


def run_audit(repo_url, claims_path, out_dir, event=None):
    llm = LLMClient()
    if not llm.available:
        raise RuntimeError("Задай OPENAI_BASE_URL, OPENAI_API_KEY и OPENAI_MODEL.")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    log_path = out_path / "run.log"
    log_path.write_text("", encoding="utf-8")
    event = logger(event, log_path)

    claims_text = Path(claims_path).read_text(encoding="utf-8")
    emit(event, "LLM анализирует файл с claims...")
    claims = extract_claims(claims_text, llm)
    emit(event, f"Найдено claims: {len(claims)}")

    metadata = empty_metadata(repo_url)
    metadata_loaded = False
    audits = []
    notes = []

    with tempfile.TemporaryDirectory(prefix="repotruth-") as temp_dir:
        emit(event, "Клонирую или открываю репозиторий...")
        repo_path = clone_repo(repo_url, Path(temp_dir) / "repo")
        repo_index = build_repo_index(repo_path)

        for claim in claims:
            emit(event, f"{claim.text}: планирую поиск и выбираю tools...")
            plan = plan_claim(claim, repo_index, llm)
            evidence = []
            tools_used = []

            if "github_metadata_tool" in plan.tools:
                emit(event, f"{claim.text}: читаю GitHub API...")
                if not metadata_loaded:
                    metadata = get_github_metadata(repo_url)
                    metadata_loaded = True
                    if metadata.api_error:
                        notes.append(metadata.api_error)
                evidence += metadata_to_evidence(metadata)
                tools_used.append("github_metadata_tool")

            if "repo_evidence_search_tool" in plan.tools:
                emit(event, f"{claim.text}: ищу следы в коде и зависимостях...")
                evidence += search_evidence(repo_path, plan)
                tools_used.append("repo_evidence_search_tool")

            emit(event, f"{claim.text}: LLM верифицирует найденные evidence...")
            verdict = verify_claim(claim, plan, evidence, llm)
            emit(event, f"Verdict: {verdict.verdict}, evidence: {len(evidence)}")
            audits.append(ClaimAudit(claim=claim, plan=plan, evidence=evidence, verdict=verdict, tools_used=tools_used))

    report = AuditReport(
        repo_url=repo_url,
        generated_at=now_moscow(),
        metadata=metadata,
        audits=audits,
        llm_model=llm.model,
        notes=notes,
    )
    emit(event, "Пишу report.md и report.json...")
    markdown_path, json_path = write_report(report, out_dir)
    return report, markdown_path, json_path


def empty_metadata(repo_url):
    owner, name = parse_github_url(repo_url)
    return RepoMetadata(url=repo_url, owner=owner, name=name)


def emit(event, message):
    if event:
        event(message)


def logger(event, log_path):
    def write(message):
        line = f"{now_moscow()} {message}"
        with log_path.open("a", encoding="utf-8") as log:
            log.write(line + "\n")
        if event:
            event(message)

    return write


def now_moscow():
    return datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S MSK")
