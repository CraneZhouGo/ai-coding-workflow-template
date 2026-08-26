---
description: 自动分析需求复杂度并选择 L0/L1/L2/L3 Workflow
---

# New Task

你现在负责处理一个新的开发需求。

## Step 1 — Workflow Assessment

必须先读取：

- `.claude/skills/workflow-router/SKILL.md`
- `.claude/skills/workflow-router/complexity-matrix.md`
- `.claude/skills/workflow-router/routing-rules.md`

然后：

1. 理解用户需求。
2. 结合当前代码库进行必要的探索。
3. 计算复杂度。
4. 判断最低安全 Workflow Level。
5. 输出简短的 Assessment。
6. 加载对应的 L0/L1/L2/L3 Workflow。

## Step 2 — Execute Selected Workflow

严格执行对应 Workflow 文件中的流程。

## Step 3 — Re-evaluation

在真正修改代码前，如果发现以下任一情况：

- 影响范围扩大
- 跨模块
- 跨服务
- 数据结构变化
- 核心业务规则变化
- 高风险链路
- 需要多 Agent
- 架构方案发生变化

重新评估 Workflow Level。

如果需要升级，立即升级并执行更高等级 Workflow。

## Step 4 — Final Verification

完成后必须报告：

- Selected Level
- Final Level
- Changed Files
- Tests
- Verification Result
- Remaining Risks
