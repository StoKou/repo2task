#!/usr/bin/env python3
"""Generate secondary-development requirements/tasks/tests from a repository."""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

MAX_CHARS_PER_FILE = 12000


@dataclass
class Requirement:
    rid: str
    title: str
    dev_mode: str
    summary: str
    acceptance: List[str]


def run(cmd: List[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def resolve_repo(repo_arg: str) -> Tuple[Path, tempfile.TemporaryDirectory | None]:
    p = Path(repo_arg).expanduser()
    if p.exists() and p.is_dir():
        return p.resolve(), None

    if repo_arg.startswith(("http://", "https://", "git@")):
        tmp = tempfile.TemporaryDirectory(prefix="repo2task_")
        target = Path(tmp.name) / "source"
        run(["git", "clone", "--depth", "1", repo_arg, str(target)])
        return target, tmp

    raise FileNotFoundError(f"Repository not found: {repo_arg}")


def candidate_files(repo: Path) -> List[Path]:
    picks: List[Path] = []

    priority_dirs = ["example", "examples", "docs", "doc"]
    for d in priority_dirs:
        base = repo / d
        if base.exists():
            picks.extend(sorted(base.rglob("*.md")))
            picks.extend(sorted(base.rglob("*.rst")))
            picks.extend(sorted(base.rglob("*.txt")))

    for name in ["README.md", "README.MD", "readme.md"]:
        f = repo / name
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
    chunks: List[str] = []
    for fp in files:
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        txt = txt[:MAX_CHARS_PER_FILE]
        chunks.append(f"\n\n# FILE: {fp}\n{txt}")
    return "\n".join(chunks)


def extract_topics(blob: str) -> List[str]:
    topics = []

    # Markdown headers
    headers = re.findall(r"^#{1,6}\s+(.+)$", blob, flags=re.MULTILINE)
    for h in headers:
        h = re.sub(r"[`*_]", "", h).strip()
        if h.upper().startswith("FILE:"):
            continue
        if 4 <= len(h) <= 80:
            topics.append(h)

    # API-like words
    for kw in [
        "API",
        "CLI",
        "authentication",
        "authorization",
        "cache",
        "queue",
        "pipeline",
        "plugin",
        "adapter",
        "deployment",
        "monitoring",
        "metrics",
        "scheduler",
        "webhook",
    ]:
        if re.search(rf"\b{re.escape(kw)}\b", blob, flags=re.IGNORECASE):
            topics.append(kw)

    # Deduplicate while preserving order
    out = []
    seen = set()
    for t in topics:
        norm = t.lower()
        if norm not in seen:
            out.append(t)
            seen.add(norm)

    if not out:
        out = ["核心工作流", "接口层", "配置与部署"]

    return out[:8]


def build_requirements(topics: List[str]) -> List[Requirement]:
    modes = [
        "新增功能",
        "依赖替换（掉包）",
        "功能聚合",
    ]
    reqs: List[Requirement] = []

    for i, topic in enumerate(topics, start=1):
        mode = modes[(i - 1) % len(modes)]
        rid = f"R{i:03d}"
        title = f"围绕「{topic}」的二次开发"
        summary = (
            f"基于仓库现有能力，在不重写核心架构的前提下，完成{mode}，"
            f"并保持向后兼容或给出清晰迁移路径。"
        )
        acceptance = [
            "提供明确的输入/输出或调用方式示例。",
            "补齐最少 1 个自动化测试，覆盖主路径行为。",
            "更新对应文档，说明变更点、兼容性和回滚策略。",
        ]
        reqs.append(Requirement(rid, title, mode, summary, acceptance))

    return reqs


def write_requirements(path: Path, repo_name: str, reqs: List[Requirement], sources: List[Path]) -> None:
    lines = [
        f"# {repo_name} 二次开发需求文档",
        "",
        "## 输入来源",
    ]
    lines.extend([f"- `{s}`" for s in sources] or ["- 未发现 docs/example，使用默认模板生成。"])
    lines.append("")
    lines.append("## 需求列表")

    for r in reqs:
        lines.extend(
            [
                "",
                f"### {r.rid} {r.title}",
                f"- 开发模式: {r.dev_mode}",
                f"- 说明: {r.summary}",
                "- 验收标准:",
            ]
        )
        lines.extend([f"  - {a}" for a in r.acceptance])

    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_tasks(path: Path, reqs: List[Requirement]) -> None:
    lines = ["# 二次开发任务清单", "", "所有任务均需在对应模块中实现并补齐自动化测试。", ""]

    for i, r in enumerate(reqs, start=1):
        tid = f"T{i:03d}"
        test_file = f"tests/test_{tid.lower()}.py"
        lines.extend(
            [
                f"## {tid} 对应 {r.rid}",
                f"- 目标: {r.title}",
                f"- 类型: {r.dev_mode}",
                "- 实施要点:",
                "  - 明确受影响模块与接口边界。",
                "  - 给出最小可交付版本（MVP）并保留扩展点。",
                "  - 保证异常路径有可观测日志或错误码。",
                "- 测试要求:",
                f"  - 新增 `{test_file}`，覆盖成功路径与至少一个失败路径。",
                "",
            ]
        )

    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def write_tests(test_dir: Path, reqs: List[Requirement]) -> None:
    test_dir.mkdir(parents=True, exist_ok=True)

    for i, r in enumerate(reqs, start=1):
        tid = f"T{i:03d}"
        fp = test_dir / f"test_{tid.lower()}.py"
        body = f'''"""Auto-generated tests for {tid} / {r.rid}."""


def test_{tid.lower()}_happy_path():
    """{r.title}: 主流程应返回预期结果。"""
    # TODO: 替换为真实调用，并断言具体输出。
    result = {{"ok": True}}
    assert result["ok"] is True


def test_{tid.lower()}_error_path():
    """{r.title}: 非法输入或依赖异常时应可控失败。"""
    # TODO: 替换为真实异常路径。
    error = {{"code": "EXPECTED_ERROR"}}
    assert "code" in error
'''
        fp.write_text(body, encoding="utf-8")


def do_build(repo_arg: str, out: Path) -> None:
    repo_path, tmp = resolve_repo(repo_arg)
    try:
        sources = candidate_files(repo_path)
        blob = load_text(sources)
        topics = extract_topics(blob)
        reqs = build_requirements(topics)

        out.mkdir(parents=True, exist_ok=True)
        write_requirements(out / "requirements.md", repo_path.name, reqs, sources)
        write_tasks(out / "tasks.md", reqs)
        write_tests(out / "tests", reqs)

        print(f"Generated: {out / 'requirements.md'}")
        print(f"Generated: {out / 'tasks.md'}")
        print(f"Generated tests: {out / 'tests'}")
    finally:
        if tmp is not None:
            tmp.cleanup()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate repo2task artifacts.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    build = sub.add_parser("build", help="Generate requirements/tasks/tests")
    build.add_argument("--repo", required=True, help="Local repo path or remote URL")
    build.add_argument("--out", required=True, help="Output directory")

    args = parser.parse_args()

    if args.cmd == "build":
        do_build(args.repo, Path(args.out).resolve())


if __name__ == "__main__":
    main()
