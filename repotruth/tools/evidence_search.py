import json
import tomllib
from pathlib import Path

from repotruth.models import EvidenceItem, RepoIndex


SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build"}
TEXT_EXTENSIONS = {".py", ".md", ".txt", ".toml", ".json", ".yml", ".yaml", ".js", ".ts", ".tsx", ".jsx", ".env"}


def build_repo_index(repo_path):
    root = Path(repo_path)
    return RepoIndex(files=list_files(root), dependencies=[d["name"] for d in read_dependencies(root)])


def search_evidence(repo_path, plan):
    root = Path(repo_path)
    dependencies = read_dependencies(root)
    evidence = []
    evidence += file_evidence(root, plan)
    evidence += dependency_evidence(plan, dependencies)
    evidence += text_evidence(root, plan)
    return dedupe(evidence)


def list_files(root):
    files = []
    for path in root.rglob("*"):
        if path.is_file() and not skipped(path, root):
            files.append(path.relative_to(root).as_posix())
    return files


def skipped(path, root):
    return any(part in SKIP_DIRS for part in path.relative_to(root).parts)


def file_evidence(root, plan):
    evidence = []
    files = list_files(root)
    hints = [h.lower().strip("/") for h in plan.likely_files]
    for file_path in files:
        lower = file_path.lower()
        name = Path(file_path).name.lower()
        if any(h and (h == lower or h == name or h in lower) for h in hints):
            snippet = first_line(root / file_path) or f"file exists: {file_path}"
            evidence.append(EvidenceItem(kind=kind_for_file(file_path), path=file_path, snippet=snippet, matched_signal="file"))
    return evidence


def dependency_evidence(plan, dependencies):
    wanted = {clean_dep(name) for name in plan.dependency_names}
    evidence = []
    for dep in dependencies:
        if clean_dep(dep["name"]) in wanted:
            evidence.append(
                EvidenceItem(
                    kind="dependency",
                    path=dep["path"],
                    line=dep.get("line"),
                    snippet=dep["raw"],
                    matched_signal=f"dependency:{dep['name']}",
                )
            )
    return evidence


def text_evidence(root, plan):
    needles = unique(plan.code_patterns + plan.keywords)
    if not needles:
        return []

    evidence = []
    for file_path in list_files(root):
        path = root / file_path
        if not text_file(path):
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            lower = line.lower()
            for needle in needles:
                if needle.lower() in lower:
                    evidence.append(
                        EvidenceItem(
                            kind=kind_for_file(file_path),
                            path=file_path,
                            line=line_number,
                            snippet=line.strip()[:240],
                            matched_signal=f"pattern:{needle}",
                        )
                    )
                    break
    return evidence


def read_dependencies(root):
    deps = []
    deps += requirements(root / "requirements.txt")
    deps += pyproject(root / "pyproject.toml")
    deps += package_json(root / "package.json")
    return deps


def requirements(path):
    if not path.exists():
        return []
    deps = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        raw = line.strip()
        if raw and not raw.startswith("#"):
            deps.append({"name": clean_req(raw), "path": path.name, "line": line_number, "raw": raw})
    return deps


def pyproject(path):
    if not path.exists():
        return []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []
    return [{"name": clean_req(dep), "path": path.name, "raw": str(dep)} for dep in data.get("project", {}).get("dependencies", [])]


def package_json(path):
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []
    deps = []
    for group in ("dependencies", "devDependencies"):
        for name, version in data.get(group, {}).items():
            deps.append({"name": name, "path": path.name, "raw": f"{name}: {version}"})
    return deps


def clean_req(raw):
    return str(raw).split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()


def clean_dep(name):
    return str(name).lower().replace("_", "-").strip()


def text_file(path):
    return path.suffix.lower() in TEXT_EXTENSIONS or path.suffix == ""


def first_line(path):
    if not text_file(path):
        return ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            return line.strip()[:240]
    return ""


def kind_for_file(path):
    name = Path(path).name.lower()
    if "readme" in name:
        return "readme"
    if Path(path).suffix.lower() in {".toml", ".json", ".yml", ".yaml"} or Path(path).suffix == "":
        return "config"
    return "code"


def dedupe(items):
    result = []
    seen = set()
    for item in items:
        key = (item.path, item.line, item.snippet)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


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
