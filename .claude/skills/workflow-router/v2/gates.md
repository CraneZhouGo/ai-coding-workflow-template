# Composable Gate Catalog v2.1

最终工作流由基础档位门控和以下语义/交付门控取并集。每个门控只执行一次。

| Gate | 触发条件 | 必须产物/验证 |
|---|---|---|
| `architecture` | 模块/服务边界、核心组件或技术策略变化 | 方案对比、ADR、依赖方向、失败模式和架构评审 |
| `data` | Schema、回填、迁移、一致性变化 | 数据影响说明、备份/回滚、dry-run、前后校验；R4 需切换与恢复演练 |
| `security` | 权限、认证、密钥、敏感数据、安全边界 | 威胁与滥用场景、最小权限、秘密扫描、专项测试 |
| `compliance` | 隐私、审计、监管或行业规则 | 法规/策略映射、审计证据、数据保留与访问记录 |
| `contract` | 公共 API、事件、跨服务协议 | 兼容性策略、消费者影响、契约测试、协调升级顺序 |
| `infrastructure` | 共享配置、日志、监控、安全平台、部署管道 | 影响范围、默认值、容量与故障模式、回滚验证 |
| `delivery` | 用户可见高风险变更、协调发布、迁移 | Feature Flag/灰度策略、回滚条件、发布审批、变更窗口 |
| `observability` | 关键链路、迁移、基础设施、分阶段发布 | 发布前基线、指标/日志/追踪、告警阈值、观察窗口和停止条件 |
| `isolation` | 2+ 独立批次或并发执行 | DAG、所有权、worktree/分支隔离、收敛点与集成顺序 |

## Gate 叠加规则

1. `data`、`security`、`compliance` 不得因基础档位较低而省略。
2. `delivery` 必须与 `observability` 配套用于 R4、不可逆迁移和协调发布。
3. `isolation` 由 Delivery Profile 触发，不改变 final tier。
4. 同一事实只产生一次产物；例如 API 迁移中的 rollout 同时满足 contract/delivery 时，共享一份发布顺序说明。
5. 不适用的门控必须写明 `not_applicable` 和依据，不能静默跳过。
