# AI Coding Workflow V2 设计文档

- 日期：2026-08-26
- 状态：草案（待用户评审）
- 版本：V2.0

## 1. 背景与问题

现有模板采用 L0/L1/L2/L3 四层强度模型，已在真实项目（单体、小团队）跑过多个需求。实践中暴露的结构性问题：

1. **评分矩阵有盲区**：日志基础设施集成这类"代码改动少、但影响所有服务/横切/需部署运维配合"的需求被误判为 L0（实际应至少 L2）。根因：7 个维度里没有"基础设施/横切影响"维度，且各维度等权求和，Risk/Data 权重不足。
2. **评分与规则合并不明确**：总分映射 Level 与 Mandatory Rules 冲突时如何取最终等级没有公式，结果不可复现。
3. **工具可用性不检查**：L2/L3 依赖 OpenSpec、Plannotator，但路由时不检查是否已安装/初始化，实际运行会卡死。
4. **双 Source of Truth**：Superpowers 的 brainstorming/writing-plans 与 OpenSpec 的 design.md/tasks.md 职责重叠，易双写、漂移。
5. **无数据自优化闭环**：没有记录每次任务的真实等级、升级率、返工率，Router 规则无法基于数据调优。

## 2. 目标与非目标

### 目标

1. **可靠可复现**：路由决策有确定公式，输出可复核。
2. **开箱即用**：内建工具可用性检查与初始化引导、需求输入模板。
3. **文档化可教**：概念简洁，团队只需记一条规则，无需记等级。
4. **数据自优化**：内建 Metrics 记录与报告，支持规则调参。
5. **兼容单体到微服务**：路由规则不预设项目形态。

### 非目标

- 不引入新的外部依赖（只用已有的 Claude Code + Superpowers + OpenSpec + Plannotator）。
- 不做 V3 的自动调参引擎（只做数据采集与人工辅助调参）。
- 不改变各工具的官方安装/配置方式。

## 3. 核心设计决策

| # | 决策 |
|---|---|
| D1 | 抛弃 L0-L3 等级模型，改为 **风险档 R1~R4 + 门控叠加** |
| D2 | 定义 **S0~S9 天花板**（完整工程流程），风险驱动向下裁剪 |
| D3 | **产物归 OpenSpec、过程归 Superpowers、评审归 Plannotator、执行归 Claude Code** |
| D4 | **确认点全标配，评审工具按风险分级** |
| D5 | 评分 **8 维加权 + 红旗规则**，最终档位 = `max(score_level, rules_level, red_flags)` |
| D6 | 路由输出 **Assessment 含各维度明细 + 命中规则**，可复核 |
| D7 | 路由阶段内建 **Tool Check**（OpenSpec/Plannotator 可用性 + 初始化引导） |
| D8 | 内建 **Metrics 数据层** 与 `/workflow-report` 命令 |

## 4. 风险档模型（D1）

不再有"选 L 几"，Router 输出 **风险档 R1~R4**，并给出该档 **必须开启的门控列表**。

| 档 | 名称 | 定位 | 示例 |
|---|---|---|---|
| R1 | Low | 明确小改动、低风险 | 文案、单点配置、明确小 Bug |
| R2 | Medium | 有业务规则/数据或架构影响的常规功能 | 新查询接口、常规 CRUD 增强 |
| R3 | High | 中高风险业务、基础设施/数据/架构显著影响 | 订单状态机、日志基础设施集成、Schema 变更 |
| R4 | Critical | 架构级、核心链路、多服务、数据迁移 | 微服务拆分、核心交易重构、大规模迁移 |

风险档不依赖项目形态：单体的 R3 与微服务的 R3 走同一套门控强度，规则自动适配。

## 5. 天花板 S0~S9（D2）

定义完整工程流程作为模板上限，低风险任务裁剪。

| 阶段 | 目的 | 产物 | 人工 Gate | 主要工具 |
|---|---|---|---|---|
| S0 需求治理 | 澄清 Goal/Scope/Non-goals/AC/Constraints | 需求说明 | 需求评审 | Superpowers(brainstorming) + Claude Code |
| S1 规格化 | 行为规格（Given/When/Then） | proposal.md + specs/ | 规格评审 | OpenSpec + Claude Code |
| S2 架构设计 | 方案对比、ADR、数据/契约设计 | design.md + ADR | 架构评审 | Superpowers(brainstorming) + OpenSpec |
| S3 计划 | 任务清单、依赖、测试策略 | tasks.md | **Plannotator Plan Review** | Superpowers(writing-plans) + OpenSpec |
| S4 实施 | TDD 编码 | 代码 + 测试 | — | Claude Code + Superpowers(TDD/executing) |
| S5 验证 | 多层测试 + 变更完整性 | 测试报告 + openspec status | 验证评审 | Claude Code + OpenSpec(verify) |
| S6 代码评审 | 逐变更评审 | 评审记录 | **Plannotator Code Review** | Plannotator + Superpowers(review) |
| S7 集成 | 合并/冲突/契约一致性 | 集成分支 + 回归 | 集成验证 | Claude Code + Superpowers(finishing) |
| S8 交付 | apply/archive、文档、发布 | 归档 + 变更日志 | 发布审批 | OpenSpec(apply/archive) |
| S9 度量 | 记录指标、分析误判 | Metrics 报告 | — | Claude Code + Plannotator(Compound) |

## 6. 工具职责边界（D3）

**原则：产物唯一，过程共享。** 用 Superpowers 方法论产出 OpenSpec 产物，不双写。

| 职责 | 归属 |
|---|---|
| 产物/生命周期/审计（State） | OpenSpec：`proposal.md`/`specs/`/`design.md`/`tasks.md` + `apply`/`archive`/`verify` |
| 过程方法论（Flow） | Superpowers：brainstorming / writing-plans / TDD / verification / review / finishing |
| 人工评审 Gate | Plannotator：Plan Review + Code Review + Compound Planning |
| 执行层 | Claude Code：读写代码、跑命令、测试、git |

### 重叠节点处理

| 重叠点 | 处理 |
|---|---|
| 需求理解 | brainstorming 探索 → 沉淀 `proposal.md` |
| 行为规格 | 只写 OpenSpec `specs/`；brainstorming 不产长期文件 |
| 设计 | 方案对比在对话内完成，只把选定方案写入 `design.md` |
| 任务/计划 | **用 writing-plans 方法论填充 `tasks.md`，不另建 plan 文件** |
| 结构校验 | `openspec status`/`verify`（Change 完整性）与 `verification-before-completion`（实现真实性）互补，均保留 |

### 两个必须显式覆盖的"写盘"动作

1. **brainstorming 默认写 `docs/superpowers/specs/`** → 覆盖：设计产物改写入 OpenSpec change 目录。
2. **writing-plans 默认生成独立 plan 文件** → 覆盖：任务直接写入 OpenSpec `tasks.md`。

Plannotator 只审 OpenSpec 一处（`tasks.md` 计划 + 代码 diff），不审 Superpowers 过程产物。

## 7. 评分矩阵 v2（D5）

8 维，每维 0~3 分。

| 维度 | 权重 | 说明 |
|---|---|---|
| Scope 影响范围 | ×1 | 文件/模块/服务数量 |
| Business 业务复杂度 | ×1 | 业务规则与状态 |
| Code Impact 代码影响 | ×1 | 调用链深度 |
| Architecture 架构影响 | ×2 | 模块边界/组件协作 |
| Data 数据影响 | ×2 | Schema/迁移/一致性 |
| **Infrastructure 基础设施/横切** | ×2 | **NEW：日志/监控/安全/配置/部署管道等平台性变更** |
| Risk 业务运行风险 | ×3 | 交易/库存/支付/权限等 |
| Collaboration 协作/并发 | ×1 | 单 Agent→多 Agent |

- 总分范围：0 ~ 39（8 维全部 3 分加权）
- 档位映射（**建议值，可按 Metrics 调整**）：0~5 → R1；6~12 → R2；13~24 → R3；25~39 → R4

### 红旗规则（任一命中直接升档，取最高）

| 红旗 | 最低档 |
|---|---|
| Risk ≥ 3（库存扣减/支付/核心链路等） | R3 |
| Data = 3（数据迁移/核心表重构） | R3 |
| Infrastructure ≥ 3（日志/监控/基础设施集成） | R3 |
| Architecture = 3（模块边界重构） | R3 |
| 微服务拆分 / 核心架构重构 / 关键基础设施替换 | R4 |
| 多 Agent / 多隔离 Worktree 需要 | R4 |

### 最终档位公式

```
final_tier = max(level_from(weighted_score), level_from(mandatory_rules), level_from(red_flags))
```

任一命中取最高，保证可复现。

## 8. 路由决策流程（D6、D7）

### Phase A — 需求理解（模板化）
明确 Goal / Scope / **Non-goals** / Acceptance Criteria / Constraints。R2 及以上若 AC/Constraints 缺失，必须追问补齐；R1 可省略。

### Phase B — 代码库探索
只探索与任务相关的范围（防过度扫描）。探索中若发现复杂度提升，立即 Re-evaluate 升级档位。

### Phase C — 评分
按 8 维加权打分，记录各维度明细。

### Phase D — 规则应用
应用 Mandatory Rules 与红旗规则。

### Phase E — 合并与输出
`final_tier = max(...)`，输出 **Assessment**（含各维度分数表、命中规则、理由），供人工复核。

### Phase F — Tool Check（开箱即用）
根据 final_tier 所需工具，检查可用性：
- R2+ 需 OpenSpec → 检查 `openspec/` 是否存在，缺失给初始化引导
- R2+ 需 Plannotator → 检查配置，缺失说明
- R4 需 git worktree / 多 Agent → 检查 git 状态与隔离方案

### Phase G — Re-evaluate
升级自动发生；降级必须说明原因 + 被移除流程 + 风险变化，并请求确认。

## 9. 评审模型（D4）

**确认点全标配**：任何任务必须有 ① 计划确认 ② diff 过目。
**工具强度分级**：

| 风险档 | Plan Review | Code Review |
|---|---|---|
| R1 | 终端内确认计划（必） | AI 自审 diff + 用户终端过目（必） |
| R2 | Plannotator Plan Review（必） | Plannotator Code Review（必） |
| R3/R4 | Plannotator Plan Review + 规格/架构确认 | Plannotator Code Review + 专项（安全/数据） |

实现要点：所有工作流强制第一步"先出计划、批准后执行"（Claude Code 原生 plan approval）；R2+ 接 Plannotator 增强。

## 10. 门控配置总表（风险档 × 阶段产物/Gate）

| 能力 | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| S0 需求 | 简化(Goal+Scope) | ✓ AC/约束 | ✓ Non-goals | ✓ 完整 |
| S1 规格 | — | proposal+specs | ✓ | ✓ 完整 delta |
| S2 设计 | — | 设计记录 | design.md | design.md+ADR |
| S3 计划 | 终端计划确认 | tasks.md | ✓ 详细 | ✓ WBS+依赖 |
| Plan Review | 终端确认 | Plannotator | Plannotator | Plannotator |
| S4 实施 | ✓ 最小改动 | TDD | TDD | TDD+多Agent |
| S5 验证 | 相关测试+diff | 单元+构建 | +集成+契约 | +迁移+专项 |
| S6 Code Review | 终端过目 | Plannotator | Plannotator | Plannotator+专项 |
| S7 集成 | — | — | — | ✓ |
| S8 交付 | — | — | apply/archive | apply/archive+发布审批 |
| S9 Metrics | ✓ | ✓ | ✓ | ✓ |

## 11. Metrics 数据层（D8）

每次任务完成，记录一条 record：

```
date, task_summary, initial_tier, final_tier, upgraded, changed_files,
changed_modules, review_reject, rework, duration
```

- 存储：`.claude/workflow-metrics/tasks.md`（追加）或 JSONL
- 新增 `/workflow-report` 命令：汇总升级率、各档分布、返工率，输出调参建议（提示哪些维度偏低/哪些红旗缺失）

## 12. 文件结构变更

**新增**
- `.claude/skills/workflow-router/v2/`：`complexity-matrix.md`（8 维加权）、`routing-rules.md`（红旗）、`levels.md`（R1-R4 门控配置）、`toolcheck.md`（工具检查引导）、`metrics.md`
- `.claude/commands/workflow-report.md`
- `.claude/workflow-metrics/tasks.md`（运行时生成）

**修改**
- `.claude/skills/workflow-router/SKILL.md`（路由流程 D6/D7，引用 v2 组件）
- `.claude/skills/workflow-router/workflows/*.md` → 改为 `gates/R1.md`~`R4.md`
- `.claude/commands/new-task.md`（Step 1 路由 + Tool Check）
- `CLAUDE.md`（Global Rules 更新：风险档、确认点全标配、Metrics）
- `AI-Coding-Workflow-Template-详细使用说明.md`（同步 V2）

**删除**
- 冗余 `claude/`（无点号）目录

## 13. 开放点（待用户确认）

1. 评分权重与档位阈值数字（§7 为建议值，用 Metrics 校准）
2. 门控配置总表的每项细节（§10）
3. 是否 `git init` 以提交本设计文档
4. Metrics 存储位置与格式
