# Routing Rules v2

## 红旗升档规则（任一命中，final_tier 取最高）

| 红旗条件 | 最低档 |
|---|---|
| Risk ≥ 3（库存扣减/支付/核心链路等） | R3 |
| Data = 3（数据迁移/核心表重构） | R3 |
| Infrastructure ≥ 3（日志/监控/基础设施集成） | R3 |
| Architecture = 3（模块边界重构） | R3 |
| 微服务拆分 / 核心架构重构 / 关键基础设施替换 | R4 |
| 多 Agent / 多隔离 Worktree 需要 | R4 |

## 最终档位公式

final_tier = max(level_from(weighted_score), level_from(rules), level_from(red_flags))

## 用户覆盖

- 用户可指定档位（如 `R2：xxx`），Router 可尊重。
- 但高风险任务不得因用户指定低档位而绕过安全要求。
- 若用户要求降档，必须说明被跳过的门控（Plan/Code Review 等），并请求确认。

## 升降级

- 升级（如 R2→R3）在实现中发现复杂度上升时自动发生，立即执行更高档流程。
- 降级不允许静默发生：必须说明原因、被移除的流程、风险变化，等待确认。
