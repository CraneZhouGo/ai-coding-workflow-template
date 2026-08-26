---
date created: 2026-08-25 11:55:06
date modified: 2026-08-27
---
# AI Coding Workflow Template

这是一个可复制到 Java / Spring Boot / 微服务项目中的 AI Coding Workflow 模板。

核心思想：

> 根据需求复杂度自动评估风险档 R1~R4，并叠加对应门控。

## Components

- Claude Code：执行
- Superpowers：Agent workflow（过程方法论）
- OpenSpec：Specification Source of Truth（产物）
- Plannotator：Human Review Gate（评审）

工具职责边界一句话：

> 产物归 OpenSpec、过程归 Superpowers、评审归 Plannotator、执行归 Claude Code。

## Risk Tiers

### R1（Low）

直接执行，最小改动。

适合低风险、极小范围任务（明确小 Bug、文案、单点配置）。

### R2（Medium）

需求分析 + 代码探索 + OpenSpec（proposal/specs/tasks）+ Plan Review + TDD 实现 + Code Review。

适合常规 Feature、新查询接口、CRUD 增强。

### R3（High）

OpenSpec（含 design.md）+ Plannotator Plan/Code Review + 规格/架构确认 + 集成/契约测试。

适合订单状态机、日志基础设施集成、Schema 变更等中高风险需求。

### R4（Critical）

完整工程流程 + design.md/ADR + WBS 计划 + 多 Agent / 隔离 Worktree（必要时）+ 集成验证 + apply/archive + 发布审批。

适合微服务拆分、核心架构重构、核心交易链路、数据迁移。

## Tool Check

路由输出风险档后、执行流程前，会检查该档所需工具是否可用，缺失则给出初始化引导（例如 R2+ 需要 OpenSpec 与 Plannotator，R4 需要 git worktree）。

## Metrics

每次任务完成后自动记录一条 Metrics 记录，可用 `/workflow-report` 汇总升级率、各档分布、返工率并给出调参建议。

## Quick Start

1. 将 `.claude/` 和 `CLAUDE.md` 复制到项目根目录。
2. 安装并启用 Superpowers。
3. 初始化 OpenSpec。
4. 安装/配置 Plannotator。
5. 启动 Claude Code。
6. 使用：

```text
/new-task 你的需求
```

7. 定期使用：

```text
/workflow-report
```

## Example

```text
/new-task 给订单增加30分钟自动取消功能
```

Router 会先评估复杂度，并自动执行 Tool Check。

预期可能进入：

```text
R3
```

然后按照 R3 门控流程执行。

## Existing Project

对于已有项目，建议第一次先让 Claude Code：

```text
分析当前项目架构、模块边界、核心业务链路、测试方式和现有工程规范，
并根据这些信息补充 CLAUDE.md 中的项目工程规则。
```

## New Project

新项目建议：

1. 创建 Git repository
2. 初始化项目
3. 安装 Claude Code
4. 安装 Superpowers
5. 初始化 OpenSpec
6. 安装 Plannotator
7. 复制本模板
8. 完善 CLAUDE.md
9. 用 `/new-task` 开始第一个需求

## Important

这个模板中的评分阈值和权重只是初始建议值。

真正使用几十个需求后，应根据 `/workflow-report` 输出的实际数据调整：

- Score thresholds
- Weights
- Red-flag rules
- High-risk domains
- Review gates
