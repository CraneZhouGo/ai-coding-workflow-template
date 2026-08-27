# AI Coding Workflow Template V3 Adaptive

这是一个面向 Claude Code 的薄编排模板。它不会重新实现 Superpowers、OpenSpec 或 Plannotator，而是根据需求的真实风险自动选择三种执行模式，并把三者放在各自最有价值的节点。

用户只需描述需求，或使用：

```text
/new-task <需求>
```

## Three modes

| 模式 | 适用范围 | OpenSpec | Plannotator | Token 策略 |
|---|---|---|---|---|
| Fast | 清晰、局部、低风险、易回滚 | 不创建新 change | 无强制 Gate | 只读目标、直接依赖和直接测试 |
| Standard | 普通功能、模块内协作、有限设计选择 | 原生 propose/apply/validate/archive | Plan Review | 一个 change、定向探索、两遍 AI review |
| Governed | 数据迁移、权限/资金/库存、契约破坏、跨服务交付 | explore/propose/apply/validate/archive | Plan + Code Review | 隔离高噪声探索，完整风险与交付证据 |

路由不使用加权分数。高风险触发器先决定最低保障；只有同时满足全部准入条件才走 Fast；其他任务默认 Standard。

## Tool contract

- Superpowers：brainstorming、planning、TDD、debugging、verification、review 等开发方法。
- OpenSpec：Standard/Governed 的唯一持久化需求与变更事实源。
- Plannotator：计划和代码的人类决策界面；计划评审由 Hook 自动触发。
- Claude Code：代码探索、编辑、命令执行和工具编排。

模板只决定“何时调用”，具体步骤由各工具当前安装版本负责，因此不会因复制旧版命令而快速过时。

## Business package

分发包只有 6 个运行时文件：

```text
CLAUDE.md
.claude/project-profile.yaml
.claude/skills/new-task/SKILL.md
.claude/skills/workflow-router/SKILL.md
.claude/skills/workflow-router/ROUTING.md
.claude/skills/workflow-router/PLAYBOOKS.md
```

业务项目不包含 Python、Metrics、路由评测或模板 CI。

## Setup

1. 将分发包解压到项目根目录；已有 `CLAUDE.md` 时合并规则，不要直接覆盖项目约定。
2. 填写 `.claude/project-profile.yaml` 中的真实验证命令、关键目录和交付能力。
3. 安装 Superpowers、OpenSpec 和 Plannotator，并重启 Claude Code 让 plugins/skills/hooks 生效。
4. 在项目中执行 `openspec init`，选择 Claude Code；以后升级 OpenSpec 后执行 `openspec update`。
5. 使用 `/new-task <需求>`，后续模式和工具节点由 Router 自动处理。

安装与行为细节见项目根目录的《AI Coding Workflow Template 详细使用说明》。

## Maintainer validation

以下命令只用于维护模板，不需要复制到业务项目：

```text
python scripts/validate_workflow.py
python scripts/evaluate_routing.py
python -m unittest discover -s tests -v
python scripts/build_distribution.py
python scripts/validate_workflow.py --archive ai-coding-workflow-template.zip
```
