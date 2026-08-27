---
name: workflow-router
description: 根据行为风险、影响范围和不确定性，把编码任务路由到 Fast、Standard 或 Governed，并编排 Superpowers、OpenSpec 与 Plannotator。处理新功能、Bug、重构、迁移和基础设施变更时使用。
---

# Workflow Router — V3 Adaptive

本 skill 是薄编排层。它选择工具和关卡，但不复制 Superpowers、OpenSpec 或 Plannotator 的内部方法。

## 1. Build the evidence set

先读 `.claude/project-profile.yaml`。从最窄范围开始探索，只收集路由所需事实：

- 变更后的用户可观察行为和验收条件
- 直接修改范围与消费者
- 公共 API、事件、Schema、权限和关键业务语义
- 回滚难度、发布协调和当前未知项

不要在路由前扫描整个仓库。探索输出应是证据，不是长篇仓库摘要。

## 2. Select the mode

读取 `ROUTING.md`。先检查 Governed 风险触发器，再检查 Fast 的全部准入条件；其余任务进入 Standard。

```text
if any governed trigger: governed
else if every fast condition: fast
else: standard
```

不计算加权总分。未知事实不能当作低风险；先按 Standard 继续定向探索，必要时升级。

## 3. Check capabilities

按所选模式确认能力真实可用：

- Superpowers：相关 skills 可被发现和加载。
- OpenSpec：Standard/Governed 时 `openspec` 已初始化，原生 OPSX skills/commands 可用。
- Plannotator：需要评审时插件/Hook 与 `plannotator` 能力可用。
- 项目验证：profile 中对应命令可运行，或能从仓库发现可信替代命令。

优先调用原生能力。不要复制 OpenSpec 模板、Superpowers 步骤或 Plannotator Hook 配置。

若能力缺失，先给出恢复方法。只有会降低保障级别的降级才需要用户确认。

## 4. Execute the playbook

读取 `PLAYBOOKS.md`，严格执行对应模式。Superpowers 的分析与计划结论直接写入当前 OpenSpec change（若启用），不再创建第二套长期文档。

## 5. Re-evaluate

在以下时点重新路由：

- 初次代码探索完成后
- 发现公共契约、Schema、数据迁移、权限或关键业务语义变化时
- 修改超出原模块或出现新的消费者时
- 实现方案发生实质变化时
- 最终交付前

升级立即生效。降级只允许在新证据消除风险后发生，并在 Route Card 中说明移除的关卡。

## 6. Finish with evidence

运行实际验证，检查最终 diff，完成当前模式要求的规格校验和评审。不得把计划执行的检查写成已经通过。
