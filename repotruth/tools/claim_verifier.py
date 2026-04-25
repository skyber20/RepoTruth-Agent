from repotruth.models import ClaimVerdict
from repotruth.prompts import CLAIM_VERIFIER_PROMPT


def verify_claim(claim, plan, evidence, llm):
    payload = {
        "claim": claim.model_dump(),
        "plan": plan.model_dump(),
        "evidence": [item.model_dump() | {"ref": item.ref} for item in evidence],
        "allowed_refs": [item.ref for item in evidence],
    }
    data = llm.complete_json(CLAIM_VERIFIER_PROMPT, payload)
    verdict = ClaimVerdict.model_validate(data)
    verdict.verdict = verdict.verdict if verdict.verdict in {"confirmed", "partial", "missing"} else "missing"
    verdict.evidence_used = [ref for ref in verdict.evidence_used if ref in payload["allowed_refs"]]
    if verdict.verdict == "missing":
        verdict.evidence_used = []
    return verdict
