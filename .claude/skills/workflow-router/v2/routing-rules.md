# Routing Rules v2.1

## 最终档位

```text
final_tier = max(baseline_tier_from_score, minimum_tier_from_semantic_red_flags)
required_gates = baseline_gates(final_tier) union semantic_gates union delivery_gates
```

不再使用含义不明确的 `mandatory_rules`，也不把多 Agent 当作风险红旗。

## 语义红旗

红旗判断的是“本次变更改变了什么”，不是文件路径或业务名词是否出现。

| 条件 | 最低档 | 叠加门控 |
|---|---|---|
| 改变资金、库存、权限、交易状态或受监管业务语义 | R3 | `security`, `compliance`（适用时） |
| 新增或改变敏感数据采集、访问、传输、脱敏或保留策略 | R3 | `security`, `compliance` |
| 可逆 Schema 迁移、数据回填或跨服务一致性协议变化 | R3 | `data`, `contract` |
| 公共 API/事件契约存在不兼容变化 | R3 | `contract`, `delivery` |
| 改变共享基础设施默认行为、全局日志/监控/安全策略 | R3 | `infrastructure`, `delivery` |
| 不可逆迁移、大规模核心数据切换、没有可信回滚路径 | R4 | `data`, `delivery` |
| 微服务拆分、核心架构重构、关键基础设施替换 | R4 | `architecture`, `contract`, `delivery` |
| 需要停机、双写、分阶段切流或多服务强协调发布 | R4 | `delivery`, `observability` |

## 不应触发红旗的例子

- 支付页面文案调整，但不改变支付流程、金额或状态。
- 库存模块中的测试命名修改。
- 安全组件的注释、格式化或无运行时影响的重构。

这些任务仍按实际 Scope、Code Impact 和 Runtime Risk 评分。

## 可组合门控

读取 `gates.md`。红旗、代码库证据和 Delivery Profile 可以叠加多个门控，但不重复执行同一个产物或评审。

## 用户覆盖

- 用户可以要求更高档位或额外门控。
- 用户指定低档位不能绕过语义红旗对应的最低档位和安全门控。
- 降级必须说明评分变化、移除的门控和残余风险，并获得确认。

## Re-evaluation 检查点

至少在以下时点重新评估：

1. 首次代码库探索完成后。
2. 修改公共契约、Schema、权限或部署配置之前。
3. 实际 diff 超出原 Scope 时。
4. 进入发布或迁移步骤之前。
