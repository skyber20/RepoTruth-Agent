from pydantic import BaseModel, ConfigDict, Field


class AtomicClaim(BaseModel):
    """Одно проверяемое утверждение."""

    model_config = ConfigDict(extra="ignore")

    id: str
    text: str
    source_line: int | None = None


class SearchPlan(BaseModel):
    """План поиска доказательств."""

    model_config = ConfigDict(extra="ignore")

    claim_id: str
    claim_type: str = "unknown"
    keywords: list[str] = Field(default_factory=list)
    likely_files: list[str] = Field(default_factory=list)
    dependency_names: list[str] = Field(default_factory=list)
    code_patterns: list[str] = Field(default_factory=list)
    strong_signals: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    """Найденное доказательство."""

    model_config = ConfigDict(extra="ignore")

    kind: str
    path: str
    line: int | None = None
    snippet: str
    matched_signal: str

    @property
    def ref(self):
        if self.line:
            return f"{self.path}:{self.line}"
        return self.path


class ClaimVerdict(BaseModel):
    """Вердикт по одному утверждению."""

    model_config = ConfigDict(extra="ignore")

    verdict: str
    confidence: float
    reason: str
    evidence_used: list[str] = Field(default_factory=list)
    missing_signals: list[str] = Field(default_factory=list)
    llm_used: bool = False


class RepoMetadata(BaseModel):
    """Краткая информация о репозитории."""

    model_config = ConfigDict(extra="ignore")

    url: str
    owner: str | None = None
    name: str | None = None
    default_branch: str | None = None
    description: str | None = None
    languages: dict[str, int] = Field(default_factory=dict)
    readme: str | None = None
    api_error: str | None = None


class RepoIndex(BaseModel):
    """Карта реальных файлов репозитория."""

    model_config = ConfigDict(extra="ignore")

    file_count: int
    files: list[str] = Field(default_factory=list)
    important_files: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class ClaimAudit(BaseModel):
    """Полная проверка одного утверждения."""

    model_config = ConfigDict(extra="ignore")

    claim: AtomicClaim
    plan: SearchPlan
    evidence: list[EvidenceItem] = Field(default_factory=list)
    verdict: ClaimVerdict
    tools_used: list[str] = Field(default_factory=list)


class AuditReport(BaseModel):
    """Итоговый отчет аудита."""

    model_config = ConfigDict(extra="ignore")

    repo_url: str
    generated_at: str
    metadata: RepoMetadata
    audits: list[ClaimAudit] = Field(default_factory=list)
    llm_model: str | None = None
    notes: list[str] = Field(default_factory=list)

    @property
    def total_count(self):
        return len(self.audits)

    @property
    def confirmed_count(self):
        return sum(1 for audit in self.audits if audit.verdict.verdict == "confirmed")

    @property
    def partial_count(self):
        return sum(1 for audit in self.audits if audit.verdict.verdict == "partial")

    @property
    def missing_count(self):
        return sum(1 for audit in self.audits if audit.verdict.verdict == "missing")

    @property
    def supported_count(self):
        return self.confirmed_count + self.partial_count
