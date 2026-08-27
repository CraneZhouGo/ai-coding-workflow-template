# AI Coding Workflow V2.1 设计文档

- 初始日期：2026-08-26
- V2.1 日期：2026-08-27
- 状态：已实施
- 版本：V2.1

## 1. 背景

V2.0 将旧 L0~L3 模型升级为 R1~R4、8 维加权、红旗规则、Tool Check 和 Metrics，解决了基础设施变更被低估、工具职责重叠和路由公式不确定的问题。

V2.0 实施后仍有以下结构性问题：

1. 维度只有名称，没有 0~3 分锚点，Agent 之间难以复现。
2. Scope/Code/Architecture/Infrastructure 存在重复计分空间。
3. Collaboration 参与风险分，且“多 Agent → R4 → 考虑多 Agent”形成循环。
4. 档位绑定固定流程，数据、安全、契约、发布等横向门控不够灵活。
5. 红旗偏领域名词，可能把支付文案与支付状态语义同等处理。
6. Tool Check 偏目录检查，缺少版本、命令、验证能力和降级策略。
7. Markdown Metrics 字段过少，无法可靠分析误判原因。
8. 规则没有可执行一致性测试，压缩包可能与源码漂移。
9. R4 发布阶段缺少 Feature Flag、灰度、可观测性和停止条件的完整定义。

## 2. V2.1 目标

1. **稳定评分**：每维具备 0~3 锚点和机器可验证的校准案例。
2. **风险与执行解耦**：风险档、required gates、Delivery Profile 分别判断。
3. **语义优先**：判断本次变更改变什么，不按模块名称机械升档。
4. **能力导向**：检查可执行能力，允许受控降级并完整审计。
5. **真实闭环**：JSONL Metrics、样本约束报告、自动验证和确定性分发包。
6. **生产可交付**：高风险发布具备回滚、灰度、观测和停止条件。

## 3. 核心设计决策

| # | 决策 |
|---|---|
| D1 | 保留 R1~R4，风险档仍表示变更本身的风险 |
| D2 | 完整生命周期仍为 S0~S9 |
| D3 | 产物归 OpenSpec、过程归 Superpowers、评审归 Plannotator、执行归 Claude Code |
| D4 | 评分改为 7 个锚定风险维度；Collaboration 移入 Delivery Profile |
| D5 | 最终流程 = baseline gates ∪ semantic gates ∪ delivery gates |
| D6 | 红旗基于变更语义，不基于目录或业务关键词 |
| D7 | Tool Check 升级为 Capability Check：available/degraded/missing |
| D8 | R1 增加严格约束的预授权 Fast Path |
| D9 | Metrics 改为 schema 化 JSONL，并设置最小调参样本数 |
| D10 | 项目事实进入 `.claude/project-profile.yaml` |
| D11 | R4/协调发布强制 delivery + observability gates |
| D12 | 使用校准案例、验证脚本、CI 和 manifest 防止规则/分发漂移 |

## 4. 风险评分模型

### 4.1 维度与权重

| 维度 | 权重 | 判断对象 |
|---|---:|---|
| Scope | ×1 | 文件、模块、服务和消费者范围 |
| Business | ×1 | 业务规则和状态复杂度 |
| Code Impact | ×1 | 调用链、公共 API 和异步消费者 |
| Architecture | ×2 | 组件/模块/服务边界变化 |
| Data | ×2 | Schema、回填、迁移和一致性 |
| Infrastructure | ×2 | 配置、平台、部署和横切默认行为 |
| Runtime Risk | ×3 | 资金、库存、权限、敏感数据、安全和回滚难度 |

每维 0~3，完整锚点以 `v2/complexity-matrix.md` 为实现 Source of Truth。总分 0~36：

| 分数 | baseline tier |
|---:|---|
| 0~5 | R1 |
| 6~11 | R2 |
| 12~22 | R3 |
| 23~36 | R4 |

评分纪律：同一事实不得重复放大；每一分都必须有需求或代码库证据。

### 4.2 语义红旗

```text
final_tier = max(baseline_tier_from_score, minimum_tier_from_semantic_red_flags)
```

R3 语义红旗包括：改变资金/库存/权限/交易状态，改变敏感数据处理，可逆迁移或一致性协议，不兼容公共契约，共享基础设施默认行为。

R4 语义红旗包括：不可逆或无可信回滚的数据切换，微服务拆分/核心架构重构/关键基础设施替换，停机/双写/分阶段切流/多服务强协调发布。

“支付”“库存”“安全”等目录或名词本身不触发红旗；必须改变相关运行时语义。

### 4.3 Delivery Profile

Delivery Profile 不参与风险分：

- agents: 1 / 2+
- worktrees: none / optional / required
- rollout: none / standard / coordinated
- ownership: single / multi-team

多 Agent 只在 DAG 中存在至少两个无共享状态、可独立测试的批次时启用。它增加 isolation/integration gate，不反向决定 final tier。

## 5. 可组合门控

```text
required_gates = baseline_gates(final_tier)
               union semantic_gates
               union delivery_gates
```

| Gate | 核心要求 |
|---|---|
| architecture | 方案对比、ADR、依赖方向、失败模式、架构评审 |
| data | 影响说明、备份/回滚、dry-run、前后校验 |
| security | 威胁场景、最小权限、秘密扫描、专项测试 |
| compliance | 策略映射、审计证据、保留和访问记录 |
| contract | 兼容策略、消费者影响、契约测试、升级顺序 |
| infrastructure | 默认值、容量/故障模式、回滚验证 |
| delivery | Feature Flag/灰度、回滚条件、审批、窗口 |
| observability | 基线、指标/日志/追踪、告警、观察窗口、停止条件 |
| isolation | DAG、所有权、worktree、收敛点和集成顺序 |

门控按集合合并，同一产物不重复写。不适用的高风险门控必须记录依据。

## 6. S0~S9 基础流程

| 阶段 | 目的 | 主要产物 |
|---|---|---|
| S0 | 需求治理 | Goal/Scope/Non-goals/AC/Constraints |
| S1 | 规格 | proposal/specs 或批准的等价产物 |
| S2 | 设计 | design/ADR/失败模式 |
| S3 | 计划 | tasks/WBS/DAG/测试与发布策略 |
| S4 | 实施 | TDD 代码与测试 |
| S5 | 验证 | 多层测试和 required gates 证据 |
| S6 | 评审 | Plan/Code/专项评审记录 |
| S7 | 集成 | 收敛、冲突处理、回归 |
| S8 | 交付 | apply/archive、发布和观测 |
| S9 | 度量 | JSONL Metrics |

基础档位裁剪见 `v2/levels.md`；具体执行见 `gates/R1.md`~`R4.md`。

## 7. R1 Fast Path

Fast Path 仅用于 score≤2、局部、无业务语义/契约/Schema/权限/基础设施默认值变化、可快速验证和回滚、且没有冲突用户改动的任务。

Fast Path 可以在宣布计划后直接执行，但仍必须完成测试、AI 自审、diff 过目和 Metrics。任一条件失效立即退回 Regular Path 并重新评估。

## 8. Capability Check

能力状态：

- available：首选能力健康可用。
- degraded：存在安全替代路径，并记录批准情况。
- missing：required gate 没有可信执行路径，任务暂停。

R2 可将 OpenSpec 降级为单一紧凑变更记录，将 Plannotator 降级为终端人工确认；R3/R4 对这两类降级必须获得明确批准。Build/Test/Migration/Delivery 能力缺失时不能声称相应验证完成。

## 9. 生产交付要求

R4、不可逆迁移和协调发布必须同时开启 delivery + observability：

1. Feature Flag、灰度/金丝雀或等价风险隔离。
2. 明确回滚触发条件、负责人和执行命令。
3. 发布前指标基线和发布后观察窗口。
4. 指标、日志、追踪和告警阈值。
5. 自动/人工停止条件和恢复验证。

## 10. Metrics

存储：`.claude/workflow-metrics/tasks.jsonl`，每行符合 `.claude/skills/workflow-router/v2/metrics-schema.json`。

除档位、文件数和返工外，必须记录维度、红旗、required gates、Delivery Profile、能力降级、测试、评审严重度、执行/等待时间和 escaped defect。

样本少于项目画像的 `minimum_samples_for_tuning`（默认 20）时，报告只展示统计，不建议调权重或阈值。

## 11. 项目画像

`.claude/project-profile.yaml` 保存构建、测试、迁移命令，高风险语义、合规领域、Fast Path 策略、Metrics 路径和发布能力。首次接入真实项目必须用代码库证据填充，避免每次任务重新猜测。

## 12. 自动验证与分发

- `.claude/skills/workflow-router/v2/calibration-cases.json`：固定基准任务及预期分数/档位。
- `scripts/validate_workflow.py`：验证必需文件、评分计算、V2.1 术语、项目画像和分发内容。
- `scripts/record_workflow_metric.py`：依据 schema 校验并安全追加 JSONL。
- `scripts/workflow_report.py`：计算档位矩阵、返工、能力降级和缺陷率。
- `scripts/build_distribution.py` + `distribution-manifest.json`：生成确定性 ZIP。
- `.github/workflows/validate-workflow-template.yml`：CI 执行验证、报告 smoke test 和分发校验。

## 13. 工具职责与降级

OpenSpec 仍是首选正式规格 Source of Truth；Superpowers 只提供方法；Plannotator 是首选人工 Gate；Claude Code 负责执行。降级替代不能创建第二份长期规格，也不能把自动自审伪装成人工批准。

## 14. V2.0 → V2.1 迁移

| V2.0 | V2.1 |
|---|---|
| 8 维、最高 39 | 7 风险维度、最高 36；协作独立建模 |
| 档位绑定固定门控 | 基础档位 + 可组合门控 |
| 领域/数值红旗 | 变更语义红旗 |
| 目录存在性 Tool Check | 能力探测和可审计降级 |
| Markdown Metrics | schema 化 JSONL |
| 所有 R1 先批准计划 | 严格条件下的预授权 Fast Path |
| R4 才笼统发布审批 | delivery + observability 明确产物 |
| 手工文档终验 | 校准案例 + 脚本 + CI + manifest |
