# Composable Execution Playbooks

Router 从本文件选择节点并去重，生成一次任务的 ordered workflow。`REQUIRED` 不可静默跳过；Superpowers 节点必须调用已安装版本的原生 skill，常见名称为 `superpowers:<name>`。

```text
Core Spine + Task Method + Risk Safeguards + Specialized Gates
```

## Confirmation policy

- Route Card：通知，立即继续。
- 内部节点、模式升级、本地文件和 OpenSpec 生命周期：不确认。
- Fast：没有预定人工 Gate。
- Standard：只有 1 个预定人工 Gate，即 Plannotator Plan Review。
- Governed：有 Plan Review 和 Code Review 两类预定人工 Gate；被拒后修订并重新进入同一 Gate。

## Integration Adapter Contract

项目级编排优先于 plugin skill 的默认文件位置、提交动作和交互 Gate，但不得删减其分析、调试、测试、Review 与验证方法。

### Superpowers adapter

- 只调用与 Task Method 和 Risk Safeguards 实际匹配的原生 skill；Standard Bug 不因模式名称而被强制执行 Feature brainstorming。
- Feature 的 `brainstorming` 必须包含项目探索、必要澄清、2–3 个方案及取舍、推荐方案和完整设计。
- 真正影响结果且无法从证据推断的问题可以暂停；已由需求或代码库回答的问题不得重复询问。
- brainstorming 默认的逐段设计批准、独立 spec review 和 writing-plans 的额外批准，统一合并到当前工作流唯一一次 Plannotator Plan Review。
- brainstorming 与 writing-plans 不创建 `docs/superpowers/` 副本，不自动提交；持久设计和任务写入唯一 OpenSpec change。
- executing-plans 的批次 checkpoint 是非阻塞进度更新，不是审批点。
- finishing-a-development-branch 执行验证和状态收尾；merge/commit/push/cleanup 等未授权选择放入最终报告，不阻塞本地任务完成。

### OpenSpec adapter

- Standard/Governed 使用当前原生 `explore`、`propose`、`apply`、validate、archive 能力，不仿造 OpenSpec 内部 schema。
- `propose`、`apply`、`archive` 子工作流的 planning/implementation boundary 仍有效，但其 `stop` 或 `ready for next command` 只表示返回父 Router。
- Router 收回控制权后更新 `workflow-state.yaml` 并自动调用下一节点；不得要求用户手动输入下一条 OPSX 命令。
- workflow-state 是编排器 sidecar，只记录路由和节点进度，不复制 proposal/spec/design/tasks 内容。

### Plannotator adapter

- Standard 的 Plan Review 一次性评审 OpenSpec 中的规格、方法计划、测试与适用专项 Gate。
- Governed 的 Plan Review 还覆盖迁移、回滚、发布和停止条件；Code Review 只审实际 diff、验证证据与交付风险。

## Core Spine

所有 change 请求都包含以下主链。模块插入点决定 Task Method、Mode 和 Gate 节点的位置：

1. **C1 REQUIRED — intake-and-route**：确认 intent、task type、initial mode、gates、验收和授权边界，输出 Route Card。
2. **C2 REQUIRED — capability-and-focused-exploration**：读取最窄相关代码、直接消费者与项目验证命令，检查所需能力。
3. **C3 REQUIRED — compose-ledger**：展开并去重 ordered workflow；Standard/Governed 在 propose 后将账本持久化。
4. **C4 REQUIRED — execute-task-method**：按 Task Method 的调查、设计/根因/基线、实施节点执行。
5. **C5 REQUIRED — verify**：调用 `verification-before-completion` 或等价的直接验证，执行 profile 与 Gate 要求的检查。
6. **C6 REQUIRED — review-and-reroute**：核对完整 diff、规格符合性、代码质量和风险变化；阻断问题修复后回到 C5。
7. **C7 REQUIRED — finish-and-persist**：运行适用的 `finishing-a-development-branch`、记录剩余风险；Standard/Governed 完成 OpenSpec validate、状态 completed 和 archive。

## Task Method modules

### Feature method

按顺序组合：

1. **M-FE1 REQUIRED — superpowers:brainstorming**：探索用户行为、方案与取舍，形成推荐设计。
2. **M-FE2 REQUIRED from Standard — openspec:propose + superpowers:writing-plans**：将规格、设计、任务和验证写入同一 change。
3. **M-FE3 REQUIRED — superpowers:test-driven-development**：生产行为执行 RED-GREEN-REFACTOR；无生产行为时记录 N/A 证据。

### Bug method

按顺序组合，brainstorming 仅在根因明确后出现真实产品/架构取舍时才追加：

1. **M-BU1 REQUIRED — superpowers:systematic-debugging**：复现、收集证据、缩小边界，禁止猜测式修复。
2. **M-BU2 REQUIRED — root-cause-evidence**：记录失败机制、影响范围和根因证据。
3. **M-BU3 REQUIRED — failing-regression-test**：先建立能因该根因失败的测试；确实无法自动化时记录限制与替代验证。
4. **M-BU4 REQUIRED — minimal-fix**：只修根因，然后完成 GREEN 与必要重构。

### Refactor method

1. **M-RE1 REQUIRED — behavior-baseline**：明确必须保持的外部行为和当前验证结果。
2. **M-RE2 REQUIRED — impact-analysis**：追踪消费者、状态和隐含耦合。
3. **M-RE3 REQUIRED — characterization-tests**：为未被可靠覆盖的现有行为补保护测试。
4. **M-RE4 REQUIRED — incremental-refactor**：小步修改，每步保持基线通过。

### Upgrade/Config method

1. **M-UP1 REQUIRED — changelog-release-note-analysis**：读取官方 release notes/changelog 和 breaking changes。
2. **M-UP2 REQUIRED — compatibility-check**：核对运行时、API、配置、构建和消费者兼容性。
3. **M-UP3 REQUIRED — pre-upgrade-baseline**：记录升级前构建/测试/行为基线。
4. **M-UP4 REQUIRED — upgrade-and-regression**：实施最小升级并运行目标回归；发现不兼容时重新路由。

### Migration/Infrastructure method

1. **M-MI1 REQUIRED — impact-and-rollback-plan**：列出数据/流量/平台影响、回滚与停止条件。
2. **M-MI2 REQUIRED — dry-run-or-simulation**：在非生产环境或可逆样本上演练；无法演练时阻断并说明保障缺口。
3. **M-MI3 REQUIRED — staged-execution**：按依赖和可回滚批次实施。
4. **M-MI4 REQUIRED — rollout-verification**：验证迁移结果、运行指标、回滚可用性和发布顺序。

### Maintenance method

1. **M-MA1 REQUIRED — focused-exploration**：只读目标、直接引用和直接测试。
2. **M-MA2 REQUIRED — minimal-edit**：执行无额外业务设计的最小修改。
3. **M-MA3 REQUIRED — direct-verification**：运行最相关检查并核对 diff。

## Risk Safeguard modules

### Fast safeguards

- 不创建新 OpenSpec change，不进入 Plan Mode。
- 只执行 Core Spine、Task Method 的必要节点和适用 Gate。
- 探索中出现设计取舍、影响不明或边界变化时立即升级 Standard/Governed。
- AI diff self-review 后即可收尾。

### Standard safeguards

1. **S-OS1 REQUIRED — openspec:propose-and-state**：若 Task Method 尚未 propose，则创建 change；立即写入 `workflow-state.yaml`。
2. **S-PL1 REQUIRED — plan-readiness-check**：检查 AC、任务顺序、方法节点、测试、回滚和 Gate 覆盖。
3. **S-HG1 HUMAN GATE — plannotator-plan-review**：一次性提交完整计划；批准后自动继续，拒绝则修订并重入本 Gate。
4. **S-AP1 REQUIRED — workspace-and-openspec:apply**：评估 `using-git-worktrees`；已有隔离环境可 N/A + evidence，随后进入 OpenSpec apply。
5. **S-EX1 REQUIRED — superpowers:executing-plans**：按组合账本连续实施；checkpoint 只汇报进度。
6. **S-RV1 REQUIRED — superpowers:requesting-code-review**：先 spec-compliance，再 code-quality；修复后重新验证。
7. **S-FI1 REQUIRED — superpowers:finishing-a-development-branch + openspec validate/archive**：完成本地收尾、状态完成和归档。

Standard 只规定上述保障，不替换 Task Method；Feature 有 brainstorming，Bug 有 systematic-debugging，二者都只有同一个 Plan Review。

### Governed safeguards

包含 Standard safeguards，并增强：

1. **G-EX1 REQUIRED — openspec:explore**：调查高影响不确定性，结论进入当前 change。
2. **G-IA1 REQUIRED — isolated-impact-analysis**：按需隔离架构/安全/数据/基础设施调查，主上下文只接收证据摘要。
3. **G-PL1 REQUIRED — governed-plan-readiness**：补齐迁移、回滚、发布、观测、停止条件和 Gate 证据计划。
4. **G-WS1 REQUIRED — superpowers:using-git-worktrees**：使用安全隔离环境；已有等价隔离时记录证据。
5. **G-EX2 REQUIRED — subagent-driven-development / executing-plans**：仅并行低耦合、可独立验证任务。
6. **G-RV1 REQUIRED — full-verification-and-review**：执行完整项目矩阵、OpenSpec validate 和所有专项 Gate。
7. **G-HG1 HUMAN GATE — plannotator-code-review**：AI spec/code review 通过后评审实际 diff 和交付风险。

## Specialized Gate modules

Gate 节点在 plan-readiness 中形成验证计划，在 verify/review 中形成证据：

- **data Gate**：Schema 兼容、数据质量、样本 dry-run、备份/回滚、隐私和前后计数。
- **security Gate**：威胁边界、认证/授权负向测试、秘密处理、依赖/静态安全检查和最小权限。
- **contract Gate**：消费者清单、兼容矩阵、契约测试、版本策略和弃用路径。
- **infrastructure Gate**：配置 diff、环境矩阵、资源/权限边界、可逆演练和故障恢复。
- **release Gate**：发布顺序、feature flag/灰度、停止条件、回滚演练和责任交接。
- **observability Gate**：关键日志/指标/追踪、告警阈值、仪表盘查询和运行手册验证。

## Composition examples

### Standard Feature

```text
C1 → C2 → M-FE1 brainstorming → OpenSpec propose/state → M-FE2 writing-plans
→ S-PL1 → S-HG1 Plan Review → S-AP1 → S-EX1 + M-FE3 TDD
→ C5 verification → S-RV1 → C6 → S-FI1 → C7
```

### Standard Bug

```text
C1 → C2 → M-BU1 systematic-debugging → M-BU2 root-cause-evidence
→ M-BU3 failing-regression-test → OpenSpec propose/state → S-PL1
→ S-HG1 Plan Review → S-AP1 → S-EX1 + M-BU4 minimal-fix
→ C5 verification → S-RV1 → C6 → S-FI1 → C7
```

Standard Bug 不无条件执行 brainstorming；只有修复涉及新的行为设计或架构取舍时才在 propose 前追加 Feature brainstorming 节点。

### Governed Migration with data/release/observability Gates

```text
C1 → C2 → G-EX1 → M-MI1 → G-IA1 → OpenSpec propose/state
→ M-MI2 → G-PL1 + data/release/observability plans → S-HG1
→ G-WS1 → S-AP1 → G-EX2 + M-MI3 → G-RV1 + M-MI4 + gate evidence
→ AI review → G-HG1 Code Review → S-FI1 → C7
```

## Durable workflow state contract

Standard/Governed 在 `openspec/changes/<change-id>/workflow-state.yaml` 使用以下最小结构：

```yaml
schema_version: 1
intent: change
task_type: bug
mode: standard
specialized_gates: []
current_node: M-BU3
status: active
nodes:
  - id: M-BU1
    source: method
    required: true
    status: done
    evidence: "reproduction command and failing output"
updated_at: "ISO-8601 timestamp"
```

约束：

- `status` 只能是 `active | blocked | completed`；节点状态只能是 `pending | in_progress | done | N/A | blocked`。
- propose 获得 change id 后创建；每个节点完成后、人工 Gate 前后、重路由后和中断前更新。
- 续跑时读取 OpenSpec 工件与状态，从 ordered workflow 中最早的 pending/in_progress/blocked REQUIRED 节点继续。
- done 节点不重复；N/A 必须保留 evidence；组合发生变化时保留已有等价证据并追加新节点。
- 完成前将 status 标为 completed，运行 `openspec validate <change-id>`，再 archive。
- Fast 只在当前对话维护账本，不写 sidecar；若升级 Standard，立即创建 OpenSpec change 和状态文件。

## Native capability rule

- 原生能力可用时必须实际调用，不能只在文本中声称“采用其方法”。
- 工具调用名称可因宿主版本变化，但节点语义、顺序、状态和证据不能缺失。
- 能力恢复不需要用户确认；降级才是暂停条件。
