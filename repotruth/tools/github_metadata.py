import json
import os
import urllib.error
import urllib.request

from repotruth.models import EvidenceItem, RepoMetadata
from repotruth.tools.clone_repo import parse_github_url


def get_github_metadata(repo_url):
    """Пробует получить metadata через GitHub API."""

    owner, name = parse_github_url(repo_url)
    metadata = RepoMetadata(url=repo_url, owner=owner, name=name)
    if not owner or not name:
        metadata.api_error = "Это не GitHub URL."
        return metadata

    try:
        repo_data = github_get(f"https://api.github.com/repos/{owner}/{name}")
    except Exception as error:
        metadata.api_error = str(error)
        return metadata

    metadata.default_branch = repo_data.get("default_branch")
    metadata.description = repo_data.get("description")
    metadata.stars = repo_data.get("stargazers_count")
    metadata.forks = repo_data.get("forks_count")
    metadata.license = (repo_data.get("license") or {}).get("spdx_id")
    metadata.topics = repo_data.get("topics") or []

    try:
        metadata.languages = github_get(f"https://api.github.com/repos/{owner}/{name}/languages")
    except Exception:
        metadata.languages = {}

    return metadata


def github_get(url):
    """Делает простой GET к GitHub API."""

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "RepoTruth-Agent",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub HTTP {error.code}: {body[:300]}") from error


def metadata_to_evidence(metadata):
    """Превращает ответ GitHub API в короткие evidence items."""

    if metadata.api_error:
        return []

    repo_ref = f"GitHub API /repos/{metadata.owner}/{metadata.name}"
    evidence = [
        EvidenceItem(
            kind="api",
            path=repo_ref,
            snippet=repo_summary(metadata),
            matched_signal="github:repo_metadata",
        )
    ]

    if metadata.languages:
        evidence.append(
            EvidenceItem(
                kind="api",
                path=f"{repo_ref}/languages",
                snippet=", ".join(f"{name}: {bytes_count}" for name, bytes_count in metadata.languages.items()),
                matched_signal="github:languages",
            )
        )

    return evidence


def repo_summary(metadata):
    """Сжимает metadata в одну строку для verifier и отчета."""

    parts = [
        f"default_branch={metadata.default_branch}",
        f"stars={metadata.stars}",
        f"forks={metadata.forks}",
        f"license={metadata.license}",
    ]
    if metadata.description:
        parts.append(f"description={metadata.description}")
    if metadata.topics:
        parts.append(f"topics={', '.join(metadata.topics[:10])}")
    return "; ".join(part for part in parts if part and not part.endswith("=None"))
