---
name: workflow-router
description: 按 Intent、Task Type、Risk Mode 和 Specialized Gates 组合并连续执行工作流；可从 OpenSpec workflow-state.yaml 恢复，Route Card 后不请求流程确认。
user-invocable: false
---

# Workflow Router — V3.2.1 Composable

本 skill 负责分类、组合、持久化和执行推进。它不把三种模式误当作三条固定业务流程。

## 1. Resume before reroute

读取 `.claude/project-profile.yaml`。若 `state.resume_incomplete` 为 true，先查找 `openspec/changes/*/workflow-state.yaml` 中的 active/blocked 状态：

- 当前请求与唯一活动 change 匹配时，读取其 OpenSpec 工件和状态，从最早未完成 REQUIRED 节点继续。
- 已完成节点不得重复执行；blocked 节点在阻断条件解除后转为 in_progress。
- 多个 change 均可能匹配且无法从上下文消歧时，才暂停请用户选择。
- 没有可恢复状态时，按新任务处理。

## 2. Intent

按 `ROUTING.md` 分类为 `explain | review | diagnose-only | plan-only | change`。非 change 只执行对应只读分支，不选择风险模式，也不产生修改。

## 3. Evidence and classification

对 change 从最窄范围收集：用户可观察行为、验收条件、直接修改与消费者、公共契约/Schema/权限/关键语义、回滚和发布约束。

依次确定：

1. Task Type：feature、bug、refactor、upgrade-config、migration-infrastructure 或 maintenance。
2. Risk Mode：先应用 Governed 风险下限，再检查 Fast 全部准入条件，其余 Standard。
3. Specialized Gates：data、security、contract、infrastructure、release、observability，可为多个或 none。

关键词只是调查线索，代码库事实和行为影响才是证据。

## 4. Capability check

确认组合后实际需要的能力可调用：

- 对应 Superpowers 原生 skills
- Standard/Governed 的 OpenSpec Agent 入口：Claude Code `/opsx:apply` command 或 `openspec-apply-change` skill
- OpenSpec CLI：`status`、`instructions apply`、`validate` 和 `archive`；不得把 `/opsx:apply` 误当作 `openspec apply` CLI
- 当前模式需要的 Plannotator Hook/review
- 项目验证命令和专项 Gate 所需验证能力

能力可用就直接继续。缺失时先尝试无损恢复；只有替代方案降低保障才暂停。

## 5. Compose and persist

读取 `PLAYBOOKS.md`，按以下公式展开一个去重、有序的节点账本：

```text
Core Spine + Task Method + Risk Safeguards + Specialized Gates
```

相同语义节点只保留一次，以更严格的验证要求为准。Standard/Governed 在 OpenSpec propose 获得 change id 后立即创建 `openspec/changes/<change-id>/workflow-state.yaml`，并在每个节点边界更新。Planning 节点必须位于 Plan Review 前，任何写代码、写测试或执行 dry-run 的 Implementation 节点必须位于批准后。

## 6. Execute without gaps

节点账本格式：

```text
node | source(core|method|mode|gate) | required | status(pending|in_progress|done|N/A|blocked) | evidence
```

- REQUIRED 节点必须显式调用相应原生 skill/command。
- 不适用时写 `N/A + evidence`；任务方法不能因风险模式变化而被错误替换。
- Plan Review 前生成完整 Change Review Packet 并通过 ExitPlanMode 的 `tool_input.plan` 提交；记录所有评审文件哈希，Gate 后哈希变化必须重新评审。
- OpenSpec apply-change 是实施阶段外层入口，负责读取 change、选择未完成 tasks 和更新任务状态；Superpowers 方法在其内部负责 debugging、TDD、executing-plans 和 verification，不再作为第二个并列实施器重复执行。
- 节点完成后自动持久化并进入下一节点，不询问许可。
- OpenSpec 子工作流完成后返回 Router，不要求用户手动触发下一命令。

## 7. Re-route

探索后、发现契约/Schema/权限/关键语义变化、diff 扩大和交付前，重新评估 task type、mode 和 gates。升级或新增 Gate 后，从新组合中最早未完成 REQUIRED 节点继续，不重复等价节点，也不请求模式确认。

## 8. Complete

只有组合后所有 REQUIRED 节点均为 done 或有证据的 N/A，项目验证、Review 和 `openspec validate <change-id>` 均通过，才能将 Standard/Governed 状态标记 completed；随后 archive 并声明完成。
