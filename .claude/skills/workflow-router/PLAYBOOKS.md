# Composable Execution Playbooks — V3.2.1

Router 从本文件选择节点并去重，生成一次任务的 ordered workflow。`REQUIRED` 不可静默跳过；原生能力必须实际调用，不能用文字声称替代。

```text
Core Spine + Task Method + Risk Safeguards + Specialized Gates
```

每个方法节点属于 `planning` 或 `implementation` 阶段。Standard/Governed 的所有 implementation 节点必须位于 Plannotator Plan Review 批准后。

## Confirmation policy

- Route Card：通知，立即继续。
- 内部节点、模式升级、本地文件和 OpenSpec 生命周期：不确认。
- Fast：没有预定人工 Gate。
- Standard：只有 1 个预定人工 Gate，即 Plannotator Plan Review。
- Governed：有 Plan Review 和 Code Review 两类预定人工 Gate；被拒后修订并重新进入同一 Gate。

## Integration Adapter Contract

项目级编排优先于 plugin skill 的默认文件位置、提交动作和重复 Gate，但不得删减分析、调试、测试、Review 与验证方法。

### Superpowers adapter

- 只调用与 Task Method 实际匹配的原生 skill；Standard Bug 不因模式名称而强制执行 Feature brainstorming。
- Feature 的 `brainstorming` 必须包含项目探索、必要澄清、方案取舍、推荐方案和完整设计。
- brainstorming 默认的逐段设计批准、独立 spec review 和 writing-plans 的额外批准，统一合并到当前工作流唯一一次 Plannotator Plan Review。
- brainstorming 与 writing-plans 不创建 `docs/superpowers/` 副本，不自动提交；持久设计和任务写入唯一 OpenSpec change。
- OpenSpec apply-change 是实施阶段外层入口；Superpowers 的 systematic-debugging、TDD、executing-plans、verification 和 review 是其内部实施方法，不再作为第二个并列执行器重复整批任务。
- executing-plans 的 checkpoint 是非阻塞进度更新；finishing-a-development-branch 不自动 merge/commit/push/cleanup。

### OpenSpec adapter

必须区分 Agent 入口和终端 CLI：

| 能力 | 正确入口 | 用途 |
|---|---|---|
| Propose | `/opsx:propose` 或宿主生成的 propose skill | 创建 change 与规划工件 |
| Apply | `/opsx:apply <change-id>` 或 `openspec-apply-change` skill | 进入实施阶段、读取 tasks、更新任务状态 |
| Apply instructions fallback | `openspec instructions apply --change <change-id> --json` | 原生 Agent 入口不可用时获取官方实施指令 |
| Status/Validate/Archive | `openspec status`、`openspec validate`、`openspec archive` | CLI 状态、校验和归档 |

- 终端命令 `openspec apply` 不存在，禁止尝试或把“Router 开始改代码”记作 apply 已完成。
- 能力探测顺序固定为 `/opsx:apply` → `openspec-apply-change` → `openspec instructions apply`。前两项名称可随宿主适配器变化，但必须来自 `openspec init/update` 生成的当前能力。
- apply-change 负责加载 change、确认工件就绪、选择未完成 tasks、调用对应 Superpowers 实施方法并更新 tasks；返回 Router 后再执行统一验证和 Review。
- `propose`、apply-change、archive 子工作流的 `stop` 或 `ready for next command` 只表示返回父 Router，不结束 `/new-task`。
- workflow-state 是编排器 sidecar，不复制 proposal/spec/design/tasks。

### Plannotator adapter

- Claude Code 的 Plan Review Hook 只读取 ExitPlanMode 的 `tool_input.plan`，不会自动扫描 OpenSpec change。
- Router 必须先构造完整 Change Review Packet，再调用 ExitPlanMode；不得只发送计划摘要、文件路径或“请读取 OpenSpec”的提示。
- Standard 的一次 Plan Review 同时批准完整 OpenSpec 文档、方法计划、测试和专项 Gate；Governed 还覆盖迁移、回滚、发布和停止条件。
- Code Review 显式调用当前 Plannotator 原生 review 能力，审实际 diff、验证证据与交付风险。

## Change Review Packet contract

在每次 Plan Review 前执行：

1. **P-RP1 REQUIRED — discover-artifacts**：运行 `openspec status --change <change-id> --json`，并枚举 change 目录中的全部评审文本文件。
2. **P-RP2 REQUIRED — readiness-check**：确认当前 schema 要求的 proposal/specs/design/tasks 等工件均 ready；缺失或 blocked 时不进入 Gate。
3. **P-RP3 REQUIRED — hash-artifacts**：对稳定规划工件计算 SHA-256，使用相对 change 路径和稳定排序生成清单；`workflow-state.yaml` 作为 context-only 完整展示，但不参与失效哈希，避免 Gate 状态更新使其自失效。
4. **P-RP4 REQUIRED — render-full-packet**：将以下内容逐字写入 ExitPlanMode 的 `tool_input.plan`：change id、Route Card、文件清单、每个文件完整内容、测试/回滚/Gate checklist。不得摘要或截断。
5. **P-RP5 HUMAN GATE — exit-plan-mode/plannotator**：提交完整 packet；批准后把文件路径、SHA-256、评审时间和状态写入 workflow-state。

评审文件至少包括 change 目录内的 `.md | .yaml | .yml | .json`，包含 `.openspec.yaml`、所有 specs、proposal/design/tasks 和 `workflow-state.yaml`。其中 workflow-state 标记为 context-only；其他稳定规划工件进入批准哈希清单。若宿主 payload 限制无法容纳全部内容，属于能力降级，必须暂停说明，不能静默省略。

Gate 后任何已评审稳定规划工件的哈希变化都会使 `plan_review.status` 变为 stale；实施前必须重新生成完整 packet 并再次进入同一 Gate。仅 workflow-state 的节点进度、评审结果或时间戳变化不会自触发失效。

## Core Spine

1. **C1 REQUIRED — intake-and-route**：确认 intent、task type、mode、gates、验收和授权边界，输出 Route Card。
2. **C2 REQUIRED — capability-and-focused-exploration**：读取最窄相关代码、消费者与项目验证命令，检查实际需要的能力。
3. **C3 REQUIRED — compose-ledger**：按 phase 展开并去重 ordered workflow；Standard/Governed 在 propose 后持久化账本。
4. **C4 REQUIRED — planning-method**：执行 Task Method 的 planning 节点，不写生产代码、测试文件，不执行有副作用的 dry-run。
5. **C5 REQUIRED — plan-review-and-implementation-entry**：Standard/Governed 完成完整 Review Packet 和 Plan Gate，再调用 OpenSpec apply-change 进入 implementation；Fast 直接进入 implementation。
6. **C6 REQUIRED — verify-and-review**：运行 `verification-before-completion`、项目验证、专项 Gate 和 spec/code review；阻断问题修复后重新验证。
7. **C7 REQUIRED — validate-complete-archive**：先 `openspec validate <change-id>`，再将 workflow-state 标为 completed，最后 archive；完成 branch 收尾并报告。

## Task Method modules

### Feature method

1. **M-FE1 REQUIRED — superpowers:brainstorming [planning]**：探索用户行为、方案与取舍，形成推荐设计。
2. **M-FE2 REQUIRED from Standard — openspec:propose + superpowers:writing-plans [planning]**：将规格、设计、任务和验证写入同一 change。
3. **M-FE3 REQUIRED — superpowers:test-driven-development [implementation]**：批准后在 apply-change 内执行 RED-GREEN-REFACTOR。

### Bug method

brainstorming 只在根因明确后出现真实产品/架构取舍时追加。

1. **M-BU1 REQUIRED — superpowers:systematic-debugging [planning]**：复现、收集证据、缩小边界，禁止猜测式修复。
2. **M-BU2 REQUIRED — root-cause-evidence [planning]**：记录失败机制、影响范围和根因证据，只形成测试计划，不修改测试文件。
3. **M-BU3 REQUIRED — failing-regression-test [implementation]**：Plan Review 批准后，在 apply-change 内先建立因该根因失败的测试。
4. **M-BU4 REQUIRED — minimal-fix [implementation]**：只修根因，然后完成 GREEN 与必要重构。

### Refactor method

1. **M-RE1 REQUIRED — behavior-baseline [planning]**：运行现有验证，明确必须保持的外部行为。
2. **M-RE2 REQUIRED — impact-analysis [planning]**：追踪消费者、状态和隐含耦合。
3. **M-RE3 REQUIRED — characterization-tests [implementation]**：批准后在 apply-change 内补保护测试。
4. **M-RE4 REQUIRED — incremental-refactor [implementation]**：小步修改，每步保持基线通过。

### Upgrade/Config method

1. **M-UP1 REQUIRED — changelog-release-note-analysis [planning]**：读取官方 release notes/changelog 和 breaking changes。
2. **M-UP2 REQUIRED — compatibility-check [planning]**：核对运行时、API、配置、构建和消费者兼容性。
3. **M-UP3 REQUIRED — pre-upgrade-baseline [planning]**：只运行升级前构建/测试并记录行为基线。
4. **M-UP4 REQUIRED — upgrade-and-regression [implementation]**：批准后在 apply-change 内实施最小升级并运行目标回归。

### Migration/Infrastructure method

1. **M-MI1 REQUIRED — impact-and-rollback-plan [planning]**：列出数据/流量/平台影响、回滚与停止条件。
2. **M-MI2 REQUIRED — dry-run-or-simulation [implementation]**：批准后在 apply-change 内对非生产环境或可逆样本演练。
3. **M-MI3 REQUIRED — staged-execution [implementation]**：按依赖和可回滚批次实施。
4. **M-MI4 REQUIRED — rollout-verification [implementation]**：验证迁移结果、运行指标、回滚可用性和发布顺序。

### Maintenance method

1. **M-MA1 REQUIRED — focused-exploration [planning]**：只读目标、直接引用和直接测试。
2. **M-MA2 REQUIRED — minimal-edit [implementation]**：执行无额外业务设计的最小修改。
3. **M-MA3 REQUIRED — direct-verification [verification]**：运行最相关检查并核对 diff。

## Risk Safeguard modules

### Fast safeguards

- 不创建新 OpenSpec change，不进入 Plan Mode。
- 只执行 Core Spine、Task Method 和适用 Gate；出现设计取舍或边界变化立即升级。
- Feature 若完全无设计取舍，可执行精简 brainstorming；一旦产生备选方案必须升级 Standard 并完成持久规格和 Plan Review。

### Standard safeguards

1. **S-OS1 REQUIRED — openspec:propose-and-state [planning]**：若 Task Method 尚未 propose，则调用原生 propose；创建 workflow-state。
2. **S-PL1 REQUIRED — plan-readiness-check [planning]**：检查 AC、任务顺序、方法节点、测试、回滚和 Gate 覆盖。
3. **S-RP1 REQUIRED — complete-change-review-packet [planning]**：执行 P-RP1 至 P-RP4，保证所有 change 文档进入 `tool_input.plan`。
4. **S-HG1 HUMAN GATE — plannotator-plan-review**：执行 P-RP5；批准后自动继续，拒绝则修订并重新生成 packet。
5. **S-WS1 REQUIRED — workspace-isolation [implementation]**：评估 `using-git-worktrees`；已有隔离环境可 N/A + evidence。
6. **S-IM1 REQUIRED — openspec-implementation-entry [implementation]**：按能力探测顺序调用 `/opsx:apply`、`openspec-apply-change` 或官方 instructions fallback；在该入口内执行 Task Method 的 implementation 节点和 Superpowers 方法。
7. **S-RV1 REQUIRED — verification-and-code-review**：执行项目验证、`verification-before-completion`、spec-compliance 和 code-quality review；修复后重验。
8. **S-FI1 REQUIRED — validate-complete-archive**：先 OpenSpec validate，再状态 completed，最后 archive 和 branch finish。

### Governed safeguards

包含 Standard safeguards，并增强：

1. **G-EX1 REQUIRED — openspec:explore [planning]**：调查高影响不确定性，结论进入当前 change。
2. **G-IA1 REQUIRED — isolated-impact-analysis [planning]**：隔离架构/安全/数据/基础设施调查，主上下文只接收证据摘要。
3. **G-PL1 REQUIRED — governed-plan-readiness [planning]**：补齐迁移、回滚、发布、观测和停止条件；全部进入 Review Packet。
4. **G-WS1 REQUIRED — superpowers:using-git-worktrees [implementation]**：使用安全隔离环境；已有等价隔离时记录证据。
5. **G-IM1 REQUIRED — governed-openspec-apply-change [implementation]**：由 OpenSpec implementation entry 调度依赖图；仅并行低耦合任务，并在内部使用对应 Superpowers 方法。
6. **G-RV1 REQUIRED — full-verification-and-review**：执行完整项目矩阵、OpenSpec validate 前置检查和全部专项 Gate。
7. **G-HG1 HUMAN GATE — plannotator-code-review**：显式调用原生 Code Review，评审实际 diff 和交付风险。

## Specialized Gate modules

- **data Gate**：Schema 兼容、数据质量、样本 dry-run、备份/回滚、隐私和前后计数。
- **security Gate**：威胁边界、认证/授权负向测试、秘密处理、依赖/静态安全检查和最小权限。
- **contract Gate**：消费者清单、兼容矩阵、契约测试、版本策略和弃用路径。
- **infrastructure Gate**：配置 diff、环境矩阵、资源/权限边界、可逆演练和故障恢复。
- **release Gate**：发布顺序、feature flag/灰度、停止条件、回滚演练和责任交接。
- **observability Gate**：关键日志/指标/追踪、告警阈值、仪表盘查询和运行手册验证。

## Composition examples

### Standard Feature

```text
C1 → C2 → M-FE1 brainstorming → native OpenSpec propose/state → M-FE2 writing-plans
→ S-PL1 → S-RP1 full Change Review Packet → S-HG1 Plannotator Plan Review
→ S-WS1 → S-IM1 /opsx:apply or openspec-apply-change
   └─ M-FE3 TDD + Superpowers execution methods + OpenSpec task updates
→ S-RV1 → openspec validate → state completed → archive → C7
```

### Standard Bug

```text
C1 → C2 → M-BU1 systematic-debugging → M-BU2 root-cause-evidence/test-plan
→ native OpenSpec propose/state → S-PL1 → S-RP1 full Change Review Packet
→ S-HG1 Plannotator Plan Review → S-WS1 → S-IM1 OpenSpec implementation entry
   └─ M-BU3 failing-regression-test → M-BU4 minimal-fix → task updates
→ S-RV1 → openspec validate → state completed → archive → C7
```

### Governed Migration with data/release/observability Gates

```text
C1 → C2 → G-EX1 → M-MI1 impact/rollback plan → G-IA1 → native OpenSpec propose/state
→ G-PL1 + gate plans → S-RP1 full Change Review Packet → S-HG1 Plan Review
→ G-WS1 → G-IM1 OpenSpec apply-change
   └─ M-MI2 dry-run → M-MI3 staged execution → M-MI4 rollout verification
→ G-RV1 + gate evidence → G-HG1 Code Review
→ openspec validate → state completed → archive → C7
```

## Durable workflow state contract

Standard/Governed 在 `openspec/changes/<change-id>/workflow-state.yaml` 使用以下最小结构：

```yaml
schema_version: 1
intent: change
task_type: bug
mode: standard
specialized_gates: []
current_node: S-IM1
status: active
plan_review:
  status: approved
  reviewed_at: "ISO-8601 timestamp"
  artifacts:
    - path: proposal.md
      sha256: "hex digest"
nodes:
  - id: M-BU1
    phase: planning
    source: method
    required: true
    status: done
    evidence: "reproduction command and failing output"
updated_at: "ISO-8601 timestamp"
```

约束：

- `status` 只能是 `active | blocked | completed`；节点状态只能是 `pending | in_progress | done | N/A | blocked`。
- propose 获得 change id 后创建；每个节点完成后、人工 Gate 前后、重路由后和中断前更新。
- Plan Review 批准后保存稳定规划工件的 artifact hash 清单；任一哈希变化时将 `plan_review.status` 设为 stale，阻止 implementation entry，直到重新评审。workflow-state 自身作为 context-only，不参与该比较。
- 续跑时从 ordered workflow 中最早的 pending/in_progress/blocked REQUIRED 节点继续；done 节点不重复，N/A 必须有 evidence。
- 完成顺序固定为：项目验证与 Review → `openspec validate <change-id>` → status completed → `openspec archive <change-id>`。
- Fast 只在当前对话维护账本；升级 Standard 后立即创建 OpenSpec change 和状态文件。

## Native capability rule

- 原生 Agent command/skill 可用时必须实际调用；不得用文字标签伪装调用完成。
- `/opsx:apply` 是 Agent 命令，不是 CLI。终端只使用当前 CLI 确实提供的 status/instructions/validate/archive。
- 能力恢复不需要用户确认；完整 Review Packet 无法提交或实施入口只能被非官方方案替代时，才属于保障降级。
