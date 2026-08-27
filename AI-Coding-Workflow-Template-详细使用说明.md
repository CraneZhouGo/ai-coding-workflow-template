---
date created: 2026-08-25 11:54:49
date modified: 2026-08-27
---

# AI Coding Workflow Template 详细使用说明

> 版本：V2.1
>
> 适用范围：Java / Spring Boot / Spring Cloud / DDD / 微服务及其他软件项目
>
> 核心工具：Claude Code + Superpowers + OpenSpec + Plannotator  
> 核心思想：风险档、可组合门控和交付策略分别判断

## 1. 解决什么问题

AI Coding 常见的两个极端是：复杂需求直接编码，或者简单修改被迫走完整工程流程。V2.1 使用一个统一入口解决这两个问题：

```text
Requirement
  → Project Profile + Repository Evidence
  → Anchored Risk Score
  → Semantic Red Flags
  → R1 / R2 / R3 / R4
  → Composable Gates
  → Delivery Profile
  → Capability Check
  → Implementation / Verification / Review / Delivery
  → JSONL Metrics
```

最重要的变化是：风险、门控和执行方式不再混成一个问题。

## 2. 三层模型

### 2.1 风险档

R1~R4 表示本次变更本身的风险，不是生命周期，也不表示 Agent 数量。

| 档位 | 定位 | 示例 |
|---|---|---|
| R1 | 局部、明确、低运行时风险 | 文案、单点配置、明确小 Bug |
| R2 | 常规功能、有限业务规则 | 查询接口、CRUD、小型 Feature |
| R3 | 显著业务、数据、架构或基础设施影响 | 状态机、兼容迁移、共享日志默认值 |
| R4 | 核心结构、不可逆切换或强协调交付 | 微服务拆分、核心迁移、关键平台替换 |

### 2.2 可组合门控

档位给出基础流程，变更语义继续叠加门控：

```text
required_gates = baseline_gates(final_tier)
               union semantic_gates
               union delivery_gates
```

门控包括 architecture、data、security、compliance、contract、infrastructure、delivery、observability、isolation。

### 2.3 Delivery Profile

以下内容独立于风险评分：

```text
agents:      1 | 2+
worktrees:   none | optional | required
rollout:     none | standard | coordinated
ownership:   single | multi-team
```

多 Agent 只是一种执行策略。任务需要并行不会自动变成 R4；R4 任务也不一定适合并行。

## 3. 风险评分：7 个锚定维度

| 维度 | 权重 | 0 分 | 1 分 | 2 分 | 3 分 |
|---|---:|---|---|---|---|
| Scope | ×1 | 单点/单文件 | 同模块少量文件 | 跨模块/共享组件 | 跨服务/全局消费者 |
| Business | ×1 | 无业务语义 | 单一规则 | 多规则/有限状态变化 | 复杂状态机/监管规则 |
| Code Impact | ×1 | 叶子逻辑 | 单条调用链 | 多层或公共 API | 广泛/异步消费者 |
| Architecture | ×2 | 边界不变 | 调整既有协作 | 新组件/契约 | 边界或核心架构重构 |
| Data | ×2 | 无持久化变化 | 兼容字段/查询 | 可逆 Schema/回填 | 不可逆/大规模核心迁移 |
| Infrastructure | ×2 | 无影响 | 服务本地配置 | 共享或可选横切能力 | 全局默认/关键平台变化 |
| Runtime Risk | ×3 | 无运行时语义 | 边界清晰易回滚 | 关键用户流程可能降级 | 资金/库存/权限/敏感数据/难回滚 |

总分 0~36：

```text
0~5   → R1
6~11  → R2
12~22 → R3
23~36 → R4
```

每一分都必须有代码库或需求证据。同一事实不能重复放大。例如跨服务主要提高 Scope；只有服务边界本身变化时才同时提高 Architecture。

## 4. 语义红旗

```text
final_tier = max(baseline_tier_from_score,
                 minimum_tier_from_semantic_red_flags)
```

### 至少 R3

- 改变资金、库存、权限、交易状态或受监管业务语义。
- 改变敏感数据采集、访问、传输、脱敏或保留。
- 可逆 Schema 迁移、回填或跨服务一致性协议变化。
- 公共 API/事件契约不兼容。
- 改变共享基础设施默认行为或全局安全策略。

### 至少 R4

- 不可逆迁移、大规模核心数据切换或没有可信回滚路径。
- 微服务拆分、核心架构重构、关键基础设施替换。
- 需要停机、双写、分阶段切流或多服务强协调发布。

红旗判断变更语义，不判断目录名称。支付页面文案修改可以是 R1；改变支付状态迁移至少是 R3。

## 5. 可组合门控说明

| Gate | 触发场景 | 核心产物 |
|---|---|---|
| architecture | 模块/服务边界、核心组件、技术策略 | 方案对比、ADR、依赖方向、失败模式、架构评审 |
| data | Schema、迁移、回填、一致性 | dry-run、备份/回滚、前后校验 |
| security | 权限、认证、密钥、敏感数据 | 威胁场景、最小权限、秘密扫描、专项测试 |
| compliance | 隐私、审计、监管、行业规则 | 策略映射、审计证据、保留和访问记录 |
| contract | API、事件、跨服务协议 | 兼容策略、消费者清单、契约测试、升级顺序 |
| infrastructure | 日志、监控、安全平台、部署管道 | 默认值、容量/故障模式、回滚验证 |
| delivery | 用户可见高风险或协调发布 | Feature Flag、灰度、回滚条件、审批 |
| observability | 关键链路、迁移、分阶段发布 | 基线、指标/日志/追踪、告警、观察窗口 |
| isolation | 2+ 独立执行批次 | DAG、所有权、worktree、收敛点 |

同一产物只写一次。一个 API 迁移同时触发 contract 和 delivery 时，可以共享一份升级/发布顺序说明。

## 6. R1~R4 的基础流程

### R1

```text
Goal + Scope → 定位 → 最小改动 → 相关验证 → diff 自审/过目 → Metrics
```

满足严格条件时可走 Fast Path，详见第 11 节。

### R2

```text
AC/Constraints → 紧凑规格 → 实施计划 → Plan Review
→ TDD → 单元/构建 → Code Review → Metrics
```

OpenSpec 和 Plannotator 是首选；能力不可用时可以使用已定义的 R2 降级路径，并记录到 Metrics。

### R3

```text
完整需求 → proposal/specs/design → required gates → 详细计划
→ 规格/架构/Plan Review → TDD → 集成/契约/专项验证
→ Code Review → apply/archive/交付 → Metrics
```

规格或人工评审能力降级必须先获得用户批准。

### R4

执行完整 S0~S9，强制 delivery + observability。并行仅在 Delivery Profile 和 DAG 证明适合时启用。

## 7. 工具职责

| 职责 | 首选工具 |
|---|---|
| 正式规格、生命周期、审计 | OpenSpec |
| brainstorming、计划方法、TDD、验证方法 | Superpowers |
| Plan/Code Human Review | Plannotator |
| 代码、命令、测试、Git、交付执行 | Claude Code |

原则：产物唯一、过程共享。Superpowers 的设计和计划方法写入 OpenSpec 或批准的等价正式产物，不再生成第二份长期文档。

工具不是门控本身。工具缺失时，Capability Check 决定是否有安全替代路径，而不是直接删除门控。

## 8. 项目目录

```text
project/
├── CLAUDE.md
├── distribution-manifest.json
├── .claude/
│   ├── project-profile.yaml
│   ├── commands/
│   │   ├── new-task.md
│   │   └── workflow-report.md
│   └── skills/workflow-router/
│       ├── SKILL.md
│       ├── gates/
│       │   ├── R1.md
│       │   ├── R2.md
│       │   ├── R3.md
│       │   └── R4.md
│       └── v2/
│           ├── complexity-matrix.md
│           ├── routing-rules.md
│           ├── gates.md
│           ├── levels.md
│           ├── toolcheck.md
│           ├── metrics.md
│           ├── metrics-schema.json
│           └── calibration-cases.json
├── scripts/
│   ├── validate_workflow.py
│   ├── record_workflow_metric.py
│   ├── workflow_report.py
│   └── build_distribution.py
└── .github/workflows/validate-workflow-template.yml
```

`.claude/workflow-metrics/tasks.jsonl` 是运行时数据，默认不进入版本库。

## 9. 第一次安装

1. 将分发包内容复制到项目根目录。
2. 确认 Claude Code 可以读取 `CLAUDE.md` 和 commands/skills。
3. 按当前官方方式安装 Superpowers。
4. 初始化 OpenSpec，并验证命令、版本和 status/verify。
5. 配置 Plannotator，并实际验证 Plan/Code Review 入口。
6. 填写 `.claude/project-profile.yaml`。
7. 运行 `python scripts/validate_workflow.py`。

不要只检查目录存在；应实际运行能力探测。

## 10. 项目画像

项目画像维护以下事实：

- 构建、单元、集成、契约、静态检查命令。
- 迁移 dry-run 和 rollback 命令。
- Fast Path、工具要求和 Metrics 配置。
- 高风险业务语义和合规领域。
- Feature Flag、发布、回滚和可观测性能力。

首次进入已有项目时，应通过代码库、CI 和部署配置收集证据，替换所有 `unknown` 和空命令。画像不完整时，Router 必须把相应能力标记为 degraded 或 missing。

## 11. R1 Fast Path

Fast Path 需要项目画像允许，并同时满足：

1. Score≤2，单文件或等价局部修改。
2. 不改变业务语义、公共契约、Schema、权限或基础设施默认值。
3. 有直接快速验证，且容易回滚。
4. 没有冲突的用户改动。

Agent 先宣布 Goal、Scope、计划和验证方式，然后可以直接执行，不等待第二次计划确认。完成后仍需 diff 过目和 Metrics。

以下情况不能走 Fast Path：

- 修改金额计算或支付/库存状态。
- 修改权限判断。
- 修改 Schema 或公共 API。
- 发现影响范围超出最初单点。
- 无法运行任何可信验证。

## 12. Capability Check

| 状态 | 含义 |
|---|---|
| available | 首选能力可调用且健康检查通过 |
| degraded | 有安全替代路径，必须记录替代方案和批准 |
| missing | required gate 无可信执行路径，任务暂停 |

R2 示例：Plannotator 不可用，可以降级为终端人工计划确认和 diff 过目；Metrics 记录 degradation。

R3/R4 示例：OpenSpec 或 Plan Review 不可用，不能自行降级，必须先让用户批准等价产物或评审方式。

Build/Test/Migration/Delivery 能力缺失时，最终报告必须明确“未验证”，不能称为通过。

## 13. 四个实际示例

### 支付页面文案

```text
Scope=0, Business=0, Code=0, Architecture=0,
Data=0, Infrastructure=0, RuntimeRisk=0
score=0 → R1
```

没有改变支付语义，因此不触发红旗；满足条件时可走 Fast Path。

### 有边界的查询接口

```text
Scope=1, Business=1, Code=1, Architecture=1,
Data=0, Infrastructure=0, RuntimeRisk=1
score=1+1+1+2+0+0+3=8 → R2
```

使用紧凑规格、计划、TDD 和 Review。

### 修改共享日志默认值

```text
Scope=1, Business=0, Code=1, Architecture=2,
Data=0, Infrastructure=3, RuntimeRisk=2
score=1+0+1+4+0+6+6=18 → R3
```

同时触发共享基础设施语义红旗，叠加 infrastructure + delivery + observability。

### 不可逆核心数据迁移

示例评分可能只有 22（R3 区间），但命中“不可逆/无可信回滚的数据切换”红旗，因此 final tier 为 R4，并叠加 data + delivery + observability。

## 14. Re-evaluation

至少四次检查：

1. 初次探索完成后。
2. 修改公共契约、Schema、权限或部署配置之前。
3. diff 超出原 Scope 时。
4. 进入迁移或发布前。

升级自动发生。降级必须说明新证据、评分变化、移除门控和残余风险，获得确认后才能执行。

## 15. 多 Agent 与 Worktree

启用多 Agent 前先建立 DAG：

1. 节点是任务，边是依赖。
2. 做拓扑分层并识别关键路径。
3. 标记任务所有权、并行扇出和收敛点。
4. 至少拆出两个无共享状态、可独立测试的批次。
5. 每批次使用隔离 worktree，并在收敛点执行集成验证。

无法满足第 4 条时使用单 Agent 串行。这不会改变 final tier。

## 16. 生产发布门控

R4、不可逆迁移和协调发布必须同时具备：

- Feature Flag、灰度/金丝雀或等价隔离。
- 明确的回滚条件、负责人和命令。
- 发布前指标基线。
- 发布后指标、日志、追踪和告警。
- 观察窗口和停止条件。
- 数据/契约向前向后兼容策略。

缺少可信回滚或发布后观测能力时，不得声称“可发布”。

## 17. Workflow Metrics

每次任务向以下文件追加一条 JSON：

```text
.claude/workflow-metrics/tasks.jsonl
```

记录内容包括：

- initial/final tier 和 score
- 7 个维度、语义红旗、required gates
- Delivery Profile 和 Capability degradation
- 变更范围、测试、评审严重度、返工
- Agent 执行时间、人工等待时间
- escaped defect（未知为 null）

Metrics 不得包含秘密、个人数据、完整代码或敏感需求正文。

先生成单条记录，再用脚本校验并追加：

```text
python scripts/record_workflow_metric.py --record <record.json>
```

运行：

```text
/workflow-report
```

或：

```text
python scripts/workflow_report.py
```

报告输出 Initial→Final 档位矩阵、升级信号、各档耗时/返工、能力降级和 escaped defect。样本少于默认 20 条时，只展示统计，不建议调权重。

## 18. 自动验证与分发

```text
python scripts/validate_workflow.py --repository
python scripts/build_distribution.py
python scripts/validate_workflow.py --repository --archive ai-coding-workflow-template.zip
```

验证内容：

- 必需文件和项目画像字段。
- 校准案例的分数及 final tier。
- V2.1 关键术语和旧实现残留。
- 分发 manifest 与 ZIP 内容一致。

GitHub Actions 会执行同样检查。ZIP 使用固定时间戳和排序生成，使相同源码得到相同分发内容。

## 19. 团队使用方式

团队成员只需记两个入口：

```text
/new-task <需求>
/workflow-report
```

Router 负责评分、门控、能力探测和交付策略。人仍负责批准高风险降级、架构/规格、发布和无法自动证明的业务判断。

## 20. 版本演进

### V1（历史）

L0~L3、7 维等权、强制升级规则。主要问题是基础设施盲区、公式冲突、工具不检查和缺少 Metrics。

### V2.0（历史）

引入 R1~R4、8 维最高 39 分、红旗、Tool Check、OpenSpec/Plannotator 边界和 Markdown Metrics。主要问题是评分锚点不足、协作循环、固定门控、能力检查偏弱和数据难分析。

### V2.1（当前）

- 7 个锚定风险维度，最高 36 分。
- 风险、可组合门控和 Delivery Profile 解耦。
- 语义红旗取代领域关键词。
- Capability Check 和受控降级。
- R1 Fast Path。
- 项目画像、JSONL Metrics、最小样本纪律。
- 生产发布和可观测性门控。
- 校准案例、验证脚本、CI 和确定性分发。

## 21. 最重要的原则

1. 判断本次变更改变什么，而不是它位于什么目录。
2. 每个评分必须有证据，每个高风险门控必须有产物。
3. 风险档不决定 Agent 数量，Agent 数量也不决定风险档。
4. 工具缺失只能触发受控降级或阻塞，不能让门控消失。
5. 简单任务在严格条件下快速完成，高风险任务保留完整审计和交付保障。
6. 没有测试、回滚或可观测证据时，不能声称完成或可发布。
7. 用 JSONL 数据和足够样本校准规则，不凭少数印象改阈值。

最终闭环：

> **Requirement → Evidence → Risk Tier → Required Gates → Delivery Profile → Capability Check → Implementation → Verification → Review → Delivery → Metrics**
