---
name: workflow-router
description: 根据需求复杂度和代码库实际影响范围，自动评估风险档 R1/R2/R3/R4 并加载对应门控流程。适用于新 Feature、Bug、Refactoring、Architecture Change 等开发任务。
---

# Workflow Router v2

## Goal
把用户自然语言需求路由到最合适的风险档（R1~R4），并给出该档必须开启的门控。

## Core Principle
简单任务快速完成，复杂任务增加规格、规划与人工评审。不要因为简单而流程化，也不要因为复杂而直接编码。

## 输入模板（Phase A）
明确 Goal / Scope / Non-goals / Acceptance Criteria / Constraints。
R2 及以上若 AC/Constraints 缺失，必须追问补齐；R1 可省略。

## 代码库探索（Phase B）
只探索任务相关范围，防止过度扫描。发现复杂度提升时立即 Re-evaluate。

## 评分（Phase C）
读取 `v2/complexity-matrix.md`，按 8 维加权评分，记录各维度明细。

## 规则应用（Phase D）
读取 `v2/routing-rules.md`，应用红旗升档规则与用户覆盖规则。

## 合并与输出（Phase E）
final_tier = max(level_from(weighted_score), level_from(rules), level_from(red_flags))
读取 `v2/levels.md` 加载对应门控配置。
输出 Assessment：

Workflow Assessment
-------------------
final_tier: R{n}
score: {n}/39
dimensions:
  scope: n | business: n | code: n | architecture: n
  data: n | infrastructure: n | risk: n | collaboration: n
red_flags_hit: [list]
reason: ...
workflow: gates/R{n}.md
required_tools: [...]

## Tool Check（Phase F）
读取 `v2/toolcheck.md`，按 final_tier 检查工具可用性，缺失给初始化引导。

## Re-evaluate（Phase G）
升级自动；降级需说明原因+被移除流程+风险变化并请求确认。

## 完成后
按 `v2/metrics.md` 记录一条 record，按 CLAUDE.md「完成要求」报告。
