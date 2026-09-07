---
name: new-task
description: 识别意图并通过确定性 Router 连续处理一个开发请求；修改类请求自动组合任务方法、Fast/Standard/Governed 保障和专项 Gate，只在真实 Gate 或阻断条件下暂停。
argument-hint: "<需求>"
disable-model-invocation: true
---

# New Task

处理 `$ARGUMENTS`；参数为空时使用用户当前需求。

调用本 skill 即授权当前项目内的读取、修改、非破坏性命令、构建、测试和当前 OpenSpec change 的本地生命周期。它不授权提交、推送、部署、秘密访问或破坏性动作。

1. 读取 `CLAUDE.md` 和 `.claude/project-profile.yaml`。
2. 显式加载 `workflow-router` skill；确认项目画像 ready、Hook 已幂等安装，并先查找可恢复的 `workflow-state.json`。
3. 对新请求提取结构化 route facts，必须调用 `.claude/scripts/workflow-runtime.mjs route`；不得手工决定模式或节点。输出 Route Card，它是状态通知，不是审批请求：

```text
intent: explain | review | diagnose-only | plan-only | change
task_type: feature | bug | refactor | upgrade-config | migration-infrastructure | maintenance | N/A
mode: fast | standard | governed | N/A
specialized_gates: data | security | contract | infrastructure | release | observability | none
workflow: Core Spine + 实际 Task Method + 实际 Risk Safeguards + 实际 Specialized Gates
route_fingerprint: sha256
planning_depth: concise | normal | extensive | N/A
validation_scope: targeted | affected | full | N/A
resume: new | <change-id>:<next-node>
human_gates: none | spec-diff-review | spec-diff-review+code-diff-review
```

4. 非 `change` 意图进入只读分支并直接完成；`diagnose-only` 只能给根因与证据，`plan-only` 只能给计划，均不得修改项目。
5. `change` 在同一响应中立即进入第一个未完成节点。禁止询问“是否继续”“是否采用该模式”或逐节点确认。
6. 使用 runtime `compose/init-state/next/transition` 冻结并推进有序工作流；每个节点必须有证据，只有 `CLAUDE.md` Autonomy Contract 列出的情况可以暂停。
7. Standard/Governed 的 S-DF1 调用 runtime `capture-spec-diff`；S-HG1 显式调用 `/plannotator-review` 的 `uncommitted` 视图，并用 runtime `review --type spec` 校验实际展示文件。不得手动拼接文档正文；存在用户原有修改时必须先进入隔离 worktree。
8. 实施阶段调用 `/opsx:apply <change-id>` 或 `openspec-apply-change` skill；不得尝试不存在的终端命令 `openspec apply`。原生入口不可用时，使用 `openspec instructions apply --change <change-id> --json` 获取官方指令。
9. 每完成节点、进入或退出人工 Gate、重路由和上下文压缩时更新 `workflow-state.json`；Hook 阻止规划阶段越界编辑和未完成时提前停止。
10. Standard/Governed 最终运行参数化验证、Review、`openspec validate <change-id> --strict --no-interactive` 和 `openspec archive <change-id> --yes`；只有 runtime `archive-complete` 成功后才能报告 completed。
