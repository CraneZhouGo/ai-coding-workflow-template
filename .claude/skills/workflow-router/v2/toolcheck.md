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
