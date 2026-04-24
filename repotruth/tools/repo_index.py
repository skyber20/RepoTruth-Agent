from pathlib import Path

from repotruth.models import RepoIndex
from repotruth.tools.evidence_search import collect_dependencies, is_text_file, list_repo_files


IMPORTANT_NAMES = {
    "readme.md",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    ".gitlab-ci.yml",
}


def build_repo_index(repo_path):
    """Собирает компактную карту репозитория."""

    root = Path(repo_path)
    files = list_repo_files(root)
    dependencies = collect_dependencies(root)

    return RepoIndex(
        file_count=len(files),
        files=files[:500],
        important_files=important_files(files)[:120],
        dependencies=unique([item["name"] for item in dependencies]),
    )


def important_files(files):
    """Выбирает самые полезные файлы для LLM."""

    result = []
    for file_path in files:
        name = Path(file_path).name.lower()
        lower = file_path.lower()
        if name in IMPORTANT_NAMES or lower.startswith(".github/workflows/"):
            result.append(file_path)
        elif lower.endswith((".py", ".js", ".ts", ".tsx", ".jsx")) and any(part in lower for part in ["main", "app", "bot", "api", "router", "handler", "rag", "retriever"]):
            result.append(file_path)
        elif lower.startswith("tests/") or "/tests/" in lower:
            result.append(file_path)
    return unique(result)


def repo_index_payload(index):
    """Готовит repo_index для prompt."""

    return {
        "file_count": index.file_count,
        "files": index.files[:350],
        "important_files": index.important_files[:100],
        "dependencies": index.dependencies[:120],
    }


def align_plan_with_repo(plan, index):
    """Подставляет в plan реальные файлы repo."""

    files = index.files
    matched = []
    for file_hint in plan.likely_files:
        matched.extend(match_files(file_hint, files)[:10])

    matched.extend(score_files(plan, files)[:12])
    plan.likely_files = unique(matched)[:20]
    return plan


def match_files(file_hint, files):
    """Ищет реальные файлы по подсказке."""

    hint = str(file_hint).strip().lower().strip("/")
    if not hint:
        return []

    result = []
    for file_path in files:
        lower = file_path.lower()
        name = Path(file_path).name.lower()
        if hint == lower or hint == name or hint in lower:
            result.append(file_path)
        elif hint == "tests" and (lower.startswith("tests/") or "/tests/" in lower):
            result.append(file_path)
        elif hint == "test_" and name.startswith("test_"):
            result.append(file_path)
        elif hint == "_test.py" and name.endswith("_test.py"):
            result.append(file_path)
    return result


def score_files(plan, files):
    """Находит похожие файлы по словам из плана."""

    tokens = path_tokens(plan)
    scored = []
    for file_path in files:
        lower = file_path.lower()
        if not useful_for_context(file_path):
            continue
        score = sum(1 for token in tokens if token in lower)
        if score:
            scored.append((score, file_path))

    scored.sort(key=lambda item: (-item[0], len(item[1]), item[1]))
    return [file_path for _, file_path in scored]


def path_tokens(plan):
    """Достает слова для поиска файлов."""

    values = [plan.claim_type]
    values.extend(plan.keywords)
    values.extend(plan.dependency_names)
    values.extend(plan.code_patterns)

    tokens = []
    for value in values:
        clean = str(value).lower()
        for char in ["/", "\\", "-", "_", ".", "(", ")", "@", ":", "\"", "'"]:
            clean = clean.replace(char, " ")
        for word in clean.split():
            if len(word) >= 4:
                tokens.append(word)
    return unique(tokens)


def select_context_files(plan, evidence, index):
    """Выбирает файлы, которые стоит дать verifier."""

    paths = []
    paths.extend(plan.likely_files)
    paths.extend([item.path for item in evidence if item.kind in ["code", "import", "config", "file"]])
    paths.extend(index.important_files)

    existing = set(index.files)
    return [path for path in unique(paths) if path in existing and useful_for_context(path)][:8]


def read_file_contexts(repo_path, paths, evidence=None, window=18, max_chars=8000, total_chars=30000):
    """Читает контекст вокруг evidence."""

    root = Path(repo_path)
    evidence = evidence or []
    line_map = evidence_lines_by_path(evidence)
    contexts = []
    used = 0

    for file_path in paths:
        path = root / file_path
        if not path.exists() or not path.is_file() or not is_text_file(path):
            continue
        if path.stat().st_size > 300_000:
            continue

        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        content = context_content(lines, line_map.get(file_path, []), window, max_chars)
        if not content:
            continue
        used += len(content)
        if used > total_chars:
            break

        contexts.append({"path": file_path, "content": content})

    return contexts


def evidence_lines_by_path(evidence):
    """Группирует номера строк evidence по файлам."""

    result = {}
    for item in evidence:
        if not item.line:
            continue
        result.setdefault(item.path, []).append(item.line)
    return result


def context_content(lines, target_lines, window, max_chars):
    """Готовит куски файла с номерами строк."""

    if target_lines:
        ranges = merge_ranges(context_ranges(target_lines, len(lines), window))
    else:
        ranges = [(1, min(len(lines), 120))]

    result = []
    size = 0

    for start, end in ranges:
        if result:
            result.append("...")
        for line_number in range(start, end + 1):
            row = f"{line_number}: {lines[line_number - 1]}"
            size += len(row)
            if size > max_chars:
                result.append("... файл обрезан ...")
                return "\n".join(result)
            result.append(row)

    return "\n".join(result)


def context_ranges(target_lines, total_lines, window):
    """Строит диапазоны вокруг строк evidence."""

    ranges = []
    for line_number in sorted(set(target_lines)):
        start = max(1, line_number - window)
        end = min(total_lines, line_number + window)
        ranges.append((start, end))
    return ranges


def merge_ranges(ranges):
    """Склеивает пересекающиеся диапазоны."""

    if not ranges:
        return []

    merged = [ranges[0]]
    for start, end in ranges[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end + 1:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def useful_for_context(file_path):
    """Отсекает файлы, которые не стоит читать LLM."""

    path = Path(file_path)
    name = path.name.lower()
    if name in IMPORTANT_NAMES:
        return True
    return is_text_file(path)


def unique(values):
    """Оставляет уникальные значения."""

    result = []
    seen = set()
    for value in values:
        item = str(value).strip()
        key = item.lower()
        if item and key not in seen:
            seen.add(key)
            result.append(item)
    return result
