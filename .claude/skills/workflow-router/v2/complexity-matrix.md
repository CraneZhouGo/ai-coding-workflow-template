# Complexity Matrix v2

## 评分维度（每维 0~3 分，加权求和）

| 维度 | 权重 | 说明 |
|---|---|---|
| Scope 影响范围 | ×1 | 文件/模块/服务数量 |
| Business 业务复杂度 | ×1 | 业务规则与状态 |
| Code Impact 代码影响 | ×1 | 调用链深度 |
| Architecture 架构影响 | ×2 | 模块边界/组件协作 |
| Data 数据影响 | ×2 | Schema/迁移/一致性 |
| Infrastructure 基础设施/横切 | ×2 | 日志/监控/安全/配置/部署管道等平台性变更 |
| Risk 业务运行风险 | ×3 | 交易/库存/支付/权限等 |
| Collaboration 协作/并发 | ×1 | 单 Agent→多 Agent |

## 总分与档位映射

总分范围：0 ~ 39

| 总分 | 档位 |
|---:|---|
| 0~5 | R1 |
| 6~12 | R2 |
| 13~24 | R3 |
| 25~39 | R4 |

总分不是唯一依据：必须应用 `routing-rules.md` 的红旗升档规则。

## 评分示例

示例：集成日志基础设施（logs/ 平台性变更）

Scope=1, Business=0, CodeImpact=1, Architecture=2, Data=0, Infrastructure=3, Risk=2, Collaboration=0
加权 = 1×1 + 0×1 + 1×1 + 2×2 + 0×2 + 3×2 + 2×3 + 0×1 = 18 → R3
命中红旗 `Infrastructure≥3` → 至少 R3 → 最终 R3
