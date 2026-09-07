# V3.3 Deterministic Composable Architecture Decision

## 问题

V3.2.2 已把固定模式链拆成 Task Method、Risk Safeguards 和 Specialized Gates，但最终分类、节点推进和续跑仍主要依赖模型遵守 Markdown。相同需求在不同上下文可能产生不同节点；状态缺少机器可校验的转换；上下文压缩或工具子流程返回后也可能提前结束。

## 决策

保留三种风险模式，不新增第四种固定流程；增加一个无外部依赖的 Node runtime 作为唯一控制面：

```text
AI: requirement/code evidence → route_facts
Runtime: facts → route fingerprint → ordered nodes → workflow hash
Agent: execute current node → evidence
Runtime: validate transition → persist → next node
```

组合公式仍为：

```text
Core Spine + Task Method + Risk Safeguards + Specialized Gates
```

同时从风险模式派生 `planning_depth`、`validation_scope`、`isolation`、`review_policy` 和 `execution_strategy`，使模式保持粗粒度风险层，执行策略保持可调，而不产生模式组合爆炸。

## 确定性边界

- AI 可以补充证据和 route facts，但不能手工覆盖 runtime 的 mode、Gate 或节点顺序。
- 相同工作流版本、profile 状态和 facts 必须产生相同 `route_fingerprint`；相同 route 必须产生相同 `workflow_hash`。
- 项目画像未明确 `ready` 时 Fast fail closed；Feature 最低 Standard。
- 状态只允许法定转换，完成、阻塞和 N/A 都需要 evidence；人工 Gate、Spec Diff 捕获和 archive completion 只能由专用命令推进。
- 自动重路由只允许在固定检查点升级；降级需要明确授权并写入历史。

## 工具边界

```text
Runtime: route + compose + state + hook guards
Superpowers: development methods
OpenSpec: durable requirements/design/tasks + lifecycle
Plannotator: human diff decisions
Claude Code: exploration + edits + commands + verification
```

OpenSpec apply 使用 `/opsx:apply` 或生成的 apply-change skill；CLI fallback 只读取 `openspec instructions apply`，不调用不存在的 `openspec apply`。规划 Gate 调用 `/plannotator-review` 的 `uncommitted` 视图并展示真实 OpenSpec 文件；Governed 代码 Gate 使用 `since-base`。

## 生命周期约束

借鉴 Everything Claude Code 的 session lifecycle 思路，但只采用与本模板问题直接相关的四个轻量 Hook：

- SessionStart：注入唯一活动状态的 current node。
- PreToolUse(Edit/Write)：阻止规划阶段修改业务文件。
- PreCompact：原子保存并记录压缩次数。
- Stop：存在可继续节点时阻止提前结束；人工 Gate、真实 blocked 和 stop-hook 重入时放行。

没有引入每次编辑全量格式化/类型检查、tmux 依赖、通用会话日志、全量 Agent/MCP 或固定覆盖率阈值。验证命令来自项目画像，专项 Agent 只在实际风险触发时使用。

## 状态与归档

Fast 状态位于被忽略的 `.claude/workflow-runs/`；Standard/Governed 状态位于当前 OpenSpec change。JSON schema v2 保存 facts、两个哈希、ordered nodes、证据、Review 路径/哈希和 reroute history。

Standard/Governed 不得在 archive 前标记 completed：

```text
verify/review → openspec strict validate → archive_status ready
→ openspec archive --yes → runtime archive-complete → completed
```

## 结果与代价

- 同一事实得到稳定模式与节点，Hook 和状态账本降低重复确认、漏节点和压缩后漂移。
- Feature brainstorming、Bug debugging、OpenSpec lifecycle 和两个 Plannotator 视图都有可检查的明确节点。
- 风险强度、任务方法和专项风险仍正交，Token 不会因新增固定模式而线性增长。
- 代价是业务包增加一个 Node runtime、一个 schema、一个 Hook 片段和 Fast 状态忽略文件；首次接入需要填写画像并安装一次 Hook。
