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
├── task_001/
├── task_002/
├── task_003/
└── task_004/
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
  --repos-json /path/to/repos.json \
  --index 3 \
  --out ./generated-batch
```

## 示例 4：验证某个任务包

```bash
cd generated/junegunn-fzf/task_001
bash test/test.sh
```

校验包含：
- Phase 1：安装与固定 commit 检查
- Phase 2：任务行为与 baseline 回归检查
