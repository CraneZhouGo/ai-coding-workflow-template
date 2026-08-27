---
name: new-task
description: 识别意图并连续处理一个开发请求；修改类请求自动组合任务方法、Fast/Standard/Governed 保障和专项 Gate。只在计划内人工 Gate、真实分歧、能力降级或外部/破坏性动作前暂停。
argument-hint: "<需求>"
disable-model-invocation: true
---

# New Task

处理 `$ARGUMENTS`；参数为空时使用用户当前需求。

调用本 skill 即授权当前项目内的读取、修改、非破坏性命令、构建、测试和当前 OpenSpec change 的本地生命周期。它不授权提交、推送、部署、秘密访问或破坏性动作。

1. 读取 `CLAUDE.md` 和 `.claude/project-profile.yaml`。
2. 显式加载 `workflow-router` skill；先查找可恢复的 `workflow-state.yaml`，再对新请求分类。
3. 输出 Route Card；它是状态通知，不是审批请求：

```text
intent: explain | review | diagnose-only | plan-only | change
task_type: feature | bug | refactor | upgrade-config | migration-infrastructure | maintenance | N/A
mode: fast | standard | governed | N/A
specialized_gates: data | security | contract | infrastructure | release | observability | none
workflow: Core Spine + 实际 Task Method + 实际 Risk Safeguards + 实际 Specialized Gates
resume: new | <change-id>:<next-node>
human_gates: none | plan-review | plan-review+code-review
```

4. 非 `change` 意图进入只读分支并直接完成；`diagnose-only` 只能给根因与证据，`plan-only` 只能给计划，均不得修改项目。
5. `change` 在同一响应中立即进入第一个未完成节点。禁止询问“是否继续”“是否采用该模式”或逐节点确认。
6. 按组合后的有序工作流连续执行；只有 `CLAUDE.md` Autonomy Contract 列出的情况可以暂停。
7. Standard/Governed 每完成节点、进入或退出人工 Gate 时更新 OpenSpec change 内的 `workflow-state.yaml`；面向用户只汇报关键进展。
8. 最终按 Completion Report 汇报，并将状态标为 completed 后 archive 当前 change。
