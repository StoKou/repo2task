#!/usr/bin/env python3
"""Generate repo secondary-development tasks from docs/examples.

Output layout:
<out>/<gitname>/<subtopic>/instruction.md
<out>/<gitname>/<subtopic>/test/test_01.py
<out>/<gitname>/<subtopic>/test/test_02.py
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple
from urllib.request import urlretrieve

MAX_CHARS_PER_FILE = 18000
MAX_TOPICS = 6


@dataclass
class TopicPlan:
    slug: str
    title: str
    concept: str
    requirement: str
    implementation: List[str]
    acceptance: List[str]
    risks: List[str]
    dev_mode: str


def run(cmd: Sequence[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def sanitize_slug(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "subtopic"


def normalize_repo_dirname(repo_name: str) -> str:
    # owner/repo -> owner-repo
    cleaned = repo_name.strip().replace("/", "-")
    return sanitize_slug(cleaned)


def repo_url_from_name(name: str) -> str:
    return f"https://github.com/{name}.git"


def _extract_github_name(repo_arg: str) -> str | None:
    # Supports owner/repo or github URL
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
            if target.exists():
                return True
            os.rename(extracted, target)
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


def load_repo_name_from_json(json_path: Path, index: int) -> str:
    items = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(items, list) or not items:
        raise ValueError("repos.json is empty or invalid")
    if index < 0 or index >= len(items):
        raise IndexError(f"index {index} is out of range (0..{len(items)-1})")
    item = items[index]
    if not isinstance(item, dict) or "name" not in item:
        raise ValueError("selected item has no 'name' field")
    return str(item["name"]).strip()


def candidate_files(repo: Path) -> List[Path]:
    picks: List[Path] = []

    priority_dirs = ["examples", "example", "docs", "doc"]
    for d in priority_dirs:
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
        txt = txt[:MAX_CHARS_PER_FILE]
        blocks.append(f"\n\nSOURCE_FILE: {fp}\n{txt}")
    return "\n".join(blocks)


def extract_topics(blob: str) -> List[str]:
    topics: List[str] = []
    headers = re.findall(r"^#{1,6}\s+(.+)$", blob, flags=re.MULTILINE)
    stop_words = {
        "readme",
        "quick start",
        "installation",
        "license",
        "contributing",
    }
    for h in headers:
        h = re.sub(r"[`*_]", "", h).strip()
        lower = h.lower()
        if len(h) < 4 or len(h) > 70:
            continue
        if lower in stop_words:
            continue
        if "table of contents" in lower:
            continue
        topics.append(h)

    # Fallback keyword-based topics
    if not topics:
        for kw in ["search", "cli", "performance", "plugin", "integration", "workflow"]:
            if re.search(rf"\b{re.escape(kw)}\b", blob, flags=re.IGNORECASE):
                topics.append(kw.upper())

    if not topics:
        topics = ["核心检索能力", "命令行体验", "可扩展工作流"]

    uniq: List[str] = []
    seen = set()
    for t in topics:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            uniq.append(t)

    return uniq[:MAX_TOPICS]


def build_plans(topics: List[str], repo_name: str) -> List[TopicPlan]:
    modes = ["新增功能", "依赖替换（掉包）", "功能聚合"]
    plans: List[TopicPlan] = []

    for i, topic in enumerate(topics, start=1):
        mode = modes[(i - 1) % len(modes)]
        slug = f"{i:02d}-{sanitize_slug(topic)}"
        title = f"{topic} 的二次开发方案"

        concept = (
            f"{topic} 在 {repo_name} 中是核心能力或关键交互点。二次开发应在保留现有行为和用户心智的前提下，"
            f"通过模块化改造提升可扩展性、可观测性与可维护性。"
        )

        requirement = (
            f"围绕“{topic}”实现 {mode}：不仅新增或替换能力，还要提供可回滚路径、"
            f"兼容策略与性能/稳定性基线，避免对既有用户造成破坏性影响。"
        )

        implementation = [
            "梳理现有调用链与依赖边界，明确可插拔点与不可变契约。",
            "设计分层接口（domain/service/adapter），使新旧实现可并行切换。",
            "为关键路径增加日志、指标与错误分类，支持上线后快速定位问题。",
            "补齐迁移文档和灰度开关策略，保证失败时能快速回滚。",
        ]

        acceptance = [
            "功能在默认配置下与旧行为兼容，或明确声明不兼容点。",
            "至少覆盖主流程、异常流程、边界输入三类自动化测试。",
            "在文档中给出使用示例、迁移步骤和验证命令。",
        ]

        risks = [
            "历史用户依赖隐式行为，替换后可能出现兼容性回归。",
            "缺少指标会导致线上问题难以定位。",
            "未定义回滚步骤会放大发布风险。",
        ]

        plans.append(
            TopicPlan(
                slug=slug,
                title=title,
                concept=concept,
                requirement=requirement,
                implementation=implementation,
                acceptance=acceptance,
                risks=risks,
                dev_mode=mode,
            )
        )

    return plans


def instruction_markdown(repo_name: str, plan: TopicPlan) -> str:
    lines = [
        f"# {plan.title}",
        "",
        f"- 仓库: `{repo_name}`",
        f"- 开发模式: {plan.dev_mode}",
        "",
        "## 概念理解",
        plan.concept,
        "",
        "## 需求说明",
        plan.requirement,
        "",
        "## 实施方案",
    ]
    lines.extend([f"- {x}" for x in plan.implementation])
    lines.extend(["", "## 验收标准"])
    lines.extend([f"- {x}" for x in plan.acceptance])
    lines.extend(["", "## 风险与约束"])
    lines.extend([f"- {x}" for x in plan.risks])
    lines.extend(
        [
            "",
            "## 交付物",
            "- 代码变更（模块化、可切换实现、可观测性增强）",
            "- 文档变更（迁移路径、示例、回滚策略）",
            "- 测试变更（主流程/异常流程/边界条件）",
            "",
            "## 建议验证命令",
            "```bash",
            "pytest -q",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def test_template(repo_name: str, plan: TopicPlan, idx: int) -> str:
    fn = sanitize_slug(plan.slug).replace("-", "_")
    return f'''"""Auto-generated test #{idx} for {repo_name} / {plan.slug}."""


def test_{fn}_contract_{idx}():
    """验证 {plan.title} 的对外契约。"""
    # TODO: 接入真实模块调用
    response = {{"ok": True, "mode": "{plan.dev_mode}"}}
    assert response["ok"] is True


def test_{fn}_regression_{idx}():
    """验证 {plan.title} 的回归场景。"""
    # TODO: 将回归场景替换为真实输入与断言
    error = {{"code": "EXPECTED_ERROR"}}
    assert "code" in error
'''


def write_output(out_root: Path, repo_name: str, plans: List[TopicPlan]) -> Path:
    gitname = normalize_repo_dirname(repo_name)
    repo_dir = out_root / gitname
    repo_dir.mkdir(parents=True, exist_ok=True)

    for plan in plans:
        topic_dir = repo_dir / plan.slug
        test_dir = topic_dir / "test"
        test_dir.mkdir(parents=True, exist_ok=True)

        (topic_dir / "instruction.md").write_text(
            instruction_markdown(repo_name, plan), encoding="utf-8"
        )
        (test_dir / "test1.py").write_text(test_template(repo_name, plan, 1), encoding="utf-8")
        (test_dir / "test2.py").write_text(test_template(repo_name, plan, 2), encoding="utf-8")

    return repo_dir


def build_from_repo(repo_arg: str, out: Path) -> Path:
    repo_path, tmp = resolve_repo(repo_arg)
    try:
        files = candidate_files(repo_path)
        blob = load_text(files)
        topics = extract_topics(blob)
        repo_name = repo_path.name if "/" not in repo_arg else repo_arg.strip().rstrip(".git")
        plans = build_plans(topics, repo_name)
        generated = write_output(out, repo_name, plans)
        print(f"Generated repo task package: {generated}")
        return generated
    finally:
        if tmp is not None:
            tmp.cleanup()


def build_from_json(json_path: Path, index: int, out: Path) -> Path:
    repo_name = load_repo_name_from_json(json_path, index)
    print(f"Selected repo[{index}]: {repo_name}")
    return build_from_repo(repo_name, out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate repo2task outputs")
    sub = parser.add_subparsers(dest="cmd", required=True)

    by_repo = sub.add_parser("build", help="Build from local path / github URL / owner/repo")
    by_repo.add_argument("--repo", required=True)
    by_repo.add_argument("--out", required=True)

    by_json = sub.add_parser("build-from-json", help="Build from repos.json by index")
    by_json.add_argument("--repos-json", required=True)
    by_json.add_argument("--index", type=int, default=0)
    by_json.add_argument("--out", required=True)

    args = parser.parse_args()

    out = Path(args.out).resolve()

    if args.cmd == "build":
        build_from_repo(args.repo, out)
    elif args.cmd == "build-from-json":
        build_from_json(Path(args.repos_json).resolve(), args.index, out)


if __name__ == "__main__":
    main()
