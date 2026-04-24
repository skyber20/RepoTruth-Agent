from repotruth.models import AtomicClaim
from repotruth.patterns import registry_plan_for_claim
from repotruth.tools.claim_verifier import verify_by_rules, verify_claim
from repotruth.tools.evidence_search import search_evidence


def test_fastapi_rule_verdict_confirmed(tmp_path):
    (tmp_path / "requirements.txt").write_text("fastapi==0.1.0\n", encoding="utf-8")
    (tmp_path / "main.py").write_text(
        "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/')\ndef root():\n    return {}\n",
        encoding="utf-8",
    )
    claim = AtomicClaim(id="C1", text="Есть FastAPI backend")
    plan = registry_plan_for_claim(claim)
    evidence = search_evidence(tmp_path, plan)

    verdict = verify_by_rules(plan, evidence)

    assert verdict.verdict == "confirmed"
    assert verdict.evidence_used


def test_missing_when_no_evidence():
    claim = AtomicClaim(id="C1", text="Есть Telegram-интеграция")
    plan = registry_plan_for_claim(claim)

    verdict = verify_by_rules(plan, [])

    assert verdict.verdict == "missing"


def test_verifier_drops_fake_llm_refs():
    class FakeLLM:
        available = True

        def try_complete_json(self, prompt, payload):
            return {
                "verdict": "confirmed",
                "confidence": 0.99,
                "reason": "fake",
                "evidence_used": ["fake.py:1"],
                "missing_signals": [],
            }

    claim = AtomicClaim(id="C1", text="Есть тесты")
    plan = registry_plan_for_claim(claim)

    verdict = verify_claim(claim, plan, [], [], FakeLLM())

    assert verdict.verdict == "missing"
    assert verdict.evidence_used == []
