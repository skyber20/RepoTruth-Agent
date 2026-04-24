from repotruth.patterns import fallback_extract_claims, registry_plan_for_claim
from repotruth.tools.repo_index import align_plan_with_repo, build_repo_index, read_file_contexts, select_context_files


def test_bullets_become_claims():
    text = "- Есть FastAPI backend\n- Проект запускается в Docker\n"

    claims = fallback_extract_claims(text)

    assert [claim.text for claim in claims] == ["Есть FastAPI backend", "Проект запускается в Docker"]
    assert claims[0].id == "C1"


def test_registry_detects_fastapi():
    claim = fallback_extract_claims("- Есть FastAPI backend")[0]

    plan = registry_plan_for_claim(claim)

    assert plan.claim_type == "fastapi"
    assert "fastapi" in plan.dependency_names
    assert "@app.get" in plan.code_patterns
    assert "repo_evidence_search_tool" in plan.tools
    assert "claim_verifier_tool" in plan.tools


def test_repo_index_makes_plan_use_real_files(tmp_path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "telegram_handlers.py").write_text("from aiogram import Router\nrouter = Router()\n", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("aiogram==3.0.0\n", encoding="utf-8")
    claim = fallback_extract_claims("- Есть Telegram-интеграция")[0]
    plan = registry_plan_for_claim(claim)
    index = build_repo_index(tmp_path)

    plan = align_plan_with_repo(plan, index)

    assert "src/telegram_handlers.py" in plan.likely_files
    assert "bot.py" not in plan.likely_files


def test_context_reads_relevant_file(tmp_path):
    (tmp_path / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()\n", encoding="utf-8")
    claim = fallback_extract_claims("- Есть FastAPI backend")[0]
    plan = registry_plan_for_claim(claim)
    index = build_repo_index(tmp_path)
    plan = align_plan_with_repo(plan, index)

    paths = select_context_files(plan, [], index)
    contexts = read_file_contexts(tmp_path, paths)

    assert contexts
    assert contexts[0]["path"] == "main.py"
    assert "1: from fastapi import FastAPI" in contexts[0]["content"]


def test_context_prefers_window_around_evidence(tmp_path):
    content = "\n".join([f"line {index}" for index in range(1, 81)])
    (tmp_path / "rag.py").write_text(content, encoding="utf-8")
    evidence = type("Evidence", (), {"path": "rag.py", "line": 50})()

    contexts = read_file_contexts(tmp_path, ["rag.py"], [evidence], window=2)

    assert "48: line 48" in contexts[0]["content"]
    assert "50: line 50" in contexts[0]["content"]
    assert "52: line 52" in contexts[0]["content"]
    assert "1: line 1" not in contexts[0]["content"]
