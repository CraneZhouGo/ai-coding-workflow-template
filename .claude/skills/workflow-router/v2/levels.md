# Risk Levels v2.1 — 基础门控

本文件只定义档位基础门控。最终流程还必须叠加 `gates.md` 中由变更语义和 Delivery Profile 触发的门控。

| 能力 | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| S0 需求 | Goal + Scope | + AC/约束 | + Non-goals | 完整治理 |
| S1 规格 | — | 紧凑规格 | proposal + specs | 完整 delta |
| S2 设计 | — | 必要时简短设计记录 | design.md | design.md + ADR |
| S3 计划 | 简短计划 | tasks/实施计划 | 详细依赖与测试策略 | WBS + DAG + 发布策略 |
| Plan Review | 快速通道或终端确认 | Plannotator；可记录降级 | Plannotator；降级须批准 | Plannotator；降级须批准 |
| S4 实施 | 最小改动 | TDD | TDD | TDD；并行仅由 Delivery Profile 决定 |
| S5 验证 | 相关检查 + diff | 单元 + 构建 | + 集成/契约 | + 迁移/专项/全量回归 |
| S6 Code Review | AI 自审 + diff 过目 | Plannotator；可记录降级 | Plannotator + 专项 | Plannotator + 专项 |
| S7 集成 | — | — | 适用时 | 必须；并行分支在收敛点验证 |
| S8 交付 | — | 适用时 | apply/archive + required gates | apply/archive + delivery + observability |
| S9 Metrics | JSONL | JSONL | JSONL | JSONL |

## 产物模式

- OpenSpec 是首选规格 Source of Truth。
- R2 在 OpenSpec 不可用时，可以使用单一、可审计的紧凑变更记录，并把降级写入 Metrics。
- R3/R4 若 OpenSpec 或等价规格能力不可用，必须停止并获得用户对替代产物的明确批准。
- Superpowers 提供过程方法，不能另建与正式规格重复的长期产物。
