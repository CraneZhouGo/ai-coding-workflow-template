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
```text
Workflow Report
---------------
total tasks: 12
tier distribution (final): R1=3, R2=4, R3=4, R4=1
upgrade rate: 33% (4/12)
rework rate: 17%
suggestion: upgrade rate high → review weighted score thresholds
```
