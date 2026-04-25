import json
from pathlib import Path


def write_report(report, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    md = out / "report.md"
    js = out / "report.json"
    md.write_text(markdown(report), encoding="utf-8")
    js.write_text(json.dumps(report.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return md, js


def markdown(report):
    lines = [
        "# RepoTruth Report",
        "",
        f"Repo: {report.repo_url}",
        f"Generated: {report.generated_at}",
        f"Model: {report.llm_model}",
        f"Score: {report.confirmed_count}/{report.total_count} confirmed",
        "",
    ]

    for audit in report.audits:
        lines += [
            f"## {audit.claim.text}",
            "",
            f"- verdict: `{audit.verdict.verdict}`",
            f"- confidence: `{audit.verdict.confidence:.2f}`",
            f"- tools: `{', '.join(audit.tools_used) or '-'}`",
            f"- reason: {audit.verdict.reason}",
        ]
        if audit.verdict.evidence_used:
            lines.append(f"- evidence used: {', '.join(audit.verdict.evidence_used)}")
        if audit.verdict.missing_signals:
            lines.append(f"- missing: {', '.join(audit.verdict.missing_signals)}")

        lines += ["", "Evidence:"]
        if audit.evidence:
            for item in audit.evidence:
                lines.append(f"- `{item.ref}` [{item.kind}] {item.matched_signal}: `{item.snippet}`")
        else:
            lines.append("- none")
        lines.append("")

    if report.notes:
        lines += ["## Notes", ""]
        lines += [f"- {note}" for note in report.notes]

    return "\n".join(lines).rstrip() + "\n"
