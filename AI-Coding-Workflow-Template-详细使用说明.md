---
date created: 2026-08-25 11:54:49
date modified: 2026-08-25 12:04:44
---
# AI Coding Workflow Template 详细使用说明

> 版本：V1.0  
> 适用范围：Java / Spring Boot / Spring Cloud / DDD / 微服务项目  
> 核心工具：Claude Code + Superpowers + OpenSpec + Plannotator  
> 核心思想：根据需求复杂度自动选择 L0 / L1 / L2 / L3 Workflow

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
复杂度分析
 ↓
自动选择 L0/L1/L2/L3
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

# 2. L0 / L1 / L2 / L3 到底是什么

L0/L1/L2/L3 不是软件开发生命周期，也不是“项目阶段”。

它们代表：

> 根据当前需求复杂度选择不同强度的 AI Coding Workflow。

## L0

适用于：

- 明确的小 Bug
- 配置修改
- 文案修改
- 简单 SQL 修改
- 单字段调整
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

## L1

适用于：

- 小型 Feature
- 2~5 个文件的局部修改
- 普通业务逻辑
- 没有重大架构变化
- 风险较低

流程：

```text
需求
 ↓
分析
 ↓
代码探索
 ↓
轻量 Plan
 ↓
实现
 ↓
测试
 ↓
Self Review
```

主要工具：

```text
Superpowers
Claude Code
```

OpenSpec 和 Plannotator 可以根据情况使用。

---

## L2

适用于：

- 中型 Feature
- 跨模块
- 复杂业务规则
- 数据或架构有明显影响
- 中高风险业务

流程：

```text
需求
 ↓
Superpowers
 ↓
需求分析
 ↓
代码探索
 ↓
OpenSpec
 ↓
Design / Spec
 ↓
Implementation Plan
 ↓
Plannotator Plan Review
 ↓
人工批准
 ↓
Claude Code 实现
 ↓
测试
 ↓
Plannotator Code Review
 ↓
修复
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

## L3

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
需求
 ↓
完整代码库理解
 ↓
Superpowers
 ↓
Architecture Analysis
 ↓
OpenSpec
 ↓
Proposal
 ↓
Design
 ↓
Specs
 ↓
Tasks
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
并行实现
 ↓
单元测试
 ↓
集成测试
 ↓
Integration
 ↓
Plannotator Code Review
 ↓
最终验证
 ↓
Merge
 ↓
OpenSpec Archive
```

---

# 3. 四个工具分别负责什么

不要把四个工具理解成同一种东西。

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

> Agent Workflow 能力层

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

> 当前任务应该使用什么强度的 Workflow。

---

## OpenSpec

定位：

> Specification Source of Truth

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

# 4. 最终架构

```text
                         User Requirement
                                │
                                ▼
                      ┌────────────────────┐
                      │  Workflow Router   │
                      │                    │
                      │ Complexity Analysis│
                      └──────────┬─────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             ▼                   ▼                   ▼
            L0                  L1                  L2
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
                                                  L3
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
│   │   └── new-task.md
│   │
│   └── skills/
│       └── workflow-router/
│           ├── SKILL.md
│           ├── complexity-matrix.md
│           ├── routing-rules.md
│           │
│           └── workflows/
│               ├── L0.md
│               ├── L1.md
│               ├── L2.md
│               └── L3.md
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
3. 判断复杂度
4. 选择 L0/L1/L2/L3
5. 执行对应 Workflow

---

## workflow-router/SKILL.md

Workflow Router 核心 Skill。

负责定义：

- 如何分析需求
- 如何探索代码
- 如何评分
- 如何选择 Level
- 如何重新评估
- 如何自动升级

---

## complexity-matrix.md

复杂度评分标准。

当前使用：

```text
Scope
Business Complexity
Code Impact
Architecture Impact
Data Impact
Risk
Collaboration
```

每项 0~3 分。

---

## routing-rules.md

强制升级规则。

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

## workflows/L0~L3.md

分别定义四套执行流程。

Router 判断出 Level 后加载对应文件。

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
这是 L1
```

Router 自动判断。

---

# 11. L0 实际示例

需求：

```text
/new-task 修复 OrderService.getOrder() 的 NPE
```

Router 分析：

```text
Scope: 0
Business: 0
Code Impact: 0
Architecture: 0
Data: 0
Risk: 1
Collaboration: 0

Total: 1

Level: L0
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

# 12. L1 实际示例

需求：

```text
/new-task 给订单列表增加订单状态和创建时间范围筛选
```

可能判断：

```text
Scope: 1
Business: 1
Code Impact: 1
Architecture: 0
Data: 1
Risk: 1
Collaboration: 0

Total: 5

Level: L1
```

流程：

```text
Superpowers
 ↓
分析
 ↓
代码探索
 ↓
轻量 Plan
 ↓
实现
 ↓
测试
 ↓
Self Review
```

---

# 13. L2 实际示例

需求：

```text
/new-task 增加订单创建后30分钟自动取消功能
```

Router 可能判断：

```text
订单状态
定时任务
Redis/Kafka
库存释放
异步流程
```

即使代码修改范围不是特别大，也可能因为风险规则直接进入 L2。

流程：

```text
Superpowers
 ↓
OpenSpec
 ↓
Design
 ↓
Tasks
 ↓
Plan
 ↓
Plannotator Review
 ↓
人工批准
 ↓
Claude Code
 ↓
Tests
 ↓
Plannotator Code Review
 ↓
Final Verification
```

---

# 14. L3 实际示例

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
L3
```

因为：

- 微服务拆分
- 架构变化
- Kafka
- 服务边界变化
- 数据一致性
- 多服务联动

流程：

```text
Architecture Analysis
 ↓
Superpowers
 ↓
OpenSpec Proposal
 ↓
OpenSpec Design
 ↓
OpenSpec Specs
 ↓
OpenSpec Tasks
 ↓
Implementation Plan
 ↓
Plannotator
 ↓
人工批准
 ↓
任务拆分
 ↓
多 Agent（需要时）
 ↓
实现
 ↓
Integration
 ↓
Integration Test
 ↓
Plannotator Code Review
 ↓
Merge
 ↓
OpenSpec Archive
```

---

# 15. 为什么不能只根据需求文字判断

例如：

```text
增加订单一个字段
```

从文字看：

```text
L0/L1
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
L2
```

因此 Router 必须：

```text
需求分析
 +
代码库探索
 =
最终 Workflow
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

L1
 ↓
探索代码
 ↓
发现 Kafka
 ↓
发现跨服务
 ↓
发现数据一致性问题
 ↓
升级 L2
```

允许：

```text
L0 → L1 → L2 → L3
```

升级可以自动发生。

---

# 17. 为什么不建议自动降级

假设：

```text
初始 L2
```

后来发现：

```text
实际修改非常简单
```

可以建议：

```text
建议降级 L1。
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

---

# 18. 复杂度评分

当前模板采用：

```text
Scope                 0~3
Business Complexity   0~3
Code Impact           0~3
Architecture Impact   0~3
Data Impact           0~3
Risk                  0~3
Collaboration         0~2
```

最高：

```text
20 分
```

基础映射：

```text
0~3     → L0
4~7     → L1
8~13    → L2
14~20   → L3
```

但是：

> 总分不是唯一依据。

必须应用 Mandatory Upgrade Rules。

---

# 19. 强制升级规则

最低 L2：

```text
跨微服务
数据库 Schema 重要变化
数据迁移
Kafka 消息链路
Redis 分布式一致性
订单状态机
库存
支付
权限模型
跨服务事务
重要异步流程
核心 API 契约变化
```

直接 L3：

```text
微服务拆分
核心架构重构
大规模数据迁移
核心交易链路整体重构
多个服务结构性改造
需要多个 Agent 并行
多个隔离 Worktree
大规模模块边界重构
关键基础设施替换
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

所以不能：

```text
L0
```

至少：

```text
L2
```

这可以避免 AI 因为“修改文件少”而低估核心业务风险。

---

# 21. L2 中 OpenSpec 的作用

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

# 22. L2 中 Plannotator 的位置

推荐：

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

# 23. L3 中多 Agent 的使用原则

不要看到 L3 就强行多 Agent。

应该先判断：

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

# 24. Worktree 的使用

L3 如果需要并行开发，建议：

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

# 25. 如何处理用户强制指定 Level

用户可以说：

```text
/new-task L2：增加商品查询接口
```

Router 可以尊重。

但是：

如果用户要求：

```text
L0：修改支付逻辑
```

不能简单执行 L0。

应该提示：

```text
该需求涉及支付核心链路。

按照项目 Routing Rules：
最低安全等级为 L2。

如果强制执行 L0，将跳过：
- Specification
- Plan Review
- Code Review

是否继续？
```

---

# 26. 什么时候直接使用 Claude Code，不使用 /new-task

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

# 27. 建议的日常工作方式

每天开发时：

```text
进入项目
 ↓
claude
 ↓
/new-task <需求>
 ↓
Router 自动判断
 ↓
执行 Workflow
 ↓
测试
 ↓
Review
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

# 28. 新项目与旧项目的区别

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
L2/L3
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

# 29. 医药电商项目的特殊建议

对于订单、库存、支付、处方、退款等业务，可以进一步增强：

```text
routing-rules.md
```

例如：

```text
处方审核          → 至少 L2
处方购药          → 至少 L2
订单状态机        → 至少 L2
库存扣减          → 至少 L2
支付              → 至少 L2
退款              → 至少 L2
订单/库存一致性   → 至少 L2
GSP 核心规则      → 至少 L2
跨服务事务        → L2/L3
订单系统拆分      → L3
```

这样 Router 会更符合实际业务风险。

---

# 30. 如何逐步优化 Router

第一版不要追求完美。

建议运行：

```text
20~50 个真实需求
```

然后记录：

```text
Requirement
Initial Level
Final Level
Upgrade?
Review Reject?
Changed Files
Changed Modules
Development Time
Bug / Rework
```

例如：

```text
AI 判断 L1
实际 L2
```

出现很多次，就说明：

```text
complexity-matrix.md
```

需要调整。

例如：

```text
AI 判断 L2
实际 L3
```

很多次，就说明：

```text
routing-rules.md
```

缺少强制升级条件。

---

# 31. 建议建立 Workflow Metrics

长期可以记录：

| 指标 | 作用 |
|---|---|
| Initial Level | Router 初始判断 |
| Final Level | 实际最终等级 |
| Upgrade Rate | 评估是否经常低估 |
| Review Reject Rate | 方案质量 |
| Rework Rate | 返工率 |
| Changed Files | 修改规模 |
| Changed Modules | 影响范围 |
| Test Failure Rate | 测试稳定性 |
| Completion Time | 效率 |
| Bug Rate | 质量 |

最终可以形成：

```text
历史任务
 ↓
Workflow Metrics
 ↓
Router Rule 优化
 ↓
更准确的 Level 判断
```

---

# 32. V1 / V2 / V3 演进路线

## V1

当前模板：

```text
CLAUDE.md
+
Workflow Router Skill
+
Complexity Matrix
+
Routing Rules
+
L0~L3
+
/new-task
```

目标：

> 先跑起来。

---

## V2

增加：

```text
Codebase-aware Assessment
+
Dynamic Re-evaluation
+
更丰富的 Risk Rules
```

目标：

> 让 Level 判断更加准确。

---

## V3

增加：

```text
历史任务数据
+
Workflow Metrics
+
自动优化规则
+
项目级领域 Risk Profile
```

目标：

> 让 Router 从静态规则逐渐变成项目专属的 Workflow Intelligence。

---

# 33. 最终推荐的团队规范

团队成员只需要记住：

```text
新开发需求：

/new-task <需求>
```

不需要记：

```text
这个应该用 OpenSpec 吗？
这个应该用 Superpowers 吗？
这个要不要 Plannotator？
这个是 L1 还是 L2？
```

这些问题交给：

```text
Workflow Router
```

---

# 34. 最终完整闭环

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
                    Routing Rules
                           │
                           ▼
                  L0 / L1 / L2 / L3
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
       L0                 L1                 L2
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
                                             L3
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
                                      OpenSpec Archive
```

---

# 35. 最重要的设计原则

最后把整套体系浓缩成 8 条：

1. **需求复杂度决定 Workflow Level。**
2. **用户不需要手动判断 Level。**
3. **Workflow Router 是统一入口。**
4. **代码库探索后可以重新评估。**
5. **复杂度增加时自动升级。**
6. **高风险任务不能因为代码改动少而降级。**
7. **L2/L3 在 Coding 前增加人工 Plan Review。**
8. **L3 只有在真正适合并行时才使用 Multi-Agent。**

最终形成：

> **Requirement → Assessment → Routing → Specification → Planning → Human Gate → Coding → Verification → Review → Delivery**

这就是这套 **Claude Code + Superpowers + OpenSpec + Plannotator + L0/L1/L2/L3** 体系的完整落地闭环。
