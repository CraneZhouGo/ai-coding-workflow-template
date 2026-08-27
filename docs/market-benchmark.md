# 2026 AI Coding Workflow Benchmark

调研日期：2026-08-27。只采用产品官方文档或官方仓库，目的不是堆砌功能，而是明确模板应承担的组合职责。

## Market signals

| 市场实践 | 官方依据 | V3.2.1 决策 |
|---|---|---|
| 稳定约定常驻，可复用流程按需加载 | [Claude Code extension architecture](https://code.claude.com/docs/en/features-overview)、[OpenAI Codex skills](https://developers.openai.com/codex/build-skills) | 宪法保持短小，Router 按任务加载 routing/playbooks |
| 方法论按任务问题选择技能，而不是把所有技能串成每次必经链 | [Superpowers official repository](https://github.com/obra/superpowers) | Task Type 分别选择 brainstorming、systematic-debugging、TDD、planning 和 verification |
| OpenSpec CLI 是引擎，slash command/skill 是 Agent steering wheel | [OpenSpec commands](https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md)、[OpenSpec CLI](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md) | `/opsx:apply`/apply-change skill 负责实施入口；CLI 只用 instructions/status/validate/archive |
| Plan Review Hook 只读取 `tool_input.plan`，代码评审是独立 diff Gate | [Plannotator architecture](https://github.com/backnotprop/plannotator/blob/main/AGENTS.md) | Gate 前动态嵌入全部 change 文档；Standard 保留一个 Plan Gate，Governed 增加 Code Gate |
| 子代理的主要价值是上下文隔离 | [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)、[OpenAI Codex subagents](https://developers.openai.com/codex/agent-configuration/subagents) | 仅 Governed 高噪声调查或低耦合执行使用子代理 |
| 本地范围内工作应自主推进，高影响外部动作才确认 | [OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model) | Route Card 和内部节点不确认，保留明确人类 Gate 与授权边界 |
| 项目规则应按范围加载，不让无关上下文常驻 | [Cursor project rules](https://docs.cursor.com/context/rules-for-ai)、[Kiro steering](https://kiro.dev/docs/steering/) | 通用模板只保留项目画像，领域规则在业务项目按真实目录增加 |

## Architecture consequences

### Orthogonal routing instead of bigger modes

模式数量增加会产生组合爆炸，固定模式链又会把 Feature 方法错误套给 Bug。V3.2.1 保留三种风险模式，但把 Intent、Task Type 和 Specialized Gates 独立出来。新增风险通常只需增加 Gate，新增任务形态只需增加 Method module。

### Thin orchestration with explicit handoffs

OpenSpec、Superpowers 和 Plannotator 都在快速迭代。模板只固定职责、选择条件、交接点、状态和完成证据，具体 skill 内部步骤由安装版本负责。项目级 Adapter Contract 合并重复批准、文件和自动提交边界。

“调用工具”必须对应真实入口：模板不得把不存在的 CLI 命令写成节点，也不得把 Router 自己开始编辑当成 OpenSpec apply 已执行。Plan Review 也不得依赖 Plannotator 自动读取文件；完整输入由 Router 明确装配。

### Durable state without a workflow platform

长任务会跨越上下文压缩和人工评审。把最小节点账本放进当前 OpenSpec change，既能续跑，又不引入数据库、指标平台或业务包脚本。完成后随 change 一起归档。

### Risk floors instead of scores

高风险事实直接设置 Governed 下限；Fast 必须证明全部准入条件；其余修改默认 Standard。任务方法不会降低这个风险下限。

### Human attention is scarce

工作流只保留真正需要决定的 Plannotator Gate。宿主安全权限仍独立存在，不能被工作流宽泛绕过。

### Evals stay outside business runtime

维护仓库用案例校准 Intent、Task Type 和 Risk Mode，用测试校准组合顺序与状态恢复。分发包仍只有 6 个运行时文件。

## Deliberately excluded

- 第四或更多固定模式：专项 Gate 比复制整条流程更可扩展。
- 默认 Metrics 平台：没有规模与决策闭环时只增加维护成本。
- 自定义 OpenSpec schema：状态使用 workflow-owned sidecar，不劫持 OpenSpec 工件格式。
- 默认多 Agent：并行会增加协调、合并和 Token 成本。
- 通用领域 rules 和安全 Hook：应在业务项目接入时按真实边界配置。
