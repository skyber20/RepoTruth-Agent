from repotruth.models import AtomicClaim, SearchPlan
from repotruth.patterns import fallback_extract_claims, merge_plans, registry_plan_for_claim
from repotruth.prompts import CLAIM_EXTRACTOR_PROMPT, CLAIM_PLANNER_PROMPT
from repotruth.tools.repo_index import align_plan_with_repo, repo_index_payload


def extract_claims(text, llm=None):
    """Достает атомарные claims."""

    local_claims = fallback_extract_claims(text)
    if not llm or not llm.available:
        return local_claims, False

    data = llm.try_complete_json(CLAIM_EXTRACTOR_PROMPT, {"text": text})
    if not data:
        return local_claims, False

    try:
        claims = [AtomicClaim.model_validate(item) for item in data.get("claims", [])]
    except Exception:
        return local_claims, False

    if not claims:
        return local_claims, False

    return normalize_claim_ids(claims), True


def plan_claim(claim, repo_index=None, llm=None):
    """Строит план поиска evidence."""

    local_plan = registry_plan_for_claim(claim)
    if repo_index:
        local_plan = align_plan_with_repo(local_plan, repo_index)

    if not llm or not llm.available:
        return local_plan, False

    payload = {"claim": claim.model_dump()}
    if repo_index:
        payload["repo_index"] = repo_index_payload(repo_index)

    data = llm.try_complete_json(CLAIM_PLANNER_PROMPT, payload)
    if not data:
        return local_plan, False

    try:
        llm_plan = SearchPlan.model_validate(data)
    except Exception:
        return local_plan, False

    llm_plan.claim_id = claim.id
    plan = merge_plans(local_plan, llm_plan)
    if repo_index:
        plan = align_plan_with_repo(plan, repo_index)
    return plan, True


def normalize_claim_ids(claims):
    """Делает id предсказуемыми."""

    result = []
    for index, claim in enumerate(claims, start=1):
        result.append(AtomicClaim(id=f"C{index}", text=claim.text, source_line=claim.source_line))
    return result
