# AI Coding Workflow Template V3.3 Deterministic Composable

这是一个同时面向 Claude Code 和 Codex Desktop/CLI 的薄编排模板。AI 只负责从需求和代码库提取结构化事实；两个宿主共用同一份 Node runtime，路由、节点顺序、状态迁移和 Review 范围不会因宿主不同而分叉。

```text
Intent → Task Type → Risk Mode → Specialized Gates → Ordered Execution

Final workflow
= Core Spine
+ Task Method
+ Risk Safeguards
+ Specialized Gates
```

Claude Code 用户只需描述需求或执行 `/new-task <需求>`；Codex 用户可以直接描述需求，或显式调用 `$ai-coding-workflow`。

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

默认只安装两个必要 Hook：`SessionStart` 恢复唯一活动任务，`Stop` 在仍有可执行 REQUIRED 节点时阻止提前结束。需要更强约束的项目可选择 strict profile，额外启用 `PreToolUse` 阻止规划阶段越界修改。Route Card 只是通知；Standard 只在 Spec Diff Review 暂停，Governed 额外在 Code Diff Review 暂停。

OpenSpec 规划 Review 不再手动拼接文档。Runtime 从 Git 捕获当前 change 的真实文件列表和 SHA-256，Plannotator 必须使用 `uncommitted` 视图展示同一组文件；代码 Review 使用 `since-base`。批准后的稳定规划文件发生变化时，流程自动回到 Diff Review。

## Codex Desktop 安装

1. 安装仓库 Marketplace。克隆仓库后在其根目录做本地测试：

```text
codex plugin marketplace add .
```

仓库推送到 GitHub 后，也可以直接使用远程源：

```text
codex plugin marketplace add CraneZhouGo/ai-coding-workflow-template
```

2. 重启 Codex Desktop，在侧栏 Plugins 中选择 `AI Coding Workflow` Marketplace，安装 `AI Coding Workflow`。若使用支持插件市场的 Codex CLI，则进入交互界面后输入：

```text
/plugins
```

3. 在业务项目开启一个新任务，调用 `$ai-coding-workflow-setup`。它会一次性检查 Node.js（OpenSpec 要求 20.19.0+）、Superpowers、OpenSpec、Plannotator、项目 Skills 和画像，只安装缺失项；普通任务自动触发 setup 时会先汇总并只询问一次。
4. 在 Codex 中信任业务项目，并审查、信任插件自带 Hook。Setup 自动创建 `.codex/ai-coding-workflow/project-profile.yaml`；补齐项目真实命令和风险位置后设为 `ready`。
5. 再开启一个新任务，直接描述需求或使用 `$ai-coding-workflow`。OpenSpec 项目 Skills 位于 `.agents/skills/openspec-*`；Plannotator Skill 不可用但 CLI 可用时，Gate 自动使用 `plannotator review --git`。

Codex 当前不支持插件间依赖声明，因此安装页不会静默连装第三方插件；setup Skill 提供受控的一次性初始化。Superpowers 使用官方插件页或 Codex CLI 的 `/plugins` 交互入口；系统权限、远程安装器和 Hook 信任仍由用户确认。

Codex 默认 Hook profile 不限制编辑。需要规划期写入保护时，把项目画像中的 `hook_profile` 改为 `strict`；切回 `default` 即可，无需重装插件。

## Claude Code 安装

1. 把发行压缩包解压到业务项目根目录；已有 `CLAUDE.md` 或 `.claude/settings.json` 时合并，不覆盖项目规则。
2. 填写 `.claude/project-profile.yaml` 的项目事实和真实验证命令，完成后设置 `profile_status: "ready"`。
3. 安装 Superpowers、OpenSpec、Plannotator；执行 `openspec init` 并选择 Claude Code。
4. 幂等安装生命周期 Hook：

```text
node .claude/scripts/workflow-runtime.mjs install-hooks
```

默认配置不拦截写入。确需严格限制 planning/human-gate 阶段写文件时使用：

```text
node .claude/scripts/workflow-runtime.mjs install-hooks --profile strict
```

两种配置可重复执行和相互切换；安装器只调整本工作流管理的 Hook，保留项目已有 Hook。

5. 重启 Claude Code，使用 `/new-task <需求>`。

## 发行包文件

Codex 发行包为 `ai-coding-workflow-codex.zip`，其根目录是可移植插件：

| 文件 | 运行时用途 |
|---|---|
| `plugin.json` | 通用 Agent Plugin 清单 |
| `.codex-plugin/plugin.json` | Codex 兼容清单和展示信息 |
| `skills/ai-coding-workflow/` | 自动路由入口、规则与节点合同 |
| `skills/ai-coding-workflow-setup/` | 依赖检测、一次性授权和修复流程 |
| `scripts/workflow-runtime.mjs` | 与 Claude 版字节一致的确定性控制器 |
| `scripts/setup-check.mjs` | 只读检查依赖并记录 setup 状态 |
| `hooks/hooks.json` | SessionStart、Stop 和按 profile 生效的 PreToolUse |
| `assets/project-profile.yaml` | 首次接入时复制到业务项目的画像模板 |
| `assets/workflow-state.schema.json` | 状态文件 schema |

Claude Code 发行包为 `ai-coding-workflow-template.zip`：

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
python -B scripts/build_distribution.py --platform all
python -B scripts/validate_workflow.py --archive ai-coding-workflow-template.zip --codex-archive ai-coding-workflow-codex.zip
```

详细行为见项目根目录《AI Coding Workflow Template 详细使用说明》。
