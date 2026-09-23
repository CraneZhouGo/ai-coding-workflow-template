---
name: ai-coding-workflow
description: 根据请求意图、任务类型和风险，为代码理解、评审、诊断、规划、功能、修复、重构、升级与迁移自动选择并连续执行确定性开发工作流；在 Codex 中协调 Superpowers、OpenSpec 和 Plannotator。用于用户提出软件项目相关任务时，不用于与代码库无关的一般问答。
---

# AI Coding Workflow for Codex

把当前用户请求作为输入，不要求用户先选择模式。用户明确要求修改时，授权范围仅包含当前项目内的读取、修改、非破坏性命令、构建、测试和当前 OpenSpec change 的本地生命周期；不包含提交、推送、部署、秘密访问或破坏性动作。

## 入口

1. 定位本插件根目录和项目 Git 根目录。首次用于该项目时运行：

   ```text
   node <plugin-root>/scripts/workflow-runtime.mjs init-project --host codex --root <project-root>
   ```

   该命令只在缺失时创建 `.codex/ai-coding-workflow/project-profile.yaml`，并同步状态 schema；不得覆盖用户已经填写的画像。
2. 若项目画像不存在，或其中的 `setup.status` 不是 `ready`，先只读运行插件 `scripts/setup-check.mjs --root <project-root>`。依赖缺失时使用 `$ai-coding-workflow-setup` 的一次性修复流程；普通开发请求没有安装授权时，只汇总缺失项并询问一次，不写画像、不逐项确认。
3. 读取项目画像。若 `profile_status` 不是 `ready`，先通过最窄项目探索补齐可从仓库验证的事实；无法确定的关键事实才询问。画像未 ready 时禁止 Fast。
4. 先恢复唯一匹配的未完成 `workflow-state.json`；完成节点不得重做。没有匹配状态时再创建新路线。

## 确定性路由

读取 [references/ROUTING.md](references/ROUTING.md)，提取结构化 `route_facts`，再调用 runtime `route`。不得凭文字自行决定模式。向用户展示简短 Route Card 后立即继续；Route Card 不是批准 Gate。

非 `change` 意图保持只读并直接完成。`change` 意图调用 runtime `compose`，再按 `next` 返回的唯一当前节点执行。每个节点开始、完成、阻断或不适用都通过 `transition` 记录真实 evidence。

## 节点执行

只读取 [references/PLAYBOOKS.md](references/PLAYBOOKS.md) 中公共合同、本次 Task Method、Risk Safeguards 和实际 Specialized Gates。遵循以下宿主适配：

- Superpowers：调用当前任务实际需要的原生 skill，例如 `brainstorming`、`systematic-debugging`、`test-driven-development`、`verification-before-completion`；不为模式名称调用无关 skill。
- OpenSpec：Codex 只使用 skill 入口。Propose 调用 `$openspec-propose`，实施调用 `$openspec-apply-change`，可用时验证调用 `$openspec-verify-change`。终端 CLI 只用于 `status`、`instructions apply`、`validate` 和 `archive`，不得运行不存在的 `openspec apply`。
- Plannotator：优先调用 `$plannotator-review` 展示真实 VCS diff；该 Skill 不可用但 CLI 可用时，调用 `plannotator review --git`。Spec Gate 评审当前 change 的 uncommitted diff；Governed 的 Code Gate 评审 since-base 代码 diff。不得手工拼接 OpenSpec 文档正文。

Standard 只在 Spec Diff Review 暂停，Governed 额外在 Code Diff Review 暂停。除此之外不询问“是否继续”或逐节点确认。工具缺失时先尝试无损恢复；只有保障会降低、需要新权限或存在真实产品分歧时才暂停。

## 完成条件

Fast 在定向验证通过后完成。Standard/Governed 必须完成项目验证、专项 Gate、OpenSpec strict validate 和 archive；状态文件进入 archive 目录并由 runtime `archive-complete` 成功后，才能报告 completed。Git 提交、推送和部署仍需用户明确要求。
