import base64
import json
import os
import urllib.error
import urllib.request

from repotruth.models import RepoMetadata
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
        metadata.default_branch = repo_data.get("default_branch")
        metadata.description = repo_data.get("description")
        metadata.languages = github_get(f"https://api.github.com/repos/{owner}/{name}/languages")
        metadata.readme = get_readme(owner, name)
    except Exception as error:
        metadata.api_error = str(error)

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
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub HTTP {error.code}: {body[:300]}") from error


def get_readme(owner, name):
    """Читает README через GitHub API."""

    data = github_get(f"https://api.github.com/repos/{owner}/{name}/readme")
    content = data.get("content")
    if not content:
        return None
    return base64.b64decode(content).decode("utf-8", errors="replace")
