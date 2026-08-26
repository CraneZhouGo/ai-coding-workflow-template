# AI Coding Workflow Constitution

## 1. Purpose

本项目采用“需求复杂度驱动”的 AI Coding Workflow：

- R1：低风险
- R2：中风险
- R3：高风险
- R4：极高风险（门控叠加）

R1~R4 不是开发生命周期，而是根据需求复杂度选择不同强度的工作流。

核心组件：

- Claude Code：执行引擎
- Superpowers：Agent 工作流能力
- OpenSpec：Specification Source of Truth
- Plannotator：Plan / Code 的人工 Review Gate

## 2. Global Rules

1. 收到新需求后，优先进行 Workflow Assessment（评估风险档 R1~R4）。
2. 不要求用户手动指定档位；默认自动判断。
3. 若探索后发现实际复杂度高于初始判断，必须升级档位。
4. 自动升级允许：R1→R2→R3→R4。
5. 降级不允许静默发生；应向用户说明原因与风险变化并请求确认。
6. 涉及核心交易、支付、库存、权限、数据迁移、基础设施（日志/监控/安全）、跨服务一致性或架构变更时，不能仅凭代码改动数量判断复杂度。
7. R2 及以上在开始编码前必须有明确实现计划，并通过人工 Plan Review。
8. 确认点全标配：任何任务都必须有人工确认（计划确认 + 变更过目），工具强度按风险档分级。
9. 完成后必须验证；高风险变更必须再次进行代码 Review。
10. 不要为了流程而流程：简单任务不要强行套用完整流程。
11. 不要为了省流程而省流程：高风险任务不得降级为简单执行。
12. 每次任务完成按 `.claude/skills/workflow-router/v2/metrics.md` 记录 Metrics。
13. 所有结论必须基于当前代码库实际情况，而不是假设。

## 3. Workflow Selection

先加载：

`.claude/skills/workflow-router/SKILL.md`

再根据判断结果加载：

`.claude/skills/workflow-router/gates/R1.md`
`.claude/skills/workflow-router/gates/R2.md`
`.claude/skills/workflow-router/gates/R3.md`
`.claude/skills/workflow-router/gates/R4.md`

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
