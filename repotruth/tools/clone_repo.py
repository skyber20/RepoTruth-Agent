import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse


def parse_github_url(repo_url):
    """Достает owner и repo из GitHub URL."""

    parsed = urlparse(repo_url)
    if parsed.netloc.lower() != "github.com":
        return None, None

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return None, None

    name = parts[1]
    if name.endswith(".git"):
        name = name[:-4]

    return parts[0], name


def clone_repo(repo_url, target_dir):
    """Клонирует публичный репозиторий."""

    source = Path(repo_url).expanduser()
    if source.exists() and source.is_dir():
        return source

    if not shutil.which("git"):
        raise RuntimeError("git не найден. Установи git и повтори запуск.")

    target = Path(target_dir)
    command = ["git", "clone", "--depth", "1", repo_url, str(target)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"Не удалось клонировать репозиторий: {message}")

    return target
