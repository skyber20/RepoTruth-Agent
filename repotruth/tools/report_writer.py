import json
from pathlib import Path


def write_report(report, out_dir):
    """Пишет Markdown и JSON отчет."""

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)

    markdown_path = output / "report.md"
    json_path = output / "report.json"

    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(
        json.dumps(report.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return markdown_path, json_path


def render_markdown(report):
    """Собирает Markdown отчет."""

    lines = [
        "# RepoTruth Report",
        "",
        f"Repo: {report.repo_url}",
        f"Generated: {report.generated_at}",
        f"Model: {report.llm_model or 'not configured'}",
        "",
        f"Score: {report.confirmed_count}/{report.total_count} confirmed, {report.supported_count}/{report.total_count} supported",
        "",
    ]

    if report.metadata.description:
        lines.extend(["## Repository", "", report.metadata.description, ""])
    if report.metadata.api_error:
        lines.extend([f"> GitHub API note: {report.metadata.api_error}", ""])

    lines.extend(render_group("Confirmed", report, "confirmed"))
    lines.extend(render_group("Partial", report, "partial"))
    lines.extend(render_group("Missing", report, "missing"))
    lines.extend(render_evidence(report))
    lines.extend(render_notes(report))

    return "\n".join(lines).rstrip() + "\n"


def render_group(title, report, verdict):
    """Рендерит группу verdict."""

    lines = [f"## {title}", ""]
    items = [audit for audit in report.audits if audit.verdict.verdict == verdict]
    if not items:
        return lines + ["None", ""]

    for audit in items:
        lines.append(f"- {audit.claim.text}")
        lines.append(f"  - verdict confidence: {audit.verdict.confidence:.2f}")
        lines.append(f"  - reason: {audit.verdict.reason}")
        if audit.verdict.evidence_used:
            lines.append(f"  - evidence: {', '.join(audit.verdict.evidence_used)}")
    lines.append("")
    return lines


def render_evidence(report):
    """Рендерит таблицу evidence."""

    lines = ["## Evidence", ""]
    for audit in report.audits:
        lines.append(f"### {audit.claim.id}. {audit.claim.text}")
        if not audit.evidence:
            lines.append("No evidence found.")
            lines.append("")
            continue
        for item in audit.evidence[:12]:
            lines.append(f"- `{item.ref}` [{item.kind}] {item.matched_signal}: `{item.snippet}`")
        lines.append("")
    return lines


def render_notes(report):
    """Рендерит заметки."""

    if not report.notes:
        return []
    lines = ["## Notes", ""]
    for note in report.notes:
        lines.append(f"- {note}")
    lines.append("")
    return lines
