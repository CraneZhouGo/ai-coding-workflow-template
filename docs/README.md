---
date created: 2026-08-25 11:55:06
date modified: 2026-08-27
---

# AI Coding Workflow Template V2.1

这是一套可复制到 Java / Spring Boot / 微服务项目中的 AI Coding Workflow 模板。

核心模型：

```text
变更风险评分 → R1~R4 基础档位
变更语义     → data/security/contract/... 门控
交付特征     → Agent/worktree/rollout 策略
```

三者分别判断，最终工作流为基础门控与可组合门控的并集。

## Components

- Claude Code：执行代码、命令、测试和 Git 操作
- Superpowers：需求、计划、TDD、验证等过程方法
- OpenSpec：首选规格 Source of Truth
- Plannotator：首选 Plan/Code Human Review Gate

工具不可用时使用 Capability Check 定义的受控降级；门控不能静默消失。

## Risk Tiers

| 档位 | 定位 |
|---|---|
| R1 | 明确、局部、低运行时风险；严格条件下可走 Fast Path |
| R2 | 常规功能或有限业务规则；紧凑规格 + 计划 + TDD + Review |
| R3 | 显著业务/数据/架构/基础设施风险；设计和专项门控 |
| R4 | 核心架构、不可逆迁移或协调发布；完整 S0~S9 |

风险采用 7 个锚定维度，最高 36 分。协作和多 Agent 不参与风险分，而是进入 Delivery Profile。

## Composable Gates

按变更语义叠加：architecture、data、security、compliance、contract、infrastructure、delivery、observability、isolation。

例如，位于支付模块的纯文案可以是 R1；真正改变支付状态语义时至少 R3，并叠加相应安全/合规门控。

## Quick Start

1. 复制 `.claude/`、`CLAUDE.md` 和 `scripts/` 中的运行时脚本。
2. 用真实代码库信息填写 `.claude/project-profile.yaml`。
3. 安装并启用所需工具；OpenSpec/Plannotator 缺失时按 Capability Check 处理。
4. 使用 `/new-task 你的需求`。
5. 定期使用 `/workflow-report`。

## Validation

```text
python scripts/validate_workflow.py --repository
python scripts/record_workflow_metric.py --record <record.json> --dry-run
python scripts/workflow_report.py
python scripts/build_distribution.py
```

验证脚本会检查评分基准、规则一致性和分发 manifest；CI 会构建并验证确定性 ZIP。

## Key Files

- `.claude/skills/workflow-router/SKILL.md`：路由主流程
- `.claude/skills/workflow-router/v2/complexity-matrix.md`：评分锚点
- `.claude/skills/workflow-router/v2/routing-rules.md`：语义红旗
- `.claude/skills/workflow-router/v2/gates.md`：可组合门控目录
- `.claude/skills/workflow-router/v2/toolcheck.md`：Capability Check
- `.claude/project-profile.yaml`：项目画像
- `.claude/skills/workflow-router/v2/metrics-schema.json`：Metrics Schema
- `scripts/record_workflow_metric.py`：Metrics 校验与追加
- `docs/superpowers/specs/2026-08-26-ai-coding-workflow-v2-design.md`：V2.1 设计

评分阈值只是初始建议。至少积累项目画像配置的最小样本数后，再结合档位矩阵、升级信号、返工和 escaped defects 调整。
