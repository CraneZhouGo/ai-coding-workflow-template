# AI Coding Workflow Template V3.2 Composable

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
| Standard | 普通修改的默认安全网 | propose/apply/validate/archive + workflow-state | 一次 Plan Review |
| Governed | 高风险事实触发；完整交付证据与隔离 | explore + Standard 生命周期与状态 | Plan + Code Review |

模式不再规定固定业务节点。Standard Feature 和 Standard Bug 共享相同保障，但使用不同 Task Method。专项 Gate 可叠加，不需要新增第四种模式。

## Continuous execution and resume

Route Card 只是通知。Router 不会询问是否采用模式，也不会在内部节点间逐步确认。Standard 唯一预定暂停点是 Plan Review；Governed 再增加 Code Review。

Standard/Governed 会在当前 OpenSpec change 内维护：

```text
openspec/changes/<change-id>/workflow-state.yaml
```

它记录 intent、task type、mode、gates、ordered nodes、状态和证据。对话中断或压缩后，Router 从最早未完成 REQUIRED 节点继续，不重复已完成步骤。

## Tool ownership

- Superpowers：提供 brainstorming、systematic-debugging、planning、TDD、review、verification 等方法。
- OpenSpec：保存 Standard/Governed 的规格、任务与编排状态。
- Plannotator：承载计划和代码的人类决策 Gate。
- Claude Code：执行探索、编辑、命令、测试、Git 与工具交接。

Integration Adapter Contract 会合并工具默认流程中的重复批准和重复文档；OpenSpec 子流程的 stop/ready 只返回 Router，后续节点自动继续。

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
