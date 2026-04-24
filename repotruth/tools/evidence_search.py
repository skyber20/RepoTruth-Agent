import json
import os
import shutil
import subprocess
import tomllib
from pathlib import Path

from repotruth.models import EvidenceItem


SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".pytest_cache"}
TEXT_EXTENSIONS = {
    ".py", ".txt", ".md", ".toml", ".yml", ".yaml", ".json", ".js", ".jsx", ".ts", ".tsx",
    ".env", ".ini", ".cfg", ".dockerfile", ".sh", ".sql", ".html", ".css",
}


def search_evidence(repo_path, plan):
    """Ищет доказательства по плану."""

    root = Path(repo_path)
    evidence = []
    files = list_repo_files(root)
    dependencies = collect_dependencies(root)

    evidence.extend(find_file_evidence(root, files, plan))
    evidence.extend(find_dependency_evidence(dependencies, plan))
    evidence.extend(search_code_patterns(root, plan))

    return limit_evidence(dedupe_evidence(evidence), 80)


def list_repo_files(root):
    """Возвращает файлы репозитория."""

    result = []
    for path in root.rglob("*"):
        if should_skip(path, root):
            continue
        if path.is_file():
            result.append(path.relative_to(root).as_posix())
    return result


def should_skip(path, root):
    """Проверяет пропускаемые папки."""

    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    return any(part in SKIP_DIRS for part in relative.parts)


def find_file_evidence(root, files, plan):
    """Ищет совпадения по именам файлов."""

    evidence = []
    for file_path in files:
        lower_path = file_path.lower()
        name = Path(file_path).name.lower()
        for expected in plan.likely_files:
            expected_lower = expected.lower().strip("/")
            if not strong_file_hint(expected_lower, plan.claim_type):
                continue
            if file_matches(lower_path, name, expected_lower):
                evidence.append(file_evidence(root, file_path, expected))
    return evidence


def file_evidence(root, file_path, expected):
    """Создает evidence для найденного файла."""

    path = root / file_path
    line, snippet = first_meaningful_line(path)
    return EvidenceItem(
        kind="config" if path.name.lower() in ["dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"] else "file",
        path=file_path,
        line=line,
        snippet=snippet or f"file exists: {file_path}",
        matched_signal=f"file:{expected}",
    )


def first_meaningful_line(path):
    """Читает первую непустую строку."""

    if not path.exists() or not path.is_file() or path.stat().st_size > 1_000_000:
        return None, ""

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for index, line in enumerate(lines, start=1):
        if line.strip():
            return index, line.strip()[:300]
    return None, ""


def strong_file_hint(expected, claim_type):
    """Отсекает слишком общие имена файлов."""

    common = {"main.py", "app/main.py", "server.py", "api.py", "routers.py"}
    if expected in common:
        return claim_type in {"fastapi"}
    return True


def file_matches(lower_path, name, expected):
    """Сравнивает файл с ожидаемым шаблоном."""

    if not expected:
        return False
    if expected in lower_path or expected == name:
        return True
    if expected == "tests" and (lower_path.startswith("tests/") or "/tests/" in lower_path):
        return True
    if expected == "test_" and name.startswith("test_"):
        return True
    if expected == "_test.py" and name.endswith("_test.py"):
        return True
    return False


def collect_dependencies(root):
    """Собирает зависимости из популярных файлов."""

    dependencies = []
    dependencies.extend(read_requirements(root / "requirements.txt"))
    dependencies.extend(read_pyproject(root / "pyproject.toml"))
    dependencies.extend(read_package_json(root / "package.json"))
    return dependencies


def read_requirements(path):
    """Читает requirements.txt."""

    if not path.exists():
        return []

    result = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        clean = line.strip()
        if not clean or clean.startswith("#"):
            continue
        name = clean.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
        result.append({"name": name, "path": path.name, "line": line_number, "raw": clean})
    return result


def read_pyproject(path):
    """Читает зависимости pyproject.toml."""

    if not path.exists():
        return []

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []

    result = []
    project_dependencies = data.get("project", {}).get("dependencies", [])
    for item in project_dependencies:
        name = str(item).split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
        result.append({"name": name, "path": path.name, "line": None, "raw": str(item)})

    poetry_dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    for name, version in poetry_dependencies.items():
        if name.lower() != "python":
            result.append({"name": name, "path": path.name, "line": None, "raw": f"{name} {version}"})

    return result


def read_package_json(path):
    """Читает зависимости package.json."""

    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []

    result = []
    for group in ["dependencies", "devDependencies"]:
        for name, version in data.get(group, {}).items():
            result.append({"name": name, "path": path.name, "line": None, "raw": f"{name}: {version}"})
    return result


def find_dependency_evidence(dependencies, plan):
    """Ищет совпадения в зависимостях."""

    evidence = []
    wanted = [normalize_dep(name) for name in plan.dependency_names]
    for dependency in dependencies:
        current = normalize_dep(dependency["name"])
        for expected in wanted:
            if current == expected:
                evidence.append(
                    EvidenceItem(
                        kind="dependency",
                        path=dependency["path"],
                        line=dependency["line"],
                        snippet=dependency["raw"],
                        matched_signal=f"dependency:{dependency['name']}",
                    )
                )
    return evidence


def normalize_dep(name):
    """Нормализует имя зависимости."""

    return str(name).lower().replace("_", "-").strip()


def search_code_patterns(root, plan):
    """Ищет строки кода."""

    patterns = []
    patterns.extend(plan.code_patterns)
    patterns.extend(plan.keywords)
    patterns = [pattern for pattern in unique(patterns) if len(pattern) >= 3]

    if shutil.which("rg"):
        return rg_search(root, patterns)
    return python_search(root, patterns)


def rg_search(root, patterns):
    """Ищет через ripgrep."""

    evidence = []
    for pattern in patterns:
        command = ["rg", "-n", "-i", "-F", "--hidden"]
        for folder in SKIP_DIRS:
            command.extend(["--glob", f"!{folder}/**"])
        command.extend([pattern, str(root)])

        result = subprocess.run(command, capture_output=True, text=True, timeout=45)
        if result.returncode not in [0, 1]:
            continue

        for line in result.stdout.splitlines()[:25]:
            item = parse_rg_line(root, line, pattern)
            if item:
                evidence.append(item)

    return evidence


def parse_rg_line(root, line, pattern):
    """Парсит строку ripgrep."""

    parts = line.split(":", 2)
    if len(parts) != 3:
        return None

    path, line_number, snippet = parts
    try:
        relative = Path(path).relative_to(root).as_posix()
        number = int(line_number)
    except Exception:
        return None

    return EvidenceItem(
        kind=kind_for_path(relative, pattern),
        path=relative,
        line=number,
        snippet=snippet.strip()[:300],
        matched_signal=f"pattern:{pattern}",
    )


def python_search(root, patterns):
    """Ищет через Python, если нет rg."""

    evidence = []
    for path in root.rglob("*"):
        if should_skip(path, root) or not path.is_file() or not is_text_file(path):
            continue
        if path.stat().st_size > 1_000_000:
            continue

        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        relative = path.relative_to(root).as_posix()
        for line_number, line in enumerate(lines, start=1):
            lower_line = line.lower()
            for pattern in patterns:
                if pattern.lower() in lower_line:
                    evidence.append(
                        EvidenceItem(
                            kind=kind_for_path(relative),
                            path=relative,
                            line=line_number,
                            snippet=line.strip()[:300],
                            matched_signal=f"pattern:{pattern}",
                        )
                    )
                    break
    return evidence


def is_text_file(path):
    """Отсекает явно бинарные файлы."""

    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if path.name in ["Dockerfile", "docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"]:
        return True
    return False


def kind_for_path(path, pattern=""):
    """Определяет тип evidence по пути."""

    lower = path.lower()
    pattern_lower = str(pattern).lower()
    if "readme" in lower:
        return "readme"
    if lower.endswith((".toml", ".json", ".yml", ".yaml", ".ini", ".cfg")):
        return "config"
    if lower.endswith(".py") and ("import " in pattern_lower or "from " in pattern_lower):
        return "import"
    return "code"


def dedupe_evidence(evidence):
    """Убирает дубли evidence."""

    result = []
    seen = set()
    for item in evidence:
        key = (item.kind, item.path, item.line, item.snippet)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def limit_evidence(evidence, limit):
    """Ограничивает evidence, сохраняя порядок."""

    return evidence[:limit]


def unique(values):
    """Оставляет уникальные строки."""

    result = []
    seen = set()
    for value in values:
        item = str(value).strip()
        key = item.lower()
        if item and key not in seen:
            seen.add(key)
            result.append(item)
    return result
