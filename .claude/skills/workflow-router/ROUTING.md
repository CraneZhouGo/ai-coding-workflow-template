# Composable Routing Policy

路由顺序固定为：

```text
Intent → Task Type → Risk Mode → Specialized Gates → Ordered Execution
```

任务类型决定“用什么方法做”，风险模式决定“需要多强保障”，专项 Gate 决定“哪些风险必须额外证明”。三者不可互相替代。

## Intent

- `explain`：理解项目、回答问题、解释代码；只读。
- `review`：评审代码、设计、计划或 diff；只读，输出发现。
- `diagnose-only`：调查故障、定位根因；允许运行非破坏性诊断和测试，不修改。
- `plan-only`：制定方案、规格或迁移计划；不实施。
- `change`：用户明确要求新增、修复、重构、升级、迁移或修改。

若“诊断并修复”“规划并实施”等请求明确包含实施，归入 change。不得从“发现问题”推断用户授权修复。

## Task Type

change 请求选择一个主类型；混合任务选择最能决定核心方法的类型，并把其余风险映射为 Gate：

- `feature`：新增或改变用户可观察能力。方法核心是 brainstorming、规格/计划和 TDD。
- `bug`：已有行为失败或偏离预期。方法核心是 systematic-debugging、根因证据和失败回归测试。
- `refactor`：目标是不改变外部行为地改善结构。方法核心是行为基线、影响分析和 characterization tests。
- `upgrade-config`：依赖、运行时、构建、配置或策略版本变化。方法核心是 release notes/changelog、兼容性和回归基线。
- `migration-infrastructure`：Schema、数据、平台、网络、部署或基础设施迁移。方法核心是影响/回滚、dry-run 和 rollout verification。
- `maintenance`：文档、测试、格式、机械修改或其他无新业务设计的维护。方法核心是定向探索、最小编辑和直接验证。

如果探索证明主类型错误，Router 自动重分类并重组剩余节点。

## Risk Mode

模式路由顺序是“Governed 风险下限 → Fast 全条件准入 → Standard 默认”，不使用主观总分。

### Governed: any trigger is enough

只要本次变更实际改变以下任一语义，最低为 Governed：

- 资金、库存、身份认证、授权、隐私、敏感数据或监管行为
- 公共 API/事件契约的不兼容变化，或多个服务必须协调上线
- Schema 迁移、数据回填、双写、切流、停机或难以验证的历史数据修复
- 全局安全策略、共享基础设施默认行为或核心架构边界
- 缺少可信回滚路径，或失败会造成严重且难恢复的影响
- 跨多个仓库/团队交付，且任一方的版本或发布顺序影响正确性

影响面无法可靠界定、消费者众多、实施批次相互依赖或关键测试环境不可用，也可将 Standard 升级为 Governed。

### Fast: every condition must hold

只有同时满足以下条件才进入 Fast：

- 目标和验收标准明确，不需要产品或架构取舍
- 修改局限于一个局部，直接消费者清晰
- 不改变公共契约、持久化 Schema、权限、安全边界或关键业务语义
- 变更易回滚，失败影响有限
- 存在一个直接、可信且成本较低的验证方式

### Standard: the default

不满足 Fast 且未触发 Governed 的修改进入 Standard。它是普通功能、复杂 Bug、模块重构、兼容升级和有限业务规则变更的默认安全网。

## Specialized Gates

Gate 可叠加，不创建第四种模式：

- `data`：Schema、数据转换、回填、双写、数据质量或隐私数据。
- `security`：认证、授权、秘密、输入边界、安全策略或敏感数据处理。
- `contract`：公共 API、事件、SDK、文件格式或消费者兼容性。
- `infrastructure`：CI/CD、运行平台、网络、共享基础设施或资源策略。
- `release`：协调上线、灰度、回滚、feature flag、版本顺序或停机窗口。
- `observability`：新故障模式需要日志、指标、追踪、告警或运行手册证明。

Gate 由实际影响触发；目录位置和关键词只帮助定位证据。

## Overrides and unknowns

- 用户可以要求更高模式或额外 Gate。
- 用户要求更低模式不能绕过 Governed 触发器；必须说明保障损失并取得明确决定。
- 关键信息未知时先以 Standard 做定向探索；高影响区域的未知可直接触发 Governed。
- 非 change 意图不因“看起来高风险”而自动获得修改授权。
