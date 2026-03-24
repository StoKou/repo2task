# Usage Examples

## 示例 1：从 GitHub 仓库生成

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build \
  --repo junegunn/fzf \
  --out ./generated
```

输出示例：

```text
generated/junegunn-fzf/
└── 01-vim-neovim-plugin/
    ├── instruction.md
    ├── task.toml
    ├── environment/
    ├── solution/
    └── test/
```

## 示例 2：从本地仓库生成

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build \
  --repo ../repo2skill \
  --out ./generated-local
```

## 示例 3：从 repos.json 第 N 个仓库生成

```bash
python3 repo2task-skill/scripts/generate_repo2task.py \
  build-from-json \
  --repos-json /mnt/d/2026/skillsfolder/code/data/reposkills/repos.json \
  --index 3 \
  --out ./generated-batch
```

## 示例 4：仅验证某个子任务结构

```bash
cd generated/junegunn-fzf/01-vim-neovim-plugin
bash test/test.sh
```

这个校验会检查：
- 必要文件是否存在
- `instruction.md` 是否包含问题、开发要求、验收标准
- `task.toml` 是否包含核心段落
