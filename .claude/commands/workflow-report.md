---
description: 汇总 JSONL Workflow Metrics，输出档位矩阵、返工、能力降级和有样本约束的调参建议
---

# Workflow Report v2.1

## 首选执行

```text
python scripts/workflow_report.py --metrics .claude/workflow-metrics/tasks.jsonl --minimum-samples 20
```

若项目画像配置了其他 `metrics_path` 或 `minimum_samples_for_tuning`，使用项目画像值。

## 输出要求

1. 总任务数、completed/blocked。
2. Initial → Final 档位矩阵和升级率。
3. 各档平均交付时间、人工等待时间和返工率。
4. 升级任务中最常见的高分维度和语义红旗。
5. Capability degradation 与评审问题分布。
6. escaped defect 率（只统计已知 true/false，排除 null）。
7. 样本不足时明确写 `insufficient sample for tuning`，不得建议调整阈值。

脚本不可用时可以直接读取 JSONL 生成同等报告，但不能退回旧 Markdown Metrics 格式。
