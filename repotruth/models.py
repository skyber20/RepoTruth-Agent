from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    model_config = ConfigDict(extra="ignore")


class AtomicClaim(Model):
    id: str
    text: str
    source_line: int | None = None


class SearchPlan(Model):
    claim_id: str
    claim_type: str = "unknown"
    keywords: list[str] = Field(default_factory=list)
    likely_files: list[str] = Field(default_factory=list)
    dependency_names: list[str] = Field(default_factory=list)
    code_patterns: list[str] = Field(default_factory=list)
    strong_signals: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class EvidenceItem(Model):
    kind: str
    path: str
    snippet: str
    matched_signal: str
    line: int | None = None

    @property
    def ref(self):
        return f"{self.path}:{self.line}" if self.line else self.path


class ClaimVerdict(Model):
    verdict: str
    confidence: float
    reason: str
    evidence_used: list[str] = Field(default_factory=list)
    missing_signals: list[str] = Field(default_factory=list)


class RepoMetadata(Model):
    url: str
    owner: str | None = None
    name: str | None = None
    description: str | None = None
    stars: int | None = None
    forks: int | None = None
    license: str | None = None
    topics: list[str] = Field(default_factory=list)
    languages: dict[str, int] = Field(default_factory=dict)
    api_error: str | None = None


class RepoIndex(Model):
    files: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class ClaimAudit(Model):
    claim: AtomicClaim
    plan: SearchPlan
    evidence: list[EvidenceItem]
    verdict: ClaimVerdict
    tools_used: list[str]


class AuditReport(Model):
    repo_url: str
    generated_at: str
    metadata: RepoMetadata
    audits: list[ClaimAudit]
    llm_model: str | None = None
    notes: list[str] = Field(default_factory=list)

    @property
    def total_count(self):
        return len(self.audits)

    @property
    def confirmed_count(self):
        return sum(a.verdict.verdict == "confirmed" for a in self.audits)

    @property
    def supported_count(self):
        return sum(a.verdict.verdict in {"confirmed", "partial"} for a in self.audits)
