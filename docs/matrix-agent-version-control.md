# Matrix Agent 版本控制与发布流程

本文档定义个人 Fork `zhangyaoyi/hermes-agent` 的开发、上游同步和多电脑部署流程。
目标是让官方代码、个人定制和运行环境彼此分离，并使每次发布都可审查、验证和回滚。

## 分支与远端职责

```text
NousResearch/hermes-agent
└── upstream/main                    官方代码，只读来源
          ↓ 快进同步
zhangyaoyi/hermes-agent
├── origin/main                      官方代码镜像，不放个人定制
└── origin/matrix-agent              验证通过的个人稳定版本
          ↑ PR
          ├── feature/<name>          单项功能开发
          ├── fix/<name>              单项缺陷修复
          └── chore/sync-upstream-*   官方更新集成与测试
```

约束：

- `main` 永远保持为官方代码镜像。
- `matrix-agent` 只接受经过检查的 PR，不直接进行日常开发。
- 一个功能或修复使用一个独立分支。
- 只在一台主开发电脑上同步 `upstream/main`。
- 其他运行电脑只消费 `origin/matrix-agent`，不自行合并官方代码。

## 一次性远端配置

在主开发电脑的源码仓库中配置：

```bash
git remote set-url origin https://github.com/zhangyaoyi/hermes-agent.git
git remote get-url upstream >/dev/null 2>&1 \
  || git remote add upstream https://github.com/NousResearch/hermes-agent.git

git remote set-url upstream https://github.com/NousResearch/hermes-agent.git
git remote -v
```

预期关系：

```text
origin    https://github.com/zhangyaoyi/hermes-agent.git
upstream  https://github.com/NousResearch/hermes-agent.git
```

## 开发个人功能

始终从最新的稳定分支创建功能分支：

```bash
git switch matrix-agent
git pull --ff-only origin matrix-agent
git switch -c feature/<name>
```

修改完成后只暂存相关文件：

```bash
git status
git add <files>
git commit -m "feat: <description>"
git push -u origin feature/<name>
```

在 GitHub 创建 PR：

```text
feature/<name> -> matrix-agent
```

缺陷修复使用 `fix/<name>`，提交信息使用 `fix: <description>`，其余流程相同。

## 同步官方更新

### 1. 更新官方镜像分支

```bash
git fetch upstream
git switch main
git merge --ff-only upstream/main
git push origin main
```

如果 `--ff-only` 失败，停止操作并检查 `main` 是否混入了个人提交；不要使用强制推送掩盖分歧。

### 2. 创建上游集成分支

```bash
git switch matrix-agent
git pull --ff-only origin matrix-agent
git switch -c chore/sync-upstream-YYYY-MM-DD
git merge main
```

解决冲突并完成验证后推送：

```bash
git status
git push -u origin chore/sync-upstream-YYYY-MM-DD
```

在 GitHub 创建 PR：

```text
chore/sync-upstream-YYYY-MM-DD -> matrix-agent
```

PR 中应记录：

- 同步到的 `upstream/main` 提交。
- 发生冲突的文件及解决方式。
- 执行过的测试和人工验证。
- 配置迁移、Desktop 或 Gateway 的影响。

## 发布稳定版本

PR 合并并验证后，在主开发电脑更新本地稳定分支：

```bash
git switch matrix-agent
git pull --ff-only origin matrix-agent
```

重要版本可以打日期标签：

```bash
git tag matrix-agent-YYYY-MM-DD
git push origin matrix-agent-YYYY-MM-DD
```

同一天发布多个版本时使用递增后缀，例如 `matrix-agent-YYYY-MM-DD.2`。

## 更新其他电脑

每台运行电脑的 `origin` 必须指向个人 Fork，代码分支必须跟踪 `origin/matrix-agent`。
更新前可先查看只读计划：

```bash
hermes update --plan --branch matrix-agent
```

正式更新：

```bash
hermes update --backup --branch matrix-agent
```

Hermes 会处理代码更新、依赖安装、配置迁移以及运行中服务的刷新。更新后验证：

```bash
cd ~/.hermes/hermes-agent
git status --short --branch
hermes --version
```

预期 Git 状态为：

```text
## matrix-agent...origin/matrix-agent
```

## 回滚

不要直接在运行电脑上改写分支历史。发现发布问题时，在主开发电脑上对有问题的 PR 或提交执行
GitHub Revert，或者创建一个 `fix/<name>` 分支提交修复，再通过 PR 合并到 `matrix-agent`。

修复发布后，各运行电脑重新执行：

```bash
hermes update --branch matrix-agent
```

日期标签用于确认最后一个已知稳定点。除非已经核对影响范围，不要对共享分支执行
`git push --force` 或 `git reset --hard`。

## 源码与运行数据边界

Git 只管理源码。不得向仓库提交以下内容：

- `~/.hermes/` 整个数据目录。
- `.env`、API Key、OAuth 令牌和认证文件。
- 会话、日志、配对信息和 Gateway 运行状态。
- 电脑专属路径或本地生成的构建缓存。

运行数据使用 `hermes backup` 管理，不通过 Git 在电脑之间同步。

## 日常检查清单

开发或同步前：

```bash
git status --short --branch
git remote -v
```

确认：

- 工作区没有意外修改或未跟踪文件。
- 当前分支符合本次任务。
- `origin` 指向个人 Fork，`upstream` 指向官方仓库。
- 功能提交不进入 `main`。
- 未将密钥、配置或运行数据加入暂存区。
