# V3 Adaptive Architecture Decision

## Problem

前一版使用四档加权评分并在模板内描述三项工具的详细流程。它看似完整，但有三类长期成本：评分主观却表现为精确、同一计划在多处重复、工具升级后模板命令迅速过时。

## Decision

采用三层结构：

1. `CLAUDE.md`：只放跨任务稳定约束。
2. `new-task` 与 `workflow-router` skills：按需加载入口、路由和编排。
3. OpenSpec、Superpowers、Plannotator：各自拥有规格、方法和人工决策的实现细节。

路由采用三模式：Fast、Standard、Governed。风险触发器设置 Governed 下限；Fast 使用全条件准入；Standard 是默认安全网。

## Tool handoffs

```text
User request
  -> Router evidence + mode
  -> Superpowers method
  -> OpenSpec durable state (Standard/Governed)
  -> Plannotator decision gate
  -> Claude implementation + verification
  -> OpenSpec validation/archive when authorized
```

Superpowers 的计划结论进入 OpenSpec tasks；Plannotator 评审同一份计划和实际 diff；Claude Code 不创建额外规格副本。

## Token model

- 常驻：短 `CLAUDE.md` 与项目画像。
- 按需：Router 的 routing/playbook references。
- 隔离：Governed 的高噪声探索由子代理执行。
- 持久化：只有 Standard/Governed 建立 OpenSpec change。
- 人工反馈：只返回决策和阻断项。

## Verification

模板结构由 validator 检查；发行包字节可复现；校准案例验证关键路由不变量，尤其是“高风险覆盖 Fast 外形”和“未知信息默认 Standard”。
