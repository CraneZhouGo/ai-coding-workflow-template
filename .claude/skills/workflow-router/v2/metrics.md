# Workflow Metrics v2.1

每次任务完成后，向 `.claude/workflow-metrics/tasks.jsonl` 追加一个 UTF-8 JSON 对象。每行一条记录，不使用 Markdown 表格。

## 必需字段

| 字段 | 说明 |
|---|---|
| schema_version | 固定为 `1` |
| timestamp | ISO-8601 完成时间 |
| task_id / task_summary | 稳定标识和需求简述 |
| initial_tier / final_tier | 初始与最终风险档 |
| initial_score / final_score | 0~36 |
| dimensions | 7 个最终维度分数 |
| semantic_red_flags | 命中的语义红旗名称 |
| required_gates | 实际要求的可组合门控 |
| delivery_profile | agents/worktrees/rollout/ownership |
| capability_degradations | 能力、替代路径、批准状态 |
| changed_files / changed_modules | 实际影响范围 |
| tests | 执行的命令、结果和未执行原因 |
| plan_review_rounds | 计划评审往返次数 |
| code_review_findings | critical/high/medium/low 数量 |
| rework | 是否发生返工 |
| duration_minutes / human_wait_minutes | 执行耗时与人工等待时间 |
| escaped_defect | 已知交付后缺陷；未知用 `null` |

完整约束见 `metrics-schema.json`。

## 写入规则

1. 只追加，不改写历史记录。
2. 不记录秘密、个人数据、完整需求正文或代码内容。
3. 升级时保留 initial 与 final 评分；原因写入 `reassessment_reasons`。
4. 没有执行的测试必须记录原因，不能省略字段。
5. Capability Check 的所有 degraded 状态必须写入。
6. 若任务中断，写入 `outcome: "blocked"`；成功完成写入 `outcome: "completed"`。

推荐先生成一个临时 JSON 对象，再通过以下命令校验并追加：

```text
python scripts/record_workflow_metric.py --record <record.json>
```

可以先使用 `--dry-run` 验证。不要通过字符串拼接直接修改 JSONL。

## 报告与调参纪律

- 使用 `python scripts/workflow_report.py` 或 `/workflow-report`。
- 样本少于项目画像的 `minimum_samples_for_tuning` 时只展示统计，不建议调整权重或阈值。
- 调参应优先看升级发生阶段、维度分布、红旗命中和 escaped defects，不能只看升级率。
