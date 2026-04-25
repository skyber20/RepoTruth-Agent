from repotruth.models import AtomicClaim, SearchPlan
from repotruth.prompts import CLAIM_EXTRACTOR_PROMPT, CLAIM_PLANNER_PROMPT


TOOLS = {"github_metadata_tool", "repo_evidence_search_tool"}


def extract_claims(text, llm):
    data = llm.complete_json(CLAIM_EXTRACTOR_PROMPT, {"text": text})
    items = data.get("claims", []) if isinstance(data, dict) else data
    if not items:
        raise RuntimeError("LLM не нашла claims в файле.")
    claims = [
        AtomicClaim(id=f"C{i}", text=str(item.get("text", "")).strip(), source_line=item.get("source_line"))
        for i, item in enumerate(items, 1)
        if str(item.get("text", "")).strip()
    ]
    if not claims:
        raise RuntimeError("LLM вернула пустые claims.")
    return claims


def plan_claim(claim, repo_index, llm):
    data = llm.complete_json(CLAIM_PLANNER_PROMPT, {"claim": claim.model_dump(), "repo_index": repo_index.model_dump()})
    if isinstance(data, list):
        data = {"claim_id": claim.id, "keywords": data, "tools": ["repo_evidence_search_tool"]}
    if not isinstance(data, dict):
        raise RuntimeError(f"LLM вернула непонятный план для claim: {claim.text}")

    plan = SearchPlan.model_validate(data)
    plan.claim_id = claim.id
    plan.tools = [tool for tool in unique(plan.tools) if tool in TOOLS] or ["repo_evidence_search_tool"]
    plan.likely_files = real_files_only(plan.likely_files, repo_index.files)
    plan.keywords = unique(plan.keywords)
    plan.dependency_names = unique(plan.dependency_names)
    plan.code_patterns = unique(plan.code_patterns)
    plan.strong_signals = unique(plan.strong_signals)
    return plan


def real_files_only(hints, files):
    result = []
    for hint in hints:
        clean = str(hint).lower().strip("/")
        for file_path in files:
            lower = file_path.lower()
            if clean == lower or clean == lower.split("/")[-1] or clean in lower:
                result.append(file_path)
    return unique(result)


def unique(values):
    result = []
    seen = set()
    for value in values:
        text = str(value).strip()
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            result.append(text)
    return result
