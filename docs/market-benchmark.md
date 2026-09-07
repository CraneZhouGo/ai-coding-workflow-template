# 2026 AI Coding Workflow Benchmark

调研日期：2026-09-06。只采用产品官方文档或官方仓库；目标是筛选能降低流程漂移的机制，不是复制一个全功能配置仓库。

## 市场信号与取舍

| 市场实践 | 官方依据 | V3.3 决策 |
|---|---|---|
| SessionStart、PreToolUse、PreCompact、Stop 可约束完整 Agent 生命周期 | [Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide)、[hooks reference](https://code.claude.com/docs/en/hooks) | 增加四个轻量 Hook，恢复状态、阻止规划期越界编辑、压缩前保存、阻止提前结束 |
| Everything Claude Code 用 Hooks、agents、skills、rules 和 evals 构成持续反馈系统 | [Everything Claude Code](https://github.com/WorldFlowAI/everything-claude-code)、[hooks.json](https://github.com/WorldFlowAI/everything-claude-code/blob/main/hooks/hooks.json) | 采用 lifecycle、选择性 specialists 和行为 eval；不整体搬入其语言规则、MCP、tmux 与每次编辑检查 |
| 方法论应按问题选择，不应把所有技能串成每次必经链 | [Superpowers](https://github.com/obra/superpowers)、[brainstorming skill](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md) | Feature 最低 Standard 并执行 brainstorming；Bug、重构、升级、迁移各走自己的 Method |
| OpenSpec Agent 命令与 CLI 职责不同 | [OpenSpec commands](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md)、[OpenSpec CLI](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md) | `/opsx:apply`/apply-change skill 进入实施；CLI 仅用于 instructions/status/validate/archive，归档使用 `--yes` |
| Plannotator 默认代码 Review 是 since-base，Spec Review 需要显式 uncommitted | [Plannotator](https://github.com/backnotprop/plannotator)、[AGENTS.md](https://github.com/backnotprop/plannotator/blob/main/AGENTS.md) | Spec Gate 校验 uncommitted 实际文件列表；Governed Code Gate 使用 since-base |
| Evals 应验证行为闭环，而不是只验证提示词存在 | [Everything Claude Code eval harness](https://github.com/WorldFlowAI/everything-claude-code/tree/main/skills/eval-harness) | Python 评测调用同一个 Node Router；单元测试执行状态迁移、Hook、Review 范围与 hash drift |

## 架构结论

### 三种模式足够，但模式不承载全部细节

Fast、Standard、Governed 只表示风险保障下限。Task Type 选择开发方法，Specialized Gates 添加领域证据，派生 execution policy 调整计划、验证、隔离、Review 和执行策略。这样既能覆盖日常开发，也不会因添加第四、第五个模式造成组合爆炸。

### 确定性控制面比更长提示词有效

AI 对自然语言和代码语义做判断，runtime 对枚举、优先级、节点排序、hash 和状态迁移做机械决策。相同输入可重放，非法跳转可拒绝，长上下文压缩后也可以从状态文件恢复。

### 生命周期 Hook 必须轻量

Hook 只做毫秒级状态检查，不运行全项目测试、不自动格式化、不阻止 OpenSpec Markdown、不要求 tmux。完整验证仍是明确的 verification 节点，命令来自项目画像。

### 专项 Agent 按触发器使用

architect、security、e2e 或 build-error specialist 只在相应风险或失败出现时启用。Planner、TDD、debugging 和 code review 已由工作流节点、Superpowers 与统一 Review 覆盖，不重复启动同义 Agent。

### 人工注意力只用于真实决定

Route Card、内部节点、模式升级和 OpenSpec 子流程返回不暂停。Standard 只有 OpenSpec Spec Diff Review；Governed 再增加 Code Diff Review。宿主权限确认和外部高影响动作仍独立遵守安全边界。

## 明确不采用

- Everything Claude Code 的完整 agents/commands/rules/MCP 集合：会把与项目无关的上下文和维护成本带入业务仓库。
- 每次编辑自动跑 formatter/typecheck：延迟高，且与 verification 节点重复。
- 固定 80% 覆盖率或固定 npm/TypeScript 命令：不同项目不可通用。
- 强制 tmux、会话日志和持续学习数据库：不是流程正确性的必要条件。
- 默认并行多 Agent：只有低耦合且可独立验证的 Governed 子任务才值得并行。
- 更多固定风险模式：专项 Gate 和 execution policy 已能表达细节。
