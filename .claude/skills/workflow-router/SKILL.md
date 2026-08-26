---
name: workflow-router
description: 根据需求复杂度和代码库实际影响范围，自动选择 L0/L1/L2/L3 AI Coding Workflow。适用于新 Feature、Bug、Refactoring、Architecture Change 等开发任务。
---

# Workflow Router

## Goal

把用户的自然语言需求路由到最合适的 Workflow Level。

Level 不是开发阶段，而是需求复杂度对应的工作流强度。

## Core Principle

简单任务快速完成，复杂任务增加规格、规划和人工审核。

不要因为任务简单而强行流程化，也不要因为任务复杂而直接编码。

## Assessment Dimensions

读取 `complexity-matrix.md`，从以下维度分析：

1. Scope
2. Business Complexity
3. Code Impact
4. Architecture Impact
5. Data Impact
6. Risk
7. Collaboration

## Assessment Order

### Phase A — Understand

明确：

- Goal
- Scope
- Acceptance Criteria
- Constraints
- Expected Output

### Phase B — Repository Reality

根据任务需要检查：

- 项目结构
- 相关模块
- 相关类
- 数据模型
- API
- MQ / Redis / DB
- 配置
- 测试
- 依赖关系

不要为了评分而无意义地扫描整个仓库。

### Phase C — Score

按照 `complexity-matrix.md` 计算基础分。

### Phase D — Mandatory Rules

按照 `routing-rules.md` 应用最低等级和强制升级规则。

### Phase E — Select

输出：

```text
Workflow Assessment
-------------------
Level:
Score:
Risk:
Scope:
Architecture Impact:
Data Impact:
Reason:
Workflow:
Required Tools:
```

### Phase F — Re-evaluate

代码库探索或实现过程中发现复杂度提升时，立即升级。

允许：

L0 → L1 → L2 → L3

不允许静默降级。

## Tool Mapping

### L0

Claude Code

### L1

Superpowers + Claude Code

### L2

Superpowers + OpenSpec + Claude Code + Plannotator

### L3

Superpowers + OpenSpec + Claude Code + Plannotator + 多 Agent/隔离工作区（需要时）

## Important

不要把 Workflow Level 当成用户必须理解的概念。

用户只需要描述需求。

Router 负责选择流程。
