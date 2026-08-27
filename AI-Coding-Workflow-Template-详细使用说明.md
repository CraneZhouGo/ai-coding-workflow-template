# AI Coding Workflow Template V3.2 Composable 详细使用说明

## 1. 设计目标

这套模板在“Token 消耗”和“实现保障”之间按任务实际需要取平衡。它不再让三种风险模式各自维护一条越来越长的固定流程，而是自动组合：

```text
Core Spine + Task Method + Risk Safeguards + Specialized Gates
```

- Superpowers 提供分析、设计、调试、测试、评审和验证方法。
- OpenSpec 保存 Standard/Governed 的规格、任务和工作流状态。
- Plannotator 承载真正需要人决定的计划与代码评审。
- Claude Code 执行探索、修改、命令和工具编排。

## 2. 安装与项目画像

将 `ai-coding-workflow-template.zip` 解压到业务项目根目录。已有 `CLAUDE.md` 或 `.claude/` 时，保留项目原有构建、风格和安全约定，再合并本模板规则，不覆盖工具自动生成的文件。

安装 Superpowers：

```text
/plugin install superpowers@claude-plugins-official
```

安装和初始化 OpenSpec：

```text
npm install -g @fission-ai/openspec@latest
openspec init
```

初始化时选择 Claude Code。升级后执行 `openspec update`。

安装 Plannotator：

```text
/plugin marketplace add backnotprop/plannotator
/plugin install plannotator@plannotator
```

安装插件后重启 Claude Code。然后编辑 `.claude/project-profile.yaml`，填写真实验证命令、公共契约/迁移/共享基础设施位置，以及回滚、观测和发布能力。

## 3. 日常入口与 Route Card

推荐只启动一次：

```text
/new-task 修复订单重复提交问题
```

Router 输出类似：

```text
intent: change
task_type: bug
mode: standard
specialized_gates: none
workflow: Core Spine + Bug Method + Standard Safeguards
resume: new
human_gates: plan-review
```

Route Card 是通知，不是审批。随后立即进入第一个节点。

## 4. 四层自动路由

### 4.1 Intent：先判断授权

- explain：理解或解释，只读。
- review：评审代码、计划或 diff，只读。
- diagnose-only：定位问题，可运行诊断和测试，但不修复。
- plan-only：只制定方案，不实施。
- change：明确要求新增、修复、重构、升级、迁移或修改。

“诊断登录失败但不要修”不会被自动改代码；“诊断并修复”才进入 change。

### 4.2 Task Type：决定方法

| 类型 | 主要节点 |
|---|---|
| Feature | brainstorming → spec/plan → TDD |
| Bug | systematic-debugging → 根因证据 → 失败回归测试 → 最小修复 |
| Refactor | 行为基线 → 影响分析 → characterization tests → 小步重构 |
| Upgrade/Config | changelog/release notes → 兼容检查 → 升级前基线 → 回归 |
| Migration/Infrastructure | 影响与回滚 → dry-run → 分批实施 → rollout verification |
| Maintenance | 定向探索 → 最小编辑 → 直接验证 |

因此 Standard Bug 不会无条件跑 brainstorming；如果根因修复出现新的产品/架构取舍，才动态追加 brainstorming。

### 4.3 Risk Mode：决定保障强度

Fast 必须证明需求明确、修改局部、消费者清楚、不改变公共边界/Schema/权限/关键语义、易回滚且可直接验证。它不创建 OpenSpec change，也没有预定人工 Gate。

Standard 是普通修改默认模式，使用 OpenSpec 持久化并保留一次 Plannotator Plan Review。

Governed 由关键业务语义、权限/敏感数据、Schema/回填、不兼容契约、共享基础设施、跨服务协调发布、缺少可信回滚等事实触发。在 Standard 之上增加高影响探索、隔离、完整验证和 Plannotator Code Review。

### 4.4 Specialized Gates：补专项证据

- data：Schema、回填、数据质量、隐私、备份与回滚。
- security：认证授权、秘密、输入边界、安全策略和负向测试。
- contract：消费者、兼容矩阵、契约测试、版本与弃用。
- infrastructure：环境矩阵、资源权限、可逆演练和恢复。
- release：发布顺序、灰度、停止条件和回滚演练。
- observability：日志、指标、追踪、告警和运行手册。

Gate 可以叠加，不增加新模式。例如数据库迁移通常是 `Migration/Infrastructure + Governed + data/release/observability`。

## 5. 三个工具的明确节点

Superpowers 只在对应方法节点调用原生 skill。Feature 必须 brainstorming；Bug 必须 systematic-debugging；生产行为变化执行 TDD；完成前执行 verification 和 review。

OpenSpec 从 Standard 开始使用 propose/apply/validate/archive，Governed 可先 explore。各 OPSX 子流程的 stop/ready 只把控制权交还 Router，用户不需要手动输入下一条命令。

Plannotator 在 Standard/Governed 计划完整后触发一次 Plan Review；Governed 在实际 diff 和验证证据完成后再触发 Code Review。

Integration Adapter Contract 会把 Superpowers 默认的逐段设计批准、独立设计/计划文件和 OpenSpec 的阶段停止合并到上述单一事实源和 Gate，但不会删减分析、调试、TDD、Review 与验证方法。

## 6. 状态持久化与续跑

Standard/Governed 在 OpenSpec change 内创建：

```text
openspec/changes/<change-id>/workflow-state.yaml
```

它只记录 intent、task type、mode、gates、current node、ordered nodes、状态和证据，不复制 proposal/spec/design/tasks。

状态在以下时机更新：propose 获得 change id 后、每个节点完成后、人工 Gate 前后、重路由后和中断前。新对话或上下文压缩后，Router 匹配活动 change，从最早未完成 REQUIRED 节点继续，已完成节点不会重复。

若同时有多个活动 change 且请求无法消歧，Router 才会询问要恢复哪一个。Fast 不创建 sidecar；升级 Standard 时再创建。

## 7. 什么时候需要你操作

| 动作 | 是否手动 |
|---|---|
| 启动 `/new-task` 或描述需求 | 一次 |
| Intent、Task Type、Mode、Gates 选择 | 不需要 |
| Superpowers 与 OpenSpec 内部节点 | 不需要 |
| Standard/Governed Plan Review | 需要在 Plannotator 批准或反馈 |
| Governed Code Review | 需要在 Plannotator 批准或反馈 |
| Git 提交、推送、部署 | 需要明确授权 |

真正影响结果且代码库无法回答的分歧、能力缺失导致降级、外部写入、秘密或破坏性动作也会暂停。Claude Code 自身权限弹窗属于宿主安全策略，不是工作流 Gate。

## 8. Token 控制

- 非 change 意图不加载修改链。
- Fast 不创建持久规格，不扫描全库。
- 任务类型只加载对应方法，不执行无关 brainstorming 或迁移步骤。
- Standard 只维护一个 OpenSpec change 和一次计划评审。
- Governed 的高噪声调查可隔离给子代理，主上下文只保留证据摘要。
- 专项风险通过 Gate 叠加，不复制完整模式流程。
- 状态文件避免上下文中断后重复探索、重复确认和重复 Token。

## 9. 降级与完成标准

Superpowers、OpenSpec 或 Plannotator 缺失时先尝试恢复；若替代方案降低保障才请求决定。关键测试环境不可用会使 Fast 失效，高风险验证缺失可升级 Governed。

任务完成时应看到：intent、task type、初始/最终 mode、gates、实际 ordered workflow、节点状态、工具调用、测试与规格校验、评审结果、未验证项和剩余风险。Standard/Governed 还必须先将状态标记 completed，再 validate 和 archive。

## 10. 维护脚本

以下文件只维护模板，不进入业务压缩包，也不需要业务开发者手动运行：

- `scripts/validate_workflow.py`：检查组合合同、状态合同、引用和发行包。
- `scripts/evaluate_routing.py`：校准 Intent、Task Type 和 Risk Mode。
- `scripts/build_distribution.py`：构建可复现压缩包。
- `evals/routing-cases.json`：覆盖解释、诊断、功能、Bug、重构、升级、迁移和维护场景。
