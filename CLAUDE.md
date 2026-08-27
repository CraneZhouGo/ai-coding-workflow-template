# AI Coding Workflow Constitution — V3 Adaptive

## Purpose

本项目使用一个薄编排层，根据变更风险与影响范围自动选择 Fast、Standard 或 Governed 工作流，在 Token 成本、交付速度和工程可靠性之间取得平衡。

用户只需描述需求或调用 `/new-task`；不要要求用户手动挑选模式或逐个触发工具。

## Stable Rules

1. 新任务先读取 `.claude/project-profile.yaml`，再加载 `workflow-router` skill。
2. 路由以代码库证据和行为风险为准；文件数量、目录名和业务关键词不能单独决定模式。
3. 高风险触发器决定最低模式；范围、耦合和不确定性只能将模式升级。
4. 探索后、发现公共契约/数据/权限变化时、diff 明显扩大时和交付前重新评估。
5. Superpowers 负责开发方法，OpenSpec 负责持久化需求状态，Plannotator 负责人类决策，Claude Code 负责执行；不得复制彼此的产物。
6. 优先调用工具的原生 skill、命令和 Hook，不在本模板中复刻其内部流程。
7. 子代理用于隔离高噪声探索或独立工作；只有低耦合、可独立验证的任务才并行。
8. 工具缺失时说明缺少的能力和恢复方法；涉及降低保障级别时必须征得用户同意。
9. 完成声明必须附带实际执行的验证证据、Review 结果、未验证项和剩余风险。
10. 不自动提交、推送、部署或归档规格，除非用户已授权对应动作。

## Source of Truth

- 项目事实与验证命令：`.claude/project-profile.yaml`
- 路由与执行契约：`.claude/skills/workflow-router/`
- Standard/Governed 需求与变更状态：OpenSpec `openspec/`
- 实现计划：优先写入当前 OpenSpec change 的 tasks；不要另建重复计划
- 评审意见：Plannotator 当前会话与代码 diff

## Completion Report

最终答复应简洁包含：

- 初始模式、最终模式和关键证据
- 实际使用的 Superpowers、OpenSpec、Plannotator 节点
- 修改结果
- 测试、规格校验和 Review 结果
- 未验证事项、风险和需要用户执行的后续动作
