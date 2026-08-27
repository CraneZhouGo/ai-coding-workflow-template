# AI Coding Workflow Template V3.2.2 Composable

这是一个面向 Claude Code 的薄编排模板。它不重新实现 Superpowers、OpenSpec 或 Plannotator，而是先识别意图，再把任务方法、风险保障和专项 Gate 自动组合成一次任务真正需要的流程。

```text
Intent → Task Type → Risk Mode → Specialized Gates → Ordered Execution

Final workflow
= Core Spine
+ Task Method
+ Risk Safeguards
+ Specialized Gates
```

用户只需描述需求，或使用：

```text
/new-task <需求>
```

## Four routing dimensions

| 维度 | 选项 | 决定什么 |
|---|---|---|
| Intent | explain / review / diagnose-only / plan-only / change | 是否获得修改授权 |
| Task Type | Feature / Bug / Refactor / Upgrade-Config / Migration-Infrastructure / Maintenance | 使用哪组 Superpowers 方法 |
| Risk Mode | Fast / Standard / Governed | OpenSpec、评审、隔离和验证强度 |
| Specialized Gates | data / security / contract / infrastructure / release / observability | 需要补充哪些风险证据 |

这解决了固定模式链的错配：普通 Feature 走 brainstorming、规格和 TDD；Bug 先 systematic-debugging、根因证据和失败回归测试；重构先建立行为基线；升级先查 changelog 与兼容性；迁移先做影响、回滚和 dry-run。

## Three risk modes

| 模式 | 准入与保障 | OpenSpec | Plannotator |
|---|---|---|---|
| Fast | 全部低风险条件成立；最窄探索和直接验证 | 不创建新 change | 无预定 Gate |
| Standard | 普通修改的默认安全网 | Agent propose/apply-change + CLI validate/archive + workflow-state | 一次 OpenSpec Spec Diff Review |
| Governed | 高风险事实触发；完整交付证据与隔离 | explore + Standard 生命周期与状态 | Spec Diff + Code Diff Review |

模式不再规定固定业务节点。Standard Feature 和 Standard Bug 共享相同保障，但使用不同 Task Method。专项 Gate 可叠加，不需要新增第四种模式。

## Continuous execution and resume

Route Card 只是通知。Router 不会询问是否采用模式，也不会在内部节点间逐步确认。Standard 唯一预定暂停点是 OpenSpec Spec Diff Review；Governed 再增加实施后的 Code Diff Review。

Standard/Governed 会在当前 OpenSpec change 内维护：

```text
openspec/changes/<change-id>/workflow-state.yaml
```

它记录 intent、task type、mode、gates、ordered nodes、Git review base、状态、证据和 Spec Diff Review 已批准规划工件的 SHA-256。对话中断后从最早未完成节点继续；规划工件变化时自动重新打开 diff。

## Tool ownership

- Superpowers：提供 brainstorming、systematic-debugging、planning、TDD、review、verification 等方法。
- OpenSpec：保存规格、任务与编排状态；`/opsx:apply` 或 `openspec-apply-change` 是 Agent 实施入口，不是终端 CLI。
- Plannotator：通过 `/plannotator-review` 的文件树和逐行 diff 承载 OpenSpec 文档与代码评审。
- Claude Code：执行探索、编辑、命令、测试、Git 与工具交接。

Integration Adapter Contract 会合并工具默认流程中的重复批准和重复文档；OpenSpec 子流程的 stop/ready 只返回 Router，后续节点自动继续。

Spec Diff Gate 前，Router 会记录 Git baseline；若存在用户原有修改则先进入隔离 worktree。OpenSpec 文档生成后，只有 `openspec/changes/<change-id>/**` 可以出现在当前 diff，再调用 `/plannotator-review` 直接展示变化文件。不会创建 Review Packet，也不会手动拼接文档正文。

OpenSpec 入口严格区分：

```text
/opsx:apply <change-id>                         # Claude Code Agent command
openspec-apply-change                           # 生成的 Agent skill
openspec instructions apply --change <id> --json # 官方 CLI fallback
openspec apply                                  # 不存在，禁止调用
```

## Business package

分发包仍只有 6 个运行时文件：

```text
CLAUDE.md
.claude/project-profile.yaml
.claude/skills/new-task/SKILL.md
.claude/skills/workflow-router/SKILL.md
.claude/skills/workflow-router/ROUTING.md
.claude/skills/workflow-router/PLAYBOOKS.md
```

业务项目不会收到 Python、测试、评测案例或模板 CI。

## Setup

1. 将分发包解压到项目根目录；已有 `CLAUDE.md` 时合并规则，不直接覆盖项目约定。
2. 填写 `.claude/project-profile.yaml` 的真实验证命令、关键目录、风险和交付能力。
3. 安装 Superpowers、OpenSpec 和 Plannotator，并重启 Claude Code。
4. 执行 `openspec init` 并选择 Claude Code；OpenSpec 升级后执行 `openspec update`。
5. 使用 `/new-task <需求>`；Router 自动分类、组合、执行和续跑。

详细行为见项目根目录《AI Coding Workflow Template 详细使用说明》。

## Maintainer validation

```text
python -B scripts/validate_workflow.py
python -B scripts/evaluate_routing.py
python -B -m unittest discover -s tests -v
python -B scripts/build_distribution.py
python -B scripts/validate_workflow.py --archive ai-coding-workflow-template.zip
```
