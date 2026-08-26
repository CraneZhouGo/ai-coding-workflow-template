# Complexity Matrix

## Scoring

每个维度按照 0~3 分评分。

### 1. Scope

| Score | Condition |
|---|---|
| 0 | 单文件或极小局部修改 |
| 1 | 2~5 个相关文件 |
| 2 | 多模块或明显跨边界 |
| 3 | 多服务/大范围影响 |

### 2. Business Complexity

| Score | Condition |
|---|---|
| 0 | 简单逻辑、CRUD、配置 |
| 1 | 普通业务规则 |
| 2 | 多状态、复杂规则、业务流程 |
| 3 | 核心交易/强一致/复杂领域规则 |

### 3. Code Impact

| Score | Condition |
|---|---|
| 0 | 单点修改 |
| 1 | 局部调用链 |
| 2 | 多模块调用链 |
| 3 | 大规模重构/多个服务 |

### 4. Architecture Impact

| Score | Condition |
|---|---|
| 0 | 无架构变化 |
| 1 | 局部设计变化 |
| 2 | 模块边界/组件协作变化 |
| 3 | 微服务拆分、核心架构、通信模式变化 |

### 5. Data Impact

| Score | Condition |
|---|---|
| 0 | 无数据结构变化 |
| 1 | 简单字段/索引/查询变化 |
| 2 | 新表、重要 Schema 变化 |
| 3 | 数据迁移、历史数据兼容、核心表重构 |

### 6. Risk

| Score | Condition |
|---|---|
| 0 | 低风险 |
| 1 | 一般风险 |
| 2 | 高风险 |
| 3 | 极高风险/核心链路 |

### 7. Collaboration

| Score | Condition |
|---|---|
| 0 | 单 Agent |
| 1 | 多任务但可串行 |
| 2 | 多 Agent / 多分支 / 多团队协作 |

## Base Level

| Total | Level |
|---:|---|
| 0~3 | L0 |
| 4~7 | L1 |
| 8~13 | L2 |
| 14~21 | L3 |

总分不是唯一依据，必须结合 Mandatory Rules。
