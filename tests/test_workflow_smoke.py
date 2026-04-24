from repotruth.workflow import run_audit


def test_workflow_writes_reports_for_local_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "requirements.txt").write_text("fastapi==0.115.0\n", encoding="utf-8")
    (repo / "main.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef root():\n    return {}\n",
        encoding="utf-8",
    )
    (repo / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    claims = tmp_path / "claims.md"
    claims.write_text(
        "- Есть FastAPI backend\n- Проект запускается в Docker\n- Есть тесты\n",
        encoding="utf-8",
    )

    report, markdown_path, json_path = run_audit(str(repo), claims, tmp_path / "out", no_llm=True)

    assert report.confirmed_count >= 2
    assert report.missing_count >= 1
    assert all(audit.tools_used for audit in report.audits)
    assert markdown_path.exists()
    assert json_path.exists()
