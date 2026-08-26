# AI Coding Workflow V2 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 L0/L1/L2/L3 四层模型重构为"风险档 R1~R4 + 门控叠加"模型，修复评分盲区、建立可复现路由闭环、工具可用性检查与 Metrics 数据层。

**Architecture:** 保留已验证的"复杂度驱动"思想，但把"选一个强度等级"改为"评估风险档 + 按档裁剪 S0~S9 天花板门控"。工具职责分离：产物归 OpenSpec、过程归 Superpowers、评审归 Plannotator、执行归 Claude Code。最终档位由确定公式 `final_tier = max(score, rules, red_flags)` 得出，输出含明细可复核。

**Tech Stack:** Claude Code（`.claude/skills/` + `.claude/commands/`）、Markdown 文档、无运行时代码。

**Spec:** `docs/superpowers/specs/2026-08-26-ai-coding-workflow-v2-design.md`。本计划从 spec 论证，执行时两者同读。

## Global Constraints

1. 所有文件正文用中文（除代码块/命令）。
2. 术语统一：风险档 `R1`~`R4`；最终档位变量名 `final_tier`。除"背景描述旧模型"外，不得再出现 `L0/L1/L2/L3`。
3. 所有跨文件引用路径必须真实存在；删除文件前必须确认无残留引用。
4. 评分权重、档位阈值、红旗清单、门控配置表的**数值与 spec §7/§8/§10 完全一致**。
5. 每个文件单一职责；`SKILL.md` 只做路由编排，不内嵌大表，细则放 `v2/` 与 `gates/`。
6. 每次任务完成后 `git commit`（Task 1 先 `git init`）。
7. `.claude/workflow-metrics/` 为运行时数据，必须被 `.gitignore` 排除，不进入版本库。

## File Structure

### 创建
| 文件 | 职责 |
|---|---|
| `.claude/skills/workflow-router/v2/complexity-matrix.md` | 8 维加权评分 + 档位映射 + 示例 |
| `.claude/skills/workflow-router/v2/routing-rules.md` | 红旗升档规则、用户覆盖、升降级 |
| `.claude/skills/workflow-router/v2/levels.md` | R1~R4 门控配置总表（spec §10） |
| `.claude/skills/workflow-router/v2/toolcheck.md` | 工具可用性检查 + 初始化引导 |
| `.claude/skills/workflow-router/v2/metrics.md` | Metrics record 定义与记录时机 |
| `.claude/skills/workflow-router/gates/R1.md` | 低风险流程 |
| `.claude/skills/workflow-router/gates/R2.md` | 中风险流程 |
| `.claude/skills/workflow-router/gates/R3.md` | 高风险流程 |
| `.claude/skills/workflow-router/gates/R4.md` | 极高风险流程 |
| `.claude/commands/workflow-report.md` | `/workflow-report` 汇总命令 |
| `.gitignore` | 排除运行时数据 |

### 修改
| 文件 | 改动 |
|---|---|
| `.claude/skills/workflow-router/SKILL.md` | 路由流程 Phase A~G + Assessment 模板 + 引用 v2/gates |
| `.claude/commands/new-task.md` | Step 1 路由 + Tool Check，Step 2 加载 gates/Rn |
| `CLAUDE.md` | §3 选择路径、Global Rules 风险档化、Metrics、确认点全标配 |
| `AI-Coding-Workflow-Template-详细使用说明.md` | 同步 V2 模型与工具映射 |

### 删除
| 文件 | 原因 |
|---|---|
| `.claude/skills/workflow-router/complexity-matrix.md` | 被 v2/ 取代 |
| `.claude/skills/workflow-router/routing-rules.md` | 被 v2/ 取代 |
| `.claude/skills/workflow-router/workflows/`（L0~L3） | 被 gates/ 取代 |
| `claude/`（无点号目录） | 冗余副本，Claude Code 不识别 |

---

## Task 1: 初始化 git 仓库

**Files:**
- Create: `.gitignore`
- （git init 于项目根目录）

**Interfaces:**
- Produces: git 仓库基线，后续所有任务依赖它做 commit

- [ ] **Step 1: 确认当前 git 状态**

Run: `git rev-parse --is-inside-work-tree`
Expected: 输出 `true`（已初始化，跳到 Step 4）或报错（未初始化，继续）。

- [ ] **Step 2: 创建 .gitignore**

内容：

```gitignore
# 运行时数据（不进版本库）
.claude/workflow-metrics/
```

- [ ] **Step 3: 初始化 git**

```bash
git init
```

- [ ] **Step 4: 初始提交**

```bash
git add .
git commit -m "chore: init repo with V1 workflow template and V2 spec"
```

- [ ] **Step 5: 验证**

Run: `git log --oneline -1`
Expected: 显示该初始 commit；工作区干净。

---

## Task 2: 创建 v2/complexity-matrix.md

**Files:**
- Create: `.claude/skills/workflow-router/v2/complexity-matrix.md`

**Interfaces:**
- Consumes: spec §7 评分矩阵
- Produces: 被 `SKILL.md` Phase C 引用；被 `routing-rules.md` 引用为"分数非唯一依据"

- [ ] **Step 1: 创建文件，写入评分矩阵**

文件必须包含以下内容（数值与 spec §7 完全一致）：

```markdown
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
```

- [ ] **Step 2: 验证**

Run: Glob `.claude/skills/workflow-router/v2/complexity-matrix.md`
Expected: 存在；用 Grep 验证含 `Infrastructure 基础设施/横切` 与 `| 25~39 | R4 |`。

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/workflow-router/v2/complexity-matrix.md
git commit -m "feat: add v2 complexity matrix with weighted scoring"
```

---

## Task 3: 创建 v2/routing-rules.md

**Files:**
- Create: `.claude/skills/workflow-router/v2/routing-rules.md`

**Interfaces:**
- Consumes: spec §7 红旗清单
- Produces: 被 `SKILL.md` Phase D 引用；被 `levels.md` 引用

- [ ] **Step 1: 创建文件，写入红旗与覆盖规则**

文件必须包含（与 spec §7 红旗表一致）：

```markdown
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
```

- [ ] **Step 2: 验证**

Run: Grep pattern `Infrastructure ≥ 3` in `.claude/skills/workflow-router/v2/routing-rules.md`
Expected: 命中。

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/workflow-router/v2/routing-rules.md
git commit -m "feat: add v2 routing rules with red flags"
```

---

## Task 4: 创建 v2/levels.md

**Files:**
- Create: `.claude/skills/workflow-router/v2/levels.md`

**Interfaces:**
- Consumes: spec §10 门控配置总表
- Produces: 被 `SKILL.md` Phase E 引用；被 `gates/R1~R4.md` 引用为配置依据

- [ ] **Step 1: 创建文件，写入门控配置总表**

完整复制 spec §10 表格：

```markdown
# Risk Levels 门控配置

## 门控配置总表

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

## 使用说明

- 档位越高，保留的天花板阶段越多。
- R1 不建 OpenSpec Change；R2+ 启用 OpenSpec 四件套（proposal/specs/design/tasks）。
- 每档的完整流程见 `gates/R{n}.md`。
```

- [ ] **Step 2: 验证**

Run: Grep pattern `TDD+多Agent` in `.claude/skills/workflow-router/v2/levels.md`
Expected: 命中。

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/workflow-router/v2/levels.md
git commit -m "feat: add v2 risk levels gate configuration"
```

---

## Task 5: 创建 v2/toolcheck.md

**Files:**
- Create: `.claude/skills/workflow-router/v2/toolcheck.md`

**Interfaces:**
- Produces: 被 `SKILL.md` Phase F 引用；被 `new-task.md` 引用

- [ ] **Step 1: 创建文件，写入工具检查流程**

```markdown
# Tool Check（工具可用性检查）

按 final_tier 检查所需工具，缺失则给初始化引导。检查在路由输出后、执行流程前进行。

| 档位 | 必需工具 | 检查方式 | 缺失引导 |
|---|---|---|---|
| R1 | Claude Code | — | — |
| R2+ | OpenSpec | 存在 `openspec/` 目录 | 提示：运行 `openspec init` 或按 OpenSpec 官方文档初始化 |
| R2+ | Plannotator | 检查 Plannotator 配置/斜杠命令可用 | 提示：按 Plannotator 官方文档配置 Claude Code 插件与 hooks |
| R4 | git worktree/多 Agent | `git worktree list` 可用；确认在 git 仓库内 | 提示：先完成 git init/提交，再规划隔离 worktree |

## 输出格式

Tool Check Result
-----------------
final_tier: R{n}
required tools: [list]
available: [ok / missing: ...]
action: [proceed / init guidance shown]
```

- [ ] **Step 2: 验证**

Run: Grep pattern `Tool Check Result` in `.claude/skills/workflow-router/v2/toolcheck.md`
Expected: 命中。

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/workflow-router/v2/toolcheck.md
git commit -m "feat: add v2 tool availability check"
```

---

## Task 6: 创建 v2/metrics.md

**Files:**
- Create: `.claude/skills/workflow-router/v2/metrics.md`

**Interfaces:**
- Produces: 被 `SKILL.md`（Completion 段）与 `gates/R1~R4.md`（Completion 段）引用；被 `workflow-report.md` 引用

- [ ] **Step 1: 创建文件，写入 record 定义**

```markdown
# Workflow Metrics

每次任务完成后，向 `.claude/workflow-metrics/tasks.md`（追加）写入一条记录。

## Record 字段

| 字段 | 含义 |
|---|---|
| date | 完成日期（YYYY-MM-DD） |
| task_summary | 需求简述 |
| initial_tier | 初始判断档位 |
| final_tier | 最终档位 |
| upgraded | 是否升级（true/false） |
| changed_files | 改动文件数 |
| changed_modules | 涉及模块数 |
| review_reject | 评审是否被拒（true/false） |
| rework | 是否返工（true/false） |
| duration | 耗时（近似小时） |

## 追加格式（Markdown 表格行）

| date | task_summary | initial_tier | final_tier | upgraded | changed_files | changed_modules | review_reject | rework | duration |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-27 | 集成日志基础设施 | R1 | R3 | true | 4 | 3 | true | true | 6 |

## 记录时机

- 任务完成的 Completion 阶段写入。
- 记录是 Router 自优化（/workflow-report）的数据源。
```

- [ ] **Step 2: 验证**

Run: Grep pattern `final_tier` in `.claude/skills/workflow-router/v2/metrics.md`
Expected: 命中。

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/workflow-router/v2/metrics.md
git commit -m "feat: add v2 workflow metrics definition"
```

---

## Task 7: 创建 gates/R1.md ~ R4.md

**Files:**
- Create: `.claude/skills/workflow-router/gates/R1.md`
- Create: `.claude/skills/workflow-router/gates/R2.md`
- Create: `.claude/skills/workflow-router/gates/R3.md`
- Create: `.claude/skills/workflow-router/gates/R4.md`

**Interfaces:**
- Consumes: spec §5（天花板）、§9（评审分级）、§10（门控表）；`v2/levels.md`
- Produces: 被 `SKILL.md` Phase E 加载；被 `new-task.md` Step 2 加载

- [ ] **Step 1: 创建 R1.md（低风险流程）**

```markdown
# R1 Workflow — Low Risk

## Suitable For
- 明确的小 Bug、文案、单点配置、简单 SQL、单字段调整
- 低风险、极小范围

## Workflow
1. Understand request（Goal + Scope 即可，AC/约束可省略）。
2. Inspect only relevant code.
3. **Plan confirmation**：先给出简明计划，用户在终端确认后再动手（Claude Code 原生 plan approval）。
4. Implement the smallest safe change.
5. Run the most relevant tests/checks.
6. Inspect final diff 并给用户终端过目。
7. 按 `v2/metrics.md` 记录一条 record。
8. 按 CLAUDE.md「完成要求」报告。

## Constraints
- 不创建 OpenSpec Change。
- 不使用 Plannotator（评审用终端轻量确认）。
- 不扩大需求范围。
```

- [ ] **Step 2: 创建 R2.md（中风险流程）**

```markdown
# R2 Workflow — Medium Risk

## Suitable For
- 常规功能、有业务规则/数据或架构影响
- R2 档（6~12 分且无红旗）

## Workflow
1. S0 需求理解：Goal/Scope/**Acceptance Criteria**/Constraints（缺 AC 需追问补齐）。
2. S1 规格：创建 OpenSpec Change，写 `proposal.md` + `specs/`（行为规格 Given/When/Then）。
3. S3 计划：用 Superpowers writing-plans 方法论生成任务，写入 OpenSpec `tasks.md`（不另建 plan 文件）。
4. **Plannotator Plan Review**：通过 `tasks.md` 计划，未批准不得进入实现。
5. S4 实施：TDD 编码。
6. S5 验证：单元测试 + 构建 + `openspec status`。
7. S6 **Plannotator Code Review**：评审代码 diff，批准后进入完成。
8. S9 记录 metrics + 按 CLAUDE.md「完成要求」报告。

## Constraints
- OpenSpec 是规格 Source of Truth；Superpowers 只提供方法论。
- 探索中若发现跨服务/数据迁移/核心一致性等，升级 R3。
```

- [ ] **Step 3: 创建 R3.md（高风险流程）**

```markdown
# R3 Workflow — High Risk

## Suitable For
- 中高风险业务、基础设施/数据/架构显著影响
- R3 档（13~24 分或命中任一 R3 红旗）

## Workflow
1. S0 需求理解：完整（含 **Non-goals**）。
2. S1 规格：OpenSpec `proposal.md` + `specs/`（完整 delta）。
3. S2 设计：`design.md`（选定方案+实现约束）；方案对比在对话内完成，不双写。
4. S3 计划：`tasks.md`（详细），含依赖与测试策略。
5. **Plannotator Plan Review** + 规格/架构确认。
6. S4 实施：TDD。
7. S5 验证：单元 + 集成 + 契约（适用时）+ `openspec verify/status`。
8. S6 **Plannotator Code Review** + 专项（安全/数据，适用时）。
9. S8 交付：`openspec apply` + `archive`。
10. S9 记录 metrics + 报告。

## Constraints
- 涉及数据迁移/核心表重构时，验证必须含迁移 dry-run 与回滚演练。
```

- [ ] **Step 4: 创建 R4.md（极高风险流程）**

```markdown
# R4 Workflow — Critical Risk

## Suitable For
- 架构级、核心交易链路、多服务结构性变更、数据迁移
- R4 档（25~39 分或命中 R4 红旗）

## Workflow
完整天花板 S0~S9：
1. S0 完整需求治理（含 Non-goals）→ 需求评审。
2. S1 规格（完整 delta）→ 规格评审。
3. S2 设计：`design.md` + **ADR** + 数据/契约设计 → 架构评审。
4. S3 计划：WBS + 依赖图 + 并行策略（多 Agent / 隔离 worktree，需判断是否适合并行）→ **Plannotator Plan Review**。
5. S4 实施：TDD；多 Agent 并行时各自隔离 worktree。
6. S5 验证：单元 + 集成 + 契约 + 迁移验证 + 静态检查 + 专项。
7. S6 **Plannotator Code Review** + 专项评审。
8. S7 集成：合并 worktree、解决冲突/接口/Schema/契约不一致、全量回归 → 集成验证。
9. S8 交付：`openspec apply` + `archive` + 发布审批。
10. S9 记录 metrics + 报告。

## Constraints
- 不因 L4 就强行多 Agent；先判断任务是否可独立/低耦合/可独立测试。
```

- [ ] **Step 5: 验证四个文件存在**

Run: Glob `.claude/skills/workflow-router/gates/*.md`
Expected: 返回 R1.md ~ R4.md 四个文件。

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/workflow-router/gates/
git commit -m "feat: add R1-R4 gate workflows"
```

---

## Task 8: 重写 SKILL.md

**Files:**
- Modify: `.claude/skills/workflow-router/SKILL.md`（全文重写）

**Interfaces:**
- Consumes: `v2/complexity-matrix.md`, `v2/routing-rules.md`, `v2/levels.md`, `v2/toolcheck.md`, `v2/metrics.md`, `gates/R1~R4.md`
- Produces: 被 `new-task.md` Step 1 加载

- [ ] **Step 1: 重写 SKILL.md**

frontmatter：

```markdown
---
name: workflow-router
description: 根据需求复杂度和代码库实际影响范围，自动评估风险档 R1/R2/R3/R4 并加载对应门控流程。适用于新 Feature、Bug、Refactoring、Architecture Change 等开发任务。
---
```

正文必须包含以下结构（Phase A~G 与 spec §8 一致）：

```markdown
# Workflow Router v2

## Goal
把用户自然语言需求路由到最合适的风险档（R1~R4），并给出该档必须开启的门控。

## Core Principle
简单任务快速完成，复杂任务增加规格、规划与人工评审。不要因为简单而流程化，也不要因为复杂而直接编码。

## 输入模板（Phase A）
明确 Goal / Scope / Non-goals / Acceptance Criteria / Constraints。
R2 及以上若 AC/Constraints 缺失，必须追问补齐；R1 可省略。

## 代码库探索（Phase B）
只探索任务相关范围，防止过度扫描。发现复杂度提升时立即 Re-evaluate。

## 评分（Phase C）
读取 `v2/complexity-matrix.md`，按 8 维加权评分，记录各维度明细。

## 规则应用（Phase D）
读取 `v2/routing-rules.md`，应用红旗升档规则与用户覆盖规则。

## 合并与输出（Phase E）
final_tier = max(level_from(weighted_score), level_from(rules), level_from(red_flags))
读取 `v2/levels.md` 加载对应门控配置。
输出 Assessment：

Workflow Assessment
-------------------
final_tier: R{n}
score: {n}/39
dimensions:
  scope: n | business: n | code: n | architecture: n
  data: n | infrastructure: n | risk: n | collaboration: n
red_flags_hit: [list]
reason: ...
workflow: gates/R{n}.md
required_tools: [...]

## Tool Check（Phase F）
读取 `v2/toolcheck.md`，按 final_tier 检查工具可用性，缺失给初始化引导。

## Re-evaluate（Phase G）
升级自动；降级需说明原因+被移除流程+风险变化并请求确认。

## 完成后
按 `v2/metrics.md` 记录一条 record，按 CLAUDE.md「完成要求」报告。
```

- [ ] **Step 2: 验证交叉引用**

Run: Grep pattern `gates/R` in `.claude/skills/workflow-router/SKILL.md`
Expected: 命中 `gates/R{n}.md` 引用；再用 Glob 确认所有引用文件存在。

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/workflow-router/SKILL.md
git commit -m "feat: rewrite workflow router skill for v2 risk tiers"
```

---

## Task 9: 更新 new-task.md

**Files:**
- Modify: `.claude/commands/new-task.md`

**Interfaces:**
- Consumes: `SKILL.md`
- Produces: 命令入口，最终加载 `gates/R{n}.md`

- [ ] **Step 1: 重写 new-task.md**

正文改为：

```markdown
# New Task

你现在负责处理一个新的开发需求。

## Step 1 — Workflow Assessment
1. 读取 `.claude/skills/workflow-router/SKILL.md` 及其引用的 v2 组件（complexity-matrix/routing-rules/levels/toolcheck）。
2. 理解需求，结合代码库做必要探索。
3. 按 8 维加权评分，应用红旗规则，输出 final_tier 与 Assessment。
4. 执行 Tool Check（确认 OpenSpec/Plannotator 可用性）。
5. 加载 `gates/R{n}.md`。

## Step 2 — Execute Selected Workflow
严格执行对应 gates/R{n}.md 中的流程。

## Step 3 — Re-evaluation
实现前若发现影响范围扩大/跨模块/跨服务/数据结构变化/核心规则变化/高风险链路/需多 Agent，重新评估 final_tier，如需升级立即升级。

## Step 4 — Final Verification
完成后记录 metrics，并报告：
- Initial tier / Final tier
- Changed Files
- Tests / Verification Result
- Review Result
- Remaining Risks
```

- [ ] **Step 2: 验证**

Run: Grep pattern `gates/R` in `.claude/commands/new-task.md`
Expected: 命中。

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/new-task.md
git commit -m "feat: update new-task command for v2 risk tiers"
```

---

## Task 10: 更新 CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Produces: 项目级宪法，`gates/R1~R4.md` 与 `SKILL.md` 均引用其「完成要求」

- [ ] **Step 1: 更新 §3 Workflow Selection**

将：

```markdown
先加载 `.claude/skills/workflow-router/SKILL.md`
再根据判断结果加载 `.claude/skills/workflow-router/workflows/L0.md` ~ `L3.md`
```

改为：

```markdown
先加载 `.claude/skills/workflow-router/SKILL.md`
再根据判断结果加载 `.claude/skills/workflow-router/gates/R1.md` ~ `R4.md`
```

- [ ] **Step 2: 更新 Global Rules**

在 Global Rules 中增加/改写以下条目（对应风险档模型）：

```markdown
1. 收到新需求后，优先进行 Workflow Assessment（评估风险档 R1~R4）。
2. 不要求用户手动指定档位；默认自动判断。
3. 若探索后发现实际复杂度高于初始判断，必须升级档位。
4. 自动升级允许：R1→R2→R3→R4。
5. 降级不允许静默发生；应向用户说明原因与风险变化并请求确认。
6. 涉及核心交易、支付、库存、权限、数据迁移、基础设施（日志/监控/安全）、跨服务一致性或架构变更时，不能仅凭代码改动数量判断复杂度。
7. R2 及以上在开始编码前必须有明确实现计划，并通过人工 Plan Review。
8. 确认点全标配：任何任务都必须有人工确认（计划确认 + 变更过目），工具强度按风险档分级。
9. 完成后必须验证；高风险变更必须再次进行代码 Review。
10. 不要为了流程而流程：简单任务不要强行套用完整流程。
11. 不要为了省流程而省流程：高风险任务不得降级为简单执行。
12. 每次任务完成按 `.claude/skills/workflow-router/v2/metrics.md` 记录 Metrics。
13. 所有结论必须基于当前代码库实际情况，而不是假设。
```

- [ ] **Step 3: 更新组件描述（§1）**

将 "L0：直接执行 / L1：轻量工作流 / L2：标准工程工作流 / L3：完整工程工作流" 改为 "R1：低风险 / R2：中风险 / R3：高风险 / R4：极高风险（门控叠加）"。

- [ ] **Step 4: 验证**

Run: Grep pattern `L[0-3]` in `CLAUDE.md`
Expected: 除标题「L0/L1/L2/L3 不是开发生命周期」这类迁移说明外，无残留（如有残留需一并更新）。

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md constitution for v2 risk tiers"
```

---

## Task 11: 删除旧文件与冗余目录

**Files:**
- Delete: `.claude/skills/workflow-router/complexity-matrix.md`
- Delete: `.claude/skills/workflow-router/routing-rules.md`
- Delete: `.claude/skills/workflow-router/workflows/`（整目录 L0~L3）
- Delete: `claude/`（无点号目录，整目录）

**Interfaces:**
- 前置：必须确认 Task 8/9/10 已把所有旧引用更新完毕

- [ ] **Step 1: 确认无残留引用**

Run: Grep pattern `workflow-router/workflows/|workflow-router/complexity-matrix|workflow-router/routing-rules` in `.claude/` and `CLAUDE.md`
Expected: 无命中（引用已全部指向 v2/ 与 gates/）。

- [ ] **Step 2: 删除文件**

```bash
git rm -r .claude/skills/workflow-router/complexity-matrix.md
git rm -r .claude/skills/workflow-router/routing-rules.md
git rm -r .claude/skills/workflow-router/workflows
git rm -r claude
```

- [ ] **Step 3: 验证删除**

Run: Glob `.claude/skills/workflow-router/**` 与 Glob `claude/**`
Expected: 旧文件不存在；`.claude/skills/workflow-router/` 下仅剩 SKILL.md、v2/、gates/。

- [ ] **Step 4: Commit**

```bash
git commit -m "chore: remove legacy L0-L3 files and redundant claude dir"
```

---

## Task 12: 同步详细使用说明文档

**Files:**
- Modify: `AI-Coding-Workflow-Template-详细使用说明.md`

**Interfaces:**
- Consumes: spec 全部内容

- [ ] **Step 1: 更新模型描述**

将全文中 L0/L1/L2/L3 章节改写为 R1~R4 风险档模型：
- §2「L0/L1/L2/L3 到底是什么」→「R1~R4 风险档是什么」
- §11~14 的实际示例（NPE 修复→R1、列表筛选→R2、自动取消→R3、订单拆分→R4）
- §18 评分改为 8 维加权；§19 强制升级改为红旗规则
- 新增 Tool Check 与 Metrics 章节（引用 `.claude/skills/workflow-router/v2/`）
- 更新目录结构图（v2/ 与 gates/）
- 更新 `/new-task` 与 `/workflow-report` 用法

保留有价值章节：安装步骤、新旧项目差异、医药电商规则、演进路线（将 V1 标注为历史，V2 为当前）。

- [ ] **Step 2: 验证**

Run: Grep pattern `L0/L1/L2/L3` in `AI-Coding-Workflow-Template-详细使用说明.md`
Expected: 仅剩"V1 历史/迁移说明"性质的提及，无描述当前模型的 L0-L3。

- [ ] **Step 3: Commit**

```bash
git add AI-Coding-Workflow-Template-详细使用说明.md
git commit -m "docs: sync user guide to v2 risk tiers"
```

---

## Task 13: 创建 workflow-report 命令

**Files:**
- Create: `.claude/commands/workflow-report.md`

**Interfaces:**
- Consumes: `.claude/workflow-metrics/tasks.md`（运行时数据）

- [ ] **Step 1: 创建命令文件**

```markdown
---
description: 汇总 Workflow Metrics，输出升级率/误判提示，辅助调整评分与规则
---

# Workflow Report

读取 `.claude/workflow-metrics/tasks.md`，输出：

## 报告内容
1. 任务总数、各档（initial/final）分布
2. 升级率：initial_tier < final_tier 的比例
3. 误判提示：若升级率偏高（如 >30%），提示评分矩阵或红旗规则可能低估，建议调整 v2/complexity-matrix.md 或 v2/routing-rules.md
4. 返工率与评审被拒率：过高则提示计划/评审门控需加强

## 输出示例
Workflow Report
---------------
total tasks: 12
tier distribution (final): R1=3, R2=4, R3=4, R4=1
upgrade rate: 33% (4/12)
rework rate: 17%
suggestion: upgrade rate high → review weighted score thresholds
```

- [ ] **Step 2: 验证**

Run: Glob `.claude/commands/workflow-report.md`
Expected: 存在。

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/workflow-report.md
git commit -m "feat: add workflow-report command for metrics analysis"
```

---

## Task 14: 终验与收尾

**Files:**
- Modify: `docs/superpowers/specs/2026-08-26-ai-coding-workflow-v2-design.md`（状态：草案→已实施）

**Interfaces:**
- 覆盖全部 task 产物

- [ ] **Step 1: 全引用一致性检查**

Run: Grep pattern `workflows/L|complexity-matrix\.md|routing-rules\.md`（旧路径）in `.claude/` `CLAUDE.md` `AI-Coding-Workflow-Template-详细使用说明.md`
Expected: 无命中。

Run: 遍历 `.claude/skills/workflow-router/SKILL.md` 与 `.claude/commands/*.md` 中所有 `.md` 引用路径，逐一 Glob 确认存在。

- [ ] **Step 2: 术语残留检查**

Run: Grep pattern `L0|L1|L2|L3` in `.claude/` `CLAUDE.md`
Expected: 仅剩背景/迁移说明性质的提及。

- [ ] **Step 3: 更新 spec 状态**

将 spec 头部 `状态：草案（待用户评审）` 改为 `状态：已实施（2026-08-27）`。

- [ ] **Step 4: 最终提交**

```bash
git add .
git commit -m "docs: finalize v2 workflow spec status"
```

- [ ] **Step 5: 汇报**

向用户汇报：What changed / Why / Tests run（验证命令结果）/ Remaining uncertainty / Side effects。

---

## Self-Review 备注

- **Spec 覆盖**：D1→Task 2/3/4/7；D2→Task 7（R1-R4 裁剪）；D3→Task 2-9（工具边界）；D4→Task 7（评审分级）；D5→Task 2/3；D6→Task 8；D7→Task 5/9；D8→Task 6/13。§12 文件变更全部对应 Task 2-13。
- **占位符**：所有 Task 均给出实际文件内容骨架与验证命令，无 TBD。
- **类型一致**：术语统一为 `final_tier`、`R1~R4`；引用路径在 Task 8/11/14 三处显式校验。
