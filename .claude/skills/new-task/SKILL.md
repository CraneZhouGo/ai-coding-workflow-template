---
name: new-task
description: 统一启动一个编码任务，自动选择 Fast、Standard 或 Governed 工作流并执行。用户描述新需求、修复、重构或调用 /new-task 时使用。
argument-hint: "<需求>"
disable-model-invocation: true
---

# New Task

处理 `$ARGUMENTS`；如果参数为空，则以用户当前消息作为需求。

1. 读取项目根目录的 `CLAUDE.md` 和 `.claude/project-profile.yaml`。
2. 加载 `workflow-router` skill，由它完成证据探索、模式选择、工具检查、执行和重新评估。
3. 在修改前只输出一份简短 Route Card：

```text
mode: fast | standard | governed
why: 1-3 条代码库或需求证据
durable_spec: none | openspec
human_gates: none | plan | plan+code
next: 紧接着执行的动作
```

4. 除非存在需要用户决策的真实分歧，否则直接继续，不让用户再次选择模式或确认路由。
5. 最终按 `CLAUDE.md` 的 Completion Report 汇报。
