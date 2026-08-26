# AI Coding Workflow Constitution

## 1. Purpose

本项目采用“需求复杂度驱动”的 AI Coding Workflow：

- L0：直接执行
- L1：轻量工作流
- L2：标准工程工作流
- L3：完整工程工作流

L0/L1/L2/L3 不是开发生命周期，而是根据需求复杂度选择不同强度的工作流。

核心组件：

- Claude Code：执行引擎
- Superpowers：Agent 工作流能力
- OpenSpec：Specification Source of Truth
- Plannotator：Plan / Code 的人工 Review Gate

## 2. Global Rules

1. 收到新需求后，优先进行 Workflow Assessment。
2. 不要求用户手动指定 L0/L1/L2/L3；默认自动判断。
3. 如果代码库探索后发现实际复杂度高于初始判断，必须升级 Workflow。
4. 默认允许自动升级：L0→L1→L2→L3。
5. 自动降级不允许静默发生；如果判断可以降级，应向用户说明原因并请求确认。
6. 涉及核心交易、支付、库存、权限、数据迁移、跨服务一致性或架构变更时，不能仅凭代码改动数量判断复杂度。
7. L2/L3 在开始编码前必须有明确的实现计划。
8. L2/L3 的计划应经过人工 Review Gate 后再进入实现。
9. L2/L3 完成后必须进行验证；涉及高风险变更时应再次进行代码 Review。
10. 不要为了流程而流程：简单任务不要强行套用完整工作流。
11. 不要为了省流程而省流程：高风险任务不得降级为简单执行。
12. 所有结论都必须基于当前代码库实际情况，而不是假设。

## 3. Workflow Selection

先加载：

`.claude/skills/workflow-router/SKILL.md`

再根据判断结果加载：

`.claude/skills/workflow-router/workflows/L0.md`
`.claude/skills/workflow-router/workflows/L1.md`
`.claude/skills/workflow-router/workflows/L2.md`
`.claude/skills/workflow-router/workflows/L3.md`

## 4. Project Engineering Rules

以下规则由具体项目继续补充：

- Java version:
- Spring Boot version:
- Spring Cloud version:
- Build tool:
- Database:
- Cache:
- MQ:
- Registry:
- Observability:
- Test framework:

## 5. Completion Requirements

任何级别的任务都必须在完成前回答：

- What changed?
- Why was it changed?
- What tests were run?
- What remains unverified?
- Were there unexpected side effects?

不得在没有实际验证的情况下声称“已完成”。
