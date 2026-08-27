# Capability Check v2.1

检查实际能力，不以“目录存在”代替“工具可用”。读取 `.claude/project-profile.yaml` 获取项目命令和降级策略。

## 状态

- `available`：能力可调用且基本健康检查通过。
- `degraded`：首选能力不可用，但存在已定义的安全替代路径。
- `missing`：没有满足 required gate 的可信路径，必须暂停。

## 检查项

| 能力 | 探测方式 | 允许降级 |
|---|---|---|
| OpenSpec | 命令可执行、版本可读取、项目已初始化、status/verify 可运行 | R2 可使用单一紧凑变更记录；R3/R4 须明确批准 |
| Plan Review | Plannotator 入口可调用并能读取计划产物 | R2 可终端人工确认并记录；R3/R4 须明确批准 |
| Code Review | Plannotator 入口可调用并能读取目标 diff | R2 可 AI 自审 + 人工 diff 过目；R3/R4 须明确批准 |
| Git | 仓库、HEAD、工作区状态可读取 | 无 Git 时禁用 worktree/自动 diff，必须说明 |
| Worktree | `git worktree list` 可用，存在可用基线提交 | 退回单 Agent 串行，不改变风险档 |
| Build/Test | 项目画像中的命令存在且可执行 | 缺失时不得声称对应验证已完成 |
| Migration | dry-run、备份、前后校验、回滚命令已定义 | required data gate 下不允许静默降级 |
| Delivery | feature flag/灰度/回滚/监控能力与负责人明确 | R4 或协调发布时不允许静默降级 |

## 输出

```text
Capability Check
----------------
available: [...]
degraded: [{capability, fallback, approval}]
missing: [{capability, blocked_gate, action}]
decision: proceed | proceed_degraded | blocked
```

所有 `degraded` 和 `missing` 结果都写入最终报告与 Metrics。
