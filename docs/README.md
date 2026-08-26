---
date created: 2026-08-25 11:55:06
date modified: 2026-08-25 11:56:18
---
# AI Coding Workflow Template

这是一个可复制到 Java / Spring Boot / 微服务项目中的 AI Coding Workflow 模板。

核心思想：

> 根据需求复杂度自动选择 L0/L1/L2/L3 Workflow。

## Components

- Claude Code：执行
- Superpowers：Agent workflow
- OpenSpec：Specification
- Plannotator：Human Review

## Levels

### L0

直接执行。

适合低风险、极小范围任务。

### L1

轻量分析 + Plan + 实现 + 验证。

适合小 Feature。

### L2

Superpowers + OpenSpec + Plan Review + Implementation + Code Review。

适合中型 Feature。

### L3

完整工程流程 + OpenSpec + 人工 Gate + 多 Agent（必要时）+ 集成验证。

适合架构级和高风险需求。

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

## Example

```text
/new-task 给订单增加30分钟自动取消功能
```

Router 会先评估复杂度。

预期可能进入：

```text
L2
```

然后按照 L2 Workflow 执行。

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

这个模板中的复杂度分数只是初始版本。

真正使用几十个需求后，应根据实际数据调整：

- Score threshold
- Mandatory upgrade rules
- High-risk domains
- Review gates
