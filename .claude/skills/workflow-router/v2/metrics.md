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
