---
description: 自动分析需求复杂度并选择 R1/R2/R3/R4 Workflow
---

# New Task

你现在负责处理一个新的开发需求。

## Step 1 — Workflow Assessment
1. 读取 `.claude/skills/workflow-router/SKILL.md` 及其引用的 v2 组件（complexity-matrix/routing-rules/levels/toolcheck）。
2. 理解需求，结合代码库做必要探索。
3. 按 8 维加权评分，应用红旗规则，输出 final_tier 与 Assessment。
4. 执行 Tool Check（确认 OpenSpec/Plannotator 可用性）。
5. 加载 `gates/R{n}.md`。

## Step 2 — Execute Selected Workflow
严格执行对应 gates/R{n}.md 中的流程。

## Step 3 — Re-evaluation
实现前若发现影响范围扩大/跨模块/跨服务/数据结构变化/核心规则变化/高风险链路/需多 Agent，重新评估 final_tier，如需升级立即升级。

## Step 4 — Final Verification
完成后记录 metrics，并报告：
- Initial tier / Final tier
- Changed Files
- Tests / Verification Result
- Review Result
- Remaining Risks
