# AI Coding Workflow Template V3.3 详细使用说明

## 1. 它解决什么问题

这套工作流希望同时做到两件事：小任务不过度消耗 Token，高风险任务不漏掉设计、规格、验证和 Review。V3.3 不再只靠 AI 记住流程；AI 提取事实，确定性 runtime 计算路线并维护节点状态。

```text
需求与代码证据 → route_facts → 确定性 Router
→ Core + Task Method + Risk Safeguards + Specialized Gates
→ 逐节点执行与证据 → 验证、归档、完成
```

## 2. 首次接入

### Codex Desktop / CLI

1. 克隆仓库后在根目录执行 `codex plugin marketplace add .`；远程版本发布后也可以执行 `codex plugin marketplace add CraneZhouGo/ai-coding-workflow-template`。重启 Codex Desktop，然后从 `AI Coding Workflow` Marketplace 安装插件。
2. 在业务项目的新任务中调用 `$ai-coding-workflow-setup`。它集中检查 Node.js 20.19.0+、Superpowers、OpenSpec、Plannotator 和项目 Skills；显式 setup 请求授权标准安装，普通任务触发时只集中确认一次。Superpowers 仍通过官方插件页或 `/plugins` 交互入口安装，因为 Codex 插件清单不能声明插件依赖。
3. 信任业务项目并审查、信任插件 Hook。第三方插件安装或新 Skill 生效后开启新任务，再直接描述需求或调用 `$ai-coding-workflow`。
4. Setup 创建 `.codex/ai-coding-workflow/project-profile.yaml` 并记录检查状态。补齐真实 build/test/static/security 命令和风险位置后，将 `profile_status` 改为 `ready`。
5. `hook_profile: "default"` 只恢复和续跑；改为 `strict` 后额外阻止 Spec Review 前越界编辑。两者直接修改画像即可切换，不需要重新安装 Hook。

Codex 版使用 `$openspec-propose`、`$openspec-apply-change`、可选的 `$openspec-verify-change` 和 `$plannotator-review`；不会调用 Claude Code 的 `/opsx:*` 或 `/plannotator-review`。

### Claude Code

1. 解压 `ai-coding-workflow-template.zip` 到业务项目根目录。已有 `CLAUDE.md` 和 `.claude/settings.json` 时应合并规则，不直接覆盖。
2. 安装 Superpowers、OpenSpec 和 Plannotator，并执行 `openspec init` 选择 Claude Code。
3. 编辑 `.claude/project-profile.yaml`：填写真实 build/test/static/security 命令、公共契约和迁移目录、回滚、观测及部署能力。确认完成后设置：

```yaml
profile_status: "ready"
```

4. 运行一次 Hook 安装命令；它会保留现有 settings，并默认幂等安装 SessionStart + Stop：

```text
node .claude/scripts/workflow-runtime.mjs install-hooks
```

只有明确需要规划期写入强制拦截的项目才安装 strict profile：

```text
node .claude/scripts/workflow-runtime.mjs install-hooks --profile strict
```

再次执行默认命令可以从 strict 切回默认配置；安装器不会删除项目自有 Hook。

5. 重启 Claude Code。以后只需描述需求或执行 `/new-task <需求>`。

画像未 ready 时工作流仍可运行，但禁止 Fast，以免未知项目条件被误判为低风险。

## 3. 自动路由

路由按固定顺序计算：

1. Intent：解释、评审、仅诊断、仅计划或修改。只有 change 获得改代码授权。
2. Task Type：Feature、Bug、Refactor、Upgrade/Config、Migration/Infrastructure 或 Maintenance。
3. Risk Mode：任一高风险事实先锁定 Governed；Fast 必须满足全部准入条件；其余为 Standard。
4. Specialized Gates：按实际影响叠加 data、security、contract、infrastructure、release、observability。
5. Ordered Execution：runtime 组合节点并生成 route/workflow hash。

同一组事实、画像状态和工作流版本会得到同一个 `route_fingerprint`。Feature 即使改动很小也最低 Standard，因为 Superpowers brainstorming 需要把设计决定放进可评审的 OpenSpec change。

## 4. 三种模式覆盖什么

| 模式 | 典型场景 | 人工 Gate | 执行策略 |
|---|---|---|---|
| Fast | 文档小修、局部机械维护、明确且可直接验证的非 Feature 修改 | 无 | concise + targeted + sequential |
| Standard | 普通功能、复杂 Bug、模块重构、有限兼容升级 | Spec Diff Review | normal/affected + isolate-if-dirty |
| Governed | 资金、权限、敏感数据、Schema/回填、不兼容契约、共享基础设施、协调发布 | Spec Diff + Code Diff Review | extensive/full + mandatory worktree |

三种模式只表示风险层。任务具体怎么做由 Task Method 决定：Feature 使用 brainstorming/spec/TDD；Bug 使用 systematic-debugging/根因证据/失败回归测试；其他类型也有独立方法。因此无需再增加固定模式。

## 5. 三个工具在什么节点出现

### Superpowers

- Feature planning：`brainstorming`，探索行为、方案、取舍和推荐设计。
- Bug planning：`systematic-debugging`，先复现和证明根因。
- Implementation：按任务调用 TDD、debugging、executing-plans 等方法。
- Verification：完成前验证和独立 Review。

### OpenSpec

Standard/Governed 使用同一个 change 保存 proposal/specs/design/tasks。实施入口按顺序探测：

```text
/opsx:apply <change-id>
openspec-apply-change skill
openspec instructions apply --change <change-id> --json   # fallback
```

终端没有 `openspec apply` 命令。完成顺序是：项目验证和 Review → `openspec validate <change-id> --strict --no-interactive` → archive ready → `openspec archive <change-id> --yes` → runtime `archive-complete` → completed。没有 spec delta 的 change 在 `.openspec.yaml` 使用 `skip_specs: true`。

### Plannotator

- Standard/Governed planning：调用 `/plannotator-review` 并选择 `uncommitted`，直接显示发生变化的 OpenSpec 文件树和逐行 diff。
- Governed verification 后：再次调用 `/plannotator-review`，使用 `since-base` 评审完整代码变化。

Runtime 会比较 Plannotator 实际展示路径和 Git 捕获的 expected paths；少文件、多文件或混入其他 change 都不能批准。不会创建 Review Packet，也不会手动拼接文档正文。

## 6. 为什么能连续执行

所有 change 都有 `workflow-state.json`：

```text
Fast:               .claude/workflow-runs/<route-fingerprint>/workflow-state.json
Standard/Governed:  openspec/changes/<change-id>/workflow-state.json
```

其中记录 route facts、route/workflow hash、current node、节点证据、Review 文件与 SHA-256、重路由历史和归档状态。状态只允许 `pending → in_progress → done/blocked/N/A` 等法定转换，完成和跳过都必须有证据。

Hook 的作用：

- SessionStart（默认）：恢复唯一活动任务和当前节点。
- Stop（默认）：还有可执行 REQUIRED 节点时阻止 Agent 提前结束；人工 Gate 或真实 blocked 时允许停下。
- PreToolUse（strict 可选）：Spec Diff Review 前不允许改业务代码；Fast 的 planning 完成前也不允许编辑。

不再安装 PreCompact。每次节点转换、Review、重路由和归档都会原子保存状态，上下文压缩 Hook 不会增加实际可靠性。

你不需要手动运行状态命令。正常情况下 Router 会自动调用 route、compose、init-state、next、transition、capture-spec-diff、review、reroute 和 archive-complete。只有首次安装 Hook 需要手动执行一次安装命令。

## 7. 什么时候需要用户操作

| 场景 | 是否暂停 |
|---|---|
| Route Card、模式选择、内部节点、模式自动升级 | 否 |
| Standard/Governed Spec Diff Review | 是，在 Plannotator 批准或反馈 |
| Governed Code Diff Review | 是，在 Plannotator 批准或反馈 |
| 代码库无法消除的产品分歧、保障降级、多个活动 change 无法消歧 | 是 |
| Git 提交/推送、部署、秘密、破坏性或外部写入 | 需要明确授权 |

OpenSpec 子命令显示 stop 或 ready 只表示返回父 Router，不表示整项任务完成，也不需要用户手动触发下一步。

## 8. 每个发行文件的用途

Codex 插件位于 `plugins/ai-coding-workflow/`：

| 文件 | 用途 | 触发时机 |
|---|---|---|
| `plugin.json` | 通用插件身份 | 安装、发布和新格式宿主发现 |
| `.codex-plugin/plugin.json` | Codex 兼容清单 | Codex Desktop/CLI 安装和展示 |
| `skills/ai-coding-workflow/SKILL.md` | 单一自动路由入口 | 软件项目请求匹配或显式 `$ai-coding-workflow` |
| `skills/ai-coding-workflow-setup/SKILL.md` | 依赖检测与一次性初始化 | 安装、配置、修复或缺失依赖时 |
| `skills/ai-coding-workflow/references/` | Codex 路由与节点合同 | Skill 按本次任务选择性读取 |
| `scripts/workflow-runtime.mjs` | 确定性路由和状态机 | Skill 与 Hook 自动调用 |
| `scripts/setup-check.mjs` | 只读依赖检测并更新画像 setup 状态 | Setup 和首次开发请求 |
| `hooks/hooks.json` | 恢复、续跑与可选严格写入保护 | 安装后经用户信任生效 |
| `assets/project-profile.yaml` | Codex 项目画像模板 | 首次运行复制到业务项目 |
| `assets/workflow-state.schema.json` | 状态结构合同 | 首次运行同步到业务项目 |

Claude Code 发行文件如下：

| 文件 | 用途 | 触发时机 |
|---|---|---|
| `CLAUDE.md` | 全局授权边界和稳定规则 | 会话开始 |
| `.claude/project-profile.yaml` | 业务项目真实能力 | 首次接入与能力变化时维护 |
| `.claude/skills/new-task/SKILL.md` | 单一入口 | `/new-task` |
| `.claude/skills/workflow-router/SKILL.md` | Router 操作规程 | 每项任务 |
| `ROUTING.md` | 路由判据 | 新路由或重路由 |
| `PLAYBOOKS.md` | 节点和工具交接语义 | 只加载本次相关章节 |
| `.claude/scripts/workflow-runtime.mjs` | 可执行控制器 | Agent 自动调用；首次安装 Hook 手动调用 |
| `.claude/workflow-state.schema.json` | JSON 状态结构 | runtime/CI 校验 |
| `.claude/hooks/workflow-hooks.json` | Hook 安装片段 | install-hooks 合并时 |
| `.claude/workflow-runs/.gitignore` | 防止 Fast 临时状态进入 Git | 自动 |

## 9. 维护仓库文件

这些文件不进入业务压缩包，也不需要业务开发者运行：

- `scripts/evaluate_routing.py`：调用同一个 Node Router 重放路由案例。
- `tests/test_workflow_tools.py`：验证路由稳定性、状态机、Hook、Review 范围和 hash drift。
- `scripts/validate_workflow.py`：校验运行时合同和发行包。
- `scripts/build_distribution.py`：构建字节可复现的压缩包。
- `evals/routing-cases.json`：覆盖日常任务与风险边界。

## 10. Token 控制原则

- 非 change 不加载修改链。
- 只读取本次 Task Method、模式和实际 Gate 对应的 playbook 段落。
- Fast 使用最短计划和 targeted 验证；Standard 不增加第二个人工代码 Gate。
- Governed 只按风险选择 architect/security/e2e 等 specialist，不默认启动全部 Agent。
- Hook 不执行全量测试或格式化；验证集中在明确节点。
- 持久状态避免上下文压缩后重复探索、重复 Review 和重复确认。
