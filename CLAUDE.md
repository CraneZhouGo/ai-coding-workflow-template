# AI Coding Workflow Constitution v2.1

## 1. Purpose

本项目采用“变更风险 + 可组合门控 + 交付策略”工作流：

- R1：低风险
- R2：中风险
- R3：高风险
- R4：极高风险

风险档不是生命周期。完整工程流程为 S0~S9，Router 按风险选择基础流程，再叠加数据、安全、合规、契约、基础设施、发布、可观测性和隔离门控。

核心职责：产物归 OpenSpec、过程归 Superpowers、评审归 Plannotator、执行归 Claude Code。工具不可用时按 Capability Check 使用有审计记录的替代路径，门控本身不能静默消失。

## 2. Global Rules

1. 新需求先读取 `.claude/project-profile.yaml` 并执行 Workflow Assessment。
2. 按 `.claude/skills/workflow-router/v2/complexity-matrix.md` 的 7 个锚定维度评估变更本身，不能凭目录名、业务关键词或文件数量猜测。
3. Collaboration、多 Agent、worktree 和跨团队协作属于 Delivery Profile，不计入风险总分。
4. 按语义红旗计算最低安全档；支付、库存等领域中的纯文案不自动升档，改变其核心业务语义时不得降档。
5. 最终工作流等于基础档位门控与 required gates 的并集；同一产物不重复创建。
6. 探索后、修改公共契约/Schema/权限/部署配置前、diff 扩大时和发布前必须重新评估。
7. 升级自动发生；降级必须说明评分变化、移除门控和残余风险，并请求确认。
8. R1 只有满足 `gates/R1.md` 和项目画像全部条件时才能走 Fast Path；否则先确认计划。
9. R2 的规格或评审能力可以使用已定义的安全降级并记录；R3/R4 的降级必须先获得用户明确批准。
10. required data/security/compliance/contract/delivery/observability gate 不得因工具缺失而省略。
11. R4 或协调发布必须定义 Feature Flag/灰度策略、可信回滚、监控基线、告警阈值、观察窗口和停止条件。
12. 多 Agent 仅在 DAG 拆出至少两个无共享状态、可独立测试的批次时启用；否则单 Agent 串行。
13. 完成前必须验证实现、规格、required gates 和最终 diff；不得把未执行的检查描述为通过。
14. 每次任务向 `.claude/workflow-metrics/tasks.jsonl` 追加符合 schema 的 Metrics，不记录秘密或个人数据。
15. 修改工作流模板自身时，必须运行 `python scripts/validate_workflow.py`，并交叉核对 design spec、Router、levels、gates、命令和用户指南。

## 3. Workflow Selection

统一入口：`.claude/commands/new-task.md`。

执行顺序：

1. `.claude/skills/workflow-router/SKILL.md`
2. `.claude/skills/workflow-router/v2/complexity-matrix.md`
3. `.claude/skills/workflow-router/v2/routing-rules.md`
4. `.claude/skills/workflow-router/v2/gates.md`
5. `.claude/skills/workflow-router/v2/toolcheck.md`
6. `.claude/skills/workflow-router/v2/levels.md`
7. `.claude/skills/workflow-router/gates/R{n}.md`

## 4. Project Engineering Profile

技术栈、构建、测试、迁移、风险领域和发布能力维护在 `.claude/project-profile.yaml`。首次接入真实项目时，必须用代码库证据替换空命令和 `unknown`，不能保留未经验证的假设。

## 5. Completion Requirements

每次完成必须报告：

- What changed and why?
- Initial tier、final tier、score 和 required gates 是什么？
- Delivery Profile 和 Capability Check 结果是什么？
- 执行了哪些测试、评审、迁移和发布验证？
- 哪些能力发生降级，谁批准了替代路径？
- 什么仍未验证，剩余风险和意外副作用是什么？
- Metrics 是否成功追加？

不得在没有实际证据的情况下声称“已完成”或“可发布”。
