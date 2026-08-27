# Risk Levels 门控配置

## 门控配置总表

| 能力 | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| S0 需求 | 简化(Goal+Scope) | ✓ AC/约束 | ✓ Non-goals | ✓ 完整 |
| S1 规格 | — | proposal+specs | ✓ | ✓ 完整 delta |
| S2 设计 | — | 设计记录 | design.md | design.md+ADR |
| S3 计划 | 终端计划确认 | tasks.md | ✓ 详细 | ✓ WBS+DAG拆分 |
| Plan Review | 终端确认 | Plannotator | Plannotator | Plannotator |
| S4 实施 | ✓ 最小改动 | TDD | TDD | TDD+多Agent |
| S5 验证 | 相关测试+diff | 单元+构建 | +集成+契约 | +迁移+专项 |
| S6 Code Review | 终端过目 | Plannotator | Plannotator | Plannotator+专项 |
| S7 集成 | — | — | — | ✓ |
| S8 交付 | — | — | apply/archive | apply/archive+发布审批 |
| S9 Metrics | ✓ | ✓ | ✓ | ✓ |

## 使用说明

- 档位越高，保留的天花板阶段越多。
- R1 不建 OpenSpec Change；R2 启用 OpenSpec 变更（proposal/specs/tasks，设计仅记录）；R3+ 必含 design.md。
- 每档的完整流程见 `gates/R{n}.md`。
