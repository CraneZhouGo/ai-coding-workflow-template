# Native Tool Playbooks

工具职责固定：Superpowers 管方法，OpenSpec 管持久化意图，Plannotator 管人类决策，Claude Code 管代码与命令执行。

## Node map

| 节点 | Fast | Standard | Governed |
|---|---|---|---|
| 探索与推理 | Claude 定向探索；加载适用的 Superpowers debugging/TDD skill | Superpowers brainstorming（存在取舍时）+ 定向影响分析 | Superpowers brainstorming + 隔离子代理做架构/安全/数据影响分析 |
| 持久规格 | 无；已有 OpenSpec change 时保持同步 | OpenSpec 原生 `propose`，只维护一个 change | OpenSpec `explore`（不确定时）→ `propose`，完整表达风险、迁移与发布约束 |
| 实现计划 | 对话内 1–3 步，不落盘 | Superpowers writing-plans 的结论写入 OpenSpec tasks | 详细 tasks/依赖关系写入 OpenSpec；必要时标注并行边界与收敛点 |
| Plan Review | 无 | Plannotator Plan Review Hook，批准后实现 | Plannotator Plan Review；高风险决策未批准不得实现 |
| 实现 | 最小 diff；行为变化使用 TDD | Superpowers TDD/systematic-debugging + Claude | TDD；独立高噪声任务用子代理，独立实现批次才用 worktree |
| 验证 | 最相关测试 + diff 自审 | 单元/构建/相关集成 + `openspec validate` + verification-before-completion | 单元、集成、契约及适用的迁移/回滚/安全/发布验证 + OpenSpec 校验 |
| Code Review | AI diff 自审 | AI spec-compliance + code-quality review；用户可直接检查 diff | Plannotator `/plannotator-review` + 必要的安全/数据/架构专项 review |
| 收尾 | 汇报证据 | 经授权后 OpenSpec `archive`；汇报证据 | 所有阻断项解决且经授权后 archive；记录上线与观察条件 |

## Fast

1. 确认满足全部 Fast 条件并输出 Route Card。
2. 只读取目标文件、直接依赖和直接测试。
3. Bug 使用 Superpowers systematic-debugging；行为变化使用 TDD；纯文档/机械修改不强制测试先行。
4. 实施最小修改，运行最相关验证并检查完整 diff。
5. 若出现设计取舍、跨模块影响或风险触发器，立即升级。

Token 约束：不创建规格或计划文件，不做全库扫描，不启动评审 UI。

## Standard

1. 明确 Goal、Acceptance Criteria、Constraints 和 Non-goals；有真实取舍时使用 Superpowers brainstorming。
2. 调用 OpenSpec 当前原生 `propose` 能力。让 OpenSpec schema 决定工件，不手工仿造旧版 proposal/design/tasks 流程。
3. 使用 Superpowers writing-plans 细化同一 OpenSpec change 的 tasks，不另建重复计划。
4. 进入 Claude Code Plan Mode；由 Plannotator Hook 打开 Plan Review。处理反馈并获得批准。
5. 调用 OpenSpec `apply`，按 Superpowers TDD/systematic-debugging 实施。
6. 执行相关测试、构建和 `openspec validate <change>`；使用 verification-before-completion 检查声明与证据。
7. 做 spec-compliance 与 code-quality 两遍 AI review。用户已授权收尾时再 archive。

Token 约束：探索限制在相关模块和直接消费者；一个需求只保留一个 OpenSpec change；评审反馈只传递决策与阻断项。

## Governed

1. 补齐 Goal、Non-goals、失败模式、消费者、数据/契约影响、回滚、观测和发布约束。
2. 不确定时先调用 OpenSpec `explore`，稳定后调用 `propose`；所有长期结论进入同一个 change。
3. 使用隔离子代理调查高噪声领域，只把证据摘要带回主上下文。并行只用于无共享状态且可独立验证的任务。
4. Superpowers writing-plans 将任务、依赖、迁移、回滚和发布检查写入 OpenSpec。
5. Plannotator Plan Review 批准规格、实施顺序和风险控制后才开始编码。
6. 调用 OpenSpec `apply`；使用 TDD，必要时在隔离 worktree 执行独立批次，并在明确收敛点集成。
7. 运行项目验证矩阵及适用的迁移 dry-run、回滚、契约、安全和发布演练；校验 OpenSpec。
8. 运行 Plannotator `/plannotator-review`。阻断问题修复后重新验证和 review。
9. 仅在授权且交付条件满足后 archive；汇报 feature flag、灰度、监控、告警、观察窗口和停止条件。

## Native capability rule

- OpenSpec 命令名称以当前安装版本生成的 OPSX skill/command 为准；不要把模板文档当作 OpenSpec 实现。
- Plannotator Plan Review 由 Plan Mode Hook 自动触发；Code Review 使用其原生 review 能力。
- Superpowers skill 的具体步骤由已安装版本提供；本模板只决定何时需要哪类能力。
