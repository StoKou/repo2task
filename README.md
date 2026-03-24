# repo2task

一句话导入 skill：

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" && mkdir -p "$CODEX_HOME/skills" && cp -R ./repo2task-skill "$CODEX_HOME/skills/repo2task"
```

一句话使用 skill 解析 repo：

```text
请使用 repo2task skill，解析这个仓库并生成任务包：https://github.com/junegunn/fzf
```

输出目录结构：`<out>/<gitname>/<subtopic>/{instruction.md,task.toml,environment/,solution/,test/}`。
