---
description: 评估变更风险，组合所需门控并执行 R1/R2/R3/R4 Workflow
---

# New Task v2.1

## Step 1 — Context

读取 `.claude/project-profile.yaml`、`CLAUDE.md` 和 `.claude/skills/workflow-router/SKILL.md`。

## Step 2 — Assessment

1. 结合代码库证据按 7 个锚定维度评分，得到 baseline tier。
2. 应用语义红旗，得到 final tier。
3. 组合基础、语义和交付门控。
4. 独立生成 Delivery Profile；Agent 数量不参与风险评分。
5. 输出完整 Workflow Assessment。

## Step 3 — Capability Check

探测 OpenSpec、评审、Git/worktree、构建测试、迁移和发布能力。输出 available/degraded/missing；需要批准或被阻塞时不得静默继续。

## Step 4 — Execute

加载 `gates/R{n}.md` 和 `v2/gates.md`。执行基础流程与全部 required gates。R1 仅在满足项目画像条件时使用 Fast Path。

## Step 5 — Re-evaluate

在探索后、修改公共契约/Schema/权限/部署配置前、diff 超出范围时、发布前重新评估。

## Step 6 — Completion

追加 JSONL Metrics，并报告 Initial/Final Tier、Score、Required Gates、Delivery Profile、Changed Files、Tests、Reviews、Capability Degradations、Remaining Risks 和 Side Effects。
