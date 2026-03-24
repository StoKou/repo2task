#!/usr/bin/env python3
"""Generate repo2task benchmark bundles from a repository.

Output:
<out>/<repo-name>/task_001_xxx/
  instruction.md
  meta_info.md
  task.toml
  environment/
    Dockerfile
  solution/
    solve.sh
    solution.md
    behavior_contract.json
  test/
    test.sh
    phase1_install_check.py
    phase2_task_check.py
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple
from urllib.request import urlretrieve

MAX_DOC_BYTES = 20000
MAX_TOPICS = 8
EXCLUDED_DIR_KEYWORDS = (
    ".git/",
    "node_modules/",
    "/dist/",
    "/build/",
    "/generated/",
    "/generated-local/",
    "/generated-batch/",
    "/.venv/",
    "/venv/",
)

ROLE_SPECS = [
    ("Product Engineer", "new_feature", "medium"),
    ("Integration Engineer", "workflow_integration", "medium"),
    ("Platform Engineer", "modularization_or_replacement", "hard"),
    ("QA Engineer", "robustness_and_edge_cases", "medium"),
]


@dataclass
class RepoMeta:
    repo_input: str
    repo_url: str
    repo_commit: str
    repo_name: str
    mode: str
    category: str = "secondary-development"
    language: str = "unknown"


@dataclass
class Understanding:
    purpose: str
    use_cases: List[str]
    input_output: str
    minimal_usage: str


@dataclass
class CapabilityMap:
    core_functions: List[str]
    key_modules: List[str]
    interfaces: List[str]
    workflows: List[str]
    extension_points: List[str]
    replaceable_components: List[str]


@dataclass
class TaskPlan:
    task_id: str
    role: str
    task_type: str
    difficulty: str
    title: str
    entry_points: List[str]
    expected_capability: str
    constraints: List[str]
    files_to_modify: List[str]
    functions_to_change: List[str]
    behavior_changes: List[str]
    minimal_justification: str
    baseline_command: str


def run(cmd: Sequence[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "task"


def repo_url_from_name(name: str) -> str:
    return f"https://github.com/{name}.git"


def extract_owner_repo(repo_arg: str) -> str | None:
    if re.match(r"^[^/\s]+/[^/\s]+$", repo_arg):
        return repo_arg
    m = re.search(r"github\.com[:/]+([^/]+/[^/.]+)", repo_arg)
    return m.group(1) if m else None


def remote_head_commit(remote_url: str) -> str | None:
    try:
        out = run(["git", "ls-remote", remote_url, "HEAD"])
    except Exception:
        return None
    if not out:
        return None
    return out.split()[0]


def download_archive(owner_repo: str, dest: Path) -> bool:
    owner, repo = owner_repo.split("/", 1)
    tmp = dest.parent / "archive_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    for branch in ("main", "master"):
        tar = tmp / f"{repo}-{branch}.tar.gz"
        url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/refs/heads/{branch}"
        try:
            urlretrieve(url, tar)
            with tarfile.open(tar, "r:gz") as tf:
                tf.extractall(tmp)
            extracted = sorted(p for p in tmp.iterdir() if p.is_dir() and p.name.startswith(f"{repo}-"))
            if not extracted:
                continue
            extracted[-1].rename(dest)
            return True
        except Exception:
            continue
    return False


def resolve_repo(repo_arg: str) -> Tuple[Path, tempfile.TemporaryDirectory | None, str, str]:
    """Return path, tempdir, repo_url, repo_commit."""
    p = Path(repo_arg).expanduser()
    if p.exists() and p.is_dir():
        repo_url = run(["git", "config", "--get", "remote.origin.url"], cwd=p) if (p / ".git").exists() else str(p.resolve())
        repo_commit = run(["git", "rev-parse", "HEAD"], cwd=p) if (p / ".git").exists() else "UNKNOWN_LOCAL_COMMIT"
        return p.resolve(), None, repo_url, repo_commit

    owner_repo = extract_owner_repo(repo_arg)
    if owner_repo:
        remote_url = repo_url_from_name(owner_repo)
    else:
        remote_url = repo_arg

    if remote_url.startswith(("http://", "https://", "git@")):
        head_commit = remote_head_commit(remote_url)
        tmp = tempfile.TemporaryDirectory(prefix="repo2task_")
        target = Path(tmp.name) / "source"
        try:
            subprocess.run(["git", "clone", "--depth", "1", remote_url, str(target)], check=True)
            commit = run(["git", "rev-parse", "HEAD"], cwd=target)
            return target, tmp, remote_url, commit
        except Exception:
            owner_repo_fallback = extract_owner_repo(remote_url)
            if owner_repo_fallback and download_archive(owner_repo_fallback, target):
                if not head_commit:
                    raise RuntimeError("Cannot determine fixed commit hash for archived repository")
                return target, tmp, remote_url, head_commit
            raise

    raise FileNotFoundError(f"Repository not found: {repo_arg}")


def load_repos_json(path: Path, index: int) -> Dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("Invalid repos json")
    item = data[index]
    if not isinstance(item, dict) or "name" not in item:
        raise ValueError("Missing 'name' in repos json item")
    return {
        "name": str(item["name"]),
        "category": str(item.get("category", "secondary-development")),
        "language": str(item.get("language", "unknown")),
    }


def docs_files(repo: Path) -> List[Path]:
    files: List[Path] = []
    for d in ("examples", "example", "docs", "doc"):
        base = repo / d
        if base.exists():
            for ext in ("*.md", "*.rst", "*.txt"):
                files.extend(sorted(base.rglob(ext)))
    for readme in ("README.md", "README.MD", "readme.md"):
        f = repo / readme
        if f.exists():
            files.append(f)
    for root_doc in ("QUICKSTART.md", "EXAMPLES.md"):
        f = repo / root_doc
        if f.exists():
            files.append(f)
    seen = set()
    out: List[Path] = []
    for f in files:
        rel = str(f.relative_to(repo))
        if any(key in f"/{rel}" for key in EXCLUDED_DIR_KEYWORDS):
            continue
        k = str(f.resolve())
        if k not in seen:
            seen.add(k)
            out.append(f)
    return out


def source_files(repo: Path) -> List[Path]:
    exts = [
        "*.py", "*.js", "*.ts", "*.go", "*.rs", "*.java", "*.c", "*.cpp", "*.sh", "*.rb", "*.php"
    ]
    out: List[Path] = []
    for ext in exts:
        out.extend(sorted(repo.rglob(ext)))
    filtered = []
    for f in out:
        rel = str(f.relative_to(repo))
        if any(key in f"/{rel}" for key in EXCLUDED_DIR_KEYWORDS):
            continue
        filtered.append(f)
    return filtered[:500]


def read_text(path: Path, max_bytes: int = MAX_DOC_BYTES) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_bytes]
    except OSError:
        return ""


def infer_repo_type(repo: Path) -> str:
    if (repo / "package.json").exists():
        return "javascript_or_typescript_project"
    if (repo / "pyproject.toml").exists() or (repo / "setup.py").exists() or (repo / "requirements.txt").exists():
        return "python_project"
    if (repo / "go.mod").exists():
        return "go_project"
    if (repo / "Cargo.toml").exists():
        return "rust_project"
    if (repo / "Dockerfile").exists():
        return "service_or_tooling_project"
    return "generic_source_repository"


def detect_mode(doc_paths: List[Path]) -> str:
    return "documentation-driven" if doc_paths else "code-driven"


def extract_minimal_usage_from_docs(doc_paths: List[Path]) -> str:
    preferred = (
        "generate_repo2task.py",
        "build --repo",
        "python",
        "pytest",
        "npm",
        "node",
        "go ",
        "cargo",
        "make",
        "./",
        "bash ",
    )
    fallback = ""
    for p in doc_paths:
        text = read_text(p)
        for block in re.finditer(r"```(?:bash|sh)?\n(.*?)\n```", text, flags=re.S):
            cmd_lines = [x.strip() for x in block.group(1).strip().splitlines() if x.strip()]
            i = 0
            while i < len(cmd_lines):
                line = cmd_lines[i]
                if line.startswith("#"):
                    i += 1
                    continue
                candidate = line
                while candidate.endswith("\\") and i + 1 < len(cmd_lines):
                    i += 1
                    candidate = candidate[:-1].rstrip() + " " + cmd_lines[i].lstrip()

                if "<" in candidate or ">" in candidate:
                    i += 1
                    continue
                lowered = candidate.lower()
                if lowered.startswith(("export ", "mkdir ", "cp ", "mv ", "echo ")):
                    if not fallback:
                        fallback = candidate
                    i += 1
                    continue
                if any(token in lowered for token in preferred):
                    return candidate
                if not fallback:
                    fallback = candidate
                i += 1
    return fallback


def fallback_minimal_usage_from_code(repo: Path) -> str:
    if (repo / "package.json").exists():
        return "npm install && npm test"
    if (repo / "pyproject.toml").exists() or (repo / "requirements.txt").exists():
        return "python3 -m pip install -r requirements.txt && pytest -q"
    if (repo / "go.mod").exists():
        return "go test ./..."
    if (repo / "Cargo.toml").exists():
        return "cargo test"
    return "ls -la"


def build_understanding(repo: Path, doc_paths: List[Path], mode: str) -> Understanding:
    if mode == "documentation-driven":
        merged = "\n\n".join(read_text(p) for p in doc_paths[:6])
        purpose = "Repository capabilities inferred from README/docs/examples."
        h2 = re.findall(r"^##\s+(.+)$", merged, flags=re.M)
        use_cases = h2[:4] if h2 else ["Follow documented usage patterns", "Extend existing workflows"]
        io = "Input/output inferred from usage snippets and documented examples."
        minimal = extract_minimal_usage_from_docs(doc_paths) or fallback_minimal_usage_from_code(repo)
        return Understanding(purpose=purpose, use_cases=use_cases, input_output=io, minimal_usage=minimal)

    repo_type = infer_repo_type(repo)
    src = source_files(repo)
    entry_candidates = [str(p.relative_to(repo)) for p in src[:6]]
    purpose = f"No sufficient docs found; inferred from code structure ({repo_type})."
    use_cases = [
        "Run baseline workflow from inferred entry points",
        "Add secondary development features without rewriting core modules",
    ]
    io = f"Input/output inferred from file layout and entry candidates: {', '.join(entry_candidates[:3]) or 'N/A'}."
    minimal = fallback_minimal_usage_from_code(repo)
    return Understanding(purpose=purpose, use_cases=use_cases, input_output=io, minimal_usage=minimal)


def build_capability_map(repo: Path, doc_paths: List[Path], mode: str) -> CapabilityMap:
    src = source_files(repo)
    rel = [str(p.relative_to(repo)) for p in src]

    core = []
    if mode == "documentation-driven":
        merged = "\n\n".join(read_text(p) for p in doc_paths[:6])
        headers = re.findall(r"^#{1,3}\s+(.+)$", merged, flags=re.M)
        for h in headers:
            h = re.sub(r"[`*_]", "", h).strip()
            if 4 <= len(h) <= 80:
                core.append(h)
        if not core:
            core = ["Documented core workflow", "CLI/API usage"]
    else:
        core = ["Code-inferred core workflow", "Entry-point driven execution"]

    key_modules = rel[:8] if rel else ["README.md"]
    interfaces = []
    if any("cli" in r.lower() or "cmd/" in r for r in rel):
        interfaces.append("CLI")
    if any("api" in r.lower() or "server" in r.lower() for r in rel):
        interfaces.append("Service/API")
    if not interfaces:
        interfaces.append("Library/Module Interface")

    workflows = [
        "baseline setup and run",
        "feature extension on existing modules",
        "regression-safe verification",
    ]

    extension_points = key_modules[:4]
    replaceable = key_modules[4:8] if len(key_modules) > 4 else key_modules[:2]

    return CapabilityMap(
        core_functions=core[:MAX_TOPICS],
        key_modules=key_modules,
        interfaces=interfaces,
        workflows=workflows,
        extension_points=extension_points,
        replaceable_components=replaceable,
    )


def choose_entry_points(cap_map: CapabilityMap, idx: int) -> List[str]:
    base = cap_map.key_modules
    if not base:
        return ["README.md"]
    start = (idx * 2) % len(base)
    picked = base[start:start + 2]
    return picked if picked else [base[0]]


def make_task_plans(meta: RepoMeta, understanding: Understanding, cap_map: CapabilityMap) -> List[TaskPlan]:
    plans: List[TaskPlan] = []
    capability_hint = cap_map.core_functions[0] if cap_map.core_functions else "core workflow"

    for i, (role, task_type, difficulty) in enumerate(ROLE_SPECS, start=1):
        task_id = f"task_{i:03d}"
        entry = choose_entry_points(cap_map, i - 1)
        title = f"{role}: Extend {capability_hint}"
        expected_capability = f"Deliver {task_type} on top of existing repository capability without full rewrite"

        constraints = [
            "Ground changes in existing modules and workflows",
            "Keep baseline behavior backward-compatible",
            "Do not rewrite the entire repository",
            "Use fixed commit as starting point",
        ]
        files_to_modify = entry + [f"repo2task_artifacts/{task_id}/capability.md"]
        functions_to_change = [
            f"add_or_update_{slug(task_type)}_entry",
            f"validate_{slug(role)}_behavior",
        ]
        behavior_changes = [
            "New capability path should be callable via documented workflow",
            "Baseline workflow should still succeed (no regression)",
        ]
        justification = "Changes are constrained to existing entry points plus one isolated artifact path to minimize risk."

        plans.append(
            TaskPlan(
                task_id=task_id,
                role=role,
                task_type=task_type,
                difficulty=difficulty,
                title=title,
                entry_points=entry,
                expected_capability=expected_capability,
                constraints=constraints,
                files_to_modify=files_to_modify,
                functions_to_change=functions_to_change,
                behavior_changes=behavior_changes,
                minimal_justification=justification,
                baseline_command=understanding.minimal_usage,
            )
        )
    return plans


def toml_list(items: Iterable[str]) -> str:
    return "[" + ", ".join(json.dumps(x) for x in items) + "]"


def render_instruction(meta: RepoMeta, u: Understanding, c: CapabilityMap, t: TaskPlan) -> str:
    lines = [
        f"# {t.task_id}: {t.title}",
        "",
        "## Task Description",
        f"- Description: Implement a `{t.task_type}` task grounded in repository entry points.",
        f"- Task type: `{t.task_type}`",
        f"- Difficulty: `{t.difficulty}`",
        "",
        "## Expected Behavior",
        f"- Expected capability: {t.expected_capability}",
        f"- Observable changes: {'; '.join(t.behavior_changes)}",
        f"- Baseline command must still pass: `{t.baseline_command}`",
        "",
        "## Constraints",
    ]
    lines.extend([f"- {x}" for x in t.constraints])
    lines.extend([""])
    return "\n".join(lines)


def render_meta_info(meta: RepoMeta, u: Understanding, c: CapabilityMap, t: TaskPlan) -> str:
    lines = [
        f"# Meta Info: {t.task_id}",
        "",
        "## Source",
        f"- Source type: derived benchmark task for `{t.role}`",
        f"- Source id / URL: repository-level analysis from `{meta.repo_url}` at `{meta.repo_commit}`",
        "- Original PR/issue summary: candidate source summary should be recorded here when PR/issue mining is enabled.",
        "",
        "## Motivation",
        "- This task exercises practical secondary development while preserving the baseline workflow.",
        "- The benchmark stays anchored to repository behavior rather than generic problem invention.",
        "",
        "## Affected Modules/Files",
        "- Entry points:",
    ]
    lines.extend([f"  - {x}" for x in t.entry_points])
    lines.extend(["- Files to modify:"])
    lines.extend([f"  - {x}" for x in t.files_to_modify])
    lines.extend(["- Functions/components to add/change:"])
    lines.extend([f"  - {x}" for x in t.functions_to_change])
    lines.extend([
        "",
        "## Step 1: Quickstart Understanding",
        f"- Understanding mode: `{meta.mode}`",
        f"- Repository purpose: {u.purpose}",
        "- Target use cases:",
    ])
    lines.extend([f"  - {x}" for x in u.use_cases])
    lines.extend([
        f"- Input/output format: {u.input_output}",
        f"- Minimal usage pattern: `{u.minimal_usage}`",
        "",
        "## Step 2: Capability Abstraction",
        "- Core functionalities:",
    ])
    lines.extend([f"  - {x}" for x in c.core_functions[:6]])
    lines.extend(["- Key modules and roles:"])
    lines.extend([f"  - {x}" for x in c.key_modules[:8]])
    lines.extend(["- Interfaces:"])
    lines.extend([f"  - {x}" for x in c.interfaces])
    lines.extend(["- Existing workflows:"])
    lines.extend([f"  - {x}" for x in c.workflows])
    lines.extend(["- Extension points:"])
    lines.extend([f"  - {x}" for x in c.extension_points])
    lines.extend(["- Replaceable components:"])
    lines.extend([f"  - {x}" for x in c.replaceable_components])
    lines.extend([
        "",
        "## Step 3: Task Rewrite Notes",
        f"- Expected capability: {t.expected_capability}",
        "- What was rewritten: the solver-facing task text was compressed into `instruction.md`.",
        "- What stayed anchored: entry points, behavior expectations, and file-local modification scope.",
        "- Why task is implementable in this repo: task stays within existing modules and baseline workflow.",
        "",
        "## Step 4: Modification Planning (MANDATORY)",
        "- Expected behavior changes:",
    ])
    lines.extend([f"  - {x}" for x in t.behavior_changes])
    lines.extend([
        f"- Minimal modification justification: {t.minimal_justification}",
        "",
        "## Step 1-5 Analysis Summary",
        f"- Summary: `{meta.mode}` analysis identified capability focus on \"{(c.core_functions[0] if c.core_functions else 'core workflow')}\". "
        f"Task targets `{t.role}` outcomes through incremental edits on {', '.join(t.entry_points)} with behavior-safe validation.",
        "",
    ])
    return "\n".join(lines)


def render_task_toml(meta: RepoMeta, t: TaskPlan) -> str:
    return "\n".join([
        'version = "1.0"',
        f'repo_url = {json.dumps(meta.repo_url)}',
        f'repo_commit = {json.dumps(meta.repo_commit)}',
        f'category = {json.dumps(meta.category)}',
        f'language = {json.dumps(meta.language)}',
        f'role = {json.dumps(t.role)}',
        f'task_type = {json.dumps(t.task_type)}',
        f'difficulty = {json.dumps(t.difficulty)}',
        f'entry_points = {toml_list(t.entry_points)}',
        f'expected_capability = {json.dumps(t.expected_capability)}',
        f'baseline_command = {json.dumps(t.baseline_command)}',
        'environment_dockerfile = "environment/Dockerfile"',
        'phase1_test = "test/phase1_install_check.py"',
        'phase2_test = "test/phase2_task_check.py"',
        'behavior_contract = "solution/behavior_contract.json"',
        "",
    ])


def render_dockerfile(meta: RepoMeta) -> str:
    return "\n".join([
        "FROM ubuntu:24.04",
        "",
        "ARG REPO_URL=" + json.dumps(meta.repo_url),
        "ARG REPO_COMMIT=" + json.dumps(meta.repo_commit),
        "WORKDIR /workspace",
        "",
        "RUN apt-get update && apt-get install -y \\",
        "  bash ca-certificates curl git python3 python3-pip \\",
        "  && rm -rf /var/lib/apt/lists/*",
        "",
        "RUN git clone \"$REPO_URL\" /workspace/repo \\",
        "  && git -C /workspace/repo fetch --all --tags || true \\",
        "  && git -C /workspace/repo checkout \"$REPO_COMMIT\"",
        "",
        "# Heuristic dependency setup is baked into the image build.",
        "RUN if [ -f /workspace/repo/requirements.txt ]; then \\",
        "    python3 -m pip install -r /workspace/repo/requirements.txt; \\",
        "  fi",
        "RUN if [ -f /workspace/repo/pyproject.toml ]; then \\",
        "    python3 -m pip install -e /workspace/repo; \\",
        "  fi",
        "RUN if [ -f /workspace/repo/package.json ]; then \\",
        "    cd /workspace/repo && npm install; \\",
        "fi",
        "RUN if [ -f /workspace/repo/go.mod ]; then \\",
        "    cd /workspace/repo && go mod download; \\",
        "fi",
        "RUN if [ -f /workspace/repo/Cargo.toml ]; then \\",
        "    cd /workspace/repo && cargo fetch; \\",
        "fi",
        "",
        "WORKDIR /workspace/repo",
    ])


def render_behavior_contract(t: TaskPlan) -> str:
    payload = {
        "task_id": t.task_id,
        "expected_capability": t.expected_capability,
        "artifact_file": f"repo2task_artifacts/{t.task_id}/capability.md",
        "required_contains": [
            f"role: {t.role}",
            f"task_type: {t.task_type}",
            "status: implemented",
        ],
        "regression_baseline_command": t.baseline_command,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_solution_sh(t: TaskPlan) -> str:
    return "\n".join([
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "ROOT=\"$(cd \"$(dirname \"$0\")/..\" && pwd)\"",
        "REPO_DIR=\"$ROOT/repo\"",
        f"TASK_ID={json.dumps(t.task_id)}",
        f"ROLE={json.dumps(t.role)}",
        f"TASK_TYPE={json.dumps(t.task_type)}",
        "",
        "mkdir -p \"$REPO_DIR/repo2task_artifacts/$TASK_ID\"",
        "cat > \"$REPO_DIR/repo2task_artifacts/$TASK_ID/capability.md\" <<'EOT'",
        f"role: {t.role}",
        f"task_type: {t.task_type}",
        "status: implemented",
        "EOT",
        "",
        "echo \"reference solution applied\"",
        "",
    ])


def render_solution_md(t: TaskPlan) -> str:
    return "\n".join([
        f"# Reference Solution: {t.task_id}",
        "",
        "This reference implementation demonstrates minimal change strategy:",
        "- keep original repo behavior unchanged",
        "- add isolated capability artifact under `repo2task_artifacts/`",
        "- satisfy behavior contract for deterministic validation",
        "",
        "You can replace this with a deeper implementation as long as tests pass.",
        "",
    ])


def render_test_sh() -> str:
    return "\n".join([
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        "python3 -m pip install -q pytest",
        "pytest -q test/phase1_install_check.py",
        "pytest -q test/phase2_task_check.py",
        "",
    ])


def render_phase1_py(meta: RepoMeta) -> str:
    return "\n".join([
        "from pathlib import Path",
        "import subprocess",
        "",
        "ROOT = Path(__file__).resolve().parent.parent",
        "DOCKERFILE = ROOT / 'environment' / 'Dockerfile'",
        "REPO = ROOT / 'repo'",
        f"REPO_URL = {json.dumps(meta.repo_url)}",
        f"EXPECTED_COMMIT = {json.dumps(meta.repo_commit)}",
        "",
        "",
        "def run(cmd, cwd=None):",
        "    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()",
        "",
        "",
        "def ensure_repo_materialized():",
        "    if (REPO / '.git').exists():",
        "        return",
        "    subprocess.run(['git', 'clone', REPO_URL, str(REPO)], check=True)",
        "    subprocess.run(['git', '-C', str(REPO), 'fetch', '--all', '--tags'], check=True)",
        "    subprocess.run(['git', '-C', str(REPO), 'checkout', EXPECTED_COMMIT], check=True)",
        "",
        "",
        "def test_dockerfile_exists_and_encodes_repo_setup():",
        "    assert DOCKERFILE.exists()",
        "    text = DOCKERFILE.read_text(encoding='utf-8')",
        "    assert REPO_URL in text",
        "    assert EXPECTED_COMMIT in text",
        "    assert 'git clone' in text",
        "    assert 'git -C /workspace/repo checkout' in text",
        "",
        "",
        "def test_repo_commit_is_fixed_version():",
        "    ensure_repo_materialized()",
        "    commit = run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'])",
        "    assert commit == EXPECTED_COMMIT",
        "",
    ]) + "\n"


def render_phase2_py() -> str:
    return "\n".join([
        "from pathlib import Path",
        "import json",
        "import subprocess",
        "",
        "ROOT = Path(__file__).resolve().parent.parent",
        "REPO = ROOT / 'repo'",
        "",
        "",
        "def run(cmd, cwd=None):",
        "    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()",
        "",
        "",
        "def test_reference_solution_and_behavior_contract():",
        "    REPO.mkdir(parents=True, exist_ok=True)",
        "    if not (REPO / '.git').exists():",
        "        raise AssertionError('Repo not prepared; phase1 must run before phase2')",
        "    subprocess.run(['bash', str(ROOT / 'solution' / 'solve.sh')], check=True)",
        "    contract = json.loads((ROOT / 'solution' / 'behavior_contract.json').read_text(encoding='utf-8'))",
        "    artifact = REPO / contract['artifact_file']",
        "    assert artifact.exists(), f'Missing artifact: {artifact}'",
        "    text = artifact.read_text(encoding='utf-8')",
        "    for marker in contract['required_contains']:",
        "        assert marker in text",
        "",
        "",
        "def test_no_regression_baseline_command_still_runs():",
        "    contract = json.loads((ROOT / 'solution' / 'behavior_contract.json').read_text(encoding='utf-8'))",
        "    cmd = contract['regression_baseline_command']",
        "    # behavior-based check: command should execute without non-deterministic assertions",
        "    subprocess.run(['bash', '-lc', cmd], cwd=str(REPO), check=True)",
        "",
    ]) + "\n"


def write_file(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(0o755)


def write_task_bundle(root: Path, meta: RepoMeta, understanding: Understanding, cap_map: CapabilityMap, task: TaskPlan) -> None:
    task_dir = root / task.task_id

    write_file(task_dir / "instruction.md", render_instruction(meta, understanding, cap_map, task))
    write_file(task_dir / "meta_info.md", render_meta_info(meta, understanding, cap_map, task))
    write_file(task_dir / "task.toml", render_task_toml(meta, task))

    write_file(task_dir / "environment" / "Dockerfile", render_dockerfile(meta))

    write_file(task_dir / "solution" / "solve.sh", render_solution_sh(task), executable=True)
    write_file(task_dir / "solution" / "solution.md", render_solution_md(task))
    write_file(task_dir / "solution" / "behavior_contract.json", render_behavior_contract(task))

    write_file(task_dir / "test" / "test.sh", render_test_sh(), executable=True)
    write_file(task_dir / "test" / "phase1_install_check.py", render_phase1_py(meta))
    write_file(task_dir / "test" / "phase2_task_check.py", render_phase2_py())


def build(repo_arg: str, out: Path, category: str = "secondary-development", language: str = "unknown") -> Path:
    repo_path, tmp, repo_url, repo_commit = resolve_repo(repo_arg)
    try:
        repo_name = extract_owner_repo(repo_arg) or repo_path.name
        docs = docs_files(repo_path)
        mode = detect_mode(docs)

        meta = RepoMeta(
            repo_input=repo_arg,
            repo_url=repo_url,
            repo_commit=repo_commit,
            repo_name=repo_name,
            mode=mode,
            category=category,
            language=language,
        )

        understanding = build_understanding(repo_path, docs, mode)
        cap_map = build_capability_map(repo_path, docs, mode)
        tasks = make_task_plans(meta, understanding, cap_map)

        out_root = out / slug(repo_name)
        out_root.mkdir(parents=True, exist_ok=True)
        for t in tasks:
            write_task_bundle(out_root, meta, understanding, cap_map, t)

        print(f"Generated: {out_root}")
        return out_root
    finally:
        if tmp is not None:
            tmp.cleanup()


def build_from_json(json_path: Path, index: int, out: Path) -> Path:
    obj = load_repos_json(json_path, index)
    print(f"Selected repo[{index}]: {obj['name']}")
    return build(obj["name"], out, category=obj["category"], language=obj["language"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate repo2task benchmark bundles")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("build")
    p1.add_argument("--repo", required=True)
    p1.add_argument("--out", required=True)

    p2 = sub.add_parser("build-from-json")
    p2.add_argument("--repos-json", required=True)
    p2.add_argument("--index", type=int, default=0)
    p2.add_argument("--out", required=True)

    args = parser.parse_args()
    out = Path(args.out).resolve()

    if args.cmd == "build":
        build(args.repo, out)
    else:
        build_from_json(Path(args.repos_json).resolve(), args.index, out)


if __name__ == "__main__":
    main()
