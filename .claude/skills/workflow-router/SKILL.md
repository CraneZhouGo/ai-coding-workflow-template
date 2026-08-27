---
name: workflow-router
description: 根据变更本身的风险证据评估 R1/R2/R3/R4，并将语义门控和交付门控组合为可执行工作流。适用于 Feature、Bug、Refactoring、Architecture Change 等开发任务。
---

# Workflow Router v2.1

## Goal

稳定地回答三个不同问题：

1. 变更本身的风险档位是什么？
2. 数据、安全、契约、基础设施、合规和发布等哪些门控必须叠加？
3. 单 Agent、多 Agent、worktree 和协调发布采用什么交付策略？

风险、门控和交付策略分别判断，避免循环推理和重复加分。

## Phase A — 需求输入

明确 Goal / Scope / Non-goals / Acceptance Criteria / Constraints。R2+ 缺少 AC 或约束时必须补齐；R1 可以使用简化输入。

R2+ 使用 `superpowers:brainstorming` 的方法澄清需求，结论写入唯一规格产物，不额外创建重复文档。

## Phase B — 代码库与项目画像

1. 读取 `.claude/project-profile.yaml`。
2. 只探索与需求相关的代码、测试、契约、数据和部署范围。
3. 对每个评分和门控记录证据，不按目录名或业务关键词直接升档。

## Phase C — 风险评分

读取 `v2/complexity-matrix.md`：

- 按 7 个锚定维度计算 0~36 分。
- 得到 `baseline_tier`。
- 独立生成 Delivery Profile，不将 Agent 数量计入风险分。

## Phase D — 语义红旗与门控

1. 读取 `v2/routing-rules.md`，按变更语义计算 `final_tier`。
2. 读取 `v2/gates.md`，把语义门控和交付门控叠加到基础档位门控。
3. 不适用的高风险门控必须给出依据。

## Phase E — Assessment 输出

```text
Workflow Assessment
-------------------
baseline_tier: R{n}
final_tier: R{n}
score: {n}/36
dimensions:
  scope: n | business: n | code_impact: n | architecture: n
  data: n | infrastructure: n | runtime_risk: n
evidence: [...]
semantic_red_flags: [...]
required_gates: [...]
delivery_profile:
  agents: 1|2+ | worktrees: none|optional|required
  rollout: none|standard|coordinated | ownership: single|multi-team
workflow: gates/R{n}.md + v2/gates.md
```

## Phase F — Capability Check

读取 `v2/toolcheck.md`。能力状态分为 `available`、`degraded`、`missing`：

- 可安全降级时，说明替代路径并写入 Metrics。
- R3/R4 的规格或评审能力降级需要用户明确批准。
- 缺少构建、迁移或回滚能力且门控要求它们时，不得声称完成。

## Phase G — 执行

读取 `v2/levels.md` 和 `gates/R{n}.md`，执行基础流程与全部 required gates。

R1 满足项目画像中的快速通道条件时，可以在宣布简短计划后直接执行；否则先确认计划。

## Phase H — Re-evaluate

按 `routing-rules.md` 的检查点重新评分。升级自动发生；降级必须说明评分变化、移除门控和残余风险，并请求确认。

## Completion

1. 验证实现、规格、门控产物和最终 diff。
2. 按 `v2/metrics.md` 生成记录，并通过 `scripts/record_workflow_metric.py` 校验后向 JSONL 追加。
3. 按 CLAUDE.md 完成要求报告，包括能力降级和未验证事项。
