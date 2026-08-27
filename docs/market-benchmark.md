# 2026 AI Coding Workflow Benchmark

调研日期：2026-08-27。只采用产品官方文档或官方仓库，目的不是堆砌功能，而是确定本模板应承担和不应承担的职责。

## Market signals

| 市场实践 | 官方依据 | V3 决策 |
|---|---|---|
| 常驻上下文只放稳定约定，可复用流程按需加载为 skills | [Claude Code extension architecture](https://code.claude.com/docs/en/features-overview)、[OpenAI Codex skills](https://developers.openai.com/codex/build-skills) | `CLAUDE.md` 只保留宪法；入口和 Router 都迁为 skills |
| 子代理的核心价值是上下文隔离，适合高噪声调查和独立任务 | [Claude Code subagents](https://code.claude.com/docs/en/sub-agents)、[OpenAI Codex subagents](https://developers.openai.com/codex/agent-configuration/subagents) | Governed 才按证据使用子代理；并行不是复杂度指标 |
| Hook 适合每次都必须发生的确定性自动化 | [Claude Code hooks](https://code.claude.com/docs/en/hooks)、[OpenAI Codex hooks](https://developers.openai.com/codex/hooks) | 不自建重复 Hook；计划评审交给 Plannotator 自己的 Hook，项目检查留给项目 CI/Hook |
| 规格流应轻量、可迭代，而不是固定瀑布阶段 | [OpenSpec official repository](https://github.com/Fission-AI/openspec) | 调用当前 OPSX 原生 explore/propose/apply/archive，不复制旧版工件模板 |
| 方法论已覆盖 brainstorming、worktree、planning、TDD、review、verification | [Superpowers official repository](https://github.com/obra/superpowers) | Router 只选择所需能力，不再维护另一套步骤说明 |
| 计划评审可以自动进入浏览器，代码评审是显式 diff Gate | [Plannotator official repository](https://github.com/backnotprop/plannotator) | Standard 强制 Plan Review；Governed 增加 Code Review |
| 项目规则逐步加载并按路径/场景作用，避免所有规则常驻 | [Cursor project rules](https://docs.cursor.com/context/rules-for-ai)、[Kiro steering](https://kiro.dev/docs/steering/) | 通用模板不预造领域规则；接入业务项目后才按真实目录增加 scoped rules |
| 代理工作应隔离环境并重视命令执行和数据外泄风险 | [Cursor background agents](https://docs.cursor.com/background-agent)、[OpenAI Codex worktrees](https://developers.openai.com/codex/environments/git-worktrees) | 只有独立、低耦合、可独立验证的批次才使用 worktree；不默认并行 |

## Architecture consequences

### Thin orchestration

OpenSpec、Superpowers 和 Plannotator 都在快速迭代。把它们的具体内部步骤复制进模板会立即形成第四套事实源。V3 只固定职责、选择条件、交接点和完成证据；命令细节以安装版本为准。

### Risk floors instead of scores

加权分数适合报表，不适合安全边界。两行授权逻辑可能高风险，几十个文档文件可能低风险。V3 让高风险事实直接设定 Governed 下限，Fast 必须证明全部准入条件，其余默认 Standard。

### Human attention is the scarce resource

每个任务都打开两次评审会制造审批疲劳。V3 把计划评审放在需要持久规格的 Standard/Governed，把代码评审强制留给 Governed；Fast 只保留验证和 diff 自审。

### Evals outside the business runtime

模板维护需要可重复校准，但业务项目不应携带维护脚本。`evals/routing-cases.json` 和 `scripts/evaluate_routing.py` 只验证模板策略，发行包仍保持 6 个文件。

## Deliberately excluded

- 默认 Metrics 平台：缺少规模和决策闭环时只会增加维护成本。
- 自定义 OpenSpec schema：应由采用团队根据真实治理需要扩展。
- 通用领域 rules：不知道业务目录时预设 path scope 容易误导。
- 默认多 Agent：并行会增加协调、合并和 Token 成本，只在任务独立时有收益。
- 自定义安全 Hook：每个项目的危险命令、lint 和测试策略不同，应在业务项目接入阶段配置。
