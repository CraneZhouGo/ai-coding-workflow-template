# V3.2.2 Composable Architecture Decision

## Problem

V3.1 用 Fast、Standard、Governed 三条有序状态机补全了工具节点和自动推进，但 Standard 固定链隐含了“所有普通任务都是功能开发”。结果是 Bug、重构、升级和维护也被迫先 brainstorming；流程节点越补越长，Token 使用与任务价值失衡。同时节点状态只依赖当前上下文，中断后容易重复执行或再次确认。

## Decision

把工作流从一维模式切换为四维组合：

```text
Intent → Task Type → Risk Mode → Specialized Gates → Ordered Execution
```

最终工作流为：

```text
Core Spine + Task Method + Risk Safeguards + Specialized Gates
```

- Intent 管授权：解释、评审、仅诊断、仅计划或修改。
- Task Type 管方法：Feature、Bug、Refactor、Upgrade/Config、Migration/Infrastructure、Maintenance。
- Risk Mode 管保障：Fast、Standard、Governed。
- Specialized Gates 管领域证据：data、security、contract、infrastructure、release、observability。

组合器按阶段插入节点、去重等价能力并采用更严格的验证要求。模式不再复制任务方法。

## Tool boundaries

```text
Router: classify + compose + resume
Superpowers: development methods
OpenSpec: durable artifacts + workflow state
Plannotator: human decisions
Claude Code: edits + commands + verification + git
```

Integration Adapter Contract 保留各工具的核心方法，但把重复设计文档和审批合并到 OpenSpec 单一事实源与 Plannotator Gate。子流程 stop 只返回 Router。

V3.2.2 明确两项真实集成边界：

- `/opsx:apply` 与 `openspec-apply-change` 是宿主 Agent 入口，不是 `openspec apply` CLI；低层 CLI fallback 是 `openspec instructions apply --change <id> --json`。
- Standard/Governed 的规划 Gate 使用 `/plannotator-review` 展示当前 OpenSpec change 的 VCS 文件 diff，不使用 ExitPlanMode，也不拼接文档正文。

OpenSpec apply-change 是实施阶段外层入口，负责读取 change 和更新 tasks；Superpowers debugging/TDD/execution methods 在其内部提供实施方法，避免两个并列执行器重复执行。

## Durable state

Fast 的账本只存在当前对话。Standard/Governed 在：

```text
openspec/changes/<change-id>/workflow-state.yaml
```

记录路由维度、Git review base、当前节点、完整节点账本、状态、证据和已评审 artifact hash。新回合优先匹配未完成 change；Spec Diff Gate 后任何规划工件哈希变化都会使批准失效。该 sidecar 不复制 OpenSpec proposal/spec/design/tasks。

## Human attention

- Route Card、内部节点、模式升级和本地 OpenSpec 生命周期不是 Gate。
- Standard 只有 OpenSpec Spec Diff Review。
- Governed 只有 Spec Diff Review 与 Code Diff Review 两类预定 Gate。
- 能从需求与代码库证据解决的问题不向用户重复确认。

## Consequences

- Feature 的 brainstorming 不会丢失。
- Bug 默认使用 systematic-debugging，不为凑固定链浪费 brainstorming Token。
- 高风险 Bug 仍可获得 Governed 保障；任务方法与风险强度正交。
- 新风险通过 Gate 组合扩展，无需增加模式或复制完整流程。
- 状态持久化提升长任务、上下文压缩和人工 Gate 后的连续性。
- Bug 回归测试、characterization tests 和 migration dry-run 均位于 Spec Diff Review 批准后的 implementation phase。
- Plannotator 文件树直接展示本次 OpenSpec 变化；Git baseline、早期隔离和 path allowlist 防止混入无关文件。

代价是 Router 必须正确分类并维护节点账本，因此模板用可执行路由案例、结构校验和组合合同测试防止漂移。
