# AI Coding Workflow Template V3.3 Deterministic Composable

这是一个面向 Claude Code 的薄编排模板。AI 只负责从需求和代码库提取结构化事实；Node runtime 是路由、节点顺序、状态迁移和 Review 范围的唯一执行源，避免同一需求在不同回合走出不同流程。

```text
Intent → Task Type → Risk Mode → Specialized Gates → Ordered Execution

Final workflow
= Core Spine
+ Task Method
+ Risk Safeguards
+ Specialized Gates
```

用户只需描述需求，或执行 `/new-task <需求>`。

## 路由模型

| 维度 | 选项 | 职责 |
|---|---|---|
| Intent | explain / review / diagnose-only / plan-only / change | 判断是否有修改授权 |
| Task Type | Feature / Bug / Refactor / Upgrade-Config / Migration-Infrastructure / Maintenance | 选择 Superpowers 方法 |
| Risk Mode | Fast / Standard / Governed | 决定 OpenSpec、隔离、验证与人工 Review 强度 |
| Specialized Gates | data / security / contract / infrastructure / release / observability | 添加领域风险证据 |

Feature 最低 Standard，确保 `brainstorming` 和设计批准不会被 Fast 跳过。Bug 先执行 `systematic-debugging`；重构先建立行为基线；升级先查官方变更记录；迁移先设计回滚、dry-run 和分批执行。

| 模式 | 使用条件 | OpenSpec | Plannotator | 验证 |
|---|---|---|---|---|
| Fast | 项目画像 ready、非 Feature，且全部低风险事实成立 | 不创建 change | 无预定 Gate | targeted |
| Standard | 普通修改默认 | propose → apply-change → strict validate → archive | 一次 OpenSpec Spec Diff Review | affected |
| Governed | 任一高风险事实触发 | Standard 生命周期 + 高影响探索 | Spec Diff + Code Diff Review | full |

## 连续执行

每次路由生成稳定的 `route_fingerprint`，节点组合生成 `workflow_hash`。所有 change 都持久化状态：

```text
Fast:                .claude/workflow-runs/<route-fingerprint>/workflow-state.json
Standard/Governed:   openspec/changes/<change-id>/workflow-state.json
```

`SessionStart` 恢复唯一活动任务，`PreToolUse` 阻止规划阶段越界修改，`PreCompact` 原子保存状态，`Stop` 在仍有可执行 REQUIRED 节点时阻止提前结束。Route Card 只是通知；Standard 只在 Spec Diff Review 暂停，Governed 额外在 Code Diff Review 暂停。

OpenSpec 规划 Review 不再手动拼接文档。Runtime 从 Git 捕获当前 change 的真实文件列表和 SHA-256，Plannotator 必须使用 `uncommitted` 视图展示同一组文件；代码 Review 使用 `since-base`。批准后的稳定规划文件发生变化时，流程自动回到 Diff Review。

## 安装

1. 把发行压缩包解压到业务项目根目录；已有 `CLAUDE.md` 或 `.claude/settings.json` 时合并，不覆盖项目规则。
2. 填写 `.claude/project-profile.yaml` 的项目事实和真实验证命令，完成后设置 `profile_status: "ready"`。
3. 安装 Superpowers、OpenSpec、Plannotator；执行 `openspec init` 并选择 Claude Code。
4. 幂等安装生命周期 Hook：

```text
node .claude/scripts/workflow-runtime.mjs install-hooks
```

5. 重启 Claude Code，使用 `/new-task <需求>`。

## 发行包文件

| 文件 | 运行时用途 | 何时使用 |
|---|---|---|
| `CLAUDE.md` | 稳定授权、边界和完成标准 | 每次会话自动读取 |
| `.claude/project-profile.yaml` | 项目命令、风险位置、运行能力 | 首次接入填写；项目变化时更新 |
| `.claude/skills/new-task/SKILL.md` | 单一任务入口 | 用户调用 `/new-task` 时 |
| `.claude/skills/workflow-router/SKILL.md` | 事实提取与工具编排 | 每个任务自动加载 |
| `ROUTING.md` | Intent、Task Type、模式与 Gate 判据 | 路由时按需读取 |
| `PLAYBOOKS.md` | 节点语义和三个工具的交接合同 | 只读取本次相关章节 |
| `.claude/scripts/workflow-runtime.mjs` | 确定性路由、状态机、Review 校验和 Hook | Agent 自动调用；安装 Hook 时手动运行一次 |
| `.claude/workflow-state.schema.json` | 状态文件结构合同 | runtime/CI 校验时 |
| `.claude/hooks/workflow-hooks.json` | 待合并的 Claude Code Hook 配置 | `install-hooks` 使用 |
| `.claude/workflow-runs/.gitignore` | 忽略 Fast 临时状态 | 自动生效 |

维护仓库中的 Python、测试、评测案例和 CI 不进入业务发行包。

## 维护者验证

```text
python -B scripts/validate_workflow.py
python -B scripts/evaluate_routing.py
python -B -m unittest discover -s tests -v
python -B scripts/build_distribution.py
python -B scripts/validate_workflow.py --archive ai-coding-workflow-template.zip
```

详细行为见项目根目录《AI Coding Workflow Template 详细使用说明》。
