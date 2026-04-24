from repotruth.models import AtomicClaim
from repotruth.patterns import registry_plan_for_claim
from repotruth.tools.evidence_search import search_evidence


def test_fastapi_evidence_has_path_and_line(tmp_path):
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (tmp_path / "requirements.txt").write_text("fastapi==0.1.0\n", encoding="utf-8")
    (app_dir / "main.py").write_text(
        "from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/health')\ndef health():\n    return {'ok': True}\n",
        encoding="utf-8",
    )
    claim = AtomicClaim(id="C1", text="Есть FastAPI backend")
    plan = registry_plan_for_claim(claim)

    evidence = search_evidence(tmp_path, plan)
    refs = [item.ref for item in evidence]

    assert "requirements.txt:1" in refs
    assert "app/main.py:1" in refs


def test_dockerfile_becomes_evidence(tmp_path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    claim = AtomicClaim(id="C1", text="Проект запускается в Docker")
    plan = registry_plan_for_claim(claim)

    evidence = search_evidence(tmp_path, plan)

    assert any(item.path == "Dockerfile" for item in evidence)
