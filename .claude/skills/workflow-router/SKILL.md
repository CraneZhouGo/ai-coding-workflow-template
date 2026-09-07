---
name: workflow-router
description: 按 Intent、Task Type、Risk Mode 和 Specialized Gates 确定性组合并连续执行工作流；可从 OpenSpec workflow-state.json 恢复，Route Card 后不请求流程确认。
user-invocable: false
---

# Workflow Router — V3.3 Deterministic Composable

本 skill 负责事实提取和任务执行；`.claude/scripts/workflow-runtime.mjs` 是路由、节点顺序和状态转换的唯一执行源。不得在 Markdown 中手工模拟脚本结果。

## 1. Resume before reroute

读取 `.claude/project-profile.yaml`。若 `profile_status` 不是 `ready`，先通过最窄项目探索补齐真实构建/测试命令、关键目录和交付能力；无法从仓库确定的事实才询问。画像未完成时禁止 Fast。

若 `state.resume_incomplete` 为 true，先运行 runtime `next` 或查找 `openspec/changes/**/workflow-state.json` 中的 active/blocked 状态：

- 当前请求与唯一活动 change 匹配时，读取其 OpenSpec 工件和状态，从最早未完成 REQUIRED 节点继续。
- 已完成节点不得重复执行；blocked 节点在阻断条件解除后转为 in_progress。
- 多个 change 均可能匹配且无法从上下文消歧时，才暂停请用户选择。
- 没有可恢复状态时，按新任务处理。旧版 YAML 状态只迁移一次为 schema v2 JSON，不并行维护两份状态。

## 2. Intent

按 `ROUTING.md` 提取结构化 `route_facts`，再调用 runtime `route`。非 change 只执行对应只读分支，不创建状态，也不产生修改。

## 3. Evidence and classification

对 change 从最窄范围收集：用户可观察行为、验收条件、直接修改与消费者、公共契约/Schema/权限/关键语义、回滚和发布约束。

脚本依次确定：

1. Task Type：feature、bug、refactor、upgrade-config、migration-infrastructure 或 maintenance。
2. Risk Mode：先应用 Governed 风险下限，再检查 Fast 全部准入条件，其余 Standard。
3. Specialized Gates：data、security、contract、infrastructure、release、observability，可为多个或 none。

关键词只是调查线索，代码库事实和行为影响才是证据。相同 facts、profile 状态和工作流版本必须产生相同 route fingerprint。

## 4. Capability check

确认组合后实际需要的能力可调用：

- 对应 Superpowers 原生 skills
- Standard/Governed 的 OpenSpec Agent 入口：Claude Code `/opsx:apply` command 或 `openspec-apply-change` skill
- OpenSpec CLI：`status`、`instructions apply`、`validate` 和 `archive`；不得把 `/opsx:apply` 误当作 `openspec apply` CLI
- Standard/Governed 的 Plannotator `/plannotator-review`；不把 ExitPlanMode Plan Review Hook 用作预定 Gate
- 项目验证命令和专项 Gate 所需验证能力
- Node.js 与 `.claude/hooks/workflow-hooks.json`；首次接入运行 runtime `install-hooks`，幂等合并到 `.claude/settings.json`

能力可用就直接继续。缺失时先尝试无损恢复；只有替代方案降低保障才暂停。

## 5. Compose and persist

先读 `ROUTING.md`，再只读取 `PLAYBOOKS.md` 中公共合同、已选 Task Method、Risk Safeguards 和实际 Specialized Gates。调用 runtime `compose` 展开去重、有序的节点账本：

```text
Core Spine + Task Method + Risk Safeguards + Specialized Gates
```

相同语义节点只保留一次，以更严格的验证要求为准。Standard/Governed 在任何规划写入前记录 Git baseline；已有未提交修改时先进入隔离 worktree。OpenSpec propose 获得 change id 后，用 runtime `init-state` 创建 `workflow-state.json`，并为 propose 前已完成的连续节点提供真实 evidence。Planning 节点必须位于 Spec Diff Review 前，任何写代码、写测试或执行 dry-run 的 Implementation 节点必须位于批准后。

## 6. Execute without gaps

状态遵循 `.claude/workflow-state.schema.json`。每次只执行 runtime `next` 返回的 current node：

```text
node | phase | prerequisites | source(core|method|mode|gate) | required | status | evidence[]
```

- 节点开始和完成分别调用 runtime `transition`；`done | N/A | blocked` 必须有 evidence，非法跳转会被拒绝。
- REQUIRED 节点必须显式调用相应原生 skill/command；任务方法不能因风险模式变化而被错误替换。
- S-DF1 使用 runtime `capture-spec-diff`，只接受当前 change 的 uncommitted 文件并计算 artifact hash。
- S-HG1 调用 `/plannotator-review`，确认界面处于 `uncommitted` 视图；用 runtime `review --type spec` 校验 displayed paths 与 expected paths 完全一致。规划哈希变化时 runtime 自动退回 S-DF1。
- Governed 的 G-HG1 使用 `since-base` 视图和 runtime `review --type code`。
- OpenSpec apply-change 是实施阶段外层入口，负责读取 change、选择未完成 tasks 和更新任务状态；Superpowers 方法在其内部负责 debugging、TDD、executing-plans 和 verification，不再作为第二个并列实施器重复执行。
- 节点完成后脚本自动持久化并进入下一节点，不询问许可。PreToolUse Hook 阻止规划阶段越界编辑；Stop Hook 阻止仍有可执行 REQUIRED 节点时提前结束。
- OpenSpec 子工作流完成后返回 Router，不要求用户手动触发下一命令。

## 7. Re-route

只在 `post-exploration | root-cause-known | boundary-discovered | diff-expanded | pre-delivery` 检查点调用 runtime `reroute`。必须记录新 facts 和 reason；runtime 会确认检查点前置节点已经完成。自动重路由只升级，降级需要明确授权。Fast 升级时先创建 OpenSpec change，并通过 `change_id + --output openspec/changes/<change-id>/workflow-state.json` 原子迁移唯一状态文件。脚本冻结新 workflow hash，从最早未完成 REQUIRED 节点继续。

## 8. Complete

Fast 在 C7 完成后结束。Standard/Governed 先完成参数化验证、Review 和 `openspec validate <change-id> --strict --no-interactive`，S-FI1 将 archive_status 置为 ready，再运行 `openspec archive <change-id> --yes`。归档成功后在 archive 目录调用 runtime `archive-complete`，最后才能把状态标记 completed。
