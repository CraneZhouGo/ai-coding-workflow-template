---
date created: 2026-08-25 11:54:49
date modified: 2026-08-27
---
# AI Coding Workflow Template 详细使用说明

> 版本：V2.0  
> 适用范围：Java / Spring Boot / Spring Cloud / DDD / 微服务项目  
> 核心工具：Claude Code + Superpowers + OpenSpec + Plannotator  
> 核心思想：根据需求复杂度自动评估风险档 R1~R4，并叠加对应门控

---

# 1. 这套体系解决什么问题

传统 AI Coding 很容易变成：

```text
用户提出需求
    ↓
Claude Code 直接修改代码
    ↓
测试
    ↓
结束
```

简单需求这样做没有问题。

但是复杂需求会出现：

- 没有充分理解需求就开始编码
- 修改范围失控
- 架构设计不完整
- AI 自己决定方案，没有人工 Review
- 多个 Agent 修改相同代码产生冲突
- 数据库、MQ、Redis、事务等风险没有提前暴露
- 简单需求又被迫走非常重的流程，浪费时间

本体系采用：

```text
需求
 ↓
Workflow Router
 ↓
风险/复杂度分析
 ↓
自动评估 R1/R2/R3/R4
 ↓
叠加对应门控
 ↓
执行对应 Workflow
 ↓
验证
 ↓
完成
```

核心原则：

> 简单任务快速完成，复杂任务增加规格、规划和人工审核。

---

# 2. R1~R4 风险档是什么

R1/R2/R3/R4 不是软件开发生命周期，也不是“项目阶段”。

它们代表：

> 根据当前需求复杂度评估出的风险档位，以及该档位必须开启的门控列表。

有一个“天花板”概念需要先理解：S0~S9 定义了完整工程流程（需求治理 → 规格化 → 架构设计 → 计划 → 实施 → 验证 → 代码评审 → 集成 → 交付 → 度量）。低风险任务从这条完整流程上裁剪不需要的阶段，档位越高保留的阶段与人工 Gate 越多，这就是**门控叠加**。

## R1（Low，低风险）

适用于：

- 明确的小 Bug
- 文案修改
- 单点配置修改
- 单文件或极小范围修改
- 低风险任务

流程：

```text
需求
 ↓
理解
 ↓
定位
 ↓
修改
 ↓
测试
 ↓
查看 diff
 ↓
完成
```

主要工具：

```text
Claude Code
```

不要求：

- OpenSpec
- Plannotator
- 完整 Plan Review

---

## R2（Medium，中风险）

适用于：

- 新查询接口
- 常规 CRUD 增强
- 小型 Feature
- 有业务规则/数据或架构影响的常规功能
- 风险中等

流程：

```text
需求
 ↓
需求分析
 ↓
代码探索
 ↓
OpenSpec
 ↓
proposal / specs / tasks
 ↓
计划确认
 ↓
Plannotator Plan Review
 ↓
人工批准
 ↓
TDD 实现
 ↓
测试
 ↓
Plannotator Code Review
 ↓
最终验证
```

主要工具：

```text
Superpowers
OpenSpec
Claude Code
Plannotator
```

---

## R3（High，高风险）

适用于：

- 订单状态机
- 日志基础设施集成
- Schema 变更
- 基础设施/数据/架构有显著影响的需求
- 中高风险业务

流程：

```text
需求（含 Non-goals）
 ↓
代码探索
 ↓
OpenSpec
 ↓
proposal / specs / design.md / 详细 tasks
 ↓
Plannotator Plan Review
 ↓
规格/架构确认
 ↓
人工批准
 ↓
TDD 实现
 ↓
单元 + 集成 + 契约测试
 ↓
Plannotator Code Review
 ↓
专项评审（安全/数据）
 ↓
最终验证
```

主要工具：

```text
Superpowers
OpenSpec
Claude Code
Plannotator
```

---

## R4（Critical，极高风险 / 门控全开）

适用于：

- 微服务拆分
- 核心架构变化
- 大规模重构
- 多服务结构性变化
- 核心交易链路
- 数据迁移
- 多 Agent 协作
- 高风险工程任务

流程：

```text
完整需求（Goal/Scope/Non-goals/AC/Constraints）
 ↓
代码库理解
 ↓
Superpowers
 ↓
Architecture Analysis
 ↓
OpenSpec Proposal
 ↓
OpenSpec Design（+ADR）
 ↓
OpenSpec Specs
 ↓
OpenSpec Tasks（WBS + 依赖）
 ↓
Implementation Plan
 ↓
Plannotator Plan Review
 ↓
人工批准
 ↓
任务拆分
 ↓
多 Agent / 独立 Worktree（需要时）
 ↓
并行实现（TDD）
 ↓
单元 / 集成 / 迁移 / 专项测试
 ↓
Integration
 ↓
Plannotator Code Review
 ↓
Merge
 ↓
OpenSpec apply / archive + 发布审批
```

---

# 3. 四个工具分别负责什么

不要把四个工具理解成同一种东西。

工具职责边界可以浓缩成一句话：

> **产物归 OpenSpec、过程归 Superpowers、评审归 Plannotator、执行归 Claude Code。**

| 职责 | 归属 |
|---|---|
| 产物/生命周期/审计（State） | OpenSpec：`proposal.md` / `specs/` / `design.md` / `tasks.md` + `apply`/`archive`/`verify` |
| 过程方法论（Flow） | Superpowers：brainstorming / writing-plans / TDD / verification / review / finishing |
| 人工评审 Gate | Plannotator：Plan Review + Code Review + Compound Planning |
| 执行层 | Claude Code：读写代码、跑命令、测试、git |

## Claude Code

定位：

> AI Coding 执行引擎

负责：

- 读取代码
- 修改代码
- 执行命令
- 编写测试
- 调试
- 验证
- Git 操作

它是执行层。

---

## Superpowers

定位：

> Agent Workflow 能力层（过程方法论）

负责：

- 需求理解
- 代码库探索
- 分析
- 规划
- 执行
- 测试
- Review
- 多 Agent 协作能力

Superpowers 中已经包含多个开发工作流能力。

因此不需要把其中的具体节点再人为复制一套。

本体系只需要规定：

> 当前任务应该使用什么风险档的 Workflow。

---

## OpenSpec

定位：

> Specification Source of Truth（产物）

负责：

- Proposal
- Design
- Requirements / Specs
- Tasks
- 变更记录

它解决的是：

> AI 到底应该实现什么？

而不是：

> AI 怎么执行每一步？

---

## Plannotator

定位：

> Human Review Gate

负责：

```text
AI Plan
 ↓
Human Review
 ↓
Approve / Reject
```

以及：

```text
AI Code
 ↓
Human Review
 ↓
Approve / Reject
```

它解决的是：

> AI 提出的方案和最终代码是否值得让人批准？

---

## 双重写规避（设计/计划只沉淀 OpenSpec）

Superpowers 默认会自己产生两类文件，与 OpenSpec 的产物职责重叠：

1. **brainstorming 默认写 `docs/superpowers/specs/`** → 与 OpenSpec 的 `design.md` 重叠。
2. **writing-plans 默认生成独立 plan 文件** → 与 OpenSpec 的 `tasks.md` 重叠。

如果两个位置各写一份，就会形成双 Source of Truth，容易双写、漂移，且不知道该以哪份为准。

V2 的约定是**产物唯一，过程共享**：用 Superpowers 的方法论产出 OpenSpec 的产物，不双写。

| 重叠点 | 处理 |
|---|---|
| 需求理解 | brainstorming 在对话内探索，只把结论沉淀为 OpenSpec `proposal.md` |
| 行为规格 | 只写 OpenSpec `specs/`；brainstorming 不产长期文件 |
| 设计 | 方案对比在对话内完成，只把选定方案写入 OpenSpec `design.md` |
| 任务/计划 | **用 writing-plans 方法论填充 `tasks.md`，不另建 plan 文件** |

因此，Plannotator 只审 OpenSpec 一处（`tasks.md` 计划 + 代码 diff），不审 Superpowers 过程产物。

---

# 4. 最终架构

```text
                         User Requirement
                                │
                                ▼
                      ┌────────────────────┐
                      │  Workflow Router   │
                      │  风险档 + 门控叠加   │
                      └──────────┬─────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             ▼                   ▼                   ▼
            R1                  R2                  R3
             │                   │                   │
             ▼                   ▼                   ▼
        Claude Code        Superpowers        Superpowers
                                                   │
                                                OpenSpec
                                                   │
                                             Claude Code
                                                   │
                                            Plannotator
                                                   │
                                                   ▼
                                                  R4
                                                   │
                                            Full Workflow
                                                   │
                         ┌─────────────────────────┼───────────────┐
                         ▼                         ▼               ▼
                    Superpowers                OpenSpec       Claude Code
                         │                         │               │
                         └─────────────────────────┼───────────────┘
                                                   ▼
                                              Plannotator
                                                   │
                                                   ▼
                                              Multi-Agent
                                              / Worktree
                                                   │
                                                   ▼
                                               Integration
```

---

# 5. 项目目录结构

将模板复制到 Java 项目根目录后：

```text
project/
│
├── CLAUDE.md
│
├── .claude/
│   ├── commands/
│   │   ├── new-task.md
│   │   └── workflow-report.md
│   │
│   ├── workflow-metrics/
│   │   └── tasks.md        （运行时自动生成）
│   │
│   └── skills/
│       └── workflow-router/
│           ├── SKILL.md
│           │
│           ├── v2/
│           │   ├── complexity-matrix.md
│           │   ├── routing-rules.md
│           │   ├── levels.md
│           │   ├── toolcheck.md
│           │   └── metrics.md
│           │
│           └── gates/
│               ├── R1.md
│               ├── R2.md
│               ├── R3.md
│               └── R4.md
│
├── openspec/
│
├── pom.xml
│
└── src/
```

---

# 6. 每个文件的职责

## CLAUDE.md

项目级 AI Coding 宪法。

负责：

- 全局规则
- 工程规范
- Workflow 基本原则
- 完成标准

建议每个项目都保留一个。

---

## .claude/commands/new-task.md

统一入口。

开发者输入：

```text
/new-task xxx
```

Claude Code 自动：

1. 加载 Workflow Router
2. 分析需求
3. 评估复杂度与风险
4. 执行 Tool Check（检查工具可用性）
5. 输出风险档 R1~R4
6. 执行对应门控流程

---

## .claude/commands/workflow-report.md

Metrics 汇总命令。

负责：

- 汇总历史任务的升级率、各档分布、返工率
- 输出调参建议（提示哪些评分维度偏低、哪些红旗缺失）

---

## workflow-router/SKILL.md

Workflow Router 核心 Skill。

负责定义路由流程：

- Phase A 需求理解
- Phase B 代码库探索
- Phase C 评分
- Phase D 规则应用
- Phase E 合并与输出
- Phase F Tool Check
- Phase G Re-evaluate

---

## v2/complexity-matrix.md

复杂度评分标准（8 维加权）。

每项 0~3 分，加权求和，最高 39 分。

---

## v2/routing-rules.md

红旗升档规则。

解决：

> 有些需求代码改动很少，但是风险极高。

例如：

- 库存
- 支付
- 订单状态
- 数据迁移
- Kafka
- Redis 分布式一致性
- 跨服务事务

---

## v2/levels.md

R1~R4 四档的门控配置总表。

Router 判断出档位后加载对应配置。

---

## v2/toolcheck.md

工具可用性检查。

按 final_tier 检查所需工具，缺失给初始化引导。

---

## v2/metrics.md

Metrics 记录字段与写入格式。

每次任务完成后向 `.claude/workflow-metrics/tasks.md` 追加一条记录。

---

## gates/R1~R4.md

分别定义四档执行流程。

Router 判断出档位后加载对应文件。

---

# 7. 第一次安装

## Step 1：复制模板

将：

```text
CLAUDE.md
.claude/
```

复制到项目根目录。

---

## Step 2：确认 Claude Code

在项目目录启动：

```bash
claude
```

确认 Claude Code 可以读取项目文件。

---

## Step 3：安装 Superpowers

按照当前 Superpowers 项目的官方安装方式安装。

安装后确认 Claude Code 可以发现对应 Skills。

---

## Step 4：初始化 OpenSpec

按照当前 OpenSpec 版本的官方安装/初始化方式初始化项目。

初始化后应该出现类似：

```text
openspec/
├── specs/
└── changes/
```

具体目录结构以当前 OpenSpec 版本为准。

---

## Step 5：安装 Plannotator

按照 Plannotator 当前版本的官方安装方式配置。

确认能够对 Plan 和 Code Change 进行 Review。

---

# 8. 第一次进入已有项目

对于已有 Java 项目，不要马上开发。

先让 Claude Code：

```text
分析当前项目的：

1. 项目结构
2. Maven/Gradle 模块
3. Java/Spring Boot 版本
4. 微服务边界
5. 数据库
6. Redis
7. Kafka/MQ
8. 事务边界
9. API 结构
10. 测试体系
11. 日志和监控
12. 现有工程规范

不要修改代码。

根据分析结果，给出应该补充到 CLAUDE.md 的 Project Engineering Rules。
```

然后人工检查。

---

# 9. 新项目的推荐初始化顺序

新项目推荐：

```text
创建 Git Repository
        ↓
创建 Java / Spring Boot 项目
        ↓
配置 Maven / Gradle
        ↓
启动基础工程
        ↓
安装 Claude Code
        ↓
安装 Superpowers
        ↓
初始化 OpenSpec
        ↓
安装 Plannotator
        ↓
复制本模板
        ↓
完善 CLAUDE.md
        ↓
开始 /new-task
```

不要在项目完全没有基本结构时，直接让 AI 开始大量业务开发。

---

# 10. 正式开发统一入口

推荐统一使用：

```text
/new-task <需求>
```

例如：

```text
/new-task 修复订单查询接口偶发 NPE
```

或者：

```text
/new-task 给商品增加品牌筛选条件
```

或者：

```text
/new-task 增加订单创建后30分钟自动取消功能
```

或者：

```text
/new-task 将订单和库存拆成两个独立微服务
```

用户不需要告诉 AI：

```text
这是 R3
```

Router 自动评估风险档，并自动执行 Tool Check。

---

# 11. R1 实际示例

需求：

```text
/new-task 修复 OrderService.getOrder() 的 NPE
```

Router 分析（8 维加权）：

```text
Scope:             0 ×1 = 0
Business:          0 ×1 = 0
Code Impact:       0 ×1 = 0
Architecture:      0 ×2 = 0
Data:              0 ×2 = 0
Infrastructure:    0 ×2 = 0
Risk:              1 ×3 = 3
Collaboration:     0 ×1 = 0

加权总分: 3

无红旗命中

final_tier: R1
```

然后：

```text
定位代码
 ↓
理解问题
 ↓
修复
 ↓
运行测试
 ↓
查看 diff
 ↓
完成
```

不会创建 OpenSpec。

---

# 12. R2 实际示例

需求：

```text
/new-task 给订单列表增加订单状态和创建时间范围筛选
```

可能判断：

```text
Scope:             1 ×1 = 1
Business:          1 ×1 = 1
Code Impact:       1 ×1 = 1
Architecture:      0 ×2 = 0
Data:              1 ×2 = 2
Infrastructure:    0 ×2 = 0
Risk:              1 ×3 = 3
Collaboration:     0 ×1 = 0

加权总分: 8

无红旗命中

final_tier: R2
```

流程：

```text
需求分析
 ↓
代码探索
 ↓
OpenSpec proposal / specs / tasks
 ↓
计划确认
 ↓
Plannotator Plan Review
 ↓
人工批准
 ↓
TDD 实现
 ↓
测试
 ↓
Plannotator Code Review
 ↓
最终验证
```

---

# 13. R3 实际示例

需求：

```text
/new-task 增加订单创建后30分钟自动取消功能
```

Router 考虑的因素：

```text
订单状态
定时任务
Redis/Kafka
库存释放
异步流程
```

可能判断：

```text
Scope:             2 ×1 = 2
Business:          2 ×1 = 2
Code Impact:       1 ×1 = 1
Architecture:      1 ×2 = 2
Data:              1 ×2 = 2
Infrastructure:    0 ×2 = 0
Risk:              2 ×3 = 6
Collaboration:     0 ×1 = 0

加权总分: 15

无红旗命中

final_tier: R3
```

此处进入 R3 是因为评分结果（总分 15 在 13~24 区间），而非红旗规则；其他场景也可能因命中红旗规则而进入 R3。

流程：

```text
OpenSpec
 ↓
proposal / specs / design.md / 详细 tasks
 ↓
Plannotator Plan Review
 ↓
规格/架构确认
 ↓
人工批准
 ↓
TDD 实现
 ↓
单元 + 集成 + 契约测试
 ↓
Plannotator Code Review
 ↓
最终验证
```

---

# 14. R4 实际示例

需求：

```text
/new-task

将现有订单系统拆分成：

Order Service
Inventory Service
Product Service

并通过 Kafka 实现订单事件异步处理。
```

直接判定：

```text
final_tier: R4
```

因为：

- 微服务拆分
- 架构变化
- Kafka
- 服务边界变化
- 数据一致性
- 多服务联动
- 多 Agent / 隔离 Worktree

评分参考：

```text
Scope:             3 ×1 = 3
Business:          3 ×1 = 3
Code Impact:       3 ×1 = 3
Architecture:      3 ×2 = 6
Data:              3 ×2 = 6
Infrastructure:    2 ×2 = 4
Risk:              3 ×3 = 9
Collaboration:     2 ×1 = 2

加权总分: 36

命中红旗：微服务拆分 → R4
final_tier: R4
```

流程：

```text
Architecture Analysis
 ↓
Superpowers
 ↓
OpenSpec Proposal
 ↓
OpenSpec Design（+ADR）
 ↓
OpenSpec Specs
 ↓
OpenSpec Tasks（WBS + 依赖）
 ↓
Implementation Plan
 ↓
Plannotator
 ↓
人工批准
 ↓
任务拆分
 ↓
多 Agent / 独立 Worktree（需要时）
 ↓
实现
 ↓
单元 / 集成 / 迁移 / 专项测试
 ↓
Integration
 ↓
Plannotator Code Review
 ↓
Merge
 ↓
OpenSpec apply / archive + 发布审批
```

---

# 15. 为什么不能只根据需求文字判断

例如：

```text
增加订单一个字段
```

从文字看：

```text
R1/R2
```

但探索代码后可能发现：

```text
Order Service
 ↓
Kafka Event
 ↓
Inventory Service
 ↓
Search Service
 ↓
ES
 ↓
Data Sync
```

那么实际复杂度可能变成：

```text
R3
```

因此 Router 必须：

```text
需求分析
 +
代码库探索
 =
最终风险档
```

而不是：

```text
只看用户输入
```

---

# 16. Workflow Re-evaluation

Router 不是只判断一次。

例如：

```text
初始：

R1
 ↓
探索代码
 ↓
发现 Kafka
 ↓
发现跨服务
 ↓
发现数据一致性问题
 ↓
升级 R2 / R3
```

允许：

```text
R1 → R2 → R3 → R4
```

升级可以自动发生，立即执行更高档的流程。

---

# 17. 为什么不建议自动降级

假设：

```text
初始 R2
```

后来发现：

```text
实际修改非常简单
```

可以建议：

```text
建议降级 R1。
原因：
...
```

但是不应该静默降级。

因为降级意味着可能取消：

- OpenSpec
- Plan Review
- Code Review
- 人工审批

因此应由开发者决定。

降级时必须说明：原因、被移除的流程、风险变化，并请求确认。

---

# 18. 复杂度评分（8 维加权）

当前模板采用：

```text
Scope                  ×1   0~3
Business Complexity    ×1   0~3
Code Impact            ×1   0~3
Architecture Impact    ×2   0~3
Data Impact            ×2   0~3
Infrastructure         ×2   0~3   （日志/监控/安全/配置/部署管道等横切变更）
Risk                   ×3   0~3
Collaboration          ×1   0~3
```

最高：

```text
39 分
```

基础映射：

```text
0~5     → R1
6~12    → R2
13~24   → R3
25~39   → R4
```

但是：

> 总分不是唯一依据。

必须应用红旗升档规则（见下一节）。

---

# 19. 红旗规则

任一红旗命中，final_tier 直接取最高。

| 红旗 | 最低档 |
|---|---|
| Risk ≥ 3（库存扣减/支付/核心链路等） | R3 |
| Data = 3（数据迁移/核心表重构） | R3 |
| Infrastructure ≥ 3（日志/监控/基础设施集成） | R3 |
| Architecture = 3（模块边界重构） | R3 |
| 微服务拆分 / 核心架构重构 / 关键基础设施替换 | R4 |
| 多 Agent / 多隔离 Worktree 需要 | R4 |

最终档位公式（保证可复现）：

```text
final_tier = max(level_from(weighted_score),
                 level_from(rules),
                 level_from(red_flags))
```

---

# 20. 为什么“风险”必须单独存在

例如：

```text
修改库存扣减一行代码
```

Scope：

```text
0
```

但是：

```text
Risk = 3
```

命中红旗：

```text
Risk ≥ 3 → 至少 R3
```

所以不能：

```text
R1
```

这可以避免 AI 因为“修改文件少”而低估核心业务风险。

---

# 21. Tool Check（工具可用性检查）

路由输出 final_tier 之后、执行流程之前，先检查该档位所需的工具是否可用。缺失则给出初始化引导。

| 档位 | 必需工具 | 检查方式 | 缺失引导 |
|---|---|---|---|
| R1 | Claude Code | — | — |
| R2+ | OpenSpec | 存在 `openspec/` 目录 | 提示：运行 `openspec init` 或按 OpenSpec 官方文档初始化 |
| R2+ | Plannotator | 检查 Plannotator 配置/斜杠命令可用 | 提示：按 Plannotator 官方文档配置插件与 hooks |
| R4 | git worktree / 多 Agent | `git worktree list` 可用；确认在 git 仓库内 | 提示：先完成 git init/提交，再规划隔离 worktree |

由 `/new-task` 自动完成，不需要用户手动执行。

例如，一个被判定为 R3 的任务要求 OpenSpec，但项目还没有初始化 `openspec/`，Router 会在此处停下并提示初始化，而不是直接卡死在流程中。

---

# 22. R2+ 中 OpenSpec 的作用

OpenSpec 不应该被理解成：

> “又多写几个 Markdown 文件。”

它真正解决的是：

```text
需求
 ↓
明确行为
 ↓
明确设计
 ↓
明确任务
 ↓
AI 实现
```

因此：

```text
OpenSpec
```

是 Specification Source of Truth。

如果实现过程中出现争议，应优先回到 Spec 判断：

> 当前实现是否符合需求定义？

---

# 23. R2+ 中 Plannotator 的位置

先明确评审模型：**确认点全标配，工具强度按风险档分级。**

确认点全标配：任何任务都必须有 ① 计划确认 ② diff 过目。

工具强度分级：

| 风险档 | Plan Review | Code Review |
|---|---|---|
| R1 | 终端内确认计划（必） | AI 自审 diff + 用户终端过目（必） |
| R2 | Plannotator Plan Review（必） | Plannotator Code Review（必） |
| R3/R4 | Plannotator Plan Review + 规格/架构确认 | Plannotator Code Review + 专项（安全/数据） |

推荐的位置：

```text
OpenSpec
 ↓
Implementation Plan
 ↓
Plannotator
 ↓
Human Approval
 ↓
Coding
```

不要：

```text
Coding
 ↓
发现方案不对
 ↓
返工
```

人工 Review 的核心目的：

> 在修改大量代码之前发现错误。

---

# 24. R4 中多 Agent 的使用原则

不要看到 R4 就强行多 Agent。启用多 Agent 前必须完成 **DAG 拆分**（见 `gates/R4.md` S3）：

```text
1. 任务建模为 DAG：节点 = 任务，边 = 依赖。
2. 拓扑分层：同层任务无互相依赖（可并行），跨层有依赖（需串行）。
3. 识别关键路径（最长依赖链），关键路径任务优先规划、不因并行而延迟。
4. 标注并行扇出与收敛点（join）：并行分支完成后需收敛/集成验证。
5. 只有拆出 ≥2 个无共享状态、可独立测试的批次才启用多 Agent（各自隔离 worktree）；否则单 Agent 串行。
```

DAG 拆分前用以下定性判断做快速筛选：

```text
任务是否可以独立？
任务之间是否低耦合？
是否有明确边界？
是否可以独立测试？
```

```text
任务是否可以独立？
任务之间是否低耦合？
是否有明确边界？
是否可以独立测试？
```

例如：

```text
Order Service
Inventory Service
Product Service
```

可以考虑：

```text
Agent A → Order
Agent B → Inventory
Agent C → Product
```

但：

```text
三个 Agent
同时修改
同一个核心 Domain
```

就不适合简单并行。

---

# 25. Worktree 的使用

R4 如果需要并行开发，建议：

```text
main
 │
 ├── worktree/order
 ├── worktree/inventory
 └── worktree/product
```

而不是多个 Agent 全部修改同一个工作目录。

这样可以降低：

- 文件覆盖
- Git 冲突
- 半成品互相污染
- 测试环境相互干扰

---

# 26. 如何处理用户强制指定档位

用户可以说：

```text
/new-task R2：增加商品查询接口
```

Router 可以尊重。

但是：

如果用户要求：

```text
/new-task R1：修改支付逻辑
```

不能简单按 R1 执行。

应该提示：

```text
该需求涉及支付核心链路。

按照项目 Routing Rules：
最低安全档为 R3。

如果按 R1 执行，将跳过：
- Specification
- Plan Review
- Code Review

是否继续？
```

---

# 27. 什么时候直接使用 Claude Code，不使用 /new-task

可以。

例如：

```text
帮我查看 OrderService 有哪些方法
```

这是探索，不是开发任务。

或者：

```text
解释这个异常
```

也是咨询。

只有真正需要执行开发任务时，推荐：

```text
/new-task
```

---

# 28. 建议的日常工作方式

每天开发时：

```text
进入项目
 ↓
claude
 ↓
/new-task <需求>
 ↓
Router 自动评估风险档
 ↓
Tool Check
 ↓
执行对应门控流程
 ↓
测试
 ↓
Review
 ↓
记录 Metrics
 ↓
完成
```

开发者主要参与：

```text
需求表达
方案确认
Plan Review
高风险决策
最终 Review
```

而不是：

```text
自己手工安排每一个 Agent 步骤
```

---

# 29. 新项目与旧项目的区别

## 新项目

重点是：

```text
架构
 ↓
Domain
 ↓
模块边界
 ↓
工程规范
```

建议更积极使用：

```text
R3/R4
```

因为早期架构决策会影响整个项目。

---

## 旧项目

重点是：

```text
Codebase Exploration
 ↓
理解现有系统
 ↓
识别隐式规则
 ↓
最小改动
```

不要让 AI 因为一个 Feature 顺手重构整个项目。

---

# 30. 医药电商项目的特殊建议

对于订单、库存、支付、处方、退款等业务，可以进一步增强：

```text
routing-rules.md
```

中的红旗规则。例如：

```text
处方审核          → 最低 R3
处方购药          → 最低 R3
订单状态机        → 最低 R3
库存扣减          → 最低 R3
支付              → 最低 R3
退款              → 最低 R3
订单/库存一致性   → 最低 R3
GSP 核心规则      → 最低 R3
跨服务事务        → R3/R4
订单系统拆分      → R4
```

这些业务普遍命中 `Risk ≥ 3` 红旗（交易/库存/支付/权限），因此最低 R3 与红旗规则保持一致。这样 Router 会更符合实际业务风险。

---

# 31. Workflow Metrics（内置）

V2 内建 Metrics 数据层，不需要手工维护表格。

每次任务完成时，Router 自动向：

```text
.claude/workflow-metrics/tasks.md
```

追加一条记录：

```text
date, task_summary, initial_tier, final_tier, upgraded,
changed_files, changed_modules, review_reject, rework, duration
```

新增命令：

```text
/workflow-report
```

作用：

- 汇总历史任务的升级率、各档分布、返工率
- 输出调参建议（提示哪些评分维度偏低、哪些红旗缺失）

---

# 32. 如何逐步优化 Router

第一版不要追求完美。

建议运行：

```text
20~50 个真实需求
```

然后通过：

```text
/workflow-report
```

查看统计：

```text
Requirement
Initial Tier
Final Tier
Upgrade?
Review Reject?
Changed Files
Changed Modules
Development Time
Bug / Rework
```

例如：

```text
AI 判断 R1
实际 R2
```

出现很多次，就说明：

```text
complexity-matrix.md
```

的阈值/权重需要调整。

例如：

```text
AI 判断 R2
实际 R3
```

很多次，就说明：

```text
routing-rules.md
```

缺少红旗条件。

---

# 33. V1 / V2 / V3 演进路线

## V1（历史，已归档）

V1 采用 L0/L1/L2/L3 四层强度模型：

- 7 维等权评分（最高 20 分）
- 强制升级规则
- `workflows/L0.md` ~ `L3.md`

V1 在真实项目跑过多个需求，暴露的问题：

- 评分矩阵没有“基础设施/横切”维度，日志基础设施集成这类需求被误判为最低档
- 评分与规则合并没有明确公式，结果不可复现
- 路由时不检查工具可用性，实际运行会卡死
- Superpowers 与 OpenSpec 职责重叠，易双写、漂移
- 没有数据自优化闭环

## V2（当前）

V2 改为“风险档 R1~R4 + 门控叠加”模型：

- 8 维加权评分（最高 39 分）+ 红旗规则
- 确定性的 `final_tier` 公式
- 路由阶段内建 Tool Check（工具可用性检查 + 初始化引导）
- 内建 Workflow Metrics 与 `/workflow-report`
- 明确工具职责边界：产物归 OpenSpec、过程归 Superpowers、评审归 Plannotator、执行归 Claude Code

## V3（未来）

增加：

```text
历史任务数据
+
Workflow Metrics 自动优化规则
+
项目级领域 Risk Profile
```

目标：

> 让 Router 从静态规则逐渐变成项目专属的 Workflow Intelligence。

---

# 34. 最终推荐的团队规范

团队成员只需要记住：

```text
新开发需求：

/new-task <需求>
```

另外，定期跑一次：

```text
/workflow-report
```

不需要记：

```text
这个应该用 OpenSpec 吗？
这个应该用 Superpowers 吗？
这个要不要 Plannotator？
这个是 R1 还是 R2？
```

这些问题交给：

```text
Workflow Router
```

---

# 35. 最终完整闭环

```text
                         用户需求
                            │
                            ▼
                     /new-task
                            │
                            ▼
                  ┌──────────────────┐
                  │ Workflow Router  │
                  └────────┬─────────┘
                           │
                    需求复杂度分析
                           │
                    代码库必要探索
                           │
                    Routing / 红旗规则
                           │
                     Tool Check
                           │
                           ▼
                  R1 / R2 / R3 / R4
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
       R1                 R2                 R3
        │                  │                  │
   Claude Code       Superpowers       Superpowers
                                          │
                                       OpenSpec
                                          │
                                          Plan
                                          │
                                    Plannotator
                                          │
                                      Approval
                                          │
                                    Claude Code
                                          │
                                         Test
                                          │
                                    Code Review
                                          │
                                          ▼
                                         R4
                                          │
                                  Full Engineering
                                          │
                              Architecture + Spec
                                          │
                                     Plan Review
                                          │
                                  Multi-Agent
                                  （需要时）
                                          │
                                     Integration
                                          │
                                    Code Review
                                          │
                                        Merge
                                          │
                                OpenSpec apply/archive
                                          │
                                        完成
                                          │
                                       记录 Metrics
                                          │
                                    /workflow-report
```

---

# 36. 最重要的设计原则

最后把整套体系浓缩成 8 条：

1. **需求复杂度决定风险档 R1~R4。**
2. **用户不需要手动判断档位。**
3. **Workflow Router 是统一入口（`/new-task`）。**
4. **代码库探索后可以重新评估。**
5. **复杂度增加时自动升级。**
6. **高风险任务不能因为代码改动少而降级。**
7. **确认点全标配：任何任务必须有计划确认 + diff 过目；R2+ 用 Plannotator。**
8. **R4 只有在真正适合并行时才使用 Multi-Agent / Worktree。**

最终形成：

> **Requirement → Assessment → Routing → Tool Check → Specification → Planning → Human Gate → Coding → Verification → Review → Delivery → Metrics**

这就是这套 **Claude Code + Superpowers + OpenSpec + Plannotator + R1/R2/R3/R4** 体系的完整落地闭环。
