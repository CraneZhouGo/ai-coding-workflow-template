# AI Coding Workflow Template V3 Adaptive 详细使用说明

## 1. 设计目标

这套模板解决的不是“让 AI 多走几步”，而是让保障强度与需求风险匹配：小任务避免规格和评审开销，普通功能保留意图与计划，高风险变更得到完整的人类关卡和交付证据。

它是编排层，不是第四套开发方法论：

- Superpowers 决定怎样分析、计划、测试、调试和验证。
- OpenSpec 保存需求、变更和任务状态。
- Plannotator 承载需要人决定的计划与代码评审。
- Claude Code 执行探索、修改、命令和编排。

## 2. 使用前准备

### 2.1 合并模板

将 `ai-coding-workflow-template.zip` 解压到业务项目根目录。

如果项目已有 `CLAUDE.md` 或 `.claude/`：

1. 保留项目已有的构建、风格、安全和目录约定。
2. 合并本模板的 Stable Rules 与两个 skills。
3. 不覆盖 OpenSpec、Superpowers 或 Plannotator 自动生成的文件。

### 2.2 安装三项能力

在 Claude Code 中安装 Superpowers：

```text
/plugin install superpowers@claude-plugins-official
```

在终端安装并初始化 OpenSpec：

```text
npm install -g @fission-ai/openspec@latest
openspec init
```

初始化时选择 Claude Code。OpenSpec 升级后运行 `openspec update`，让其重新生成当前版本的 skills/commands。

在 Claude Code 中安装 Plannotator：

```text
/plugin marketplace add backnotprop/plannotator
/plugin install plannotator@plannotator
```

安装插件后重启 Claude Code，使 skills 和 hooks 生效。

### 2.3 填写项目画像

编辑 `.claude/project-profile.yaml`：

- `validation`：填入项目真实的构建、单元、集成、契约和静态检查命令。
- `risk.critical_domains`：列出项目不可低估的业务语义。
- `public_contract_locations`：填写 API、事件或 SDK 契约目录。
- `migration_locations`：填写数据库迁移与数据脚本目录。
- `shared_infrastructure_locations`：填写共享 CI、网关、鉴权或平台配置位置。
- `delivery`：说明回滚、观测和发布方式。

Profile 只保存项目事实。不要把路由规则复制进去，否则多处维护会产生漂移。

## 3. 日常使用

推荐入口：

```text
/new-task 为订单列表增加按科室筛选
```

也可以直接描述需求；Router skill 的描述覆盖新功能、Bug、重构、迁移和基础设施变更时，Claude Code 可以自动加载它。

你不需要手动选择模式。Router 会先给出简短 Route Card，然后继续执行：

```text
mode: standard
why: 新增用户行为；涉及 API 与页面；无 Schema/权限变化
durable_spec: openspec
human_gates: plan
next: 创建 OpenSpec change 并准备计划评审
```

只有出现真正的产品/架构分歧、工具缺失导致保障降级，或外部授权动作时，流程才会停下来询问。

## 4. 三种模式如何选择

### Fast

必须同时满足：需求明确、修改局部、消费者清楚、不碰公共契约/Schema/安全边界/关键业务语义、容易回滚、存在直接验证、无需设计取舍。

流程：定向探索 → 适用的 Superpowers debugging/TDD → 最小修改 → 直接测试 → diff 自审。

Fast 不创建 OpenSpec change，不打开 Plannotator，也不写持久计划。

### Standard

这是默认模式，适合普通功能、兼容性接口扩展、模块内多组件修改和有限业务规则。

流程：

1. 必要时使用 Superpowers brainstorming 澄清取舍。
2. 调用当前 OpenSpec 的原生 `propose`，只保留一个 change。
3. 用 Superpowers writing-plans 细化 OpenSpec tasks。
4. 进入 Plan Mode，Plannotator Hook 自动打开计划评审。
5. 批准后调用 OpenSpec `apply`，使用 TDD/debugging 实现。
6. 运行项目验证和 `openspec validate <change>`。
7. 做 spec-compliance 与 code-quality 两遍 AI review。
8. 用户已授权收尾时才 archive。

### Governed

任一高风险触发器都进入 Governed，包括：关键业务语义、权限与敏感数据、Schema 迁移或回填、不兼容公共契约、跨服务协调发布、共享安全/基础设施默认行为、缺少可信回滚、跨仓库发布顺序。

流程在 Standard 基础上增加：OpenSpec explore（存在不确定性时）、完整风险/迁移/发布约束、隔离子代理调查、高风险计划审批、迁移与回滚验证、Plannotator Code Review，以及适用的安全/数据/架构专项评审。

文件少不代表 Fast。一个只有两行的授权判断或数据库迁移仍然是 Governed；反过来，只修改“支付结果页文案”也不会因为出现“支付”两个字自动升级。

## 5. 工具是否需要手动触发

| 动作 | 默认触发方式 | 你是否要手动操作 |
|---|---|---|
| 启动任务 | `/new-task <需求>` 或直接描述需求 | 只需启动一次 |
| 选择模式 | Router 根据证据自动完成 | 不需要 |
| Superpowers skills | Router/Claude 按任务加载当前原生 skill | 不需要逐项触发 |
| OpenSpec 流程 | Router 调用当前 OPSX 能力 | 正常不需要；宿主不支持 skill 间调用时会提示唯一下一条命令 |
| Plannotator Plan Review | Claude Code Plan Mode 的 Hook 自动打开 | 需要在界面批准或反馈 |
| Plannotator Code Review | Governed 收尾时调用原生 review | 需要在界面批准或反馈 |
| Git 提交、推送、部署 | 仅在明确授权后执行 | 需要明确授权 |

因此，自动化的是“选择和编排”，保留给人的只有有价值的决策与授权。

## 6. Token 控制机制

- `CLAUDE.md` 只保留长期不变规则；具体流程按需从 skill 加载。
- Fast 不创建持久工件，不扫描全库，不进入 Plan Mode。
- Standard 只探索相关模块和直接消费者，Superpowers 结论写入同一个 OpenSpec change。
- Governed 把大范围调查放入隔离子代理，主上下文只接收证据摘要。
- 不复制 OpenSpec、Superpowers 和 Plannotator 的内部说明，避免版本漂移与重复 Token。
- 评审反馈只回传决策、阻断项和必要上下文。

## 7. 降级与故障处理

- Superpowers 不可用：恢复 plugin/skill；不能无声替换其 TDD、debugging 或 verification 保障。
- OpenSpec 不可用：Standard/Governed 暂停并给出 `openspec init/update` 指引；临时用对话计划替代属于保障降级，需要确认。
- Plannotator 不可用：需要人工 Gate 的模式暂停；可在用户确认后改用明确的文本审批。
- 测试环境不可用：Fast 不再成立；关键验证缺失时可升级 Governed。

## 8. 模板维护与业务项目的边界

压缩包内只有 6 个运行时文件。以下内容只用于模板自身维护，不需要业务开发者手动触发：

- `scripts/validate_workflow.py`：检查运行时结构、引用与发行包。
- `scripts/evaluate_routing.py`：执行校准案例，防止路由规则漂移。
- `scripts/build_distribution.py`：构建可复现压缩包。
- `evals/routing-cases.json`：覆盖小改动、普通功能、权限、迁移、契约和关键词误判等案例。

## 9. 完成标准

任务完成时应看到：初始/最终模式及证据、实际使用的三个工具节点、修改结果、已执行测试与规格校验、评审结果，以及未验证项和剩余风险。没有运行过的检查不能被描述为“通过”。
