#!/usr/bin/env python3
"""Generate benchmark-style secondary-development tasks from GitHub repositories.

Per subtopic output layout:
<out>/<gitname>/<subtopic>/
  instruction.md
  task.toml
  environment/
    Dockerfile
    skill_config.toml
    io_config.json
  solution/
    solve.sh
    solution.md
  test/
    test.sh
    test_state.py
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
from typing import Iterable, List, Sequence, Tuple
from urllib.request import urlretrieve

MAX_CHARS_PER_FILE = 22000
MAX_TOPICS = 6


@dataclass
class RepoMeta:
    name: str
    category: str = "secondary-development"
    language: str = "unknown"


@dataclass
class TopicPlan:
    index: int
    slug: str
    title: str
    dev_mode: str
    concept: str
    requirement: str
    implementation: List[str]
    acceptance: List[str]
    risks: List[str]


def run(cmd: Sequence[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def sanitize_slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "subtopic"


def normalize_repo_dirname(repo_name: str) -> str:
    return sanitize_slug(repo_name.replace("/", "-"))


def repo_url_from_name(name: str) -> str:
    return f"https://github.com/{name}.git"


def _extract_github_name(repo_arg: str) -> str | None:
    if repo_arg.startswith(("http://", "https://", "git@")):
        m = re.search(r"github\.com[:/]+([^/]+/[^/.]+)", repo_arg)
        return m.group(1) if m else None
    if "/" in repo_arg and not repo_arg.startswith("."):
        return repo_arg
    return None


def _download_github_archive(repo_name: str, target: Path) -> bool:
    owner, repo = repo_name.split("/", 1)
    tmp = target.parent / "archive_tmp"
    tmp.mkdir(parents=True, exist_ok=True)

    for branch in ("main", "master"):
        archive = tmp / f"{repo}-{branch}.tar.gz"
        url = f"https://codeload.github.com/{owner}/{repo}/tar.gz/refs/heads/{branch}"
        try:
            urlretrieve(url, archive)
            if not archive.exists() or archive.stat().st_size == 0:
                continue
            with tarfile.open(archive, "r:gz") as tf:
                tf.extractall(tmp)
            candidates = sorted(p for p in tmp.iterdir() if p.is_dir() and p.name.startswith(f"{repo}-"))
            if not candidates:
                continue
            extracted = candidates[-1]
            extracted.rename(target)
            return True
        except Exception:
            continue
    return False


def resolve_repo(repo_arg: str) -> Tuple[Path, tempfile.TemporaryDirectory | None]:
    p = Path(repo_arg).expanduser()
    if p.exists() and p.is_dir():
        return p.resolve(), None

    if repo_arg.startswith(("http://", "https://", "git@")):
        tmp = tempfile.TemporaryDirectory(prefix="repo2task_")
        target = Path(tmp.name) / "source"
        try:
            run(["git", "clone", "--depth", "1", repo_arg, str(target)])
            return target, tmp
        except subprocess.CalledProcessError:
            repo_name = _extract_github_name(repo_arg)
            if repo_name and _download_github_archive(repo_name, target):
                return target, tmp
            raise

    if "/" in repo_arg and not repo_arg.startswith("."):
        return resolve_repo(repo_url_from_name(repo_arg))

    raise FileNotFoundError(f"Repository not found: {repo_arg}")


def load_repo_meta_from_json(json_path: Path, index: int) -> RepoMeta:
    items = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(items, list) or not items:
        raise ValueError("repos.json is empty or invalid")
    if index < 0 or index >= len(items):
        raise IndexError(f"index {index} is out of range (0..{len(items)-1})")
    item = items[index]
    if not isinstance(item, dict) or "name" not in item:
        raise ValueError("selected item has no 'name' field")
    return RepoMeta(
        name=str(item["name"]).strip(),
        category=str(item.get("category", "secondary-development")),
        language=str(item.get("language", "unknown")),
    )


def candidate_files(repo: Path) -> List[Path]:
    picks: List[Path] = []

    for d in ("examples", "example", "docs", "doc"):
        base = repo / d
        if base.exists():
            for ext in ("*.md", "*.rst", "*.txt"):
                picks.extend(sorted(base.rglob(ext)))

    for readme in ("README.md", "README.MD", "readme.md"):
        f = repo / readme
        if f.exists():
            picks.append(f)

    uniq: List[Path] = []
    seen = set()
    for f in picks:
        key = str(f.resolve())
        if key not in seen and f.is_file():
            uniq.append(f)
            seen.add(key)
    return uniq


def load_text(files: Iterable[Path]) -> str:
    blocks: List[str] = []
    for fp in files:
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        blocks.append(f"\n\nSOURCE_FILE: {fp}\n{txt[:MAX_CHARS_PER_FILE]}")
    return "\n".join(blocks)


def _header_candidates(blob: str) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []
    for line in blob.splitlines():
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not m:
            continue
        level = len(m.group(1))
        title = re.sub(r"[`*_]", "", m.group(2)).strip()
        out.append((level, title))
    return out


def extract_topics(blob: str) -> List[str]:
    scored: List[Tuple[int, str]] = []

    include_kw = [
        "feature",
        "usage",
        "use",
        "integration",
        "plugin",
        "api",
        "advanced",
        "performance",
        "key binding",
        "completion",
        "search",
        "query",
        "workflow",
        "custom",
        "extension",
    ]
    exclude_kw = [
        "installation",
        "install",
        "homebrew",
        "linux package",
        "windows package",
        "binary release",
        "license",
        "contributing",
        "table of contents",
    ]

    for level, title in _header_candidates(blob):
        lower = title.lower()
        if len(title) < 4 or len(title) > 80:
            continue

        score = 0
        if level <= 2:
            score += 2
        if any(k in lower for k in include_kw):
            score += 4
        if any(k in lower for k in exclude_kw):
            score -= 4
        if re.search(r"\b(api|cli|plugin|performance|workflow|search)\b", lower):
            score += 3

        scored.append((score, title))

    scored.sort(key=lambda x: x[0], reverse=True)

    topics: List[str] = []
    seen = set()
    for score, title in scored:
        if score < 1:
            continue
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        topics.append(title)
        if len(topics) >= MAX_TOPICS:
            break

    if not topics:
        fallback = ["核心检索流程", "交互式命令行能力", "扩展与集成能力"]
        return fallback[:MAX_TOPICS]

    return topics


def build_plans(topics: List[str], repo_name: str) -> List[TopicPlan]:
    modes = ["新增功能", "依赖替换（掉包）", "功能聚合"]
    plans: List[TopicPlan] = []

    for i, topic in enumerate(topics, start=1):
        mode = modes[(i - 1) % len(modes)]
        slug = f"{i:02d}-{sanitize_slug(topic)}"

        concept = (
            f"{topic} 是 {repo_name} 的关键能力点。需要先识别该能力的输入契约、状态流转和依赖关系，"
            f"再进行二次开发，避免对现有用户行为造成隐式破坏。"
        )
        requirement = (
            f"围绕 {topic} 设计 {mode} 方案：要求具备可落地的模块边界、兼容策略、回滚路径与观测指标，"
            f"并对关键行为给出可执行测试。"
        )

        implementation = [
            "梳理当前模块与调用链，明确可替换点与必须兼容的接口。",
            "按 domain/service/adapter 拆分实现，支持新旧方案并存切换。",
            "为核心路径新增日志、指标和错误分类，确保故障可定位。",
            "补齐迁移说明（启用、回滚、兼容性）并提供命令行验证示例。",
        ]
        acceptance = [
            "默认行为对现有用户保持兼容，或在文档中明确列出不兼容项。",
            "至少覆盖主路径、异常路径、边界条件三类自动化测试。",
            "能通过任务内 `test/test.sh` 完成验证并给出明确结果。",
        ]
        risks = [
            "依赖替换时行为细节变化导致回归。",
            "缺乏观测信息导致线上问题排障困难。",
            "回滚步骤不完整导致发布风险放大。",
        ]

        plans.append(
            TopicPlan(
                index=i,
                slug=slug,
                title=topic,
                dev_mode=mode,
                concept=concept,
                requirement=requirement,
                implementation=implementation,
                acceptance=acceptance,
                risks=risks,
            )
        )

    return plans


def render_instruction(plan: TopicPlan, repo: RepoMeta) -> str:
    lines = [
        f"# 问题: {plan.title} 二次开发", "", "## 背景", plan.concept, "", "## 目标", plan.requirement, "",
        "## 开发要求",
    ]
    lines.extend([f"- {x}" for x in plan.implementation])
    lines.extend(["", "## 验收标准"])
    lines.extend([f"- {x}" for x in plan.acceptance])
    lines.extend(["", "## 风险与约束"])
    lines.extend([f"- {x}" for x in plan.risks])
    lines.extend(
        [
            "",
            "## 上下文",
            f"- 仓库: `{repo.name}`",
            f"- 类型: `{repo.category}`",
            f"- 语言: `{repo.language}`",
            f"- 开发模式: `{plan.dev_mode}`",
            "",
        ]
    )
    return "\n".join(lines)


def render_task_toml(plan: TopicPlan, repo: RepoMeta) -> str:
    tags = [
        "secondary-dev",
        sanitize_slug(plan.dev_mode),
        sanitize_slug(repo.language),
        sanitize_slug(repo.category),
    ]
    tags_str = ", ".join(f'"{t}"' for t in tags)
    return "\n".join(
        [
            'version = "1.0"',
            "",
            "[metadata]",
            f'author_name = "repo2task"',
            f'author_email = "noreply@example.com"',
            'difficulty = "medium"',
            'category = "programming"',
            f"tags = [{tags_str}]",
            f'repo = "{repo.name}"',
            f'subtopic = "{plan.slug}"',
            f'dev_mode = "{plan.dev_mode}"',
            "",
            "[verifier]",
            "timeout_sec = 600.0",
            "",
            "[agent]",
            "timeout_sec = 900.0",
            "",
            "[environment]",
            "build_timeout_sec = 1200.0",
            "cpus = 2",
            'memory = "4G"',
            'storage = "20G"',
            "",
        ]
    )


def render_dockerfile() -> str:
    return "\n".join(
        [
            "FROM ubuntu:24.04",
            "",
            "WORKDIR /app",
            "",
            "RUN apt-get update && apt-get install -y \\",
            "    bash \\",
            "    ca-certificates \\",
            "    curl \\",
            "    git \\",
            "    python3 \\",
            "    python3-pip \\",
            "    && rm -rf /var/lib/apt/lists/*",
            "",
        ]
    )


def render_skill_config(repo: RepoMeta, plan: TopicPlan) -> str:
    return "\n".join(
        [
            '[skill]',
            'name = "repo2task"',
            f'repo = "{repo.name}"',
            f'subtopic = "{plan.slug}"',
            f'dev_mode = "{plan.dev_mode}"',
            "",
            '[io]',
            'input_dir = "/app/input"',
            'output_dir = "/app/output"',
            'workspace = "/app"',
            "",
        ]
    )


def render_io_config(repo: RepoMeta, plan: TopicPlan) -> str:
    return json.dumps(
        {
            "repo": repo.name,
            "subtopic": plan.slug,
            "expected_inputs": [
                "source repository",
                "docs/examples/readme context",
                "existing module contracts",
            ],
            "expected_outputs": [
                "code changes",
                "updated docs",
                "passing tests",
            ],
        },
        ensure_ascii=False,
        indent=2,
    ) + "\n"


def render_solution_sh(plan: TopicPlan) -> str:
    return "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            "",
            f'echo "[repo2task] Solving subtopic: {plan.slug}"',
            "",
            "# 1) Implement required code changes in target modules.",
            "# 2) Update docs for compatibility and rollback.",
            "# 3) Run tests and fix regressions.",
            "",
            "# Example placeholders (replace with real project commands):",
            "# git diff -- .",
            "# pytest -q",
            "",
            "echo \"done\"",
            "",
        ]
    )


def render_solution_md(plan: TopicPlan, repo: RepoMeta) -> str:
    lines = [
        f"# Solution Notes: {plan.slug}",
        "",
        "## Recommended Execution Steps",
        "1. Locate the current module boundary and public contract.",
        "2. Implement the selected secondary-development mode incrementally.",
        "3. Keep migration and rollback instructions synchronized with code.",
        "4. Run `test/test.sh` and ensure all checks pass.",
        "",
        "## Suggested Change Scope",
        "- Core module adaptation",
        "- Adapter replacement or aggregation layer",
        "- Observability and error handling",
        "- Documentation updates",
        "",
        "## Context",
        f"- Repo: `{repo.name}`",
        f"- Subtopic: `{plan.slug}`",
        f"- Mode: `{plan.dev_mode}`",
        "",
    ]
    return "\n".join(lines)


def render_test_sh() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            "",
            "python3 -m pip install -q pytest",
            "pytest -q test/test_state.py",
            "",
        ]
    )


def render_test_state_py() -> str:
    return "\n".join(
        [
            "from pathlib import Path",
            "",
            "BASE = Path(__file__).resolve().parent.parent",
            "",
            "",
            "def test_required_files_exist():",
            "    required = [",
            "        BASE / 'instruction.md',",
            "        BASE / 'task.toml',",
            "        BASE / 'environment' / 'Dockerfile',",
            "        BASE / 'environment' / 'skill_config.toml',",
            "        BASE / 'environment' / 'io_config.json',",
            "        BASE / 'solution' / 'solve.sh',",
            "        BASE / 'solution' / 'solution.md',",
            "        BASE / 'test' / 'test.sh',",
            "        BASE / 'test' / 'test_state.py',",
            "    ]",
            "    for p in required:",
            "        assert p.exists(), f'Missing file: {p}'",
            "",
            "",
            "def test_instruction_has_problem_and_requirements():",
            "    text = (BASE / 'instruction.md').read_text(encoding='utf-8')",
            "    assert '问题' in text",
            "    assert '开发要求' in text",
            "    assert '验收标准' in text",
            "",
            "",
            "def test_task_toml_has_core_sections():",
            "    text = (BASE / 'task.toml').read_text(encoding='utf-8')",
            "    for key in ['[metadata]', '[verifier]', '[agent]', '[environment]']:",
            "        assert key in text",
            "",
        ]
    ) + "\n"


def write_subtopic(out_repo: Path, repo: RepoMeta, plan: TopicPlan) -> None:
    root = out_repo / plan.slug
    env_dir = root / "environment"
    sol_dir = root / "solution"
    test_dir = root / "test"

    env_dir.mkdir(parents=True, exist_ok=True)
    sol_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    (root / "instruction.md").write_text(render_instruction(plan, repo), encoding="utf-8")
    (root / "task.toml").write_text(render_task_toml(plan, repo), encoding="utf-8")

    (env_dir / "Dockerfile").write_text(render_dockerfile(), encoding="utf-8")
    (env_dir / "skill_config.toml").write_text(render_skill_config(repo, plan), encoding="utf-8")
    (env_dir / "io_config.json").write_text(render_io_config(repo, plan), encoding="utf-8")

    solve = sol_dir / "solve.sh"
    solve.write_text(render_solution_sh(plan), encoding="utf-8")
    solve.chmod(0o755)
    (sol_dir / "solution.md").write_text(render_solution_md(plan, repo), encoding="utf-8")

    t_sh = test_dir / "test.sh"
    t_sh.write_text(render_test_sh(), encoding="utf-8")
    t_sh.chmod(0o755)
    (test_dir / "test_state.py").write_text(render_test_state_py(), encoding="utf-8")


def write_output(out_root: Path, repo: RepoMeta, plans: List[TopicPlan]) -> Path:
    repo_dir = out_root / normalize_repo_dirname(repo.name)
    repo_dir.mkdir(parents=True, exist_ok=True)
    for plan in plans:
        write_subtopic(repo_dir, repo, plan)
    return repo_dir


def build_from_repo(repo_arg: str, out: Path) -> Path:
    repo_path, tmp = resolve_repo(repo_arg)
    try:
        files = candidate_files(repo_path)
        blob = load_text(files)
        topics = extract_topics(blob)
        name = repo_arg if "/" in repo_arg else repo_path.name
        repo = RepoMeta(name=name)
        plans = build_plans(topics, repo.name)
        generated = write_output(out, repo, plans)
        print(f"Generated repo task package: {generated}")
        return generated
    finally:
        if tmp is not None:
            tmp.cleanup()


def build_from_json(json_path: Path, index: int, out: Path) -> Path:
    repo = load_repo_meta_from_json(json_path, index)
    print(f"Selected repo[{index}]: {repo.name}")
    repo_path, tmp = resolve_repo(repo.name)
    try:
        files = candidate_files(repo_path)
        blob = load_text(files)
        topics = extract_topics(blob)
        plans = build_plans(topics, repo.name)
        generated = write_output(out, repo, plans)
        print(f"Generated repo task package: {generated}")
        return generated
    finally:
        if tmp is not None:
            tmp.cleanup()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate repo2task outputs")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("build", help="Build from local path / github URL / owner/repo")
    p1.add_argument("--repo", required=True)
    p1.add_argument("--out", required=True)

    p2 = sub.add_parser("build-from-json", help="Build from repos.json by index")
    p2.add_argument("--repos-json", required=True)
    p2.add_argument("--index", type=int, default=0)
    p2.add_argument("--out", required=True)

    args = parser.parse_args()
    out = Path(args.out).resolve()

    if args.cmd == "build":
        build_from_repo(args.repo, out)
    else:
        build_from_json(Path(args.repos_json).resolve(), args.index, out)


if __name__ == "__main__":
    main()
