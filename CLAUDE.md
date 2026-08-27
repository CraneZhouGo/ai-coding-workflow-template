# AI Coding Workflow Constitution — V3.2.2 Composable

## Purpose

本项目先识别用户意图，再按任务类型选择 Superpowers 方法、按风险选择 Fast/Standard/Governed 保障，并按专项风险叠加 Gate。

最终工作流不是固定清单，而是：

```text
Core Spine + Task Method + Risk Safeguards + Specialized Gates
```

用户只需描述需求或调用 `/new-task`。Route Card 是通知，内部节点和模式升级不是审批事项。

## Autonomy Contract

一次 `/new-task` 或明确的修改/构建/修复请求，授权在当前项目内连续执行：读取与搜索、创建/修改文件、运行非破坏性命令、构建与测试，以及当前 OpenSpec change 的 propose、apply、validate、状态更新和 archive。

以下动作不需要再次确认：

- 意图、任务类型、风险模式、专项 Gate 和节点组合
- Route Card、模式自动升级和内部节点推进
- Superpowers、OpenSpec 与 Claude Code 的内部交接
- 本地实现、测试、静态检查、diff review 和 OpenSpec 生命周期
- 已批准计划范围内的修复、重新验证和状态恢复

只在以下情况暂停：

- 存在会实质改变结果且无法从需求或代码库证据消除的分歧
- 到达当前模式预定的 Plannotator 人工 Gate
- 必需能力缺失且替代方案会降低保障
- 多个未完成 OpenSpec change 均可能对应当前请求，无法可靠恢复
- 需要外部写入、秘密、破坏性动作、提交、推送或部署

不得在 Route Card 后询问“是否继续/是否采用此流程”，不得逐节点请求许可。宿主权限弹窗不是工作流 Gate，也不得用宽泛授权绕过。

## Stable Rules

1. 新任务先读取 `.claude/project-profile.yaml`，再加载 `workflow-router` skill。
2. 路由顺序固定为 `Intent → Task Type → Risk Mode → Specialized Gates → Ordered Execution`。
3. `explain | review | diagnose-only | plan-only` 默认保持只读；只有 `change` 进入修改主链。诊断请求不得擅自修复。
4. 风险模式和任务类型正交：模式决定保障强度，任务类型决定方法节点。文件数量、目录名和关键词不能单独决定任一项。
5. 高风险触发器决定 Governed 下限；Fast 必须满足全部准入条件；其余修改默认 Standard。
6. Feature 使用 brainstorming/spec/TDD；Bug 使用 systematic-debugging/根因证据/回归测试；Refactor、Upgrade/Config、Migration/Infrastructure 和 Maintenance 使用各自方法，不强制套用 Feature 链。
7. Standard/Governed 必须执行组合后所有 REQUIRED 节点；不适用节点记录 `N/A + evidence`，不能静默跳过。
8. Superpowers 管方法，OpenSpec 管持久化需求与流程状态，Plannotator 管人类决策，Claude Code 管执行；不得复制长期产物。
9. 按 `PLAYBOOKS.md` 的 Integration Adapter Contract 整合工具：保留原生方法，但重复审批、独立设计/计划文件和自动提交由 Plannotator Gate、OpenSpec 单一事实源和本项目授权边界替代。
10. OpenSpec 实施入口必须调用宿主生成的 `/opsx:apply <change-id>` 或 `openspec-apply-change` skill；终端不存在 `openspec apply`。只有原生入口不可用时，才使用 `openspec instructions apply --change <change-id> --json` 获取官方实施指令。
11. Standard/Governed 的规划 Gate 使用 `/plannotator-review` 打开 OpenSpec Spec Diff Review，直接展示当前 change 的新增/修改文件；禁止通过 ExitPlanMode 手动拼接全文。Gate 前必须确认工作区 diff 只包含 `openspec/changes/<change-id>/**`，否则先隔离或消除无关变化。
12. 子 skill/command 的 `stop`、`ready for next` 或完成消息只把控制权交还 Router；Router 自动持久化状态并调用下一节点。
13. Standard/Governed 在 `openspec/changes/<change-id>/workflow-state.yaml` 保存节点账本、Git review base 和已评审规划工件哈希；新回合优先恢复最早未完成 REQUIRED 节点。Spec Diff Review 后规划工件哈希变化会使批准失效并重新打开文件 diff。
14. 探索完成、发现公共契约/数据/权限/关键语义变化、diff 扩大和交付前重新路由；升级不需要确认。
15. 子代理用于隔离高噪声探索；只有低耦合且可独立验证的任务才并行。
16. 完成声明必须附实际验证、规格与状态文件结果、Review 结果、未验证项和剩余风险。必须先 validate/review 通过，再将状态设为 completed，最后 archive。
17. `/new-task` 授权本地 OpenSpec archive，但不授权 Git 提交、推送、部署或破坏性清理。

## Source of Truth

- 项目事实与验证命令：`.claude/project-profile.yaml`
- 路由、组合规则和状态合同：`.claude/skills/workflow-router/`
- Standard/Governed 的需求、设计、任务和状态：当前 OpenSpec change
- 人工评审决定：Plannotator 会话
- 实现事实：代码、测试结果和最终 diff

## Completion Report

- intent、task type、initial/final mode、specialized gates 与证据
- 实际组合出的 ordered workflow
- 节点状态：`done | N/A + evidence | blocked`
- Superpowers、OpenSpec、Plannotator 的实际调用
- 修改、测试、规格校验、状态归档和 Review 结果
- 未验证项、剩余风险和需要用户授权的外部动作
